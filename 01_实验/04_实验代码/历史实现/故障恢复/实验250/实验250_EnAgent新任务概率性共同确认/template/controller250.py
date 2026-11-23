"""Full configured EnAgent stages with durable same-run progress, no old candidates."""
from common166 import *
import asyncio,copy,shutil
from collections import Counter
from types import SimpleNamespace
import checkpoint250 as ck
from checkpoint239 import UnsafeResume,atomic,inventory
from controller225 import NormalGenerationFailure
def run(core,spec,workdir,factory,bridge,resume=None):
 assert spec['ensemble_size']==3 and spec['coder_max_steps']==200 and spec['selector_max_turn']==30
 core.forbidden_keys(spec);work=Path(workdir);work.mkdir(parents=True,exist_ok=True);env=bridge.env;rootstate=E/'checkpoints'/env.task_id;clock=rootstate/'GENESIS.json'
 semantic_spec=copy.deepcopy(spec);semantic_spec['initial_repo']='/workspace/common_public_C0'
 env.started=float(os.environ.get('EXP239_LEASE_STARTED_MONOTONIC',env.started))
 if not clock.exists():atomic(clock,{'original_T0_monotonic':env.started,'actual_POST_T0_UTC':None,'actual_POST_T0_monotonic':None,'preparation_started_monotonic':env.started,'end_to_end_clock_includes_forward_supervisor_preparation':True,'initial_spec':spec,'initial_spec_SHA256':digest(semantic_spec),'new_independent_full_parameter_group':True,'old_candidates_or_outputs_reused':False})
 else:
  original=read(clock);assert original['initial_spec_SHA256']==digest(semantic_spec),'FROZEN_FULL_SPEC_DRIFT';env.started=original['original_T0_monotonic']
  if time.monotonic()<env.started:raise UnsafeResume('HOST_CLOCK_REBOOT_CANNOT_RESUME')
 counters=rootstate/'GLOBAL_ACCOUNTING.json'
 if counters.exists():
  values=read(counters);env.calls=values['LLM_request_intents'];env.out_tokens=values['output_tokens'];env.native_calls=values['public_native_calls'];env._product_native_roots=values['product_native_roots']
 ck.start_endpoint_timer(env)
 # New execution leases copy old paid evidence without a provider invocation.
 for previous in (E/'leases').glob('lease_*/f/'+env.task_id+'/'+env.method+'/llm'):
  if previous.resolve()==(env.out/'llm').resolve():continue
  for x in previous.glob('*'):
   target=env.out/'llm'/x.name;target.parent.mkdir(exist_ok=True)
   if target.exists() and sha(target)!=sha(x):raise UnsafeResume('PAID_EVIDENCE_COLLISION')
   if not target.exists():shutil.copyfile(x,target)
 stage_map={}
 def make(role,index,root):
  st=ck.Stage(env,role,index,root,bridge);stage_map[role,index]=st;base=factory(role,index,root);result=ck.transport(type(base),st)(env,role,index,root,bridge);result.turn=st.state['request_transport_turn'] if st.state['phase'] in ('MODEL_SETTLED_RESPONSE','TOOLS_RESPONSE_PENDING','MODEL_NOT_POSTED') else st.state['next_transport_turn'];return result
 def context_for(root,t):return core.Context(root,t,bridge.command_runner,bridge.edit_guard,spec['protected_paths'],{'business_paths':spec['business_paths'],'business_sha256':spec['business_sha256']})
 ck.install(core);cfg=SimpleNamespace(model=spec['model'],temperature=.5,top_p=1.,parallel_tool_calls=False,model_provider=SimpleNamespace(provider='openai'));tools=['str_replace_based_edit_tool','bash','sequentialthinking','task_done','read_full_failure','read_current_source','list_current_sources','read_public_history','read_public_test_view'];acfg=SimpleNamespace(model=cfg,max_steps=200,tools=tools,mcp_servers_config=None,allow_mcp_servers=[])
 flowfile=rootstate/'FLOW_STATE.json';flow=read(flowfile) if flowfile.exists() else {'N':3,'coder_max_steps':200,'selector_max_turn':30,'generations':{},'native_done':{},'votes':[]}
 if flow.get('native_inflight'):raise UnsafeResume('NATIVE_INFLIGHT_NO_AUTOMATIC_REEXECUTION')
 def flowcommit():atomic(flowfile,flow);atomic(counters,ck.accounting(env))
 initial={'business_paths':spec['business_paths'],'business_sha256':spec['business_sha256']}
 def clone(root):
  if not root.exists():core.snapshot_copy(spec['initial_repo'],root,spec['business_paths'],spec['business_sha256'])
 def native_once(key,root,ids):
  before={p:sha(root/p) for p in spec['business_paths']};binding=digest({'stable_role_clone_key':key,'ids':ids,'business':before})
  if key in flow['native_done']:
   value=flow['native_done'][key];assert value['input_SHA256']==binding;return value['result']
  flow['native_inflight']={'key':key,'input_SHA256':binding};flowcommit();result=bridge.public_runner(root,ids);flow['native_done'][key]={'input_SHA256':binding,'result':result};flow.pop('native_inflight');flowcommit();return result
 candidates=[];generations=[]
 for i in range(3):
  root=work/f'coder_{i}';clone(root)
  if str(i) in flow['generations']:row=flow['generations'][str(i)]
  else:
   t=make('coder',i,root);context=context_for(root,t);core.ACTIVE.context=context;agent=core.TraeAgent(acfg);agent.new_task('Resolve issue',extra_args={'project_path':str(root),'issue':spec['issue'],'must_patch':'true'});st=stage_map['coder',i];st.bind(agent,agent._llm_client,context)
   execution=ck.unpacked(st.state['execution']) if st.state['phase']=='ROLE_COMPLETED' else asyncio.run(agent.execute_task());context.check_protected();bridge.raise_if_failed()
   if getattr(env,'_generation_fatal',None) is not None:raise env._generation_fatal
   patch=agent.remove_patches_to_tests(agent.get_git_diff());row={'index':i,'success':bool(execution.success),'actual_steps':len(execution.steps),'final_result':str(execution.final_result),'nonempty_patch':bool(patch.strip()),'completion_policy':'original retains actual nonempty patch even without task_done'};st.state['execution']=ck.packed(execution);st.commit('ROLE_COMPLETED');flow['generations'][str(i)]=row;flowcommit();save(work/f'coder_{i}_actual_completion.json',row)
  patch=core.TraeAgent.remove_patches_to_tests(None,core.git(root,'diff','--no-ext-diff','--binary','HEAD'));changed=[p for p in core.git(root,'diff','--name-only','HEAD').splitlines() if p in spec['business_paths']];generations.append(row)
  if patch.strip():candidates.append({'id':i,'patch':patch,'files':{p:(root/p).read_bytes() for p in changed},'normalized':core.clean_patch(patch),'steps':row['actual_steps'],'initial_sha256':spec['business_sha256']})
 save(work/'generation_summary.json',{'actual_independent_attempts':len(generations),'rows':generations,'nonempty_candidate_count':len(candidates)})
 if not candidates:raise NormalGenerationFailure('ALL_CONFIGURED_ACTUAL_GENERATORS_RETURNED_NO_NONEMPTY_PATCH')
 tester_root=work/'tester_initial';clone(tester_root);ids=spec['public_test_ids'];baseline=native_once('initial_pass_baseline',tester_root,ids);assert set(baseline)==set(ids);passing=[k for k in ids if baseline[k]=='PASS']
 if not passing:raise RuntimeError('NO_EXECUTABLE_INITIALLY_PASSING_ORDINARY_TESTS')
 if 'tester_content' not in flow:
  t=make('tester',0,tester_root);context=context_for(tester_root,t);core.ACTIVE.context=context;tester=core.NativeClient(t);st=stage_map['tester',0];st.bind(None,tester,context);response=tester.chat([core.LLMMessage(role='user',content=core.regression_prompt(spec['issue'],passing))],SimpleNamespace(**(vars(cfg)|{'temperature':0.0})));flow['tester_content']=response.content;st.commit('ROLE_COMPLETED');flowcommit()
 content=flow['tester_content'];excluded=set(content.strip().splitlines());retained=[k for k in passing if k not in excluded];env.record('original_public_regression_exclusion',{'passing':passing,'raw_response':content,'retained':retained,'author_prompt':True,'private_read':False})
 for candidate in candidates:
  root=work/f"regression_{candidate['id']}";clone(root)
  for p,data in candidate['files'].items():(root/p).write_bytes(data)
  outcomes=native_once('regression_'+str(candidate['id']),root,retained) if retained else {};assert set(outcomes)==set(retained) and all(v in {'PASS','FAIL'} for v in outcomes.values());candidate['regression_failures']=[k for k,v in outcomes.items() if v!='PASS']
 pruned=[c for c in candidates if not c['regression_failures']] or candidates;unique=[];seen=set()
 for c in pruned:
  if c['normalized'] not in seen:unique.append(c);seen.add(c['normalized'])
 root=work/'selector';clone(root);candidate_list=[core.CandidatePatch(c['id'],c['patch'],c['normalized'],not c['regression_failures'],None) for c in unique];votes=flow['votes'];scfg=SimpleNamespace(**(vars(cfg)|{'temperature':.2}))
 for vote in range(len(votes),3):
  if votes and max(Counter(votes).values())>3/2:break
  t=make('selector',vote,root);context=context_for(root,t);core.ACTIVE.context=context;selector=core.SelectorAgent(llm_config=scfg,sandbox=core.NativeSandbox(context),project_path=str(root),issue_description=spec['issue'],trajectory_file_name=str(work/f'vote_{vote}.json'),candidate_list=candidate_list,max_turn=30);st=stage_map['selector',vote];st.bind(None,selector.llm_client,context)
  if st.state['phase']=='ROLE_COMPLETED':chosen=st.state['chosen']
  else:chosen,patch=selector.run();context.check_protected();bridge.raise_if_failed();st.state['chosen']=chosen;st.commit('ROLE_COMPLETED')
  votes.append(chosen);flowcommit();env.record('original_selector_actual_vote',{'vote':vote,'chosen':chosen,'votes':list(votes),'majority_threshold':3/2,'N':3})
 chosen=Counter(votes).most_common(1)[0][0];picked=next(c for c in unique if c['id']==chosen);result={'status':'CORE_FINISHED_FINAL_ACCEPTANCE_NOT_RUN','selected_candidate_id':chosen,'patch':picked['patch'],'generated_attempts':3,'generated_candidates':len(candidates),'generation_rows':generations,'voter_upper_bound':3,'actual_votes':votes,'initial_business_sha256':spec['business_sha256'],'public_initial_outcomes':baseline,'retained_public_regressions':retained,'candidate_regression_failures':{str(c['id']):c['regression_failures'] for c in candidates},'unique_after_prune':len(unique),'candidate_steps':[c['steps'] for c in candidates],'hidden_reads':0,'target_validation':False,'author_tie_policy':'source first highest-count insertion order; paper random tie differs','checkpoint_all_roles':True}
 flow['controller_result']=result;flowcommit();save(work/'result.json',result);return result

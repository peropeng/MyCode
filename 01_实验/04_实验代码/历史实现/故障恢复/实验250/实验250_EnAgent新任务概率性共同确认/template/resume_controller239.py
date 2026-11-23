"""Continue original selector exactly; completed generations/tester/votes are inputs."""
from common166 import *
import copy,shutil
from collections import Counter
from types import SimpleNamespace
from checkpoint239 import Store,UnsafeResume,install,checkpoint_transport,inventory,llm_messages
from controller225 import NormalGenerationFailure
CURRENT_STORE=None

def run(core,spec,workdir,factory,bridge,resume=None):
 global CURRENT_STORE
 p=authorization();manifest=Path(p['resume_lineage'][bridge.env.task_id]['path'])
 if sha(manifest)!=p['resume_lineage'][bridge.env.task_id]['SHA256']:raise UnsafeResume('LINEAGE_SOURCE_DRIFT')
 line=read(manifest);line['_lineage_path']=str(manifest)
 if not line.get('can_resume_exact_safe_boundary'):raise UnsafeResume('OLD_MUTABLE_TOOL_STATE_NOT_RECONSTRUCTED')
 for path,h in line['source_refs_SHA256'].items():
  if sha(path)!=h:raise UnsafeResume('HISTORICAL_AUTHOR_ARTIFACT_DRIFT')
 oldspec=line['old_original_spec']
 for k in ('ensemble_size','coder_max_steps','selector_max_turn','business_paths','business_sha256','public_test_ids','model'):
  if spec[k]!=oldspec[k]:raise UnsafeResume('ORIGINAL_ALGORITHM_OR_C0_CHANGED '+k)
 work=Path(workdir);work.mkdir(parents=True,exist_ok=True)
 for label,expected in line['old_immutable_clone_inventories'].items():
  if label not in ('coder_0','coder_1','regression_0','regression_1','tester_initial','selector'):raise UnsafeResume('UNDECLARED_AUTHOR_CLONE')
  saved=manifest.parent/'clones'/label
  if inventory(saved)!=expected:raise UnsafeResume('SAVED_AUTHOR_CLONE_DRIFT')
  target=work/label
  if not target.exists():shutil.copytree(saved,target)
  elif label!='selector' and inventory(target)!=expected:
   actual=inventory(target);changed={k for k in set(actual)|set(expected) if actual.get(k)!=expected.get(k)}
   # Original git diff refreshes cached stat data in index. Completed business,
   # refs and objects remain immutable; restore only this exact saved index.
   if changed!={'.git/index'}:raise UnsafeResume('COMPLETED_CODER_OR_TESTER_CLONE_CHANGED')
   index=target/'.git/index';oldbytes=index.read_bytes();journal=E/'checkpoint_metadata_history'/bridge.env.task_id/(label+'_'+sha(index)+'.index')
   journal.parent.mkdir(parents=True,exist_ok=True)
   if not journal.exists():journal.write_bytes(oldbytes)
   index.write_bytes((saved/'.git/index').read_bytes())
   if inventory(target)!=expected:raise UnsafeResume('COMPLETED_CLONE_INDEX_RESTORE_DIFFERS')
 for i,row in enumerate(line['generation_summary']['rows']):save(work/f'coder_{i}_actual_completion.json',row)
 save(work/'generation_summary.json',line['generation_summary'])
 env=bridge.env;env._science_lineage=line
 store=Store(E/'checkpoints'/env.task_id,work,env,line);store.bridge=bridge;CURRENT_STORE=store
 # Same scientific T0 and cumulative usage. The failed unsent intent remains
 # in the request-intent counter; reissued action retains its original seed/turn.
 counts=store.state.get('accounting')
 if counts:
  env.calls=counts['LLM_request_intents'];env.out_tokens=counts['output_tokens'];env.native_calls=counts['public_native_calls'];env._product_native_roots=counts['product_native_roots'];env._prior_resume_active_elapsed=max(0,counts['active_elapsed_seconds']-line['science_old_active_elapsed_seconds'])
 else:
  env.calls=line['old_request_intents'];env.out_tokens=line['old_output_tokens'];env.native_calls=line['old_public_native_calls'];env._product_native_roots=line['old_public_native_calls'];env._prior_resume_active_elapsed=0
 env._prior_resume_active_elapsed=p.get('_prior_resume_active_elapsed_seconds',0)
 if time.monotonic()<line['science_original_T0_monotonic']:raise UnsafeResume('HOST_BOOT_CLOCK_SPAN_CHANGED_EXACT_T0_REQUIRES_RECONCILIATION')
 env.started=line['science_original_T0_monotonic'];store.recover_uncertain_model()
 if store.state.get('inflight_tool'):raise UnsafeResume('OLD_OR_CURRENT_INFLIGHT_TOOL_NO_AUTOMATIC_REEXECUTION')
 if store.state['phase']=='CONTROLLER_COMPLETED':
  result=store.state['controller_result'];save(work/'result.json',result);return result
 store.restore_work()
 if store.state.get('bash_cwd','.') not in ('','.'):raise UnsafeResume('NONROOT_PERSISTENT_BASH_CWD_REQUIRES_EXPLICIT_RESTORE_SOURCE')
 # Preserve previous actual paid receipts and response evidence in the new
 # owner, never invoke provider for these existing transactions.
 oldllm=Path(line['old_flow'])/'llm';newllm=env.out/'llm';newllm.mkdir(exist_ok=True)
 for n in range(1,line['old_settled_API_calls']+1):
  for suffix in ('request','response','finance_receipt','http_response'):
   old=oldllm/f'{n:03d}_{suffix}.json';target=newllm/old.name
   if old.exists():
    if target.exists() and sha(target)!=sha(old):raise UnsafeResume('OLD_SETTLED_ARTIFACT_REWRITE')
    if not target.exists():shutil.copyfile(old,target)
 initial={'business_paths':spec['business_paths'],'business_sha256':spec['business_sha256']}
 candidates=[]
 for identity,patch in zip(line['candidate_ids_in_author_order'],line['candidate_patches_in_author_order'],strict=True):
  root=work/f'coder_{identity}'
  actual=core.TraeAgent.remove_patches_to_tests(None,core.git(root,'diff','--no-ext-diff','--binary','HEAD'))
  if actual!=patch:raise UnsafeResume('RECOVERED_CANDIDATE_PATCH_DIFFERS_FROM_ORIGINAL_SELECTOR_INPUT')
  candidates.append({'id':identity,'patch':patch,'normalized':core.clean_patch(patch),'regression_failures':[],'steps':line['generation_summary']['rows'][identity]['actual_steps']})
 if len({x['normalized'] for x in candidates})!=len(candidates):raise UnsafeResume('ORIGINAL_NORMALIZATION_ORDER_REQUIRES_MAPPING')
 cfg=SimpleNamespace(model=spec['model'],temperature=.2,top_p=1.,parallel_tool_calls=False,model_provider=SimpleNamespace(provider='openai'))
 hooks=install(core,store);env.record('checkpoint_source_hooks239',hooks)
 candidate_list=[core.CandidatePatch(c['id'],c['patch'],c['normalized'],True,None) for c in candidates]
 votes=store.state['votes'];N=spec['ensemble_size']
 for vote in range(store.state['vote_index'],N):
  root=work/'selector';transport=checkpoint_transport(type(factory('selector',vote,root)),store)(env,'selector',vote,root,bridge)
  transport.turn=store.state['next_turn']
  context=core.Context(root,transport,bridge.command_runner,bridge.edit_guard,spec['protected_paths'],initial);core.ACTIVE.context=context;store.context=context
  # The original ctor resets tracked business. Preserve the exact mutable state
  # around that original side effect, then restore the committed clone bytes.
  if 'blob_inventory' not in store.state:store.commit('SELECTOR_NEXT_MODEL')
  selector=core.SelectorAgent(llm_config=cfg,sandbox=core.NativeSandbox(context),project_path=str(root),issue_description=spec['issue'],trajectory_file_name=str(work/f'vote_{vote}.json'),candidate_list=candidate_list,max_turn=spec['selector_max_turn'])
  store.restore_work()
  editor=getattr(context,'_source_editor_with_undo',None)
  if editor is not None:
   from collections import defaultdict
   editor._file_history=defaultdict(list,{root/rel:list(values) for rel,values in store.state['editor_undo_state'].items()})
  selector.llm_client.history=copy.deepcopy(store.state['history'])
  # Known unsent states are retryable; the exact action cursor was not consumed.
  if store.state['phase']=='MODEL_NOT_POSTED':store.state['phase']='SELECTOR_NEXT_MODEL'
  chosen,patch=selector.run();context.check_protected();bridge.raise_if_failed();votes.append(chosen)
  env.record('original_selector_actual_vote',{'vote':vote,'chosen':chosen,'votes':list(votes),'majority_threshold':N/2,'N':N,'prior_vote_resumed_not_reexecuted':True})
  store.state.update(votes=votes,vote_index=vote+1,next_turn=0,history=[],incoming=[],tool_results={});store.commit('VOTE_COMPLETED')
  if max(Counter(votes).values())>N/2:break
 chosen=Counter(votes).most_common(1)[0][0];picked=next(c for c in candidates if c['id']==chosen)
 result={'status':'CORE_FINISHED_FINAL_ACCEPTANCE_NOT_RUN','selected_candidate_id':chosen,'patch':picked['patch'],'generated_attempts':N,'generated_candidates':len(candidates),'generation_rows':line['generation_summary']['rows'],'voter_upper_bound':N,'actual_votes':votes,'initial_business_sha256':spec['business_sha256'],'public_initial_outcomes':line['baseline'],'retained_public_regressions':line['tester_regression_record']['retained'],'candidate_regression_failures':{str(c['id']):[] for c in candidates},'unique_after_prune':len(candidates),'candidate_steps':[c['steps'] for c in candidates],'hidden_reads':0,'target_validation':False,'author_tie_policy':'first highest-count candidate in insertion order','resume_lineage_SHA256':sha(manifest),'prior_paid_API_reposted':0,'same_original_scientific_T0':True,'checkpoint_accounting':store.accounting()}
 save(work/'result.json',result);store.state['controller_result']=result;store.commit('CONTROLLER_COMPLETED');return result

def verify_first_author_body(body):
 store=CURRENT_STORE
 if store is not None and store.state.get('repair_evidence_SHA256'):
  repair_path=Path(authorization()['seed_cursor_repair_SOURCE']['path'])
  if sha(repair_path)!=store.state['repair_evidence_SHA256']:raise UnsafeResume('SEED_CURSOR_REPAIR_EVIDENCE_DRIFT')
  evidence=read(repair_path);bodyhash=digest(body)
  if bodyhash in {x['pre_C0_body_SHA256'] for x in evidence['settled_bodies']}:raise UnsafeResume('SETTLED_COMPLETE_AUTHOR_BODY_NO_REPOST')
  tag='Common current C0 evidence for every method. Decode exact-line envelopes before use. '
  for receiptpath in (store.env.out/'llm').glob('*_finance_receipt.json'):
   if read(receiptpath).get('status')!='SETTLED':continue
   requestpath=receiptpath.with_name(receiptpath.name.replace('_finance_receipt','_request'))
   if not requestpath.exists():raise UnsafeResume('SETTLED_REQUEST_EVIDENCE_MISSING')
   paid=copy.deepcopy(read(requestpath)['body']);paid['messages']=[x for x in paid['messages'] if not str(x.get('content','')).startswith(tag)]
   if digest(paid)==bodyhash:raise UnsafeResume('SETTLED_COMPLETE_AUTHOR_BODY_NO_REPOST')
  if store.state.get('repair_first_corrected_body_not_yet_checked'):
   if bodyhash!=store.state['repair_first_corrected_author_body_SHA256']:raise UnsafeResume('CORRECTED_FIRST_AUTHOR_BODY_DIFFERS_BEFORE_POST')
   store.state['repair_first_corrected_body_not_yet_checked']=False
  return
 if store is None or not store.state.get('first_original_unsent_body_not_yet_checked'):return
 if digest(body)!=store.lineage['expected_first_unsent_author_body_SHA256']:raise UnsafeResume('FIRST_RESUME_BODY_DIFFERS_FROM_OLD_UNSENT_INTENT_BEFORE_POST')
 store.state['first_original_unsent_body_not_yet_checked']=False

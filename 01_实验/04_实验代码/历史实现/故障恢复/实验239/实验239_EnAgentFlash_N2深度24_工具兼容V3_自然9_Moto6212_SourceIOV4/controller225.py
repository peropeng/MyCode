"""Configured independent EnAgent generation, public pruning and original voting."""
from common166 import *
import asyncio,copy
from collections import Counter
from types import SimpleNamespace

class NormalGenerationFailure(RuntimeError):pass

def run(core,spec,workdir,factory,bridge,resume=None):
 core.forbidden_keys(spec);workdir=Path(workdir);workdir.mkdir(parents=True,exist_ok=False)
 initial={'business_paths':spec['business_paths'],'business_sha256':spec['business_sha256']}
 cfg=SimpleNamespace(model=spec['model'],temperature=.7,top_p=1.,parallel_tool_calls=False,model_provider=SimpleNamespace(provider='openai'))
 tools=['str_replace_based_edit_tool','bash','sequentialthinking','task_done','read_full_failure','read_current_source','list_current_sources','read_public_history']
 acfg=SimpleNamespace(model=cfg,max_steps=spec['coder_max_steps'],tools=tools,mcp_servers_config=None,allow_mcp_servers=[])
 N=int(spec['ensemble_size']);assert N>=2
 candidates=[];generations=[];env=bridge.env
 for i in range(N):
  if resume:
   oldroot=Path(resume['workdir'])/f'coder_{i}';root=workdir/f'coder_{i}'
   row=read(Path(resume['workdir'])/f'coder_{i}_actual_completion.json');generations.append(row)
   patch=core.TraeAgent.remove_patches_to_tests(None,core.git(oldroot,'diff','--no-ext-diff','--binary','HEAD'))
   changed=[p for p in core.git(oldroot,'diff','--name-only','HEAD').splitlines() if p in spec['business_paths']]
   core.snapshot_copy(spec['initial_repo'],root,spec['business_paths'],spec['business_sha256'])
   frozen_files={p:(oldroot/p).read_bytes() for p in changed}
   for p,data in frozen_files.items():(root/p).write_bytes(data)
   if core.TraeAgent.remove_patches_to_tests(None,core.git(root,'diff','--no-ext-diff','--binary','HEAD'))!=patch:raise RuntimeError('FROZEN_GENERATOR_PATCH_DRIFT_ON_CONTINUATION')
   save(workdir/f'coder_{i}_actual_completion.json',row)
   env.record('frozen_actual_generation_continued_without_reroll',{'index':i,'patch_sha256':hashlib.sha256(patch.encode()).hexdigest(),'prior_actual_steps':row['actual_steps'],'new_model_generation_calls':0})
   if patch.strip():candidates.append({'id':i,'patch':patch,'files':frozen_files,'normalized':core.clean_patch(patch),'steps':row['actual_steps'],'initial_sha256':spec['business_sha256']})
   continue
  root=workdir/f'coder_{i}';env.record('N_actual_generation_start',{'index':i,'configured_N':N,'same_FAILED_inventory':spec['business_sha256']})
  core.snapshot_copy(spec['initial_repo'],root,spec['business_paths'],spec['business_sha256'])
  context=core.Context(root,factory('coder',i,root),bridge.command_runner,bridge.edit_guard,spec['protected_paths'],initial);core.ACTIVE.context=context
  agent=core.TraeAgent(acfg);agent.new_task('Resolve issue',extra_args={'project_path':str(root),'issue':spec['issue'],'must_patch':'true'})
  execution=asyncio.run(agent.execute_task());context.check_protected();bridge.raise_if_failed()
  if getattr(env,'_generation_fatal',None) is not None:raise env._generation_fatal
  patch=agent.remove_patches_to_tests(agent.get_git_diff())
  changed=[p for p in core.git(root,'diff','--name-only','HEAD').splitlines() if p in spec['business_paths']]
  row={'index':i,'success':bool(execution.success),'actual_steps':len(execution.steps),'final_result':str(execution.final_result),'nonempty_patch':bool(patch.strip()),'completion_policy':'retain actual patch even if task_done not emitted; author selector skips only empty patches'}
  generations.append(row);save(workdir/f'coder_{i}_actual_completion.json',row);env.record('N_actual_generation_finished',row)
  if patch.strip():candidates.append({'id':i,'patch':patch,'files':{p:(root/p).read_bytes() for p in changed},'normalized':core.clean_patch(patch),'steps':len(execution.steps),'initial_sha256':spec['business_sha256']})
 save(workdir/'generation_summary.json',{'actual_independent_attempts':len(generations),'rows':generations,'nonempty_candidate_count':len(candidates)})
 if not candidates:raise NormalGenerationFailure('ALL_CONFIGURED_ACTUAL_GENERATORS_RETURNED_NO_NONEMPTY_PATCH')
 tester_root=workdir/'tester_initial';core.snapshot_copy(spec['initial_repo'],tester_root,spec['business_paths'],spec['business_sha256'])
 ids=spec['public_test_ids'];baseline=resume['baseline'] if resume else bridge.public_runner(tester_root,ids)
 if set(baseline)!=set(ids):raise RuntimeError('PUBLIC_RUNNER_OMITTED_ORDINARY_OUTCOME')
 passing=[k for k in ids if baseline[k]=='PASS']
 if not passing:raise RuntimeError('NO_EXECUTABLE_INITIALLY_PASSING_ORDINARY_TESTS')
 if resume:content=resume['tester_content']
 else:
  tester=core.NativeClient(factory('tester',0,tester_root));tcfg=SimpleNamespace(**(vars(cfg)|{'temperature':0.0}))
  response=tester.chat([core.LLMMessage(role='user',content=core.regression_prompt(spec['issue'],passing))],tcfg);content=response.content
 excluded=set(content.strip().splitlines());retained=[k for k in passing if k not in excluded]
 env.record('original_public_regression_exclusion',{'passing':passing,'raw_response':content,'retained':retained,'author_prompt':True,'private_read':False,'no_generation_reroll':bool(resume),'empty_regression_list_author_semantics':'len(regressions)==0; not a wrapper exception'})
 for candidate in candidates:
  root=workdir/f"regression_{candidate['id']}";core.snapshot_copy(spec['initial_repo'],root,spec['business_paths'],spec['business_sha256'])
  for p,data in candidate['files'].items():(root/p).write_bytes(data)
  outcomes=bridge.public_runner(root,retained) if retained else {}
  if not retained:env.record('empty_original_regression_set',{'candidate':candidate['id'],'retained':[],'failures':[],'actual_regression_tests_run':0,'author_empty_regressions_pass_predicate':True,'all_ordinary_and_goal_still_evaluated_after_selection':True})
  if set(outcomes)!=set(retained) or any(v not in {'PASS','FAIL'} for v in outcomes.values()):raise RuntimeError('ORDINARY_REGRESSION_NATIVE_OUTCOME_UNKNOWN')
  candidate['regression_failures']=[k for k,v in outcomes.items() if v!='PASS']
 pruned=[c for c in candidates if not c['regression_failures']] or candidates
 unique=[];seen=set()
 for candidate in pruned:
  if candidate['normalized'] not in seen:unique.append(candidate);seen.add(candidate['normalized'])
 selector_root=workdir/'selector';core.snapshot_copy(spec['initial_repo'],selector_root,spec['business_paths'],spec['business_sha256'])
 candidate_list=[core.CandidatePatch(c['id'],c['patch'],c['normalized'],not c['regression_failures'],None) for c in unique]
 votes=[];scfg=SimpleNamespace(**(vars(cfg)|{'temperature':.2}))
 for vote in range(N):
  context=core.Context(selector_root,factory('selector',vote,selector_root),bridge.command_runner,bridge.edit_guard,spec['protected_paths'],initial);core.ACTIVE.context=context
  selector=core.SelectorAgent(llm_config=scfg,sandbox=core.NativeSandbox(context),project_path=str(selector_root),issue_description=spec['issue'],trajectory_file_name=str(workdir/f'vote_{vote}.json'),candidate_list=candidate_list,max_turn=spec['selector_max_turn'])
  chosen,patch=selector.run();context.check_protected();bridge.raise_if_failed();votes.append(chosen)
  env.record('original_selector_actual_vote',{'vote':vote,'chosen':chosen,'votes':list(votes),'majority_threshold':N/2,'N':N})
  if max(Counter(votes).values())>N/2:break
 counts=Counter(votes);chosen=counts.most_common(1)[0][0];picked=next(c for c in unique if c['id']==chosen)
 result={'status':'CORE_FINISHED_FINAL_ACCEPTANCE_NOT_RUN','selected_candidate_id':chosen,'patch':picked['patch'],'generated_attempts':N,'generated_candidates':len(candidates),'generation_rows':generations,'voter_upper_bound':N,'actual_votes':votes,'initial_business_sha256':spec['business_sha256'],'public_initial_outcomes':baseline,'retained_public_regressions':retained,'candidate_regression_failures':{str(c['id']):c['regression_failures'] for c in candidates},'unique_after_prune':len(unique),'candidate_steps':[c['steps'] for c in candidates],'hidden_reads':0,'target_validation':False,'author_tie_policy':'first highest-count candidate in insertion order'}
 save(workdir/'result.json',result);return result

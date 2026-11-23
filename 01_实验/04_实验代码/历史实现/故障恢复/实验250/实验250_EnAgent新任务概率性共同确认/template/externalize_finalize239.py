"""Freeze completed EnAgent business choice; actor never executes final/private."""
from pathlib import Path
import copy,time

def public_only_probe(env,original):
 """Keep original public G/O callbacks; reject the old final/private route."""
 def probe(active,frozen,nodes,out,python,package,deadline):
  allowed=set(env.recovery_goal_nodes)|set(env.public_regression_nodes)
  output=Path(out).resolve()
  if getattr(env,'_final_validation_running',False) or not isinstance(nodes,(list,tuple)) or not nodes or not set(nodes)<=allowed:raise RuntimeError('EA21_AUTHOR_PRIVATE_PROBE_FORBIDDEN_ROOT_EXTERNAL_ONLY')
  if Path(active).resolve()!=Path(env.active).resolve() or Path(frozen).resolve()!=Path(env._paths['frozen']).resolve() or Path(python).resolve()!=Path(env._paths['python']).resolve() or package!=env.package:raise RuntimeError('EA21_ORIGINAL_PUBLIC_PROBE_BINDINGS_REQUIRED')
  if not output.is_relative_to(Path(env.out).resolve()) or any(x in {'final_preservation','final_public_acceptance','private','hidden'} for x in output.relative_to(Path(env.out).resolve()).parts):raise RuntimeError('EA21_AUTHOR_FINAL_PROBE_ROUTE_FORBIDDEN')
  return original(active,frozen,nodes,out,python,package,deadline)
 return probe

def require_actor_source_release():
 from common166 import E,authorization,read
 import control235
 p=authorization()
 if p.get('private_authorized') or p.get('once_private_authorized'):raise RuntimeError('EA21_AUTHOR_PRIVATE_AUTHORITY_MUST_BE_FALSE')
 if not control235.MECHANICAL:
  g=read(E/'root_grant239.json')
  if g.get('Root_local_public_native_qualification_admitted') is not True or g.get('Root_external_final_source_review_admitted') is not True:raise RuntimeError('EA21_FRESH_ORDINARY300_AND_EXTERNAL_FINAL_SOURCE_REVIEW_REQUIRED')

def install(env):
 from common166 import E,authorization,read,sha,digest,save,require_open
 p=authorization()
 if p.get('private_authorized') or p.get('once_private_authorized'):raise RuntimeError('EA21_AUTHOR_PRIVATE_AUTHORITY_MUST_BE_FALSE')
 # The original replay probe also serves legitimate public G/O callbacks.
 # Forward only those exact callbacks, never the historical hidden final path.
 env.run.probe=public_only_probe(env,env.run.probe)
 def freeze(result):
  require_open();current=authorization()
  if current.get('private_authorized') or current.get('once_private_authorized'):raise RuntimeError('EA21_AUTHOR_PRIVATE_GRANT_CHANGED')
  if getattr(env,'_generation_fatal',None) is not None:raise env._generation_fatal
  if result.get('status')!='COMPLETED' or result.get('runtime_core',{}).get('complete') is not True or not getattr(env,'flow_configuration_sealed',False):raise RuntimeError('EA21_COMPLETE_ORIGINAL_CORE_REQUIRED_BEFORE_SELECTION')
  final=result.get('final_snapshot');core=result.get('enagent_core_result',{})
  if not final or type(core.get('selected_candidate_id')) is not int or not 0<=core['selected_candidate_id']<current['budget']['enagent_ensemble_size']:raise RuntimeError('EA21_ORIGINAL_IMMUTABLE_SELECTION_REQUIRED')
  selected_before=env.out/'selection_before_hidden.json'
  if read(selected_before).get('snapshot')!=final:raise RuntimeError('EA21_ORIGINAL_ENV_SELECTION_DOES_NOT_MATCH_COMPLETED_CONTROLLER')
  snapshot_id=final.get('id');registered=getattr(env,'_snapshots',{}).get(snapshot_id)
  if not isinstance(snapshot_id,str) or not snapshot_id.startswith('s') or not snapshot_id[1:].isdigit() or registered!=final:raise RuntimeError('EA21_ORIGINAL_REGISTERED_SNAPSHOT_REQUIRED')
  registry_path=(env.out/'snapshots'/snapshot_id/'snapshot.json').resolve()
  if Path(final.get('archive_path','')).resolve()!=registry_path.parent or not registry_path.is_relative_to((env.out/'snapshots').resolve()) or read(registry_path)!=registered:raise RuntimeError('EA21_ORIGINAL_PERSISTED_SNAPSHOT_REGISTRATION_REQUIRED')
  controller_result=E/'r'/('%02d'%current['task_order'].index(env.task_id))/'w/result.json'
  if read(controller_result)!=core or core.get('status')!='CORE_FINISHED_FINAL_ACCEPTANCE_NOT_RUN' or core.get('generated_attempts')!=current['budget']['enagent_ensemble_size'] or core.get('hidden_reads')!=0:raise RuntimeError('EA21_COMPLETE_ORIGINAL_CONTROLLER_ARTIFACT_REQUIRED')
  repo=env.active/'repo'
  if Path(env.active).is_symlink() or repo.is_symlink() or not repo.resolve().is_relative_to(E.resolve()):raise RuntimeError('EA21_ORIGINAL_RUNTIME_SELECTION_OWNER_REQUIRED')
  runtime_before=env.run.qualify.inventory(repo)
  if digest(runtime_before)!=final.get('inventory_sha256'):raise RuntimeError('EA21_SELECTED_RUNTIME_DIFFERS_FROM_ORIGINAL_SNAPSHOT')
  actual_diff={rel:runtime_before.get(rel) for rel in sorted(set(runtime_before)|set(env._original)) if runtime_before.get(rel)!=env._original.get(rel)}
  if final.get('diff')!=actual_diff:raise RuntimeError('EA21_SELECTED_RUNTIME_DIFF_DIFFERS_FROM_ORIGINAL_SNAPSHOT')
  if any(not env._core.is_business('repo/'+rel) for rel in actual_diff):raise RuntimeError('EA21_SELECTED_RUNTIME_NONBUSINESS_CHANGE_FORBIDDEN')
  # The existing supervisor deadline remains authoritative throughout freezing.
  parent_deadline=float(__import__('os').environ['EXP239_FLOW_DEADLINE_MONOTONIC'])
  if env.deadline!=parent_deadline or time.monotonic()>=parent_deadline:raise RuntimeError('EA21_ORIGINAL_SCIENTIFIC_CLOCK_NOT_AVAILABLE')
  evidence_before={str(path):sha(path) for path in (selected_before,registry_path,controller_result)}
  business={rel:h for rel,h in runtime_before.items() if env._core.is_business('repo/'+rel)}
  if not business:raise RuntimeError('EA21_NONEMPTY_BUSINESS_SELECTION_REQUIRED')
  paths={}
  for rel in business:
   if not isinstance(rel,str) or '\\' in rel or ':' in rel or any(part in ('','.','..') for part in rel.split('/')):raise RuntimeError('EA21_IMMUTABLE_BUSINESS_SELECTION_PATH_INVALID')
   source=repo/rel;cursor=repo
   for part in rel.split('/'):
    cursor=cursor/part
    if cursor.is_symlink():raise RuntimeError('EA21_IMMUTABLE_BUSINESS_SELECTION_PATH_INVALID')
   if not source.resolve().is_relative_to(repo.resolve()) or not source.is_file() or sha(source)!=business[rel]:raise RuntimeError('EA21_SELECTED_BUSINESS_SOURCE_DRIFT_BEFORE_COPY')
   paths[rel]=source
  if any(rel not in business for rel in actual_diff):raise RuntimeError('EA21_SELECTED_BUSINESS_DELETION_UNSUPPORTED')
  selection_path=env.out/'immutable_selection.json';selected=env.out/'immutable_business_selection'
  if selection_path.exists() or selected.exists():raise RuntimeError('EA21_NO_SELECTION_REWRITE_OR_RETRY')
  selected.mkdir();inventory={}
  for rel in sorted(business):
   source=paths[rel];target=selected/rel
   if sha(source)!=business[rel]:raise RuntimeError('EA21_SELECTED_BUSINESS_SOURCE_DRIFT_DURING_COPY')
   target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes());inventory[rel]=sha(target)
   if inventory[rel]!=business[rel] or sha(source)!=business[rel]:raise RuntimeError('EA21_SELECTED_BUSINESS_SOURCE_OR_COPY_DRIFT')
  runtime_after=env.run.qualify.inventory(repo)
  if runtime_after!=runtime_before or digest(runtime_after)!=final['inventory_sha256'] or env.run.qualify.inventory(selected)!=inventory:raise RuntimeError('EA21_SELECTED_WHOLE_RUNTIME_OR_COPY_DRIFT_AFTER_COPY')
  if any(sha(path)!=h for path,h in evidence_before.items()) or env._snapshots.get(snapshot_id)!=final:raise RuntimeError('EA21_ORIGINAL_SELECTION_EVIDENCE_DRIFT_DURING_COPY')
  require_open();after_authority=authorization()
  if after_authority.get('private_authorized') or after_authority.get('once_private_authorized') or after_authority.get('scope_id')!=current['scope_id']:raise RuntimeError('EA21_AUTHOR_PRIVATE_OR_SCOPE_GRANT_CHANGED_DURING_FREEZE')
  if env.deadline!=parent_deadline or time.monotonic()>=parent_deadline:raise RuntimeError('EA21_ORIGINAL_SCIENTIFIC_CLOCK_NOT_AVAILABLE')
  selection={'schema':'EA21-complete-author-immutable-business-selection/1','task_id':env.task_id,'method':env.method,'status':'SELECTED_AWAIT_EXTERNAL_PRIVATE','success':None,'author_done':True,'core_completed':True,'complete_search_under_declared_budget':True,'unknown':None,'budget_censored':False,'private_calls_before_selection':0,'requires_once_private_external_to_actor':True,'selection_root':str(selected),'business_paths_sha256':inventory,'selected_sha256':digest(inventory),'original_selected_snapshot':copy.deepcopy(final),'enagent_core_result':copy.deepcopy(core),'original_runtime_core':copy.deepcopy(result['runtime_core']),'selection_before_hidden_path':str(env.out/'selection_before_hidden.json'),'selection_before_hidden_SHA256':sha(env.out/'selection_before_hidden.json'),'method_protocol_SHA256':sha(E/'protocol225.json'),'method_source_seal_SHA256':sha(E/'source_seal239.json'),'scope_id':current['scope_id'],'original_science_started_monotonic':env.started,'original_flow_deadline_monotonic':parent_deadline,'LLM_calls':env.calls,'output_tokens':env.out_tokens,'author_public_native_calls':env.native_calls,'author_product_native_roots':env._product_native_roots,'no_private_or_final_in_author_process':True}
  selection.update(original_controller_result_path=str(controller_result),original_controller_result_SHA256=sha(controller_result))
  selection.update(original_snapshot_registry_path=str(registry_path),original_snapshot_registry_SHA256=sha(registry_path),original_snapshot_registered_and_persisted=True,original_runtime_inventory_before_copy=runtime_before,original_runtime_inventory_after_copy=runtime_after,original_runtime_inventory_SHA256=digest(runtime_before),original_selected_runtime_business_paths_SHA256=business,original_selected_runtime_and_copy_stable=True)
  selection.update(pre_science_pool_elapsed_seconds=0,pre_science_pool_OS_roots=0,pre_science_pool_product_native_roots=0,local_initial_PASS_measured_inside_author_flow=True)
  if hasattr(env,'_science_lineage'):
   from resume_controller239 import CURRENT_STORE
   selection['scientific_lineage']=CURRENT_STORE.accounting();selection['scientific_lineage']['owned_OS_before_current_lease']=current.get('_scientific_lineage_OS_roots_before_lease',0)
   selection['scientific_lineage']['old_lineage_path']=env._science_lineage['_lineage_path'];selection['execution_lease_id']=current['execution_lease_id']
  save(selection_path,selection)
  env.record('EA21_ORIGINAL_COMPLETE_SELECTION_FROZEN_NO_PRIVATE',{'manifest_path':str(selection_path),'SHA256':sha(selection_path),'business_digest':selection['selected_sha256'],'selected_candidate_id':core['selected_candidate_id'],'private_calls':0,'original_flow_deadline_monotonic':parent_deadline})
  elapsed=time.monotonic()-env.started;changed=[n for n,h in inventory.items() if env._original.get(n)!=h]
  full={**copy.deepcopy(result),'task_id':env.task_id,'method':env.method,'status':'SELECTED_AWAIT_EXTERNAL_PRIVATE','success':None,'evaluation_status':'UNRUN_ROOT_FINAL','selection_manifest_path':str(selection_path),'selection_manifest_SHA256':sha(selection_path),'author_done':True,'private_calls_before_selection':0,'hidden_acceptance_calls':0,'final_hidden_known':False,'public_acceptance_known':False,'preservation_pass':None,'visible_pass':None,'public_regression_pass':None,'LLM_calls':env.calls,'output_tokens':env.out_tokens,'public_native_calls':env.native_calls,'product_native_roots_total':env._product_native_roots,'elapsed_seconds':elapsed,'scientific_phase_elapsed_seconds':elapsed,'independent_final_attempts':0,'changed_business_files':len(changed),'complete_actual_nonzero':False,'requires_once_private_external_to_actor':True,'original_flow_deadline_monotonic':parent_deadline}
  save(env.out/'selected_await_external_private.json',full);return full
 env.finalize=freeze
 return env

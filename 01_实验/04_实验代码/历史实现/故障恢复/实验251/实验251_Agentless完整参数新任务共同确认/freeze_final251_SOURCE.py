"""Freeze unchanged complete author selection; no private result is read."""
import argparse
from runtime251 import *

def freeze(path):
 c,out,*_=checked_contract(path);terminal_path=out/'PUBLIC_ONLY_NATURAL_TERMINAL.json';t=read(terminal_path);s=read(out/'STATUS.json')
 if s['status']!='PUBLIC_ONLY_NATURAL_TERMINAL' or t.get('error') is not None or not t['runtime_core']['complete']:raise RuntimeError('EXP251_NOT_A_COMPLETE_AUTHOR_TERMINAL')
 if t['selection'].get('uses_hidden') is not False or t.get('hidden_calls_in_adapter')!=0:raise RuntimeError('EXP251_PUBLIC_AUTHOR_SELECTION_ONLY')
 source_path=out/'SELECTED_BUSINESS_SOURCE.json';source=read(source_path);hashes={p:hashlib.sha256(v.encode()).hexdigest() for p,v in source.items()};snapshot=t['final_snapshot']
 if t['selection']['snapshot']!=snapshot:raise RuntimeError('EXP251_SELECTION_SNAPSHOT_DRIFT')
 completed=[]
 for p in sorted((out/'native_requests').glob('native*/COMPLETED_PUBLIC.json')):
  r=verify_parent_completed(p)
  if r.get('native_kind')=='G_O' and r['candidate_source_sha256']==hashes and r['candidate_snapshot']==snapshot:completed.append((p,r))
 evidence={'schema':'EXP251-frozen-complete-author-public-selection/1','UTC':now(),'method':METHOD,'task_id':c['task_id'],'trial_id':c['trial_id'],
  'terminal_status':t['status'],'candidate_snapshot':snapshot,'candidate_source_sha256':hashes,'public_terminal_path':str(terminal_path),'public_terminal_SHA256':sha(terminal_path),
  'business_source_file':str(source_path),'business_source_file_SHA256':sha(source_path),'method_contract_path':str(Path(path).resolve()),'method_contract_SHA256':sha(path),
  'science_T0_path':str(out/'SCIENCE_T0_TRIAL_PREPARATION_STARTED.json'),'science_T0_SHA256':sha(out/'SCIENCE_T0_TRIAL_PREPARATION_STARTED.json'),
  'author_selected_before_G_or_private_acceptance':True,'original_parameters_not_changed':True,'private_feedback_cannot_change_selection':True}
 final_dir=out/'frozen_final';frozen=final_dir/'FROZEN_PUBLIC_SELECTION.json'
 if frozen.exists():
  previous=read(frozen);evidence['UTC']=previous['UTC']
  if previous!=evidence:raise RuntimeError('EXP251_FROZEN_AUTHOR_SELECTION_CANNOT_CHANGE')
 else:save(frozen,evidence)
 actual=completed[-1] if completed else None
 if actual is not None:
  p,r=actual
  if sha(r['public_native_path'])!=r['public_native_SHA256']:raise RuntimeError('EXP251_SELECTED_NATIVE_RECORD_DRIFT')
  if r.get('ordinary_all_pass') is not True or r.get('failed_goals')!=0:actual=None
 if actual is None:
  if not completed and t['status']!='MODEL_SEMANTIC_FAILURE':raise RuntimeError('EXP251_SELECTED_PUBLIC_G_O_COMPLETION_UNKNOWN')
  save(final_dir/'PUBLIC_NATURAL_ENDPOINT.json',{**evidence,'natural_success':False,'public_G_O_all_pass':False,'normal_author_negative_result_preserved':True,'private_native_calls':0,'not_private_failure':True})
  return {'status':'COMPLETE_AUTHOR_PUBLIC_NATURAL_FAILURE_FROZEN','receipt':ref(final_dir/'PUBLIC_NATURAL_ENDPOINT.json')}
 completed_path,r=actual;parent=Path(r['parent_supervision_path']);public=read(c['public_contract']['path']);binding=next(v for v in read(E249/'TASK_BINDINGS249_SOURCE.json')['tasks'] if v['task_id']==c['task_id'])
 ready={**evidence,'schema':'EXP251-once-final-ready/1','attempt':r['attempt'],'frozen_selection_path':str(frozen),'frozen_selection_SHA256':sha(frozen),
  'public_completed_path':str(completed_path),'public_completed_SHA256':sha(completed_path),'public_supervision_path':str(parent),'public_supervision_SHA256':sha(parent),
  'public_contract':c['public_contract'],'public_test_scope_contract':c['public_test_scope_contract'],'goal_nodes':public['public_target_nodes'],'ordinary_nodes':public['ordinary_nodes'],
  'Root_only_task_manifest_path':binding['Root_only_original_isolation_manifest_path'],'native_output':str(HERE/'final_private_ROOT'/METHOD/c['task_id']/c['trial_id']),
  'once_private_required':True,'private_feedback_to_method':False}
 ready_path=final_dir/'FINAL_READY.json';save(ready_path,ready)
 g=read(completed_path.parent/'ROOT_PUBLIC_NATIVE_GRANT_FALSE.json')
 for k in ('native_kind','exact_G_O_nodes','product_dependency_paths','dependency_files_sha256','maximum_new_product_native'):g.pop(k,None)
 g.update(schema='EXP251-once-final-grant/1',root_authorized=False,native_authorized=False,private_authorized=False,once_private_authorized=False,model_authorized=False,finance_authorized=False,no_feedback_to_model=True,maximum_new_private_native=1,ready_SHA256=sha(ready_path),
  task_manifest_SHA256=None,original_private_nodes_SHA256=None,parent_owned_job_name='RootExp251_Final_'+c['task_id'].replace('-','_')+'_'+c['trial_id'],lease_end_UTC=None,root_stop_paths=[])
 false=final_dir/'ROOT_FINAL_NATIVE_GRANT_FALSE.json';save(false,g)
 return {'status':'COMPLETE_AUTHOR_SELECTION_FROZEN_FINAL_READY_FALSE','ready':ref(ready_path),'false_grant':ref(false),'actual_private_native':0}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--contract',required=True);a=p.parse_args();print(canonical(freeze(a.contract)))

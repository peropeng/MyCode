"""Bind one exact pending action, permissions remain entirely false."""
import argparse
from runtime251 import *

def prepare_model(slot):
 slot=Path(slot).resolve();ready_path=slot/'FIRST_UNPOST_READY.json';r=read(ready_path);body=read(slot/'FIRST_UNPOST_BODY.json')
 if not slot.is_relative_to(HERE/'runs'/METHOD) and not slot.is_relative_to(HERE/'source_previews'):raise RuntimeError('EXP251_FALSE_MODEL_SCOPE')
 c,out,*_=checked_contract(r['contract_path'])
 if r['method']!=METHOD or r['body_SHA256']!=digest(body) or sha(r['contract_path'])!=r['contract_SHA256'] or r['method_source_seal']!=c['method_source_seal']:raise RuntimeError('EXP251_FALSE_MODEL_BODY_CONTRACT')
 g={'schema':'EXP251-single-model-grant/1','root_authorized':False,'model_authorized':False,'finance_authorized':False,'native_authorized':False,'private_authorized':False,'maximum_new_requests':1}
 for k in ('method','task_id','trial_id','call_ordinal','finance_phase','body_SHA256','finance_configuration','contract_SHA256'):g[k]=copy.deepcopy(r[k])
 g.update(ready_SHA256=sha(ready_path),method_source_seal_SHA256=c['method_source_seal']['sha256'],lease_end_UTC=None,root_stop_paths=[],source_preview_never_POST=r.get('source_preview_only'))
 target=slot/'ROOT_EXACT_MODEL_GRANT_FALSE.json';save(target,g);return ref(target)
def prepare_native(ready_path):
 ready_path=Path(ready_path).resolve();r=read(ready_path)
 if not ready_path.is_relative_to(HERE/'runs'/METHOD) or r['method']!=METHOD or r['native_kind'] not in ('G_O','generated'):raise RuntimeError('EXP251_FALSE_NATIVE_SCOPE')
 c,*_=checked_contract(r['method_contract_path']);task=r['task_id'];policy=E249/'ROOT_RELEASES'/(task+('.current_C0.public_channel_v4.actual.json' if task=='dask__dask-9378' else '.current_C0.mask_v3.actual.json'));p=read(policy)
 controller=ROOT/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'
 g={'schema':'EXP251-single-native-grant/1','root_authorized':False,'native_authorized':False,'model_authorized':False,'private_authorized':False,'finance_authorized':False,'maximum_new_product_native':1,
  'method':METHOD,'task_id':task,'trial_id':r['trial_id'],'attempt':r['attempt'],'native_kind':r['native_kind'],'ready_SHA256':sha(ready_path),
  'candidate_source_inventory_SHA256':digest(r['candidate_source_sha256']),'native_source_seal':c['method_source_seal'],
  'qualified_runtime_policy':ref(policy),'current_identity_receipt':ref(E249/'qualification'/task/'identity/COMPLETED_IDENTITY249.json'),
  'exact_G_O_nodes':list(dict.fromkeys(r['goal_nodes']+r['ordinary_nodes'])),'lease_end_UTC':None,'root_stop_paths':[],
  'parent_owned_job_name':'RootExp251_Candidate_'+task.replace('-','_')+'_'+r['trial_id']+'_native'+str(r['attempt']),
  'controller_launch_python':str(controller),'controller_launch_SHA256':sha(controller),'product_dependency_paths':[],'dependency_files_sha256':{}}
 for k in ('current_process_clock_policy','common_precise_clock_contract','Root_current_process_precise_clock_admitted'):g[k]=copy.deepcopy(p.get(k))
 if r['native_kind']=='generated':g['generated_code_SHA256']=r['generated_code_SHA256']
 target=ready_path.parent/'ROOT_PUBLIC_NATIVE_GRANT_FALSE.json';save(target,g);return ref(target)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--model-ready-dir');p.add_argument('--native-ready');a=p.parse_args()
 if bool(a.model_ready_dir)==bool(a.native_ready):raise RuntimeError('EXP251_ONE_EXACT_FALSE_GRANT_KIND')
 print(canonical(prepare_model(a.model_ready_dir) if a.model_ready_dir else prepare_native(a.native_ready)))

"""Activate reviewed same-science repair only after explicit budget authorization."""
import shutil
from common import *
import trainer153 as training
def run():
 require_time(new_long_task=True)
 auth=read(E/'repair_authorization.json');failure=read(E/'runtime_failure_receipt.json');old=read(E/'protocol.json')
 if auth.get('authorized') is not True or auth.get('actual_stage_execution_cap',0)<270 or auth.get('scientific_plan_sha256')!=sha(E/'approved_plan.json'):
  raise RuntimeError('Explicit same-plan270 physical-stage budget authorization required')
 if (E/'training/all_models_sealed.json').exists() or (E/'results').exists():raise RuntimeError('Unexpected model/prediction seal before repair activation')
 check_hashes(old['protected_old_files_sha256']);check_hashes(old['initializations'])
 archived=E/'invalid_runtime_attempt_01';source=E/'training';staged=E/'restart_staged_training';destination=archived/'original_active_training'
 for path in (source,staged,destination):
  if not path.resolve().is_relative_to(E.resolve()):raise RuntimeError('Repair move outside owned experiment')
 if staged.exists() or destination.exists():raise RuntimeError('Repair activation paths already exist; no overwrite')
 staged.mkdir()
 for path,h in old['initializations'].items():
  initial=Path(path);target=staged/initial.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(initial,target)
  if sha(target)!=h:raise RuntimeError('Frozen initialization staging copy changed')
 # Native pathlib renames stay within the validated owned experiment; preserve
 # every failed artifact rather than deleting the previous active training tree.
 source.rename(destination);staged.rename(source)
 new={**old,'at_utc':now(),'runtime_backend_policy':training.EXPECTED_BACKEND,
  'training_sources':{path:sha(path) for path in old['training_sources']},
  'repair_attempt':{'original_protocol_sha256':sha(archived/'protocol.json'),'failure_receipt':str(E/'runtime_failure_receipt.json'),
   'failure_receipt_sha256':sha(E/'runtime_failure_receipt.json'),'authorization':str(E/'repair_authorization.json'),
   'authorization_sha256':sha(E/'repair_authorization.json'),'invalid_started_stage_executions':72,'invalid_completed_stage_executions':71,
   'physical_stage_execution_cap':270,'same_scientific_plan':True,'original_invalid_models_rejected':True,'fresh_fit_from_identical_frozen_initializations':True}}
 new['inputs']={**old['inputs'],str(E/'runtime_policy_repair_receipt.json'):sha(E/'runtime_policy_repair_receipt.json'),
  str(E/'runtime_failure_receipt.json'):sha(E/'runtime_failure_receipt.json'),str(E/'repair_authorization.json'):sha(E/'repair_authorization.json')}
 atomic(E/'protocol.json',new)
 status('REPAIRED_PROTOCOL_AND_INITIALIZATIONS_SEALED',completed_optimization_stages=0,optimizer_updates=0,final_models=0,new_ranker_outputs=0,
  valid_optimization_stages=0,all_completed_models_valid=True,invalid_previous_started_stages=72,invalid_previous_completed_stages=71,
  physical_stage_execution_cap=270,ETA_observation=None,next='launch153.py;198 fresh valid stages; report72 prior invalid started executions separately')
 print(canonical({'Exp153':'SAME_SCIENCE_RUNTIME_REPAIR_ACTIVATED','valid_stages':198,'prior_invalid_started_stages':72,'physical_cap':270,'runtime_policy':training.EXPECTED_BACKEND}),flush=True)
if __name__=='__main__':run()

"""Preserve invalid runtime attempt and exact costs; no model forward or labels."""
import shutil
import torch
from common import *
def run():
 p=read(E/'protocol.json');old=read(E/'checkpoint.json');archive=E/'invalid_runtime_attempt_01';code=archive/'code';code.mkdir(parents=True,exist_ok=True)
 for name in ('approved_plan.json','protocol.json','prepared_inputs.json','initialization_audit.json','checkpoint.json','execution_state.json','process_events.jsonl'):
  if (E/name).exists():shutil.copyfile(E/name,archive/name)
 old_trainer=(E/'trainer153.py').read_bytes().decode('utf-8')
 block="def backend_policy():\n return {'deterministic_algorithms':torch.are_deterministic_algorithms_enabled(),'cudnn_deterministic':torch.backends.cudnn.deterministic,\n  'cudnn_benchmark':torch.backends.cudnn.benchmark,'matmul_allow_tf32':torch.backends.cuda.matmul.allow_tf32,\n  'cudnn_allow_tf32':torch.backends.cudnn.allow_tf32,'num_threads':torch.get_num_threads()}\nEXPECTED_BACKEND={'deterministic_algorithms':True,'cudnn_deterministic':True,'cudnn_benchmark':False,'matmul_allow_tf32':False,'cudnn_allow_tf32':False,'num_threads':4}\n"
 old_trainer=old_trainer.replace(block,'').replace(" models.seed_all(row['initialization_seed'])\n if backend_policy()!=EXPECTED_BACKEND:raise RuntimeError('Frozen runtime backend policy not active')\n",'').replace("'runtime_backend_policy':backend_policy(),",'')
 (code/'trainer153.py').write_bytes(old_trainer.encode())
 old_predict=(E/'predict153.py').read_bytes().decode('utf-8').replace('from trainer153 import verify_protocol,predict,backend_policy,EXPECTED_BACKEND','from trainer153 import verify_protocol,predict').replace(" require_time(new_long_task=True);p=verify_protocol();models.seed_all(0)\n if backend_policy()!=EXPECTED_BACKEND:raise RuntimeError('Frozen inference backend policy not active')\n seal=read(E/'training/all_models_sealed.json')"," require_time(new_long_task=True);p=verify_protocol();seal=read(E/'training/all_models_sealed.json')")
 (code/'predict153.py').write_bytes(old_predict.encode())
 if sha(code/'trainer153.py')!=p['training_sources'][str(E/'trainer153.py')] or sha(code/'predict153.py')!=p['training_sources'][str(E/'predict153.py')]:raise RuntimeError('Invalid attempt original code reconstruction hash mismatch')
 for path,h in p['training_sources'].items():
  source=Path(path)
  if source.name in ('trainer153.py','predict153.py'):continue
  dest=code/source.relative_to(E);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
  if sha(dest)!=h:raise RuntimeError('Frozen original source backup mismatch')
 files={str(q):sha(q) for q in (E/'training').rglob('*') if q.is_file()};copied={}
 for path,h in files.items():
  dest=archive/'training'/Path(path).relative_to(E/'training')
  if sha(dest)!=h:raise RuntimeError('Invalid attempt training preservation mismatch')
  copied[str(dest)]=h
 stages=[read(q) for name in ('source_fit.json','selection.json','refit.json') for q in (E/'training').rglob(name)]
 complete=sum(r['updates'] for r in stages);finished={r['checkpoint'] for r in stages if r['stage'] in ('source_fit','refit')}
 folder=E/'training'/old['current_suite']/old['current_arm']/(str(old['current_seed']) if old['current_suite']=='source' else f"{old['current_seed']}_{old['current_outer']}")
 active=torch.load(folder/(old['current_stage']+'_resume.pt'),map_location='cpu',weights_only=False)
 active_updates=active['updates'];active_epoch=active['epoch'];bound=36 if old['current_stage']=='refit' else 31
 receipt={'at_utc':now(),'experiment':'Exp153','status':'INVALID_RUNTIME_ATTEMPT_PRESERVED_REPAIR_READY_RESTART_NOT_YET_AUTHORIZED',
  'reason':'Fresh training subprocess never called seed_all; restoring RNG alone did not restore deterministic backend policy. Initializer freeze had correct flags in a different exited process.',
  'observed_fresh_subprocess_defaults':read(E/'runtime_policy_repair_receipt.json')['before'],
  'all_prior_models_rejected_for_protocol_conformance':True,'target_rank_outputs':0,'target_evaluation_joins':0,
  'completed_invalid_optimization_stage_executions':len(stages),'partial_invalid_stage_executions':1,'total_invalid_started_stage_executions':len(stages)+1,
  'invalid_finished_fitted_models':len(finished),'completed_stage_optimizer_updates':complete,'active_completed_epoch_optimizer_updates':active_updates,
  'known_optimizer_update_lower_bound':complete+active_updates,'unrecorded_stopped_partial_epoch_updates_upper_bound':bound,'known_optimizer_update_upper_bound':complete+active_updates+bound,
  'active_stage':old['current_stage'],'active_saved_epoch':active_epoch,'frozen_plan_stage_cap':198,'needed_valid_rerun_stage_executions':198,
  'physical_stage_executions_if_full_repair_rerun':len(stages)+1+198,'valid_final_model_goal':108,'target_output_goal':69264,
  'same_scientific_plan_SHA256':sha(E/'approved_plan.json'),'original_protocol_SHA256':sha(archive/'protocol.json'),
  'original_frozen_code_verified':True,'training_backup_sha256':copied,'training_backed_up_files':len(copied),
  'backup_path':str(archive),'current_to_backup_prefix_map':{str(E/'training'):str(archive/'training')},
  'runtime_repair_receipt':str(E/'runtime_policy_repair_receipt.json'),'new_encoder_API_download_Gold_independent_tasks':0,'fee_CNY':'0',
  'next_required':'Plan owner must resolve explicit198 actual optimization-stage cap before restarting all fixed stages; no old invalid checkpoint resume/mix.'}
 atomic(E/'runtime_failure_receipt.json',receipt)
 status('RUNTIME_POLICY_ERROR_STOP',current_pid=None,current_command=None,all_completed_models_valid=False,valid_optimization_stages=0,
  invalid_completed_stages=len(stages),invalid_started_stages=len(stages)+1,invalid_finished_models=len(finished),
  optimizer_updates_lower_bound=receipt['known_optimizer_update_lower_bound'],optimizer_updates_upper_bound=receipt['known_optimizer_update_upper_bound'],
  runtime_failure_receipt=str(E/'runtime_failure_receipt.json'),recent_error=receipt['reason'],restart_compute_budget_required=receipt['physical_stage_executions_if_full_repair_rerun'],next=receipt['next_required'])
 print(canonical({k:v for k,v in receipt.items() if k!='training_backup_sha256'}),flush=True)
if __name__=='__main__':run()

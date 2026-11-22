"""Seal only the runner and static public inputs; templates all false.

Does not inspect or write the active trial; Root fills the concrete handoff
from a stopped boundary after finishing its manual actions.
"""
import ast
from runner251 import *

paths=list(HERE.glob('*.py'));sources={str(p):sha(p) for p in paths}
for p in paths:ast.parse(p.read_text('utf-8-sig'))
sources[str(IDENTITY)]=sha(IDENTITY)
sources[str(E249/'native249_ROOT_MASK_V3_CAPACITY.py')]=sha(E249/'native249_ROOT_MASK_V3_CAPACITY.py')
method_seal=METHOD_ROOT/'SOURCE_SEAL251_V2.json';method.verify_source_seal(method_seal)
inputs={str(method_seal):sha(method_seal),str(METHOD_ROOT/'protocol251_SOURCE.json'):sha(METHOD_ROOT/'protocol251_SOURCE.json')}
source_seal={'schema':'EXP251-independent-whole-trial-runner-source/2','UTC':now(),'sources_SHA256':sources,'inputs_SHA256':inputs,
 'does_not_replace_or_modify_method_core':True,'private_native_in_runner':0,'templates_all_false':True,'SOURCE_model_native_finance_or_existing_trial_writes':0}
seal_path=HERE/'RUNNER_SOURCE_SEAL251_R2.json';save(seal_path,source_seal)
identity_path=E249/'qualification/getmoto__moto-5072/identity/COMPLETED_IDENTITY249.json';physical=read(identity_path)['controller_self_identity']
template_rows=[]
for row in read(METHOD_ROOT/'FIRST_TWO_THREE_CONTRACTS251_SOURCE.json')['rows']:
 cpath=Path(row['contract']['path']);c=read(cpath);task=c['task_id'];trial=c['trial_id']
 runid='ROOT_TO_FILL_NEW_RUN_ID'
 g={'schema':'EXP251-whole-trial-Root-grant/1','method':c['method'],'task_id':task,'trial_id':trial,'runner_run_id':runid,
  'root_authorized':False,'whole_trial_execution_authorized':False,'preparation_authorized':False,'model_authorized':False,'finance_authorized':False,'native_authorized':False,
  'private_authorized':False,'once_private_authorized':False,'new_encoder_authorized':False,'new_download_authorized':False,
  'maximum_trial_model_requests':88,'maximum_trial_product_native':121,'maximum_new_controller_commands':1024,'maximum_final_private_native':0,
  'method_parameters_unchanged':True,'unknown_or_inflight_never_resent':True,'source_or_response_reuse_across_trials':False,
  'trial_contract':ref(cpath),'method_source_seal':c['method_source_seal'],'runner_source_seal':ref(seal_path),'finance_configuration':c['finance_configuration'],'finance_phase':c['finance_phase'],
  'Root_handoff_boundary':None,'lease_end_UTC':None,'hard_stop_paths':[],'safe_boundary_stop_paths':[],
  'controller_launch_python':str(CONTROLLER),'controller_launch_SHA256':sha(CONTROLLER),
  'qualified_controller_physical_identity':{'actual_OS_image':physical['actual_OS_image'],'actual_OS_image_SHA256':physical['actual_OS_image_SHA256']},
  'parent_owned_job_name':'RootExp251_WholeTrial_'+task.replace('-','_')+'_'+trial+'_'+runid,
  'closed_template_cannot_start_or_resume_existing_trial':True,'Root_must_explicitly_release_exact_stopped_handoff':True}
 fp=HERE/'false_grants'/task/(trial+'.WHOLE_TRIAL_FALSE.json');save(fp,g)
 handoff={'schema':'EXP251-exact-known-safe-handoff/1','method':c['method'],'task_id':task,'trial_id':trial,'contract_SHA256':sha(cpath),
  'Root_safe_boundary_accepted':False,'no_active_previous_model_or_native_owner':False,'current_method_STATUS':None,'original_trial_T0':None,
  'complete_settled_same_trial_model_prefix':None,'complete_STOP_same_trial_native_prefix':None,'prior_runner_parent_STOP':None,
  'Root_only_fills_from_actual_immutable_same_trial_witnesses':True,'existing_seed_T0_messages_costs_and_counts_preserved':True}
 hp=HERE/'false_grants'/task/(trial+'.HANDOFF_FALSE.json');save(hp,handoff)
 capture={'schema':'EXP251-public-stopped-edge-capture-Root-grant/1','method':c['method'],'task_id':task,'trial_id':trial,
  'root_authorized':False,'public_handoff_capture_authorized':False,'Root_previous_manual_or_runner_owner_stopped':False,
  'model_authorized':False,'native_authorized':False,'private_authorized':False,'finance_authorized':False,'encoder_authorized':False,
  'trial_contract':ref(cpath),'exact_status_before_capture':None,'prior_runner_parent_STOP':None,
  'output_handoff_path':str(HERE/'ROOT_RELEASES'/(task+'_'+trial+'.HANDOFF_ACTUAL_ROOT.json')),'lease_end_UTC':None}
 cp=HERE/'false_grants'/task/(trial+'.HANDOFF_CAPTURE_FALSE.json');save(cp,capture)
 template_rows.append({'task_id':task,'trial_id':trial,'false_grant':ref(fp),'false_handoff':ref(hp),
  'Root_readonly_capture_false':ref(cp),
  'actual_argv':[str(CONTROLLER),'-X','utf8','-B',str(HERE/'runner251.py'),'--root-trial-grant','<Root actual exact whole-trial grant>']})
save(HERE/'RUNNER_DELIVERY251_SOURCE.json',{'schema':'EXP251-independent-runner-source-delivery/1','runner_source_seal':ref(seal_path),'unchanged_method_source_seal':ref(method_seal),'rows':template_rows,
 'runner_version':'R2','outer_active_process_cap':16,'controller_active_process_cap':16,'original_product_native_supervisor_active_total_caps':[8,24],
 'trusted_worker_inherits_existing_key':True,'only_exact_dispatch_controller_inherits_key':True,'controller_environments_never_recorded':True,
 'maximum_trial_model_stages':88,'maximum_product_native':121,'API_budget_full_peak_old_continuous_ledger_unchanged':True,
 'existing_settled_prefix_only_consumed_no_rePOST':True,'same_trial_conditional_continuation_not_new_independent_repeat':True,
 'all_unknown_or_inflight_closed_no_retry':True,'safe_stop_at_command_boundary_hard_stop_at_guard_or_lease':True,'complete_public_final_frozen_then_exit_private0':True,
 'actual_model_POST_product_native_encoder_private_ledger_or_active_trial_writes':0})
print(canonical({'status':'INDEPENDENT_WHOLE_TRIAL_RUNNER_SOURCE_FALSE','runner_source_seal_SHA256':sha(seal_path),'templates':len(template_rows),'actual_operations':0}))

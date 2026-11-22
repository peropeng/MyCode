"""Freeze public final sources and closed once-private pointers; never private IO."""
import argparse
from decimal import Decimal
from final_common262 import *

def main():
 p=argparse.ArgumentParser();p.add_argument('--trial',default='trial1',choices=('trial1','trial2','trial3'));a=p.parse_args();trial=a.trial
 base=H/'runs/getmoto__moto-7081'/trial;prepared=[];public_inputs={};ready_values=[]
 audit=read(R/'工作区/1012-astra-v2/progress-source-audit/MOTO7081_PARTIAL_STATE_SOURCE_AUDIT.json')
 manifest_ref=next({'path':v['path'],'sha256':v['sha256']} for v in audit['source_assets'] if Path(v['path']).name=='task_manifest.json')
 identity=R/'工作区/1012-exp249-prospective-confirmation/实验/实验249_固定顺序新任务共同确认/next_six_qualification_SOURCE/qualification/getmoto__moto-7081/identity/COMPLETED_IDENTITY249.json'
 for policy in ['SET','COUNT','O_ONLY']:
  out=base/policy;terminal_path=out/'PUBLIC_ONLY_NATURAL_TERMINAL.json';terminal=read(terminal_path);parent_path=out/'Root_owner600/PARENT_TERMINAL262.json';parent=read(parent_path)
  assert terminal['status']=='COMPLETED' and terminal.get('error') is None and parent['exit_code']==0 and parent['error'] is None
  assert parent['stop_receipt']['all_owned_descendants_terminated'] and parent['stop_receipt']['job_active_processes_after_termination']==0
  source_path=out/'SELECTED_BUSINESS_SOURCE.json';source=read(source_path);hashes={p:hashlib.sha256(t.encode()).hexdigest() for p,t in source.items()};cpath=H/'contracts'/trial/(policy+'.json');c=read(cpath)
  assert len(hashes)==861 and set(hashes)==set(read(H/'PARTIAL_BUSINESS_STATE.json')['business_SHA256'])
  publics=[p for p in (out/'native_public').glob('*/ROOT_COMPLETED_PUBLIC.json') if read(p)['candidate_source_inventory_SHA256']==digest(hashes)]
  assert len(publics)==1;public_path=publics[0];public=read(public_path);native=checked({'path':public['public_native_path'],'sha256':public['public_native_SHA256']});nodes=c['goal_nodes']+c['ordinary_nodes']
  assert native['passed'] and native['completed_guarded_coverage'] and native['requested_nodes']==nodes and all(native['pytest']['outcomes'][n]['status']=='passed' for n in nodes)
  checked(public['parent_stop_ref']);responses=[];cost=Decimal(0);calls=0
  for response_path in sorted((out/'calls').glob('call*/SETTLED_RAW_RESPONSE.json')):
   response=read(response_path);receipt=response['_finance_receipt'];assert receipt['status']=='SETTLED';cost+=Decimal(receipt['usage_accounting_upper_CNY']);calls+=1;responses.append(ref(response_path))
  frozen=out/'FINAL_SELECTED_SOURCE_FROZEN262.json'
  if not frozen.exists():intent(frozen,{'schema':'EXP262-immutable-selected-public-source-before-private/1','task_id':c['task_id'],'trial_id':trial,'policy':policy,'selected_snapshot':terminal['final_snapshot'],'candidate_source_sha256':hashes,'candidate_source_inventory_SHA256':digest(hashes),'selected_business_source':ref(source_path),'terminal':ref(terminal_path),'public_GO_completed':ref(public_path),'parent_real_STOP':ref(parent_path),'generation_SETTLED_responses':responses,'current_public_goal_PASS':nodes[:3],'current_ordinary_PASS':True,'selected_before_any_private':True,'no_private_feedback_to_later_repeats':True})
  selection=read(frozen);assert selection['candidate_source_sha256']==hashes and selection['selected_snapshot']==terminal['final_snapshot']
  ready={'schema':'EXP262-once-independent-Root-final-ready/1','SOURCE_ONLY':True,'root_authorized':False,'native_authorized':False,'private_authorized':False,'model_authorized':False,'finance_authorized':False,'task_id':c['task_id'],'trial_id':trial,'policy':policy,'method':'OURS248_FULL_PRESSURE_'+policy,'attempt':int(terminal['final_snapshot']['id'].removeprefix('attempt')),'candidate_source_inventory_SHA256':digest(hashes),'selected_business_source':ref(source_path),'frozen_selection':ref(frozen),'public_terminal':ref(terminal_path),'public_completed':ref(public_path),'public_parent_stop':ref(parent_path),'science_T0':ref(out/'SCIENCE_T0_TRIAL_PREPARATION_STARTED.json'),'method_contract':ref(cpath),'current_pressure_public_contract':ref(H/'PRESSURE_PUBLIC_CONTRACT262.json'),'current_public_scope':ref(H/'CURRENT_SCOPE262.json'),'Root_current_qualified_partial_start':ref(H/'qualification/once_original_G_O/CURRENT_PARTIAL_START262.json'),'Root_qualified_runtime_acceptance':ref(H/'ROOT_CURRENT_NATIVE_READONLY_ACCEPTANCE262.json'),'original_product_identity':ref(identity),'Root_only_original_isolation_manifest':manifest_ref,'native_output':str(H/'final_private_ROOT'/trial/policy),'original_selected_source_and_all4_public_PASS_before_final':True,'public_model_calls':calls,'public_usage_upper_CNY':str(cost),'maximum_new_private_native':1,'original_private_probe_not_executed_by_preparation':True,'private_metadata_selectors_or_body_not_opened_by_this_script':True,'original_native_timeout_seconds':300,'no_model_finance_or_feedback_authority':True}
  ready_values.append((out/'independent_final_READY262/ROOT_INDEPENDENT_FINAL_READY_FALSE.json',ready));prepared.append({'policy':policy,'public_go4_PASS':True,'model_calls':calls,'usage_upper_CNY':str(cost),'source_digest':digest(hashes),'public_parent_STOP':True})
  for value in ready.values():
   if isinstance(value,dict) and set(value)=={'path','sha256'}:public_inputs[value['path']]=value['sha256']
 native=read(H/'NATIVE_READY262_FALSE.json');deps={v['path']:v['sha256'] for v in native['source_assets'].values()}
 for pp in [CONTROLLER,OLD/'native_executor242_prospective.py',OLD/'native_capacity_v10.py',COMMON/'native_four_slots_v5_SOURCE.py',COMMON/'ROOT_COMMON_NATIVE_SCHEDULING_V5_FOUR_SOURCE.json',R/'工作区/1012-exp249-prospective-confirmation/实验/实验249_固定顺序新任务共同确认/native249_ROOT_MASK_V3_CAPACITY.py']:
  deps[str(pp)]=sha(pp)
 seal={'schema':'EXP262-Root-only-once-independent-final-source-seal/1','SOURCE_ONLY':True,'sources':{str(pp):sha(pp) for pp in SOURCE.glob('*.py')},'dependencies':deps,'public_inputs_SHA256':public_inputs,'original_probe_held_jobs_native300_identity_core_preserved':True,'namespace_E_current_output_identity_source_explicit_SOURCE':True,'private_selectors_only_true_granted_worker_reads':True,'preparation_native_private_model_finance_calls':0}
 sealpath=SOURCE/('SOURCE_SEAL262_FINAL_'+trial+'_FALSE.json')
 assert not sealpath.exists();intent(sealpath,seal)
 for ready_path,ready in ready_values:
  ready['final_source_seal']=ref(sealpath);intent(ready_path,ready)
  grant_path=ready_path.parent/'ROOT_INDEPENDENT_FINAL_GRANT_TEMPLATE_FALSE.json'
  grant={'schema':'Root-EXP262-once-independent-private-final/1','root_authorized':False,'native_authorized':False,'private_authorized':False,'once_private_authorized':False,'no_feedback_to_model':False,'model_authorized':False,'finance_authorized':False,'maximum_new_private_native':1,'task_id':ready['task_id'],'trial_id':trial,'policy':ready['policy'],'ready':ref(ready_path),'candidate_source_inventory_SHA256':ready['candidate_source_inventory_SHA256'],'native_source_seal':ref(sealpath),'current_identity_receipt':ready['original_product_identity'],'qualified_runtime_policy':ready['Root_qualified_runtime_acceptance'],'original_private_manifest':manifest_ref,'original_private_nodes_SHA256':None,'current_process_clock_policy':'ROOT_ORIGINAL_CLOCK_EXPLICITLY_ADMITTED','parent_owned_job_name':None,'controller_launch_python':str(CONTROLLER),'controller_launch_SHA256':sha(CONTROLLER),'lease_end_UTC':'2026-10-12T23:29:05+08:00','root_stop_paths':[],'native_timeout_seconds':300,'source_worker':ref(SOURCE/'final262_ROOT_ONLY.py')}
  intent(grant_path,grant)
 print(canonical({'SOURCE_ONLY':True,'trial':trial,'final_source_seal':ref(sealpath),'prepared':prepared,'ready_paths':[str(p) for p,_ in ready_values],'private_native_model_finance':0}))
if __name__=='__main__':main()

"""Read-only verification of existing pilot observations; no model or native."""
from common166 import *
import copy,re
from decimal import Decimal
def main():
 seal=read(E/'runtime_seal224.json');supervision=read(E/'supervision.json');rows=[];scan=[]
 methods=('AGENTLESS_FSE2025_4L4P4T_FLASH','G_PROGRESSIVE_SEMANTIC_FLASH')
 # Scan only messages/tool schemas actually supplied to the model, not finance role.
 needles=(E.parents[1].name,E.name,*methods,'OURS_G153_PROGRESSIVE_SEMANTIC')
 for tid in read(E/'protocol224.json')['pilot_ids']:
  for method in methods:
   flow=E/'recovery'/tid/method;result=read(flow/'result.json');ledger=lines(flow/'stage_ledger.jsonl')
   receipts=[read(p) for p in flow.glob('llm/*_finance_receipt.json')];settled=[r for r in receipts if r['status']=='SETTLED']
   assert Decimal(result['fees_CNY'])==sum((Decimal(r['usage_peak_cost_CNY']) for r in settled),Decimal(0))
   for path in sorted(flow.glob('llm/*_request.json')):
    body=read(path)['body'];text=canonical({'messages':body['messages'],'tools':body.get('tools',[])})
    hits=[]
    for needle in needles:
     if needle in text:
      index=text.index(needle);hits.append({'needle':needle,'context':text[max(0,index-120):index+len(needle)+120]})
    scan.append({'request':str(path),'request_sha256':sha(path),'body_sha256':digest(body),'case':tid,'method':method,'path_or_arm_needle_hits':hits})
   errors=[r for r in ledger if r['stage']=='failure']
   if method==methods[0]:
    end=datetime.datetime.fromisoformat(result['at_utc']);approx_start=end-datetime.timedelta(seconds=result['elapsed_seconds']);expired=approx_start+datetime.timedelta(seconds=900)<datetime.datetime.now(datetime.timezone.utc)
    rows.append({'task_id':tid,'method':method,'raw_result':str(flow/'result.json'),'raw_result_sha256':sha(flow/'result.json'),'success':result['success'],'complete_core':False,'first_actual_error_utc':errors[0]['at_utc'] if errors else None,'error':result['error'],'original_elapsed_seconds_until_censored_result':result['elapsed_seconds'],'original_start_utc_derived_from_at_minus_elapsed':approx_start.isoformat(),'original900s_deadline':(approx_start+datetime.timedelta(seconds=900)).isoformat(),'original900s_already_expired':expired,'fees_CNY':result['fees_CNY'],'private_calls_even_though_core_unknown':result['hidden_acceptance_calls'],'cannot_restart_wall_clock_and_call_it_same_flow':True})
    continue
   assert result['success'] is True and result['runtime_core']['complete'] and result['public_acceptance_known'] and result['final_hidden_known'] and result['visible_pass'] and result['public_regression_pass'] and result['preservation_pass']
   assert result['changed_business_files']>0 and result['final_legal_edit_check']['legal'] and result['elapsed_seconds']<=900 and result['hidden_acceptance_calls']==1
   native=[]
   for p in sorted(flow.glob('public_native/*/run.json'))+[flow/'final_preservation/run.json']:
    v=read(p);assert v.get('executed') and v.get('guard_loaded') and v.get('business_state_unchanged') and v.get('frozen_tests_unchanged') and not v.get('timeout')
    native.append({'path':str(p),'sha256':sha(p),'executed':v['executed'],'guard_loaded':v['guard_loaded'],'exact_coverage':v.get('exact_test_coverage'),'passed':v.get('passed'),'requested_nodes':v.get('requested_nodes'),'frozen_and_business_unchanged':True,'actual_product_import':v.get('pytest',{}).get('product_import'),'exit_code':v.get('exit_code'),'process_birth':v.get('process_birth'),'per_native_PID_birth_recorded':bool(v.get('process_birth'))})
   audit={'schema':'Exp224-existing-OURS-composite-result-readonly-audit/1','at_utc':now(),'task_id':tid,'raw_result':str(flow/'result.json'),'raw_result_sha256':sha(flow/'result.json'),'status':'PASS_EXISTING_COMPLETE_COMPOSITE_SUCCESS','success':True,'complete_core':True,'core':result['runtime_core'],'initial_C0_sha256':result['initial_snapshot']['inventory_sha256'],'selected_final_sha256':result['selected']['snapshot']['inventory_sha256'],'selected_before_hidden':result['selected']['selected_before_hidden'],'goal_pass':True,'ordinary_pass':True,'private_preservation_pass':True,'once_final_private':1,'legal_business_change':result['final_legal_edit_check'],'changed_business_files':result['changed_business_files'],'elapsed_seconds':result['elapsed_seconds'],'within900':True,'actual_model_calls':result['LLM_calls'],'paid_calls':len(settled),'usage_peak_upper_cost_CNY':result['fees_CNY'],'receipt_files':[{'path':str(p),'sha256':sha(p)} for p in flow.glob('llm/*_finance_receipt.json')],'native':native,'supervised_runner_birth':supervision['runner_creation_time100ns'],'supervised_runner_pid':supervision['runner_pid'],'runner_suspended_before_job_assignment':supervision['suspended_until_assigned_to_job'],'job_closed_all_owned_descendants_terminated':supervision['job_closed_all_owned_descendants_terminated'],'native_birth_limit':'Original native helper records synchronous return, guard and protected hashes but no individual native PID/birth. Job inheritance/close contains/stops descendants; no retrospective per-native birth proof is claimed.','runtime_source_input_seal':str(E/'runtime_seal224.json'),'runtime_source_input_seal_sha256':sha(E/'runtime_seal224.json'),'read_only_no_new_native_API_or_Gold':True}
   save(flow/'audited_result224.json',audit);rows.append({'task_id':tid,'method':method,'audited_result':str(flow/'audited_result224.json'),'success':True,'complete_core':True,'fees_CNY':result['fees_CNY'],'native_birth_individual_unknown':True})
 findings=[r for r in scan if r['path_or_arm_needle_hits']]
 save(E/'audit224/llm_public_path_scan224.json',{'at_utc':now(),'scope':'Saved original request body messages and tools, not transport role metadata','requests_scanned':len(scan),'requests_with_path_or_arm_needle':len(findings),'rows':scan,'raw_requests_never_modified':True,'known_limited_needles':needles,'not_a_claim_of_exhaustive_ANSI_or_CJK_path_neutralization':True})
 save(E/'audit224/pilot_evidence224.json',{'at_utc':now(),'rows':rows,'stage_total_fee_CNY':str(sum((Decimal(r['fees_CNY']) for r in rows),Decimal(0))),'scan_requests':len(scan),'scan_needle_hits':len(findings),'original_invalid_reader_first_error_utc':'2026-10-08T16:14:52.834234+00:00','reader_patch_completed_clock_observation_utc':'2026-10-08T16:20:40+00:00','repair_from_first_actual_error_seconds':347.165766,'repair_window5min_overrun_seconds':47.165766,'original_UNKNOWN_retained':True,'new_POST_native_private_or_finance':0,'remaining_Pilot_CNY_parent_latest':'0.049','next_2238_required_related_elements_output_reserve_alone_CNY':'0.065536','next5093_patch_output_reserve_alone_CNY':'0.131072','no_further_AL_POST_admissible_under_remaining_pilot':True,'fresh_main_requires_explicit_new_namespace_version_and_budget_not_fake_same_flow_continuation':True})
 print(canonical({'rows':rows,'scan_requests':len(scan),'scan_path_or_arm_hits':len(findings)}))
if __name__=='__main__':main()

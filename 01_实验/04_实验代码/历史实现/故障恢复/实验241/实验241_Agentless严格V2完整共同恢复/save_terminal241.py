"""Archive actual closed two-case evidence. No model/native/private/ledger writes."""
import datetime,importlib.util
from decimal import Decimal
from contracts241 import *

TASKS=['Project-MONAI__MONAI-2238','Project-MONAI__MONAI-5093']
def main():
 reader=module('terminal_shared_reader241',ROOT/'工作区/1008-2320-baseline-main/read_finance_sharedelete_root.py')
 ledger=reader.read_shared();paid=[r for r in ledger['reservations'] if r.get('pilot')==FINANCE_PHASE]
 if len(paid)!=32 or any(r['status']!='SETTLED' for r in paid):raise EngineeringUnknown('PILOT_FINANCE_NOT_EXACT32_SETTLED')
 rows=[];recovery=[]
 for task in TASKS:
  flow=HERE/'runs'/task/METHOD;supervision=HERE/'supervision'/task
  actor=read(flow/'result.json');selected=read(flow/'immutable_selection.json');external=read(flow/'external_once_private/result.json')
  author_stop=read(supervision/'parent_stop_receipt.json');external_stop=read(supervision/'external_parent_stop_receipt.json')
  for stop in [author_stop,external_stop]:
   if stop['exit_code']!=0 or stop['timeout'] or not all(stop['stop_receipt'].get(k) for k in ('root_stopped','own_Job_empty_before_close','descendants_stopped')):
    raise EngineeringUnknown('CLOSED_AUTHOR_OR_EXTERNAL_STOP_NOT_VERIFIED')
  if not actor['runtime_core']['complete'] or external['status']!='COMPLETE_EXTERNAL_ONCE_PRIVATE' or external['private_attempts']!=1:
   raise EngineeringUnknown('EXACT_WHOLE_CORE_AND_ONCE_PRIVATE_REQUIRED')
  if sha(flow/'immutable_selection.json')!=external['selection_manifest_sha256'] or inventory(selected['selection_root'])!=selected['business_paths_sha256']:
   raise EngineeringUnknown('SELECTED_PATCH_CHANGED_AFTER_PRIVATE')
  events=[__import__('json').loads(x) for x in (supervision/'events.jsonl').read_text('utf-8').splitlines() if x.strip()]
  birth=author_stop['births'][0]['creation_time100ns']/10000000-11644473600
  final_stop=max(datetime.datetime.fromisoformat(e['at_utc']).timestamp() for e in events if e.get('event')=='SUPERVISION_FINALLY_STOP')
  elapsed=final_stop-birth
  if elapsed>900 or not all(external.get(k) for k in ('public_passed','ordinary_passed','private_passed')):
   raise EngineeringUnknown('FINAL_COMPOSITE_SUCCESS_NOT_WITHIN_ORIGINAL900')
  model_rows=[r for r in paid if task in r['role']]
  if len(model_rows)!=16:raise EngineeringUnknown('EXACT16_AUTHOR_RESPONSES_NOT_SETTLED')
  phase_fee=sum((Decimal(r['usage_accounting_upper_CNY']) for r in model_rows),Decimal(0))
  source_seal=read(HERE/'candidate'/task/'source_seal.json')
  for path,h in {**source_seal['sources'],**source_seal['inputs']}.items():
   if sha(path)!=h:raise EngineeringUnknown('FINAL_SOURCE_INPUT_DRIFT '+path)
  stage=[__import__('json').loads(x) for x in (flow/'stage_ledger.jsonl').read_text('utf-8').splitlines() if x.strip()]
  regression=next(e['evidence'] for e in stage if e['stage']=='ordinary_regression_selection')
  responses=[e['evidence'] for e in stage if e['stage']=='ACTUAL_FLASH_RESPONSE']
  row={'task_id':task,'scientific_status':'COMPLETE_EXTERNAL_ONCE_PRIVATE','success':True,'historically_exposed_task':True,
   'author_core':actor['runtime_core'],'actual_paid_responses':len(responses),'output_tokens':actor['output_tokens'],
   'output_truncated_responses':sum(r['finish_reason']=='length' for r in responses),'actual_fee_accounting_upper_CNY':str(phase_fee),
   'public_passed':True,'ordinary_passed':True,'private_passed':True,'private_attempts':1,'actor_received_private_feedback':False,
   'product_native_roots':external['product_native_roots'],'all_OS_native_roots':external['all_OS_native_roots'],
   'native_root_kinds':external['native_root_kinds'],'original900_elapsed_to_final_STOP_seconds':elapsed,
   'author_seconds':author_stop['seconds'],'external_evaluator_seconds':external_stop['seconds'],
   'selected_sample':selected['author_original_selection']['reason']['selected_sample'],
   'selected_business_sha256':selected['selected_sha256'],'selected_manifest_sha256':sha(flow/'immutable_selection.json'),
   'source_seal_canonical_sha256':digest(source_seal),'source_seal_rawfile_sha256':sha(HERE/'candidate'/task/'source_seal.json'),
   'original_ordinary_passing_nodes':regression['original_passing_tests'],'original_selector_excluded':regression['LLM_excluded'],
   'original_retained_regression_nodes':regression['retained_regression'],
   'empty_selected_regression_set_not_filled_from_private':not regression['retained_regression'],
   'no_verified_reproduction_original_fallback':selected['author_original_selection']['reason']['no_verified_reproduction_fallback'],
   'author_parent_stop':str(supervision/'parent_stop_receipt.json'),'external_parent_stop':str(supervision/'external_parent_stop_receipt.json'),
   'raw_author_result':str(flow/'result.json'),'raw_once_private_result':str(flow/'external_once_private/result.json'),
   'raw_requests_responses':str(flow/'llm'),'immutable_selected_business':selected['selection_root'],
   'full_raw_and_original_branch_results_preserved':True,'all_started_jobs_root_and_descendants_STOP':True}
  rows.append(row)
  cpath=HERE/'candidate'/task/'public_contract.json';c=read(cpath)
  # Final runtime has the selected patch. Preserve that exact unique state as
  # an overlay; only the reconstructible template clone is later disposable.
  runtime=flow/'runtime/tree/repo';runtime_inv=inventory(runtime)
  expected=dict(c['template_inventory']);expected.update(selected['business_paths_sha256'])
  if runtime_inv!=expected:raise EngineeringUnknown('RUNTIME_NOT_EXACT_SELECTED_OVER_TEMPLATE')
  recovery.append({'destination':str(runtime),'source_template':c['template'],'public_contract':str(cpath),
   'template_inventory_field':'template_inventory','selected_business_overlay':selected['selection_root'],
   'selected_inventory':selected['business_paths_sha256'],'expected_inventory_sha256':digest(expected),
   'original_unique_selected_and_snapshots_retained':True,'parent_stop':str(supervision/'parent_stop_receipt.json'),
   'all_owned_jobs_STOP':True,'bytes':sum(p.stat().st_size for p in runtime.rglob('*') if p.is_file()),'deleted':False})
  external_runtime=flow/'external_once_private/runtime/repo'
  if inventory(external_runtime)!=expected:raise EngineeringUnknown('EXTERNAL_RUNTIME_DRIFT')
  recovery.append({**recovery[-1],'destination':str(external_runtime),'parent_stop':str(supervision/'external_parent_stop_receipt.json'),
   'bytes':sum(p.stat().st_size for p in external_runtime.rglob('*') if p.is_file())})
 save(HERE/'RECOVERY_INDEX241.json',{'schema':'Agentless241-runtime-recovery/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'clones':recovery,'restore':'Recreate template from public_contract.template_inventory then overlay immutable_selection business bytes; verify expected digest. Never reopen closed experiment clocks or resend model requests.',
  'mechanical_recovery':str(HERE/'MECHANICAL_RECOVERY241.json'),'keep_all_original_raw_responses_selected_patches_snapshots_tests_and_receipts':True})
 save(HERE/'TERMINAL_SUMMARY241.json',{'schema':'Agentless241-two-case-complete-pilot/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'experiment':241,'version':'STRICT224_V2_AUTHOR_DIRECT_PUBLICPACK_NEW_DEPLOYMENT241','cases':rows,
  'counts':{'complete':2,'success':2,'normal_failure':0,'unknown_scientific':0,'unrun_in_pilot':0},
  'engineering_preparation_failures_separately_retained':3,'science_reruns':0,'post_retries':0,
  'coordination_interruption':'Root requested read-only reconciliation at16:42Z; cause not specified. Existing first run was already complete; no process/request restart. Second run only started after root continuation.',
  'phase_spent_CNY':ledger['pilots'][FINANCE_PHASE]['spent_CNY'],'phase_held_CNY':ledger['pilots'][FINANCE_PHASE]['held_CNY'],
  'phase_settled_records':len(paid),'continuous_ledger_spent_CNY':ledger['spent_CNY'],'continuous_held_CNY':ledger['held_CNY'],
  'continuous_record_count':len(ledger['reservations']),'old973_not_reset':digest(ledger['reservations'][:973])==read(HERE/'finance_config241.json')['old_reservations_sha256'],
  'original_author_core_SHA256':rows and read(HERE/'AUTHOR_SOURCE_MANIFEST241.json')['method_sha256'],
  'no_core_prompt_parser_vote_normalization_change':True,'no_added_reader_self_loop':True,
  'scientific_nonzero_full_method_qualified':True,'paired_comparative_advantage_established':False,'not_merged_into_old_Main21':True,
  'pilot_boundary_STOP_no_automatic_main':True,'recovery_index':str(HERE/'RECOVERY_INDEX241.json'),'audit_ledger_writes':0})
 print(canonical({'complete':2,'success':2,'normal_failure':0,'unknown_scientific':0,'unrun_pilot':0,
  'total_fees_CNY':ledger['pilots'][FINANCE_PHASE]['spent_CNY'],'all_owned_jobs_STOP':True,
  'original900_elapsed_seconds':{r['task_id']:r['original900_elapsed_to_final_STOP_seconds'] for r in rows},
  'summary':str(HERE/'TERMINAL_SUMMARY241.json')}))
if __name__=='__main__':main()

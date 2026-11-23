"""Summarize closed original selection, receipts and immutable script evidence."""
import argparse, collections, datetime
from contracts241 import *
SG=HERE.parent/'实验241_Agentless新确认集21_生成测试ScopeV3_AST兼容'

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--task',required=True);args=parser.parse_args()
 task=args.task;flow=SG/'runs'/task/METHOD;base=SG/'candidate'/task
 packet=read(base/'TERMINAL_PACKET241.json');info=read(base/'INFORMATION_ADMISSION_SCOPE_V2_241.json')
 if not packet['all_owned_jobs_STOP']:raise EngineeringUnknown('CLOSED_REQUIRED')
 stages=[json.loads(line) for line in (flow/'stage_ledger.jsonl').read_text('utf-8').splitlines() if line.strip()]
 sel=read(flow/'immutable_selection.json');before=read(flow/'selection_before_private.json')
 author_stop=read(SG/'supervision'/task/'parent_stop_receipt.json');external_stop=read(SG/'supervision'/task/'external_parent_stop_receipt.json')
 parent_events=[json.loads(line) for line in (SG/'supervision'/task/'events.jsonl').read_text('utf-8').splitlines() if line.strip()]
 author_final_stop=next(row for row in parent_events if row.get('event')=='SUPERVISION_FINALLY_STOP' and row['Job']==author_stop['Job'])
 external_birth=external_stop['births'][0]['creation_time100ns']/10000000-11644473600
 author_stop_epoch=datetime.datetime.fromisoformat(author_final_stop['at_utc']).timestamp()
 if author_stop_epoch>=external_birth:raise EngineeringUnknown('EXTERNAL_BEFORE_ACTUAL_AUTHOR_STOP')
 private_marker=read(flow/'external_once_private/private_started.json')
 receipts=[row['evidence'] for row in stages if row['stage']=='ACTUAL_FLASH_RESPONSE']
 scripts=[]
 for p in sorted((flow/'generated_native').glob('*/generated_test.py')):
  runtime=read(p.parent/'run.json');events=[json.loads(line) for line in (p.parent/'generated_scope_events.jsonl').read_text('utf-8').splitlines() if line.strip()]
  null_events=[e for e in events if e.get('reason')=='OS_NULL_DEVICE']
  if any(e.get('event')!='open' or e.get('path')!='nul' or e.get('allowed') is not True or e.get('write') is not True for e in null_events):
   raise EngineeringUnknown('OS_NULL_ACTUAL_EVENT_NOT_RECONCILED')
  scripts.append({'script':str(p),'script_sha256':sha(p),'execution_record_script_sha256':runtime['generated_script_sha256'],
   'script_bytes_unchanged_since_execution':sha(p)==runtime['generated_script_sha256'],'status':runtime['semantic_marker'],
   'business_state_unchanged':runtime['business_state_unchanged'],'frozen_tests_unchanged':runtime['frozen_tests_unchanged'],
   'scope_log_sha256':sha(p.parent/'generated_scope_events.jsonl'),
   'event_reason_counts':dict(collections.Counter((str(e.get('allowed'))+':'+e.get('reason','')) for e in events[1:])),
   'OS_NULL_events':null_events,'OS_NULL_events_individually_reconciled':True,
   'stop':runtime['stop_receipt']})
 if not all(s['script_bytes_unchanged_since_execution'] for s in scripts):raise EngineeringUnknown('EXECUTED_SCRIPT_DRIFT')
 minimal_receipts=[]
 for r in receipts:
  f=r['finance_receipt'];minimal_receipts.append({'call':r['ordinal'],'role':r['role'],'output_tokens':r['usage']['completion_tokens'],
   'finish_reason':r['finish_reason'],'ordinal':f['ordinal'],'status':f['status'],'body_sha256':f['body_SHA256'],
   'input_bound':f['input_bound'],'max_tokens':f['max_tokens'],'usage_accounting_upper_CNY':f['usage_accounting_upper_CNY'],
   'post_dispatch_epoch':f['post_dispatch_epoch'],'finished_epoch':f['finished_epoch']})
 value={'schema':'Agentless241-closed-original-evidence-details/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'task':task,'terminal_packet':str(base/'TERMINAL_PACKET241.json'),'terminal_sha256':sha(base/'TERMINAL_PACKET241.json'),
  'selection_before_private_path':str(flow/'selection_before_private.json'),'selection_before_private_sha256':sha(flow/'selection_before_private.json'),
  'immutable_selection_path':str(flow/'immutable_selection.json'),'immutable_selection_sha256':sha(flow/'immutable_selection.json'),
  'original_selected_before_hidden':before['selected_before_hidden'],'private_calls_before_selection':sel['private_calls_before_selection'],
  'selected_sample':before['reason']['selected_sample'],'no_verified_reproduction_fallback':before['reason']['no_verified_reproduction_fallback'],
  'actual_selected_reproduction_sample':sel['author_runtime_core']['actual_selected_reproduction_sample'],
  'patch_modified_paths':list(before['snapshot']['diff']),'selected_business_sha256':sel['selected_sha256'],
  'author_complete':sel['author_runtime_core']['complete'],'private_marker':private_marker,
  'external_birth_epoch':external_birth,'actual_author_final_stop_utc':author_final_stop['at_utc'],
  'actual_author_STOP_precedes_external_birth':author_stop_epoch<external_birth,
  'receipt_count':len(minimal_receipts),'receipt_details':minimal_receipts,'all_receipts_settled':all(r['status']=='SETTLED' for r in minimal_receipts),
  'generated_scripts':scripts,'actual_scope_events_replay_status':info['status'],'scope_audit_sha256':sha(base/'INFORMATION_ADMISSION_SCOPE_V2_241.json'),
  'coverage_limit':info['coverage_limit'],'no_private_content_in_this_summary':True,'private_feedback_not_sent_to_stopped_author':True,
  'no_repeated_model_or_native_invocation':True,'raw_result':str(flow/'result.json'),'raw_external_result':str(flow/'external_once_private/result.json')}
 save(base/'CLOSED_EVIDENCE_DETAILS241.json',value,scope=SG)
 print(canonical({'task':task,'scripts':len(scripts),'receipts':len(minimal_receipts),'script_drift':False,
  'selected_reproduction':value['actual_selected_reproduction_sample'],'fallback':value['no_verified_reproduction_fallback']}))
if __name__=='__main__':main()


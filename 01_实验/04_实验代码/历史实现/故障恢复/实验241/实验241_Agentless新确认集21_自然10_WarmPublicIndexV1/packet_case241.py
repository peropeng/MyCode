"""Read-only terminal audit into a per-case packet; no POST or native calls."""
import argparse,datetime
from decimal import Decimal
from contracts241 import *

def closed(stop):
 return not stop['timeout'] and all(stop['stop_receipt'].get(k) for k in ('root_stopped','own_Job_empty_before_close','descendants_stopped'))

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--task',required=True);args=parser.parse_args()
 task=args.task;base=HERE/'candidate'/task;flow=HERE/'runs'/task/METHOD;supervision=HERE/'supervision'/task
 actor=read(flow/'result.json');author_stop=read(supervision/'parent_stop_receipt.json')
 if not closed(author_stop):raise EngineeringUnknown('AUTHOR_NOT_CLOSED')
 external_path=flow/'external_once_private/result.json';external=read(external_path) if external_path.is_file() else {}
 external_stop_path=supervision/'external_parent_stop_receipt.json';external_stop=read(external_stop_path) if external_stop_path.is_file() else None
 if external_stop and not closed(external_stop):raise EngineeringUnknown('EXTERNAL_NOT_CLOSED')
 selected=read(flow/'immutable_selection.json') if (flow/'immutable_selection.json').is_file() else None
 if selected:
  if inventory(selected['selection_root'])!=selected['business_paths_sha256']:raise EngineeringUnknown('IMMUTABLE_SELECTION_DRIFT')
  if external and sha(flow/'immutable_selection.json')!=external['selection_manifest_sha256']:raise EngineeringUnknown('FINAL_PRIVATE_SELECTION_DRIFT')
 seal=read(base/'source_seal.json')
 for path,h in {**seal['sources'],**seal['inputs']}.items():
  if sha(path)!=h:raise EngineeringUnknown('TERMINAL_SOURCE_INPUT_DRIFT '+path)
 reader=module('terminal_finance_reader241',ROOT/'工作区/1008-2320-baseline-main/read_finance_sharedelete_root.py')
 ledger=reader.read_shared();paid=[r for r in ledger['reservations'] if r.get('pilot')==FINANCE_PHASE and task in r.get('role','')]
 if any(r['status']!='SETTLED' for r in paid):raise EngineeringUnknown('TASK_FINANCE_NOT_SETTLED')
 stages=[json.loads(x) for x in (flow/'stage_ledger.jsonl').read_text('utf-8').splitlines() if x.strip()]
 responses=[v['evidence'] for v in stages if v['stage']=='ACTUAL_FLASH_RESPONSE']
 if len(paid)!=len(responses):raise EngineeringUnknown('REAL_RESPONSE_FINANCE_COUNT_MISMATCH')
 events=[json.loads(x) for x in (supervision/'events.jsonl').read_text('utf-8').splitlines() if x.strip()]
 birth=author_stop['births'][0]['creation_time100ns']/10000000-11644473600
 end=max(datetime.datetime.fromisoformat(e['at_utc']).timestamp() for e in events if e.get('event')=='SUPERVISION_FINALLY_STOP')
 complete=bool(actor.get('runtime_core',{}).get('complete')) and external.get('status')=='COMPLETE_EXTERNAL_ONCE_PRIVATE'
 if complete and (external.get('private_attempts')!=1 or not external_stop or end-birth>900):raise EngineeringUnknown('WHOLE_ONCEPRIVATE_OR_WALL_NOT_VALID')
 success=external.get('success') if complete else actor.get('success')
 status='COMPLETE_SUCCESS' if complete and success else 'COMPLETE_NORMAL_FAILURE' if complete and success is False else actor.get('status','ENGINEERING_UNKNOWN')
 profiles={}
 for f in flow.glob('**/actual_runtime_profile.json'):profiles[str(f)]=read(f)
 row={'schema':'Agentless241-newMain-per-case-terminal-packet/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'task_id':task,'natural_index':read(base/'protocol.json')['natural_index'],'scientific_status':status,'success':success,'complete':complete,
  'author_core':actor.get('runtime_core'),'actual_response_count':len(responses),'prePOST_attempts':actor.get('LLM_calls'),
  'output_tokens':actor.get('output_tokens'),'truncated_responses':sum(r['finish_reason']=='length' for r in responses),
  'actual_fee_upper_CNY':str(sum((Decimal(r['usage_accounting_upper_CNY']) for r in paid),Decimal(0))),
  'phase_spent_CNY':ledger['pilots'][FINANCE_PHASE]['spent_CNY'],'phase_held_CNY':ledger['pilots'][FINANCE_PHASE]['held_CNY'],
  'continuous_spent_CNY':ledger['spent_CNY'],'continuous_held_CNY':ledger['held_CNY'],'continuous_records':len(ledger['reservations']),
  'old973_unchanged':digest(ledger['reservations'][:973])==read(HERE/'finance_config241.json')['old_reservations_sha256'],
  'private_attempts':external.get('private_attempts',0),'public_passed':external.get('public_passed'),
  'ordinary_passed':external.get('ordinary_passed'),'private_passed':external.get('private_passed'),
  'actor_received_private_feedback':False,'all_owned_jobs_STOP':True,'elapsed_from_author_birth_to_final_STOP_seconds':end-birth,
  'author_seconds':author_stop['seconds'],'external_seconds':external_stop['seconds'] if external_stop else None,
  'product_native_roots':external.get('product_native_roots',actor.get('product_native_roots')),
  'all_OS_native_roots':external.get('all_OS_native_roots',actor.get('all_OS_native_roots')),
  'native_root_kinds':external.get('native_root_kinds',actor.get('native_root_kinds')),
  'selected_business_sha256':selected.get('selected_sha256') if selected else None,
  'original_selection':selected.get('author_original_selection') if selected else None,
  'actual_runtime_profiles':profiles,'source_seal_sha256':digest(seal),'source_input_sha_all_pass':True,
  'author_core_sha256':actor['author_core_sha256'],'pilot_oldMain_not_merged':True,'scientific_reruns':0,'POST_retries':0,
  'raw_author_result':str(flow/'result.json'),'raw_external_result':str(external_path),'author_stop':str(supervision/'parent_stop_receipt.json'),
  'external_stop':str(external_stop_path),'preserve_all_negative_or_unknown_results':True,'audit_ledger_writes':0}
 save(base/'TERMINAL_PACKET241.json',row)
 print(canonical({k:row[k] for k in ('task_id','scientific_status','success','complete','actual_response_count','output_tokens',
  'actual_fee_upper_CNY','private_attempts','all_owned_jobs_STOP','elapsed_from_author_birth_to_final_STOP_seconds')}))
if __name__=='__main__':main()

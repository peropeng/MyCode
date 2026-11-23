"""Write a censored terminal record only after verified external Job closure."""
from common166 import *
from publicpack_v2_224 import V
from decimal import Decimal
def main():
 stop=read(V/'moto5406_external_deadline_stop_v2.json')
 assert stop['status']=='STOPPED' and all(stop['process_handles_signaled'])
 out=V/'main/recovery/getmoto__moto-5406/AGENTLESS_FSE2025_4L4P4T_FLASH'
 assert not (out/'result.json').exists(),'PRESERVE_ANY_ORIGINAL_TERMINAL_RESULT'
 receipts=[read(p) for p in out.glob('llm/*_finance_receipt.json')]
 assert len(receipts)==2 and all(x['status']=='SETTLED' for x in receipts)
 assert not list(out.rglob('*.process.json')),'UNEXPECTED_NATIVE_AFTER_DENSE_PREPARATION'
 fee=sum((Decimal(x['usage_peak_cost_CNY']) for x in receipts),Decimal(0))
 outputs=sum(read(p)['usage']['completion_tokens'] for p in out.glob('llm/*_response.json') if not p.name.endswith('_http_response.json'))
 original=read(out/'worker_started.json');started=datetime.datetime.fromisoformat(original['at_utc'])
 end=datetime.datetime.fromisoformat(stop['deadline_action_utc'])
 record={'task_id':'getmoto__moto-5406','method':'AGENTLESS_FSE2025_4L4P4T_FLASH','scientific_method':'AGENTLESS_FSE2025','status':'BUDGET_CENSORED','success':None,'runtime_core':{'complete':False,'real_dense_retrieval_connected':False},'declared_method_failure_known':False,'engineering_outcome_unknown':False,'error':{'type':'ExternalCaseDeadline','message':'LOCAL_DENSE_ENCODING_INCOMPLETE_AT_ORIGINAL_900_SECOND_BOUNDARY'},'reason':'Root explicitly requires an unfinished budget-censored null record; incomplete opponent does not establish a win. No resumption or reroll.', 'external_termination_provenance':True,'external_stop_receipt_sha256':sha(V/'moto5406_external_deadline_stop_v2.json'),'raw_paid_and_stage_files_unchanged':True,'LLM_calls':2,'new_paid_API':2,'new_fees_CNY':str(fee),'fees_CNY':str(fee),'output_tokens':outputs,'public_native_calls':0,'hidden_acceptance_calls':0,'hidden_calls_in_adapter':0,'new_Gold':0,'new_encoding':None,'new_training':0,'elapsed_seconds':(end-started).total_seconds(),'version':'V2_AUTH_DIRECT_PUBLICPACK_MAIN','primary_eligible':True,'calibration_only':False,'main_source_pin_sha256':sha(V/'main_addendum_source_pin_v2.json'),'source_seal_sha256':sha(V/'source_seal_v2.json'),'pack_registry_sha256':sha(V/'pack_registry_v2.json'),'actual_worker':original['actual_worker'],'reused_calibration_or_V1_outputs':0,'finance_fatal':False,'no_private_after_terminal_disposition':True,'no_further_candidate_in_this_flow':True}
 # Main workers use main_source_pin_v2.json; the order addendum is separate.
 record['main_source_pin_sha256']=original['main_source_pin_sha256']
 save(out/'result.json',record)
 append(V/'completed_main-agentless_v2main.jsonl',{k:record[k] for k in ('task_id','scientific_method','status','success','new_paid_API','new_fees_CNY','LLM_calls','public_native_calls','hidden_acceptance_calls')})
 s=read(V/'supervision_main-agentless_v2astsafe.json')
 s.update(status='STOPPED',at_utc=now(),exit_code=124,external_case_clock_termination=True,job_closed_all_owned_descendants_terminated=True,external_stop_receipt_sha256=sha(V/'moto5406_external_deadline_stop_v2.json'))
 save(V/'supervision_main-agentless_v2astsafe.json',s)
 print(canonical({k:record[k] for k in ('status','success','LLM_calls','new_paid_API','new_fees_CNY','elapsed_seconds')}))
if __name__=='__main__':main()

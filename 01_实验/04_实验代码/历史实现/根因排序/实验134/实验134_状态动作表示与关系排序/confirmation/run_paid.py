"""Single producer, task-first native baseline rotation, durable bounded resume."""
from decimal import Decimal,ROUND_UP
import os
import sys
import time
sys.dont_write_bytecode=True
from shared import *
import paid_methods
sys.path.insert(0,str(RES))
from continuation_client import SameEpochContinuationClient
from balance_client import ResourceBudgetAbstention
from model_client import ResourceBlocked

class StageStop(Exception):pass

def main():
    p=verify();records=read(T/'fresh_public_records.json')['records']
    if sha(T/'local_predictions.json')!=read(T/'local_prediction_seal.json')['predictions_sha256']:raise RuntimeError('local_outputs_not_sealed')
    local=read(T/'local_predictions.json')['predictions'];saved=lines(T/'paid_condition_predictions.jsonl')
    keys=[(r['sample_id'],r['condition']) for r in saved]
    if len(keys)!=len(set(keys)):raise RuntimeError('duplicate_saved_native_condition')
    by={(r['sample_id'],r['condition']):r['prediction'] for r in saved}
    client=SameEpochContinuationClient(p['authorization_file'],API,timeout=120)
    if client.unresolved_upper()!=0:raise StageStop('prior_unknown_charge_no_automatic_reissue')
    if (T/'prediction_seal.json').exists():raise RuntimeError('all_fresh_predictions_already_sealed')
    lock=API/'producer.lock';fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    with os.fdopen(fd,'w') as f:json.dump({'pid':os.getpid(),'at_utc':now(),'owner':'Exp134-fresh-confirmation'},f)
    current_record=None;current_condition=None;pending_payload=None;runstart=time.monotonic()
    def own_calls():return [r for r in client.calls if r.get('event')=='completed' and 'Exp134.confirmation.' in r.get('stage','')]
    def quote(messages,cap):
        client._verify_model()
        body={'model':'deepseek-flash','messages':messages,'temperature':0,'max_tokens':cap,'stream':False,'thinking':{'type':'disabled'}}
        upper,proof=client._request_input_bound(body);prices=client._registered_time_prices()
        reserve=((Decimal(upper)*Decimal(prices['input_miss_peak'])+Decimal(cap)*Decimal(prices['output_peak']))/Decimal(1000000)).quantize(Decimal('.000001'),rounding=ROUND_UP)
        spent=client.spent_upper()-Decimal(p['funding_anchor_epoch_usage_CNY']);budget=Decimal(client.config['exp134_confirmation_budget']['cap_CNY'])
        return {'input_UTF8_token_upper':upper,'output_token_cap':cap,'request_prices':prices,'exact_worst_request_reserve_CNY':str(reserve),
            'stage_spent_CNY':str(spent),'stage_cap_CNY':str(budget),'minimum_stage_cap_topup_for_next_request_CNY':str(max(Decimal(0),spent+reserve-budget)),
            'input_bound_proof':proof}
    def progress(phase,error=None):
        own=own_calls();resource=client.summary();complete=sum(all((r['sample_id'],c) in by for c in PAID) for r in records)
        kwargs={'fresh_confirmation':{'completed_tasks':complete,'total_tasks':len(records),'local_complete_tasks':len(records),
                    'native_paid_conditions_completed':len(by),'native_paid_conditions_total':4*len(records),'unexposed_test_label_accesses':0},
            'paid_API_calls':len(own),'stage_cost_upper_CNY':str(client.spent_upper()-Decimal(p['funding_anchor_epoch_usage_CNY'])),
            'phase_cap_CNY':client.config['exp134_confirmation_budget']['cap_CNY'],'balance_CNY':resource['latest_observed_balance_cny'],
            'unsettled_requests':sum(r.get('event')=='reserved' and r['request_id'] not in {x['request_id'] for x in client.calls if x.get('event') in ('completed','reservation_released_no_submission')} for r in client.calls),
            'current_sample_id':None if current_record is None else current_record['sample_id'],'current_condition':current_condition,
            'current_pid':os.getpid() if phase=='EXP134_CONFIRMATION_RUNNING' else None,
            'current_command':str(Path(__file__)) if phase=='EXP134_CONFIRMATION_RUNNING' else None,'recent_error':error,
            'confirmation_resource':resource,'confirmation_elapsed_seconds':time.monotonic()-runstart,
            'next_executable_command':str(Path(__file__))+' (replays only already paid exact slots; never resamples)' if phase=='EXP134_CONFIRMATION_RUNNING' else 'See confirmation/execution_checkpoint.json; preserve complete cohort before score'}
        CORE.status(phase,**kwargs)
        atomic(T/'execution_checkpoint.json',{'at_utc':now(),'phase':phase,'completed_condition_keys':[list(k) for k in by],
            'paid_request_slots':[{'sample_id':r['sample_id'],'stage':r['stage'],'request_id':r['request_id']} for r in own],
            'current_sample_id':kwargs['current_sample_id'],'current_condition':current_condition,'phase_cost_upper_CNY':kwargs['stage_cost_upper_CNY'],
            'exact_pending_payload':str(T/'pending_request.json') if pending_payload is not None else None,
            'unsettled_requests':kwargs['unsettled_requests'],'fresh_Gold_accesses':0,'no_reissue_unknown':True,
            'protocol':str(T/'protocol.json'),'next_command':kwargs['next_executable_command']})
    class Proxy:
        def __init__(self,condition):self.condition=condition;self.config=client.config
        @property
        def calls(self):return client.calls
        def generate(self,messages,*,sample_id,stage,max_tokens=2048,remaining_seconds=None):
            nonlocal pending_payload
            if sample_id!=current_record['sample_id']:raise StageStop('native_baseline_sample_binding_changed')
            name='Exp134.confirmation.'+self.condition+'.'+stage;slot='cap'+str(max_tokens)+'/'+name
            completed=[r for r in client.calls if r.get('event')=='completed' and r.get('sample_id')==sample_id and r.get('stage')==slot]
            if len(completed)>1:raise StageStop('duplicate_paid_slot_found')
            reused=bool(completed)
            if reused:
                event=completed[0];request=read(API/(event['request_id']+'.request.json'))
                if request['body']['messages']!=messages or request['body']['max_tokens']!=max_tokens:raise StageStop('cached_paid_payload_changed')
                raw=read(API/(event['request_id']+'.response.json'));choice=raw['choices'][0]
                response={'request_id':event['request_id'],'text':choice['message']['content'],'finish_reason':choice['finish_reason'],
                    'usage':raw['usage'],'elapsed_seconds':event['elapsed_seconds'],'cost_upper_cny':float(event['cost_upper_cny']),
                    'cost_lower_cny':float(event['cost_lower_cny']),'model':event['model_returned']}
            else:
                if any(r.get('event')=='reserved' and r.get('sample_id')==sample_id and r.get('stage')==slot for r in client.calls):raise StageStop('unknown_or_already_reserved_slot_no_resubmit')
                try:
                    q=quote(messages,max_tokens);pending_payload={'at_utc':now(),'sample_id':sample_id,'condition':self.condition,'stage':stage,
                        'messages':messages,'quote':q,'worst_remaining_binary_slots_bounded_by_public_tree':True}
                    atomic(T/'pending_request.json',pending_payload);progress('EXP134_CONFIRMATION_RUNNING')
                    response=client.generate(messages,sample_id=sample_id,stage=name,max_tokens=max_tokens,remaining_seconds=min(120,remaining_seconds or 120))
                except (ResourceBudgetAbstention,ResourceBlocked,RuntimeError) as exc:
                    if pending_payload is not None:
                        try:pending_payload['quote_at_stop']=quote(messages,max_tokens)
                        except Exception:pass
                        pending_payload['stop_reason']=str(exc);atomic(T/'pending_request.json',pending_payload)
                    raise StageStop(str(exc)) from None
            append(T/'call_receipts.jsonl',{'at_utc':now(),'sample_id':sample_id,'condition':self.condition,'stage':stage,
                'request_id':response['request_id'],'reused_paid_response':reused,'finish_reason':response['finish_reason'],
                'usage':response['usage'],'cost_upper_CNY':response['cost_upper_cny']})
            pending_payload=None;progress('EXP134_CONFIRMATION_RUNNING')
            if response['finish_reason']!='stop':raise paid_methods.llm_methods.FormatError('nonstop_or_output_limit_response')
            return response
    try:
        if not any(r.get('event')=='exp134_fresh_confirmation_start' for r in client.calls):
            client._append({'event':'exp134_fresh_confirmation_start','timestamp':now(),'protocol_sha256':sha(T/'protocol.json'),
                'authorization_sha256':client.authorization_sha256,'actual_n':len(records),'primary':'B','phase_CNY':'2.25',
                'original_epoch_spending_anchor_CNY':p['funding_anchor_epoch_usage_CNY'],'no_new_epoch_or_old_cost_refund':True,
                'decision_sha256':sha(T/'approved_decision.json'),'all_15_models_already_frozen':True})
        append(T/'run_events.jsonl',{'at_utc':now(),'pid':os.getpid(),'known_completed_conditions':len(by),'protocol_sha256':sha(T/'protocol.json')})
        for record in records:
            current_record=record;sid=record['sample_id']
            for condition in PAID:
                current_condition=condition
                if (sid,condition) in by:continue
                result=paid_methods.diagnose(condition,record,Proxy(condition))
                if client.unresolved_upper()!=0 or client.halt.exists():raise StageStop('unknown_charge_or_global_halt_blocks_new_condition')
                row={'at_utc':now(),'sample_id':sid,'record_id':record['record_id'],'condition':condition,'prediction':result,
                    'public_record_sha256':digest(record),'fresh_Gold_accesses':0}
                append(T/'paid_condition_predictions.jsonl',row);by[(sid,condition)]=result
                progress('EXP134_CONFIRMATION_RUNNING')
            complete=sum(all((r['sample_id'],c) in by for c in PAID) for r in records)
            print(canonical({'completed_independent_tasks':complete,'total_tasks':len(records),'paid_API_calls':len(own_calls()),
                'phase_cost_upper_CNY':str(client.spent_upper()-Decimal(p['funding_anchor_epoch_usage_CNY'])),
                'latest_balance_CNY':client.summary()['latest_observed_balance_cny'],'fresh_Gold_accesses':0}),flush=True)
        merged=[]
        for record in records:
            sid=record['sample_id'];conditions=dict(local[sid]);conditions.update({c:by[(sid,c)] for c in PAID})
            for name,source in PROJECTED.items():conditions[name]=event_projection(conditions[source],record,name,source)
            if set(conditions)!=set(CONDITIONS):raise RuntimeError('complete_frozen_condition_set_mismatch')
            merged.append({'sample_id':sid,'record_id':record['record_id'],'task_group':record['task_group'],'domain':record['domain'],
                'public_record_sha256':digest(record),'conditions':conditions})
        write(T/'predictions.json',{'at_utc':now(),'records':merged,'all_native_and_projection_rows_separate':True,'fresh_Gold_accesses':0})
        write(T/'prediction_seal.json',{'at_utc':now(),'predictions_sha256':sha(T/'predictions.json'),'protocol_sha256':sha(T/'protocol.json'),
            'n':len(records),'conditions_each':len(CONDITIONS),'total_scheduled_rows':len(records)*len(CONDITIONS),
            'all_frozen_conditions_completed_before_any_Gold':True,'model_seal_sha256':p['model_seal_sha256'],'fresh_Gold_accesses':0})
        write(T/'execution_receipt.json',{'at_utc':now(),'paid_API_calls':len(own_calls()),
            'phase_cost_upper_CNY':str(client.spent_upper()-Decimal(p['funding_anchor_epoch_usage_CNY'])),'resource':client.summary(),
            'duplicate_paid_slots':False,'unsettled_requests':0,'whole_scope_complete':True})
        progress('EXP134_CONFIRMATION_ALL_PREDICTIONS_SEALED')
    except Exception as exc:
        append(T/'execution_errors.jsonl',{'at_utc':now(),'error':str(exc),'type':type(exc).__name__,'sample_id':None if current_record is None else current_record['sample_id'],'condition':current_condition})
        missing=[{'sample_id':r['sample_id'],'missing_conditions':[c for c in PAID if (r['sample_id'],c) not in by]} for r in records if not all((r['sample_id'],c) in by for c in PAID)]
        atomic(T/'minimum_required_continuation.json',{'at_utc':now(),'error':str(exc),'missing_tasks':missing,
            'exact_next_payload_and_reserve':str(T/'pending_request.json') if pending_payload else None,
            'stage_cost_upper_CNY':str(client.spent_upper()-Decimal(p['funding_anchor_epoch_usage_CNY'])),
            'shared_remaining_hardcap_CNY':client.summary()['remaining_additional_hardcap_cny'],
            'latest_observed_balance_CNY':client.summary()['latest_observed_balance_cny'],
            'unresolved_reserve_CNY':str(client.unresolved_upper()),'no_partial_accuracy_evaluation':True,'fresh_Gold_accesses':0})
        progress('EXP134_CONFIRMATION_BUDGET_OR_TECHNICAL_STOP',str(exc));raise
    finally:lock.unlink()

if __name__=='__main__':main()

"""Read-only extended queue/finance/results observation; no actor or native run."""
from common166 import *
from decimal import Decimal
from publicpack_v2_224 import V

def observe():
    order=read(V/'main_addendum_source_pin_v2.json')['task_order']
    methods={'main-agentless':'AGENTLESS_FSE2025_4L4P4T_FLASH','main-ours':'G_PROGRESSIVE_SEMANTIC_FLASH'}
    rows=[]; summaries={}
    for mode,method in methods.items():
        finished=[];active=[]
        for index,task in enumerate(order):
            out=V/'main/recovery'/task/method
            if (out/'result.json').exists():
                result=read(out/'result.json')
                receipts=[read(p) for p in out.glob('llm/*_finance_receipt.json')]
                settled=[x for x in receipts if x.get('status')=='SETTLED']
                fee=sum((Decimal(x['usage_peak_cost_CNY']) for x in settled),Decimal(0))
                assert fee==Decimal(result['new_fees_CNY']) and len(settled)==result['new_paid_API']
                row={k:result.get(k) for k in ('status','success','LLM_calls','public_native_calls','hidden_acceptance_calls',
                                              'new_fees_CNY','elapsed_seconds','error','primary_eligible','actual_worker')}
                row.update(task_id=task,task_index=index,mode=mode,method=method,result_sha256=sha(out/'result.json'),
                           complete=result.get('runtime_core',{}).get('complete'),result_present=True)
                rows.append(row);finished.append(row)
            elif (out/'worker_started.json').exists():
                stage={};events=out/'stage_ledger.jsonl'
                if events.exists():
                    with events.open(encoding='utf-8-sig') as stream:
                        for line in stream:
                            if line.strip():
                                event=json.loads(line);stage={k:event.get(k) for k in ('at_utc','ordinal','stage')}
                receipts=[read(p) for p in out.glob('llm/*_finance_receipt.json')]
                settled=[x for x in receipts if x.get('status')=='SETTLED']
                active.append({'task_id':task,'task_index':index,'actual_stage':stage,'settled_calls_so_far':len(settled),
                               'fees_so_far_CNY':str(sum((Decimal(x['usage_peak_cost_CNY']) for x in settled),Decimal(0)))})
        wait=V/('extended_checkpoint_'+mode+'.json')
        supervisor=V/('supervision_'+mode+'_v2astsafe.json')
        if not supervisor.exists():supervisor=V/('supervision_'+mode+'_v2ioretry.json')
        if not supervisor.exists():supervisor=V/('supervision_'+mode+'_v2scoped.json')
        if not supervisor.exists():supervisor=V/('supervision_'+mode+'_v2extended.json')
        summaries[mode]={'finished':len(finished),'success':sum(x['success'] is True for x in finished),
                         'known_failure':sum(x['success'] is False for x in finished),'unknown':sum(x['success'] is None for x in finished),
                         'active_or_started_unfinished':active,'supervision':read(supervisor) if supervisor.exists() else None,
                         'peer_wait_last_record':read(wait) if wait.exists() else None}
    ledger=read(ROOT/'工作区/1003-diagnosis-investigation/exp132_review/new_window_2332/finance/shared_flash_budget.json')
    finance={k:ledger.get(k) for k in ('cap_CNY','spent_CNY','held_CNY','floor_CNY','blocked','last_valid_balance_CNY')}
    output={'at_utc':now(),'version':'V2_AUTH_DIRECT_PUBLICPACK_MAIN','order':order,'summaries':summaries,'results':rows,
            'shared_continuous_finance':finance,'source_pin_sha256':sha(V/'ast_safe_main_source_pin_v2.json') if (V/'ast_safe_main_source_pin_v2.json').exists() else sha(V/'io_retry_main_source_pin_v2.json') if (V/'io_retry_main_source_pin_v2.json').exists() else sha(V/'scoped_main_source_pin_v2.json') if (V/'scoped_main_source_pin_v2.json').exists() else sha(V/'extended_main_source_pin_v2.json'),
            'new_model_POST_native_private_Gold_for_observation':0}
    save(V/'extended_main_observation_v2.json',output)
    compact={mode:{k:value for k,value in summary.items() if k in ('finished','success','known_failure','unknown','active_or_started_unfinished')}
             for mode,summary in summaries.items()}
    print(canonical({'at_utc':output['at_utc'],'summaries':compact,'finance':finance}))

if __name__=='__main__':observe()

"""Read-only results/receipt audit; never constructs environment or model."""
from common166 import *
from decimal import Decimal
from publicpack_v2_224 import V

def observe():
    rows=[]
    for task in ('Project-MONAI__MONAI-5093','getmoto__moto-5134'):
        for method in ('AGENTLESS_FSE2025_4L4P4T_FLASH','G_PROGRESSIVE_SEMANTIC_FLASH'):
            out=V/'main/recovery'/task/method
            if not (out/'result.json').exists():
                receipts=[read(p) for p in out.glob('llm/*_finance_receipt.json')]
                settled=[x for x in receipts if x['status']=='SETTLED']
                stage={}
                if (out/'stage_ledger.jsonl').exists():
                    with (out/'stage_ledger.jsonl').open(encoding='utf-8-sig') as stream:
                        for line in stream:
                            if line.strip():
                                event=json.loads(line); stage={k:event.get(k) for k in ('at_utc','ordinal','stage')}
                rows.append({'task_id':task,'method':method,'result_present':False,
                             'worker_started':(out/'worker_started.json').exists(),
                             'latest_actual_stage':stage,'settled_calls_so_far':len(settled),
                             'fees_so_far_CNY':str(sum((Decimal(x['usage_peak_cost_CNY']) for x in settled),Decimal(0)))}); continue
            r=read(out/'result.json')
            receipts=[read(p) for p in out.glob('llm/*_finance_receipt.json')]
            settled=[x for x in receipts if x['status']=='SETTLED']
            fee=sum((Decimal(x['usage_peak_cost_CNY']) for x in settled),Decimal(0))
            assert fee==Decimal(r['new_fees_CNY']) and len(settled)==r['new_paid_API']
            events=[json.loads(line) for line in (out/'stage_ledger.jsonl').read_text('utf-8-sig').splitlines()]
            routes=[x['evidence'] for x in events if x['stage']=='V2_MAIN_EXPLICIT_PHASE_ROUTING']
            assert len(routes)==r['LLM_calls']
            assert all(x['actual_registered_finance_phase']=='Round2320Main' and x['body_and_seed_unchanged'] is True for x in routes)
            processes=[read(p) for p in out.rglob('*.process.json')]
            assert all(x['root_PID_birth_verified'] and x['stop_receipt']['owned_job_closed'] and
                       x['stop_receipt']['all_owned_descendants_terminated'] for x in processes)
            assert r['version']=='V2_AUTH_DIRECT_PUBLICPACK_MAIN'
            row={k:r.get(k) for k in ('task_id','method','status','success','primary_eligible','LLM_calls','public_native_calls',
                                     'hidden_acceptance_calls','new_paid_API','new_fees_CNY','elapsed_seconds','error','actual_worker')}
            row.update(result_present=True,result_sha256=sha(out/'result.json'),complete=r.get('runtime_core',{}).get('complete'),
                       actual_owned_process_receipts=len(processes),all_native_owned_births_closed=True,actual_phase_Main=True)
            rows.append(row)
    result={'at_utc':now(),'version':'V2_AUTH_DIRECT_PUBLICPACK_MAIN','rows':rows,
            'new_model_native_private_Gold_for_observation':0,
            'independent_controller_pin_sha256':sha(V/'independent_main_source_pin_v2.json')}
    save(V/'independent_main_observation_v2.json',result); print(canonical(result))

if __name__=='__main__':observe()

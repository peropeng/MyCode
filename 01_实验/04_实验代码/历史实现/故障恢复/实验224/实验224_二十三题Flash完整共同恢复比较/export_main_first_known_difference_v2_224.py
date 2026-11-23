"""Read-only full-core paired difference; UNKNOWN is excluded from score imputation."""
from common166 import *
from decimal import Decimal
from publicpack_v2_224 import V

def export():
    task='python__mypy-11134';rows=[]
    for method in ('AGENTLESS_FSE2025_4L4P4T_FLASH','G_PROGRESSIVE_SEMANTIC_FLASH'):
        out=V/'main/recovery'/task/method;r=read(out/'result.json')
        assert r['version']=='V2_AUTH_DIRECT_PUBLICPACK_MAIN' and r['runtime_core']['complete'] is True
        assert r['primary_eligible'] and r['hidden_acceptance_calls']==1 and isinstance(r['success'],bool)
        receipts=[read(p) for p in out.glob('llm/*_finance_receipt.json')]
        assert len(receipts)==r['new_paid_API'] and all(x['status']=='SETTLED' for x in receipts)
        assert sum((Decimal(x['usage_peak_cost_CNY']) for x in receipts),Decimal(0))==Decimal(r['new_fees_CNY'])
        events=[json.loads(line) for line in (out/'stage_ledger.jsonl').read_text('utf-8-sig').splitlines()]
        routes=[x['evidence'] for x in events if x['stage']=='V2_MAIN_EXPLICIT_PHASE_ROUTING']
        assert len(routes)==r['LLM_calls'] and all(x['actual_registered_finance_phase']=='Round2320Main' and x['body_and_seed_unchanged'] for x in routes)
        processes=[read(p) for p in out.rglob('*.process.json')]
        assert all(x['root_PID_birth_verified'] and x['stop_receipt']['all_owned_descendants_terminated'] for x in processes)
        row={k:r.get(k) for k in ('task_id','method','status','success','LLM_calls','new_paid_API','new_fees_CNY',
                                  'elapsed_seconds','public_native_calls','hidden_acceptance_calls')}
        row.update(result_sha256=sha(out/'result.json'),core_complete=True,all_processes_closed=True,
                   actual_physical_process_receipts=len(processes),actual_Main_phase=True)
        rows.append(row)
    assert rows[0]['success'] is False and rows[1]['success'] is True
    report={'at_utc':now(),'task_id':task,'version':'V2_AUTH_DIRECT_PUBLICPACK_MAIN','rows':rows,
            'interpretation':'First complete-core paired difference favors ours on this task. Fixed21 queue incomplete; previous UNKNOWN remain null, no stable population advantage claim.',
            'new_POST_native_private_Gold_for_audit':0}
    save(V/'first_known_paired_difference_mypy11134_v2.json',report)
    print(canonical(report))
if __name__=='__main__':export()

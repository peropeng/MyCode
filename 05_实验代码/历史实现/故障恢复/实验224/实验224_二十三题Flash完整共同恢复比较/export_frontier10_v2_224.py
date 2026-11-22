"""Audit fixed Main21 records without starting model, native, or private work."""
from common166 import *
from decimal import Decimal
from publicpack_v2_224 import V


def export():
    order = read(V / 'main_addendum_source_pin_v2.json')['task_order']
    methods = ('AGENTLESS_FSE2025_4L4P4T_FLASH', 'G_PROGRESSIVE_SEMANTIC_FLASH')
    rows = []
    for index, task in enumerate(order):
        pair = []
        for method in methods:
            out = V / 'main/recovery' / task / method
            path = out / 'result.json'
            if not path.exists():
                pair.append({'method': method, 'disposition': 'RUNNING' if (out / 'worker_started.json').exists() else 'UNRUN', 'success': None})
                continue
            result = read(path)
            assert result['version'] == 'V2_AUTH_DIRECT_PUBLICPACK_MAIN'
            receipts = [read(p) for p in out.glob('llm/*_finance_receipt.json')]
            assert all(x['status'] == 'SETTLED' for x in receipts)
            assert len(receipts) == result['new_paid_API']
            assert sum((Decimal(x['usage_peak_cost_CNY']) for x in receipts), Decimal(0)) == Decimal(result['new_fees_CNY'])
            processes = [read(p) for p in out.rglob('*.process.json')]
            assert all(p['root_PID_birth_verified'] and p['stop_receipt']['all_owned_descendants_terminated'] for p in processes)
            success = result['success']
            core = result.get('runtime_core', {}).get('complete') is True
            known = core or (success is False and result.get('declared_method_failure_known') is True)
            if success is True:
                assert core and result['hidden_acceptance_calls'] == 1
            if success is False:
                assert known
            row = {k: result.get(k) for k in ('method', 'status', 'success', 'LLM_calls', 'new_paid_API', 'new_fees_CNY', 'elapsed_seconds', 'public_native_calls', 'hidden_acceptance_calls')}
            row.update(disposition='KNOWN' if known and isinstance(success, bool) else 'UNKNOWN', core_complete=core, result_sha256=sha(path), actual_closed_process_receipts=len(processes))
            pair.append(row)
        comparable = all(x['disposition'] == 'KNOWN' for x in pair)
        outcome = ('OURS_WIN' if pair[1]['success'] and not pair[0]['success'] else 'AL_WIN' if pair[0]['success'] and not pair[1]['success'] else 'TIE') if comparable else None
        rows.append({'task_index': index, 'task_id': task, 'methods': pair, 'known_pair': comparable, 'paired_outcome': outcome})
    evidence = []
    path = V / 'main/recovery/getmoto__moto-5406/G_PROGRESSIVE_SEMANTIC_FLASH/stage_ledger.jsonl'
    if path.exists():
        for line in path.read_text('utf-8-sig').splitlines():
            event = json.loads(line)
            if event['stage'] == 'ranked_repair178_output_failure':
                entry = event['evidence']
                evidence.append({k: entry.get(k) for k in ('attempt', 'outcome', 'output_error', 'evidence_steps', 'output_truncated', 'applied', 'response_content_sha256')})
    summary = {name: sum(x['paired_outcome'] == name for x in rows) for name in ('OURS_WIN', 'AL_WIN', 'TIE')}
    report = {'at_utc': now(), 'fixed_denominator': len(order), 'administrative_frontier': read(V / 'root_ast_safe_main_grant_v2.json')['allowed_through_index'], 'rows': rows, 'paired_known_count': sum(x['known_pair'] for x in rows), 'paired_outcomes': summary, 'ours_moto5406_output_failures': evidence, 'interpretation': 'Declared normal semantic failures count as failures; incomplete engineering/budget records remain UNKNOWN. Administrative frontier is not a scientific sample filter. Remaining fixed tasks stay UNRUN. No stable population advantage is established.', 'new_POST_native_private_Gold_for_audit': 0}
    save(V / 'frontier10_fixed21_audit_v2.json', report)
    print(canonical({k: report[k] for k in ('at_utc', 'fixed_denominator', 'administrative_frontier', 'paired_known_count', 'paired_outcomes')}))


if __name__ == '__main__':
    export()

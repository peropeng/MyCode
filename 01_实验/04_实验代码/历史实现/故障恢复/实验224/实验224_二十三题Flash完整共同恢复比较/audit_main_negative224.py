"""Read completed public Main records; never initialize an experimental actor."""
import collections
import datetime
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    rows = []
    for path in sorted((E / 'fresh_main/recovery').glob('*/AGENTLESS*/result.json')):
        result = json.loads(path.read_text('utf-8-sig'))
        if result.get('success') is not False:
            continue
        ledger = path.parent / 'stage_ledger.jsonl'
        events = [json.loads(x) for x in ledger.read_text('utf-8-sig').splitlines() if x.strip()]
        returned = [x['evidence'] for x in events if x['stage'] == 'Flash_actual_response224']
        readers = [x['evidence'] for x in events if x['stage'] == 'actual_public_reader224']
        errors = [x['evidence'] for x in events if x['stage'] == 'public_reader_argument_error224']
        stage_counts = collections.Counter(x['role'] for x in returned)
        reader_keys = collections.Counter(json.dumps({'name': x['name'], 'arguments': x['arguments'],
                                                     'output_sha256': x['output_sha256']}, sort_keys=True)
                                         for x in readers)
        generation = 0
        within_generation = collections.Counter()
        for event in events:
            if event['stage'] == 'Flash_actual_response224' and event['evidence'].get('reader_index') == 0:
                generation += 1
            if event['stage'] == 'actual_public_reader224':
                x = event['evidence']
                within_generation[(generation, json.dumps(x, sort_keys=True))] += 1
        within_duplicates = sum(n - 1 for n in within_generation.values())
        core = result.get('runtime_core', {})
        restores = [x['evidence'] for x in events if x['stage'] == 'agentless_independent_generation_C0_restored224']
        final_role = returned[-1]['role'] if returned else None
        final_stage = [x for x in returned if x['role'] == final_role]
        terminal_start = next((x['ordinal'] for x in reversed(events)
                               if x['stage'] == 'Flash_actual_response224'
                               and x['evidence'].get('reader_index') == 0), -1)
        terminal_responses = [x['evidence'] for x in events
                              if x['stage'] == 'Flash_actual_response224'
                              and x['ordinal'] >= terminal_start]
        rows.append({
            'task_id': result['task_id'], 'status': result['status'], 'success': False,
            'reason': result.get('reason'), 'error': result.get('error'),
            'result_sha256': sha(path), 'ledger_sha256': sha(ledger),
            'final_model_role': final_role,
            'final_role_reader_indices': [x.get('reader_index') for x in final_stage],
            'terminal_generation_reader_indices': [x.get('reader_index') for x in terminal_responses],
            'responses_by_role': dict(stage_counts),
            'completed_scientific_stages': core.get('actual_stages'),
            'independent_C0_restores': restores,
            'same_C0_business_digest_after_every_restore': len({x['after_business_digest'] for x in restores}) == 1 if restores else None,
            'valid_candidate_count': core.get('actual_valid_patches', 0),
            'reproduction_generations': core.get('actual_reproduction_generations', 0),
            'public_native_calls': result.get('public_native_calls'),
            'private_calls': result.get('hidden_acceptance_calls'),
            'goal_checked_on_any_candidate': bool(result.get('public_native_calls')),
            'public_reader_successes': len(readers),
            'exact_duplicate_reads_with_same_output': sum(n - 1 for n in reader_keys.values()),
            'exact_duplicate_reads_within_same_generation': within_duplicates,
            'duplicate_measurement_scope': 'Global duplicates include independent stages/samples. Within-generation duplicates hold the logical generation fixed; neither metric establishes causal waste.',
            'reader_argument_errors': [{'tool': x['tool'], 'arguments': x['arguments'],
                                        'message': x['result']['message']} for x in errors],
            'terminal_generation_successful_reads': [x['evidence'] for x in events
                if x['stage'] == 'actual_public_reader224'
                and x['ordinal'] > terminal_start],
            'fees_CNY': result.get('new_fees_CNY'), 'logical_calls': result.get('LLM_calls'),
            'output_tokens': result.get('output_tokens'), 'elapsed_seconds': result.get('elapsed_seconds'),
            'whole_flow_call_budget_remaining': max(0, 64 - result.get('LLM_calls', 0)),
            'whole_flow_output_budget_remaining': max(0, 65536 - result.get('output_tokens', 0)),
            'whole_flow_wall_remaining_seconds': max(0, 900 - result.get('elapsed_seconds', 0)),
            'interpretation': 'Declared reader-stage budget failure retained. No native target failure can be inferred when native_calls=0; a valid candidate is not an accepted repair.',
        })
    output = {'schema': 'Exp224-public-normal-negative-audit/1',
              'at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scope': 'Completed Agentless Main normal negatives only; public ledger and status metadata. No private contents read.',
              'new_model_calls': 0, 'new_native_calls': 0, 'actor_or_core_changes': 0,
              'raw_results_unchanged': True, 'rows': rows}
    target = E / 'audit224/main_normal_negative_mechanisms224.json'
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    print(json.dumps([{k: r[k] for k in ('task_id', 'final_model_role', 'valid_candidate_count',
                     'public_native_calls', 'public_reader_successes', 'exact_duplicate_reads_with_same_output')}
                     for r in rows], ensure_ascii=False))


if __name__ == '__main__':
    main()

"""Project completed repair attempts without reading any private test files."""
import datetime
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parent


def main():
    rows = []
    public_path = E / 'data/public_inputs.jsonl'
    public_inputs = [json.loads(x) for x in public_path.read_text('utf-8-sig').splitlines() if x.strip()]
    preservation_scope = [{'task_id': x['instance_id'],
                           'frozen_metadata_initially_passed': x.get('public_regression_initially_passed'),
                           'public_regression_node_count': len(x.get('public_regression_tests', [])),
                           'public_regression_node_names': x.get('public_regression_tests', [])}
                          for x in public_inputs]
    fields = ('attempt', 'evidence_count', 'evidence_steps', 'parsed', 'applied',
              'public_passed', 'public_failure_count', 'outcome', 'output_error',
              'call_ordinal', 'physical_native_calls', 'payload_sha256',
              'response_content_sha256', 'current_business_diff_bytes')
    for path in sorted((E / 'fresh_main/recovery').glob('*/G_PROGRESSIVE*/result.json')):
        result = json.loads(path.read_text('utf-8-sig'))
        attempts = [{k: x.get(k) for k in fields} for x in result.get('attempt_history', [])]
        rows.append({'task_id': result['task_id'], 'result_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                     'attempts': attempts, 'complete_core': result.get('runtime_core', {}).get('complete'),
                     'selected_snapshot_sha256': result.get('final_snapshot', {}).get('inventory_sha256'),
                     'selected_before_private': result.get('selection', {}).get('selected_before_hidden'),
                     'selection_used_private': result.get('selection', {}).get('reason', {}).get('uses_hidden'),
                     'final_status': result.get('status'), 'final_success': result.get('success'),
                     'public_native_calls': result.get('public_native_calls'),
                     'private_call_count_only': result.get('hidden_acceptance_calls')})
    output = {'schema': 'Exp224-public-attempt-projection/1',
              'at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'new_model_native_private_calls': 0, 'core_and_outputs_unchanged': True,
              'public_input_sha256': hashlib.sha256(public_path.read_bytes()).hexdigest(),
              'frozen_public_preservation_scope': preservation_scope,
              'preservation_scope_interpretation': 'Historical frozen metadata, not a new initial native run. One named public regression node per case does not establish broad functional preservation.',
              'interpretation': 'Observed later success is not a causal estimate for additional evidence: cumulative state, public feedback and fixed attempt seed also change.',
              'rows': rows}
    (E / 'audit224/main_public_attempts224.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    print(json.dumps([{'task_id': x['task_id'], 'attempt_outcomes': [a['outcome'] for a in x['attempts']]} for x in rows]))


if __name__ == '__main__':
    main()

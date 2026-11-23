"""Read existing public artifacts; write only corrected summaries and an archive.

No experiment module is imported. No POST, native, private or ledger operation.
The terminal cursor is an audited aggregate, not a new restart checkpoint.
"""
import datetime
import hashlib
import json
import os
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def ref(path):
    return {'path': str(path), 'SHA256': sha(path)}


def save(path, value):
    data = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()
    temporary = path.with_name(path.name + '.public-summary-tmp')
    with temporary.open('wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def mechanism_input(request, relation_path):
    tail = []
    for message in request['body']['messages']:
        content = message.get('content')
        if not isinstance(content, str):
            continue
        try:
            value = json.loads(content)
        except ValueError:
            continue
        if isinstance(value, dict) and value.get('schema') == 'current-public-feedback-source-binding/1':
            tail.append(value)
    assert len(tail) == 1
    tail = tail[0]
    relation = read(relation_path)
    audit = relation['public_failure_anchor_audit']
    assert tail['binding'] == audit['current_feedback_binding']
    spans = tail['current_business_functions']
    assert all(span['complete_source_span'] is True for span in spans)
    return {
        'actual_request_body_SHA256': request['body_SHA256'],
        'source_feedback_binding': tail['binding'],
        'public_Goal_summary': tail['current_public_Goal_summary'],
        'whole_current_source_span_count': len(spans),
        'whole_current_source_text_bytes': sum(len(span['text'].encode()) for span in spans),
        'relation_manifest': ref(relation_path),
        'derived_static_edges': relation['edge_count'],
        'current_public_business_frame_count': len(audit['current_public_business_frames']),
        'static_public_Goal_business_function_matches': len(audit['public_Goal_method_business_matches']),
        'declared_Goal_AST_provenance': audit['public_Goal_masked_test_AST_audit'],
        'fallback_to_ranked_only': audit['fallback_to_ranked_only'],
        'source_is_current_sha_bound_not_historical': tail['current_source_is_authoritative'],
        'historical_image_not_current': tail['historical_before_after_is_never_current_source'],
        'no_task_specific_patch_or_other_method_output': tail['no_task_specific_patch_or_other_method_output'],
        'causal_edge_claim': False,
    }


def build(index):
    forward = HERE / 'forward' / str(index)
    replay = HERE / 'replay' / str(index)
    terminal_path = forward / 'PUBLIC_ONLY_NATURAL_TERMINAL.json'
    terminal = read(terminal_path)
    history = terminal['attempt_history']
    core = terminal['runtime_core']
    initial_state = read(replay / 'checkpoint.json')
    goal_nodes = initial_state['guard']['goals']
    assert terminal['status'] == 'COMPLETED' and terminal['error'] is None
    assert terminal['first_public_pass_attempt'] == 2
    assert len(history) == 2 and core['complete'] is True
    for key in ('actual_generation_requests', 'actual_returned_model_responses',
                'actual_public_validation_calls', 'actual_physical_candidate_native_calls'):
        assert core[key] == 2, key
    receipts, model_evidence, native_evidence, input_chain = [], [], [], []
    usage_sum = {key: 0 for key in ('prompt_tokens', 'completion_tokens', 'total_tokens',
                                   'prompt_cache_hit_tokens', 'prompt_cache_miss_tokens')}
    cost_sum = Decimal('0')
    for attempt, attempt_record in enumerate(history, 1):
        llm = (replay / 'new_generation' / 'llm' if attempt == 1 else
               forward / 'ready' / 'call002' / 'new_generation' / 'llm')
        stem = f'{attempt:03d}'
        request_path = llm / (stem + '_request.json')
        response_path = llm / (stem + '_response.json')
        receipt_path = llm / (stem + '_finance_receipt.json')
        http_path = llm / (stem + '_http_response.json')
        request, response, receipt = read(request_path), read(response_path), read(receipt_path)
        raw = read(http_path)
        usage = response['usage']
        assert raw['status_code'] == 200 and json.loads(raw['body_text'])['usage'] == usage
        assert attempt_record['usage'] == usage
        assert response['_finance_receipt'] == receipt
        assert request['body_SHA256'] == digest(request['body']) == receipt['body_SHA256']
        assert receipt['status'] == 'SETTLED' and receipt['call_ordinal'] == attempt
        assert response['choices'][0]['finish_reason'] == 'stop'
        assert not response['choices'][0]['message'].get('tool_calls')
        assert attempt_record['call_ordinal'] == attempt and attempt_record['physical_native_calls'] == 1
        for key in usage_sum:
            usage_sum[key] += usage[key]
        cost_sum += Decimal(receipt['usage_accounting_upper_CNY'])
        receipts.append({
            'status': receipt['status'], 'ordinal': receipt['ordinal'],
            'body_SHA256': receipt['body_SHA256'],
            'usage_accounting_upper_CNY': receipt['usage_accounting_upper_CNY'],
            'price_basis': receipt['price_basis'], 'not_invoice': receipt['not_invoice'],
            'input_tokens': usage['prompt_tokens'], 'output_tokens': usage['completion_tokens'],
            'actual_usage': usage, 'post_dispatch_epoch': receipt['post_dispatch_epoch'],
            'finished_epoch': receipt['finished_epoch'], 'receipt_file': ref(receipt_path),
        })
        model_evidence.append({
            'attempt': attempt, 'request': ref(request_path), 'response': ref(response_path),
            'provider_http_response': ref(http_path), 'SETTLED_receipt': ref(receipt_path),
            'body_complete_canonical_hash_equal': True, 'response_and_terminal_usage_equal': True,
            'provider_usage': usage, 'tool_call_count': 0, 'counted_actual_POST': 1,
        })
        out = forward / 'public_native' / f'attempt{attempt}'
        completed_path, supervision_path = out / 'COMPLETED_PUBLIC.json', out / 'SUPERVISION.json'
        completed, supervision = read(completed_path), read(supervision_path)
        run_path = Path(completed['public_native_path'])
        run = read(run_path)
        assert sha(run_path) == completed['public_native_SHA256']
        assert supervision['exit_code'] == 0 and supervision['error'] is None
        stop = supervision['stop_receipt']
        assert all(stop[key] is True for key in ('owned_job_closed', 'root_process_stopped',
                                                'all_owned_descendants_terminated'))
        assert completed['native_calls'] == 1 and completed['private'] == completed['model'] == 0
        assert all(run[key] is True for key in ('executed', 'guard_loaded', 'business_state_unchanged',
                                               'frozen_tests_unchanged', 'exact_test_coverage',
                                               'completed_guarded_coverage'))
        assert run['timeout'] is False
        assert completed['ordinary_all_pass'] is True
        assert completed['failed_goals'] == attempt_record['public_failure_count']
        assert run['passed'] is (attempt == 2)
        native_evidence.append({
            'attempt': attempt, 'actual_public_run': ref(run_path),
            'COMPLETED_PUBLIC': ref(completed_path), 'held_parent_STOP': ref(supervision_path),
            'ordinary_all_PASS': completed['ordinary_all_pass'],
            'actual_Goal_PASS_nodes': completed['goal_actual_pass'],
            'actual_failed_Goal_nodes': [node for node in goal_nodes
                                         if run['pytest']['outcomes'][node]['status'] != 'passed'],
            'actual_failed_Goal_count': completed['failed_goals'],
            'requested_nodes': run['requested_nodes'],
            'public_outcomes': {node: {'status': value['status'], 'phase': value.get('phase')}
                                for node, value in run['pytest']['outcomes'].items()},
            'public_G_O_all_PASS': run['passed'], 'physical_candidate_native_calls': 1,
            'held_parent_STOP_all_descendants_terminated': True,
            'public_native_seconds': run['seconds'],
            'public_completion_at_UTC': completed['at_utc'],
            'held_parent_STOP_at_UTC': supervision['at_utc'],
            'observed_business_inventory_SHA256': digest(completed['candidate_source_sha256']),
        })
        input_chain.append(mechanism_input(request, replay / 'relations' / f'attempt_{attempt}.json'))
    terminal_cursor = {'calls': len(model_evidence), 'native': len(native_evidence),
                       'output_tokens': usage_sum['completion_tokens']}
    initial_checkpoint_path = replay / 'checkpoint.json'
    boundary_path = forward / 'public_native' / 'attempt2' / 'checkpoint.json'
    initial_checkpoint, boundary = read(initial_checkpoint_path), read(boundary_path)
    assert initial_checkpoint['status'] == 'MODEL_READY' and initial_checkpoint['cursor']['calls'] == 1
    assert boundary['status'] == 'PUBLIC_NATIVE_READY'
    assert boundary['cursor'] == {'calls': 2, 'native': 1, 'output_tokens': usage_sum['completion_tokens']}
    assert input_chain[1]['source_feedback_binding']['source_native_witness_SHA256'] == native_evidence[0]['actual_public_run']['SHA256']
    assert input_chain[0]['source_feedback_binding']['source_inventory_SHA256'] == digest(initial_state['initial_source'])
    assert input_chain[1]['source_feedback_binding']['source_inventory_SHA256'] == native_evidence[0]['observed_business_inventory_SHA256']
    source_preparation = read(replay / 'SOURCE_BODY_PREPARATION_COST.json')
    assert input_chain[0]['source_feedback_binding']['source_native_witness_SHA256'] == source_preparation['public_C0_observation_reuse']['SHA256']
    assert source_preparation['frozen_RQ1_plan_SHA256'] == terminal['source_evidence']['G_frozen_plan_sha256']
    t0_path = HERE / 'science' / initial_checkpoint['task'] / 'SCIENCE_T0_ACTUAL_POST_DISPATCH.json'
    t0 = read(t0_path)
    assert t0['body_SHA256'] == receipts[0]['body_SHA256']
    stop_at = datetime.datetime.fromisoformat(native_evidence[-1]['held_parent_STOP_at_UTC'])
    started = datetime.datetime.fromisoformat(t0['at_UTC'])
    frozen_path = HERE / 'final_ready' / str(index) / 'FROZEN_BUSINESS_SOURCE.json'
    ready_path = HERE / 'final_ready' / str(index) / 'READY.json'
    frozen_source = read(frozen_path)
    frozen_inventory = {path: hashlib.sha256(text.encode()).hexdigest() for path, text in sorted(frozen_source.items())}
    assert digest(frozen_inventory) == core['public_state_admission']['incumbent_source_inventory_sha256']
    assert digest(frozen_inventory) == native_evidence[-1]['observed_business_inventory_SHA256']
    return {
        'index': index, 'task': initial_checkpoint['task'],
        'status': 'PUBLIC_ONLY_NATURAL_TERMINAL_PRIVATE_ACCEPTANCE_OUTSIDE_THIS_RECORD',
        'first_public_PASS_attempt': 2, 'normal_terminal_error': None,
        'public_G_O_all_PASS': True, 'exact_new_settled_model_calls': len(receipts),
        'actual_physical_public_candidate_native_calls': len(native_evidence),
        'settled_public_model_receipts': receipts,
        'complete_checkpoint_cursor': terminal_cursor,
        'complete_checkpoint_cursor_is_terminal_aggregate_not_raw_restart_state': True,
        'cumulative_provider_usage': usage_sum,
        'cumulative_usage_accounting_upper_CNY': str(cost_sum), 'accounting_upper_is_not_invoice': True,
        'initial_replay_checkpoint': {**ref(initial_checkpoint_path), 'status': initial_checkpoint['status'],
                                      'cursor': initial_checkpoint['cursor']},
        'latest_physical_native_boundary_checkpoint': {**ref(boundary_path), 'status': boundary['status'],
                                                       'cursor': boundary['cursor'],
                                                       'boundary_is_before_second_native_completion': True},
        'terminal_count_derivation': 'Two exact-body SETTLED model responses plus two distinct completed public native/STOP receipts; terminal runtime_core and both attempt_history entries independently agree.',
        'public_terminal': ref(terminal_path), 'terminal_runtime_core_count_check': {
            key: core[key] for key in ('complete', 'actual_generation_requests',
                                       'actual_returned_model_responses', 'actual_public_validation_calls',
                                       'actual_physical_candidate_native_calls', 'max_generation_attempts',
                                       'progressive_evidence_counts')},
        'model_call_evidence': model_evidence, 'original_public_native_trajectory': native_evidence,
        'actual_request_current_feedback_source_chain': input_chain,
        'terminal_public_state_admission': core['public_state_admission'],
        'scientific_T0': t0, 'scientific_T0_file': ref(t0_path),
        'public_terminal_held_parent_STOP_at_UTC': native_evidence[-1]['held_parent_STOP_at_UTC'],
        'elapsed_actual_first_POST_T0_to_public_terminal_STOP_seconds': (stop_at - started).total_seconds(),
        'T0_marker_keeps_original_dispatch_time_not_resume_or_summary_time': True,
        'public_elapsed_does_not_include_historical_RQ1_training_or_current_C0_preparation': True,
        'source_body_preparation_cost': ref(replay / 'SOURCE_BODY_PREPARATION_COST.json'),
        'source_selected': terminal['final_snapshot'],
        'selected_business_inventory_SHA256': digest(frozen_inventory),
        'immutable_selected_business_source': ref(frozen_path),
        'final_ready_path': str(ready_path), 'final_ready_SHA256': sha(ready_path),
        'private_reads_by_actor': 0, 'private_acceptance_not_in_this_record': True,
        'no_third_sample_after_public_PASS': True, 'RQ1_order_closure_and_SET_preserved': True,
        'seed_is_client_identity_not_server_determinism_claim': True,
        'single_trajectory_is_development_evidence_not_independent_repetition': True,
    }


def main():
    seals = [HERE / name for name in ('SOURCE_SEAL.json', 'FOLLOWUP_SOURCE_SEAL.json',
                                      'PURE_EXECUTION_ADAPTER_SOURCE_SEAL.json')]
    protected = {str(path): sha(path) for path in seals}
    for seal in seals[:2]:
        for path, expected in read(seal)['sources_SHA256'].items():
            assert sha(path) == expected, 'FROZEN_SOURCE_DRIFT: ' + path
            protected[path] = expected
    for index in (3, 4):
        for name in ('READY.json', 'FROZEN_BUSINESS_SOURCE.json', 'FROZEN_PUBLIC_SELECTION_CERTIFICATE.json'):
            path = HERE / 'final_ready' / str(index) / name
            protected[str(path)] = sha(path)
    summary_path = HERE / 'PUBLIC_PILOT_TRAJECTORIES248.json'
    archive_path = HERE / 'PUBLIC_PILOT_TRAJECTORIES248_BEFORE_CURSOR_CORRECTION.json'
    if not archive_path.exists():
        with archive_path.open('xb') as stream:
            stream.write(summary_path.read_bytes())
            stream.flush()
            os.fsync(stream.fileno())
    previous = read(archive_path)
    assert previous['schema'] == 'public-pilot-trajectories/1'
    rows = [build(index) for index in (3, 4)]
    summary = {
        'schema': 'public-pilot-trajectories/2',
        'at_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'correction_scope': 'Summary only; original algorithm source, READY, raw checkpoints and observations remain unchanged.',
        'old_summary_exact_archive': ref(archive_path),
        'old_complete_checkpoint_cursor_was_initial_replay_boundary_not_terminal': True,
        'rows': rows, 'aggregate_new_development_model_calls': sum(row['exact_new_settled_model_calls'] for row in rows),
        'aggregate_new_development_public_candidate_native_calls': sum(row['actual_physical_public_candidate_native_calls'] for row in rows),
        'aggregate_provider_usage': {key: sum(row['cumulative_provider_usage'][key] for row in rows)
                                     for key in rows[0]['cumulative_provider_usage']},
        'aggregate_usage_accounting_upper_CNY': str(sum((Decimal(row['cumulative_usage_accounting_upper_CNY']) for row in rows), Decimal('0'))),
        'new_model_POST_by_summary_actor': 0, 'new_native_by_summary_actor': 0,
        'private_reads_by_summary_actor': 0, 'ledger_writes_by_summary_actor': 0,
    }
    audit = {
        'schema': 'public-terminal-checkpoint-aggregate-audit/1',
        'at_UTC': summary['at_UTC'], 'kind': 'Existing-artifact audit, not an executable restart checkpoint',
        'rows': [{key: row[key] for key in (
            'index', 'task', 'complete_checkpoint_cursor', 'initial_replay_checkpoint',
            'latest_physical_native_boundary_checkpoint', 'terminal_count_derivation', 'public_terminal',
            'terminal_runtime_core_count_check', 'model_call_evidence', 'original_public_native_trajectory',
            'terminal_public_state_admission', 'scientific_T0_file',
            'elapsed_actual_first_POST_T0_to_public_terminal_STOP_seconds',
            'selected_business_inventory_SHA256', 'immutable_selected_business_source',
            'final_ready_path', 'final_ready_SHA256')} for row in rows],
        'protected_source_and_READY_SHA256_all_equal': True,
        'protected_files_SHA256': protected,
        'new_model_POST': 0, 'new_native': 0, 'private_reads': 0, 'ledger_writes': 0,
    }
    assert all(sha(path) == expected for path, expected in protected.items())
    save(HERE / 'PUBLIC_TERMINAL_CHECKPOINT_AUDIT248.json', audit)
    save(summary_path, summary)
    assert all(sha(path) == expected for path, expected in protected.items())
    print(json.dumps({'summary': ref(summary_path),
                      'checkpoint_audit': ref(HERE / 'PUBLIC_TERMINAL_CHECKPOINT_AUDIT248.json'),
                      'rows': [{'task': row['task'], 'terminal_cursor': row['complete_checkpoint_cursor'],
                                'usage': row['cumulative_provider_usage'],
                                'accounting_upper_CNY': row['cumulative_usage_accounting_upper_CNY'],
                                'public_elapsed_seconds': row['elapsed_actual_first_POST_T0_to_public_terminal_STOP_seconds']}
                               for row in rows],
                      'protected_unchanged': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()

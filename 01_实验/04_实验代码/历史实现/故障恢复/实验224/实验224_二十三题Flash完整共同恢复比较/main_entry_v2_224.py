"""Prepared ADD-only fresh Main queue. No calibration or V1 response reuse."""
from common166 import *
import copy, traceback
from decimal import Decimal
from publicpack_v2_224 import V
from budget_semantics224 import should_stop_queue
from main_identity_v2_224 import verify_worker
from main_environment_v2_224 import MainEnvironmentV2, authorize_main, install_isolated_main, PIN, GRANT, MAIN_VERSION

METHODS = {'main-agentless': ('AGENTLESS_FSE2025', 'AGENTLESS_FSE2025_4L4P4T_FLASH'),
           'main-ours': ('OURS_G153_PROGRESSIVE_SEMANTIC', 'G_PROGRESSIVE_SEMANTIC_FLASH')}


def run(mode):
    authorize_main(); grant = read(GRANT)
    assert mode in METHODS and METHODS[mode][1] in grant['approved_methods']
    identity = verify_worker(read(V / ('supervision_' + mode + '_v2main.json')))
    install_isolated_main()
    label, method = METHODS[mode]
    refs = {r['task_id']: r for r in read(E / 'data/selected_task_bindings.json')['tasks']}
    plans = read(E / 'ranking/plan_registry224.json')['plans']; order = read(PIN)['task_order']
    for index, task in enumerate(order):
        authorize_main()
        while index > int(read(GRANT)['allowed_through_index']):
            save(V / ('main_checkpoint_' + mode + '.json'), {'at_utc': now(), 'phase': 'WAIT_ROOT_PAIRED_WINDOW',
                 'task_id': task, 'task_index': index, 'actual_worker': identity, 'no_POST_native_in_boundary_wait': True})
            if time.time() >= NO_TEST: return
            time.sleep(1); authorize_main()
        out = V / 'main/recovery' / task / method
        assert task not in ('dask__dask-9378', 'getmoto__moto-5072'), 'CALIBRATION_MUST_NOT_REPLAY_IN_MAIN'
        if (out / 'result.json').exists():
            previous = read(out / 'result.json')
            assert previous.get('main_source_pin_sha256') == sha(PIN) and previous.get('version') == MAIN_VERSION
            if should_stop_queue(previous): return
            continue  # Completed observations never regenerate within Main.
        out.mkdir(parents=True, exist_ok=True)
        with (out / 'worker_started.json').open('x', encoding='utf-8') as f:
            f.write(canonical({'at_utc': now(), 'task_id': task, 'task_index': index, 'method': method,
                              'PID': identity['actual_self_PID'], 'creation_time100ns': identity['actual_self_creation_time100ns'],
                              'actual_worker': identity, 'main_source_pin_sha256': sha(PIN)}) + '\n')
        ref = copy.deepcopy(refs[task]); ref.update(G_frozen_plan=plans[task]['path'],
            _output_namespace='v2_auth_direct_publicpack/main/recovery',
            _native_namespace='v2_auth_direct_publicpack/main/native_active')
        env = None
        try:
            env = MainEnvironmentV2(ref, method)
            core = sys.modules['agentless178'] if label == 'AGENTLESS_FSE2025' else sys.modules['ranked_repair178']
            full = env.finalize(core.run(env))
        except Exception as error:
            private_births = set()
            for path in (out / 'final_preservation').rglob('*.process.json'):
                private_births.update((x['pid'], x['creation_time100ns']) for x in read(path).get('process_birth', []))
            full = {'task_id': task, 'method': method, 'status': 'ENGINEERING_UNKNOWN', 'success': None,
                    'error': {'type': type(error).__name__, 'message': str(error)}, 'traceback': traceback.format_exc(),
                    'LLM_calls': getattr(env, 'calls', 0), 'public_native_calls': getattr(env, 'native_calls', 0),
                    'hidden_acceptance_calls': len(private_births), 'runtime_core': {}}
        receipts = [read(path) for path in out.glob('llm/*_finance_receipt.json')]
        settled = [r for r in receipts if r.get('status') == 'SETTLED']
        fee = sum((Decimal(r['usage_peak_cost_CNY']) for r in settled), Decimal(0))
        full.update(version=MAIN_VERSION, scientific_method=label, primary_eligible=True,
                    calibration_only=False, main_source_pin_sha256=sha(PIN), source_seal_sha256=sha(V / 'source_seal_v2.json'),
                    pack_registry_sha256=sha(V / 'pack_registry_v2.json'), new_fees_CNY=str(fee), fees_CNY=str(fee),
                    new_paid_API=len(settled), reused_calibration_or_V1_outputs=0, actual_worker=identity)
        save(out / 'result.json', full)
        append(V / ('completed_' + mode + '_v2main.jsonl'), {k: full.get(k) for k in
            ('task_id', 'scientific_method', 'status', 'success', 'new_paid_API', 'new_fees_CNY', 'LLM_calls', 'public_native_calls', 'hidden_acceptance_calls')})
        print(canonical({k: full.get(k) for k in ('task_id', 'status', 'success', 'new_fees_CNY')}), flush=True)
        if should_stop_queue(full): return


if __name__ == '__main__': run(sys.argv[1])

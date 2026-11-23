"""V2 preparation or explicitly granted two-case calibration. Never run by default."""
from common166 import *
import ast, copy
from decimal import Decimal
from publicpack_v2_224 import V, build, decode, render
from environment_v2_224 import EnvironmentV2, authorize_v2, body_v2, initial_index_v2, ROOT_V2_PROTOCOL, ROOT_V2_SHA
from budget_semantics224 import should_stop_queue

VERSION = 'V2_AUTH_DIRECT_PUBLICPACK'
ORDER = ['dask__dask-9378', 'getmoto__moto-5072']


def prepare():
    build()
    old = read(E / 'protocol224.json')
    protocol = {**copy.deepcopy(old), 'schema': 'Exp224-V2-author-direct-publicpack/1',
                'version': VERSION, 'execution_authorized': False, 'calibration_order': ORDER,
                'same23_C0_inputs_and_G153_plans': True, 'source_v1_seal_sha256': sha(E / 'fresh_ready_seal224.json'),
                'AL_interface': 'Original author issue/tree/skeleton/coarse/fine text and SEARCH/REPLACE; no added shared-reader loop',
                'G_mechanism': 'Original ranked_repair178; at most3 progressive cumulative semantic corrections',
                'common_pack': 'Exact lossless public failure/history line dictionary, every node/phase/occurrence reversible; same pack all3 arms',
                'first_case_gate': 'Before second case require actual AL patch and reproduction responses and actual public native; never reroll failed first case',
                'finance': 'Explicit root Pilot grant required; continuous ledger and remaining Pilot gates unchanged; no borrowing Main',
                'primary_eligible': False, 'V1_scores_not_merged': True}
    protocol['budget'].pop('max_reader_rounds', None)
    save(V / 'protocol_v2.json', protocol)
    import agentless178 as al
    from agentless_bridge.local_core166 import structure
    from agentless_bridge import official_core166 as official
    registry = read(V / 'pack_registry_v2.json'); refs = {x['task_id']: x for x in read(E / 'data/selected_task_bindings.json')['tasks']}
    bodies = []
    for row in registry['tasks']:
        ref = refs[row['task_id']]; pack = read(row['path']); decoded = decode(pack)
        files = {p: (Path(ref['template']) / p).read_text('utf-8') for p in pack['c0_business_paths_sha256']}
        assert all(sha(Path(ref['template']) / p) == h for p, h in pack['c0_business_paths_sha256'].items())
        tree = official.show_project_structure(structure(files)).strip()
        problem = 'Recover the observed public failure and preserve already passing ordinary behavior. Original issue background: ' + decoded['original_issue']
        problem += '\nObserved current public recovery failure: ' + json.dumps(initial_index_v2(pack), ensure_ascii=False, sort_keys=True)
        for role, template in [('suspicious_files', 'obtain_relevant_files_prompt'), ('irrelevant_folders', 'obtain_irrelevant_files_prompt')]:
            prompt = al.PROMPTS[template].format(problem_statement=problem, structure=tree).strip()
            messages = [{'role': 'system', 'content': 'You are a helpful assistant. Only the supplied public business source and public test interfaces are available. Fixed tests, private tests and references are immutable; never access them.'}, {'role': 'user', 'content': prompt}]
            body = body_v2('agentless_' + role, messages, 0, al.seed(row['task_id'], role, 0), 8192, row['task_id'], al.METHOD, pack)
            n = len(canonical(body).encode()); bound = n + 4096 * len(body['messages']) + 2048
            bodies.append({'task_id': row['task_id'], 'role': role, 'kind': 'conservative_deterministic_author_stage_body_bound',
                           'body_utf8_bytes': n, 'input_token_conservative_byte_bound': bound,
                           'peak_request_reserve_CNY': str((Decimal(bound) * 2 + Decimal(8192) * 8) / 1000000),
                           'body_sha256': digest(body), 'no_tools': 'tools' not in body,
                           'context_transport_byte_gate_pass': bound + 8192 <= 1048576})
    preflight = {'version': VERSION, 'new_model_native_private_Gold': 0, 'actors_constructed': 0,
                 'all23_roundtrip_pass': True, 'c0_all23_business_source_verified': True,
                 'requests': bodies, 'max_conservative_first_stage_body_bytes': max(x['body_utf8_bytes'] for x in bodies),
                 'actual_future_selected_coarse_fine_patch_bodies': 'Unknown until fixed model selections; each actual body is hashed and bounded before POST. No clipping or saved V1 responses used by V2 actors.',
                 'calibration_first_requests': [x for x in bodies if x['task_id'] in ORDER],
                 'fee_policy': 'Peak full-body byte upper reserve, input2/output8 per1M; preflight makes no ledger reservation, balance request or POST. Root owns updated budget authorization.'}
    save(V / 'preflight_v2.json', preflight)
    from check_v2_224 import check
    check()
    for path in (E / 'publicpack_v2_224.py', E / 'environment_v2_224.py', E / 'entry_v2_224.py', E / 'supervise_v2_224.py'):
        ast.parse(path.read_text('utf-8-sig'))
    previous = read(E / 'fresh_ready_seal224.json')
    sealed = {**previous['sources'], **previous['inputs']}
    sealed[str(ROOT_V2_PROTOCOL)] = ROOT_V2_SHA
    specs = [OLD / 'agentless_bridge/official_prompts166.json', OLD / 'agentless_bridge/official_core166.py',
             OLD / 'agentless_bridge/local_core166.py', OLD / 'agentless_source_derivative178.json',
             OLD / 'agentless178.py', OLD / 'ranked_repair178.py']
    for path in specs: sealed[str(path)] = sha(path)
    for path in (E / 'publicpack_v2_224.py', E / 'environment_v2_224.py', E / 'entry_v2_224.py', E / 'supervise_v2_224.py', E / 'check_v2_224.py', V / 'pure_checks_v2.json', V / 'protocol_v2.json', V / 'pack_registry_v2.json', V / 'preflight_v2.json'):
        sealed[str(path)] = sha(path)
    sealed.update({x['path']: x['sha256'] for x in registry['tasks']})
    for row in registry['tasks']:
        sealed.update(read(row['path'])['read_only_public_source_files_sha256'])
    assert all(sha(p) == h for p, h in sealed.items()), 'V1_OR_V2_SOURCE_INPUT_DRIFT'
    save(V / 'source_seal_v2.json', {'version': VERSION, 'prepared_only': True, 'sealed_files': sealed,
         'read_only_original_specs': {str(p): sha(p) for p in specs},
         'V1_seal_sha256': sha(E / 'fresh_ready_seal224.json'), 'V2_pack_registry_sha256': sha(V / 'pack_registry_v2.json'),
         'financial_counter_policy': 'Only SETTLED receipts count as paid API; rejected/unknown receipts remain separately preserved and do not become successes.',
         'new_model_native_private_Gold': 0, 'calibration_order': ORDER,
         'CLI': [str(PYTHON), '-B', str(E / 'supervise_v2_224.py'), 'calibrate-agentless']})
    print(canonical({'prepared_only': True, 'source_seal_sha256': sha(V / 'source_seal_v2.json'),
                     'pack_registry_sha256': sha(V / 'pack_registry_v2.json'),
                     'max_body_bound_bytes': preflight['max_conservative_first_stage_body_bytes']}))


def run(mode):
    authorize_v2()
    assert mode in ('calibrate-agentless', 'calibrate-ours')
    label = 'AGENTLESS_FSE2025' if mode.endswith('agentless') else 'OURS_G153_PROGRESSIVE_SEMANTIC'
    method = 'AGENTLESS_FSE2025_4L4P4T_FLASH' if label == 'AGENTLESS_FSE2025' else 'G_PROGRESSIVE_SEMANTIC_FLASH'
    refs = {x['task_id']: x for x in read(E / 'data/selected_task_bindings.json')['tasks']}; plans = read(E / 'ranking/plan_registry224.json')['plans']
    for index, task in enumerate(ORDER):
        authorize_v2(); grant = read(V / 'root_calibration_grant_v2.json')
        if index > int(grant.get('allowed_calibration_index', 0)): return
        if index:
            first = read(V / 'calibration/recovery' / ORDER[0] / 'AGENTLESS_FSE2025_4L4P4T_FLASH/result.json')
            if not first.get('actual_patch_repro_native_gate'): return
        ref = copy.deepcopy(refs[task]); ref.update(G_frozen_plan=plans[task]['path'],
             _output_namespace='v2_auth_direct_publicpack/calibration/recovery', _native_namespace='v2_auth_direct_publicpack/calibration/native_active')
        out = E / ref['_output_namespace'] / task / method
        if (out / 'result.json').exists():
            previous = read(out / 'result.json')
            assert previous.get('version') == VERSION and previous.get('source_seal_sha256') == sha(V / 'source_seal_v2.json'), 'V2_COMPLETED_CASE_BINDING_DRIFT'
            if should_stop_queue(previous): return
            continue  # Completed same-version observations never run again.
        env = EnvironmentV2(ref, method)
        core = sys.modules['agentless178'] if label == 'AGENTLESS_FSE2025' else sys.modules['ranked_repair178']
        result = core.run(env); full = env.finalize(result)
        receipts = [read(p) for p in out.glob('llm/*_finance_receipt.json')]
        settled = [r for r in receipts if r.get('status') == 'SETTLED']
        fee = sum((Decimal(r['usage_peak_cost_CNY']) for r in settled), Decimal(0))
        events = lines(out / 'stage_ledger.jsonl')
        roles = [x['evidence']['role'] for x in events if x['stage'] == 'Flash_actual_response224']
        gate = 'agentless_patch' in roles and 'agentless_reproduction' in roles and env.native_calls > 0
        full.update(version=VERSION, primary_eligible=False, calibration_only=True, fees_CNY=str(fee),
                    new_fees_CNY=str(fee), new_paid_API=len(settled), scientific_method=label,
                    actual_patch_repro_native_gate=gate, pack_registry_sha256=sha(V / 'pack_registry_v2.json'),
                    source_seal_sha256=sha(V / 'source_seal_v2.json'), reused_v1_outputs=0)
        save(out / 'result.json', full)
        append(V / ('completed_' + mode + '.jsonl'), {k: full.get(k) for k in ('task_id', 'status', 'success', 'fees_CNY', 'actual_patch_repro_native_gate')})
        print(canonical({'task_id': task, 'status': full.get('status'), 'success': full.get('success'), 'actual_patch_repro_native_gate': gate}), flush=True)
        if should_stop_queue(full) or (index == 0 and label == 'AGENTLESS_FSE2025' and not gate): return


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'prepare'
    if mode == 'prepare': prepare()
    else: run(mode)

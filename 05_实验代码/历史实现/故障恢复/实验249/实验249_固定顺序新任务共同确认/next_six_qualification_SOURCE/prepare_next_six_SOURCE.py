"""Minimal identity qualification for fixed natural slots 7--12, source only."""
import ast
import copy
import hashlib
import json
import sys
from pathlib import Path

N = Path(__file__).resolve().parent
Q = N.parent
R = Path('D:/Code/毕设/graduate-thesis-experiments')
TASKS = ['python__mypy-10392', 'python__mypy-11134', 'getmoto__moto-7081',
    'getmoto__moto-6212', 'getmoto__moto-5406', 'getmoto__moto-6387']

def read(p): return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p): return {'path': str(Path(p).resolve()), 'sha256': sha(p)}
def write(p, value):
    p = Path(p).resolve()
    if not p.is_relative_to(N): raise RuntimeError('NEXT_SIX_SOURCE_WRITE_SCOPE')
    p.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    if p.exists() and p.read_bytes() != raw: raise RuntimeError('NEXT_SIX_SOURCE_ALREADY_FROZEN:' + str(p))
    if not p.exists(): p.write_bytes(raw)
def source(p, raw):
    if p.exists() and p.read_bytes() != raw: raise RuntimeError('NEXT_SIX_SOURCE_ALREADY_WRITTEN:' + str(p))
    if not p.exists(): p.write_bytes(raw)
def replace(text, before, after):
    if text.count(before) != 1: raise RuntimeError('NEXT_SIX_SOURCE_ANCHOR:' + before)
    return text.replace(before, after)

def prepare():
    common = (Q / 'common249.py').read_text('utf-8-sig')
    begin = common.index('TASKS = '); end = common.index('CONTROLLER = ', begin)
    common = common[:begin] + 'TASKS = ' + repr(TASKS) + '\nFIRST_TWO = TASKS  # Legacy alias; exact fixed new six identities only.\n' + common[end:]
    common = replace(common, '        g = self.value\n', "        g = self.value\n        if self.action != 'identity': raise RuntimeError('NEXT_SIX_ONLY_IDENTITY_EXECUTION_SOURCE_READY')\n")
    source(N / 'common_next_six249.py', common.encode('utf-8'))
    parent_native = Q / 'native249_ROOT_BATCH3_R2.py'; native = parent_native.read_text('utf-8-sig'); tree = ast.parse(native)
    keep = ('load_jobs', 'stopped', 'parent_member', 'supervise', 'run_identity')
    functions = {n.name: ast.get_source_segment(native, n) for n in tree.body if isinstance(n, ast.FunctionDef)}
    result = '"""Root-granted identity only; zero business imports or tests.\n\nCurrent C0 and masking remain closed pending separate source qualification.\n"""\nimport argparse\nimport ctypes\nimport subprocess\nimport types\nfrom common_next_six249 import *\n\n'
    result += '\n\n'.join(functions[name] for name in keep)
    result += '''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=('identity',), required=True)
    parser.add_argument('--task', choices=TASKS, required=True)
    parser.add_argument('--root-grant', required=True)
    parser.add_argument('--worker', action='store_true')
    args = parser.parse_args()
    grant = Grant(args.root_grant, 'identity', [args.task])
    if grant.value.get('identity_entry_SHA256') != sha(__file__):
        raise RuntimeError('NEXT_SIX_IDENTITY_ENTRY_NOT_EXACTLY_BOUND')
    jobs = load_jobs(grant)
    out = E / 'qualification' / args.task / 'identity'
    if not args.worker:
        return supervise(args, grant, out, jobs)
    if not parent_member(jobs, grant.value['parent_owned_job_name']):
        raise RuntimeError('NEXT_SIX_WORKER_NOT_IN_EXACT_PARENT_JOB')
    identity = module('_next_six_controller_identity', E / 'physical_identity249.py')
    save(out / 'CONTROLLER_SELF_IDENTITY.json', identity.capture())
    row, contract = binding(args.task)
    intent(out / 'WORKER_STARTED_ONCE.json', {'UTC': now(), 'stage': 'identity', 'Root_grant_SHA256': grant.sha256})
    run_identity(args, grant, out, jobs, row, contract)


if __name__ == '__main__': main()
'''
    source(N / 'native_next_six249.py', result.encode('utf-8'))
    source(N / 'physical_identity249.py', (Q / 'physical_identity249.py').read_bytes())

    plan_path = R / '结论/20261009_复盘再实验/新确认集与共同预算_前瞻.json'; plan = read(plan_path)
    if plan['new_main_order'][6:12] != TASKS: raise RuntimeError('NEXT_SIX_NATURAL_ORDER_MISMATCH')
    source23 = R / '工作区/1008-2320-baseline-main/baseline2025_common_readiness/new_public_contract_preflight/expanded_observed_failure23_manifest.json'
    registry = read(source23); old_contracts = R / '实验/实验241_Agentless新确认集21_生成测试ScopeV2/candidate'
    rows = []; inputs = {str(p): sha(p) for p in (plan_path, source23, Q / 'protocol249_SOURCE.json', Q / 'SOURCE_SEAL249.json')}
    source_paths = [parent_native, Q / 'common249.py', Q / 'physical_identity249.py', Q / 'native_capacity249_ROOT_V11_SOURCE.py',
        R / '工作区/1011-our19/native_executor242_prospective.py', R / '工作区/1010-unified-six/native_four_slots_v5_SOURCE.py']
    schedule = R / '工作区/1010-unified-six/ROOT_COMMON_NATIVE_SCHEDULING_V5_FOUR_SOURCE.json'; inputs[str(schedule)] = sha(schedule)
    for index, task in enumerate(TASKS, 6):
        original = old_contracts / task / 'public_contract.json'; c = read(original)
        target = N / 'contracts' / task / 'public_contract.json'; target.parent.mkdir(parents=True, exist_ok=True); source(target, original.read_bytes())
        if c['task_id'] != task or sha(c['pack']) != c['pack_sha256'] or sha(c['source_inventory_reference']) != c['source_inventory_reference_sha256']:
            raise RuntimeError('NEXT_SIX_ORIGINAL_PUBLIC_CONTRACT_INPUT_DRIFT:' + task)
        item = next(row for row in registry['tasks'] if row['task_id'] == task)
        if c['public_target_nodes'] != item['public_goal_nodes'] or c['ordinary_nodes'] != item['public_ordinary_nodes']:
            raise RuntimeError('NEXT_SIX_PUBLIC_G_O_DECLARATION_DRIFT')
        python = Path(c['logical_product_python']); cfg = python.parent.parent / 'pyvenv.cfg'
        cfg_values = {k.strip(): v.strip() for line in cfg.read_text('utf-8-sig').splitlines() if '=' in line for k, v in [line.split('=', 1)]}
        base = Path(cfg_values.get('executable') or str(Path(cfg_values['home']) / 'python.exe')).resolve()
        private_path = (Path(item['binding']['task_path']) / 'task_manifest.json').resolve()
        row = {'task_id': task, 'natural_slot_one_based': index + 1, 'plan21_index_zero_based': index,
            'public_contract': str(target), 'public_contract_SHA256': sha(target), 'original_public_contract': bind(original),
            'original_C0_template': c['template'], 'c0_business_inventory_SHA256': c['c0_business_inventory_sha256'],
            'business_paths_count': len(c['c0_business_paths_sha256']), 'pack': bind(c['pack']),
            'source_inventory_reference': bind(c['source_inventory_reference']),
            'public_goal_nodes': c['public_target_nodes'], 'public_ordinary_nodes': c['ordinary_nodes'],
            'original_frozen_G_O_source_root': c['frozen_public_test_root'], 'original_frozen_inventory_SHA256': c['frozen_inventory_sha256'],
            'original_harness': c['harness'], 'original_harness_sources_SHA256': c['harness_sources'],
            'logical_product_python': str(python), 'logical_product_python_SHA256': sha(python),
            'pyvenv_cfg': str(cfg), 'pyvenv_cfg_SHA256': sha(cfg), 'configured_python_version': cfg_values.get('version'),
            'configured_base_candidate': str(base), 'configured_base_candidate_SHA256': sha(base),
            'configured_path_is_not_actual_physical_identity': True,
            'Root_only_original_isolation_manifest_path': str(private_path), 'private_metadata_SHA256_not_read_pending_Root': True,
            'historically_exposed': True, 'exposure_source': bind(plan_path),
            'prior_development_or_mechanism_tags_not_cleared': True, 'not_claimed_unseen_or_training_disjoint': True,
            'known_prior_mechanism_development_observation': task == 'python__mypy-10392',
            'old_qualification_or_result_not_inherited': True, 'identity_qualified': False, 'current_C0_qualified': False,
            'public_mask_qualified': False, 'current_C0_status': 'UNRUN_CURRENT_QUALIFICATION_UNKNOWN',
            'model_native_tests_private_finance': 0}
        rows.append(row)
        for p in (original, target, Path(c['pack']), Path(c['source_inventory_reference']), python, cfg, base): inputs[str(p)] = sha(p)
        for p, expected in c['harness_sources'].items():
            if sha(p) != expected: raise RuntimeError('NEXT_SIX_ORIGINAL_HARNESS_DRIFT')
            source_paths.append(Path(p))
    amendment = Path(plan['initial_qualification_amendment_V2']['certificate_path'])
    if sha(amendment) != plan['initial_qualification_amendment_V2']['certificate_SHA256']: raise RuntimeError('OLD_SYNTAX_OBSERVATION_REFERENCE_DRIFT')
    inputs[str(amendment)] = sha(amendment)
    blockers = {'schema': 'EXP249-next-six-explicit-pending-gates/1', 'all_current_C0_qualifications': False,
        'python__mypy-10392': {'historical_observer_certificate': bind(amendment), 'historical_classification': 'C0_COLLECTION_BLOCKED_BY_LEGAL_BUSINESS_SYNTAX',
            'current_classification': 'UNKNOWN_UNRUN', 'old_certificate_not_inherited': True,
            'fresh_collection_failure_may_be_reported_as_mechanism_evidence_only': True, 'never_fabricate_per_Goal_completed_FAIL': True},
        'mypy_public_mask': {'status': 'PENDING_DATA_DRIVEN_CASE_MAPPING',
            'unmapped_case_source_must_not_be_actor_readable': True, 'safe_conservative_omission_requires_separate_Root_source_review': True},
        'all_six_mask_and_G_O': {'status': 'CLOSED_SOURCE_NOT_READY', 'original_G_O_unchanged': True,
            'original_public_and_private_test_sources_not_read_by_preparation': True,
            'new_Root_mask_scope_and_complete_current_guarded_G_O_STOP_required': True,
            'V11_capacity_source': bind(Q / 'native_capacity249_ROOT_V11_SOURCE.py'), 'V11_not_executed_in_identity': True},
        'fixed_slots_retained_on_unknown_no_replacement': True}
    write(N / 'KNOWN_QUALIFICATION_BLOCKERS_SOURCE.json', blockers)
    protocol = {'schema': 'EXP249-next-six-natural-slots7-12-identity-only-source/1', 'task_order': TASKS,
        'natural_slots_one_based': list(range(7, 13)), 'selection_rule': plan['selection_rule'], 'source_plan21': bind(plan_path),
        'historically_exposed_cohort_label': plan['new_cohort_name'], 'development_tags_not_reset': True,
        'old_first_six_protocol_not_extended_or_edited': True, 'task_count_prepared': 6, 'task_count_currently_qualified': 0,
        'actual_ready_stage': 'identity_only_no_business_imports', 'identity_OS_roots_per_task': 1,
        'source_defined_but_not_implemented_stages': ['trusted_mask', 'current_original_G_O_and_masked_channel'],
        'parent_Job_active_lifetime_limits': [8, 24], 'V5_four_shared_native_slots_unchanged': True,
        'common_qualification_cost_separate_from_scientific_trial_T0': True, 'old_clocks_or_response_reuse': False,
        'continuous_existing_finance_required_if_later_expansion_granted': True, 'qualification_has_no_finance_client': True,
        'no_method_baseline_repair_queue_training_or_forward_prepared': True,
        'source_only': True, 'READY': False, 'root_authorized': False, 'native_authorized': False,
        'model_authorized': False, 'private_execution_authorized': False, 'finance_authorized': False}
    write(N / 'protocol249_SOURCE.json', protocol)
    write(N / 'TASK_BINDINGS249_SOURCE.json', {'schema': 'EXP249-next-six-public-task-bindings/1', 'tasks': rows,
        'original_unmasked_tests_private_metadata_Gold_not_read': True, 'historical_method_results_not_used_for_selection': True})
    inventory = {'original_source_paths': sorted(set(str(p.resolve()) for p in source_paths)), 'public_inputs_SHA256': inputs}
    write(N / 'SOURCE_INPUTS_PREPARATION.json', inventory)
    print(json.dumps({'status': 'NEXT_SIX_METADATA_IDENTITY_SOURCE_PREPARED', 'tasks': TASKS, 'actual_calls': 0}, ensure_ascii=False), flush=True)

def seal():
    inputs = read(N / 'SOURCE_INPUTS_PREPARATION.json'); sources = {p: sha(p) for p in inputs['original_source_paths']}
    for p in sorted(N.glob('*.py')): ast.parse(p.read_text('utf-8-sig'), filename=str(p)); sources[str(p)] = sha(p)
    public = dict(inputs['public_inputs_SHA256'])
    controller = R / '工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'
    for p in (controller, controller.parent.parent / 'pyvenv.cfg'):
        public[str(p)] = sha(p)
    for name in ('SOURCE_INPUTS_PREPARATION.json', 'protocol249_SOURCE.json', 'TASK_BINDINGS249_SOURCE.json', 'KNOWN_QUALIFICATION_BLOCKERS_SOURCE.json', 'SOURCE_VALIDATION.json'):
        public[str(N / name)] = sha(N / name)
    if read(N / 'SOURCE_VALIDATION.json')['status'] != 'PASS': raise RuntimeError('NEXT_SIX_SOURCE_VALIDATION_REQUIRED')
    sp = N / 'SOURCE_SEAL249.json'; write(sp, {'schema': 'EXP249-next-six-identity-source-seal/1', 'sources_SHA256': sources, 'public_inputs_SHA256': public,
        'actual_calls': 0, 'identity_only_source_ready': True, 'mask_G_O_not_qualified': True, 'READY': False})
    controller = R / '工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'; rows = []
    for task in TASKS:
        c = read(N / 'contracts' / task / 'public_contract.json')
        base = {'schema': 'EXP249-next-six-exact-Root-action-grant-false/1', 'root_authorized': False, 'native_authorized': False,
            'model_authorized': False, 'private_execution_authorized': False, 'finance_authorized': False,
            'trusted_original_test_source_read_authorized': False, 'task_ids': [task], 'lease_end_UTC': None,
            'root_stop_paths': [str(Q / 'ROOT_STOP_REQUESTED.json')], 'protocol_SHA256': sha(N / 'protocol249_SOURCE.json'),
            'source_seal_SHA256': sha(sp), 'controller_launch_python': str(controller), 'controller_launch_SHA256': sha(controller), 'source_only': True}
        identity = {**base, 'action': 'identity', 'max_identity_OS_roots': 1, 'no_business_import_or_pytest': True,
            'identity_entry_SHA256': sha(N / 'native_next_six249.py'), 'parent_owned_job_name': 'RootExp249_NextSix_identity_' + task.replace('-', '_'),
            'execution_source_ready': True}
        gp = N / 'grant_templates' / (task + '.identity.false.json'); write(gp, identity)
        closed = {**base, 'action': 'current_C0', 'max_original_G_O_native': 1, 'max_masked_ordinary_native': 1,
            'trusted_original_G_O_oracle_execution_authorized': False, 'execution_source_ready': False,
            'exact_G_O_nodes': list(dict.fromkeys(c['public_target_nodes'] + c['ordinary_nodes'])),
            'current_identity_receipt_SHA256': None, 'current_identity_parent_STOP_SHA256': None, 'masked_scope_SHA256': None,
            'current_process_clock_policy': None, 'common_precise_clock_contract': None, 'Root_current_process_precise_clock_admitted': False,
            'activation_requires_separate_source_seal_and_Root_current_qualification_policy': True}
        write(N / 'grant_templates' / (task + '.current_C0.closed_not_ready.json'), closed)
        row = next(x for x in read(N / 'TASK_BINDINGS249_SOURCE.json')['tasks'] if x['task_id'] == task)
        masking = {**base, 'action': 'materialize', 'max_materialized_tasks': 1, 'execution_source_ready': False,
            'trusted_masking_inputs': {task: {'manifest_path': row['Root_only_original_isolation_manifest_path'], 'manifest_SHA256': None}},
            'unmapped_data_driven_cases_not_readable': True, 'activation_requires_separate_safe_mask_source_seal': True}
        write(N / 'grant_templates' / (task + '.materialize.closed_not_ready.json'), masking)
        rows.append({'task_id': task, 'closed_identity_grant': bind(gp), 'actual_authorized': False,
            'argv': [str(controller), '-X', 'utf8', '-B', str(N / 'native_next_six249.py'), '--stage', 'identity', '--task', task,
                '--root-grant', str(N / 'ROOT_RELEASES' / (task + '.identity.actual.json'))]})
    manifest = N / 'FIRST_IDENTITY_COMMANDS_SOURCE.json'
    write(manifest, {'schema': 'EXP249-next-six-first-real-identity-command-source/1', 'source_seal': bind(sp), 'commands': rows,
        'first_task': TASKS[0], 'first_real_argv': rows[0]['argv'], 'actual_authorized': False, 'current_C0_qualified_count': 0,
        'Root_identity_sign_fields': ['root_authorized=true', 'native_authorized=true', 'finite lease_end_UTC', 'source_only=false'],
        'all_other_permissions_remain_false': True, 'mask_G_O_grants_not_executable': True, 'actual_calls': 0})
    print(json.dumps({'status': 'NEXT_SIX_IDENTITY_SOURCE_READY_FALSE', 'seal': bind(sp), 'commands': bind(manifest), 'current_C0_qualified_count': 0, 'actual_calls': 0}, ensure_ascii=False), flush=True)

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument('--stage', choices=('prepare', 'seal'), required=True); args = ap.parse_args()
    if args.stage == 'prepare': prepare()
    else: seal()

"""Freeze six natural tasks, three repeats and exact zero-model gate sources."""
import ast
import shutil
from common249 import *


def main():
    if (E / 'SOURCE_SEAL249.json').exists():
        raise RuntimeError('EXP249_SOURCE_ALREADY_SEALED_NO_OVERWRITE')
    source23 = R / '工作区/1008-2320-baseline-main/baseline2025_common_readiness/new_public_contract_preflight/expanded_observed_failure23_manifest.json'
    plan21 = R / '结论/20261009_复盘再实验/新确认集与共同预算_前瞻.json'
    registry = read(source23)
    plan = read(plan21)
    if plan['new_main_order'][:6] != TASKS:
        raise RuntimeError('EXP249_NOT_FROZEN_NATURAL_FIRST_SIX')
    review = R / '工作区/1011-exp247-ours-unbudgeted/实验/实验247_本文完整排序证据无外部预算/NEXT_CONFIRMATION_SOURCE_REVIEW.json'
    before = read(review)
    if [v['task_id'] for v in before['selected_first_two']] != FIRST_TWO:
        raise RuntimeError('EXP249_PREDECLARED_FIRST_TWO_DRIFT')
    rows = []
    inputs = {str(p): sha(p) for p in (source23, plan21, review)}
    source_files = [OLD / 'native_executor242_prospective.py', OLD / 'native_capacity_v10.py', OLD / 'progress_guard240.py',
                    COMMON / 'native_four_slots_v5_SOURCE.py', COMMON / 'precise_product_bootstrap_v9_SOURCE.py',
                    COMMON / 'prepare_public_test_view_proposal.py',
                    R / '工作区/1002-exp129-expanded-baselines/实验/实验129_扩展基线与恢复证据/executor/run.py']
    shared_descriptor = read(V14 / 'SOURCE_READY_FALSE.json')
    for path, expected in shared_descriptor['sources'].items():
        if sha(path) != expected:
            raise RuntimeError('EXP249_V14_SOURCE_DRIFT')
        source_files.append(Path(path))
    for p in (V14 / 'SOURCE_READY_FALSE.json', COMMON / 'ROOT_COMMON_NATIVE_SCHEDULING_V5_FOUR_SOURCE.json',
              COMMON / 'COMMON_MASKED_PUBLIC_TEST_SCOPE.json',
              E / 'common249.py', E / 'materialize249_ROOT_ONLY.py', E / 'native249.py', E / 'physical_identity249.py'):
        inputs[str(p)] = sha(p)
    for task in TASKS:
        old = PUBLIC_CONTRACTS / task / 'public_contract.json'
        c = read(old)
        target = E / 'contracts' / task / 'public_contract.json'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(old.read_bytes())
        if sha(target) != sha(old) or sha(c['pack']) != c['pack_sha256']:
            raise RuntimeError('EXP249_ORIGINAL_PUBLIC_INPUT_CHANGED')
        oldrow = next(v for v in registry['tasks'] if v['task_id'] == task)
        private_path = Path(oldrow['binding']['task_path']) / 'task_manifest.json'
        python = Path(c['logical_product_python'])
        cfg = python.parent.parent / 'pyvenv.cfg'
        config = {k.strip(): v.strip() for line in cfg.read_text('utf-8-sig').splitlines() if '=' in line for k, v in [line.split('=', 1)]}
        candidate_base = Path(config.get('executable') or str(Path(config['home']) / 'python.exe')).resolve()
        row = {'task_id': task, 'plan21_index_zero_based': TASKS.index(task), 'old_qualification_status_not_inherited': True,
               'public_contract': str(target), 'public_contract_SHA256': sha(target), 'original_public_contract': str(old),
               'original_public_contract_SHA256': sha(old), 'pack': c['pack'], 'pack_SHA256': c['pack_sha256'],
               'c0_business_inventory_SHA256': c['c0_business_inventory_sha256'],
               'public_goal_nodes': c['public_target_nodes'], 'public_ordinary_nodes': c['ordinary_nodes'],
               'logical_product_python': str(python), 'logical_product_python_SHA256': sha(python),
               'pyvenv_cfg': str(cfg), 'pyvenv_cfg_SHA256': sha(cfg),
               'configured_base_candidate': str(candidate_base), 'configured_base_candidate_SHA256': sha(candidate_base),
               'configured_path_is_not_actual_physical_identity': True,
               'Root_only_original_isolation_manifest_path': str(private_path.resolve()),
               'Root_only_isolation_metadata_SHA256_pending_Root_grant': True,
               'original_independent_once_standard_preserved': True,
               'identity_qualified': False, 'current_C0_qualified': False, 'model_authorized': False,
               'mechanical_actual_scope_now': task in FIRST_TWO}
        rows.append(row)
        for p in (old, target, Path(c['pack']), Path(c['source_inventory_reference']), python, cfg, candidate_base):
            inputs[str(p)] = sha(p)
        for path, expected in c['harness_sources'].items():
            if sha(path) != expected:
                raise RuntimeError('EXP249_ORIGINAL_HARNESS_SOURCE_DRIFT')
            source_files.append(Path(path))
    protocol = {'schema': 'EXP249-frozen-natural-six-three-repeats/1', 'frozen_UTC': now(),
        'task_order': TASKS, 'first_mechanical_tasks': FIRST_TWO, 'method_order': METHODS,
        'source23_SHA256': sha(source23), 'plan21_SHA256': sha(plan21),
        'selection_rule': plan['selection_rule'], 'task_count': 6, 'planned_complete_repeats_per_method_task': 3,
        'trial_ids': ['trial1', 'trial2', 'trial3'], 'trial_master_seeds': [2026101201, 2026101202, 2026101203],
        'trial_is_not_new_issue': True, 'unit_of_independent_task_analysis': 'issue',
        'all_trials_reported_no_best_of_three_substitution': True,
        'schedule': 'task natural order; trial1/trial2/trial3; all three methods per trial before using results to decide expansion',
        'original_248_development_tasks_excluded_from_this_six': ['python__mypy-15155', 'getmoto__moto-5516'],
        'not_claimed_globally_unseen_or_RQ1_training_disjoint': True,
        'model': 'deepseek-flash', 'thinking': 'disabled',
        'full_internal_method_parameters': {
            'OURS_CURRENT_FAILURE_BOUND_248': {'max_attempts': 3, 'RQ1_order': 'existing model15 AB_GLOBAL frozen ranking', 'closure': True, 'SET': True, 'current_feedback_binding': True, 'extra_failure_seeds': False},
            'AGENTLESS_FSE2025': {'fine_localization_samples': 4, 'repair_samples_per_context': 10, 'total_patch_slots': 40, 'reproduction_samples': 40},
            'ENAGENT_ICSE2026': {'ensemble_N': 3, 'coder_max_steps': 200, 'selector_max_turn': 30}},
        'method_generation_source_seals_pending_separate_Root_release_after_development_pilot': True,
        'fixed_resource_observation_endpoint': {'seconds': 1800, 'model_calls': 128, 'output_tokens': 131072,
             'qualified_repair_required_before_any_cap': True, 'same_actual_trajectory_as_natural_endpoint': True},
        'natural_endpoint': {'external_research_cutoff_disabled_until_method_natural_stop': True,
             'finance_unknown_or_safety_stop_is_censored_not_algorithm_failure': True,
             'internal_parameters_unchanged_from_fixed_endpoint': True},
        'timing': {'scientific_trial_T0': 'first actual model POST callback', 'common_qualification_and_prior_RQ1_cost': 'separately disclosed for all methods',
                   'no_old_clock_or_paid_response_reuse': True},
        'mechanical': {'product_identity_probe_per_task': 1, 'original_G_O_native_per_task': 1,
             'masked_v14_ordinary_native_per_task': 1, 'per_native_timeout_seconds': 300,
             'one_mechanical_repair_minutes_max': 5, 'failed_qualification_same_status_all_methods': True,
             'dask_runtime_not_upgraded_to_hide_incompatibility': True},
        'mask_policy': {'exact_current_six_AST_policy_source_SHA256': sha(COMMON / 'prepare_public_test_view_proposal.py'),
             'Goal_functions_and_decorators': 'pass placeholder retaining line span',
             'independent_preservation_functions_and_decorators': 'same masking',
             'unknown_mapping': 'omit whole module', 'actor_unmasked_test_or_Git_reads': False,
             'original_G_O_oracle_distinct_from_masked_public_tests': True},
        'shared_v14': {'path': str(V14 / 'SOURCE_READY_FALSE.json'), 'SHA256': sha(V14 / 'SOURCE_READY_FALSE.json')},
        'shared_V5': {'path': str(COMMON / 'ROOT_COMMON_NATIVE_SCHEDULING_V5_FOUR_SOURCE.json'),
                      'SHA256': sha(COMMON / 'ROOT_COMMON_NATIVE_SCHEDULING_V5_FOUR_SOURCE.json')},
        'finance': {'continuous_ledger_required': True, 'auto_recharge': False, 'balance_source': 'Root actual current query',
                    'no_finance_factory_in_qualification': True},
        'Root_grants_required_per_action': True, 'source_only': True, 'READY': False,
        'execution_authorized': False, 'model_authorized': False, 'native_authorized': False,
        'private_execution_authorized': False, 'finance_authorized': False}
    save(E / 'protocol249_SOURCE.json', protocol)
    save(E / 'TASK_BINDINGS249_SOURCE.json', {'schema': 'EXP249-public-task-bindings/1', 'tasks': rows,
         'private_manifest_content_not_read_by_preparation': True, 'historical_results_not_selected_or_loaded': True})
    grants = E / 'grant_templates'
    base = {'schema': 'EXP249-exact-Root-action-grant/1', 'root_authorized': False,
            'model_authorized': False, 'private_execution_authorized': False, 'finance_authorized': False,
            'native_authorized': False, 'trusted_original_test_source_read_authorized': False,
            'lease_end_UTC': None, 'root_stop_paths': [], 'protocol_SHA256': sha(E / 'protocol249_SOURCE.json'),
            'source_seal_SHA256': None, 'controller_launch_python': str(CONTROLLER),
            'controller_launch_SHA256': sha(CONTROLLER), 'source_only': True}
    for task in FIRST_TWO:
        g = {**base, 'action': 'identity', 'task_ids': [task], 'max_identity_OS_roots': 1,
             'parent_owned_job_name': 'RootExp249_identity_' + task.replace('-', '_'),
             'no_business_import_or_pytest': True}
        save(grants / (task + '.identity.false.json'), g)
        c = read(E / 'contracts' / task / 'public_contract.json')
        g = {**base, 'action': 'current_C0', 'task_ids': [task], 'max_original_G_O_native': 1,
             'max_masked_ordinary_native': 1, 'trusted_original_G_O_oracle_execution_authorized': False,
             'parent_owned_job_name': 'RootExp249_C0_' + task.replace('-', '_'),
             'current_identity_receipt_SHA256': None, 'current_identity_parent_STOP_SHA256': None,
             'masked_scope_SHA256': None, 'exact_G_O_nodes': list(dict.fromkeys(c['public_target_nodes'] + c['ordinary_nodes'])),
             'current_process_clock_policy': None, 'common_precise_clock_contract': None,
             'Root_current_process_precise_clock_admitted': False}
        save(grants / (task + '.current_C0.false.json'), g)
    g = {**base, 'action': 'materialize', 'task_ids': FIRST_TWO, 'max_materialized_tasks': 2,
         'trusted_masking_inputs': {r['task_id']: {'manifest_path': r['Root_only_original_isolation_manifest_path'],
             'manifest_SHA256': None} for r in rows if r['task_id'] in FIRST_TWO}}
    save(grants / 'first_two.materialize.false.json', g)
    source_files += list(E.glob('*.py'))
    sources = {str(p.resolve()): sha(p) for p in source_files}
    for path in (E / 'protocol249_SOURCE.json', E / 'TASK_BINDINGS249_SOURCE.json', CONTROLLER, CONTROLLER.parent.parent / 'pyvenv.cfg'):
        inputs[str(path)] = sha(path)
    save(E / 'SOURCE_SEAL249.json', {'schema': 'EXP249-source-and-public-input-seal/1', 'created_UTC': now(),
         'sources_SHA256': sources, 'public_inputs_SHA256': inputs,
         'Root_only_private_metadata_binding_deferred_to_materialization_grant': True,
         'private_test_files_not_read_or_hashed_by_source_preparation': True,
         'actual_product_interpreter_not_inferred': True, 'READY': False})
    seal_sha = sha(E / 'SOURCE_SEAL249.json')
    for path in grants.glob('*.json'):
        g = read(path); g['source_seal_SHA256'] = seal_sha; save(path, g)
    commands = []
    for task in FIRST_TWO:
        commands.append({'stage': 'identity', 'task': task,
            'argv': [str(CONTROLLER), '-X', 'utf8', '-B', str(E / 'native249.py'), '--stage', 'identity', '--task', task,
                     '--root-grant', str(E / 'ROOT_RELEASES' / (task + '.identity.actual.json'))],
            'Root_template': str(grants / (task + '.identity.false.json')), 'actual_authorized': False})
    save(E / 'ROOT_FIRST_TWO_IDENTITY_COMMANDS249.json', {'source_seal_SHA256': seal_sha, 'commands': commands,
         'all_false': True, 'no_product_imports_or_tests': True})
    for path in E.glob('*.py'):
        ast.parse(path.read_text('utf-8-sig'), filename=str(path))
    print(canonical({'status': 'SOURCE_FIRST_TWO_IDENTITY_READY_FALSE', 'task_order': TASKS,
                     'source_seal_SHA256': seal_sha, 'source_count': len(sources), 'public_input_count': len(inputs),
                     'model_native_private_finance': 0}))


if __name__ == '__main__':
    main()

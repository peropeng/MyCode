"""Pin complete OURS248 source and prepare the first accepted new-task contract."""
import ast
from trial_runtime249 import *


def main():
    seal_path = HERE / 'OURS_SOURCE_SEAL249_V1.json'
    if seal_path.exists(): raise RuntimeError('EXP249_OURS_SOURCE_ALREADY_SEALED')
    source_map = read(HERE / 'OURS_ORIGINAL_SOURCE_MAP249.json')
    for path, row in source_map['files'].items():
        if sha(path) != row['SHA256'] or sha(row['source']) != row['SHA256']:
            raise RuntimeError('EXP249_ORIGINAL_248_CORE_BYTES_CHANGED')
    own_sources = list(HERE.glob('*.py')) + list((HERE / 'ours_core').glob('*.py'))
    source_files = own_sources + [OLD / 'ancestor_sources/common_environment224.py', OLD / 'masked_boundary242.py',
        FIN / 'continuous_core_v3.py', FIN / 'completion_transport_v3.py', FIN / 'common_public_feedback_codec.py']
    for path in own_sources: ast.parse(path.read_text('utf-8-sig'), filename=str(path))
    pub = read(HERE / 'PUBLIC_SOURCE_BINDINGS249.json')
    inputs = dict(pub['public_inputs_SHA256'])
    for path in (HERE / 'PUBLIC_SOURCE_BINDINGS249.json', HERE / 'OURS_ORIGINAL_SOURCE_MAP249.json',
                 HERE / 'COMMON_C0_SCHEMA_REQUIREMENTS249.json'):
        inputs[str(path)] = sha(path)
    seal = {'schema': 'EXP249-OURS248-complete-method-source/1', 'frozen_UTC': now(),
        'sources_SHA256': {str(p.resolve()): sha(p) for p in source_files}, 'public_inputs_SHA256': inputs,
        'core_algorithm_source_bytes_unchanged': True, 'method_MAX_ATTEMPTS': 3,
        'changed_boundaries': ['new task/public resources', 'fresh Root C0 and current mask', 'isolated method/task/trial',
                               'predeclared repeat seed master', 'real preparation T0', 'durable event pause/replay and exact dispatch'],
        'no_prior_trial_or_other_method_output_input': True, 'no_new_RQ1_fit_or_forward': True,
        'model_native_private_finance_during_preparation': 0, 'actual_model_grant_required': True}
    save(seal_path, seal)
    task = 'getmoto__moto-5072'; trial = 'trial1'
    finance = ROOT / '工作区/1012-until0900-common/CONFIRMATION_ACCEPTED_C0_V1_FINANCE_CONFIG.json'
    config = read(finance)
    registry = read(config['common_C0_supplement_registry']); accepted = registry['tasks'][task]
    if accepted.get('Root_actual_C0_accepted') is not True: raise RuntimeError('EXP249_FIRST_TASK_NOT_ROOT_ACCEPTED')
    scope = E249 / 'public_views_v2/COMMON_MASKED_PUBLIC_TEST_SCOPE249.json'
    if sha(scope) != '540b6451f1df6898c18789f7622f9ea67aada01e270575c90e3be5189aa9b65e':
        raise RuntimeError('EXP249_CURRENT_ROOT_V2_SCOPE_DRIFT')
    bind = lambda path: {'path': str(Path(path).resolve()), 'sha256': sha(path)}
    contract = {'schema': 'EXP249-OURS248-new-task-trial-contract/1', 'method': 'OURS248_FULL',
        'task_id': task, 'trial_id': trial, 'trial_master_seed': 2026101201,
        'output_root': str(HERE / 'runs/OURS248_FULL' / task / trial),
        'public_contract': bind(E249 / 'contracts' / task / 'public_contract.json'),
        'public_test_scope_contract': bind(scope),
        'current_C0_observation': bind(accepted['current_observation_path']),
        'current_C0_parent_terminal': bind(accepted['current_parent_path']),
        'finance_configuration': bind(finance), 'finance_phase': 'Until0900ConfirmOurs24920261012',
        'method_source_seal': bind(seal_path), 'clock_policy': 'START_AT_FIRST_REAL_TRIAL_PREPARATION',
        'clock_authority': 'Root later explicit direction: count actual method preparation/generation trajectory from its beginning; preserve original T0 across all continuations',
        'old_protocol_first_POST_only_clock_not_overwritten': True,
        'RQ1_existing_output_reuse': {'path': pub['tasks'][task]['G_frozen_plan'], 'sha256': pub['tasks'][task]['G_frozen_plan_SHA256'],
            'new_fit_forward': 0, 'prior_encoding_ranking_preparation_cost_separately_disclosed': True,
            'not_claimed_new_unseen_RQ1_confirmation': True},
        'fixed_resource_endpoint': read(E249 / 'protocol249_SOURCE.json')['fixed_resource_observation_endpoint'],
        'natural_endpoint_internal_parameters_unchanged': True, 'user0900_is_recheck_minimum_not_automatic_algorithm_failure': True,
        'full_reader_messages_source_candidates_guard_and_native_cursor_checkpointed': True,
        'source_preparation_only': True, 'model_authorized': False, 'native_authorized': False,
        'private_authorized': False, 'finance_authorized': False}
    path = HERE / 'contracts' / task / (trial + '.OURS248_SOURCE.json')
    save(path, contract)
    save(HERE / 'OURS_FIRST_TRIAL_COMMANDS249_SOURCE.json', {'contract': str(path), 'contract_SHA256': sha(path),
        'source_seal_SHA256': sha(seal_path),
        'pure_prepare_argv': [str(ROOT / '工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'), '-X', 'utf8', '-B', str(HERE / 'ours_entry249.py'), '--contract', str(path)],
        'continuation_argv_is_same_pure_entry': True,
        'dispatch_argv_template': ['<working controller Python>', '-X', 'utf8', '-B', str(HERE / 'dispatch_one249.py'),
            '--ready-dir', '<exact MODEL_READY ready_dir>', '--root-grant', '<separate exact Root model grant>'],
        'candidate_native_boundary': '<trial>/native_requests/attemptN/NATIVE_READY.json; exact Root G/O action then completed witness+parentSTOP',
        'model_native_private_finance': 0})
    print(canonical({'source_seal_SHA256': sha(seal_path), 'contract': str(path), 'contract_SHA256': sha(path), 'method': 'OURS248_FULL', 'task': task, 'trial': trial}))


if __name__ == '__main__': main()

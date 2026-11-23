"""Prepare declared first-two x three contracts; no method or trial is started."""
from trial_runtime249 import *

finance = ROOT / '工作区/1012-until0900-common/CONFIRMATION_ACCEPTED_C0_V2_FINANCE_CONFIG.json'
config = read(finance); registry = read(config['common_C0_supplement_registry'])
protocol = read(E249 / 'protocol249_SOURCE.json')
public = read(HERE / 'PUBLIC_SOURCE_BINDINGS249.json')
base_path = HERE / 'contracts/getmoto__moto-5072/trial1.OURS248_SOURCE_V2.json'
base = read(base_path); seal = base['method_source_seal']; verify_source_seal(seal['path'])
if sha(seal['path']) != seal['sha256']: raise RuntimeError('EXP249_OURS_EXISTING_SOURCE_SEAL_DRIFT')
bind = lambda path: {'path': str(Path(path).resolve()), 'sha256': sha(path)}
rows = []
for task in protocol['task_order'][:2]:
    accepted = registry['tasks'][task]
    if accepted.get('Root_actual_C0_accepted') is not True: raise RuntimeError('EXP249_REPEAT_TASK_NOT_CURRENT_ROOT_ACCEPTED')
    for trial, master in zip(protocol['trial_ids'], protocol['trial_master_seeds']):
        if task == base['task_id'] and trial == base['trial_id']:
            rows.append({'task_id': task, 'trial_id': trial, 'path': str(base_path), 'sha256': sha(base_path),
                'existing_original_contract_and_T0_preserved': True, 'new_contract': False})
            continue
        c = copy.deepcopy(base); c.update(task_id=task, trial_id=trial, trial_master_seed=master,
            output_root=str(HERE / 'runs/OURS248_FULL' / task / trial), public_contract=bind(E249 / 'contracts' / task / 'public_contract.json'),
            current_C0_observation=bind(accepted['current_observation_path']), current_C0_parent_terminal=bind(accepted['current_parent_path']),
            finance_configuration=bind(finance))
        c['RQ1_existing_output_reuse'].update(path=public['tasks'][task]['G_frozen_plan'], sha256=public['tasks'][task]['G_frozen_plan_SHA256'])
        c['predeclared_repeat_identity'] = {'fixed_trial_count': 3, 'independent_new_trajectory': True,
            'prior_trial_response_or_candidate_reuse': False, 'seed_does_not_claim_provider_determinism': True,
            'trial_preparation_starts_only_via_required_launcher': True}
        path = HERE / 'contracts' / task / (trial + '.OURS248_SOURCE_V2.json')
        if path.exists() and read(path) != c: raise RuntimeError('EXP249_REPEAT_CONTRACT_ALREADY_FROZEN')
        if not path.exists(): save(path, c)
        checked_contract(path, 'OURS248_FULL')
        rows.append({'task_id': task, 'trial_id': trial, 'path': str(path), 'sha256': sha(path),
            'new_contract': True, 'body_or_business_preparation_in_this_script': False,
            'model_native_private_finance': 0})
save(HERE / 'OURS_FIRST_TWO_THREE_TRIAL_CONTRACTS249_SOURCE.json', {'schema': 'EXP249-declared-first-two-three-trials/1',
    'rows': rows, 'fixed_new_issues': 2, 'fixed_trials_per_issue': 3, 'completed_trials_not_inferred': True,
    'source_seal': seal, 'launcher': str(HERE / 'ours_launcher249.py'), 'model_native_private_finance': 0})
print(canonical({'status': 'FIRST_TWO_THREE_TRIAL_CONTRACTS_READY', 'rows': rows}), flush=True)

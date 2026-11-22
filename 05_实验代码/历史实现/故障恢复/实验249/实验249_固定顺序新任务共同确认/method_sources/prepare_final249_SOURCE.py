"""Freeze an already selected public terminal; never read private metadata."""
import argparse
from trial_runtime249 import *


def freeze(contract_path):
    c, out, _, _, _ = checked_contract(contract_path, 'OURS248_FULL')
    terminal_path = out / 'PUBLIC_ONLY_NATURAL_TERMINAL.json'
    terminal = read(terminal_path)
    status = read(out / 'STATUS.json')
    if (status['status'] != 'PUBLIC_ONLY_NATURAL_TERMINAL' or terminal.get('error') is not None
            or terminal.get('engineering_outcome_unknown') is True or terminal['status'] == 'BUDGET_CENSORED'):
        raise RuntimeError('EXP249_NO_COMPLETE_PUBLIC_TERMINAL_TO_FREEZE')
    if terminal.get('selection', {}).get('uses_hidden') is not False or terminal.get('hidden_calls_in_adapter') != 0:
        raise RuntimeError('EXP249_PUBLIC_ONLY_SELECTION_REQUIRED')
    source_path = out / 'SELECTED_BUSINESS_SOURCE.json'
    source = read(source_path); hashes = {p: hashlib.sha256(t.encode()).hexdigest() for p, t in source.items()}
    selected = terminal['runtime_core']['terminal_frontier_selection']
    if selected['selected_source_sha256'] != hashes or selected['final_frontier_preserved'] is not True:
        raise RuntimeError('EXP249_SELECTED_SET_FRONTIER_OR_SOURCE_DRIFT')
    attempt = selected['selected_observation_attempt']
    evidence = {'schema': 'EXP249-frozen-public-terminal/1', 'UTC': now(),
        'method': c['method'], 'task_id': c['task_id'], 'trial_id': c['trial_id'],
        'terminal_status': terminal['status'], 'candidate_snapshot': terminal['final_snapshot'],
        'candidate_source_sha256': hashes, 'selected_attempt': attempt,
        'public_terminal_path': str(terminal_path), 'public_terminal_SHA256': sha(terminal_path),
        'business_source_file': str(source_path), 'business_source_file_SHA256': sha(source_path),
        'method_contract_path': str(Path(contract_path).resolve()), 'method_contract_SHA256': sha(contract_path),
        'science_T0_path': str(out / 'SCIENCE_T0_TRIAL_PREPARATION_STARTED.json'),
        'science_T0_SHA256': sha(out / 'SCIENCE_T0_TRIAL_PREPARATION_STARTED.json'),
        'no_private_read_or_execution': True, 'private_result_cannot_change_selection': True}
    final_dir = out / 'frozen_final'
    if (final_dir / 'FROZEN_PUBLIC_SELECTION.json').exists():
        previous = read(final_dir / 'FROZEN_PUBLIC_SELECTION.json')
        evidence['UTC'] = previous['UTC']
        if previous != evidence: raise RuntimeError('EXP249_FROZEN_SELECTION_CANNOT_BE_REPLACED')
    else: save(final_dir / 'FROZEN_PUBLIC_SELECTION.json', evidence)
    goals = read(c['public_contract']['path'])['public_target_nodes']
    public_pass = bool(terminal['first_public_pass_attempt'] is not None and attempt > 0 and set(goals) <= set(selected['selected_actual_goal_PASS']))
    if not public_pass:
        save(final_dir / 'PUBLIC_NATURAL_ENDPOINT.json', {**evidence, 'public_G_O_all_pass': False,
            'requires_private_to_determine_success': False, 'natural_success': False,
            'private_native_calls': 0, 'public_failure_kept': True})
        return {'status': 'PUBLIC_NATURAL_FAILURE_FROZEN', 'path': str(final_dir / 'PUBLIC_NATURAL_ENDPOINT.json')}
    native_dir = out / 'native_requests' / ('attempt' + str(attempt))
    completed_path = native_dir / 'COMPLETED_PUBLIC.json'; completed = read(completed_path)
    parent_path = Path(completed['parent_supervision_path']); parent = read(parent_path)
    if (sha(parent_path) != completed['parent_supervision_SHA256'] or parent.get('exit_code') != 0
            or parent.get('error') is not None or parent.get('stop_receipt', {}).get('all_owned_descendants_terminated') is not True
            or completed['candidate_snapshot'] != terminal['final_snapshot'] or completed['candidate_source_sha256'] != hashes
            or completed.get('ordinary_all_pass') is not True or completed.get('failed_goals') != 0
            or sha(completed['public_native_path']) != completed['public_native_SHA256']):
        raise RuntimeError('EXP249_PUBLIC_PASS_SELECTED_SOURCE_AND_PARENT_STOP_REQUIRED')
    public = read(c['public_contract']['path'])
    bindings = read(E249 / 'TASK_BINDINGS249_SOURCE.json')
    binding = next(row for row in bindings['tasks'] if row['task_id'] == c['task_id'])
    ready = {**evidence, 'schema': 'EXP249-once-independent-final-native-ready/1', 'attempt': attempt,
        'frozen_selection_path': str(final_dir / 'FROZEN_PUBLIC_SELECTION.json'),
        'frozen_selection_SHA256': sha(final_dir / 'FROZEN_PUBLIC_SELECTION.json'),
        'public_completed_path': str(completed_path), 'public_completed_SHA256': sha(completed_path),
        'public_supervision_path': str(parent_path), 'public_supervision_SHA256': sha(parent_path),
        'public_contract': c['public_contract'], 'public_test_scope_contract': c['public_test_scope_contract'],
        'goal_nodes': public['public_target_nodes'], 'ordinary_nodes': public['ordinary_nodes'],
        'Root_only_task_manifest_path': binding['Root_only_original_isolation_manifest_path'],
        'native_output': str(HERE / 'final_private_ROOT' / c['method'] / c['task_id'] / c['trial_id']),
        'once_private_required': True, 'private_feedback_to_method': False}
    ready_path = final_dir / 'FINAL_READY.json'
    if ready_path.exists() and read(ready_path) != ready: raise RuntimeError('EXP249_FINAL_READY_ALREADY_FROZEN')
    if not ready_path.exists(): save(ready_path, ready)
    base = read(native_dir / 'ROOT_PUBLIC_NATIVE_GRANT_FALSE.json')
    grant = {k: copy.deepcopy(base[k]) for k in ('method', 'task_id', 'trial_id', 'attempt',
        'qualified_runtime_policy', 'current_identity_receipt', 'controller_launch_python', 'controller_launch_SHA256',
        'current_process_clock_policy', 'common_precise_clock_contract', 'Root_current_process_precise_clock_admitted')}
    seal = HERE / 'OURS_FINAL_NATIVE_SOURCE_SEAL249_V1.json'
    grant.update(schema='EXP249-once-independent-final-Root-grant/1', root_authorized=False, native_authorized=False,
        private_authorized=False, once_private_authorized=False, model_authorized=False, finance_authorized=False,
        no_feedback_to_model=True, maximum_new_private_native=1, ready_SHA256=sha(ready_path),
        candidate_source_inventory_SHA256=digest(hashes), native_source_seal={'path': str(seal), 'sha256': sha(seal)},
        task_manifest_SHA256=None, original_private_nodes_SHA256=None,
        lease_end_UTC=None, root_stop_paths=[], parent_owned_job_name='RootExp249_Final_' + c['task_id'].replace('-', '_') + '_' + c['trial_id'])
    false_path = final_dir / 'ROOT_FINAL_NATIVE_GRANT_FALSE.json'
    if false_path.exists() and read(false_path) != grant: raise RuntimeError('EXP249_FALSE_FINAL_GRANT_ALREADY_FROZEN')
    if not false_path.exists(): save(false_path, grant)
    return {'status': 'PUBLIC_SELECTION_FROZEN_FINAL_SOURCE_READY', 'ready': str(ready_path), 'ready_SHA256': sha(ready_path),
        'false_grant': str(false_path), 'false_grant_SHA256': sha(false_path), 'actual_native_private_model_finance': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--contract', required=True); args = parser.parse_args()
    print(canonical(freeze(args.contract)), flush=True)

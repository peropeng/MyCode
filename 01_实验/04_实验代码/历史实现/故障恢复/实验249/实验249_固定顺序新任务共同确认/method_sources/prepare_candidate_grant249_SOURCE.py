"""Create a false exact candidate grant; no authorization or native execution."""
import argparse
from trial_runtime249 import *


def prepare(ready_path):
    ready_path = Path(ready_path).resolve()
    if not ready_path.is_relative_to(HERE / 'runs/OURS248_FULL'): raise RuntimeError('EXP249_CANDIDATE_READY_SCOPE')
    r = read(ready_path); task = r['task_id']; p = read(E249 / 'protocol249_SOURCE.json')
    if task not in p['task_order'][:2] or r['trial_id'] not in p['trial_ids'] or r['attempt'] not in (1, 2, 3):
        raise RuntimeError('EXP249_CANDIDATE_DECLARED_FIRST_TWO_REPEAT_SCOPE')
    policy_path = E249 / 'ROOT_RELEASES' / (task + ('.current_C0.public_channel_v4.actual.json' if task == 'dask__dask-9378' else '.current_C0.mask_v3.actual.json'))
    policy = read(policy_path); identity = E249 / 'qualification' / task / 'identity/COMPLETED_IDENTITY249.json'
    seal = HERE / 'OURS_CANDIDATE_NATIVE_SOURCE_SEAL249_V1.json'; verify_source_seal(seal)
    bind = lambda path: {'path': str(Path(path).resolve()), 'sha256': sha(path)}
    controller = ROOT / '工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'
    g = {'schema': 'EXP249-exact-candidate-public-native-Root-grant/1', 'root_authorized': False,
        'native_authorized': False, 'model_authorized': False, 'private_authorized': False, 'finance_authorized': False,
        'maximum_new_original_G_O_native': 1, 'method': r['method'], 'task_id': task, 'trial_id': r['trial_id'], 'attempt': r['attempt'],
        'ready_SHA256': sha(ready_path), 'candidate_source_inventory_SHA256': digest(r['candidate_source_sha256']),
        'native_source_seal': bind(seal), 'qualified_runtime_policy': bind(policy_path), 'current_identity_receipt': bind(identity),
        'exact_G_O_nodes': list(dict.fromkeys(r['goal_nodes'] + r['ordinary_nodes'])), 'lease_end_UTC': None, 'root_stop_paths': [],
        'parent_owned_job_name': 'RootExp249_Candidate_' + task.replace('-', '_') + '_' + r['trial_id'] + '_attempt' + str(r['attempt']),
        'controller_launch_python': str(controller), 'controller_launch_SHA256': sha(controller)}
    for key in ('current_process_clock_policy', 'common_precise_clock_contract', 'Root_current_process_precise_clock_admitted'):
        g[key] = copy.deepcopy(policy.get(key))
    path = ready_path.parent / 'ROOT_PUBLIC_NATIVE_GRANT_FALSE.json'
    if path.exists():
        previous = read(path)
        # First Moto template predates this generic naming function. Preserve it
        # when its exact action/source/runtime binding is otherwise identical.
        g['parent_owned_job_name'] = previous['parent_owned_job_name']
        if previous != g: raise RuntimeError('EXP249_CANDIDATE_FALSE_GRANT_ALREADY_DIFFERS')
    else: save(path, g)
    return {'false_grant': str(path), 'sha256': sha(path), 'actual_calls': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--ready', required=True); args = parser.parse_args()
    print(canonical(prepare(args.ready)), flush=True)

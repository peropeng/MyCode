"""Create exact all-false single-body grant metadata; never dispatch a request."""
import argparse
from trial_runtime249 import *


def prepare(slot):
    slot = Path(slot).resolve()
    if not slot.is_relative_to(HERE / 'runs/OURS248_FULL'): raise RuntimeError('EXP249_MODEL_READY_SCOPE')
    path = slot / 'FIRST_UNPOST_READY.json'; r = read(path); body = read(slot / 'FIRST_UNPOST_BODY.json')
    if r['method'] != 'OURS248_FULL' or r['body_SHA256'] != digest(body): raise RuntimeError('EXP249_COMPLETE_METHOD_BODY_DRIFT')
    c, out, _, _, _ = checked_contract(r['contract_path'], r['method'])
    if sha(r['contract_path']) != r['contract_SHA256'] or not slot.is_relative_to(out): raise RuntimeError('EXP249_MODEL_CONTRACT_BINDING')
    seal = c['method_source_seal']; verify_source_seal(seal['path'])
    if sha(seal['path']) != seal['sha256'] or r['method_source_seal'] != seal: raise RuntimeError('EXP249_MODEL_SOURCE_SEAL_DRIFT')
    g = {'schema': 'EXP249-exact-single-model-Root-grant/1', 'root_authorized': False, 'model_authorized': False,
        'finance_authorized': False, 'native_authorized': False, 'private_authorized': False, 'maximum_new_requests': 1}
    for key in ('method', 'task_id', 'trial_id', 'call_ordinal', 'finance_phase', 'body_SHA256', 'finance_configuration', 'contract_SHA256'):
        g[key] = copy.deepcopy(r[key])
    g.update(ready_SHA256=sha(path), method_source_seal_SHA256=seal['sha256'], lease_end_UTC=None, root_stop_paths=[])
    target = slot / 'ROOT_EXACT_MODEL_GRANT_FALSE.json'
    if target.exists() and read(target) != g: raise RuntimeError('EXP249_FALSE_MODEL_GRANT_ALREADY_FROZEN')
    if not target.exists(): save(target, g)
    return {'false_grant': str(target), 'sha256': sha(target), 'actual_generation_native_private_finance': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--ready-dir', required=True); args = parser.parse_args()
    print(canonical(prepare(args.ready_dir)), flush=True)

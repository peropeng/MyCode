"""Source-only final boundary preparation, with no task/private execution."""
import ast
from trial_runtime249 import *

previous_path = HERE / 'OURS_CANDIDATE_NATIVE_SOURCE_SEAL249_V1.json'
previous = verify_source_seal(previous_path)
sources = dict(previous['sources_SHA256'])
for name in ('prepare_final249_SOURCE.py', 'final249_ROOT_ONLY.py', 'seal_final249_SOURCE.py'):
    path = HERE / name
    ast.parse(path.read_text('utf-8-sig'), filename=str(path))
    sources[str(path)] = sha(path)
inputs = dict(previous['public_inputs_SHA256'])
inputs[str(previous_path)] = sha(previous_path)
inputs[str(E249 / 'TASK_BINDINGS249_SOURCE.json')] = sha(E249 / 'TASK_BINDINGS249_SOURCE.json')
value = {'schema': 'EXP249-once-final-native-source-seal/1', 'sources_SHA256': sources,
    'public_inputs_SHA256': inputs, 'source_only': True, 'actual_native_private_model_finance': 0,
    'private_metadata_not_read_during_source_preparation': True,
    'private_manifest_and_selector_hashes_bound_only_by_later_Root_actual_grant': True,
    'same_original_guard_probe_runtime_identity_and_V5_scheduling_as_qualified_C0': True,
    'public_only_selected_candidate_frozen_before_any_private_read': True,
    'unknown_never_rerun': True}
seal_path = HERE / 'OURS_FINAL_NATIVE_SOURCE_SEAL249_V1.json'
if seal_path.exists() and read(seal_path) != value: raise RuntimeError('EXP249_FINAL_SOURCE_SEAL_ALREADY_FROZEN')
if not seal_path.exists(): save(seal_path, value)
verify_source_seal(seal_path)
print(canonical({'status': 'SOURCE_ONLY_SEALED', 'path': str(seal_path), 'sha256': sha(seal_path),
    'sources': len(sources), 'public_inputs': len(inputs), 'actual_calls': 0}), flush=True)

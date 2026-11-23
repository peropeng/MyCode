"""Pure Root helper: exact public C0 feedback for the three method adapters.

Returns objects only. The calling Root decides the registry location and writes
it after independently verifying qualification and parent STOP. No private IO.
"""
import importlib.util
from pathlib import Path
from shared_public249 import ROOT, read, sha, digest

OLD = ROOT / '工作区/1011-our19'
CODEC = ROOT / '工作区/1010-unified-six/finance_queue_remaining_SOURCE/common_public_feedback_codec.py'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


def make_supplement(task_id, public_contract_path, public_observation_path, parent_terminal_path,
                    *, expected_observation_SHA256, expected_parent_terminal_SHA256,
                    masked_scope_path, masked_scope_SHA256):
    c = read(public_contract_path)
    if c['task_id'] != task_id or sha(public_observation_path) != expected_observation_SHA256 or sha(parent_terminal_path) != expected_parent_terminal_SHA256:
        raise RuntimeError('EXP249_ROOT_C0_EXPORT_INPUT_DRIFT')
    parent = read(parent_terminal_path)
    if parent.get('task_id') != task_id or parent.get('exit_code') != 0 or parent.get('error') is not None or parent.get('stop_receipt', {}).get('all_owned_descendants_terminated') is not True:
        raise RuntimeError('EXP249_ROOT_C0_PARENT_STOP_REQUIRED')
    if sha(masked_scope_path) != masked_scope_SHA256:
        raise RuntimeError('EXP249_CURRENT_MASKED_SCOPE_DRIFT')
    obs = read(public_observation_path)
    if obs['task_id'] != task_id or obs['actual_C0_source_SHA256'] != c['c0_business_paths_sha256']:
        raise RuntimeError('EXP249_ROOT_C0_BUSINESS_BINDING_DRIFT')
    validation = obs['current_incumbent_public_feedback']
    if 'public_validation' in validation:
        validation = validation['public_validation']
    guard_module = load('_Root249_original_progress_guard', OLD / 'progress_guard240.py')
    guard = guard_module.RepairProgressGuard('PROGRESS_SET', c['public_target_nodes'], c['ordinary_nodes'], validation, c['c0_business_paths_sha256'])
    if guard.failed_count < 1:
        raise RuntimeError('EXP249_ROOT_C0_MUST_HAVE_REAL_GOAL_FAILURE')
    projection = load('_Root249_original_feedback_projection', OLD / 'public_projection181.py')
    current = projection.project_feedback(guard.current_public_feedback(c['c0_business_paths_sha256']))
    codec = load('_Root249_original_public_codec', CODEC)
    encoded, audit = codec.encode(current)
    if codec.decode(encoded) != current:
        raise RuntimeError('EXP249_CURRENT_C0_CODEC_ROUNDTRIP')
    native = validation['native_record']
    native_path = native.get('path') or str(Path(native['log']).with_name('run.json'))
    value = {'schema': 'common-fresh-selected-dataset-C0-public-observation/1', 'task_id': task_id,
        'previous_full_public_pack_SHA256': c['pack_sha256'], 'current_C0_native_record_SHA256': sha(native_path),
        'actual_C0_source_SHA256': c['c0_business_paths_sha256'], 'actual_ABI': obs['actual_ABI'],
        'original_public_goal_ordinary_scope_only': True, 'goal_failure_count': guard.failed_count,
        'ordinary_PASS_count': len(c['ordinary_nodes']), 'current_incumbent_public_feedback': encoded,
        'decoded_current_incumbent_SHA256': digest(current), 'same_for_all_three_every_model_request': True,
        'independent_final_or_Gold_or_other_methods_outputs': False,
        'transport_expression_not_method_contribution': True, 'current_masked_scope_SHA256': masked_scope_SHA256,
        'fresh_C0_observation_SHA256': expected_observation_SHA256, 'fresh_C0_parent_terminal_SHA256': expected_parent_terminal_SHA256}
    return value, current, {'codec_source_SHA256': sha(CODEC), 'codec_audit': audit,
                            'raw_public_G_O_native_path': native_path, 'raw_public_G_O_native_SHA256': sha(native_path),
                            'qualification_is_not_scientific_trial_T0': True, 'model_native_private_finance': 0}

"""Prepare false batch3 grants; inspect only published public views/receipts.

No original test or isolation manifest is opened. No native/model/finance client.
The Root signs and runs materialization, then --after-mask binds the public view.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
E = HERE.parent
TASKS = ['getmoto__moto-6352', 'pydantic__pydantic-8567']
PY = Path('D:/Code/毕设/graduate-thesis-experiments/工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe')

def read(p): return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v): return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
def digest(v): return hashlib.sha256(canonical(v).encode()).hexdigest()
def save(p, v):
    p = Path(p).resolve()
    if not p.is_relative_to(HERE.resolve()): raise RuntimeError('BATCH3_SOURCE_ONLY_WRITE_SCOPE')
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        if read(p) != v: raise RuntimeError('BATCH3_SOURCE_ARTIFACT_ALREADY_FROZEN ' + str(p))
        return
    with p.open('x', encoding='utf-8') as stream:
        json.dump(v, stream, ensure_ascii=False, indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())

def exact_function(tree, node):
    target = tree
    for part in node.split('::')[1:]:
        name = part.split('[', 1)[0]
        matches = [n for n in getattr(target, 'body', []) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == name]
        if len(matches) != 1: return None
        target = matches[0]
    return target if isinstance(target, (ast.FunctionDef, ast.AsyncFunctionDef)) else None

def public_mask_audit(c, scope):
    task = c['task_id']; row = next(r for r in scope['tasks'] if r['task_id'] == task)
    if row.get('materialization_qualified') is not True: raise RuntimeError('BATCH3_PUBLIC_VIEW_NOT_MATERIALIZED ' + task)
    root = Path(row['public_source_repo_view']).resolve()
    expected_root = (E / 'public_views_batch3' / task / 'repo').resolve()
    if root != expected_root: raise RuntimeError('BATCH3_PUBLIC_VIEW_PATH_DRIFT')
    for rel, expected in row['business_and_support_files_in_view'].items():
        if sha(root / rel) != expected: raise RuntimeError('BATCH3_PUBLIC_VIEW_FILE_DRIFT ' + rel)
    for rel, expected in c['c0_business_paths_sha256'].items():
        if row['business_and_support_files_in_view'].get(rel) != expected or sha(root / rel) != expected:
            raise RuntimeError('BATCH3_PUBLIC_C0_BUSINESS_NOT_EXACT')
    trees = {}
    for rel, expected in row['public_test_py_files_SHA256'].items():
        path = (root / rel).resolve()
        if not path.is_relative_to(root) or sha(path) != expected: raise RuntimeError('BATCH3_MASKED_TEST_PATH_OR_SHA_DRIFT')
        trees[rel] = ast.parse(path.read_text('utf-8-sig'), filename=rel)
    goal_checks = []
    for node in c['public_target_nodes']:
        tree = trees.get(node.split('::')[0]); target = exact_function(tree, node) if tree else None
        if target is not None: raise RuntimeError('BATCH3_ORIGINAL_GOAL_FUNCTION_REMAINS_VISIBLE ' + node)
        goal_checks.append({'node': node, 'function_removed_or_whole_module_omitted': True})
    ordinary_available = all(node.split('::')[0] in trees and exact_function(trees[node.split('::')[0]], node) is not None for node in c['ordinary_nodes'])
    selected = list(c['ordinary_nodes']); auxiliary = False
    if not ordinary_available:
        # Same prospective, result-independent auxiliary channel rule used for
        # Dask: first lexical available public top-level no-argument test.
        choices = []
        for rel, tree in trees.items():
            for n in tree.body:
                if isinstance(n, ast.FunctionDef) and n.name.startswith('test_') and not (n.args.posonlyargs or n.args.args or n.args.kwonlyargs or n.args.vararg or n.args.kwarg):
                    choices.append(rel + '::' + n.name)
        if not choices: raise RuntimeError('BATCH3_NO_DECLARED_PUBLIC_AUXILIARY_CHANNEL')
        selected = [min(choices)]; auxiliary = True
    return {'task_id': task, 'public_view_root': str(root), 'all_current_business_SHA256_exact': True,
        'business_file_count': len(c['c0_business_paths_sha256']), 'declared_masked_test_files': len(trees),
        'public_Goal_function_source_removed': goal_checks, 'original_ordinary_function_available_in_masked_view': ordinary_available,
        'masked_channel_qualification_nodes': selected, 'auxiliary_channel_only_original_G_O_unchanged': auxiliary,
        'auxiliary_selection_rule': 'First lexical available public top-level no-argument test, independent of any test outcome' if auxiliary else None,
        'private_metadata_or_original_unmasked_test_read': False, 'actual_C0_or_channel_qualified': False,
        'source_static_check_not_native_PASS': True}

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--after-mask', action='store_true'); args = parser.parse_args()
    batch_path = E / 'ROOT_BATCH3_SOURCE_SEAL.json'; batch = read(batch_path)
    if batch['prospective_third_batch'] != TASKS: raise RuntimeError('BATCH3_NATURAL_ORDER_DRIFT')
    old = read(E / 'SOURCE_SEAL249.json')
    for p, h in {**old['sources_SHA256'], **old['public_inputs_SHA256'], **batch['sources_SHA256']}.items():
        if sha(p) != h: raise RuntimeError('BATCH3_SEALED_SOURCE_INPUT_DRIFT ' + p)
    for p in batch['sources_SHA256']:
        if p.endswith('.py'): ast.parse(Path(p).read_text('utf-8-sig'), filename=p)
    bindings = {r['task_id']: r for r in read(E / 'TASK_BINDINGS249_SOURCE.json')['tasks']}
    base = {'schema': 'EXP249-exact-Root-action-grant/1', 'root_authorized': False, 'model_authorized': False,
        'private_execution_authorized': False, 'finance_authorized': False, 'native_authorized': False,
        'trusted_original_test_source_read_authorized': False, 'lease_end_UTC': None, 'root_stop_paths': [str(E / 'ROOT_STOP_REQUESTED.json')],
        'protocol_SHA256': sha(E / 'protocol249_SOURCE.json'), 'source_seal_SHA256': sha(E / 'SOURCE_SEAL249.json'),
        'controller_launch_python': str(PY), 'controller_launch_SHA256': sha(PY), 'source_only': True,
        'Root_mask_v2_sources_SHA256': batch['sources_SHA256'], 'Root_batch3_source_seal_SHA256': sha(batch_path),
        'Root_mask_v2_repair': True, 'uniform_common_active_process_limit': 8, 'uniform_common_lifetime_two_native_process_limit': 24}
    materialize = {**base, 'action': 'materialize', 'task_ids': TASKS, 'max_materialized_tasks': 2,
        'trusted_masking_inputs': {task: {'manifest_path': bindings[task]['Root_only_original_isolation_manifest_path'], 'manifest_SHA256': None} for task in TASKS},
        'Root_only_completion_fields': ['root_authorized=true', 'trusted_original_test_source_read_authorized=true', 'finite lease_end_UTC',
            'exact manifest_SHA256 values measured by trusted Root only'], 'no_original_private_metadata_read_by_preparer': True}
    save(HERE / 'BATCH3_MATERIALIZE_GRANT_FALSE.json', materialize)
    scope_path = E / 'public_views_batch3/COMMON_MASKED_PUBLIC_TEST_SCOPE249.json'
    if args.after_mask and not scope_path.exists(): raise RuntimeError('BATCH3_WAIT_FOR_ROOT_MATERIALIZATION')
    scope = read(scope_path) if args.after_mask else None
    rows = []; source_inputs = {str(batch_path): sha(batch_path)}
    for task in TASKS:
        cpath = E / 'contracts' / task / 'public_contract.json'; c = read(cpath)
        identity_path = E / 'qualification' / task / 'identity/COMPLETED_IDENTITY249.json'; parent_path = identity_path.parent / 'PARENT_TERMINAL249.json'
        identity = read(identity_path); parent = read(parent_path); actual = identity['product_identity']; obs = identity['process_observation']
        if (identity['task_id'] != task or parent['task_id'] != task or parent.get('error') is not None or parent.get('exit_code') != 0
                or parent.get('stop_receipt', {}).get('all_owned_descendants_terminated') is not True
                or actual.get('specific_named_Job_membership') is not True or actual.get('product_imports_or_tests') != 0
                or obs.get('root_PID_birth_verified') is not True or obs.get('stop_receipt', {}).get('all_owned_descendants_terminated') is not True
                or sha(actual['actual_OS_image']) != actual['actual_OS_image_SHA256']):
            raise RuntimeError('BATCH3_ACTUAL_IDENTITY_OR_PARENT_STOP_UNKNOWN')
        if identity['logical_product_python_SHA256'] != sha(c['logical_product_python']) or identity['pyvenv_cfg_SHA256'] != sha(Path(c['logical_product_python']).parent.parent / 'pyvenv.cfg'):
            raise RuntimeError('BATCH3_ACTUAL_RUNTIME_DRIFT')
        audit = public_mask_audit(c, scope) if scope is not None else None
        grant = {**base, 'action': 'current_C0', 'task_ids': [task], 'max_original_G_O_native': 1, 'max_masked_ordinary_native': 1,
            'trusted_original_G_O_oracle_execution_authorized': False,
            'parent_owned_job_name': 'RootExp249_C0_' + task.replace('-', '_') + '_Batch3',
            'current_identity_receipt_SHA256': sha(identity_path), 'current_identity_parent_STOP_SHA256': sha(parent_path),
            'masked_scope_SHA256': sha(scope_path) if scope is not None else None,
            'exact_G_O_nodes': list(dict.fromkeys(c['public_target_nodes'] + c['ordinary_nodes'])),
            'current_process_clock_policy': 'ROOT_ORIGINAL_CLOCK_EXPLICITLY_ADMITTED', 'common_precise_clock_contract': None,
            'Root_current_process_precise_clock_admitted': False,
            'Root_original_clock_common_policy': 'Same original current OS clock for all methods; no cross-ABI clock capability inheritance.',
            'masked_channel_qualification_nodes': audit['masked_channel_qualification_nodes'] if audit else None,
            'Root_auxiliary_channel_only_original_O_retained': bool(audit and audit['auxiliary_channel_only_original_G_O_unchanged']),
            'Root_only_completion_fields': ['root_authorized=true', 'native_authorized=true', 'trusted_original_G_O_oracle_execution_authorized=true',
                'finite lease_end_UTC', 'use after-mask bound false grant only'],
            'generation_stays_closed_until_complete_actual_Gfail_Opass_and_masked_channel_and_parent_STOP': True}
        suffix = 'AFTER_MASK_BOUND_FALSE' if args.after_mask else 'PENDING_MASK_FALSE'
        target = HERE / (task + '.CURRENT_C0_' + suffix + '.json'); save(target, grant)
        if audit: save(HERE / (task + '.PUBLIC_MASK_STATIC_AUDIT.json'), audit)
        rows.append({'task_id': task, 'Goal_count': len(c['public_target_nodes']), 'ordinary_count': len(c['ordinary_nodes']),
            'Goal_nodes_SHA256': digest(c['public_target_nodes']), 'ordinary_nodes_SHA256': digest(c['ordinary_nodes']),
            'current_C0_false_grant': str(target), 'current_C0_false_grant_SHA256': sha(target),
            'actual_identity': actual, 'identity_SHA256': sha(identity_path), 'parent_STOP_SHA256': sha(parent_path),
            'mask_static_audit': audit, 'actual_C0_qualification': False})
        for p in (cpath, identity_path, parent_path): source_inputs[str(p)] = sha(p)
    commands = {'schema': 'EXP249-batch3-Root-action-command-sequence/1', 'readme': 'Commands are exact argv arrays; Root signs copies in ROOT_RELEASES. This preparer cannot authorize or execute actions.',
        'materialize_false_grant': str(HERE / 'BATCH3_MATERIALIZE_GRANT_FALSE.json'), 'materialize_false_grant_SHA256': sha(HERE / 'BATCH3_MATERIALIZE_GRANT_FALSE.json'),
        'materialize_argv': [str(PY), '-X', 'utf8', '-B', str(E / 'materialize249_ROOT_BATCH3.py'), '--root-grant', str(E / 'ROOT_RELEASES/batch3.materialize.actual.json')],
        'after_materialize_public_only_prepare_argv': [str(PY), '-X', 'utf8', '-B', str(Path(__file__).resolve()), '--after-mask'],
        'current_C0_argv': {task: [str(PY), '-X', 'utf8', '-B', str(E / 'native249_ROOT_BATCH3.py'), '--stage', 'current_C0', '--task', task,
            '--root-grant', str(E / 'ROOT_RELEASES' / (task + '.current_C0.batch3.actual.json'))] for task in TASKS},
        'Root_only_manifest_hash_binding_before_materialize': True, 'no_original_test_or_private_body_read_by_preparer': True,
        'actual_native_model_private_finance': 0, 'rows': rows}
    out = HERE / ('BATCH3_COMMANDS_AFTER_MASK_SOURCE.json' if args.after_mask else 'BATCH3_COMMANDS_PENDING_MASK_SOURCE.json'); save(out, commands)
    source_seal = {'schema': 'EXP249-batch3-false-grant-preparation-source-seal/1', 'sources_SHA256': {str(Path(__file__).resolve()): sha(__file__), **batch['sources_SHA256']},
        'public_inputs_SHA256': source_inputs, 'Root_batch3_execution_source_unmodified': True, 'actual_calls': 0}
    save(HERE / 'BATCH3_PREPARATION_SOURCE_SEAL.json', source_seal)
    print(canonical({'commands': str(out), 'commands_SHA256': sha(out), 'preparation_seal_SHA256': sha(HERE / 'BATCH3_PREPARATION_SOURCE_SEAL.json'),
        'materialize_false_SHA256': sha(HERE / 'BATCH3_MATERIALIZE_GRANT_FALSE.json'), 'after_mask': args.after_mask, 'tasks': TASKS, 'actual_calls': 0}), flush=True)

if __name__ == '__main__': main()

import ast
from common_current_C0 import *

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
    if row.get('materialization_qualified') is not True: raise RuntimeError('BATCH2_PUBLIC_VIEW_NOT_MATERIALIZED ' + task)
    root = Path(row['public_source_repo_view']).resolve()
    expected_root = (E / 'public_views' / task / 'repo').resolve()
    if root != expected_root: raise RuntimeError('BATCH2_PUBLIC_VIEW_PATH_DRIFT')
    for rel, expected in row['business_and_support_files_in_view'].items():
        if sha(root / rel) != expected: raise RuntimeError('BATCH2_PUBLIC_VIEW_FILE_DRIFT ' + rel)
    for rel, expected in c['c0_business_paths_sha256'].items():
        if row['business_and_support_files_in_view'].get(rel) != expected or sha(root / rel) != expected:
            raise RuntimeError('BATCH2_PUBLIC_C0_BUSINESS_NOT_EXACT')
    if c['package'] == 'mypy' and any('test-data' in Path(rel).parts or Path(rel).suffix in ('.test', '.data') for rel in row['business_and_support_files_in_view']):
        raise RuntimeError('NEXT_C0_UNMAPPED_DATA_CASE_SUPPORT_VISIBLE')
    trees = {}
    for rel, expected in row['public_test_py_files_SHA256'].items():
        path = (root / rel).resolve()
        if not path.is_relative_to(root) or sha(path) != expected: raise RuntimeError('BATCH2_MASKED_TEST_PATH_OR_SHA_DRIFT')
        trees[rel] = ast.parse(path.read_text('utf-8-sig'), filename=rel)
    goal_checks = []
    for node in c['public_target_nodes']:
        tree = trees.get(node.split('::')[0]); target = exact_function(tree, node) if tree else None
        if target is not None: raise RuntimeError('BATCH2_ORIGINAL_GOAL_FUNCTION_REMAINS_VISIBLE ' + node)
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
        selected = [min(choices)] if choices else []; auxiliary = True
    return {'task_id': task, 'public_view_root': str(root), 'all_current_business_SHA256_exact': True,
        'business_file_count': len(c['c0_business_paths_sha256']), 'declared_masked_test_files': len(trees),
        'public_Goal_function_source_removed': goal_checks, 'original_ordinary_function_available_in_masked_view': ordinary_available,
        'masked_channel_qualification_nodes': selected, 'auxiliary_channel_only_original_G_O_unchanged': auxiliary,
        'auxiliary_selection_rule': 'First lexical available public top-level no-argument test, independent of any test outcome' if auxiliary else None,
        'private_metadata_or_original_unmasked_test_read': False, 'actual_C0_or_channel_qualified': False,
        'source_static_check_not_native_PASS': True}

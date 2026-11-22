"""Trusted masking materializer. Never import/run without an exact Root grant.

Original test bytes and heldout node metadata are read only inside this action.
No model, pytest, product import, Git command, private evaluation, or finance.
"""
import argparse
import ast
import shutil
from common249_ROOT_BATCH2 import *


def mask_text(text, targets):
    """Same AST function/decorator removal and conservative omission as current six."""
    tree = ast.parse(text)
    spans = []
    matched = set()
    def visit(nodes, prefix=()):
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                key = prefix + (node.name,)
                if key in targets or (node.name,) in targets:
                    start = min([node.lineno] + [d.lineno for d in node.decorator_list])
                    spans.append((start, node.end_lineno, node.col_offset))
                    matched.add(key)
            elif isinstance(node, ast.ClassDef):
                visit(node.body, prefix + (node.name,))
    visit(tree.body)
    missing = [key for key in targets if key not in matched and not any(m[-1:] == key[-1:] for m in matched)]
    dynamic_unknown = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                          and n.func.id in ('exec', 'eval', 'globals', 'locals', 'setattr') for n in ast.walk(tree))
    absent = [key for key in missing if key[-1] not in text and not dynamic_unknown]
    missing = [key for key in missing if key not in absent]
    if missing:
        return None, {'masked_count': len(spans), 'unmapped_count': len(missing)}
    lines = text.splitlines(keepends=True)
    for start, end, indent in sorted(spans, reverse=True):
        lines[start - 1:end] = [' ' * indent + 'pass  # withheld independent test\n'] + ['\n'] * (end - start)
    result = ''.join(lines)
    ast.parse(result)
    return result, {'masked_count': len(spans), 'unmapped_count': 0, 'provably_absent_identifier_count': len(absent)}


def test_source(rel):
    return rel.endswith('.py') and (rel.startswith(('tests/', 'test-data/', 'mypy/test/', 'conans/test/')) or '/tests/' in rel or rel == 'conftest.py')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root-grant', required=True)
    args = parser.parse_args()
    grant = Grant(args.root_grant, 'materialize', FIRST_TWO)
    for source_path, expected in grant.value['Root_mask_v2_sources_SHA256'].items():
        if sha(source_path) != expected: raise RuntimeError('EXP249_ROOT_MASK_V2_SOURCE_DRIFT')
    if grant.value['Root_mask_v2_sources_SHA256'].get(str(Path(__file__).resolve())) != sha(__file__):
        raise RuntimeError('EXP249_ROOT_MASK_V2_SELF_NOT_BOUND')
    dest = E / 'public_views_batch2'
    if dest.exists():
        raise RuntimeError('EXP249_MASKING_ONCE_OUTPUT_ALREADY_EXISTS')
    if grant.value.get('max_materialized_tasks') != 2:
        raise RuntimeError('EXP249_MATERIALIZE_COUNT_NOT_BOUND')
    # Bind private metadata with Root's separate seal before any original test read.
    root_inputs = grant.value.get('trusted_masking_inputs', {})
    for task in FIRST_TWO:
        row, c = binding(task)
        approved = root_inputs.get(task, {})
        path = Path(row['Root_only_original_isolation_manifest_path']).resolve()
        if approved.get('manifest_path') != str(path) or approved.get('manifest_SHA256') != sha(path):
            raise RuntimeError('EXP249_ROOT_ISOLATION_METADATA_BINDING_REQUIRED')
        if sha(c['pack']) != c['pack_sha256']:
            raise RuntimeError('EXP249_PUBLIC_PACK_DRIFT')
    dest.mkdir()
    intent(dest / 'STARTED_ONCE.json', {'UTC': now(), 'Root_grant_SHA256': grant.sha256, 'tasks': FIRST_TWO, 'model_native_private_finance': 0})
    rows = []
    provenance = []
    for task in TASKS:
        row, c = binding(task)
        view = dest / task / 'repo'
        public_row = {'task_id': task, 'public_source_repo_view': str(view), 'actor_tests_are_immutable': True,
                      'actors_may_read_or_execute_only_this_public_test_view': True,
                      'public_test_py_files_SHA256': {}, 'business_and_support_files_in_view': {},
                      'materialization_qualified': False, 'current_C0_native_qualified': False,
                      'original_frozen_private_cases_not_read_or_rewritten': True}
        if task not in FIRST_TWO:
            rows.append(public_row)
            continue
        grant.check()
        original = Path(c['template']).resolve()
        meta = read(root_inputs[task]['manifest_path'])
        if meta.get('task_id') != task:
            raise RuntimeError('EXP249_ISOLATION_MANIFEST_TASK_MISMATCH')
        hidden = meta.get('hidden_preservation_tests')
        if not isinstance(hidden, list) or not hidden:
            raise RuntimeError('EXP249_HELDOUT_METADATA_UNAVAILABLE')
        targets = {}
        # Goal source remains hidden even where older hidden-preservation sets differ.
        for node in list(hidden) + list(c['public_target_nodes']):
            parts = node.split('::')
            if len(parts) < 2:
                raise RuntimeError('EXP249_NONFUNCTION_MASK_TARGET')
            rel = safe_rel(parts[0])
            key = tuple(v.split('[', 1)[0] for v in parts[1:])
            targets.setdefault(rel, set()).add(key)
        files = {}; modified = []; omitted = []
        for rel, expected in c['template_inventory'].items():
            grant.check()
            safe_rel(rel)
            src = original / rel
            if src.is_symlink() or not src.resolve().is_relative_to(original) or sha(src) != expected:
                raise RuntimeError('EXP249_ORIGINAL_TEMPLATE_DRIFT')
            target = view / rel
            if rel in targets:
                raw = src.read_bytes()
                try:
                    masked, details = mask_text(raw.decode('utf-8-sig'), targets[rel])
                except (UnicodeError, SyntaxError):
                    masked, details = None, {'masked_count': 0, 'unmapped_count': len(targets[rel])}
                if masked is None:
                    omitted.append({'path': rel, 'policy': 'whole_module_omitted_pending_mask_review', **details})
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(masked.encode('utf-8'))
                modified.append({'path': rel, 'source_SHA256': expected, 'view_SHA256': sha(target), **details})
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, target)
            files[rel] = sha(target)
        for rel in targets:
            if rel not in c['template_inventory']:
                omitted.append({'path': rel, 'policy': 'not_in_original_tracked_public_tree'})
        for rel, h in c['c0_business_paths_sha256'].items():
            if files.get(rel) != h:
                raise RuntimeError('EXP249_MASK_MUST_PRESERVE_EXACT_C0_BUSINESS')
        public_row.update(public_test_py_files_SHA256={p: h for p, h in files.items() if test_source(p)},
                          business_and_support_files_in_view=files, materialization_qualified=True,
                          source_template_inventory_SHA256=digest(c['template_inventory']),
                          withheld_function_body_and_decorator_count=sum(x['masked_count'] for x in modified),
                          conservative_complete_file_omission=[x['path'] for x in omitted],
                          all_Goal_bodies_withheld=True, no_Git_access=True)
        rows.append(public_row)
        provenance.append({'task_id': task, 'original_template': str(original), 'modified_files': modified,
                           'omitted_files': omitted, 'source_manifest_SHA256': root_inputs[task]['manifest_SHA256'],
                           'hidden_node_names_or_source_not_exported': True, 'heldout_count_only': len(hidden),
                           'private_or_gold_execution': 0, 'Root_grant_SHA256': grant.sha256})
    scope = {'schema': 'EXP249-same-current-masked-public-test-boundary/1', 'created_UTC': now(),
             'task_order': TASKS, 'tasks': rows, 'all_three_methods_same_read_execute_permission': True,
             'all_four_methods_same_read_execute_permission': True,
             'legacy_four_methods_field_is_transport_compatibility_not_extra_method': True,
             'original_unmasked_repo_test_source_or_git_blobs_must_not_be_actor_accessible': True,
             'Goal_and_independent_preservation_function_bodies_and_decorators_withheld': True,
             'unknown_dynamic_mapping_omits_entire_module': True, 'actor_tests_immutable': True,
             'source_only': True, 'execution_authorized': False, 'model_authorized': False,
             'private_execution_authorized': False, 'finance_authorized': False}
    save(dest / 'COMMON_MASKED_PUBLIC_TEST_SCOPE249.json', scope)
    save(E / 'trusted_materialization' / 'ROOT_ONLY_MASKING_PROVENANCE249_BATCH2.json',
         {'tasks': provenance, 'original_test_source_not_printed': True, 'model_native_private_finance': 0})
    save(dest / 'COMPLETED_MASKED_MATERIALIZATION249.json',
         {'UTC': now(), 'scope_path': str(dest / 'COMMON_MASKED_PUBLIC_TEST_SCOPE249.json'),
          'scope_SHA256': sha(dest / 'COMMON_MASKED_PUBLIC_TEST_SCOPE249.json'),
          'qualified_tasks': FIRST_TWO, 'remaining_tasks_plan_only': [t for t in TASKS if t not in FIRST_TWO],
          'Root_grant_SHA256': grant.sha256, 'current_C0_native_qualification_pending': True})
    print(canonical({'status': 'MASKED_VIEW_MATERIALIZED_NO_NATIVE', 'tasks': FIRST_TWO,
                     'scope_SHA256': sha(dest / 'COMMON_MASKED_PUBLIC_TEST_SCOPE249.json')}))


if __name__ == '__main__':
    main()

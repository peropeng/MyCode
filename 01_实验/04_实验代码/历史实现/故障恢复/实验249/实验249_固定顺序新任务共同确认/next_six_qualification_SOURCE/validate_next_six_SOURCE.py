"""AST and closed-grant checks only; no native subprocess, API, or test reads."""
import ast
import json
from pathlib import Path
from common_next_six249 import *

checks = []
def check(name, ok):
    if not ok: raise AssertionError(name)
    checks.append({'name': name, 'passed': True})
def refuse(name, action, tasks, value, expected):
    p = E / 'validation_cases' / (name + '.json'); save(p, value)
    try: Grant(p, action, tasks)
    except RuntimeError as exc: check(name, expected in str(exc)); return
    raise AssertionError(name)

protocol = read(E / 'protocol249_SOURCE.json'); rows = read(E / 'TASK_BINDINGS249_SOURCE.json')['tasks']
plan = read(protocol['source_plan21']['path'])
check('fixed_plan21_slots7_to12_exact_order', TASKS == plan['new_main_order'][6:12] and [r['task_id'] for r in rows] == TASKS)
check('six_prepared_zero_current_qualified', len(rows) == 6 and protocol['task_count_currently_qualified'] == 0 and all(r['current_C0_qualified'] is False and r['identity_qualified'] is False and r['public_mask_qualified'] is False for r in rows))
check('historical_and_development_exposure_not_cleared', all(r['historically_exposed'] and r['prior_development_or_mechanism_tags_not_cleared'] and r['not_claimed_unseen_or_training_disjoint'] for r in rows))
for row in rows:
    c = read(row['public_contract'])
    check(row['task_id'] + '_public_contract_raw_bytes_original', sha(row['public_contract']) == row['original_public_contract']['sha256'])
    check(row['task_id'] + '_exact_public_G_O', row['public_goal_nodes'] == c['public_target_nodes'] and row['public_ordinary_nodes'] == c['ordinary_nodes'])
    check(row['task_id'] + '_logical_python_cfg_and_candidate_image_bound',
        sha(row['logical_product_python']) == row['logical_product_python_SHA256']
        and sha(row['pyvenv_cfg']) == row['pyvenv_cfg_SHA256']
        and sha(row['configured_base_candidate']) == row['configured_base_candidate_SHA256']
        and row['configured_path_is_not_actual_physical_identity'])
old = ast.parse((E.parent / 'native249_ROOT_BATCH3_R2.py').read_text('utf-8-sig'))
new = ast.parse((E / 'native_next_six249.py').read_text('utf-8-sig'))
def funcs(tree): return {n.name: ast.dump(n, include_attributes=False) for n in tree.body if isinstance(n, ast.FunctionDef)}
a = funcs(old); b = funcs(new)
for name in ('load_jobs', 'stopped', 'parent_member', 'supervise', 'run_identity'):
    check('qualified_identity_function_unchanged_' + name, a[name] == b[name])
check('no_product_C0_function_in_identity_entry', 'run_current_C0' not in b and 'load_original_probe' not in b)
check('physical_identity_source_byte_exact', sha(E / 'physical_identity249.py') == sha(E.parent / 'physical_identity249.py'))
for p in E.glob('*.py'): ast.parse(p.read_text('utf-8-sig'), filename=str(p))
identity_tree = ast.parse((E / 'physical_identity249.py').read_text('utf-8-sig'), feature_version=(3, 8))
check('physical_identity_source_syntax_accepts_python38', identity_tree is not None)
refuse('closed_identity_stops_before_any_Job_or_source_load', 'identity', [TASKS[0]],
    {'root_authorized': False, 'action': 'identity', 'task_ids': [TASKS[0]]}, 'ROOT_EXACT_ACTION_NOT_GRANTED')
refuse('materialize_has_no_executable_source_authority', 'materialize', [TASKS[0]], {}, 'ONLY_IDENTITY_EXECUTION_SOURCE_READY')
refuse('current_C0_has_no_executable_source_authority', 'current_C0', [TASKS[0]], {}, 'ONLY_IDENTITY_EXECUTION_SOURCE_READY')
refuse('old_first_six_not_accepted_in_new_identity_queue', 'identity', ['dask__dask-9378'],
    {'root_authorized': True, 'action': 'identity', 'task_ids': ['dask__dask-9378']}, 'FIRST_TWO_ONLY_AT_THIS_GATE')
blockers = read(E / 'KNOWN_QUALIFICATION_BLOCKERS_SOURCE.json')
check('mypy10392_old_collection_failure_does_not_become_current_Goal_FAIL', blockers['python__mypy-10392']['current_classification'] == 'UNKNOWN_UNRUN'
    and blockers['python__mypy-10392']['never_fabricate_per_Goal_completed_FAIL'])
check('unmapped_data_driven_cases_stay_unreadable', blockers['mypy_public_mask']['unmapped_case_source_must_not_be_actor_readable'])
check('no_actual_output_directories_created', not (E / 'qualification').exists() and not (E / 'public_views').exists() and not (E / 'ROOT_RELEASES').exists())
result = {'schema': 'EXP249-next-six-minimal-identity-source-validation/1', 'status': 'PASS', 'checks': checks,
    'actual_model_calls': 0, 'actual_native_tests': 0, 'actual_identity_processes': 0, 'actual_Job_operations': 0,
    'private_metadata_or_unmasked_test_or_Gold_reads': 0, 'finance_calls_or_writes': 0, 'training_or_forward': 0,
    'existing_protocol_registry_finance_live_writes': 0, 'current_C0_qualified_count': 0}
save(E / 'SOURCE_VALIDATION.json', result)
print(canonical({'status': 'PASS', 'checks': len(checks), 'validation_SHA256': sha(E / 'SOURCE_VALIDATION.json'), 'actual_calls': 0}), flush=True)

"""One necessary stdlib-only Exp157 split/INITIAL metadata check, before training.

No model/data module imports, neural constructors, tensor loads, Gold or scores.
The root freezer validates actual INITIAL bytes and RNG; this checks its bindings.
"""
import ast
from collections import Counter, defaultdict
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import time
import traceback
import unittest

sys.dont_write_bytecode = True
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
E = Path(__file__).resolve().parent
ROOT = E.parents[3]
E153 = ROOT / '工作区/1007-exp153-global-context/实验/实验153_候选条件全轨迹上下文'
E134 = ROOT / '工作区/1006-exp134-event-relation/实验/实验134_状态动作表示与关系排序'
E138 = ROOT / '工作区/1006-exp138-aftraj-matched/实验/实验138_AFTraj同数据外折四基线比较'
PLAN_SHA = '75a5bbe34d9349bc383cf4cbc6f0a31228090220e979801a436d69f6a72eaa51'
BLOCKS = ('split_A', 'split_B', 'split_C')
ARMS = ('AB_GLOBAL', 'SF_REF', 'AB_REF')
SOURCE_SEEDS = (20261006, 20261007, 20261008)
AF_SEEDS = (20260816, 20260817, 20260818)
EXPECTED_BACKEND = {'deterministic_algorithms': True, 'cudnn_deterministic': True,
                    'cudnn_benchmark': False, 'matmul_allow_tf32': False,
                    'cudnn_allow_tf32': False, 'num_threads': 4}
COUNTERS = {'fixture_runs': 1, 'JSON_metadata_files_read': 0, 'public_metadata_records_parsed': 0,
            'source_partition_reconstructions': 0, 'AF_partition_reconstructions': 0,
            'source_schedule_rows_checked': 0, 'AF_schedule_rows_checked': 0,
            'scaler_fit_bindings_checked': 0, 'INITIAL_binding_rows_checked': 0,
            'unique_parent_INITIAL_metadata_checked': 0, 'runtime_config_checks': 0,
            'model_constructors': 0, 'neural_forwards': 0, 'loss_calls': 0,
            'backward_calls': 0, 'optimizer_updates': 0, 'weight_bytes_read': 0,
            'tensor_deserializations': 0, 'Gold_values_loaded': 0, 'old_scores_loaded': 0,
            'actual_RNG_capture_restore_calls': 0, 'new_encoder_API_downloads': 0}
DETAILS = []
ACCESSED = {}
P = OLD = INITIAL_AUDIT = SOURCE_PUBLIC = AF_PUBLIC = None
SOURCE_EXPECTED = {}
AF_EXPECTED = {}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def safe_file_sha(path):
    path = Path(path).resolve()
    if path.suffix not in ('.json', '.py') or 'private' in path.name or 'labels' in path.name:
        raise RuntimeError('Fixture may only read explicit public/code/protocol JSON metadata: ' + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata_read(path):
    path = Path(path).resolve()
    allowed = {str((E / n).resolve()) for n in ('approved_plan.json', 'protocol.json', 'prepared_inputs.json', 'initialization_audit.json')}
    allowed |= {str((E153 / 'protocol.json').resolve()),
                str((E134 / 'data/public_records.json').resolve()),
                str((E138 / 'data/public_records.json').resolve())}
    if str(path) not in allowed:
        raise RuntimeError('Unapproved metadata file read: ' + str(path))
    value = json.loads(path.read_text('utf-8-sig'))
    COUNTERS['JSON_metadata_files_read'] += 1
    ACCESSED[str(path)] = safe_file_sha(path)
    return value


def write_receipt(path, value):
    path = Path(path).resolve()
    if not path.is_relative_to(E.resolve()) or (path.parent != (E / 'fixtures').resolve()
                                               and path != (E / 'fixture_static_checkpoint.json').resolve()):
        raise RuntimeError('Fixture output outside assigned scope')
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f'.{os.getpid()}.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', 'utf-8')
    os.replace(temporary, path)


def hash_order(groups, prefix):
    return sorted(groups, key=lambda group: (hashlib.sha256((prefix + group).encode('utf-8')).hexdigest(), group))


def expected_source_splits():
    pool = set(OLD['source_ids']['train']) | set(OLD['source_ids']['validation'])
    records = [r for r in SOURCE_PUBLIC if r['sample_id'] in pool]
    if len(records) != 614 or len({r['task_group'] for r in records}) != 614:
        raise RuntimeError('Original614 distinct source group pool required')
    if Counter(r['domain'] for r in records) != {'coding': 320, 'math': 294}:
        raise RuntimeError('Original coding320/math294 source domain pool changed')
    result = {}
    for block in BLOCKS:
        COUNTERS['source_partition_reconstructions'] += 1
        validation_groups = set()
        orders = {}
        for domain, nval in (('coding', 64), ('math', 58)):
            groups = [r['task_group'] for r in records if r['domain'] == domain]
            ordered = hash_order(groups, f'Exp157-source-v1|{block}|{domain}|')
            validation_groups.update(ordered[:nval])
            orders[domain] = ordered
        result[block] = {'fit_ids': [r['sample_id'] for r in records if r['task_group'] not in validation_groups],
                         'validation_ids': [r['sample_id'] for r in records if r['task_group'] in validation_groups],
                         'ordered_groups_by_domain': orders}
    return result


def expected_AF_partitions():
    groups = {r['task_group'] for r in AF_PUBLIC}
    if len(AF_PUBLIC) != 731 or len(groups) != 716:
        raise RuntimeError('Original731 records/716 AF groups required')
    result = {}
    for block in BLOCKS:
        for seed in AF_SEEDS:
            COUNTERS['AF_partition_reconstructions'] += 1
            ordered = hash_order(groups, f'Exp157-AF-v1|{block}|{seed}|')
            result[block, seed] = {'ordered_groups': ordered,
                                  'folds': {fold: [g for i, g in enumerate(ordered) if i % 5 == fold]
                                            for fold in range(5)}}
    return result


def schedule_key(row):
    return row['suite'], row['replication_block'], row['arm'], row['seed'], row.get('outer')


def hex_digest(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


class SplitMetadataBehavior(unittest.TestCase):
    def test_01_source_three_domain_hash_splits_and_public_order(self):
        self.assertEqual(tuple(P['blocks']), BLOCKS)
        self.assertEqual(tuple(P['arms']), ARMS)
        self.assertEqual(tuple(P['source_seeds']), SOURCE_SEEDS)
        self.assertEqual(set(P['source_splits']), set(BLOCKS))
        pool = set(OLD['source_ids']['train']) | set(OLD['source_ids']['validation'])
        by = {r['sample_id']: r for r in SOURCE_PUBLIC}
        for block in BLOCKS:
            split, expected = P['source_splits'][block], SOURCE_EXPECTED[block]
            actual = {'fit_ids': split['ids']['train'], 'validation_ids': split['ids']['validation']}
            self.assertEqual(split['domain_hash_order'], expected['ordered_groups_by_domain'])
            self.assertEqual(P['source_ids'][block], split['ids'])
            for key in ('fit_ids', 'validation_ids'):
                self.assertEqual(actual[key], expected[key], (block, key))
                self.assertEqual(len(actual[key]), len(set(actual[key])))
            fit, validation = actual['fit_ids'], actual['validation_ids']
            self.assertEqual((len(fit), len(validation)), (492, 122))
            self.assertTrue(set(fit).isdisjoint(validation))
            self.assertEqual(set(fit) | set(validation), pool)
            self.assertEqual(Counter(by[s]['domain'] for s in fit), {'coding': 256, 'math': 236})
            self.assertEqual(Counter(by[s]['domain'] for s in validation), {'coding': 64, 'math': 58})
            DETAILS.append({'kind': 'source_block', 'block': block, 'fit492_validation122': True,
                            'domain_counts': {'fit': {'coding': 256, 'math': 236}, 'validation': {'coding': 64, 'math': 58}},
                            'hash_membership_and_original_public_order_exact': True,
                            'old_member_overlap': {new + '_vs_old_' + old: len(set(actual[new]) & set(OLD['source_ids'][old]))
                                                  for new in ('fit_ids', 'validation_ids') for old in ('train', 'validation')}})
        schedule = P['source_schedule']
        self.assertEqual(len(schedule), 27)
        self.assertEqual({(r['replication_block'], r['arm'], r['seed']) for r in schedule},
                         {(b, a, s) for b in BLOCKS for a in ARMS for s in SOURCE_SEEDS})
        for row in schedule:
            COUNTERS['source_schedule_rows_checked'] += 1
            self.assertEqual(row['initialization_seed'], row['seed'])
            self.assertEqual(row['fit_ids'], SOURCE_EXPECTED[row['replication_block']]['fit_ids'])
            self.assertEqual(row['validation_ids'], SOURCE_EXPECTED[row['replication_block']]['validation_ids'])

    def test_02_AF_nine_hash_partitions_nested_groups_and_once_OOF(self):
        self.assertEqual(tuple(P['AF_seeds']), AF_SEEDS)
        old_schedule = {(r['arm'], r['seed'], r['outer']): r for r in OLD['af_schedule']}
        schedule = P['af_schedule']
        self.assertEqual(len(schedule), 135)
        self.assertEqual({(r['replication_block'], r['arm'], r['seed'], r['outer']) for r in schedule},
                         {(b, a, s, o) for b in BLOCKS for a in ARMS for s in AF_SEEDS for o in range(5)})
        for key, partition in AF_EXPECTED.items():
            self.assertEqual([len(partition['folds'][i]) for i in range(5)], [144, 143, 143, 143, 143])
            saved = P['AF_partitions'][key[0]][str(key[1])]
            self.assertEqual(saved['hash_group_order'], partition['ordered_groups'])
            self.assertEqual(saved['fold_groups'], {str(f): groups for f, groups in partition['folds'].items()})
            assignment = {group: i % 5 for i, group in enumerate(partition['ordered_groups'])}
            self.assertEqual(saved['group_fold_assignment'], assignment)
            self.assertEqual(saved['group_fold_assignment_sha256'], digest(assignment))
            DETAILS.append({'kind': 'AF_partition', 'block': key[0], 'seed': key[1],
                            'ordered_group_sha256': digest(partition['ordered_groups']),
                            'fold_group_counts': [144, 143, 143, 143, 143]})
        for row in schedule:
            COUNTERS['AF_schedule_rows_checked'] += 1
            folds = AF_EXPECTED[row['replication_block'], row['seed']]['folds']
            outer = row['outer']
            validation_fold = min(f for f in range(5) if f != outer)
            self.assertEqual(row['validation_fold'], validation_fold)
            expected_groups = {'held_groups': set(folds[outer]), 'validation_groups': set(folds[validation_fold]),
                               'inner_fit_groups': set(g for f in range(5) if f not in (outer, validation_fold) for g in folds[f]),
                               'refit_groups': set(g for f in range(5) if f != outer for g in folds[f])}
            for group_key, ids_key in (('held_groups', 'held_ids'), ('validation_groups', 'validation_ids'),
                                        ('inner_fit_groups', 'selection_fit_ids'), ('refit_groups', 'refit_ids')):
                self.assertEqual(set(row[group_key]), expected_groups[group_key], (row['replication_block'], row['seed'], outer, group_key))
                self.assertEqual(len(row[group_key]), len(set(row[group_key])))
                expected_ids = [r['sample_id'] for r in AF_PUBLIC if r['task_group'] in expected_groups[group_key]]
                self.assertEqual(row[ids_key], expected_ids)
            self.assertTrue(set(row['refit_ids']).isdisjoint(row['held_ids']))
            self.assertTrue(set(row['selection_fit_ids']).isdisjoint(row['validation_ids']))
            old = old_schedule[row['arm'], row['seed'], outer]
            self.assertEqual(row['initialization_seed'], old['initialization_seed'])
            self.assertEqual(row['inference_batches_sha256'],
                             digest([row['held_ids'][i:i + 16] for i in range(0, len(row['held_ids']), 16)]))
        for block in BLOCKS:
            for arm in ARMS:
                for seed in AF_SEEDS:
                    ids = [sid for r in schedule if (r['replication_block'], r['arm'], r['seed']) == (block, arm, seed)
                           for sid in r['held_ids']]
                    self.assertEqual(len(ids), 731)
                    self.assertEqual(len(set(ids)), 731)
                    self.assertEqual(set(ids), {r['sample_id'] for r in AF_PUBLIC})

    def test_03_all_scaler_fit_ID_metadata_bindings(self):
        expected = {}
        for row in P['source_schedule']:
            expected[schedule_key(row) + ('source_fit',)] = row['fit_ids']
        for original in P['af_schedule']:
            row = {'suite': 'AF', **original}
            expected[schedule_key(row) + ('selection',)] = row['selection_fit_ids']
            expected[schedule_key(row) + ('refit',)] = row['refit_ids']
        bindings = P['scaler_fit_specs']
        self.assertEqual(len(bindings), 297)
        self.assertEqual({schedule_key(r) + (r['stage'],) for r in bindings}, set(expected))
        for row in bindings:
            COUNTERS['scaler_fit_bindings_checked'] += 1
            ids = expected[schedule_key(row) + (row['stage'],)]
            self.assertEqual(row['scaler_fit_ids_sha256'], digest(ids))
        DETAILS.append({'kind': 'scaler_fit_contracts', 'stage_bindings': 297,
                        'each_scaler_ID_list_exactly_current_source_or_AF_fit': True,
                        'fixture_did_not_fit_or_load_a_scaler': True})

    def test_04_original_INITIAL_reference_and_RNG_metadata_runtime_config(self):
        self.assertEqual(P['runtime_backend_policy'], EXPECTED_BACKEND)
        self.assertEqual(INITIAL_AUDIT['runtime_backend_policy'], EXPECTED_BACKEND)
        self.assertEqual(INITIAL_AUDIT['status'], 'PASS')
        self.assertTrue(INITIAL_AUDIT['canonical_INITIAL_state_and_RNG_digests_verified'])
        self.assertEqual(INITIAL_AUDIT['unique_canonical153_INITIAL_files'], 54)
        self.assertEqual(INITIAL_AUDIT['final_training_references'], 162)
        self.assertEqual(INITIAL_AUDIT['new_initializations_created'], 0)
        self.assertEqual(INITIAL_AUDIT['new_model_constructors_or_forwards_for_preparation'], 0)
        COUNTERS['runtime_config_checks'] += 1
        old = {(r['suite'], r['arm'], r['seed'], r.get('outer')): r for r in OLD['initialization_records']}
        records = P['initialization_records']
        expected = {('source', b, a, s, None) for b in BLOCKS for a in ARMS for s in SOURCE_SEEDS}
        expected |= {('AF', b, a, s, o) for b in BLOCKS for a in ARMS for s in AF_SEEDS for o in range(5)}
        self.assertEqual(len(records), 162)
        self.assertEqual({schedule_key(r) for r in records}, expected)
        self.assertEqual(INITIAL_AUDIT['records'], records)
        self.assertEqual(P['parameters'], {'AB_GLOBAL': 337457, 'SF_REF': 277633, 'AB_REF': 300593})
        schedules = {schedule_key(r): r for r in P['source_schedule'] + [{'suite': 'AF', **r} for r in P['af_schedule']]}
        paths, fingerprints = set(), {}
        for row in records:
            COUNTERS['INITIAL_binding_rows_checked'] += 1
            previous = old[row['suite'], row['arm'], row['seed'], row.get('outer')]
            path = str(Path(row['path']).resolve())
            self.assertEqual(path, str(Path(previous['path']).resolve()))
            self.assertEqual(Path(path).name, 'initial.pt')
            self.assertNotIn('invalid_runtime', path)
            self.assertEqual(row['sha256'], previous['sha256'])
            self.assertEqual(OLD['initializations'][previous['path']], row['sha256'])
            self.assertEqual(row['canonical_seed'], previous['canonical_seed'])
            self.assertEqual(row['state_digest'], previous['state_digest'])
            self.assertEqual(str(Path(schedules[schedule_key(row)]['initialization_path']).resolve()), path)
            self.assertEqual(row['initialization_seed'], schedules[schedule_key(row)]['initialization_seed'])
            self.assertEqual(row['parameter_count'], P['parameters'][row['arm']])
            self.assertTrue(row['valid_153_INITIAL_only'])
            self.assertEqual(row['trained_parent_weight_loads'], 0)
            self.assertEqual(row['invalid_runtime_asset_loads'], 0)
            rng = row['training_rng_digest']
            self.assertEqual(set(rng), {'python', 'numpy', 'torch', 'cuda'})
            self.assertTrue(all(hex_digest(value) for value in rng.values()))
            signature = (row['sha256'], row['state_digest'], canonical(rng), row['canonical_seed'])
            if path in fingerprints:
                self.assertEqual(signature, fingerprints[path], 'All stress blocks must reference the same canonical INITIAL/RNG')
            fingerprints[path] = signature
            paths.add(path)
        self.assertEqual(len(paths), 54)
        self.assertEqual(set(P['initializations']), paths)
        for path in paths:
            self.assertEqual(P['initializations'][path], fingerprints[path][0])
            COUNTERS['unique_parent_INITIAL_metadata_checked'] += 1
        DETAILS.append({'kind': 'original_INITIAL_metadata', 'final_model_references': 162,
                        'unique_original_initials': 54, 'source_unique': 9, 'AF_unique': 45,
                        'same_INITIAL_state_and_RNG_metadata_across_three_blocks': True,
                        'state_digests_match_original153_JSON_metadata': True,
                        'INITIAL_bytes_and_RNG_digests_verified_by_root_freezer_only': True,
                        'actual_RNG_restoration_will_be_verified_in_every_training_stage': True,
                        'fixture_weight_bytes_or_RNG_operations': 0, 'six_runtime_flags': EXPECTED_BACKEND})


def main():
    global P, OLD, INITIAL_AUDIT, SOURCE_PUBLIC, AF_PUBLIC, SOURCE_EXPECTED, AF_EXPECTED
    if datetime.datetime.now(datetime.timezone.utc) >= datetime.datetime(2026, 10, 7, 1, 58, tzinfo=datetime.timezone.utc):
        raise TimeoutError('NO_NEW_TEST_AFTER0958_BEIJING')
    started = time.monotonic()
    path = E / 'fixtures/split_test_receipt.json'
    previous_runs = []
    if path.exists():
        prior = json.loads(path.read_text('utf-8-sig'))
        prior_bytes = path.read_bytes()
        name = 'split_prior_receipt_' + hashlib.sha256(prior_bytes).hexdigest()[:16] + '.json'
        archive = path.parent / name
        if not archive.exists():
            archive.write_bytes(prior_bytes)
        previous_runs = list(prior.get('prior_runs', []))
        previous_runs.append({'receipt_file': name, 'status': prior['status'], 'tests_run': prior['tests_run'],
                              'compute_counters': prior['compute_counters']})
    stream, result, setup_error = io.StringIO(), None, None
    try:
        self_source = ast.parse((E / 'test_splits157.py').read_text('utf-8-sig'))
        imports = [n.module if isinstance(n, ast.ImportFrom) else ','.join(x.name for x in n.names)
                   for n in ast.walk(self_source) if isinstance(n, (ast.Import, ast.ImportFrom))]
        if any(any(name in str(module) for name in ('torch', 'numpy', 'model', 'data157', 'trainer', 'common')) for module in imports):
            raise RuntimeError('Fixture must import only stdlib; no runtime or data modules')
        plan = metadata_read(E / 'approved_plan.json')
        if safe_file_sha(E / 'approved_plan.json') != PLAN_SHA or tuple(plan['arms']) != ARMS or tuple(plan['stress_blocks']) != BLOCKS:
            raise RuntimeError('Frozen Exp157 plan/arms/blocks changed')
        P = metadata_read(E / 'protocol.json')
        if P['approved_plan_sha256'] != PLAN_SHA:
            raise RuntimeError('Pretrain protocol not bound to Exp157 frozen plan')
        OLD = metadata_read(E153 / 'protocol.json')
        INITIAL_AUDIT = metadata_read(E / 'initialization_audit.json')
        SOURCE_PUBLIC = metadata_read(E134 / 'data/public_records.json')['records']
        AF_PUBLIC = metadata_read(E138 / 'data/public_records.json')['records']
        COUNTERS['public_metadata_records_parsed'] = len(SOURCE_PUBLIC) + len(AF_PUBLIC)
        SOURCE_EXPECTED = expected_source_splits()
        AF_EXPECTED = expected_AF_partitions()
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(SplitMetadataBehavior))
        for file, before in ACCESSED.items():
            if safe_file_sha(file) != before:
                raise RuntimeError('Read-only metadata changed during fixture execution: ' + file)
    except Exception:
        setup_error = traceback.format_exc()
    passed = setup_error is None and result is not None and result.wasSuccessful()
    counters = {k: v + sum(r['compute_counters'].get(k, 0) for r in previous_runs) for k, v in COUNTERS.items()}
    receipt = {'experiment': 'Exp157', 'status': 'PASS' if passed else 'FAIL',
               'kind': 'necessary_pretrain_split_INITIAL_JSON_metadata_only', 'approved_plan_sha256': PLAN_SHA,
               'protocol_sha256': ACCESSED.get(str((E / 'protocol.json').resolve())),
               'at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'tests_run': 0 if result is None else result.testsRun, 'compute_counters': COUNTERS,
               'physical_cumulative_compute_counters': counters, 'prior_runs': previous_runs,
               'source_sha256': {'test_splits157.py': safe_file_sha(E / 'test_splits157.py')},
               'metadata_inputs_sha256': ACCESSED, 'details': DETAILS,
               'no_weights_Gold_or_old_score_reads': True, 'no_model_runtime_imports': True,
               'RNG_and_backend_check_scope': 'Frozen root metadata/config only; this fixture does not instantiate models or access CUDA/RNG',
               'seconds': time.monotonic() - started, 'test_log': stream.getvalue(), 'setup_error': setup_error,
               'failures': [] if result is None else [{'test': str(t), 'traceback': s} for t, s in result.failures],
               'errors': [] if result is None else [{'test': str(t), 'traceback': s} for t, s in result.errors]}
    write_receipt(path, receipt)
    print(stream.getvalue(), end='')
    print(canonical({'status': receipt['status'], 'tests': receipt['tests_run'], 'counts': COUNTERS,
                     'receipt': str(path)}), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())

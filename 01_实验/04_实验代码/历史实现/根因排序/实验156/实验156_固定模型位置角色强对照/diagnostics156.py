"""Post-seal mechanical diagnostics of fixed Exp153/155 caches and Exp156 controls.

This module imports no model/encoder/training code. Importing it reads no assets.
Only run() reads evaluated Gold, old prediction scores, or writes result artifacts.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations
import math
import traceback
import unicodedata

from common import *

SCOPES = (*COHORTS, 'AF')
LENGTH_LABELS = ('[1,4]', '[5,8]', '[9,16]', '[17,32]', '[33,+inf]')
CASE_SALT = 'Exp156-case-v1|'
CASE_TYPES = ('C1', 'C2', 'C3', 'C4')
PARENT_ARMS = {
    'Exp153': ('AB_GLOBAL', 'AB_LOCAL', 'AB_STATIC', 'AB_VALUE_PERM', 'AB_REF', 'SF_REF'),
    'Exp154': ('A_GLOBAL_CAP390', 'AB_GLOBAL_NO_CONTENT', 'AB_GLOBAL_PERM_REL', 'AB_GLOBAL_DUP_TEMPORAL'),
    'Exp155': ('AB_GLOBAL', 'SF_REF', 'AB_REF', 'AB_GLOBAL_DUP_TEMPORAL'),
}
SOURCE_IDENTITY_FIELDS = ('source_identity', 'sourceidentity', 'source_dataset',
                          'domain', 'source_member', 'source_split', 'source_row',
                          'question_ID', 'source_conv_id', 'record_id')
ZERO_NEW_COMPUTE = {'new_model_forward': 0, 'new_optimization_training': 0,
                    'new_neural_models': 0, 'new_encoder': 0, 'new_API': 0,
                    'new_downloads': 0, 'new_Gold': 0, 'new_independent_tasks': 0,
                    'new_ranker_outputs': 0, 'fee_CNY': '0'}
SCHEMA_CONTRACT = {
    'evaluation_outcomes': {'scopes': 'source4+AF', 'scope_fields':
        ['ids', 'gold', 'controls', 'views', 'SF_views']},
    'outputs': ['strata.json', 'cache_consistency.json', 'exact_task_overlap.json',
                'case_evidence/index.json'],
    'strata_axes': ['length', 'Gold_relative_position', 'domain', 'source_member', 'Engineer_present'],
    'case_maximum_distinct_groups': 18,
    'all_diagnostics_descriptive_only': True,
}


def demand(ok, message):
    if not ok:
        raise RuntimeError(message)


def checkpoint_state(phase, **extra):
    path = E / 'diagnostics_static_checkpoint.json'
    old = read(path) if path.exists() else {}
    value = {**old, 'experiment': 'Exp156', 'phase': phase, 'at_utc': now(),
             'approved_plan_sha256': PLAN_SHA, **extra}
    atomic(path, value)
    return value


def scope_public_path(protocol, scope):
    return Path(protocol['AF_public_records'] if scope == 'AF'
                else protocol['target_cohorts'][scope]['public_records'])


def load_public(protocol, evaluated, accessed):
    public = {}
    for scope in SCOPES:
        path = scope_public_path(protocol, scope)
        rows = read(path)['records']
        ids = evaluated['scopes'][scope]['ids']
        demand([r['sample_id'] for r in rows] == ids, 'Public scope/order changed: ' + scope)
        demand(len(ids) == len(set(ids)), 'Duplicate public sample IDs: ' + scope)
        by = {r['sample_id']: r for r in rows}
        for sid in ids:
            record = by[sid]
            demand(isinstance(record.get('task_group'), str) and bool(record['task_group']),
                   'Missing original task_group: ' + sid)
            n = len(record['turns'])
            demand(n > 0 and len(record['coordinate_map']) == n, 'Original public coordinates changed: ' + sid)
            gold = evaluated['scopes'][scope]['gold'][sid]
            demand(type(gold) is int and 0 <= gold < n, 'Evaluated Gold outside original coordinates: ' + sid)
        public[scope] = by
        accessed[str(path.resolve())] = sha(path)
    return public


def verify_gate():
    """Gate is evaluated before any Gold or old score object is decoded."""
    require_time(new_long_task=True)
    demand(sha(E / 'approved_plan.json') == PLAN_SHA, 'Approved Exp156 plan changed')
    protocol_path = E / 'protocol.json'
    seal_path = E / 'results/all_predictions_sealed.json'
    outcomes_path = E / 'evaluation_outcomes.json'
    demand(seal_path.is_file() and outcomes_path.is_file(),
           'ALL18816_PREDICTIONS_SEALED_AND_EVALUATED_REQUIRED_BEFORE_CACHE_DIAGNOSTICS')
    protocol = read(protocol_path)
    seal = read(seal_path)
    demand(protocol['approved_plan_sha256'] == PLAN_SHA and tuple(protocol['controls']) == CONTROLS
           and tuple(protocol['locked_model_views']) == VIEWS, 'Frozen Exp156 identities changed')
    demand(seal['all_fixed_outputs_sealed'] is True and seal['outputs'] == 18816
           and seal['target_labels_joined'] == 0 and seal['new_neural_forward'] == 0
           and seal['protocol_sha256'] == sha(protocol_path), 'Incomplete/unbound Exp156 prediction seal')
    check_hashes(seal['files'])
    inputs = {str(p.resolve()): sha(p) for p in
              (E / 'approved_plan.json', protocol_path, seal_path, outcomes_path)}
    evaluated = read(outcomes_path)
    demand(evaluated['experiment'] == 'Exp156' and evaluated['approved_plan_sha256'] == PLAN_SHA
           and evaluated['protocol_sha256'] == sha(protocol_path)
           and evaluated['prediction_seal_sha256'] == sha(seal_path)
           and evaluated['new_control_outputs'] == 18816,
           'Evaluation outcomes not bound to complete18816 output seal')
    demand(set(evaluated['scopes']) == set(SCOPES), 'All original five scopes required')
    for scope in SCOPES:
        item = evaluated['scopes'][scope]
        ids = item['ids']
        demand(isinstance(ids, list) and len(ids) == len(set(ids)) and set(item['gold']) == set(ids),
               'Evaluation IDs/Gold scope changed: ' + scope)
        demand(set(item['controls']) == set(CONTROLS) and set(item['views']) == set(VIEWS)
               and set(item['SF_views']) == set(VIEWS), 'Fixed control/view scope changed: ' + scope)
        for kind in ('controls', 'views', 'SF_views'):
            for name, rows in item[kind].items():
                demand(set(rows) == set(ids), 'Complete evaluation denominator required: ' + name)
                for sid, row in rows.items():
                    demand(row['sample_id'] == sid and type(row['Top1']) is int and row['Top1'] in (0, 1),
                           'Evaluation outcome schema changed: ' + sid)
    return protocol, seal, evaluated, inputs


def descriptive_summary(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row['task_group']].append(row)
    record, group = {}, {}
    for key in ('Top1', 'MRR', 'Top3'):
        available = bool(rows) and all(r.get(key) is not None for r in rows)
        record[key] = math.fsum(float(r[key]) for r in rows) / len(rows) if available else None
        group[key] = (math.fsum(math.fsum(float(r[key]) for r in rs) / len(rs)
                               for rs in groups.values()) / len(groups) if available else None)
    return {'records': len(rows), 'groups': len(groups), 'record_equal': record, 'group_equal': group,
            'record_Top1_hits': sum(r['Top1'] for r in rows),
            'invalid_records': sum(r.get('valid') is not True for r in rows),
            'group_equal_invalid_rate': (math.fsum(sum(r.get('valid') is not True for r in rs) / len(rs)
                                                  for rs in groups.values()) / len(groups) if groups else None),
            'complete_original_denominator_kept': True}


def pair_description(left, right, ids, public):
    grouped = defaultdict(list)
    changes = []
    for sid in ids:
        delta = left[sid]['Top1'] - right[sid]['Top1']
        changes.append(delta)
        grouped[public[sid]['task_group']].append(delta)
    group_changes = [Fraction(sum(values), len(values)) for values in grouped.values()]
    return {'records': len(ids), 'groups': len(grouped),
            'record_equal': {'left_minus_right_Top1': sum(changes) / len(changes) if changes else None,
                'positive_records': sum(x > 0 for x in changes), 'negative_records': sum(x < 0 for x in changes),
                'tied_records': sum(x == 0 for x in changes)},
            'group_equal': {'left_minus_right_Top1': float(sum(group_changes) / len(group_changes)) if group_changes else None,
                'positive_groups': sum(x > 0 for x in group_changes), 'negative_groups': sum(x < 0 for x in group_changes),
                'tied_groups': sum(x == 0 for x in group_changes)},
            'descriptive_only': True, 'new_p_values': 0}


def method_rows(item):
    rows = {f'primary/{view}': item['views'][view] for view in VIEWS}
    rows.update({f'SF/{view}': item['SF_views'][view] for view in VIEWS})
    rows.update({f'control/{name}': item['controls'][name] for name in CONTROLS})
    return rows


def subset_table(item, public, ids):
    methods = method_rows(item)
    pairs = {}
    for view in VIEWS:
        pairs[f'{view}_vs_matching_SF'] = pair_description(item['views'][view], item['SF_views'][view], ids, public)
        for control in CONTROLS:
            pairs[f'{view}_vs_{control}'] = pair_description(item['views'][view], item['controls'][control], ids, public)
    changes = {f'{left}_minus_{right}': pair_description(item['views'][left], item['views'][right], ids, public)
               for left, right in combinations(VIEWS, 2)}
    return {'records': len(ids), 'groups': len({public[s]['task_group'] for s in ids}),
            'sample_ids': ids, 'metrics': {name: descriptive_summary([rows[s] for s in ids])
                                         for name, rows in methods.items()},
            'paired_primary_differences': pairs, 'three_primary_view_changes': changes}


def build_strata(evaluated, public):
    result = {}
    for scope in SCOPES:
        item, by = evaluated['scopes'][scope], public[scope]
        buckets = {axis: defaultdict(list) for axis in SCHEMA_CONTRACT['strata_axes']}
        for value in LENGTH_LABELS:
            buckets['length'][value] = []
        for value in ('0', '1', '2', '3'):
            buckets['Gold_relative_position'][value] = []
        for value in ('absent', 'present'):
            buckets['Engineer_present'][value] = []
        for sid in item['ids']:
            record = by[sid]
            n, target = len(record['turns']), item['gold'][sid]
            length = '[1,4]' if n <= 4 else '[5,8]' if n <= 8 else '[9,16]' if n <= 16 else '[17,32]' if n <= 32 else '[33,+inf]'
            relative = 0 if n == 1 else min(3, (4 * target) // (n - 1))
            engineer = any(str(t.get('role', '')).strip().casefold() == 'engineer' for t in record['turns'])
            values = {'length': length, 'Gold_relative_position': str(relative),
                      'domain': str(record.get('domain') or 'UNKNOWN'),
                      'source_member': str(record.get('source_member') or 'UNKNOWN'),
                      'Engineer_present': 'present' if engineer else 'absent'}
            for axis, value in values.items():
                buckets[axis][value].append(sid)
        result[scope] = {'overall': subset_table(item, by, item['ids']),
                         'tables': {axis: {name: subset_table(item, by, groups[name])
                                           for name in (LENGTH_LABELS if axis == 'length' else sorted(groups))}
                                    for axis, groups in buckets.items()}}
    return {'scopes': result, 'definitions': SCHEMA_CONTRACT['strata_axes'],
            'length_bins': [[1, 4], [5, 8], [9, 16], [17, 32], [33, None]],
            'Gold_relative_position': 'n=1:0; otherwise min(3,floor(4*y/(n-1)))',
            'Engineer_definition': "public turn.role strip+casefold exact 'engineer'",
            'source_member_missing': 'UNKNOWN; no sample ID parsing',
            'AF_group_unit': 'Each original group has weight1 within the stratum; average its included records first',
            'groups_may_span_strata_and_are_not_new_independent_tasks': True,
            'new_p_values': 0, 'new_threshold_searches': 0}


class CachedPredictions:
    """Validate JSON cache bindings; never load a neural checkpoint."""
    def __init__(self, protocol, control_seal, accessed):
        self.accessed = accessed
        self.expected = {str(Path(p).resolve()): h for p, h in control_seal['files'].items()}
        self.read_events = 0
        self.rows_parsed = 0
        protected = {str(Path(p).resolve()): h for p, h in protocol['protected_old_files_sha256'].items()}
        for root, key in ((E153, 'predseal153_sha256'), (E154, 'predseal154_sha256'), (E155, 'predseal155_sha256')):
            path = root / 'results/all_predictions_sealed.json'
            current = sha(path)
            if str(path.resolve()) in protected:
                demand(current == protected[str(path.resolve())], 'Immutable parent seal changed')
            parents = read(E / 'approved_plan.json')['parents']
            if key in parents:
                demand(current == parents[key], 'Approved parent prediction seal changed')
            seal = read(path)
            demand(seal['all_fixed_outputs_sealed'] is True, 'Only valid sealed parent caches allowed')
            self.expected.update({str(Path(p).resolve()): h for p, h in seal['files'].items()})
            accessed[str(path.resolve())] = current

    def load(self, path, ids, public):
        require_time()
        path = Path(path).resolve()
        demand('invalid_runtime' not in str(path) and str(path) in self.expected,
               'Cache must appear in an original valid prediction seal: ' + str(path))
        current = sha(path)
        demand(current == self.expected[str(path)], 'Sealed prediction cache changed: ' + str(path))
        saved = read(path)
        predictions = saved['predictions']
        demand(set(predictions) == set(ids), 'Full original cache denominator changed: ' + str(path))
        self.read_events += 1
        self.rows_parsed += len(predictions)
        self.accessed[str(path)] = current
        for sid, row in predictions.items():
            n = len(public[sid]['turns'])
            if row.get('valid') is True:
                order = row.get('order', row.get('ranking'))
                chosen = row.get('chosen_step', row.get('predicted_step'))
                demand(isinstance(order, list) and len(order) == n and all(type(i) is int for i in order)
                       and sorted(order) == list(range(n)) and chosen == order[0],
                       'Native complete original-coordinate cache rank required: ' + sid)
                for field in ('scores', 'probabilities'):
                    values = row.get(field)
                    if values is not None:
                        demand(isinstance(values, list) and len(values) == n
                               and all(type(v) in (int, float) and math.isfinite(v) for v in values),
                               'Native cache score shape changed: ' + sid)
        return predictions


def parent_path(root, scope, arm, variant):
    return root / 'results' / scope / f'{arm}_{variant}.json'


def prediction_outcome(prediction, record, gold):
    valid = prediction.get('valid') is True
    chosen = prediction.get('chosen_step', prediction.get('predicted_step')) if valid else None
    order = prediction.get('order', prediction.get('ranking'))
    return {'sample_id': record['sample_id'], 'task_group': record['task_group'],
            'chosen_step': chosen, 'valid': valid, 'Top1': int(valid and chosen == gold),
            'MRR': 1 / (order.index(gold) + 1) if valid else 0.,
            'Top3': bool(gold in order[:3]) if valid else False}


def choice_agreement(left, right):
    return bool(left.get('valid') is True and right.get('valid') is True
                and left.get('chosen_step') == right.get('chosen_step'))


def average(values):
    return math.fsum(float(x) for x in values) / len(values) if values else None


def build_cache_consistency(evaluated, public, cache):
    result = {}
    for scope in SCOPES:
        item, by = evaluated['scopes'][scope], public[scope]
        old_seeds = AF_NEURAL_153_SEEDS if scope == 'AF' else SOURCE_NEURAL_153_SEEDS
        new_seeds = AF_NEURAL_155_SEEDS if scope == 'AF' else SOURCE_NEURAL_155_SEEDS
        sequence = [('Exp153', E153, s) for s in old_seeds] + [('Exp155', E155, s) for s in new_seeds]
        primary, sf = [], []
        seed_labels, sources = [], []
        for parent, root, seed in sequence:
            seed_labels.append(f'{parent}/seed_{seed}')
            pair = []
            for arm in ('AB_GLOBAL', 'SF_REF'):
                path = parent_path(root, scope, arm, seed)
                raw = cache.load(path, item['ids'], by)
                rows = {sid: prediction_outcome(raw[sid], by[sid], item['gold'][sid]) for sid in item['ids']}
                pair.append(rows)
                sources.append({'condition': f'{parent}/{arm}/seed_{seed}', 'source_path': str(path.resolve()),
                                'source_sha256': cache.accessed[str(path.resolve())]})
            primary.append(pair[0]); sf.append(pair[1])
        records = {}
        grouped = defaultdict(list)
        for sid in item['ids']:
            group = by[sid]['task_group']
            main_flags = [v[sid]['Top1'] for v in primary]
            sf_flags = [v[sid]['Top1'] for v in sf]
            main_pattern = [item['views'][v][sid]['Top1'] for v in VIEWS]
            sf_pattern = [item['SF_views'][v][sid]['Top1'] for v in VIEWS]
            agreements = {control: {view: int(choice_agreement(item['controls'][control][sid], item['views'][view][sid]))
                                     for view in VIEWS} for control in CONTROLS}
            records[sid] = {'sample_id': sid, 'task_group': group, 'nine_seed_primary_correct': main_flags,
                            'nine_seed_SF_correct': sf_flags, 'primary_correct_count9': sum(main_flags),
                            'SF_correct_count9': sum(sf_flags),
                            'paired_primary_minus_SF_seed_flags': [a - b for a, b in zip(main_flags, sf_flags)],
                            'three_primary_ensemble_correct_pattern': main_pattern,
                            'three_SF_ensemble_correct_pattern': sf_pattern,
                            'paired_primary_minus_SF_ensemble_flags': [a - b for a, b in zip(main_pattern, sf_pattern)],
                            'simple_control_primary_Top1_choice_agreement': agreements,
                            'primary_SF_Top1_choice_agreement': {v: int(choice_agreement(item['views'][v][sid], item['SF_views'][v][sid]))
                                                                 for v in VIEWS}}
            grouped[group].append(sid)
        groups = {}
        for group, ids in sorted(grouped.items()):
            groups[group] = {'task_group': group, 'sample_ids': ids, 'records': len(ids),
                'nine_seed_primary_group_correct_rates': [average([records[s]['nine_seed_primary_correct'][i] for s in ids]) for i in range(9)],
                'nine_seed_SF_group_correct_rates': [average([records[s]['nine_seed_SF_correct'][i] for s in ids]) for i in range(9)],
                'mean_record_primary_correct_count9': average([records[s]['primary_correct_count9'] for s in ids]),
                'mean_record_SF_correct_count9': average([records[s]['SF_correct_count9'] for s in ids]),
                'three_primary_ensemble_group_correct_rates': [average([records[s]['three_primary_ensemble_correct_pattern'][i] for s in ids]) for i in range(3)],
                'three_SF_ensemble_group_correct_rates': [average([records[s]['three_SF_ensemble_correct_pattern'][i] for s in ids]) for i in range(3)],
                'simple_control_primary_Top1_choice_agreement': {c: {v: average([records[s]['simple_control_primary_Top1_choice_agreement'][c][v] for s in ids])
                                                                   for v in VIEWS} for c in CONTROLS},
                'primary_SF_Top1_choice_agreement': {v: average([records[s]['primary_SF_Top1_choice_agreement'][v] for s in ids]) for v in VIEWS}}
        agreement_summary = {c: {v: {'record_equal': average([r['simple_control_primary_Top1_choice_agreement'][c][v] for r in records.values()]),
                                         'group_equal': average([g['simple_control_primary_Top1_choice_agreement'][c][v] for g in groups.values()])}
                                  for v in VIEWS} for c in CONTROLS}
        result[scope] = {'records': len(records), 'groups': len(groups), 'seed_order': seed_labels,
                        'ensemble_order': list(VIEWS), 'source_files': sources, 'record_details': records,
                        'group_details': groups, 'simple_control_primary_choice_agreement': agreement_summary,
                        'record_correct_count_histogram': {
                            'primary': {str(i): sum(r['primary_correct_count9'] == i for r in records.values()) for i in range(10)},
                            'SF': {str(i): sum(r['SF_correct_count9'] == i for r in records.values()) for i in range(10)}},
                        'three_primary_record_pattern_histogram': dict(sorted(Counter(''.join(map(str, r['three_primary_ensemble_correct_pattern'])) for r in records.values()).items())),
                        'three_SF_record_pattern_histogram': dict(sorted(Counter(''.join(map(str, r['three_SF_ensemble_correct_pattern'])) for r in records.values()).items())),
                        'group_equal_mean_correct_count9': {'primary': average([g['mean_record_primary_correct_count9'] for g in groups.values()]),
                                                          'SF': average([g['mean_record_SF_correct_count9'] for g in groups.values()])}}
    return {'scopes': result, 'nine_seed_repetitions_are_not_independent_tasks': True,
            'AF_group_handling': 'Record outcomes averaged within each original group, then each group gets weight1',
            'partial_group_correctness_kept_as_fraction_not_forced_to_bool': True,
            'choice_agreement_definition': 'Both valid and same native original chosen_step; invalid/None never counts as agreement',
            'cached_ranker_outputs_new_count': 0, 'new_p_values': 0}


def normalized_task_hash(record):
    task = record.get('task')
    demand(task is None or isinstance(task, str), 'Public task text schema changed')
    normalized = ' '.join(unicodedata.normalize('NFKC', task or '').casefold().split())
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest() if normalized else None


def identity_entry(dataset, record):
    existing = {key: record[key] for key in SOURCE_IDENTITY_FIELDS if key in record}
    task_hash = normalized_task_hash(record)
    # Exact existing field tuples only; no sample-ID parsing or guessed identity.
    if record.get('source_identity') not in (None, ''):
        identity = {'source_identity': record['source_identity']}
    elif record.get('sourceidentity') not in (None, ''):
        identity = {'sourceidentity': record['sourceidentity']}
    elif record.get('source_conv_id') not in (None, ''):
        identity = {'source_conv_id': record['source_conv_id']}
    elif record.get('source_member') not in (None, '') and record.get('source_row') is not None:
        identity = {key: record.get(key) for key in ('domain', 'source_member', 'source_split', 'source_row')}
    else:
        identity = None
    return {'dataset': dataset, 'sample_id': record['sample_id'], 'task_group': record['task_group'],
            'task_text_sha256': task_hash,
            'task_text_status': 'KNOWN' if task_hash else 'UNKNOWN',
            'existing_source_identity_fields': existing,
            'source_identity_exact_field_tuple': identity}


def overlap_by_key(left, right, key):
    a, b = defaultdict(list), defaultdict(list)
    for rows, table in ((left, a), (right, b)):
        for row in rows:
            value = row.get(key)
            if value is not None and value != '':
                table[canonical(value) if isinstance(value, dict) else str(value)].append(row)
    matches = sorted(set(a) & set(b))
    listing = [{'value': value, 'left_records': a[value], 'right_records': b[value]} for value in matches]
    return {'distinct_intersection_values': len(matches),
            'left_matching_records': sum(len(a[v]) for v in matches),
            'right_matching_records': sum(len(b[v]) for v in matches),
            'left_matching_groups': len({r['task_group'] for v in matches for r in a[v]}),
            'right_matching_groups': len({r['task_group'] for v in matches for r in b[v]}),
            'matches': listing}


def overlap_comparison(left, right):
    return {'left_records': len(left), 'right_records': len(right),
            'left_groups': len({r['task_group'] for r in left}),
            'right_groups': len({r['task_group'] for r in right}),
            'exact_normalized_task_text': overlap_by_key(left, right, 'task_text_sha256'),
            'original_task_group': overlap_by_key(left, right, 'task_group'),
            'existing_source_identity_exact_field_tuple': overlap_by_key(left, right, 'source_identity_exact_field_tuple'),
            'left_UNKNOWN_task_records': sum(r['task_text_sha256'] is None for r in left),
            'right_UNKNOWN_task_records': sum(r['task_text_sha256'] is None for r in right)}


def build_exact_overlap(protocol, public, accessed):
    source_path = Path(protocol['source_public_records'])
    source = {r['sample_id']: r for r in read(source_path)['records']}
    accessed[str(source_path.resolve())] = sha(source_path)
    fit_ids, val_ids = protocol['source_fit_ids'], protocol['source_validation_ids']
    demand((len(fit_ids), len(val_ids)) == (492, 122) and set(fit_ids).isdisjoint(val_ids),
           'Original492/122 source identity-audit scope changed')
    datasets = {'source_fit492': [identity_entry('source_fit492', source[s]) for s in fit_ids],
                'source_validation122': [identity_entry('source_validation122', source[s]) for s in val_ids]}
    datasets.update({scope: [identity_entry(scope, r) for r in public[scope].values()] for scope in SCOPES})
    targets = [r for scope in COHORTS for r in datasets[scope]]
    demand(len(targets) == 2155 and len(datasets['AF']) == 731, 'All2155 target/731 AF records required')
    source_target = {}
    for source_name in ('source_fit492', 'source_validation122'):
        source_target[source_name + '_vs_all2155targets'] = overlap_comparison(datasets[source_name], targets)
        for cohort in COHORTS:
            source_target[source_name + '_vs_' + cohort] = overlap_comparison(datasets[source_name], datasets[cohort])
    cross = {left + '_vs_' + right: overlap_comparison(datasets[left], datasets[right])
             for left, right in combinations(COHORTS, 2)}
    af = {r['sample_id']: r for r in datasets['AF']}
    schedule = protocol['AF_schedule']
    demand(len(schedule) == 15 and {(r['seed'], r['outer']) for r in schedule}
           == {(s, f) for s in AF_SEEDS for f in range(5)}, 'Exact original15 AF schedules required')
    folds = []
    for row in schedule:
        left = [af[s] for s in row['refit_ids']]
        right = [af[s] for s in row['held_ids']]
        fit_groups = sorted({r['task_group'] for r in left})
        held_groups = sorted({r['task_group'] for r in right})
        demand(set(fit_groups) == set(row['refit_groups']) and set(held_groups) == set(row['held_groups']),
               'Original AF fold group/record lists changed')
        folds.append({'seed': row['seed'], 'outer': row['outer'],
                      'refit_groups': fit_groups, 'held_groups': held_groups,
                      'original_group_intersection': sorted(set(fit_groups) & set(held_groups)),
                      'original_group_intersection_count': len(set(fit_groups) & set(held_groups)),
                      'refit_vs_held': overlap_comparison(left, right)})
    return {'normalization': 'UnicodeNFKC then casefold then whitespace split/join; SHA256 of UTF8',
            'UNKNOWN_empty_tasks_do_not_match_each_other': True,
            'source_identity_definition': 'Only explicit source_identity/sourceidentity, source_conv_id, or exact existing(domain,source_member,source_split,source_row) tuple; raw original fields shown beside each record',
            'source_identity_missing_not_inferred': True,
            'records_by_dataset': {name: {r['sample_id']: r for r in rows} for name, rows in datasets.items()},
            'dataset_counts': {name: {'records': len(rows), 'groups': len({r['task_group'] for r in rows}),
                                     'UNKNOWN_tasks': sum(r['task_text_sha256'] is None for r in rows)}
                               for name, rows in datasets.items()},
            'source_fit_and_validation_vs_targets': source_target,
            'cross_target_cohorts': cross, 'AF_original15_refit_vs_held': folds,
            'exact_text_overlap_is_not_a_Gold_or_leakage_claim': True,
            'sample_removals': 0, 'alternative_score_recomputations': 0,
            'fuzzy_matches': 0, 'new_embeddings': 0}


def fraction_payload(value):
    return {'numerator': value.numerator, 'denominator': value.denominator, 'value': float(value)}


def group_eligibility(scope, item, public):
    grouped = defaultdict(list)
    for sid in item['ids']:
        grouped[public[sid]['task_group']].append(sid)
    result = {}
    for group, ids in sorted(grouped.items()):
        ids = sorted(ids)
        primary = {v: Fraction(sum(item['views'][v][s]['Top1'] for s in ids), len(ids)) for v in VIEWS}
        sf = {v: Fraction(sum(item['SF_views'][v][s]['Top1'] for s in ids), len(ids)) for v in VIEWS}
        controls = {c: Fraction(sum(item['controls'][c][s]['Top1'] for s in ids), len(ids)) for c in CONTROLS}
        eligibility = {'C1': all(x == 1 for x in primary.values()) and all(x == 0 for x in sf.values()),
                       'C2': all(x == 0 for x in primary.values()) and all(x == 1 for x in sf.values()),
                       'C3': len(set(primary.values())) > 1,
                       'C4': all(x == 1 for x in primary.values()) and any(x == 1 for x in controls.values())}
        result[group] = {'scope': scope, 'task_group': group, 'sample_ids': ids, 'records': len(ids),
                         'representative_sample_id': ids[0],
                         'case_sort_sha256': hashlib.sha256((CASE_SALT + group).encode('utf-8')).hexdigest(),
                         'primary_group_correct_rates': {k: fraction_payload(v) for k, v in primary.items()},
                         'SF_group_correct_rates': {k: fraction_payload(v) for k, v in sf.items()},
                         'control_group_correct_rates': {k: fraction_payload(v) for k, v in controls.items()},
                         'eligible': eligibility,
                         'record_qualification': {s: {'primary': {v: item['views'][v][s]['Top1'] for v in VIEWS},
                                                      'SF': {v: item['SF_views'][v][s]['Top1'] for v in VIEWS},
                                                      'controls': {c: item['controls'][c][s]['Top1'] for c in CONTROLS}}
                                                  for s in ids}}
    return result


def case_variants(parent, scope):
    if parent == 'Exp155':
        return (*(AF_NEURAL_155_SEEDS if scope == 'AF' else SOURCE_NEURAL_155_SEEDS), 'block_A', 'block_B')
    return (*(AF_NEURAL_153_SEEDS if scope == 'AF' else SOURCE_NEURAL_153_SEEDS), 'ensemble')


def export_cases(protocol, evaluated, public, cache, metadata):
    all_groups, pools, selected, used = {}, [], [], set()
    for scope in ('coding363', 'AF'):
        item, by = evaluated['scopes'][scope], public[scope]
        eligibility = group_eligibility(scope, item, by)
        all_groups[scope] = eligibility
        for category in CASE_TYPES:
            pool = sorted((g for g, row in eligibility.items() if row['eligible'][category]),
                          key=lambda g: (eligibility[g]['case_sort_sha256'], g))
            unused = [g for g in pool if g not in used]
            chosen = unused[:2]
            for group in chosen:
                selected.append({'scope': scope, 'category': category, **eligibility[group]})
                used.add(group)
            pools.append({'scope': scope, 'category': category, 'eligible_groups_hash_order': pool,
                          'already_selected_groups_excluded': [g for g in pool if g in used and g not in chosen],
                          'eligible_unused_groups': len(unused), 'selected_groups': chosen,
                          'selected_count': len(chosen), 'quota': 2, 'no_replacement_for_short_pool': True})
    scope = 'math155'
    item, by = evaluated['scopes'][scope], public[scope]
    no_content_path = parent_path(E154, scope, 'AB_GLOBAL_NO_CONTENT', 'ensemble')
    raw = cache.load(no_content_path, item['ids'], by)
    no_content = {sid: prediction_outcome(raw[sid], by[sid], item['gold'][sid]) for sid in item['ids']}
    eligibility = group_eligibility(scope, item, by)
    for group, row in eligibility.items():
        ids = row['sample_ids']
        old_global = Fraction(sum(item['views'][VIEWS[0]][s]['Top1'] for s in ids), len(ids))
        control = Fraction(sum(no_content[s]['Top1'] for s in ids), len(ids))
        row['eligible'] = {'MATH_SHARED_GLOBAL_NO_CONTENT': old_global == 1 and control == 1}
        row['NO_CONTENT_group_correct_rate'] = fraction_payload(control)
        for sid in ids:
            row['record_qualification'][sid]['Exp154_NO_CONTENT'] = no_content[sid]['Top1']
    all_groups[scope] = eligibility
    pool = sorted((g for g, row in eligibility.items() if row['eligible']['MATH_SHARED_GLOBAL_NO_CONTENT']),
                  key=lambda g: (eligibility[g]['case_sort_sha256'], g))
    unused = [g for g in pool if g not in used]
    chosen = unused[:2]
    for group in chosen:
        selected.append({'scope': scope, 'category': 'MATH_SHARED_GLOBAL_NO_CONTENT', **eligibility[group]})
        used.add(group)
    pools.append({'scope': scope, 'category': 'MATH_SHARED_GLOBAL_NO_CONTENT',
                  'eligible_groups_hash_order': pool,
                  'already_selected_groups_excluded': [g for g in pool if g in used and g not in chosen],
                  'eligible_unused_groups': len(unused), 'selected_groups': chosen,
                  'selected_count': len(chosen), 'quota': 2, 'no_replacement_for_short_pool': True})
    demand(len(selected) <= 18 and len(used) == len(selected), 'Case quota/global group deduplication failed')
    # Decode each native score file once for this export, retaining only selected records.
    native_by_case = {(r['scope'], r['representative_sample_id']): {} for r in selected}
    for scope in ('coding363', 'AF', 'math155'):
        selected_sids = [r['representative_sample_id'] for r in selected if r['scope'] == scope]
        if not selected_sids:
            continue
        ids, by = evaluated['scopes'][scope]['ids'], public[scope]
        for parent, root in (('Exp153', E153), ('Exp154', E154), ('Exp155', E155)):
            for arm in PARENT_ARMS[parent]:
                for variant in case_variants(parent, scope):
                    path = parent_path(root, scope, arm, variant)
                    raw = cache.load(path, ids, by)
                    for sid in selected_sids:
                        native_by_case[scope, sid][f'{parent}/{arm}/{variant}'] = {
                            'source_path': str(path.resolve()), 'source_sha256': cache.accessed[str(path.resolve())],
                            'prediction': raw[sid]}
        for control in CONTROLS:
            path = control_prediction_path(scope, control)
            raw = cache.load(path, ids, by)
            for sid in selected_sids:
                native_by_case[scope, sid][f'Exp156/{control}'] = {
                    'source_path': str(path.resolve()), 'source_sha256': cache.accessed[str(path.resolve())],
                    'prediction': raw[sid]}
    files, index_rows = {}, []
    for ordinal, selection in enumerate(selected, 1):
        scope, sid = selection['scope'], selection['representative_sample_id']
        record = public[scope][sid]
        path = E / 'case_evidence' / f"{scope}_{ordinal:02d}_{selection['case_sort_sha256'][:12]}.json"
        predictions = native_by_case[scope, sid]
        demand(len(predictions) == 77, 'Each case must retain72 parent and5 current predictions')
        body = {**metadata, 'scope': scope, 'case_category': selection['category'],
                'task_group': record['task_group'], 'representative_sample_id': sid,
                'representative_rule': 'Lexicographically smallest sample_id in the selected original group',
                'selection': selection, 'public_record': record,
                'task': record.get('task'), 'turns': record['turns'], 'coordinate_map': record['coordinate_map'],
                'Gold_original_ordinal': evaluated['scopes'][scope]['gold'][sid],
                'source_public_records': str(scope_public_path(protocol, scope).resolve()),
                'source_public_records_sha256': cache.accessed[str(scope_public_path(protocol, scope).resolve())],
                'cached_and_new_control_predictions': predictions,
                'original_predictions_exported_without_score_or_rank_fabrication': True,
                'AF_AA_Binary_SDBL_optional_single_choice_not_exported_or_reranked': True,
                'mechanical_evidence_only_no_root_cause_interpretation': True,
                'selected_explanatory_cases_are_not_independent_statistical_denominators': True}
        atomic(path, body)
        files[str(path.resolve())] = sha(path)
        index_rows.append({'scope': scope, 'category': selection['category'], 'task_group': record['task_group'],
                           'representative_sample_id': sid, 'case_sort_sha256': selection['case_sort_sha256'],
                           'path': str(path.resolve()), 'sha256': files[str(path.resolve())]})
    index = {**metadata, 'case_salt': CASE_SALT, 'scope_order': ['coding363', 'AF', 'math155'],
             'category_order': list(CASE_TYPES), 'maximum_cases': 18, 'selected_count': len(selected),
             'selected_groups': index_rows, 'pools': pools, 'all_group_eligibility_details': all_groups,
             'across_scope_task_group_deduplication': True, 'no_replacement_for_short_pools': True,
             'AF_case_eligibility_uses_exact_group_mean_1_or_0_and_C3_inequality': True,
             'case_files_sha256': files}
    index_path = E / 'case_evidence/index.json'
    atomic(index_path, index)
    files[str(index_path.resolve())] = sha(index_path)
    return index, files


def run():
    started = time.monotonic()
    protocol, seal, evaluated, inputs = verify_gate()
    accessed = dict(inputs)
    code_hashes = {str((E / name).resolve()): sha(E / name)
                   for name in ('diagnostics156.py', 'common.py')}
    old_checkpoint = read(E / 'diagnostics_static_checkpoint.json') if (E / 'diagnostics_static_checkpoint.json').exists() else {}
    history = list(old_checkpoint.get('run_history', []))
    history.append({'started_utc': now(), 'status': 'RUNNING', 'new_compute': ZERO_NEW_COMPUTE})
    checkpoint_state('RUNNING_POST_SEAL_CACHE_DIAGNOSTICS', status='RUNNING',
                     run_history=history, input_hashes=inputs, code_sha256=code_hashes,
                     current_pid=os.getpid(), new_compute=ZERO_NEW_COMPUTE, actual_run_started=True)
    try:
        public = load_public(protocol, evaluated, accessed)
        cache = CachedPredictions(protocol, seal, accessed)
        metadata = {'experiment': 'Exp156', 'status': 'COMPLETE', 'at_utc': now(),
                    'approved_plan_sha256': PLAN_SHA, 'protocol_sha256': sha(E / 'protocol.json'),
                    'prediction_seal_sha256': sha(E / 'results/all_predictions_sealed.json'),
                    'evaluation_outcomes_sha256': sha(E / 'evaluation_outcomes.json'),
                    'descriptive_only': True, 'new_compute': ZERO_NEW_COMPUTE}
        results = {}
        for name, value in (('strata.json', build_strata(evaluated, public)),
                            ('cache_consistency.json', build_cache_consistency(evaluated, public, cache)),
                            ('exact_task_overlap.json', build_exact_overlap(protocol, public, accessed))):
            require_time()
            path = E / name
            atomic(path, {**metadata, **value})
            results[str(path.resolve())] = sha(path)
        index, case_files = export_cases(protocol, evaluated, public, cache, metadata)
        results.update(case_files)
        check_hashes(code_hashes)
        check_hashes(accessed)
        scope_counts = {scope: {'records': len(evaluated['scopes'][scope]['ids']),
                                'groups': len({r['task_group'] for r in public[scope].values()})}
                        for scope in SCOPES}
        demand([scope_counts[s]['records'] for s in SCOPES] == [363, 170, 155, 1467, 731]
               and scope_counts['AF']['groups'] == 716, 'Full original diagnostic scope changed')
        history[-1].update(status='COMPLETE', completed_utc=now(), case_groups=index['selected_count'],
                           existing_prediction_file_read_events=cache.read_events,
                           existing_prediction_rows_parsed=cache.rows_parsed)
        receipt = checkpoint_state('CACHE_DIAGNOSTICS_COMPLETE', status='PASS', current_pid=None,
            input_hashes=inputs, code_sha256=code_hashes, old_and_current_accessed_files_sha256=accessed,
            results_sha256=results, scopes=scope_counts, case_groups=index['selected_count'],
            existing_prediction_file_read_events=cache.read_events,
            existing_prediction_rows_parsed=cache.rows_parsed, new_compute=ZERO_NEW_COMPUTE,
            evaluation_gold_ordinals_reused=sum(len(evaluated['scopes'][s]['ids']) for s in SCOPES),
            run_history=history, elapsed_seconds=time.monotonic() - started,
            static_validation='AST/schema only; no extra model/control tests', root_cause_interpretation=None)
        print(canonical({'Exp156': 'CACHE_DIAGNOSTICS_COMPLETE', 'scopes': scope_counts,
                         'case_groups': index['selected_count'], 'result_files': len(results),
                         'new_compute': ZERO_NEW_COMPUTE}), flush=True)
        return receipt
    except Exception:
        history[-1].update(status='FAIL', failed_utc=now(), traceback=traceback.format_exc())
        checkpoint_state('CACHE_DIAGNOSTICS_FAILED', status='FAIL', current_pid=None,
                         input_hashes=inputs, code_sha256=code_hashes, run_history=history,
                         old_and_current_accessed_files_sha256=accessed, new_compute=ZERO_NEW_COMPUTE,
                         elapsed_seconds=time.monotonic() - started)
        raise


if __name__ == '__main__':
    run()

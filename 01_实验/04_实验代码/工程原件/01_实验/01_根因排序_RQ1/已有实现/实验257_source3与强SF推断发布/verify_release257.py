"""Read-only numerical and provenance audit of completed Exp257 outputs.

No model construction/forward, training, task outcome, Gold or native calls.
Writes only a new independent audit and a consumer selection handoff.
"""
import datetime
import hashlib
import json
import math
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')
E = Path(__file__).resolve().parent
ROOT = Path('D:/Code/毕设/graduate-thesis-experiments')


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(name, value):
    path = E / name
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', 'utf-8')


def main():
    release = read(E / 'RQ1_SOURCE3_RELEASE.json')
    audit = read(E / 'RANKING_INTERVENTION_OPPORTUNITIES.json')
    protocol = read(E / 'PROTOCOL257.json')
    assert release['status'] == 'COMPLETE_REAL_INFERENCE_RELEASE'
    assert release['real_ranker_loads'] == 21 and release['real_forward_batches'] == 42
    assert release['task_order'] == protocol['qualified18_order'] == audit['task_order']
    assert release['protocol_sha256'] == sha(E / 'PROTOCOL257.json')
    assert release['intervention_audit_sha256'] == sha(E / 'RANKING_INTERVENTION_OPPORTUNITIES.json')
    checked_hashes = 0
    for path, expected in release['source_SHA256'].items():
        assert sha(path) == expected, ('SOURCE_OR_PUBLIC_INPUT_SHA_DRIFT', path)
        checked_hashes += 1
    inventory = read(ROOT / '工作区/1012-post-review-execution/READONLY_ASSET_LOCATIONS_ROOT.json')
    inventory_raw_hashes = {}
    for row in inventory['raw_feature_candidates']:
        path, expected = row['tensor']['path'], row['tensor']['sha256']
        assert sha(path) == expected, path
        assert release['source_SHA256'][path] == expected
        inventory_raw_hashes[path] = expected
    permodel_tasks = 0
    for key, predictions in release['model_outputs'].items():
        assert set(predictions) == set(release['task_order'])
        for tid, p in predictions.items():
            probability = p['probabilities']
            n = len(probability)
            assert sorted(p['order']) == list(range(n))
            assert p['order'] == sorted(range(n), key=lambda i: (-probability[i], i))
            assert p['chosen_step'] == p['order'][0]
            assert all(math.isfinite(x) and x >= 0 for x in probability)
            assert abs(math.fsum(probability) - 1) < 1e-5
            logits = p['logits']
            exp = [math.exp(x - max(logits)) for x in logits]
            expected = [x / math.fsum(exp) for x in exp]
            assert max(abs(a - b) for a, b in zip(expected, probability)) < 1e-6
            permodel_tasks += 1
    ensemble_max_error = 0
    for method, predictions in release['ensembles'].items():
        for tid, p in predictions.items():
            model_probabilities = [v[tid]['probabilities'] for key, v in release['model_outputs'].items() if key.startswith(method + '/')]
            expected = [math.fsum(values) / len(model_probabilities) for values in zip(*model_probabilities)]
            error = max(abs(a - b) for a, b in zip(expected, p['probabilities']))
            ensemble_max_error = max(ensemble_max_error, error)
            assert error < 1e-12
            assert p['order'] == sorted(range(len(expected)), key=lambda i: (-expected[i], i))
    p224 = ROOT / '工作区/1008-2320-exp224-flash-common/实验/实验224_二十三题Flash完整共同恢复比较'
    refs = {r['task_id']: r for r in read(p224 / 'data/selected_task_bindings.json')['tasks']}
    historical_AF = []
    for tid in release['task_order']:
        path = Path(refs[tid].get('G_frozen_plan') or p224 / 'ranking/plans' / tid / 'OURS_G153_VBR.json')
        old = read(path)
        old_prob = old['probabilities']
        new = release['ensembles']['AF15'][tid]
        error = max(abs(a - b) for a, b in zip(old_prob, new['probabilities']))
        assert error < 1e-5, ('AF15_INTERFACE_NUMERIC_DRIFT', tid, error)
        historical_AF.append({'task_id': tid, 'public_prediction_path': str(path), 'public_prediction_sha256': sha(path), 'max_probability_error': error,
                              'full_order_equal': old['complete_original_ordinal_order'] == new['order'], 'comparison_only_public_saved_prediction': True})
    eligible = []
    for tid in release['task_order']:
        row = audit['rows'][tid]
        mapping = {m['step']: m for m in refs[tid]['mapping']}
        candidate_ids = {v['call_id'] for v in row['legal_changed_edit_bindings']}
        assert row['candidate_count'] == len(candidate_ids)
        for method, order in row['complete_original_ordinal_orders'].items():
            assert sorted(order) == list(range(len(mapping)))
            selected, seen = [], set()
            for ordinal in order:
                for call_id in mapping[ordinal]['successful_edit_ids']:
                    if call_id not in seen and call_id in candidate_ids:
                        selected.append(call_id)
                    seen.add(call_id)
            assert selected == [v['call_id'] for v in row['all_legal_edit_orders'][method]]
            assert row['progressive_prefix_call_ids'][method] == [selected[:i] for i in (1, 2, 3)]
        if row['candidate_count'] >= 2 and row['progressive_prefix_call_ids']['SOURCE3'][2] != row['progressive_prefix_call_ids']['SF_ALG50'][2]:
            eligible.append(tid)
    assert eligible == audit['eligible_in_original_order'] and eligible[:2] == release['selected_first_two']
    result = {'schema': 'EXP257-independent-readonly-release-verification/1', 'at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': 'PASS',
              'release_sha256': sha(E / 'RQ1_SOURCE3_RELEASE.json'), 'release_source_and_input_hashes_checked': checked_hashes, 'exact_raw_tensor_inventory_hashes': inventory_raw_hashes,
              'permodel_complete_probability_and_logits_rows_checked': permodel_tasks, 'float64_ensemble_max_probability_error': ensemble_max_error,
              'AF15_saved_public_prediction_interface_checks': historical_AF, 'AF15_max_probability_error': max(r['max_probability_error'] for r in historical_AF),
              'AF15_saved_full_order_equal_count': sum(r['full_order_equal'] for r in historical_AF), 'legal_call_ID_mapping_and_MAX3_checked_all_methods_tasks': 90,
              'selected_first_two': eligible[:2], 'new_model_forward_POST_native_training_Gold': 0}
    save('INDEPENDENT_RELEASE_VERIFICATION257.json', result)
    handoff = {'schema': 'EXP257-parent-control-selected-tasks-handoff/1', 'at_utc': result['at_utc'], 'status': 'READY_REAL_SORTING',
               'release_path': str(E / 'RQ1_SOURCE3_RELEASE.json'), 'release_sha256': result['release_sha256'], 'protocol_sha256': release['protocol_sha256'],
               'independent_verification_path': str(E / 'INDEPENDENT_RELEASE_VERIFICATION257.json'), 'independent_verification_sha256': sha(E / 'INDEPENDENT_RELEASE_VERIFICATION257.json'),
               'selected_first_two': []}
    for tid in eligible[:2]:
        row = audit['rows'][tid]
        plans = {}
        for method in ('SOURCE3', 'SF_ALG50', 'AF15'):
            path = E / 'ranking/plans' / tid / (method + '.json')
            plans[method] = {'path': str(path), 'sha256': sha(path), 'first_three_call_IDs': row['progressive_prefix_call_ids'][method][2]}
        handoff['selected_first_two'].append({'task_id': tid, 'original_plan_slot': row['original_plan_slot'], 'legal_candidate_count': row['candidate_count'], 'plans': plans,
                                             'current_C0_qualification': protocol['qualification'][tid], 'selection_uses_no_outcomes_or_Gold': True})
    save('SELECTION_READY257.json', handoff)
    print(json.dumps({k: result[k] for k in ('status', 'release_source_and_input_hashes_checked', 'permodel_complete_probability_and_logits_rows_checked', 'float64_ensemble_max_probability_error', 'AF15_max_probability_error', 'AF15_saved_full_order_equal_count', 'selected_first_two')}, ensure_ascii=False))


if __name__ == '__main__':
    main()

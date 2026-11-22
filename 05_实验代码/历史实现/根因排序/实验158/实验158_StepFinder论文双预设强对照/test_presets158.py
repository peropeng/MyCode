"""Four necessary CPU/artificial-only paper-preset checks; no neural forward/training."""
import ast
import importlib
import io
import math
import platform
import sys
import time
import traceback
import unittest
from unittest import mock

from common import *
import torch
import models158 as models
import data158 as data

P = PLAN = SELECTOR = None
ALG, HC = ARMS
COUNTERS = {'fixture_runs': 1, 'CPU_model_constructor_calls': 0,
            'synthetic_state_loads': 0, 'artificial_source_loss_calls': 0,
            'artificial_AF_group_loss_calls': 0, 'total_artificial_loss_calls': 0,
            'plain_artificial_stub_instances': 0, 'plain_artificial_stub_calls': 0,
            'artificial_validation_selection_calls': 0,
            'static_derived_accounting_checks': 0, 'neural_forwards': 0,
            'GPU_forwards': 0, 'backward_calls': 0, 'optimizer_constructions': 0,
            'optimizer_updates': 0, 'checkpoint_load_attempts': 0,
            'real_weight_loads': 0, 'real_Gold_values': 0, 'old_score_values': 0,
            'actual_RNG_capture_restore_calls': 0, 'new_encoder_API_downloads': 0}
DETAILS = []
EXPECTED_PROFILES = {
    'SF_ALG_PAPER50': {'parameters': 277633, 'lr': .001, 'alpha': .1, 'beta': .9,
                       'gamma': .4, 'lambda_temporal': .9, 'scales': [1, 2],
                       'max_epochs': 50, 'patience': 10},
    'SF_HC_PAPER50': {'parameters': 277633, 'lr': .00001, 'alpha': .3, 'beta': .1,
                      'gamma': .75, 'lambda_temporal': .02, 'scales': [1, 2],
                      'max_epochs': 50, 'patience': 10},
}


def forbidden(counter):
    def reject(*args, **kwargs):
        COUNTERS[counter] += 1
        raise RuntimeError('Necessary Exp158 fixtures prohibit ' + counter)
    return reject


def real_attributes(model):
    return {'parameters': sum(p.numel() for p in model.parameters()),
            'alpha': model.asi.alpha, 'beta': model.scoring.beta,
            'gamma': model.scoring.gamma, 'scales': list(model.scoring.scales)}


class PlainScoringStub:
    def __call__(self, h, mask):
        COUNTERS['plain_artificial_stub_calls'] += 1
        return torch.zeros(2, 3), torch.tensor(0.)

    def temporal_head(self, previous):
        COUNTERS['plain_artificial_stub_calls'] += 1
        return torch.ones_like(previous)


class PlainSFStub:
    """Precomputed CPU tensors, with no nn.Module or learned model invocation."""
    def __init__(self):
        COUNTERS['plain_artificial_stub_instances'] += 1
        self.scoring = PlainScoringStub()

    def tfe(self, content, mask):
        COUNTERS['plain_artificial_stub_calls'] += 1
        return torch.zeros(2, 3, 1)

    def asi(self, h, agent, mask):
        COUNTERS['plain_artificial_stub_calls'] += 1
        return h


class PresetBehavior(unittest.TestCase):
    def test_01_explicit_complete_profiles_and_load_state_preserves_nonlearned_config(self):
        self.assertEqual(PROFILES, EXPECTED_PROFILES)
        self.assertEqual(PLAN['new_baseline_arms'], EXPECTED_PROFILES)
        self.assertEqual(P['profiles'], EXPECTED_PROFILES)
        trainer_ast = ast.parse((E / 'trainer158.py').read_text('utf-8-sig'))
        profile_keys = {node.slice.value for node in ast.walk(trainer_ast)
                        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant)
                        and isinstance(node.value, ast.Subscript) and isinstance(node.value.value, ast.Name)
                        and node.value.value.id == 'PROFILES'}
        self.assertTrue({'lr', 'max_epochs', 'patience'} <= profile_keys,
                        'Trainer must apply each complete preset training configuration')
        initialized = {}
        for arm in ARMS:
            COUNTERS['CPU_model_constructor_calls'] += 1
            with torch.device('cpu'):
                model = models.create(arm)
            expected = {k: EXPECTED_PROFILES[arm][k] for k in ('parameters', 'alpha', 'beta', 'gamma', 'scales')}
            self.assertEqual(real_attributes(model), expected)
            self.assertTrue(all(p.device.type == 'cpu' for p in model.parameters()))
            initialized[arm] = model
        synthetic_state = {k: torch.zeros_like(value) for k, value in initialized[ALG].state_dict().items()}
        states = {}
        for arm, model in initialized.items():
            COUNTERS['synthetic_state_loads'] += 1
            model.load_state_dict(synthetic_state)
            actual = real_attributes(model)
            self.assertEqual(actual, {k: EXPECTED_PROFILES[arm][k] for k in actual})
            self.assertEqual(models.require_model_configuration(model, arm), actual)
            self.assertTrue(all(torch.equal(v, synthetic_state[k]) for k, v in model.state_dict().items()))
            states[arm] = models.state_digest(model.state_dict())
            DETAILS.append({'kind': 'CPU_synthetic_state_preset', 'arm': arm,
                            'actual_nonlearned_model_attributes_after_load': actual,
                            'complete_training_profile': PROFILES[arm],
                            'synthetic_learned_state_digest': states[arm],
                            'no_original_or_trained_weight_loaded': True})
        self.assertEqual(states[ALG], states[HC])

    def test_02_source_and_AF_group_losses_really_use_each_preset_lambda(self):
        ids = ['artificial-a', 'artificial-b']
        batch = {'ids': ids, 'mask': torch.ones(2, 3, dtype=torch.bool),
                 'content': torch.zeros(2, 3, 128), 'agent': torch.zeros(2, 3, 32),
                 'lengths': torch.tensor([3, 3])}
        labels = {'artificial-a': 0, 'artificial-b': 1}
        by = {s: {'task_group': 'artificial-only-group'} for s in ids}
        logits = torch.zeros(2, 3)
        scores = [logits[0], logits[1]]
        temporal = torch.tensor(2.)
        outputs = {}
        for arm in ARMS:
            coefficient = EXPECTED_PROFILES[arm]['lambda_temporal']
            COUNTERS['artificial_source_loss_calls'] += 1
            COUNTERS['total_artificial_loss_calls'] += 1
            source = models.loss(scores, (logits, temporal), arm, batch, labels)
            self.assertFalse(source.requires_grad)
            self.assertAlmostEqual(float(source), math.log(3) + coefficient * 2, places=6)
            COUNTERS['artificial_AF_group_loss_calls'] += 1
            COUNTERS['total_artificial_loss_calls'] += 1
            af = data.grouped_loss(PlainSFStub(), arm, batch, labels, by)
            self.assertFalse(af.requires_grad)
            self.assertAlmostEqual(float(af), math.log(3) + coefficient * (2 / (2 + 1e-6)), places=6)
            outputs[arm] = {'source_loss': float(source), 'AF_group_loss': float(af), 'lambda': coefficient}
        self.assertGreater(outputs[ALG]['source_loss'], outputs[HC]['source_loss'])
        self.assertGreater(outputs[ALG]['AF_group_loss'], outputs[HC]['AF_group_loss'])
        DETAILS.append({'kind': 'four_artificial_loss_calls', 'results': outputs,
                        'source_temporal_scalar': 2., 'AF_plain_stub_temporal_scalar': 2 / (2 + 1e-6),
                        'CE_expected': math.log(3), 'neural_module_calls': 0,
                        'real_labels_weights_scores': 0, 'backward_optimizer': 0})

    def test_03_validation_Top1_then_MRR_then_fixed_ALG_tie(self):
        examples = [
            ({ALG: {'Top1': .6, 'MRR': .9}, HC: {'Top1': .7, 'MRR': .2}}, HC),
            ({ALG: {'Top1': .5, 'MRR': .4}, HC: {'Top1': .5, 'MRR': .6}}, HC),
            ({ALG: {'Top1': .5, 'MRR': .7}, HC: {'Top1': .5, 'MRR': .7}}, ALG),
            ({ALG: {'Top1': .8, 'MRR': .1}, HC: {'Top1': .7, 'MRR': .9}}, ALG),
        ]
        for metrics, expected in examples:
            COUNTERS['artificial_validation_selection_calls'] += 1
            actual = SELECTOR.choose_preset(metrics)
            self.assertEqual(actual, expected)
        DETAILS.append({'kind': 'four_artificial_validation_decisions',
                        'Top1_before_MRR': True, 'full_tie_ALG': True,
                        'target_Gold_or_score_access': 0})

    def test_04_derived_alias_and_ensemble_views_do_not_add_fits_or_neural_outputs(self):
        resources = PLAN['resources']
        source, af = 2155, 731
        scoring = 2 * 3 * (source + af)
        ensembles = 2 * (source + af)
        derived = (3 + 1) * (source + af)
        self.assertEqual((scoring, ensembles, scoring + ensembles, derived), (17316, 5772, 23088, 11544))
        for name, expected in (('new_valid_optimization_stages', 66), ('new_final_fitted_models', 36),
                               ('unique_parent_INITIAL_references', 18), ('new_model_scoring_record_outputs', scoring),
                               ('new_three_seed_ensemble_outputs', ensembles), ('new_ranker_outputs', scoring + ensembles),
                               ('derived_selection_view_records', derived)):
            self.assertEqual(resources[name], expected)
        self.assertEqual(P['expected_optimization_stages'], 66)
        self.assertEqual(P['expected_final_models'], 36)
        self.assertEqual(P['expected_outputs'], 23088)
        self.assertEqual(P['expected_derived_selection_view_records'], 11544)
        self.assertEqual(P['new_model_scoring_record_outputs'], 17316)
        self.assertEqual(P['new_three_seed_ensemble_outputs'], 5772)
        self.assertEqual(P['frozen_primary_forward_or_fit_new'], 0)
        selector_ast = ast.parse((E / 'select158.py').read_text('utf-8-sig'))
        forbidden_names = {'forward', 'backward', 'fit', 'train', 'load_model', 'initial_model', 'create', 'predict'}
        for node in ast.walk(selector_ast):
            if isinstance(node, ast.Call):
                name = node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id if isinstance(node.func, ast.Name) else None
                self.assertNotIn(name, forbidden_names, 'Selection/view construction cannot score or fit a neural model')
        predictor_ast = ast.parse((E / 'predict158.py').read_text('utf-8-sig'))
        helpers = {node.name: node for node in predictor_ast.body if isinstance(node, ast.FunctionDef)}
        self.assertTrue({'derive_selected', 'ensemble', 'add_roles'} <= set(helpers))
        for helper in ('derive_selected', 'ensemble', 'add_roles'):
            for node in ast.walk(helpers[helper]):
                if isinstance(node, ast.Call):
                    name = node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id if isinstance(node.func, ast.Name) else None
                    self.assertNotIn(name, forbidden_names, 'Derived views use only existing JSON/probabilities')
        zero_markers = []
        for node in ast.walk(helpers['derive_selected']):
            if isinstance(node, ast.Dict):
                for key, value in zip(node.keys, node.values):
                    if isinstance(key, ast.Constant) and key.value in ('new_neural_forward', 'new_optimization_training'):
                        self.assertIsInstance(value, ast.Constant)
                        self.assertEqual(value.value, 0)
                        zero_markers.append(key.value)
        self.assertTrue({'new_neural_forward', 'new_optimization_training'} <= set(zero_markers))
        COUNTERS['static_derived_accounting_checks'] += 1
        DETAILS.append({'kind': 'derived_accounting_static', 'new_valid_optimization_stages': 66,
                        'new_final_models': 36, 'actual_model_scoring_record_outputs': 17316,
                        'new_three_seed_ensemble_outputs': 5772, 'new_ranker_outputs': 23088,
                        'derived_selection_view_records': 11544, 'derived_extra_neural_forwards_or_fits': 0,
                        'derived_not_added_to_new_model_scoring_count': True,
                        'derive_selected_ensemble_add_roles_AST_no_neural_or_fit_calls': True})


def source_hashes():
    names = ('common.py', 'context_base.py', 'models158.py', 'data158.py', 'trainer158.py',
             'predict158.py', 'select158.py', 'test_presets158.py')
    result = {name: sha(E / name) for name in names}
    result.update({str(path.relative_to(E)).replace('\\', '/'): sha(path) for path in sorted((E / 'sources').glob('*.py'))})
    return result


def main():
    global P, PLAN, SELECTOR
    require_time(new_test=True)
    started = time.monotonic()
    receipt_path = E / 'fixtures/preset_test_receipt.json'
    prior_runs = []
    if receipt_path.exists():
        previous_bytes = receipt_path.read_bytes()
        previous = read(receipt_path)
        name = 'preset_prior_receipt_' + hashlib.sha256(previous_bytes).hexdigest()[:16] + '.json'
        saved = receipt_path.parent / name
        if not saved.exists():
            saved.write_bytes(previous_bytes)
        prior_runs = list(previous.get('prior_runs', []))
        prior_runs.append({'receipt_file': name, 'status': previous['status'], 'tests_run': previous['tests_run'],
                           'compute_counters': previous['compute_counters']})
    log, result, setup_error = io.StringIO(), None, None
    hashes = {}
    protocol_hash = None
    try:
        PLAN = read(E / 'approved_plan.json')
        if sha(E / 'approved_plan.json') != PLAN_SHA:
            raise RuntimeError('Frozen Exp158 plan changed')
        protocol_hash = sha(E / 'protocol.json')
        P = read(E / 'protocol.json')
        if P['approved_plan_sha256'] != PLAN_SHA:
            raise RuntimeError('Frozen158 protocol not bound to approved plan')
        hashes = source_hashes()
        for name in hashes:
            ast.parse((E / name).read_text('utf-8-sig'), filename=name)
        SELECTOR = importlib.import_module('select158')
        with mock.patch.object(torch, 'load', forbidden('checkpoint_load_attempts')), \
             mock.patch.object(torch.nn.Module, '_call_impl', forbidden('neural_forwards')), \
             mock.patch.object(torch.autograd, 'backward', forbidden('backward_calls')), \
             mock.patch.object(torch.Tensor, 'backward', forbidden('backward_calls')), \
             mock.patch.object(torch.optim.Optimizer, '__init__', forbidden('optimizer_constructions')):
            result = unittest.TextTestRunner(stream=log, verbosity=2).run(
                unittest.defaultTestLoader.loadTestsFromTestCase(PresetBehavior))
        if source_hashes() != hashes or sha(E / 'protocol.json') != protocol_hash:
            raise RuntimeError('Checked code/protocol changed during necessary fixture')
    except Exception:
        setup_error = traceback.format_exc()
    cumulative = {k: v + sum(r['compute_counters'].get(k, 0) for r in prior_runs) for k, v in COUNTERS.items()}
    passed = setup_error is None and result is not None and result.wasSuccessful()
    receipt = {'experiment': 'Exp158', 'status': 'PASS' if passed else 'FAIL',
               'approved_plan_sha256': PLAN_SHA, 'protocol_sha256': protocol_hash,
               'kind': 'four_necessary_CPU_synthetic_preset_fixtures_without_neural_forward',
               'at_utc': now(), 'tests_run': 0 if result is None else result.testsRun,
               'compute_counters': COUNTERS, 'physical_cumulative_compute_counters': cumulative,
               'prior_runs': prior_runs, 'source_sha256': hashes, 'details': DETAILS,
               'two_CPU_constructors_and_four_artificial_loss_calls_only': True,
               'no_real_weights_Gold_old_scores_or_GPU_forward': True,
               'root_checked18_original_INITIAL_digests_and_each_stage_checks_actual_RNG': True,
               'old_splits_masks_group_scaler_GPU_checks_not_rebuilt': True,
               'Python': {'version': platform.python_version(), 'executable': sys.executable},
               'torch_version': torch.__version__, 'seconds': time.monotonic() - started,
               'test_log': log.getvalue(), 'setup_error': setup_error,
               'failures': [] if result is None else [{'test': str(t), 'traceback': s} for t, s in result.failures],
               'errors': [] if result is None else [{'test': str(t), 'traceback': s} for t, s in result.errors]}
    atomic(receipt_path, receipt)
    print(log.getvalue(), end='')
    print(canonical({'Exp158': 'necessary_fixture', 'status': receipt['status'], 'tests': receipt['tests_run'],
                     'counts': COUNTERS, 'receipt': str(receipt_path)}), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())

"""Necessary CPU behavior fixtures for the frozen context readout operator.

Only artificial tensors and newly initialized parameters are used. No backward,
optimizer, real batch, embedding, result, or Gold asset is opened.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import math
import platform
import sys
import time
import unittest
from pathlib import Path
from unittest import mock
import copy

sys.dont_write_bytecode = True
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import torch
import fixture_context153 as fx

HERE = Path(__file__).resolve().parent
PLAN_SHA = "0521e7ed973b083872808139fa54f9b313b290d9204bcb0c3db71bdb28de3713"
ARMS = ["AB_GLOBAL", "AB_LOCAL", "AB_STATIC", "AB_VALUE_PERM"]
ARTIFICIAL_SEED = 50391


class ContextBehavior(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cm = importlib.import_module("context_models")
        original_context = cls.cm.ContextRanker.context_readout
        def counted_context(model, *args, **kwargs):
            fx.COUNTERS["context_readout_calls"] += 1
            with torch.no_grad():
                return original_context(model, *args, **kwargs)
        cls.context_patch = mock.patch.object(cls.cm.ContextRanker, "context_readout", counted_context)
        cls.context_patch.start()
        cls.addClassCleanup(cls.context_patch.stop)
        cls.models, cls.rngs, cls.audits = {}, {}, {}
        for arm in ["AB_REF", *ARMS, "SF_REF"]:
            model, rng, audit = fx.initialized(cls.cm, arm, ARTIFICIAL_SEED)
            cls.models[arm], cls.rngs[arm], cls.audits[arm] = model, rng, audit
        cls.batch, cls.entries, cls.scaler, cls.labels = fx.collate(cls.cm)

    def assert_scores(self, first, second, exact=True):
        self.assertEqual(len(first), len(second))
        for a, b in zip(first, second):
            torch.testing.assert_close(a, b, rtol=0 if exact else 1e-6, atol=0 if exact else 1e-6)

    def assert_rng_equal(self, a, b):
        self.assertEqual(a["python"], b["python"])
        self.assertEqual(a["numpy"][0], b["numpy"][0])
        self.assertTrue((a["numpy"][1] == b["numpy"][1]).all())
        self.assertEqual(a["numpy"][2:], b["numpy"][2:])
        self.assertTrue(torch.equal(a["torch"], b["torch"]))
        self.assertEqual(len(a["cuda"]), len(b["cuda"]))
        self.assertTrue(all(torch.equal(x, y) for x, y in zip(a["cuda"], b["cuda"])))

    def test_01_flat_collate_preserves_task_coordinate_and_has_no_attention_padding(self):
        batch = self.batch
        self.assertIs(self.cm.collate, self.cm.original.collate)
        self.assertEqual(batch["ids"], ["artificial.alpha", "artificial.beta"])
        self.assertEqual(batch["lengths"].tolist(), [5, 3])
        self.assertEqual(tuple(batch["x"].shape), (8, 183))
        self.assertEqual(batch["task_index"].tolist(), [0, 0, 0, 0, 0, 1, 1, 1])
        self.assertEqual(tuple(batch["content"].shape), (2, 5, 128))
        self.assertEqual(batch["mask"].tolist(), [[True] * 5, [True, True, True, False, False]])
        self.assertTrue(torch.equal(batch["content"][1, :3], self.entries["artificial.beta"]["content"]))
        self.assertTrue(torch.equal(batch["agent"][1, :3], self.entries["artificial.beta"]["agent"]))
        self.assertTrue(torch.equal(batch["content"][1, 3:], torch.zeros(2, 128)))
        for arm in ARMS:
            allowed = fx.mask(self.cm, batch["task_index"], batch["adjacency"], arm)
            self.assertEqual(tuple(allowed.shape), (8, 8))
            self.assertFalse(allowed[:5, 5:].any())
            self.assertFalse(allowed[5:, :5].any())
            self.assertTrue(allowed.diagonal().all())

    def test_02_local_mask_matches_exact_four_relation_receiving_zero_one_two_hops(self):
        task_index, adjacency, expected = fx.directed_mask_fixture()
        actual = fx.mask(self.cm, task_index, adjacency, "AB_LOCAL")
        self.assertTrue(torch.equal(actual, expected), (actual, expected))
        self.assertFalse(actual[0, 1], "A sender must not see its receiver through a reversed edge")
        self.assertFalse(actual[4, 1], "Three receiving hops must remain masked")
        for arm in ["AB_GLOBAL", "AB_STATIC", "AB_VALUE_PERM"]:
            self.assertTrue(torch.equal(fx.mask(self.cm, task_index, adjacency, arm), task_index[:, None] == task_index[None, :]))

    def test_03_nonzero_readout_cannot_see_other_task_representations(self):
        h = fx.representation()
        changed = h.clone()
        changed[5:] += 37
        for arm in ARMS:
            with self.subTest(arm=arm):
                model = fx.identity_readout(fx.clone(self.models[arm]))
                a = model.context_readout(h, self.batch["adjacency"], self.batch["task_index"], self.batch["lengths"], self.batch["ids"])
                b = model.context_readout(changed, self.batch["adjacency"], self.batch["task_index"], self.batch["lengths"], self.batch["ids"])
                self.assertTrue(torch.equal(a[:5], b[:5]))
                self.assertFalse(torch.equal(a[5:], b[5:]))

    def test_04_static_unified_mean_query_context_and_declared_residual_formula(self):
        h = fx.representation()
        for arm in ["AB_GLOBAL", "AB_STATIC"]:
            with self.subTest(arm=arm):
                model = fx.identity_readout(fx.clone(self.models[arm]), o_scale=2)
                query_inputs = []
                hook = model.Q.register_forward_pre_hook(lambda module, args: query_inputs.append(args[0].detach().clone()))
                context = model.context_readout(h, self.batch["adjacency"], self.batch["task_index"], self.batch["lengths"], self.batch["ids"])
                hook.remove()
                expected = fx.independent_expected_context(h, [5, 3], static=arm == "AB_STATIC", o_scale=2)
                torch.testing.assert_close(context, expected, rtol=1e-6, atol=1e-6)
                if arm == "AB_STATIC":
                    self.assertEqual(tuple(query_inputs[0].shape), (2, 96))
                    self.assertTrue(torch.equal(query_inputs[0], torch.stack([h[:5].mean(0), h[5:].mean(0)])))
                    first_task = context[0:1].expand(5, -1)
                    second_task = context[5:6].expand(3, -1)
                    fx.NUMERIC_DETAILS.append({"kind": "float32_STATIC_shared_context", "query_exactly_equals_task_mean": True,
                                               "max_abs_task0_difference": (context[:5] - first_task).abs().max().item(),
                                               "max_abs_task1_difference": (context[5:] - second_task).abs().max().item(),
                                               "shared_context_rtol": 1e-6, "shared_context_atol": 1e-6})
                    torch.testing.assert_close(context[:5], first_task, rtol=1e-6, atol=1e-6)
                    torch.testing.assert_close(context[5:], second_task, rtol=1e-6, atol=1e-6)
                else:
                    self.assertTrue(torch.equal(query_inputs[0], h))
                    self.assertFalse(torch.equal(context[0], context[1]))

    def test_05_value_permutation_fixed_hash_derangement_and_unchanged_key_coordinate(self):
        for sid in ["artificial.alpha", "arbitrary-renamed-record"]:
            for n in [1, 2, 3, 8]:
                with self.subTest(sid=sid, n=n):
                    result = fx.permutation(self.cm, sid, n)
                    expected_hash = hashlib.sha256(("Exp153-value-perm-v1|" + sid).encode()).digest()
                    shift = 0 if n == 1 else 1 + int.from_bytes(expected_hash, "big") % (n - 1)
                    self.assertTrue(torch.equal(result, (torch.arange(n) + shift) % n))
                    self.assertEqual(sorted(result.tolist()), list(range(n)))
                    self.assertTrue(torch.equal(result, fx.permutation(self.cm, sid, n)))
                    self.assertTrue((result == torch.arange(n)).all() if n == 1 else (result != torch.arange(n)).all())
        h = fx.representation()
        snapshot = h.clone()
        model = fx.identity_readout(fx.clone(self.models["AB_VALUE_PERM"]), o_scale=2)
        key_inputs = []
        hook = model.K.register_forward_pre_hook(lambda module, args: key_inputs.append(args[0].detach().clone()))
        context = model.context_readout(h, self.batch["adjacency"], self.batch["task_index"], self.batch["lengths"], self.batch["ids"])
        hook.remove()
        self.assertTrue(torch.equal(key_inputs[0], snapshot))
        self.assertTrue(torch.equal(h, snapshot))
        expected = fx.independent_expected_context(h, [5, 3], permuted=True, sample_ids=self.batch["ids"], o_scale=2)
        torch.testing.assert_close(context, expected, rtol=1e-6, atol=1e-6)
        self.assertIs(self.cm.variant_features("AB_VALUE_PERM", self.entries), self.entries)
        self.assertEqual(self.batch["ids"], list(self.labels))

    def test_06_equal_parameters_canonical_base_qkvo_and_restored_training_rng(self):
        reference = self.models["AB_REF"].state_dict()
        self.assertEqual(sum(p.numel() for p in self.models["AB_REF"].parameters()), 300593)
        first = self.models[ARMS[0]].state_dict()
        for arm in ARMS:
            with self.subTest(arm=arm):
                model, state = self.models[arm], self.models[arm].state_dict()
                self.assertEqual(sum(p.numel() for p in model.parameters()), 337457)
                self.assertEqual(set(state) - set(reference), {"Q.weight", "K.weight", "V.weight", "O.weight"})
                for key in reference:
                    self.assertTrue(torch.equal(reference[key], state[key]), (arm, key))
                for key in state:
                    self.assertTrue(torch.equal(first[key], state[key]), (arm, key))
                self.assertTrue(torch.equal(model.O.weight, torch.zeros(96, 96)))
                for name in ["Q", "K", "V", "O"]:
                    self.assertIsNone(getattr(model, name).bias)
                self.assert_rng_equal(self.rngs["AB_REF"], self.rngs[arm])
                self.assertEqual(self.audits[arm]["base_state_digest"], self.audits["AB_REF"]["state_digest"])
                self.assertEqual(self.audits[arm]["independent_context_seed"], ARTIFICIAL_SEED + 153000)

    def test_07_zero_o_eval_and_equal_rng_train_mode_match_original_ab(self):
        for training in [False, True]:
            with self.subTest(training=training):
                reference = self.models["AB_REF"]
                reference.train(training)
                self.cm.restore_rng(self.rngs["AB_REF"])
                scores, extra = fx.forward(self.cm, reference, "AB_REF", self.batch, original=True)
                baseline_loss = fx.loss(self.cm, scores, extra, "AB_REF", self.batch, self.labels, original=True)
                for arm in ARMS:
                    model = self.models[arm]
                    model.train(training)
                    self.cm.restore_rng(self.rngs[arm])
                    candidate, candidate_extra = fx.forward(self.cm, model, arm, self.batch)
                    self.assert_scores(scores, candidate)
                    candidate_loss = fx.loss(self.cm, candidate, candidate_extra, arm, self.batch, self.labels)
                    torch.testing.assert_close(candidate_loss, baseline_loss, rtol=0, atol=0)

    def test_08_sf_original_raw_padding_forward_and_loss_path_unchanged(self):
        model = self.models["SF_REF"].eval()
        self.assertEqual(sum(p.numel() for p in model.parameters()), 277633)
        self.assertIsInstance(model, self.cm.original.StepFinder)
        self.assertFalse(any(hasattr(model, name) for name in ["Q", "K", "V", "O"]))
        raw = self.batch["content"].clone()
        scores, extra = fx.forward(self.cm, model, "SF_REF", self.batch)
        original_scores, original_extra = fx.forward(self.cm, model, "SF_REF", self.batch, original=True)
        self.assert_scores(scores, original_scores)
        torch.testing.assert_close(extra[0], original_extra[0], rtol=0, atol=0)
        torch.testing.assert_close(extra[1], original_extra[1], rtol=0, atol=0)
        actual_loss = fx.loss(self.cm, scores, extra, "SF_REF", self.batch, self.labels)
        original_loss = fx.loss(self.cm, original_scores, original_extra, "SF_REF", self.batch, self.labels, original=True)
        torch.testing.assert_close(actual_loss, original_loss, rtol=0, atol=0)
        targets = torch.tensor([self.labels[sid] for sid in self.batch["ids"]])
        expected_loss = torch.nn.functional.cross_entropy(extra[0].masked_fill(~self.batch["mask"], -1e9), targets) + .9 * extra[1]
        torch.testing.assert_close(actual_loss, expected_loss, rtol=0, atol=0)
        padded = dict(self.batch)
        padded["content"], padded["agent"] = self.batch["content"].clone(), self.batch["agent"].clone()
        padded["content"][~padded["mask"]] = 999
        padded["agent"][~padded["mask"]] = -999
        padded_scores, padded_extra = fx.forward(self.cm, model, "SF_REF", padded)
        self.assert_scores(scores, padded_scores)
        torch.testing.assert_close(extra[1], padded_extra[1], rtol=0, atol=0)
        self.assertTrue(torch.equal(self.batch["content"], raw))


class DataBehavior(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_api = importlib.import_module("data153")

    def test_09_scaler_reads_only_fit_nodes_and_constant_std_fallback(self):
        data = self.data_api
        first = torch.cat([torch.full((2, 1), 7.), torch.arange(22).float()[None].repeat(2, 1) + torch.tensor([[0.], [2.]])], dim=1)
        second = torch.cat([torch.full((1, 1), 7.), torch.arange(22).float()[None] - 1], dim=1)
        class ForbiddenOutsideFit:
            def __getitem__(self, key):
                raise AssertionError("Validation/held structures cannot enter fit-only scaler")
        entries = {"artificial.fit0": {"raw_structure": first}, "artificial.fit1": {"raw_structure": second},
                   "artificial.validation": ForbiddenOutsideFit(), "artificial.held": ForbiddenOutsideFit()}
        ids = ["artificial.fit0", "artificial.fit1"]
        fx.COUNTERS["scaler_calls"] += 1
        mean, std = data.scaler_for(entries, ids)
        values = torch.cat([first, second])
        torch.testing.assert_close(mean, values.mean(0), rtol=0, atol=0)
        torch.testing.assert_close(std[1:], values.std(0, unbiased=False)[1:], rtol=0, atol=0)
        self.assertEqual(std[0].item(), 1)
        entries["artificial.validation"] = {"raw_structure": torch.full((3, 23), 1e6)}
        entries["artificial.held"] = {"raw_structure": torch.full((2, 23), -1e6)}
        fx.COUNTERS["scaler_calls"] += 1
        changed = data.scaler_for(entries, ids)
        self.assertTrue(torch.equal(mean, changed[0]))
        self.assertTrue(torch.equal(std, changed[1]))

    def test_10_group_equal_loss_matches_record_means_and_original_sf_objective(self):
        data = self.data_api
        ids = ["artificial.group0.a", "artificial.group0.b", "artificial.group1.a"]
        by = {ids[0]: {"task_group": "group0"}, ids[1]: {"task_group": "group0"}, ids[2]: {"task_group": "group1"}}
        values = [torch.tensor(1.), torch.tensor(3.), torch.tensor(8.)]
        self.assertEqual(data.mean_by_group(values, ids, by).item(), 5)
        self.assertEqual(data.mean_by_group(list(reversed(values)), list(reversed(ids)), by).item(), 5)
        self.assertNotEqual(data.mean_by_group(values, ids, by).item(), torch.stack(values).mean().item())
        batch, sf_stub, logits, h, scores, labels, by = fx.artificial_group_loss()
        targets = torch.tensor([labels[sid] for sid in batch["ids"]])
        ce = torch.nn.functional.cross_entropy(logits.masked_fill(~batch["mask"], -1e9), targets, reduction="none")
        expected_graph = ((ce[0] + ce[1]) / 2 + ce[2]) / 2
        with mock.patch.object(data.models, "forward", return_value=(scores, None)), torch.no_grad():
            fx.COUNTERS["grouped_loss_calls"] += 1
            actual_graph = data.grouped_loss(object(), "AB_GLOBAL", batch, labels, by)
        torch.testing.assert_close(actual_graph, expected_graph, rtol=0, atol=0)
        future = batch["mask"][:, 1:].unsqueeze(-1).float()
        temporal = ((h[:, 1:] * future) ** 2).sum((1, 2)) / (future.sum((1, 2)) + 1e-6)
        per_record_sf = ce + .9 * temporal
        expected_sf = ((per_record_sf[0] + per_record_sf[1]) / 2 + per_record_sf[2]) / 2
        with torch.no_grad():
            fx.COUNTERS["grouped_loss_calls"] += 1
            actual_sf = data.grouped_loss(sf_stub, "SF_REF", batch, labels, by)
        torch.testing.assert_close(actual_sf, expected_sf, rtol=0, atol=0)

    def test_11_complete_oof_and_group_partition_on_artificial_metadata(self):
        data = self.data_api
        public, folds = fx.artificial_af_metadata(data.AF_SEEDS)
        original_public = copy.deepcopy(public)
        fx.COUNTERS["AF_schedule_calls"] += 1
        schedule = data.af_schedule(public, folds)
        self.assertEqual(len(schedule), 90)
        all_ids = {r["sample_id"] for r in public}
        by = {r["sample_id"]: r for r in public}
        for arm in data.ARMS:
            for seed in data.AF_SEEDS:
                rows = [r for r in schedule if r["arm"] == arm and r["seed"] == seed]
                self.assertEqual(len(rows), 5)
                held = [sid for row in rows for sid in row["held_ids"]]
                self.assertEqual(len(held), 731)
                self.assertEqual(set(held), all_ids)
                self.assertEqual(len(set(held)), len(held))
                for row in rows:
                    fit_groups = {by[s]["task_group"] for s in row["selection_fit_ids"]}
                    val_groups = {by[s]["task_group"] for s in row["validation_ids"]}
                    refit_groups = {by[s]["task_group"] for s in row["refit_ids"]}
                    held_groups = {by[s]["task_group"] for s in row["held_ids"]}
                    self.assertFalse(fit_groups & val_groups)
                    self.assertFalse(refit_groups & held_groups)
                    self.assertEqual(fit_groups | val_groups, refit_groups)
                    for name, group_name in [("selection_fit_ids", "inner_fit_groups"), ("validation_ids", "validation_groups"), ("refit_ids", "refit_groups"), ("held_ids", "held_groups")]:
                        self.assertEqual(row[name], [r["sample_id"] for r in public if r["task_group"] in set(row[group_name])])
        self.assertEqual(public, original_public, "Original artificial record coordinates must remain unchanged")
        overlap = copy.deepcopy(folds)
        first_seed = str(data.AF_SEEDS[0])
        overlap[first_seed][0]["validation_groups"].append(overlap[first_seed][0]["inner_fit_groups"][0])
        fx.COUNTERS["AF_schedule_calls"] += 1
        with self.assertRaisesRegex(RuntimeError, "AF nested leakage"):
            data.af_schedule(public, overlap)
        duplicated_outer = copy.deepcopy(folds)
        duplicated_outer[first_seed][4] = copy.deepcopy(duplicated_outer[first_seed][3])
        duplicated_outer[first_seed][4]["outer"] = 4
        fx.COUNTERS["AF_schedule_calls"] += 1
        with self.assertRaisesRegex(RuntimeError, "exactly1 OOF"):
            data.af_schedule(public, duplicated_outer)


class CountedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_counts = {}
    def startTest(self, test):
        name = type(test).__name__
        self.class_counts[name] = self.class_counts.get(name, 0) + 1
        super().startTest(test)


def main():
    started = time.perf_counter()
    target = HERE / "fixtures/context_test_receipt.json"
    prior_runs = []
    if target.is_file():
        previous_raw = target.read_bytes()
        previous = json.loads(previous_raw)
        prior_name = "context_prior_receipt_" + hashlib.sha256(previous_raw).hexdigest()[:16] + ".json"
        prior_path = target.parent / prior_name
        if not prior_path.exists():
            prior_path.write_bytes(previous_raw)
        prior_runs = list(previous.get("prior_runs", []))
        prior_runs.append({"receipt_file": prior_name, "status": previous["status"], "test_cases_run": previous["test_cases_run"],
                           "compute_counters": previous["compute_counters"],
                           "repeat_reason": "New data API fixtures for fit-only/group/OOF" if previous["status"] == "PASS" else "Resolve observed float32 shared-context末位差异; preserve initial bitwise-equality fixture failure, check the fixed formula at rtol/atol1e-6."})
    suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(ContextBehavior), unittest.defaultTestLoader.loadTestsFromTestCase(DataBehavior)])
    result = unittest.TextTestRunner(verbosity=2, resultclass=CountedResult).run(suite)
    source_files = ["common.py", "context_models.py", "test_context153.py", "fixture_context153.py",
                    "sources/original_models.py", "sources/owned_exp130_model.py", "sources/stepfinder_model.py"]
    source_files += ["data153.py", "trainer153.py"]
    receipt = {"experiment": "Exp153", "kind": "artificial_context_behavior_fixtures",
               "approved_plan_sha256": PLAN_SHA, "status": "PASS" if result.wasSuccessful() else "FAIL",
               "test_cases_run": result.testsRun, "compute_counters": dict(fx.COUNTERS),
               "prior_runs": prior_runs, "numeric_details": fx.NUMERIC_DETAILS,
               "artificial_entries": 2, "artificial_candidates": 8, "real_records_or_batches": 0,
               "old_scores_Gold_weights_or_model_results_read": False, "new_encoder_API_downloads": 0,
               "optimizer_or_backward_executed": False, "CUDA_numerical_forward_performed": False,
               "single_candidate_permutation": {"tested": True, "n": 1, "behavior": "identity_degenerate"},
               "data_behavior_tests_run": result.class_counts.get("DataBehavior", 0),
               "artificial_schedule_records": 731, "artificial_schedule_groups": 716,
               "remaining_data_training_checks": "None for this delegated behavior scope; no real optimization or dataset read performed.",
               "Python": {"version": platform.python_version(), "executable": sys.executable}, "torch_version": torch.__version__,
               "source_sha256": {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in source_files},
               "seconds": time.perf_counter() - started,
               "failures": [{"test": str(test), "traceback": trace} for test, trace in result.failures],
               "errors": [{"test": str(test), "traceback": trace} for test, trace in result.errors],
               "skipped": [{"test": str(test), "reason": why} for test, why in result.skipped]}
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    data_failures = [item for item in receipt["failures"] if "DataBehavior" in item["test"]]
    data_errors = [item for item in receipt["errors"] if "DataBehavior" in item["test"]]
    data_receipt = {"experiment": "Exp153", "kind": "artificial_fit_group_OOF_behavior_fixtures",
                    "status": "PASS" if result.class_counts.get("DataBehavior", 0) == 3 and not data_failures and not data_errors else "FAIL",
                    "tests_run": result.class_counts.get("DataBehavior", 0), "approved_plan_sha256": PLAN_SHA,
                    "artificial_metadata_records": 731, "artificial_metadata_groups": 716,
                    "real_records_or_batches": 0, "optimizer_steps": 0, "backward_calls": 0,
                    "source_sha256": receipt["source_sha256"], "failures": data_failures, "errors": data_errors,
                    "context_receipt": str(target), "static_trainer_review": {
                        "status": "NO_OBVIOUS_DEVIATION_IN_READ_CODE", "training_not_executed": True,
                        "fit_only_scaler": "fit() calls scaler_for(data,fit_ids) for source, selection and fresh refit.",
                        "complete_group_batches": "AF batches shuffle sorted complete groups; grouped_loss is record mean then group mean.",
                        "fresh_refit": "selection and refit each load the same frozen initial state/training RNG; refit uses selected epoch and no validation.",
                        "held_prediction_deferred": "run() only validates on val_ids during fitting; all18+90 final models must be sealed before held prediction.",
                        "batch_epoch_budget": "Source492/122, AF90 selection/refit pairs, max40/patience8, AdamW/lr/wd/clip and 198/108 checks match the frozen declarations."}}
    (HERE / "fixtures/data_test_receipt.json").write_text(json.dumps(data_receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())

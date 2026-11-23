"""Offline checks of intervention boundaries and data leakage controls."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from thesis_recovery import rq1_study as study
from thesis_recovery.ranking import load_models


class RQ1StudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = load_models(ROOT)

    def records(self):
        data = {}
        for sid, n in [("one", 4), ("two", 3)]:
            data[sid] = {"content": torch.randn(n, 128), "agent": torch.randn(n, 32),
                         "raw_structure": torch.randn(n, 23),
                         "paired_partner": torch.arange(n)[:, None].repeat(1, 2),
                         "paired_valid": torch.zeros(n, 2),
                         "adjacency": [(torch.arange(n)[:, None], torch.ones(n, 1)) for _ in range(4)]}
        return data

    def test_existing_complete_constructor_and_state_remain_identical(self):
        self.api.seed_all(17)
        old = self.api.create("AB_GLOBAL")
        new = study.create_model("complete", 17, self.api)
        for key, value in old.state_dict().items():
            self.assertTrue(torch.equal(value, new.state_dict()[key]), key)

    def test_common_initial_parameters_and_graph_removal_boundary(self):
        full = study.create_model("complete", 17, self.api)
        node = study.create_model("without_multirelation", 17, self.api)
        mean = study.create_model("without_candidate_attention", 17, self.api)
        for key, value in full.state_dict().items():
            if not key.startswith("layers."):
                self.assertTrue(torch.equal(value, node.state_dict()[key]), key)
            if key in mean.state_dict():
                self.assertTrue(torch.equal(value, mean.state_dict()[key]), key)
        self.assertTrue(all(isinstance(layer, self.api.original.NodeLayer) for layer in node.layers))
        self.assertIsNotNone(node.event)
        self.assertTrue(hasattr(node, "Q"))
        data = self.records()
        batch = self.api.collate(["one", "two"], data, (torch.zeros(23), torch.ones(23)), "cpu")
        node.eval()
        first, _ = study.score_batch(node, "without_multirelation", batch, self.api)
        batch["adjacency"] = [(torch.flip(index, [0]), valid) for index, valid in batch["adjacency"]]
        second, _ = study.score_batch(node, "without_multirelation", batch, self.api)
        for a, b in zip(first, second):
            self.assertTrue(torch.equal(a, b))

    def test_training_scaler_excludes_other_records(self):
        data = {"fit": {"raw_structure": torch.tensor([[1., 2.], [3., 2.]])},
                "validation": {"raw_structure": torch.tensor([[999., 999.]])}}
        mean, std = study.fit_scaler(data, ["fit"])
        self.assertTrue(torch.equal(mean, torch.tensor([2., 2.])))
        self.assertTrue(torch.equal(std, torch.tensor([1., 1.])))

    def test_prepare_binds_exact_category_members_without_loading_labels(self):
        protocol = study.prepare(ROOT)
        self.assertEqual(len(protocol["conditions"]["coding_only"]["members"]["train"]), 256)
        self.assertEqual(len(protocol["conditions"]["coding_only"]["members"]["validation"]), 64)
        self.assertEqual(len(protocol["conditions"]["complete"]["members"]["train"]), 492)
        study.verify_bindings(protocol, ROOT)
        bad = json.loads(json.dumps(protocol))
        bad["bindings"]["src/thesis_recovery/rq1_study.py"] = "changed"
        with self.assertRaisesRegex(ValueError, "changed"):
            study.verify_bindings(bad, ROOT)

    def test_native_ranking_metrics_do_not_accept_partial_rankings(self):
        result = study.ranking_metrics({"a": [1, 0, 2], "b": [0, 1]}, {"a": 0, "b": 0})
        self.assertEqual((result["correct"], result["total"]), (1, 2))
        self.assertEqual(result["MRR"], .75)
        with self.assertRaises(ValueError):
            study.ranking_metrics({"a": [3]}, {"a": 3})

    def test_committed_epoch_resume_matches_uninterrupted_synthetic_run(self):
        # Synthetic tensors only: exercise the driver without research labels.
        self.api.seed_all(72)
        data = self.records()
        config = study.settings("complete")
        config["max_epochs"] = 2
        protocol = {"bindings": {}, "seeds": [17], "conditions": {"complete": {
            "members": {"train": ["one"], "validation": ["two"]}, "settings": config}}}
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            protocols = []
            for name in ("continuous", "resumed"):
                root = base / name
                (root / study.SOURCE / "data").mkdir(parents=True)
                (root / study.SOURCE / "features").mkdir()
                torch.save({"records": data}, root / study.SOURCE / "features/train_validation_features.pt")
                (root / study.SOURCE / "data/selected_train_labels.private.json").write_text(json.dumps({"labels": [
                    {"sample_id": "one", "target_ordinal": 0}, {"sample_id": "two", "target_ordinal": 1}]}), encoding="utf-8")
                path = root / "protocol.json"
                path.write_text(json.dumps(protocol), encoding="utf-8")
                protocols.append((root, path))
            with mock.patch.object(study, "load_models", return_value=self.api):
                study.train(protocols[0][1], "complete", 17, root=protocols[0][0])
                original_save = torch.save
                calls = 0
                def interrupt_second_commit(*args, **kwargs):
                    nonlocal calls
                    calls += 1
                    if calls == 2:
                        raise RuntimeError("synthetic interruption")
                    return original_save(*args, **kwargs)
                with mock.patch.object(torch, "save", side_effect=interrupt_second_commit):
                    with self.assertRaisesRegex(RuntimeError, "synthetic interruption"):
                        study.train(protocols[1][1], "complete", 17, root=protocols[1][0])
                study.train(protocols[1][1], "complete", 17, root=protocols[1][0])
            states = [torch.load(next(root.rglob("resume.pt")), weights_only=False) for root, _ in protocols]
            self.assertEqual([r["validation"] for r in states[0]["history"]],
                             [r["validation"] for r in states[1]["history"]])
            for key, value in states[0]["model"].items():
                self.assertTrue(torch.equal(value, states[1]["model"][key]), key)


if __name__ == "__main__":
    unittest.main()

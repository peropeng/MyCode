"""Offline contract checks. Fake responses are never experiment predictions."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from thesis_recovery.diagnostic_baselines import DiagnosticSession, PendingRequestError


class DiagnosticBaselineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "session.json"
        self.sample = {"sample_id": "synthetic-contract-only", "task": "Synthetic fixture",
                       "steps": [{"role": "r" + str(i % 2), "content": "fixture " + str(i)} for i in range(5)]}
        self.config = {"backend": "local:contract-fixture", "max_requests": 8,
                       "max_output_tokens": 128, "max_model_seconds": 60}

    def session(self, method="binary_search"):
        return DiagnosticSession.create(self.path, self.sample, method, self.config)

    def respond(self, session, text, elapsed=1, usage=True, finish_reason="stop"):
        request = session.next_request()
        session.mark_submitted(request["request_id"])
        receipt = {"text": text, "finish_reason": finish_reason}
        if usage:
            receipt["usage"] = {"prompt_tokens": 40, "completion_tokens": 2}
        session.record_response(request["request_id"], receipt, elapsed)
        return request, receipt

    def test_resume_preserves_segment_and_never_repeats_submitted_request(self):
        session = self.session()
        self.respond(session, "lower half")
        request = session.next_request()
        self.assertEqual(request["range"], [3, 4])
        session.mark_submitted(request["request_id"])
        restored = DiagnosticSession.resume(self.path, self.sample, "binary_search", self.config)
        with self.assertRaises(PendingRequestError):
            restored.next_request()
        with self.assertRaises(PendingRequestError):
            restored.mark_submitted(request["request_id"])
        receipt = {"text": "upper half", "usage": {"prompt_tokens": 30, "completion_tokens": 2}}
        restored.record_response(request["request_id"], receipt, 2)
        restored.record_response(request["request_id"], receipt, 2)
        self.assertEqual(restored.state["result"]["predicted_step"], 3)
        self.assertIsNone(restored.state["result"]["ranking"])
        self.assertEqual(restored.totals()["submitted_requests"], 2)
        self.assertEqual(restored.totals()["prompt_tokens"], 70)
        self.assertIsNone(restored.next_request())

    def test_prepared_request_export_is_idempotent_and_prompt_has_no_answer(self):
        session = self.session()
        first = session.next_request()
        restored = DiagnosticSession.resume(self.path, self.sample, "binary_search", self.config)
        self.assertEqual(first, restored.next_request())
        self.assertEqual(restored.totals()["submitted_requests"], 0)
        text = first["messages"][1]["content"]
        self.assertIn("from step 0 to step 2", text)
        self.assertNotIn("The Answer for the problem", text)
        self.assertIn("r0: fixture 0", text)

    def test_ambiguous_output_is_not_a_completed_prediction_or_free_retry(self):
        session = self.session()
        self.respond(session, "upper half or lower half", usage=False)
        self.assertEqual(session.state["status"], "invalid_output")
        self.assertIsNone(session.state["result"])
        self.assertFalse(session.totals()["usage_complete"])
        self.assertIsNone(session.totals()["prompt_tokens"])
        with self.assertRaises(ValueError):
            session.next_request()
        self.assertEqual([session.state["low"], session.state["high"]], [0, 4])
        session.retry_invalid()
        self.assertEqual(session.next_request()["range"], [0, 4])
        self.assertEqual(session.totals()["submitted_requests"], 1)

    def test_wrong_input_config_protocol_and_journal_mutation_cannot_resume(self):
        self.session()
        changed = copy.deepcopy(self.sample)
        changed["steps"][0]["content"] = "different"
        with self.assertRaises(ValueError):
            DiagnosticSession.resume(self.path, changed, "binary_search", self.config)
        config = {**self.config, "max_requests": 9}
        with self.assertRaises(ValueError):
            DiagnosticSession.resume(self.path, self.sample, "binary_search", config)
        with self.assertRaises(ValueError):
            DiagnosticSession.resume(self.path, self.sample, "all_at_once", self.config)
        state = json.loads(self.path.read_text(encoding="utf-8"))
        state["high"] = 0
        self.path.write_text(json.dumps(state), encoding="utf-8")
        with self.assertRaises(ValueError):
            DiagnosticSession.resume(self.path, self.sample, "binary_search", self.config)

    def test_limits_and_failure_receipt_are_preserved(self):
        self.config["max_requests"] = 1
        session = self.session()
        request = session.next_request()
        session.mark_submitted(request["request_id"])
        session.record_failure(request["request_id"], "synthetic transport failure", 2)
        self.assertFalse(session.totals()["usage_complete"])
        session.retry_invalid()
        self.assertIsNone(session.next_request())
        self.assertEqual(session.state["status"], "budget_exhausted")
        self.assertEqual(session.totals()["submitted_requests"], 1)

    def test_all_at_once_preserves_single_position_and_native_role(self):
        session = self.session("all_at_once")
        self.respond(session, "Agent Name: r1\nStep Number: 3\nReason for Mistake: Synthetic reason")
        result = session.state["result"]
        self.assertEqual(result["predicted_step"], 3)
        self.assertTrue(result["role_matches_selected_step"])
        self.assertIsNone(result["ranking"])
        self.assertEqual(result["agent_output_origin"], "native_model_output")

    def test_late_truncated_or_out_of_bounds_output_cannot_complete(self):
        for method, text, seconds, finish in [
            ("binary_search", "upper half", 61, "stop"),
            ("binary_search", "upper half", 1, "length"),
            ("all_at_once", "Agent Name: r0\nStep Number: 9\nReason for Mistake: x", 1, "stop"),
        ]:
            with self.subTest(method=method, seconds=seconds, finish=finish):
                self.path = self.path.with_name(method + str(seconds) + finish + ".json")
                session = self.session(method)
                self.respond(session, text, elapsed=seconds, finish_reason=finish)
                self.assertEqual(session.state["status"], "invalid_output")
                self.assertIsNone(session.state["result"])

    def test_no_labels_no_unknown_methods_and_no_overwrite(self):
        with self.assertRaises(ValueError):
            DiagnosticSession.create(self.path, {**self.sample, "gold": 1}, "binary_search", self.config)
        with self.assertRaises(ValueError):
            self.session("invented")
        self.session()
        with self.assertRaises(FileExistsError):
            self.session()


if __name__ == "__main__":
    unittest.main()

"""Synthetic checks of original scope admission; no real private data is read."""
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest

ENTRY = Path(__file__).resolve().parents[1] / 'tools/accept_rq2_controls.py'
SPEC = importlib.util.spec_from_file_location('control_acceptance_fixture', ENTRY)
accept = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(accept)


class OriginalScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.task = 'synthetic-only'
        self.cert = self.root / self.task / 'FLOW/external_once_private/result.json'
        self.packet = self.root / 'terminal.json'
        self.binding = self.root / 'binding.json'
        self.spec = {'task_id': self.task, 'goal_nodes': ['public-goal'], 'ordinary_nodes': ['ordinary']}
        self.nodes = ['public-goal', 'ordinary', 'synthetic-independent']
        self.data = {'status': 'COMPLETE_EXTERNAL_ONCE_PRIVATE', 'private_attempts': 1,
                     'raw_native_result': {'executed': True, 'guard_loaded': True,
                         'business_state_unchanged': True, 'frozen_tests_unchanged': True,
                         'timeout': False, 'requested_nodes': self.nodes,
                         'stop_receipt': {'root_stopped': True, 'descendants_stopped': True,
                                          'own_Job_empty_before_close': True}}}
        self.anchor = {'task_id': self.task, 'complete': True,
                       'raw_external_result': 'D:/old/' + self.task + '/FLOW/external_once_private/result.json'}

    def bind(self):
        for p, value in [(self.cert, self.data), (self.packet, self.anchor)]:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(value), encoding='utf-8')
        self.binding.write_text(json.dumps({'task_id': self.task, 'certificate_path': str(self.cert),
            'certificate_sha256': accept.sha(self.cert), 'terminal_packet_path': str(self.packet),
            'terminal_packet_sha256': accept.sha(self.packet)}), encoding='utf-8')
        return types.SimpleNamespace(scope_binding=self.binding)

    def test_taskless_archived_certificate_uses_bound_terminal_and_exact_scope(self):
        nodes, independent, chain = accept.original_scope(self.spec, self.bind())
        self.assertEqual(nodes, self.nodes)
        self.assertEqual(independent, ['synthetic-independent'])
        self.assertTrue(chain['scope_exactly_reused'])

    def test_certificate_cannot_be_reassigned_to_another_task(self):
        self.anchor['task_id'] = 'different-task'
        with self.assertRaisesRegex(accept.AdmissionError, 'TASK_ANCHOR_MISMATCH'):
            accept.original_scope(self.spec, self.bind())

    def test_incomplete_old_stop_is_rejected(self):
        self.data['raw_native_result']['stop_receipt']['descendants_stopped'] = False
        with self.assertRaisesRegex(accept.AdmissionError, 'STOP_UNKNOWN'):
            accept.original_scope(self.spec, self.bind())

    def test_scope_cannot_drop_a_current_public_goal(self):
        self.data['raw_native_result']['requested_nodes'] = ['ordinary', 'synthetic-independent']
        with self.assertRaisesRegex(accept.AdmissionError, 'PUBLIC_SCOPE_DIFFER'):
            accept.original_scope(self.spec, self.bind())


if __name__ == '__main__':
    unittest.main()

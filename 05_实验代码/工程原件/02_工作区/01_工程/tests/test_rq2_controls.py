"""Synthetic public-only integration of frozen core and durable order adapter."""
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest import mock

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE / 'src'))
from thesis_recovery.rq2_control_env import ControlEnvironment, digest, sha, save, load_frozen, wrap_public_validation, observe_case, read


def native_value(goals, ordinary, passed=False):
    states = {n: {'status': 'passed' if n in ordinary or passed else 'failed', 'detail': ''} for n in goals + ordinary}
    return {'executed': True, 'guard_loaded': True, 'business_state_unchanged': True,
        'frozen_tests_unchanged': True, 'exact_test_coverage': True, 'completed_guarded_coverage': True,
        'timeout': False, 'requested_nodes': goals + ordinary, 'pytest': {'outcomes': states},
        'expected_test_count': len(states), 'passed_count': sum(v['status'] == 'passed' for v in states.values()),
        'passed': passed, 'stdout': '', 'stderr': '', 'stop_receipt': {'owned_job_closed': True,
             'root_process_stopped': True, 'all_owned_descendants_terminated': True}}


class Client:
    def __init__(self, interrupt=False): self.cache = {}; self.actual = 0; self.interrupt = interrupt
    def generate_body(self, body, *, sample_id, stage, remaining_seconds):
        key = (sample_id, stage, digest(body))
        if key not in self.cache:
            self.actual += 1
            if '/tool0' in stage:
                message = {'role': 'assistant', 'content': None, 'tool_calls': [{'id': 'fixture-call', 'type': 'function',
                       'function': {'name': 'read_current_source', 'arguments': json.dumps({'path': 'module.py'})}}]}
            else:
                message = {'role': 'assistant', 'content': json.dumps({'rationale': 'synthetic only',
                         'edits': [{'path': 'module.py', 'old': 'return 0', 'new': 'return 1'}]})}
            self.cache[key] = {'message': message, 'text': message['content'], 'usage': {'prompt_tokens': 10, 'completion_tokens': 20},
                              'finish_reason': 'tool_calls' if '/tool0' in stage else 'stop', 'request_id': stage}
            if self.interrupt and '/tool1' in stage:
                self.interrupt = False
                raise RuntimeError('Synthetic crash after durable client settlement')
        return self.cache[key]


class ControlsTests(unittest.TestCase):
    def setUp(self):
        (ENGINE / '.rebuild').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='controls-test-', dir=ENGINE / '.rebuild')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = 'def answer():\n    return 0\n'
        for name in ['business', 'public', 'frozen', 'assets', 'task/visible']:
            (self.root / name).mkdir(parents=True)
        (self.root / 'business/module.py').write_text(source, encoding='utf-8')
        test = 'def test_goal():\n    pass\n\ndef test_ordinary():\n    pass\n'
        for name in ['public', 'frozen']: (self.root / name / 'test_public.py').write_text(test, encoding='utf-8')
        edits = []
        for i in range(2):
            before, after = source.replace('0', str(i + 2)), source.replace('0', str(i + 3))
            for side, text in [('before', before), ('after', after)]:
                (self.root / 'assets' / (str(i) + side)).write_text(text, encoding='utf-8')
            edits.append({'call_id': str(i), 'state_path': 'repo/module.py',
                'before': {'blob': str(i) + 'before', 'sha256': sha(self.root / 'assets' / (str(i) + 'before'))},
                'after': {'blob': str(i) + 'after', 'sha256': sha(self.root / 'assets' / (str(i) + 'after'))}})
        save(self.root / 'task/visible/edits.json', edits)
        save(self.root / 'plan.json', {'complete_original_ordinal_order': [0, 1]})
        pack = load_frozen().codec.encode({'original_issue': 'Synthetic only', 'public_history': [{'source_message_index': 0, 'content': 'fixture'}],
                                         'failure_feedback': {'test_public.py::test_goal': {'status': 'failed', 'detail': ''}}})
        save(self.root / 'pack.json', pack)
        self.goals, self.ordinary = ['test_public.py::test_goal'], ['test_public.py::test_ordinary']
        self.spec = {'task_id': 'synthetic-only', 'business_root': str(self.root / 'business'),
            'business_hashes': {'module.py': sha(self.root / 'business/module.py')}, 'public_view': str(self.root / 'public'),
            'support_hashes': {'test_public.py': sha(self.root / 'public/test_public.py')},
            'public_test_py_files_SHA256': {'test_public.py': sha(self.root / 'public/test_public.py')},
            'frozen_root': str(self.root / 'frozen'), 'frozen_inventory': {'test_public.py': sha(self.root / 'frozen/test_public.py')},
            'pack': str(self.root / 'pack.json'), 'ref': {'mapping': [{'step': i, 'successful_edit_ids': [str(i)]} for i in range(2)],
            'task_path': str(self.root / 'task'), 'asset_root': str(self.root / 'assets')}, 'ranking_plan': str(self.root / 'plan.json'),
            'goal_nodes': self.goals, 'ordinary_nodes': self.ordinary,
            'initial_validation': wrap_public_validation(native_value(self.goals, self.ordinary), self.ordinary),
            'python': sys.executable, 'package': 'fixture'}
        self.native_calls = 0
    def native(self, active, frozen, nodes, output, python, package, deadline):
        self.native_calls += 1
        return native_value(self.goals, self.ordinary, passed='return 1' in (active / 'repo/module.py').read_text(encoding='utf-8'))
    def environment(self, condition, client):
        return ControlEnvironment(self.spec, condition, client=client, native=self.native,
                                  output=self.root / 'runs' / condition)
    def test_frozen_core_tools_and_completed_result_replay(self):
        client = Client()
        env = self.environment('SOURCE3', client)
        result = env.run()
        self.assertEqual(result['status'], 'COMPLETED', result.get('error'))
        self.assertEqual(result['first_public_pass_attempt'], 1)
        self.assertEqual((client.actual, self.native_calls), (2, 1))
        again = self.environment('SOURCE3', client).run()
        self.assertEqual(again['first_public_pass_attempt'], 1)
        self.assertEqual((client.actual, self.native_calls), (2, 1))
    def test_reverse_and_sorted_expose_distinct_original_edit_prefixes(self):
        sorted_env, reversed_env = self.environment('SOURCE3', Client()), self.environment('REVERSE', Client())
        left, _ = sorted_env.source_evidence(); right, _ = reversed_env.source_evidence()
        self.assertEqual(left['selected_evidence_ids'], ['0', '1'])
        self.assertEqual(right['selected_evidence_ids'], ['1', '0'])
    def test_restart_reuses_durable_tool_response_and_unchanged_pending_body(self):
        client = Client(interrupt=True)
        first = self.environment('SOURCE3', client).run()
        self.assertEqual(first['status'], 'ENGINEERING_UNKNOWN')
        self.assertEqual(self.native_calls, 0)
        resumed = self.environment('SOURCE3', client).run()
        self.assertEqual(resumed['status'], 'COMPLETED', resumed.get('error'))
        self.assertEqual((client.actual, self.native_calls), (2, 1))
    def test_common_C0_observation_is_not_reexecuted_after_known_completion(self):
        output = self.root / 'common_C0'
        first, path = observe_case(self.spec, output=output, native=self.native)
        self.assertTrue(first['native_record']['completed_guarded_coverage'])
        second, repeated = observe_case(self.spec, output=output, native=self.native)
        self.assertEqual((path, first), (repeated, second))
        self.assertEqual(self.native_calls, 1)
    def test_resume_preserves_scientific_clock_without_preview_starting_it(self):
        env = self.environment('SOURCE3', Client())
        self.assertFalse((env.out / 'SCIENCE_CLOCK.json').exists())
        env.run()
        resumed = self.environment('SOURCE3', Client())
        with mock.patch('thesis_recovery.rq2_control_env.time.time', return_value=resumed.clock['wall_start'] + 1801):
            self.assertEqual(resumed.time_left(), 0)
    def test_test_source_is_denied_and_not_read_during_real_body_construction(self):
        env = self.environment('SOURCE3', Client())
        with self.assertRaises(PermissionError): env.reader('list_public_masked_tests', {})
        with self.assertRaises(PermissionError): env.reader('read_public_masked_test', {'path': 'test_public.py'})
        original = Path.read_text
        def block_test_sources(path, *args, **kwargs):
            if path.is_relative_to(self.root / 'public') or path.is_relative_to(self.root / 'frozen'):
                raise AssertionError('Body attempted to open native-only test source')
            return original(path, *args, **kwargs)
        with mock.patch.object(Path, 'read_text', block_test_sources):
            result = env.run()
        self.assertEqual(result['status'], 'COMPLETED', result.get('error'))
        body = read(env.out / 'calls/001/request.json')['body']
        tool_names = {t['function']['name'] for t in body['tools']}
        self.assertNotIn('list_public_masked_tests', tool_names)
        self.assertNotIn('read_public_masked_test', tool_names)
        self.assertIn('read_current_source', tool_names)
        self.assertIn('read_public_history', tool_names)
        self.assertTrue(any('Test source is not shared' in m.get('content', '') for m in body['messages']))
    def test_existing_condition_producer_prevents_duplicate_model_or_native_dispatch(self):
        client = Client()
        env = self.environment('SOURCE3', client)
        (env.out / 'producer.lock').write_text('other-producer', encoding='utf-8')
        with self.assertRaises(FileExistsError): env.run()
        self.assertEqual((client.actual, self.native_calls), (0, 0))


if __name__ == '__main__': unittest.main()

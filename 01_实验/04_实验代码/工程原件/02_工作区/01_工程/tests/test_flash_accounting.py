"""Synthetic HTTP receipts only; never use experiment tasks or real API calls."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from thesis_recovery.flash_accounting import FlashClient, UnresolvedRequest, write


class FlashAccountingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.client = FlashClient(self.root, {'allowed_sample_ids': ['fixture'], 'initial_balance_cny': '29.34',
                                               'max_requests': 4, 'max_spend_cny': 3, 'balance_floor_cny': 1})
        write(self.root / 'metadata.json', {'model': {'context_window': 10000}})
        self.body = {'model': 'deepseek-flash', 'messages': [{'role': 'user', 'content': 'fixture only'}],
                     'max_tokens': 128, 'temperature': 0, 'tools': [{'type': 'function', 'function': {'name': 'read', 'parameters': {'type': 'object'}}}]}
        self.payload = {'model': 'deepseek-flash', 'usage': {'prompt_tokens': 100, 'completion_tokens': 4},
                        'choices': [{'message': {'role': 'assistant', 'content': None, 'tool_calls': [
                            {'id': 'synthetic-call-id', 'type': 'function', 'function': {'name': 'read', 'arguments': '{}'}}]},
                            'finish_reason': 'tool_calls'}]}

    def fake(self, path, body=None, timeout=90):
        if path == '/chat/completions':
            self.assertEqual(body['tools'], self.body['tools'])
            return self.payload
        return {'is_available': True, 'balance_infos': [{'currency': 'CNY', 'total_balance': '29.34'}]}

    def test_tool_message_and_receipt_reuse_preserve_call_ids_without_repost(self):
        with mock.patch.object(self.client, '_http', side_effect=self.fake) as request:
            a = self.client.generate_body(self.body, sample_id='fixture', stage='sorted/attempt1/tool1')
            b = self.client.generate_body(self.body, sample_id='fixture', stage='sorted/attempt1/tool1')
            self.assertEqual(a, b)
            self.assertEqual(a['message']['tool_calls'][0]['id'], 'synthetic-call-id')
            self.assertEqual(sum(c.args[0] == '/chat/completions' for c in request.call_args_list), 1)
            self.assertEqual(self.client.summary()['submitted_requests'], 1)

    def test_unknown_transport_is_never_automatically_retried(self):
        def fail(path, body=None, timeout=90):
            if body is not None:
                raise TimeoutError()
            return self.fake(path, body, timeout)
        with mock.patch.object(self.client, '_http', side_effect=fail) as request:
            for _ in range(2):
                with self.assertRaises(UnresolvedRequest):
                    self.client.generate_body(self.body, sample_id='fixture', stage='sorted/attempt1/tool1')
            self.assertEqual(sum(c.args[0] == '/chat/completions' for c in request.call_args_list), 1)
            self.assertEqual(self.client.summary()['unresolved_requests'], 1)

    def test_saved_response_survives_balance_failure_and_reconciles_without_post(self):
        balances = 0
        def once_fail_after(path, body=None, timeout=90):
            nonlocal balances
            if path == '/user/balance':
                balances += 1
                if balances == 2:
                    raise TimeoutError()
            return self.fake(path, body, timeout)
        with mock.patch.object(self.client, '_http', side_effect=once_fail_after) as request:
            with self.assertRaises(UnresolvedRequest):
                self.client.generate_body(self.body, sample_id='fixture', stage='reverse/attempt1/tool1')
            result = self.client.generate_body(self.body, sample_id='fixture', stage='reverse/attempt1/tool1')
            self.assertEqual(result['finish_reason'], 'tool_calls')
            self.assertEqual(sum(c.args[0] == '/chat/completions' for c in request.call_args_list), 1)
            self.assertEqual(self.client.summary()['unresolved_requests'], 0)


if __name__ == '__main__':
    unittest.main()

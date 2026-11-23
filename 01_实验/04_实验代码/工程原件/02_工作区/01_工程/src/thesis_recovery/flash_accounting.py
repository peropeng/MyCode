"""Current-task Flash transport; preserve tool messages and reconcile before retry.

No requests on import. Credentials are read only for the HTTP Authorization
header. Usage estimates use the verified CNY peak price bounds, not invoices.
"""
from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.request

BASE = 'https://api.deepseek.com'
D = Decimal


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w', encoding='utf-8', newline='\n') as stream:
        stream.write(canonical(value) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


class UnresolvedRequest(RuntimeError):
    pass


class FlashClient:
    def __init__(self, directory, config, *, opener=None):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.config = json.loads(Path(config).read_text(encoding='utf-8')) if isinstance(config, (str, Path)) else config
        self.opener = opener or urllib.request.urlopen
        self.config_digest = digest(self.config)

    def _http(self, route, body=None, timeout=90):
        key = os.environ.get('DEEPSEEK_API_KEY')
        if not key:
            raise RuntimeError('DEEPSEEK_API_KEY_MISSING')
        req = urllib.request.Request(BASE + route,
            data=None if body is None else canonical(body).encode('utf-8'),
            headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'},
            method='GET' if body is None else 'POST')
        with self.opener(req, timeout=timeout) as response:
            return json.loads(response.read().decode('utf-8'))

    def metadata(self):
        catalog = self._http('/models')
        rows = [r for r in catalog.get('data', []) if r.get('id') == 'deepseek-flash']
        if len(rows) != 1 or rows[0].get('name', '').casefold() != 'deepseek-v4.1-flash':
            raise RuntimeError('FLASH_MAPPING_CHANGED')
        result = {'at_utc': datetime.now(timezone.utc).isoformat(), 'model': rows[0], 'balance': self._balance()}
        write(self.directory / 'metadata.json', result)
        return result

    def _balance(self):
        payload = self._http('/user/balance', timeout=30)
        rows = [r for r in payload.get('balance_infos', []) if r.get('currency') == 'CNY']
        if not payload.get('is_available') or len(rows) != 1:
            raise RuntimeError('CNY_BALANCE_UNKNOWN')
        value = D(str(rows[0]['total_balance']))
        if not value.is_finite() or value < 0:
            raise RuntimeError('CNY_BALANCE_INVALID')
        return str(value)

    def _records(self):
        return sorted([json.loads(p.read_text(encoding='utf-8')) for p in (self.directory / 'calls').glob('*.json')
                if not p.name.endswith('.response.json')], key=lambda r: r['submitted_at_utc'])

    def summary(self):
        rows = self._records()
        done = [r for r in rows if r['status'] == 'completed']
        pending = [r for r in rows if r['status'] != 'completed']
        return {'submitted_requests': len(rows), 'completed_requests': len(done), 'unresolved_requests': len(pending),
                'prompt_tokens': sum(r['receipt']['usage']['prompt_tokens'] for r in done),
                'completion_tokens': sum(r['receipt']['usage']['completion_tokens'] for r in done),
                'usage_cost_upper_cny': str(sum((D(r['receipt']['cost_upper_cny']) for r in done), D(0))),
                'usage_cost_lower_cny': str(sum((D(r['receipt']['cost_upper_cny']) / 2 for r in done), D(0))),
                'unresolved_hold_cny': str(sum((D(r['reserved_cny']) for r in pending), D(0))),
                'latest_observed_balance_cny': done[-1]['receipt']['balance_after_cny'] if done else self.config['initial_balance_cny'],
                'cost_basis': 'usage-based official peak upper/idle lower estimate; account balance is rounded, not per-call invoice'}

    def _settle(self, path, record, saved):
        payload, elapsed = saved['payload'], saved['elapsed_seconds']
        message = payload['choices'][0]['message']
        usage = payload['usage']
        if not isinstance(message.get('content'), str) and not message.get('tool_calls'):
            raise ValueError('MISSING_CONTENT_AND_TOOL_CALLS')
        if any(type(usage.get(k)) is not int or usage[k] < 0 for k in ('prompt_tokens', 'completion_tokens')):
            raise ValueError('USAGE_UNVERIFIED')
        if usage['completion_tokens'] > record['body']['max_tokens']:
            raise ValueError('OUTPUT_CAP_EXCEEDED')
        if payload.get('model', '').casefold() not in ('deepseek-flash', 'deepseek-v4.1-flash'):
            raise ValueError('RETURNED_MODEL_CHANGED')
        hit = usage.get('prompt_cache_hit_tokens', 0)
        miss = usage.get('prompt_cache_miss_tokens', usage['prompt_tokens'] - hit)
        if type(hit) is not int or type(miss) is not int or min(hit, miss) < 0 or hit + miss != usage['prompt_tokens']:
            hit, miss = 0, usage['prompt_tokens']
        upper = (D(hit) * D('.04') + D(miss) * D(2) + D(usage['completion_tokens']) * D(8)) / D(1000000)
        after = self._balance()
        receipt = {'text': message.get('content') or '', 'content': message.get('content') or '',
                   'message': message, 'tool_calls': message.get('tool_calls'), 'usage': usage,
                   'request_id': record['request_id'], 'finish_reason': payload['choices'][0].get('finish_reason'),
                   'elapsed_seconds': elapsed, 'cost_upper_cny': str(upper), 'cost_lower_cny': str(upper / 2),
                   'balance_before_cny': record['balance_before_cny'], 'balance_after_cny': after,
                   'model': payload.get('model'), 'system_fingerprint': payload.get('system_fingerprint')}
        record.update(status='completed', receipt=receipt)
        write(path, record)
        return receipt

    def generate_body(self, body, *, sample_id, stage, remaining_seconds=None):
        body = json.loads(canonical(body))
        if body.get('model', 'deepseek-flash') != 'deepseek-flash' or body.get('stream', False):
            raise ValueError('FLASH_NONSTREAM_REQUIRED')
        body['model'] = 'deepseek-flash'
        body['stream'] = False
        body.setdefault('thinking', {'type': 'disabled'})
        if body['thinking'] != {'type': 'disabled'}:
            raise ValueError('FROZEN_NONTHINKING_MODE_REQUIRED')
        cap = body.get('max_tokens')
        if type(cap) is not int or not 1 <= cap <= 16384 or sample_id not in self.config['allowed_sample_ids']:
            raise ValueError('OUTSIDE_CURRENT_SMALL_COMPARISON')
        if remaining_seconds is not None and remaining_seconds <= 0:
            raise RuntimeError('FLOW_TIME_EXHAUSTED')
        key = digest({'body': body, 'sample_id': sample_id, 'stage': stage, 'config': self.config_digest})
        path = self.directory / 'calls' / (key + '.json')
        raw_path = path.with_suffix('.response.json')
        if path.exists():
            record = json.loads(path.read_text(encoding='utf-8'))
            if record['status'] == 'completed':
                return record['receipt']
            if raw_path.exists():
                return self._settle(path, record, json.loads(raw_path.read_text(encoding='utf-8')))
            raise UnresolvedRequest('RECONCILE_WITHOUT_REPOST:' + key)
        lock = self.directory / 'budget.lock'
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(descriptor)
        try:
            rows = self._records()
            if any(r['status'] != 'completed' for r in rows):
                raise UnresolvedRequest('PRIOR_REQUEST_OUTCOME_UNRESOLVED')
            if len(rows) >= self.config['max_requests']:
                raise RuntimeError('CURRENT_REQUEST_LIMIT')
            metadata = json.loads((self.directory / 'metadata.json').read_text(encoding='utf-8'))
            window = metadata['model']['context_window']
            if len(canonical(body).encode('utf-8')) + cap + 4096 > window:
                raise RuntimeError('CONTEXT_BOUND_EXCEEDED_NO_CLIPPING')
            reserve = (D(window) * D(2) + D(cap) * D(8)) / D(1000000)
            upper = D(self.summary()['usage_cost_upper_cny'])
            before = D(self._balance())
            if upper + reserve > D(str(self.config['max_spend_cny'])) or before - reserve < D(str(self.config['balance_floor_cny'])):
                raise RuntimeError('CURRENT_COMPARISON_COST_BOUND')
            record = {'request_id': key, 'status': 'submitted', 'body': body, 'sample_id': sample_id,
                      'stage': stage, 'config_sha256': self.config_digest, 'reserved_cny': str(reserve),
                      'balance_before_cny': str(before), 'submitted_at_utc': datetime.now(timezone.utc).isoformat()}
            write(path, record)
            started = time.monotonic()
            try:
                payload = self._http('/chat/completions', body, timeout=min(120, remaining_seconds or 120))
                saved = {'payload': payload, 'elapsed_seconds': time.monotonic() - started}
                write(raw_path, saved)
                return self._settle(path, record, saved)
            except Exception as exc:
                record.update(status='outcome_unresolved', error_class=type(exc).__name__, http_status=getattr(exc, 'code', None))
                write(path, record)
                raise UnresolvedRequest('REQUEST_UNRESOLVED:' + key + ':' + type(exc).__name__) from None
        finally:
            lock.unlink()

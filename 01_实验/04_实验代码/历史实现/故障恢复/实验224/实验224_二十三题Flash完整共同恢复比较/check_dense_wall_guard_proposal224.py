"""Synthetic deadline and delegation checks; no business model/native calls."""
from common166 import *
from types import SimpleNamespace
from dense_wall_guard_proposal224 import bounded_prepare, prepared_scope


def fixture_prepare(texts, device='cpu', batch_size=4):
    result = []
    for start in range(0, len(texts), batch_size):
        result.extend(encoder(device).encode(texts[start:start + batch_size], normalize=True))
    return result


def check():
    calls = []; clock = {'remaining': 2}; checks = []

    class FakeEncoder:
        def encode(self, texts, **kwargs):
            calls.append((texts, kwargs))
            return [len(x) for x in texts]

    fake = FakeEncoder()
    def factory(device):
        assert device == 'cpu'
        return fake
    def require():
        checks.append(clock['remaining'])
        if clock['remaining'] <= 0:
            raise RuntimeError('METHOD_SEARCH_WALL_BUDGET')

    checked = bounded_prepare(fixture_prepare, factory, require)
    text = ['aa', 'b', 'ccc', 'd', 'ee']
    assert checked(text, batch_size=4) == [2, 1, 3, 1, 2]
    assert calls == [(text[:4], {'normalize': True}), (text[4:], {'normalize': True})]
    assert len(checks) == 6
    clock['remaining'] = 0; old_count = len(calls)
    try:
        checked(text)
        raise AssertionError('Expired deadline accepted')
    except RuntimeError as error:
        assert str(error) == 'METHOD_SEARCH_WALL_BUDGET'
    assert len(calls) == old_count

    clock['remaining'] = 1
    class ExpiringEncoder:
        def encode(self, texts, **kwargs):
            calls.append((texts, kwargs)); clock['remaining'] = 0
            return [len(x) for x in texts]
    checked = bounded_prepare(fixture_prepare, lambda device: ExpiringEncoder(), require)
    old_count = len(calls)
    try:
        checked(text, batch_size=4)
        raise AssertionError('Deadline overrun accepted')
    except RuntimeError as error:
        assert str(error) == 'METHOD_SEARCH_WALL_BUDGET'
    assert len(calls) == old_count + 1

    dense = SimpleNamespace(prepare=fixture_prepare, encoder=factory)
    env = SimpleNamespace(_require=require)
    try:
        with prepared_scope(dense, env):
            assert dense.prepare is not fixture_prepare
            dense.prepare(text)
    except RuntimeError:
        pass
    assert dense.prepare is fixture_prepare
    report = {'at_utc': now(), 'status': 'PASS_SYNTHETIC_NOT_INSTALLED', 'cases': ['exact_text_output_device_batch_kwargs', 'checks_before_after_each_batch', 'expired_no_encoding', 'crossing_deadline_no_next_batch', 'scope_restores_original_on_exception'], 'new_model_POST_native_private_Gold': 0, 'proposal_source_sha256': sha(E / 'dense_wall_guard_proposal224.py'), 'test_source_sha256': sha(E / 'check_dense_wall_guard_proposal224.py')}
    save(E / 'v2_auth_direct_publicpack/dense_wall_guard_proposal_pure_checks_v2.json', report)
    print(canonical(report))


if __name__ == '__main__':
    check()

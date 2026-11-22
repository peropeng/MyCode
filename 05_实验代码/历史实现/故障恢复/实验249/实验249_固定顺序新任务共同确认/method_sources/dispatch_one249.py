"""Single complete sealed body; separate exact Root grant, no automatic resend."""
import argparse
import types
from trial_runtime249 import *
import shared_input249


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--ready-dir', required=True); parser.add_argument('--root-grant', required=True)
    args = parser.parse_args(); slot = Path(args.ready_dir).resolve()
    if not slot.is_relative_to(HERE / 'runs'): raise RuntimeError('EXP249_DISPATCH_OUTPUT_SCOPE')
    ready = read(slot / 'FIRST_UNPOST_READY.json'); body = read(slot / 'FIRST_UNPOST_BODY.json')
    grant_path = Path(args.root_grant).resolve(); grant = read(grant_path); grant_sha = sha(grant_path)
    for field in ('root_authorized', 'model_authorized', 'finance_authorized'):
        if grant.get(field) is not True: raise RuntimeError('EXP249_EXACT_MODEL_GRANT_CLOSED_' + field)
    if (grant.get('native_authorized') is not False or grant.get('private_authorized') is not False
            or grant.get('maximum_new_requests') != 1
            or any(grant.get(k) != ready[k] for k in ('method', 'task_id', 'trial_id', 'call_ordinal', 'finance_phase'))
            or grant.get('body_SHA256') != digest(body) or ready['body_SHA256'] != digest(body)
            or grant.get('ready_SHA256') != sha(slot / 'FIRST_UNPOST_READY.json')):
        raise RuntimeError('EXP249_MODEL_TASK_TRIAL_BODY_GRANT_MISMATCH')
    seal_ref = ready['method_source_seal']
    if sha(seal_ref['path']) != seal_ref['sha256'] or grant.get('method_source_seal_SHA256') != seal_ref['sha256']:
        raise RuntimeError('EXP249_MODEL_SOURCE_SEAL_NOT_BOUND')
    verify_source_seal(seal_ref['path'])
    if sha(ready['contract_path']) != ready['contract_SHA256'] or grant.get('contract_SHA256') != ready['contract_SHA256']:
        raise RuntimeError('EXP249_TRIAL_CONTRACT_DRIFT')
    config_ref = ready['finance_configuration']
    if config_ref != grant.get('finance_configuration') or sha(config_ref['path']) != config_ref['sha256']:
        raise RuntimeError('EXP249_CONTINUOUS_FINANCE_CONFIG_DRIFT')
    config = read(config_ref['path']); trial = Path(ready['trial_output_root']).resolve()
    if not trial.is_relative_to(HERE / 'runs') or not slot.is_relative_to(trial): raise RuntimeError('EXP249_TRIAL_OUTPUT_BINDING')
    t0_path = trial / 'SCIENCE_T0_TRIAL_PREPARATION_STARTED.json'
    if not t0_path.exists(): raise RuntimeError('EXP249_REAL_TRIAL_PREPARATION_T0_MISSING')
    t0 = read(t0_path)
    if t0.get('task_id') != ready['task_id'] or t0.get('trial_id') != ready['trial_id'] or t0.get('real_preparation_time_included') is not True:
        raise RuntimeError('EXP249_ORIGINAL_TRIAL_T0_INVALID')
    limit = datetime.datetime.fromisoformat(grant['lease_end_UTC']).timestamp()
    def check():
        if sha(grant_path) != grant_sha or time.time() >= limit or (HERE / 'STOP_REQUESTED.json').exists() or any(Path(p).exists() for p in grant.get('root_stop_paths', [])):
            raise RuntimeError('EXP249_MODEL_GRANT_STOP_LEASE_OR_DRIFT')
        if sha(config_ref['path']) != config_ref['sha256']: raise RuntimeError('EXP249_LIVE_CONFIG_CHANGED')
    check()
    state_path = slot / 'DISPATCH_STATE.json'
    if state_path.exists():
        old = read(state_path)
        if old.get('status') == 'SETTLED_RESPONSE_SAVED' and old.get('body_SHA256') == digest(body):
            print(canonical({'status': 'ALREADY_SETTLED_NO_REPOST', 'task_id': ready['task_id'], 'trial_id': ready['trial_id']})); return
        raise RuntimeError('EXP249_INTENT_INFLIGHT_OR_UNKNOWN_NEVER_AUTO_RESEND')
    stripped = copy.deepcopy(body)
    stripped['messages'] = [m for m in stripped['messages'] if not str(m.get('content', '')).startswith(shared_input249.TAG)]
    if shared_input249.inject(stripped, config, ready['task_id']) != body:
        raise RuntimeError('EXP249_COMPLETE_COMMON_C0_REINJECTION_DRIFT')
    sys.path.insert(0, str(FIN)); transport = module('_exp249_original_continuous_transport', FIN / 'completion_transport_v3.py')
    env = types.SimpleNamespace(out=slot / 'new_generation', calls=ready['call_ordinal'], task_id=ready['task_id'], time_left=lambda: max(0, min(604800, limit - time.time())))
    state = {'schema': 'EXP249-single-request-durable-state/1', 'status': 'INTENT_PERSISTED_NO_RETRY',
             'method': ready['method'], 'task_id': ready['task_id'], 'trial_id': ready['trial_id'], 'call_ordinal': ready['call_ordinal'],
             'body_SHA256': digest(body), 'Root_grant_SHA256': grant_sha, 'original_trial_T0': t0,
             'lease_end_UTC': grant['lease_end_UTC'], 'full_peak_reserve_CNY': ready['full_peak_reserve_CNY']}
    class IO(transport.LegacyIO):
        def write_artifact(self, env, suffix, value, key): save(str(self.stem(env)) + suffix, self.clean(value, key))
        def request(self, env, role, body, bounds, key):
            check()
            if digest(body) != grant['body_SHA256']: raise RuntimeError('EXP249_ACTUAL_REQUEST_BODY_CHANGED')
            self.write_artifact(env, '_request.json', {'at_utc': now(), 'role': role, 'call_ordinal': env.calls,
                'body': body, 'body_SHA256': digest(body), 'bounds': bounds}, key)
        def post(self, body, key, timeout):
            check(); stamp = now()
            state.update(status='ACTUAL_POST_DISPATCH_INFLIGHT_NO_RESEND', post_dispatch_started_UTC=stamp)
            save(state_path, state)
            first = trial / 'FIRST_ACTUAL_POST_DISPATCH.json'
            if not first.exists():
                with first.open('x', encoding='utf-8') as stream:
                    json.dump({'at_UTC': stamp, 'task_id': ready['task_id'], 'trial_id': ready['trial_id'],
                        'body_SHA256': digest(body), 'original_trial_T0': t0, 'does_not_reset_preparation_clock': True}, stream, ensure_ascii=False)
                    stream.flush(); os.fsync(stream.fileno())
            return super().post(body, key, timeout)
        def raw_response(self, env, role, raw, key):
            self.write_artifact(env, '_http_response.json', raw, key)
            try: self.write_artifact(env, '_response.json', json.loads(raw['body_text']), key)
            except (ValueError, TypeError, KeyError): pass
        def receipt(self, env, receipt, key): self.write_artifact(env, '_finance_receipt.json', receipt, key)
        def error(self, env, role, error, key): self.write_artifact(env, '_error.json', error, key)
        def final_response(self, env, result, key): self.write_artifact(env, '_response.json', result, key)
    owner_path = slot / 'DISPATCH_OWNER_EXCLUSIVE.json'
    with owner_path.open('x', encoding='utf-8') as stream:
        json.dump({'pid': os.getpid(), 'at_UTC': now(), 'body_SHA256': digest(body), 'method': ready['method'],
                   'task_id': ready['task_id'], 'trial_id': ready['trial_id']}, stream, ensure_ascii=False)
        stream.flush(); os.fsync(stream.fileno())
    save(state_path, state)
    gate = transport.make_transport(config, IO())
    try:
        response = gate.generate(env, body, 'Exp249/' + ready['method'] + '/' + ready['task_id'] + '/' + ready['trial_id'] + '/' + ready['role'], ready['finance_phase'])
    except BaseException as exc:
        state.update(status='STOPPED_NO_RESEND_PENDING_EXACT_RECONCILIATION', error={'type': type(exc).__name__, 'message': str(exc)}, at_UTC=now())
        save(state_path, state); raise
    state.update(status='SETTLED_RESPONSE_SAVED', at_UTC=now(), response_SHA256=digest(response), usage=response['usage'])
    save(state_path, state)
    checkpoint = read(slot / 'checkpoint.json')
    checkpoint.update(status='SETTLED_MODEL_RESPONSE_PUBLIC_PROCESSING_PENDING', complete_response=response,
                      response_SHA256=digest(response), original_science_started=t0)
    checkpoint['cursor']['calls'] = ready['call_ordinal']; checkpoint['cursor']['output_tokens'] += response['usage']['completion_tokens']
    save(slot / 'checkpoint_after_model.json', checkpoint)
    print(canonical({'status': state['status'], 'method': ready['method'], 'task_id': ready['task_id'], 'trial_id': ready['trial_id'],
                     'call': ready['call_ordinal'], 'usage': response['usage'], 'native_private': 0}), flush=True)


if __name__ == '__main__': main()

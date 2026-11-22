"""Pure control/routing boundary checks; no actor, POST, native or private test."""
from common166 import *
import ast, copy, types
from publicpack_v2_224 import V
import main_environment_v2_224 as m
import main_identity_v2_224 as identity
from supervise_main_v2_224 import reviewed_wrapper_text
from budget_semantics224 import should_stop_queue


def check():
    pin = read(m.PIN); protocol = read(m.MAIN_PROTOCOL)
    assert sha(m.MAIN_PROTOCOL) == m.MAIN_PROTOCOL_SHA
    expected = [x for x in protocol['fixed_observation_mask23']['order'] if x not in protocol['calibration_ids_not_rerun']]
    assert expected == pin['task_order'] == protocol['execution_order_remaining21'] and len(expected) == 21
    assert expected[0] == 'Project-MONAI__MONAI-2238'
    for p, h in {**read(V / 'source_seal_v2.json')['sealed_files'], **pin['new_sources'], **pin['read_only_inputs']}.items(): assert sha(p) == h
    path, source = reviewed_wrapper_text(); tree = ast.parse(source)
    run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run')
    saves = [n.lineno for n in ast.walk(run) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'save'
             and any(isinstance(v, ast.Constant) and v.value == 'RUNNING' for v in ast.walk(n))]
    resumes = [n.lineno for n in ast.walk(run) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'NtResumeProcess']
    assert min(saves) < min(resumes), 'RUNNING_MUST_PRECEDE_RESUME'
    original_identity = (identity.os, identity.current_birth, identity.actual_parent_pid, identity.pid_birth)
    identity.os = types.SimpleNamespace(getpid=lambda: 55); identity.current_birth = lambda: 700
    identity.actual_parent_pid = lambda: 44; identity.pid_birth = lambda pid: 400
    supervisor = {'status': 'RUNNING', 'job_kill_on_close': True, 'suspended_until_assigned_to_job': True,
                  'runner_pid': 44, 'runner_creation_time100ns': 400}
    assert identity.verify_worker(supervisor)['actual_self_PID'] == 55
    identity.actual_parent_pid = lambda: 43
    try: identity.verify_worker(supervisor)
    except AssertionError: pass
    else: raise AssertionError('WRONG_REDIRECT_PARENT_ALLOWED')
    identity.actual_parent_pid = lambda: 44
    assert identity.verify_worker({**supervisor, 'runner_pid': 55, 'runner_creation_time100ns': 700})['logical_launcher_PID'] == 55
    identity.os, identity.current_birth, identity.actual_parent_pid, identity.pid_birth = original_identity
    real_read, real_grant = m.read, m.GRANT
    class FakeGrant:
        def exists(self): return True
    fake = FakeGrant(); m.GRANT = fake
    grant = {'root_authorized': True, 'version': m.MAIN_VERSION, 'phase': 'Round2320Main',
             'main_source_pin_sha256': sha(m.PIN), 'source_seal_sha256': m.PARENT, 'pack_registry_sha256': m.PACK,
             'root_main_protocol_sha256': m.MAIN_PROTOCOL_SHA, 'max_lead_cases': 1, 'allowed_through_index': 0}
    runtime = {'root_runtime_ready': True, 'comparison_version': m.MAIN_VERSION, 'root_main_protocol_sha256': m.MAIN_PROTOCOL_SHA}
    runtime_path = ROOT / '工作区/1008-2320-baseline-main/coordination/runtime_release.json'
    m.read = lambda p: grant if p is fake else runtime if Path(p) == runtime_path else real_read(p)
    assert m.authorize_main()['version'] == m.MAIN_VERSION
    grant['allowed_through_index'] = 1
    try: m.authorize_main()
    except AssertionError as e: assert 'MAIN_BIG_QUEUE_REQUIRES_ACTUAL_V2_ENAGENT' in str(e)
    else: raise AssertionError('UNQUALIFIED_BIG_QUEUE_ALLOWED')
    grant['allowed_through_index'] = 0; grant['phase'] = 'Round2320Pilot'
    try: m.authorize_main()
    except AssertionError: pass
    else: raise AssertionError('PILOT_GRANT_BORROWED_FOR_MAIN')
    m.read, m.GRANT = real_read, real_grant
    calls = []
    class FakeTransport:
        def generate(self, env, body, role, phase): calls.append((body, role, phase)); return {'routing_only': True}
    class Recorder:
        def record(self, *a): pass
    old_module, old_auth = m._original_module, m.authorize_main
    m._original_module = lambda name, path: FakeTransport(); m.authorize_main = lambda: None
    body = {'seed': 17, 'messages': [{'role': 'user', 'content': 'pure routing input'}]}
    m.routed_module('pure', TRANSPORT).generate(Recorder(), body, 'original-role', phase='Round2320Pilot')
    assert calls == [(body, 'original-role', 'Round2320Main')] and calls[0][0] is body
    m._original_module, m.authorize_main = old_module, old_auth
    class ClosedRecorder:
        finance_fatal = None
        def budget_context(self):
            return {'finance_fatal': None, 'global_cutoff': False, 'wall_limited_by_global': False,
                    'search_wall_exhausted': False, 'full_wall_exhausted': False}
        def closed_result(self, result, disposition):
            return {**result, **disposition, 'hidden_acceptance_calls': 0}
    normal = m.MainEnvironmentV2.finalize(ClosedRecorder(), {'status': 'MODEL_SEMANTIC_FAILURE',
             'declared_method_failure_known': True, 'runtime_core': {'complete': False}, 'final_snapshot': {'diff': {}}})
    unknown = m.MainEnvironmentV2.finalize(ClosedRecorder(), {'status': 'UNRECOGNIZED_INCOMPLETE',
              'runtime_core': {'complete': False}, 'final_snapshot': {'diff': {}}})
    assert normal['success'] is False and normal['hidden_acceptance_calls'] == 0 and not should_stop_queue(normal)
    assert unknown['success'] is None and unknown['hidden_acceptance_calls'] == 0 and should_stop_queue(unknown)
    result = {'status': 'PASS', 'Main_version': m.MAIN_VERSION, 'main_source_pin_sha256': sha(m.PIN),
              'root_main_protocol_sha256': m.MAIN_PROTOCOL_SHA, 'remaining21_order_exact': True,
              'calibration_replay_forbidden': True, 'RUNNING_before_resume': True,
              'direct_and_redirect_birth_branches': True, 'wrong_parent_rejected': True,
              'first_only_admission_without_external_V2_nonzero': True, 'unqualified_big_queue_blocked': True,
              'Pilot_grant_cannot_route_Main': True, 'actual_delegate_phase_Main_body_role_seed_unchanged': True,
              'normal_terminal_advances_unknown_stops_without_private': True,
              'parent129_source_and_peer_seal_unchanged': True, 'actors_constructed': 0,
              'new_model_POST_native_private_Gold': 0}
    save(V / 'main21_pure_checks_v2.json', result)
    print(canonical(result))


if __name__ == '__main__': check()

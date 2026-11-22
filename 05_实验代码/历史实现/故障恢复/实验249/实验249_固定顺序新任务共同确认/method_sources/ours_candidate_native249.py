"""One exact candidate G/O run using the Root-qualified EXP249 native boundary.

No model/provider/finance/private API. The method receives original public G/O
only after the complete parent STOP. All candidate bytes are immutable inputs.
"""
import argparse
import ctypes
import subprocess
import types
from trial_runtime249 import *

ROOT_NATIVE = E249 / 'native249_ROOT_MASK_V3_CAPACITY.py'


class NativeGrant:
    def __init__(self, path, ready_path):
        self.path = Path(path).resolve(); self.sha256 = sha(self.path); self.value = read(self.path)
        self.ready_path = Path(ready_path).resolve(); self.ready = read(self.ready_path)
        self.check(full=True)

    def check(self, full=False):
        g = self.value; ready = self.ready
        if sha(self.path) != self.sha256 or g.get('root_authorized') is not True or g.get('native_authorized') is not True:
            raise RuntimeError('EXP249_CANDIDATE_NATIVE_GRANT_CLOSED_OR_CHANGED')
        if any(g.get(k) is not False for k in ('model_authorized', 'private_authorized', 'finance_authorized')):
            raise RuntimeError('EXP249_CANDIDATE_NATIVE_ONLY')
        if g.get('maximum_new_original_G_O_native') != 1 or g.get('ready_SHA256') != sha(self.ready_path):
            raise RuntimeError('EXP249_EXACT_CANDIDATE_NATIVE_READY_REQUIRED')
        if any(g.get(k) != ready[k] for k in ('method', 'task_id', 'trial_id', 'attempt')):
            raise RuntimeError('EXP249_CANDIDATE_TASK_TRIAL_ATTEMPT_MISMATCH')
        if g.get('candidate_source_inventory_SHA256') != digest(ready['candidate_source_sha256']):
            raise RuntimeError('EXP249_CANDIDATE_SOURCE_INVENTORY_MISMATCH')
        if time.time() >= datetime.datetime.fromisoformat(g['lease_end_UTC']).timestamp() or (HERE / 'STOP_REQUESTED.json').exists() or any(Path(p).exists() for p in g.get('root_stop_paths', [])):
            raise RuntimeError('EXP249_CANDIDATE_NATIVE_STOP_OR_LEASE')
        if not self.ready_path.is_relative_to(HERE / 'runs/OURS248_FULL'):
            raise RuntimeError('EXP249_CANDIDATE_NATIVE_OUTPUT_SCOPE')
        if full:
            spec = g['native_source_seal']
            if sha(spec['path']) != spec['sha256']: raise RuntimeError('EXP249_NATIVE_SOURCE_SEAL_DRIFT')
            verify_source_seal(spec['path'])
            for ref in (ready['public_contract'], ready['public_test_scope_contract'], g['qualified_runtime_policy'], g['current_identity_receipt']):
                if sha(ref['path']) != ref['sha256']: raise RuntimeError('EXP249_NATIVE_BOUND_RUNTIME_OR_PUBLIC_INPUT_DRIFT')
        return True


def helper():
    sys.path.insert(0, str(E249))
    return module('_exp249_actual_Root_native_boundary', ROOT_NATIVE)


def supervise(grant, h, jobs):
    ready = grant.ready; out = Path(ready['native_output']).resolve()
    if out != grant.ready_path.parent or not out.is_relative_to(HERE / 'runs/OURS248_FULL'):
        raise RuntimeError('EXP249_CANDIDATE_OUTPUT_BINDING')
    started = out / 'SUPERVISOR_STARTED_ONCE.json'
    if started.exists() or (out / 'NATIVE_INTENT.json').exists() or (out / 'COMPLETED_PUBLIC.json').exists():
        raise RuntimeError('EXP249_NATIVE_STARTED_UNKNOWN_OR_COMPLETED_NO_RETRY')
    name = grant.value['parent_owned_job_name']
    if not name.startswith('RootExp249_Candidate_'): raise RuntimeError('EXP249_CANDIDATE_PARENT_JOB_NAMESPACE')
    python = Path(grant.value['controller_launch_python']).resolve()
    if python != (ROOT / '工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe').resolve() or sha(python) != grant.value['controller_launch_SHA256']:
        raise RuntimeError('EXP249_WORKING_CONTROLLER_BINDING')
    argv = [str(python), '-X', 'utf8', '-B', str(Path(__file__).resolve()), '--ready', str(grant.ready_path), '--root-grant', str(grant.path), '--worker']
    with started.open('x', encoding='utf-8') as stream:
        json.dump({'UTC': now(), 'argv': argv, 'Root_grant_SHA256': grant.sha256, 'specific_parent_Job': name}, stream, ensure_ascii=False)
        stream.flush(); os.fsync(stream.fileno())
    k = jobs.api(); job = jobs.checked(k.CreateJobObjectW(None, name), 'EXP249_CANDIDATE_PARENT_JOB_CREATE')
    limits = jobs.Extended(); limits.BasicLimitInformation.LimitFlags = 0x2000
    jobs.checked(k.SetInformationJobObject(job, 9, ctypes.byref(limits), ctypes.sizeof(limits)), 'EXP249_CANDIDATE_PARENT_KILL_ON_CLOSE')
    process = None; assigned = False; birth = None; error = None; code = None; stop = None
    child = {key: os.environ[key] for key in ('SystemRoot', 'WINDIR', 'SYSTEMDRIVE', 'PATH', 'TEMP', 'TMP', 'USERPROFILE', 'LOCALAPPDATA') if key in os.environ}
    child.update(PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', EXP249_PARENT_JOB=name)
    try:
        with (out / 'worker.log').open('xb') as log:
            process = subprocess.Popen(argv, cwd=str(HERE), env=child, stdout=log, stderr=subprocess.STDOUT, creationflags=0x08000000 | 4)
            held = jobs.wintypes.HANDLE(int(process._handle)); birth = jobs.held_identity(k, held)
            if birth['pid'] != process.pid or Path(birth['actual_OS_image']).resolve() != python:
                raise RuntimeError('EXP249_CANDIDATE_HELD_CONTROLLER_IDENTITY')
            jobs.checked(k.AssignProcessToJobObject(job, held), 'EXP249_CANDIDATE_PARENT_ASSIGN')
            assigned = jobs.membership(k, held, job)
            if not assigned or jobs.accounting(k, job)['active_processes'] != 1: raise RuntimeError('EXP249_CANDIDATE_PARENT_MEMBERSHIP')
            save(out / 'PARENT_HELD_BIRTH.json', {'identity': birth, 'assigned_before_resume': True, 'specific_parent_Job': name})
            ntdll = ctypes.WinDLL('ntdll'); ntdll.NtResumeProcess.argtypes = [jobs.wintypes.HANDLE]; ntdll.NtResumeProcess.restype = ctypes.c_long
            if ntdll.NtResumeProcess(held) != 0: raise RuntimeError('EXP249_CANDIDATE_WORKER_RESUME')
            while process.poll() is None:
                grant.check(); accounting = jobs.accounting(k, job)
                if accounting['active_processes'] > 8 or accounting['total_processes'] > 24:
                    raise RuntimeError('EXP249_CANDIDATE_OWNED_PROCESS_CAP')
                time.sleep(.2)
            code = process.wait(timeout=10)
    except BaseException as exc:
        error = {'type': type(exc).__name__, 'message': str(exc)}
    finally:
        try: stop = jobs.stop_owned(k, job, process, assigned); job = None
        except BaseException as exc: stop = {'all_owned_descendants_terminated': None, 'STOP_error': str(exc)}
        if job: k.CloseHandle(job)
    parent_path = out / 'PARENT_TERMINAL249.json'
    save(parent_path, {'UTC': now(), 'task_id': ready['task_id'], 'trial_id': ready['trial_id'], 'attempt': ready['attempt'],
         'exit_code': code, 'error': error, 'held_launcher': birth, 'stop_receipt': stop, 'Root_grant_SHA256': grant.sha256,
         'method_native_calls': 1, 'model_private_finance': 0})
    if error or code != 0 or stop.get('all_owned_descendants_terminated') is not True:
        raise RuntimeError('EXP249_CANDIDATE_NATIVE_PARENT_UNKNOWN')
    result = read(out / 'WORKER_COMPLETED_PUBLIC.json')
    result.update(parent_supervision_path=str(parent_path), parent_supervision_SHA256=sha(parent_path))
    save(out / 'COMPLETED_PUBLIC.json', result)
    print(canonical({'status': 'EXACT_PUBLIC_G_O_COMPLETED_AND_PARENT_STOPPED', 'task_id': ready['task_id'],
                     'trial_id': ready['trial_id'], 'attempt': ready['attempt'], 'complete': str(out / 'COMPLETED_PUBLIC.json')}), flush=True)


def worker(grant, h, jobs):
    ready = grant.ready; out = Path(ready['native_output']).resolve()
    if not h.parent_member(jobs, grant.value['parent_owned_job_name']): raise RuntimeError('EXP249_CANDIDATE_WORKER_NOT_IN_PARENT_JOB')
    with (out / 'NATIVE_INTENT.json').open('x', encoding='utf-8') as stream:
        json.dump({'UTC': now(), 'Root_grant_SHA256': grant.sha256, 'candidate_inventory': ready['candidate_source_inventory_SHA256'] if 'candidate_source_inventory_SHA256' in ready else digest(ready['candidate_source_sha256'])}, stream)
        stream.flush(); os.fsync(stream.fileno())
    c = read(ready['public_contract']['path']); runtime = read(grant.value['current_identity_receipt']['path'])
    expected = runtime['product_identity']; python = Path(c['logical_product_python']).resolve()
    if (sha(python) != runtime['logical_product_python_SHA256'] or sha(python.parent.parent / 'pyvenv.cfg') != runtime['pyvenv_cfg_SHA256']
            or sha(expected['actual_OS_image']) != expected['actual_OS_image_SHA256']):
        raise RuntimeError('EXP249_CANDIDATE_QUALIFIED_RUNTIME_CHANGED')
    policy = read(grant.value['qualified_runtime_policy']['path'])
    for key in ('current_process_clock_policy', 'common_precise_clock_contract', 'Root_current_process_precise_clock_admitted'):
        if grant.value.get(key) != policy.get(key): raise RuntimeError('EXP249_CANDIDATE_RUNTIME_POLICY_DIFFERS_FROM_CURRENT_C0')
    source_path = Path(ready['business_source_file']).resolve()
    if not source_path.is_relative_to(HERE / 'runs/OURS248_FULL') or sha(source_path) != ready['business_source_file_SHA256']:
        raise RuntimeError('EXP249_CANDIDATE_SOURCE_ARTIFACT_DRIFT')
    source = read(source_path); hashes = {p: hashlib.sha256(t.encode()).hexdigest() for p, t in source.items()}
    if hashes != ready['candidate_source_sha256'] or set(hashes) != set(c['c0_business_paths_sha256']):
        raise RuntimeError('EXP249_CANDIDATE_LEGAL_BUSINESS_SCOPE_DRIFT')
    scope_ref = ready['public_test_scope_contract']
    p = {'task_order': read(E249 / 'protocol249_SOURCE.json')['task_order'], 'public_test_scope_contract': scope_ref}
    masked = module('_exp249_candidate_v14', ROOT / '工作区/1010-unified-six/shared_native_v14_certificate_complete/native_masked_public239.py')
    scope = masked.load_scope(p, ready['task_id'])
    active = out / 'runtime'; repo = active / 'repo'; repo.mkdir(parents=True, exist_ok=False)
    for rel, text in source.items():
        path = repo / rel
        if not path.resolve().is_relative_to(repo.resolve()) or not rel.endswith('.py') or any(x in ('test', 'tests', '.git') for x in Path(rel).parts):
            raise RuntimeError('EXP249_CANDIDATE_NONBUSINESS_PATH')
        path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(text.encode())
    supports = masked.materialize_support(repo, scope, hashes); masked.verify_actor(repo, hashes, supports)
    if digest({**hashes, **supports}) != ready['candidate_snapshot']['inventory_sha256']:
        raise RuntimeError('EXP249_CANDIDATE_MATERIALIZATION_SNAPSHOT_MISMATCH')
    run = h.load_original_probe(c); events = []
    env = types.SimpleNamespace(run=run, package=c['package'], record=lambda stage, value: events.append({'stage': stage, 'value': value}))
    jobs.install(env); jobs.MAX_PRODUCT_NATIVE_ROOTS = 1
    capacity = module('_exp249_candidate_original_capacity', OLD / 'native_capacity_v10.py'); capacity.NATIVE_TIMEOUT_SECONDS = 300; capacity.install(env)
    execute = run.qualify.execute
    def measured(argv, cwd, log, timeout=300, env=None):
        receipt = Path(log).with_name('ACTUAL_PRODUCT_SELF249.json')
        actual = h.wrap_native_argv(argv, receipt, grant, expected['actual_OS_image'])
        result = execute(actual, cwd, log, timeout, env)
        result['actual_product_identity'] = h.verify_measured_identity(result, receipt, expected, grant)
        result['actual_product_identity_SHA256'] = sha(receipt); result['original_semantic_argv'] = list(map(str, argv))
        return result
    run.qualify.execute = measured
    nodes = list(dict.fromkeys(ready['goal_nodes'] + ready['ordinary_nodes']))
    if nodes != list(dict.fromkeys(c['public_target_nodes'] + c['ordinary_nodes'])) or grant.value.get('exact_G_O_nodes') != nodes:
        raise RuntimeError('EXP249_CANDIDATE_EXACT_ORIGINAL_G_O_REQUIRED')
    scheduler = module('_exp249_candidate_four_slots', ROOT / '工作区/1010-unified-six/native_four_slots_v5_SOURCE.py')
    schedule = read(ROOT / '工作区/1010-unified-six/ROOT_COMMON_NATIVE_SCHEDULING_V5_FOUR_SOURCE.json')
    with scheduler.native_lane(schedule['lock_path'], c['package'], grant.check, lambda value: events.append({'stage': 'V5_four_slots', 'value': value})):
        grant.check(full=True)
        remaining = datetime.datetime.fromisoformat(grant.value['lease_end_UTC']).timestamp() - time.time()
        result = run.probe(active, Path(c['frozen_public_test_root']), nodes, out / 'actual_G_O', python, c['package'], time.monotonic() + min(300, max(.1, remaining)))
    guard = module('_exp249_candidate_original_guard', OLD / 'progress_guard240.py')
    value = guard.observe({'native_record': result, 'outcomes': {n: result['pytest']['outcomes'][n] for n in ready['ordinary_nodes']}}, ready['goal_nodes'], ready['ordinary_nodes'])
    masked.verify_actor(repo, hashes, supports)
    if {p: sha(repo / p) for p in hashes} != hashes: raise RuntimeError('EXP249_NATIVE_CHANGED_CANDIDATE')
    save(out / 'NATIVE_TRANSPORT_EVIDENCE.json', events)
    save(out / 'WORKER_COMPLETED_PUBLIC.json', {'task_id': ready['task_id'], 'trial_id': ready['trial_id'], 'attempt': ready['attempt'],
         'candidate_snapshot': ready['candidate_snapshot'], 'candidate_source_sha256': hashes,
         'public_native_path': str(out / 'actual_G_O/run.json'), 'public_native_SHA256': sha(out / 'actual_G_O/run.json'),
         'ordinary_all_pass': value['ordinary_pass'], 'goal_actual_pass': sorted(value['goal_pass']), 'failed_goals': value['failed_goals'],
         'one_original_G_O_native': True, 'masked_placeholder_not_executed_as_Goal': True,
         'Root_grant_SHA256': grant.sha256, 'model_private_finance': 0})


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--ready', required=True); parser.add_argument('--root-grant', required=True); parser.add_argument('--worker', action='store_true')
    args = parser.parse_args(); grant = NativeGrant(args.root_grant, args.ready); h = helper(); jobs = h.load_jobs(grant)
    if args.worker: worker(grant, h, jobs)
    else: supervise(grant, h, jobs)


if __name__ == '__main__': main()

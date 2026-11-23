"""Root-granted identity only; zero business imports or tests.

Current C0 and masking remain closed pending separate source qualification.
"""
import argparse
import ctypes
import subprocess
import types
from common_next_six249 import *

def load_jobs(grant):
    # Bind the original executor's common interface to this experiment only.
    bridge = types.ModuleType('common166')
    values = dict(Path=Path, json=json, os=os, sys=sys, time=time, ROOT=R, E=E,
                  save=save, read=read, sha=sha, now=now, canonical=canonical,
                  authorization=grant.check, MAX_ALL_OS_ROOTS=8,
                  MAX_PRODUCT_NATIVE_ROOTS=2, NATIVE_TIMEOUT_SECONDS=300)
    bridge.__dict__.update(values)
    sys.modules['common166'] = bridge
    jobs = module('_exp249_original_native_executor', OLD / 'native_executor242_prospective.py')
    jobs.OS_ROOT_RESERVATIONS = 2
    jobs.PRODUCT_ROOT_RESERVATIONS = 0
    return jobs

def stopped(value):
    result = value.get('stop_receipt', {})
    observations = result.get('actual_job_accounting_observations', [])
    return (value.get('native_failure') is None and value.get('root_PID_birth_verified') is True
            and value.get('root_resumed') is True and value.get('specific_Job_membership_observed') is True
            and all(result.get(k) is True for k in ('owned_job_closed', 'root_process_stopped', 'all_owned_descendants_terminated'))
            and result.get('job_active_processes_after_termination') == 0
            and observations and observations[-1].get('active_processes') == 0)

def parent_member(jobs, name):
    k = jobs.api()
    k.OpenJobObjectW.argtypes = [jobs.wintypes.DWORD, jobs.wintypes.BOOL, jobs.wintypes.LPCWSTR]
    k.OpenJobObjectW.restype = jobs.wintypes.HANDLE
    k.GetCurrentProcess.argtypes = []; k.GetCurrentProcess.restype = jobs.wintypes.HANDLE
    handle = k.OpenJobObjectW(4, False, name)
    if not handle:
        return False
    try:
        return jobs.membership(k, k.GetCurrentProcess(), handle)
    finally:
        k.CloseHandle(handle)

def supervise(args, grant, out, jobs):
    if out.exists():
        raise RuntimeError('EXP249_STAGE_ALREADY_STARTED_NO_AUTO_RERUN')
    out.mkdir(parents=True)
    name = grant.value.get('parent_owned_job_name')
    if not isinstance(name, str) or not name.startswith('RootExp249_'):
        raise RuntimeError('EXP249_EXACT_PARENT_JOB_NAME_REQUIRED')
    python = Path(grant.value.get('controller_launch_python', '')).resolve()
    if python != CONTROLLER.resolve() or sha(python) != grant.value.get('controller_launch_SHA256'):
        raise RuntimeError('EXP249_VERIFIED_WORKING_CONTROLLER_LAUNCHER_REQUIRED')
    argv = [str(python), '-X', 'utf8', '-B', str(Path(__file__).resolve()),
            '--stage', args.stage, '--task', args.task, '--root-grant', str(grant.path), '--worker']
    intent(out / 'SUPERVISOR_STARTED_ONCE.json', {'UTC': now(), 'argv': argv, 'Root_grant_SHA256': grant.sha256,
           'logical_launcher_not_claimed_physical_runtime': True, 'specific_parent_Job': name})
    k = jobs.api()
    job = jobs.checked(k.CreateJobObjectW(None, name), 'EXP249_PARENT_JOB_CREATE')
    limits = jobs.Extended(); limits.BasicLimitInformation.LimitFlags = 0x2000
    jobs.checked(k.SetInformationJobObject(job, 9, ctypes.byref(limits), ctypes.sizeof(limits)), 'EXP249_PARENT_KILL_ON_CLOSE')
    process = None; assigned = False; identity = None; code = None; error = None; stop = None
    child_env = {key: os.environ[key] for key in ('SystemRoot', 'WINDIR', 'SYSTEMDRIVE', 'PATH', 'TEMP', 'TMP', 'USERPROFILE', 'LOCALAPPDATA') if key in os.environ}
    child_env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', EXP249_PARENT_JOB=name)
    try:
        with (out / 'worker.log').open('xb') as log:
            process = subprocess.Popen(argv, cwd=str(E), env=child_env, stdout=log, stderr=subprocess.STDOUT,
                                       creationflags=0x08000000 | 0x00000004)
            held = jobs.wintypes.HANDLE(int(process._handle))
            identity = jobs.held_identity(k, held)
            if Path(identity['actual_OS_image']).resolve() != python or identity['pid'] != process.pid:
                raise RuntimeError('EXP249_HELD_CONTROLLER_LAUNCHER_IDENTITY_MISMATCH')
            jobs.checked(k.AssignProcessToJobObject(job, held), 'EXP249_PARENT_ASSIGN')
            assigned = jobs.membership(k, held, job)
            if not assigned or jobs.accounting(k, job)['active_processes'] != 1:
                raise RuntimeError('EXP249_PARENT_MEMBERSHIP_BEFORE_RESUME_UNKNOWN')
            save(out / 'PARENT_HELD_BIRTH.json', {'identity': identity, 'specific_parent_Job': name,
                 'assigned_before_resume': True, 'logical_launcher_identity_only': True})
            ntdll = ctypes.WinDLL('ntdll')
            ntdll.NtResumeProcess.argtypes = [jobs.wintypes.HANDLE]; ntdll.NtResumeProcess.restype = ctypes.c_long
            if ntdll.NtResumeProcess(held) != 0:
                raise RuntimeError('EXP249_WORKER_RESUME_FAILED')
            while process.poll() is None:
                grant.check()
                accounting = jobs.accounting(k, job)
                if accounting['active_processes'] > 8 or accounting['total_processes'] > 24:
                    raise RuntimeError('EXP249_PARENT_ACTIVE8_OR_TOTAL24_PROCESS_COUNT_CAP')
                time.sleep(.2)
            code = process.wait(timeout=10)
    except BaseException as exc:
        error = {'type': type(exc).__name__, 'message': str(exc)}
    finally:
        try:
            stop = jobs.stop_owned(k, job, process, assigned); job = None
        except BaseException as exc:
            stop = {'all_owned_descendants_terminated': None, 'STOP_error': str(exc)}
        if job:
            k.CloseHandle(job)
    save(out / 'PARENT_TERMINAL249.json', {'UTC': now(), 'task_id': args.task, 'stage': args.stage,
         'exit_code': code, 'error': error, 'held_launcher': identity, 'stop_receipt': stop,
         'Root_grant_SHA256': grant.sha256, 'outcome_not_inferred_from_STOP': True,
         'model_calls': 0, 'private_calls': 0, 'finance_writes': 0})
    if error or code != 0 or stop.get('all_owned_descendants_terminated') is not True:
        raise RuntimeError('EXP249_STAGE_PARENT_UNKNOWN_PRESERVE_PARTIAL')
    print(canonical({'status': 'ZERO_MODEL_STAGE_RETURNED_AND_STOPPED', 'task_id': args.task,
                     'stage': args.stage, 'output': str(out)}), flush=True)

def run_identity(args, grant, out, jobs, row, c):
    if grant.value.get('max_identity_OS_roots') != 1:
        raise RuntimeError('EXP249_ONE_IDENTITY_ROOT_REQUIRED')
    python = Path(c['logical_product_python']).resolve()
    product = out / 'product'; product.mkdir()
    argv = [str(python), '-S', '-B', str(E / 'physical_identity249.py')]
    scheduler = module('_exp249_four_slots', COMMON / 'native_four_slots_v5_SOURCE.py')
    scheduling = read(COMMON / 'ROOT_COMMON_NATIVE_SCHEDULING_V5_FOUR_SOURCE.json')
    events = []
    with scheduler.native_lane(scheduling['lock_path'], c['package'], grant.check, events.append):
        grant.check(full=True)
        value = jobs.execute(argv, E, product / 'identity.log', timeout=30, product_native=False)
    if value.get('exit_code') != 0 or value.get('timeout') or not stopped(value):
        raise RuntimeError('EXP249_PHYSICAL_IDENTITY_PROBE_UNKNOWN')
    identity = json.loads(value['stdout'].strip())
    if (identity.get('specific_named_Job_membership') is not True
            or identity['specific_job_name'] != value['stop_receipt']['specific_job_name']
            or identity.get('product_imports_or_tests') != 0):
        raise RuntimeError('EXP249_PHYSICAL_SELF_NOT_OWNED_ZERO_PRODUCT')
    save(out / 'COMPLETED_IDENTITY249.json', {'UTC': now(), 'task_id': args.task,
         'logical_product_python': str(python), 'logical_product_python_SHA256': sha(python),
         'pyvenv_cfg_SHA256': sha(python.parent.parent / 'pyvenv.cfg'),
         'product_identity': identity, 'process_observation': value,
         'controller_self_identity': read(out / 'CONTROLLER_SELF_IDENTITY.json'),
         'scheduler_events': events, 'Root_grant_SHA256': grant.sha256,
         'fresh_current_identity_only_not_G_O_qualification': True, 'model_native_tests_private_finance': 0})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=('identity',), required=True)
    parser.add_argument('--task', choices=TASKS, required=True)
    parser.add_argument('--root-grant', required=True)
    parser.add_argument('--worker', action='store_true')
    args = parser.parse_args()
    grant = Grant(args.root_grant, 'identity', [args.task])
    if grant.value.get('identity_entry_SHA256') != sha(__file__):
        raise RuntimeError('NEXT_SIX_IDENTITY_ENTRY_NOT_EXACTLY_BOUND')
    jobs = load_jobs(grant)
    out = E / 'qualification' / args.task / 'identity'
    if not args.worker:
        return supervise(args, grant, out, jobs)
    if not parent_member(jobs, grant.value['parent_owned_job_name']):
        raise RuntimeError('NEXT_SIX_WORKER_NOT_IN_EXACT_PARENT_JOB')
    identity = module('_next_six_controller_identity', E / 'physical_identity249.py')
    save(out / 'CONTROLLER_SELF_IDENTITY.json', identity.capture())
    row, contract = binding(args.task)
    intent(out / 'WORKER_STARTED_ONCE.json', {'UTC': now(), 'stage': 'identity', 'Root_grant_SHA256': grant.sha256})
    run_identity(args, grant, out, jobs, row, contract)


if __name__ == '__main__': main()

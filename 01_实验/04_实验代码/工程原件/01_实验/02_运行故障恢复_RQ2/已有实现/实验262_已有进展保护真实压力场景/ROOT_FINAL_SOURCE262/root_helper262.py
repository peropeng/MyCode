"""Original held Jobs/probe/identity helper; E=output, IDENTITY_SOURCE=code."""
import argparse,contextlib,ctypes,subprocess
from final_common262 import *
def load_jobs(grant):
    bridge = types.ModuleType('common166')
    values = dict(Path=Path, json=json, os=os, sys=sys, time=time, ROOT=R, E=E, save=save, read=read, sha=sha, now=now, canonical=canonical, authorization=grant.check, MAX_ALL_OS_ROOTS=8, MAX_PRODUCT_NATIVE_ROOTS=2, NATIVE_TIMEOUT_SECONDS=300)
    bridge.__dict__.update(values)
    sys.modules['common166'] = bridge
    jobs = module('_exp249_original_native_executor', OLD / 'native_executor242_prospective.py')
    jobs.OS_ROOT_RESERVATIONS = 2
    jobs.PRODUCT_ROOT_RESERVATIONS = 0
    return jobs

def stopped(value):
    result = value.get('stop_receipt', {})
    observations = result.get('actual_job_accounting_observations', [])
    return value.get('native_failure') is None and value.get('root_PID_birth_verified') is True and (value.get('root_resumed') is True) and (value.get('specific_Job_membership_observed') is True) and all((result.get(k) is True for k in ('owned_job_closed', 'root_process_stopped', 'all_owned_descendants_terminated'))) and (result.get('job_active_processes_after_termination') == 0) and observations and (observations[-1].get('active_processes') == 0)

def parent_member(jobs, name):
    k = jobs.api()
    k.OpenJobObjectW.argtypes = [jobs.wintypes.DWORD, jobs.wintypes.BOOL, jobs.wintypes.LPCWSTR]
    k.OpenJobObjectW.restype = jobs.wintypes.HANDLE
    k.GetCurrentProcess.argtypes = []
    k.GetCurrentProcess.restype = jobs.wintypes.HANDLE
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
    argv = [str(python), '-X', 'utf8', '-B', str(FINAL_WORKER_SOURCE), '--stage', args.stage, '--task', args.task, '--root-grant', str(grant.path), '--worker']
    intent(out / 'SUPERVISOR_STARTED_ONCE.json', {'UTC': now(), 'argv': argv, 'Root_grant_SHA256': grant.sha256, 'logical_launcher_not_claimed_physical_runtime': True, 'specific_parent_Job': name})
    k = jobs.api()
    job = jobs.checked(k.CreateJobObjectW(None, name), 'EXP249_PARENT_JOB_CREATE')
    limits = jobs.Extended()
    limits.BasicLimitInformation.LimitFlags = 8192
    jobs.checked(k.SetInformationJobObject(job, 9, ctypes.byref(limits), ctypes.sizeof(limits)), 'EXP249_PARENT_KILL_ON_CLOSE')
    process = None
    assigned = False
    identity = None
    code = None
    error = None
    stop = None
    child_env = {key: os.environ[key] for key in ('SystemRoot', 'WINDIR', 'SYSTEMDRIVE', 'PATH', 'TEMP', 'TMP', 'USERPROFILE', 'LOCALAPPDATA') if key in os.environ}
    child_env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', EXP249_PARENT_JOB=name)
    try:
        with (out / 'worker.log').open('xb') as log:
            process = subprocess.Popen(argv, cwd=str(E), env=child_env, stdout=log, stderr=subprocess.STDOUT, creationflags=134217728 | 4)
            held = jobs.wintypes.HANDLE(int(process._handle))
            identity = jobs.held_identity(k, held)
            if Path(identity['actual_OS_image']).resolve() != python or identity['pid'] != process.pid:
                raise RuntimeError('EXP249_HELD_CONTROLLER_LAUNCHER_IDENTITY_MISMATCH')
            jobs.checked(k.AssignProcessToJobObject(job, held), 'EXP249_PARENT_ASSIGN')
            assigned = jobs.membership(k, held, job)
            if not assigned or jobs.accounting(k, job)['active_processes'] != 1:
                raise RuntimeError('EXP249_PARENT_MEMBERSHIP_BEFORE_RESUME_UNKNOWN')
            save(out / 'PARENT_HELD_BIRTH.json', {'identity': identity, 'specific_parent_Job': name, 'assigned_before_resume': True, 'logical_launcher_identity_only': True})
            ntdll = ctypes.WinDLL('ntdll')
            ntdll.NtResumeProcess.argtypes = [jobs.wintypes.HANDLE]
            ntdll.NtResumeProcess.restype = ctypes.c_long
            if ntdll.NtResumeProcess(held) != 0:
                raise RuntimeError('EXP249_WORKER_RESUME_FAILED')
            while process.poll() is None:
                grant.check()
                accounting = jobs.accounting(k, job)
                if accounting['active_processes'] > 8 or accounting['total_processes'] > 24:
                    raise RuntimeError('EXP249_PARENT_ACTIVE8_OR_TOTAL24_PROCESS_COUNT_CAP')
                time.sleep(0.2)
            code = process.wait(timeout=10)
    except BaseException as exc:
        error = {'type': type(exc).__name__, 'message': str(exc)}
    finally:
        try:
            stop = jobs.stop_owned(k, job, process, assigned)
            job = None
        except BaseException as exc:
            stop = {'all_owned_descendants_terminated': None, 'STOP_error': str(exc)}
        if job:
            k.CloseHandle(job)
    save(out / 'PARENT_TERMINAL249.json', {'UTC': now(), 'task_id': args.task, 'stage': args.stage, 'exit_code': code, 'error': error, 'held_launcher': identity, 'stop_receipt': stop, 'Root_grant_SHA256': grant.sha256, 'outcome_not_inferred_from_STOP': True, 'model_calls': 0, 'private_calls': 0, 'finance_writes': 0})
    if error or code != 0 or stop.get('all_owned_descendants_terminated') is not True:
        raise RuntimeError('EXP249_STAGE_PARENT_UNKNOWN_PRESERVE_PARTIAL')
    print(canonical({'status': 'ZERO_MODEL_STAGE_RETURNED_AND_STOPPED', 'task_id': args.task, 'stage': args.stage, 'output': str(out)}), flush=True)

def load_original_probe(c):
    q = module('_exp249_task_original_qualifier', Path(c['harness']) / 'qualify.py')
    original = R / '工作区/1002-exp129-expanded-baselines/实验/实验129_扩展基线与恢复证据/executor/run.py'
    tree = ast.parse(original.read_text('utf-8-sig'))
    names = {'assess_probe', 'probe'}
    nodes = [v for v in tree.body if isinstance(v, ast.FunctionDef) and v.name in names]
    if {v.name for v in nodes} != names:
        raise RuntimeError('EXP249_ORIGINAL_PROBE_FUNCTIONS_CHANGED')
    run = types.ModuleType('_exp249_original_probe_functions')
    run.__file__ = str(original)
    run.__dict__.update(Path=Path, ast=ast, time=time, qualify=q, load=read, write=save, read_jsonl=lambda p: [json.loads(v) for v in Path(p).read_text('utf-8-sig').splitlines() if v.strip()])
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(original), 'exec'), run.__dict__)
    return run

def identity_prefix(receipt):
    spec = {'identity_source': str(IDENTITY_SOURCE), 'source_SHA256': sha(IDENTITY_SOURCE), 'receipt': str(owned(receipt))}
    return 'import sys as _id_sys, os as _id_os\n_id_path=list(_id_sys.path);_id_base=_id_os.path.normcase(_id_os.path.realpath(_id_sys.base_prefix))\n_id_sys.path=[p for p in _id_sys.path if p and _id_os.path.normcase(_id_os.path.realpath(p)).startswith(_id_base+_id_os.sep)]\nimport json as _id_json, hashlib as _id_hash, runpy as _id_runpy\nfrom pathlib import Path as _id_Path\n_id_spec=' + repr(spec) + "\nassert _id_hash.sha256(_id_Path(_id_spec['identity_source']).read_bytes()).hexdigest()==_id_spec['source_SHA256']\n_id_value=_id_runpy.run_path(_id_spec['identity_source'],run_name='_exp249_fixed_identity')['capture']()\n_id_value['before_product_import']=True\nwith _id_Path(_id_spec['receipt']).open('x',encoding='utf-8') as _id_f:_id_f.write(_id_json.dumps(_id_value,ensure_ascii=False,sort_keys=True)+'\\n')\n_id_sys.path=_id_path\n"

def wrap_native_argv(argv, receipt, grant, expected_image):
    supplied = list(map(str, argv))
    prefix = identity_prefix(receipt)
    policy = grant.value.get('current_process_clock_policy')
    if policy == 'ROOT_PRECISE_CLOCK_V9':
        descriptor = grant.value.get('common_precise_clock_contract')
        clock = module('_exp249_Root_precise_clock', COMMON / 'precise_product_bootstrap_v9_SOURCE.py')
        prefix += clock.make_bootstrap({'common_precise_clock_contract': descriptor}, grant.value, Path(receipt).with_name('precise_clock_receipt.json'), expected_image, job_env_key='COMMON_NATIVE_OWNED_JOB') + '\n'
    elif policy != 'ROOT_ORIGINAL_CLOCK_EXPLICITLY_ADMITTED':
        raise RuntimeError('EXP249_CURRENT_RUNTIME_CLOCK_POLICY_PENDING_ROOT')
    if supplied[1:3] == ['-m', 'pytest']:
        tail = 'import site;site.main();import runpy,sys;sys.argv=' + repr(['pytest'] + supplied[3:]) + ";runpy.run_module('pytest',run_name='__main__',alter_sys=True)"
        return [supplied[0], '-S', '-B', '-c', prefix + tail]
    if '-S' in supplied and supplied.count('-c') == 1:
        where = supplied.index('-c')
        return supplied[:where + 1] + [prefix + supplied[where + 1]] + supplied[where + 2:]
    raise RuntimeError('EXP249_UNRECOGNIZED_ORIGINAL_NATIVE_BOOTSTRAP')

def verify_measured_identity(value, receipt, expected, grant):
    if not stopped(value):
        raise RuntimeError('EXP249_ACTUAL_NATIVE_STOP_OR_HELD_IDENTITY_UNKNOWN')
    identity = read(receipt)
    if identity.get('before_product_import') is not True or identity.get('specific_named_Job_membership') is not True or identity.get('specific_job_name') != value['stop_receipt']['specific_job_name'] or (Path(identity['actual_OS_image']).resolve() != Path(expected['actual_OS_image']).resolve()) or (identity.get('actual_OS_image_SHA256') != expected['actual_OS_image_SHA256']) or (type(identity.get('pid')) is not int) or (identity['pid'] <= 0) or (type(identity.get('creation_time100ns')) is not int) or (identity['creation_time100ns'] <= 0):
        raise RuntimeError('EXP249_ACTUAL_PRODUCT_IDENTITY_NOT_SAME_QUALIFIED_RUNTIME')
    if grant.value.get('current_process_clock_policy') == 'ROOT_PRECISE_CLOCK_V9':
        clock = module('_exp249_Root_clock_verifier', COMMON / 'precise_product_bootstrap_v9_SOURCE.py')
        clock.verify_receipt({'common_precise_clock_contract': grant.value['common_precise_clock_contract']}, Path(receipt).with_name('precise_clock_receipt.json'), identity['actual_OS_image'], value['stop_receipt']['specific_job_name'])
    return identity

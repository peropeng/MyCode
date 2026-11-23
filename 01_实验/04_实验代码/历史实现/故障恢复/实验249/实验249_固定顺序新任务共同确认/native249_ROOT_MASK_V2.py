"""Root-granted zero-model identity and exact current-C0 G/O qualification.

The original held-Job executor, probe functions, selectors, guards, and capacity
adapter are loaded by hash. No original helper or historical result is edited.
"""
import argparse
import ast
import contextlib
import ctypes
import subprocess
import types
from common249 import *


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
                if jobs.accounting(k, job)['total_processes'] > 12:
                    raise RuntimeError('EXP249_PARENT_ACTUAL_PROCESS_COUNT_CAP')
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
    run.__dict__.update(Path=Path, ast=ast, time=time, qualify=q, load=read,
                        write=save, read_jsonl=lambda p: [json.loads(v) for v in Path(p).read_text('utf-8-sig').splitlines() if v.strip()])
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(original), 'exec'), run.__dict__)
    return run


def identity_prefix(receipt):
    spec = {'identity_source': str(E / 'physical_identity249.py'), 'source_SHA256': sha(E / 'physical_identity249.py'),
            'receipt': str(owned(receipt))}
    return ("import sys as _id_sys, os as _id_os\n"
            "_id_path=list(_id_sys.path);_id_base=_id_os.path.normcase(_id_os.path.realpath(_id_sys.base_prefix))\n"
            "_id_sys.path=[p for p in _id_sys.path if p and _id_os.path.normcase(_id_os.path.realpath(p)).startswith(_id_base+_id_os.sep)]\n"
            "import json as _id_json, hashlib as _id_hash, runpy as _id_runpy\n"
            "from pathlib import Path as _id_Path\n"
            "_id_spec=" + repr(spec) + "\n"
            "assert _id_hash.sha256(_id_Path(_id_spec['identity_source']).read_bytes()).hexdigest()==_id_spec['source_SHA256']\n"
            "_id_value=_id_runpy.run_path(_id_spec['identity_source'],run_name='_exp249_fixed_identity')['capture']()\n"
            "_id_value['before_product_import']=True\n"
            "with _id_Path(_id_spec['receipt']).open('x',encoding='utf-8') as _id_f:_id_f.write(_id_json.dumps(_id_value,ensure_ascii=False,sort_keys=True)+'\\n')\n"
            "_id_sys.path=_id_path\n")


def wrap_native_argv(argv, receipt, grant, expected_image):
    supplied = list(map(str, argv))
    prefix = identity_prefix(receipt)
    policy = grant.value.get('current_process_clock_policy')
    if policy == 'ROOT_PRECISE_CLOCK_V9':
        descriptor = grant.value.get('common_precise_clock_contract')
        clock = module('_exp249_Root_precise_clock', COMMON / 'precise_product_bootstrap_v9_SOURCE.py')
        prefix += clock.make_bootstrap({'common_precise_clock_contract': descriptor}, grant.value,
                                       Path(receipt).with_name('precise_clock_receipt.json'), expected_image,
                                       job_env_key='COMMON_NATIVE_OWNED_JOB') + '\n'
    elif policy != 'ROOT_ORIGINAL_CLOCK_EXPLICITLY_ADMITTED':
        raise RuntimeError('EXP249_CURRENT_RUNTIME_CLOCK_POLICY_PENDING_ROOT')
    if supplied[1:3] == ['-m', 'pytest']:
        tail = ('import site;site.main();import runpy,sys;'
                'sys.argv=' + repr(['pytest'] + supplied[3:]) + ';'
                "runpy.run_module('pytest',run_name='__main__',alter_sys=True)")
        return [supplied[0], '-S', '-B', '-c', prefix + tail]
    if '-S' in supplied and supplied.count('-c') == 1:
        where = supplied.index('-c')
        return supplied[:where + 1] + [prefix + supplied[where + 1]] + supplied[where + 2:]
    raise RuntimeError('EXP249_UNRECOGNIZED_ORIGINAL_NATIVE_BOOTSTRAP')


def verify_measured_identity(value, receipt, expected, grant):
    if not stopped(value):
        raise RuntimeError('EXP249_ACTUAL_NATIVE_STOP_OR_HELD_IDENTITY_UNKNOWN')
    identity = read(receipt)
    if (identity.get('before_product_import') is not True or identity.get('specific_named_Job_membership') is not True
            or identity.get('specific_job_name') != value['stop_receipt']['specific_job_name']
            or Path(identity['actual_OS_image']).resolve() != Path(expected['actual_OS_image']).resolve()
            or identity.get('actual_OS_image_SHA256') != expected['actual_OS_image_SHA256']
            or type(identity.get('pid')) is not int or identity['pid'] <= 0
            or type(identity.get('creation_time100ns')) is not int or identity['creation_time100ns'] <= 0):
        raise RuntimeError('EXP249_ACTUAL_PRODUCT_IDENTITY_NOT_SAME_QUALIFIED_RUNTIME')
    if grant.value.get('current_process_clock_policy') == 'ROOT_PRECISE_CLOCK_V9':
        clock = module('_exp249_Root_clock_verifier', COMMON / 'precise_product_bootstrap_v9_SOURCE.py')
        clock.verify_receipt({'common_precise_clock_contract': grant.value['common_precise_clock_contract']},
                             Path(receipt).with_name('precise_clock_receipt.json'), identity['actual_OS_image'],
                             value['stop_receipt']['specific_job_name'])
    return identity


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


def run_current_C0(args, grant, out, jobs, row, c):
    if (grant.value.get('max_original_G_O_native') != 1 or grant.value.get('max_masked_ordinary_native') != 1
            or grant.value.get('trusted_original_G_O_oracle_execution_authorized') is not True):
        raise RuntimeError('EXP249_TWO_EXACT_ZERO_MODEL_PUBLIC_NATIVE_GATES_REQUIRED')
    identity_path = E / 'qualification' / args.task / 'identity' / 'COMPLETED_IDENTITY249.json'
    parent_path = identity_path.parent / 'PARENT_TERMINAL249.json'
    if grant.value.get('current_identity_receipt_SHA256') != sha(identity_path) or grant.value.get('current_identity_parent_STOP_SHA256') != sha(parent_path):
        raise RuntimeError('EXP249_FRESH_IDENTITY_AND_PARENT_STOP_BINDING_REQUIRED')
    previous_parent = read(parent_path)
    if previous_parent.get('error') is not None or previous_parent.get('exit_code') != 0 or previous_parent['stop_receipt'].get('all_owned_descendants_terminated') is not True:
        raise RuntimeError('EXP249_CURRENT_IDENTITY_PARENT_STOP_UNKNOWN')
    identity = read(identity_path)
    python = Path(c['logical_product_python']).resolve()
    if identity['logical_product_python_SHA256'] != sha(python) or identity['pyvenv_cfg_SHA256'] != sha(python.parent.parent / 'pyvenv.cfg'):
        raise RuntimeError('EXP249_QUALIFIED_RUNTIME_ENTRY_DRIFT')
    expected = identity['product_identity']
    if sha(expected['actual_OS_image']) != expected['actual_OS_image_SHA256']:
        raise RuntimeError('EXP249_QUALIFIED_PHYSICAL_IMAGE_DRIFT')
    scope_path = E / 'public_views_v2' / 'COMMON_MASKED_PUBLIC_TEST_SCOPE249.json'
    if grant.value.get('masked_scope_SHA256') != sha(scope_path):
        raise RuntimeError('EXP249_MASKED_SCOPE_NOT_ROOT_BOUND')
    p = {'task_order': TASKS, 'public_test_scope_contract': {'path': str(scope_path), 'sha256': sha(scope_path)},
         'masked_native_owner_root': str(E), 'masked_native_guard_directory': str(V14 / 'guard_v10'),
         'masked_native_guard_source_SHA256': {n: sha(V14 / 'guard_v10' / n) for n in ('sitecustomize.py', 'runner.py')},
         'audit_trace_mode': 'all_permissions_checked_denials_persisted',
         'budget': {'native_roots_total': 2, 'native_timeout_seconds': 300}}
    masked = module('_exp249_shared_native_v14', V14 / 'native_masked_public239.py')
    scope = masked.load_scope(p, args.task)
    if scope.get('materialization_qualified') is not True:
        raise RuntimeError('EXP249_MASKED_VIEW_NOT_MATERIALIZED')
    active = out / 'runtime'; repo = active / 'repo'; repo.mkdir(parents=True)
    for rel, h in c['c0_business_paths_sha256'].items():
        source = Path(scope['public_source_repo_view']) / safe_rel(rel)
        if sha(source) != h:
            raise RuntimeError('EXP249_PUBLIC_VIEW_C0_DRIFT')
        target = repo / rel; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(source.read_bytes())
    supports = masked.materialize_support(repo, scope, c['c0_business_paths_sha256'])
    masked.verify_actor(repo, c['c0_business_paths_sha256'], supports)
    events = []
    run = load_original_probe(c)
    env = types.SimpleNamespace(run=run, package=c['package'], task_id=args.task, native_calls=0, out=out,
          _paths={'python': python, 'frozen': Path(c['frozen_public_test_root'])},
          _require=grant.check, record=lambda stage, value: events.append({'stage': stage, 'value': value}),
          business_files=lambda: {rel: (repo / rel).read_text('utf-8') for rel in c['c0_business_paths_sha256']},
          time_left=lambda: max(.1, datetime.datetime.fromisoformat(grant.value['lease_end_UTC']).timestamp() - time.time()))
    jobs.install(env)
    capacity = module('_exp249_original_capacity', OLD / 'native_capacity_v10.py')
    capacity.NATIVE_TIMEOUT_SECONDS = 300; capacity.install(env)
    scheduler = module('_exp249_common_four_slots', COMMON / 'native_four_slots_v5_SOURCE.py')
    scheduling = read(COMMON / 'ROOT_COMMON_NATIVE_SCHEDULING_V5_FOUR_SOURCE.json')
    env.native_lane = lambda: scheduler.native_lane(scheduling['lock_path'], c['package'], grant.check,
                                                   lambda v: events.append({'stage': 'V5_four_slots', 'value': v}))
    original_execute = run.qualify.execute
    def measured_execute(argv, cwd, log, timeout=300, env=None):
        receipt = Path(log).with_name('ACTUAL_PRODUCT_SELF249.json')
        actual_argv = wrap_native_argv(argv, receipt, grant, expected['actual_OS_image'])
        value = original_execute(actual_argv, cwd, log, timeout, env)
        self_id = verify_measured_identity(value, receipt, expected, grant)
        value['actual_product_identity'] = self_id
        value['actual_product_identity_SHA256'] = sha(receipt)
        value['original_semantic_argv'] = list(map(str, argv))
        return value
    run.qualify.execute = measured_execute
    nodes = list(dict.fromkeys(c['public_target_nodes'] + c['ordinary_nodes']))
    if grant.value.get('exact_G_O_nodes') != nodes:
        raise RuntimeError('EXP249_EXACT_PUBLIC_NODE_RELEASE_REQUIRED')
    intent(out / 'G_O_NATIVE_INTENT.json', {'UTC': now(), 'task_id': args.task, 'nodes': nodes,
           'source_inventory': c['c0_business_inventory_sha256'], 'Root_grant_SHA256': grant.sha256})
    with env.native_lane():
        grant.check(full=True)
        raw = run.probe(active, Path(c['frozen_public_test_root']), nodes, out / 'original_G_O', python, c['package'], time.monotonic() + min(300, env.time_left()))
    guard = module('_exp249_original_public_observer', OLD / 'progress_guard240.py')
    validation = {'native_record': raw, 'outcomes': {n: raw.get('pytest', {}).get('outcomes', {}).get(n, {}) for n in c['ordinary_nodes']}}
    observed = guard.observe(validation, c['public_target_nodes'], c['ordinary_nodes'])
    if not observed['ordinary_pass'] or observed['failed_goals'] < 1:
        save(out / 'ORIGINAL_G_O_NOT_ELIGIBLE.json', {'ordinary_pass': observed['ordinary_pass'], 'failed_goals': observed['failed_goals'],
             'goal_pass': sorted(observed['goal_pass']), 'actual_record': str(out / 'original_G_O/run.json'),
             'all_methods_same_qualification_exclusion': True, 'method_outcome': None})
        raise RuntimeError('EXP249_C0_NOT_ORIGINAL_GOAL_FAILURE_AND_ORDINARY_PASS')
    # A separate real ordinary leaf validates the v14 masked source/tool channel.
    env.native_calls = 1
    masked_result = masked.execute(env, repo, scope, list(c['ordinary_nodes']), collect_only=False,
            label='zero_model_masked_ordinary', protocol=p,
            owner_check=lambda: parent_member(jobs, grant.value['parent_owned_job_name']))
    if masked_result.get('known') is not True or masked_result.get('status') != 'PUBLIC_RUN_COMPLETE' or any(
            masked_result['pytest']['outcomes'].get(n, {}).get('status') != 'passed' for n in c['ordinary_nodes']):
        raise RuntimeError('EXP249_MASKED_V14_ORDINARY_GATE_UNKNOWN_OR_NOT_PASS')
    masked.verify_actor(repo, c['c0_business_paths_sha256'], supports)
    if {rel: sha(repo / rel) for rel in c['c0_business_paths_sha256']} != c['c0_business_paths_sha256']:
        raise RuntimeError('EXP249_C0_CHANGED_AFTER_NATIVE')
    save(out / 'PUBLIC_CURRENT_C0_OBSERVATION249.json', {'schema': 'EXP249-fresh-common-C0-public-observation/1',
         'task_id': args.task, 'UTC': now(), 'previous_full_public_pack_SHA256': c['pack_sha256'],
         'actual_C0_source_SHA256': c['c0_business_paths_sha256'], 'actual_ABI': expected,
         'current_incumbent_public_feedback': observed['complete_validation'],
         'ordinary_PASS_count': len(c['ordinary_nodes']), 'goal_failure_count': observed['failed_goals'],
         'goal_actual_PASS_nodes': sorted(observed['goal_pass']), 'same_for_all_three_methods': True,
         'independent_private_or_Gold_or_other_methods_outputs': False,
         'original_public_G_O_native_calls': 1, 'masked_ordinary_native_calls': 1,
         'model_calls': 0, 'private_calls': 0, 'finance_writes': 0})
    save(out / 'NATIVE_TRANSPORT_EVIDENCE249.json', events)
    save(out / 'COMPLETED_CURRENT_C0_WORKER249.json', {'task_id': args.task, 'UTC': now(),
         'status': 'FRESH_CURRENT_C0_GFAIL_OPASS_AND_MASKED_V14_ORDINARY_PASS',
         'observation_SHA256': sha(out / 'PUBLIC_CURRENT_C0_OBSERVATION249.json'),
         'fresh_identity_receipt_SHA256': sha(identity_path), 'Root_grant_SHA256': grant.sha256,
         'parent_STOP_still_required_before_Root_common_release': True,
         'model_private_finance': 0, 'scientific_repair_success': None})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=('identity', 'current_C0'), required=True)
    parser.add_argument('--task', choices=FIRST_TWO, required=True)
    parser.add_argument('--root-grant', required=True)
    parser.add_argument('--worker', action='store_true')
    args = parser.parse_args()
    grant = Grant(args.root_grant, args.stage, [args.task])
    for source_path, expected in grant.value['Root_mask_v2_sources_SHA256'].items():
        if sha(source_path) != expected: raise RuntimeError('EXP249_ROOT_MASK_V2_SOURCE_DRIFT')
    if grant.value['Root_mask_v2_sources_SHA256'].get(str(Path(__file__).resolve())) != sha(__file__):
        raise RuntimeError('EXP249_ROOT_MASK_V2_SELF_NOT_BOUND')
    jobs = load_jobs(grant)
    out = E / 'qualification' / args.task / ('current_C0_mask_v2' if args.stage == 'current_C0' else args.stage)
    if not args.worker:
        return supervise(args, grant, out, jobs)
    if not parent_member(jobs, grant.value['parent_owned_job_name']):
        raise RuntimeError('EXP249_WORKER_NOT_IN_EXACT_PARENT_JOB')
    identity = module('_exp249_controller_identity', E / 'physical_identity249.py')
    save(out / 'CONTROLLER_SELF_IDENTITY.json', identity.capture())
    row, c = binding(args.task)
    intent(out / 'WORKER_STARTED_ONCE.json', {'UTC': now(), 'stage': args.stage, 'Root_grant_SHA256': grant.sha256})
    if args.stage == 'identity':
        run_identity(args, grant, out, jobs, row, c)
    else:
        run_current_C0(args, grant, out, jobs, row, c)


if __name__ == '__main__':
    main()

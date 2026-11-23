"""ADD-only fixed moto5072 controller; frozen V2 algorithms and seal unchanged."""
from common166 import *
import copy, ctypes, traceback
from ctypes import wintypes
from decimal import Decimal
from publicpack_v2_224 import V
from environment_v2_224 import EnvironmentV2, authorize_v2

PIN = V / 'second_entry_source_pin_v2.json'
TASK = 'getmoto__moto-5072'
METHODS = {'calibrate-agentless': 'AGENTLESS_FSE2025_4L4P4T_FLASH',
           'calibrate-ours': 'G_PROGRESSIVE_SEMANTIC_FLASH'}


def verify_addendum(mode=None, require_root=True):
    pin = read(PIN)
    assert pin['version'] == 'V2_AUTH_DIRECT_PUBLICPACK' and pin['fixed_second_task'] == TASK
    assert sha(V / 'source_seal_v2.json') == pin['immutable_parent_seal_sha256']
    assert sha(V / 'pack_registry_v2.json') == pin['pack_registry_sha256']
    for path, expected in {**pin['new_sources'], **pin['read_only_inputs']}.items():
        assert sha(path) == expected, 'SECOND_ENTRY_PIN_DRIFT ' + path
    first = read(V / 'calibration/recovery/dask__dask-9378/AGENTLESS_FSE2025_4L4P4T_FLASH/result.json')
    assert first.get('actual_patch_repro_native_gate') is True, 'FIRST_DASK_STAGE_GATE_REQUIRED'
    assert first.get('source_seal_sha256') == pin['immutable_parent_seal_sha256']
    if require_root:
        authorize_v2()
        grant = read(V / 'root_calibration_grant_v2.json')
        assert int(grant.get('allowed_calibration_index', 0)) >= 1, 'ROOT_SECOND_INDEX1_GRANT_REQUIRED'
        assert grant.get('second_entry_source_pin_sha256') == sha(PIN), 'ROOT_ADDITIONAL_SOURCE_PIN_REQUIRED'
        assert mode in METHODS and METHODS[mode] in grant.get('approved_methods', []), 'ROOT_SECOND_METHOD_NOT_APPROVED'
    return pin


def current_birth():
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.GetCurrentProcess.restype = wintypes.HANDLE
    handle = k.GetCurrentProcess(); values = [wintypes.FILETIME() for _ in range(4)]
    k.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    assert k.GetProcessTimes(handle, *[ctypes.byref(x) for x in values])
    return (values[0].dwHighDateTime << 32) | values[0].dwLowDateTime


def actual_parent_pid():
    # Toolhelp reports the physical current process's parent, including the
    # live venv redirect launcher rather than confusing its PID with self.
    class Entry(ctypes.Structure):
        _fields_ = [('dwSize', wintypes.DWORD), ('cntUsage', wintypes.DWORD),
                    ('th32ProcessID', wintypes.DWORD), ('th32DefaultHeapID', ctypes.c_size_t),
                    ('th32ModuleID', wintypes.DWORD), ('cntThreads', wintypes.DWORD),
                    ('th32ParentProcessID', wintypes.DWORD), ('pcPriClassBase', wintypes.LONG),
                    ('dwFlags', wintypes.DWORD), ('szExeFile', wintypes.WCHAR * 260)]
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    k.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    k.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
    k.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
    k.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = k.CreateToolhelp32Snapshot(2, 0)
    assert handle and handle != ctypes.c_void_p(-1).value, 'SELF_PARENT_SNAPSHOT_FAILED'
    entry = Entry(); entry.dwSize = ctypes.sizeof(entry)
    try:
        more = k.Process32FirstW(handle, ctypes.byref(entry))
        while more:
            if entry.th32ProcessID == os.getpid(): return int(entry.th32ParentProcessID)
            more = k.Process32NextW(handle, ctypes.byref(entry))
        raise RuntimeError('SELF_PARENT_IDENTITY_UNKNOWN')
    finally: k.CloseHandle(handle)


def pid_birth(pid):
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    k.OpenProcess.restype = wintypes.HANDLE
    k.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    k.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = k.OpenProcess(0x1000, False, pid)
    assert handle, 'LIVE_LAUNCHER_QUERY_FAILED'
    try:
        values = [wintypes.FILETIME() for _ in range(4)]
        assert k.GetProcessTimes(handle, *[ctypes.byref(x) for x in values])
        return (values[0].dwHighDateTime << 32) | values[0].dwLowDateTime
    finally: k.CloseHandle(handle)


def run(mode):
    verify_addendum(mode)
    method = METHODS[mode]
    label = 'AGENTLESS_FSE2025' if mode == 'calibrate-agentless' else 'OURS_G153_PROGRESSIVE_SEMANTIC'
    refs = {r['task_id']: r for r in read(E / 'data/selected_task_bindings.json')['tasks']}
    plans = read(E / 'ranking/plan_registry224.json')['plans']
    ref = copy.deepcopy(refs[TASK]); ref.update(G_frozen_plan=plans[TASK]['path'],
        _output_namespace='v2_auth_direct_publicpack/calibration/recovery',
        _native_namespace='v2_auth_direct_publicpack/calibration/native_active')
    out = E / ref['_output_namespace'] / TASK / method
    assert not (out / 'result.json').exists(), 'SECOND_EXISTING_RESULT_NO_RERUN'
    out.mkdir(parents=True, exist_ok=True)
    birth = current_birth()
    supervisor = read(V / ('supervision_second_' + mode + '_v2.json'))
    assert supervisor['status'] == 'RUNNING' and supervisor['job_kill_on_close'] and supervisor['suspended_until_assigned_to_job'], 'SECOND_OWNED_PARENT_JOB_REQUIRED'
    launcher_pid = supervisor['runner_pid']; launcher_birth = supervisor['runner_creation_time100ns']
    if launcher_pid == os.getpid():
        assert launcher_birth == birth, 'SECOND_DIRECT_SELF_BIRTH_MISMATCH'
        parent = actual_parent_pid()
    else:
        parent = actual_parent_pid()
        assert parent == launcher_pid and pid_birth(launcher_pid) == launcher_birth, 'SECOND_REDIRECT_PARENT_BIRTH_MISMATCH'
    started = {'version': 'V2_AUTH_DIRECT_PUBLICPACK', 'task_id': TASK, 'mode': mode,
               'PID': os.getpid(), 'creation_time100ns': birth, 'at_utc': now(),
               'parent_job_required': True, 'source_pin_sha256': sha(PIN),
               'logical_launcher_PID': launcher_pid, 'logical_launcher_birth100ns': launcher_birth,
               'actual_parent_PID': parent, 'direct_or_redirect_lineage_verified': True,
               'no_Dask_or_V1_model_or_patch_reuse': True}
    # An exclusive marker prevents duplicate workers even before any POST.
    with (out / 'worker_started.json').open('x', encoding='utf-8') as f:
        f.write(canonical(started) + '\n')
    env = None
    try:
        env = EnvironmentV2(ref, method)
        core = sys.modules['agentless178'] if label == 'AGENTLESS_FSE2025' else sys.modules['ranked_repair178']
        result = core.run(env); full = env.finalize(result)
    except Exception as error:
        private_births = set()
        for p in (out / 'final_preservation').rglob('*.process.json'):
            for process in read(p).get('process_birth', []):
                private_births.add((process['pid'], process['creation_time100ns']))
        full = {'task_id': TASK, 'method': method, 'status': 'ENGINEERING_UNKNOWN', 'success': None,
                'error': {'type': type(error).__name__, 'message': str(error)}, 'traceback': traceback.format_exc(),
                'LLM_calls': getattr(env, 'calls', 0), 'public_native_calls': getattr(env, 'native_calls', 0),
                'hidden_acceptance_calls': len(private_births), 'runtime_core': {}}
    receipts = [read(p) for p in out.glob('llm/*_finance_receipt.json')]
    settled = [r for r in receipts if r.get('status') == 'SETTLED']
    fee = sum((Decimal(r['usage_peak_cost_CNY']) for r in settled), Decimal(0))
    full.update(version='V2_AUTH_DIRECT_PUBLICPACK', scientific_method=label, primary_eligible=False,
                calibration_only=True, fees_CNY=str(fee), new_fees_CNY=str(fee), new_paid_API=len(settled),
                source_seal_sha256=sha(V / 'source_seal_v2.json'), pack_registry_sha256=sha(V / 'pack_registry_v2.json'),
                second_entry_source_pin_sha256=sha(PIN), reused_v1_outputs=0, reused_first_case_outputs=0)
    save(out / 'result.json', full)
    append(V / ('completed_second_' + mode + '.jsonl'), {k: full.get(k) for k in
        ('task_id', 'scientific_method', 'status', 'success', 'new_paid_API', 'new_fees_CNY', 'LLM_calls', 'public_native_calls', 'hidden_acceptance_calls')})
    print(canonical({k: full.get(k) for k in ('task_id', 'status', 'success', 'new_fees_CNY')}), flush=True)


if __name__ == '__main__': run(sys.argv[1])

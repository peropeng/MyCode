"""Zero-product identity probe: only stdlib, current process and own named Job."""
import ctypes
import hashlib
import json
import os
import platform
import sys
import sysconfig
from ctypes import wintypes
from pathlib import Path


def capture():
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    defs = {'GetCurrentProcess': ([], wintypes.HANDLE), 'GetCurrentProcessId': ([], wintypes.DWORD),
            'GetProcessTimes': ([wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4, wintypes.BOOL),
            'QueryFullProcessImageNameW': ([wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)], wintypes.BOOL),
            'OpenJobObjectW': ([wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR], wintypes.HANDLE),
            'IsProcessInJob': ([wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)], wintypes.BOOL),
            'CloseHandle': ([wintypes.HANDLE], wintypes.BOOL)}
    for name, (args, restype) in defs.items():
        getattr(k, name).argtypes = args; getattr(k, name).restype = restype
    current = k.GetCurrentProcess()
    times = [wintypes.FILETIME() for _ in range(4)]
    if not k.GetProcessTimes(current, *[ctypes.byref(x) for x in times]):
        raise RuntimeError('EXP249_SELF_BIRTH_UNKNOWN')
    size = wintypes.DWORD(32768); buf = ctypes.create_unicode_buffer(size.value)
    if not k.QueryFullProcessImageNameW(current, 0, buf, ctypes.byref(size)):
        raise RuntimeError('EXP249_SELF_IMAGE_UNKNOWN')
    name = os.environ.get('COMMON_NATIVE_OWNED_JOB') or os.environ.get('EXP249_PARENT_JOB')
    if not name:
        raise RuntimeError('EXP249_SPECIFIC_OWNED_JOB_REQUIRED')
    job = k.OpenJobObjectW(4, False, name)
    if not job:
        raise RuntimeError('EXP249_SELF_JOB_OPEN_FAILED')
    try:
        member = wintypes.BOOL()
        if not k.IsProcessInJob(current, job, ctypes.byref(member)) or not member.value:
            raise RuntimeError('EXP249_SELF_NOT_IN_DECLARED_JOB')
    finally:
        k.CloseHandle(job)
    physical = Path(buf.value).resolve()
    return {'schema': 'EXP249-actual-physical-runtime-identity/1', 'pid': int(k.GetCurrentProcessId()),
            'creation_time100ns': (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime,
            'actual_OS_image': str(physical), 'actual_OS_image_SHA256': hashlib.sha256(physical.read_bytes()).hexdigest(),
            'logical_sys_executable': sys.executable, 'sys_prefix': sys.prefix, 'sys_base_prefix': sys.base_prefix,
            'version': sys.version, 'version_info': list(sys.version_info), 'platform': sys.platform,
            'machine': platform.machine(), 'SOABI': sysconfig.get_config_var('SOABI'),
            'EXT_SUFFIX': sysconfig.get_config_var('EXT_SUFFIX'), 'specific_job_name': name,
            'specific_named_Job_membership': True, 'product_imports_or_tests': 0,
            'identity_is_observed_not_inferred_from_venv_configuration': True}


if __name__ == '__main__':
    print(json.dumps(capture(), ensure_ascii=False, sort_keys=True), flush=True)

"""Windows CreateProcess cwd alias only; no command or source rewriting."""
import ctypes
from ctypes import wintypes
from pathlib import Path

def createprocess_cwd(cwd):
    original = Path(cwd).resolve()
    if not original.is_dir():
        raise NotADirectoryError('NATIVE_CWD_NOT_AN_EXISTING_DIRECTORY: ' + str(original))
    source = str(original)
    if len(source) < 240:
        return source, {'adapted': False, 'original': source, 'effective': source}
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetShortPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    kernel.GetShortPathNameW.restype = wintypes.DWORD
    buffer = ctypes.create_unicode_buffer(32768)
    count = kernel.GetShortPathNameW(source, buffer, len(buffer))
    if not count or count >= len(buffer) or len(buffer.value) >= 240:
        raise RuntimeError('WINAPI_SHORT_CWD_UNAVAILABLE: ' + str(ctypes.get_last_error()))
    effective = buffer.value
    if not Path(effective).is_dir() or not Path(effective).samefile(original):
        raise RuntimeError('WINAPI_SHORT_CWD_IDENTITY_DIFFERS')
    return effective, {'adapted': True, 'original': source, 'effective': effective,
        'GetShortPathNameW_count': count, 'samefile_verified_before_CreateProcess': True,
        'argv_source_guard_and_requested_image_unchanged': True}

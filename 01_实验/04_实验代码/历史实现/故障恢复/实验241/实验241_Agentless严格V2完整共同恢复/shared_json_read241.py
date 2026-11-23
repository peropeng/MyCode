"""Read-only JSON with Windows READ|WRITE|DELETE sharing. No work on import."""
import ctypes,json,os
from pathlib import Path
from ctypes import wintypes as W
SHARE_READ_WRITE_DELETE=1|2|4
def read_bytes_shared(path):
 if os.name!='nt':return Path(path).read_bytes()
 k=ctypes.WinDLL('kernel32',use_last_error=True)
 k.CreateFileW.argtypes=[W.LPCWSTR,W.DWORD,W.DWORD,ctypes.c_void_p,W.DWORD,W.DWORD,W.HANDLE];k.CreateFileW.restype=W.HANDLE
 k.ReadFile.argtypes=[W.HANDLE,ctypes.c_void_p,W.DWORD,ctypes.POINTER(W.DWORD),ctypes.c_void_p];k.ReadFile.restype=W.BOOL
 k.CloseHandle.argtypes=[W.HANDLE];k.CloseHandle.restype=W.BOOL
 h=k.CreateFileW(str(Path(path).resolve()),0x80000000,SHARE_READ_WRITE_DELETE,None,3,0x80,None)
 if h==ctypes.c_void_p(-1).value:raise ctypes.WinError(ctypes.get_last_error())
 try:
  chunks=[];buffer=ctypes.create_string_buffer(65536);count=W.DWORD()
  while True:
   if not k.ReadFile(h,buffer,len(buffer),ctypes.byref(count),None):raise ctypes.WinError(ctypes.get_last_error())
   if not count.value:break
   chunks.append(buffer.raw[:count.value])
  return b''.join(chunks)
 finally:k.CloseHandle(h)
def read_json_shared(path):return json.loads(read_bytes_shared(path).decode('utf-8-sig'))

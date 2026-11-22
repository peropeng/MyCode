import ctypes,os,struct
from ctypes import wintypes as w
from common166 import now
class Basic(ctypes.Structure):
 _fields_=[('PerProcessUserTimeLimit',ctypes.c_longlong),('PerJobUserTimeLimit',ctypes.c_longlong),('LimitFlags',w.DWORD),('MinimumWorkingSetSize',ctypes.c_size_t),('MaximumWorkingSetSize',ctypes.c_size_t),('ActiveProcessLimit',w.DWORD),('Affinity',ctypes.c_size_t),('SchedulingClass',w.DWORD)]
class IO(ctypes.Structure):
 _fields_=[(n,ctypes.c_ulonglong) for n in ('ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount')]
class Extended(ctypes.Structure):
 _fields_=[('BasicLimitInformation',Basic),('IoInfo',IO),('ProcessMemoryLimit',ctypes.c_size_t),('JobMemoryLimit',ctypes.c_size_t),('PeakProcessMemoryUsed',ctypes.c_size_t),('PeakJobMemoryUsed',ctypes.c_size_t)]
def kernel():
 k=ctypes.WinDLL('kernel32',use_last_error=True)
 signatures={
 'GetCurrentProcess':([],w.HANDLE),
 'GetProcessTimes':([w.HANDLE,*([ctypes.POINTER(w.FILETIME)]*4)],w.BOOL),
 'GetModuleFileNameW':([w.HMODULE,w.LPWSTR,w.DWORD],w.DWORD),
 'CreateJobObjectW':([ctypes.c_void_p,w.LPCWSTR],w.HANDLE),
 'OpenJobObjectW':([w.DWORD,w.BOOL,w.LPCWSTR],w.HANDLE),
 'SetInformationJobObject':([w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD],w.BOOL),
 'AssignProcessToJobObject':([w.HANDLE,w.HANDLE],w.BOOL),
 'IsProcessInJob':([w.HANDLE,w.HANDLE,ctypes.POINTER(w.BOOL)],w.BOOL),
 'QueryInformationJobObject':([w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD,ctypes.POINTER(w.DWORD)],w.BOOL),
 'OpenProcess':([w.DWORD,w.BOOL,w.DWORD],w.HANDLE),
 'QueryFullProcessImageNameW':([w.HANDLE,w.DWORD,w.LPWSTR,ctypes.POINTER(w.DWORD)],w.BOOL),
 'CloseHandle':([w.HANDLE],w.BOOL),
 'TerminateJobObject':([w.HANDLE,w.UINT],w.BOOL),
 }
 for n,(args,result) in signatures.items():getattr(k,n).argtypes=args;getattr(k,n).restype=result
 return k
def filetime(k,h):
 vals=[w.FILETIME() for _ in range(4)];assert k.GetProcessTimes(h,*[ctypes.byref(x) for x in vals]),ctypes.get_last_error()
 return (vals[0].dwHighDateTime<<32)|vals[0].dwLowDateTime
def self_identity(job_name=None):
 k=kernel();h=k.GetCurrentProcess();buf=ctypes.create_unicode_buffer(32768);n=k.GetModuleFileNameW(None,buf,len(buf));assert 0<n<len(buf)
 r={'at_utc':now(),'actual_PID':os.getpid(),'creation_time100ns':filetime(k,h),'actual_OS_image_GetModuleFileName':buf.value,'pointer_bytes':ctypes.sizeof(ctypes.c_void_p),'FILETIME_bytes':ctypes.sizeof(w.FILETIME),'BOOL_bytes':ctypes.sizeof(w.BOOL),'GetCurrentProcess_restype':'HANDLE'}
 if job_name:
  j=k.OpenJobObjectW(4,False,job_name);assert j,('OpenJobObjectW',ctypes.get_last_error());membership=w.BOOL()
  try:assert k.IsProcessInJob(h,j,ctypes.byref(membership)) and membership.value
  finally:k.CloseHandle(j)
  r.update(specific_named_Job=job_name,IsProcessInJob_specific_own_Job=True)
 return r
def birth(k,h,j,pid):
 membership=w.BOOL();assert k.IsProcessInJob(h,j,ctypes.byref(membership)) and membership.value
 buf=ctypes.create_unicode_buffer(32768);n=w.DWORD(len(buf));assert k.QueryFullProcessImageNameW(h,0,buf,ctypes.byref(n))
 return {'at_utc':now(),'PID':pid,'creation_time100ns':filetime(k,h),'OS_image_QueryFullProcessImageName':buf.value,'specific_named_Job_member':True}
def pids(k,j):
 b=ctypes.create_string_buffer(32776);n=w.DWORD();assert k.QueryInformationJobObject(j,3,b,len(b),ctypes.byref(n))
 assigned,count=struct.unpack_from('<II',b.raw);size=ctypes.sizeof(ctypes.c_size_t)
 return list(struct.unpack_from('<'+('Q' if size==8 else 'I')*count,b.raw,8)) if count else []

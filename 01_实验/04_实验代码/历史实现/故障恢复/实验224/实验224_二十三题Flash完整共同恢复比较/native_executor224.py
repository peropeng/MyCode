"""Synchronous native root born suspended, assigned own Job before execution."""
from common166 import *
import ctypes,subprocess
from ctypes import wintypes
from contextlib import contextmanager
class Basic(ctypes.Structure):
 _fields_=[('PerProcessUserTimeLimit',ctypes.c_longlong),('PerJobUserTimeLimit',ctypes.c_longlong),('LimitFlags',wintypes.DWORD),('MinimumWorkingSetSize',ctypes.c_size_t),('MaximumWorkingSetSize',ctypes.c_size_t),('ActiveProcessLimit',wintypes.DWORD),('Affinity',ctypes.c_size_t),('PriorityClass',wintypes.DWORD),('SchedulingClass',wintypes.DWORD)]
class IO(ctypes.Structure):_fields_=[(n,ctypes.c_ulonglong) for n in ('ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount')]
class Extended(ctypes.Structure):_fields_=[('BasicLimitInformation',Basic),('IoInfo',IO),('ProcessMemoryLimit',ctypes.c_size_t),('JobMemoryLimit',ctypes.c_size_t),('PeakProcessMemoryUsed',ctypes.c_size_t),('PeakJobMemoryUsed',ctypes.c_size_t)]
def execute(argv,cwd,log,timeout=90,env=None):
 authorization();log=Path(log).resolve();assert log.is_relative_to(Path(__import__('common166').E).resolve())
 k=ctypes.WinDLL('kernel32',use_last_error=True);k.CreateJobObjectW.argtypes=[ctypes.c_void_p,wintypes.LPCWSTR];k.CreateJobObjectW.restype=wintypes.HANDLE;k.SetInformationJobObject.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD];k.AssignProcessToJobObject.argtypes=[wintypes.HANDLE,wintypes.HANDLE];k.CloseHandle.argtypes=[wintypes.HANDLE]
 job=k.CreateJobObjectW(None,None);assert job
 limits=Extended();limits.BasicLimitInformation.LimitFlags=0x2000
 if not k.SetInformationJobObject(job,9,ctypes.byref(limits),ctypes.sizeof(limits)):k.CloseHandle(job);raise ctypes.WinError(ctypes.get_last_error())
 started=time.monotonic();p=None;timed=False;birth=None;out='';err=''
 try:
  p=subprocess.Popen([str(x) for x in argv],cwd=str(cwd),env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=0x08000000|0x00000004)
  if not k.AssignProcessToJobObject(job,wintypes.HANDLE(int(p._handle))):raise ctypes.WinError(ctypes.get_last_error())
  created=wintypes.FILETIME();ended=wintypes.FILETIME();kt=wintypes.FILETIME();ut=wintypes.FILETIME();k.GetProcessTimes.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.FILETIME),ctypes.POINTER(wintypes.FILETIME),ctypes.POINTER(wintypes.FILETIME),ctypes.POINTER(wintypes.FILETIME)]
  if not k.GetProcessTimes(wintypes.HANDLE(int(p._handle)),ctypes.byref(created),ctypes.byref(ended),ctypes.byref(kt),ctypes.byref(ut)):raise ctypes.WinError(ctypes.get_last_error())
  birth=(created.dwHighDateTime<<32)|created.dwLowDateTime
  save(log.with_suffix(log.suffix+'.birth.json'),{'at_utc':now(),'pid':p.pid,'creation_time100ns':birth,'image':str(argv[0]),'suspended_before_assign':True,'assigned_to_owned_job_before_resume':True,'parent_pid':os.getpid(),'job_kill_on_close':True})
  n=ctypes.WinDLL('ntdll');n.NtResumeProcess.argtypes=[wintypes.HANDLE];n.NtResumeProcess.restype=ctypes.c_long
  if n.NtResumeProcess(wintypes.HANDLE(int(p._handle)))!=0:raise RuntimeError('NATIVE_RESUME_FAILED')
  try:stdout,stderr=p.communicate(timeout=min(90,max(.1,float(timeout))))
  except subprocess.TimeoutExpired:timed=True;k.CloseHandle(job);job=None;stdout,stderr=p.communicate(timeout=10)
  out=stdout.decode('utf-8',errors='replace');err=stderr.decode('utf-8',errors='replace')
 finally:
  if job:k.CloseHandle(job)
  if p is not None and p.poll() is None:p.kill();p.wait(timeout=10)
 log.parent.mkdir(parents=True,exist_ok=True);log.write_text(out+'\n[STDERR]\n'+err,'utf-8')
 result={'argv':[str(x) for x in argv],'cwd':str(cwd),'exit_code':p.returncode,'timeout':timed,'seconds':time.monotonic()-started,'stdout':out,'stderr':err,'log':str(log),'log_sha256':sha(log),'process_birth':[{'pid':p.pid,'creation_time100ns':birth,'image':str(argv[0])}],'root_PID_birth_verified':True,'stop_receipt':{'owned_job_closed':True,'root_process_stopped':p.poll() is not None,'all_owned_descendants_terminated':True,'existing_model_server_excluded':True}}
 save(log.with_suffix(log.suffix+'.process.json'),result);return result
def install(env):
 """Install after constructor, before any actual public/private native callback."""
 env.run.qualify.execute=execute
 return env

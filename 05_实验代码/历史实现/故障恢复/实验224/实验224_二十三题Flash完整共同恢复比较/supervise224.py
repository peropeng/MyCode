"""Windows job closes all owned runner descendants on completion or hard deadline."""
import ctypes,subprocess
from ctypes import wintypes
from common166 import *
_time_authority={"hard_stop_utc":"2026-10-08T18:20:00+00:00"}
class Basic(ctypes.Structure):
 _fields_=[('PerProcessUserTimeLimit',ctypes.c_longlong),('PerJobUserTimeLimit',ctypes.c_longlong),('LimitFlags',wintypes.DWORD),('MinimumWorkingSetSize',ctypes.c_size_t),('MaximumWorkingSetSize',ctypes.c_size_t),('ActiveProcessLimit',wintypes.DWORD),('Affinity',ctypes.c_size_t),('PriorityClass',wintypes.DWORD),('SchedulingClass',wintypes.DWORD)]
class IO(ctypes.Structure):
 _fields_=[(n,ctypes.c_ulonglong) for n in ('ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount')]
class Extended(ctypes.Structure):
 _fields_=[('BasicLimitInformation',Basic),('IoInfo',IO),('ProcessMemoryLimit',ctypes.c_size_t),('JobMemoryLimit',ctypes.c_size_t),('PeakProcessMemoryUsed',ctypes.c_size_t),('PeakJobMemoryUsed',ctypes.c_size_t)]
def run():
 kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.CreateJobObjectW.restype=wintypes.HANDLE;kernel.CreateJobObjectW.argtypes=[ctypes.c_void_p,wintypes.LPCWSTR]
 kernel.SetInformationJobObject.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD];kernel.AssignProcessToJobObject.argtypes=[wintypes.HANDLE,wintypes.HANDLE];kernel.CloseHandle.argtypes=[wintypes.HANDLE]
 job=kernel.CreateJobObjectW(None,None)
 if not job:raise ctypes.WinError(ctypes.get_last_error())
 limits=Extended();limits.BasicLimitInformation.LimitFlags=0x2000
 if not kernel.SetInformationJobObject(job,9,ctypes.byref(limits),ctypes.sizeof(limits)):kernel.CloseHandle(job);raise ctypes.WinError(ctypes.get_last_error())
 log=E/'logs/pilot224.log';log.parent.mkdir(parents=True,exist_ok=True)
 with log.open('ab') as f:
  child=subprocess.Popen([str(PYTHON),'-B',str(E/'launch224.py')],cwd=W,stdout=f,stderr=subprocess.STDOUT,creationflags=0x08000000|0x00000004)
  if not kernel.AssignProcessToJobObject(job,wintypes.HANDLE(int(child._handle))):
   error=ctypes.get_last_error();child.kill();child.wait();kernel.CloseHandle(job);raise ctypes.WinError(error)
  created=wintypes.FILETIME();ended=wintypes.FILETIME();kt=wintypes.FILETIME();ut=wintypes.FILETIME()
  kernel.GetProcessTimes.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.FILETIME),ctypes.POINTER(wintypes.FILETIME),ctypes.POINTER(wintypes.FILETIME),ctypes.POINTER(wintypes.FILETIME)]
  if not kernel.GetProcessTimes(wintypes.HANDLE(int(child._handle)),ctypes.byref(created),ctypes.byref(ended),ctypes.byref(kt),ctypes.byref(ut)):kernel.CloseHandle(job);raise ctypes.WinError(ctypes.get_last_error())
  birth=(created.dwHighDateTime<<32)|created.dwLowDateTime
  nt=ctypes.WinDLL('ntdll');nt.NtResumeProcess.argtypes=[wintypes.HANDLE];nt.NtResumeProcess.restype=ctypes.c_long
  if nt.NtResumeProcess(wintypes.HANDLE(int(child._handle)))!=0:kernel.CloseHandle(job);raise RuntimeError('RUNNER_RESUME_FAILED')
  save(E/'supervision.json',{'at_utc':now(),'status':'RUNNING','runner_creation_time100ns':birth,'suspended_until_assigned_to_job':True,'birth_guard_installed':True,'runner_pid':child.pid,'supervisor_pid':os.getpid(),'job_kill_on_close':True,'existing_model_server_excluded_from_native_job':True,'hard_deadline_utc':_time_authority['hard_stop_utc']})
  timed_out=False
  try:exit_code=child.wait(timeout=max(.1,remaining()))
  except subprocess.TimeoutExpired:timed_out=True;kernel.CloseHandle(job);job=None;exit_code=child.wait(timeout=10)
  finally:
   if job:kernel.CloseHandle(job)
 save(E/'supervision.json',{'at_utc':now(),'status':'STOPPED','runner_pid':child.pid,'supervisor_pid':os.getpid(),'exit_code':exit_code,'runner_creation_time100ns':birth,'suspended_until_assigned_to_job':True,'hard_deadline_triggered':timed_out,'job_closed_all_owned_descendants_terminated':True,'model_server_excluded_from_native_job':True})
 print(canonical({'Exp224':'owned_runner_stopped','exit_code':exit_code,'runner_creation_time100ns':birth,'suspended_until_assigned_to_job':True,'hard_deadline_triggered':timed_out}),flush=True)
 sys.exit(exit_code if not timed_out else 124)
if __name__=='__main__':run()

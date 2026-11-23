"""Root-authorized external clock; terminate only the verified AL Job owner."""
from common166 import *
import ctypes
from ctypes import wintypes as w
from publicpack_v2_224 import V
K=ctypes.WinDLL('kernel32',use_last_error=True)
K.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];K.OpenProcess.restype=w.HANDLE
K.GetProcessTimes.argtypes=[w.HANDLE]+[ctypes.POINTER(w.FILETIME)]*4
K.TerminateProcess.argtypes=[w.HANDLE,w.UINT]
K.WaitForSingleObject.argtypes=[w.HANDLE,w.DWORD]
K.CloseHandle.argtypes=[w.HANDLE]
K.IsProcessInJob.argtypes=[w.HANDLE,w.HANDLE,ctypes.POINTER(w.BOOL)]
class Entry(ctypes.Structure):
 _fields_=[('size',w.DWORD),('usage',w.DWORD),('pid',w.DWORD),('heap',ctypes.c_size_t),('module',w.DWORD),('threads',w.DWORD),('parent',w.DWORD),('priority',w.LONG),('flags',w.DWORD),('exe',w.WCHAR*260)]
K.CreateToolhelp32Snapshot.argtypes=[w.DWORD,w.DWORD];K.CreateToolhelp32Snapshot.restype=w.HANDLE
K.Process32FirstW.argtypes=[w.HANDLE,ctypes.POINTER(Entry)];K.Process32NextW.argtypes=[w.HANDLE,ctypes.POINTER(Entry)]
def parents():
 h=K.CreateToolhelp32Snapshot(2,0);assert h and h!=ctypes.c_void_p(-1).value
 e=Entry();e.size=ctypes.sizeof(e);out={}
 try:
  ok=K.Process32FirstW(h,ctypes.byref(e))
  while ok:out[int(e.pid)]=int(e.parent);ok=K.Process32NextW(h,ctypes.byref(e))
 finally:K.CloseHandle(h)
 return out
def birth(h):
 a=[w.FILETIME() for _ in range(4)];assert K.GetProcessTimes(h,*[ctypes.byref(x) for x in a])
 return (a[0].dwHighDateTime<<32)|a[0].dwLowDateTime
def main():
 s=read(V/'supervision_main-agentless_v2astsafe.json');assert s['status']=='RUNNING' and s['job_kill_on_close']
 out=V/'main/recovery/getmoto__moto-5406/AGENTLESS_FSE2025_4L4P4T_FLASH'
 started=read(out/'worker_started.json');a=started['actual_worker']
 ids=[s['supervisor_pid'],a['logical_launcher_PID'],a['actual_self_PID']]
 assert ids==[69576,73028,67084]
 handles=[K.OpenProcess(0x100000|0x1000|(1 if i==0 else 0),False,p) for i,p in enumerate(ids)]
 assert all(handles)
 births=[birth(h) for h in handles];assert births[1:]==[134359740347816137,134359740348365978]
 p=parents();assert p[ids[1]]==ids[0] and p[ids[2]]==ids[1] and births[0]<=births[1]
 for h in handles[1:]:
  flag=w.BOOL();assert K.IsProcessInJob(h,None,ctypes.byref(flag)) and flag.value
 cutoff=datetime.datetime.fromisoformat('2026-10-08T23:28:32+00:00').timestamp()
 report={'at_utc':now(),'status':'ARMED','cutoff_utc':'2026-10-08T23:28:32+00:00','original_worker_started_utc':started['at_utc'],'PIDs':ids,'births100ns':births,'launcher_parent_and_worker_parent_verified':True,'worker_and_launcher_in_parent_owned_kill_on_close_Job':True,'no_model_native_private_Gold':0}
 save(V/'moto5406_external_deadline_stop_v2.json',report);print(canonical(report),flush=True)
 while time.time()<cutoff:time.sleep(min(.1,cutoff-time.time()))
 report['deadline_action_utc']=now()
 if K.WaitForSingleObject(handles[0],0)==258:
  assert birth(handles[0])==births[0]
  assert K.TerminateProcess(handles[0],124),'EXACT_OWNER_TERMINATION_FAILED'
 report['process_handles_signaled']=[K.WaitForSingleObject(h,10000)==0 for h in handles]
 assert all(report['process_handles_signaled']),'OWNED_JOB_NOT_CLOSED'
 report.update(status='STOPPED',at_utc=now(),parent_owner_handle_closed_triggered_kill_on_close=True,source_and_case_clock_not_modified=True)
 save(V/'moto5406_external_deadline_stop_v2.json',report)
 print(canonical(report),flush=True)
 for h in handles:K.CloseHandle(h)
if __name__=='__main__':main()

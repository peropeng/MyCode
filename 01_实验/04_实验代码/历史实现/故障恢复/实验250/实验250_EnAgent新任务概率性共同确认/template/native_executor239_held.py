"""Actual held-handle identity, specific Job membership and measured STOP."""
from common166 import *
import ctypes,subprocess,uuid
from ctypes import wintypes
class Basic(ctypes.Structure):
 _fields_=[('PerProcessUserTimeLimit',ctypes.c_longlong),('PerJobUserTimeLimit',ctypes.c_longlong),('LimitFlags',wintypes.DWORD),('MinimumWorkingSetSize',ctypes.c_size_t),('MaximumWorkingSetSize',ctypes.c_size_t),('ActiveProcessLimit',wintypes.DWORD),('Affinity',ctypes.c_size_t),('PriorityClass',wintypes.DWORD),('SchedulingClass',wintypes.DWORD)]
class IO(ctypes.Structure):
 _fields_=[(n,ctypes.c_ulonglong) for n in ('ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount')]
class Extended(ctypes.Structure):
 _fields_=[('BasicLimitInformation',Basic),('IoInfo',IO),('ProcessMemoryLimit',ctypes.c_size_t),('JobMemoryLimit',ctypes.c_size_t),('PeakProcessMemoryUsed',ctypes.c_size_t),('PeakJobMemoryUsed',ctypes.c_size_t)]
class Accounting(ctypes.Structure):
 _fields_=[('TotalUserTime',ctypes.c_longlong),('TotalKernelTime',ctypes.c_longlong),('ThisPeriodTotalUserTime',ctypes.c_longlong),('ThisPeriodTotalKernelTime',ctypes.c_longlong),('TotalPageFaultCount',wintypes.DWORD),('TotalProcesses',wintypes.DWORD),('ActiveProcesses',wintypes.DWORD),('TotalTerminatedProcesses',wintypes.DWORD)]
OS_ROOT_RESERVATIONS=1
PRODUCT_ROOT_RESERVATIONS=0
def api():
 k=ctypes.WinDLL('kernel32',use_last_error=True)
 definitions={
 'CreateJobObjectW':([ctypes.c_void_p,wintypes.LPCWSTR],wintypes.HANDLE),
 'SetInformationJobObject':([wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD],wintypes.BOOL),
 'AssignProcessToJobObject':([wintypes.HANDLE,wintypes.HANDLE],wintypes.BOOL),
 'IsProcessInJob':([wintypes.HANDLE,wintypes.HANDLE,ctypes.POINTER(wintypes.BOOL)],wintypes.BOOL),
 'QueryInformationJobObject':([wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(wintypes.DWORD)],wintypes.BOOL),
 'QueryFullProcessImageNameW':([wintypes.HANDLE,wintypes.DWORD,wintypes.LPWSTR,ctypes.POINTER(wintypes.DWORD)],wintypes.BOOL),
 'GetProcessId':([wintypes.HANDLE],wintypes.DWORD),
 'GetProcessTimes':([wintypes.HANDLE,ctypes.POINTER(wintypes.FILETIME),ctypes.POINTER(wintypes.FILETIME),ctypes.POINTER(wintypes.FILETIME),ctypes.POINTER(wintypes.FILETIME)],wintypes.BOOL),
 'TerminateJobObject':([wintypes.HANDLE,wintypes.UINT],wintypes.BOOL),
 'TerminateProcess':([wintypes.HANDLE,wintypes.UINT],wintypes.BOOL),
 'WaitForSingleObject':([wintypes.HANDLE,wintypes.DWORD],wintypes.DWORD),
 'CloseHandle':([wintypes.HANDLE],wintypes.BOOL)}
 for name,(args,result) in definitions.items():
  fn=getattr(k,name);fn.argtypes=args;fn.restype=result
 return k
def checked(value,label):
 if not value:raise RuntimeError(label+': '+str(ctypes.get_last_error()))
 return value
def held_birth(k,handle):
 pid=int(checked(k.GetProcessId(handle),'HELD_PROCESS_ID_UNKNOWN'))
 created=wintypes.FILETIME();ended=wintypes.FILETIME();kt=wintypes.FILETIME();ut=wintypes.FILETIME()
 checked(k.GetProcessTimes(handle,ctypes.byref(created),ctypes.byref(ended),ctypes.byref(kt),ctypes.byref(ut)),'HELD_BIRTH_QUERY_FAILED')
 birth=(created.dwHighDateTime<<32)|created.dwLowDateTime
 if birth<=0:raise RuntimeError('HELD_BIRTH_NOT_POSITIVE_ACTUAL_FILETIME')
 return {'pid':pid,'creation_time100ns':birth}
def held_identity(k,handle):
 result=held_birth(k,handle);size=wintypes.DWORD(32768);buffer=ctypes.create_unicode_buffer(size.value)
 checked(k.QueryFullProcessImageNameW(handle,0,buffer,ctypes.byref(size)),'HELD_IMAGE_QUERY_FAILED')
 result.update(image=buffer.value,actual_OS_image=buffer.value,
 identity_source='GetProcessId/GetProcessTimes/QueryFullProcessImageNameW on held process handle')
 return result
def membership(k,process,job):
 result=wintypes.BOOL()
 checked(k.IsProcessInJob(process,job,ctypes.byref(result)),'SPECIFIC_JOB_MEMBERSHIP_QUERY_FAILED')
 return bool(result.value)
def accounting(k,job):
 value=Accounting();length=wintypes.DWORD()
 checked(k.QueryInformationJobObject(job,1,ctypes.byref(value),ctypes.sizeof(value),ctypes.byref(length)),'SPECIFIC_JOB_ACCOUNTING_QUERY_FAILED')
 return {'active_processes':int(value.ActiveProcesses),'total_processes':int(value.TotalProcesses),
         'total_terminated_processes':int(value.TotalTerminatedProcesses)}
def stop_owned(k,job,process,assigned):
 observations=[];root_stopped=None;closed=False
 if job:
  before=accounting(k,job);observations.append(before)
  if before['active_processes']:checked(k.TerminateJobObject(job,0xE242),'OWNED_JOB_TERMINATION_FAILED')
 if process is not None:
  handle=wintypes.HANDLE(int(process._handle))
  if not assigned and k.WaitForSingleObject(handle,0)!=0:
   checked(k.TerminateProcess(handle,0xE242),'UNRESUMED_HELD_ROOT_TERMINATION_FAILED')
  root_stopped=k.WaitForSingleObject(handle,10000)==0
  if not root_stopped:raise RuntimeError('HELD_ROOT_STOP_NOT_OBSERVED')
 if job:
  deadline=time.monotonic()+10
  while True:
   current=accounting(k,job);observations.append(current)
   if current['active_processes']==0:break
   if time.monotonic()>=deadline:raise RuntimeError('OWNED_JOB_ACTIVE_PROCESS_STOP_UNKNOWN')
   time.sleep(.02)
  closed=bool(k.CloseHandle(job))
  if not closed:raise RuntimeError('OWNED_JOB_CLOSE_FAILED')
 return {'owned_job_closed':closed,'root_process_stopped':root_stopped,
 'all_owned_descendants_terminated':bool(observations and observations[-1]['active_processes']==0 and root_stopped),
 'job_active_processes_after_termination':observations[-1]['active_processes'] if observations else None,
 'actual_job_accounting_observations':observations,'assigned_root_verified_member':assigned,
 'STOP_evidence':'specific Job QueryInformationJobObject active=0 before CloseHandle; held root WaitForSingleObject=WAIT_OBJECT_0'}
def execute(argv,cwd,log,timeout=90,env=None,product_native=False):
 global OS_ROOT_RESERVATIONS,PRODUCT_ROOT_RESERVATIONS
 authorization();log=Path(log).resolve();assert log.is_relative_to(E.resolve())
 if OS_ROOT_RESERVATIONS>=MAX_ALL_OS_ROOTS:raise RuntimeError('EXP242_ALL_OS_ROOT_CAP')
 if product_native and PRODUCT_ROOT_RESERVATIONS>=MAX_PRODUCT_NATIVE_ROOTS:raise RuntimeError('EXP242_PRODUCT_NATIVE_ROOT_CAP')
 OS_ROOT_RESERVATIONS+=1;PRODUCT_ROOT_RESERVATIONS+=int(product_native)
 k=api();job_name='Exp242Native_'+str(os.getpid())+'_'+uuid.uuid4().hex
 child_env=os.environ.copy() if env is None else dict(env)
 child_env['COMMON_NATIVE_OWNED_JOB']=job_name
 job=checked(k.CreateJobObjectW(None,job_name),'OWNED_JOB_CREATE_FAILED')
 limits=Extended();limits.BasicLimitInformation.LimitFlags=0x2000
 try:checked(k.SetInformationJobObject(job,9,ctypes.byref(limits),ctypes.sizeof(limits)),'OWNED_JOB_KILL_ON_CLOSE_SET_FAILED')
 except Exception:k.CloseHandle(job);raise
 began=time.monotonic();p=None;assigned=False;resumed=False;timed=False
 identity=None;after_birth=None;receipt=None;stdout=b'';stderr=b'';failure=None
 try:
  p=subprocess.Popen([str(x) for x in argv],cwd=str(cwd),env=child_env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                     creationflags=0x08000000|0x00000004)
  handle=wintypes.HANDLE(int(p._handle));identity=held_identity(k,handle)
  if identity['pid']!=p.pid or Path(identity['actual_OS_image']).resolve()!=Path(argv[0]).resolve():
   raise RuntimeError('ACTUAL_HELD_ROOT_PID_OR_IMAGE_NOT_REQUESTED_EXECUTABLE')
  checked(k.AssignProcessToJobObject(job,handle),'OWNED_JOB_ASSIGN_FAILED')
  assigned=membership(k,handle,job)
  if not assigned:raise RuntimeError('HELD_ROOT_NOT_IN_SPECIFIC_OWNED_JOB')
  before=accounting(k,job)
  if before['active_processes']!=1:raise RuntimeError('PRE_RESUME_SPECIFIC_JOB_PROCESS_COUNT_UNKNOWN')
  save(log.with_suffix(log.suffix+'.birth.json'),{'at_utc':now(),**identity,'requested_image':str(argv[0]),
   'specific_job_name':job_name,'held_job_handle':int(job),'held_process_handle':int(p._handle),
   'specific_Job_membership_observed':assigned,'actual_job_before_resume':before,
   'created_suspended':True,'resumed':resumed,'parent_pid':os.getpid()})
  n=ctypes.WinDLL('ntdll');n.NtResumeProcess.argtypes=[wintypes.HANDLE];n.NtResumeProcess.restype=ctypes.c_long
  if n.NtResumeProcess(handle)!=0:raise RuntimeError('NATIVE_RESUME_FAILED')
  resumed=True
  try:stdout,stderr=p.communicate(timeout=min(NATIVE_TIMEOUT_SECONDS,max(.1,float(timeout))))
  except subprocess.TimeoutExpired:
   timed=True;checked(k.TerminateJobObject(job,0xE242),'TIMED_OUT_OWNED_JOB_TERMINATION_FAILED')
   stdout,stderr=p.communicate(timeout=10)
  after_birth=held_birth(k,handle)
  if after_birth!={key:identity[key] for key in ('pid','creation_time100ns')}:
   raise RuntimeError('ACTUAL_POST_RUN_HELD_ROOT_BIRTH_DRIFT')
 except Exception as exc:failure={'type':type(exc).__name__,'message':str(exc)}
 finally:
  try:receipt=stop_owned(k,job,p,assigned);job=None
  except Exception as stop_error:
   failure={'type':'NativeSTOPUnknown','message':str(stop_error),'original_failure':failure}
   receipt={'owned_job_closed':False,'root_process_stopped':None,'all_owned_descendants_terminated':None,
            'STOP_error':str(stop_error),'specific_job_name':job_name}
   if job:k.CloseHandle(job);job=None
 out=stdout.decode('utf-8',errors='replace');err=stderr.decode('utf-8',errors='replace')
 log.parent.mkdir(parents=True,exist_ok=True);log.write_text(out+'\n[STDERR]\n'+err,'utf-8')
 if p is not None:p.poll()
 verified=bool(identity and after_birth=={key:identity[key] for key in ('pid','creation_time100ns')} and assigned and resumed)
 receipt['specific_job_name']=job_name
 result={'argv':[str(x) for x in argv],'cwd':str(cwd),'exit_code':p.returncode if p is not None else None,
  'timeout':timed,'seconds':time.monotonic()-began,'stdout':out,'stderr':err,'log':str(log),'log_sha256':sha(log),
  'process_birth':[identity] if identity else [],'root_PID_birth_verified':verified,
  'actual_post_run_held_birth':after_birth,'root_resumed':resumed,'specific_Job_membership_observed':assigned,
  'stop_receipt':receipt,'native_failure':failure,
  'native_owned_job_environment_binding':{'COMMON_NATIVE_OWNED_JOB':job_name,'caller_env_not_mutated':True},
  'budget_root_reservations':{'all_OS_roots':OS_ROOT_RESERVATIONS,'product_native_roots':PRODUCT_ROOT_RESERVATIONS,
    'controller_or_worker_counted':1,'failed_birth_reservation_not_refunded':True}}
 save(log.with_suffix(log.suffix+'.process.json'),result)
 if failure:raise RuntimeError('EXP242_NATIVE_MECHANICAL_UNKNOWN '+canonical(failure))
 if not verified or not receipt.get('all_owned_descendants_terminated'):
  raise RuntimeError('EXP242_NATIVE_IDENTITY_OR_STOP_UNKNOWN')
 return result
def install(env):
 def scoped_product_execute(argv,cwd,log,timeout=90,env=None):
  return execute(argv,cwd,log,timeout=timeout,env=env,product_native=True)
 env.run.qualify.execute=scoped_product_execute
 return env

"""Future Windows owned-process runner; import creates no process or OS handle."""
import ctypes, os, struct, subprocess, threading, time, uuid, datetime
from dataclasses import asdict
from ctypes import wintypes as W
from contracts241 import EngineeringUnknown, sha
from supervision_classification241 import Observation, classify

class Basic(ctypes.Structure):
    _fields_=[('PerProcessUserTimeLimit',ctypes.c_longlong),('PerJobUserTimeLimit',ctypes.c_longlong),('LimitFlags',W.DWORD),('MinimumWorkingSetSize',ctypes.c_size_t),('MaximumWorkingSetSize',ctypes.c_size_t),('ActiveProcessLimit',W.DWORD),('Affinity',ctypes.c_size_t),('PriorityClass',W.DWORD),('SchedulingClass',W.DWORD)]
class IO(ctypes.Structure):
    _fields_=[(n,ctypes.c_ulonglong) for n in ('ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount')]
class Extended(ctypes.Structure):
    _fields_=[('BasicLimitInformation',Basic),('IoInfo',IO),('ProcessMemoryLimit',ctypes.c_size_t),('JobMemoryLimit',ctypes.c_size_t),('PeakProcessMemoryUsed',ctypes.c_size_t),('PeakJobMemoryUsed',ctypes.c_size_t)]
def kernel():
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    signatures={'GetCurrentProcess':([],W.HANDLE),'GetProcessTimes':([W.HANDLE,*([ctypes.POINTER(W.FILETIME)]*4)],W.BOOL),
        'GetModuleFileNameW':([W.HMODULE,W.LPWSTR,W.DWORD],W.DWORD),'CreateJobObjectW':([ctypes.c_void_p,W.LPCWSTR],W.HANDLE),
        'OpenJobObjectW':([W.DWORD,W.BOOL,W.LPCWSTR],W.HANDLE),'SetInformationJobObject':([W.HANDLE,ctypes.c_int,ctypes.c_void_p,W.DWORD],W.BOOL),
        'AssignProcessToJobObject':([W.HANDLE,W.HANDLE],W.BOOL),'IsProcessInJob':([W.HANDLE,W.HANDLE,ctypes.POINTER(W.BOOL)],W.BOOL),
        'QueryInformationJobObject':([W.HANDLE,ctypes.c_int,ctypes.c_void_p,W.DWORD,ctypes.POINTER(W.DWORD)],W.BOOL),
        'OpenProcess':([W.DWORD,W.BOOL,W.DWORD],W.HANDLE),'QueryFullProcessImageNameW':([W.HANDLE,W.DWORD,W.LPWSTR,ctypes.POINTER(W.DWORD)],W.BOOL),
        'GetExitCodeProcess':([W.HANDLE,ctypes.POINTER(W.DWORD)],W.BOOL),'WaitForSingleObject':([W.HANDLE,W.DWORD],W.DWORD),
        'CloseHandle':([W.HANDLE],W.BOOL),'TerminateJobObject':([W.HANDLE,W.UINT],W.BOOL)}
    for n,(args,result) in signatures.items(): getattr(k,n).argtypes=args; getattr(k,n).restype=result
    return k
def times(k,h):
    fs=[W.FILETIME() for _ in range(4)]
    if not k.GetProcessTimes(h,*[ctypes.byref(f) for f in fs]): raise EngineeringUnknown('PROCESS_TIMES_UNKNOWN')
    return [(f.dwHighDateTime<<32)|f.dwLowDateTime for f in fs]
def members(k,j):
    buf=ctypes.create_string_buffer(32776); size=W.DWORD()
    if not k.QueryInformationJobObject(j,3,buf,len(buf),ctypes.byref(size)): raise EngineeringUnknown('JOB_MEMBERS_UNKNOWN')
    count=struct.unpack_from('<II',buf.raw)[1];fmt='Q' if ctypes.sizeof(ctypes.c_size_t)==8 else 'I'
    return list(struct.unpack_from('<'+fmt*count,buf.raw,8)) if count else []
def observed(k,h,j,pid,required=False,record=None,job_name=None):
    inside=W.BOOL()
    member=bool(k.IsProcessInJob(h,j,ctypes.byref(inside)) and inside.value)
    times_read_error=None
    try:initial_ts=times(k,h)
    except EngineeringUnknown as error:
        times_read_error={'type':type(error).__name__,'message':str(error),'winerror':ctypes.get_last_error()}
        initial_ts=[None,None,None,None]
    ts=list(initial_ts);image=ctypes.create_unicode_buffer(32768);n=W.DWORD(len(image))
    good=bool(k.QueryFullProcessImageNameW(h,0,image,ctypes.byref(n)));error=None if good else ctypes.get_last_error()
    signaled=k.WaitForSingleObject(h,0)==0
    code=W.DWORD();exit_known=bool(k.GetExitCodeProcess(h,ctypes.byref(code)))
    refreshed=False;bounded_exit_completion_wait_ms=0
    if not good:
        signaled=k.WaitForSingleObject(h,0)==0
        # A known non-STILL_ACTIVE exit code may precede the process object
        # becoming signaled while final kernel cleanup finishes. Wait only
        # on this same held handle, never reopen a PID or certify a live image.
        if not required and not signaled and exit_known and code.value!=259:
            bounded_exit_completion_wait_ms=50
            signaled=k.WaitForSingleObject(h,50)==0
        if signaled:
            try:same_handle_times=times(k,h)
            except EngineeringUnknown as error:
                times_read_error={'type':type(error).__name__,'message':str(error),'winerror':ctypes.get_last_error()}
                same_handle_times=list(initial_ts)
            if initial_ts[0] is not None and same_handle_times[0]!=initial_ts[0]:raise EngineeringUnknown('HELD_HANDLE_BIRTH_CHANGED')
            ts=list(same_handle_times);refreshed=True
            exit_known=bool(k.GetExitCodeProcess(h,ctypes.byref(code)))
    fact=Observation(required,True,member,ts[0],image.value if good else None,error,
                     signaled,code.value if exit_known else None,ts[1])
    policy=classify(fact)
    if record is not None:
        record({'event':'PROCESS_OBSERVATION_BEFORE_ABORT','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'Job':job_name,'PID':pid,'raw_observation':asdict(fact),'initial_exit_time_100ns':initial_ts[1],
                'exit_times_refreshed_on_same_signaled_handle':refreshed,'times_read_error':times_read_error,'bounded_known_exit_completion_wait_ms':bounded_exit_completion_wait_ms,'classification':policy})
    return {'PID':pid,'creation_time100ns':ts[0],'OS_image':fact.image,'specific_Job_member':member,**policy}

def self_identity(job_name,expected_image):
    k=kernel();h=k.GetCurrentProcess();j=k.OpenJobObjectW(4,False,job_name)
    if not j: raise EngineeringUnknown('OWN_NAMED_JOB_NOT_OPEN')
    try:
        row=observed(k,h,j,os.getpid(),required=True);buf=ctypes.create_unicode_buffer(32768)
        n=k.GetModuleFileNameW(None,buf,len(buf))
        if row['abort_owned_job'] or not 0<n<len(buf) or os.path.normcase(os.path.realpath(buf.value))!=os.path.normcase(os.path.realpath(expected_image)):
            raise EngineeringUnknown('ACTUAL_SELF_PHYSICAL_PYTHON_OR_JOB_MISMATCH')
        return {**row,'actual_OS_image_GetModuleFileName':buf.value,'specific_named_Job':job_name,
                'IsProcessInJob_specific_own_Job':True,'pointer_bytes':ctypes.sizeof(ctypes.c_void_p),
                'before_product_import':True}
    finally:k.CloseHandle(j)

class JobRunner:
    def __init__(self,owner): self.owner=owner
    def execute(self,argv,cwd,log,timeout=90,env=None,stdin_text=None,controller=False):
        from pathlib import Path
        self.owner.require_action('native');self.owner.reserve_native()
        k=kernel();name='PatchPilotNative_'+str(os.getpid())+'_'+uuid.uuid4().hex;j=k.CreateJobObjectW(None,name)
        limits=Extended();limits.BasicLimitInformation.LimitFlags=0x2000
        if not j or not k.SetInformationJobObject(j,9,ctypes.byref(limits),ctypes.sizeof(limits)): raise EngineeringUnknown('CREATE_OWN_JOB_FAILED')
        actual=dict(env or {});actual['PATCHPILOT_JOB']=name
        if controller:actual['PATCHPILOT_CONTROLLER_JOB']=name
        actual['PATCHPILOT_ROOT_JOB_IMAGE']=str(argv[0])
        p=None; births={};metadata=[];io={};started=time.monotonic();timed=False
        try:
            p=subprocess.Popen(list(map(str,argv)),cwd=str(cwd),env=actual,stdin=subprocess.PIPE if stdin_text is not None else None,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                               creationflags=0x08000000|4)
            h=W.HANDLE(int(p._handle))
            if not k.AssignProcessToJobObject(j,h): raise EngineeringUnknown('SUSPENDED_ASSIGN_FAILED')
            root=observed(k,h,j,p.pid,required=True,record=self.owner.record,job_name=name)
            if root['abort_owned_job'] or os.path.normcase(os.path.realpath(root['OS_image']))!=os.path.normcase(os.path.realpath(str(argv[0]))):
                raise EngineeringUnknown('ACTUAL_ROOT_IMAGE_BEFORE_RESUME_MISMATCH')
            births[p.pid]=root;self.owner.record({'event':'NATIVE_ROOT_BIRTH','Job':name,'argv':list(map(str,argv)),'birth':root,'before_resume':True})
            nt=ctypes.WinDLL('ntdll');nt.NtResumeProcess.argtypes=[W.HANDLE];nt.NtResumeProcess.restype=ctypes.c_long
            if nt.NtResumeProcess(h)!=0: raise EngineeringUnknown('NATIVE_RESUME_FAILED')
            t=threading.Thread(target=lambda:io.update(data=p.communicate(input=stdin_text.encode('utf-8') if stdin_text is not None else None)),daemon=True);t.start()
            until=time.monotonic()+min(float(timeout),900 if controller else 90,self.owner.time_left())
            while t.is_alive():
                self.owner.require_action('observe',allow_no_new=True)
                for pid in members(k,j):
                    if pid in births:continue
                    child=k.OpenProcess(0x1000|0x100000,False,pid)
                    if not child:
                        # No held handle cannot certify identity. A stale PID
                        # removed from this same Job snapshot is metadata only.
                        if pid not in members(k,j):
                            metadata.append({'PID':pid,'status':'LEFT_JOB_BEFORE_HANDLE','qualified_image':False});continue
                        raise EngineeringUnknown('LIVE_DESCENDANT_HANDLE_UNKNOWN')
                    try:
                        row=observed(k,child,j,pid,record=self.owner.record,job_name=name)
                        if row['abort_owned_job']:raise EngineeringUnknown(row['status'])
                        if row['qualified_image']:births[pid]=row
                        else:metadata.append(row)
                    finally:k.CloseHandle(child)
                if time.monotonic()>=until:timed=True;k.TerminateJobObject(j,226);break
                t.join(.01)
            t.join(10)
            if t.is_alive() or p.poll() is None:raise EngineeringUnknown('OWNED_NATIVE_STOP_UNKNOWN')
            out,err=io['data'];k.TerminateJobObject(j,226)
            stop_by=time.monotonic()+3
            while members(k,j) and time.monotonic()<stop_by:time.sleep(.02)
            if members(k,j):raise EngineeringUnknown('OWNED_JOB_NOT_EMPTY')
            log=Path(log);log.parent.mkdir(parents=True,exist_ok=True)
            log.write_bytes(out+b'\n[STDERR]\n'+err)
            value={'executed':True,'exit_code':p.returncode,'timeout':timed,'stdout':out.decode('utf-8','replace'),
                   'stderr':err.decode('utf-8','replace'),'log':str(log),'log_sha256':sha(log),'births':list(births.values()),
                   'retired_descendant_metadata':metadata,'Job':name,'seconds':time.monotonic()-started,
                   'stop_receipt':{'root_stopped':True,'own_Job_empty_before_close':True,'descendants_stopped':True}}
            self.owner.record({'event':'NATIVE_ROOT_STOP',**value});return value
        except BaseException as error:
            self.owner.latch_unknown(error,stage='NATIVE_SUPERVISION');raise
        finally:
            empty=False;termination_requested=False;stop_error=None
            try:
                if j:
                    termination_requested=bool(k.TerminateJobObject(j,226))
                    stop_by=time.monotonic()+3
                    while members(k,j) and time.monotonic()<stop_by:time.sleep(.02)
                    empty=not bool(members(k,j))
                if p is not None and p.poll() is None:
                    try:p.wait(timeout=10)
                    except subprocess.TimeoutExpired:p.kill();p.wait(timeout=3)
            except BaseException as stop_exception:
                stop_error={'type':type(stop_exception).__name__,'message':str(stop_exception)}
            finally:
                try:
                    self.owner.record({'event':'SUPERVISION_FINALLY_STOP','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        'Job':name,'termination_requested':termination_requested,'known_births':list(births.values()),
                        'stop_receipt':{'root_stopped':p is None or p.poll() is not None,'own_Job_empty_before_close':empty,'descendants_stopped':empty},'stop_error':stop_error})
                finally:
                    if j:k.CloseHandle(j)

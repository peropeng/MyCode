"""Owned Job lifetime accounting and before-Popen checks; never touches unrelated jobs."""
import ctypes,os,subprocess,threading
from ctypes import wintypes as w
from common166 import *
from flow_bounds239 import check_count,require_time
import winjob225 as jobs
class Accounting(ctypes.Structure):
    _fields_=[(n,ctypes.c_longlong) for n in ('TotalUserTime','TotalKernelTime','ThisPeriodTotalUserTime','ThisPeriodTotalKernelTime')]+[(n,w.DWORD) for n in ('TotalPageFaultCount','TotalProcesses','ActiveProcesses','TotalTerminatedProcesses')]
def accounting(k,j):
    value=Accounting();size=w.DWORD()
    if not k.QueryInformationJobObject(j,1,ctypes.byref(value),ctypes.sizeof(value),ctypes.byref(size)):raise RuntimeError('OWN_JOB_LIFETIME_ACCOUNTING_UNKNOWN')
    return {n:int(getattr(value,n)) for n in ('TotalProcesses','ActiveProcesses','TotalTerminatedProcesses')}
def own_accounting():
    name=os.environ.get('EXP225_V2_PARENT_JOB')
    if not name:raise RuntimeError('SPECIFIC_PARENT_OWN_JOB_REQUIRED')
    k=jobs.kernel();j=k.OpenJobObjectW(4,False,name)
    if not j:raise RuntimeError('SPECIFIC_OWN_JOB_QUERY_FAILED')
    try:return accounting(k,j)
    finally:k.CloseHandle(j)
_original=None;_environment=None;_lock=threading.RLock()
def install_process_creation_guard(env=None):
    global _original,_environment
    if env is not None:_environment=env
    if _original is not None:return
    _original=subprocess.Popen
    def checked(*args,**kwargs):
        with _lock:
            try:
                require_open();p=authorization();left=remaining()
                if left<=0:raise RuntimeError('METHOD_SEARCH_WALL_BUDGET')
                counts=own_accounting()
                check_count(counts['TotalProcesses']+p.get('_pool_OS_root_offset',0),p['budget']['all_owned_OS_roots_total'],'ALL_OWNED_OS')
                if _environment is not None:_environment.record('all_owned_OS_lifetime_before_spawn239',counts)
                if os.name=='nt':kwargs['creationflags']=kwargs.get('creationflags',0)|0x08000000
                return _original(*args,**kwargs)
            except BaseException as exc:
                if _environment is not None:_environment._generation_fatal=exc
                raise
    checked._exp239_owned_process_budget=True
    subprocess.Popen=checked

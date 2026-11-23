"""Finite whole-flow owned Job; completion STOP watcher and lifetime process accounting."""
from common166 import *
import subprocess,ctypes
import winjob225 as jobs
from process_budget239 import accounting

def main():
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--task',required=True);a.add_argument('--mechanical',action='store_true');a.add_argument('--capture',action='store_true');a.add_argument('--masked-public',action='store_true');args=a.parse_args()
    mechanical=args.mechanical or args.capture or args.masked_public
    from control235 import verify,PHASE,start_mechanical
    if mechanical:start_mechanical()
    p=verify(args.task,PHASE);require_open();b=p['budget']
    seconds=300 if mechanical else finite_seconds(b['flow_wall_seconds'])
    begun=time.monotonic();finish=begun+seconds
    label=('masked_public_' if args.masked_public else 'mechanical_' if mechanical else '')+args.task
    out=E/'supervision'/label;out.mkdir(parents=True,exist_ok=False)
    program='mechanical_masked_public239.py' if args.masked_public else 'mechanical239.py' if mechanical else 'entry_sourceio_v4_239.py'
    argv=[str(PYTHON),'-X','utf8','-B',str(E/program),'--task',args.task]+(['--capture'] if mechanical and not args.masked_public else [])
    k=jobs.kernel();name='Exp239SixV3_'+str(os.getpid())+'_'+args.task.replace('-','_');j=k.CreateJobObjectW(None,name);assert j
    limits=jobs.Extended();limits.BasicLimitInformation.LimitFlags=0x2000|0x8
    limits.BasicLimitInformation.ActiveProcessLimit=b['all_owned_OS_roots_total']
    assert k.SetInformationJobObject(j,9,ctypes.byref(limits),ctypes.sizeof(limits))
    child=os.environ.copy()
    if mechanical:child.pop('DEEPSEEK_API_KEY',None)
    child.update(EXP225_V2_PARENT_JOB=name,EXP239_FLOW_DEADLINE_MONOTONIC=str(finish),PYTHONPATH=str(E),GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='core.longpaths',GIT_CONFIG_VALUE_0='true')
    process=None;birth=None;code=None;reason=None;peak=0;launch_error=None
    try:
        with (out/'worker.log').open('ab') as log:
            process=subprocess.Popen(argv,cwd=W,env=child,stdout=log,stderr=subprocess.STDOUT,creationflags=0x08000000|0x00000004)
            from ctypes import wintypes as w
            h=w.HANDLE(int(process._handle));assert k.AssignProcessToJobObject(j,h)
            birth=jobs.birth(k,h,j,process.pid)
            save(out/'supervision.json',{'status':'RUNNING','at_utc':now(),'specific_named_Job':name,'worker_birth':birth,'supervisor_pid':os.getpid(),'mechanical':mechanical,'global_deadline':None,'finite_flow_seconds':seconds,'monotonic_deadline':finish,'all_owned_OS_budget':b['all_owned_OS_roots_total']})
            nt=ctypes.WinDLL('ntdll');nt.NtResumeProcess.argtypes=[w.HANDLE];nt.NtResumeProcess.restype=ctypes.c_long;assert nt.NtResumeProcess(h)==0
            while process.poll() is None:
                counts=accounting(k,j);peak=max(peak,counts['TotalProcesses'])
                if request_closed():reason='USER_STOP_COMPLETION_FLAG'
                elif time.monotonic()>=finish:reason='FINITE_FLOW_WALL_TIMEOUT'
                elif counts['TotalProcesses']>b['all_owned_OS_roots_total']:reason='OWN_JOB_LIFETIME_PROCESS_CAP'
                if reason:k.TerminateJobObject(j,239);break
                try:process.wait(timeout=.1)
                except subprocess.TimeoutExpired:pass
            code=process.wait(timeout=10)
    except BaseException as exc:
        launch_error={'type':type(exc).__name__,'message':str(exc)}
        reason=reason or 'OWN_FLOW_LAUNCH_OR_ACCOUNTING_UNKNOWN'
    finally:
        if process is not None and process.poll() is None:k.TerminateJobObject(j,239);process.wait(timeout=10)
        if jobs.pids(k,j):k.TerminateJobObject(j,239)
        until=time.monotonic()+3
        while jobs.pids(k,j) and time.monotonic()<until:time.sleep(.02)
        assert not jobs.pids(k,j),'OWN_JOB_STILL_LIVE'
        final_counts=accounting(k,j);peak=max(peak,final_counts['TotalProcesses']);k.CloseHandle(j)
    save(out/'supervision.json',{'status':'STOPPED','at_utc':now(),'specific_named_Job':name,'worker_birth':birth,'supervisor_pid':os.getpid(),'exit_code':code,'termination_reason':reason,'launch_or_accounting_error':launch_error,'timeout':reason=='FINITE_FLOW_WALL_TIMEOUT','global_deadline':None,'finite_flow_seconds':seconds,'actual_elapsed_seconds':time.monotonic()-begun,'all_owned_OS_lifetime_counts':final_counts,'all_owned_OS_lifetime_peak_observed':peak,'all_owned_OS_budget':b['all_owned_OS_roots_total'],'own_Job_empty_before_close':True,'all_owned_descendants_stopped':True,'stop_or_budget_censor_never_scientific_success':bool(reason)})
    print(canonical({'status':'STOPPED','task':args.task,'exit_code':code,'reason':reason,'whole_flow_seconds':seconds}),flush=True)
    sys.exit(code or (239 if reason else 0))
if __name__=='__main__':main()

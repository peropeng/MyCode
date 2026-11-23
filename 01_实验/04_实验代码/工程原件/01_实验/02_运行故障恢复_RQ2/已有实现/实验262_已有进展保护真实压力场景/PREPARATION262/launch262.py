"""Hold a fresh controller in its exact kill-on-close Job until Root release.

The controller is CREATE_SUSPENDED; owner PID/birth/Job are persisted before
Root policy registration. No model/native code runs before an exact RESUME.
"""
import argparse, ctypes, subprocess, types
from stage_entry262 import authority, read, sha, ref, PYTHON as CONTROLLER, SITE as CONTROLLER_SITE, H
import copy,datetime,hashlib,importlib.util,json,os,sys,time
from pathlib import Path
SOURCE=H/'SOURCE';E=H;ROOT=Path('D:/Code/毕设/graduate-thesis-experiments')
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def owned(p):
 p=Path(p).resolve()
 if not p.is_relative_to(H):raise RuntimeError('EXP262_HELD_OWNER_WRITE_SCOPE')
 return p
def save(p,v):
 p=owned(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.'+str(os.getpid())+'.tmp')
 with tmp.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def jobs_module(guard):
 bridge=types.ModuleType('common166');bridge.__dict__.update(Path=Path,json=json,os=os,sys=sys,time=time,ROOT=ROOT,E=H,save=save,read=read,sha=sha,now=now,canonical=canonical,authorization=guard.check)
 sys.modules['common166']=bridge;p=SOURCE/'native_executor242_prospective.py';spec=importlib.util.spec_from_file_location('_exp262_actual_held_jobs',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


class LaunchGuard:
    def __init__(self,contract,grant,grant_path):self.contract=contract;self.grant=grant;self.grant_path=grant_path;self.grant_sha=sha(grant_path)
    def check(self,*args,**kwargs):
        if sha(self.grant_path)!=self.grant_sha or any(Path(p).exists() for p in self.grant['root_stop_paths']):raise RuntimeError('EXP262_PREPARATION_GRANT_CHANGED_OR_ROOT_STOP')
        if time.time()>=datetime.datetime.fromisoformat('2026-10-12T23:29:05+08:00').timestamp():raise RuntimeError('EXP262_WINDOW_STOP')
        seal=read(self.contract['method_source_seal']['path'])
        if sha(self.contract['method_source_seal']['path'])!=self.contract['method_source_seal']['sha256']:raise RuntimeError('EXP262_HELD_SOURCE_SEAL_DRIFT')
        for p,h in seal['sources'].items():
            if sha(p)!=h:raise RuntimeError('EXP262_HELD_RUNTIME_SOURCE_DRIFT')
        return True


def main():
    p=argparse.ArgumentParser();p.add_argument('--root-preparation-grant',required=True);p.add_argument('--trial',required=True);p.add_argument('--condition',required=True);p.add_argument('--policy',required=True);p.add_argument('--finance-grant',required=True);p.add_argument('--whole-grant',required=True);p.add_argument('--suspend-timeout',type=int,default=600);p.add_argument('--owner-directory',default='Root_owner600')
    args=p.parse_args();g,c,slot=authority(args.root_preparation_grant,args.trial,args.condition);args.contract=slot['contract']['path']
    if args.owner_directory!='Root_owner600' or args.suspend_timeout!=600:raise RuntimeError('EXP262_EXACT_FIRST_OWNER_READY600_REQUIRED')
    out=owned(c['output_root'])/args.owner_directory
    if out.exists():raise RuntimeError('EXP262_OWNER_STARTED_ONCE_NO_RECREATE')
    out.mkdir(parents=True);guard=LaunchGuard(c,g,args.root_preparation_grant);jobs=jobs_module(guard);k=jobs.api()
    name='RootExp262_Flow_'+digest({'contract':sha(args.contract),'T0':read(Path(c['output_root'])/'SCIENCE_T0_TRIAL_PREPARATION_STARTED.json')})[:24]
    job=jobs.checked(k.CreateJobObjectW(None,name),'EXP262_OWNED_FLOW_JOB_CREATE');limits=jobs.Extended();limits.BasicLimitInformation.LimitFlags=0x2000
    jobs.checked(k.SetInformationJobObject(job,9,ctypes.byref(limits),ctypes.sizeof(limits)),'EXP262_FLOW_KILL_ON_CLOSE')
    argv=[str(CONTROLLER),'-X','utf8','-B',str(SOURCE/'environment262.py'),'--contract',str(Path(args.contract).resolve()),'--execute','--policy',str(Path(args.policy).resolve()),'--finance-grant',str(Path(args.finance_grant).resolve()),'--whole-grant',str(Path(args.whole_grant).resolve())]
    process=None;assigned=False;birth=None;error=None;code=None;stop=None;resumed=False;whole=None
    # Key copied only as an inherited secret, never persisted in argv/log/body.
    child=dict(os.environ);child.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',EXP262_PARENT_JOB=name,
        PYTHONPATH=str(CONTROLLER_SITE)+(os.pathsep+os.environ['PYTHONPATH'] if os.environ.get('PYTHONPATH') else ''))
    save(out/'OWNER_INTENT.json',{'UTC':now(),'argv':argv,'specific_owned_Job':name,'suspended_before_Root_registration':True,'model_native_finance':0})
    try:
        with (out/'controller.log').open('xb') as log:
            process=subprocess.Popen(argv,cwd=str(SOURCE),env=child,stdout=log,stderr=subprocess.STDOUT,creationflags=0x08000000|4)
            held=jobs.wintypes.HANDLE(int(process._handle));birth=jobs.held_identity(k,held)
            if birth['pid']!=process.pid or Path(birth['actual_OS_image']).resolve()!=CONTROLLER.resolve():raise RuntimeError('EXP262_HELD_CONTROLLER_IDENTITY')
            jobs.checked(k.AssignProcessToJobObject(job,held),'EXP262_FLOW_ASSIGN_BEFORE_RESUME');assigned=jobs.membership(k,held,job)
            if not assigned:raise RuntimeError('EXP262_OWNER_EXACT_JOB_MEMBERSHIP')
            ready={'schema':'EXP262-suspended-owner-ready-for-Root-registration/1','UTC':now(),'task_id':c['task_id'],'control':c['policy'],'trial_id':c['trial_id'],
                   'owner_PID':birth['pid'],'owner_birth':str(birth['creation_time100ns']),'specific_owned_Job':name,'identity':birth,'assigned_before_resume':True,
                   'contract':{'path':str(Path(args.contract).resolve()),'sha256':sha(args.contract)},'caller_source_seal':c['method_source_seal'],
                   'original_T0':read(Path(c['output_root'])/'SCIENCE_T0_TRIAL_PREPARATION_STARTED.json'),'policy_path':str(Path(args.policy).resolve()),'finance_grant_path':str(Path(args.finance_grant).resolve()),'whole_grant_path':str(Path(args.whole_grant).resolve()),'resume_control':str(out/'ROOT_RESUME262.json'),'wait_seconds':args.suspend_timeout,'model_native_finance':0}
            save(out/'SUSPENDED_OWNER_READY.json',ready);print(canonical(ready),flush=True)
            until=time.monotonic()+args.suspend_timeout
            resume_path=out/'ROOT_RESUME262.json'
            while not resume_path.exists():
                guard.check()
                if process.poll() is not None:raise RuntimeError('EXP262_SUSPENDED_OWNER_EXITED')
                if time.monotonic()>until:raise RuntimeError('EXP262_ROOT_REGISTRATION_WAIT_EXPIRED')
                time.sleep(.2)
            resume=read(resume_path)
            if resume.get('root_authorized') is not True or resume.get('owner_PID')!=process.pid or resume.get('owner_birth')!=str(birth['creation_time100ns']) or resume.get('specific_owned_Job')!=name:raise RuntimeError('EXP262_ROOT_RESUME_IDENTITY_DRIFT')
            for key,path in (('policy',args.policy),('finance_grant',args.finance_grant),('whole_grant',args.whole_grant)):
                if resume.get(key)!={'path':str(Path(path).resolve()),'sha256':sha(path)}:raise RuntimeError('EXP262_ROOT_RESUME_AUTHORITY_SHA_DRIFT:'+key)
            whole=read(args.whole_grant)
            if whole.get('owner_PID')!=process.pid or whole.get('owner_birth')!=str(birth['creation_time100ns']) or whole.get('specific_owned_Job')!=name or whole.get('execution_authorized') is not True:raise RuntimeError('EXP262_WHOLE_OWNER_GRANT_REQUIRED')
            ntdll=ctypes.WinDLL('ntdll');ntdll.NtResumeProcess.argtypes=[jobs.wintypes.HANDLE];ntdll.NtResumeProcess.restype=ctypes.c_long
            if ntdll.NtResumeProcess(held)!=0:raise RuntimeError('EXP262_CONTROLLER_RESUME_FAILED')
            resumed=True;save(out/'ROOT_RESUMED262.json',{'UTC':now(),'owner':ready,'resume_SHA256':sha(resume_path),'whole_grant_SHA256':sha(args.whole_grant)})
            while process.poll() is None:
                guard.check()
                if any(Path(x).exists() for x in whole.get('root_stop_paths',[])):raise RuntimeError('EXP262_ROOT_FLOW_STOP')
                counts=jobs.accounting(k,job)
                if counts['active_processes']>16 or counts['total_processes']>128:raise RuntimeError('EXP262_COMMON_PROCESS_SAFETY_CAP')
                if time.monotonic()-ready['original_T0']['monotonic']>1800:raise RuntimeError('EXP262_FIXED_30MIN_BUDGET_CUTOFF')
                time.sleep(.2)
            code=process.wait(timeout=10)
    except BaseException as exc:error={'type':type(exc).__name__,'message':str(exc)}
    finally:
        try:stop=jobs.stop_owned(k,job,process,assigned);job=None
        except BaseException as exc:stop={'all_owned_descendants_terminated':None,'STOP_error':str(exc)}
        if job:k.CloseHandle(job)
        save(out/'PARENT_TERMINAL262.json',{'UTC':now(),'task_id':c['task_id'],'control':c['policy'],'trial_id':c['trial_id'],'exit_code':code,'error':error,'held_launcher':birth,'root_resumed':resumed,'stop_receipt':stop,'private_calls':0,'independent_once_only_external_after_STOP':True})
    print(canonical(read(out/'PARENT_TERMINAL262.json')),flush=True)
    if error or code!=0 or stop.get('all_owned_descendants_terminated') is not True:raise RuntimeError('EXP262_PARENT_FLOW_ENGINEERING_OR_BUDGET_CENSORED')

if __name__=='__main__':main()

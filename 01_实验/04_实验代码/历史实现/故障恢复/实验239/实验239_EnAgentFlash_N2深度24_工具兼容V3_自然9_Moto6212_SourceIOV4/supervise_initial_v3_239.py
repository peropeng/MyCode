"""Suspended hidden own Job; bounded whole flow and verified empty STOP."""
from common166 import *
import subprocess,ctypes
import winjob225 as jobs
PEER=ROOT/'工作区/1008-2320-exp224-flash-common/实验/实验224_二十三题Flash完整共同恢复比较'
sys.path.append(str(PEER))
def main():
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--task');a.add_argument('--mechanical',action='store_true');a.add_argument('--capture',action='store_true');args=a.parse_args()
 mechanical=args.mechanical or args.capture
 label=('mechanical' if args.mechanical else 'capture') if mechanical else args.task
 entry=E/('mechanical239.py' if mechanical else 'entry_initial_v3_239.py')
 argv=[str(PYTHON),'-X','utf8','-B',str(entry)]+(['--task',args.task] if args.task else [])+(['--capture'] if args.capture else [])
 if not mechanical:
  from control235 import verify,PHASE
  verify(args.task,PHASE)
 out=E/'supervision'/label
 if mechanical and out.exists():label=label+'_'+str(os.getpid());out=E/'supervision'/label
 out.mkdir(parents=True,exist_ok=False)
 k=jobs.kernel();name='Exp239_'+str(os.getpid())+'_'+label.replace('-','_');j=k.CreateJobObjectW(None,name);assert j
 limits=jobs.Extended();limits.BasicLimitInformation.LimitFlags=0x2000
 assert k.SetInformationJobObject(j,9,ctypes.byref(limits),ctypes.sizeof(limits))
 env=os.environ.copy()
 if mechanical:env.pop('DEEPSEEK_API_KEY',None)
 env['EXP225_V2_PARENT_JOB']=name
 env['PYTHONPATH']=str(ROOT/'工作区/1008-2320-exp224-flash-common/实验/实验224_二十三题Flash完整共同恢复比较')
 env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='core.longpaths',GIT_CONFIG_VALUE_0='true')
 p=None;timed=False;born=None;code=None
 try:
  with (out/'worker.log').open('ab') as log:
   p=subprocess.Popen(argv,cwd=W,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=0x08000000|0x00000004)
   from ctypes import wintypes as w
   h=w.HANDLE(int(p._handle));assert k.AssignProcessToJobObject(j,h)
   born=jobs.birth(k,h,j,p.pid)
   save(out/'supervision.json',{'status':'RUNNING','at_utc':now(),'specific_named_Job':name,'worker_birth':born,'supervisor_pid':os.getpid(),'mechanical':mechanical})
   nt=ctypes.WinDLL('ntdll');nt.NtResumeProcess.argtypes=[w.HANDLE];nt.NtResumeProcess.restype=ctypes.c_long;assert nt.NtResumeProcess(h)==0
   try:code=p.wait(timeout=min(300 if mechanical else 900,max(0,remaining())))
   except subprocess.TimeoutExpired:timed=True;k.TerminateJobObject(j,239);code=p.wait(timeout=10)
 finally:
  if p is not None and p.poll() is None:k.TerminateJobObject(j,239);p.wait(timeout=10)
  if jobs.pids(k,j):k.TerminateJobObject(j,239)
  until=time.monotonic()+3
  while jobs.pids(k,j) and time.monotonic()<until:time.sleep(.02)
  assert not jobs.pids(k,j),'OWN_JOB_STILL_LIVE'
  k.CloseHandle(j)
 save(out/'supervision.json',{'status':'STOPPED','at_utc':now(),'specific_named_Job':name,'worker_birth':born,'supervisor_pid':os.getpid(),'exit_code':code,'flow900_timeout':timed,'own_Job_empty_before_close':True,'all_owned_descendants_stopped':True})
 print(canonical({'status':'STOPPED','case':label,'exit_code':code,'timeout':timed}),flush=True)
 sys.exit(code)
if __name__=='__main__':main()

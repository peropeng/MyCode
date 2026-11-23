"""Unique hidden suspended qualification Job; no science/model authority."""
import pathlib,sys,os,subprocess,ctypes,time,json
E=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(E))
from common166 import *
sys.path.append(str(ROOT/'工作区/1008-2320-exp224-flash-common/实验/实验224_二十三题Flash完整共同恢复比较'))
import winjob225 as jobs
import control235
control235.start_mechanical();control235.verify('pydantic__pydantic-8567',control235.PHASE)
D=E/'qualification_v3_driver';run=D/('supervision_'+str(os.getpid()));run.mkdir(exist_ok=False)
kernel=jobs.kernel();name='EA239_V3_QUAL_'+str(os.getpid());job=kernel.CreateJobObjectW(None,name)
limits=jobs.Extended();limits.BasicLimitInformation.LimitFlags=0x2000
assert kernel.SetInformationJobObject(job,9,ctypes.byref(limits),ctypes.sizeof(limits))
env=os.environ.copy();env.pop('DEEPSEEK_API_KEY',None);env['EXP225_V2_PARENT_JOB']=name
env['PYTHONPATH']=str(ROOT/'工作区/1008-2320-exp224-flash-common/实验/实验224_二十三题Flash完整共同恢复比较')
env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='core.longpaths',GIT_CONFIG_VALUE_0='true')
process=None;birth=None;timed=False;code=None
try:
 with (run/'worker.log').open('ab') as log:
  process=subprocess.Popen([str(PYTHON),'-X','utf8','-B',str(D/'driver.py')],cwd=W,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=0x08000000|0x00000004)
  from ctypes import wintypes as win
  handle=win.HANDLE(int(process._handle));assert kernel.AssignProcessToJobObject(job,handle)
  birth=jobs.birth(kernel,handle,job,process.pid)
  save(run/'supervision.json',{'status':'RUNNING','specific_named_Job':name,'worker_birth':birth,'at_utc':now(),'driver_sha256':sha(D/'driver.py'),'models':0,'private':0})
  native=ctypes.WinDLL('ntdll');native.NtResumeProcess.argtypes=[win.HANDLE];native.NtResumeProcess.restype=ctypes.c_long;assert native.NtResumeProcess(handle)==0
  try:code=process.wait(timeout=min(300,remaining()))
  except subprocess.TimeoutExpired:timed=True;kernel.TerminateJobObject(job,239);code=process.wait(timeout=10)
finally:
 if process is not None and process.poll() is None:kernel.TerminateJobObject(job,239);process.wait(timeout=10)
 if jobs.pids(kernel,job):kernel.TerminateJobObject(job,239)
 until=time.monotonic()+3
 while jobs.pids(kernel,job) and time.monotonic()<until:time.sleep(.02)
 assert not jobs.pids(kernel,job)
 kernel.CloseHandle(job)
save(run/'supervision.json',{'status':'STOPPED','specific_named_Job':name,'worker_birth':birth,'at_utc':now(),'exit_code':code,'timeout':timed,'all_owned_descendants_stopped':True,'own_Job_empty_before_close':True,'driver_sha256':sha(D/'driver.py'),'models':0,'private':0})
print(canonical({'status':'STOPPED','exit_code':code,'timeout':timed,'directory':str(run)}))
sys.exit(code)

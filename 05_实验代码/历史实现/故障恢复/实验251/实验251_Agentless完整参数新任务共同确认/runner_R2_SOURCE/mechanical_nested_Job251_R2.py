"""Free synthetic OS-process/Job nesting; no method, network or trial actions."""
from runner251 import *

class MechanicalGrant:
 def check(self,full=False):return True

def parent_layer(h,jobs,out,stage,next_stage,active,total,root_name=None):
 out.mkdir(parents=True,exist_ok=True);k=jobs.api();name='RootExp251_Mechanical_R2_'+stage+'_'+uuid.uuid4().hex
 root_name=root_name or name
 argv=[str(CONTROLLER),'-X','utf8','-B',str(Path(__file__).resolve()),'--stage',next_stage,'--out',str(out.parent),'--root-name',root_name]
 child=clean_environment();child['COMMON_NATIVE_OWNED_JOB']=name;child['MECHANICAL_ROOT_JOB']=root_name
 job=jobs.checked(k.CreateJobObjectW(None,name),'R2_MECHANICAL_PARENT_CREATE');limits=jobs.Extended();limits.BasicLimitInformation.LimitFlags=0x2000|0x8;limits.BasicLimitInformation.ActiveProcessLimit=active
 jobs.checked(k.SetInformationJobObject(job,9,ctypes.byref(limits),ctypes.sizeof(limits)),'R2_MECHANICAL_PARENT_LIMITS')
 p=None;assigned=False;birth=None;code=None;error=None;stop=None;observations=[]
 try:
  with (out/'worker.log').open('xb') as log:
   p=subprocess.Popen(argv,cwd=str(HERE),env=child,stdout=log,stderr=subprocess.STDOUT,creationflags=0x08000000|4)
   held=jobs.wintypes.HANDLE(int(p._handle));birth=jobs.held_identity(k,held)
   if birth['pid']!=p.pid or Path(birth['actual_OS_image']).resolve()!=CONTROLLER.resolve():raise RuntimeError('R2_MECHANICAL_HELD_BIRTH')
   jobs.checked(k.AssignProcessToJobObject(job,held),'R2_MECHANICAL_ASSIGN');assigned=jobs.membership(k,held,job)
   if not assigned or jobs.accounting(k,job)['active_processes']!=1:raise RuntimeError('R2_MECHANICAL_PRE_RESUME')
   ntdll=ctypes.WinDLL('ntdll');ntdll.NtResumeProcess.argtypes=[jobs.wintypes.HANDLE];ntdll.NtResumeProcess.restype=ctypes.c_long
   if ntdll.NtResumeProcess(held)!=0:raise RuntimeError('R2_MECHANICAL_RESUME')
   deadline=time.monotonic()+40
   while p.poll() is None:
    counts=jobs.accounting(k,job);observations.append(counts)
    if counts['active_processes']>active or counts['total_processes']>total:raise RuntimeError('R2_MECHANICAL_PROCESS_CAP')
    if time.monotonic()>=deadline:raise RuntimeError('R2_MECHANICAL_TIMEOUT')
    time.sleep(.05)
   observations.append(jobs.accounting(k,job));code=p.wait(timeout=10)
 except BaseException as e:error={'type':type(e).__name__,'message':str(e)}
 finally:
  try:stop=jobs.stop_owned(k,job,p,assigned);job=None
  except BaseException as e:stop={'all_owned_descendants_terminated':None,'STOP_error':str(e)}
  if job:k.CloseHandle(job)
 value={'schema':'EXP251-R2-synthetic-nested-Job-layer/1','UTC':now(),'stage':stage,'synthetic_not_method_or_product_native':True,
  'active_cap':active,'total_cap':total,'specific_job_name':name,'held_launcher':birth,'exit_code':code,'error':error,
  'actual_accounting_observations':observations,'maximum_observed_active':max((v['active_processes'] for v in observations),default=0),
  'maximum_observed_total':max((v['total_processes'] for v in observations),default=0),'stop_receipt':stop,'model_API_finance_private_trial_actions':0}
 save(out/'LAYER_STOP.json',value)
 if error or code!=0 or stop.get('all_owned_descendants_terminated') is not True:raise RuntimeError('R2_MECHANICAL_LAYER_FAILED '+stage)
 return value

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['outer','worker','native-parent','native-worker','leaf','sleep-leaf'],default='outer');p.add_argument('--out');p.add_argument('--root-name');a=p.parse_args()
 out=Path(a.out).resolve() if a.out else HERE/'mechanical_checks'/('nested_'+uuid.uuid4().hex)
 if not out.is_relative_to(HERE/'mechanical_checks'):raise RuntimeError('R2_MECHANICAL_OUTPUT_SCOPE')
 h,jobs=load_jobs(MechanicalGrant())
 if a.stage=='outer':
  value=parent_layer(h,jobs,out/'outer','outer','worker',16,16384)
  native=read(out/'native-parent/LAYER_STOP.json');entry=read(out/'controller_entry.log.process.json');leaf=read(out/'native_leaf.log.process.json')
  if not h.stopped(entry) or not h.stopped(leaf):raise RuntimeError('R2_MECHANICAL_CONTROLLER_STOP')
  save(HERE/'RUNNER_NESTED_JOB_VALIDATION251_R2.json',{'schema':'EXP251-R2-free-nested-Job-validation/1','UTC':now(),'output':str(out),
   'structure':'runner parent16 > trusted worker > controller Job16 > native parent8/24 > native worker > held product-shaped leaf',
   'outer_layer':ref(out/'outer/LAYER_STOP.json'),'native_layer':ref(out/'native-parent/LAYER_STOP.json'),
   'controller_entry_STOP':ref(out/'controller_entry.log.process.json'),'native_leaf_STOP':ref(out/'native_leaf.log.process.json'),
   'actual_outer_peak_processes':value['maximum_observed_active'],'actual_native_parent_peak_processes':native['maximum_observed_active'],
   'all_owned_Job_STOP_observed':True,'actual_model_API_finance_private_current_trial_or_product_native_actions':0,'mechanical_only_not_scientific_comparison':True})
  print(canonical({'status':'R2_NESTED_JOB_MECHANICAL_PASS','outer_peak':value['maximum_observed_active'],'native_peak':native['maximum_observed_active'],'actual_model_API_product_native_private':0}),flush=True)
 elif a.stage=='native-parent':parent_layer(h,jobs,out/'native-parent','native-parent','native-worker',8,24,a.root_name)
 elif a.stage in ('worker','native-worker'):
  if not h.parent_member(jobs,os.environ['COMMON_NATIVE_OWNED_JOB']) or not h.parent_member(jobs,a.root_name):raise RuntimeError('R2_MECHANICAL_PARENT_MEMBERSHIP')
  script=HERE/'mechanical_nested_Job251_R2.py';next_stage='native-parent' if a.stage=='worker' else 'leaf';log=out/('controller_entry.log' if a.stage=='worker' else 'native_leaf.log')
  result=jobs.execute([str(CONTROLLER),'-X','utf8','-B',str(script),'--stage',next_stage,'--out',str(out),'--root-name',a.root_name],HERE,log,timeout=30,env=clean_environment(),product_native=False)
  if result['exit_code']!=0 or not h.stopped(result):raise RuntimeError('R2_MECHANICAL_CHILD_STOP')
 elif a.stage=='leaf':
  if not h.parent_member(jobs,os.environ['COMMON_NATIVE_OWNED_JOB']) or not h.parent_member(jobs,a.root_name):raise RuntimeError('R2_MECHANICAL_LEAF_PARENT_MEMBERSHIP')
  identity=module('_exp251_R2_mechanical_leaf_identity',IDENTITY).capture();save(out/'LEAF_SELF_IDENTITY.json',identity);time.sleep(1)
 elif a.stage=='sleep-leaf':time.sleep(1)
if __name__=='__main__':main()

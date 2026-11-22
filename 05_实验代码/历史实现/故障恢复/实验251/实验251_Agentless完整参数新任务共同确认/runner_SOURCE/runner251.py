"""Root-granted whole-trial boundary runner; unchanged sealed Agentless methods.

Import and false grants do not start a trial. Root must transfer one exact safe
boundary, including the immutable settled prefix, before worker authorization.
Private acceptance is never dispatched by this runner.
"""
import argparse,ctypes,datetime,hashlib,importlib.util,json,os,subprocess,sys,time,uuid
from pathlib import Path

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
METHOD_ROOT=HERE.parent
sys.path.insert(0,str(METHOD_ROOT))
import runtime251 as method
ROOT=method.ROOT
E249=method.E249
CONTROLLER=ROOT/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'
IDENTITY=E249/'physical_identity249.py'

def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,v):
 p=Path(p).resolve()
 if not p.is_relative_to(HERE):raise RuntimeError('EXP251_RUNNER_WRITE_SCOPE')
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.'+str(os.getpid())+'.tmp')
 with tmp.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def inside_trial(p,out):
 p=Path(p).resolve()
 if not p.is_relative_to(out):raise RuntimeError('EXP251_RUNNER_CROSS_TRIAL_PATH')
 return p
def exact_reference(value):
 if sha(value['path'])!=value['sha256']:raise RuntimeError('EXP251_RUNNER_REFERENCE_DRIFT '+value['path'])
 return read(value['path'])
def scan_model_prefix(out):
 rows=[]
 for slot in sorted((out/'calls').glob('call*')):
  ordinal=int(slot.name.removeprefix('call'));state_path=slot/'DISPATCH_STATE.json'
  if not state_path.exists():
   if (slot/'DISPATCH_OWNER_EXCLUSIVE.json').exists():raise RuntimeError('EXP251_RUNNER_ORPHAN_MODEL_OWNER_UNKNOWN')
   continue
  state=read(state_path)
  ready=read(slot/'FIRST_UNPOST_READY.json')
  if any(state.get(k)!=v or ready.get(k)!=v for k,v in (('method','AGENTLESS_FULL'),('task_id',out.parent.name),('trial_id',out.name),('call_ordinal',ordinal))):raise RuntimeError('EXP251_RUNNER_MODEL_PREFIX_CROSS_TRIAL_OR_ORDINAL')
  if state.get('status')!='SETTLED_RESPONSE_SAVED':raise RuntimeError('EXP251_RUNNER_MODEL_INFLIGHT_OR_UNKNOWN_NEVER_REPOST')
  stem=slot/'new_generation/llm';request=stem/('%03d_request.json'%ordinal);response=stem/('%03d_response.json'%ordinal);receipt=stem/('%03d_finance_receipt.json'%ordinal)
  rq=read(request);rp=read(response);rc=read(receipt);body=read(slot/'FIRST_UNPOST_BODY.json')
  if rc.get('status')!='SETTLED' or rq.get('body')!=body or rq.get('body_SHA256')!=digest(body) or state.get('body_SHA256')!=digest(body) or digest(rp)!=state.get('response_SHA256'):
   raise RuntimeError('EXP251_RUNNER_EXACT_FULL_SETTLED_RESPONSE_REQUIRED')
  if type(rp.get('usage',{}).get('completion_tokens')) is not int:raise RuntimeError('EXP251_RUNNER_SETTLED_USAGE_UNKNOWN')
  rows.append({'call':ordinal,'body_SHA256':digest(body),'request':ref(request),'response':ref(response),'receipt':ref(receipt),'state':ref(state_path),'output_tokens':rp['usage']['completion_tokens']})
 if [r['call'] for r in rows]!=list(range(1,len(rows)+1)):raise RuntimeError('EXP251_RUNNER_NONCONTIGUOUS_SETTLED_PREFIX')
 return rows
def scan_native_prefix(out):
 rows=[]
 for slot in sorted((out/'native_requests').glob('native*')):
  ordinal=int(slot.name.removeprefix('native'));completed=slot/'COMPLETED_PUBLIC.json'
  if not completed.exists():
   if (slot/'NATIVE_INTENT.json').exists() or (slot/'SUPERVISOR_STARTED_ONCE.json').exists():raise RuntimeError('EXP251_RUNNER_NATIVE_INFLIGHT_OR_UNKNOWN_NEVER_RERUN')
   continue
  r=method.verify_parent_completed(completed)
  if r.get('task_id')!=out.parent.name or r.get('trial_id')!=out.name:raise RuntimeError('EXP251_RUNNER_NATIVE_PREFIX_CROSS_TRIAL')
  if r['attempt']!=ordinal or sha(r['public_native_path'])!=r['public_native_SHA256']:raise RuntimeError('EXP251_RUNNER_NATIVE_PREFIX_DRIFT')
  rows.append({'native_ordinal':ordinal,'completed':ref(completed),'parent_STOP':ref(r['parent_supervision_path']),'original_public_native':ref(r['public_native_path']),'native_kind':r['native_kind']})
 if [r['native_ordinal'] for r in rows]!=list(range(1,len(rows)+1)):raise RuntimeError('EXP251_RUNNER_NONCONTIGUOUS_NATIVE_PREFIX')
 return rows

class Grant:
 def __init__(self,path):
  self.path=Path(path).resolve();self.sha256=sha(self.path);self.value=read(self.path);self.active_command=False
  self.check(full=True)
  self.contract_path=Path(self.value['trial_contract']['path']).resolve();self.contract,self.trial,*_=method.checked_contract(self.contract_path)
  runid=self.value['runner_run_id']
  if not isinstance(runid,str) or runid.startswith('ROOT_TO_FILL') or not runid or len(runid)>80 or any(ch not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for ch in runid):raise RuntimeError('EXP251_RUNNER_NEW_RUN_ID_REQUIRED')
  self.out=HERE/'runs'/self.contract['task_id']/self.contract['trial_id']/self.value['runner_run_id']
  if not self.out.resolve().is_relative_to(HERE/'runs'):raise RuntimeError('EXP251_RUNNER_RUN_NAMESPACE')
 def check(self,full=False):
  g=self.value
  if sha(self.path)!=self.sha256 or any(g.get(k) is not True for k in ('root_authorized','whole_trial_execution_authorized','preparation_authorized','model_authorized','finance_authorized','native_authorized')):
   raise RuntimeError('EXP251_WHOLE_TRIAL_ROOT_GRANT_CLOSED_OR_CHANGED')
  if any(g.get(k) is not False for k in ('private_authorized','once_private_authorized','new_encoder_authorized','new_download_authorized')) or g.get('maximum_final_private_native')!=0:
   raise RuntimeError('EXP251_RUNNER_PRIVATE_ENCODER_DOWNLOAD_ALWAYS_CLOSED')
  if (g.get('maximum_trial_model_requests')!=88 or g.get('maximum_trial_product_native')!=121 or g.get('maximum_new_controller_commands')!=1024
      or g.get('method_parameters_unchanged') is not True or g.get('unknown_or_inflight_never_resent') is not True
      or g.get('source_or_response_reuse_across_trials') is not False):raise RuntimeError('EXP251_RUNNER_EXACT_CORE_OR_OPERATIONAL_LIMITS')
  if time.time()>=datetime.datetime.fromisoformat(g['lease_end_UTC']).timestamp() or any(Path(p).exists() for p in g.get('hard_stop_paths',[])):
   raise RuntimeError('EXP251_RUNNER_HARD_STOP_OR_LEASE')
  if not self.active_command and any(Path(p).exists() for p in g.get('safe_boundary_stop_paths',[])):
   raise SafeBoundaryStop('EXP251_RUNNER_REQUESTED_SAFE_BOUNDARY_STOP')
  if full:
   c=exact_reference(g['trial_contract']);seal=exact_reference(g['runner_source_seal'])
   for p,h in seal['sources_SHA256'].items():
    if sha(p)!=h:raise RuntimeError('EXP251_RUNNER_SOURCE_DRIFT '+p)
   for p,h in seal['inputs_SHA256'].items():
    if sha(p)!=h:raise RuntimeError('EXP251_RUNNER_INPUT_DRIFT '+p)
   if g['method_source_seal']!=c['method_source_seal'] or g['finance_configuration']!=c['finance_configuration'] or g['finance_phase']!=c['finance_phase']:
    raise RuntimeError('EXP251_RUNNER_METHOD_SOURCE_CONFIG_PHASE_DRIFT')
   method.verify_source_seal(c['method_source_seal']['path']);exact_reference(g['method_source_seal']);exact_reference(g['finance_configuration'])
   if g['method']!=c['method'] or g['task_id']!=c['task_id'] or g['trial_id']!=c['trial_id'] or c['method']!='AGENTLESS_FULL':raise RuntimeError('EXP251_RUNNER_EXACT_METHOD_TASK_TRIAL')
   if g['controller_launch_python']!=str(CONTROLLER) or sha(CONTROLLER)!=g['controller_launch_SHA256']:
    raise RuntimeError('EXP251_RUNNER_WORKING_CONTROLLER')
  return True

class SafeBoundaryStop(RuntimeError):pass

def load_jobs(grant):
 sys.path.insert(0,str(E249));h=module('_exp251_runner_Root_native_helper',E249/'native249_ROOT_MASK_V3_CAPACITY.py')
 h.save=save;h.owned=lambda p:Path(p).resolve() if Path(p).resolve().is_relative_to(HERE) else (_ for _ in ()).throw(RuntimeError('EXP251_RUNNER_HELPER_WRITE_SCOPE'))
 jobs=h.load_jobs(grant);jobs.MAX_ALL_OS_ROOTS=1026;return h,jobs

def inspect_handoff(grant):
 g=grant.value;out=Path(read(g['trial_contract']['path'])['output_root']).resolve()
 handoff=exact_reference(g['Root_handoff_boundary'])
 if (handoff.get('Root_safe_boundary_accepted') is not True or handoff.get('no_active_previous_model_or_native_owner') is not True
     or handoff.get('method')!=g['method'] or handoff.get('task_id')!=g['task_id'] or handoff.get('trial_id')!=g['trial_id']
     or handoff.get('contract_SHA256')!=g['trial_contract']['sha256']):raise RuntimeError('EXP251_RUNNER_EXPLICIT_ROOT_SAFE_HANDOFF_REQUIRED')
 if handoff.get('prior_runner_parent_STOP'):
  parent=exact_reference(handoff['prior_runner_parent_STOP'])
  if parent.get('exit_code') is None or parent.get('stop_receipt',{}).get('all_owned_descendants_terminated') is not True:raise RuntimeError('EXP251_RUNNER_PREVIOUS_PARENT_NOT_STOPPED')
 current_status=handoff['current_method_STATUS'];inside_trial(current_status['path'],out);exact_reference(current_status)
 t0=handoff['original_trial_T0'];inside_trial(t0['path'],out);clock=exact_reference(t0)
 if clock.get('real_preparation_time_included') is not True or clock.get('task_id')!=g['task_id'] or clock.get('trial_id')!=g['trial_id']:
  raise RuntimeError('EXP251_RUNNER_ORIGINAL_T0_REQUIRED_NO_RESET')
 models=scan_model_prefix(out);natives=scan_native_prefix(out)
 if models!=handoff['complete_settled_same_trial_model_prefix'] or natives!=handoff['complete_STOP_same_trial_native_prefix']:
  raise RuntimeError('EXP251_RUNNER_HANDOFF_PREFIX_CHANGED_OR_UNKNOWN')
 return handoff,models,natives

def owned_controller_command(grant,h,jobs,argv,kind,state):
 grant.check(full=True)
 if len(state['commands'])>=grant.value['maximum_new_controller_commands']:raise RuntimeError('EXP251_RUNNER_CONTROLLER_RESOURCE_CENSOR')
 ordinal=len(state['commands'])+1;step=grant.out/'steps'/('%04d'%ordinal);intent=step/'INTENT_NO_AUTORETRY.json'
 if intent.exists():raise RuntimeError('EXP251_RUNNER_COMMAND_ALREADY_INTENDED_UNKNOWN_NO_RETRY')
 save(intent,{'UTC':now(),'kind':kind,'argv':argv,'argv_SHA256':digest(argv),'grant_SHA256':grant.sha256,'original_T0':state['original_trial_T0']})
 grant.active_command=True
 try:result=jobs.execute(argv,METHOD_ROOT,step/'controller.log',timeout=max(.1,min(86400,datetime.datetime.fromisoformat(grant.value['lease_end_UTC']).timestamp()-time.time())),product_native=False)
 finally:grant.active_command=False
 if not h.stopped(result) or result['exit_code']!=0 or result.get('timeout'):
  save(step/'UNKNOWN_COMMAND_RESULT.json',result);raise RuntimeError('EXP251_RUNNER_COMMAND_UNKNOWN_NO_REPEAT')
 save(step/'COMPLETE_COMMAND_RESULT.json',result)
 state['commands'].append({'ordinal':ordinal,'kind':kind,'argv_SHA256':digest(argv),'receipt':ref(step/'COMPLETE_COMMAND_RESULT.json'),'actual_own_Job_STOP':True})
 save(grant.out/'RUNNER_STATE.json',state);return result

def actual_from_false(grant,false_path,target,kind):
 f=read(false_path)
 if any(f.get(k) is not False for k in ('root_authorized','model_authorized','finance_authorized','native_authorized','private_authorized')):
  raise RuntimeError('EXP251_RUNNER_EXPECTED_ALL_FALSE_ACTION_TEMPLATE')
 for k in ('method','task_id','trial_id'):
  if f[k]!=grant.value[k]:raise RuntimeError('EXP251_RUNNER_FALSE_ACTION_CROSS_TRIAL')
 f['root_authorized']=True
 if kind=='prepare':f['preparation_authorized']=True
 elif kind=='model':f['model_authorized']=True;f['finance_authorized']=True
 elif kind=='native':f['native_authorized']=True
 else:raise RuntimeError('EXP251_RUNNER_NO_PRIVATE_ACTION_KIND')
 f['lease_end_UTC']=grant.value['lease_end_UTC'];f['root_stop_paths']=list(grant.value.get('hard_stop_paths',[]))
 f['Root_whole_trial_runner_grant']={'path':str(grant.path),'sha256':grant.sha256};f['Root_original_trial_T0_preserved']=True
 save(target,f);return target

def worker(grant,h,jobs):
 g=grant.value
 if not h.parent_member(jobs,g['parent_owned_job_name']):raise RuntimeError('EXP251_RUNNER_WORKER_NOT_IN_OWN_PARENT_JOB')
 identity=module('_exp251_runner_fixed_identity',IDENTITY).capture();identity['before_model_and_product_clients_import']=True
 expected=g['qualified_controller_physical_identity']
 if (identity.get('specific_named_Job_membership') is not True or identity.get('specific_job_name')!=g['parent_owned_job_name']
     or identity.get('actual_OS_image_SHA256')!=expected['actual_OS_image_SHA256'] or Path(identity['actual_OS_image']).resolve()!=Path(expected['actual_OS_image']).resolve()):raise RuntimeError('EXP251_RUNNER_ACTUAL_CONTROLLER_IDENTITY')
 save(grant.out/'WORKER_SELF_IDENTITY.json',identity)
 handoff,models,natives=inspect_handoff(grant);out=grant.trial
 if len(models)>88 or len(natives)>121:raise RuntimeError('EXP251_RUNNER_EXISTING_PREFIX_EXCEEDS_CORE_MAXIMUM')
 state={'schema':'EXP251-independent-complete-trial-runner-state/1','status':'RUNNING','UTC':now(),'method':g['method'],'task_id':g['task_id'],'trial_id':g['trial_id'],
  'Root_grant':{'path':str(grant.path),'sha256':grant.sha256},'original_trial_T0':handoff['original_trial_T0'],'handoff':g['Root_handoff_boundary'],
  'settled_prefix_at_takeover':models,'native_STOP_prefix_at_takeover':natives,'commands':[],'new_requests_dispatched':0,'new_product_native_dispatched':0,
  'same_trial_conditional_continuation_not_new_repeat':bool(models or natives),'private_calls':0,'method_parameters_changed':False,'method_source_seal':g['method_source_seal']}
 save(grant.out/'RUNNER_STATE.json',state)
 prep_false=METHOD_ROOT/'grant_templates'/g['task_id']/(g['trial_id']+'.PREPARATION_FALSE.json')
 prep_actual=actual_from_false(grant,prep_false,grant.out/'action_grants/PREPARATION_ACTUAL.json','prepare')
 consume=[str(CONTROLLER),'-X','utf8','-B',str(METHOD_ROOT/'entry251.py'),'--contract',str(grant.contract_path),'--root-preparation-grant',str(prep_actual)]
 try:
  # The exact known prefix is consumed first. Existing SETTLED requests are not
  # sent through dispatch, and existing completed natives are not rerun.
  owned_controller_command(grant,h,jobs,consume,'PURE_SAME_TRIAL_CONSUME',state)
  while True:
   grant.check(full=True);models=scan_model_prefix(out);natives=scan_native_prefix(out)
   if len(models)>88 or len(natives)>121:raise RuntimeError('EXP251_RUNNER_CORE_BOUNDARY_COUNTS_EXCEEDED')
   status=read(out/'STATUS.json');state.update(current_method_STATUS=ref(out/'STATUS.json'),actual_total_settled_calls=len(models),actual_total_output_tokens=sum(r['output_tokens'] for r in models),actual_total_completed_product_native=len(natives),UTC=now())
   if status['status']=='PUBLIC_ONLY_NATURAL_TERMINAL':
    owned_controller_command(grant,h,jobs,[str(CONTROLLER),'-X','utf8','-B',str(METHOD_ROOT/'freeze_final251_SOURCE.py'),'--contract',str(grant.contract_path)],'FREEZE_COMPLETE_PUBLIC_AUTHOR_SELECTION',state)
    state.update(status='COMPLETE_PUBLIC_AUTHOR_SELECTION_FROZEN_AWAIT_ROOT_PRIVATE' if (out/'frozen_final/FINAL_READY.json').exists() else 'COMPLETE_AUTHOR_PUBLIC_NATURAL_FAILURE_FROZEN',private_calls=0)
    break
   if status['status']=='MODEL_READY_NOT_POSTED':
    slot=inside_trial(status['ready_dir'],out);ready=read(slot/'FIRST_UNPOST_READY.json')
    if ready.get('source_preview_only') is not False or ready['call_ordinal']!=len(models)+1 or len(models)>=88:raise RuntimeError('EXP251_RUNNER_NEXT_MODEL_NOT_EXACT_DECLARED_SLOT')
    if (slot/'DISPATCH_STATE.json').exists():raise RuntimeError('EXP251_RUNNER_PREPARED_SLOT_ALREADY_DISPATCHED_OR_UNKNOWN')
    owned_controller_command(grant,h,jobs,[str(CONTROLLER),'-X','utf8','-B',str(METHOD_ROOT/'prepare_false_grants251_SOURCE.py'),'--model-ready-dir',str(slot)],'FALSE_SINGLE_MODEL_TEMPLATE',state)
    actual=actual_from_false(grant,slot/'ROOT_EXACT_MODEL_GRANT_FALSE.json',grant.out/'action_grants'/('model%03d_ACTUAL.json'%ready['call_ordinal']),'model')
    owned_controller_command(grant,h,jobs,[str(CONTROLLER),'-X','utf8','-B',str(METHOD_ROOT/'dispatch_once251_ROOT_ONLY.py'),'--ready-dir',str(slot),'--root-grant',str(actual)],'EXACT_SINGLE_MODEL_DISPATCH',state)
    state['new_requests_dispatched']+=1
   elif status['status']=='PUBLIC_NATIVE_READY':
    ready_path=inside_trial(status['ready_path'],out);ready=read(ready_path)
    if ready['attempt']!=len(natives)+1 or len(natives)>=121:raise RuntimeError('EXP251_RUNNER_NEXT_NATIVE_NOT_EXACT_DECLARED_SLOT')
    if (ready_path.parent/'NATIVE_INTENT.json').exists() or (ready_path.parent/'SUPERVISOR_STARTED_ONCE.json').exists():raise RuntimeError('EXP251_RUNNER_NATIVE_ALREADY_STARTED_OR_UNKNOWN')
    owned_controller_command(grant,h,jobs,[str(CONTROLLER),'-X','utf8','-B',str(METHOD_ROOT/'prepare_false_grants251_SOURCE.py'),'--native-ready',str(ready_path)],'FALSE_SINGLE_NATIVE_TEMPLATE',state)
    actual=actual_from_false(grant,ready_path.parent/'ROOT_PUBLIC_NATIVE_GRANT_FALSE.json',grant.out/'action_grants'/('native%03d_ACTUAL.json'%ready['attempt']),'native')
    owned_controller_command(grant,h,jobs,[str(CONTROLLER),'-X','utf8','-B',str(METHOD_ROOT/'native_once251_ROOT_ONLY.py'),'--ready',str(ready_path),'--root-grant',str(actual)],'EXACT_SINGLE_PRODUCT_NATIVE',state)
    state['new_product_native_dispatched']+=1
   elif status['status'] in ('ENGINEERING_UNKNOWN','DEPLOYMENT_RESOURCE_CENSORED','MODEL_INFLIGHT_OR_UNKNOWN_NO_RESEND','NATIVE_INFLIGHT_OR_UNKNOWN_NO_RERUN'):
    state.update(status='STOPPED_UNKNOWN_OR_RESOURCE_CENSOR_NO_RETRY',method_status=status);break
   else:raise RuntimeError('EXP251_RUNNER_UNDECLARED_METHOD_BOUNDARY '+status['status'])
   save(grant.out/'RUNNER_STATE.json',state)
   owned_controller_command(grant,h,jobs,consume,'PURE_SAME_TRIAL_CONSUME',state)
 except SafeBoundaryStop as e:state.update(status='STOPPED_AT_REQUESTED_SAFE_BOUNDARY',reason=str(e))
 except BaseException as e:
  state.update(status='STOPPED_UNKNOWN_NO_RETRY',error={'type':type(e).__name__,'message':str(e)});save(grant.out/'RUNNER_STATE.json',state);raise
 finally:
  state['UTC']=now();save(grant.out/'RUNNER_STATE.json',state)
 print(canonical({'status':state['status'],'task_id':g['task_id'],'trial_id':g['trial_id'],'private_calls':0}),flush=True)

def supervise(grant,h,jobs):
 out=grant.out
 if out.exists():raise RuntimeError('EXP251_RUNNER_RUN_ALREADY_STARTED_NO_AUTORETRY')
 out.mkdir(parents=True);g=grant.value;name=g['parent_owned_job_name']
 if not name.startswith('RootExp251_WholeTrial_'):raise RuntimeError('EXP251_RUNNER_PARENT_JOB_NAMESPACE')
 argv=[str(CONTROLLER),'-X','utf8','-B',str(Path(__file__).resolve()),'--root-trial-grant',str(grant.path),'--worker']
 save(out/'SUPERVISOR_INTENT_ONCE.json',{'UTC':now(),'argv':argv,'Root_grant_SHA256':grant.sha256,'specific_parent_Job':name})
 k=jobs.api();job=jobs.checked(k.CreateJobObjectW(None,name),'EXP251_RUNNER_PARENT_CREATE');limits=jobs.Extended();limits.BasicLimitInformation.LimitFlags=0x2000
 jobs.checked(k.SetInformationJobObject(job,9,ctypes.byref(limits),ctypes.sizeof(limits)),'EXP251_RUNNER_PARENT_KILL_ON_CLOSE')
 p=None;assigned=False;birth=None;code=None;error=None;stop=None
 child={key:os.environ[key] for key in ('SystemRoot','WINDIR','SYSTEMDRIVE','PATH','TEMP','TMP','USERPROFILE','LOCALAPPDATA') if key in os.environ};child.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',COMMON_NATIVE_OWNED_JOB=name)
 try:
  with (out/'worker.log').open('xb') as log:
   p=subprocess.Popen(argv,cwd=str(HERE),env=child,stdout=log,stderr=subprocess.STDOUT,creationflags=0x08000000|4)
   held=jobs.wintypes.HANDLE(int(p._handle));birth=jobs.held_identity(k,held)
   if birth['pid']!=p.pid or Path(birth['actual_OS_image']).resolve()!=CONTROLLER.resolve():raise RuntimeError('EXP251_RUNNER_HELD_LAUNCHER_IDENTITY')
   jobs.checked(k.AssignProcessToJobObject(job,held),'EXP251_RUNNER_PARENT_ASSIGN');assigned=jobs.membership(k,held,job)
   if not assigned or jobs.accounting(k,job)['active_processes']!=1:raise RuntimeError('EXP251_RUNNER_PARENT_PRE_RESUME_MEMBERSHIP')
   save(out/'PARENT_HELD_BIRTH.json',{'identity':birth,'specific_parent_Job':name,'assigned_before_resume':True})
   ntdll=ctypes.WinDLL('ntdll');ntdll.NtResumeProcess.argtypes=[jobs.wintypes.HANDLE];ntdll.NtResumeProcess.restype=ctypes.c_long
   if ntdll.NtResumeProcess(held)!=0:raise RuntimeError('EXP251_RUNNER_WORKER_RESUME')
   while p.poll() is None:
    # Soft stop is consumed by the worker only between complete commands.
    grant.active_command=True
    try:grant.check()
    finally:grant.active_command=False
    accounting=jobs.accounting(k,job)
    if accounting['active_processes']>32 or accounting['total_processes']>16384:raise RuntimeError('EXP251_RUNNER_PARENT_PROCESS_CAP')
    time.sleep(.2)
   code=p.wait(timeout=10)
 except BaseException as e:error={'type':type(e).__name__,'message':str(e)}
 finally:
  try:stop=jobs.stop_owned(k,job,p,assigned);job=None
  except BaseException as e:stop={'all_owned_descendants_terminated':None,'STOP_error':str(e)}
  if job:k.CloseHandle(job)
 parent={'UTC':now(),'method':g['method'],'task_id':g['task_id'],'trial_id':g['trial_id'],'runner_run_id':g['runner_run_id'],'exit_code':code,'error':error,'held_launcher':birth,'stop_receipt':stop,'Root_grant_SHA256':grant.sha256,'private_calls':0,'natural_algorithm_outcome_not_inferred_from_STOP':True}
 save(out/'PARENT_TERMINAL_RUNNER.json',parent)
 if error or code!=0 or stop.get('all_owned_descendants_terminated') is not True:raise RuntimeError('EXP251_RUNNER_PARENT_UNKNOWN_PRESERVE_PARTIAL_NO_RETRY')
 print(canonical({'status':'COMPLETE_RUNNER_RETURNED_AND_ALL_OWNED_STOPPED','receipt':str(out/'PARENT_TERMINAL_RUNNER.json'),'private_calls':0}),flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--root-trial-grant',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();grant=Grant(a.root_trial_grant);h,jobs=load_jobs(grant)
 if a.worker:worker(grant,h,jobs)
 else:inspect_handoff(grant);supervise(grant,h,jobs)
if __name__=='__main__':main()

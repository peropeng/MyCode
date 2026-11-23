"""One Root-authorized exact G/O public native, guarded original runtime, held Jobs."""
import argparse, contextlib, copy, ctypes, datetime, hashlib, json, os, subprocess, sys, time, types
from pathlib import Path
from dispatch248 import E,R,read,save,sha,digest,canonical,load,now
OLD=R/'工作区/1011-our19'
SCHEDULING=R/'工作区/1010-unified-six/ROOT_COMMON_NATIVE_SCHEDULING_V5_FOUR_SOURCE.json'
SCHEDULING_SHA='883a0524ae6d4f6ae0f4546dfd413bfa4a33218768319e0a0835ee9092f5e074'
HELPER_SHA='62f5364a19df43f9c27d989cfdefd79376e3b25b41fbb001cf6b906e140609ea'
sys.dont_write_bytecode=True

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--ready',required=True);parser.add_argument('--root-grant',required=True);parser.add_argument('--worker',action='store_true');args=parser.parse_args()
 ready_path=Path(args.ready).resolve();grant_path=Path(args.root_grant).resolve()
 if not ready_path.is_relative_to(E):raise RuntimeError('EXP248_NATIVE_READY_OUTSIDE_OWN_SCOPE')
 ready=read(ready_path);grant=read(grant_path);grant_hash=sha(grant_path)
 out=Path(ready['native_output']).resolve()
 if not out.is_relative_to(E/'forward'):raise RuntimeError('EXP248_NATIVE_OUTPUT_SCOPE')
 deadline=datetime.datetime.fromisoformat(grant['forward_lease_end_UTC']).timestamp()
 def require():
  if sha(grant_path)!=grant_hash:raise RuntimeError('EXP248_NATIVE_GRANT_CHANGED')
  if (grant.get('root_authorized') is not True or grant.get('native_authorized') is not True
      or grant.get('model_authorized') is not False or grant.get('private_authorized') is not False
      or grant.get('max_new_public_native')!=1 or grant['task_id']!=ready['task_id']
      or grant['ready_SHA256']!=sha(ready_path)
      or grant['candidate_source_inventory_SHA256']!=digest(ready['candidate_source_sha256'])):
   raise RuntimeError('EXP248_EXACT_PUBLIC_NATIVE_GRANT_CLOSED')
  if time.time()>=deadline or Path(grant['forward_stop_path']).exists():raise RuntimeError('EXP248_PUBLIC_NATIVE_STOP_OR_LEASE')
 def full_check():
  require()
  for path,h in grant['sources_SHA256'].items():
   if sha(path)!=h:raise RuntimeError('EXP248_PUBLIC_NATIVE_SOURCE_DRIFT '+path)
  if grant['sources_SHA256'].get(str(Path(__file__).resolve()))!=sha(__file__):raise RuntimeError('EXP248_NATIVE_SOURCE_NOT_BOUND')
  if sha(ready['business_source_file'])!=ready['business_source_file_SHA256']:raise RuntimeError('EXP248_CANDIDATE_SOURCE_FILE_DRIFT')
  for item in (ready['original_masked_scope'],ready['original_oracle_contract']):
   if sha(item['path'])!=item['sha256']:raise RuntimeError('EXP248_PUBLIC_CONTRACT_DRIFT')
  if sha(SCHEDULING)!=SCHEDULING_SHA:raise RuntimeError('EXP248_V5_NATIVE_CONTRACT_DRIFT')
  scheduling=read(SCHEDULING)
  if sha(scheduling['source_path'])!=HELPER_SHA or scheduling['native_slot_offsets']!=[1,2,4,5]:raise RuntimeError('EXP248_V5_NATIVE_HELPER_DRIFT')
  return scheduling
 scheduling=full_check()
 sys.path.insert(0,str(OLD))
 jobs=load('_exp248_native_jobs',OLD/'native_executor242_prospective.py')
 jobs.E=E;jobs.save=save;jobs.authorization=require
 jobs.MAX_ALL_OS_ROOTS=int(grant.get('all_owned_OS_roots_total',8));jobs.MAX_PRODUCT_NATIVE_ROOTS=1
 jobs.NATIVE_TIMEOUT_SECONDS=int(grant['per_native_timeout_seconds'])
 if not 1<=jobs.NATIVE_TIMEOUT_SECONDS<=300:raise RuntimeError('EXP248_NATIVE_TIMEOUT_SCOPE')
 jobs.OS_ROOT_RESERVATIONS=2
 if not args.worker:
  launch=out/'SUPERVISOR_STARTED.json'
  if launch.exists() or (out/'COMPLETED_PUBLIC.json').exists():raise RuntimeError('EXP248_NATIVE_ALREADY_STARTED_NO_RERUN')
  name=grant['parent_owned_job_name']
  if not name.startswith('RootExp248Public_'):raise RuntimeError('EXP248_PARENT_JOB_NAME')
  python=Path(grant['controller_python']).resolve()
  argv=[str(python),'-X','utf8','-B',str(Path(__file__).resolve()),'--ready',str(ready_path),'--root-grant',str(grant_path),'--worker']
  with launch.open('x',encoding='utf-8') as stream:
   json.dump({'at_utc':now(),'argv':argv,'root_grant_SHA256':grant_hash,'specific_named_Job':name,'native_not_yet_started':True},stream,ensure_ascii=False,indent=2)
   stream.flush();os.fsync(stream.fileno())
  k=jobs.api();job=jobs.checked(k.CreateJobObjectW(None,name),'EXP248_PARENT_JOB_CREATE');limits=jobs.Extended();limits.BasicLimitInformation.LimitFlags=0x2000
  jobs.checked(k.SetInformationJobObject(job,9,ctypes.byref(limits),ctypes.sizeof(limits)),'EXP248_PARENT_KILL_ON_CLOSE')
  process=None;assigned=False;birth=None;code=None;error=None;stop=None
  try:
   with (out/'worker.log').open('xb') as log:
    process=subprocess.Popen(argv,cwd=str(E),env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},stdout=log,stderr=subprocess.STDOUT,creationflags=0x08000000|4)
    held=jobs.wintypes.HANDLE(int(process._handle));birth=jobs.held_identity(k,held)
    if Path(birth['actual_OS_image']).resolve()!=python:raise RuntimeError('EXP248_CONTROLLER_HELD_IMAGE_DRIFT')
    jobs.checked(k.AssignProcessToJobObject(job,held),'EXP248_PARENT_ASSIGN');assigned=jobs.membership(k,held,job)
    if not assigned:raise RuntimeError('EXP248_PARENT_MEMBERSHIP_UNKNOWN')
    save(out/'PARENT_BIRTH.json',{'identity':birth,'specific_named_Job':name,'assigned_before_resume':True})
    ntdll=ctypes.WinDLL('ntdll');ntdll.NtResumeProcess.argtypes=[jobs.wintypes.HANDLE];ntdll.NtResumeProcess.restype=ctypes.c_long
    if ntdll.NtResumeProcess(held)!=0:raise RuntimeError('EXP248_WORKER_RESUME_FAILED')
    while process.poll() is None:
     require()
     if jobs.accounting(k,job)['total_processes']>jobs.MAX_ALL_OS_ROOTS:raise RuntimeError('EXP248_ALL_OWNED_OS_ROOT_CAP')
     time.sleep(.25)
    code=process.wait(timeout=10)
  except BaseException as exc:error={'type':type(exc).__name__,'message':str(exc)}
  finally:
   try:stop=jobs.stop_owned(k,job,process,assigned);job=None
   except BaseException as exc:stop={'all_owned_descendants_terminated':None,'STOP_error':str(exc)}
   if job:k.CloseHandle(job)
  save(out/'SUPERVISION.json',{'task':ready['task_id'],'at_utc':now(),'exit_code':code,'error':error,'worker_birth':birth,'stop_receipt':stop,'success_not_inferred_from_exit':True})
  if error or code!=0 or stop.get('all_owned_descendants_terminated') is not True:raise RuntimeError('EXP248_PUBLIC_NATIVE_SUPERVISION_UNKNOWN')
  print(canonical({'status':'PUBLIC_NATIVE_RETURNED_AND_STOPPED','task':ready['task_id'],'completed_path':str(out/'COMPLETED_PUBLIC.json')}),flush=True)
  return
 # Worker belongs to the exact Root named Job before any product process.
 k=jobs.api();k.OpenJobObjectW.argtypes=[jobs.wintypes.DWORD,jobs.wintypes.BOOL,jobs.wintypes.LPCWSTR];k.OpenJobObjectW.restype=jobs.wintypes.HANDLE
 k.GetCurrentProcess.argtypes=[];k.GetCurrentProcess.restype=jobs.wintypes.HANDLE
 handle=k.OpenJobObjectW(4,False,grant['parent_owned_job_name'])
 if not handle:raise RuntimeError('EXP248_ROOT_PARENT_JOB_NOT_OPEN')
 try:
  if not jobs.membership(k,k.GetCurrentProcess(),handle):raise RuntimeError('EXP248_NATIVE_WORKER_NOT_IN_ROOT_PARENT_JOB')
 finally:k.CloseHandle(handle)
 if (out/'NATIVE_INTENT.json').exists():raise RuntimeError('EXP248_NATIVE_INFLIGHT_OR_UNKNOWN_NO_RERUN')
 source=read(ready['business_source_file']);source_sha={rel:hashlib.sha256(text.encode()).hexdigest() for rel,text in source.items()}
 if source_sha!=ready['candidate_source_sha256']:raise RuntimeError('EXP248_CANDIDATE_SOURCE_SHA_MISMATCH')
 active=out/'runtime';repo=active/'repo';repo.mkdir(parents=True,exist_ok=False)
 for rel,text in source.items():
  dest=(repo/rel).resolve()
  if not dest.is_relative_to(repo.resolve()) or dest.suffix!='.py' or 'tests' in Path(rel).parts:raise RuntimeError('EXP248_NONBUSINESS_SOURCE')
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(text.encode())
 protocol=ready['original_runtime_contract'];spec=protocol['shared_masked_native_source']
 for path,h in spec['guard_sources_sha256'].items():
  if sha(path)!=h:raise RuntimeError('EXP248_SHARED_MASKED_NATIVE_SOURCE_DRIFT')
 masked=load('_exp248_shared_masked',spec['path']);scope=masked.load_scope(protocol,ready['task_id'])
 supports=masked.materialize_support(repo,scope,source_sha);masked.verify_actor(repo,source_sha,supports)
 if digest({**source_sha,**supports})!=ready['candidate_snapshot']['inventory_sha256']:raise RuntimeError('EXP248_MATERIALIZED_SNAPSHOT_INVENTORY_DRIFT')
 oracle=next(row for row in read(ready['original_oracle_contract']['path'])['tasks'] if row['task_id']==ready['task_id'])
 if oracle['target_nodes']!=ready['goal_nodes'] or oracle['ordinary_nodes']!=ready['ordinary_nodes'] or oracle['private_hidden_feedback_to_model'] is not False:raise RuntimeError('EXP248_PUBLIC_NODE_SCOPE_DRIFT')
 ref=ready['ref'];frozen=Path(ref['frozen_tests'])
 if frozen.resolve()!=Path(oracle['trusted_native_oracle_root']).resolve():raise RuntimeError('EXP248_TRUSTED_PUBLIC_ORACLE_ROOT_DRIFT')
 common150=load('_exp248_native_loader',R/'工作区/1006-exp150-unified-recovery/实验/实验150_统一任务排序与恢复/common150.py')
 run=common150.load_replay()
 evidence=[];env=types.SimpleNamespace(run=run,package=ref['package'],record=lambda stage,data:evidence.append({'stage':stage,'evidence':data}))
 jobs.install(env)
 capacity=load('_exp248_native_capacity',OLD/'native_capacity_v10.py');capacity.NATIVE_TIMEOUT_SECONDS=jobs.NATIVE_TIMEOUT_SECONDS;capacity.install(env)
 scheduler=load('_exp248_common_four_slots',scheduling['source_path'])
 nodes=list(dict.fromkeys(ready['goal_nodes']+ready['ordinary_nodes']))
 native_out=out/'actual'
 with (out/'NATIVE_INTENT.json').open('x',encoding='utf-8') as stream:
  json.dump({'at_utc':now(),'task':ready['task_id'],'candidate_inventory':ready['candidate_snapshot']['inventory_sha256'],'nodes':nodes,'root_grant_SHA256':grant_hash,'resend_or_rerun_on_unknown':False},stream,ensure_ascii=False,indent=2)
  stream.flush();os.fsync(stream.fileno())
 with scheduler.native_lane(scheduling['lock_path'],ref['package'],require,lambda value:evidence.append({'stage':'common_four_slot_scheduler','evidence':value})):
  full_check();masked.verify_actor(repo,source_sha,supports)
  result=run.probe(active,frozen,nodes,native_out,Path(ref['python']),ref['package'],time.monotonic()+min(jobs.NATIVE_TIMEOUT_SECONDS,max(.1,deadline-time.time())))
 # Validate complete identity/guard/coverage/STOP, not just pytest exit status.
 from progress_guard240 import observe
 validation={'native_record':result,'outcomes':{n:result.get('pytest',{}).get('outcomes',{}).get(n,{}) for n in ready['ordinary_nodes']}}
 observed=observe(validation,ready['goal_nodes'],ready['ordinary_nodes'])
 masked.verify_actor(repo,source_sha,supports)
 if {rel:sha(repo/rel) for rel in source_sha}!=source_sha:raise RuntimeError('EXP248_NATIVE_MUTATED_BUSINESS_SOURCE')
 save(out/'NATIVE_TRANSPORT_EVIDENCE.json',evidence)
 save(out/'COMPLETED_PUBLIC.json',{'task_id':ready['task_id'],'attempt':ready['attempt'],'candidate_snapshot':ready['candidate_snapshot'],
   'candidate_source_sha256':source_sha,'public_native_path':str(native_out/'run.json'),'public_native_SHA256':sha(native_out/'run.json'),
   'ordinary_all_pass':observed['ordinary_pass'],'goal_actual_pass':sorted(observed['goal_pass']),'failed_goals':observed['failed_goals'],
   'native_calls':1,'private':0,'model':0,'root_grant_SHA256':grant_hash,'at_utc':now()})
if __name__=='__main__':main()

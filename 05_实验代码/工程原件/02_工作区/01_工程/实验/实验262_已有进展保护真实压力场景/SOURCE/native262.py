"""Complete original G/O boundary; current Root receipt only, never hidden IO."""
import inspect
from common262 import *
def candidate_native(env,snapshot,label):
 env.check_execution();out=owned(env.out/'native_public'/label);out.mkdir(parents=True,exist_ok=True)
 state=source_sha(env);business=out/'CANDIDATE_BUSINESS_SOURCE.json';save(business,env.files)
 ready={'schema':'EXP262-current-partial-candidate-original-G-O-ready/1','task_id':env.task_id,'policy':env.condition,'trial_id':env.contract['trial_id'],'candidate_snapshot':snapshot,'candidate_business_source':{'path':str(business),'sha256':sha(business)},'candidate_source_sha256':state,'candidate_source_inventory_SHA256':digest(state),'goal_nodes':env.recovery_goal_nodes,'ordinary_nodes':env.public_regression_nodes,'Root_current_partial_start':env.contract['current_partial_start'],'native_output':str(out),'one_original_G_O_native':True,'model_private_finance':0}
 save(out/'NATIVE_READY.json',ready)
 receipt=out/'ROOT_COMPLETED_PUBLIC.json'
 if not receipt.exists():
  delegate_current_candidate(env,out,ready,state)
 value=read(receipt)
 if value.get('candidate_source_inventory_SHA256')!=digest(state) or value.get('task_id')!=env.task_id or value.get('policy')!=env.condition or value.get('trial_id')!=env.contract['trial_id']:raise RuntimeError('EXP262_CANDIDATE_NATIVE_RECEIPT_NOT_EXACT_TRIAL_SOURCE')
 parent=verify_ref(value['parent_stop_ref'])
 if parent.get('exit_code')!=0 or parent.get('timeout') or not parent.get('stop_receipt',{}).get('all_owned_descendants_terminated'):raise RuntimeError('EXP262_CANDIDATE_PARENT_STOP_UNKNOWN')
 native=read(value['public_native_path'])
 if sha(value['public_native_path'])!=value['public_native_SHA256'] or native['requested_nodes']!=env.recovery_goal_nodes+env.public_regression_nodes:raise RuntimeError('EXP262_CANDIDATE_ORIGINAL_G_O_DRIFT')
 if not native.get('completed_guarded_coverage') or not native.get('guard_loaded') or not native.get('business_state_unchanged') or not native.get('frozen_tests_unchanged'):raise RuntimeError('EXP262_CANDIDATE_INCOMPLETE_OR_UNGUARDED_NATIVE')
 return value
def source_sha(env):return {p:hashlib.sha256(t.encode()).hexdigest() for p,t in sorted(env.files.items())}
def delegate_current_candidate(env,out,ready,state):
 import types
 import inspect
 env.check_execution();g=env.whole_grant
 if g.get('delegate_exact_child_actions_authorized') is not True or g.get('native_execution_authorized') is not True:raise RuntimeError('EXP262_EXACT_NATIVE_CHILD_NOT_ROOT_DELEGATED')
 if any((out/p).exists() for p in ('DELEGATED_CONTROLLER_INTENT.json','PARENT_NATIVE_CONTROLLER_STOP.json','native_once/NATIVE_INTENT.json','native_once/ROOT_COMPLETED_PUBLIC.json')):raise RuntimeError('EXP262_NATIVE_INFLIGHT_OR_UNKNOWN_NO_REDISPATCH')
 base=read(E/'NATIVE_READY262_FALSE.json');runtime=out/'runtime/repo';runtime.mkdir(parents=True,exist_ok=False)
 for rel,text in env.files.items():
  p=(runtime/rel).resolve()
  if not p.is_relative_to(runtime.resolve()) or not rel.startswith('moto/') or not rel.endswith('.py'):raise RuntimeError('EXP262_CANDIDATE_ILLEGAL_BUSINESS_SCOPE')
  p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(text.encode('utf-8'))
 state_path=out/'CANDIDATE_STATE.json';save(state_path,{'source_root':str(runtime),'business_SHA256':state,'business_inventory_SHA256':digest(state)})
 base.update(native_output=str(out/'native_once'),partial_state={'path':str(state_path),'sha256':sha(state_path)},policy=env.condition,trial_id=env.contract['trial_id'])
 delegated_ready=out/'DELEGATED_NATIVE_READY.json';save(delegated_ready,base)
 grant={'schema':'Root-EXP262-once-native-only/1','root_authorized':True,'native_authorized':True,'model_authorized':False,'private_authorized':False,'finance_authorized':False,'ready':{'path':str(delegated_ready),'sha256':sha(delegated_ready)},'maximum_new_original_G_O_native':1,'lease_end_UTC':g['lease_end_UTC'],'root_stop_paths':g['root_stop_paths'],'source_seal':env.contract['method_source_seal'],'delegated_by_exact_Root_whole_grant_SHA256':env.whole_grant_SHA256}
 grant_path=out/'DELEGATED_NATIVE_ONLY_GRANT.json';save(grant_path,grant)
 with (out/'DELEGATED_CONTROLLER_INTENT.json').open('x',encoding='utf-8') as f:
  f.write(canonical({'grant_ref':{'path':str(grant_path),'sha256':sha(grant_path)},'candidate_source_inventory_SHA256':digest(state),'no_automatic_native_retry':True})+'\n');f.flush();os.fsync(f.fileno())
 def gate():env.check_execution()
 bridge=types.ModuleType('common166');bridge.__dict__.update(Path=Path,json=json,os=os,sys=sys,time=time,ROOT=ROOT,E=E,save=save,read=read,sha=sha,now=now,canonical=canonical,authorization=gate,MAX_ALL_OS_ROOTS=8,MAX_PRODUCT_NATIVE_ROOTS=3,NATIVE_TIMEOUT_SECONDS=max(.1,min(300,env.time_left())));sys.modules['common166']=bridge
 jobs=module('_exp262_native_controller_jobs',E/'SOURCE/native_executor242_prospective.py');jobs.OS_ROOT_RESERVATIONS=1
 result=jobs.execute([str(CONTROLLER),'-X','utf8','-B',str(E/'SOURCE/qualify_candidate262_DELEGATED.py'),'--root-grant',str(grant_path)],E,out/'controller.log',timeout=min(360,env.time_left()),env={k:os.environ[k] for k in ('SystemRoot','WINDIR','SYSTEMDRIVE','PATH','TEMP','TMP','USERPROFILE','LOCALAPPDATA') if k in os.environ})
 save(out/'PARENT_NATIVE_CONTROLLER_STOP.json',result)
 if result['exit_code']!=0 or result['timeout'] or not result['stop_receipt']['all_owned_descendants_terminated']:raise RuntimeError('EXP262_EXACT_NATIVE_CHILD_STOP_OR_EXECUTION_UNKNOWN')
 value=read(out/'native_once/ROOT_COMPLETED_PUBLIC.json')
 value['parent_stop_ref']={'path':str(out/'PARENT_NATIVE_CONTROLLER_STOP.json'),'sha256':sha(out/'PARENT_NATIVE_CONTROLLER_STOP.json')}
 value['delegated_grant_ref']={'path':str(grant_path),'sha256':sha(grant_path)}
 save(out/'ROOT_COMPLETED_PUBLIC.json',value)

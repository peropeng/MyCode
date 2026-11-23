"""One exact prospective model request, Root-gated, with durable no-resend state."""
import argparse, datetime, hashlib, importlib.util, json, os, sys, time, types
from pathlib import Path
sys.dont_write_bytecode=True
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
E=Path(__file__).resolve().parent
R=Path('D:/Code/毕设/graduate-thesis-experiments')
FIN=R/'工作区/1010-unified-six/finance_queue_remaining_SOURCE'
COMMON=R/'工作区/1011-unbudgeted-common'
PHASE='UnifiedSixOurs24220261010'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,v):
 p=Path(p).resolve();assert p.is_relative_to(E)
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.'+str(os.getpid())+'.tmp')
 with tmp.open('w',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def main():
 p=argparse.ArgumentParser();p.add_argument('--index',type=int,required=True);p.add_argument('--root-grant',required=True);a=p.parse_args()
 slot=E/'replay'/str(a.index);ready=read(slot/'FIRST_UNPOST_READY.json');body=read(slot/'FIRST_UNPOST_BODY.json')
 grant_path=Path(a.root_grant).resolve();grant=read(grant_path)
 for field in ('root_authorized','model_authorized','finance_authorized'):
  if grant.get(field) is not True:raise RuntimeError('EXP248_ROOT_EXACT_MODEL_GRANT_CLOSED '+field)
 if (ready['task']!=grant.get('task_id') or digest(body)!=ready['body_SHA256']
     or digest(body)!=grant.get('body_SHA256') or grant.get('phase')!=PHASE
     or grant.get('maximum_new_requests')!=1 or grant.get('native_authorized') is not False
     or grant.get('private_authorized') is not False):raise RuntimeError('EXP248_EXACT_FIRST_REQUEST_GRANT_DRIFT')
 for path,h in grant['sources_SHA256'].items():
  if sha(path)!=h:raise RuntimeError('EXP248_SOURCE_DRIFT '+path)
 if grant['sources_SHA256'].get(str(Path(__file__).resolve()))!=sha(__file__):raise RuntimeError('EXP248_DISPATCH_SOURCE_NOT_BOUND')
 config_path=COMMON/'FINANCE_CONFIG_CONTINUE.json';config=read(config_path)
 if sha(config_path)!=grant['finance_configuration_SHA256']:raise RuntimeError('EXP248_FINANCE_CONFIG_DRIFT')
 state_path=slot/'DISPATCH_STATE.json'
 if state_path.exists():
  state=read(state_path)
  if state['status']=='SETTLED_RESPONSE_SAVED':
   print(canonical({'status':'ALREADY_SETTLED_NO_REPOST','task':ready['task'],'body_SHA256':digest(body)}));return
  raise RuntimeError('EXP248_EXISTING_INTENT_UNKNOWN_OR_INFLIGHT_NO_RESEND')
 limit=datetime.datetime.fromisoformat(grant['forward_lease_end_UTC']).timestamp()
 if time.time()>=limit:raise RuntimeError('EXP248_FORWARD_LEASE_EXPIRED')
 stop=Path(config['forward_closure_flag'])
 if stop.exists():raise RuntimeError('EXP248_NEW_FORWARD_STOP')
 sys.path.insert(0,str(FIN));transport=load('_exp248_registered_finance',FIN/'completion_transport_v3.py')
 out=slot/'new_generation';checkpoint=read(slot/'checkpoint.json')
 env=types.SimpleNamespace(out=out,calls=checkpoint['cursor']['calls']+1,task_id=ready['task'],time_left=lambda:max(0,limit-time.time()))
 class IO(transport.LegacyIO):
  def write_artifact(self,env,suffix,value,key):save(str(self.stem(env))+suffix,self.clean(value,key))
  def request(self,env,role,body,bounds,key):
   if digest(body)!=grant['body_SHA256']:raise RuntimeError('EXP248_ACTUAL_REQUEST_BODY_DRIFT')
   self.write_artifact(env,'_request.json',{'at_utc':now(),'role':role,'call_ordinal':env.calls,'body':body,'body_SHA256':digest(body),'bounds':bounds},key)
  def post(self,body,key,timeout):
   # This callback begins only after a full reservation and final atomic
   # permission check. Preparing the body never starts the new science clock.
   current_start=now();t0_path=E/'science'/ready['task']/'SCIENCE_T0_ACTUAL_POST_DISPATCH.json'
   if not t0_path.exists():
    t0_path.parent.mkdir(parents=True,exist_ok=True)
    with t0_path.open('x',encoding='utf-8') as stream:
     json.dump({'schema':'new-mechanism-first-actual-POST-dispatch/1','at_UTC':current_start,
       'task':ready['task'],'body_SHA256':digest(body),'method_version':248,'network_response_still_unknown':True,
       'old_clock_used_only_as_historical_record':True},stream,ensure_ascii=False,indent=2)
     stream.flush();os.fsync(stream.fileno())
   t0=read(t0_path)
   state.update(status='ACTUAL_POST_DISPATCH_INFLIGHT_NO_RESEND',post_dispatch_started_UTC=current_start,
      new_scientific_T0_UTC=t0['at_UTC'],new_scientific_T0_record=str(t0_path))
   save(state_path,state)
   return super().post(body,key,timeout)
  def raw_response(self,env,role,raw,key):
   self.write_artifact(env,'_http_response.json',raw,key)
   try:self.write_artifact(env,'_response.json',json.loads(raw['body_text']),key)
   except (ValueError,TypeError,KeyError):pass
  def receipt(self,env,receipt,key):self.write_artifact(env,'_finance_receipt.json',receipt,key)
  def error(self,env,role,error,key):self.write_artifact(env,'_error.json',error,key)
  def final_response(self,env,result,key):self.write_artifact(env,'_response.json',result,key)
 gate=transport.make_transport(config,IO())
 # Common C0 supplement is already present in the sealed, exact full body.
 common=load('_exp248_common_verify',FIN/'common_model_input_six.py')
 stripped=json.loads(canonical(body));stripped['messages']=[m for m in stripped['messages'] if not str(m.get('content','')).startswith(common.TAG)]
 if common.inject(stripped,config,ready['task'])!=body:raise RuntimeError('EXP248_COMMON_C0_BODY_REINJECTION_DRIFT')
 state={'schema':'durable-single-dispatch/1','status':'INTENT_PERSISTED_NO_RETRY','task':ready['task'],'attempt':ready['attempt'],
  'body_SHA256':digest(body),'forward_lease_start_UTC':now(),'forward_lease_end_UTC':grant['forward_lease_end_UTC'],
  'original_science_started':checkpoint['original_science_started'],'prior_calls':checkpoint['cursor'],
  'root_grant_SHA256':sha(grant_path),'full_peak_reserve_CNY':ready['full_peak_reserve_CNY'],'native':0,'private':0}
 # O_EXCL protects concurrent owners, independently of the financial lock.
 lock=slot/'DISPATCH_OWNER_EXCLUSIVE.json'
 with lock.open('x',encoding='utf-8') as f:json.dump({'pid':os.getpid(),'body_SHA256':digest(body),'at_utc':now()},f);f.flush();os.fsync(f.fileno())
 save(state_path,state)
 try:
  response=gate.generate(env,body,'Exp248/OURS/'+ready['task']+'/attempt'+str(ready['attempt']),PHASE)
 except BaseException as exc:
  state.update(status='STOPPED_NO_RESEND_PENDING_EXACT_RECONCILIATION',exception={'type':type(exc).__name__,'message':str(exc)},at_utc=now());save(state_path,state);raise
 state.update(status='SETTLED_RESPONSE_SAVED',at_utc=now(),response_SHA256=digest(response),usage=response['usage'])
 save(state_path,state)
 checkpoint.update(status='NEW_MODEL_RESPONSE_SAVED_PUBLIC_PROCESSING_PENDING',new_response=response,new_response_SHA256=digest(response),
   forward_lease_start_UTC=state['forward_lease_start_UTC'],forward_lease_end_UTC=grant['forward_lease_end_UTC'])
 checkpoint['original_science_started']=read(state['new_scientific_T0_record'])
 checkpoint['cursor']['calls']=env.calls;checkpoint['cursor']['output_tokens']+=response['usage']['completion_tokens']
 save(slot/'checkpoint_after_model.json',checkpoint)
 print(canonical({'task':ready['task'],'status':state['status'],'usage':response['usage'],'new_native':0,'private':0}),flush=True)
if __name__=='__main__':main()

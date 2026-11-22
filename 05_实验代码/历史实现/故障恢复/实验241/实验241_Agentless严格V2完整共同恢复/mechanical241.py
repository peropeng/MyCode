"""One actual zero-model C0/deployment qualification per new task."""
import argparse,ctypes,datetime,os,sys,traceback
from contracts241 import *
from environment241 import Environment241
from public_v2_241 import body_v2,AL
from winjob241 import JobRunner,kernel,self_identity

class MechanicalEnvironment(Environment241):
 def require_action(self,kind,allow_no_new=False):
  if kind=='LLM' or self.calls:raise EngineeringUnknown('MECHANICAL_NO_MODEL')
  if self.protocol.get('execution_authorized') or read(self.grant_path).get('root_authorized'):raise EngineeringUnknown('MECHANICAL_REQUIRES_FALSE_SCIENCE_GRANT')
  self.assert_no_unknown()
  if time.time()>=deadline_epoch(HARD) or self.time_left()<=0:raise EngineeringUnknown('MECHANICAL_BUDGET_END')
  if kind!='observe':
   for path,h in self.seal['sources'].items():
    if sha(path)!=h:raise EngineeringUnknown('MECHANICAL_SOURCE_DRIFT '+path)
 def llm(self,*a,**k):raise EngineeringUnknown('MECHANICAL_LLM_POST_FORBIDDEN')

def child(task,namespace='mechanical_native'):
 base=HERE/'candidate'/task;out=HERE/namespace/task
 p=read(base/'protocol.json');p['output_root']=str(out/'owned_flow');save(out/'protocol.json',p)
 save(out/'grant.json',read(base/'root_grant.template.json'))
 own=MechanicalEnvironment(out/'protocol.json',out/'grant.json',base/'source_seal.json',base/'public_contract.json')
 own.runner=JobRunner(own)
 k=kernel();buf=ctypes.create_unicode_buffer(32768);n=k.GetModuleFileNameW(None,buf,len(buf));assert 0<n<len(buf)
 controller=self_identity(os.environ['PATCHPILOT_CONTROLLER_JOB'],buf.value)
 own.grant['controller_physical_python_expected']=buf.value
 cert=out/'product_identity.json'
 raw=own.runner.execute([str(own.logical_python),'-X','utf8','-B',str(HERE/'physical_self_probe241.py'),str(cert)],HERE,
  out/'product_identity.log',90,dict(os.environ))
 if raw['exit_code']!=0 or not cert.is_file():raise EngineeringUnknown('NEUTRAL_PRODUCT_PHYSICAL_IDENTITY_FAILED')
 product=read(cert);own.physical_python=product['actual_OS_image_GetModuleFileName']
 own.contract['physical_product_python_expected']=own.physical_python;own.grant['product_physical_python_expected']=own.physical_python
 own.initialize()
 from agentless_bridge.local_core166 import structure
 from agentless_bridge import official_core166 as official
 files=own.business_files();tree=official.show_project_structure(structure(files)).strip()
 problem=own.goal+'\nObserved current public recovery failure: '+__import__('json').dumps(own.initial_public_feedback,ensure_ascii=False,sort_keys=True)
 first_messages=[{'role':'system','content':'You are a helpful assistant. Only the supplied public business source and public test interfaces are available. Fixed tests, private tests and references are immutable; never access them.'},
  {'role':'user','content':own.core.PROMPTS['obtain_relevant_files_prompt'].format(problem_statement=problem,structure=tree).strip()}]
 first_body=body_v2('agentless_suspicious_files',first_messages,0,own.core.seed(task,'suspicious_files',0),8192,task,METHOD,own.pack,None,[],0)
 if 'tools' in first_body or 'tool_choice' in first_body:raise EngineeringUnknown('NO_ADDED_READER_TOOLS_ALLOWED')
 import flash_transport241 as transport
 real_transport=transport.construct(own);state=real_transport.io.read();real_transport.validate(state,FINANCE_PHASE)
 exact_bounds=transport.bounds(first_body,real_transport.c)
 artifact=own.output_root/'constructor_scope_probe.json';real_transport.io.m.save(artifact,{'actual_scoped_constructor':True,'no_POST':True})
 outside=HERE/'forbidden_artifact_scope_probe.json';blocked=False
 try:real_transport.io.m.save(outside,{'must_not_be_written':True})
 except EngineeringUnknown:blocked=True
 if not blocked or outside.exists() or 'replace_retry' not in real_transport.io.m.atomic.__code__.co_names:
  raise EngineeringUnknown('ACTUAL_ARTIFACT_SCOPE_OR_SINGLE_ATOMIC_CHAIN_FAILED')
 before=own.actor_business_inventory();native=own.verify_public();outcomes=native['outcomes']
 if (set(outcomes)!=set(own.contract['public_target_nodes']+own.contract['ordinary_nodes'])
     or not all(outcomes[n]['status']=='failed' for n in own.contract['public_target_nodes'])
     or not all(outcomes[n]['status']=='passed' for n in own.contract['ordinary_nodes'])):
  raise EngineeringUnknown('ACTUAL_PUBLIC_C0_FAILURE_ORDINARY_CONTRACT_NOT_REPRODUCED')
 ordinary=own.run_regression(own.initial_snapshot,own.public_regression_nodes,'neutral_ordinary_support')
 if not ordinary['passed']:raise EngineeringUnknown('REAL_ORDINARY_REGRESSION_NOT_SUPPORTED')
 repro=own.run_reproduction('import '+own.contract['package']+'\nprint("Other issues")\n',own.initial_snapshot,'neutral_product_reproduction_support')
 if repro['not_reproduced'] is not True:raise EngineeringUnknown('REAL_REPRODUCTION_RUNTIME_MARKER_OR_PRODUCT_GUARD_NOT_SUPPORTED')
 dense_paths,dense=own.core.retrieve(files,own.retrieval_query,None,list(files))
 if not dense_paths or dense.get('real_dense_embedding') is not True:raise EngineeringUnknown('ACTUAL_AUTHOR_DENSE_CORE_NOT_FUNCTIONAL')
 if before!=own.actor_business_inventory() or own.calls:raise EngineeringUnknown('MECHANICAL_C0_OR_MODEL_CHANGED')
 dependencies={}
 for name,mod in sys.modules.copy().items():
  path=getattr(mod,'__file__',None)
  if path and Path(path).is_file() and any(inside(path,d) for d in own.protocol['controller_dependency_paths']):
   dependencies[str(Path(path).resolve())]=sha(path)
 save(out/'mechanical_receipt.json',{'schema':'Agentless241-actual-runtime-mechanical/1','status':'PASS_ACTUAL_RUNTIME_MECHANICAL_NOT_METHOD_SUCCESS',
  'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'controller_identity':controller,'product_identity':product,
  'actual_native_public_C0_target_failed':True,'actual_ordinary_C0_passed':True,'outcomes':{n:v['status'] for n,v in outcomes.items()},
  'actual_reproduction_support':repro,'actual_regression_support':ordinary,'actual_dense_retrieval':dense,
  'actual_original_core_SHA256':sha(AL/'agentless178.py'),'original_source_derivative_receipt':own.core.implementation_receipt(),
  'actual_transport_constructor':True,'actual_single_atomic_wrapper_chain':True,'actual_finance_readonly_validate':True,
  'actual_artifact_scope_inside_write_and_outside_rejection':True,'complete_unclipped_first_body':first_body,
  'complete_first_body_sha256':digest(first_body),'first_body_bounds':exact_bounds,'exact_C0_unchanged':True,
  'all_owned_child_jobs_STOP':True,'parent_stop_required':True,'model_API_private_ledger_writes':0,
  'native_roots':own.native_roots,'native_root_kinds':own.native_root_kinds,'actual_controller_dependencies':dependencies,
  'full_method_nonzero_qualification_still_required':True})
 save(out/'public_contract_physical_qualified.json',own.contract)

class Parent:
 def __init__(self,out):self.out=out;self.started=time.monotonic();self.unknown=None;self.native_roots=0
 def require_action(self,*a,**k):
  if time.time()>=deadline_epoch(HARD):raise EngineeringUnknown('GLOBAL_HARD')
 def reserve_native(self):self.native_roots+=1
 def time_left(self):
  value=600-(time.monotonic()-self.started)
  if self.out.parent.name.startswith('mechanical_single_fix'):
   first=read(HERE/'mechanical_native'/self.out.name/'first_failure.json')
   value=min(value,datetime.datetime.fromisoformat(first['utc']).timestamp()+300-time.time())
  return max(0,value)
 def record(self,v):
  with (self.out/'parent_events.jsonl').open('a',encoding='utf-8') as f:f.write(canonical(v)+'\n')
 def latch_unknown(self,error,stage):self.unknown={'stage':stage,'message':str(error)}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--task',required=True);parser.add_argument('--child',action='store_true')
 parser.add_argument('--namespace',default='mechanical_native');args=parser.parse_args()
 if args.namespace not in ('mechanical_native','mechanical_single_fix','mechanical_single_fix_final','mechanical_single_fix_verified'):raise EngineeringUnknown('ONE_MECHANICAL_FIX_ONLY')
 if args.child:return child(args.task,args.namespace)
 out=HERE/args.namespace/args.task
 if out.exists():raise EngineeringUnknown('ONE_FRESH_MECHANICAL_TASK_ONLY')
 out.mkdir(parents=True);parent=Parent(out)
 image='C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
 env={k:os.environ[k] for k in ('SystemRoot','WINDIR','SYSTEMROOT','SYSTEMDRIVE','COMSPEC','PATHEXT') if k in os.environ}
 env.update(PYTHONPATH='',PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1',PATH=str(Path(image).parent),TEMP=str(out),TMP=str(out))
 try:
  raw=JobRunner(parent).execute([image,'-X','utf8','-B',str(HERE/'mechanical241.py'),'--task',args.task,'--namespace',args.namespace,'--child'],HERE,out/'child.log',600,env,controller=True)
  save(out/'parent_stop_receipt.json',raw)
  if raw['exit_code']!=0 or raw['timeout']:raise EngineeringUnknown('MECHANICAL_CHILD_FAILED '+raw['stderr'][-4000:])
  print(canonical({'actual_mechanical':'PASS','task':args.task,'STOP':raw['stop_receipt'],'model_POST_private_ledger_write':0}))
 except BaseException as error:
  save(out/'first_failure.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'error':{'type':type(error).__name__,'message':str(error)},'traceback':traceback.format_exc()})
  raise
if __name__=='__main__':main()

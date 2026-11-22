"""One actual zero-model C0/deployment qualification per new task."""
import argparse,ctypes,datetime,os,sys,traceback
from contracts241 import *
from initial_c0_observer_v3_241 import InitialV3Environment as Environment241, observe_initial
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
 original_judgment=official.is_just_new_function
 if not getattr(original_judgment,'_scope3_old_ast_guard',False):raise EngineeringUnknown('AST_COMPAT_ADAPTER_NOT_INSTALLED')
 original_function=original_judgment._original_is_just_new_function
 if Path(original_function.__code__.co_filename).resolve()!=Path(official.__file__).resolve():raise EngineeringUnknown('ORIGINAL_NORMALIZER_PATH_MISMATCH')
 normalization_receipt={'installed_old_AST_guard':True,'original_normalizer_path':str(Path(official.__file__).resolve()),'original_normalizer_SHA256':sha(official.__file__),'adapter_SHA256':sha(HERE/'normalization_adapter_v3_241.py')}
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
 before=own.actor_business_inventory();initial_observer=observe_initial(own.contract,before);outcomes=initial_observer['outcomes']
 if initial_observer['initial_goal_completed']!=0 or initial_observer['initial_goal_blocked']!=4 or not initial_observer['ordinary_passed']:
  raise EngineeringUnknown('ACTUAL_SHARED_INITIAL_V3_CLASSIFICATION_NOT_REPRODUCED')
 ordinary=own.run_regression(own.initial_snapshot,own.public_regression_nodes,'neutral_ordinary_support')
 if not ordinary['passed']:raise EngineeringUnknown('REAL_ORDINARY_REGRESSION_NOT_SUPPORTED')
 repro=own.run_reproduction('import '+own.contract['package']+'\nprint("Other issues")\n',own.initial_snapshot,'neutral_product_reproduction_support')
 if repro['not_reproduced'] is not True:raise EngineeringUnknown('REAL_REPRODUCTION_RUNTIME_MARKER_OR_PRODUCT_GUARD_NOT_SUPPORTED')
 synthetic=HERE/'scope_fixture_artifacts'/task
 probes={}
 for kind in ('same_case_private','other_case_private','previous_selected_patch','previous_raw_response'):
  path=synthetic/kind/'synthetic_not_private_data.json'
  save(path,{'synthetic_scope_probe_not_Gold_or_actual_result':True,'kind':kind})
  probes[kind]=str(path)
 probes['finance_config']=str(HERE/'finance_config241.json')
 probes['outside_deployment_nonexistent_artifact']=str(HERE.parent/'实验241_Agentless新确认集21/EXPLICIT_SYNTHETIC_NEVER_CREATED_scope_private_result.json')
 code='import '+own.contract['package']+'\nfrom pathlib import Path\nimport os\n'
 code+='blocked_paths='+repr(probes)+'\n'
 code+='for label,value in blocked_paths.items():\n    try:\n        Path(value).read_bytes()\n    except PermissionError:\n        pass\n    else:\n        raise AssertionError("UNEXPECTED_ARTIFACT_READ_ALLOWED "+label)\n'
 code+='assert Path('+repr(str(HERE/'contracts241.py'))+').read_bytes()\n'
 code+='assert Path('+own.contract['package']+'.__file__).read_bytes()\n'
 code+='scratch=Path(__file__).parent/"own_native_scratch.txt"\nscratch.write_text("synthetic allowed output",encoding="utf-8")\nassert scratch.read_text("utf-8")=="synthetic allowed output"\n'
 code+='audit_log=Path(__file__).parent/"generated_scope_events.jsonl"\ntry:\n    audit_log.write_text("forbidden overwrite",encoding="utf-8")\nexcept PermissionError:\n    pass\nelse:\n    raise AssertionError("AUDIT_LOG_MUTATION_ALLOWED")\n'
 code+='link_source='+repr(probes['same_case_private'])+'\n'
 code+='for operation,name in ((os.link,"hardlink"),(os.symlink,"symlink")):\n    destination=Path(__file__).parent/(name+"_forbidden_artifact.json")\n    try:\n        operation(link_source,str(destination))\n    except PermissionError:\n        pass\n    else:\n        raise AssertionError("ARTIFACT_LINK_ALLOWED "+name)\n    assert not destination.exists()\n'
 code+='for operation,argument in ((os.chmod,0o666),(os.truncate,0)):\n    try:\n        operation(link_source,argument)\n    except PermissionError:\n        pass\n    else:\n        raise AssertionError("OUTSIDE_MUTATION_ALLOWED")\n'
 code+='print("Other issues")\n'
 scope_probe=own.run_reproduction(code,own.initial_snapshot,'neutral_scope_v2_real_read_write_probe')
 if scope_probe['not_reproduced'] is not True:raise EngineeringUnknown('SCOPE_V2_TRUSTED_PROBE_FAILED')
 scope_native_out=Path(scope_probe['native_record']['log']).parent
 scope_events=[json.loads(x) for x in (scope_native_out/'generated_scope_events.jsonl').read_text('utf-8').splitlines() if x.strip()]
 if not scope_events or scope_events[0].get('event')!='SCOPE_V2_INSTALL':raise EngineeringUnknown('SCOPE_V2_EVENT_COVERAGE_NOT_INSTALLED_FIRST')
 for label,value in probes.items():
  if not any(e.get('event')=='open' and e.get('path')==str(Path(value).resolve()) and e.get('allowed') is False and e.get('write') is False for e in scope_events):
   raise EngineeringUnknown('SCOPE_V2_DENIAL_EVENT_MISSING '+label)
 for value,write in [(str(HERE/'contracts241.py'),False),(str(scope_native_out/'own_native_scratch.txt'),True),(str(scope_native_out/'own_native_scratch.txt'),False)]:
  if not any(e.get('event')=='open' and e.get('path')==str(Path(value).resolve()) and e.get('allowed') is True and e.get('write') is write for e in scope_events):
   raise EngineeringUnknown('SCOPE_V2_ALLOWED_EVENT_MISSING '+value)
 if not any(e.get('event')=='open' and e.get('reason')=='TRUSTED_SCOPE_LOG_IMMUTABLE_TO_GENERATED_CODE' and e.get('allowed') is False for e in scope_events):
  raise EngineeringUnknown('SCOPE_V2_LOG_IMMUTABILITY_NOT_PROVED')
 for event in ('os.link','os.symlink','os.chmod','os.truncate'):
  if not any(e.get('event')==event and e.get('allowed') is False for e in scope_events):
   raise EngineeringUnknown('SCOPE_V2_LINK_OR_MUTATION_DENIAL_EVENT_MISSING '+event)
 for value in probes.values():
  if str(value).startswith(str(synthetic)) and read(value).get('synthetic_scope_probe_not_Gold_or_actual_result') is not True:
   raise EngineeringUnknown('SCOPE_PROBE_SYNTHETIC_BYTES_CHANGED')
 scope_receipt={'status':'PASS_ACTUAL_SCOPE_V2_NOT_METHOD_SUCCESS','blocked_probe_paths':probes,
  'event_log':str(scope_native_out/'generated_scope_events.jsonl'),'event_log_sha256':sha(scope_native_out/'generated_scope_events.jsonl'),
  'actual_open_events':sum(e.get('event')=='open' for e in scope_events),'allowed_open_events':sum(e.get('event')=='open' and e.get('allowed') for e in scope_events),
  'all_probe_allowed_and_denied_reads_writes_individually_reconciled':True,'native_record':scope_probe['native_record'],
  'no_actual_private_contents_read':True,'no_whole_experiment_read_root':True,'audit_log_immutable_to_generated_script':True,
  'actual_Python_link_symlink_chmod_truncate_probe_denials_logged':True,
  'coverage_limit':'Audited Python entry/API hook events and these concrete probes only; no claim over arbitrary native C-layer or malicious-code bypasses'}
 save(out/'scope_v2_receipt.json',scope_receipt)
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
  'actual_native_public_C0_target_failed':False,'actual_initial_goal_collection_blocked':True,'actual_initial_goal_completed':0,
  'actual_initial_goal_blocked':4,'initial_qualification_v3_observer':initial_observer,'actual_normalization_compatibility':normalization_receipt,
  'actual_ordinary_C0_passed':True,'outcomes':{n:v['status'] for n,v in outcomes.items()},
  'actual_reproduction_support':repro,'actual_regression_support':ordinary,'actual_dense_retrieval':dense,
  'actual_original_core_SHA256':sha(AL/'agentless178.py'),'original_source_derivative_receipt':own.core.implementation_receipt(),
  'actual_transport_constructor':True,'actual_single_atomic_wrapper_chain':True,'actual_finance_readonly_validate':True,
  'actual_artifact_scope_inside_write_and_outside_rejection':True,'complete_unclipped_first_body':first_body,
  'complete_first_body_sha256':digest(first_body),'first_body_bounds':exact_bounds,'exact_C0_unchanged':True,
  'all_owned_child_jobs_STOP':True,'parent_stop_required':True,'model_API_private_ledger_writes':0,
  'native_roots':own.native_roots,'native_root_kinds':own.native_root_kinds,'actual_controller_dependencies':dependencies,
  'full_method_nonzero_qualification_still_required':True,'actual_generated_scope_version':2,
  'actual_scope_v2_probe':scope_receipt,'all_scope_probe_events_individually_reconciled':True})
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
  raw=JobRunner(parent).execute([image,'-X','utf8','-B',str(HERE/'mechanical_initial_v3_241.py'),'--task',args.task,'--namespace',args.namespace,'--child'],HERE,out/'child.log',600,env,controller=True)
  save(out/'parent_stop_receipt.json',raw)
  if raw['exit_code']!=0 or raw['timeout']:raise EngineeringUnknown('MECHANICAL_CHILD_FAILED '+raw['stderr'][-4000:])
  print(canonical({'actual_mechanical':'PASS','task':args.task,'STOP':raw['stop_receipt'],'model_POST_private_ledger_write':0}))
 except BaseException as error:
  save(out/'first_failure.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'error':{'type':type(error).__name__,'message':str(error)},'traceback':traceback.format_exc()})
  raise
if __name__=='__main__':main()

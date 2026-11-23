"""Prepare source/constants only; no model, native, fixtures, provider or old runs."""
from pathlib import Path
import ast,copy,datetime,hashlib,json
E=Path(__file__).resolve().parent;OLD=E/'source_runtime_v1';D=E/'runtime_v3_SOURCE'
R=Path('D:/Code/毕设/graduate-thesis-experiments');W=R/'工作区/1010-unified-six'
EA=R/'工作区/1009-exp239-enagent-flash-auto/实验/实验239_EnAgent_统一六题财政V3_SOURCE'
SHARED=EA/'shared_native_v3_SOURCE';F=W/'finance'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
def write(n,s):ast.parse(s);(D/n).write_text(s,'utf-8')
def rep(s,a,b):
 if a not in s:raise RuntimeError('SOURCE_ANCHOR '+a[:80])
 return s.replace(a,b)
if D.exists():raise RuntimeError('NEW_RUNTIME_V3_ONCE_NO_OVERWRITE')
D.mkdir()
for p in OLD.glob('*.py'):write(p.name,p.read_text('utf-8-sig'))
save(D/'PAPER_CORE_SOURCE_PROVENANCE241.json',read(OLD/'PAPER_CORE_SOURCE_PROVENANCE241.json'))
contracts=(D/'contracts241.py').read_text('utf-8')
contracts=rep(contracts,"or grant.get('model_generation_authorized') is not True", "or (grant.get('stage')=='FULL_PAPER_MAIN_SCIENCE_ONCE' and grant.get('model_generation_authorized') is not True)")
contracts=rep(contracts,"or grant.get('stage')!='FULL_PAPER_MAIN_SCIENCE_ONCE'", "or grant.get('stage') not in ('FULL_PAPER_MAIN_SCIENCE_ONCE','MECHANICAL_ZERO_POST')")
contracts=rep(contracts,"if (config.get('model_generation_authorized') is not True", "if (grant.get('stage')=='FULL_PAPER_MAIN_SCIENCE_ONCE' and config.get('model_generation_authorized') is not True")
contracts=rep(contracts,"if (not grant.get('neutral_mechanical_qualification_sha256') or not grant.get('parent_controller_job_qualified')", "if ((grant.get('stage')=='FULL_PAPER_MAIN_SCIENCE_ONCE' and not grant.get('neutral_mechanical_qualification_sha256')) or not grant.get('parent_controller_job_qualified')")
write('contracts241.py',contracts)
transport=(D/'flash_transport241.py').read_text('utf-8')
transport=rep(transport,"FISCAL/'completion_transport_v3.py'", "FISCAL/'completion_transport_common_C0_v4.py'")
transport=rep(transport,"owner.require_action('LLM_POST_BOUNDARY')", "owner.require_action('LLM_POST_BOUNDARY')\n if owner.grant.get('model_generation_authorized') is not True:raise EngineeringUnknown('ZERO_POST_MECHANICAL_NO_TRANSPORT')")
write('flash_transport241.py',transport)
owner=(D/'owner241.py').read_text('utf-8')
owner=rep(owner,"copy_bytes(self.contract['template'],self.repo_root,self.contract['template_inventory'])", "copy_bytes(self.contract['template'],self.repo_root,self.contract['c0_business_paths_sha256'])")
owner=rep(owner,"if digest(inventory(self.actor_root))!=self.contract['c0_business_inventory_sha256']:", "if digest(inventory(self.actor_root))!=self.contract['c0_business_inventory_sha256']:")
# Support is installed only after exact business cloning, with the shared public helper.
owner=rep(owner,"self.qualify.HERE=Path(self.contract['harness']);self.qualify.execute=self.native_execute", "self.qualify.HERE=Path(self.contract['harness']);self.qualify.execute=self.native_execute\n        from shared_facade241 import install\n        install(self)")
owner=rep(owner,"if rel.startswith('generated_tests/') and rel.endswith('.py'):continue", "if rel in getattr(self,'masked_supports',{}):\n                if expected!=self.masked_supports[rel]:raise IllegalTool('IMMUTABLE_PUBLIC_SUPPORT_DRIFT')\n                continue\n            if rel.startswith('generated_tests/') and rel.endswith('.py'):continue")
owner=rep(owner,"initial=self.contract['template_inventory']", "initial={**self.contract['c0_business_paths_sha256'],**getattr(self,'masked_supports',{})}")
write('owner241.py',owner)

facade='''"""Exact shared masked helper/guard/runner; AL facade owns actual Jobs and counts."""
from contracts241 import *
from types import SimpleNamespace
def install(owner):
 ref=owner.protocol['shared_public_helper'];public=module('_AL241_exact_shared_public_helper',ref['path'])
 if sha(ref['path'])!=ref['sha256']:raise EngineeringUnknown('EXACT_SHARED_PUBLIC_HELPER_SHA')
 row=public.load_scope(owner.protocol,owner.task_id)
 business=owner.contract['c0_business_paths_sha256'];owner.masked_supports=public.materialize_support(owner.actor_root,row,business)
 public.materialize_support(owner.repo_root,row,business);owner.masked_scope=row;owner.shared_public=public
 class Facade:
  def __init__(self):
   self.native_calls=0;self.task_id=owner.task_id;self.out=owner.output_root;self.package=owner.contract['package']
   self._paths={'python':str(owner.logical_python),'frozen':owner.contract['frozen_public_test_root']}
   self.run=SimpleNamespace(qualify=SimpleNamespace(HERE=owner.qualify.HERE,isolated_env=owner.qualify.isolated_env,execute=direct))
  def _require(self):owner.require_action('shared_masked_public')
  def business_files(self):return owner.business_files()
  def time_left(self):return owner.time_left()
  def native_lane(self):return owner.native_lane()
  def record(self,*args):return owner.record(*args)
 def direct(argv,cwd,log,timeout=90,env=None):
  child=dict(env or {});child.pop('DEEPSEEK_API_KEY',None);child.pop('OPENAI_API_KEY',None)
  child['AL_EXPECTED_PHYSICAL']=owner.physical_python
  child['AL_IDENTITY_OUTPUT']=str(Path(log).parent/'actual_python_identity.json')
  # The exact shared site guard is already installed by startup. This literal
  # performs physical self/own-Job proof before exact shared runner product imports.
  code="""import ctypes,json,os,sys,runpy
from ctypes import wintypes as V
k=ctypes.WinDLL('kernel32',use_last_error=True)
k.GetCurrentProcess.restype=V.HANDLE
k.OpenJobObjectW.argtypes=[V.DWORD,V.BOOL,V.LPCWSTR];k.OpenJobObjectW.restype=V.HANDLE
k.IsProcessInJob.argtypes=[V.HANDLE,V.HANDLE,ctypes.POINTER(V.BOOL)];k.IsProcessInJob.restype=V.BOOL
k.GetModuleFileNameW.argtypes=[V.HMODULE,V.LPWSTR,V.DWORD];k.GetModuleFileNameW.restype=V.DWORD
k.CloseHandle.argtypes=[V.HANDLE];k.CloseHandle.restype=V.BOOL
j=k.OpenJobObjectW(4,False,os.environ['PATCHPILOT_JOB']);b=V.BOOL();s=ctypes.create_unicode_buffer(32768)
assert j and k.IsProcessInJob(k.GetCurrentProcess(),j,ctypes.byref(b)) and b.value
assert k.GetModuleFileNameW(None,s,len(s)) and os.path.normcase(os.path.realpath(s.value))==os.path.normcase(os.path.realpath(os.environ['AL_EXPECTED_PHYSICAL']))
with open(os.environ['AL_IDENTITY_OUTPUT'],'w',encoding='utf-8') as f:json.dump({'actual_OS_image_GetModuleFileName':s.value,'IsProcessInJob_specific_own_Job':True,'before_product_import':True,'specific_named_Job':os.environ['PATCHPILOT_JOB'],'sys_executable':sys.executable,'sys_prefix':sys.prefix},f)
k.CloseHandle(j)
sys.argv=sys.argv[1:];runpy.run_path(sys.argv[0],run_name='__main__')
"""
  previous=owner._native_kind;owner._native_kind='pytest'
  try:r=owner.runner.execute([str(owner.logical_python),'-B','-c',code,*list(map(str,argv))[2:]],cwd,log,timeout,child)
  finally:owner._native_kind=previous
  cert=read(child['AL_IDENTITY_OUTPUT']);stop=r['stop_receipt']
  r['actual_product_python_identity']=cert
  r['stop_receipt']={**stop,'all_owned_descendants_terminated':all(stop.get(x) is True for x in ('root_stopped','own_Job_empty_before_close','descendants_stopped'))}
  return r
 owner.masked_facade=Facade()
def execute(owner,nodes=None,collect_only=False,label='masked'):
 p={**owner.protocol,'budget':{**owner.protocol['budget'],'native_roots_total':2048,'native_timeout_seconds':90}}
 def own_check():
  from winjob241 import self_identity
  return self_identity(os.environ['PATCHPILOT_CONTROLLER_JOB'],owner.grant['controller_physical_python_expected'])
 return owner.shared_public.execute(owner.masked_facade,owner.actor_root,owner.masked_scope,nodes,collect_only=collect_only,label=label,protocol=p,owner_check=own_check)
'''
write('shared_facade241.py',facade)
binding='''"""Full actual masked repository PASS discovery and candidate regression."""
from contracts241 import *
class PaperBindingUnknown(RuntimeError):pass
class PaperMainEnvironmentMixin:
 def require_paper_main_current_binding(self):
  if not self.protocol.get('shared_public_scope_root_qualified') or not self.protocol.get('common_budget_root_freeze'):
   raise PaperBindingUnknown('ROOT_SHARED_PUBLIC_ENVIRONMENT_FREEZE_REQUIRED')
  self.paper_public_repository_regression_nodes=sorted(self.masked_scope['public_test_py_files_SHA256'])
 def run_paper_repository_regression(self,snapshot=None,nodes=None,label='paper_regression'):
  self.restore(snapshot or self.initial_snapshot)
  from shared_facade241 import execute
  result=execute(self,nodes,label=label)
  if result.get('known') is not True:raise PaperBindingUnknown('MASKED_FULL_REPOSITORY_NATIVE_UNKNOWN')
  outcomes=result['pytest']['outcomes'];fail=sum(v['status']!='passed' for v in outcomes.values())
  return self.record(label,{'passed':fail==0,'failure_count':fail,'outcomes':{n:{**v,'outcome':v['status']} for n,v in outcomes.items()},
   'status':'KNOWN_SHARED_MASKED_REAL_REGRESSION','native_record':{**result['execution'],'executed':True},'collected':result['pytest']['collected'],'uses_hidden':False})
 def paper_model_call_cap(self,role,requested):
  caps={'agentless_suspicious_files':300,'agentless_irrelevant_folders':2048,'agentless_related_elements':300,'agentless_fine_locations':300,'agentless_patch':1024,'agentless_reproduction':1024,'agentless_regression_exclusion':1024}
  if role not in caps or requested>caps[role]:raise PaperBindingUnknown('PAPER_SOURCE_OUTPUT_CAP_CHANGED')
  return int(requested)
'''
write('paper_environment_binding241.py',binding)
environment=(D/'environment241.py').read_text('utf-8')
environment=rep(environment,"core.implementation_receipt()", "core.implementation_receipt()\n def actual_passing_nodes(result,selectors):\n  outcomes=result.get('outcomes',{});collected=result.get('collected',list(outcomes))\n  return [n for n in collected if any(n==s or ('::' not in s and n.startswith(s+'::')) for s in selectors) and str(outcomes[n].get('outcome',outcomes[n].get('status'))).lower() in ('passed','pass')]\n core.passing_nodes=actual_passing_nodes")
write('environment241.py',environment)

entry='''"""One full author run or zero-POST integration qualification, explicit Root grant."""
import argparse,copy
from contracts241 import *
from environment241 import Environment241
def main():
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['mechanical','science'])
 for n in ('protocol','grant','seal','contract'):a.add_argument('--'+n,required=True)
 x=a.parse_args();env=Environment241(x.protocol,x.grant,x.seal,x.contract);env.initialize()
 if x.mode=='mechanical':
  if env.grant.get('stage')!='MECHANICAL_ZERO_POST' or env.grant.get('model_generation_authorized') is not False:raise EngineeringUnknown('MECHANICAL_ZERO_POST_GRANT_REQUIRED')
  from shared_facade241 import execute
  collection=execute(env,None,collect_only=True,label='complete_collection')
  nodes=collection.get('pytest',{}).get('collected',[])
  leaf=execute(env,[nodes[0]],label='first_collected_leaf') if nodes else None
  class Captured(BaseException):pass
  def capture(role,messages,temperature,seed,max_tokens,*args,**kwargs):
   body=__import__('public_v2_241').body_v2(role,copy.deepcopy(messages),temperature,seed,max_tokens,env.task_id,METHOD,env.pack,None,[],0)
   save(env.output_root/'FIRST_BODY_ZERO_POST.json',body,scope=env.output_root);raise Captured()
  env.llm=capture
  try:env.core.run(env)
  except Captured:pass
  save(env.output_root/'MECHANICAL_ZERO_POST_RESULT.json',{'collection':collection,'first_leaf':leaf,'first_body_captured':(env.output_root/'FIRST_BODY_ZERO_POST.json').is_file(),'POSTs':0,'private':0,'C0_not_repeated':True},scope=env.output_root)
 else:
  if env.grant.get('stage')!='FULL_PAPER_MAIN_SCIENCE_ONCE':raise EngineeringUnknown('FULL_PAPER_SCIENCE_GRANT_REQUIRED')
  raw=env.core.run(env);save(env.output_root/'author_raw_result.json',raw,scope=env.output_root)
  result=env.finalize_selection(raw);save(env.output_root/'result.json',result,scope=env.output_root)
if __name__=='__main__':main()
'''
write('entry_runtime_v3_241.py',entry)

supervisor='''"""Root-owned finite session: author STOP, immutable selection then external final."""
import argparse,os,time
from contracts241 import *
from winjob241 import JobRunner
class Parent:
 def __init__(self,args):
  self.a=args;self.p=read(args.protocol);self.g=read(args.grant);self.s=read(args.seal);verify_grant(self.p,self.g,self.s,self.p['task_id'])
  self.output_root=Path(self.p['supervision_output_root']);self.output_root.mkdir(parents=True,exist_ok=False);self.unknown=None;self.native=0
 def time_left(self):return max(0,deadline_epoch(self.g['new_start_UTC'])+3600-time.time())
 def require_action(self,kind,allow_no_new=False):verify_grant(self.p,read(self.a.grant),read(self.a.seal),self.p['task_id'])
 def reserve_native(self):
  if self.native>=1:raise EngineeringUnknown('ONE_AUTHOR_CONTROLLER_ONLY')
  self.native+=1
 def record(self,v):
  with (self.output_root/'events.jsonl').open('a',encoding='utf-8') as f:f.write(canonical(v)+'\\n')
 def latch_unknown(self,error,stage):self.unknown={'stage':stage,'message':str(error)};self.record(self.unknown)
def main():
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['mechanical','science'])
 for n in ('protocol','grant','seal','contract'):a.add_argument('--'+n,required=True)
 x=a.parse_args();own=Parent(x);image=own.g['controller_physical_python_expected'];argv=[image,'-X','utf8','-B',str(HERE/'entry_runtime_v3_241.py'),x.mode]
 for n in ('protocol','grant','seal','contract'):argv+=['--'+n,str(Path(getattr(x,n)).resolve())]
 env=dict(os.environ)
 if x.mode=='mechanical':env.pop('DEEPSEEK_API_KEY',None);env.pop('OPENAI_API_KEY',None)
 env.update(PYTHONPATH='',PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1')
 result=JobRunner(own).execute(argv,HERE,own.output_root/'controller.log',300 if x.mode=='mechanical' else 3510,env,controller=True)
 save(own.output_root/'PARENT_STOP.json',result,scope=own.output_root)
 print(canonical({'author_exit':result['exit_code'],'STOP':result['stop_receipt'],'selection':str(Path(own.p['output_root'])/'immutable_selection.json'),'independent_final_owner':'Root after author STOP only'}))
if __name__=='__main__':main()
'''
write('supervisor_runtime_v3_241.py',supervisor)

ea=read(EA/'protocol225.json');physical=read(W/'ROOT_DECLARED_PHYSICAL_RUNTIME_EXPECTATIONS_SIX.json')
accepted=read(W/'ROOT_GPU_FULL_V2_ACCEPTANCE.json');gpu={v['task_id']:v for v in accepted['per_task_manifests']}
controller=physical['controller_expected_physical_image_from_cfg'];fiscal=F/'finance_config_science_common_C0_v4.json'
dependencies=read(E/'resource_gpu_f32_v1_SOURCE_ONLY/GPU_RESOURCE_PROTOCOL_SOURCE_ONLY.json')['controller_dependency_paths']
base_budget={k:v for k,v in read(OLD/'contracts241.py') .items()} if False else {'model_calls_total':1024,'output_tokens_total':8388608,'product_native_roots_total':2048,'all_owned_OS_roots_total':4096,'flow_wall_seconds_including_final':3600,'per_native_timeout_seconds':90,'final_once_independent_validation':1,'max_model_call_output_tokens':16384,'methods_keep_paper_internal_parameters':True,'no_theoretical_or_cross_model_success_guarantee':True}
inputs={};commands={}
for task in ea['task_order']:
 c=read(E/'candidate'/task/'public_contract.json');phys=next(v for v in physical['tasks'] if v['task_id']==task)
 c['physical_product_python_expected']=phys['expected_physical_image_from_declared_venv_config'];save(D/'candidate'/task/'public_contract.json',c)
 bind={'task_id':task,'Root_qualified':True,'resource_complete':True,'resource_terminal':accepted['resource_terminal'],'resource_terminal_sha256':accepted['resource_terminal_SHA256'],'resource_complete_receipt':accepted['complete_receipt'],'resource_complete_receipt_sha256':accepted['complete_receipt_SHA256'],'index_manifest':gpu[task]['manifest'],'index_manifest_sha256':gpu[task]['SHA256'],'Root_actual_acceptance':str(W/'ROOT_GPU_FULL_V2_ACCEPTANCE.json'),'Root_actual_acceptance_sha256':sha(W/'ROOT_GPU_FULL_V2_ACCEPTANCE.json'),'GPU_numerical_backend_sha256':accepted['GPU_numerical_backend_sha256']}
 save(D/'candidate'/task/'GPU_INDEX_BINDING.json',bind)
 p=read(OLD/'candidate'/task/'protocol.SOURCE_ONLY.json');p.update(schema='Agentless241-runtime-v3-shared-masked-public-source/1',source_only=True,execution_authorized=False,
  task_order=ea['task_order'],budget=base_budget,controller_dependency_paths=dependencies,product_dependency_paths=[],public_contract=str(D/'candidate'/task/'public_contract.json'),
  shared_public_helper={'path':str(SHARED/'native_masked_public239.py'),'sha256':sha(SHARED/'native_masked_public239.py')},
  public_test_scope_contract=ea['public_test_scope_contract'],masked_native_owner_root=str(D),masked_native_guard_directory=str(SHARED/'guard_v3'),
  shared_public_scope_root_qualified=True,common_budget_root_freeze={'Root_declared_source':str(W/'ROOT_SIX_SOURCE_PROTOCOL_FALSE.json')},
  fresh_current_C0_qualification=ea['shared_C0_qualification'],common_C0_not_repeated=True,
  GPU_public_index_binding=str(D/'candidate'/task/'GPU_INDEX_BINDING.json'),finance_config=str(fiscal),finance_config_sha256=sha(fiscal),
  core_source=str(D/'agentless_paper_main241.py'),output_root=str(D/'runs'/task),supervision_output_root=str(D/'supervision'/task),
  once_private_authorized=False,model_generation_authorized=False,native_authorized=False,automatic_six_same_source_seal_required=True,
  public_goal_ordinary_oracle_contract=ea['public_goal_ordinary_oracle_contract'],public_goal_ordinary_oracle_contract_sha256=ea['public_goal_ordinary_oracle_contract_sha256'])
 save(D/'candidate'/task/'protocol.SOURCE_ONLY.json',p)
 grant={'schema':'Agentless241-unified-six-paper-main-root-stage-grant/1','task_id':task,'root_authorized':False,'model_generation_authorized':False,'native_authorized':False,'private_acceptance_authorized':False,'stage':'FULL_PAPER_MAIN_SCIENCE_ONCE','finance_phase':p['finance_phase'],'new_start_UTC':None,'controller_physical_python_expected':controller,'product_physical_python_expected':c['physical_product_python_expected'],'parent_controller_job_qualified':False,'registry_sha256':p['registry_sha256'],'protocol_sha256':digest(p),'protocol_raw_sha256':sha(D/'candidate'/task/'protocol.SOURCE_ONLY.json'),'source_seal_sha256':None,'neutral_mechanical_qualification_sha256':None}
 save(D/'candidate'/task/'ROOT_SCIENCE_GRANT.false.template.json',grant);grant['stage']='MECHANICAL_ZERO_POST';save(D/'candidate'/task/'ROOT_MECHANICAL_GRANT.false.template.json',grant)
 prefix=[controller,'-X','utf8','-B',str(D/'supervisor_runtime_v3_241.py')]
 args=['--protocol',str(D/'candidate'/task/'protocol.SOURCE_ONLY.json'),'--seal',str(D/'SOURCE_SEAL.json'),'--contract',str(D/'candidate'/task/'public_contract.json')]
 commands[task]={'mechanical_zero_POST':prefix+['mechanical',*args,'--grant',str(D/'candidate'/task/'ROOT_MECHANICAL_GRANT.json')],'science_full_first':prefix+['science',*args,'--grant',str(D/'candidate'/task/'ROOT_SCIENCE_GRANT.json')]}
 for name in ('public_contract.json','GPU_INDEX_BINDING.json'):inputs[str(D/'candidate'/task/name)]=sha(D/'candidate'/task/name)
sources={str(p):sha(p) for p in D.glob('*.py')}
for p in (SHARED/'native_masked_public239.py',SHARED/'guard_v3/sitecustomize.py',SHARED/'guard_v3/runner.py',F/'completion_transport_common_C0_v4.py',F/'completion_transport_v3.py',F/'continuous_core_v3.py',F/'common_model_input_six.py',F/'common_public_feedback_codec.py'):sources[str(p)]=sha(p)
for p in (fiscal,W/'COMMON_MASKED_PUBLIC_TEST_SCOPE.json',W/'COMMON_EXISTING_PUBLIC_ORACLE_PERMISSION.json',W/'ROOT_GPU_FULL_V2_ACCEPTANCE.json',W/'ROOT_ALL_SIX_CURRENT_C0_ACCEPTANCE.json',W/'ROOT_DECLARED_PHYSICAL_RUNTIME_EXPECTATIONS_SIX.json'):inputs[str(p)]=sha(p)
seal={'author_pin':'5ce5888b9f149beaace393957a55ea8ee46c9f71','sources':sources,'inputs':inputs,'schema':'AL241-shared-runtime-v3-source-seal/1'};save(D/'SOURCE_SEAL.json',seal)
for p in (D/'candidate').rglob('*.false.template.json'):
 g=read(p);g['source_seal_sha256']=digest(seal);save(p,g)
save(D/'ROOT_COMMANDS_FALSE.json',commands)
save(D/'SOURCE_READY_RUNTIME_V3_FALSE.json',{'schema':'AL241-minimal-full-paper-shared-v3-source-ready/1','at_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'directory':str(D),'source_seal_sha256':digest(seal),'source_seal_raw_sha256':sha(D/'SOURCE_SEAL.json'),'source_AST_pass':True,'original_full_4L40P40T_unchanged':True,'task_order':ea['task_order'],'all_grants_false':True,'shared_helper_guard_runner_SHA':{str(p):sha(p) for p in (SHARED/'native_masked_public239.py',SHARED/'guard_v3/sitecustomize.py',SHARED/'guard_v3/runner.py')},'Root_commands':str(D/'ROOT_COMMANDS_FALSE.json'),'actual_API_native_fixture_encoder_private':0,'independent_final_external_to_author_required':True,'one_environment_seal_all_six_no_percase_code_change':True})
print(canonical({'ready':str(D/'SOURCE_READY_RUNTIME_V3_FALSE.json'),'seal':digest(seal),'commands':str(D/'ROOT_COMMANDS_FALSE.json'),'actual_experiments':0}))

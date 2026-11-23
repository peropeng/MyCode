"""Prepare only AST/SHA artifacts. Never import product/model/transport or run native."""
from pathlib import Path
import ast, datetime, hashlib, json

E=Path(__file__).resolve().parent
D=E/'source_runtime_v1'
ROOT=Path('D:/Code/毕设/graduate-thesis-experiments')
OLD=E.parent/'实验241_Agentless新确认集21_生成测试ScopeV3_AST兼容'
FISCAL=ROOT/'工作区/1010-unified-six/finance'
METHOD='AGENTLESS_FSE2025_PAPER_MAIN_4L40P40T_FLASH_QWEN_EMBED_ADAPTED'
PHASE='UnifiedSixAgentless24120261010'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
def source(name,text):
 ast.parse(text);(D/name).write_text(text,'utf-8')
def replace(text,old,new):
 if old not in text:raise ValueError('EXACT_SOURCE_ANCHOR_REQUIRED '+old[:90])
 return text.replace(old,new)

if D.exists():raise RuntimeError('SOURCE_RUNTIME_ONCE_PREPARATION_NO_OVERWRITE')
D.mkdir()
copied=['public_v2_241.py','normalization_adapter_v3_241.py','generated_scope_v2_241.py',
 'product_entry241.py','supervision_classification241.py','shared_json_read241.py']
for name in copied:source(name,(OLD/name).read_text('utf-8-sig'))
for name in ('agentless_paper_main241.py','paper_local_core241.py'):
 source(name,(E/name).read_text('utf-8-sig'))
save(D/'PAPER_CORE_SOURCE_PROVENANCE241.json',read(E/'PAPER_CORE_SOURCE_PROVENANCE241.json'))

contracts=(OLD/'contracts241.py').read_text('utf-8-sig')
contracts=replace(contracts,"ROOT = HERE.parents[3]","ROOT = Path("+repr(str(ROOT))+")")
contracts=replace(contracts,"NO_NEW = '2026-10-10T03:40:00Z'","NO_NEW = None")
contracts=replace(contracts,"HARD = '2026-10-10T04:00:00Z'","HARD = None")
contracts=replace(contracts,"METHOD = 'AGENTLESS_FSE2025_4L4P4T_FLASH'","METHOD = "+repr(METHOD))
contracts=replace(contracts,"FINANCE_PHASE = 'AgentlessConfirm24120261010'","FINANCE_PHASE = "+repr(PHASE))
contracts=contracts[:contracts.index('def prepare_public_contract')]+'''
COMMON_BUDGET={'model_calls_total':1024,'output_tokens_total':8388608,
 'product_native_roots_total':2048,'all_owned_OS_roots_total':4096,
 'flow_wall_seconds_including_final':3600,'per_native_timeout_seconds':90,
 'final_once_independent_validation':1,'max_model_call_output_tokens':16384,
 'methods_keep_paper_internal_parameters':True,'no_theoretical_or_cross_model_success_guarantee':True}

def verify_grant(protocol,grant,source_seal,task_id,now=None):
 now=time.time() if now is None else now
 if (grant.get('schema')!='Agentless241-unified-six-paper-main-root-stage-grant/1'
  or grant.get('root_authorized') is not True or grant.get('model_generation_authorized') is not True
  or grant.get('stage')!='FULL_PAPER_MAIN_SCIENCE_ONCE'
  or protocol.get('execution_authorized') is not True or protocol.get('source_only') is not False):
  raise EngineeringUnknown('NEW_EXPLICIT_ROOT_FULL_PAPER_STAGE_GRANT_REQUIRED')
 if protocol.get('scope')!='UNIFIED_SIX_NEW_WINDOW' or protocol.get('method')!=METHOD:
  raise EngineeringUnknown('NEW_SCOPE_OR_FULL_PAPER_METHOD_MISMATCH')
 if (grant.get('finance_phase')!=FINANCE_PHASE or protocol.get('finance_phase')!=FINANCE_PHASE
  or grant.get('task_id')!=task_id or protocol.get('task_id')!=task_id):
  raise EngineeringUnknown('TASK_OR_COMPLETION_PHASE_MISMATCH')
 if protocol.get('deadline')!={'no_new_utc':None,'hard_utc':None} or protocol.get('budget')!=COMMON_BUDGET:
  raise EngineeringUnknown('ROOT_COMMON3600_CAPACITY_AND_NO_GLOBAL_DEADLINE_REQUIRED')
 if Path(protocol['closure_flag']).resolve()!=ROOT/'工作区/1010-unified-six/STOP_NEW_SIX.json':
  raise EngineeringUnknown('ROOT_SHARED_COMPLETION_STOP_SCOPE_MISMATCH')
 if Path(protocol['closure_flag']).exists():raise EngineeringUnknown('ROOT_SHARED_COMPLETION_STOP')
 start=deadline_epoch(grant.get('new_start_UTC'))
 if not grant.get('new_start_UTC') or not start<=now<start+3600:
  raise DeclaredBudgetEnd('NEW_SINGLE_FLOW3600_CLOCK_NOT_CURRENT')
 if grant.get('source_seal_sha256')!=digest(source_seal) or grant.get('protocol_sha256')!=digest(protocol):
  raise EngineeringUnknown('SOURCE_OR_PROTOCOL_STAGE_GRANT_DRIFT')
 if protocol.get('registry_sha256')!=REGISTRY_SHA or grant.get('registry_sha256')!=REGISTRY_SHA:
  raise EngineeringUnknown('COMMON_FROZEN21_REGISTRY_MISMATCH')
 if (not grant.get('neutral_mechanical_qualification_sha256') or not grant.get('parent_controller_job_qualified')
  or not protocol.get('fresh_current_C0_qualification') or not protocol.get('common_budget_root_freeze')):
  raise EngineeringUnknown('NEW_ACTUAL_C0_JOB_AND_COMMON_BUDGET_REQUIRED')
 for p,h in source_seal['sources'].items():
  if sha(p)!=h:raise EngineeringUnknown('NEW_SEALED_SOURCE_DRIFT '+p)
 for p,h in source_seal['inputs'].items():
  if sha(p)!=h:raise EngineeringUnknown('NEW_SEALED_INPUT_DRIFT '+p)
 if source_seal.get('author_pin')!=SOURCE_PIN:raise EngineeringUnknown('PAPER_ORIGINAL_SOURCE_PIN_DRIFT')
 if sha(protocol['finance_config'])!=protocol['finance_config_sha256']:
  raise EngineeringUnknown('CONTINUOUS_COMPLETION_CONFIG_DRIFT')
 config=read(protocol['finance_config'])
 if (config.get('model_generation_authorized') is not True or config.get('schema')!='continuous-human-completion/3'
  or config.get('hard_deadline_utc') is not None or config.get('no_new_utc') is not None
  or task_id not in config.get('common_tasks',[]) or FINANCE_PHASE not in config.get('phases',{})):
  raise EngineeringUnknown('ROOT_LIVE_COMPLETION_FISCAL_AUTHORIZATION_REQUIRED')
 return True
'''
source('contracts241.py',contracts)

owner=(OLD/'owner241.py').read_text('utf-8-sig')
owner=replace(owner,'self.started+900','self.started+3600')
owner=replace(owner,'original_birth+900','original_birth+3600')
owner=replace(owner,"self.started=time.monotonic();self.flow_deadline=", "self.started=time.monotonic();self.flow_deadline=")
owner=replace(owner,"self.output_root=Path(self.protocol['output_root']).resolve();self.out=self.output_root",
 "self.flow_deadline=min(self.flow_deadline,time.monotonic()+max(0,deadline_epoch(self.grant.get('new_start_UTC'))+3600-time.time()))\n        self.output_root=Path(self.protocol['output_root']).resolve();self.out=self.output_root")
owner=replace(owner,"now=min(time.time(),deadline_epoch(NO_NEW)-1) if allow_no_new else None","now=None")
owner=owner.replace('DECLARED_COMMON900_WALL_END','DECLARED_COMMON3600_WALL_END')
owner=replace(owner,"self.protocol['budget']['native_roots_total']","self.protocol['budget']['all_owned_OS_roots_total']")
owner=replace(owner,'DEPLOYMENT_ALL_OS_NATIVE90_RESOURCE_CENSORED','COMMON_ALL_OWNED_OS4096_RESOURCE_CENSORED')
owner=replace(owner,'COMMON_ACTUAL_PRODUCT_NATIVE64_BUDGET_BEFORE_SPAWN','COMMON_ACTUAL_PRODUCT_NATIVE2048_BUDGET_BEFORE_SPAWN')
source('owner241.py',owner)

environment=(OLD/'environment241.py').read_text('utf-8-sig')
environment=replace(environment,'Deployment facade only; unchanged FSE2025 4L4P4T algorithm owns decisions.','Full paper 4L40P40T facade; exact stage output caps and guarded real regression.')
environment=replace(environment,'from owner241 import Owner','from owner241 import Owner\nfrom paper_environment_binding241 import PaperMainEnvironmentMixin')
environment=replace(environment,"core=module('agentless178',AL/'agentless178.py')","core=module('agentless_paper_main241',HERE/'agentless_paper_main241.py')")
environment=environment.replace(' original_retrieve=retrieval.retrieve\n','')
environment=replace(environment,'# Same central offset[3,2] MONAI / [2] others, not a second torch mutex.','# Full GPU preprocessing is sealed separately; this stage only reads vectors.')
environment=replace(environment,"with owner.native_lane():return original_retrieve(files,query,ref,allowed)",
 "from gpu_index_adapter241 import retrieve\n  return retrieve(owner,files,query,ref,allowed)")
environment=replace(environment,'class Environment241(Owner):','class Environment241(PaperMainEnvironmentMixin,Owner):')
environment=replace(environment,"'author_method_SHA256':sha(AL/'agentless178.py')","'author_method_SHA256':sha(HERE/'agentless_paper_main241.py')")
start=environment.index("  cap={'agentless_localize':8192")
end=environment.index('  body=body_v2',start)
environment=environment[:start]+'''  cap=self.paper_model_call_cap(role,max_tokens)
  budget=self.protocol['budget']
  if self.calls>=budget['model_calls_total'] or self.out_tokens+cap>budget['output_tokens_total']:
   raise DeclaredBudgetEnd('COMMON1024_CALL_OR8388608_OUTPUT_BUDGET')
'''+environment[end:]
source('environment241.py',environment)

binding=(E/'paper_environment_binding241.py').read_text('utf-8-sig')
binding=replace(binding,"self.paper_public_repository_regression_nodes=list(pool['nodes']);self.paper_pool=pool",
 "self.paper_public_repository_regression_nodes=list(pool['nodes']);self.paper_pool=pool;self.paper_pool_manifest_sha256=binding['public_pool_manifest_sha256']")
binding=replace(binding,"self.protocol['budget']['native_timeout_seconds']","self.protocol['budget']['per_native_timeout_seconds']")
binding=replace(binding,"self.paper_pool['manifest_sha256']","self.paper_pool_manifest_sha256")
source('paper_environment_binding241.py',binding)

transport='''"""Continuous fiscal v3 only; no constructor/import/network until true actor grant."""
import threading
from contracts241 import *
FISCAL=ROOT/'工作区/1010-unified-six/finance'
root=module('_AL241_completion_transport_v3',FISCAL/'completion_transport_v3.py')
FinanceError=root.FinanceError
FinanceGateRejected=GateRejected=root.GateRejected
FinanceUnknown=Unknown=root.Unknown
LegacyIO=root.LegacyIO
_instance=None;_owner=None;_lock=threading.Lock()
def construct(owner):
 global _instance,_owner
 owner.require_action('LLM_TRANSPORT_CONSTRUCTION')
 with _lock:
  if _instance is None:
   from scoped_finance_artifacts241 import install
   install(__import__(__name__),owner)
   _instance=root.make_transport(read(owner.protocol['finance_config']),LegacyIO());_owner=owner
  if _owner is not owner:raise EngineeringUnknown('SCOPED_TRANSPORT_OWNER_NOT_REUSABLE')
 return _instance
def generate(owner,body,role,phase=FINANCE_PHASE):
 if phase!=FINANCE_PHASE:raise FinanceUnknown('UNIFIED_PHASE_MISMATCH')
 owner.require_action('LLM_POST_BOUNDARY')
 return construct(owner).generate(owner,body,role,FINANCE_PHASE)
'''
source('flash_transport241.py',transport)
scoped=(OLD/'scoped_finance_artifacts241.py').read_text('utf-8-sig')
scoped=scoped.replace('from bounded_atomic_retry241 import patched_atomic\n','')
scoped=replace(scoped,'   self.m.atomic=patched_atomic(self.m)','   # completion_transport_v3.make_transport installs bounded Win5 atomic once.')
source('scoped_finance_artifacts241.py',scoped)

runner=(OLD/'winjob241.py').read_text('utf-8-sig')
runner=replace(runner,'900 if controller else 90','3600 if controller else 90')
source('winjob241.py',runner)
cli=(OLD/'cli241.py').read_text('utf-8-sig')
cli=replace(cli,"sha(__import__('public_v2_241').AL/'agentless178.py')","sha(HERE/'agentless_paper_main241.py')")
cli=cli.replace('One fully original author4L4P4T run','One full paper author4L40P40T run').replace('author_algorithm_unchanged=True','author_paper_main_configuration=True')
source('cli241.py',cli)

gpu='''"""Read-only qualified GPU index; original dense166 cosine/order without encoding."""
from contracts241 import *
def retrieve(owner,files,query,ref,allowed):
 from agentless_bridge import dense166
 b=read(owner.protocol['GPU_public_index_binding'])
 if (b.get('Root_qualified') is not True or b.get('resource_complete') is not True
  or b.get('task_id')!=owner.task_id):raise EngineeringUnknown('ROOT_FULL_GPU_INDEX_BINDING_REQUIRED')
 for key in ('resource_terminal','resource_complete_receipt','index_manifest','Root_actual_acceptance'):
  if not b.get(key) or sha(b[key])!=b.get(key+'_sha256'):raise EngineeringUnknown('GPU_ACTUAL_RECEIPT_SHA_DRIFT '+key)
 terminal=read(b['resource_terminal']);full=read(b['resource_complete_receipt']);cache=read(b['index_manifest'])
 stop=terminal.get('raw_job_result',{}).get('stop_receipt',{})
 if (terminal.get('status')!='COMPLETE_RESOURCE_STOP_ONLY' or terminal.get('phase')!='full_six'
  or not all(stop.get(k) is True for k in ('root_stopped','own_Job_empty_before_close','descendants_stopped'))
  or full.get('status')!='COMPLETE_GPU_PUBLIC_INDEX_ONLY' or full.get('unique_GPU_vectors')!=13877
  or full.get('complete_query_vectors')!=6 or full.get('CPU_numeric_or_qualification_value_reuse') is not False):
  raise EngineeringUnknown('ACTUAL_FULL13877_GPU_AND_OWN_STOP_REQUIRED')
 numeric=b['GPU_numerical_backend_sha256']
 if full.get('GPU_numerical_backend_sha256')!=numeric or cache.get('GPU_numerical_backend_sha256')!=numeric:
  raise EngineeringUnknown('ROOT_NEW_GPU_NUMERIC_VERSION_DRIFT')
 exact={p:hashlib.sha256(v.encode('utf-8')).hexdigest() for p,v in sorted(files.items())}
 if (cache.get('status')!='SEALED_GPU_COMPLETE' or cache.get('task_id')!=owner.task_id
  or cache.get('source_files_sha256')!=exact or cache.get('query_sha256')!=hashlib.sha256(query.encode('utf-8')).hexdigest()
  or cache.get('query_complete') is not True or cache.get('query_truncated') is not False
  or cache.get('CPU_numeric_cache_reuse') is not False or cache.get('original_model_identity')!=dense166.identity()):
  raise EngineeringUnknown('GPU_EXACT_FULL_SOURCE_QUERY_MODEL_REQUIRED_NO_ENCODER_FALLBACK')
 maps=cache['source_original_keys_to_GPU'];vectors=Path(cache['vectors_dir'])
 for source_key,gpu_key in maps.items():
  actual=full['full_vector_contentSHA_binding'].get(source_key)
  if not actual or actual['GPU_key']!=gpu_key or actual['sha256']!=cache['vector_sha256'].get(gpu_key):
   raise EngineeringUnknown('GPU_ORIGINAL_KEYS_FULL_SEAL_DRIFT')
  path=vectors/(gpu_key+'.npy')
  if sha(path)!=actual['sha256'] or not dense166.vector_valid(path):raise EngineeringUnknown('GPU_FINITE_FLOAT32_L2_OR_BYTES_DRIFT')
 # Minimal format adaptation, preserving and explicitly labelling GPU provenance.
 # All original retrieve() bypass inputs are verified above; prepare() is never called.
 compatible={**cache,'model_identity':cache['original_model_identity'],
  'model_identity_sha256':cache['original_model_identity_sha256'],'encoder_new_texts':0,
  'format_adaptation_only':True,'not_a_CPU_numeric_cache':True,'root_GPU_manifest_SHA':b['index_manifest_sha256']}
 path=owner.output_root/'retrieval_readonly/GPU_DENSE166_COMPAT_REF.json'
 save(path,compatible,scope=owner.output_root)
 result,evidence=dense166.retrieve(files,query,path,allowed)
 evidence.update(GPU_complete_index=True,GPU_numerical_backend_sha256=numeric,
  source_GPU_manifest_sha256=b['index_manifest_sha256'],new_actor_encoder_forward=0,
  original_dense166_function_unchanged=True,CPU_SHA_equivalence_claim=False,
  preprocessing_seconds_full_six=full['GPU_encode_seconds'],preprocessing_accounted_separately=True)
 return result,evidence
'''
source('gpu_index_adapter241.py',gpu)

template=read(E/'candidate/getmoto__moto-5406/protocol.SOURCE_ONLY.json')
for task in read(ROOT/'工作区/1010-unified-six/ROOT_SIX_SOURCE_PROTOCOL_FALSE.json')['proposed_tasks']:
 p=read(E/'candidate'/task/'protocol.SOURCE_ONLY.json')
 p.update(schema='Agentless241-full-paper-source-runtime-protocol/1',finance_phase=PHASE,
  deadline={'no_new_utc':None,'hard_utc':None},budget=None,common_budget_proposal=read(ROOT/'工作区/1010-unified-six/ROOT_SIX_SOURCE_PROTOCOL_FALSE.json')['common_budget_proposal'],
  finance_config=str(FISCAL/'finance_config_completion_v3.json'),finance_config_sha256=sha(FISCAL/'finance_config_completion_v3.json'),
  closure_flag=str(ROOT/'工作区/1010-unified-six/STOP_NEW_SIX.json'),core_source=str(D/'agentless_paper_main241.py'),
  GPU_public_index_binding=str(D/'candidate'/task/'GPU_PUBLIC_INDEX_BINDING.pending.json'),registry_sha256='298efeac0dcf0498ed8f78e0067c8e24a963e24c29442fc0df64d8e047b7a37c',
  output_root=str(D/'runs'/task/METHOD),supervision_output_root=str(D/'supervision'/task),
  ready_for_real_execution=False,product_controller_profiles=None,controller_dependency_paths=None,product_dependency_paths=None)
 save(D/'candidate'/task/'protocol.SOURCE_ONLY.json',p)
 save(D/'candidate'/task/'GPU_PUBLIC_INDEX_BINDING.pending.json',{'task_id':task,'Root_qualified':False,'resource_complete':False,
  'resource_terminal':None,'resource_complete_receipt':None,'index_manifest':None,'Root_actual_acceptance':None,'GPU_numerical_backend_sha256':None})
 save(D/'candidate'/task/'ROOT_STAGE_GRANT.false.template.json',{'schema':'Agentless241-unified-six-paper-main-root-stage-grant/1',
  'task_id':task,'root_authorized':False,'model_generation_authorized':False,'private_acceptance_authorized':False,
  'stage':'FULL_PAPER_MAIN_SCIENCE_ONCE','finance_phase':PHASE,'new_start_UTC':None})
sources={str(p):sha(p) for p in sorted(D.glob('*.py'))}
save(D/'SOURCE_RUNTIME_READY_NOT_EXECUTABLE.json',{'schema':'Agentless241-full-paper-runtime-source-only/1',
 'at_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':sources,'source_AST_pass':True,
 'paper_internal_4L40P40T':True,'stage_caps_original_not_old_override':True,'common_3600_capacity_proposal_not_Root_granted':True,
 'completion_transport_v3_source':str(FISCAL/'completion_transport_v3.py'),
 'fiscal_sources':{str(FISCAL/n):sha(FISCAL/n) for n in ('completion_transport_v3.py','continuous_core_v3.py','finance_config_completion_v3.json')},
 'science_and_private_grants_false':True,'actual_model_native_encoder_POST_fiscal':0,'ready_for_execution':False,
 'pending':['Root public repo testpool human authorization and new independent acceptance boundary',
  'Root fresh public C0/native physical qualification/3600 common budget stage freeze',
  'actual GPU full13877 + Root seal/STOP review + per-task binding',
  'Root live fiscal generation config and true independent actor stage grant',
  'new mechanical harness/supervisor/external-final binding must not copy old private nodes or values']})
print(json.dumps({'SOURCE_READY':str(D/'SOURCE_RUNTIME_READY_NOT_EXECUTABLE.json'),'py_files_AST':len(sources),'execution':False},ensure_ascii=False))

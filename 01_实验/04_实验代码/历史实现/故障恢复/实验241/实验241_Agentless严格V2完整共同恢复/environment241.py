"""Deployment facade only; unchanged FSE2025 4L4P4T algorithm owns decisions."""
import ast,copy,re,sys,types,uuid
from contracts241 import *
from owner241 import Owner
from public_v2_241 import AL,SOURCE,body_v2,initial_index_v2,semantic_index

def install_author(owner):
 for path in reversed(owner.protocol['controller_dependency_paths']):sys.path.insert(0,path)
 bridge=types.ModuleType('agentless_bridge');bridge.__path__=[str(AL/'agentless_bridge')]
 bridge.__package__='agentless_bridge';sys.modules['agentless_bridge']=bridge
 common=types.ModuleType('common166')
 def append(path,value):
  path=Path(path).resolve()
  if not inside(path,HERE):raise EngineeringUnknown('APPEND_WRITE_SCOPE')
  path.parent.mkdir(parents=True,exist_ok=True)
  with path.open('a',encoding='utf-8') as f:f.write(canonical(value)+'\n')
 common.__dict__.update(E=HERE,ROOT=ROOT,OLD=AL,Path=Path,os=os,sys=sys,time=time,
  hashlib=hashlib,json=json,read=read,sha=sha,canonical=canonical,digest=digest,module=module,save=save,append=append,
  now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat())
 sys.modules['common166']=common
 index_module=types.ModuleType('common_environment224');index_module.semantic_index=semantic_index
 sys.modules['common_environment224']=index_module
 retrieval=module('retrieval178',SOURCE/'retrieval178.py')
 core=module('agentless178',AL/'agentless178.py')
 original_retrieve=retrieval.retrieve
 def actual_same_dense(files,query,ref,allowed):
  owner.require_action('dense_retrieval')
  # Same central offset[3,2] MONAI / [2] others, not a second torch mutex.
  with owner.native_lane():return original_retrieve(files,query,ref,allowed)
 core.retrieve=actual_same_dense
 core.implementation_receipt()
 return core,retrieval

class Environment241(Owner):
 def __init__(self,*args):
  super().__init__(*args);self._external_evaluator=False;self.stage_ledger=[];self.snapshots={};self.patch_candidates=[]
  self.public_regression_nodes=list(self.contract['ordinary_nodes']);self.recovery_goal_nodes=list(self.contract['public_target_nodes'])
  self.goal='Recover the observed public failure and preserve already passing ordinary behavior. Original issue background: '+self.semantic['original_issue']
  self.initial_public_feedback=initial_index_v2(self.pack);self.retrieval_cache=None;self.core=None
 def time_left(self):
  reserve=0 if getattr(self,'_external_evaluator',False) else 90
  return max(0,self.flow_deadline-reserve-time.monotonic())
 def record(self,stage,evidence=None):
  if evidence is None:return super().record(stage)
  row={'stage':stage,'evidence':copy.deepcopy(evidence)};self.stage_ledger.append(row)
  self.output_root.mkdir(parents=True,exist_ok=True)
  with (self.output_root/'stage_ledger.jsonl').open('a',encoding='utf-8') as f:f.write(canonical(row)+'\n')
  super().record({'event':'AUTHOR_STAGE','stage':stage,'evidence':evidence});return evidence
 def initialize(self):
  self.before_controller();self.initial_snapshot=self.snapshot('C0')
  self.core,self.retrieval=install_author(self)
  self.retrieval_query=self.retrieval.public_query({'task':self.semantic['original_issue'],'failure_feedback':self.semantic['failure_feedback']})
  self.record('INDEPENDENT_V2_PUBLIC_INPUT',{'input_digest':self.contract['input_digest'],'pack_sha256':self.contract['pack_sha256'],
   'same_all_public_history':True,'same_original_body_function':True,'no_added_reader_loop':True,
   'business_C0_inventory_sha256':digest(self.actor_business_inventory()),'author_method_SHA256':sha(AL/'agentless178.py')})
  return self
 def business_files(self):return {p:(self.actor_root/p).read_text('utf-8') for p in self.actor_business_inventory()}
 def snapshot(self,label=None):
  inv=self.actor_business_inventory();c0=self.contract['c0_business_paths_sha256']
  changes={p:inv.get(p) for p in sorted(set(inv)|set(c0)) if inv.get(p)!=c0.get(p)}
  ident='s'+str(len(self.snapshots)).zfill(4);out=self.output_root/'snapshots'/ident;out.mkdir(parents=True,exist_ok=False)
  for rel,h in changes.items():
   if h is not None:
    target=out/'files'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((self.actor_root/rel).read_bytes())
  value={'id':ident,'label':label,'inventory_sha256':digest(inv),'diff':changes,'archive_path':str(out)}
  self.snapshots[ident]=value;save(out/'snapshot.json',value,scope=self.output_root);return copy.deepcopy(value)
 def restore(self,snapshot):
  if snapshot!=self.snapshots[snapshot['id']]:raise EngineeringUnknown('SNAPSHOT_BINDING_DRIFT')
  inv=self.actor_business_inventory();c0=self.contract['c0_business_paths_sha256']
  changed={p for p in set(inv)|set(c0) if inv.get(p)!=c0.get(p)}|set(snapshot['diff'])
  for rel in changed:
   target=self.actor_path(rel);h=snapshot['diff'].get(rel,c0.get(rel))
   if h is None:
    if target.exists():target.unlink()
   else:
    source=Path(snapshot['archive_path'])/'files'/rel if rel in snapshot['diff'] else Path(self.contract['template'])/rel
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
    if sha(target)!=h:raise EngineeringUnknown('RESTORED_BYTES_DRIFT')
  if digest(self.actor_business_inventory())!=snapshot['inventory_sha256']:raise EngineeringUnknown('RESTORED_INVENTORY_DRIFT')
 def apply_patch(self,edits,label,from_snapshot=None):
  self.require_action('patch');base=from_snapshot or self.initial_snapshot;self.restore(base);errors=[]
  try:
   if not isinstance(edits,list) or not edits:raise ValueError('EMPTY_OR_INVALID_GENERATED_PATCH')
   for edit in edits:
    path=edit['path'].removeprefix('repo/');p=self.actor_path(path)
    if 'file_text' in edit:
     if p.exists():raise ValueError('CREATED_PRODUCT_ALREADY_EXISTS')
     after=edit['file_text']
    else:
     old=edit.get('old',edit.get('old_str'));new=edit.get('new',edit.get('new_str',''));text=p.read_text('utf-8')
     if not old or text.count(old)!=1:raise ValueError('SEARCH_NOT_UNIQUE_OR_MISSING')
     after=text.replace(old,new,1)
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(after.encode('utf-8'))
   self.actor_business_inventory();legal={'legal':True}
  except (IllegalTool,ValueError,KeyError) as error:
   errors.append(type(error).__name__+': '+str(error));self.restore(base);legal={'legal':False}
  snapshot=self.snapshot(label);row={'candidate_id':len(self.patch_candidates),'snapshot':snapshot,'legal':legal,'apply_errors':errors,
   'edits':copy.deepcopy(edits),'independent_original_root':from_snapshot is None}
  self.patch_candidates.append(row);self.record('patch_application',row);return row
 def llm(self,role,messages,temperature,seed,max_tokens,schema=None,tools=None):
  self.require_action('LLM')
  if not role.startswith('agentless_') or tools:raise EngineeringUnknown('AUTHOR_ONLY_DIRECT_TEXT_NO_READER_TOOLS')
  if role in ('agentless_patch','agentless_reproduction'):
   self.restore(self.initial_snapshot)
   if self.actor_business_inventory()!=self.contract['c0_business_paths_sha256']:raise EngineeringUnknown('INDEPENDENT_CANDIDATE_NOT_C0')
  group=('agentless_localize' if role in ('agentless_suspicious_files','agentless_irrelevant_folders','agentless_related_elements','agentless_fine_locations')
   else 'agentless_regression_or_vote' if role=='agentless_regression_exclusion' else role)
  cap={'agentless_localize':8192,'agentless_patch':16384,'agentless_reproduction':8192,'agentless_regression_or_vote':4096}[group]
  if self.calls>=64 or self.out_tokens+cap>65536:raise DeclaredBudgetEnd('COMMON_CALL_OR_OUTPUT_BUDGET')
  body=body_v2(role,copy.deepcopy(messages),temperature,seed,cap,self.task_id,METHOD,self.pack,schema,[],0)
  self.record('v2_actual_body_preflight',{'role':role,'body_sha256':digest(body),'serialized_body_utf8_bytes':len(canonical(body).encode()),
   'reader_index':0,'AL_no_reader_tools':True,'pack_semantic_sha256':self.pack['decoded_semantic_sha256']})
  self.calls+=1
  import flash_transport241 as transport
  try:response=transport.generate(self,body,'Exp241/V2_AUTH_DIRECT_PUBLICPACK/'+METHOD+'/'+self.task_id+'/'+role,phase=FINANCE_PHASE)
  except transport.GateRejected as error:
   end=DeclaredBudgetEnd('DECLARED_PREPOST_FINANCE_BUDGET_END '+str(error));self.latch_unknown(end,'FINANCE_CAP');raise end from error
  except BaseException as error:self.latch_unknown(error,'FLASH_SHARED_FINANCE');raise
  usage=response['usage'];self.out_tokens+=usage['completion_tokens'];message=response['choices'][0]['message'];finish=response['choices'][0].get('finish_reason')
  self.record('ACTUAL_FLASH_RESPONSE',{'role':role,'ordinal':self.calls,'usage':usage,'seed':body['seed'],'original_fixed_stage_seed':seed,
   'reader_index':0,'temperature':temperature,'finish_reason':finish,'finance_receipt':response.get('_finance_receipt')})
  return {'content':message.get('content') or '','message':message,'tool_calls':message.get('tool_calls') or [],'usage':usage,
   'call_ordinal':self.calls,'finish_reason':finish,'output_truncated':finish=='length','finance_receipt':response.get('_finance_receipt',{})}
 def run_regression(self,snapshot=None,nodes=None,label='regression'):
  requested=list(self.public_regression_nodes if nodes is None else nodes)
  if not set(requested)<=set(self.public_regression_nodes):raise ValueError('PRIVATE_OR_NONORDINARY_TEST_REQUEST')
  self.restore(snapshot or self.initial_snapshot);state=self.snapshot(label+'_state');probe=self.verify_public()
  outcomes=probe['outcomes'];ordinary={n:{**outcomes[n],'outcome':outcomes[n]['status']} for n in requested}
  fail=sum(v['status']!='passed' for v in ordinary.values())
  result={'passed':fail==0 and len(ordinary)==len(requested),'failure_count':fail,'outcomes':ordinary,
   'status':'GUARDED_ORDINARY_REGRESSION','native_record':{**probe,'executed':True,'guard_loaded':True},'public_goal_not_added_to_paper_ranking':True}
  return self.record('ordinary_regression',result)
 def run_reproduction(self,code,snapshot=None,label='reproduction'):
  self.require_action('generated');self.restore(snapshot or self.initial_snapshot);state=self.snapshot(label+'_state');ast.parse(code)
  if not code.strip():raise ValueError('EMPTY_REPRODUCTION_TEST')
  self.materialize_actor();out=self.output_root/'generated_native'/uuid.uuid4().hex;out.mkdir(parents=True)
  script=out/'generated_test.py';script.write_bytes(code.encode('utf-8'));env=self.qualify.isolated_env(self.active,self.repo_root,
   Path(self.contract['frozen_public_test_root']),out,self.logical_python,self.contract['package']);env['PATCHPILOT_ENTRY_MODE']='generated'
  before=inventory(self.repo_root);frozen=inventory(self.contract['frozen_public_test_root'])
  native=self.native_execute([self.logical_python,str(script)],out,out/'execution.log',90,env)
  if native['timeout'] or before!=inventory(self.repo_root) or frozen!=inventory(self.contract['frozen_public_test_root']):
   raise EngineeringUnknown('REPRODUCTION_TIMEOUT_OR_BOUNDARY_DRIFT')
  if 'PATCHPILOT_GENERATED_' in native['stdout']+native['stderr']:raise EngineeringUnknown('REPRODUCTION_GUARD_SCOPE_REFUSAL')
  imports=read(out/'actual_product_imports.json') if (out/'actual_product_imports.json').exists() else []
  guard=(out/'guard_ready.json').is_file()
  if not guard:raise EngineeringUnknown('REPRODUCTION_GUARD_NOT_LOADED')
  markers=[s.strip() for s in native['stdout'].splitlines() if s.strip() in ('Issue reproduced','Issue resolved','Other issues')]
  marker=markers[0] if len(markers)==1 and native['exit_code']==0 and imports else None
  native.update(executed=True,guard_loaded=True,business_state_unchanged=True,frozen_tests_unchanged=True,
   actual_product_imports=imports,generated_script_sha256=sha(script),snapshot_sha256=state['inventory_sha256'],semantic_marker=marker)
  save(out/'run.json',native,scope=self.output_root)
  return self.record('generated_reproduction_actual',{'status':marker or 'MODEL_REPRODUCTION_INVALID','reproduced':marker=='Issue reproduced',
   'resolved':marker=='Issue resolved','not_reproduced':marker=='Other issues','stdout':native['stdout'],'stderr':native['stderr'],
   'exit_code':native['exit_code'],'native_record':native})
 def select(self,snapshot,reason):
  self.restore(snapshot);value={'snapshot':snapshot,'reason':reason,'selected_before_hidden':True}
  save(self.output_root/'selection_before_private.json',value,scope=self.output_root);return value
 def finalize_selection(self,result):
  self.assert_no_unknown()
  if self.budget_end:raise DeclaredBudgetEnd('DECLARED_BUDGET_TERMINAL')
  if not result['runtime_core']['complete']:return {'status':result['status'],'success':False if result['status']=='MODEL_SEMANTIC_FAILURE' else None,**result}
  selected=result['final_snapshot'];self.restore(selected);business=self.materialize_actor()
  destination=self.output_root/'immutable_selection';copy_bytes(self.actor_root,destination,business)
  value={'task_id':self.task_id,'method':METHOD,'status':'SELECTED_AWAIT_EXTERNAL_PRIVATE','success':None,
   'selection_root':str(destination),'business_paths_sha256':business,'selected_sha256':digest(business),
   'author_original_selection':result['selection'],'author_runtime_core':result['runtime_core'],'LLM_calls':self.calls,'output_tokens':self.out_tokens,
   'public_native_calls':self.native_calls,'native_roots_including_controller':self.native_roots,'native_root_kinds':self.native_root_kinds,
   'private_calls_before_selection':0,'unknown':None,'author_done':True,'requires_once_private_external_to_actor':True}
  save(self.output_root/'immutable_selection.json',value,scope=self.output_root)
  return {**result,**value,'author_raw_status':result['status']}

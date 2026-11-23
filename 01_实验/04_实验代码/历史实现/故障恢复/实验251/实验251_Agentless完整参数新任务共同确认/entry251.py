"""Full unchanged 4L40P40T core; pure pause/replay at every actual boundary."""
import argparse, types
from runtime251 import *

STATE_FIELDS=('calls','out_tokens','native_calls','native_actual_OS_processes','snapshots','current_snapshot','patch_candidates','rows','forward_records')

class Journal:
 def __init__(self,o):
  self.o=o;self.cursor=0;self.active=False;self.root=o.out/'checkpoint'
  for name in ('business_files','restore','apply_patch','llm','run_regression','run_reproduction','select','dense_retrieval'):
   setattr(o,name,self.wrap(name,getattr(o,name)))
  o.checkpoint_core=self.core
 def state(self):
  v={k:copy.deepcopy(getattr(self.o,k)) for k in STATE_FIELDS}
  v['current_business_deltas']={p:t for p,t in self.o.files.items() if t!=self.o.original_files[p]}
  v['snapshot_business_deltas']={key:{p:t for p,t in texts.items() if t!=self.o.original_files[p]} for key,texts in self.o.snapshot_files.items()}
  return v
 def restore(self,v):
  for k in STATE_FIELDS:setattr(self.o,k,copy.deepcopy(v[k]))
  self.o.files={**copy.deepcopy(self.o.original_files),**copy.deepcopy(v['current_business_deltas'])}
  self.o.snapshot_files={k:{**copy.deepcopy(self.o.original_files),**copy.deepcopy(texts)} for k,texts in v['snapshot_business_deltas'].items()}
 def core(self,stage,variables):
  keys=('done','calls','patches','tests','location_sets','selected_test','selected_patch','selection','base','final','status','failure','sample','location_sample','patch_sample','test_votes','patch_votes','retained','passing','min_failures','eligible','combined','coarse')
  save(self.root/'core_state.json',{'stage':stage,'action_cursor':self.cursor,'core_state':{k:copy.deepcopy(variables[k]) for k in keys if k in variables},'owner_state':self.state(),'original_T0':self.o.t0,'source_seal':self.o.contract['method_source_seal']})
 def wrap(self,name,fn):
  def call(*args,**kw):
   if self.active:return fn(*args,**kw)
   key={'name':name,'args':args,'kwargs':kw};ident=digest(key);p=self.root/'actions'/('%06d.json'%self.cursor)
   row=read(p) if p.exists() else None
   if row:
    if row['input_SHA256']!=ident:raise RuntimeError('EXP251_ACTION_CURSOR_DRIFT')
    if row['status']=='COMPLETE':self.restore(row['owner_state_after']);self.cursor+=1;return copy.deepcopy(row['result'])
    if row['status']!='PREPARED_NOT_STARTED':raise RuntimeError('EXP251_UNKNOWN_ACTION_NO_REISSUE')
    self.restore(row['owner_state_before'])
   else:
    row={'cursor':self.cursor,'input':copy.deepcopy(key),'input_SHA256':ident,'status':'PREPARED_NOT_STARTED','owner_state_before':self.state(),'original_T0':self.o.t0};save(p,row)
   self.active=True
   try:v=fn(*args,**kw)
   except BoundaryReady:
    self.active=False;save(p,row);raise
   except BaseException as e:
    self.active=False;row.update(status='UNKNOWN_NO_REISSUE',error=type(e).__name__+': '+str(e));save(p,row);raise
   self.active=False;row.update(status='COMPLETE',result=copy.deepcopy(v),owner_state_after=self.state());save(p,row);self.cursor+=1;self.o.fixed_endpoint();return v
  return call

class Environment:
 def __init__(self,path,preview=False):
  self.contract_path=Path(path).resolve();self.contract,self.trial_out,self.config,public,self.common,self.supp,self.current_C0=checked_contract(path)
  self.out=(HERE/'source_previews'/self.contract['task_id']/self.contract['trial_id']) if preview else self.trial_out
  self.preview=preview;self.task_id=self.contract['task_id'];data=public.load_public_task(self.task_id,self.contract['public_contract']['path']);self.public_contract=data['contract'];self.pack=data['pack'];self.semantic=data['semantic']
  scope=read(self.contract['public_test_scope_contract']['path']);self.scope=next(v for v in scope['tasks'] if v['task_id']==self.task_id)
  if not self.scope.get('materialization_qualified'):raise RuntimeError('EXP251_MASK_NOT_QUALIFIED')
  origin=Path(self.scope['public_source_repo_view']);self.files={p:(origin/p).read_bytes().decode('utf-8') for p in self.public_contract['c0_business_paths_sha256']}
  if self.hashes()!=self.public_contract['c0_business_paths_sha256']:raise RuntimeError('EXP251_EXACT_C0_BUSINESS')
  self.original_files=copy.deepcopy(self.files);all_view={**self.scope['business_and_support_files_in_view'],**self.scope['public_test_py_files_SHA256']};self.supports={p:h for p,h in all_view.items() if p not in self.files}
  self.calls=0;self.out_tokens=0;self.native_calls=0;self.native_actual_OS_processes=0;self.rows=[];self.forward_records=[];self.patch_candidates=[]
  self.initial_snapshot={'id':'C0','label':'independent_new_trial_C0','inventory_sha256':digest({**self.hashes(),**self.supports}),'diff':{},'archive_path':str(self.out/'snapshots/C0')}
  self.snapshots={'C0':self.initial_snapshot};self.snapshot_files={'C0':copy.deepcopy(self.files)};self.current_snapshot=self.initial_snapshot
  self.public_regression_nodes=list(self.public_contract['ordinary_nodes']);self.recovery_goal_nodes=list(self.public_contract['public_target_nodes'])
  self.goal='Recover the observed public failure and preserve already passing ordinary behavior. Original issue background: '+self.semantic['original_issue']
  self.body_codec=module('_exp251_body',HERE/'public_body251.py');self.body_codec.decode=public.decode
  self.initial_public_feedback=self.body_codec.initial_index_v2(self.pack)
  dense=read(HERE/'PUBLIC_DENSE_BINDINGS251_SOURCE.json')['tasks'][self.task_id]
  if self.contract.get('Root_prepared_exact_dense_cache'):
   receipt_ref=self.contract['Root_prepared_exact_dense_cache'];receipt_path=Path(receipt_ref['path']).resolve()
   if not receipt_path.is_relative_to(HERE/'dense_prepared_ROOT') or sha(receipt_path)!=receipt_ref['sha256']:raise RuntimeError('EXP251_ROOT_NEW_DENSE_RECEIPT_SCOPE_OR_SHA')
   receipt=read(receipt_path)
   if receipt.get('Root_accepted_public_exact_dense') is not True or receipt.get('task_id')!=self.task_id or receipt.get('source_inventory_SHA256')!=dense['source_inventory_SHA256'] or receipt.get('query_SHA256')!=dense['query_SHA256'] or receipt.get('model_native_private_API_finance')!=0:raise RuntimeError('EXP251_ROOT_NEW_DENSE_TASK_SOURCE_QUERY_OR_PUBLIC_BOUNDARY')
   dense={**dense,'exact_cache_found':True,'cache_path':receipt['cache_path'],'cache_SHA256':receipt['cache_SHA256'],'historical_preparation_seconds':receipt['preparation_seconds'],'Root_new_forward_preparation_not_historical':True}
  self.dense_binding=dense;self.retrieval_query=dense['query'];self.retrieval_cache=dense.get('cache_path')
  if not self.preview and not dense['exact_cache_found']:raise RuntimeError('EXP251_MISSING_COMPLETE_DENSE_PREPARATION_BEFORE_ANY_MODEL_POST')
  self.t0=read(self.trial_out/'SCIENCE_T0_TRIAL_PREPARATION_STARTED.json') if not preview else {'source_preview_only':True,'actual_trial_T0_not_started':True}
  save(self.out/'snapshots/C0/business_source.json',self.files);save(self.out/'snapshots/C0/snapshot.json',self.initial_snapshot)
  self.core=self.install_core();self.journal=Journal(self)
 def hashes(self):return {p:hashlib.sha256(v.encode()).hexdigest() for p,v in self.files.items()}
 def install_core(self):
  sys.path.insert(0,str(HERE/'agentless_core'))
  common=types.ModuleType('common166');common.__dict__.update(Path=Path,ROOT=ROOT,E=HERE,OLD=HERE/'agentless_core',os=os,sys=sys,time=time,hashlib=hashlib,json=json,canonical=canonical,digest=digest,module=module,save=save,read=read,sha=sha,now=now)
  sys.modules['common166']=common
  module('retrieval178',HERE/'agentless_core/retrieval178.py')
  core=module('_exp251_complete_author_core',HERE/'agentless_core/agentless178.py')
  core.retrieve=lambda files,query,cache,allowed:self.dense_retrieval(files,query,cache,allowed)
  core.implementation_receipt()
  adapter=module('_exp251_same_normalization',HERE/'agentless_core/normalization_adapter_v3_241.py');adapter.install(sys.modules['agentless_bridge.official_core166'])
  return core
 def elapsed(self):return 0 if self.preview else time.time()-datetime.datetime.fromisoformat(self.t0['at_UTC']).timestamp()
 def time_left(self):return max(0,read(HERE/'protocol251_SOURCE.json')['operational_protection']['flow_wall_seconds']-self.elapsed())
 def fixed_endpoint(self):
  if self.preview:return
  p=self.out/'FIXED_RESOURCE_ENDPOINT_FIRST_CUT.json'
  if p.exists():return
  caps=self.contract['fixed_resource_endpoint'];reasons=[]
  if self.elapsed()>=caps['seconds']:reasons.append('WALL')
  if self.calls>=caps['model_calls']:reasons.append('CALLS')
  if self.out_tokens>=caps['output_tokens']:reasons.append('OUTPUT')
  if reasons:save(p,{'method':METHOD,'task_id':self.task_id,'trial_id':self.contract['trial_id'],'UTC':now(),'elapsed_seconds':self.elapsed(),'actual_calls':self.calls,'actual_output_tokens':self.out_tokens,'reasons':reasons,'same_trajectory_continues':True,'final_acceptance_not_inferred':True,'budget_delivery_failure_unless_qualified_complete_delivery_already_existed':True})
 def check_resource(self,cap=0,native=False):
  b=read(HERE/'protocol251_SOURCE.json')['operational_protection'];self.fixed_endpoint()
  controller_entries=len(list((self.out/'entry_invocations').glob('*.json'))) if not self.preview else 0
  if self.time_left()<=0 or self.calls>=b['model_calls_total'] or self.out_tokens+cap>b['output_tokens_total'] or (native and self.native_calls>=b['product_native_roots_total']) or controller_entries+self.native_actual_OS_processes>=b['all_owned_OS_roots_total']:
   raise BudgetError('DEPLOYMENT_RESOURCE_CENSOR_NOT_METHOD_FAILURE')
 def business_files(self):return copy.deepcopy(self.files)
 def record(self,stage,evidence):self.rows.append({'stage':stage,'evidence':copy.deepcopy(evidence)});return evidence
 def restore(self,snapshot):
  if snapshot!=self.snapshots[snapshot['id']]:raise RuntimeError('EXP251_SNAPSHOT_DRIFT')
  self.files=copy.deepcopy(self.snapshot_files[snapshot['id']]);self.current_snapshot=copy.deepcopy(snapshot)
 def snapshot(self,label):
  ident='s%04d'%len(self.snapshots);hashes=self.hashes();c0=self.public_contract['c0_business_paths_sha256'];changed={p:h for p,h in hashes.items() if h!=c0.get(p)}
  s={'id':ident,'label':label,'inventory_sha256':digest({**hashes,**self.supports}),'diff':changed,'archive_path':str(self.out/'snapshots'/ident)}
  self.snapshots[ident]=s;self.snapshot_files[ident]=copy.deepcopy(self.files);self.current_snapshot=s
  save(self.out/'snapshots'/ident/'snapshot.json',s);save(self.out/'snapshots'/ident/'business_source.json',self.files);return copy.deepcopy(s)
 def apply_patch(self,edits,label,from_snapshot=None):
  base=from_snapshot or self.initial_snapshot;self.restore(base);errors=[]
  try:
   if not isinstance(edits,list) or not edits:raise ValueError('EMPTY_PATCH')
   for e in edits:
    p=e['path'].removeprefix('repo/')
    if p not in self.files or not e['old'] or self.files[p].count(e['old'])!=1:raise ValueError('NONBUSINESS_PATH_OR_NONUNIQUE_SEARCH')
    self.files[p]=self.files[p].replace(e['old'],e['new'],1)
    ast.parse(self.files[p])
  except (ValueError,KeyError,SyntaxError,TypeError) as e:errors=[type(e).__name__+': '+str(e)];self.restore(base)
  s=self.snapshot(label);row={'candidate_id':len(self.patch_candidates),'snapshot':s,'legal':{'legal':not errors},'apply_errors':errors,'edits':copy.deepcopy(edits),'independent_original_root':from_snapshot is None};self.patch_candidates.append(row);return row
 def dense_retrieval(self,files,query,cache,allowed):
  self.check_resource()
  if not self.dense_binding['exact_cache_found'] or not cache:raise RuntimeError('EXP251_EXACT_DENSE_MISSING_NO_AUTO_ENCODER_DOWNLOAD_OR_SUBSTITUTION')
  if sha(cache)!=self.dense_binding['cache_SHA256']:raise RuntimeError('EXP251_DENSE_CACHE_DRIFT')
  c=read(cache);actual={p:hashlib.sha256(v.encode()).hexdigest() for p,v in sorted(files.items())}
  if {p:h for p,h in c['source_files_sha256'].items() if p.endswith('.py')}!=actual or c['query_sha256']!=hashlib.sha256(query.encode()).hexdigest() or c.get('query_complete') is not True or c.get('query_truncated') is not False:raise RuntimeError('EXP251_DENSE_EXACT_SOURCE_QUERY_MISMATCH')
  from agentless_bridge import dense166
  paths,evidence=dense166.retrieve(files,query,cache,allowed);evidence.update(new_encoder_forward=0,exact_historical_public_preprocessing_reused=True,historical_preparation_seconds=self.dense_binding['historical_preparation_seconds']);return paths,evidence
 def checkpoint(self,status,**extra):
  return {'schema':'EXP251-complete-stage-boundary/1','status':status,'method':METHOD,'task_id':self.task_id,'trial_id':self.contract['trial_id'],'trial_master_seed':self.contract['trial_master_seed'],'original_science_started':self.t0,'cursor':{'calls':self.calls,'output_tokens':self.out_tokens,'native':self.native_calls},'all_snapshots':copy.deepcopy(self.snapshots),'all_snapshot_business_sources':{k:ref(self.out/'snapshots'/k/'business_source.json') for k in self.snapshot_files},'current_business_SHA256':self.hashes(),'complete_settled_provenance':copy.deepcopy(self.forward_records),'source_seal':self.contract['method_source_seal'],'contract_SHA256':sha(self.contract_path),**extra}
 def llm(self,role,messages,temperature,seed,max_tokens,schema=None,tools=None):
  if not role.startswith('agentless_') or tools:raise RuntimeError('EXP251_AUTHOR_DIRECT_TEXT_ONLY')
  group='localize' if role in ('agentless_suspicious_files','agentless_irrelevant_folders','agentless_related_elements','agentless_fine_locations') else 'vote' if role=='agentless_regression_exclusion' else role
  cap={'localize':8192,'agentless_patch':16384,'agentless_reproduction':8192,'vote':4096}[group]
  self.check_resource(cap)
  body=self.body_codec.body_v2(role,copy.deepcopy(messages),temperature,seed,cap,self.task_id,'AGENTLESS_FSE2025_4L4P4T_FLASH',self.pack,schema,[],0)
  body['seed']=trial_seed(self.contract,role,seed);body=self.common.inject(body,self.config,self.task_id)
  ordinal=self.calls+1;slot=self.out/'calls'/('call%03d'%ordinal);response=slot/'new_generation/llm'/('%03d_response.json'%ordinal)
  if not response.exists():
   if (slot/'DISPATCH_STATE.json').exists():save(self.out/'STATUS.json',{'status':'MODEL_INFLIGHT_OR_UNKNOWN_NO_RESEND','slot':str(slot)});raise BoundaryReady()
   bounds=financial_bounds(body,self.config)
   ready={'schema':'EXP251-exact-single-model-ready/1','method':METHOD,'task_id':self.task_id,'trial_id':self.contract['trial_id'],'call_ordinal':ordinal,'role':role,'body_SHA256':digest(body),'canonical_bytes':len(canonical(body).encode()),'full_peak_reserve_CNY':bounds['global_reserve'],'full_original_financial_bounds':bounds,'finance_configuration':self.contract['finance_configuration'],'finance_phase':PHASE,'contract_path':str(self.contract_path),'contract_SHA256':sha(self.contract_path),'method_source_seal':self.contract['method_source_seal'],'trial_output_root':str(self.trial_out),'maximum_new_requests':1,'same_trial_exact_response_reuse_only':True,'source_preview_only':self.preview,'model_native_private_finance':0}
   save(slot/'FIRST_UNPOST_BODY.json',body);save(slot/'FIRST_UNPOST_READY.json',ready);save(slot/'checkpoint.json',self.checkpoint('EXACT_REQUEST_READY_NOT_POSTED',prepared_body=body,complete_current_messages=body['messages'],original_stage_seed=seed))
   save(self.out/'STATUS.json',{'status':'MODEL_READY_NOT_POSTED','task_id':self.task_id,'trial_id':self.contract['trial_id'],'call':ordinal,'ready_dir':str(slot),'body_SHA256':digest(body),'reserve_CNY':bounds['global_reserve'],'source_preview_only':self.preview});raise BoundaryReady()
  receipt=response.with_name('%03d_finance_receipt.json'%ordinal);request=response.with_name('%03d_request.json'%ordinal);r=read(receipt);req=read(request)
  if r.get('status')!='SETTLED' or req.get('body')!=body or req.get('body_SHA256')!=digest(body):raise RuntimeError('EXP251_COMPLETE_BODY_SETTLED_ONLY_REPLAY')
  v=read(response);usage=v['usage'];self.calls=ordinal;self.out_tokens+=usage['completion_tokens'];self.forward_records.append({'call':ordinal,'body_SHA256':digest(body),'response':ref(response),'receipt':ref(receipt),'request':ref(request),'same_trial_only':True})
  msg=v['choices'][0]['message']
  if msg.get('tool_calls'):raise RuntimeError('EXP251_AUTHOR_UNEXPECTED_TOOLS')
  return {'content':msg.get('content') or '', 'message':msg,'usage':usage,'call_ordinal':ordinal,'finish_reason':v['choices'][0].get('finish_reason')}
 def native(self,kind,snapshot,label,nodes=None,code=None):
  self.check_resource(native=True)
  self.restore(snapshot);ordinal=self.native_calls+1;out=self.out/'native_requests'/('native%03d'%ordinal);completed=out/'COMPLETED_PUBLIC.json'
  ready={'schema':'EXP251-exact-single-native-ready/1','method':METHOD,'task_id':self.task_id,'trial_id':self.contract['trial_id'],'attempt':ordinal,'native_kind':kind,'label':label,'candidate_snapshot':snapshot,'candidate_source_sha256':self.hashes(),'business_source_file':str(self.out/'snapshots'/snapshot['id']/'business_source.json'),'business_source_file_SHA256':sha(self.out/'snapshots'/snapshot['id']/'business_source.json'),'goal_nodes':self.recovery_goal_nodes,'ordinary_nodes':self.public_regression_nodes,'core_requested_ordinary_nodes':list(nodes or []),'public_test_scope_contract':self.contract['public_test_scope_contract'],'public_contract':self.contract['public_contract'],'method_contract_path':str(self.contract_path),'method_contract_SHA256':sha(self.contract_path),'native_output':str(out),'model_native_private_finance':0}
  if code is not None:ready.update(generated_code=code,generated_code_SHA256=hashlib.sha256(code.encode()).hexdigest())
  if not completed.exists():
   status='NATIVE_INFLIGHT_OR_UNKNOWN_NO_RERUN' if (out/'NATIVE_INTENT.json').exists() or (out/'SUPERVISOR_STARTED_ONCE.json').exists() else 'PUBLIC_NATIVE_READY'
   if status=='PUBLIC_NATIVE_READY':save(out/'NATIVE_READY.json',ready);save(out/'checkpoint.json',self.checkpoint(status,prepared_native=ready))
   save(self.out/'STATUS.json',{'status':status,'task_id':self.task_id,'trial_id':self.contract['trial_id'],'native_kind':kind,'native_ordinal':ordinal,'ready_path':str(out/'NATIVE_READY.json')});raise BoundaryReady()
  r=verify_parent_completed(completed)
  for k in ('task_id','trial_id','attempt','native_kind','candidate_source_sha256'):
   if r[k]!=ready[k]:raise RuntimeError('EXP251_NATIVE_EXACT_CURRENT_TRIAL_DRIFT '+k)
  if r['candidate_snapshot']['inventory_sha256']!=snapshot['inventory_sha256']:raise RuntimeError('EXP251_NATIVE_SNAPSHOT_DRIFT')
  p=r['public_native_path']
  if sha(p)!=r['public_native_SHA256']:raise RuntimeError('EXP251_NATIVE_RAW_WITNESS_DRIFT')
  parent=read(r['parent_supervision_path']);counts=parent['stop_receipt'].get('actual_job_accounting_observations',[])
  if not counts or not all(type(x.get('total_processes')) is int for x in counts):raise RuntimeError('EXP251_ACTUAL_PARENT_OS_PROCESS_COUNTS_REQUIRED')
  self.native_actual_OS_processes+=max(x['total_processes'] for x in counts);self.native_calls=ordinal;probe=read(p)
  if kind=='generated':
   if r.get('generated_code_SHA256')!=ready['generated_code_SHA256']:raise RuntimeError('EXP251_GENERATED_CODE_DRIFT')
   return probe
  outcomes=probe['pytest']['outcomes'];ordinary={n:{**outcomes[n],'outcome':outcomes[n]['status']} for n in nodes};fail=sum(v['status']!='passed' for v in ordinary.values())
  return {'passed':fail==0,'failure_count':fail,'outcomes':ordinary,'status':'GUARDED_ORDINARY_REGRESSION','native_record':{**probe,'executed':True,'guard_loaded':True},'public_goal_not_added_to_paper_ranking':True}
 def run_regression(self,snapshot=None,nodes=None,label='regression'):
  requested=list(self.public_regression_nodes if nodes is None else nodes)
  if not set(requested)<=set(self.public_regression_nodes):raise RuntimeError('EXP251_ONLY_ORIGINAL_PUBLIC_ORDINARY')
  return self.native('G_O',snapshot or self.initial_snapshot,label,nodes=requested)
 def run_reproduction(self,code,snapshot=None,label='reproduction'):
  ast.parse(code)
  if not code.strip():raise ValueError('EMPTY_REPRODUCTION')
  return self.native('generated',snapshot or self.initial_snapshot,label,code=code)
 def select(self,snapshot,reason):
  self.restore(snapshot);v={'snapshot':snapshot,'reason':copy.deepcopy(reason),'selected_before_private':True,'uses_hidden':False};save(self.out/'selection_before_private.json',v);return v

def prepare_clock(c,path,grant_path):
 g=read(grant_path)
 if g.get('root_authorized') is not True or g.get('preparation_authorized') is not True or any(g.get(k) is not False for k in ('model_authorized','native_authorized','private_authorized','finance_authorized')):raise RuntimeError('EXP251_PURE_PREPARATION_ROOT_GRANT')
 if g.get('contract_SHA256')!=sha(path) or g.get('method_source_seal_SHA256')!=c['method_source_seal']['sha256'] or any(g.get(k)!=c[k] for k in ('method','task_id','trial_id')):raise RuntimeError('EXP251_PREPARATION_BINDING')
 if time.time()>=datetime.datetime.fromisoformat(g['lease_end_UTC']).timestamp() or any(Path(p).exists() for p in g.get('root_stop_paths',[])):raise RuntimeError('EXP251_PREPARATION_STOP')
 p=Path(c['output_root'])/'SCIENCE_T0_TRIAL_PREPARATION_STARTED.json'
 if not p.exists():save(p,{'schema':'EXP251-real-trial-preparation-T0/1','at_UTC':now(),'method':METHOD,'task_id':c['task_id'],'trial_id':c['trial_id'],'contract_SHA256':sha(path),'Root_preparation_grant':ref(grant_path),'real_preparation_time_included':True,'first_POST_recorded_separately':True,'preprocessing_reuse_cost_separate':True})
 return p

def main():
 p=argparse.ArgumentParser();p.add_argument('--contract',required=True);p.add_argument('--source-preview',action='store_true');p.add_argument('--root-preparation-grant');args=p.parse_args();c=read(args.contract)
 if not args.source_preview:
  if not args.root_preparation_grant:raise RuntimeError('EXP251_ACTUAL_PREPARATION_GRANT_REQUIRED')
  prepare_clock(c,args.contract,args.root_preparation_grant)
  import uuid
  save(Path(c['output_root'])/'entry_invocations'/(uuid.uuid4().hex+'.json'),{'UTC':now(),'pid':os.getpid(),'controller_root_counted':1,'method':METHOD,'task_id':c['task_id'],'trial_id':c['trial_id'],'original_T0_not_reset':True})
 started=time.monotonic();env=Environment(args.contract,args.source_preview)
 try:
  result=env.core.run(env)
  roles=[r.get('role') for r in result['stage_ledger'] if r.get('stage')=='llm']
  result['actual_generation_accounting']={'declared_patch_slots':40,'actual_patch_model_responses':roles.count('patch'),'declared_reproduction_samples':40,'actual_reproduction_model_responses':roles.count('reproduction'),'actual_fine_location_responses':roles.count('fine_locations'),'original_adapter_len_patches_is_slot_count':True,'invalid_location_slots_not_filled_with_synthetic_or_extra_sampling':True}
  save(env.out/'PUBLIC_ONLY_NATURAL_TERMINAL.json',result);save(env.out/'SELECTED_BUSINESS_SOURCE.json',env.files)
  save(env.out/'STATUS.json',{'status':'DEPLOYMENT_RESOURCE_CENSORED' if result['status']=='BUDGET_CENSORED' else 'ENGINEERING_UNKNOWN' if result.get('engineering_outcome_unknown') else 'PUBLIC_ONLY_NATURAL_TERMINAL','task_id':env.task_id,'trial_id':env.contract['trial_id'],'runtime_core':result['runtime_core'],'error':result.get('error'),'requires_Root_once_independent_final':True})
 except BoundaryReady:pass
 finally:
  save(env.out/'PUBLIC_REPLAY_RECORDS.json',env.rows);save(env.out/'EXACT_SETTLED_REPLAY.json',env.forward_records);save(env.out/'FORWARD_PREPARATION_COST.json',{'elapsed_seconds_this_entry':time.monotonic()-started,'source_preview_only':args.source_preview,'original_T0_preserved':True,'encoder_new_forward':0,'model_native_private_finance':0})
 print(canonical(read(env.out/'STATUS.json')),flush=True)
if __name__=='__main__':main()

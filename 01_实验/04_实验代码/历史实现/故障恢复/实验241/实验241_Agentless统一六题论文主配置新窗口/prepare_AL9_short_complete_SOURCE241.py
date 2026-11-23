from pathlib import Path
import ast,json,hashlib,copy,datetime
E=Path(__file__).resolve().parent;O=E/'runtime_v8_SOURCE';W=E.parent.parent;D=W/'a9';R=Path('D:/Code/毕设/graduate-thesis-experiments');U=R/'工作区/1010-unified-six'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
def source(n,t):ast.parse(t);(D/n).write_text(t,'utf-8')
def rep(t,a,b):
 if t.count(a)!=1 and not (a.startswith('  if inside(path,self.out)') and t.count(a)==2):raise RuntimeError('SOURCE_ANCHOR '+a[:80]+' count '+str(t.count(a)))
 return t.replace(a,b,1)
if D.exists():
 assert not (D/'SOURCE_SEAL.json').exists() and not (D/'SOURCE_PREPARED_WAIT_SHARED_ROOT_SHA_FALSE.json').exists()
D.mkdir(exist_ok=True)
for f in O.glob('*.py'):source(f.name,f.read_text('utf-8-sig'))
save(D/'PAPER_CORE_SOURCE_PROVENANCE241.json',read(O/'PAPER_CORE_SOURCE_PROVENANCE241.json'))
B={'flow_wall_seconds_including_final':7200,'per_native_timeout_seconds':180,'initial_repository_pool_timeout_seconds':1800,'initial_pool_parent_seconds':2100,'final_reserve_seconds':180,'model_calls_total':1024,'output_tokens_total':8388608,'product_native_roots_total':2048,'all_owned_OS_roots_total':4096,'final_once_independent_validation':1,'max_model_call_output_tokens':16384}
t=(D/'contracts241.py').read_text('utf-8');start=t.index('COMMON_BUDGET=');end=t.index('\ndef verify_grant',start);t=t[:start]+'COMMON_BUDGET='+repr(B)+'\n'+t[end:]
t=rep(t,"stage_wall=300 if grant.get('stage')=='MECHANICAL_ZERO_POST' else 3600","stage_wall=protocol['budget']['initial_pool_parent_seconds'] if grant.get('stage')=='MECHANICAL_ZERO_POST' and grant.get('root_fullpool_mechanical_only') is True else 300 if grant.get('stage')=='MECHANICAL_ZERO_POST' else protocol['budget']['flow_wall_seconds_including_final']")
# Root picks a fresh closure filename when final shared protocol is frozen.
t=rep(t,"if Path(protocol['closure_flag']).resolve()!=ROOT/'工作区/1010-unified-six/STOP_NEW_SIX.json':","if Path(protocol['closure_flag']).resolve().parent!=ROOT/'工作区/1010-unified-six' or Path(protocol['closure_flag']).name not in ('STOP_NEW_SIX_FORWARD_V10.json',):")
t=t.replace('ROOT_COMMON3600_CAPACITY_AND_NO_GLOBAL_DEADLINE_REQUIRED','ROOT_COMMON7200_CAPACITY_AND_NO_GLOBAL_DEADLINE_REQUIRED')
source('contracts241.py',t)
t=(D/'owner241.py').read_text('utf-8');t=t.replace('self.started+3600',"self.started+self.protocol['budget']['flow_wall_seconds_including_final']").replace("+3600-time.time()", "+self.protocol['budget']['flow_wall_seconds_including_final']-time.time()").replace('original_birth+3600-time.time()', "original_birth+self.protocol['budget']['flow_wall_seconds_including_final']-time.time()")
t=rep(t,'    def native_execute(self,argv,cwd,log,timeout=90,env=None):',"""    def native_timeout_cap(self):
        if getattr(self,'_initial_pool_native_inflight',False):
            if self.grant.get('initial_repository_pool_native_authorized') is not True:
                raise EngineeringUnknown('ROOT_INITIAL_FULLPOOL_PHASE_GRANT_REQUIRED')
            return self.protocol['budget']['initial_repository_pool_timeout_seconds']
        return self.protocol['budget']['per_native_timeout_seconds']

    def native_execute(self,argv,cwd,log,timeout=180,env=None):""")
t=t.replace('self.runner.execute(entry,cwd,log,min(90,timeout),env)','self.runner.execute(entry,cwd,log,min(self.native_timeout_cap(),timeout),env)')
t=t.replace('min(self.flow_deadline,time.monotonic()+90)',"min(self.flow_deadline,time.monotonic()+self.protocol['budget']['per_native_timeout_seconds'])")
t=t.replace("result=self.native_execute(args,frozen,out/'pytest.log',90,env)","result=self.native_execute(args,frozen,out/'pytest.log',self.protocol['budget']['per_native_timeout_seconds'],env)")
# Canonical pytest import mode for legacy exact public/final node execution.
t=t.replace("'--import-mode=importlib'","'--import-mode=prepend'")
source('owner241.py',t)
t=(D/'winjob241.py').read_text('utf-8')
t=rep(t,"actual=dict(env or {});actual['PATCHPILOT_JOB']=name","actual=dict(env or {});actual['PATCHPILOT_JOB']=name;actual['COMMON_NATIVE_OWNED_JOB']=name")
t=rep(t,"until=time.monotonic()+min(float(timeout),3600 if controller else 90,self.owner.time_left())","declared=self.owner.p['budget']['flow_wall_seconds_including_final'] if controller else self.owner.native_timeout_cap()\n            until=time.monotonic()+min(float(timeout),declared,self.owner.time_left())")
source('winjob241.py',t)
t=(D/'environment241.py').read_text('utf-8');t=rep(t,"reserve=0 if getattr(self,'_external_evaluator',False) else 90","reserve=0 if getattr(self,'_external_evaluator',False) else self.protocol['budget']['final_reserve_seconds']")
a="""  return [n for n in collected if any(n==s or ('::' not in s and n.startswith(s+'::')) for s in selectors) and str(outcomes[n].get('outcome',outcomes[n].get('status'))).lower() in ('passed','pass')]"""
b="""  default_pool=selectors==['__DEFAULT_FULL_PUBLIC_REPOSITORY_DISCOVERY__']
  return [n for n in collected if (default_pool or any(n==s or ('::' not in s and n.startswith(s+'::')) for s in selectors)) and str(outcomes[n].get('outcome',outcomes[n].get('status'))).lower() in ('passed','pass')]"""
t=rep(t,a,b)
t=t.replace("native=self.native_execute([self.logical_python,str(script)],out,out/'execution.log',90,env)","native=self.native_execute([self.logical_python,str(script)],out,out/'execution.log',self.protocol['budget']['per_native_timeout_seconds'],env)")
t=rep(t,"  if any(marker in native['stdout']+native['stderr'] for marker in ('PATCHPILOT_GENERATED_','SCOPE_V2_')):raise EngineeringUnknown('REPRODUCTION_GUARD_SCOPE_REFUSAL')","""  scope_rows=[json.loads(line) for line in (out/'generated_scope_events.jsonl').read_text('utf-8').splitlines()] if (out/'generated_scope_events.jsonl').exists() else []
  denials=[x for x in scope_rows if x.get('allowed') is False]
  fatal_refusal=any(marker in native['stdout']+native['stderr'] for marker in ('PATCHPILOT_GENERATED_','SCOPE_V2_','SCOPE_V8_'))
  model_origin=any(x.get('current_generated_script_origin') is True and ('SCOPE_V2_'+str(x.get('reason',''))) in native['stderr'] for x in denials)
  # Every actual refusal is retained. Only complete stopped execution with an
  # attested model-script call chain can be an invalid generated test.
  if fatal_refusal and not (denials and model_origin):raise EngineeringUnknown('UNATTRIBUTED_REPRODUCTION_GUARD_SCOPE_REFUSAL')""")
t=rep(t,"  marker=markers[0] if len(markers)==1 and native['exit_code']==0 and imports else None","""  completed=all(native.get('stop_receipt',{}).get(k) is True for k in ('root_stopped','own_Job_empty_before_close','descendants_stopped'))
  if not completed:raise EngineeringUnknown('REPRODUCTION_ACTUAL_STOP_INCOMPLETE')
  marker=markers[0] if len(markers)==1 and native['exit_code']==0 and imports and not fatal_refusal and not any(x.get('current_generated_script_origin') is True for x in denials) else None
  native.update(all_raw_guard_denials=denials,model_script_guard_refusal_invalid=fatal_refusal,author_generated_test_error_filtered_not_method_zero=True)""")
source('environment241.py',t)
# Whole initial pool uses only a trusted sealed framework phase, never a model label.
binding='''"""Fresh complete default public repository pool and original candidate regression."""
from contextlib import contextmanager
class PaperBindingUnknown(RuntimeError):pass
class PaperMainEnvironmentMixin:
 def require_paper_main_current_binding(self):
  if not self.protocol.get('shared_public_scope_root_qualified') or not self.protocol.get('common_budget_root_freeze'):
   raise PaperBindingUnknown('ROOT_SHARED_PUBLIC_ENVIRONMENT_FREEZE_REQUIRED')
  self.paper_public_repository_regression_nodes=['__DEFAULT_FULL_PUBLIC_REPOSITORY_DISCOVERY__']
 def run_paper_repository_regression(self,snapshot=None,nodes=None,label='paper_regression'):
  self.restore(snapshot or self.initial_snapshot)
  from shared_facade241 import execute
  full=nodes==['__DEFAULT_FULL_PUBLIC_REPOSITORY_DISCOVERY__']
  if full:
   if getattr(self,'_initial_pool_consumed',False):raise PaperBindingUnknown('INITIAL_FULLPOOL_ONCE_PER_FRESH_METHOD_FLOW')
   if self.grant.get('initial_repository_pool_native_authorized') is not True:raise PaperBindingUnknown('ROOT_INITIAL_POOL_CAPABILITY_REQUIRED')
   self._initial_pool_native_inflight=True
   try:result=execute(self,None,label='sealed_initial_full_repository_pool')
   finally:self._initial_pool_native_inflight=False;self._initial_pool_consumed=True
  else:result=execute(self,nodes,label=label)
  if result.get('known') is not True:raise PaperBindingUnknown('FULL_REPOSITORY_NATIVE_UNKNOWN_NO_PARTIAL_PROMOTION')
  outcomes=result['pytest']['outcomes'];fail=sum(v['status']!='passed' for v in outcomes.values())
  return self.record(label,{'passed':fail==0,'failure_count':fail,'outcomes':{n:{**v,'outcome':v['status']} for n,v in outcomes.items()},
   'status':'KNOWN_SHARED_MASKED_REAL_REGRESSION','native_record':{**result['execution'],'executed':True},'collected':result['pytest']['collected'],'uses_hidden':False})
 def paper_model_call_cap(self,role,requested):
  caps={'agentless_suspicious_files':300,'agentless_irrelevant_folders':2048,'agentless_related_elements':300,'agentless_fine_locations':300,'agentless_patch':1024,'agentless_reproduction':1024,'agentless_regression_exclusion':1024}
  if role not in caps or requested>caps[role]:raise PaperBindingUnknown('PAPER_SOURCE_OUTPUT_CAP_CHANGED')
  return int(requested)
'''
source('paper_environment_binding241.py',binding)
t=(D/'shared_facade241.py').read_text('utf-8')
t=rep(t,"p={**owner.protocol,'budget':{**owner.protocol['budget'],'native_roots_total':2048,'native_timeout_seconds':90}}","p={**owner.protocol,'budget':{**owner.protocol['budget'],'native_roots_total':owner.protocol['budget']['product_native_roots_total'],'native_timeout_seconds':owner.native_timeout_cap(),'initial_full_pool_timeout_seconds':owner.protocol['budget']['initial_repository_pool_timeout_seconds']}}")
source('shared_facade241.py',t)
t=(D/'supervisor_runtime_v3_241.py').read_text('utf-8')
t=t.replace("+(300 if self.g['stage']=='MECHANICAL_ZERO_POST' else 3600)","+((self.p['budget']['initial_pool_parent_seconds'] if self.g.get('root_fullpool_mechanical_only') else 300) if self.g['stage']=='MECHANICAL_ZERO_POST' else self.p['budget']['flow_wall_seconds_including_final'])")
t=t.replace("300 if x.mode=='mechanical' else 3510","(own.p['budget']['initial_pool_parent_seconds'] if own.g.get('root_fullpool_mechanical_only') else 300) if x.mode=='mechanical' else own.p['budget']['flow_wall_seconds_including_final']-own.p['budget']['final_reserve_seconds']")
source('supervisor_runtime_v3_241.py',t)
# Exact-node legacy/final framework uses the standard pytest package registration.
t=(D/'product_entry241.py').read_text('utf-8');t=t.replace("mode=envelope['mode'];args=envelope['argv_tail']","mode=envelope['mode'];args=envelope['argv_tail']\n    args=[('--import-mode=prepend' if x=='--import-mode=importlib' else x) for x in args]")
source('product_entry241.py',t)
# Add actual model-script origin to denied-operation events; no permission is expanded.
t=(D/'generated_scope_v2_241.py').read_text('utf-8')
t=rep(t,"  self.log=self.out/'generated_scope_events.jsonl'","  self.log=self.out/'generated_scope_events.jsonl'\n  self.output_ancestor_directories=set(self.out.parents)")
t=rep(t,' def read_decision(self,path):',' def read_decision(self,path,directory=False):')
t=rep(t,"  if inside(path,self.out):return True,'CURRENT_NATIVE_OUTPUT'","  if inside(path,self.out):return True,'CURRENT_NATIVE_OUTPUT'\n  if directory and path in self.output_ancestor_directories:return True,'OWN_OUTPUT_ANCESTOR_DIRECTORY_ENUMERATION_ONLY'")
t=rep(t,"allowed,reason=policy.read_decision(path)\n   record({'event':event","allowed,reason=policy.read_decision(path,directory=True)\n   record({'event':event")
t=rep(t," def record(event):\n  guard.logging=True",""" def record(event):
  if event.get('allowed') is False:
   frame=sys._getframe(1);model_origin=False
   while frame is not None:
    if frame.f_code.co_filename==str(policy.out/'generated_test.py'):model_origin=True;break
    frame=frame.f_back
   event.update(current_generated_script_origin=model_origin,fatal_raising_guard_refusal=True)
  guard.logging=True""")
source('generated_scope_v2_241.py',t)
assert sha(D/'agentless_paper_main241.py')==sha(O/'agentless_paper_main241.py')
future_shared=U/'shared_native_v10';commands={}
for i,task in enumerate(read(O/'science_release_candidate_FALSE/getmoto__moto-5406/protocol.SOURCE_ONLY.json')['task_order']):
 p=read(O/'science_release_candidate_FALSE'/task/'protocol.SOURCE_ONLY.json')
 p.update(budget=copy.deepcopy(B),common_budget_root_freeze=copy.deepcopy(B),core_source=str(D/'agentless_paper_main241.py'),masked_native_owner_root=str(D),masked_native_guard_directory=str(future_shared/'guard'),closure_flag=str(U/'STOP_NEW_SIX_FORWARD_V10.json'),output_root=str(D/'r'/str(i)/'f'),supervision_output_root=str(D/'r'/str(i)/'s'),natural_index_original=10+i,execution_authorized=False,source_only=True,native_authorized=False,model_generation_authorized=False,once_private_authorized=False,private_authorized=False,deployment_revision='AL9_ROOT_SHARED10_7200_FORWARD_ALL_SIX',old_T1_T2_unknown_and_all_old_clocks_preserved=True,shared_v10_exact_SHA_pending=True,shared_public_helper={'path':str(future_shared/'native_masked_public.py'),'sha256':None},private_final_Root_only_after_author_STOP=True,scientific_generation_and_private_prohibited=True,full_pool_zero_API_qualification_required_before_paid=True)
 out=D/'c'/str(i);save(out/'p.false.json',p)
 g=read(O/'science_release_candidate_FALSE'/task/'ROOT_SCIENCE_GRANT.false.template.json');g.update(root_authorized=False,native_authorized=False,model_generation_authorized=False,finance_authorized=False,private_acceptance_authorized=False,once_private_evaluation_authorized=False,new_start_UTC=None,parent_controller_job_qualified=False,protocol_sha256=digest(p),protocol_raw_sha256=sha(out/'p.false.json'),source_seal_sha256=None,neutral_mechanical_qualification_sha256=None,initial_repository_pool_native_authorized=False,max_wall_seconds=7200,new_all_six_complete_method_forward_root_release_pending=True)
 save(out/'g.false.json',g);commands[task]=[g['controller_physical_python_expected'],'-X','utf8','-B',str(D/'supervisor_runtime_v3_241.py'),'science','--protocol',str(out/'p.actual.json'),'--grant',str(out/'g.actual.json'),'--seal',str(D/'SOURCE_SEAL.json'),'--contract',p['public_contract']]
save(D/'ALL_SIX_FULL_METHOD_COMMANDS_FALSE.json',commands)
save(D/'SOURCE_PREPARED_WAIT_SHARED_ROOT_SHA_FALSE.json',{'schema':'AL9-generalized-forward-source-preparation/1','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'directory':str(D),'budget':B,'sources_AST_valid':True,'method_core4L40P40repro_normalization_vote_unchanged_SHA256':sha(D/'agentless_paper_main241.py'),'all_six_science_false':True,'actual_model_native_private_newGold_download':0,'all_old_worktree_source_result_partial_clock_untouched':True,'new_shared_root_SHA_pending':True,'new_seal_not_claimed_complete_until_Root_shared_exact_SHA':True,'run_route':['Root final shared10+budget+closure+finance binding/source seal','Root zeroAPI mechanical on fresh short-root C0 full default pool, no partial promotion','new forward common six 4L40patch40repro+completePASSLLMexclusion+candidatevalidation+vote','immutable selection and actual author STOP -> Root independentfinal once under same7200clock'], 'no_labels_grant_extra_native_time':True})
print(json.dumps({'prepared':str(D),'coreSHA':sha(D/'agentless_paper_main241.py'),'all_six_commands':str(D/'ALL_SIX_FULL_METHOD_COMMANDS_FALSE.json'),'seal_pending_sharedRoot':True,'API_native_private':0},ensure_ascii=False))
"""Prepared fresh21 queue / engineering-only replay; no execution without root."""
from common166 import *
import copy,traceback
from decimal import Decimal
import common_environment224 as shared
from common_environment224 import CommonEnvironment
from shared_projection224 import project
from native_executor224 import install as install_native
from native_guard_compat224 import install as install_guard_compat
from resume_prefix224 import ExactPublicPrefix,install as install_prefix
from budget_semantics224 import budget_disposition,should_stop_queue
METHODS={'AGENTLESS_FSE2025':'AGENTLESS_FSE2025_4L4P4T_FLASH','OURS_G153_PROGRESSIVE_SEMANTIC':'G_PROGRESSIVE_SEMANTIC_FLASH'}
def neutral_common(value,env):
 roots=[(env.repo_root,'/workspace/repo'),(env._paths['frozen'],'/public-tests'),(env.active,'/workspace'),(env.out,'/public-feedback')]
 return project(value,roots)
shared.neutral=neutral_common
class FinanceFatalController(RuntimeError):pass
class FreshEnvironment(CommonEnvironment):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);install_native(self);install_guard_compat(self);self.finance_fatal=None
  self._independent_C0_hashes={p:hashlib.sha256(t.encode()).hexdigest() for p,t in self.business_files().items()} if self.method==METHODS['AGENTLESS_FSE2025'] else None
  self.frozen_flow_wall_seconds=int(read(TIME_AUTHORITY)['budget']['max_flow_wall_seconds'])
  self.wall_limited_by_global=self.deadline<self.started+self.frozen_flow_wall_seconds
 def budget_context(self):
  return {'finance_fatal':self.finance_fatal,'global_cutoff':time.time()>=NO_TEST or remaining()<=0 or (E/'STOP_REQUESTED.json').exists(),'wall_limited_by_global':self.wall_limited_by_global,'search_wall_exhausted':self.time_left()<=0,'full_wall_exhausted':time.monotonic()>=self.started+self.frozen_flow_wall_seconds,'max_model_calls_per_flow':64,'max_output_tokens_per_flow':65536,'max_flow_wall_seconds':self.frozen_flow_wall_seconds}
 def closed_result(self,result,disposition):
  # A known declared-budget failure is terminal for this flow, with no private run.
  return {'task_id':self.task_id,'method':self.method,**result,**disposition,'budget_disposition':disposition,'budget_context':self.budget_context(),'engineering_outcome_unknown':disposition['success'] is None,'declared_method_failure_known':disposition['success'] is False,'finance_fatal':self.finance_fatal,'LLM_calls':self.calls,'output_tokens':self.out_tokens,'public_native_calls':self.native_calls,'hidden_acceptance_calls':0,'no_private_after_terminal_disposition':True,'no_further_candidate_in_this_flow':True,'elapsed_seconds':time.monotonic()-self.started}
 def llm(self,*args,**kwargs):
  if self.finance_fatal:raise FinanceFatalController('ORIGINAL_FINANCIAL_FATAL_NO_FURTHER_POST')
  role=args[0] if args else kwargs.get('role')
  if self._independent_C0_hashes is not None and role in ('agentless_patch','agentless_reproduction'):
   before={p:hashlib.sha256(t.encode()).hexdigest() for p,t in self.business_files().items()}
   self.restore(self.initial_snapshot)
   after={p:hashlib.sha256(t.encode()).hexdigest() for p,t in self.business_files().items()}
   assert after==self._independent_C0_hashes,'INDEPENDENT_AGENTLESS_C0_RESTORE_DRIFT'
   self.record('agentless_independent_generation_C0_restored224',{'role':role,'expected_C0_inventory_sha256':self.initial_snapshot['inventory_sha256'],'before_business_digest':digest(before),'after_business_digest':digest(after),'changed_paths_restored':[p for p in sorted(set(before)|set(after)) if before.get(p)!=after.get(p)],'before_generation_and_all_shared_reader_returns':True,'original_prompts_seed_temperature_and4L4P4T_unchanged':True})
  try:return super().llm(*args,**kwargs)
  except Exception as error:
   disposition=budget_disposition({'error':{'type':type(error).__name__,'message':str(error)}},self.budget_context())
   if type(error).__name__.startswith('Finance') and not (disposition and disposition['success'] is False):
    self.finance_fatal={'type':type(error).__name__,'message':str(error),'at_utc':now(),'no_new_actor_private_or_task_after_fatal':True}
    self.record('finance_fatal224',self.finance_fatal)
   raise
 def finalize(self,result):
  disposition=budget_disposition(result,self.budget_context())
  if disposition:return self.closed_result(result,disposition)
  # No private observation after an unfinished engineering/financial controller.
  if self.finance_fatal or result.get('engineering_outcome_unknown') or result.get('status') in ('ENGINEERING_UNKNOWN','CONTEXT_UNKNOWN','CONTEXT_EVIDENCE_UNKNOWN','NOT_RUN','BUDGET_CENSORED') or ((result.get('error') or {}).get('type','').startswith('Finance')):
   return {'task_id':self.task_id,'method':self.method,**result,'status':'BUDGET_CENSORED' if self.finance_fatal else result.get('status','ENGINEERING_UNKNOWN'),'success':None,'finance_fatal':self.finance_fatal,'LLM_calls':self.calls,'output_tokens':self.out_tokens,'public_native_calls':self.native_calls,'hidden_acceptance_calls':0,'selected_before_private_no_private_on_unknown':True,'elapsed_seconds':time.monotonic()-self.started}
  try:return super().finalize(result)
  except Exception as error:
   failed={**result,'error':{'type':type(error).__name__,'message':str(error)}}
   disposition=budget_disposition(failed,self.budget_context())
   if disposition:return self.closed_result(failed,disposition)
   raise
def seal():
 inputs={str(E/'data/selected_task_bindings.json'):sha(E/'data/selected_task_bindings.json'),str(E/'data/public_inputs.jsonl'):sha(E/'data/public_inputs.jsonl'),str(E/'data/common_spec224.json'):sha(E/'data/common_spec224.json'),str(E/'ranking/plan_registry224.json'):sha(E/'ranking/plan_registry224.json'),str(TIME_AUTHORITY):sha(TIME_AUTHORITY)}
 registry=read(E/'ranking/plan_registry224.json');assert registry['plans_count']==23
 for r in registry['plans'].values():inputs[r['path']]=r['sha256']
 sources={str(p):sha(p) for p in E.glob('*.py')};sources.update(__import__('bootstrap224').SOURCES)
 sources[str(TRANSPORT)]=sha(TRANSPORT)
 sources[str(E/'repro_guard224/sitecustomize.py')]=sha(E/'repro_guard224/sitecustomize.py')
 result={'at_utc':now(),'sources':sources,'inputs':inputs,'prepared_only_no_new_POST_native_private':True,'original23_mask_preserved':True,'fresh_order':read(E/'protocol224.json')['task_order'][2:],'original_first2_retained_as_pilot_not_strict_main':'No retrospective reroll or wall reset. New first2 primary results would need separately declared fresh runs.','same_C0_goals_ordinary_private_and_frozen_seeds':True,'projection':str(E/'shared_projection224.py'),'native_birth_wrapper':str(E/'native_executor224.py'),'wall_policy':'Each fresh worker starts900s; old expired pilot never relabeled within900. Engineering prefix replay explicitly not primary.','budget_classification':'Known frozen call/output/flow-wall exhaustion: DECLARED_FLOW_BUDGET_EXHAUSTED, success=false, no private or next candidate in this flow, next fixed flow permitted. Global/finance/provider/engineering censoring: success=null and queue stop. Original90s acceptance reserve preserved.','budget_classification_pure_evidence':str(E/'audit224/budget_classification224.json'),'abort':'NewRoot_release required; NO_NEW2026-10-09T01:57Z; hard2026-10-09T02:00Z; financial rejection/fatal unknown no private/new actor; no auto-Main, no API retry.'}
 save(E/'fresh_ready_seal224.json',result);return result
def run(mode):
 runtime=read(ROOT/'工作区/1008-2320-baseline-main/coordination/runtime_release.json')
 assert runtime.get('root_runtime_ready') is True,'ROOT_RUNTIME_NOT_READY_NO_POST_NATIVE'
 is_main=mode in ('main','main-ours','main-agentless')
 phase='Round2320Main' if is_main else 'Round2320Pilot';namespace='fresh_main/recovery' if is_main else 'engineering_core_check/recovery'
 assert runtime.get('root_protocol_sha256')==read(TIME_AUTHORITY)['source_root_protocol_sha256']==sha(read(TIME_AUTHORITY)['source_root_protocol']),'ROOT_COMMON_PROTOCOL_SHA_MISMATCH_NO_POST_NATIVE'
 release_names={'core':'engineering_core_release224.json','core5093':'engineering_second_core_release224.json','main':'fresh_main_release224.json','main-ours':'fresh_ours_main_release224.json','main-agentless':'fresh_agentless_main_release224.json'}
 release=E/release_names[mode]
 assert release.exists() and read(release).get('root_authorized'),'ROOT_METHOD_GRANT_MISSING_NO_POST_NATIVE'
 grant=read(release)
 assert grant.get('phase')==phase and grant.get('source_seal_sha256')==sha(E/'fresh_ready_seal224.json'),'ROOT_METHOD_GRANT_PHASE_OR_SEAL_DRIFT'
 frozen=read(E/'fresh_ready_seal224.json')
 for p,h in {**frozen['sources'],**frozen['inputs']}.items():assert sha(p)==h,'READY_SOURCE_INPUT_DRIFT '+p
 refs={r['task_id']:r for r in read(E/'data/selected_task_bindings.json')['tasks']};plans=read(E/'ranking/plan_registry224.json')['plans'];order=frozen['fresh_order'] if is_main else read(E/'protocol224.json')['pilot_ids'][1:2] if mode=='core5093' else read(E/'protocol224.json')['pilot_ids'][:1];labels=['OURS_G153_PROGRESSIVE_SEMANTIC'] if mode=='main-ours' else ['AGENTLESS_FSE2025'] if mode in ('core','core5093','main-agentless') else list(METHODS)
 for tid in order:
  runtime=read(ROOT/'工作区/1008-2320-baseline-main/coordination/runtime_release.json')
  if runtime.get('root_runtime_ready') is not True or not read(release).get('root_authorized'):return
  through=read(release).get('allowed_through_index',2) if is_main else 22
  while is_main and read(TIME_AUTHORITY)['task_order'].index(tid)>through:
   save(E/('execution_checkpoint224_'+mode+'.json'),{'at_utc':now(),'phase':'WAIT_ROOT_PAIRING_WINDOW','task_id':tid,'allowed_through_index':through,'mode':mode})
   if time.time()>=NO_TEST:return
   time.sleep(1)
   runtime=read(ROOT/'工作区/1008-2320-baseline-main/coordination/runtime_release.json')
   if runtime.get('root_runtime_ready') is not True or not read(release).get('root_authorized'):return
   through=read(release).get('allowed_through_index',2)
  for label in labels:
   if time.time()>=NO_TEST:break
   ref=copy.deepcopy(refs[tid]);ref.update(G_frozen_plan=plans[tid]['path'],_output_namespace=namespace,_native_namespace=namespace.replace('recovery','native_active'))
   out=E/namespace/tid/METHODS[label]
   assert not (out/'result.json').exists(),'EXISTING_FRESH_OBSERVATION_NO_RERUN'
   bank=None;uninstall=None;env=None
   if not is_main:bank=ExactPublicPrefix(E/'recovery'/tid/METHODS[label]);uninstall=install_prefix(bank)
   try:
    env=FreshEnvironment(ref,METHODS[label]);env.finance_phase=phase;core=sys.modules['agentless178'] if label=='AGENTLESS_FSE2025' else sys.modules['ranked_repair178'];result=core.run(env);full=env.finalize(result)
   except Exception as error:full={'task_id':tid,'method':METHODS[label],'status':'ENGINEERING_UNKNOWN','success':None,'error':{'type':type(error).__name__,'message':str(error)},'traceback':traceback.format_exc(),'runtime_core':{},'LLM_calls':getattr(env,'calls',0),'public_native_calls':getattr(env,'native_calls',0),'hidden_acceptance_calls':0}
   finally:
    if uninstall:uninstall()
   receipts=[read(p) for p in out.glob('llm/*_finance_receipt.json')];settled=[r for r in receipts if r['status']=='SETTLED' and not r.get('already_settled_prefix_reuse')]
   new_fee=sum((Decimal(r['usage_peak_cost_CNY']) for r in settled),Decimal(0));inherited_fee=sum((Decimal(r['original_cost_already_in_continuous_ledger_CNY']) for r in bank.reused),Decimal(0)) if bank else Decimal(0)
   fatal=getattr(env,'finance_fatal',None) or full.get('finance_fatal')
   if fatal:full.update(finance_fatal=fatal,status='BUDGET_CENSORED',success=None)
   full.update(scientific_method=label,stratum=ref['stratum'],version=mode,primary_eligible=is_main,fresh_wall_clock_start_not_old_pilot=True,new_paid_API=len(settled),new_fees_CNY=str(new_fee),inherited_paid_prefix_fees_CNY=str(inherited_fee),fees_CNY=str(new_fee+inherited_fee),cost_counting='Only new SETTLED transport receipts are new fees; exact replay costs remain charged once in original continuous ledger.',reused_original_prefix_calls=len(bank.reused) if bank else 0,old_wall_expired_primary_not_claimed=not is_main,ready_seal_sha256=sha(E/'fresh_ready_seal224.json'))
   save(out/'result.json',full);append(E/namespace.replace('/recovery','')/('completed_'+mode+'.jsonl'),{k:full.get(k) for k in ('task_id','scientific_method','status','success','new_paid_API','new_fees_CNY','LLM_calls','public_native_calls','hidden_acceptance_calls','primary_eligible')});print(canonical({k:full.get(k) for k in ('task_id','scientific_method','status','success','new_fees_CNY')}),flush=True)
   if should_stop_queue(full):return
   if not is_main and full.get('success') is True and full.get('runtime_core',{}).get('complete'):
    save(E/'engineering_core_nonzero_ready224.json',{'at_utc':now(),'root_main_acceptance_pending':True,'engineering_only_not_primary':True,'task_id':tid,'result':str(out/'result.json'),'result_sha256':sha(out/'result.json'),'new_fees_CNY':str(new_fee),'reused_prefix_calls':len(bank.reused),'complete_core':True,'public_and_private_success':True})
    return
if __name__=='__main__':
 mode=sys.argv[1] if len(sys.argv)>1 else 'seal'
 if mode=='seal':seal();print('FRESH_PREPARATION_READY_NO_API_NATIVE')
 elif mode in ('main','core','core5093','main-ours','main-agentless'):run(mode)
 else:raise ValueError('Unknown mode')

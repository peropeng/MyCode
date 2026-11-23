"""Pure classification/wiring check; no Environment construction or real actor."""
import ast,datetime,hashlib,json,types
from pathlib import Path
from budget_semantics224 import budget_disposition,should_stop_queue
E=Path(__file__).resolve().parent

def check():
 protocol=json.loads((E/'protocol224.json').read_text('utf-8-sig'));limits=protocol['budget']
 assert (limits['max_model_calls_per_flow'],limits['max_output_tokens_per_flow'],limits['max_flow_wall_seconds'],limits['master_seed'])==(64,65536,900,20261008)
 previous_seal=json.loads((E/'fresh_ready_seal224.json').read_text('utf-8-sig'))
 original_core={p:h for p,h in previous_seal['sources'].items() if Path(p).name in ('agentless178.py','ranked_repair178.py')}
 assert len(original_core)==2 and all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in original_core.items())
 def err(name,message,status='BUDGET_CENSORED'):
  return {'status':status,'error':{'type':name,'message':message},'runtime_core':{'complete':False}}
 normal={'finance_fatal':None,'global_cutoff':False,'wall_limited_by_global':False,'search_wall_exhausted':False,'full_wall_exhausted':False}
 cases=[
  ('call_limit64',err('BudgetError','COMMON_FLOW_CALL_OR_OUTPUT_CAP'),normal,False,False),
  ('output_limit65536',err('BudgetError','MODEL_CALL_OR_TOTAL_OUTPUT_BUDGET'),normal,False,False),
  ('frozen_public_reader_stage_limit',err('BudgetError','COMMON_PUBLIC_READER_ROUND_CAP'),normal,False,False),
  ('flow_search_acceptance_reserve',err('BudgetError','METHOD_SEARCH_WALL_BUDGET'),{**normal,'search_wall_exhausted':True},False,False),
  ('flow900_terminal_late',{'status':'COMPLETED','runtime_core':{'complete':True}},{**normal,'full_wall_exhausted':True},False,False),
  ('native_queue_flow_wall',err('TimeoutError','NATIVE_LANE_QUEUE_DEADLINE_BEFORE_PROCESS','ENGINEERING_UNKNOWN'),{**normal,'search_wall_exhausted':True},False,False),
  ('core_initial_flow_wall',err('CoreUnavailable','NO_NEW_METHOD_GLOBAL_DEADLINE','NOT_RUN'),{**normal,'search_wall_exhausted':True},False,False),
  ('global_shortened_flow',err('BudgetError','METHOD_SEARCH_WALL_BUDGET'),{**normal,'search_wall_exhausted':True,'wall_limited_by_global':True},None,True),
  ('global_no_new_hard',err('BudgetError','COMMON_FLOW_CALL_OR_OUTPUT_CAP'),{**normal,'global_cutoff':True},None,True),
  ('shared_phase_cap',err('FinanceGateRejected','SHARED_GLOBAL_OR_PILOT_CAP'),normal,None,True),
  ('account_floor',err('FinanceGateRejected','ACCOUNT_FLOOR_OR_CAP_GATE'),normal,None,True),
  ('provider_unknown',err('FinanceUnknown','PROVIDER_OR_USAGE_UNKNOWN'),normal,None,True),
  ('financial_fatal_without_error',{'status':'COMPLETED'},{**normal,'finance_fatal':{'type':'FinanceUnknown'}},None,True),
  ('unknown_context_cap',err('BudgetError','UNKNOWN_CONTEXT_CAP'),normal,None,True),
  ('normal_time_before_reservation',err('FinanceGateRejected','NO_NEW_FLASH_OR_FLOW_DEADLINE'),{**normal,'search_wall_exhausted':True},False,False),
  ('normal_time_waiting_finance_lock',err('FinanceGateRejected','FINANCE_LOCK_OR_NO_NEW_DEADLINE'),{**normal,'search_wall_exhausted':True},False,False),
  ('time_after_finance_hold',err('FinanceUnknown','DEADLINE_AFTER_RESERVATION_NO_POST'),{**normal,'search_wall_exhausted':True},None,True),
  ('failed_restore_preserved',{**err('BudgetError','COMMON_FLOW_CALL_OR_OUTPUT_CAP'),'stage_ledger':[{'stage':'restore_failure'}]},normal,None,True),
  ('original_reader_engineering',{**err('ValueError','UNKNOWN_OR_NONPUBLIC_FAILURE_NODE','ENGINEERING_UNKNOWN'),'engineering_outcome_unknown':True},normal,None,True),
 ]
 # Compile only the actual Fresh class; its base refuses any finalizer/private path.
 # No imports of bootstrap, finance, model, replay or native executor are executed.
 class NoActorBase:
  def finalize(self,result):raise AssertionError('PURE_CLASSIFIER_MUST_NOT_ENTER_PRIVATE_OR_ACTOR')
 tree=ast.parse((E/'fresh_entry224.py').read_text('utf-8-sig'))
 class_nodes=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name in ('FinanceFatalController','FreshEnvironment')]
 scope={'CommonEnvironment':NoActorBase,'budget_disposition':budget_disposition,'time':types.SimpleNamespace(monotonic=lambda:1000),'now':lambda:'PURE','E':E}
 exec(compile(ast.Module(body=class_nodes,type_ignores=[]),str(E/'fresh_entry224.py'),'exec'),scope)
 rows=[]
 for name,result,context,expected,stop in cases:
  env=scope['FreshEnvironment'].__new__(scope['FreshEnvironment']);env.task_id='PURE_NO_TASK';env.method='PURE_NO_ACTOR';env.calls=0;env.out_tokens=0;env.native_calls=0;env.started=0;env.finance_fatal=context['finance_fatal'];env.budget_context=types.MethodType(lambda self,c=context:c,env)
  full=env.finalize(result)
  assert full['success'] is expected,(name,full)
  assert full['hidden_acceptance_calls']==0,(name,full)
  assert should_stop_queue(full) is stop,(name,full)
  if expected is False:assert full['status']=='DECLARED_FLOW_BUDGET_EXHAUSTED' and full['declared_method_failure_known']
  rows.append({'case':name,'status':full['status'],'success':full['success'],'stop_queue':stop,'private_calls':0})
 # Original evidence is read only and remains engineering UNKNOWN with real private1.
 audit=json.loads((E/'audit224/pilot_evidence224.json').read_text('utf-8-sig'));old=[]
 for r in audit['rows']:
  if 'raw_result' not in r:continue
  p=Path(r['raw_result']);v=json.loads(p.read_text('utf-8-sig'))
  assert hashlib.sha256(p.read_bytes()).hexdigest()==r['raw_result_sha256']
  assert v['success'] is None and v['status']=='ENGINEERING_UNKNOWN' and v['hidden_acceptance_calls']==1
  old.append({'task_id':v['task_id'],'raw_result_sha256':r['raw_result_sha256'],'success':None,'hidden_acceptance_calls':1,'unchanged':True})
 report={'schema':'Exp224-pure-budget-classification/1','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS','classification_cases':len(rows),'rows':rows,'original_AL_evidence':old,'model_POST':0,'native_process':0,'private_read_or_execution':0,'actor_constructed_or_executed':0,'limits_seed_and_original_core_changed':False,'frozen_limits_and_master_seed':{k:limits[k] for k in ('max_model_calls_per_flow','max_output_tokens_per_flow','max_flow_wall_seconds','master_seed')},'original_core_sha256_unchanged':original_core,'scope':'Pure result classification and actual Fresh.finalize method wiring; no environment construction, mock repair or model generation.'}
 path=E/'audit224/budget_classification224.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'status':'PASS','classification_cases':len(rows),'old_AL_unchanged':len(old),'model_POST_native_private_actor':0},ensure_ascii=False))
 return report
if __name__=='__main__':check()

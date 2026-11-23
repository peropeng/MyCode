"""Pure financial bounds/journal checks. No model, subprocess, product or private."""
import ast, copy, dataclasses, importlib.util, json, sys, time, types
from decimal import Decimal
from pathlib import Path
from prepare250_SOURCE import HERE,ROOT,read,sha,canonical,save
DEP=HERE/'deployments/getmoto__moto-5072/trial1'

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec)
 sys.modules[name]=value;spec.loader.exec_module(value);return value

def main():
 p=read(DEP/'protocol225.json');g=read(DEP/'root_grant239.json');full=read(DEP/'FIRST_FULL_BODY_SOURCE_NOT_POSTED.json')
 assert all(g[k] is False for k in g if k.endswith('_authorized') or k.endswith('_admitted'))
 finance=read(DEP/'finance_config239.json')
 tree=ast.parse(Path(p['finance_core']).read_text('utf-8-sig'))
 node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='bounds')
 namespace={'canonical':canonical,'D':Decimal,'GateRejected':RuntimeError}
 exec(compile(ast.Module(body=[node],type_ignores=[]),'original_pure_finance_bounds250','exec'),namespace)
 bounds=namespace['bounds'](full,finance);saved=read(DEP/'FIRST_FULL_BODY_RESERVATION_SOURCE.json')
 assert bounds['input_bound']==saved['input_upper'] and bounds['global_reserve']==saved['full_peak_reserve_CNY']
 sys.path.insert(0,str(DEP))
 import checkpoint250 as ck
 from checkpoint239 import UnsafeResume,atomic
 fixture=HERE/'pure_qa250_fixture';fixture.mkdir(exist_ok=True)
 fake_env=types.SimpleNamespace(task_id='SOURCE_QA_SIMULATED',calls=1,out_tokens=2,native_calls=0,_product_native_roots=0,
  started=time.monotonic(),out=fixture,record=lambda *a:None)
 ck.E=fixture
 ck.CORE=types.SimpleNamespace(NS=types.SimpleNamespace())
 @dataclasses.dataclass
 class TypedState:
  messages:list
  step:int
 ck.CORE.NS.TypedState=TypedState
 state=TypedState(messages=[{'role':'assistant','tool_calls':[{'id':'typed_fake','function':{'name':'read_current_source'}}]}],step=27)
 assert ck.unpacked(ck.packed(state))==state
 atomic(fixture/'checkpoints'/fake_env.task_id/'GENESIS.json',{'original_T0_monotonic':fake_env.started,'actual_POST_T0_UTC':None,'preparation_started_monotonic':fake_env.started})
 clone=fixture/'clone';clone.mkdir(exist_ok=True);(clone/'business.py').write_text('state = "before"\n','utf-8')
 st=ck.Stage(fake_env,'coder',0,clone,types.SimpleNamespace());st.commit('MODEL_NOT_POSTED')
 assert not (fixture/'checkpoints'/fake_env.task_id/'BUDGET_ENDPOINT_OBSERVATION.json').exists()
 expected=(clone/'business.py').read_bytes();(clone/'business.py').write_text('state = "changed"\n','utf-8');st.restore()
 assert (clone/'business.py').read_bytes()==expected
 pointer=read(st.path/'LATEST.json');assert sha(st.path/'states'/pointer['file'])==pointer['SHA256']
 class NeverPOST:
  def request(self,body):raise AssertionError('PURE_QA_UNEXPECTED_NEW_MODEL_POST')
 payload={'messages':[{'role':'user','content':'exact paid mock request'}]};raw={'choices':[{'message':{'content':'settled mock'}}]}
 for phase in ('MODEL_SETTLED_RESPONSE','TOOLS_RESPONSE_PENDING'):
  stage=types.SimpleNamespace(state={'phase':phase,'model_payload':copy.deepcopy(payload),'raw_response':copy.deepcopy(raw),'request_transport_turn':7})
  transport=ck.transport(NeverPOST,stage)();transport.turn=7;transport.env=types.SimpleNamespace(calls=8,out_tokens=10)
  assert transport.request(payload)==raw and transport.turn==8 and transport.env.calls==8 and transport.env.out_tokens==10
  try:transport.request({'messages':[]})
  except UnsafeResume:pass
  else:raise AssertionError('DIFFERENT_PAID_PAYLOAD_MUST_NOT_REUSE')
 for phase in ('MODEL_INTENT','TOOL_INTENT'):
  transport=ck.transport(NeverPOST,types.SimpleNamespace(state={'phase':phase}))()
  try:transport.request(payload)
  except UnsafeResume:pass
  else:raise AssertionError('UNKNOWN_MODEL_TOOL_BOUNDARY_MUST_NOT_REPLAY')
 wire=module('_pure_qa250_wire',DEP/'wire250.py');wire.E=fixture;wire.authorization=lambda:{'trial_id':'SIMULATED_NOT_ACTUAL'}
 original_preparation=fake_env.started
 wire.start_science(fake_env,full)
 genesis=read(fixture/'checkpoints'/fake_env.task_id/'GENESIS.json');first_T0=genesis['original_T0_monotonic']
 assert first_T0==original_preparation and genesis['actual_POST_T0_monotonic']>=first_T0 and genesis['pre_POST_preparation_seconds']>=0
 wire.start_science(fake_env,full)
 assert read(fixture/'checkpoints'/fake_env.task_id/'GENESIS.json')['original_T0_monotonic']==first_T0
 assert fake_env.started==first_T0
 slow_preparation=copy.deepcopy(genesis);slow_preparation.update(original_T0_monotonic=time.monotonic()-1801,actual_POST_T0_UTC=None)
 atomic(fixture/'checkpoints'/fake_env.task_id/'GENESIS.json',slow_preparation);ck.observe_endpoint(fake_env)
 endpoint=read(fixture/'checkpoints'/fake_env.task_id/'BUDGET_ENDPOINT_OBSERVATION.json')
 assert endpoint['elapsed_seconds']>=1800 and endpoint['observation_only'] and endpoint['stop_unbounded_trajectory'] is False
 report={'SOURCE_ONLY':True,'SIMULATED_NOT_ACTUAL_SCIENTIFIC_RESULTS':True,'model_POST':0,'product_native':0,'private_reads':0,'ledger_writes':0,
  'original_financial_bounds_function_full_body_exact':bounds,'atomic_role_blob_pointer_and_restore':True,
  'typed_current_step_full_messages_roundtrip':True,'before_actual_POST_no_budget_endpoint':True,
  'actual_POST_hook_separate_from_original_forward_supervisor_T0_simulated_without_reset':True,
  'prePOST_preparation_cost_in_original_end_to_end_scientific_clock':True,
  'prePOST_preparation_alone_can_cross_fixed_resource_endpoint_without_stopping_full_trajectory':True,
  'settled_model_and_pending_tools_cache_no_POST_and_no_double_counts':True,
  'different_cached_body_or_unknown_intent_refused':True,'all_source_grant_permissions_false':True,
  'QA_fixture_isolated_from_actual_deployment_scientific_state':True,'whole_algorithm_runtime_or_effect_not_claimed':True}
 save(HERE/'SOURCE_QA250.json',report);print(canonical(report))

if __name__=='__main__':main()

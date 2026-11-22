"""Observer-only frozen syntax-blocked C0; never adds model input or repairs code."""
import ast,copy
from contracts241 import *
from environment241 import Environment241 as BaseEnvironment
CERT=ROOT/'结论/20261009_复盘再实验/初始资格V2_自然业务语法阻断.json'
CERT_SHA='51500f02d6d9ee4410fa6e6b05350f43e8fd94fc0a65ce73657e984f59ab9fce'
TASK='python__mypy-10392'

def observe_initial(contract,current_business=None):
 if contract['task_id']!=TASK or sha(CERT)!=CERT_SHA:raise EngineeringUnknown('INITIAL_V2_CERT_TASK_OR_SHA')
 cert=read(CERT)
 if (cert['classification']!='C0_COLLECTION_BLOCKED_BY_LEGAL_BUSINESS_SYNTAX' or not cert['frozen_before_first_index6_model_outcome']
     or cert['actual_initial_goal_completed']!=0 or cert['actual_initial_goal_blocked_by_collection']!=5 or cert['actual_ordinary_passed']!=1):
  raise EngineeringUnknown('INITIAL_V2_CLASSIFICATION')
 expected=contract['c0_business_paths_sha256']
 if len(expected)!=120 or cert['all_actual_C0_business_paths_SHA256']!=expected or (current_business is not None and current_business!=expected):
  raise EngineeringUnknown('INITIAL_V2_CURRENT_BUSINESS_NOT_FROZEN_C0')
 for rel,h in expected.items():
  if sha(Path(contract['template'])/rel)!=h:raise EngineeringUnknown('INITIAL_V2_C0_SOURCE_DRIFT '+rel)
 if sha(contract['pack'])!=cert['shared_pack_SHA256'] or cert['shared_pack_SHA256']!=contract['pack_sha256']:
  raise EngineeringUnknown('INITIAL_V2_PUBLIC_PACK_DRIFT')
 if Path(cert['actual_native_frozen_tests']).resolve()!=Path(contract['frozen_public_test_root']).resolve() or inventory(contract['frozen_public_test_root'])!=contract['frozen_inventory']:
  raise EngineeringUnknown('INITIAL_V2_FROZEN_PUBLIC_DRIFT')
 if {r['node'] for r in cert['public_target_declarations']}!=set(contract['public_target_nodes']):raise EngineeringUnknown('INITIAL_V2_GOAL_DECLARATIONS')
 raw_path=Path(cert['native_result_path'])
 if sha(raw_path)!=cert['native_result_SHA256']:raise EngineeringUnknown('INITIAL_V2_SHARED_RAW_SHA')
 raw=read(raw_path);stop=raw['stop_receipt'];pytest=raw['pytest']
 if (not raw.get('executed') or not raw.get('guard_loaded') or raw.get('timeout') or not raw.get('business_state_unchanged') or not raw.get('frozen_tests_unchanged')
     or not all(stop.get(k) for k in ('root_process_stopped','all_owned_descendants_terminated','owned_job_closed'))):
  raise EngineeringUnknown('INITIAL_V2_SHARED_NATIVE_GUARD_SOURCE_STOP')
 if sha(raw['log'])!=raw['log_sha256']:raise EngineeringUnknown('INITIAL_V2_SHARED_LOG_SHA')
 shared_source=Path(pytest['guard']['source_root'])
 if any(sha(shared_source/rel)!=h for rel,h in expected.items()):raise EngineeringUnknown('INITIAL_V2_SHARED_CURRENT_C0_SOURCE_DRIFT')
 ordinary=contract['ordinary_nodes'];outcomes=pytest['outcomes']
 if (set(outcomes)!=set(ordinary) or not all(outcomes[n]['status']=='passed' for n in ordinary)
     or set(pytest['requested_but_uncollected_nodes'])!=set(contract['public_target_nodes']) or not pytest['collection_errors']):
  raise EngineeringUnknown('INITIAL_V2_SHARED_NODE_COVERAGE')
 syntax=cert['observed_syntax'];source=Path(contract['template'])/syntax['business_relative']
 try:ast.parse(source.read_text('utf-8-sig'))
 except SyntaxError as error:
  if type(error).__name__!=syntax['type'] or error.lineno!=syntax['line'] or str(error.msg)!=syntax['message']:raise EngineeringUnknown('INITIAL_V2_SYNTAX_DRIFT')
 else:raise EngineeringUnknown('INITIAL_V2_SYNTAX_NOT_PRESENT')
 semantic=decode(read(contract['pack']))
 if not all('IndentationError' in semantic['failure_feedback'][n]['detail'] and 'line 154' in semantic['failure_feedback'][n]['detail'] for n in contract['public_target_nodes']):
  raise EngineeringUnknown('INITIAL_V2_ORIGINAL_PACK_MISSING_SHARED_ERROR')
 return {'classification':cert['classification'],'initial_goal_completed':0,'initial_goal_blocked':5,
  'outcomes':copy.deepcopy(outcomes),'ordinary_passed':True,'shared_raw':str(raw_path),'shared_raw_sha256':sha(raw_path),
  'certificate_sha256':CERT_SHA,'all_current_120_business_sha_checked':True,'frozen_public_sha_checked':True,
  'shared_native_all_STOP':True,'new_C0_native_executions':0,'goal_failed_outcomes_fabricated':False,
  'not_actor_feedback':True,'final_exact_goal_plus_ordinary_required':6,'final_once_private_unchanged':True}

class InitialV2Environment(BaseEnvironment):
 def run_regression(self,snapshot=None,nodes=None,label='regression'):
  chosen=snapshot or self.initial_snapshot
  if self.task_id!=TASK or chosen['inventory_sha256']!=digest(self.contract['c0_business_paths_sha256']):
   return super().run_regression(snapshot,nodes,label)
  requested=list(self.public_regression_nodes if nodes is None else nodes)
  if not set(requested)<=set(self.public_regression_nodes):raise ValueError('PRIVATE_OR_NONORDINARY_TEST_REQUEST')
  self.require_action('public');self.restore(chosen);observed=observe_initial(self.contract,self.actor_business_inventory())
  outcomes={n:{**observed['outcomes'][n],'outcome':'passed'} for n in requested}
  # Only the already-public ordinary PASS enters the unchanged original pruner.
  # No certificate/classification or fabricated target outcomes enter LLM bodies.
  result={'passed':True,'failure_count':0,'outcomes':outcomes,'status':'GUARDED_ORDINARY_SHARED_INITIAL_C0',
   'native_record':{'executed':False,'guard_loaded':True,'shared_already_executed_C0_reused':True,
    'new_C0_native_executions':0,'raw_path':observed['shared_raw'],'raw_sha256':observed['shared_raw_sha256']},
   'public_goal_not_added_to_paper_ranking':True}
  return self.record('ordinary_regression',result)

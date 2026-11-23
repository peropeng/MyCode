"""Synthetic prefix/no-retry checks; never touch an active real trial."""
import ast,shutil
from runner251 import *

parsed=[]
for p in HERE.glob('*.py'):ast.parse(p.read_text('utf-8-sig'));parsed.append(ref(p))
fixture={'SystemRoot':'synthetic','PATH':'synthetic','DEEPSEEK_API_KEY':'synthetic-non-secret','UNRELATED_SECRET':'not-for-child','PYTHONPATH':'not-for-child'}
worker_env=trusted_worker_environment('synthetic-own-job',fixture)
if worker_env.get('DEEPSEEK_API_KEY')!=fixture['DEEPSEEK_API_KEY'] or worker_env.get('COMMON_NATIVE_OWNED_JOB')!='synthetic-own-job' or 'UNRELATED_SECRET' in worker_env or 'PYTHONPATH' in worker_env:raise RuntimeError('EXP251_R2_TRUSTED_WORKER_ENV_FAILED')
allowed=0
for kind,script in COMMAND_SCRIPTS.items():
 argv=[str(CONTROLLER),'-X','utf8','-B',str(METHOD_ROOT/script),'--synthetic-construction-only']
 env=controller_environment(argv,kind,fixture)
 if ('DEEPSEEK_API_KEY' in env)!=(kind=='EXACT_SINGLE_MODEL_DISPATCH') or 'UNRELATED_SECRET' in env or 'PYTHONPATH' in env:raise RuntimeError('EXP251_R2_EXACT_DISPATCH_ENV_FAILED')
 allowed+=1
rejects=0
for argv,kind in (([str(CONTROLLER),'-X','utf8','-B',str(METHOD_ROOT/'unknown251.py')],'EXACT_SINGLE_MODEL_DISPATCH'),
 ([str(CONTROLLER),'-X','utf8','-B',str(METHOD_ROOT/'entry251.py')],'EXACT_SINGLE_MODEL_DISPATCH'),
 ([str(CONTROLLER),'-c','synthetic-no-execution'],'EXACT_SINGLE_MODEL_DISPATCH'),
 ([str(CONTROLLER),'-X','utf8','-B',str(METHOD_ROOT/'dispatch_once251_ROOT_ONLY.py')],'UNKNOWN_KIND')):
 try:controller_environment(argv,kind,fixture)
 except RuntimeError as e:
  if 'EXACT_CONTROLLER_ENTRY_REQUIRED' not in str(e):raise
  rejects+=1
 if rejects==0:raise RuntimeError('EXP251_R2_UNKNOWN_ENTRY_NOT_REJECTED')
if rejects!=4:raise RuntimeError('EXP251_R2_EXACT_REJECTION_COUNT')
scratch=HERE/'source_checks/synthetic_prefix';scratch.mkdir(parents=True,exist_ok=False)
trial=scratch/'synthetic_task/trial1';slot=trial/'calls/call001';slot.mkdir(parents=True)
def mock_save(p,v):
 if not Path(p).resolve().is_relative_to(scratch):raise RuntimeError('EXP251_RUNNER_SYNTHETIC_SCOPE')
 save(p,v)
body={'model':'synthetic_no_API','messages':[{'role':'user','content':'whole synthetic'}]};response={'choices':[{'message':{'content':'synthetic'}}],'usage':{'completion_tokens':3}}
stem=slot/'new_generation/llm';metadata={'method':'AGENTLESS_FULL','task_id':'synthetic_task','trial_id':'trial1','call_ordinal':1}
mock_save(slot/'FIRST_UNPOST_BODY.json',body);mock_save(slot/'FIRST_UNPOST_READY.json',metadata)
mock_save(stem/'001_request.json',{'body':body,'body_SHA256':digest(body)})
mock_save(stem/'001_response.json',response);mock_save(stem/'001_finance_receipt.json',{'status':'SETTLED','synthetic_not_real_finance':True})
state={**metadata,'status':'SETTLED_RESPONSE_SAVED','body_SHA256':digest(body),'response_SHA256':digest(response)};mock_save(slot/'DISPATCH_STATE.json',state)
prefix=scan_model_prefix(trial)
if len(prefix)!=1 or prefix[0]['output_tokens']!=3:raise RuntimeError('EXP251_RUNNER_SYNTHETIC_SETTLED_PREFIX_COUNT')
unknown_rejected=False
mock_save(slot/'DISPATCH_STATE.json',{**state,'status':'ACTUAL_POST_DISPATCH_INFLIGHT_NO_RESEND'})
try:scan_model_prefix(trial)
except RuntimeError as e:unknown_rejected='NEVER_REPOST' in str(e)
if not unknown_rejected:raise RuntimeError('EXP251_RUNNER_SYNTHETIC_UNKNOWN_NOT_REJECTED')
mock_save(slot/'DISPATCH_STATE.json',state);cross_trial=False
mock_save(slot/'FIRST_UNPOST_READY.json',{**metadata,'trial_id':'trial2'})
try:scan_model_prefix(trial)
except RuntimeError as e:cross_trial='CROSS_TRIAL' in str(e)
if not cross_trial:raise RuntimeError('EXP251_RUNNER_SYNTHETIC_CROSS_TRIAL_NOT_REJECTED')
native=trial/'native_requests/native001';native.mkdir(parents=True);mock_save(native/'SUPERVISOR_STARTED_ONCE.json',{'synthetic':True})
native_unknown=False
try:scan_native_prefix(trial)
except RuntimeError as e:native_unknown='NEVER_RERUN' in str(e)
if not native_unknown:raise RuntimeError('EXP251_RUNNER_SYNTHETIC_NATIVE_UNKNOWN_NOT_REJECTED')
false=HERE/'false_grants/getmoto__moto-5072/trial1.WHOLE_TRIAL_FALSE.json';closed=False
try:Grant(false)
except RuntimeError as e:closed='GRANT_CLOSED' in str(e)
if not closed:raise RuntimeError('EXP251_RUNNER_FALSE_GRANT_NOT_CLOSED_BEFORE_EXECUTION')
save(HERE/'RUNNER_SOURCE_VALIDATION251.json',{'schema':'EXP251-runner-zero-actual-source-validation/1','source_AST_parsed':parsed,'synthetic_settled_prefix_count_preserved':True,
 'synthetic_trusted_worker_credential_and_own_Job_binding':True,'exact_controller_kinds_constructed':allowed,'only_exact_dispatch_child_credential':True,
 'unknown_script_mismatched_kind_python_c_unknown_kind_rejected':rejects,'credential_values_or_environments_recorded':False,
 'synthetic_unknown_model_no_rePOST':unknown_rejected,'synthetic_other_trial_no_reuse':cross_trial,'synthetic_native_started_unknown_no_rerun':native_unknown,'all_false_grant_closed_before_loading_execution_clients':closed,
 'same_real_trial_ROOT_data_reads_or_writes':0,'actual_model_API_product_native_private_encoder_finance':0,'not_method_scientific_results':True})
if scratch.resolve()!=(HERE/'source_checks/synthetic_prefix').resolve() or not scratch.resolve().is_relative_to(HERE):raise RuntimeError('EXP251_RUNNER_SYNTHETIC_CLEANUP_SCOPE')
shutil.rmtree(scratch)
print(canonical({'status':'RUNNER_PREFIX_AND_UNKNOWN_GUARDS_PASS_SOURCE_ONLY','actual_execution':0}))

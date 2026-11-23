"""Audit existing deployment receipts and prepare future false science candidates."""
from pathlib import Path
import copy,json,hashlib,datetime
from decimal import Decimal
E=Path(__file__).resolve().parent;OLD=E/'runtime_v6_MECHANICAL_SOURCE';D=E/'runtime_v7_SOURCE'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
q=D/'single_startup_qualification5406';raw=read(q/'actor_flow/V7_STARTUP_MECHANICAL_RESULT.json');parent=read(q/'supervision/PARENT_STOP.json')
n=raw['raw_native']['native_record'];identity=n['actual_product_python_identity'];stop_keys=('root_stopped','own_Job_empty_before_close','descendants_stopped')
assert raw['status']=='KNOWN_DEPLOYMENT_NATIVE_EXECUTED' and raw['scientific_result'] is False
assert n['guard_loaded'] and n['business_state_unchanged'] and n['frozen_tests_unchanged'] and n['actual_product_imports'] and not n['timeout']
assert identity['before_product_import'] and identity['IsProcessInJob_specific_own_Job'] and identity['actual_sys_executable'] and identity['actual_sys_prefix']
assert all(n['stop_receipt'].get(k) is True and parent['stop_receipt'].get(k) is True for k in stop_keys)
seal=read(D/'SOURCE_SEAL.json');changed=[p for p,h in seal['sources'].items() if sha(p)!=h];assert not changed
qualification={'schema':'AL241-v7-real-generated-startup-qualification/1','at_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'ACTUAL_DEPLOYMENT_STARTUP_QUALIFIED_PENDING_ROOT_ACCEPTANCE','source_seal_digest':digest(seal),'source_seal_rawSHA':sha(D/'SOURCE_SEAL.json'),
 'real_result':str(q/'actor_flow/V7_STARTUP_MECHANICAL_RESULT.json'),'real_result_SHA':sha(q/'actor_flow/V7_STARTUP_MECHANICAL_RESULT.json'),
 'parent_stop':str(q/'supervision/PARENT_STOP.json'),'parent_stop_SHA':sha(q/'supervision/PARENT_STOP.json'),
 'parent_seconds':parent['seconds'],'generated_seconds':n['seconds'],'parent_STOP':parent['stop_receipt'],'generated_STOP':n['stop_receipt'],
 'actual_before_product_physical_self':identity,'guard_loaded':True,'actual_current_product_imports':len(n['actual_product_imports']),
 'business_and_frozen_SHA_stable':True,'public_script_origin_SHA':raw['script_origin_sha256'],
 'script_marker_retained_only_as_deployment_evidence':raw['raw_native']['status'],'scientific_model_result_or_recovery_score':None,
 'API_POST_private_fiscal_write_or_fee':0,'old_science_T1_not_reopened':True,'one_native_deployment_qualification_only':True,'sealed_sources_changed':changed}
save(D/'V7_STARTUP_QUALIFICATION_AUDIT241.json',qualification)
commands={}
base=read(OLD/'science_release_candidate_FALSE/getmoto__moto-6387/protocol.SOURCE_ONLY.json')
for task in base['task_order']:
 p=read(OLD/'science_release_candidate_FALSE'/task/'protocol.SOURCE_ONLY.json')
 p.update(core_source=str(D/'agentless_paper_main241.py'),masked_native_owner_root=str(D),output_root=str(D/'science_once_six'/task/'actor_flow'),
  supervision_output_root=str(D/'science_once_six'/task/'supervision'),execution_authorized=False,source_only=True,native_authorized=False,model_generation_authorized=False,
  prior_T1_scientific_UNKNOWN_preserved_no_retry=True,Root_v7_generated_deployment_actual={'path':str(D/'V7_STARTUP_QUALIFICATION_AUDIT241.json'),'sha256':sha(D/'V7_STARTUP_QUALIFICATION_AUDIT241.json')},
  Root_actual_241_mechanical_candidate={'path':str(OLD/'MECHANICAL_AUDIT_V6_241.json'),'sha256':sha(OLD/'MECHANICAL_AUDIT_V6_241.json')},
  first_future_complete_small_trial_task='getmoto__moto-6387',old_T1_model_outputs_not_used_as_scientific_continuation=True,
  no_parameters_budget_guard_permissions_finance_or_information_change=True)
 out=D/'science_release_candidate_FALSE'/task;save(out/'protocol.SOURCE_ONLY.json',p)
 g=read(OLD/'science_release_candidate_FALSE'/task/'ROOT_SCIENCE_GRANT.false.template.json')
 g.update(root_authorized=False,native_authorized=False,model_generation_authorized=False,private_acceptance_authorized=False,new_start_UTC=None,
  source_seal_sha256=digest(seal),protocol_sha256=digest(p),protocol_raw_sha256=sha(out/'protocol.SOURCE_ONLY.json'),
  neutral_mechanical_qualification_sha256=sha(D/'V7_STARTUP_QUALIFICATION_AUDIT241.json'),Root_v7_actual_startup_acceptance_pending=True)
 save(out/'ROOT_SCIENCE_GRANT.false.template.json',g)
 commands[task]=[g['controller_physical_python_expected'],'-X','utf8','-B',str(D/'supervisor_runtime_v3_241.py'),'science',
  '--protocol',str(out/'protocol.SCIENCE.release.json'),'--grant',str(out/'ROOT_SCIENCE_GRANT.actual.json'),
  '--seal',str(D/'SOURCE_SEAL.json'),'--contract',p['public_contract']]
save(D/'V7_T2_6387_EXACT_COMMAND_FALSE241.json',{'first_future_complete_small_trial':'getmoto__moto-6387','source_seal_digest':digest(seal),
 'source_seal_rawSHA':sha(D/'SOURCE_SEAL.json'),'all_science_and_private_grants_false':True,'task_order':base['task_order'],
 'T1_5406_scientific_not_retry_or_resumed':True,'T2_command_after_Root_release_only':commands['getmoto__moto-6387'],'commands_all_six_for_source_trace_only':commands,
 'full_original4L40patch40repro_and_true_whole_regression_unchanged':True})

# Preserve and summarize old partial facts, not reinterpret them as a scientific zero.
f=OLD/'science_once_six/getmoto__moto-5406/actor_flow';result=read(f/'result.json');pold=read(f.parent/'supervision/PARENT_STOP.json')
rs=[read(p) for p in (f/'llm').glob('*_finance_receipt.json')]
terminal={'schema':'AL241-v6-T1-actual-closed-partial/1','status':result['status'],'success':None,'raw_result':str(f/'result.json'),'raw_result_SHA':sha(f/'result.json'),
 'core':result['runtime_core'],'error':result['error'],'actual_SETLLED':sum(x['status']=='SETTLED' for x in rs),'actual_UNKNOWN_finance':sum(str(x['status']).startswith('UNKNOWN') for x in rs),
 'actual_known_charge_CNY':str(sum((Decimal(x.get('usage_accounting_upper_CNY','0')) for x in rs if x['status']=='SETTLED'),Decimal(0))),
 'output_tokens':result['output_tokens'],'immutable_selection_present':(f/'immutable_selection.json').exists(),
 'public_whole_regression_goal_ordinary_and_private_actual_runs':0,'reproduction_native_attempts':1,'reproduction_qualified_or_completed':0,
 'actual_parent_STOP':pold['stop_receipt'],'parent_seconds':pold['seconds'],'independent_final_caseguard_not_satisfied':True,
 'source_bug':'runpy bootstrap omitted script directory; winjob241 import failed before actual selfproof or guard',
 'new_v7_deployment_qualification_not_a_T1_scientific_retry':True,'old_full40patch48paid_responses_and_artifacts_preserved':True}
save(D/'OLD_T1_V6_CLOSED_UNKNOWN_AUDIT241.json',terminal)
print(canonical({'v7_qualification':str(D/'V7_STARTUP_QUALIFICATION_AUDIT241.json'),'qualificationSHA':sha(D/'V7_STARTUP_QUALIFICATION_AUDIT241.json'),
 'T2_false_command':str(D/'V7_T2_6387_EXACT_COMMAND_FALSE241.json'),'source_seal':digest(seal),'old_T1_charge_CNY':terminal['actual_known_charge_CNY'],'science_not_started':True}))

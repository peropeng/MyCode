"""Freeze public scalar references and a closed metadata-generation grant."""
import ast
from qualification_registry_common_SOURCE import *

def frozen(path,value):
 path=Path(path).resolve()
 if not path.is_relative_to(S):raise RuntimeError('NEXT_REGISTRY_SOURCE_PREPARATION_WRITE_SCOPE')
 path.parent.mkdir(parents=True,exist_ok=True);raw=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
 if path.exists() and path.read_bytes()!=raw:raise RuntimeError('NEXT_REGISTRY_SOURCE_ALREADY_FROZEN')
 if not path.exists():path.write_bytes(raw)

summary_path=C/'ROOT_RELEASES/ROOT_SIX_CURRENT_C0_SUMMARY_ACTUAL.json';summary=read(summary_path)
by_task={row['task_id']:row for row in summary['fixed_six']}
if set(by_task)!=set(TASKS) or summary['qualified_count']!=4:raise RuntimeError('ROOT_CURRENT_FIXED_SIX_SUMMARY_REQUIRED')
plan_path=R/'结论/20261009_复盘再实验/新确认集与共同预算_前瞻.json';plan=read(plan_path)
if plan['new_main_order'][6:12]!=TASKS:raise RuntimeError('NEXT_REGISTRY_PLAN21_NATURAL_ORDER_DRIFT')
bound_tasks={};scalar_rows=[]
contracts={row['task_id']:row for row in read(I/'TASK_BINDINGS249_SOURCE.json')['tasks']}
blockers={
 'python__mypy-10392':{'classification':'Root_reported_legal_C0_business_syntax_collection_block','type':'IndentationError','business_relative':'mypy/modulefinder.py','line':154,'preceding_for_line':153},
 'python__mypy-11134':{'classification':'Root_reported_legal_C0_business_syntax_collection_block','type':'IndentationError','business_relative':'mypy/subtypes.py','line':482,'preceding_def_line':478}}
for task in TASKS:
 row=by_task[task];stage=C/'qualification'/task/'current_C0';parent=exact(row['parent_ref'])
 if Path(row['parent_ref']['path']).resolve()!=stage/'PARENT_TERMINAL249.json' or not parent_stopped(parent) or parent['task_id']!=task or not row['parent_all_STOP_known']:raise RuntimeError('ROOT_CURRENT_C0_PARENT_STOP_REF_DRIFT')
 start=read(stage/'SUPERVISOR_STARTED_ONCE.json');argv=start['argv'];gp=Path(argv[argv.index('--root-grant')+1]).resolve()
 if not gp.is_relative_to(C) or sha(gp)!=parent['Root_grant_SHA256']:raise RuntimeError('ROOT_CURRENT_C0_RUNTIME_GRANT_PATH_DRIFT')
 ip=I/'qualification'/task/'identity/COMPLETED_IDENTITY249.json';obs=stage/'PUBLIC_CURRENT_C0_OBSERVATION249.json';worker=stage/'COMPLETED_CURRENT_C0_WORKER249.json'
 unknown=stage/'CURRENT_C0_UNKNOWN.json';negative=stage/'ORIGINAL_G_O_NOT_ELIGIBLE.json';channel=stage/'masked_public_native/0002_zero_model_masked_ordinary/run.json'
 status='QUALIFIED' if row['qualified'] else ('INELIGIBLE_PUBLIC_C0' if negative.exists() else 'UNKNOWN')
 b={'public_contract':ref(contracts[task]['public_contract']),'parent':row['parent_ref'],'identity':ref(ip),'identity_parent':ref(ip.parent/'PARENT_TERMINAL249.json'),
  'runtime_grant':ref(gp),'mask_scope':ref(C/'public_views'/task/'COMMON_MASKED_PUBLIC_TEST_SCOPE249.json'),'original_G_O':ref(stage/'original_G_O/run.json'),
  'observation':ref(obs) if obs.exists() else None,'worker':ref(worker) if worker.exists() else None,'unknown':ref(unknown) if unknown.exists() else None,
  'not_eligible':ref(negative) if negative.exists() else None,'masked_channel':ref(channel) if channel.exists() else None,
  'Root_reported_qualification_status':status,'Root_reported_collection_blocker':blockers.get(task),
  'no_original_source_snippet_read_for_diagnostic_label':True}
 bound_tasks[task]=b;scalar_rows.append({'task_id':task,'natural_slot_one_based':TASKS.index(task)+7,'Root_reported_qualification_status':status,
  'parent_all_STOP_known':True,'method_outcome':None,'unknown_not_score_zero':True,'Root_reported_collection_blocker':blockers.get(task),
  'qualification_not_independent_source_runtime_reexecution':True})
common=[t for t in TASKS if bound_tasks[t]['Root_reported_qualification_status']=='QUALIFIED']
if common!=['getmoto__moto-7081','getmoto__moto-6212','getmoto__moto-5406','getmoto__moto-6387']:raise RuntimeError('ROOT_REPORTED_COMMON_FOUR_NATURAL_ORDER_DRIFT')
old_five=['getmoto__moto-5406','getmoto__moto-6387','getmoto__moto-5980','python__mypy-15155','getmoto__moto-5516']
cohorts={'source_pool_distinct_issues':23,'prospective_original_plan_distinct_issues':21,'old_complete_five_issue_set':old_five,
 'old_complete_five_count':5,'current_first_six_issue_set':plan['new_main_order'][:6],'current_first_six_count':6,
 'next_fixed_six_issue_set':TASKS,'next_fixed_six_count':6,'next_current_qualified_issue_set':common,'next_current_qualified_count':4,
 'next_six_overlap_old_five':[t for t in TASKS if t in old_five],'overlap_means_same_issue_reassessment_under_new_protocol':True,
 'current_protocol_new_slots_do_not_establish_historically_unseen_issues':True,'repeats_do_not_increase_distinct_issue_count':True,
 'old_five_scores_not_loaded_or_merged':True,'issue_set_labels_provided_by_Root_no_historical_private_read':True}
inputs={'schema':'EXP249-next-six-public-qualification-frozen-inputs/1','task_order':TASKS,'Root_summary':ref(summary_path),'original_plan21':ref(plan_path),
 'tasks':bound_tasks,'Root_reported_common_qualified_order':common,'cohort_metadata':cohorts,
 'original_first_six_protocol':ref(Q/'protocol249_SOURCE.json'),'OURS_core_V2':ref(M/'OURS_SOURCE_SEAL249_V2.json'),
 'selected_RQ1_release':ref(W/'RQ1_SELECTED_RESEARCH_RELEASE_20261012/ROOT_RQ1_UNIFIED_RESEARCH_RELEASE_SELECTED.json'),
 'original_guard_source':ref(R/'工作区/1011-our19/progress_guard240.py'),
 'public_feedback_codec':ref(R/'工作区/1010-unified-six/finance_queue_remaining_SOURCE/common_public_feedback_codec.py'),
 'original_public_C0_export_helper':ref(M/'common_C0_export249_SOURCE.py'),'new_model_native_private_finance_training_forward_calls':0}
ipath=S/'PUBLIC_QUALIFICATION_INPUTS_SOURCE.json';frozen(ipath,inputs)
frozen(S/'FIXED_SIX_STATUS_PREVIEW_SOURCE.json',{'schema':'EXP249-fixed-six-status-preview-source/1','rows':scalar_rows,'common_qualified_order':common,
 'fixed_slots':6,'qualified':4,'unknown':2,'method_runs_prepared_or_executed_by_this_source':0,'cohort_metadata':cohorts,
 'not_a_paid_method_or_finance_authorization':True,'Root_actual_public_summary':ref(summary_path)})
checks=[]
def check(name,ok):
 if not ok:raise AssertionError(name)
 checks.append({'name':name,'passed':True})
check('full_gate_only_admits_complete_known_qualification',classify(parent_ok=True,worker_ok=True,go_known=True,go_eligible=True,masked_ok=True)=='QUALIFIED')
for field in ('parent_ok','worker_ok','go_known','masked_ok'):
 value={k:True for k in ('parent_ok','worker_ok','go_known','go_eligible','masked_ok')};value[field]=False
 check('missing_'+field+'_stays_unknown',classify(**value)=='UNKNOWN')
check('known_ineligible_public_state_not_method_failure',classify(parent_ok=True,worker_ok=False,go_known=True,go_eligible=False,masked_ok=False)=='INELIGIBLE_PUBLIC_C0')
check('unknown_collection_not_false_Goal_FAIL',classify(parent_ok=True,worker_ok=False,go_known=False,go_eligible=False,masked_ok=False)=='UNKNOWN')
check('fixed_natural_order_and_common4_separate',len(TASKS)==6 and common==[t for t in TASKS if by_task[t]['qualified']])
check('old_five_overlap_explicit_without_scores',cohorts['next_six_overlap_old_five']==['getmoto__moto-5406','getmoto__moto-6387'])
for p in S.glob('*.py'):ast.parse(p.read_text('utf-8-sig'))
vp=S/'SOURCE_VALIDATION.json';frozen(vp,{'schema':'EXP249-next-six-registry-source-policy-check/1','status':'PASS','checks':checks,
 'actual_model_native_private_finance_training_forward':0,'Root_registry_generator_not_executed':True,'original_private_or_Gold_content_not_read':True})
source_paths=list(S.glob('*.py'))+[M/'common_C0_export249_SOURCE.py',M/'shared_public249.py',M/'shared_input249.py',R/'工作区/1011-our19/progress_guard240.py',R/'工作区/1011-our19/public_projection181.py',Path(inputs['public_feedback_codec']['path']),R/'工作区/1010-unified-six/shared_native_v14_certificate_complete/native_masked_public239.py']
sources={str(p):sha(p) for p in source_paths};public={str(p):sha(p) for p in (ipath,vp,S/'FIXED_SIX_STATUS_PREVIEW_SOURCE.json')}
def collect_refs(value):
 if isinstance(value,dict):
  if set(('path','sha256'))<=set(value) and isinstance(value['path'],str) and isinstance(value['sha256'],str):public[value['path']]=value['sha256']
  for v in value.values():collect_refs(v)
 elif isinstance(value,list):
  for v in value:collect_refs(v)
collect_refs(inputs)
for p,h in public.items():
 if sha(p)!=h:raise RuntimeError('NEXT_REGISTRY_FROZEN_PUBLIC_METADATA_DRIFT')
sp=S/'SOURCE_SEAL.json';frozen(sp,{'schema':'EXP249-next-six-independent-public-registry-generator-source/1','sources_SHA256':sources,'public_inputs_SHA256':public,
 'fixed_six_four_qualified_two_unknown_from_Root_current_summary':True,'same_issue_dedup_exposure_labels_preserved':True,
 'original_first_six_RQ1_selected15_OURS_coreV2_unmodified':True,'Root_generator_private_API_native_finance_disabled':True,
 'no_original_test_private_manifest_Gold_or_historical_score_read':True,'actual_model_native_private_finance':0})
gp=S/'ROOT_PUBLIC_REGISTRY_GENERATION_FALSE.json';frozen(gp,{'schema':'EXP249-Root-public-registry-only-grant/1','root_authorized':False,'public_metadata_generation_authorized':False,
 'model_authorized':False,'native_authorized':False,'private_authorized':False,'finance_authorized':False,'training_or_forward_authorized':False,
 'source_seal':ref(sp),'public_qualification_inputs':ref(ipath),'output_directory':str(OUTPUT),'lease_end_UTC':None,
 'root_stop_paths':[str(Q/'ROOT_STOP_REQUESTED.json')],'source_only':True})
py=R/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe';manifest=S/'SOURCE_READY_FALSE.json'
frozen(manifest,{'schema':'EXP249-next-six-public-registry-source-ready-false/1','seal':ref(sp),'false_grant':ref(gp),'scalar_preview':ref(S/'FIXED_SIX_STATUS_PREVIEW_SOURCE.json'),
 'Root_generation_argv':[str(py),'-X','utf8','-B',str(S/'generate_next_six_registry_ROOT_ONLY_SOURCE.py'),'--root-public-registry-grant',str(S/'ROOT_RELEASES/ROOT_PUBLIC_REGISTRY_GENERATION_ACTUAL.json')],
 'Root_sign_fields':['root_authorized/public_metadata_generation_authorized=true','finite lease_end_UTC; source_only=false','all model/native/private/finance/training_or_forward permissions remain false'],
 'new_output_only':str(OUTPUT),'output_not_created_by_SOURCE':True,'fixed_slots':6,'current_qualified':4,'current_unknown':2,
 'remaining_gaps':['Root reviews and runs metadata generator','Root funding and complete-baseline-pilot decision','later exact method contracts and finance phase source review; no current method/finance config changed'],
 'actual_model_native_private_finance_training_forward':0})
print(canonical({'status':'NEXT_SIX_REGISTRY_SOURCE_READY_FALSE','seal':ref(sp),'manifest':ref(manifest),'policy_checks':len(checks),'qualified_from_Root':4,'unknown':2,'actual_calls':0}))

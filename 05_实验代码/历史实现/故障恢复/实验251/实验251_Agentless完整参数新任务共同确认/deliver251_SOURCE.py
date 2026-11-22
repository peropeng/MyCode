"""Current exact launch packet and source-body preflight; zero actual execution."""
from runtime251 import *

seal_path=HERE/'SOURCE_SEAL251_V2.json';verify_source_seal(seal_path)
task='getmoto__moto-5072';trial='trial1';contract_path=HERE/'contracts'/task/(trial+'.AGENTLESS_SOURCE_V2.json')
c,out,config,public,common,supp,current=checked_contract(contract_path)
slot=HERE/'source_previews'/task/trial/'calls/call001';body=read(slot/'FIRST_UNPOST_BODY.json');ready=read(slot/'FIRST_UNPOST_READY.json')
false_model=read(slot/'ROOT_EXACT_MODEL_GRANT_FALSE.json');false_prep=HERE/'grant_templates'/task/(trial+'.PREPARATION_FALSE.json');prep=read(false_prep)
fields=('root_authorized','model_authorized','finance_authorized','native_authorized','private_authorized')
if any(false_model[k] is not False or prep[k] is not False for k in fields) or prep['preparation_authorized'] is not False:raise RuntimeError('EXP251_DELIVERY_PERMISSION_NOT_FALSE')
if ready['source_preview_only'] is not True or ready['body_SHA256']!=digest(body) or ready['method_source_seal']!=ref(seal_path) or false_model['ready_SHA256']!=sha(slot/'FIRST_UNPOST_READY.json'):raise RuntimeError('EXP251_DELIVERY_READY_BODY_OR_SOURCE_DRIFT')
if c['finance_configuration']['sha256']!='f5789b9de1fb7b8134cd69a53f1107b7293c1b0e53fc288cbba333770118c9fc':raise RuntimeError('EXP251_DELIVERY_CURRENT_V2_CONFIG_REQUIRED')
messages=body['messages'];shared=[m for m in messages if str(m.get('content','')).startswith(common.TAG)]
if len(shared)!=1 or json.loads(shared[0]['content'][len(common.TAG):])!=supp:raise RuntimeError('EXP251_DELIVERY_COMPLETE_SHARED_CURRENT_C0_OBJECT')
stripped=copy.deepcopy(body);stripped['messages']=[m for m in stripped['messages'] if not str(m.get('content','')).startswith(common.TAG)]
if common.inject(stripped,config,task)!=body:raise RuntimeError('EXP251_DELIVERY_FULL_SHARED_INJECTION')
archived=HERE/'source_previews_v1_SOURCE_ONLY'/task/trial/'calls/call001/FIRST_UNPOST_BODY.json'
same_first_body=archived.exists() and archived.read_bytes()==(slot/'FIRST_UNPOST_BODY.json').read_bytes()
if not same_first_body:raise RuntimeError('EXP251_V2_CONFIG_CHANGED_SCIENTIFIC_MODEL_BODY')
if (out/'SCIENCE_T0_TRIAL_PREPARATION_STARTED.json').exists():raise RuntimeError('EXP251_SOURCE_DELIVERY_ALREADY_STARTS_ACTUAL_TRIAL')
vector=read(HERE/'PUBLIC_DENSE_BINDINGS251_SOURCE.json')['tasks'][task];cache=read(vector['cache_path'])
if sha(vector['cache_path'])!=vector['cache_SHA256'] or cache['source_files_sha256']!=public.load_public_task(task)['contract']['c0_business_paths_sha256'] or cache['query_sha256']!=vector['query_SHA256'] or cache.get('query_complete') is not True or cache.get('query_truncated') is not False:raise RuntimeError('EXP251_DELIVERY_EXACT_COMPLETE_DENSE')
verified=0
for key,h in cache['vector_sha256'].items():
 if sha(Path(cache['vectors_dir'])/(key+'.npy'))!=h:raise RuntimeError('EXP251_DELIVERY_FULL_VECTOR_DRIFT')
 verified+=1
core_path=HERE/'agentless_core/agentless178.py';source_map=read(HERE/'COPIED_SOURCE_MAP251.json')['files'];binding=source_map[str(core_path)]
if core_path.read_bytes()!=Path(binding['source']).read_bytes():raise RuntimeError('EXP251_DELIVERY_AUTHOR_CORE_NOT_EXACT')
budget=financial_bounds(body,config)
if budget!=ready['full_original_financial_bounds'] or body['max_tokens']!=8192 or body['temperature']!=0 or body['model']!='deepseek-flash':raise RuntimeError('EXP251_DELIVERY_FIRST_AUTHOR_BODY_BOUNDS')
preflight={'schema':'EXP251-source-first-complete-body-preflight/1','UTC':now(),'source_seal':ref(seal_path),'contract':ref(contract_path),
 'common_current_C0_V2_exact':True,'shared_supplement_identical_after_V1_to_V2_registry_pin':True,'full_first_body_bytes_identical_to_V1_SOURCE_preview':same_first_body,
 'complete_author_core':ref(core_path),'byte_exact_original_core':True,'all_permissions_false':True,'actual_trial_T0_not_started':True,
 'complete_first_body':ref(slot/'FIRST_UNPOST_BODY.json'),'body_semantic_SHA256':digest(body),'canonical_body_bytes':len(canonical(body).encode()),'full_peak_reserve_CNY':budget['global_reserve'],
 'source_AST_and_synthetic_replay_check':ref(HERE/'SOURCE_VALIDATION251.json'),'full_public_vector_SHA256_checks':verified,'dense_query_and_C0_complete_exact':True,
 'actual_model_POST_product_native_private_encoder_finance':0,'first_source_preview_is_not_a_method_scientific_result':True}
save(HERE/'FIRST_BODY_PREFLIGHT251_SOURCE.json',preflight)
python=str(ROOT/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe');prep_actual=HERE/'ROOT_RELEASES/Moto5072_trial1_PREPARATION_ACTUAL_ROOT.json'
actual_slot=out/'calls/call001';model_actual=actual_slot/'ROOT_EXACT_MODEL_ACTUAL_ROOT.json'
packet={'schema':'EXP251-final-full-Agentless-source-delivery/1','UTC':now(),'write_scope':str(HERE),'branch':'exp/1012-exp251-agentless-confirmation',
 'method_user_name':'Agentless','first_task':task,'first_trial':trial,'source_seal':ref(seal_path),'protocol':ref(HERE/'protocol251_SOURCE.json'),'contract':ref(contract_path),
 'first_SOURCE_body':ref(slot/'FIRST_UNPOST_BODY.json'),'first_SOURCE_ready':ref(slot/'FIRST_UNPOST_READY.json'),'body_semantic_SHA256':digest(body),'reserve_peak_CNY':budget['global_reserve'],
 'preparation_false_grant':ref(false_prep),'SOURCE_model_false_grant':ref(slot/'ROOT_EXACT_MODEL_GRANT_FALSE.json'),'preflight':ref(HERE/'FIRST_BODY_PREFLIGHT251_SOURCE.json'),
 'actual_prepare_argv':[python,'-X','utf8','-B',str(HERE/'entry251.py'),'--contract',str(contract_path),'--root-preparation-grant',str(prep_actual)],
 'after_actual_prepare_create_model_false_argv':[python,'-X','utf8','-B',str(HERE/'prepare_false_grants251_SOURCE.py'),'--model-ready-dir',str(actual_slot)],
 'first_exact_POST_after_Root_grant_argv':[python,'-X','utf8','-B',str(HERE/'dispatch_once251_ROOT_ONLY.py'),'--ready-dir',str(actual_slot),'--root-grant',str(model_actual)],
 'same_trial_pure_consume_argv':[python,'-X','utf8','-B',str(HERE/'entry251.py'),'--contract',str(contract_path),'--root-preparation-grant',str(prep_actual)],
 'native_false_argv_template':[python,'-X','utf8','-B',str(HERE/'prepare_false_grants251_SOURCE.py'),'--native-ready','<STATUS.native ready_path>'],
 'native_once_argv_template':[python,'-X','utf8','-B',str(HERE/'native_once251_ROOT_ONLY.py'),'--ready','<STATUS.native ready_path>','--root-grant','<Root exact one-native grant>'],
 'freeze_author_selection_argv':[python,'-X','utf8','-B',str(HERE/'freeze_final251_SOURCE.py'),'--contract',str(contract_path)],
 'once_independent_final_argv_template':[python,'-X','utf8','-B',str(HERE/'final_once251_ROOT_ONLY.py'),'--ready','<frozen_final/FINAL_READY.json>','--root-grant','<Root exact once-final grant>'],
 'Root_must_review_then_write_actual_grants_not_run_FALSE_as_permission':True,'no_source_preview_POST':True,
 'full_core_parameters':{'fine_location_sets':4,'patches_per_location':10,'reproduction_samples':40,'fine_temperature':.8,'patch_and_reproduction_first_greedy_rest_point8':True,'max_model_stages':88},
 'same_trial_complete_settled_request_only_resume':True,'all_stage_atomic_checkpoints':True,'no_extra_best_of_or_other_trial_reuse':True,
 'original_G_O_filters_private_once_and_negative_results_preserved':True,'Dask_plan_false':ref(HERE/'DASK_ZERO_API_DENSE_PREPARATION_PLAN251_SOURCE.json'),
 'Dask_POST_closed_until_exact_dense_ready':True,'actual_model_POST_native_private_encoder_finance':0}
save(HERE/'DELIVERY251_SOURCE_FINAL.json',packet)
print(canonical({'status':'FULL_AGENTLESS_SOURCE_READY_FOR_ROOT_REVIEW','source_seal_SHA256':sha(seal_path),'body_SHA256':digest(body),'reserve_CNY':budget['global_reserve'],'vectors_verified':verified,'delivery':str(HERE/'DELIVERY251_SOURCE_FINAL.json'),'actual_model_native':0}))

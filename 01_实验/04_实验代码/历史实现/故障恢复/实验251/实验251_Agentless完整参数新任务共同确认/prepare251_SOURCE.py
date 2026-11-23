"""Freeze six x three plan and first-two public-only contracts; no generation."""
from runtime251 import *

original=read(E249/'protocol249_SOURCE.json')
p={'schema':'EXP251-full-Agentless-fixed-six-three-trials/1','method':METHOD,'author_method':AUTHOR_METHOD,
 'task_order':original['task_order'],'trial_ids':original['trial_ids'],'trial_master_seeds':original['trial_master_seeds'],
 'first_trial_priority':'getmoto__moto-5072','issues_in_plan':6,'trials_per_issue':3,
 'author_core':read(HERE/'agentless_core/FORMAL_PARAMETERS_EVIDENCE.json')['verified_sample_parameters'],
 'stage_order':['suspicious_files','irrelevant_folders','dense_retrieval','file_combine','related_elements','fine_locations','forty_independent_patches','forty_original_reproductions','normalized_test_vote','ordinary_regression_selection','candidate_regression_reproduction','normalized_patch_vote'],
 'actual_generation_model':'deepseek-flash','dense_model':'existing local Qwen3-Embedding-0.6B','new_encoder_or_download_authorized':False,
 'public_information':'same exact public history/current C0/masked view as all three methods; no other-method candidate or acceptance',
 'fixed_resource_endpoint':{'seconds':1800,'model_calls':128,'output_tokens':131072,'qualified_repair_before_any_cap_required':True},
 'natural_endpoint':'same exact trajectory/internal sampling continues to complete; unknown/finance/process censor separate',
 'operational_protection':{'flow_wall_seconds':86400,'model_calls_total':1024,'output_tokens_total':33554432,'product_native_roots_total':2048,'all_owned_OS_roots_total':16384,'per_native_timeout_seconds':300},
 'clock_policy':'START_AT_FIRST_REAL_TRIAL_PREPARATION','SOURCE_preview_does_not_start_trial':True,
 'atomic_boundary_policy':'all complete messages/stages/candidates/tests/votes/native receipts; no inflight or unknown resend; exact settled same-trial replay only',
 'seed_is_client_identity_not_provider_determinism':True,'no_cross_trial_response_reuse':True,
 'adaptations':['Flash replaces GPT-4o','Existing local Qwen replaces text-embedding-3-small','Original fixed local G/O replaces full repository regression discovery; original G retained for common acceptance','AST skeleton/normalization compatibility'],
 'all_18_trials_reported_no_best_only':True,'new_issue_count_not_incremented_by_repeats':True,
 'source_only':True,'model_authorized':False,'native_authorized':False,'private_authorized':False,'finance_authorized':False}
save(HERE/'protocol251_SOURCE.json',p)

source_paths=[v for v in HERE.rglob('*.py') if not any(x in ('runs','source_previews','paper_review') for x in v.relative_to(HERE).parts)]
sources={str(v):sha(v) for v in source_paths}
candidate=read(SHARED/'OURS_CANDIDATE_NATIVE_SOURCE_SEAL249_V1.json')
for path,h in candidate['sources_SHA256'].items():
 if sha(path)!=h:raise RuntimeError('EXP251_INHERITED_NATIVE_CORE_SOURCE_DRIFT')
 sources[path]=h
for name in ('shared_public249.py','shared_input249.py'):
 sources[str(SHARED/name)]=sha(SHARED/name)
for name in ('continuous_core_v3.py','completion_transport_v3.py','common_public_feedback_codec.py'):
 sources[str(FIN/name)]=sha(FIN/name)
public=read(HERE/'PUBLIC_SOURCE_BINDINGS249_REFERENCE.json')
inputs=copy.deepcopy(public['public_inputs_SHA256'])
for v in (HERE/'protocol251_SOURCE.json',HERE/'PUBLIC_DENSE_BINDINGS251_SOURCE.json',HERE/'agentless_core/agentless_source_derivative178.json',HERE/'agentless_core/agentless_bridge/official_prompts166.json',HERE/'agentless_core/FORMAL_PARAMETERS_EVIDENCE.json',SHARED/'PUBLIC_SOURCE_BINDINGS249.json'):
 inputs[str(v)]=sha(v)
for row in read(HERE/'PUBLIC_DENSE_BINDINGS251_SOURCE.json')['tasks'].values():
 if row['exact_cache_found']:inputs[row['cache_path']]=row['cache_SHA256']
seal={'schema':'EXP251-complete-Agentless-source/1','frozen_UTC':now(),'sources_SHA256':sources,'public_inputs_SHA256':inputs,
 'author_core_exact_byte_copy':True,'four_location_sets_ten_patches_each_forty_reproductions':True,'MAX_model_stages':88,
 'all_original_selection_normalization_vote_stages_preserved':True,'source_preparation_model_native_private_finance':0}
seal_path=HERE/'SOURCE_SEAL251_V2.json';save(seal_path,seal)
rows=[]
for task in p['task_order'][:2]:
 base=read(SHARED/'contracts'/task/'trial1.OURS248_SOURCE_V2.json')
 for trial,master in zip(p['trial_ids'],p['trial_master_seeds']):
  c={k:copy.deepcopy(base[k]) for k in ('public_contract','public_test_scope_contract','current_C0_observation','current_C0_parent_terminal','finance_configuration','fixed_resource_endpoint')}
  c['finance_configuration']=ref(ROOT/'工作区/1012-until0900-common/CONFIRMATION_ACCEPTED_C0_V2_FINANCE_CONFIG.json')
  c.update(schema='EXP251-full-Agentless-new-task-trial-contract/1',method=METHOD,author_method=AUTHOR_METHOD,task_id=task,trial_id=trial,trial_master_seed=master,
   output_root=str(HERE/'runs'/METHOD/task/trial),finance_phase=PHASE,method_source_seal=ref(seal_path),clock_policy=p['clock_policy'],
   public_order='Exact public-contract C0 file insertion order; no task-dependent reordering',
   all_stage_atomic_checkpoint=True,source_only=True,model_authorized=False,native_authorized=False,private_authorized=False,finance_authorized=False,
   seed_does_not_guarantee_provider_determinism=True,old_or_other_trial_outputs_as_new_repeat=False,
   dense_public_preprocessing=copy.deepcopy(read(HERE/'PUBLIC_DENSE_BINDINGS251_SOURCE.json')['tasks'][task]))
  cpath=HERE/'contracts'/task/(trial+'.AGENTLESS_SOURCE_V2.json');save(cpath,c);checked_contract(cpath)
  false={'schema':'EXP251-pure-trial-preparation-root-grant/1','method':METHOD,'task_id':task,'trial_id':trial,'root_authorized':False,'preparation_authorized':False,
   'model_authorized':False,'native_authorized':False,'private_authorized':False,'finance_authorized':False,'contract_SHA256':sha(cpath),'method_source_seal_SHA256':sha(seal_path),'lease_end_UTC':None,'root_stop_paths':[]}
  fpath=HERE/'grant_templates'/task/(trial+'.PREPARATION_FALSE.json');save(fpath,false)
  rows.append({'task_id':task,'trial_id':trial,'contract':ref(cpath),'preparation_false':ref(fpath),'dense_exact_available':c['dense_public_preprocessing']['exact_cache_found'],
   'actual_prepare_argv':[str(ROOT/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'),'-X','utf8','-B',str(HERE/'entry251.py'),'--contract',str(cpath),'--root-preparation-grant','<Root actual preparation grant path>'],
   'SOURCE_preview_argv':[str(ROOT/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'),'-X','utf8','-B',str(HERE/'entry251.py'),'--contract',str(cpath),'--source-preview']})
save(HERE/'FIRST_TWO_THREE_CONTRACTS251_SOURCE.json',{'source_seal':ref(seal_path),'rows':rows,'actual_generation_native_private_finance':0})
print(canonical({'status':'SOURCE_CONTRACTS_READY_FALSE','source_seal_SHA256':sha(seal_path),'contracts':len(rows),'actual':0}))

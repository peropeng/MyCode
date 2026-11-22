"""Public-only exact-source cache inventory and zero-API local plan; no encoder."""
from runtime251 import *

task='dask__dask-9378';row=read(HERE/'PUBLIC_DENSE_BINDINGS251_SOURCE.json')['tasks'][task];public,_=shared_modules();data=public.load_public_task(task)
expected=data['contract']['c0_business_paths_sha256'];cache_root=ROOT/'工作区/1008-2320-exp224-flash-common/实验/实验224_二十三题Flash完整共同恢复比较/retrieval'
candidates=[]
for p in sorted((cache_root/'cases_v2').glob('*.json')):
 value=read(p)
 if value.get('source_files_sha256')==expected:
  code_keys=sorted({v['vector_key'] for v in value['nodes']});candidates.append({'cache':ref(p),'source_inventory_SHA256':digest(expected),
   'same_Dask_C0_source_only':True,'exact_complete_query_matches':value.get('query_sha256')==row['query_SHA256'],
   'query_SHA256':value.get('query_sha256'),'code_vector_count':len(code_keys),'vectors_dir':value['vectors_dir'],
   'model_identity_SHA256':value['model_identity_sha256'],'all_code_vectors_bound_in_cache':all(k in value['vector_sha256'] for k in code_keys)})
model=ROOT/'工作区/0922-exp124-ranking-baselines/third_party/Qwen3-Embedding-0.6B'
wrapper=ROOT/'工作区/0922-exp124-ranking-baselines/third_party/StepFinder/Q3Emb.py'
plan={'schema':'EXP251-Dask-exact-local-dense-zero-API-preparation-plan/1','task_id':task,'source_inventory_SHA256':digest(expected),'query_SHA256':row['query_SHA256'],
 'complete_query':row['query'],'currently_exact_complete_cache':False,'same_Dask_source_only_cache_candidates':candidates,
 'existing_local_model_path':str(model),'existing_local_wrapper':ref(wrapper),'model_identity_manifest':ref(ROOT/'工作区/0922-exp124-ranking-baselines/实验/实验124_责任排序强基线与外部迁移/results/preclaim_binding.json'),
 'prepare_function':{'path':str(HERE/'agentless_core/agentless_bridge/dense166.py'),'SHA256':sha(HERE/'agentless_core/agentless_bridge/dense166.py'),'symbol':'prepare'},
 'parameters':{'device':'cpu','batch_size':4,'torch_threads':4,'chunk_tokens':512,'chunk_overlap':0,'query_max_tokens':8192,'query_truncation':False},
 'reuse_rule':'Only vectors bound to an exact same-Dask C0/source/model cache, and only after current text/key/hash identity. No other-issue source cache or model outputs. Missing code/query texts get actual existing-local-model forward.',
 'execution_requires_new_exact_Root_local_preparation_grant':True,'new_trial_T0_must_start_before_real_new_forward_preparation':True,
 'CPU_owned_Job_and_peak_memory_or_timeout_censor_receipt_required':True,'all_encode_cost_measured_not_claimed_cache_hit':True,
 'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','no_model_download_fit_Gold_private_or_API':True,
 'encoder_forward_authorized':False,'root_authorized':False,'model_POST_authorized':False,'native_authorized':False,'private_authorized':False,'finance_authorized':False,
 'read_only_plan_actual_encoder_POST_native_private_finance':0,
 'next_boundary':'Root approves full exact cache after completed owned-worker STOP; add Root_prepared_exact_dense_cache immutable receipt to a new Dask contract. Current entry blocks Dask before any model POST.'}
save(HERE/'DASK_ZERO_API_DENSE_PREPARATION_PLAN251_SOURCE.json',plan)
print(canonical({'status':'DASK_LOCAL_PREPARATION_PLAN_FALSE','same_source_cache_candidates':len(candidates),'actual_encoder_API_native_private_finance':0}))

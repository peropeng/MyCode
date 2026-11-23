"""Byte-preserving relocation only. No model import/forward/native/science/fiscal."""
from pathlib import Path
import ast, copy, datetime, hashlib, json
E=Path(__file__).resolve().parent
OLD=E/'resource_gpu_f32_v1_SOURCE_ONLY'
NEW=E/'resource_gpu_f32_v2_ROOT_OWNED_SESSION'
ROOT=Path('D:/Code/毕设/graduate-thesis-experiments')
ACCEPTANCE=ROOT/'工作区/1010-unified-six/ROOT_GPU_QUALIFICATION_ACCEPTANCE.json'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')

if NEW.exists():raise RuntimeError('NEW_ROOT_OWNED_SCOPE_ONCE_NO_OVERWRITE')
old_seal_raw=sha(OLD/'SOURCE_SEAL.json');old_protocol_raw=sha(OLD/'GPU_RESOURCE_PROTOCOL_SOURCE_ONLY.json')
old_seal=read(OLD/'SOURCE_SEAL.json');old_p=read(OLD/'GPU_RESOURCE_PROTOCOL_SOURCE_ONLY.json')
assert old_seal['protocol_sha256']==digest(old_p)
acceptance=read(ACCEPTANCE)
assert acceptance['status']=='ROOT_ACCEPTED_COMPLETE_GPU_QUALIFICATION'
NEW.mkdir()
copies={}
for name,h in old_seal['source_files'].items():
 data=(OLD/name).read_bytes();assert hashlib.sha256(data).hexdigest()==h
 ast.parse(data.decode('utf-8-sig'))
 (NEW/name).write_bytes(data);assert sha(NEW/name)==h
 copies[name]={'v1':str(OLD/name),'v2':str(NEW/name),'sha256':h,'exact_bytes_equal':True}
for path,h in old_seal['external_sources'].items():assert sha(path)==h
for key in ('public_inputs','source_complete_keys','qualification_inputs'):
 assert sha(old_p[key])==old_p[key+'_sha256']

p=copy.deepcopy(old_p)
p.update(scope='AL_GPU_PUBLIC_INDEX_F32_V2_ROOT_OWNED_SESSION_UNIFIED_SIX',
 new_runtime_root=str(NEW/'runtime'),new_gpu_cache_root=str(NEW/'gpu_cache'),
 independent_ROOT_owned_full_session_required=True,subagent_must_not_launch_or_own_exec_session=True,
 prior_full_v1_completion_and_STOP='UNKNOWN_NO_TERMINAL_NO_ORIGINAL_STOP_RECEIPT',
 prior_full_v1_partial_values_reuse_forbidden=True,
 prior_successful_three_text_qualification_not_rerun=True,
 accepted_qualification_receipt={'path':str(ACCEPTANCE),'sha256':sha(ACCEPTANCE)},
 v2_all13877_GPU_unique_new_forward_required=True,full_phase_only_Root_grant=True)
save(NEW/'GPU_RESOURCE_PROTOCOL_SOURCE_ONLY.json',p)
seal=copy.deepcopy(old_seal);seal.update(protocol_sha256=digest(p),
 relocation_exact_four_py_copies=True,new_scope_no_execution=True)
save(NEW/'SOURCE_SEAL.json',seal)
g={'schema':'Agentless241-new-GPU-public-index-root-resource-grant/1','scope':p['scope'],
 'phase':'full_six','root_authorized':False,'resource_encoder_only_authorized':False,
 'GPU_exclusive_resource_lease_confirmed_by_Root':False,'all_scientific_generation_native_private_authorized':False,
 'max_wall_seconds':3600,'new_start_UTC':None,'new_hard_deadline_UTC':None,
 'protocol_sha256':digest(p),'source_seal_sha256':digest(seal),
 'qualification_actual_complete_STOP_Root_acceptance':{'path':str(ACCEPTANCE),'sha256':sha(ACCEPTANCE)},
 'no_old_CPU_clock_cache_or_result_reuse':True,'no_v1_unsealed_GPU_partial_reuse':True,
 'Root_owns_exec_session_and_waits_until_STOP':True}
save(NEW/'ROOT_GPU_FULL_SIX_GRANT.false.template.json',g)
command=[p['physical_controller_python'],'-X','utf8','-B',str(NEW/'gpu_resource_driver241.py'),
 'run','--grant',str(NEW/'ROOT_GPU_FULL_SIX_GRANT.json')]
ready={'schema':'Agentless241-GPU-v2-Root-owned-session-source-ready/1',
 'prepared_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'directory':str(NEW),
 'protocol_sha256':digest(p),'protocol_raw_sha256':sha(NEW/'GPU_RESOURCE_PROTOCOL_SOURCE_ONLY.json'),
 'source_seal_sha256':digest(seal),'source_seal_raw_sha256':sha(NEW/'SOURCE_SEAL.json'),
 'copied_four_py_exact_SHA':copies,'model_identity_and_precision_policy_identical':
 p['original_model_identity']==old_p['original_model_identity'] and p['precision_policy']==old_p['precision_policy'],
 'same_six_source_query_union13877':True,'same_public_inputs_sha256':old_seal['input_sha256'],
 'existing_actual_qualification_acceptance':g['qualification_actual_complete_STOP_Root_acceptance'],
 'qualification_forward_not_rerun':True,'full_GPU13877_all_new_recompute_required':True,
 'v1_old_partial_and_original_raw_left_unchanged':True,
 'v1_original_STOP_unknown_not_fabricated':True,'currentabsence_only_Root_reported_not_new_STOP':True,
 'v2_RUNTIME_and_GPU_cache_absent':not (NEW/'runtime').exists() and not (NEW/'gpu_cache').exists(),
 'all_new_grants_false':True,'actual_encoder_model_GPU_CPU_forward_NATIVE_API_private_fiscal':0,
 'Root_only_full_launch_command':command,'subagent_launch_prohibited':True,
 'full_execution_ready':False,'pending_Root_seal_review_true_grant_and_ROOT_owned_exec_session':True}
save(NEW/'GPU_SOURCE_READY.json',ready)
assert sha(OLD/'SOURCE_SEAL.json')==old_seal_raw
assert sha(OLD/'GPU_RESOURCE_PROTOCOL_SOURCE_ONLY.json')==old_protocol_raw
print(canonical({'directory':str(NEW),'protocol_sha256':digest(p),'source_seal_sha256':digest(seal),
 'four_py_identical':True,'newgrant_false':True,'runtime_cache_absent':True,'launch_only_Root':True}))

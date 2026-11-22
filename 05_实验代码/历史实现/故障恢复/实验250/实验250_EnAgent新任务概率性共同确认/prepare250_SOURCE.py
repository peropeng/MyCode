"""Copy only source, never an old request/patch/checkpoint/result or native tree."""
import ast, hashlib, json, shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=Path('D:/Code/毕设/graduate-thesis-experiments')
BASE=ROOT/'工作区/1011-exp245-enagent-unbudgeted/实验/实验245_EnAgent论文完整配置无外部预算'
PARENT=ROOT/'工作区/1012-exp249-prospective-confirmation/实验/实验249_固定顺序新任务共同确认'
COMMON=ROOT/'工作区/1012-until0900-common'

def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def save(p,v):
 p=Path(p).resolve();assert p.is_relative_to(HERE)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')

def replace(path,old,new,count=1):
 text=path.read_text('utf-8-sig')
 if text.count(old)!=count:raise RuntimeError('SOURCE_ANCHOR_COUNT '+str(path)+' '+str(text.count(old)))
 path.write_text(text.replace(old,new),'utf-8')

def main():
 target=HERE/'template';target.mkdir(parents=True,exist_ok=True)
 copied={}
 for src in BASE.glob('*.py'):
  if src.name.startswith(('prepare','configure','seal','source_qa','test_','mechanical')):continue
  dst=target/src.name;shutil.copyfile(src,dst);copied[str(src)]=sha(src)
 shutil.copytree(BASE/'repro_guard225',target/'repro_guard225',dirs_exist_ok=True)
 for name in ('public_environment250.py','source_control250.py','wire250.py','entry250_runtime.py'):
  shutil.copyfile(HERE/name,target/name)
 # Runtime names remain compatible with the already working source adapters.
 (target/'controller250.py').write_bytes((BASE/'controller245.py').read_bytes())
 (target/'checkpoint250.py').write_bytes((BASE/'checkpoint245.py').read_bytes())
 replace(target/'controller250.py','import checkpoint245 as ck','import checkpoint250 as ck')
 replace(target/'controller250.py',"semantic_spec=copy.deepcopy(spec);semantic_spec['initial_repo']='/workspace/common_public_C0'", "semantic_spec=copy.deepcopy(spec);semantic_spec['initial_repo']='/workspace/common_public_C0'\n env.started=float(os.environ.get('EXP239_LEASE_STARTED_MONOTONIC',env.started))")
 replace(target/'controller250.py',"{'original_T0_monotonic':env.started,'initial_spec':spec", "{'original_T0_monotonic':env.started,'actual_POST_T0_UTC':None,'actual_POST_T0_monotonic':None,'preparation_started_monotonic':env.started,'end_to_end_clock_includes_forward_supervisor_preparation':True,'initial_spec':spec")
 replace(target/'backend225.py',"('Exp245|'+self.env.task_id", "('Exp250|'+str(authorization()['trial_master_seed'])+'|'+self.env.task_id")
 # Keep the complete old author history; injection/finance are the new shared interface.
 (target/'flash_io239.py').write_text('''"""New common-C0 wrapper; same continuous finance, no warm old model prefix."""
from common166 import *
from wire250 import generate
''','utf-8')
 (target/'control235.py').write_text('from source_control250 import *\n','utf-8')
 replace(target/'worker_v2_225.py',"'controller225.py'", "'controller250.py'")
 (target/'supervisor250.py').write_bytes((BASE/'supervisor245.py').read_bytes())
 replace(target/'supervisor250.py',"'entry245.py'", "'entry250_runtime.py'")
 # Checkpoint namespaces are isolated by the deployment directory/task/trial.
 parent=read(PARENT/'protocol249_SOURCE.json')
 finance=read(COMMON/'CONFIRMATION_FIRST_SIX_FINANCE_CONFIG.json')
 blueprint=read(BASE/'protocol225.json')
 blueprint.update(schema='EXP250-full-EnAgent-new-confirmation-SOURCE/1',execution_authorized=False,model_generation_authorized=False,
  scope_id='EXP250-EnAgent-complete-new-six-three-fresh-trials',root_protocol=str(PARENT/'protocol249_SOURCE.json'),
  root_protocol_sha256=sha(PARENT/'protocol249_SOURCE.json'),parent_source_seal=str(PARENT/'SOURCE_SEAL249.json'),
  parent_source_seal_SHA256=sha(PARENT/'SOURCE_SEAL249.json'),task_order=parent['task_order'],prepared_task_ids=[],
  finance_phase='Until0900ConfirmEnAgent24920261012',resume_lineage={},new_independent_full_parameter_group=True,
  old_candidate_or_paid_response_reuse=False,trial_id='PENDING_PREPARATION',trial_master_seed=None,
  shared_public249=str(PARENT/'method_sources/shared_public249.py'),shared_public249_SHA256=sha(PARENT/'method_sources/shared_public249.py'),
  shared_input249=str(PARENT/'method_sources/shared_input249.py'),shared_input249_SHA256=sha(PARENT/'method_sources/shared_input249.py'),
  public_source_bindings249=str(PARENT/'method_sources/PUBLIC_SOURCE_BINDINGS249.json'),public_source_bindings249_SHA256=sha(PARENT/'method_sources/PUBLIC_SOURCE_BINDINGS249.json'),
  public_test_scope_contract={'path':str(PARENT/'public_views_v2/COMMON_MASKED_PUBLIC_TEST_SCOPE249.json'),'sha256':'PENDING_ROOT_CURRENT_MASK_V2'},
  finance_core=str(ROOT/'工作区/1010-unified-six/finance_queue_remaining_SOURCE/continuous_core_v3.py'),
  finance_transport=str(ROOT/'工作区/1010-unified-six/finance_queue_remaining_SOURCE/completion_transport_v3.py'),
  finance_template=str(COMMON/'CONFIRMATION_ACCEPTED_C0_V1_FINANCE_CONFIG.json'),
  finance_template_sha256='PENDING_ROOT_NEW_REGISTRY',finance_config_SHA256=sha(COMMON/'CONFIRMATION_FIRST_SIX_FINANCE_CONFIG.json'),
  algorithm='Complete original EnAgent N3 coder200 tester+public prune normalize selector30 majority; public-only inputs; external original independent acceptance',
  deployment_version='Full-Author-Core-Flash-Windows-Declared-GO-NewTasks-ThreeFreshTrajectories',
  scientific_entry='entry250_runtime.py',scientific_supervisor='supervisor250.py',
  first_body_prospective_pin=None,initial_v3_public_source_observer_certificate=None,
  source_authority={'pin':'e839e559ac61bdd0e057c375dd1dee391fee797d','original_AST_methods_and_prompts_retained':True,
   'coder_max_steps':200,'selector_max_turn':30,'ensemble_wrapper_N':3,'paper3_repetitions_planned_not_yet_run':True},
  current_parameters_authority={'ensemble_wrapper_N':3,'coder_max_steps':200,'selector_max_turn':30,'tester_one_call':True,
   'core_internal_call_upper':691,'core_complete_funding_not_guaranteed':True},
  deadline={'hard_utc':'2099-01-01T00:00:00+00:00','no_new_utc':'2099-01-01T00:00:00+00:00',
   'scientific_deadline':None,'host_only_lease_limit_seconds':86400,
   'minimum_user_continuous_work_until_UTC':'2026-10-12T01:00:00+00:00','not_an_automatic_scientific_stop':True})
 blueprint['finance_transport_sha256']=sha(blueprint['finance_transport']);blueprint['finance_core_sha256']=sha(blueprint['finance_core'])
 blueprint['budget'].update(enagent_ensemble_size=3,enagent_coder_max_steps=200,enagent_selector_max_turn=30,
  enagent_coder_temperature=.5,enagent_selector_vote_max=3,declared_model_call_upper=691,max_model_calls_per_flow=2048,
  model_call_ceiling_is_operational_only=True,max_output_tokens_per_flow=None,max_calls_scientific=None,
  max_output_tokens_scientific=None,model_call_capacity_sufficient_for_N3_200_30=True,
  sufficient_for_worst_case_original_core=False,output_capacity_sufficient_for_N3_200_30=True)
 archival_names={'finance_registration','deployment_changes','local_recovery_deployment','implementation_authenticity',
  'shared_C0_qualification','root_shared_C0_qualification_pending','public_repository_testscope_pending',
  'common_six_C0_supplement_file','common_six_C0_supplement_sha256','common_six_C0_supplement_binding_pending',
  'finance_common_C0_configuration_pending','common_model_input_file','common_model_input_sha256',
  'public_goal_ordinary_oracle_contract','public_goal_ordinary_oracle_contract_sha256','future_science_starts_at_task',
  'future_science_task_ids','dataset_provenance_path','dataset_provenance_sha256','public_vs_independent_final_environment_SOURCE',
  'independent_final_product_dependency_paths','Root_common_two_hour_protocol_pending','common_two_hour_protocol_path',
  'common_two_hour_protocol_SHA256','common_C0_registry_task_order','independent_final_common_moto_dependencies_SOURCE',
  'Root_generated_isolation_qualifiers','Root_ordinary_capacity_qualification_pending','Root_external_final_source_review_pending',
  'source_parent_v8_seal_SHA256','source_parent_v8_protocol_SHA256','finance_SOURCE_READY','finance_SOURCE_READY_sha256',
  'cohort_title','excluded_this_window_pilot','calibration_order','parent_pilot_protocol_sha256','parent_pilot_source_seal_sha256',
  'closed_parent_science_result_sha256','closed_parent_SourceIOV4_science_result_sha256','resume_scientific_contract',
  'core_algorithm_exact_parent','global_resource_budgets_exact_parent','core_algorithm_budgets_exact_parent'}
 archive={}
 for name in list(blueprint):
  if name in archival_names or name.startswith(('old_','parent_','closed_parent_')) and name not in {'parent_source_seal','parent_source_seal_SHA256'}:
   archive[name]=blueprint.pop(name)
 save(HERE/'HISTORICAL_PROTOCOL_FIELDS_NOT_CURRENT250.json',{'historical_only_not_runtime_gates_or_current_method_claims':True,'fields':archive})
 blueprint['history_archive_source']=str(HERE/'HISTORICAL_PROTOCOL_FIELDS_NOT_CURRENT250.json')
 blueprint['history_archive_source_SHA256']=sha(HERE/'HISTORICAL_PROTOCOL_FIELDS_NOT_CURRENT250.json')
 blueprint['timing']={'original_T0':'actual forward supervisor lease_started_monotonic before worker/environment/clone/preparation',
  'actual_POST_T0':'separate observed provider dispatch timestamp; never resets original_T0',
  'same_trial_resume_preserves_GENESIS_original_T0_and_preparation_cost':True}
 blueprint['closure_flag']=str(HERE/'STOP_REQUESTED.json');blueprint['forward_closure_flag']=finance['forward_closure_flag']
 save(HERE/'PROTOCOL_BLUEPRINT250_SOURCE.json',blueprint)
 deps={p:h for p,h in read(BASE/'source_seal239.json')['dependencies'].items() if Path(p).suffix=='.py'}
 for path in [PARENT/'protocol249_SOURCE.json',PARENT/'SOURCE_SEAL249.json',PARENT/'method_sources/PUBLIC_SOURCE_BINDINGS249.json',
  PARENT/'method_sources/shared_public249.py',PARENT/'method_sources/shared_input249.py',COMMON/'CONFIRMATION_FIRST_SIX_FINANCE_CONFIG.json',
  Path(blueprint['native_scheduling_contract']),Path(blueprint['native_scheduling_helper'])]:deps[str(path)]=sha(path)
 for path,h in deps.items():
  if sha(path)!=h:raise RuntimeError('SOURCE_DEPENDENCY_DRIFT '+path)
 qa=[]
 for path in [*HERE.glob('*.py'),*target.glob('*.py'),*(target/'repro_guard225').glob('*.py')]:
  ast.parse(path.read_text('utf-8-sig'),filename=str(path));qa.append(str(path))
 save(HERE/'SOURCE_ONLY_PREPARATION250.json',{'SOURCE_ONLY':True,'copied_runtime_source_SHA256':copied,
  'copied_old_requests_candidates_checkpoints_results':0,'new_model_native_private_ledger':0,
  'AST_files_parsed':len(qa),'full_parameters':[3,200,30],'role_temperatures':[.5,0,.2],
  'prepared_body_and_grants_pending_current_C0':True,'per_task_trial_isolated_deployments':True})
 sources={str(p):sha(p) for p in [*HERE.glob('*.py'),*target.rglob('*.py'),HERE/'PROTOCOL_BLUEPRINT250_SOURCE.json',HERE/'SOURCE_ONLY_PREPARATION250.json',HERE/'HISTORICAL_PROTOCOL_FIELDS_NOT_CURRENT250.json']}
 save(HERE/'SOURCE_SEAL250.json',{'schema':'EXP250-source-only-runtime-seal/1','sources':sources,'dependencies':deps,
  'READY':False,'model_authorized':False,'native_authorized':False,'private_authorized':False,'finance_authorized':False})
 print(canonical({'SOURCE_ONLY':True,'runtime_sources':len(sources),'dependencies':len(deps),'model_native_private_ledger':0,'seal_SHA256':sha(HERE/'SOURCE_SEAL250.json')}))

if __name__=='__main__':main()

import ast,hashlib,json,shutil
from pathlib import Path
E=Path(__file__).resolve().parent;R=E.parents[3];OLD=R/'工作区/1010-ea10';D=R/'工作区/1011-ea12';W=R/'工作区/1010-unified-six';N=W/'shared_native_v11';FIN=W/'finance_v11';CP=W/'Root_COMPARISON_V3_PROTOCOL_SOURCE.json'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
assert not D.exists(),'NEW_EA12_ALREADY_EXISTS_NO_OVERWRITE'
assert sha(CP)=='6f6a52aa4e1c8c853f3e5df3cd967e6cd0eaff1dbb1cd1a151ec31181628551c';common=read(CP);shared=read(N/'SOURCE_READY_FALSE.json');assert sha(N/'SOURCE_READY_FALSE.json')==common['shared_READY_SHA256']=='545703d351e2057f876104795293ea8628b78214027dcaa29bd05aaa1d19e2b2'
for path,h in common['shared_native_sources'].items():assert sha(path)==h
cfg=FIN/'finance_config_science_common_C0_v4.json';assert sha(cfg)=='39f35b53449b1184367c25378775dd208659f4da3726552e785f6bebdc9920b4'
D.mkdir();parent=read(OLD/'source_seal239.json');sources={};copied=[]
for path,h in parent['sources'].items():
 src=Path(path);assert sha(src)==h
 if src.is_relative_to(OLD):
  target=D/src.relative_to(OLD);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target);sources[str(target)]=h;copied.append(target)
 else:sources[path]=h
shutil.copyfile(cfg,D/'finance_config239.json')
def edit(name,a,b):
 f=D/name;t=f.read_text('utf-8-sig');assert t.count(a)==1,(name,a,t.count(a));f.write_text(t.replace(a,b),'utf-8')
edit('flow_bounds239.py','maximum=7200','maximum=604800');edit('flow_bounds239.py','min(7200.','min(604800.')
edit('common166.py',"def closure_paths():return (read(TIME_AUTHORITY)['closure_flag'],E/'STOP_REQUESTED.json')","def closure_paths():\n p=read(TIME_AUTHORITY)\n return (p['closure_flag'],p['forward_closure_flag'],E/'STOP_REQUESTED.json')")
trusted='''"""Private trusted author-pruner context; actor tool parameters do not set it."""
from contextlib import contextmanager
from contextvars import ContextVar
_stage=ContextVar('EA239_trusted_author_native_stage',default=None)
def current():return _stage.get()
@contextmanager
def retained_PASS_regression(passing_set_verified):
 if passing_set_verified is not True:raise RuntimeError('AUTHOR_RETAINED_REGRESSION_REQUIRES_ACTUAL_C0_PASS_SET')
 token=_stage.set('full_retained_PASS_regression')
 try:yield
 finally:_stage.reset(token)
'''
(D/'trusted_pruner_stage239.py').write_text(trusted,'utf-8');sources[str(D/'trusted_pruner_stage239.py')]=sha(D/'trusted_pruner_stage239.py')
edit('control235.py','import copy','import copy\nfrom trusted_pruner_stage239 import current as trusted_native_stage')
edit('control235.py',"p=copy.deepcopy(p);p.update(native_execution_stage='ordinary_native',execution_authorized=True,model_generation_authorized=True,native_authorized=True,private_authorized=g.get('private_authorized') is True,once_private_authorized=g.get('once_private_authorized') is True)","p=copy.deepcopy(p);stage=trusted_native_stage()\n p.update(native_execution_stage=stage or 'ordinary_native',trusted_author_PASS_regression_phase=stage=='full_retained_PASS_regression',execution_authorized=True,model_generation_authorized=stage is None,native_authorized=True,private_authorized=False if stage else g.get('private_authorized') is True,once_private_authorized=False if stage else g.get('once_private_authorized') is True)")
edit('masked_public_bridge239.py',"    record=self.masked_native(root,extra,label='author_retained_public_repository_regression')", "    if self._masked_pool is None or any(self._masked_pool.get(node)!='passed' for node in extra):raise EngineeringError('AUTHOR_PRUNER_RETAINED_SET_NOT_ACTUAL_C0_PASS')\n    from trusted_pruner_stage239 import retained_PASS_regression\n    with retained_PASS_regression(True):\n     record=self.masked_native(root,extra,label='author_retained_public_repository_regression')")
edit('native_stage_limits239.py',' return ordinary'," if protocol.get('native_execution_stage')=='full_retained_PASS_regression':\n  if protocol.get('trusted_author_PASS_regression_phase') is not True or protocol.get('model_generation_authorized') is not False or protocol.get('private_authorized') is not False:raise RuntimeError('RETAINED_PASS_LIMIT_REQUIRES_TRUSTED_AUTHOR_NATIVE_PHASE')\n  return float(b['complete_pass_regression_timeout_seconds'])\n return ordinary")
proxy="from common166 import *\n_source=module('exp239_shared_public_native_v11',Path("+repr(str(N/'native_masked_public239.py'))+"))\nfor _name in ('load_scope','support_inventory','materialize_support','verify_actor','validate_selectors','assess','execute'):\n globals()[_name]=getattr(_source,_name)\n";(D/'native_masked_public239.py').write_text(proxy,'utf-8')
p=read(OLD/'protocol225.json');b=common['common_budget'];assert p['task_order']==common['task_order']
p.update(schema='EA239-complete-unified-six-v11-large-native-capacity-SOURCE/1',scope_id='UnifiedSixEnAgent23920261011_CompleteV11',masked_native_owner_root=str(D),root_protocol=str(CP),root_protocol_sha256=sha(CP),root_protocol_pending=False,root_shared_native_interface_pending=False,masked_native_guard_directory=common['masked_native_guard_directory'],masked_native_guard_source_SHA256=common['masked_native_guard_source_SHA256'],audit_trace_mode=common['audit_trace_mode'],shared_masked_native_module=str(N/'native_masked_public239.py'),shared_masked_native_module_sha256=sha(N/'native_masked_public239.py'),global_common_native_interface_version=11,shared_native_SOURCE_READY=str(N/'SOURCE_READY_FALSE.json'),shared_native_SOURCE_READY_SHA256=sha(N/'SOURCE_READY_FALSE.json'),shared_native_pure_validation=None,shared_native_pure_validation_SHA256=None,shared_native_SOURCE_manifest=shared['source_manifest'],shared_native_SOURCE_manifest_SHA256=shared['source_manifest_SHA256'],finance_transport=str(FIN/'completion_transport_common_C0_v4.py'),finance_core=str(FIN/'continuous_core_v3.py'),finance_template=str(cfg),common_model_input_file=str(FIN/'common_model_input_six.py'),common_feedback_codec_file=str(FIN/'common_public_feedback_codec.py'),forward_closure_flag=read(cfg)['forward_closure_flag'],deployment_version='EnAgent-ICSE2026-N3-coder200-selector30-temp0.5-CompleteV11-new-actual-six',old_EA10_partial_not_reused=True,new_scope_clock_not_old_EA10_clock=True,full_initial_pool_command_limit_seconds=14400,full_initial_pool_parent_limit_seconds=15000,complete_retained_PASS_regression_command_limit_seconds=14400,model_commands_cannot_select_internal_full_stage=True,new_initial_pool_qualification_pending=True,new_first_complete_scientific_pilot_pending=True,execution_authorized=False,model_generation_authorized=False,native_authorized=False,private_authorized=False,once_private_authorized=False)
for a,bkey in (('finance_transport','finance_transport_sha256'),('finance_core','finance_core_sha256'),('finance_template','finance_template_sha256'),('common_model_input_file','common_model_input_sha256'),('common_feedback_codec_file','common_feedback_codec_sha256')):p[bkey]=sha(p[a])
p['budget'].update(flow_wall_seconds=b['flow_wall_seconds_including_final'],native_timeout_seconds=b['per_native_timeout_seconds'],initial_full_pool_timeout_seconds=b['initial_full_pool_timeout_seconds'],initial_full_pool_parent_timeout_seconds=b['initial_full_pool_parent_timeout_seconds'],complete_pass_regression_timeout_seconds=b['complete_pass_regression_timeout_seconds'],shell_timeout_seconds=b['per_native_timeout_seconds'],final_reserve_seconds=b['final_reserve_seconds'],max_model_calls_per_flow=b['model_calls_total'],max_output_tokens_per_flow=b['output_tokens_total'],native_roots_total=b['product_native_roots_total'],all_owned_OS_roots_total=b['all_owned_OS_roots_total'],common_budget_source_sha256=sha(CP),root_common_budget_PENDING=False,enagent_coder_temperature=.5)
save(D/'protocol225.json',p)
# Own pure checker from V10 is revised to the new declared capacity, not evidence of a native run.
f=D/'validate_complete_source_v10.py';t=f.read_text('utf-8-sig').replace("'initial_full_pool_timeout_seconds':1800","'initial_full_pool_timeout_seconds':14400").replace('stage(q)==1800','stage(q)==14400').replace("phase_limit_1800","phase_limit_14400").replace("(7200)==7200","(604800)==604800").replace("(7201,float","(604801,float").replace("(7200,0)==7200","(604800,0)==604800").replace("(100,7200,100+7200-1500)==5800","(100,604800,100+604800-1500)==603400").replace("(7000+300,7200","(604700+300,604800").replace("'flow_wall_seconds':7200","'flow_wall_seconds':604800").replace('7200_valid_7201','604800_valid_604801');f.write_text(t,'utf-8')
for path in list(sources):sources[path]=sha(path)
for path in sources:
 if Path(path).suffix=='.py':ast.parse(Path(path).read_text('utf-8-sig'),filename=path)
deps={path:h for path,h in parent['dependencies'].items() if '/shared_native_v10/' not in path.replace('\\','/') and '/finance/' not in path.replace('\\','/')}
deps.update(common['shared_native_sources'])
for path,h in read(FIN/'SOURCE_READY_FALSE.json')['sources'].items():deps[path]=h
for path,h in deps.items():assert sha(path)==h
inputs={path:h for path,h in parent['input_sources'].items() if '/shared_native_v10/' not in path.replace('\\','/') and Path(path).name not in ('PURE_SOURCE_VALIDATION.json','SIX_TASK_COMMANDS_FALSE.json','COMPLETE_V10_SOURCE_RATIONALE.txt')}
inputs.update({str(OLD/'source_seal239.json'):sha(OLD/'source_seal239.json'),str(OLD/'protocol225.json'):sha(OLD/'protocol225.json'),str(CP):sha(CP),str(N/'SOURCE_READY_FALSE.json'):sha(N/'SOURCE_READY_FALSE.json'),str(N/'SOURCE_MANIFEST.json'):sha(N/'SOURCE_MANIFEST.json'),str(FIN/'SOURCE_READY_FALSE.json'):sha(FIN/'SOURCE_READY_FALSE.json'),str(cfg):sha(cfg)})
for path,h in inputs.items():assert sha(path)==h
command=[];py=str(R/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe')
for task in p['task_order']:
 base=[py,'-B',str(D/'supervisor_completion239.py'),'--task',task];command.append({'task':task,'initial_pool_after_Root_native_only_grant':base+['--public-pool'],'complete_science_after_Root_full_pool_admission_and_grant':base})
save(D/'SIX_TASK_COMMANDS_FALSE.json',{'all_grants_false':True,'no_automatic_next_task_or_launch':True,'commands':command})
# Temporary SOURCE seal only; finalize after own pure tests, with every grant false.
save(D/'source_seal239.json',{'schema':'EA239-complete-v11-SOURCE-provisional/1','sources':sources,'dependencies':deps,'input_sources':inputs,'protocol_SHA256':sha(D/'protocol225.json'),'own_pure_validation_pending':True,'no_old_pool_or_science_state_copied':True})
g={'scope_id':p['scope_id'],'finance_phase':p['finance_phase'],'protocol_sha256':sha(D/'protocol225.json'),'source_seal_sha256':sha(D/'source_seal239.json'),'mechanical_authorized':False,'full_public_pool_authorized':False,'execution_authorized':False,'model_generation_authorized':False,'native_authorized':False,'private_authorized':False,'once_private_authorized':False,'finance_authorized':False,'allowed_task_ids':[],'allowed_through_index':-1}
save(D/'root_grant239.json',g);save(D/'mechanical_grant239_v3.json',g)
print(json.dumps({'owner':str(D),'sharedV11_bound':True,'financeV11_bound':True,'source_bindings':len(sources),'dependencies':len(deps),'inputs':len(inputs),'all_grants_false':True,'native_or_model_execution':False},ensure_ascii=False))

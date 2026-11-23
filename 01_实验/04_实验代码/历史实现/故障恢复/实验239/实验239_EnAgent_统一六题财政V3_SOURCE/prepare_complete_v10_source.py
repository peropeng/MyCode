import ast,hashlib,json,shutil
from pathlib import Path
E=Path(__file__).resolve().parent; V=E.parents[3]/'工作区/1010-ea9'; D=E.parents[3]/'工作区/1010-ea10'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
assert not D.exists(),'NEW_COMPLETE_OWNER_ALREADY_EXISTS';D.mkdir()
s=read(V/'source_seal239.json');mapping={};copied=[]
for path,h in s['sources'].items():
 src=Path(path);assert sha(src)==h
 if src.is_relative_to(V):
  dst=D/src.relative_to(V);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);copied.append(dst);mapping[str(dst)]=h
 else:mapping[path]=h
shutil.copyfile(V/'finance_config239.json',D/'finance_config239.json')
def edit(name,a,b):
 f=D/name;t=f.read_text('utf-8-sig');assert a in t,(name,a);f.write_text(t.replace(a,b),'utf-8')
edit('controller225.py','temperature=.7','temperature=spec[\'temperature\']')
edit('worker_v2_225.py',"'temperature':.7","'temperature':limits['enagent_coder_temperature']")
edit('worker_v2_225.py',"'coder':.7","'coder':limits['enagent_coder_temperature']")
edit('worker_v2_225.py',"limits.get('shell_timeout_seconds',45)","limits['shell_timeout_seconds']")
edit('worker_v2_225.py',"limits.get('final_reserve_seconds',90)","limits['final_reserve_seconds']")
edit('finite_environment239.py',"b.get('final_reserve_seconds',90)","b['final_reserve_seconds']")
edit('finite_environment239.py',"success,within=final_classification(full['elapsed_seconds'],p['budget']['flow_wall_seconds']", "pool=load_cache(self.task_id,p)\n            scientific_elapsed=full['elapsed_seconds']\n            logical_elapsed=scientific_elapsed+pool['cache_qualification_elapsed_seconds']\n            success,within=final_classification(logical_elapsed,p['budget']['flow_wall_seconds']")
# local import must precede the budget decision above.
edit('finite_environment239.py',"success,within=final_classification(logical_elapsed", "success,within=final_classification(logical_elapsed")
f=D/'finite_environment239.py';t=f.read_text('utf-8');t=t.replace("pool=load_cache(self.task_id,p)\n            scientific_elapsed", "from public_pool_cache239 import load_cache\n            pool=load_cache(self.task_id,p)\n            scientific_elapsed",1)
t=t.replace("            from public_pool_cache239 import load_cache\n            pool=load_cache(self.task_id,p)\n            full['pre_science_pool_elapsed_seconds']", "            full['pre_science_pool_elapsed_seconds']",1)
t=t.replace("full['scientific_phase_elapsed_seconds']=full['elapsed_seconds']","full['scientific_phase_elapsed_seconds']=scientific_elapsed")
t=t.replace("full['logical_total_flow_elapsed_seconds']=full['elapsed_seconds']+pool['cache_qualification_elapsed_seconds']","full['logical_total_flow_elapsed_seconds']=logical_elapsed\n            full['elapsed_seconds']=logical_elapsed\n            full['flow_total_includes_C0_pool_once']=True")
f.write_text(t,'utf-8')
edit('control235.py',"PHASE=read(PROTOCOL)['finance_phase'];MECHANICAL=False;MECHANICAL_NAMESPACE='probe'", "PHASE=read(PROTOCOL)['finance_phase'];MECHANICAL=False;FULL_PUBLIC_POOL=False;MECHANICAL_NAMESPACE='probe'")
edit('control235.py','def start_mechanical():\n global MECHANICAL','def start_mechanical(full_public_pool=False):\n global MECHANICAL,FULL_PUBLIC_POOL')
edit('control235.py','source_gate(g);MECHANICAL=True',"if full_public_pool and g.get('full_public_pool_authorized') is not True:raise RuntimeError('ROOT_INITIAL_FULL_POOL_STAGE_GRANT_REQUIRED')\n source_gate(g);MECHANICAL=True;FULL_PUBLIC_POOL=bool(full_public_pool)")
edit('control235.py',"native_namespace=MECHANICAL_NAMESPACE+'/n')", "native_namespace=MECHANICAL_NAMESPACE+'/n',native_execution_stage='full_initial_public_pool' if FULL_PUBLIC_POOL else 'ordinary_native')")
edit('control235.py',"source_gate(g)\n if p.get('root_protocol_pending')", "source_gate(g)\n if p.get('root_protocol_pending')")
# Source-gate bindings are mandatory for both native-only and scientific phases.
edit('control235.py',"require_open();p=read(PROTOCOL)","require_open();p=read(PROTOCOL)\n if p.get('root_shared_native_interface_pending') or p['budget'].get('root_common_budget_PENDING'):raise RuntimeError('ROOT_COMPLETE_V10_NATIVE_OR_BUDGET_REVIEW_PENDING')\n if sha(p['root_protocol'])!=p['root_protocol_sha256']:raise RuntimeError('ROOT_COMPLETE_V10_COMMON_PROTOCOL_DRIFT')")
edit('control235.py',"p=copy.deepcopy(p);p.update(execution_authorized=True,model_generation_authorized=True", "p=copy.deepcopy(p);p.update(native_execution_stage='ordinary_native',execution_authorized=True,model_generation_authorized=True")
edit('mechanical_public_pool239.py','control235.start_mechanical();', 'control235.start_mechanical(full_public_pool=True);')
edit('mechanical_public_pool239.py',"'trusted_goal_ordinary_C0_repeat':0", "'trusted_goal_ordinary_C0_repeat':0,'complete_default_pytest_discovery':True,'qualification_stage':'full_initial_public_pool','ordinary_command_limit_seconds':p['budget']['native_timeout_seconds'],'initial_pool_command_limit_seconds':p['budget']['initial_full_pool_timeout_seconds']")
edit('supervisor_completion239.py','if mechanical:start_mechanical()', 'if mechanical:start_mechanical(full_public_pool=args.public_pool)')
edit('supervisor_completion239.py','seconds=300 if mechanical else finite_seconds(b[\'flow_wall_seconds\'])', "seconds=(b['initial_full_pool_parent_timeout_seconds'] if args.public_pool else 300) if mechanical else finite_seconds(b['flow_wall_seconds'])")
limits='''"""Trusted controller-stage limits; actor labels never increase a timeout."""
def limit(protocol):
 b=protocol['budget'];ordinary=float(b['native_timeout_seconds'])
 if protocol.get('native_execution_stage')=='full_initial_public_pool':
  if protocol.get('model_generation_authorized') is not False or protocol.get('private_authorized') is not False:raise RuntimeError('FULL_POOL_REQUIRES_NATIVE_ONLY_ROOT_PHASE')
  return float(b['initial_full_pool_timeout_seconds'])
 return ordinary
'''
(D/'native_stage_limits239.py').write_text(limits,'utf-8');mapping[str(D/'native_stage_limits239.py')]=sha(D/'native_stage_limits239.py')
edit('native_executor224.py','from contextlib import contextmanager','from contextlib import contextmanager\nfrom native_stage_limits239 import limit as native_stage_limit')
edit('native_executor224.py',"_HELD.NATIVE_TIMEOUT_SECONDS=p['budget']['native_timeout_seconds']", "_HELD.NATIVE_TIMEOUT_SECONDS=native_stage_limit(p)")
edit('native_executor224.py',"min(timeout,p['budget']['native_timeout_seconds'],left)","min(timeout,native_stage_limit(p),left)")
# Preserve every-call SHA admission checks, but decode the immutable large pool once.
edit('public_pool_cache239.py','from common166 import *','from common166 import *\nfrom functools import lru_cache\n\n@lru_cache(maxsize=6)\ndef _decode_bound_entry(path,content_sha256):\n if sha(path)!=content_sha256:raise RuntimeError(\'PUBLIC_POOL_CACHE_DECODE_SHA_DRIFT\')\n return read(path)')
edit('public_pool_cache239.py',"entry=read(path);ref=p['shared_pack_references'][task];record=entry['full_public_pool_record']", "entry=_decode_bound_entry(str(path),binding['sha256']);ref=p['shared_pack_references'][task];record=dict(entry['full_public_pool_record'])")
edit('public_pool_cache239.py',"if not (record.get('known') is True", "if entry.get('qualification_stage')!='full_initial_public_pool' or entry.get('complete_default_pytest_discovery') is not True:raise RuntimeError('NEW_COMPLETE_DEFAULT_INITIAL_POOL_REQUIRED')\n if not (record.get('known') is True")
p=read(V/'protocol225.json');p.update(schema='EA239-complete-unified-six-prospective-v10-SOURCE/1',scope_id='UnifiedSixEnAgent23920261010_CompleteV10',masked_native_owner_root=str(D),output_namespace='f',native_namespace='n',root_protocol_pending=True,root_shared_native_interface_pending=True,execution_authorized=False,model_generation_authorized=False,native_authorized=False,private_authorized=False,once_private_authorized=False,finance_phase='UnifiedSixEnAgent23920261010_CompleteV10',deployment_version='EnAgent-ICSE2026-N3-coder200-selector30-YAMLtemp0.5-CompleteV10',algorithm='full N3 generation; complete original default pytest C0 PASS pool; author tester exclusion, pruning/allfail fallback, normalization/dedup, full tools selector3votes/majority/fallback; once common final acceptance',full_initial_pool_precompute_original_interface=True,full_initial_pool_precompute_cost_in_flow_once=True,all_six_new_actual_runs_required=True,old_records_read_only_no_continuation=True,scope_root_guard_SHA_pending=True,complete_pytest_default_discovery_pending_Root_helper=True)
p['budget'].update(flow_wall_seconds=7200,native_timeout_seconds=180,initial_full_pool_timeout_seconds=1800,initial_full_pool_parent_timeout_seconds=2100,shell_timeout_seconds=180,final_reserve_seconds=180,enagent_coder_temperature=.5,root_common_budget_PENDING=True,sufficient_for_worst_case_original_core=False,full_core_parameter_capacity_vs_guaranteed_runtime_distinguished=True)
save(D/'protocol225.json',p)
for f in copied:
 if f.suffix=='.py':ast.parse(f.read_text('utf-8-sig'),filename=str(f))
for path in list(mapping):mapping[path]=sha(path)
save(D/'SOURCE_INTEGRATION_PENDING_FALSE.json',{'schema':'EA239-complete-v10-source-awaiting-Root/1','physical_owner':str(D),'parent':str(V),'sources_prepared':mapping,'all_grants_false':True,'model_native_private_import_execution_now':False,'Root_inputs_required':['shared_native_v10 helper/guard/runner paths and SHA','Root_COMPARISON_V2_PROTOCOL.json and SHA/common budget','current continuous finance bindings no reset'],'protocol_pending':True,'all_six_task_order':p['task_order'],'changed_local_sources':['controller225.py','worker_v2_225.py','finite_environment239.py','control235.py','mechanical_public_pool239.py','supervisor_completion239.py','native_stage_limits239.py','native_executor224.py','public_pool_cache239.py'],'shared_helper_guard_not_modified':True})
g={'schema':'EA239-complete-v10-root-grant-FALSE/1','scope_id':p['scope_id'],'finance_phase':p['finance_phase'],'protocol_sha256':sha(D/'protocol225.json'),'source_seal_sha256':None,'mechanical_authorized':False,'full_public_pool_authorized':False,'execution_authorized':False,'model_generation_authorized':False,'native_authorized':False,'private_authorized':False,'once_private_authorized':False,'finance_authorized':False,'allowed_task_ids':[],'allowed_through_index':-1}
save(D/'root_grant239.json',g);save(D/'mechanical_grant239_v3.json',g)
commands=[]
for task in p['task_order']:
 common=[str(p['root_protocol']).split('/ROOT_SIX_SOURCE_PROTOCOL_FALSE')[0]]
 py=str(E.parents[3]/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe');base=[py,'-B',str(D/'supervisor_completion239.py'),'--task',task]
 commands.append({'task':task,'full_initial_pool_after_Root_grant':base+['--public-pool'],'complete_science_after_Root_cache_admission_and_grant':base})
save(D/'SIX_TASK_COMMANDS_FALSE.json',{'all_grants_false':True,'no_launch_script_or_automatic_next_task':True,'commands':commands})
(E/'CURRENT_COMPLETE_V10_RECOVERY.txt').write_text('Agent /root/enagent2026 parent/root. Active task COMPLETE new unified6EA source. D='+str(D)+', parent V9='+str(V)+'. Rootuserlatest authorised analyse/fix/optimise/rerun; prior singlefix90/UNKNOWNfinal notnewbound; no agent native/API/private/Gold/download. Need bind Root upcoming shared_native_v10 helper+guard+runner SHA and Root_COMPARISON_V2_PROTOCOL/budget+continuous9.10cap finance. SOURCE prepared local controller YAMLtemp.5, N3/200/30 same, phases Rootonly180ordinary1800fullpool2100parent7200flow, native_stage_limits no actorlabelescalation, cache Rootsealed/STOP/cost+roots sameflow once plus largeJSONdecode memo, total resultelapsed=pool+science. Rootowns sharedjournal O(n²)performancefix/prepend/masked ancestor+hypothesis output/defaultpytest discover; do not editshared. No source_seal final untilRoot interface arrives. Pending SOURCE_INTEGRATION_PENDING_FALSE; SIX_TASK_COMMANDS_FALSE containsallfixed6 pool+sciencecommands; bothgrantsfalse. All copied AST checked; no imports product/method/nat/api. Need pure validation testsstagepolicy cachebudget and Roothelper defaultselector then finalseal.\n','utf-8')
print(json.dumps({'physical_owner':str(D),'copied':len(copied),'local_prepared':len(mapping),'all_grants_false':True,'Root_integration_pending':True}))

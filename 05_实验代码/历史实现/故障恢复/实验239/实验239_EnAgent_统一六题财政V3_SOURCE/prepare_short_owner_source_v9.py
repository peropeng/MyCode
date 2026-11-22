import ast,hashlib,json,shutil
from pathlib import Path
E=Path(__file__).resolve().parent; V=E/'runtime_v8_SOURCE'; ROOT=E.parents[3]; D=ROOT/'工作区/1010-ea9'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
assert not D.exists(),'NEW_SHORT_OWNER_ALREADY_EXISTS';D.mkdir()
parent=read(V/'source_seal239.json');new_sources={};copied=[]
for path,h in parent['sources'].items():
 src=Path(path);assert sha(src)==h
 if src.is_relative_to(V):
  dst=D/src.relative_to(V);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);copied.append(dst);new_sources[str(dst)]=h
 else:new_sources[path]=h
for name in ('finance_config239.json',):shutil.copyfile(V/name,D/name)
mp=D/'mechanical_public_pool239.py';text=mp.read_text('utf-8-sig');anchor="control235.MECHANICAL_NAMESPACE='pre_science_pool_'+args.task+'_'+str(os.getpid())";assert text.count(anchor)==1;text=text.replace(anchor,"control235.MECHANICAL_NAMESPACE='pool_'+str(p['task_order'].index(args.task))");mp.write_text(text,'utf-8');new_sources[str(mp)]=sha(mp)
p=read(V/'protocol225.json');old_owner=p['masked_native_owner_root'];p.update(schema='EA239-short-physical-owner-complete-pool-SOURCE/9',scope_id='UnifiedSixEnAgent23920261010_ShortPhysicalOwnerV9_SOURCE',masked_native_owner_root=str(D),output_namespace='f',native_namespace='n',root_protocol_pending=True,execution_authorized=False,model_generation_authorized=False,native_authorized=False,private_authorized=False,once_private_authorized=False,prospective_transport_deployment_only=True,initial_public_pool_core_unchanged=True,unstarted_tasks_common_short_namespace='pool_<fixed_task_order_index>/f and /n; new independent owner, no algorithm or public test selector changes',old_v8_owner_not_mutated=old_owner,source_parent_v8_seal_SHA256=sha(V/'source_seal239.json'),source_parent_v8_protocol_SHA256=sha(V/'protocol225.json'))
assert p['budget']['native_timeout_seconds']==90
save(D/'protocol225.json',p)
for f in copied:
 if f.suffix=='.py':ast.parse(f.read_text('utf-8-sig'),filename=str(f))
for group in ('dependencies','input_sources'):
 for path,h in parent.get(group,{}).items():assert sha(path)==h
seal={'schema':'EA239-short-physical-owner-source-seal/9','sources':new_sources,'dependencies':parent['dependencies'],'input_sources':{**parent.get('input_sources',{}),str(V/'source_seal239.json'):sha(V/'source_seal239.json'),str(V/'protocol225.json'):sha(V/'protocol225.json')},'protocol_SHA256':sha(D/'protocol225.json'),'old_v8_source_parent':str(V),'new_short_physical_owner':str(D),'source_changes':{'mechanical_public_pool239.py':'physical output namespace changes from task+pid to fixed common task_order index only'},'all_other_copied_sources_byte_identical':True,'execution_happened':False}
save(D/'source_seal239.json',seal)
g={'schema':'EA239-short-physical-owner-root-grant-FALSE/9','scope_id':p['scope_id'],'finance_phase':p['finance_phase'],'protocol_sha256':sha(D/'protocol225.json'),'source_seal_sha256':sha(D/'source_seal239.json'),'mechanical_authorized':False,'execution_authorized':False,'model_generation_authorized':False,'native_authorized':False,'private_authorized':False,'once_private_authorized':False,'finance_authorized':False,'allowed_task_ids':[],'allowed_through_index':-1,'root_only_grant_owner':True}
save(D/'root_grant239.json',g);save(D/'mechanical_grant239_v3.json',g)
# Paths are prospective; no actor, C0 export, tester, or process is constructed here.
paths={}
for i,task in enumerate(p['task_order']):
 out=D/('pool_'+str(i))/'f'/task/'ENAGENT_C0_FULL_PUBLIC_POOL_NO_MODEL'/'masked_public_native/0001_initial_full_repository_PASS_pool'
 paths[task]={'prospective_native_output':str(out),'native_output_characters':len(str(out)),'native_guard_ready_characters':len(str(out/'masked_guard_ready.json')),'prospective_native_PYCACHEPREFIX_characters':len(str(out/'pycache'))}
assert all(v['native_PYCACHEPREFIX_characters']<260 for v in [])
for path,h in new_sources.items():assert sha(path)==h
selected=p['shared_pack_references']['conan-io__conan-14397'];scope=read(p['public_test_scope_contract']['path']);row=next(t for t in scope['tasks'] if t['task_id']=='conan-io__conan-14397')
public_files=row['public_test_py_files_SHA256'];selected_paths=sorted(x for x in public_files if Path(x).name.startswith('test_') or Path(x).name.endswith('_test.py'))
ready={'schema':'EA239-short-physical-owner-complete-pool-SOURCE-READY-FALSE/9','short_physical_owner':str(D),'task':'conan-io__conan-14397','source_seal_SHA256':sha(D/'source_seal239.json'),'protocol_SHA256':sha(D/'protocol225.json'),'parent_seal_SHA256':sha(V/'source_seal239.json'),'copy_AST_and_SHA_only':True,'source_bindings':len(new_sources),'copied_source_files':len(copied),'dependency_bindings':len(seal['dependencies']),'input_bindings':len(seal['input_sources']),'all_copied_except_namespace_byte_identical':True,'initial_public_PASS_pool_full_native_core':str(mp),'no_test_removed_or_changed':True,'public_scope_py_files':len(public_files),'same_v8_all_default_test_file_selectors':len(selected_paths),'same_existing_C0_pack':selected,'same_test_scope_SHA256':p['public_test_scope_contract']['sha256'],'same_guard_source':p['masked_native_guard_directory'],'native_timeout_seconds':90,'owned_parent_timeout_seconds':300,'uniform_prospective_output_lengths':paths,'root_native_only_command_after_review':[str(ROOT/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'),'-B',str(D/'supervisor_completion239.py'),'--task','conan-io__conan-14397','--public-pool'],'grant_paths':[str(D/'mechanical_grant239_v3.json'),str(D/'root_grant239.json')],'all_grants_false':True,'science_enabled':False,'API_private_Gold_download':False,'actor_C0_not_materialized_or_imported_now':True,'source_only_no_execution':True,'Root_admission_pending':True,'path_shortening_is_future_deployment_not_root_cause_claim':True}
save(D/'SOURCE_READY_FALSE.json',ready)
(E/'CURRENT_SHORT_OWNER_RECOVERY.txt').write_text('Agent /root/enagent2026 parent/root. Task ONLY future short physical output full C0 masked PASS-pool qualification SOURCE for original T6 conan-14397, <=90native <=300parent 0API/private/Gold. D='+str(D)+'. Parent exact v8 seal copied own source only; one source modification universal namespace pool_<fixed6index>, protocol only prospective owner/outputnames, allcore/guard/Job/lane/input/models/role unchanged. All grantsfalse, no C0/materialization/import/native executed. Ready D/SOURCE_READY_FALSE.json; source_seal239.json/protocol225.json. Root sole actualgrant/finance/executor. Oldscience/diags unchanged. Diag1 shortout161 actualsuccess, diag2 longout282 anddiag3 shortcache152 bothpre-phase native60timeout STOP, nofurtherdiagnosticchain; RootcauseUNCONFIRMED. No custom guard permissions, no API. ROOT_SOURCE evaluation next independent nativeonce after review, then known/unknown truthful.\n','utf-8')
print(json.dumps({'owner':str(D),'READY_SHA256':sha(D/'SOURCE_READY_FALSE.json'),'seal_SHA256':sha(D/'source_seal239.json'),'protocol_SHA256':sha(D/'protocol225.json'),'copied':len(copied),'bindings':len(new_sources),'deps':len(seal['dependencies']),'inputs':len(seal['input_sources']),'T6':paths['conan-io__conan-14397'],'all_false':True},ensure_ascii=False))

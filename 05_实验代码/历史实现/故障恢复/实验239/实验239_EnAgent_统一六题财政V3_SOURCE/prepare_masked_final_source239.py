"""SOURCE-only contract/config/body proposal and seal, never an execution grant."""
import ast,copy,datetime,hashlib,importlib.util,json,pathlib,shutil,sys
E=pathlib.Path(__file__).resolve().parent;R=E.parents[3];H=R/'工作区/1010-unified-six';F=H/'finance';sys.dont_write_bytecode=True
read=lambda p:json.loads(pathlib.Path(p).read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def save(p,v):
 p=pathlib.Path(p).resolve();assert p.is_relative_to(E)
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8',newline='')
p=read(E/'protocol225.json');cfgpath=F/'finance_config_common_C0_v4.json';cfg=read(cfgpath)
assert cfg['model_generation_authorized'] is False and p['finance_phase']=='UnifiedSixEnAgent23920261010'
assert cfg['common_tasks']==p['task_order'] and p['finance_phase'] in cfg['phases']
assert cfg['common_C0_supplement_registry_SHA256']==p['common_six_C0_supplement_sha256']
shutil.copyfile(cfgpath,E/'finance_config239.json');assert sha(cfgpath)==sha(E/'finance_config239.json')
scopepath=H/'COMMON_MASKED_PUBLIC_TEST_SCOPE.json';permission=H/'COMMON_EXISTING_PUBLIC_ORACLE_PERMISSION.json'
p.update(finance_template=str(cfgpath),finance_template_sha256=sha(cfgpath),finance_common_C0_configuration_pending=False,
 public_repository_testscope_pending=False,public_test_scope_contract={'path':str(scopepath),'sha256':sha(scopepath),'authority':'Root masked existing repository common READ/TEST permission'},
 public_goal_ordinary_oracle_contract=str(permission),public_goal_ordinary_oracle_contract_sha256=sha(permission),
 masked_native_owner_root=str(E),masked_native_guard_directory=str(E/'masked_public_guard'),
 actual_masked_collection_and_current_C0_PASS_pool_pending=True,
 original_public_goal_ordinary_trusted_oracle_unchanged=True,original_unmasked_reader_or_hidden_Git_blob_access=False,
 private_final_selected_once_and_never_actor_feedback=True)
assert p['root_protocol_pending'] is True
save(E/'protocol225.json',p)
sys.path.insert(0,str(E));import native_masked_public239 as native
audit=[]
for task in p['task_order']:
 row=native.load_scope(p,task);pack=read(p['shared_pack_references'][task]['path']);business=pack['c0_business_paths_sha256']
 supports=native.support_inventory(row,business)
 audit.append({'task':task,'public_test_py_files':len(row['public_test_py_files_SHA256']),'all_public_view_files':len(row['all_public_view_files_SHA256']),'C0_business_files':len(business),'immutable_support_files':len(supports),'original_omitted_module':row['conservative_complete_file_omission'],'C0_business_overwrite_forbidden':True,'root_public_view_SHA256_all_verified':True,'actual_collection_ABI_Job_PASS_pool':None,'real_native_POST_private':0})
save(E/'MASKED_PUBLIC_SCOPE_SOURCE_AUDIT239.json',{'schema':'EnAgent239-masked-public-source-projection-audit/1','tasks':audit,'scope_contract_SHA256':sha(scopepath),'public_oracle_permission_SHA256':sha(permission),'root_actual_C0_not_repeated':True,'actual_masked_native_qualification_pending':True})
task=p['task_order'][0];ref=p['shared_pack_references'][task];pack=read(ref['path'])
sys.path.insert(0,str(pathlib.Path(p['shared_publicpack_module']).parent))
spec=importlib.util.spec_from_file_location('_ea239_public_sourcebody_only',p['shared_publicpack_module']);pub=importlib.util.module_from_spec(spec);spec.loader.exec_module(pub)
contract=next(n for n in ast.parse((E/'actor_tool_contract_v3.py').read_text('utf-8')).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ACTOR_TOOL_CONTRACT' for t in n.targets))
contract=ast.literal_eval(contract.value)
issue=pub.render(pack)+'\n'+contract+'\nResolve the observed current public failure and preserve already passing ordinary behavior. The working repository is /workspace/repo. Complete business source and the approved immutable public test/support view are available through the original author tools. Run approved public tests, declared observer public nodes, or independent generated scripts; original unmasked tests and external Git blobs remain unavailable.'
body=read(E/'SOURCE_ONLY_FIRST_BODY_SCOPE242_MOTO5406.json');body['messages'][1]['content']="[Project root path]:\n/workspace/repo\n\n[Problem statement]: We're currently solving the following issue within our repository. Here's the issue text:\n"+issue+'\n'
save(E/'SOURCE_ONLY_MASKED_PUBLIC_BASE_BODY_MOTO5406.json',body)
sys.path.insert(0,str(F));import common_model_input_six as common
full=common.inject(body,cfg,task);save(E/'SOURCE_ONLY_MASKED_PUBLIC_ROOT_V4_FULL_BODY_MOTO5406.json',full)
sp=importlib.util.spec_from_file_location('_ea239_sourcebounds_without_factory',p['finance_transport']);provider=importlib.util.module_from_spec(sp);sp.loader.exec_module(provider)
bounds=provider.bounds(full,cfg)
proof={'schema':'EnAgent239-masked-public-root-common-v4-source-proposal/1','status':'COMPLETE_SOURCE_DERIVED_FIRST_BODY_NOT_ACTUAL_CAPTURE','task':task,'body_file':str(E/'SOURCE_ONLY_MASKED_PUBLIC_ROOT_V4_FULL_BODY_MOTO5406.json'),'body_file_SHA256':sha(E/'SOURCE_ONLY_MASKED_PUBLIC_ROOT_V4_FULL_BODY_MOTO5406.json'),'body_canonical_SHA256':hashlib.sha256(canonical(full).encode()).hexdigest(),'body_canonical_bytes':len(canonical(full).encode()),'messages':len(full['messages']),'source_bounds':bounds,'complete_author_system_and_original_tool_schema_retained':True,'same_Root_common_v4_supplement_exactly_once':True,'Root_finance_config_SHA256':sha(cfgpath),'permission_SHA256':sha(permission),'public_masked_scope_SHA256':sha(scopepath),'method_actual_body_ABI_Job_scope_pool':None,'actual_native_API_private_finance_IO':0,'finance_factory_constructed':False,'author_N3_200_30_unchanged':True}
save(E/'SOURCE_ONLY_MASKED_PUBLIC_BODY_PROVENANCE239.json',proof)
seal=read(E/'source_seal239.json')
for file in E.glob('*.py'):seal['sources'][str(file)]=sha(file)
for file in (E/'masked_public_guard').glob('*.py'):seal['sources'][str(file)]=sha(file)
for key in ['sources','dependencies','input_sources']:
 for file in seal[key]:seal[key][file]=sha(file)
seal['dependencies'][str(cfgpath)]=sha(cfgpath)
seal['input_sources'][str(scopepath)]=sha(scopepath);seal['input_sources'][str(permission)]=sha(permission)
seal.update(at_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),masked_public_test_support_contract_bound=True,Root_common_v4_finance_config_pending=False,Root_common_v4_sole_injector=True,actual_masked_native_qualification_pending=True)
save(E/'source_seal239.json',seal)
for name in ['root_grant239.json','mechanical_grant239_v3.json']:
 g=read(E/name)
 assert all(g.get(k) is False for k in ['execution_authorized','model_generation_authorized','native_authorized','private_authorized','once_private_authorized','mechanical_authorized'])
 g.update(protocol_sha256=sha(E/'protocol225.json'),source_seal_sha256=sha(E/'source_seal239.json'));save(E/name,g)
ready=read(E/'SOURCE_READY239_COMPLETION_V3_FALSE.json')
ready.update(status='FINAL_SOURCE_BOUND_ROOT_COMMON_V4_MASKED_PUBLIC_SCOPE_ALL_FALSE_ACTUAL_MECHANICAL_PENDING',source_seal_sha256=sha(E/'source_seal239.json'),protocol_sha256=sha(E/'protocol225.json'),runtime_sources=seal['sources'],dependencies=seal['dependencies'],input_sources=seal['input_sources'],finance_common_C0_configuration_pending=False,finance_config_file=str(E/'finance_config239.json'),finance_config_SHA256=sha(E/'finance_config239.json'),Root_finance_config_source=cfgpath.as_posix(),public_test_scope_contract=p['public_test_scope_contract'],public_goal_ordinary_oracle_contract={'path':str(permission),'sha256':sha(permission)},masked_public_view_source_audit=audit,source_complete_first_model_body=proof,actual_masked_public_collection_leafs_C0_PASS_pool=None,Root_actual_shared_C0_not_repeated=True,method_new_actual_C0_ABI_job_scope_firstbody=None)
ready['source_boundary_fixtures'].update(sha256=sha(E/'SOURCE_BOUNDARY_FIXTURES239.json'),cases=18,status='PASS')
ready['masked_public_source_boundary_fixtures']={'path':str(E/'MASKED_PUBLIC_SOURCE_FIXTURES239.json'),'sha256':sha(E/'MASKED_PUBLIC_SOURCE_FIXTURES239.json'),'cases':10,'status':'PASS'}
ready['mechanical_next_command']=str(E/'supervise239.py')+' --task getmoto__moto-5406 --masked-public'
ready['mechanical_not_started_no_grant']=True
save(E/'SOURCE_READY239_COMPLETION_V3_FALSE.json',ready)
assert all(sha(file)==h for key in ['sources','dependencies','input_sources'] for file,h in seal[key].items())
print(json.dumps({'seal':sha(E/'source_seal239.json'),'protocol':sha(E/'protocol225.json'),'READY':sha(E/'SOURCE_READY239_COMPLETION_V3_FALSE.json'),'cfg':sha(E/'finance_config239.json'),'body_canonical':proof['body_canonical_SHA256'],'bodybytes':proof['body_canonical_bytes'],'sources':len(seal['sources']),'deps':len(seal['dependencies']),'inputs':len(seal['input_sources']),'scope_files_all_verified':True,'all_grants_false':True,'actual_native_API_private_financeIO':0},ensure_ascii=False))

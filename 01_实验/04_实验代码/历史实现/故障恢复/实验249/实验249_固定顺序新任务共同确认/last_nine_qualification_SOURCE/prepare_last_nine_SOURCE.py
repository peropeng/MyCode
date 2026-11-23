"""Fixed last nine qualification SOURCE. No model, product, private or masking execution."""
import ast,copy,difflib,hashlib,json,re,sys
from pathlib import Path
sys.dont_write_bytecode=True
N=Path(__file__).resolve().parent;Q=N.parent
R=Path('D:/Code/毕设/graduate-thesis-experiments')
I=Q/'next_six_qualification_SOURCE'
C=Q/'next_six_current_C0_SOURCE'
TASKS=['getmoto__moto-5980','python__mypy-15155','getmoto__moto-5516','conan-io__conan-14397','getmoto__moto-4972','getmoto__moto-5587','pydantic__pydantic-8965','dask__dask-8484','Project-MONAI__MONAI-4109']
P=R/'结论/20261009_复盘再实验/新确认集与共同预算_前瞻.json'
S23=R/'工作区/1008-2320-baseline-main/baseline2025_common_readiness/new_public_contract_preflight/expanded_observed_failure23_manifest.json'
CONTROLLER=R/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'
INPUTS={};SOURCES={};DIFF=[];CHECKS=[]
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def canon(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canon(v).encode()).hexdigest()
def ref(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def raw(p,b):
 p=Path(p).resolve()
 if not p.is_relative_to(N):raise RuntimeError('LAST_NINE_SOURCE_WRITE_SCOPE')
 if p.exists():
  if p.read_bytes()!=b:raise RuntimeError('LAST_NINE_SOURCE_ALREADY_FROZEN:'+str(p))
 else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
def write(p,v):raw(p,(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode())
def check(name,condition):
 if not condition:raise RuntimeError('LAST_NINE_CHECK:'+name)
 CHECKS.append(name)
def pin(p,expected=None,source=False):
 p=Path(p).resolve();h=sha(p)
 if expected is not None and h!=expected:raise RuntimeError('LAST_NINE_SOURCE_REFERENCE_DRIFT:'+str(p))
 (SOURCES if source else INPUTS)[str(p)]=h
 return ref(p)
def replace(s,a,b,count=1):
 if s.count(a)!=count:raise RuntimeError('LAST_NINE_MECHANICAL_ANCHOR:'+a[:100])
 return s.replace(a,b)
def copy_source(name,origin):
 b=Path(origin).read_bytes();raw(N/name,b);pin(origin,source=True)
def source(name,s,origin):
 ast.parse(s,filename=name);raw(N/name,s.encode());pin(origin,source=True)
 DIFF.append(''.join(difflib.unified_diff(Path(origin).read_text('utf-8-sig').splitlines(True),s.splitlines(True),fromfile=str(origin),tofile=str(N/name))))
def prepare_sources():
 s=(C/'common_current_C0.py').read_text('utf-8-sig')
 start=s.index('TASKS = ');end=s.index('CONTROLLER = ',start)
 s=s[:start]+'TASKS = '+repr(TASKS)+'\nFIRST_TWO = TASKS  # compatibility alias, fixed slots13--21 only\nIDENTITY_ROOT = E\n'+s[end:]
 s=replace(s,"if self.action not in ('materialize', 'current_C0'): raise RuntimeError('NEXT_C0_NO_IDENTITY_OR_METHOD_EXECUTION')","if self.action not in ('identity', 'materialize', 'current_C0'): raise RuntimeError('LAST_NINE_QUALIFICATION_ACTIONS_ONLY')")
 source('common_last_nine249.py',s,C/'common_current_C0.py')
 origin=C/'native_cwd_R2_SOURCE/native_current_C0_cwd_R2.py';s=origin.read_text('utf-8-sig')
 s=replace(s,'sys.path.insert(0, str(Path(__file__).resolve().parent.parent))','sys.path.insert(0, str(Path(__file__).resolve().parent))')
 s=replace(s,'from common_current_C0 import *','from common_last_nine249 import *')
 s=replace(s,"expected_path = REVISION_HOME / 'SOURCE_SEAL.json'","expected_path = REVISION_HOME / 'SOURCE_SEAL249.json'")
 s=replace(s,"choices=('current_C0',)","choices=('identity', 'current_C0')")
 s=replace(s,"out = E / 'qualification' / args.task / 'current_C0'","out = E / 'qualification' / args.task / args.stage")
 source('native_last_nine249.py',s,origin)
 origin=C/'materialize_current_C0_ROOT_ONLY.py';s=origin.read_text('utf-8-sig')
 s=replace(s,'from common_current_C0 import *','from common_last_nine249 import *')
 s=replace(s,'    dest.mkdir()\n','    dest.mkdir(parents=True)\n')
 source('materialize_last_nine_ROOT_ONLY.py',s,origin)
 origin=C/'audit_public_mask_SOURCE.py';s=origin.read_text('utf-8-sig')
 s=replace(s,'from common_current_C0 import *','from common_last_nine249 import *')
 source('audit_public_mask_SOURCE.py',s,origin)
 for name,origin in [('physical_identity249.py',C/'physical_identity249.py'),('native_capacity249_ROOT_V11_SOURCE.py',C/'native_capacity249_ROOT_V11_SOURCE.py'),('windows_native_cwd.py',C/'native_cwd_R2_SOURCE/windows_native_cwd.py')]:copy_source(name,origin)
 check('samefile cwd helper exact known revision',sha(N/'windows_native_cwd.py')=='54793a815151c89cb61f35cde0e5feac13956b503c144680d175c43c8a79390e')
 before=ast.parse((C/'native_cwd_R2_SOURCE/native_current_C0_cwd_R2.py').read_text('utf-8-sig'));after=ast.parse((N/'native_last_nine249.py').read_text('utf-8-sig'))
 for name in ('load_jobs','stopped','parent_member','supervise','load_original_probe','identity_prefix','wrap_native_argv','verify_measured_identity','run_identity','run_current_C0'):
  a=next(x for x in before.body if isinstance(x,ast.FunctionDef) and x.name==name);b=next(x for x in after.body if isinstance(x,ast.FunctionDef) and x.name==name)
  check('unchanged qualified runtime function '+name,ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False))
 raw(N/'EXACT_REUSE_DIFF.patch',''.join(DIFF).encode())
def file_ref_or_gap(path,label,gaps,expected=None,hash_contents=True):
 path=Path(path).resolve()
 if not path.is_file():gaps.append({'kind':'MISSING_FILE','label':label,'path':str(path)});return {'path':str(path),'sha256':None,'exists':False}
 if not hash_contents:return {'path':str(path),'exists':True,'content_not_read':True}
 h=sha(path)
 if expected is not None and h!=expected:gaps.append({'kind':'SHA256_DRIFT','label':label,'path':str(path),'expected':expected,'actual':h})
 else:INPUTS[str(path)]=h
 return {'path':str(path),'sha256':h,'exists':True}
def dependencies(python,package,gaps):
 site=python.parent.parent/'Lib/site-packages'
 roots=[site];queue=[site];seen=set();pointers=[];distribution=[];dynamic=[]
 if package=='moto':queue.append(R/'工作区/1010-unified-six/shared_runtime_dependencies_moto311/site-packages')
 while queue:
  root=queue.pop(0).resolve()
  if root in seen:continue
  seen.add(root)
  if not root.is_dir():gaps.append({'kind':'MISSING_DEPENDENCY_DIRECTORY','path':str(root)});continue
  roots.append(root)
  for p in sorted(root.glob('*.pth')):
   p_ref=pin(p);text=p.read_text('utf-8-sig');targets=[];unsupported=[]
   for line in text.splitlines():
    line=line.strip()
    if not line or line.startswith('#'):continue
    if line.startswith(('import ','import\t')):
     try:
      tree=ast.parse(line)
      calls=[v for v in ast.walk(tree) if isinstance(v,ast.Call)]
      for call in calls:
       if isinstance(call.func,ast.Attribute) and call.func.attr in ('addsitedir','append','insert') and call.args and isinstance(call.args[-1],ast.Constant) and isinstance(call.args[-1].value,str):
        target=Path(call.args[-1].value)
        if target.is_absolute():targets.append(target)
        else:unsupported.append(line)
       else:unsupported.append(line)
     except SyntaxError:unsupported.append(line)
    else:targets.append((root/line).resolve())
   pointers.append({'source':p_ref,'resolved_directory_targets':[str(t) for t in targets],'executed_in_SOURCE':False})
   queue.extend(targets)
   if unsupported:dynamic.append({'source':p_ref,'dynamic_pth_bound_but_not_executed':True,'unresolved_statement_count':len(set(unsupported))})
  for p in sorted(root.glob('*.dist-info/METADATA')):
   text=p.read_text('utf-8-sig',errors='replace');name=next((s[6:] for s in text.splitlines() if s.startswith('Name: ')),None);version=next((s[9:] for s in text.splitlines() if s.startswith('Version: ')),None)
   refs={}
   for file in ('METADATA','WHEEL','RECORD','INSTALLER','direct_url.json'):
    q=p.parent/file
    if q.is_file():refs[file]=pin(q)
   distribution.append({'name':name,'version':version,'distribution_directory':str(p.parent),'metadata_files':refs})
 names={str(x['name']).lower().replace('_','-') for x in distribution}
 required={'moto':['pytest','boto3','botocore'],'mypy':['pytest'],'conans':['pytest'],'pydantic':['pytest','pydantic-core'],'dask':['pytest','numpy'],'monai':['pytest','torch','numpy']}[package]
 missing=[n for n in required if n not in names]
 return {'logical_site_packages':str(site),'resolved_existing_dependency_roots':sorted(set(str(p) for p in roots if p.is_dir())),'pth_bindings':pointers,'distribution_metadata':distribution,'minimum_direct_dependency_metadata_not_found':missing,'dynamic_pth_static_only':dynamic,'all_distribution_metadata_bound_not_every_installed_package_file_hashed':True,'actual_import_ABI_compatibility_unrun':True,'no_import_install_download_or_forward':True}
def prepare_assets():
 plan=read(P);reg=read(S23)
 check('exact original plan last9 natural slots13--21',plan['new_main_order'][12:21]==TASKS and len(plan['new_main_order'])==21)
 pin(P);pin(S23)
 current_binding_path=R/'工作区/1008-2320-exp224-flash-common/实验/实验224_二十三题Flash完整共同恢复比较/data/selected_task_bindings.json'
 current_bindings={v['task_id']:v for v in read(current_binding_path)['tasks']};pin(current_binding_path)
 pin(N/'SOURCE_DRAFT_CORRECTION.json')
 old_exclusion={'schema':'EXP249-last-nine-prior-qualification-exclusions-retained/1','conan-io__conan-14397':{'prior_exclusion':'Current collection / qualification mismatch; uniformly excluded in the prior fixed-five comparison.','authority':'Root explicit task instruction and cumulative report section on remaining16; no old private or repair outcome consulted.','original_exclusion_retained':True,'current_status':'UNKNOWN_UNRUN_NEW_QUALIFICATION','new_source_or_old_record_is_not_current_qualification':True,'fresh_identity_trusted_mask_full_original_G_O_guard_and_STOP_required':True},'development_exposure':{'python__mypy-15155':'Known Exp248 mechanism development issue; tag retained.','getmoto__moto-5516':'Known Exp248 mechanism development issue; tag retained.','getmoto__moto-5980':'Member of earlier exposed fixed-five issue set; no old outcome inherited.'},'issue_count_and_repeats_not_merged':True}
 write(N/'PRIOR_EXCLUSION_METADATA_SOURCE.json',old_exclusion)
 rows=[];audits=[]
 for slot,task in enumerate(TASKS,13):
  gaps=[];original=R/'实验/实验241_Agentless新确认集21_生成测试ScopeV2/candidate'/task/'public_contract.json'
  item=next(x for x in reg['tasks'] if x['task_id']==task)
  if not original.is_file():
   rows.append({'task_id':task,'natural_slot_one_based':slot,'plan21_index_zero_based':slot-1,'public_contract':str(N/'contracts'/task/'public_contract.json'),'public_contract_SHA256':None,'source_assets_available':False,'current_C0_status':'UNKNOWN_MISSING_ORIGINAL_PUBLIC_CONTRACT','current_C0_qualified':False})
   audits.append({'task_id':task,'hard_asset_gaps':[{'kind':'MISSING_ORIGINAL_CONTRACT','path':str(original)}]});continue
  c=read(original);target=N/'contracts'/task/'public_contract.json';raw(target,original.read_bytes())
  check(task+' exact contract task and original G/O declarations',c['task_id']==task and c['public_target_nodes']==item['public_goal_nodes'] and c['ordinary_nodes']==item['public_ordinary_nodes'])
  original_ref=pin(original);target_ref=pin(target)
  pack=file_ref_or_gap(c['pack'],'public_pack',gaps,c['pack_sha256'])
  source_inventory=file_ref_or_gap(c['source_inventory_reference'],'source_inventory_reference',gaps,c['source_inventory_reference_sha256'])
  registry_ref=file_ref_or_gap(c['registry'],'original_public_registry',gaps,c['registry_sha256'])
  py=Path(c['logical_product_python']).resolve();cfg=py.parent.parent/'pyvenv.cfg'
  py_ref=file_ref_or_gap(py,'logical_product_python',gaps);cfg_ref=file_ref_or_gap(cfg,'pyvenv_cfg',gaps)
  cv={k.strip():v.strip() for line in cfg.read_text('utf-8-sig').splitlines() if '=' in line for k,v in [line.split('=',1)]} if cfg.is_file() else {}
  base=Path(cv.get('executable') or str(Path(cv.get('home','MISSING'))/'python.exe')).resolve()
  base_ref=file_ref_or_gap(base,'configured_base_candidate',gaps)
  selected=current_bindings[task]
  check(task+' current public source inventory and normalized task agree',Path(selected['saved_source_inventory']).resolve()==Path(c['source_inventory_reference']).resolve() and Path(selected['task_path']).resolve()==Path(c['source_inventory_reference']).resolve().parent)
  legacy_manifest=(Path(item['binding']['task_path'])/'task_manifest.json').resolve()
  manifest=(Path(selected['task_path'])/'task_manifest.json').resolve()
  manifest_ref=file_ref_or_gap(manifest,'Root_original_manifest_metadata_opaque_hash_only',gaps)
  # Only declared business source is byte-checked here. All original test/support
  # bodies remain unread; Root's trusted materializer verifies those later.
  root=Path(c['template']).resolve();business_actual={}
  if not root.is_dir():gaps.append({'kind':'MISSING_CURRENT_C0_TEMPLATE','path':str(root)})
  for rel,expected in c['c0_business_paths_sha256'].items():
   p=root/rel
   if not p.is_file():gaps.append({'kind':'MISSING_BUSINESS_SOURCE','path':str(p)});continue
   actual=sha(p);business_actual[rel]=actual
   if actual!=expected:gaps.append({'kind':'CURRENT_BUSINESS_SOURCE_DRIFT','path':str(p),'expected':expected,'actual':actual})
  missing_template=[rel for rel in c['template_inventory'] if not (root/rel).is_file()]
  if missing_template:gaps.append({'kind':'MISSING_TEMPLATE_ASSETS_METADATA_ONLY','relative_paths':missing_template})
  frozen_root=Path(c['frozen_public_test_root']).resolve()
  missing_frozen=[rel for rel in c['frozen_inventory'] if not (frozen_root/rel).is_file()]
  if missing_frozen:gaps.append({'kind':'MISSING_ORIGINAL_FROZEN_ASSETS_METADATA_ONLY','relative_paths':missing_frozen})
  harness_refs={}
  for p,expected in c['harness_sources'].items():
   check(task+' harness source is helper only '+Path(p).name,Path(p).name in ('qualify.py','sitecustomize.py','qualification_plugin.py'))
   if Path(p).is_file() and sha(p)==expected:harness_refs[p]=pin(p,expected,source=True)
   else:file_ref_or_gap(p,'original_harness_source',gaps,expected)
  deps=dependencies(py,c['package'],gaps)
  depfile=N/'dependency_metadata'/ (task+'.json');write(depfile,deps);pin(depfile)
  businessfile=N/'business_inventory'/ (task+'.json')
  write(businessfile,{'task_id':task,'template_root':str(root),'expected_from_public_contract':c['c0_business_paths_sha256'],'actual_business_SHA256':business_actual,'original_test_or_support_body_read':False,'exact_business_inventory':business_actual==c['c0_business_paths_sha256']});pin(businessfile)
  row={'task_id':task,'natural_slot_one_based':slot,'plan21_index_zero_based':slot-1,'public_contract':str(target),'public_contract_SHA256':target_ref['sha256'],'original_public_contract':original_ref,'original_C0_template':str(root),'c0_business_inventory_SHA256':c['c0_business_inventory_sha256'],'current_business_inventory':ref(businessfile),'business_paths_count':len(c['c0_business_paths_sha256']),'pack':pack,'source_inventory_reference':source_inventory,'original_registry':registry_ref,'source_pin':c.get('source_pin'),'public_goal_nodes':c['public_target_nodes'],'public_ordinary_nodes':c['ordinary_nodes'],'original_frozen_G_O_source_root':str(frozen_root),'original_frozen_inventory_SHA256':c['frozen_inventory_sha256'],'original_harness':c['harness'],'original_harness_sources_SHA256':c['harness_sources'],'logical_product_python':str(py),'logical_product_python_SHA256':py_ref['sha256'],'pyvenv_cfg':str(cfg),'pyvenv_cfg_SHA256':cfg_ref['sha256'],'configured_python_version':cv.get('version'),'configured_base_candidate':str(base),'configured_base_candidate_SHA256':base_ref['sha256'],'configured_path_is_not_actual_physical_identity':True,'runtime_dependency_metadata':ref(depfile),'Root_only_original_isolation_manifest_path':str(manifest),'Root_only_manifest_metadata_reference':manifest_ref,'Root_manifest_metadata_only_opaque_SHA_not_parsed':True,'historically_exposed':True,'known_mechanism_development':task in ('python__mypy-15155','getmoto__moto-5516'),'prior_fixed_five_exposure':task in TASKS[:3],'prior_uniform_qualification_exclusion_retained':task=='conan-io__conan-14397','old_qualification_or_method_result_not_inherited':True,'identity_qualified':False,'public_mask_qualified':False,'current_C0_qualified':False,'current_C0_status':'UNKNOWN_UNRUN_CURRENT_QUALIFICATION','method_outcome':None,'source_assets_available':not gaps,'model_native_private_finance':0}
  rows.append(row)
  row.update(current_public_task_binding_reference=ref(current_binding_path),legacy_source23_manifest_path=str(legacy_manifest),legacy_source23_manifest_exists=legacy_manifest.is_file(),manifest_binding_rule='Existing manifest in task_path of current public selected_task_bindings, required equal to parent of exact public_contract source_inventory_reference; no manifest is synthesized.',canonical_manifest_differs_from_legacy_registry_path=manifest!=legacy_manifest)
  audits.append({'task_id':task,'natural_slot_one_based':slot,'hard_asset_gaps':gaps,'identity_entry_files_present':py.is_file() and cfg.is_file() and base.is_file(),'business_inventory_exact':business_actual==c['c0_business_paths_sha256'],'original_template_files_count':len(c['template_inventory']),'missing_template_relative_paths':missing_template,'original_frozen_files_count':len(c['frozen_inventory']),'missing_frozen_relative_paths':missing_frozen,'original_test_bodies_not_read_or_hashed':True,'original_manifest_metadata_opaque_ref':manifest_ref,'dependency_metadata':ref(depfile),'dependency_metadata_missing_names':deps['minimum_direct_dependency_metadata_not_found'],'runtime_or_dependency_imports_not_executed':True,'pending_gates':['Root actual zero-product identity and parent STOP','Root new trusted original-test masking stage','Full original G/O current C0 observation with exact coverage and guard','Published masked auxiliary channel complete PASS and unchanged C0','Parent full STOP; Root adjudication, no inherited qualification'],'prior_exclusion':old_exclusion['conan-io__conan-14397'] if task=='conan-io__conan-14397' else None})
 write(N/'TASK_BINDINGS249_SOURCE.json',{'schema':'EXP249-fixed-last-nine-public-task-bindings-source/1','tasks':rows,'private_results_or_original_test_bodies_read':False,'manifest_metadata_opaque_hash_only':True,'historical_method_outcomes_not_consulted':True})
 write(N/'ASSET_GAPS_AND_PENDING_GATES_SOURCE.json',{'schema':'EXP249-last-nine-per-slot-assets-source/1','task_order':TASKS,'slots_retained':9,'current_qualified':0,'tasks':audits,'no_native_or_test_import':True,'unknown_not_zero_or_replacement':True})
 protocol={'schema':'EXP249-last-nine-current-qualification-source/1','task_order':TASKS,'natural_slots_one_based':list(range(13,22)),'selection_rule':plan['selection_rule'],'source_plan21':ref(P),'source_pool23':ref(S23),'old_first_six_and_next_six_source_protocols_registries_unknown_slots_and_clocks_unchanged':True,'stages':['identity','trusted_mask_Root_only','current_original_G_O_and_masked_channel'],'same_actual_source_and_original_G_O_for_all_three_methods':True,'current_C0_qualified_count':0,'max_identity_OS_roots_per_task':1,'max_original_G_O_native_per_task':1,'max_masked_channel_native_per_task':1,'qualification_scientific_repair_result':False,'no_new_method_trial_or_science_T0':'Qualification cost remains separate; no old clock reset','native_parent_active_lifetime_limits':[8,24],'V11_uniform_native_seconds':300,'V5_four_shared_slots_MONAI_serial_unchanged':True,'mypy_unmapped_data_support_conservative_omission_unchanged':True,'prior_Conan_exclusion_metadata':ref(N/'PRIOR_EXCLUSION_METADATA_SOURCE.json'),'source_assets_gaps':ref(N/'ASSET_GAPS_AND_PENDING_GATES_SOURCE.json'),'source_only':True,'READY':False,'root_authorized':False,'native_authorized':False,'model_authorized':False,'private_execution_authorized':False,'finance_authorized':False,'training_or_forward_authorized':False}
 write(N/'protocol249_SOURCE.json',protocol)
 return rows,audits
def seal(rows,audits):
 for p in (R/'工作区/1011-our19/native_executor242_prospective.py',R/'工作区/1011-our19/progress_guard240.py',R/'工作区/1002-exp129-expanded-baselines/实验/实验129_扩展基线与恢复证据/executor/run.py',R/'工作区/1010-unified-six/native_four_slots_v5_SOURCE.py',R/'工作区/1010-unified-six/precise_product_bootstrap_v9_SOURCE.py'):pin(p,source=True)
 descriptor=R/'工作区/1010-unified-six/shared_native_v14_certificate_complete/SOURCE_READY_FALSE.json';d=read(descriptor);pin(descriptor)
 for p,h in d['sources'].items():pin(p,h,source=True)
 for p in (CONTROLLER,CONTROLLER.parent.parent/'pyvenv.cfg',R/'工作区/1010-unified-six/ROOT_COMMON_NATIVE_SCHEDULING_V5_FOUR_SOURCE.json',I/'SOURCE_SEAL249.json',C/'SOURCE_SEAL249.json',C/'native_cwd_R2_SOURCE/SOURCE_SEAL.json'):pin(p)
 for p in sorted(N.glob('*.py')):ast.parse(p.read_text('utf-8-sig'),filename=str(p));SOURCES[str(p)]=sha(p)
 for name in ('protocol249_SOURCE.json','TASK_BINDINGS249_SOURCE.json','ASSET_GAPS_AND_PENDING_GATES_SOURCE.json','PRIOR_EXCLUSION_METADATA_SOURCE.json','EXACT_REUSE_DIFF.patch'):pin(N/name)
 validation={'status':'PASS','checks':CHECKS,'check_count':len(CHECKS),'task_count':9,'hard_asset_gap_counts':{x['task_id']:len(x['hard_asset_gaps']) for x in audits},'original_shared_native_functions_AST_unchanged':True,'native_capacity_identity_cwd_byte_exact':True,'all_original_tests_bodies_unread':True,'Root_manifest_opaque_metadata_SHA_only':True,'new_mask_identity_current_G_O_executions':0,'model_API_GET_native_private_finance_training_forward_download':0,'old_sources_and_protocols_written':False,'single_new_source_directory':str(N)}
 write(N/'SOURCE_VALIDATION.json',validation);pin(N/'SOURCE_VALIDATION.json')
 sp=N/'SOURCE_SEAL249.json';write(sp,{'schema':'EXP249-fixed-last-nine-qualified-chain-source-seal/1','task_order':TASKS,'sources_SHA256':SOURCES,'public_inputs_SHA256':INPUTS,'qualification_current_count':0,'actual_calls':0,'Root_only_original_mask_and_oracle':True,'no_dependency_install_or_download':True})
 py_map={str(p):sha(p) for p in sorted(N.glob('*.py'))};commands=[]
 for row in rows:
  task=row['task_id'];c=read(row['public_contract']) if Path(row['public_contract']).is_file() else None
  base={'schema':'EXP249-last-nine-exact-Root-action-false/1','root_authorized':False,'native_authorized':False,'model_authorized':False,'private_execution_authorized':False,'finance_authorized':False,'trusted_original_test_source_read_authorized':False,'task_ids':[task],'lease_end_UTC':None,'root_stop_paths':[str(Q/'ROOT_STOP_REQUESTED.json')],'protocol_SHA256':sha(N/'protocol249_SOURCE.json'),'source_seal_SHA256':sha(sp),'controller_launch_python':str(CONTROLLER),'controller_launch_SHA256':sha(CONTROLLER),'source_only':True,'Root_mask_v2_sources_SHA256':py_map,'native_cwd_revision_source_seal':ref(sp),'source_assets_available':row['source_assets_available'],'current_C0_qualified':False,'prior_Conan_uniform_exclusion_not_overwritten':True}
  ident={**base,'action':'identity','max_identity_OS_roots':1,'no_business_import_or_pytest':True,'identity_entry_SHA256':sha(N/'native_last_nine249.py'),'parent_owned_job_name':'RootExp249_LastNine_identity_'+task.replace('-','_')}
  ip=N/'grant_templates'/(task+'.identity.false.json');write(ip,ident)
  manifest=row.get('Root_only_manifest_metadata_reference',{'path':None,'sha256':None})
  mask={**base,'action':'materialize','max_materialized_tasks':1,'trusted_masking_inputs':{task:{'manifest_path':manifest['path'],'manifest_SHA256':manifest['sha256']}},'Root_must_reverify_manifest_metadata_before_new_trusted_stage':True}
  mp=N/'grant_templates'/(task+'.materialize.false.json');write(mp,mask)
  ng={**base,'action':'current_C0','max_original_G_O_native':1,'max_masked_ordinary_native':1,'trusted_original_G_O_oracle_execution_authorized':False,'parent_owned_job_name':'RootExp249_LastNine_C0_'+task.replace('-','_'),'current_identity_receipt_SHA256':None,'current_identity_parent_STOP_SHA256':None,'masked_scope_SHA256':None,'exact_G_O_nodes':list(dict.fromkeys(c['public_target_nodes']+c['ordinary_nodes'])) if c else None,'current_process_clock_policy':'ROOT_ORIGINAL_CLOCK_EXPLICITLY_ADMITTED','common_precise_clock_contract':None,'Root_current_process_precise_clock_admitted':False,'masked_channel_qualification_nodes':None,'Root_auxiliary_channel_only_original_O_retained':False,'after_identity_and_mask_binding_required':True}
  gp=N/'grant_templates'/(task+'.current_C0.pending_gates.false.json');write(gp,ng)
  commands.append({'task_id':task,'slot':row['natural_slot_one_based'],'identity_false':ref(ip),'materialize_false':ref(mp),'current_C0_pending_gates_false':ref(gp),'source_assets_available':row['source_assets_available'],'identity_argv':[str(CONTROLLER),'-X','utf8','-B',str(N/'native_last_nine249.py'),'--stage','identity','--task',task,'--root-grant',str(N/'ROOT_RELEASES'/(task+'.identity.actual.json'))],'Root_materialize_argv':[str(CONTROLLER),'-X','utf8','-B',str(N/'materialize_last_nine_ROOT_ONLY.py'),'--task',task,'--root-grant',str(N/'ROOT_RELEASES'/(task+'.materialize.actual.json'))],'bind_after_identity_mask_argv':[str(CONTROLLER),'-X','utf8','-B',str(N/'bind_current_C0_after_gates_ROOT_ONLY.py'),'--task',task],'current_C0_argv':[str(CONTROLLER),'-X','utf8','-B',str(N/'native_last_nine249.py'),'--stage','current_C0','--task',task,'--root-grant',str(N/'ROOT_RELEASES'/(task+'.current_C0.actual.json'))]})
 ready={'schema':'EXP249-last-nine-all-stage-closed-source-ready/1','source_seal':ref(sp),'task_order':TASKS,'commands':commands,'actual_calls':0,'model_native_private_finance_authorized':False,'Root_stage_sign_fields':{'identity':['root_authorized=true','native_authorized=true','finite lease_end_UTC; source_only=false','all model/private/finance/trusted_source_read remain false'],'materialize':['root_authorized=true','trusted_original_test_source_read_authorized=true','reverify bound original manifest metadata SHA; finite lease; source_only=false','native/model/private_execution/finance remain false'],'current_C0':['only use AFTER_IDENTITY_MASK_BOUND_FALSE','root_authorized/native_authorized/trusted_original_G_O_oracle_execution_authorized=true','finite lease; source_only=false; original clock explicitly admitted','model/private_execution/finance/trusted_original_source_read remain false']},'completion_criteria':['Fresh exact physical identity and complete identity parent STOP','Root trusted masking preserves all exact business bytes and withholds Goal/private test bodies','Full original G/O valid guard, at least one original Goal fail and every original O pass','One result-independent selected masked channel completely known PASS','All candidate/parent owned Jobs STOP and C0 unchanged','Unknown/collection failure retains original slot with method_outcome=None; no replacements or old outcome inheritance'],'known_pending_assets':ref(N/'ASSET_GAPS_AND_PENDING_GATES_SOURCE.json'),'prior_Conan_exclusion':ref(N/'PRIOR_EXCLUSION_METADATA_SOURCE.json'),'root_masks_not_executed_by_SOURCE':True,'no_old_registry_or_protocol_or_clock_change':True}
 rp=N/'SOURCE_READY_FALSE.json';write(rp,ready)
 print(canon({'status':'LAST_NINE_ALL_STAGES_SOURCE_CLOSED','source_seal':ref(sp),'manifest':ref(rp),'tasks':TASKS,'checks':len(CHECKS),'source_count':len(SOURCES),'input_count':len(INPUTS),'gaps':validation['hard_asset_gap_counts'],'actual':0}))
if __name__=='__main__':
 prepare_sources();rows,audits=prepare_assets();seal(rows,audits)


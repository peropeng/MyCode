"""Finalize a single forward six-task SOURCE. No runtime qualification or science."""
import argparse,ast,copy,datetime,hashlib,json,runpy,sys
from pathlib import Path

E=Path(__file__).resolve().parent;D=E.parent.parent/'a9';R=D.parents[2];U=R/'工作区/1010-unified-six';OLD=E/'runtime_v8_SOURCE'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def save(p,x):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--finance-directory',required=True);parser.add_argument('--finance-config',required=True);parser.add_argument('--closure-flag',required=True);args=parser.parse_args()
 finance=Path(args.finance_directory).resolve();cfg=Path(args.finance_config).resolve();closure=Path(args.closure_flag).resolve()
 if finance.parent!=U or cfg.parent not in (U/'finance',finance) or closure.parent!=U:raise ValueError('ROOT_FINANCE_OR_CLOSURE_SCOPE')
 root_protocol=U/'Root_COMPARISON_V2_PROTOCOL.json';root=read(root_protocol);shared=U/'shared_native_v10';shared_ready=shared/'SOURCE_READY_FALSE.json'
 if sha(root_protocol)!='fcfe3bff4428c963d665c09dc455febdaee1fb7d533ce763303fc7abe7901316':raise ValueError('ROOT_FORWARD_PROTOCOL_SHA_DRIFT')
 if sha(shared_ready)!=root['shared_READY_SHA256']:raise ValueError('ROOT_SHARED_READY_SHA_DRIFT')
 for path,expected in root['shared_native_sources'].items():
  if sha(path)!=expected:raise ValueError('ROOT_SHARED_SOURCE_SHA_DRIFT '+path)
 oldseal=read(OLD/'SOURCE_SEAL.json');seal={'schema':'AL9-forward-complete-six-source-seal/1','author_pin':oldseal['author_pin'],'sources':{},'inputs':{},'forward_root_protocol_SHA256':sha(root_protocol),'all_old_science_clocks_and_outputs_untouched':True}
 for path,h in oldseal['sources'].items():
  if Path(path).is_relative_to(OLD) or 'shared_native_v6_SOURCE' in path or Path(path).is_relative_to(U/'finance'):continue
  if sha(path)!=h:raise ValueError('PREEXISTING_EXTERNAL_DEPENDENCY_DRIFT '+path)
  seal['sources'][path]=h
 for path,h in oldseal['inputs'].items():
  if Path(path).is_relative_to(OLD) or 'ROOT_SHARED_NATIVE_V6_NARROW_QUALIFICATION' in path or Path(path).is_relative_to(U/'finance'):continue
  if sha(path)!=h:raise ValueError('PREEXISTING_PUBLIC_INPUT_DRIFT '+path)
  seal['inputs'][path]=h
 seal['sources'].update(root['shared_native_sources'])
 finance_ready=finance/'SOURCE_READY_FALSE.json';finance_binding=read(finance_ready)
 if sha(cfg)!='ec74019c783340bd824c876de706c641e1382d846fe66d3976bdc7ed7a2f0b09' or finance_binding['config_SHA256']!=sha(cfg):raise ValueError('ROOT_FINANCE_FINAL_CONFIG_SHA_DRIFT')
 for path,expected in finance_binding['sources'].items():
  if sha(path)!=expected:raise ValueError('ROOT_FINANCE_FINAL_SOURCE_SHA_DRIFT '+path)
  seal['sources'][path]=expected
 for path in (root_protocol,shared_ready,cfg,finance_ready,finance/'PRIMARY_PRICING_VERIFICATION.json'):seal['inputs'][str(path)]=sha(path)
 # Only a new private-owned AL adapter points to the copied Root finance runtime.
 transport=D/'flash_transport241.py';text=transport.read_text('utf-8');start=text.index('FISCAL=');end=text.index('\nroot=module',start)
 transport.write_text(text[:start]+'FISCAL=Path('+repr(str(finance))+')'+text[end:],'utf-8')
 entry=D/'entry_runtime_v3_241.py';text=entry.read_text('utf-8');text=text.replace("fiscal=ROOT/'工作区/1010-unified-six/finance'",'fiscal=Path('+repr(str(finance))+')');entry.write_text(text,'utf-8')
 contracts=D/'contracts241.py';text=contracts.read_text('utf-8')
 text=text.replace("('STOP_NEW_SIX_FORWARD_V10.json',)",repr((closure.name,)))
 contracts.write_text(text,'utf-8')
 commands={};final_commands={}
 for index,task in enumerate(root['task_order']):
  folder=D/'c'/str(index);p=read(folder/'p.false.json');g=read(folder/'g.false.json')
  p.update(shared_public_helper={'path':str(shared/'native_masked_public239.py'),'sha256':sha(shared/'native_masked_public239.py')},
           masked_native_guard_directory=str(shared/'guard_v10'),shared_native_v10_Root_source_binding={'path':str(shared_ready),'sha256':sha(shared_ready)},
           registered_finance_closure_flag=str(U/'STOP_NEW_SIX.json'),
           shared_public_scope_root_qualified=False,shared_v10_exact_SHA_pending=False,closure_flag=str(closure),
           finance_config=str(cfg),finance_config_sha256=sha(cfg),common_budget_root_freeze=copy.deepcopy(root['common_budget']),
           Root_forward_comparison_protocol={'path':str(root_protocol),'sha256':sha(root_protocol)},
           first_future_complete_small_trial_task=root['task_order'][0],old_scientific_clock_not_reopened=True,
           new_six_forward_rerun_human_authorized=True,shared_actual_native_qualification_pending=True,
           method_core4L40P40T_preserved=True,API_private_native_not_yet_released=True)
  p['deployment_revision']='AL9_1_COMPLETE_DEFAULT_POOL_TO_AUTHOR_SELECTOR_MAPPING'
  for field in ('Root_shared_v6_actual_narrow_PASS','Root_actual_241_mechanical_candidate','Root_v7_generated_deployment_actual','shared_v6_SHA_pending',
                'prior_T1_scientific_UNKNOWN_preserved_no_retry','no_parameters_budget_guard_permissions_finance_or_information_change','old_science_T1_T2_not_retried_or_continued'):
   p.pop(field,None)
  save(folder/'p.false.json',p);seal['inputs'][str(folder/'p.false.json')]=sha(folder/'p.false.json')
  g.update(protocol_sha256=digest(p),protocol_raw_sha256=sha(folder/'p.false.json'),source_seal_sha256=None,delegation_evidence='Human continuous general repair and forward all-six comparison; SOURCE only until Root issued grant',Root_v8_actual_masked_and_full_pool_acceptance_pending=False,Root_v10_actual_shared_initial_pool_qualification_pending=True)
  for field in ('launch_authorized_only_after_Root_v6_narrow_leaf_PASS','Root_shared_v6_narrow_PASS_sha256','Root_v7_actual_startup_acceptance_pending'):g.pop(field,None)
  save(folder/'g.false.json',g)
  commands[task]=[g['controller_physical_python_expected'],'-X','utf8','-B',str(D/'supervisor_runtime_v3_241.py'),'science','--protocol',str(folder/'p.actual.json'),'--grant',str(folder/'g.actual.json'),'--seal',str(D/'SOURCE_SEAL.json'),'--contract',p['public_contract']]
  final_commands[task]=[g['controller_physical_python_expected'],'-X','utf8','-B',str(D/'external_once_private_v9_ROOT_ONLY241.py'),'--protocol',str(folder/'p.actual.json'),'--grant',str(folder/'g.final.actual.json'),'--seal',str(D/'SOURCE_SEAL.json'),'--contract',p['public_contract']]
 save(D/'ALL_SIX_FULL_METHOD_COMMANDS_FALSE.json',commands);save(D/'ALL_SIX_ROOT_FINAL_COMMANDS_FALSE.json',final_commands)
 p=copy.deepcopy(read(D/'c/0/p.false.json'));p.update(output_root=str(D/'q1/agentless_flow'),supervision_output_root=str(D/'q1/parent'),root_fullpool_mechanical_only=True,
         mechanical_single_case_only=root['task_order'][0],mechanical_root_wall_seconds=2100,qualification_only_not_science_cache=True)
 g=copy.deepcopy(read(D/'c/0/g.false.json'));g.update(stage='MECHANICAL_ZERO_POST',root_fullpool_mechanical_only=True,max_wall_seconds=2100,
         protocol_sha256=digest(p),initial_repository_pool_native_authorized=False)
 save(D/'p.pool.false.json',p);g['protocol_raw_sha256']=sha(D/'p.pool.false.json');save(D/'g.pool.false.json',g)
 seal['inputs'][str(D/'p.pool.false.json')]=sha(D/'p.pool.false.json')
 all_py=list(D.glob('*.py'))
 for path in all_py:ast.parse(path.read_text('utf-8-sig'));seal['sources'][str(path)]=sha(path)
 if sha(D/'agentless_paper_main241.py')!='195fc1be32b61709d5af538d90099f0403f8df684d379af0f5d35c68245adce0':raise ValueError('AUTHOR_COMPLETE_CORE_DRIFT')
 # Pure policy/semantic fixtures, no audit hook, native process or provider.
 sys.path.insert(0,str(D));runpy.run_path(str(D/'verify_static_boundaries_v9_241.py'))['main']()
 runpy.run_path(str(D/'verify_passing_pool_adapter241.py'))['main']()
 receipt=read(D/'STATIC_BOUNDARY_RECEIPT241_V9.json')
 if not receipt['PASS']:raise ValueError('STATIC_BOUNDARIES_NOT_PASS')
 seal['inputs'][str(D/'STATIC_BOUNDARY_RECEIPT241_V9.json')]=sha(D/'STATIC_BOUNDARY_RECEIPT241_V9.json')
 seal['inputs'][str(D/'PASSING_POOL_ADAPTER_SYNTHETIC_RECEIPT241_V9_1.json')]=sha(D/'PASSING_POOL_ADAPTER_SYNTHETIC_RECEIPT241_V9_1.json')
 previous_review=D.parent/'al9-source-reviews/first_seal_before_pool_adapter'
 old_seal=read(previous_review/'SOURCE_SEAL.json')
 difference={'schema':'AL9.1-complete-pool-interface-correction/1','at_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
   'prior_SOURCE_never_executed':True,'prior_review_archive':str(previous_review),'prior_seal_raw_SHA256':sha(previous_review/'SOURCE_SEAL.json'),
   'prior_seal_semantic_SHA256':digest(old_seal),'changed_existing_runtime_sources':[{ 'path':str(path),'before_SHA256':old_seal['sources'].get(str(path)),'after_SHA256':sha(path)} for path in (D/'environment241.py',D/'paper_environment_binding241.py',D/'entry_fullpool_v9_241.py')],
   'previous_inline_sentinel_override_existed_but_lacked_complete_snapshot_proof':True,
   'new_behavior':'Only exact default sentinel maps authenticated complete current-C0 collected leafs to the unchanged author passing_nodes; explicit selectors retain the original function; actual retained nodes dispatch unchanged to native helper.',
   'meaningful_synthetic_checks':len(read(D/'PASSING_POOL_ADAPTER_SYNTHETIC_RECEIPT241_V9_1.json')['checks']),
   'generated_deployment_result_must_be_complete_known_with_real_import_self_guard_STOP_and_Otherissues_marker':True,
   'original_core_SHA256_unchanged':sha(D/'agentless_paper_main241.py'),'original4L40P40T_regression_exclusion_and_votes_unchanged':True,
   'native_API_private_ledger_execution':0,'all_release_grants_false':True}
 save(D/'INTERFACE_POOL_MAPPING_CORRECTION241_V9_1.json',difference)
 seal['inputs'][str(D/'INTERFACE_POOL_MAPPING_CORRECTION241_V9_1.json')]=sha(D/'INTERFACE_POOL_MAPPING_CORRECTION241_V9_1.json')
 for path in (D/'ALL_SIX_FULL_METHOD_COMMANDS_FALSE.json',D/'ALL_SIX_ROOT_FINAL_COMMANDS_FALSE.json'):seal['inputs'][str(path)]=sha(path)
 save(D/'SOURCE_SEAL.json',seal)
 for folder in [D/'c'/str(i) for i in range(6)]+[D]:
  name='g.pool.false.json' if folder==D else 'g.false.json';g=read(folder/name);g['source_seal_sha256']=digest(seal);save(folder/name,g)
 argv=[g['controller_physical_python_expected'],'-X','utf8','-B',str(D/'supervisor_fullpool_v9_241.py'),'mechanical','--protocol',str(D/'p.pool.actual.json'),'--grant',str(D/'g.pool.actual.json'),'--seal',str(D/'SOURCE_SEAL.json'),'--contract',p['public_contract']]
 ready={'schema':'AL9.1-forward-source-ready-all-false/1','at_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':str(D),
        'source_seal_semantic_SHA256':digest(seal),'source_seal_raw_SHA256':sha(D/'SOURCE_SEAL.json'),'sources':len(seal['sources']),'inputs':len(seal['inputs']),
        'paper_complete_core_SHA256':sha(D/'agentless_paper_main241.py'),'AST_files':len(all_py),'static_boundary_checks':len(receipt['checks']),
        'finance_directory':str(finance),'finance_config':str(cfg),'continuous_ledger_not_reset':True,
        'root_forward_protocol_SHA256':sha(root_protocol),'shared_ready_SHA256':sha(shared_ready),'budget':root['common_budget'],
        'initial_T1_zero_API_pool_exact_argv':argv,'Root_mechanical_grant_template':str(D/'g.pool.false.json'),
        'Root_mechanical_protocol_template':str(D/'p.pool.false.json'),'native_model_finance_private_grants':False,'no_native_API_private_execution':True,
        'mechanical_then_first_paid_complete_pilot_required':True,'new_pilot_all_6_use_same_source_not_per_task_edits':True,
        'pool_qualification_must_not_be_reused_outside_science_clock':True,'ROOT_final_source_only_never_private_values_read':True}
 ready.update(passing_pool_adapter_checks=difference['meaningful_synthetic_checks'],interface_correction_receipt_SHA256=sha(D/'INTERFACE_POOL_MAPPING_CORRECTION241_V9_1.json'),pool_adapter_synthetic_receipt_SHA256=sha(D/'PASSING_POOL_ADAPTER_SYNTHETIC_RECEIPT241_V9_1.json'))
 save(D/'SOURCE_READY_ALL_FALSE241_V9.json',ready)
 print(json.dumps(ready,ensure_ascii=False))
if __name__=='__main__':main()

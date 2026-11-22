"""Prepare exact first wire body for one Root-qualified task/trial, no IO transport."""
import argparse, ast, copy, hashlib, importlib.util, json, shutil, sys
from decimal import Decimal
from pathlib import Path
from prepare250_SOURCE import HERE,ROOT,PARENT,COMMON,read,sha,canonical,save
from pure_author_body250 import original_payload

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec)
 sys.modules[name]=value;spec.loader.exec_module(value);return value
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--task',required=True);parser.add_argument('--trial',choices=['trial1','trial2','trial3'],required=True)
 parser.add_argument('--finance',default=str(COMMON/'CONFIRMATION_ACCEPTED_C0_V1_FINANCE_CONFIG.json'))
 args=parser.parse_args();blueprint=read(HERE/'PROTOCOL_BLUEPRINT250_SOURCE.json');parent=read(PARENT/'protocol249_SOURCE.json')
 if args.task not in parent['task_order']:raise RuntimeError('EXP250_TASK_NOT_FROZEN')
 trial_index=parent['trial_ids'].index(args.trial);seed=parent['trial_master_seeds'][trial_index]
 config=read(args.finance)
 if Path(args.finance).resolve().parent!=COMMON.resolve() or args.task not in config['Root_qualified_tasks_now']:raise RuntimeError('EXP250_TASK_FRESH_CURRENT_C0_NOT_QUALIFIED')
 shared=module('_source250_common_public',blueprint['shared_public249']);common=module('_source250_common_input',blueprint['shared_input249'])
 value=shared.load_public_task(args.task);contract=value['contract'];supplement,decoded=common.supplement(config,args.task)
 if supplement['actual_C0_source_SHA256']!=contract['c0_business_paths_sha256']:raise RuntimeError('EXP250_ROOT_C0_SOURCE_DIFFERS_FROM_PUBLIC_CONTRACT')
 scope=read(PARENT/'public_views_v2/COMMON_MASKED_PUBLIC_TEST_SCOPE249.json')
 row=next(row for row in scope['tasks'] if row['task_id']==args.task)
 if row.get('materialization_qualified') is not True or scope.get('all_three_methods_same_read_execute_permission') is not True:raise RuntimeError('EXP250_CURRENT_COMMON_MASK_REQUIRED')
 out=HERE/'deployments'/args.task/args.trial
 if out.exists():raise RuntimeError('EXP250_SOURCE_DEPLOYMENT_ALREADY_EXISTS_PRESERVE_FROZEN_BYTES')
 shutil.copytree(HERE/'template',out)
 ref=copy.deepcopy(value['public_ref']);ref.update(binding_kind='Exp250_public_only_verified_contract',template=contract['template'],
  harness=contract['harness'],python=contract['logical_product_python'],frozen_tests=contract['frozen_public_test_root'],
  saved_source_inventory=str(out/'public_source_inventory250.json'))
 ref.pop('binding_seal',None);ref.pop('ready_sha256',None)
 save(out/'public_source_inventory250.json',{'template':contract['template_inventory'],'frozen_tests':contract['frozen_inventory'],
  'source':'Exact Root common public contract; private manifest not consulted'})
 save(out/'selected_task_bindings240.json',{'tasks':[ref],'public_only_inputs':True})
 p=copy.deepcopy(blueprint);p.update(prepared_task_ids=[args.task],trial_id=args.trial,trial_master_seed=seed,
  flat_owner=str(out),masked_native_owner_root=str(out),selected_task_bindings_path=str(out/'selected_task_bindings240.json'),
  common_current_C0_injection_owner='EnAgent wire250 calls exact shared_input249.inject; unchanged continuous finance v3',
  finance_template_sha256=sha(args.finance),finance_config_SHA256=sha(args.finance),finance_template=str(Path(args.finance).resolve()),
  public_test_scope_contract={'path':str(PARENT/'public_views_v2/COMMON_MASKED_PUBLIC_TEST_SCOPE249.json'),'sha256':sha(PARENT/'public_views_v2/COMMON_MASKED_PUBLIC_TEST_SCOPE249.json')},
  shared_pack_references={args.task:{'path':contract['pack'],'sha256':contract['pack_sha256'],
   'semantic_sha256':contract['semantic_sha256'],'input_digest':contract['input_digest'],
   'c0_business_inventory_sha256':contract['c0_business_inventory_sha256']}},
  closure_flag=str(out/'STOP_REQUESTED.json'),parent_current_C0_supplement_registry_SHA256=config['common_C0_supplement_registry_SHA256'])
 shutil.copyfile(args.finance,out/'finance_config239.json')
 if str(Path(p['shared_publicpack_module']).parent) not in sys.path:sys.path.append(str(Path(p['shared_publicpack_module']).parent))
 publicpack=module('_source250_original_publicpack',p['shared_publicpack_module'])
 public_text=publicpack.render(value['pack'])
 actor=module('_source250_original_actor_tool_contract',out/'actor_tool_contract_v3.py').ACTOR_TOOL_CONTRACT
 issue=public_text+'\n'+actor+'\nResolve the observed current public failure and preserve already passing ordinary behavior. The working repository is /workspace/repo. Complete business source is available through the original author tools and common readers. Original tests are observer-owned; run only declared public nodes or your own generated scripts.'
 payload=original_payload(issue,public_text)
 provider_seed=int(hashlib.sha256(('Exp250|'+str(seed)+'|'+args.task+'|coder|0|0').encode()).hexdigest()[:8],16)%2147483647
 author={'model':'deepseek-flash',**payload,'thinking':{'type':'disabled'},'seed':provider_seed,'max_tokens':4096,'stream':False,'tool_choice':'auto'}
 full=common.inject(author,config,args.task)
 bound=min(len(canonical(full).encode())+4096*len(full['messages'])+2048,1048576)
 reserve=(Decimal(bound)*2+Decimal(4096)*8)/1000000
 save(out/'FIRST_AUTHOR_BODY_SOURCE_NOT_POSTED.json',author);save(out/'FIRST_FULL_BODY_SOURCE_NOT_POSTED.json',full)
 p['first_body_prospective_pin']={'task_id':args.task,'trial_id':args.trial,'authorbody_SHA256':digest(author),'fullbody_SHA256':digest(full),
  'authorbody_path':str(out/'FIRST_AUTHOR_BODY_SOURCE_NOT_POSTED.json'),'fullbody_path':str(out/'FIRST_FULL_BODY_SOURCE_NOT_POSTED.json'),
  'client_seed_only_no_provider_determinism_guarantee':True,'SOURCE_ONLY':True}
 save(out/'protocol225.json',p)
 save(out/'FIRST_FULL_BODY_RESERVATION_SOURCE.json',{'SOURCE_ONLY':True,'POST':0,'model_native_private_ledger':0,
  'task':args.task,'trial':args.trial,'canonical_bytes':len(canonical(full).encode()),'input_upper':bound,
  'output_reservation':4096,'full_peak_reserve_CNY':str(reserve),'author_body_SHA256':digest(author),'full_body_SHA256':digest(full),
  'full_body_never_clipped':True,'whole_method_funding_not_guaranteed_by_first_call':True,
  'body_built_from_original_new_task_and_tool_metadata_no_old_model_request_response_or_patch':True})
 sources={str(path):sha(path) for path in [*out.rglob('*.py'),out/'protocol225.json',out/'finance_config239.json',out/'selected_task_bindings240.json',
  out/'public_source_inventory250.json',out/'FIRST_AUTHOR_BODY_SOURCE_NOT_POSTED.json',out/'FIRST_FULL_BODY_SOURCE_NOT_POSTED.json',out/'FIRST_FULL_BODY_RESERVATION_SOURCE.json']}
 dependencies=copy.deepcopy(read(HERE/'SOURCE_SEAL250.json')['dependencies'])
 dependencies.pop(str(COMMON/'CONFIRMATION_FIRST_SIX_FINANCE_CONFIG.json'),None)
 for path in [Path(args.finance),Path(p['public_test_scope_contract']['path']),Path(config['common_C0_supplement_registry']),
  Path(common.registry(config)['tasks'][args.task]['path'])]:dependencies[str(path)]=sha(path)
 for path,h in {**sources,**dependencies}.items():
  if sha(path)!=h:raise RuntimeError('EXP250_SEAL_INPUT_DRIFT '+path)
 save(out/'source_seal239.json',{'schema':'EXP250-isolated-task-trial-source-seal/1','sources':sources,'dependencies':dependencies,
  'READY':False,'execution_authorized':False,'model_authorized':False,'native_authorized':False,'private_authorized':False})
 grant={'SOURCE_ONLY':True,'task_id':args.task,'trial_id':args.trial,'allowed_task_ids':[args.task],
  'finance_phase':p['finance_phase'],'execution_lease_id':'lease_001','scope_id':p['scope_id'],
  'protocol_sha256':sha(out/'protocol225.json'),'source_seal_sha256':sha(out/'source_seal239.json'),
  'common_contract_SHA256':p['root_protocol_sha256'],'finance_config_SHA256':sha(out/'finance_config239.json')}
 for name in ('execution_authorized','model_generation_authorized','native_authorized','finance_authorized','private_authorized','once_private_authorized',
  'Root_local_public_native_qualification_admitted','Root_external_final_source_review_admitted','Root_new_independent_core_run_admitted'):grant[name]=False
 save(out/'root_grant239.json',grant)
 for path in out.rglob('*.py'):ast.parse(path.read_text('utf-8-sig'),filename=str(path))
 command={'READY':False,'task':args.task,'trial':args.trial,'deployment':str(out),
  'once_actor_argv_pending_exact_Root_release':[str(ROOT/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'),'-X','utf8','-B',str(out/'supervisor250.py'),'--task',args.task],
  'Root_grant_path':str(out/'root_grant239.json'),'protocol_SHA256':sha(out/'protocol225.json'),
  'source_seal_SHA256':sha(out/'source_seal239.json'),'full_body_SHA256':digest(full),'first_full_peak_reserve_CNY':str(reserve),
  'external_Root_original_once_final_required_not_actor_authorized':True,'POST_native_private_ledger':0}
 save(out/'FIRST_PILOT_SOURCE_COMMANDS.json',command)
 print(canonical(command))

if __name__=='__main__':main()

"""Independent next-six current-C0 gate; trusted reads and native stay Root-only."""
import argparse
import ast
import copy
import json
import hashlib
from pathlib import Path
C = Path(__file__).resolve().parent; Q = C.parent; I = Q / 'next_six_qualification_SOURCE'
R = Path('D:/Code/毕设/graduate-thesis-experiments')
def read(p): return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p): return {'path': str(Path(p).resolve()), 'sha256': sha(p)}
def write(p, v):
 p=Path(p).resolve()
 if not p.is_relative_to(C): raise RuntimeError('NEXT_C0_SOURCE_WRITE_SCOPE')
 p.parent.mkdir(parents=True, exist_ok=True)
 raw=(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
 if p.exists() and p.read_bytes()!=raw: raise RuntimeError('NEXT_C0_SOURCE_ALREADY_FROZEN:'+str(p))
 if not p.exists(): p.write_bytes(raw)
def source(p, raw):
 if p.exists() and p.read_bytes()!=raw: raise RuntimeError('NEXT_C0_SOURCE_ALREADY_WRITTEN:'+str(p))
 if not p.exists(): p.write_bytes(raw)
def change(t,a,b):
 if t.count(a)!=1: raise RuntimeError('NEXT_C0_MECHANICAL_ANCHOR:'+a)
 return t.replace(a,b)

def prepare():
 tasks=read(I/'protocol249_SOURCE.json')['task_order']
 common=(Q/'common249.py').read_text('utf-8-sig');start=common.index('TASKS = ');end=common.index('CONTROLLER = ',start)
 common=common[:start]+'TASKS = '+repr(tasks)+'\nFIRST_TWO = TASKS\nIDENTITY_ROOT = E.parent / "next_six_qualification_SOURCE"\n'+common[end:]
 common=change(common,'        g = self.value\n',"        g = self.value\n        if self.action not in ('materialize', 'current_C0'): raise RuntimeError('NEXT_C0_NO_IDENTITY_OR_METHOD_EXECUTION')\n")
 source(C/'common_current_C0.py',common.encode())
 source(C/'physical_identity249.py',(Q/'physical_identity249.py').read_bytes())
 source(C/'native_capacity249_ROOT_V11_SOURCE.py',(Q/'native_capacity249_ROOT_V11_SOURCE.py').read_bytes())
 source(C/'TASK_BINDINGS249_SOURCE.json',(I/'TASK_BINDINGS249_SOURCE.json').read_bytes())
 native=(Q/'native249_ROOT_BATCH3_R2.py').read_text('utf-8-sig')
 native=change(native,'from common249_ROOT_BATCH3 import *','from common_current_C0 import *')
 native=change(native,"identity_path = E / 'qualification' / args.task / 'identity' / 'COMPLETED_IDENTITY249.json'","identity_path = IDENTITY_ROOT / 'qualification' / args.task / 'identity' / 'COMPLETED_IDENTITY249.json'")
 native=change(native,"scope_path = E / 'public_views_batch3' / 'COMMON_MASKED_PUBLIC_TEST_SCOPE249.json'","scope_path = E / 'public_views' / args.task / 'COMMON_MASKED_PUBLIC_TEST_SCOPE249.json'")
 native=change(native,"choices=('identity', 'current_C0')","choices=('current_C0',)")
 native=change(native,"('current_C0_batch3_r2' if args.stage == 'current_C0' else args.stage)","'current_C0'")
 native=change(native,"    observed = guard.observe(validation, c['public_target_nodes'], c['ordinary_nodes'])", "    try:\n        observed = guard.observe(validation, c['public_target_nodes'], c['ordinary_nodes'])\n    except guard.ProgressObservationUnknown as exc:\n        save(out / 'CURRENT_C0_UNKNOWN.json', {'task_id': args.task, 'stage': 'original_G_O', 'qualification_known': False, 'method_outcome': None, 'reason': str(exc), 'original_public_native': str(out / 'original_G_O/run.json'), 'original_public_native_SHA256': sha(out / 'original_G_O/run.json'), 'collection_failure_not_individual_Goal_FAIL': True, 'old_syntax_certificate_not_inherited': True, 'parent_STOP_still_required': True})\n        return")
 native=change(native,"    masked_result = masked.execute(env, repo, scope, masked_nodes, collect_only=False,", "    if not masked_nodes:\n        save(out / 'CURRENT_C0_UNKNOWN.json', {'task_id': args.task, 'stage': 'masked_channel', 'qualification_known': False, 'method_outcome': None, 'original_G_O_known': True, 'reason': 'NO_SAFE_STATIC_PUBLIC_CHANNEL_NODE', 'parent_STOP_still_required': True})\n        return\n    masked_result = masked.execute(env, repo, scope, masked_nodes, collect_only=False,")
 source(C/'native_current_C0.py',native.encode())
 mask=(Q/'materialize249_ROOT_BATCH3.py').read_text('utf-8-sig')
 mask=change(mask,'from common249_ROOT_BATCH3 import *','from common_current_C0 import *')
 mask=change(mask,"    parser.add_argument('--root-grant', required=True)","    parser.add_argument('--root-grant', required=True)\n    parser.add_argument('--task', choices=TASKS, required=True)")
 mask=change(mask,"    grant = Grant(args.root_grant, 'materialize', FIRST_TWO)","    selected_tasks = [args.task]\n    grant = Grant(args.root_grant, 'materialize', selected_tasks)")
 mask=mask.replace('FIRST_TWO','selected_tasks')
 mask=change(mask,"dest = E / 'public_views_batch3'","dest = E / 'public_views' / args.task")
 mask=change(mask,"get('max_materialized_tasks') != 2","get('max_materialized_tasks') != 1")
 mask=change(mask,"view = dest / task / 'repo'","view = E / 'public_views' / task / 'repo'")
 mask=change(mask,"            src = original / rel", "            if c['package'] == 'mypy' and ('test-data' in Path(rel).parts or Path(rel).suffix in ('.test', '.data')):\n                omitted.append({'path': rel, 'policy': 'all_mypy_data_driven_case_support_omitted_pending_mapping', 'masked_count': 0, 'unmapped_count': 0})\n                continue\n            src = original / rel")
 mask=change(mask,"E / 'trusted_materialization' / 'ROOT_ONLY_MASKING_PROVENANCE249_BATCH3.json'","E / 'trusted_materialization' / args.task / 'ROOT_ONLY_MASKING_PROVENANCE249.json'")
 source(C/'materialize_current_C0_ROOT_ONLY.py',mask.encode())
 batch=(Q/'batch2_SOURCE_preparation/prepare_batch2_grants_SOURCE.py').read_text('utf-8-sig');tree=ast.parse(batch)
 audit='import ast\nfrom common_current_C0 import *\n\n'+'\n\n'.join(ast.get_source_segment(batch,n) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('exact_function','public_mask_audit'))+'\n'
 audit=change(audit,"E / 'public_views_batch2' / task / 'repo'","E / 'public_views' / task / 'repo'")
 audit=change(audit,"        if not choices: raise RuntimeError('BATCH2_NO_DECLARED_PUBLIC_AUXILIARY_CHANNEL')\n        selected = [min(choices)]; auxiliary = True", "        selected = [min(choices)] if choices else []; auxiliary = True")
 audit=change(audit,"    trees = {}", "    if c['package'] == 'mypy' and any('test-data' in Path(rel).parts or Path(rel).suffix in ('.test', '.data') for rel in row['business_and_support_files_in_view']):\n        raise RuntimeError('NEXT_C0_UNMAPPED_DATA_CASE_SUPPORT_VISIBLE')\n    trees = {}")
 source(C/'audit_public_mask_SOURCE.py',audit.encode())
 p={'schema':'EXP249-fixed-next-six-current-C0-gates-source/1','task_order':tasks,'natural_slots_one_based':list(range(7,13)),
  'source_identity_protocol':ref(I/'protocol249_SOURCE.json'),'source_identity_seal':ref(I/'SOURCE_SEAL249.json'),
  'per_task_original_identity_and_parent_STOP_required':True,'original_G_O_unchanged':True,'one_original_G_O_and_one_masked_channel_maximum':True,
  'all_methods_same_public_scope':True,'mypy_data_driven_case_support_all_omitted_prospectively':True,
  'mypy10392_historical_collection_failure_does_not_qualify_current_or_fabricate_Goal_FAIL':True,
  'unknown_slots_not_replaced':True,'historically_exposed_and_development_tags_preserved':True,
  'V11_uniform_native_seconds':300,'native_parent_active_lifetime':[8,24],'continuous_finance_no_access_or_reset':True,
  'Root_explicit_original_clock_policy_required':True,'source_only':True,'READY':False,'current_C0_qualified_count':0,
  'model_authorized':False,'native_authorized':False,'private_execution_authorized':False,'finance_authorized':False}
 write(C/'protocol249_SOURCE.json',p)
 print(json.dumps({'status':'NEXT_SIX_CURRENT_C0_SOURCES_PREPARED','actual_calls':0}))

def seal():
 old=read(I/'SOURCE_SEAL249.json');sources=dict(old['sources_SHA256']);inputs=dict(old['public_inputs_SHA256'])
 for p in C.glob('*.py'): ast.parse(p.read_text('utf-8-sig'));sources[str(p)]=sha(p)
 for p in (Q/'native249_ROOT_BATCH3_R2.py',Q/'materialize249_ROOT_BATCH3.py',Q/'native_capacity249_ROOT_V11_SOURCE.py',R/'工作区/1011-our19/progress_guard240.py',R/'工作区/1002-exp129-expanded-baselines/实验/实验129_扩展基线与恢复证据/executor/run.py'):
  sources[str(p)]=sha(p)
 v14=R/'工作区/1010-unified-six/shared_native_v14_certificate_complete';descriptor=read(v14/'SOURCE_READY_FALSE.json')
 for p,h in descriptor['sources'].items():
  if sha(p)!=h:raise RuntimeError('NEXT_C0_SHARED_V14_DRIFT')
  sources[p]=h
 for p in (C/'protocol249_SOURCE.json',C/'TASK_BINDINGS249_SOURCE.json',C/'SOURCE_VALIDATION.json',I/'SOURCE_SEAL249.json',v14/'SOURCE_READY_FALSE.json'):inputs[str(p)]=sha(p)
 if read(C/'SOURCE_VALIDATION.json')['status']!='PASS':raise RuntimeError('NEXT_C0_SOURCE_VALIDATION_REQUIRED')
 tasks=read(C/'protocol249_SOURCE.json')['task_order'];rows=[]
 for task in tasks:
  ip=I/'qualification'/task/'identity/COMPLETED_IDENTITY249.json';pp=ip.parent/'PARENT_TERMINAL249.json';ident=read(ip);parent=read(pp)
  if ident['task_id']!=task or parent['task_id']!=task or parent.get('error') is not None or parent.get('exit_code')!=0 or parent['stop_receipt']['all_owned_descendants_terminated'] is not True:raise RuntimeError('NEXT_C0_FRESH_IDENTITY_PARENT_REQUIRED')
  for p in (ip,pp):inputs[str(p)]=sha(p)
  rows.append((task,ip,pp))
 sp=C/'SOURCE_SEAL249.json';write(sp,{'schema':'EXP249-next-six-current-C0-seal/1','sources_SHA256':sources,'public_inputs_SHA256':inputs,'actual_calls':0,'old_six_sources_unchanged':True,'mask_private_metadata_bound_only_by_later_Root':True})
 py=R/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe';commands=[];bindings={r['task_id']:r for r in read(C/'TASK_BINDINGS249_SOURCE.json')['tasks']}
 for task,ip,pp in rows:
  contract=read(bindings[task]['public_contract']);base={'schema':'EXP249-next-six-current-gate-Root-grant-false/1','root_authorized':False,'native_authorized':False,'model_authorized':False,'private_execution_authorized':False,'finance_authorized':False,'trusted_original_test_source_read_authorized':False,'lease_end_UTC':None,'root_stop_paths':[str(Q/'ROOT_STOP_REQUESTED.json')],'protocol_SHA256':sha(C/'protocol249_SOURCE.json'),'source_seal_SHA256':sha(sp),'controller_launch_python':str(py),'controller_launch_SHA256':sha(py),'source_only':True,'Root_mask_v2_sources_SHA256':{str(p):sha(p) for p in C.glob('*.py')},'task_ids':[task]}
  mg={**base,'action':'materialize','max_materialized_tasks':1,'trusted_masking_inputs':{task:{'manifest_path':bindings[task]['Root_only_original_isolation_manifest_path'],'manifest_SHA256':None}}}
  mp=C/'grant_templates'/(task+'.materialize.false.json');write(mp,mg)
  ng={**base,'action':'current_C0','max_original_G_O_native':1,'max_masked_ordinary_native':1,'trusted_original_G_O_oracle_execution_authorized':False,'parent_owned_job_name':'RootExp249_NextSix_C0_'+task.replace('-','_'),'current_identity_receipt_SHA256':sha(ip),'current_identity_parent_STOP_SHA256':sha(pp),'masked_scope_SHA256':None,'exact_G_O_nodes':list(dict.fromkeys(contract['public_target_nodes']+contract['ordinary_nodes'])),'current_process_clock_policy':'ROOT_ORIGINAL_CLOCK_EXPLICITLY_ADMITTED','common_precise_clock_contract':None,'Root_current_process_precise_clock_admitted':False,'masked_channel_qualification_nodes':None,'Root_auxiliary_channel_only_original_O_retained':False,'after_mask_binding_required':True}
  gp=C/'grant_templates'/(task+'.current_C0.pending_mask.false.json');write(gp,ng)
  commands.append({'task_id':task,'materialize_false':ref(mp),'pending_C0_false':ref(gp),'materialize_argv':[str(py),'-X','utf8','-B',str(C/'materialize_current_C0_ROOT_ONLY.py'),'--task',task,'--root-grant',str(C/'ROOT_RELEASES'/(task+'.materialize.actual.json'))],
   'after_mask_argv':[str(py),'-X','utf8','-B',str(C/'bind_after_mask_SOURCE.py'),'--task',task],
   'current_C0_argv':[str(py),'-X','utf8','-B',str(C/'native_current_C0.py'),'--stage','current_C0','--task',task,'--root-grant',str(C/'ROOT_RELEASES'/(task+'.current_C0.actual.json'))],
   'current_qualification':False})
 manifest=C/'SOURCE_READY_FALSE.json';write(manifest,{'schema':'EXP249-next-six-current-gates-ready-false/1','seal':ref(sp),'commands':commands,'current_C0_qualified_count':0,'actual_calls':0,'Root_materialize_sign_fields':['root=true','trusted_original_test_source_read=true','original manifest SHA measured by Root','finite lease; native/model/private_execution/finance=false'],
  'Root_C0_sign_fields':['use AFTER_MASK_BOUND_FALSE only','root/native/trusted_original_G_O_oracle_execution=true','finite lease','explicit common original current clock; model/private_execution/finance/trusted_original_source_read=false'],
  'public_tests_and_private_metadata_never_read_during_SOURCE':True})
 print(json.dumps({'status':'NEXT_SIX_C0_SOURCE_READY_FALSE','seal':ref(sp),'commands':ref(manifest),'actual_calls':0},ensure_ascii=False))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=('prepare','seal'),required=True);a=p.parse_args()
 if a.stage=='prepare':prepare()
 else:seal()

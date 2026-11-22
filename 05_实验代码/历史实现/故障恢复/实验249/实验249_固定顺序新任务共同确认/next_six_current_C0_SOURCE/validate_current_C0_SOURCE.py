"""Minimal syntax, source-diff and existing identity binding checks only."""
import ast
from common_current_C0 import *

checks=[]
def check(name,value):
 if not value:raise AssertionError(name)
 checks.append({'name':name,'passed':True})
for p in E.glob('*.py'):ast.parse(p.read_text('utf-8-sig'),filename=str(p))
check('all_entry_source_syntax_valid',True)
def functions(path):
 tree=ast.parse(Path(path).read_text('utf-8-sig'))
 return {n.name:ast.dump(n,include_attributes=False) for n in tree.body if isinstance(n,ast.FunctionDef)}
before=functions(E.parent/'native249_ROOT_BATCH3_R2.py');after=functions(E/'native_current_C0.py')
check('held_Job_identity_clock_original_probe_functions_unchanged',all(before[n]==after[n] for n in before if n not in ('main','run_current_C0')))
check('mask_AST_decorator_and_unknown_module_policy_unchanged',functions(E.parent/'materialize249_ROOT_BATCH3.py')['mask_text']==functions(E/'materialize_current_C0_ROOT_ONLY.py')['mask_text'])
check('capacity_v11_and_identity_bytes_unchanged',sha(E/'native_capacity249_ROOT_V11_SOURCE.py')==sha(E.parent/'native_capacity249_ROOT_V11_SOURCE.py') and sha(E/'physical_identity249.py')==sha(E.parent/'physical_identity249.py'))
for task in TASKS:
 row,c=binding(task);ip=IDENTITY_ROOT/'qualification'/task/'identity/COMPLETED_IDENTITY249.json';pp=ip.parent/'PARENT_TERMINAL249.json';ident=read(ip);parent=read(pp);measured=ident['product_identity'];obs=ident['process_observation']
 check(task+'_existing_current_identity_and_parent_STOP_bound',ident['task_id']==task and parent['task_id']==task and parent.get('error') is None and parent.get('exit_code')==0
  and parent['stop_receipt']['all_owned_descendants_terminated'] is True and parent['stop_receipt']['job_active_processes_after_termination']==0
  and measured['specific_named_Job_membership'] is True and measured['product_imports_or_tests']==0 and obs['root_PID_birth_verified'] is True
  and obs['stop_receipt']['all_owned_descendants_terminated'] is True and sha(measured['actual_OS_image'])==measured['actual_OS_image_SHA256']
  and ident['logical_product_python_SHA256']==sha(c['logical_product_python']) and ident['pyvenv_cfg_SHA256']==sha(Path(c['logical_product_python']).parent.parent/'pyvenv.cfg'))
false=E/'validation_cases/CLOSED.json';save(false,{'root_authorized':False,'action':'current_C0','task_ids':[TASKS[0]]})
try:Grant(false,'current_C0',[TASKS[0]])
except RuntimeError as e:check('closed_Root_gate_rejects_before_native_or_private_read','ROOT_EXACT_ACTION_NOT_GRANTED' in str(e))
else:raise AssertionError('closed gate')
check('no_actual_mask_or_native_directories',not (E/'qualification').exists() and not (E/'public_views').exists() and not (E/'trusted_materialization').exists())
save(E/'SOURCE_VALIDATION.json',{'schema':'EXP249-next-six-current-C0-minimal-source-check/1','status':'PASS','checks':checks,
 'verification_kind':'SOURCE_AST_BINDINGS_ONLY_NOT_RUNTIME_QUALIFICATION','actual_identity_native_model_API_finance':0,
 'original_unmasked_test_private_manifest_or_result_Gold_reads':0,'current_C0_qualified_count':0})
print(canonical({'status':'PASS_SOURCE_ONLY','checks':len(checks),'sha256':sha(E/'SOURCE_VALIDATION.json'),'actual_calls':0}))

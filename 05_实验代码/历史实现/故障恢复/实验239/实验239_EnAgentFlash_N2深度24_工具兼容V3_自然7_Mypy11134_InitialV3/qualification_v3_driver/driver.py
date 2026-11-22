"""Root-authorized qualification only: actual tools/native, no LLM or private."""
import pathlib,sys,json,asyncio,copy,hashlib,os,datetime
E=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(E))
from common166 import *
import control235
control235.start_mechanical()
control235.MECHANICAL_NAMESPACE='qualified_v3_'+str(os.getpid())
import entry_initial_v3_239 as entry239
worker=entry239.install();TASK='python__mypy-11134';control235.verify(TASK,control235.PHASE)
D=E/'qualification_v3_driver';RESULT=D/('result_'+str(os.getpid())+'.json')
rows=[]
def checkpoint(stage,**fields):
 save(D/'CURRENT_QUALIFICATION239_V3.json',{'stage':stage,'at_utc':now(),'PID':os.getpid(),'task':TASK,'namespace':control235.MECHANICAL_NAMESPACE,'driver_sha256':sha(pathlib.Path(__file__)),'POSTs':0,'private_calls':0,**fields})
class NoModel:
 def request(self,payload):raise RuntimeError('QUALIFICATION_MODEL_CALL_FORBIDDEN')

ref=copy.deepcopy(next(x for x in read(worker.PEER/'data/selected_task_bindings.json')['tasks'] if x['task_id']==TASK))
ref.update(_output_namespace=control235.MECHANICAL_NAMESPACE+'/f',_native_namespace=control235.MECHANICAL_NAMESPACE+'/n')
env=worker.CommonEnvironment(ref,'EA239_V3_QUALIFICATION_ONLY');env.finance_phase=control235.PHASE
from native_guard_compat225 import install
install(env)
bridge=worker.Bridge(env);owner=worker.ShellOwner(bridge)
core=worker.module('ea239_v3_qualification_core',worker.OLD175/'enagent_native.py')
initial=bridge.export();business=sorted(bridge.initial);root=bridge.owned/'qualification_actor'
initial_digest=core.digest(initial,business);core.snapshot_copy(initial,root,business,initial_digest)
context=core.Context(root,NoModel(),bridge.command_runner,bridge.edit_guard,[worker.CERT],{'business_paths':business,'business_sha256':initial_digest});core.ACTIVE.context=context
worker.shim.install(core,command_guard=bridge.command_guard,shell_launcher=owner.launch,record=lambda row:env.record('qualification_original_author_tools',row),product_python=lambda r:env._paths['python'],native_command=bridge.native_command,path_map=bridge.path_map,neutral_output=bridge.neutral)
executor=core.ToolExecutor([core.NS.tools_registry[n](model_provider='openai') for n in ('bash','str_replace_based_edit_tool')])
async def tool(name,args,expected=True):
 result=(await executor.sequential_tool_call([core.ToolCall(name=name,call_id=str(len(rows)),arguments=args,id=str(len(rows)))]))[0]
 row={'tool':name,'args':args,'success':result.success,'result':result.result,'error':result.error};rows.append(row)
 if bool(result.success)!=expected:raise RuntimeError('ACTUAL_AUTHOR_TOOL_EXPECTATION_FAILED '+json.dumps(row,ensure_ascii=False))
 return row
async def run_tools():
 checkpoint('CURRENT_C0_V3_SHARED_CERTIFICATE_REUSE')
 certpath=Path(read(E/'protocol225.json')['initial_v3_public_source_observer_certificate']['path'])
 if sha(certpath)!='59f51375a82194d525b48c57ce16cf3e62b463cec93a1465abd05c7e30b1d166':raise RuntimeError('CURRENT_INITIAL_V3_CERTIFICATE_DRIFT')
 certificate=read(certpath)
 if certificate['task']!=TASK or not certificate['all_owned_STOP']:raise RuntimeError('CURRENT_INITIAL_V3_TASK_OR_STOP_MISMATCH')
 actual={path:sha(root/path) for path in certificate['all_actual_C0_business_paths_SHA256']}
 if actual!=certificate['all_actual_C0_business_paths_SHA256']:raise RuntimeError('CURRENT_C0_V3_ALL_SOURCE_FILES_MISMATCH')
 import ast,shlex
 try:ast.parse((root/certificate['observed_syntax']['business_relative']).read_text('utf-8'))
 except SyntaxError as syntax:
  observed={'type':type(syntax).__name__,'line':syntax.lineno,'offset':syntax.offset,'message':syntax.msg}
 else:raise RuntimeError('CURRENT_C0_EXPECTED_LEGAL_BUSINESS_SYNTAX_BLOCK_NOT_PRESENT')
 if any(observed[k]!=certificate['observed_syntax'][k] for k in observed):raise RuntimeError('CURRENT_INITIAL_SYNTAX_DIFFERS_FROM_COMMON_V3')
 common_native=Path(certificate['native_result_path'])
 if sha(common_native)!=certificate['native_result_SHA256']:raise RuntimeError('CURRENT_COMMON_NATIVE_SHA_DRIFT')
 ordinary={node:'PASS' for node in env.public_regression_nodes}
 save(D/'C0_CURRENT_11134.json',{'schema':'observer-initial-qualification-v3-reuse/1','certificate_path':str(certpath),'certificate_sha256':sha(certpath),'ordinary':ordinary,'ordinary_actual_native_evidence_reused_not_new_result':True,'actual_initial_goal_completed':0,'actual_initial_goal_collection_blocked':len(env.recovery_goal_nodes),'individual_goal_failed_outcomes_NOT_fabricated':True,'observed_syntax':observed,'actual_current_C0_source_paths_checked':len(actual),'all_current_source_SHA_equal_common_certificate':True,'common_native_result_path':str(common_native),'common_native_result_sha256':sha(common_native),'STOP':{'common_own_jobs_stopped':certificate['all_owned_STOP']}})
 checkpoint('ACTUAL_CODER_C0_PUBLIC_QUERY_KNOWN_NEGATIVE')
 before_native=env.native_calls
 await tool('bash',{'command':shlex.join(['pytest',*env.recovery_goal_nodes])},expected=False)
 if env.native_calls!=before_native+1 or bridge.engineering_error:raise RuntimeError('ACTUAL_CODER_KNOWN_NEGATIVE_NOT_NATIVE_OR_FATAL')
 certified=[row for row in env.stage_ledger if row['stage']=='certified_known_public_source_collection_failure']
 accepted=[row for row in env.stage_ledger if row['stage']=='enagent_bridge_observer_initial_v3_known_source_negative_accepted_as_tool_feedback_only']
 if len(certified)!=1 or len(accepted)!=1:raise RuntimeError('ACTUAL_C0_NEGATIVE_ENV_AND_BRIDGE_CERTIFICATE_REQUIRED')
 public_records=[row['evidence']['native_record'] for row in env.stage_ledger if row['stage']=='ordinary_regression']
 negative=public_records[-1]
 if negative['exact_test_coverage'] or negative['completed_guarded_coverage'] or negative['passed'] or negative['assertions_executed']:raise RuntimeError('ACTUAL_INITIAL_COVERAGE_OR_GOAL_OUTCOME_REWRITTEN')
 if set(negative['pytest']['outcomes'])!=set(env.public_regression_nodes):raise RuntimeError('ACTUAL_GOAL_OUTCOMES_FABRICATED')
 save(D/'ACTUAL_CODER_C0_PUBLIC_QUERY.json',{'native_record':negative,'environment_certificate_event':certified[0],'diagnostic_acceptance_event':accepted[0],'native_delta':1,'author_tool_row':rows[-1],'raw_negative_returned_to_actor':True,'final_acceptance_NOT_GRANTED':True})
 checkpoint('ACTUAL_ORIGINAL_TESTER_INITIAL_ORDINARY_CACHE')
 tester_root=bridge.owned/'w/tester_initial';tester_root.parent.mkdir(parents=True,exist_ok=True)
 core.snapshot_copy(initial,tester_root,business,initial_digest)
 before_native=env.native_calls
 cached=bridge.public_runner(tester_root,list(env.public_regression_nodes))
 if cached!=ordinary or env.native_calls!=before_native:raise RuntimeError('INITIAL_V3_ORIGINAL_TESTER_CACHE_NOT_ACTUAL_OR_NEW_NATIVE_EXECUTED')
 if not any(row['stage']=='certified_public_failure_cache_reuse' for row in env.stage_ledger):raise RuntimeError('ORIGINAL_ENV_CACHE_EVENT_MISSING')
 strict_checks=[]
 for label,modify in [('generated',None),('timeout',lambda n:n.update(timeout=True)),('guard',lambda n:n.update(guard_loaded=False)),('exact_unknown',lambda n:n.pop('exact_test_coverage')),('goal_fabricated',lambda n:n['pytest']['outcomes'].update({env.recovery_goal_nodes[0]:{'status':'failed'}}))]:
  trial=copy.deepcopy(negative)
  if modify:modify(trial)
  allowed=bridge._known_initial_source_negative(trial,generated=(label=='generated')) is not None
  strict_checks.append({'label':label,'diagnostic_allowed':allowed})
  if allowed:raise RuntimeError('INVALID_OR_NON_C0_DIAGNOSTIC_ACCEPTED '+label)
 mutation=env.repo_root/certificate['observed_syntax']['business_relative'];previous_bytes=mutation.read_bytes();mutation.write_bytes(previous_bytes+b'\n')
 try:
  if bridge._known_initial_source_negative(negative) is not None:raise RuntimeError('NON_C0_SOURCE_DIAGNOSTIC_ACCEPTED')
 finally:mutation.write_bytes(previous_bytes)
 strict_checks.append({'label':'non_C0_source','diagnostic_allowed':False,'bytes_restored':sha(mutation)==certificate['observed_syntax']['sha256']})
 save(D/'ACTUAL_INITIAL_ORDINARY_CACHE_PROBE.json',{'requested_ordinary_ids':list(env.public_regression_nodes),'answer':cached,'current_C0_122_exact':True,'new_native_calls':env.native_calls-before_native,'cache_is_original_environment_probe_cache':True,'strict_checks':strict_checks,'only_observer_copy_touched_and_restored':True,'model_and_private_calls':0})
 checkpoint('ACTUAL_SCOPE_FALLBACK_PROBE')
 # This trusted observer fixture intentionally bypasses the actor AST filter to
 # exercise runtime fallback. All outside artifacts are harmless owned sentinels.
 artifacts=D/'synthetic_artifacts';artifacts.mkdir(exist_ok=True)
 for name in ('private.txt','othercase.txt','root_grant.json','selected.json','llm_response.json'):(artifacts/name).write_text('SYNTHETIC_ONLY_NOT_SCIENCE','utf-8')
 probe='''import os,json,sys,importlib
from pathlib import Path
import importlib.machinery
package=importlib.import_module(PACKAGE_LITERAL)
abi={'version':sys.version,'version_info':list(sys.version_info[:3]),'executable':sys.executable,'base_executable':getattr(sys,'_base_executable',None),'package':PACKAGE_LITERAL,'package_file':package.__file__,'package_version':getattr(package,'__version__',None),'extension_suffixes':importlib.machinery.EXTENSION_SUFFIXES}
if PACKAGE_LITERAL=='mypy':
 version_module=importlib.import_module('mypy.version')
 abi.update(package_version=version_module.__version__,package_version_file=version_module.__file__)
print(json.dumps({'V3_NATIVE_ABI':abi}))
out=Path(os.environ['EXP166_REPRO_OUTPUT']); results=[]
def expect(label,fn,allowed):
 try:
  fn();actual=True;error=None
 except PermissionError as exc:
  actual=False;error=str(exc)
 results.append({'label':label,'allowed':actual,'expected':allowed,'error':error})
 if actual!=allowed:raise AssertionError(label)
own=out/'owned_probe.txt'
expect('owned_write',lambda:own.write_text('owned'),True)
expect('owned_read',lambda:own.read_text(),True)
expect('owned_list',lambda:list(out.iterdir()),True)
expect('owned_chmod',lambda:os.chmod(own,384),True)
expect('owned_truncate',lambda:os.truncate(own,0),True)
expect('link_denied',lambda:os.link(own,out/'hardlink.txt'),False)
expect('symlink_denied',lambda:os.symlink(own,out/'symlink.txt'),False)
expect('log_write_denied',lambda:(out/'generated_scope_events.jsonl').write_text('tamper'),False)
expect('log_truncate_denied',lambda:os.truncate(out/'generated_scope_events.jsonl',0),False)
expect('frozen_denied',lambda:(Path(os.environ['EXP129_FROZEN_ROOT'])/'synthetic_unreadable_marker.txt').read_text(),False)
ARTIFACTS_PLACEHOLDER
print(json.dumps({'V3_RUNTIME_SCOPE_PROBE':results}))
'''
 probe=probe.replace('PACKAGE_LITERAL',repr(env.package))
 probe=probe.replace('ARTIFACTS_PLACEHOLDER','\n'.join("expect("+repr(name)+",lambda:Path("+repr(str(artifacts/name))+").read_text(),False)" for name in ('private.txt','othercase.txt','root_grant.json','selected.json','llm_response.json')))
 snap=bridge.snapshot_clone(root,'scope_current_C0')
 probe_result=env.run_reproduction(probe,snapshot=snap,label='v3_scope_runtime_probe')
 bridge._valid(probe_result['native_record'],generated=True)
 if probe_result['exit_code']!=0:raise RuntimeError('ACTUAL_SCOPE_FALLBACK_PROBE_FAILED '+probe_result.get('stderr','')+' '+probe_result.get('stdout',''))
 save(D/'ACTUAL_RUNTIME_SCOPE_PROBE.json',probe_result)
 await executor.close_tools()

try:
 asyncio.run(run_tools())
 checkpoint('ACTUAL_FULL_FIRST_BODY_CAPTURE')
 class BodyCaptured(BaseException):pass
 class Capture:
  @staticmethod
  def generate(capture_env,body,role,phase):
   save(D/'ACTUAL_FIRST_BODY_11134.json',body)
   finance=module('ea239_v3_readonly_finance',ROOT/'工作区/1009-research-resume/finance/resume_transport.py')
   config=read(E/'finance_config239.json');transport=finance.make_transport(config)
   state=transport.io.read();pending=transport.validate(state,phase)
   names=transport.io.m.atomic.__code__.co_names
   save(D/'ACTUAL_FIRST_BODY_RECEIPT_11134.json',{'canonical_body_sha256':digest(body),'body_bytes':len(canonical(body).encode()),'tools':[t['function']['name'] for t in body['tools']],'tool_choice':body['tool_choice'],'phase':phase,'bounds':finance.bounds(body,config),'scoped_factory_actual_constructed':True,'single_atomic_replace_retry':names.count('replace_retry')==1,'readonly_pending_validation':True,'pending_count':len(pending),'old_prefix_records':config['old_record_count'],'POSTs':0,'no_fabricated_model_response':True})
   if names.count('replace_retry')!=1:raise RuntimeError('SCOPED_SINGLE_ATOMIC_NOT_VERIFIED')
   raise BodyCaptured()
 import backend225
 previous=backend225.module
 backend225.module=lambda name,path:Capture if Path(path).resolve()==TRANSPORT.resolve() else previous(name,path)
 control235.MECHANICAL_NAMESPACE='qualified_capture_v3_'+str(os.getpid())
 try:worker.run(TASK,control235.PHASE)
 except BodyCaptured:pass
 else:raise RuntimeError('ACTUAL_FIRST_BODY_NOT_REACHED')
 save(RESULT,{'status':'ACTUAL_NATIVE_TOOL_C0_SCOPE_FIRSTBODY_PASS','at_utc':now(),'task':TASK,'driver_sha256':sha(pathlib.Path(__file__)),'tools':rows,'C0':read(D/'C0_CURRENT_11134.json'),'first_body_receipt':read(D/'ACTUAL_FIRST_BODY_RECEIPT_11134.json'),'scope_probe':str(D/'ACTUAL_RUNTIME_SCOPE_PROBE.json'),'native_calls':env.native_calls,'business_restored':core.digest(root,business)==initial_digest,'POSTs':0,'private_calls':0,'scientific_success_not_claimed':True})
 checkpoint('DRIVER_COMPLETE_WAIT_PARENT_JOB_STOP',result=str(RESULT))
 print(canonical({'status':'QUALIFICATION_PASS_PENDING_SUPERVISOR_STOP','result':str(RESULT),'POSTs':0,'private_calls':0}))
except BaseException as exc:
 checkpoint('DRIVER_FAILED',error_type=type(exc).__name__,error=str(exc))
 raise
finally:owner.close()

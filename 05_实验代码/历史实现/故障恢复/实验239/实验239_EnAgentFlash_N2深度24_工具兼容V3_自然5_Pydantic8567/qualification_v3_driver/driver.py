"""Root-authorized qualification only: actual tools/native, no LLM or private."""
import pathlib,sys,json,asyncio,copy,hashlib,os,datetime
E=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(E))
from common166 import *
import control235
control235.start_mechanical()
control235.MECHANICAL_NAMESPACE='qualified_v3_'+str(os.getpid())
import entry239
worker=entry239.install();TASK='pydantic__pydantic-8567';control235.verify(TASK,control235.PHASE)
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
 checkpoint('CURRENT_C0_PUBLIC_NATIVE')
 ordinary=bridge.public_runner(root,list(env.public_regression_nodes));c0=read(env.native_records[-1]['path'])
 if set(ordinary.values())!={'PASS'} or c0['passed'] is not False or not c0['completed_guarded_coverage']:raise RuntimeError('CURRENT_C0_NOT_REAL_FAIL_WITH_ORDINARY_PASS')
 save(D/'C0_CURRENT_8567.json',{'ordinary':ordinary,'native_record':env.native_records[-1],'actual_product':c0['pytest'].get('product_import'),'actual_outcome_count':len(c0['pytest']['outcomes']),'statuses':{s:sum(v['status']==s for v in c0['pytest']['outcomes'].values()) for s in ('passed','failed')},'STOP':c0['stop_receipt']})
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
if PACKAGE_LITERAL=='pydantic':
 core=importlib.import_module('pydantic_core');extension=importlib.import_module('pydantic_core._pydantic_core')
 abi.update(pydantic_core_version=core.__version__,pydantic_core_file=core.__file__,compiled_extension_file=extension.__file__,compiled_extension_suffix=next((s for s in importlib.machinery.EXTENSION_SUFFIXES if extension.__file__.endswith(s)),None))
 if sys.version_info[:2]!=(3,11) or not extension.__file__.endswith('.cp311-win_amd64.pyd') or core.__version__!='2.15.0':raise AssertionError('CURRENT_PYDANTIC_NATIVE_ABI_MISMATCH')
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
   save(D/'ACTUAL_FIRST_BODY_8567.json',body)
   finance=module('ea239_v3_readonly_finance',ROOT/'工作区/1009-research-resume/finance/resume_transport.py')
   config=read(E/'finance_config239.json');transport=finance.make_transport(config)
   state=transport.io.read();pending=transport.validate(state,phase)
   names=transport.io.m.atomic.__code__.co_names
   save(D/'ACTUAL_FIRST_BODY_RECEIPT_8567.json',{'canonical_body_sha256':digest(body),'body_bytes':len(canonical(body).encode()),'tools':[t['function']['name'] for t in body['tools']],'tool_choice':body['tool_choice'],'phase':phase,'bounds':finance.bounds(body,config),'scoped_factory_actual_constructed':True,'single_atomic_replace_retry':names.count('replace_retry')==1,'readonly_pending_validation':True,'pending_count':len(pending),'old_prefix_records':config['old_record_count'],'POSTs':0,'no_fabricated_model_response':True})
   if names.count('replace_retry')!=1:raise RuntimeError('SCOPED_SINGLE_ATOMIC_NOT_VERIFIED')
   raise BodyCaptured()
 import backend225
 previous=backend225.module
 backend225.module=lambda name,path:Capture if Path(path).resolve()==TRANSPORT.resolve() else previous(name,path)
 control235.MECHANICAL_NAMESPACE='qualified_capture_v3_'+str(os.getpid())
 try:worker.run(TASK,control235.PHASE)
 except BodyCaptured:pass
 else:raise RuntimeError('ACTUAL_FIRST_BODY_NOT_REACHED')
 save(RESULT,{'status':'ACTUAL_NATIVE_TOOL_C0_SCOPE_FIRSTBODY_PASS','at_utc':now(),'task':TASK,'driver_sha256':sha(pathlib.Path(__file__)),'tools':rows,'C0':read(D/'C0_CURRENT_8567.json'),'first_body_receipt':read(D/'ACTUAL_FIRST_BODY_RECEIPT_8567.json'),'scope_probe':str(D/'ACTUAL_RUNTIME_SCOPE_PROBE.json'),'native_calls':env.native_calls,'business_restored':core.digest(root,business)==initial_digest,'POSTs':0,'private_calls':0,'scientific_success_not_claimed':True})
 checkpoint('DRIVER_COMPLETE_WAIT_PARENT_JOB_STOP',result=str(RESULT))
 print(canonical({'status':'QUALIFICATION_PASS_PENDING_SUPERVISOR_STOP','result':str(RESULT),'POSTs':0,'private_calls':0}))
except BaseException as exc:
 checkpoint('DRIVER_FAILED',error_type=type(exc).__name__,error=str(exc))
 raise
finally:owner.close()

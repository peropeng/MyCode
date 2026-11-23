"""Real author tools and first-controller-body capture, no generated response."""
from common166 import *
import control235
control235.start_mechanical()
import entry235
entry235.install()
worker=entry235.worker
import asyncio,copy
TASK='Project-MONAI__MONAI-2238'
class BodyCaptured(BaseException):pass
class Capture:
 @staticmethod
 def generate(env,body,role,phase):
  save(E/'first_actual_body235.json',body)
  save(E/'first_body_capture235.json',{'task_id':TASK,'body_sha256':digest(body),'body_bytes':len(canonical(body).encode()),'messages':len(body['messages']),'original_tool_names':[t['function']['name'] for t in body.get('tools',[])],'max_output_tokens':body['max_tokens'],'actual_model_POSTs':0,'logical_request_construction':1,'no_response_or_tool_invented':True,'old_outputs_reused':False})
  raise BodyCaptured()
def main():
 begin=time.time();p=control235.authorization()
 ref=copy.deepcopy(next(x for x in read(worker.PEER/'data/selected_task_bindings.json')['tasks'] if x['task_id']==TASK))
 ref.update(_output_namespace=control235.MECHANICAL_NAMESPACE+'/tools',_native_namespace=control235.MECHANICAL_NAMESPACE+'/native')
 env=worker.CommonEnvironment(ref,'EA235_MECHANICAL_NO_MODEL')
 from native_guard_compat225 import install
 install(env)
 bridge=entry235.Bridge235(env);owner=worker.ShellOwner(bridge)
 core=worker.module('exp225_frozen_enagent',worker.OLD175/'enagent_native.py')
 initial=bridge.export();business=sorted(bridge.initial);root=bridge.owned/'tools_actor'
 core.snapshot_copy(initial,root,business,core.digest(initial,business))
 class NoModel:
  def request(self,payload):raise RuntimeError('MECHANICAL_MODEL_DISABLED')
 core.ACTIVE.context=core.Context(root,NoModel(),bridge.command_runner,bridge.edit_guard,[worker.CERT],{'business_paths':business,'business_sha256':core.digest(initial,business)})
 worker.shim.install(core,command_guard=bridge.command_guard,shell_launcher=owner.launch,record=lambda x:env.record('actual_mechanical_author_tools235',x),product_python=lambda r:env._paths['python'],native_command=bridge.native_command,path_map=bridge.path_map,neutral_output=bridge.neutral)
 before=core.digest(root,business);answers=[]
 async def check():
  tools=[core.NS.tools_registry[n](model_provider='openai') for n in ('bash','str_replace_based_edit_tool')];executor=core.ToolExecutor(tools)
  steps=[('bash',{'command':'pwd'}),('str_replace_based_edit_tool',{'command':'create','path':'/tmp/test_deploy235.py','file_text':'import monai\nprint("EA235_PRODUCT_OK")\n'}),('str_replace_based_edit_tool',{'command':'view','path':'/tmp/test_deploy235.py'}),('str_replace_based_edit_tool',{'command':'str_replace','path':'/tmp/test_deploy235.py','old_str':'EA235_PRODUCT_OK','new_str':'EA235_CHANGED'}),('str_replace_based_edit_tool',{'command':'undo_edit','path':'/tmp/test_deploy235.py'}),('bash',{'command':'python /tmp/test_deploy235.py'})]
  for i,(name,args) in enumerate(steps):
   x=(await executor.sequential_tool_call([core.ToolCall(name=name,call_id=str(i),arguments=args,id=str(i))]))[0]
   answers.append({'tool':name,'arguments':args,'success':x.success,'result':x.result,'error':x.error})
   if not x.success:raise RuntimeError('ACTUAL_TOOL_FAILURE '+str(answers[-1]))
  assert 'EA235_PRODUCT_OK' in answers[-1]['result'] and core.digest(root,business)==before
  await executor.close_tools()
 try:
  asyncio.run(check())
  ordinary=list(env.public_regression_nodes)[:1];outcomes=bridge.public_runner(root,ordinary)
  assert set(outcomes)==set(ordinary) and set(outcomes.values())=={'PASS'}
  # Replay one actual new native feedback string through the same bridge projection.
  from relative_traceback_projection228 import neutral_relative_traceback
  relative=os.path.relpath(env.repo_root,env._paths['frozen'])
  projected=bridge.neutral(root,relative+os.sep+env.package+os.sep+'example.py:1: E RuntimeError: preserved')
  assert relative not in projected and 'RuntimeError: preserved' in projected and '/workspace/repo' in projected
  save(E/'mechanical_receipt235.json',{'status':'AUTHOR_TOOLS_PRODUCT_ENV_ORDINARY_NATIVE_PASS','at_utc':now(),'tools':answers,'public_ordinary_nodes':ordinary,'public_ordinary_outcomes':outcomes,'actual_product_python':str(env._paths['python']),'business_digest_unchanged':core.digest(root,business)==before,'full_business_paths':len(business),'short_actor_root':str(root),'max_business_path_characters':max(len(str(root/x)) for x in business),'actual_native_calls':env.native_calls,'model_POSTs':0,'private_calls':0,'all_shell_Jobs_closed':all(x.closed for x in owner.processes),'traceback_prefix':relative,'projected_traceback':projected,'elapsed_seconds':time.time()-begin,'native_records_attribute_available':hasattr(env,'public_native_records'),'native_records_from_stage_ledger':True})
 finally:owner.close()
 # Enter the actual N3 controller, stop exactly at its first real request body.
 import backend225
 original=backend225.module
 def captured(name,path):return Capture if Path(path).resolve()==TRANSPORT.resolve() else original(name,path)
 backend225.module=captured
 try:worker.run(TASK,control235.PHASE)
 except BodyCaptured:pass
 else:raise RuntimeError('FIRST_ACTUAL_REQUEST_BOUNDARY_NOT_REACHED')
 print(canonical({'mechanical_native':env.native_calls,'model_POSTs':0,'first_body_captured':True,'elapsed_seconds':time.time()-begin}),flush=True)
if __name__=='__main__':main()

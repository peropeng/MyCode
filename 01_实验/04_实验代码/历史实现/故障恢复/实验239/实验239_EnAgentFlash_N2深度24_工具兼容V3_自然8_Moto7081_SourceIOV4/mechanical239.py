"""Actual author editor/native and full first body, no fabricated generation."""
from common166 import *
import control235
control235.start_mechanical()
import entry239
worker=entry239.install()
import asyncio,copy
TASK='Project-MONAI__MONAI-2238'
class BodyCaptured(BaseException):pass
class Capture:
 @staticmethod
 def generate(env,body,role,phase):
  save(E/('first_body_'+TASK+'.json'),body)
  transport=module('exp239_finance_bounds',ROOT/'工作区/1009-research-resume/finance/resume_transport.py')
  config=read(ROOT/'工作区/1009-research-resume/finance/finance_config_template.json')
  b=transport.bounds(body,config)
  save(E/('first_body_receipt_'+TASK+'.json'),{'task_id':TASK,'body_sha256':digest(body),'body_bytes':len(canonical(body).encode()),'tools':[t['function']['name'] for t in body.get('tools',[])],'tool_choice':body.get('tool_choice'),'bounds':b,'POSTs':0,'no_response_fabricated':True})
  raise BodyCaptured()
def main():
 global TASK
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--task',default=TASK);a.add_argument('--capture',action='store_true');args=a.parse_args();TASK=args.task
 control235.MECHANICAL_NAMESPACE=('capture_'+TASK if args.capture else 'mechanical')+'_'+str(os.getpid())
 if not args.capture:
  ref=copy.deepcopy(next(x for x in read(worker.PEER/'data/selected_task_bindings.json')['tasks'] if x['task_id']==TASK))
  ref.update(_output_namespace=control235.MECHANICAL_NAMESPACE+'/tools',_native_namespace=control235.MECHANICAL_NAMESPACE+'/native')
  env=worker.CommonEnvironment(ref,'EA239_MECHANICAL_NO_MODEL')
  from native_guard_compat225 import install
  install(env)
  bridge=worker.Bridge(env);owner=worker.ShellOwner(bridge)
  core=worker.module('exp225_frozen_enagent',worker.OLD175/'enagent_native.py')
  initial=bridge.export();business=sorted(bridge.initial);root=bridge.owned/'tools_actor'
  core.snapshot_copy(initial,root,business,core.digest(initial,business))
  class NoModel:
   def request(self,payload):raise RuntimeError('MECHANICAL_MODEL_DISABLED')
  core.ACTIVE.context=core.Context(root,NoModel(),bridge.command_runner,bridge.edit_guard,[worker.CERT],{'business_paths':business,'business_sha256':core.digest(initial,business)})
  worker.shim.install(core,command_guard=bridge.command_guard,shell_launcher=owner.launch,record=lambda x:env.record('mechanical_author_tools239',x),product_python=lambda r:env._paths['python'],native_command=bridge.native_command,path_map=bridge.path_map,neutral_output=bridge.neutral)
  answers=[];before=core.digest(root,business)
  async def check():
   tools=[core.NS.tools_registry[n](model_provider='openai') for n in ('bash','str_replace_based_edit_tool')];executor=core.ToolExecutor(tools)
   steps=[('bash',{'command':'pwd'}),('str_replace_based_edit_tool',{'command':'view','path':'/workspace/'+bridge.public_aliases()[1]+'/monai/networks/blocks/convolutions.py','view_range':[1,3]}),('str_replace_based_edit_tool',{'command':'create','path':'/tmp/test_deploy239.py','file_text':'import monai\nprint("EA239_PRODUCT_OK")\n'}),('str_replace_based_edit_tool',{'command':'str_replace','path':'/tmp/test_deploy239.py','old_str':'EA239_PRODUCT_OK','new_str':'EA239_CHANGED'}),('str_replace_based_edit_tool',{'command':'undo_edit','path':'/tmp/test_deploy239.py'}),('bash',{'command':'python /tmp/test_deploy239.py'})]
   for i,(name,args) in enumerate(steps):
    x=(await executor.sequential_tool_call([core.ToolCall(name=name,call_id=str(i),arguments=args,id=str(i))]))[0]
    answers.append({'tool':name,'arguments':args,'success':x.success,'result':x.result,'error':x.error})
    if not x.success:raise RuntimeError('ACTUAL_TOOL_FAILURE '+str(answers[-1]))
   assert 'EA239_PRODUCT_OK' in answers[-1]['result'] and core.digest(root,business)==before
   await executor.close_tools()
  try:
   asyncio.run(check())
   ordinary=list(env.public_regression_nodes)[:1];outcomes=bridge.public_runner(root,ordinary)
   assert set(outcomes)==set(ordinary) and set(outcomes.values())=={'PASS'}
   save(E/'mechanical_receipt239.json',{'status':'AUTHOR_TOOLS_PRODUCT_NATIVE_PASS','at_utc':now(),'tools':answers,'ordinary':outcomes,'business_digest_unchanged':core.digest(root,business)==before,'full_business_paths':len(business),'actual_native_calls':env.native_calls,'POSTs':0,'private_calls':0})
  finally:owner.close()
 import backend225
 original=backend225.module
 def captured(name,path):return Capture if Path(path).resolve()==TRANSPORT.resolve() else original(name,path)
 backend225.module=captured
 try:worker.run(TASK,control235.PHASE)
 except BodyCaptured:pass
 else:raise RuntimeError('FIRST_ACTUAL_REQUEST_BOUNDARY_NOT_REACHED')
 print(canonical({'task':TASK,'POSTs':0,'first_body_captured':True}),flush=True)
if __name__=='__main__':main()

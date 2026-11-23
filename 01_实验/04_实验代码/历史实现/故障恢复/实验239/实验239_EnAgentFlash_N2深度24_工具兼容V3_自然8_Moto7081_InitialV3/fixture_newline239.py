"""Actual frozen author operations verify LF/CRLF/Undo exact bytes, 0 models."""
from common166 import *
import control235
control235.start_mechanical();control235.MECHANICAL_NAMESPACE='newline_fixture_'+str(os.getpid())
import entry239
worker=entry239.install()
import asyncio,copy
def main():
 task='dask__dask-9378';ref=copy.deepcopy(next(x for x in read(worker.PEER/'data/selected_task_bindings.json')['tasks'] if x['task_id']==task))
 ref.update(_output_namespace=control235.MECHANICAL_NAMESPACE+'/tools',_native_namespace=control235.MECHANICAL_NAMESPACE+'/n')
 env=worker.CommonEnvironment(ref,'EA239_NEWLINE_MECHANICAL_NO_MODEL')
 bridge=worker.Bridge(env);owner=worker.ShellOwner(bridge)
 core=worker.module('exp225_frozen_enagent',worker.OLD175/'enagent_native.py')
 initial=bridge.export();business=sorted(bridge.initial);root=bridge.owned/'tools_actor'
 core.snapshot_copy(initial,root,business,core.digest(initial,business))
 class NoModel:
  def request(self,payload):raise RuntimeError('MECHANICAL_MODEL_DISABLED')
 core.ACTIVE.context=core.Context(root,NoModel(),bridge.command_runner,bridge.edit_guard,[worker.CERT],{'business_paths':business,'business_sha256':core.digest(initial,business)})
 worker.shim.install(core,command_guard=bridge.command_guard,shell_launcher=owner.launch,record=lambda x:env.record('actual_newline_fixture239',x),product_python=lambda r:env._paths['python'],native_command=bridge.native_command,path_map=bridge.path_map,neutral_output=bridge.neutral)
 before=core.digest(root,business);rows=[]
 async def check():
  executor=core.ToolExecutor([core.NS.tools_registry['str_replace_based_edit_tool'](model_provider='openai')])
  for label,nl in [('LF',b'\n'),('CRLF',b'\r\n')]:
   path=root/'generated_tests'/('fixture_'+label+'.py');path.parent.mkdir(parents=True,exist_ok=True)
   original=nl.join([b'alpha = 1',b'beta = 2',b'']);path.write_bytes(original)
   expected=original.replace(b'alpha = 1',b'alpha = 3')
   inserted=nl.join([b'alpha = 3',b'gamma = 4',b'beta = 2',b''])
   steps=[({'command':'str_replace','path':str(path),'old_str':'alpha = 1','new_str':'alpha = 3'},expected),({'command':'insert','path':str(path),'insert_line':1,'new_str':'gamma = 4'},inserted),({'command':'undo_edit','path':str(path)},expected),({'command':'undo_edit','path':str(path)},original)]
   for i,(args,exact) in enumerate(steps):
    result=(await executor.sequential_tool_call([core.ToolCall(name='str_replace_based_edit_tool',call_id=label+str(i),arguments=args,id=label+str(i))]))[0]
    actual=path.read_bytes();rows.append({'profile':label,'command':args['command'],'success':result.success,'actual_sha256':hashlib.sha256(actual).hexdigest(),'expected_sha256':hashlib.sha256(exact).hexdigest(),'exact_bytes':actual==exact,'model_argument_unchanged':True})
    assert result.success and actual==exact,rows[-1]
  create=root/'generated_tests'/'fixture_create.py';text='alpha = "café"\nbeta = 2\n'
  result=(await executor.sequential_tool_call([core.ToolCall(name='str_replace_based_edit_tool',call_id='create',arguments={'command':'create','path':str(create),'file_text':text},id='create')]))[0]
  rows.append({'profile':'new_LF_UTF8','command':'create','success':result.success,'exact_bytes':create.read_bytes()==text.encode('utf-8')})
  assert result.success and create.read_bytes()==text.encode('utf-8')
  await executor.close_tools()
 try:
  asyncio.run(check());assert core.digest(root,business)==before
  save(E/'newline_fixture_receipt239.json',{'status':'ACTUAL_AUTHOR_STRREPLACE_INSERT_UNDO_CREATE_EXACT_BYTES_PASS','at_utc':now(),'rows':rows,'original_business_digest_unchanged':True,'original_content_operation_methods_unchanged':True,'model_POSTs':0,'public_native':0,'private_calls':0,'LF_and_CRLF_existing':True,'mixed_newline':'original writer fallback with explicit deployment event, preservation not asserted'})
 finally:owner.close()
 print(canonical({'fixture':'PASS','rows':len(rows),'POSTs':0,'private':0}))
if __name__=='__main__':main()

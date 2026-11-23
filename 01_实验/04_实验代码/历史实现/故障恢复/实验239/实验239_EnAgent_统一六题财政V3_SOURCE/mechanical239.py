"""Root-authorized exact-task first request capture, no model response or POST."""
from common166 import *
import control235,entry_sourceio_v4_239
class BodyCaptured(BaseException):pass
class Capture:
 @staticmethod
 def generate(env,body,role,phase):
  p=read(E/'protocol225.json');provider=module('ea239_pure_completion_bounds',p['finance_transport'])
  config=read(E/'finance_config239.json');body=provider.common.inject(body,config,env.task_id);b=provider.bounds(body,config)
  save(E/('actual_first_body_'+env.task_id+'.json'),body)
  save(E/('actual_first_body_receipt_'+env.task_id+'.json'),{'task_id':env.task_id,'body_sha256':digest(body),'body_bytes':len(canonical(body).encode()),'tools':[t['function']['name'] for t in body.get('tools',[])],'tool_choice':body.get('tool_choice'),'bounds':b,'Root_common_v4_injection_applied_before_capture':True,'env_time_left':env.time_left(),'global_deadline':None,'finite_flow_deadline':env.deadline,'POSTs':0,'no_response_fabricated':True,'no_IO_factory_or_ledger_read':True})
  raise BodyCaptured()
def main():
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--task',required=True);a.add_argument('--capture',action='store_true');args=a.parse_args()
 control235.start_mechanical();control235.verify(args.task,control235.PHASE)
 control235.MECHANICAL_NAMESPACE='capture_completion_'+args.task+'_'+str(os.getpid())
 worker=entry_sourceio_v4_239.install();import backend225
 original=backend225.module
 backend225.module=lambda name,path:Capture if Path(path).resolve()==TRANSPORT.resolve() else original(name,path)
 try:worker.run(args.task,control235.PHASE)
 except BodyCaptured:pass
 else:raise RuntimeError('FIRST_ACTUAL_REQUEST_BOUNDARY_NOT_REACHED')
 print(canonical({'task':args.task,'POSTs':0,'first_body_captured':True}),flush=True)
if __name__=='__main__':main()

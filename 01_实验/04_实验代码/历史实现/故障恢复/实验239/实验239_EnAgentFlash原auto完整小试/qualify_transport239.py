"""Exercise exact actual finance inheritance, file writes and current ledger, no HTTP."""
from common166 import *
from types import SimpleNamespace
def main():
 transport=module('exp239_resume_finance',ROOT/'工作区/1009-research-resume/finance/resume_transport.py')
 config=read(E/'finance_config239.json');t=transport.make_transport(config)
 s=t.io.read();pending=t.validate(s,'EnAgentResume23920261009')
 before=digest(s)
 for i,task in enumerate(read(E/'protocol225.json')['task_order']):
  body=read(E/('first_body_'+task+'.json'));b=transport.bounds(body,config)
  t.cap_check(s,'EnAgentResume23920261009',b)
  env=SimpleNamespace(out=E/'transport_qualification'/task,calls=i+1)
  # Persist this actual captured author body through the exact production IO.
  t.io.request(env,'MECHANICAL_FIRST_BODY',body,b,'NOT_AN_API_KEY')
  assert (env.out/'llm'/('%03d_request.json'%(i+1))).is_file()
 assert digest(t.io.read())==before,'READONLY_QUALIFICATION_MUTATED_LEDGER'
 save(E/'transport_qualification239.json',{'status':'EXACT_TRANSPORT_IO_CONSTRUCTION_VALIDATE_AND_ARTIFACT_WRITE_PASS','at_utc':now(),'phase':'EnAgentResume23920261009','old_records':config['old_record_count'],'records':len(s['reservations']),'spent_CNY':s['spent_CNY'],'held_CNY':s['held_CNY'],'pending':len(pending),'ledger_unchanged':True,'http_POSTs':0,'balance_GETs':0,'artifact_inside_owned_E':True,'actual_shared_IO_class':type(t.io).__name__,'phase_cap_CNY':s['pilots']['EnAgentResume23920261009']['cap_CNY'],'credential_in_execution_environment':bool(os.environ.get('DEEPSEEK_API_KEY'))})
 print(canonical({'status':'PASS','POSTs':0,'pending':len(pending),'key_available':bool(os.environ.get('DEEPSEEK_API_KEY'))}))
if __name__=='__main__':main()

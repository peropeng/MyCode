"""Exercise exact actual finance inheritance, file writes and current ledger, no HTTP."""
from common166 import *
from types import SimpleNamespace
def main():
 transport=module('exp239_resume_finance',ROOT/'工作区/1009-research-resume/finance/resume_transport.py')
 config=read(E/'finance_config239.json');t=transport.make_transport(config)
 def no_shared_write(*args,**kwargs):raise RuntimeError('READONLY_QUALIFICATION_SHARED_WRITE_FORBIDDEN')
 t.io.write=no_shared_write;t.io.event=no_shared_write;t.io.block=no_shared_write
 s=t.io.read();pending=t.validate(s,read(E/'protocol225.json')['finance_phase'])
 before=digest(s)
 for i,task in enumerate(read(E/'protocol225.json')['task_order'][:2]):
  body=read(E/('first_body_'+task+'.json'));b=transport.bounds(body,config)
  t.cap_check(s,read(E/'protocol225.json')['finance_phase'],b)
  env=SimpleNamespace(out=E/'transport_qualification'/task,calls=i+1)
  # Persist this actual captured author body through the exact production IO.
  t.io.request(env,'MECHANICAL_FIRST_BODY',body,b,'NOT_AN_API_KEY')
  assert (env.out/'llm'/('%03d_request.json'%(i+1))).is_file()
 unchanged=digest(t.io.read())==before
 save(E/'transport_qualification239.json',{'status':'EXACT_TRANSPORT_IO_CONSTRUCTION_VALIDATE_AND_ARTIFACT_WRITE_PASS','at_utc':now(),'phase':read(E/'protocol225.json')['finance_phase'],'old_records':config['old_record_count'],'records':len(s['reservations']),'spent_CNY':s['spent_CNY'],'held_CNY':s['held_CNY'],'pending':len(pending),'shared_write_methods_disabled':True,'ledger_snapshot_unchanged':unchanged,'concurrent_other_phase_updates_permitted':not unchanged,'http_POSTs':0,'balance_GETs':0,'artifact_inside_owned_E':True,'actual_shared_IO_class':type(t.io).__name__,'phase_cap_CNY':s['pilots'][read(E/'protocol225.json')['finance_phase']]['cap_CNY'],'credential_in_execution_environment':bool(os.environ.get('DEEPSEEK_API_KEY'))})
 print(canonical({'status':'PASS','POSTs':0,'pending':len(pending),'key_available':bool(os.environ.get('DEEPSEEK_API_KEY'))}))
if __name__=='__main__':main()

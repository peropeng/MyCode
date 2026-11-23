"""Serial owned child process with durable logs and absolute10Beijing timeout."""
import subprocess,traceback
from common import *

def run_child(script,*args):
 require_time(new_long_task=script in ('trainer157.py','predict157.py'))
 cmd=[str(PYTHON),'-B',str(E/script),*args]
 append(E/'process_events.jsonl',{'at_utc':now(),'event':'START_CHILD','cmd':cmd,'remaining_seconds':remaining()})
 logfile=E/'logs'/(script.removesuffix('.py')+'.log');logfile.parent.mkdir(exist_ok=True)
 try:
  with logfile.open('a',encoding='utf-8') as log:
   result=subprocess.run(cmd,cwd=W,stdout=log,stderr=subprocess.STDOUT,timeout=max(.1,remaining()),check=False)
  append(E/'process_events.jsonl',{'at_utc':now(),'event':'CHILD_EXIT','cmd':cmd,'code':result.returncode,'log':str(logfile)})
  if result.returncode:raise RuntimeError('Child failed '+script+' code '+str(result.returncode)+'; log '+str(logfile))
 except Exception as exc:
  append(E/'process_events.jsonl',{'at_utc':now(),'event':'CHILD_STOP','cmd':cmd,'error':str(exc),'type':type(exc).__name__,'traceback':traceback.format_exc()})
  raise
 print(canonical({'Exp157':'CHILD_EXIT0','script':script,'args':args,'log':str(logfile)}),flush=True)

if __name__=='__main__':
 run_child('trainer157.py','run')

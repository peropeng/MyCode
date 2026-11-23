"""Serial analytic children constrained by the10Beijing cutoff."""
import subprocess,traceback
from common import *
def run_child(script):
 require_time(new_long_task=script=='predict156.py')
 cmd=[str(PYTHON),'-B',str(E/script)]
 append(E/'process_events.jsonl',{'at_utc':now(),'event':'START_CHILD','cmd':cmd,'remaining_seconds':remaining()})
 result=subprocess.run(cmd,cwd=W,timeout=max(.1,remaining()),check=False)
 append(E/'process_events.jsonl',{'at_utc':now(),'event':'CHILD_EXIT','cmd':cmd,'code':result.returncode})
 if result.returncode:raise RuntimeError('Child failed '+script+' code '+str(result.returncode))
def run():
 try:
  for script in ('predict156.py','evaluate156.py','diagnostics156.py','finalize156.py'):run_child(script)
 except Exception as exc:
  append(E/'process_events.jsonl',{'at_utc':now(),'event':'LAUNCHER_STOP','error':str(exc),'type':type(exc).__name__,'traceback':traceback.format_exc()});raise
if __name__=='__main__':run()

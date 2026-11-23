"""One child at a time; every execution timeout uses the absolute cutoff."""
import subprocess,traceback
from common import *
def run_child(script,*args):
 require_time(new_long_task=script=='trainer153.py')
 cmd=[str(PYTHON),'-B',str(E/script),*args]
 append(E/'process_events.jsonl',{'at_utc':now(),'event':'START_CHILD','cmd':cmd,'remaining_seconds':remaining()})
 try:
  result=subprocess.run(cmd,cwd=W,timeout=max(.1,remaining()),check=False)
  append(E/'process_events.jsonl',{'at_utc':now(),'event':'CHILD_EXIT','cmd':cmd,'code':result.returncode})
  if result.returncode:raise RuntimeError('Child failed '+script+' code '+str(result.returncode))
 except subprocess.TimeoutExpired:
  status('DEADLINE_STOP',recent_error='Absolute10Beijing cutoff child terminated',next='Preserve existing model and prediction receipts; no further execution')
  raise
def run():
 try:
  run_child('trainer153.py','run')
  run_child('predict153.py')
  run_child('evaluate153.py')
  run_child('finalize153.py')
 except Exception as exc:
  append(E/'process_events.jsonl',{'at_utc':now(),'event':'LAUNCHER_STOP','error':str(exc),'type':type(exc).__name__,'traceback':traceback.format_exc()})
  raise
if __name__=='__main__':run()

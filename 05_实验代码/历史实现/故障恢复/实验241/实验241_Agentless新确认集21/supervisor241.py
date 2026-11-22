"""Explicit root-granted one flow; assign controller to owned Job before resume."""
import argparse,datetime,os,time
from contracts241 import *
from winjob241 import JobRunner

def controller_env(image,temp):
 env={k:os.environ[k] for k in ('SystemRoot','WINDIR','SYSTEMROOT','SYSTEMDRIVE','COMSPEC','PATHEXT') if k in os.environ}
 env.update(PYTHONPATH='',PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1',PATH=str(Path(image).parent),
  TEMP=str(temp),TMP=str(temp))
 if os.environ.get('DEEPSEEK_API_KEY'):env['DEEPSEEK_API_KEY']=os.environ['DEEPSEEK_API_KEY']
 return env

class ParentOwner:
 def __init__(self,args):
  self.args=args;self.protocol=read(args.protocol);self.grant=read(args.grant);self.seal=read(args.seal)
  self.task_id=self.protocol['task_id'];self.output_root=Path(self.protocol.get('supervision_output_root',str(HERE/'supervision'/self.task_id))).resolve()
  if not inside(self.output_root,HERE):raise EngineeringUnknown('SUPERVISION_WRITE_SCOPE')
  verify_grant(self.protocol,self.grant,self.seal,self.task_id)
  if self.output_root.exists():raise EngineeringUnknown('NO_REPEATED_CONTROLLER_PARENT_OUTPUT')
  self.native_roots=0;self.native_calls=0;self.unknown=None;self.started=time.monotonic()
  self.deadline=min(self.started+900,self.started+max(0,deadline_epoch(HARD)-time.time()))
  self.output_root.mkdir(parents=True)
 def time_left(self):return max(0,self.deadline-time.monotonic())
 def require_action(self,kind,allow_no_new=False):
  if self.unknown:raise EngineeringUnknown('PARENT_STICKY_UNKNOWN')
  verify_grant(self.protocol,read(self.args.grant),read(self.args.seal),self.task_id,
   min(time.time(),deadline_epoch(NO_NEW)-1) if allow_no_new else None)
  if self.time_left()<=0:raise DeclaredBudgetEnd('PARENT_ORIGINAL900_DEADLINE')
 def reserve_native(self):
  if self.native_roots>=2:raise EngineeringUnknown('ONE_AUTHOR_PLUS_ONE_EXTERNAL_EVALUATOR_NO_RERUN')
  self.native_roots+=1
 def record(self,value):
  with (self.output_root/'events.jsonl').open('a',encoding='utf-8') as f:f.write(canonical(value)+'\n')
 def latch_unknown(self,error,stage):
  if self.unknown is None:self.unknown={'stage':stage,'type':type(error).__name__,'message':str(error)};self.record({'sticky_unknown':self.unknown})

def main():
 parser=argparse.ArgumentParser()
 for name in ('protocol','grant','seal','contract'):parser.add_argument('--'+name,required=True)
 args=parser.parse_args()
 for name in ('protocol','grant','seal','contract'):setattr(args,name,str(Path(getattr(args,name)).resolve()))
 own=ParentOwner(args);own.require_action('parent_start')
 image=own.grant.get('controller_physical_python_expected')
 if not image:raise EngineeringUnknown('NEUTRAL_CONTROLLER_PHYSICAL_PYTHON_REQUIRED')
 argv=[image,'-X','utf8','-B',str(HERE/'cli241.py')]
 for name in ('protocol','grant','seal','contract'):argv += ['--'+name,getattr(args,name)]
 env=controller_env(image,own.output_root)
 own.record({'event':'FLASH_CONTROLLER_TRANSPORT_KEY_BOOLEAN','paid_key_present':bool(env.get('DEEPSEEK_API_KEY'))})
 value=JobRunner(own).execute(argv,HERE,own.output_root/'controller.log',900,env,controller=True)
 save(own.output_root/'parent_stop_receipt.json',value,scope=own.output_root)
 # The author process and its owned descendants are already STOPPED. This
 # new process is a one-way evaluator; no acceptance result reaches author.
 flow=Path(own.protocol['output_root']);result_path=flow/'result.json'
 raw=read(result_path) if result_path.is_file() else {}
 private_status={'status':'NOT_RUN','reason':raw.get('status','AUTHOR_RESULT_ABSENT'),'private_attempts':0}
 if (value['exit_code']==0 and not value['timeout']
     and all(value['stop_receipt'].get(k) for k in ('root_stopped','own_Job_empty_before_close','descendants_stopped'))
     and raw.get('status')=='SELECTED_AWAIT_EXTERNAL_PRIVATE'):
  eval_argv=[image,'-X','utf8','-B',str(HERE/'external_once_private241.py')]
  for name in ('protocol','grant','seal','contract'):eval_argv+=['--'+name,getattr(args,name)]
  birth=value['births'][0]['creation_time100ns']/10000000-11644473600
  own.deadline=min(own.deadline,time.monotonic()+max(0,birth+900-time.time()))
  eval_env=controller_env(image,own.output_root);eval_env.pop('DEEPSEEK_API_KEY',None)
  eval_stop=JobRunner(own).execute(eval_argv,HERE,own.output_root/'external_evaluator.log',90,eval_env,controller=True)
  save(own.output_root/'external_parent_stop_receipt.json',eval_stop,scope=own.output_root)
  eval_result=flow/'external_once_private/result.json'
  private_status=read(eval_result) if eval_result.is_file() else {'status':'EXTERNAL_UNKNOWN','success':None,'private_attempts':0,'reason':'EVALUATOR_RESULT_ABSENT'}
 save(own.output_root/'automatic_external_summary.json',{'task_id':own.task_id,'author_status':raw.get('status'),
  'external_status':private_status.get('status'),'success':private_status.get('success'),
  'private_attempts':private_status.get('private_attempts',0),'reason':private_status.get('reason'),
  'actor_received_private_feedback':False,'LLM_calls_including_prepost_attempts':raw.get('LLM_calls'),
  'automatic_after_author_STOP':True},scope=own.output_root)
 print(canonical({'task_id':own.task_id,'parent_job_fully_stopped':value['stop_receipt']['own_Job_empty_before_close'],
  'timeout':value['timeout'],'exit_code':value['exit_code'],'log':value['log'],
  'external_status':private_status.get('status'),'success':private_status.get('success'),
  'private_attempts':private_status.get('private_attempts',0)}))
if __name__=='__main__':main()

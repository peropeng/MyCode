"""Unchanged finance/common249; actual POST timing never resets supervisor T0."""
from common166 import *
from checkpoint239 import atomic,UnsafeResume
_transport=None
class FirstBodyGateRejected(RuntimeError):pass

def start_science(env,body):
 path=E/'checkpoints'/env.task_id/'GENESIS.json';value=read(path)
 if not isinstance(value.get('original_T0_monotonic'),(int,float)):raise UnsafeResume('EXP250_FORWARD_SUPERVISOR_T0_REQUIRED')
 if value.get('actual_POST_T0_UTC') is None:
  value.update(actual_POST_T0_monotonic=time.monotonic(),actual_POST_T0_UTC=now(),first_actual_full_body_SHA256=digest(body),
   pre_POST_preparation_seconds=time.monotonic()-value['original_T0_monotonic'],
   trial_id=authorization()['trial_id'],fresh_full_trajectory_no_old_response_reuse=True)
  atomic(path,value)
 if env.started!=value['original_T0_monotonic']:raise UnsafeResume('EXP250_END_TO_END_CLOCK_DRIFT_BEFORE_POST')
 atomic(E/'INFLIGHT_POST250.json',{'status':'POST_DISPATCH','task_id':env.task_id,'trial_id':authorization()['trial_id'],
  'call':env.calls,'body_SHA256':digest(body),'UTC':now(),'original_T0_monotonic':env.started})

def generate(env,body,role,phase):
 global _transport
 p=authorization()
 if sha(p['shared_input249'])!=p['shared_input249_SHA256'] or sha(p['finance_transport'])!=p['finance_transport_sha256']:raise RuntimeError('EXP250_SHARED_WIRE_SOURCE_DRIFT')
 common=module('_exp250_shared_input249',p['shared_input249']);config=read(E/'finance_config239.json')
 full=common.inject(body,config,env.task_id)
 if env.calls==1:
  pin=p['first_body_prospective_pin']
  if not pin or digest(body)!=pin['authorbody_SHA256'] or digest(full)!=pin['fullbody_SHA256']:raise FirstBodyGateRejected('EXP250_FIRST_COMPLETE_BODY_DRIFT_NO_POST')
 if _transport is None:
  base=module('_exp250_unchanged_continuous_finance_v3',p['finance_transport'])
  class IO(base.LegacyIO):
   def post(self,request,key,timeout):
    start_science(self.current_env,request)
    return super().post(request,key,timeout)
  _transport=base.make_transport(config,IO())
 _transport.io.current_env=env
 value=_transport.generate(env,full,role,phase)
 receipt=value.get('_finance_receipt',{})
 if receipt.get('status')!='SETTLED':raise UnsafeResume('EXP250_MODEL_RECEIPT_NOT_SETTLED')
 atomic(E/'INFLIGHT_POST250.json',{'status':'SETTLED','task_id':env.task_id,'trial_id':p['trial_id'],
  'call':env.calls,'body_SHA256':digest(full),'receipt_ordinal':receipt.get('ordinal'),'UTC':now()})
 return value

"""Shared bounded actual Flash with preserved full EnAgent history/tools."""
from common166 import *
import copy
from budget_policy225 import DeclaredFlowBudgetExhausted

class Transport:
 def __init__(self,env,stage,index,root,bridge):self.env,self.stage,self.index,self.root,self.bridge,self.turn=env,stage,index,Path(root),bridge,0
 def request(self,payload):
  if getattr(self.env,'_generation_fatal',None) is not None:raise self.env._generation_fatal
  try:return self._request(payload)
  except Exception as exc:
   self.env._generation_fatal=exc
   self.env.record('provider_or_budget_fatal_before_next_actor225',{'type':type(exc).__name__,'error':str(exc),'stage':self.stage,'index':self.index,'turn':self.turn,'source_BaseAgent_may_swallow_exception_but_whole_flow_must_stop':True})
   raise
 def _request(self,payload):
  self.bridge.raise_if_failed();self.env._require();protocol=authorization();limits=protocol['budget']
  cap=int(limits['role_output_caps']['enagent_'+self.stage]);temperature={'coder':.7,'tester':0.,'selector':.2}[self.stage]
  if payload['temperature']!=temperature:raise RuntimeError('AUTHOR_STAGE_TEMPERATURE_DRIFT')
  if self.env.calls>=limits['max_model_calls_per_flow']:raise DeclaredFlowBudgetExhausted('model_calls')
  if self.env.out_tokens+cap>limits['max_output_tokens_per_flow']:raise DeclaredFlowBudgetExhausted('output_tokens_with_frozen_role_reservation')
  messages=copy.deepcopy(payload['messages'])
  def public_paths(value):
   if isinstance(value,str):return self.bridge.neutral(self.root,value)
   if isinstance(value,list):return [public_paths(x) for x in value]
   if isinstance(value,dict):return {k:public_paths(v) for k,v in value.items()}
   return value
  messages=public_paths(messages)
  serialized=canonical(messages)
  if 'ENAGENT_ICSE2026_N3_QWEN7B' in serialized or 'ENAGENT_ICSE2026_N3_FLASH' in serialized or '1008-2320-exp225-enagent-flash' in serialized:raise RuntimeError('COMMON_ACTOR_PATH_PROJECTION_UNKNOWN_BEFORE_POST')
  seed=int(hashlib.sha256(('Exp225|'+self.env.task_id+'|'+self.stage+'|'+str(self.index)+'|'+str(self.turn)).encode()).hexdigest()[:8],16)%2147483647
  body={'model':'deepseek-flash','messages':messages,'thinking':{'type':'disabled'},'temperature':temperature,'top_p':payload.get('top_p',1.),'seed':seed,'max_tokens':cap,'stream':False}
  if payload.get('tools'):body.update(tools=copy.deepcopy(payload['tools']),tool_choice='auto')
  self.env.record('EnAgent_actual_full_history_request225',{'stage':self.stage,'index':self.index,'turn':self.turn,'seed':seed,'temperature':temperature,'cap':cap,'full_body_sha256':digest(body),'messages':len(messages),'original_tools_and_incremental_history':True})
  self.turn+=1;self.env.calls+=1
  transport=module('exp225_shared_transport',TRANSPORT);raw=transport.generate(self.env,body,'Exp225/ENAGENT/'+self.env.task_id+'/'+self.stage,phase=self.env.finance_phase)
  self.env.out_tokens+=raw['usage']['completion_tokens'];choice=raw['choices'][0]
  if choice.get('finish_reason')=='length':self.env.truncated_responses.append(self.env.calls)
  self.env.record('EnAgent_actual_response225',{'stage':self.stage,'index':self.index,'call_ordinal':self.env.calls,'usage':raw['usage'],'finish_reason':choice.get('finish_reason'),'finance':raw.get('_finance_receipt',{})})
  return raw

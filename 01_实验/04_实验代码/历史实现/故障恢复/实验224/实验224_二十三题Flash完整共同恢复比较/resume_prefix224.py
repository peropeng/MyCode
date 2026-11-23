"""Mechanical continuation: only exact-body original paid prefix responses.

Already settled costs remain in the continuous ledger. This never borrows a
response from another case/arm and cannot reselect an evaluated final patch.
"""
from common166 import *
import copy
class ExactPublicPrefix:
 def __init__(self,source_flow,allow_new_post=True):
  self.source=Path(source_flow).resolve();self.position=1;self.reused=[];self.active=True;self.allow_new_post=allow_new_post
 def generate(self,real_generate,env,body,role,phase):
  request=self.source/'llm'/f'{self.position:03d}_request.json'
  response=self.source/'llm'/f'{self.position:03d}_response.json'
  receipt=self.source/'llm'/f'{self.position:03d}_finance_receipt.json'
  if self.active and request.exists() and response.exists() and receipt.exists():
   saved=read(request);settled=read(receipt)
   if digest(saved['body'])==digest(body) and saved['role']==role and settled['status']=='SETTLED':
    original_response=read(response);proof={'at_utc':now(),'status':'REUSED_PAID_PREFIX','original_request':str(request),'original_request_sha256':sha(request),'original_response':str(response),'original_response_sha256':sha(response),'original_finance_receipt':str(receipt),'original_finance_receipt_sha256':sha(receipt),'original_finance_ordinal':settled['ordinal'],'body_sha256':digest(body),'input_seed_temperature_tools_output_budget_identical':True,'call_output_count_inherited':True,'new_API':0,'new_cost_CNY':'0','original_cost_already_in_continuous_ledger_CNY':settled['usage_peak_cost_CNY'],'same_flow_mechanical_lineage':True}
    save(env.out/'llm'/f'{env.calls:03d}_reused_prefix.json',proof);self.reused.append(proof);self.position+=1
    value=copy.deepcopy(original_response);value['_finance_receipt']={**settled,'status':'REUSED_PAID_PREFIX','original_status':'SETTLED','original_receipt_sha256':sha(receipt),'already_settled_prefix_reuse':True,'new_cost_CNY':'0','new_paid_API':0};env.record('exact_public_paid_prefix_reuse224',proof);return value
   self.active=False;env.record('public_prefix_reuse_stopped224',{'original_ordinal':self.position,'reason':'COMPLETE_BODY_OR_ROLE_OR_SETTLEMENT_NOT_IDENTICAL','actual_body_sha256':digest(body),'original_body_sha256':digest(saved['body']),'no_nonidentical_response_reused':True})
  else:self.active=False
  if not self.allow_new_post:raise RuntimeError('PREFLIGHT_EXACT_PREFIX_EXHAUSTED_NEW_POST_DISABLED')
  return real_generate(env,body,role,phase=phase)
def install(bank):
 import common_environment224 as shared
 original=shared.module
 def scoped_module(name,path):
  result=original(name,path)
  if Path(path).resolve()==TRANSPORT.resolve():
   actual=result.generate
   result.generate=lambda env,body,role,phase='Round2320Pilot':bank.generate(actual,env,body,role,phase)
  return result
 shared.module=scoped_module
 return lambda:setattr(shared,'module',original)

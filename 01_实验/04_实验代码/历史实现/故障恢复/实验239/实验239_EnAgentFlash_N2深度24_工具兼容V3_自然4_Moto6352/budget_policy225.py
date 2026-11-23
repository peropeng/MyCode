"""Pure termination semantics: declared per-flow limits vs external censoring."""
import time

class DeclaredFlowBudgetExhausted(RuntimeError):
 def __init__(self,resource):
  self.resource=resource
  super().__init__('DECLARED_FLOW_BUDGET_EXHAUSTED: '+resource)

COUNTER_LIMITS={'COMMON_FLOW_CALL_OR_OUTPUT_BUDGET','COMMON_FLOW_CALL_OR_OUTPUT_CAP','LLM_CALL_OR_OUTPUT_TOKEN_BUDGET','MODEL_CALL_OR_TOTAL_OUTPUT_BUDGET','PUBLIC_NATIVE_BUDGET9','DECLARED_GIT_BASH_ROOT_CAP','CANDIDATE_SUBMISSION_BUDGET9'}
TIME_LIMITS={'METHOD_SEARCH_WALL_BUDGET','METHOD_NATIVE_QUEUE_WALL_BUDGET','NATIVE_LANE_QUEUE_DEADLINE_BEFORE_PROCESS','NO_NEW_FLASH_OR_FLOW_DEADLINE','NO_NEW_FINAL_NATIVE_AFTER_STOP_OR_DEADLINE'}

def classify(exc,env=None,limits=None,*,no_new_epoch,hard_epoch,wall_now=None,mono_now=None):
 """No I/O or actions. A configured method can fail its own frozen budget.

 No candidate/native/private feedback is fabricated. Declared failure terminates
 only this task; money, endpoint, deployment and global cutoff stop the queue.
 """
 wall_now=time.time() if wall_now is None else wall_now
 mono_now=time.monotonic() if mono_now is None else mono_now
 name=type(exc).__name__;message=str(exc);configured=bool(getattr(env,'flow_configuration_sealed',False))
 def unknown(scope,status='BUDGET_CENSORED'):
  return {'status':status,'success':None,'evaluation_status':'UNKNOWN','budget_scope':scope,'stop_queue':True,'declared_flow_budget_evaluable':False}
 # An external cutoff takes priority even if a per-flow counter also expired.
 if wall_now>=no_new_epoch or wall_now>=hard_epoch or 'USER_STOP' in message:
  return unknown('GLOBAL_OR_USER_CUTOFF')
 if name.startswith('Finance') and message not in TIME_LIMITS:
  return unknown('ACCOUNT_PHASE_OR_FINANCIAL_TRANSACTION')
 resource=getattr(exc,'resource',None) if isinstance(exc,DeclaredFlowBudgetExhausted) else None
 if message in COUNTER_LIMITS:resource=message
 if message in TIME_LIMITS:
  limits=limits or {};start=getattr(env,'started',None);deadline=getattr(env,'deadline',None);search=getattr(env,'search_deadline',None)
  if start is None or deadline is None or search is None:return unknown('UNVERIFIED_FLOW_OR_GLOBAL_WALL')
  declared=float(start)+float(limits.get('flow_wall_seconds',900))
  # The frozen 90-second final reserve is part of the existing 900-second flow.
  # A shortened deadline caused by the overall round is external censoring.
  if float(deadline)<declared-0.001:return unknown('GLOBAL_ROUND_TRUNCATED_FLOW')
  if mono_now>=float(search) or mono_now>=declared:resource='flow_wall_or_frozen_final_reserve'
  else:return unknown('UNVERIFIED_FLOW_OR_GLOBAL_WALL')
 if resource is not None and configured:
  return {'status':'DECLARED_FLOW_BUDGET_EXHAUSTED','success':False,'evaluation_status':'KNOWN_FAIL','budget_scope':'DECLARED_PER_FLOW','stop_queue':False,'declared_flow_budget_evaluable':True,'exhausted_resource':resource}
 if resource is not None:return unknown('CONFIGURATION_NOT_SEALED','ENGINEERING_UNKNOWN')
 return unknown('MODEL_OR_DEPLOYMENT_FAILURE','ENGINEERING_UNKNOWN')

def stop_queue(result):
 if result.get('status')=='DECLARED_FLOW_BUDGET_EXHAUSTED' and result.get('evaluation_status')=='KNOWN_FAIL':return False
 return bool(result.get('stop_queue',result.get('status') in ('BUDGET_CENSORED','ENGINEERING_UNKNOWN')))

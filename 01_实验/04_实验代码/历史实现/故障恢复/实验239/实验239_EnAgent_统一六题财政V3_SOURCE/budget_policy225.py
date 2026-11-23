"""Preserve partial/UNKNOWN when a finite resource, completion stop or finance blocks."""
import time
class DeclaredFlowBudgetExhausted(RuntimeError):
 def __init__(self,resource):self.resource=resource;super().__init__('DECLARED_FLOW_BUDGET_EXHAUSTED: '+resource)
def classify(exc,env=None,limits=None,*,no_new_epoch=None,hard_epoch=None,wall_now=None,mono_now=None):
 from common166 import request_closed
 message=str(exc);name=type(exc).__name__
 stopped=request_closed() or 'USER_STOP' in message or 'COMPLETION_FLAG' in message
 scope='GLOBAL_OR_USER_COMPLETION_STOP' if stopped else 'ACCOUNT_PHASE_OR_FINANCIAL_TRANSACTION' if name.startswith('Finance') or 'FINANCE' in message else 'DECLARED_PER_FLOW_RESOURCE' if isinstance(exc,DeclaredFlowBudgetExhausted) or 'BUDGET' in message or 'ROOT_CAP' in message or 'FLOW' in message else 'MODEL_OR_DEPLOYMENT_FAILURE'
 return {'status':'BUDGET_CENSORED' if scope in ('GLOBAL_OR_USER_COMPLETION_STOP','ACCOUNT_PHASE_OR_FINANCIAL_TRANSACTION','DECLARED_PER_FLOW_RESOURCE') else 'ENGINEERING_UNKNOWN','success':None,'evaluation_status':'UNKNOWN','budget_scope':scope,'stop_queue':True,'declared_flow_budget_evaluable':False,'partial_generations_retained':True}
def stop_queue(result):return bool(result.get('stop_queue',result.get('status') in ('BUDGET_CENSORED','ENGINEERING_UNKNOWN')))

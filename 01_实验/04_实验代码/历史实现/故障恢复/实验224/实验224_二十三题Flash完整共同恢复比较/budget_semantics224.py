"""Pure disposition rules for declared flow limits versus external censoring."""
CALL_OUTPUT_REASONS={
 'COMMON_FLOW_CALL_OR_OUTPUT_CAP':'DECLARED_CALL_OR_OUTPUT_LIMIT',
 'MODEL_CALL_OR_TOTAL_OUTPUT_BUDGET':'DECLARED_CALL_OR_OUTPUT_LIMIT',
 'COMMON_PUBLIC_READER_ROUND_CAP':'DECLARED_PUBLIC_READER_STAGE_LIMIT',
}
WALL_REASONS={'METHOD_SEARCH_WALL_BUDGET','METHOD_NATIVE_QUEUE_WALL_BUDGET','NATIVE_LANE_QUEUE_DEADLINE_BEFORE_PROCESS','NO_NEW_FINAL_NATIVE_AFTER_STOP_OR_DEADLINE'}
PRE_RESERVATION_FLOW_TIME_REASONS={'NO_NEW_FLASH_OR_FLOW_DEADLINE','FINANCE_LOCK_OR_NO_NEW_DEADLINE'}

def budget_disposition(result,context):
 error=result.get('error') or {};name=error.get('type','');reason=error.get('message','')
 if error.get('restore_error') or any(r.get('stage')=='restore_failure' for r in result.get('stage_ledger',[]) if isinstance(r,dict)):
  return {'status':'ENGINEERING_UNKNOWN','success':None,'reason':'FAILED_RESTORE_AFTER_ERROR'}
 # These two exact legacy gates run before reservation/POST. A flow-time race
 # here has no unknown financial hold. All later or unknown finance errors stay fatal.
 if name=='FinanceGateRejected' and reason in PRE_RESERVATION_FLOW_TIME_REASONS and not context.get('finance_fatal'):
  if context.get('global_cutoff') or context.get('wall_limited_by_global'):
   return {'status':'GLOBAL_WINDOW_CENSORED','success':None,'reason':'GLOBAL_PRE_RESERVATION_TIME_CUTOFF'}
  if context.get('search_wall_exhausted') or context.get('full_wall_exhausted'):
   return {'status':'DECLARED_FLOW_BUDGET_EXHAUSTED','success':False,'reason':'DECLARED_FLOW_TIME_ENDED_BEFORE_RESERVATION_OR_POST'}
 if context.get('finance_fatal') or result.get('finance_fatal') or name.startswith('Finance'):
  return {'status':'BUDGET_CENSORED','success':None,'reason':'ACCOUNT_PHASE_PROVIDER_OR_FINANCE_UNKNOWN'}
 if context.get('global_cutoff'):
  return {'status':'GLOBAL_WINDOW_CENSORED','success':None,'reason':'GLOBAL_NO_NEW_HARD_OR_USER_STOP'}
 if name=='BudgetError' and reason in CALL_OUTPUT_REASONS:
  return {'status':'DECLARED_FLOW_BUDGET_EXHAUSTED','success':False,'reason':CALL_OUTPUT_REASONS[reason]}
 if (name=='BudgetError' and reason in WALL_REASONS) or (name=='TimeoutError' and reason=='NATIVE_LANE_QUEUE_DEADLINE_BEFORE_PROCESS') or (name=='CoreUnavailable' and reason=='NO_NEW_METHOD_GLOBAL_DEADLINE'):
  if context.get('wall_limited_by_global'):
   return {'status':'GLOBAL_WINDOW_CENSORED','success':None,'reason':'GLOBAL_WINDOW_SHORTENED_FLOW_SEARCH_OR_FINAL_TIME'}
  if context.get('search_wall_exhausted') or context.get('full_wall_exhausted'):
   return {'status':'DECLARED_FLOW_BUDGET_EXHAUSTED','success':False,'reason':'DECLARED_FLOW_WALL_INCLUDING_FROZEN_ACCEPTANCE_RESERVE'}
 if not name and context.get('full_wall_exhausted') and result.get('status') in ('COMPLETED','MODEL_SEMANTIC_FAILURE'):
  return {'status':'GLOBAL_WINDOW_CENSORED' if context.get('wall_limited_by_global') else 'DECLARED_FLOW_BUDGET_EXHAUSTED','success':None if context.get('wall_limited_by_global') else False,'reason':'NO_VERIFIED_TERMINAL_RESULT_BEFORE_FULL_FLOW_WALL'}
 if result.get('status')=='BUDGET_CENSORED' or name=='BudgetError':
  return {'status':'BUDGET_CENSORED','success':None,'reason':'UNRECOGNIZED_BUDGET_SOURCE_NOT_ASSUMED_METHOD_FAILURE'}
 return None

def should_stop_queue(result):
 if result.get('finance_fatal'):return True
 if result.get('status')=='DECLARED_FLOW_BUDGET_EXHAUSTED':return False
 return bool(result.get('engineering_outcome_unknown') or result.get('status') in (
  'ENGINEERING_UNKNOWN','CONTEXT_UNKNOWN','CONTEXT_EVIDENCE_UNKNOWN','BUDGET_CENSORED',
  'OUTPUT_TRUNCATED_CENSORED','GLOBAL_WINDOW_CENSORED','NOT_RUN','USER_INTERRUPTED'
 ) or (result.get('error') or {}).get('type','').startswith('Finance'))

"""Pure completion-window resource policy; fixtures need no OS or model process."""
import math,time
from pathlib import Path
class CompletionStopped(RuntimeError):pass
class FlowBoundaryExceeded(RuntimeError):pass
def finite_seconds(value,maximum=604800):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not 0<value<=maximum:raise FlowBoundaryExceeded('FINITE_INDIVIDUAL_FLOW_REQUIRED')
    return float(value)
def deadline_for(start,seconds,parent_deadline=None):
    seconds=finite_seconds(seconds)
    if isinstance(start,bool) or not isinstance(start,(int,float)) or not math.isfinite(start):raise FlowBoundaryExceeded('FINITE_FLOW_START_REQUIRED')
    result=float(start)+seconds
    if parent_deadline is not None:
        if isinstance(parent_deadline,bool) or not isinstance(parent_deadline,(int,float)) or not math.isfinite(parent_deadline):raise FlowBoundaryExceeded('FINITE_PARENT_FLOW_REQUIRED')
        result=min(result,float(parent_deadline))
    return result
def check_open(paths,exists=None):
    exists=exists or (lambda p:Path(p).exists())
    if any(exists(p) for p in paths if p is not None):raise CompletionStopped('USER_STOP_COMPLETION_FLAG_BEFORE_NEW_ACTION')
def check_count(value,maximum,resource,additional=1):
    if any(isinstance(x,bool) or not isinstance(x,int) or x<0 for x in (value,maximum,additional)) or maximum<=0:raise FlowBoundaryExceeded('INVALID_'+resource+'_COUNTER')
    if value+additional>maximum:raise FlowBoundaryExceeded('DECLARED_'+resource+'_ROOT_CAP')
    return value+additional
def time_left(deadline,now=None):
    now=time.monotonic() if now is None else now
    if not math.isfinite(deadline) or not math.isfinite(now):raise FlowBoundaryExceeded('NONFINITE_INDIVIDUAL_FLOW')
    return min(604800.,max(0.,deadline-now))
def require_time(deadline,now=None):
    if time_left(deadline,now)<=0:raise FlowBoundaryExceeded('METHOD_SEARCH_WALL_BUDGET')
def public_final_permission(grant):
    if not all(grant.get(k) is True for k in ('execution_authorized','model_generation_authorized','native_authorized','private_authorized','once_private_authorized')):raise CompletionStopped('PRIVATE_ONCE_INDEPENDENT_AUTHORITY_REQUIRED')
def final_classification(elapsed,limit,public_known,public_pass,ordinary_pass,private_known,private_pass,legal):
    within=0<=elapsed<=finite_seconds(limit)
    if not public_known or not private_known:return None,within
    if not within:return None,False
    return bool(public_pass and ordinary_pass and private_pass and legal),True

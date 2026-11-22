"""Completion window facade: finite per-flow timer, final once, no old900 success cutoff."""
from common166 import *
from contextlib import contextmanager
from flow_bounds239 import time_left,require_time,public_final_permission,final_classification

def completion_environment(base):
    class CompletionEnvironment(base):
        def __init__(self,ref,method):
            super().__init__(ref,method)
            p=authorization();b=p['budget']
            self.deadline=flow_deadline_for(self.started,b['flow_wall_seconds'])
            self.search_deadline=self.deadline-b.get('final_reserve_seconds',90)
            self._independent_final_attempts=0
            self._product_native_roots=0
            self.record('unified_six_actual_resource_authority239',{'scope_id':p['scope_id'],'completion_condition':p['completion_condition'],'global_deadline':None,'flow_seconds':b['flow_wall_seconds'],'native_timeout':b['native_timeout_seconds'],'model_calls':b['max_model_calls_per_flow'],'total_output':b['max_output_tokens_per_flow'],'product_native_roots':b['native_roots_total'],'all_owned_OS_roots':b['all_owned_OS_roots_total'],'N':3,'coder_steps':200,'selector_rounds':30,'private_once_permission_not_implicitly_granted':True})
        def llm(self,*args,**kwargs):raise RuntimeError('ENAGENT_ORIGINAL_NATIVE_CLIENT_TRANSPORT_REQUIRED')
        def time_left(self):return time_left(self.search_deadline)
        def _require(self):
            try:
                require_open();require_time(self.search_deadline)
                if getattr(self,'_generation_fatal',None) is not None:raise self._generation_fatal
            except BaseException as exc:self._generation_fatal=exc;raise
        @contextmanager
        def native_lane(self,final=False):
            require_open();authorization()
            if final:require_time(self.deadline)
            else:self._require()
            from native_lane178 import native_lane
            with native_lane(self.package,self.deadline if final else self.search_deadline,self.record):
                require_open()
                if final:require_time(self.deadline)
                else:self._require()
                yield
        def finalize(self,result):
            require_open();p=authorization();public_final_permission(read(E/'root_grant239.json'))
            if self._independent_final_attempts!=0:raise RuntimeError('ONCE_FINAL_VALIDATION_ALREADY_ATTEMPTED')
            self._independent_final_attempts+=1
            self._final_validation_running=True
            try:full=super().finalize(result)
            finally:self._final_validation_running=False
            success,within=final_classification(full['elapsed_seconds'],p['budget']['flow_wall_seconds'],full.get('public_acceptance_known') is True,full.get('visible_pass'),full.get('public_regression_pass'),full.get('final_hidden_known') is True,full.get('preservation_pass'),full.get('final_legal_edit_check',{}).get('legal'))
            full.pop('within_900_seconds',None);full.pop('within_720_seconds',None)
            full.update(success=success,within_flow_seconds=within,flow_wall_limit_seconds=p['budget']['flow_wall_seconds'],global_deadline=None,product_native_roots_total=self._product_native_roots,independent_final_attempts=self._independent_final_attempts)
            if not within:full.update(status='BUDGET_CENSORED',evaluation_status='UNKNOWN',success=None)
            if full.get('hidden_acceptance_calls',0)>1:raise RuntimeError('MULTIPLE_PRIVATE_NATIVE_CALLS_FORBIDDEN')
            return full
    return CompletionEnvironment

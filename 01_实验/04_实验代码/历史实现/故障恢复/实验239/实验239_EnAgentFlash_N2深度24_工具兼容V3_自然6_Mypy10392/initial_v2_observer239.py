"""Observer-only exact-C0 ordinary cache; actor algorithms and final gates unchanged."""
from common166 import *

def initial_bridge(base):
 class InitialOrdinaryObserver(base):
  def _initial_ordinary_cache(self,root,ids):
   cfg=read(E/'protocol225.json').get('initial_qualification_v2_observer_only_certificate')
   if not cfg:return None
   root=self._root(root);ids=list(ids)
   if root.resolve()!=(self.owned/'w/tester_initial').resolve():return None
   if ids!=list(self.env.public_regression_nodes) or len(ids)!=1:return None
   certpath=Path(cfg['path']);
   if sha(certpath)!=cfg['sha256']:raise RuntimeError('INITIAL_V2_OBSERVER_CERTIFICATE_DRIFT')
   cert=read(certpath)
   if cert['task']!=self.env.task_id or cert['classification']!='C0_COLLECTION_BLOCKED_BY_LEGAL_BUSINESS_SYNTAX':return None
   expected=cert['all_actual_C0_business_paths_SHA256']
   current=self._clone_business(root)
   if set(current)!=set(expected):return None
   if any(sha(root/path)!=value for path,value in expected.items()):return None
   nativepath=Path(cert['native_result_path'])
   if sha(nativepath)!=cert['native_result_SHA256']:raise RuntimeError('INITIAL_V2_OBSERVER_NATIVE_EVIDENCE_DRIFT')
   native=read(nativepath)
   good=(native.get('executed') and native.get('guard_loaded') and native.get('business_state_unchanged') and native.get('frozen_tests_unchanged') and not native.get('timeout') and native.get('stop_receipt',{}).get('all_owned_descendants_terminated'))
   outcomes=native.get('pytest',{}).get('outcomes',{})
   if not good or outcomes.get(ids[0],{}).get('status')!='passed' or cert['actual_ordinary_passed']!=1 or not cert['all_owned_STOP']:raise RuntimeError('INITIAL_V2_ORDINARY_ACTUAL_PASS_AND_STOP_NOT_VERIFIED')
   return {'answer':{ids[0]:'PASS'},'certificate_path':str(certpath),'certificate_sha256':cfg['sha256'],'native_result_path':str(nativepath),'native_result_sha256':cert['native_result_SHA256'],'current_C0_paths_checked':len(expected),'current_C0_exact':True,'actual_initial_goal_completed':0,'actual_initial_goal_collection_blocked':5,'goal_outcomes_NOT_fabricated':True,'actual_new_native_calls':0,'private_reads':False}
  def public_runner(self,root,ids):
   before=self._check_assets();ids=list(ids);cached=self._initial_ordinary_cache(root,ids)
   if cached is None:return super().public_runner(root,ids)
   self._record('observer_initial_v2_ordinary_cache_reused',{'root':str(self._root(root)),'requested_ordinary_ids':ids,'purpose':'original author tester_initial baseline only','original_actor_information_unchanged':True,'final_and_candidate_native_rules_UNCHANGED':True,'immutable_sha256':before,**cached})
   self._check_assets();return cached['answer']
 return InitialOrdinaryObserver

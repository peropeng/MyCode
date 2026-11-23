"""Known current-C0 public SyntaxError is diagnostic feedback, never final PASS."""
from common166 import *

def diagnostic_bridge(base):
 class PublicInitialSourceObserver(base):
  def _known_initial_source_negative(self,record,generated=False):
   if generated:return None
   cfg=read(E/'protocol225.json').get('initial_v3_public_source_observer_certificate')
   if not cfg or not cfg.get('path') or not cfg.get('sha256'):return None
   if not all(record.get(k) is True for k in ('executed','guard_loaded','business_state_unchanged','frozen_tests_unchanged')) or record.get('timeout') is not False:return None
   if type(record.get('exit_code')) is not int or record['exit_code']==0:return None
   if not all(record.get(k) is False for k in ('exact_test_coverage','completed_guarded_coverage','passed','assertions_executed','raw_exact_test_coverage')):return None
   if record.get('stop_receipt',{}).get('all_owned_descendants_terminated') is not True:return None
   if not all(record.get(k) is True for k in ('known_public_product_collection_failure','all_matched_syntax_source_bytes_unchanged_from_initial','dependency_environment_errors_not_accepted','original_certified_failure_rule_reused')):return None
   certpath=Path(cfg['path'])
   if sha(certpath)!=cfg['sha256']:raise RuntimeError('INITIAL_V3_CURRENT_CERTIFICATE_DRIFT')
   cert=read(certpath)
   if cert.get('task')!=self.env.task_id or cert.get('all_owned_STOP') is not True or cert.get('classification')!='C0_COLLECTION_BLOCKED_BY_LEGAL_BUSINESS_SYNTAX':return None
   ref=read(E/'protocol225.json')['shared_pack_references'][self.env.task_id]
   if cert.get('shared_pack_path')!=ref['path'] or cert.get('shared_pack_SHA256')!=ref['sha256']:return None
   if sha(Path(ref['path']))!=ref['sha256']:raise RuntimeError('INITIAL_V3_SHARED_PACK_DRIFT')
   nativepath=Path(cert['native_result_path'])
   if sha(nativepath)!=cert['native_result_SHA256']:raise RuntimeError('INITIAL_V3_CURRENT_NATIVE_CERTIFICATE_DRIFT')
   expected=cert['all_actual_C0_business_paths_SHA256'];current=self.env.business_files()
   if expected!=read(Path(ref['path']))['c0_business_paths_sha256']:return None
   if set(current)!=set(expected) or any(sha(self.env.repo_root/path)!=h for path,h in expected.items()):return None
   errors=record.get('pytest',{}).get('collection_errors',[])
   if not errors or not all(any(kind in x.get('detail','') for kind in ('SyntaxError','IndentationError','TabError')) for x in errors):return None
   goals=set(self.env.recovery_goal_nodes);ordinary=set(self.env.public_regression_nodes)
   if not goals or not ordinary or goals&ordinary:return None
   if cert.get('actual_initial_goal_completed')!=0 or cert.get('actual_initial_goal_blocked_by_collection')!=len(goals) or cert.get('actual_ordinary_passed')!=len(ordinary):return None
   if set(record.get('matched_public_goal_nodes',[]))!=goals or set(record.get('requested_nodes',[]))!=goals|ordinary:return None
   outcomes=record.get('pytest',{}).get('outcomes',{})
   if set(outcomes)!=ordinary or set(record.get('pytest',{}).get('requested_but_uncollected_nodes',[]))!=goals:return None
   if not all(outcomes[node].get('status')=='passed' for node in ordinary):return None
   keys=('known_public_product_collection_failure','matched_public_goal_nodes','actual_failures','assertions_executed','raw_exact_test_coverage','original_certified_failure_rule_reused','all_matched_syntax_source_bytes_unchanged_from_initial','dependency_environment_errors_not_accepted')
   recorded=any(row.get('stage')=='certified_known_public_source_collection_failure' and all(row['evidence'].get(k)==record.get(k) for k in keys) for row in self.env.stage_ledger)
   if not recorded:return None
   return {'certificate_sha256':cfg['sha256'],'current_C0_source_paths_checked':len(expected),'raw_exact_test_coverage':False,'raw_completed_guarded_coverage':False,'actual_goal_completed':0,'goal_collection_blocked':len(goals),'ordinary_actual_PASS':list(self.env.public_regression_nodes),'final_acceptance_NOT_GRANTED':True,'goal_states_NOT_fabricated':True,'already_certified_by_actual_environment':True}
  def _valid(self,record,generated=False):
   diagnostic=self._known_initial_source_negative(record,generated)
   if diagnostic is None:return super()._valid(record,generated)
   self._record('observer_initial_v3_known_source_negative_accepted_as_tool_feedback_only',diagnostic)
   # No record/goalcache/ordinary/native results are rewritten here. Final
   # actual target+ordinary exact PASS and independent once-private are strict.
 return PublicInitialSourceObserver

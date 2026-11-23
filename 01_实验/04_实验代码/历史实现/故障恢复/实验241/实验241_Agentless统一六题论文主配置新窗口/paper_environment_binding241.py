"""Prospective real repository regression and model-cap wiring; no fallback to ordinary."""
import copy
from pathlib import Path
import hashlib,json

def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class PaperBindingUnknown(RuntimeError):pass
class PaperMainEnvironmentMixin:
 def require_paper_main_current_binding(self):
  binding=read(self.protocol['paper_public_pool_binding'])
  if binding.get('root_qualified') is not True or self.protocol.get('execution_authorized') is not True:raise PaperBindingUnknown('NEW_ROOT_PAPER_MAIN_AND_COMMON_POOL_NOT_QUALIFIED')
  if binding.get('scope')!='UNIFIED_SIX_NEW_WINDOW' or binding.get('independent_acceptance_disjoint_qualified') is not True:raise PaperBindingUnknown('NEW_COMMON_PUBLIC_POOL_INDEPENDENT_BOUNDARY_REQUIRED')
  if not self.protocol.get('common_budget_root_freeze') or not self.protocol.get('fresh_current_C0_qualification'):raise PaperBindingUnknown('NEW_CURRENT_C0_AND_COMMON_BUDGET_REQUIRED')
  if sha(binding['public_pool_manifest'])!=binding['public_pool_manifest_sha256']:raise PaperBindingUnknown('COMMON_PUBLIC_TEST_POOL_MANIFEST_DRIFT')
  pool=read(binding['public_pool_manifest'])
  if pool['task_id']!=self.task_id or pool.get('derived_from_original_repo_commit') is not True or not pool.get('nodes'):raise PaperBindingUnknown('REAL_ORIGINAL_REPOSITORY_TEST_POOL_REQUIRED')
  self.paper_public_repository_regression_nodes=list(pool['nodes']);self.paper_pool=pool
 def run_paper_repository_regression(self,snapshot=None,nodes=None,label='paper_repository_regression'):
  requested=list(self.paper_public_repository_regression_nodes if nodes is None else nodes)
  if not set(requested)<=set(self.paper_public_repository_regression_nodes):raise PaperBindingUnknown('PAPER_TEST_NODE_OUTSIDE_ROOT_PUBLIC_POOL')
  if not requested:return {'passed':True,'failure_count':0,'outcomes':{},'status':'EMPTY_LLM_SELECTED_REGRESSION_SET','native_record':{'executed':False}}
  self.restore(snapshot or self.initial_snapshot);self.materialize_actor()
  root=Path(self.paper_pool['root']);out=self.output_root/'paper_regression_native'/label;out.mkdir(parents=True,exist_ok=False)
  if root.resolve()!=Path(self.contract['frozen_public_test_root']).resolve():raise PaperBindingUnknown('COMMON_POOL_MUST_BE_BOUND_TO_ACTUAL_PRODUCT_ENTRY_PUBLIC_GUARD_ROOT')
  from contracts241 import inventory
  before_public=inventory(root);before_repo=inventory(self.repo_root)
  if before_public!=self.paper_pool['files_sha256']:raise PaperBindingUnknown('ROOT_FROZEN_PUBLIC_POOL_SOURCE_DRIFT')
  # Existing trusted physical-native guard executes these actual public test nodes.
  # New pool root/inventory must be frozen by Root; old heldout tree is never used.
  result=self.qualify.probe(self.active,root,requested,out,self.logical_python,self.contract['package'],min(self.flow_deadline,__import__('time').monotonic()+self.protocol['budget']['native_timeout_seconds']))
  outcomes=result.get('pytest',{}).get('outcomes',{})
  if inventory(root)!=before_public or inventory(self.repo_root)!=before_repo:raise PaperBindingUnknown('PUBLIC_POOL_OR_CANDIDATE_MUTATED_DURING_REGRESSION')
  if not result.get('executed') or not result.get('guard_loaded') or result.get('timeout') or set(outcomes)!=set(requested) or result.get('pytest',{}).get('collection_errors'):raise PaperBindingUnknown('REAL_REPOSITORY_REGRESSION_EXACT_GUARD_COVERAGE_UNKNOWN')
  rows={n:{**outcomes[n],'outcome':outcomes[n]['status']} for n in requested};fail=sum(v['status']!='passed' for v in rows.values())
  value={'passed':fail==0,'failure_count':fail,'outcomes':rows,'status':'GUARDED_REAL_REPOSITORY_REGRESSION','native_record':result,'ordinary_proxy_used':False,'public_goal_added_to_regression_ranking':False,'full_root_public_pool_manifest_sha256':self.paper_pool['manifest_sha256']}
  return self.record(label,value)
 def paper_model_call_cap(self,role,requested):
  # The source's 300/2048/1024 requests are respected, unlike old 16K/8K override.
  caps={'agentless_suspicious_files':300,'agentless_irrelevant_folders':2048,'agentless_related_elements':300,'agentless_fine_locations':300,'agentless_patch':1024,'agentless_reproduction':1024,'agentless_regression_exclusion':1024}
  if role not in caps or requested>caps[role]:raise PaperBindingUnknown('SOURCE_PAPER_STAGE_MODEL_CAP_MISMATCH')
  return int(requested)

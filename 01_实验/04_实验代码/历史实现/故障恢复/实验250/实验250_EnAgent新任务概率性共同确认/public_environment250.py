"""Replace legacy task_manifest/resource reads with the shared public-only view."""
from common166 import *
import copy

def install(worker):
 parent=read(E/'protocol225.json')
 if sha(parent['shared_public249'])!=parent['shared_public249_SHA256']:raise RuntimeError('EXP250_COMMON_PUBLIC_ADAPTER_DRIFT')
 shared=module('_exp250_shared_public249',parent['shared_public249'])
 import environment166
 original_load=environment166.load_replay
 base=worker.CommonEnvironment
 class PublicOnlyEnvironment(base):
  def __init__(self,ref,method):
   value=shared.load_public_task(ref['task_id']);c=value['contract'];task_path=Path(ref['task_path']).resolve()
   if c['input_digest']!=ref['input_digest']:raise RuntimeError('EXP250_PUBLIC_PREFIX_BINDING_DRIFT')
   def load():
    replay=original_load()
    def resources(path):
     if Path(path).resolve()!=task_path:raise RuntimeError('EXP250_UNDECLARED_RESOURCE_TASK')
     return copy.deepcopy(value['resources_manifest']),copy.deepcopy(value['resources_paths'])
    def export(path):
     if Path(path).resolve()!=task_path:raise RuntimeError('EXP250_UNDECLARED_EXPORT_TASK')
     return copy.deepcopy(value['export_input'])
    def verify(path,harness):
     if Path(path).resolve()!=task_path or Path(harness).resolve()!=Path(c['harness']).resolve():raise RuntimeError('EXP250_PUBLIC_RESOURCE_PATH_DRIFT')
     for name,h in c['harness_sources'].items():
      candidate=Path(name) if Path(name).is_absolute() else Path(c['harness'])/name
      if sha(candidate)!=h:raise RuntimeError('EXP250_PUBLIC_HARNESS_DRIFT')
     for rel,h in c['c0_business_paths_sha256'].items():
      if sha(Path(c['template'])/rel)!=h:raise RuntimeError('EXP250_CURRENT_C0_BUSINESS_SOURCE_DRIFT')
     return True
    replay.resources=resources;replay.export_input=export;replay.verify_execution_binding=verify
    return replay
   environment166.load_replay=load
   try:super().__init__(ref,method)
   finally:environment166.load_replay=original_load
   self.record('EXP250_SHARED_PUBLIC_ONLY_RESOURCE_VIEW',{'public_contract_SHA256':sha(value['source_binding']['public_contract']),
    'original_task_manifest_read':False,'hidden_node_fields_unavailable':True,'empty_actor_hidden_list_not_empty_final_requirement':True,
    'external_Root_original_independent_acceptance_required':True,'trial_id':parent['trial_id'],
    'client_seed_is_request_identity_not_provider_determinism':True})
 worker.CommonEnvironment=PublicOnlyEnvironment
 return worker

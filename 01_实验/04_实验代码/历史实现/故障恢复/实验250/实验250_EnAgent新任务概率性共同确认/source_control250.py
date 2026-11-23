"""Exact task/trial/lease release; preparation never confers execution permission."""
from common166 import *
import copy,re

VERSION='V2_AUTH_DIRECT_PUBLICPACK';V=E
PROTOCOL=E/'protocol225.json';GRANT=E/'root_grant239.json';SEAL=E/'source_seal239.json'
PHASE=read(PROTOCOL)['finance_phase'];MECHANICAL=False;MECHANICAL_NAMESPACE='probe';SINGLE_PUBLIC_LEAF=False

def start_mechanical(*args,**kwargs):raise RuntimeError('EXP250_SCIENCE_ADAPTER_HAS_NO_MECHANICAL_GRANT_ROUTE')

def authorization():
 require_open();p=read(PROTOCOL);g=read(GRANT)
 for name in ('execution_authorized','model_generation_authorized','native_authorized','finance_authorized',
  'Root_local_public_native_qualification_admitted','Root_external_final_source_review_admitted','Root_new_independent_core_run_admitted'):
  if g.get(name) is not True:raise RuntimeError('EXP250_ROOT_TASK_TRIAL_RELEASE_REQUIRED '+name)
 if any(g.get(name) is not False for name in ('private_authorized','once_private_authorized')):raise RuntimeError('EXP250_ACTOR_PRIVATE_FORBIDDEN')
 if p.get('resume_lineage') or p.get('old_candidate_or_paid_response_reuse') is not False:raise RuntimeError('EXP250_NO_OLD_SCIENTIFIC_PREFIX')
 if g.get('trial_id')!=p['trial_id'] or g.get('task_id')!=p['prepared_task_ids'][0] or g.get('finance_phase')!=PHASE:raise RuntimeError('EXP250_EXACT_TRIAL_PHASE_REQUIRED')
 if g.get('protocol_sha256')!=sha(PROTOCOL) or g.get('source_seal_sha256')!=sha(SEAL):raise RuntimeError('EXP250_RUNTIME_SEAL_GRANT_DRIFT')
 if sha(p['root_protocol'])!=p['root_protocol_sha256'] or sha(p['parent_source_seal'])!=p['parent_source_seal_SHA256']:raise RuntimeError('EXP250_PARENT_FROZEN_SCIENCE_DRIFT')
 if g.get('common_contract_SHA256')!=p['root_protocol_sha256'] or g.get('finance_config_SHA256')!=sha(E/'finance_config239.json') or sha(E/'finance_config239.json')!=p['finance_template_sha256']:raise RuntimeError('EXP250_COMMON_FINANCE_BINDING_DRIFT')
 for path,h in {**read(SEAL)['sources'],**read(SEAL)['dependencies']}.items():
  if sha(path)!=h:raise RuntimeError('EXP250_SOURCE_OR_PUBLIC_BINDING_DRIFT '+path)
 lease=g.get('execution_lease_id')
 if not isinstance(lease,str) or not re.fullmatch(r'lease_[0-9]{3,}',lease):raise RuntimeError('EXP250_EXACT_LEASE_ID_REQUIRED')
 p=copy.deepcopy(p);p.update(execution_authorized=True,model_generation_authorized=True,execution_lease_id=lease,
  output_namespace='leases/'+lease+'/f',native_namespace='leases/'+lease+'/n')
 offset=0;prior_active=0;task=p['prepared_task_ids'][0]
 for prior in (E/'supervision'/task).glob('lease_*/supervision.json'):
  row=read(prior)
  if row.get('execution_lease_id')==lease:continue
  if row.get('status')!='STOPPED' or row.get('all_owned_descendants_stopped') is not True:raise RuntimeError('EXP250_PRIOR_SAME_TRIAL_OWN_JOB_STOP_UNKNOWN')
  offset+=row['all_owned_OS_lifetime_counts']['TotalProcesses'];prior_active+=row['actual_elapsed_seconds']
 p['_pool_OS_root_offset']=offset;p['_scientific_lineage_OS_roots_before_lease']=offset;p['_prior_resume_active_elapsed_seconds']=prior_active
 counter=E/'checkpoints'/task/'GLOBAL_ACCOUNTING.json'
 if counter.exists():p['_pool_native_root_offset']=read(counter)['product_native_roots']
 return p

def verify(task,phase):
 p=authorization()
 if p['prepared_task_ids']!=[task] or read(GRANT).get('allowed_task_ids')!=[task] or phase!=PHASE:raise RuntimeError('EXP250_SINGLE_FROZEN_TASK_TRIAL_REQUIRED')
 load_pack(task);return p

def load_pack(task):
 p=read(PROTOCOL)
 if sha(p['shared_public249'])!=p['shared_public249_SHA256']:raise RuntimeError('EXP250_PUBLIC_CODEC_DRIFT')
 shared=module('_exp250_frozen_public_task249',p['shared_public249']);value=shared.load_public_task(task)
 parent=str(Path(p['shared_publicpack_module']).resolve().parent)
 if parent not in sys.path:sys.path.append(parent)
 pub=module('_exp250_common_original_publicpack',p['shared_publicpack_module']);pack=value['pack']
 ref=p['shared_pack_references'][task]
 if sha(ref['path'])!=ref['sha256'] or digest(pub.decode(pack))!=ref['semantic_sha256'] or pack['input_digest']!=ref['input_digest']:raise RuntimeError('EXP250_PACK_OR_SEMANTIC_DRIFT')
 return pub,pack,ref

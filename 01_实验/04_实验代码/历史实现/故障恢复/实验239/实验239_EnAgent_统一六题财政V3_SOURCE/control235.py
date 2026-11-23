"""Fresh six-task grant and common-C0 gate; no inherited CLOSED authority."""
from common166 import *
import copy
VERSION='V3_COMPLETION_UNIFIED_EXISTING_SIX';V=E
PROTOCOL=E/'protocol225.json';GRANT=E/'root_grant239.json';SEAL=E/'source_seal239.json'
PHASE=read(PROTOCOL)['finance_phase'];MECHANICAL=False;MECHANICAL_NAMESPACE='probe'

def source_gate(g):
 require_open();p=read(PROTOCOL)
 if g.get('scope_id')!=p['scope_id'] or g.get('finance_phase')!=PHASE:raise RuntimeError('FRESH_SIX_SCOPE_OR_PHASE_REQUIRED')
 if g.get('protocol_sha256')!=sha(PROTOCOL) or g.get('source_seal_sha256')!=sha(SEAL):raise RuntimeError('FRESH_SIX_GRANT_SHA_DRIFT')
 for path,h in read(SEAL)['sources'].items():
  if sha(path)!=h:raise RuntimeError('FRESH_SIX_RUNTIME_SOURCE_DRIFT '+path)
 for path,h in read(SEAL).get('dependencies',{}).items():
  if sha(path)!=h:raise RuntimeError('FRESH_SIX_DEPENDENCY_DRIFT '+path)
 if sha(p['dataset_provenance_path'])!=p['dataset_provenance_sha256'] or read(p['dataset_provenance_path'])['tasks']!=p['task_order']:raise RuntimeError('EXISTING_DATASET_SIX_IDENTITY_DRIFT')
 if p['deadline']!={'hard_utc':None,'no_new_utc':None} or p['completion_condition']!='six_tasks_complete_or_balance_insufficient':raise RuntimeError('OLD_GLOBAL_FIXED_WINDOW_NOT_ALLOWED')
 return p

def start_mechanical():
 global MECHANICAL
 g=read(E/'mechanical_grant239_v3.json')
 if not (g.get('mechanical_authorized') is True and g.get('native_authorized') is True):raise RuntimeError('NEW_SIX_ROOT_MECHANICAL_REVIEW_REQUIRED')
 source_gate(g);MECHANICAL=True

def authorization():
 if MECHANICAL:
  g=read(E/'mechanical_grant239_v3.json');p=source_gate(g)
  p=copy.deepcopy(p);p.update(execution_authorized=True,model_generation_authorized=False,native_authorized=True,private_authorized=False,once_private_authorized=False,output_namespace=MECHANICAL_NAMESPACE+'/f',native_namespace=MECHANICAL_NAMESPACE+'/n')
  return p
 g=read(GRANT)
 if not all(g.get(k) is True for k in ('execution_authorized','model_generation_authorized','native_authorized')):raise RuntimeError('FRESH_SIX_SCIENCE_ROOT_RELEASE_REQUIRED')
 p=source_gate(g)
 if p.get('root_protocol_pending') or p.get('root_shared_C0_qualification_pending') or p.get('public_repository_testscope_pending'):raise RuntimeError('NEW_COMMON_SCOPE_C0_OR_TESTSCOPE_PENDING')
 q=p['shared_C0_qualification']
 if not q.get('path') or sha(q['path'])!=q.get('sha256'):raise RuntimeError('FRESH_SHARED_C0_QUALIFICATION_REQUIRED')
 if not p.get('common_six_C0_supplement_file') or not p.get('common_six_C0_supplement_sha256'):raise RuntimeError('FRESH_C0_COMMON_SUPPLEMENT_PENDING')
 p=copy.deepcopy(p);p.update(execution_authorized=True,model_generation_authorized=True,native_authorized=True,private_authorized=g.get('private_authorized') is True,once_private_authorized=g.get('once_private_authorized') is True)
 return p

def verify(task,phase):
 p=authorization();g=read(E/('mechanical_grant239_v3.json' if MECHANICAL else 'root_grant239.json'))
 if task not in p['task_order'] or task not in p['prepared_task_ids'] or task not in g['allowed_task_ids'] or phase!=PHASE:raise RuntimeError('EXACT_SELECTED_SIX_TASK_GRANT_REQUIRED')
 if not MECHANICAL and p['task_order'].index(task)>g.get('allowed_through_index',-1):raise RuntimeError('NO_AUTOMATIC_NEXT_SIX_TASK')
 load_pack(task)
 if not MECHANICAL:
  from common_six_C0_supplement239 import load_supplement
  load_supplement(task,p)
 return p

def load_pack(task):
 p=read(PROTOCOL)
 if p.get('root_shared_C0_qualification_pending') or not p.get('shared_registry') or not p.get('shared_pack_references'):raise RuntimeError('NEW_SHARED_COMMON_C0_PACK_NOT_BOUND')
 if sha(p['shared_registry'])!=p['shared_registry_sha256']:raise RuntimeError('NEW_SHARED_REGISTRY_DRIFT')
 if read(p['shared_publisher_seal']).get('V2_pack_registry_sha256')!=p['shared_registry_sha256']:raise RuntimeError('NEW_COMMON_PUBLISHER_DRIFT')
 ref=p['shared_pack_references'][task]
 if sha(ref['path'])!=ref['sha256']:raise RuntimeError('NEW_COMMON_PACK_DRIFT')
 # The publisher imports this exact pure dependency by its canonical name.
 # Load it from the sealed path; do not rely on another worktree being on PATH.
 projection=p['shared_public_projection_module']
 if sha(projection)!=p['shared_public_projection_sha256']:raise RuntimeError('NEW_SHARED_PUBLIC_PROJECTION_DRIFT')
 module('shared_projection224',projection)
 pub=module('exp239_new_six_publicpack',p['shared_publicpack_module']);pack=read(ref['path'])
 if digest(pub.decode(pack))!=ref['semantic_sha256'] or pack['task_id']!=task or pack['input_digest']!=ref['input_digest']:raise RuntimeError('NEW_COMMON_INPUT_DRIFT')
 return pub,pack,ref

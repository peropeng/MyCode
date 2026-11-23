"""V3 prospective one-task gate; Root grants separately authorize mechanical/science."""
from common166 import *
import copy
VERSION='V2_AUTH_DIRECT_PUBLICPACK';V=E
PROTOCOL=E/'protocol225.json';GRANT=E/'root_grant239.json';SEAL=E/'source_seal239.json'
PHASE=read(PROTOCOL)['finance_phase']
MECHANICAL=False;MECHANICAL_NAMESPACE='probe'
def start_mechanical():
 global MECHANICAL
 g=read(E/'mechanical_grant239_v3.json')
 if not (g.get('mechanical_authorized') is True and g.get('native_authorized') is True):raise RuntimeError('V3_ROOT_MECHANICAL_REVIEW_REQUIRED')
 if g.get('protocol_sha256')!=sha(PROTOCOL) or g.get('source_seal_sha256')!=sha(SEAL):raise RuntimeError('V3_MECHANICAL_GRANT_DRIFT')
 for path,h in read(SEAL)['sources'].items():
  if sha(path)!=h:raise RuntimeError('V3_MECHANICAL_SOURCE_DRIFT '+path)
 MECHANICAL=True
def authorization():
 p=read(PROTOCOL)
 if MECHANICAL:
  p=copy.deepcopy(p);p.update(execution_authorized=True,model_generation_authorized=False,output_namespace=MECHANICAL_NAMESPACE+'/f',native_namespace=MECHANICAL_NAMESPACE+'/n')
  return p
 g=read(GRANT)
 if not all(g.get(k) is True for k in ('execution_authorized','model_generation_authorized','native_authorized')):raise RuntimeError('EXP239_ROOT_RELEASE_REQUIRED')
 if g['protocol_sha256']!=sha(PROTOCOL) or g['source_seal_sha256']!=sha(SEAL):raise RuntimeError('EXP239_GRANT_DRIFT')
 for path,h in read(SEAL)['sources'].items():
  if sha(path)!=h:raise RuntimeError('EXP239_SOURCE_DRIFT '+path)
 if g.get('finance_phase')!=PHASE:raise RuntimeError('EXP239_PHASE_MISMATCH')
 p=copy.deepcopy(p);p.update(execution_authorized=True,model_generation_authorized=True)
 return p
def verify(task,phase):
 p=authorization()
 if task not in p['prepared_task_ids']:raise RuntimeError('V3_ONLY_PROSPECTIVE_PREPARED_TASK')
 if MECHANICAL and task not in read(E/'mechanical_grant239_v3.json')['allowed_task_ids']:raise RuntimeError('V3_MECHANICAL_TASK_NOT_GRANTED')
 if not MECHANICAL and task not in read(GRANT)['allowed_task_ids']:raise RuntimeError('V3_SCIENCE_TASK_NOT_GRANTED')
 if phase!=PHASE or task not in p['task_order']:raise RuntimeError('EXP239_TASK_NOT_FROZEN')
 if not MECHANICAL and p['task_order'].index(task)>read(GRANT).get('allowed_through_index',-1):raise RuntimeError('EXP239_TASK_NOT_GRANTED')
 load_pack(task)
 return p
def load_pack(task):
 p=read(PROTOCOL)
 if sha(p['shared_registry'])!=p['shared_registry_sha256']:raise RuntimeError('SHARED_REGISTRY_DRIFT')
 if read(p['shared_publisher_seal']).get('V2_pack_registry_sha256')!=p['shared_registry_sha256']:raise RuntimeError('PUBLISHER_DRIFT')
 ref=p['shared_pack_references'][task]
 if sha(ref['path'])!=ref['sha256']:raise RuntimeError('SHARED_PACK_DRIFT')
 pub=module('exp239_publicpack',p['shared_publicpack_module']);pack=read(ref['path'])
 if digest(pub.decode(pack))!=ref['semantic_sha256'] or pack['task_id']!=task or pack['input_digest']!=ref['input_digest']:raise RuntimeError('SHARED_INPUT_DRIFT')
 return pub,pack,ref

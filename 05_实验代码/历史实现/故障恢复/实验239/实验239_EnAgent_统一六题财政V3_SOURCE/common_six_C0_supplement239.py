"""Validate immutable fresh-C0 references; Root common-v4 alone injects them."""
from common166 import *
def refs_from_registry(registry,tasks):
    values=registry.get('task_supplements',registry.get('task_files',registry.get('tasks')))
    if isinstance(values,list):
        pairs=[(v.get('task',v.get('task_id')),v) for v in values]
        if len({t for t,v in pairs})!=len(pairs):raise RuntimeError('COMMON_C0_DUPLICATE_TASK')
        values=dict(pairs)
    if not isinstance(values,dict) or set(values)!=set(tasks):raise RuntimeError('COMMON_C0_EXACT_SELECTED_SIX_REQUIRED')
    return values
def load_supplement(task,p):
    path=p.get('common_six_C0_supplement_file');expected=p.get('common_six_C0_supplement_sha256')
    if not path or not expected:raise RuntimeError('NEW_SHARED_C0_SUPPLEMENT_REQUIRED_BEFORE_MODEL')
    owner_root=(ROOT/'工作区/1010-unified-six').resolve()
    if not Path(path).resolve().is_relative_to(owner_root):raise RuntimeError('COMMON_C0_ROOT_APPROVED_INPUT_SCOPE_REQUIRED')
    if sha(path)!=expected:raise RuntimeError('NEW_SHARED_C0_SUPPLEMENT_REGISTRY_DRIFT')
    registry=read(path);refs=refs_from_registry(registry,p['task_order']);ref=refs[task]
    if not isinstance(ref,dict):raise RuntimeError('COMMON_C0_EXPLICIT_FILE_SHA_REQUIRED')
    item=ref.get('path',ref.get('file'));h=ref.get('sha256',ref.get('SHA256'))
    if not item or not Path(item).resolve().is_relative_to(owner_root):raise RuntimeError('COMMON_C0_ROOT_APPROVED_TASK_FILE_REQUIRED')
    if not item or not h or sha(item)!=h:raise RuntimeError('COMMON_C0_TASK_SUPPLEMENT_DRIFT')
    value=read(item)
    if value.get('task',value.get('task_id'))!=task:raise RuntimeError('COMMON_C0_TASK_IDENTITY_DRIFT')
    # Root supplies only the fresh original public goal+ordinary record. Keep the
    # entire approved object exactly; original pack is a separate immutable input.
    return value,{'registry_sha256':expected,'supplement_file_sha256':h,'task':task,'complete_approved_public_object':True,'no_private_result_or_label_generated':True}

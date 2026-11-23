"""Reusable masked-public pytest transport; caller owns Job, budgets and output.

No native process, product import, provider or finance construction on import.
The C0 PASS pool is an actual run result, never inferred from a file inventory.
"""
import copy,hashlib,json,os,shutil,time
from pathlib import Path

HERE=Path(__file__).resolve().parent
SCHEMA='masked-public-native-collection-run/1'

def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text('utf-8-sig'))
def save(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf-8')

def safe_rel(value):
    p=Path(value)
    if not isinstance(value,str) or p.is_absolute() or '..' in p.parts or '.git' in p.parts or ':' in value or '\\' in value:raise ValueError('MASKED_PUBLIC_RELATIVE_PATH_REQUIRED')
    return p.as_posix()

def load_scope(protocol,task):
    ref=protocol['public_test_scope_contract'];path=Path(ref['path']).resolve()
    if sha(path)!=ref['sha256']:raise ValueError('MASKED_PUBLIC_SCOPE_CONTRACT_DRIFT')
    value=read(path)
    if not value.get('all_four_methods_same_read_execute_permission') or not value.get('original_unmasked_repo_test_source_or_git_blobs_must_not_be_actor_accessible'):raise ValueError('MASKED_PUBLIC_FOUR_METHOD_BOUNDARY_REQUIRED')
    rows={r['task_id']:r for r in value['tasks']}
    if set(rows)!=set(protocol['task_order']) or task not in rows:raise ValueError('MASKED_PUBLIC_SELECTED_SIX_REQUIRED')
    row=copy.deepcopy(rows[task]);root=Path(row['public_source_repo_view']).resolve()
    owner=path.parent.resolve()
    if not root.is_relative_to(owner) or not row.get('actor_tests_are_immutable') or not row.get('actors_may_read_or_execute_only_this_public_test_view'):raise ValueError('MASKED_PUBLIC_SOURCE_OWNER_REQUIRED')
    files=dict(row['business_and_support_files_in_view']);files.update(row['public_test_py_files_SHA256'])
    for rel,h in files.items():
        safe_rel(rel);p=root/rel
        if p.is_symlink() or not p.is_file() or sha(p)!=h:raise ValueError('MASKED_PUBLIC_VIEW_FILE_DRIFT '+rel)
    row['all_public_view_files_SHA256']=files
    row['scope_contract_SHA256']=ref['sha256']
    return row

def support_inventory(row,business_paths):
    return {p:h for p,h in row['all_public_view_files_SHA256'].items() if p not in business_paths}

def materialize_support(root,row,business_inventory):
    root=Path(root).resolve();origin=Path(row['public_source_repo_view']).resolve()
    for rel,h in business_inventory.items():
        if sha(root/rel)!=h:raise ValueError('CURRENT_BUSINESS_C0_BYTES_DRIFT '+rel)
    supports=support_inventory(row,business_inventory)
    for rel,h in supports.items():
        dest=root/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():
            if dest.is_symlink() or sha(dest)!=h:raise ValueError('MASKED_SUPPORT_COLLISION '+rel)
        else:shutil.copyfile(origin/rel,dest)
    for rel,h in business_inventory.items():
        if sha(root/rel)!=h:raise ValueError('MASKED_SUPPORT_OVERWROTE_C0 '+rel)
    return supports

def verify_actor(root,business_paths,supports):
    root=Path(root).resolve()
    for rel,h in supports.items():
        p=root/rel
        if p.is_symlink() or not p.is_file() or sha(p)!=h:raise ValueError('IMMUTABLE_MASKED_ACTOR_SUPPORT_DRIFT '+rel)
    for rel in business_paths:
        if (root/rel).is_symlink() or not (root/rel).is_file():raise ValueError('ACTOR_BUSINESS_PATH_MISSING '+rel)

def validate_selectors(row,targets):
    if targets is None:return sorted(row['public_test_py_files_SHA256'])
    if not isinstance(targets,list) or not targets:raise ValueError('MASKED_PUBLIC_EXPLICIT_SELECTORS_REQUIRED')
    values=[]
    for item in targets:
        if not isinstance(item,str):raise ValueError('MASKED_PUBLIC_SELECTOR_STRING_REQUIRED')
        rel=item.split('::',1)[0];safe_rel(rel)
        if rel not in row['public_test_py_files_SHA256']:raise ValueError('TEST_SELECTOR_OUTSIDE_MASKED_PUBLIC_VIEW')
        if item not in values:values.append(item)
    return values

def assess(raw,execution,collect_only):
    collected=raw.get('collected',[]);outcomes=raw.get('outcomes',{})
    source_ok=raw.get('product_origin_within_current_actor') is True
    stable=execution.get('business_state_unchanged') and execution.get('masked_support_unchanged')
    stopped=execution.get('stop_receipt',{}).get('all_owned_descendants_terminated') is True
    infrastructure=bool(raw.get('product_import_error') or raw.get('collection_errors') or execution.get('guard_denials'))
    valid_exit=execution.get('exit_code') in ({0,1,5} if collect_only else {0,1}) and type(execution.get('exit_code')) is int
    complete=bool(stable and stopped and source_ok and execution.get('guard_loaded') and execution.get('scope_log_complete') and not execution.get('timeout') and valid_exit and not infrastructure and raw.get('session_finished'))
    if collect_only:
        return {'known':complete,'status':'COLLECTION_COMPLETE' if complete else 'COLLECTION_UNKNOWN','current_C0_PASS_pool':None,'collection_is_not_PASS_evidence':True}
    leaf_complete=bool(collected) and set(outcomes)==set(collected) and all(any(p['when']=='teardown' for p in v.get('phases',[])) and v.get('status') in {'passed','failed','error','skipped'} for v in outcomes.values())
    complete=complete and leaf_complete
    return {'known':complete,'status':'PUBLIC_RUN_COMPLETE' if complete else 'PUBLIC_RUN_UNKNOWN','current_C0_PASS_pool':[n for n in collected if outcomes.get(n,{}).get('status')=='passed'] if complete else None,'completed_leaf_coverage':leaf_complete,'no_unknown_leaf_filled_FAIL':True}

def execute(env,root,row,targets=None,*,collect_only=False,label='masked_public',protocol=None,owner_check=None):
    """Generic env API: _require/native_lane/run.qualify.execute/out/paths/package.

    The caller must install its typed Job/native cap executor before this call.
    q.execute owns child STOP; no subprocess escapes the existing owner path.
    """
    env._require();p=protocol
    if p is None:raise ValueError('EXPLICIT_CURRENT_METHOD_PROTOCOL_REQUIRED')
    if not callable(owner_check) or not owner_check():raise ValueError('MASKED_NATIVE_REQUIRES_OWNED_PARENT_JOB')
    root=Path(root).resolve()
    owner=Path(p['masked_native_owner_root']).resolve();guard=Path(p['masked_native_guard_directory']).resolve()
    if not root.is_relative_to(owner):raise ValueError('MASKED_NATIVE_OWNED_ACTOR_ROOT_REQUIRED')
    selectors=validate_selectors(row,targets)
    business={rel:sha(root/rel) for rel in env.business_files()}
    supports=support_inventory(row,business);verify_actor(root,business,supports)
    if env.native_calls>=p['budget']['native_roots_total']:raise RuntimeError('DECLARED_PRODUCT_NATIVE_ROOT_CAP')
    env.native_calls+=1;ordinal=env.native_calls
    out=Path(env.out)/'masked_public_native'/f'{ordinal:04d}_{label}';out.mkdir(parents=True,exist_ok=False)
    q=env.run.qualify;python=Path(env._paths['python']).resolve()
    child_env=q.isolated_env(out,root,root,out,python,env.package)
    child_env['PYTHONPATH']=os.pathsep.join((str(guard),str(q.HERE),str(root)))
    # The original private tree is a denied path, not a pytest input or reader.
    plan={'schema':SCHEMA,'task_id':env.task_id,'package':env.package,'actor_root':str(root),'output':str(out),'selectors':selectors,'collect_only':collect_only,'business_SHA256':business,'masked_support_SHA256':supports,'scope_contract_SHA256':row['scope_contract_SHA256'],'original_private_denied_root':str(env._paths['frozen']),'trusted_qualifier':str(q.HERE),'source_view_manifest_SHA256':hashlib.sha256(canonical(row['all_public_view_files_SHA256']).encode()).hexdigest()}
    save(out/'plan.json',plan)
    child_env.update(EA_MASKED_PUBLIC_PLAN=str(out/'plan.json'),EA_MASKED_PUBLIC_ORIGINAL_GUARD=str(Path(q.HERE)/'sitecustomize.py'))
    timeout=min(float(p['budget']['native_timeout_seconds']),max(.1,env.time_left()))
    with env.native_lane():
        env._require();result=q.execute([str(python),'-B',str(guard/'runner.py'),str(out/'plan.json')],root,out/'execution.log',timeout,child_env)
    raw=read(out/'outcomes.json') if (out/'outcomes.json').is_file() else {}
    after_business={rel:sha(root/rel) for rel in business};after_support={rel:sha(root/rel) for rel in supports}
    denials=[];scope_rows=[]
    if (out/'masked_scope_events.jsonl').exists():
        scope_rows=[json.loads(v) for v in (out/'masked_scope_events.jsonl').read_text('utf-8').splitlines() if v.strip()]
        denials=[v for v in scope_rows if v.get('allowed') is False]
    if (out/'guard_events.jsonl').exists():
        denials.extend({'original_native_guard_denial':json.loads(v)} for v in (out/'guard_events.jsonl').read_text('utf-8').splitlines() if v.strip())
    scope_complete=bool(scope_rows and scope_rows[0].get('event')=='MASKED_PUBLIC_SCOPE_INSTALL' and scope_rows[-1].get('event')=='MASKED_PUBLIC_SCOPE_CLOSE')
    execution={**result,'business_state_unchanged':after_business==business,'masked_support_unchanged':after_support==supports,'guard_loaded':(out/'masked_guard_ready.json').is_file(),'scope_log_complete':scope_complete,'scope_log_rows':len(scope_rows),'guard_denials':denials}
    judged=assess(raw,execution,collect_only)
    record={'schema':SCHEMA,'task_id':env.task_id,'kind':'collection' if collect_only else 'run','selected_test_paths_or_leafs':selectors,'actual_business_SHA256':business,'actual_masked_support_SHA256':supports,'scope_contract_SHA256':row['scope_contract_SHA256'],'python_requested':str(python),'execution':execution,'pytest':raw,**judged,'private_or_gold_input':False,'C0_PASS_pool_from_actual_native_only':True,'partial_outcomes_retained':True,'original_private_feedback_to_actor':False}
    save(out/'run.json',record)
    env.record('masked_public_collection_or_run239',{'record':str(out/'run.json'),'sha256':sha(out/'run.json'),'kind':record['kind'],'status':record['status'],'known':record['known'],'public_scope_SHA256':row['scope_contract_SHA256'],'original_private_input':False})
    return record

"""Root-owned masked view and current C0 references; import has no execution."""
from common166 import *
import copy, shutil

def canonical_record_paths(value):
    if isinstance(value,list):
        for item in value:canonical_record_paths(item)
    elif isinstance(value,dict):
        record=value.get('native_record');path=record.get('path') if isinstance(record,dict) else None
        if isinstance(path,str) and path.replace('\\','/').startswith('/public-feedback/'):
            tail=[v for v in path.replace('\\','/').split('/') if v][1:]
            if tail and tail[0]=='public_native':tail=tail[1:]
            record['path']='/public-feedback/'+'/'.join(tail)
        for item in value.values():canonical_record_paths(item)

def source_contract():
    p=read(TIME_AUTHORITY)
    spec=p['shared_masked_native_source']
    path=Path(spec['path']).resolve()
    if not path.is_relative_to((ROOT/'工作区/1010-unified-six/shared_native_v14_certificate_complete').resolve()) or sha(path)!=spec['sha256']:
        raise RuntimeError('EXP242_SHARED_MASKED_SOURCE_UNKNOWN_OR_DRIFT')
    for guard_path,expected in spec['guard_sources_sha256'].items():
        if sha(guard_path)!=expected:raise RuntimeError('EXP242_SHARED_MASKED_GUARD_SOURCE_DRIFT')
    return p,module('_shared_masked_native239_for_242',path)

def oracle_reference(env):
    contract=read(TIME_AUTHORITY)['public_goal_ordinary_oracle_contract']
    if sha(contract['path'])!=contract['sha256']:raise RuntimeError('EXP242_PUBLIC_ORACLE_PERMISSION_DRIFT')
    doc=read(contract['path']);row=next(r for r in doc['tasks'] if r['task_id']==env.task_id)
    if (not row['same_four_methods'] or row['private_hidden_feedback_to_model'] or row['new_Gold_read']
            or set(row['target_nodes'])!=set(env.recovery_goal_nodes)
            or set(row['ordinary_nodes'])!=set(env.public_regression_nodes)
            or Path(row['trusted_native_oracle_root']).resolve()!=Path(env._paths['frozen']).resolve()):
        raise RuntimeError('EXP242_PUBLIC_ORACLE_NODES_OR_TRUSTED_ROOT_UNKNOWN')
    return row

def common_C0_reference(task):
    p=read(TIME_AUTHORITY);config=read(E/'finance_config240.json')
    expected=p['finance']['config_sha256']
    if sha(E/'finance_config240.json')!=expected:
        raise RuntimeError('EXP242_ROOT_FINANCE_V4_CONFIG_DRIFT')
    path=Path(p['finance']['common_input_module']).resolve()
    if sha(path)!=p['finance']['common_input_module_sha256']:
        raise RuntimeError('EXP242_COMMON_C0_LOADER_SOURCE_DRIFT')
    codec_path=path.parent/'common_public_feedback_codec.py'
    if sha(codec_path)!=config['transport_source_SHA256']['common_public_feedback_codec.py']:
        raise RuntimeError('EXP242_ROOT_COMMON_C0_CODEC_DRIFT')
    module('common_public_feedback_codec',codec_path)
    common=module('_exp242_Root_common_model_input_six',path)
    supplement,decoded=common.supplement(config,task)
    if supplement['independent_final_or_Gold_or_other_methods_outputs'] is not False:
        raise RuntimeError('EXP242_COMMON_C0_HAS_FORBIDDEN_OTHER_EVIDENCE')
    return supplement,decoded

def install_actor(env):
    p,runner=source_contract();row=runner.load_scope(p,env.task_id)
    oracle_reference(env)
    root=env.repo_root.resolve()
    if not root.is_relative_to(E.resolve()):raise RuntimeError('EXP242_MASKED_ACTOR_OUTSIDE_OWNED_E')
    business={rel:sha(root/rel) for rel in env.business_files()}
    expected=env.pack['c0_business_paths_sha256']
    if {rel:hashlib.sha256(text.encode()).hexdigest() for rel,text in env.business_files().items()}!=expected:
        raise RuntimeError('EXP242_MASKED_INSTALL_C0_BUSINESS_DRIFT')
    # Materialize is private plumbing before any model reader; remove every
    # original auxiliary byte, including tests and Git, before adding Root view.
    for dest in sorted(root.rglob('*'),key=lambda f:len(f.parts),reverse=True):
        if dest.is_symlink():raise RuntimeError('EXP242_ACTOR_SYMLINK_NOT_ALLOWED')
        resolved=dest.resolve()
        if not resolved.is_relative_to(root):raise RuntimeError('EXP242_ACTOR_CLEANUP_ESCAPED_ROOT')
        if dest.is_file() and dest.relative_to(root).as_posix() not in business:dest.unlink()
        elif dest.is_dir() and not any(dest.iterdir()):dest.rmdir()
    supports=runner.materialize_support(root,row,business)
    runner.verify_actor(root,business,supports)
    actual=env.run.qualify.inventory(root)
    if set(actual)!=set(business)|set(supports):raise RuntimeError('EXP242_UNMASKED_ACTOR_AUXILIARY_REMAINS')
    env._original=copy.deepcopy(actual)
    env.masked_public_row=row;env.masked_public_supports=supports
    env._masked_shared_runner=runner
    env.initial_snapshot=env.snapshot('Root_masked_C0_baseline')
    env.record('masked_public_source_boundary242',{'scope_SHA256':row['scope_contract_SHA256'],
        'business_SHA256_exact_preserved':len(business),'immutable_masked_support_files':len(supports),
        'original_unmasked_tests_or_Git_in_actor':False,'frozen_final_tree_unchanged':True,
        'actual_test_pool_or_test_collection':None,'native_model_private':0})

def verify_actor(env):
    _,runner=source_contract()
    runner.verify_actor(env.repo_root,env.business_files(),env.masked_public_supports)
    actual=env.run.qualify.inventory(env.repo_root)
    if set(actual)-set(env.business_files())!=set(env.masked_public_supports):
        raise RuntimeError('EXP242_UNAUTHORIZED_AUXILIARY_OR_GIT_BLOB')

def actual_parent_job_member(env):
    """Root names the controller Job; query current held process membership."""
    import ctypes
    from ctypes import wintypes
    import common166
    grant=read(E/('root_masked_mechanical242.json' if common166.ACTIVE_MASKED_MECHANICAL_SCOPE is not None else 'root_public_C0_release242.json' if common166.ACTIVE_PUBLIC_C0_SCOPE is not None else 'root_release240.json'))
    name=grant.get('parent_owned_job_name')
    if not isinstance(name,str) or not name.startswith('RootUnifiedSix242_'):
        raise RuntimeError('EXP242_ROOT_PARENT_JOB_IDENTITY_NOT_BOUND')
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.OpenJobObjectW.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.LPCWSTR];k.OpenJobObjectW.restype=wintypes.HANDLE
    k.GetCurrentProcess.argtypes=[];k.GetCurrentProcess.restype=wintypes.HANDLE
    k.IsProcessInJob.argtypes=[wintypes.HANDLE,wintypes.HANDLE,ctypes.POINTER(wintypes.BOOL)];k.IsProcessInJob.restype=wintypes.BOOL
    k.CloseHandle.argtypes=[wintypes.HANDLE];k.CloseHandle.restype=wintypes.BOOL
    job=k.OpenJobObjectW(0x0004,False,name)
    if not job:raise RuntimeError('EXP242_ROOT_PARENT_JOB_OPEN_UNKNOWN')
    try:
        member=wintypes.BOOL()
        if not k.IsProcessInJob(k.GetCurrentProcess(),job,ctypes.byref(member)):
            raise RuntimeError('EXP242_ACTUAL_PARENT_JOB_QUERY_UNKNOWN')
        if not member.value:raise RuntimeError('EXP242_CONTROLLER_NOT_IN_ROOT_SPECIFIC_JOB')
        return True
    finally:k.CloseHandle(job)

TOOLS=[{'type':'function','function':{'name':'list_public_masked_tests',
    'description':'List the common readonly masked public repository test files. Original unmasked tests and independent final tests are unavailable.',
    'parameters':{'type':'object','properties':{},'additionalProperties':False}}},
 {'type':'function','function':{'name':'read_public_masked_test',
    'description':'Read one complete common readonly masked public repository test file, or an explicit line interval. Test editing is forbidden.',
    'parameters':{'type':'object','properties':{'path':{'type':'string'},'start_line':{'type':'integer','minimum':1},'end_line':{'type':'integer','minimum':1}},'required':['path'],'additionalProperties':False}}}]

def reader(env,name,args):
    verify_actor(env)
    files=env.masked_public_row['public_test_py_files_SHA256']
    if name=='list_public_masked_tests':return {'paths':sorted(files),'readonly':True,'complete':True,'scope_SHA256':env.masked_public_row['scope_contract_SHA256']}
    if name!='read_public_masked_test':raise ValueError('UNKNOWN_MASKED_READER')
    rel=args['path'].removeprefix('/workspace/repo/').removeprefix('repo/')
    env._masked_shared_runner.safe_rel(rel)
    if rel not in files:raise ValueError('ORIGINAL_OR_FINAL_TEST_NOT_IN_PUBLIC_MASKED_SCOPE')
    path=env.repo_root/rel
    if sha(path)!=files[rel]:raise ValueError('IMMUTABLE_PUBLIC_MASKED_TEST_DRIFT')
    rows=path.read_text('utf-8').splitlines(keepends=True);start=args.get('start_line',1);end=args.get('end_line',len(rows))
    if type(start)!=int or type(end)!=int or not 1<=start<=end<=len(rows):raise ValueError('INVALID_EXPLICIT_TEST_LINE_RANGE')
    return {'path':rel,'start_line':start,'end_line':end,'total_lines':len(rows),'complete_requested_text':''.join(rows[start-1:end]),'whole_source_sha256':files[rel],'readonly':True,'no_silent_clipping':True}

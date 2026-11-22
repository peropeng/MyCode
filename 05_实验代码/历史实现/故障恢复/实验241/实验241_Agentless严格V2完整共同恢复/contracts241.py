"""Public-only contract, byte-preserving clone and phase-specific source guards."""
import copy, datetime, hashlib, importlib.util, json, os, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ROOT_MAIN = ROOT / '工作区/1008-2320-baseline-main'
REGISTRY_SHA = '298efeac0dcf0498ed8f78e0067c8e24a963e24c29442fc0df64d8e047b7a37c'
SOURCE_PIN = '5ce5888b9f149beaace393957a55ea8ee46c9f71'
NO_NEW = '2026-10-10T03:40:00Z'
HARD = '2026-10-10T04:00:00Z'
METHOD = 'AGENTLESS_FSE2025_4L4P4T_FLASH'
FINANCE_PHASE = 'AgentlessPilot24120261010'
def deadline_epoch(value):
    return float('inf') if value is None else datetime.datetime.fromisoformat(value).timestamp()

class EngineeringUnknown(RuntimeError): pass
class DeclaredBudgetEnd(RuntimeError): pass
class IllegalTool(ValueError): pass

def read(p): return json.loads(Path(p).read_text('utf-8-sig'))
def canonical(x): return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
def digest(x): return hashlib.sha256(canonical(x).encode()).hexdigest()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inside(p, root):
    try: Path(p).resolve().relative_to(Path(root).resolve()); return True
    except ValueError: return False
def save(p, value, scope=HERE):
    p = Path(p).resolve()
    if not inside(p, scope): raise EngineeringUnknown('WRITE_SCOPE')
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + '.' + str(os.getpid()) + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(tmp, p)
def inventory(root):
    root=Path(root).resolve(); out={}
    for p in root.rglob('*'):
        if p.is_symlink(): raise EngineeringUnknown('SYMLINK_IN_TREE')
        if p.is_file() and not set(p.relative_to(root).parts)&{'.git','__pycache__','.pytest_cache'}:
            out[p.relative_to(root).as_posix()]=sha(p)
    return out
def module(name, path):
    spec=importlib.util.spec_from_file_location(name, path); m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m; spec.loader.exec_module(m); return m
def decode(pack):
    pool=pack['unique_exact_lines']
    def visit(x):
        if isinstance(x,dict) and set(x)=={'$public_text_lines'}: return ''.join(pool[i] for i in x['$public_text_lines'])
        if isinstance(x,dict): return {k:visit(v) for k,v in x.items()}
        if isinstance(x,list): return [visit(v) for v in x]
        return x
    value=visit(pack['semantic_structure'])
    if digest(value)!=pack['decoded_semantic_sha256']: raise EngineeringUnknown('LOSSLESS_PUBLIC_PACK_DRIFT')
    return value
def business_path(rel, package):
    parts=Path(rel).parts; roots={'conan','conans'} if package=='conans' else {package}
    return bool(parts and parts[0] in roots and rel.endswith('.py') and not set(parts)&{'test','tests','.git','__pycache__'} and '..' not in parts)
def copy_bytes(source, target, paths):
    source=Path(source).resolve(); target=Path(target).resolve()
    if target.exists(): raise EngineeringUnknown('CLONE_ALREADY_EXISTS_NO_REPEAT')
    target.mkdir(parents=True)
    for rel, expected in paths.items():
        src=source/rel; dest=target/rel
        if not inside(src,source) or not inside(dest,target) or src.is_symlink() or sha(src)!=expected:
            raise EngineeringUnknown('C0_SOURCE_OR_PATH_DRIFT '+rel)
        dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(src.read_bytes())
    if inventory(target)!=paths: raise EngineeringUnknown('BYTE_CLONE_NOT_EXACT')

def prepare_public_contract(task_id, destination):
    """Only existing public metadata/source hashes; no old response/patch/results."""
    parent=read(ROOT_MAIN/'frozen_main_v2_remaining21_protocol.json')
    registry=Path(parent['common_pack']['registry'])
    if sha(registry)!=REGISTRY_SHA: raise EngineeringUnknown('REGISTRY_DRIFT')
    row=next(r for r in read(registry)['tasks'] if r['task_id']==task_id)
    if sha(row['path'])!=row['sha256']: raise EngineeringUnknown('PACK_DRIFT')
    pack=read(row['path']); semantic=decode(pack)
    current=ROOT/'工作区/1008-2320-exp224-flash-common/实验/实验224_二十三题Flash完整共同恢复比较'
    refs=read(current/'data/selected_task_bindings.json')
    ref=next(r for r in refs['tasks'] if r['task_id']==task_id)
    # Manifest parsing is only for public node identities. No private nodes,
    # outcomes, reference patches, Gold files or previously selected outputs.
    mf=read(Path(ref['task_path'])/'task_manifest.json')
    public_nodes=list(mf['visible_target_tests'])
    ordinary=list(semantic['public_regression_tests'])
    inv=read(ref['saved_source_inventory'])
    harness=Path(ref['harness'])
    value={'schema':'PatchPilotNative-public-only-contract/1','task_id':task_id,'input_version':'V2_AUTH_DIRECT_PUBLICPACK',
           'source_pin':SOURCE_PIN,'registry':str(registry),'registry_sha256':REGISTRY_SHA,
           'pack':str(row['path']),'pack_sha256':row['sha256'],'input_digest':row['input_digest'],
           'semantic_sha256':row['semantic_sha256'],'c0_business_inventory_sha256':row['c0_business_inventory_sha256'],
           'c0_business_paths_sha256':pack['c0_business_paths_sha256'],
           'template':ref['template'],'template_inventory':inv['template'],
           'frozen_public_test_root':ref['frozen_tests'],'frozen_inventory_sha256':digest(inv['frozen_tests']),
           'frozen_inventory':inv['frozen_tests'], 'package':ref['package'],
           'logical_product_python':ref['python'], 'physical_product_python_expected':None,
           'physical_product_python_verified_by':'root neutral mechanical self identity, not inferred from launcher',
           'public_target_nodes':public_nodes,'ordinary_nodes':ordinary,
           'issue':semantic['original_issue'],'repository':mf.get('repository','public-repository'),
           'harness':str(harness),'harness_sources':{str(harness/n):sha(harness/n) for n in ('qualify.py','sitecustomize.py','qualification_plugin.py')},
           'source_inventory_reference':ref['saved_source_inventory'],
           'source_inventory_reference_sha256':sha(ref['saved_source_inventory']),
           'actor_private_nodes_fields_or_callback':False,'old_model_outputs_selected_patches_Gold':False}
    if not public_nodes or not ordinary or set(public_nodes)&set(ordinary):
        raise EngineeringUnknown('NONEMPTY_DISJOINT_PUBLIC_TARGET_ORDINARY_REQUIRED')
    if digest(value['c0_business_paths_sha256'])!=row['c0_business_inventory_sha256']:
        raise EngineeringUnknown('C0_INVENTORY_DIGEST_DRIFT')
    for rel,expected in value['c0_business_paths_sha256'].items():
        if not business_path(rel,ref['package']) or sha(Path(ref['template'])/rel)!=expected:
            raise EngineeringUnknown('PUBLIC_C0_BYTES_DRIFT '+rel)
    save(destination,value); return value

def verify_grant(protocol, grant, source_seal, task_id, now=None):
    now=time.time() if now is None else now
    if grant.get('schema')!='Agentless241-root-grant/1' or grant.get('root_authorized') is not True or grant.get('model_generation_authorized') is not True:
        raise EngineeringUnknown('EXPLICIT_BACKUP_ROOT_GRANT_REQUIRED')
    if protocol.get('execution_authorized') is not True or protocol.get('finance_phase')!=FINANCE_PHASE:
        raise EngineeringUnknown('BACKUP_MAIN_PROTOCOL_NOT_RELEASED')
    if grant.get('finance_phase')!=FINANCE_PHASE or grant.get('task_id')!=task_id or protocol['task_id']!=task_id:
        raise EngineeringUnknown('TASK_OR_PHASE_GRANT_MISMATCH')
    if protocol['deadline']!={'no_new_utc':NO_NEW,'hard_utc':HARD}:
        raise EngineeringUnknown('BACKUP_FROZEN_DEADLINES_CHANGED')
    if now>=deadline_epoch(NO_NEW): raise EngineeringUnknown('GLOBAL_NO_NEW_CUTOFF')
    if protocol['budget']!={'model_calls_total':64,'output_tokens_total':65536,'max_per_call_output':16384,'wall_seconds':900,'native_roots_total':90,'native_timeout_seconds':90,'product_native_roots_total':64}:
        raise EngineeringUnknown('COMMON_BUDGET_CHANGED')
    if grant['source_seal_sha256']!=digest(source_seal) or grant['protocol_sha256']!=digest(protocol):
        raise EngineeringUnknown('SOURCE_OR_PROTOCOL_GRANT_DRIFT')
    if protocol['registry_sha256']!=REGISTRY_SHA or grant['registry_sha256']!=REGISTRY_SHA:
        raise EngineeringUnknown('COMMON_REGISTRY_GRANT_DRIFT')
    if not grant.get('neutral_mechanical_qualification_sha256') or not grant.get('parent_controller_job_qualified'):
        raise EngineeringUnknown('NEW_MECHANICAL_AND_PARENT_JOB_REQUIRED')
    for p,expected in source_seal['sources'].items():
        if sha(p)!=expected: raise EngineeringUnknown('BACKUP_SEALED_SOURCE_DRIFT '+p)
    for p,expected in source_seal['inputs'].items():
        if sha(p)!=expected: raise EngineeringUnknown('BACKUP_SEALED_INPUT_DRIFT '+p)
    if source_seal['author_pin']!=SOURCE_PIN: raise EngineeringUnknown('AUTHOR_PIN_CHANGED')
    return True

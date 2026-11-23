"""Public-only Exp262 source namespace and atomic writes; import does no work."""
import copy, datetime, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
sys.dont_write_bytecode = True
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
SOURCE = Path(__file__).resolve().parent
E = SOURCE.parent
ROOT = Path('D:/Code/毕设/graduate-thesis-experiments')
P249 = ROOT / '工作区/1012-exp249-prospective-confirmation/实验/实验249_固定顺序新任务共同确认'
P224 = ROOT / '工作区/1008-2320-exp224-flash-common/实验/实验224_二十三题Flash完整共同恢复比较'
P257 = ROOT / '工作区/1012-exp257-source3-postreview/实验/实验257_source3与强SF推断发布'
P259 = ROOT / '工作区/1012-exp259-window-finance-postreview/实验/实验259_四小时连续费用隔离'
OLD = ROOT / '工作区/1011-our19'
COMMON = ROOT / '工作区/1010-unified-six'
CONTROLLER = Path('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')
CONTROLLER_SITE = ROOT / '工作区/0922-exp124-ranking-baselines/.venv/Lib/site-packages'

def canonical(v): return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
def digest(v): return hashlib.sha256(canonical(v).encode()).hexdigest()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p): return json.loads(Path(p).read_text('utf-8-sig'))
def clean(v):
    if isinstance(v, dict): return {str(k): clean(x) for k, x in v.items()}
    if isinstance(v, (set, tuple)): return [clean(x) for x in sorted(v)]
    if isinstance(v, list): return [clean(x) for x in v]
    if isinstance(v, Path): return str(v)
    return v
def owned(p):
    p = Path(p).resolve()
    if not p.is_relative_to(E.resolve()): raise RuntimeError('EXP262_WRITE_SCOPE')
    return p
def save(p, value):
    p = owned(p); p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + '.' + str(os.getpid()) + '.tmp')
    with tmp.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(clean(value), f, ensure_ascii=False, indent=2, allow_nan=False); f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, p)
def module(name, p):
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m
def verify_ref(ref):
    if sha(ref['path']) != ref['sha256']: raise RuntimeError('EXP262_BOUND_ASSET_SHA_DRIFT:' + ref['path'])
    return read(ref['path'])
def verify_seal(ref):
    seal = verify_ref(ref)
    for p,h in {**seal['sources'], **seal.get('dependencies', {}), **seal.get('public_inputs_SHA256', {})}.items():
        if sha(p) != h: raise RuntimeError('EXP262_SOURCE_OR_INPUT_DRIFT:' + p)
    return seal
class BoundaryReady(BaseException): pass
class BudgetExhausted(RuntimeError): pass

"""Independent complete Agentless trial state; import has no execution clients."""
import ast, copy, datetime, hashlib, importlib.util, json, os, sys, time
from decimal import Decimal
from pathlib import Path

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=Path('D:/Code/毕设/graduate-thesis-experiments')
E249=ROOT/'工作区/1012-exp249-prospective-confirmation/实验/实验249_固定顺序新任务共同确认'
SHARED=E249/'method_sources'
sys.path.insert(0,str(SHARED))
OLD=ROOT/'工作区/1011-our19'
FIN=ROOT/'工作区/1010-unified-six/finance_queue_remaining_SOURCE'
METHOD='AGENTLESS_FULL'
AUTHOR_METHOD='AGENTLESS_FSE2025_4L40P40T_FLASH'
PHASE='Until0900ConfirmAgentless24920261012'

def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def clean(v):
 if isinstance(v,dict):return {str(k):clean(x) for k,x in v.items()}
 if isinstance(v,(tuple,set)):return [clean(x) for x in (sorted(v) if isinstance(v,set) else v)]
 if isinstance(v,list):return [clean(x) for x in v]
 if isinstance(v,Path):return str(v)
 return v
def save(p,v):
 p=Path(p).resolve()
 if not p.is_relative_to(HERE):raise RuntimeError('EXP251_WRITE_SCOPE')
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.'+str(os.getpid())+'.tmp')
 with tmp.open('x',encoding='utf-8') as f:
  json.dump(clean(v),f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def ref(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def verify_source_seal(p):
 s=read(p)
 for path,h in s['sources_SHA256'].items():
  if sha(path)!=h:raise RuntimeError('EXP251_SOURCE_DRIFT '+path)
 for path,h in s.get('public_inputs_SHA256',{}).items():
  if sha(path)!=h:raise RuntimeError('EXP251_PUBLIC_INPUT_DRIFT '+path)
 return s
def shared_modules():
 sys.path.insert(0,str(SHARED))
 return module('_exp251_shared_public',SHARED/'shared_public249.py'),module('_exp251_shared_input',SHARED/'shared_input249.py')
def trial_seed(c,role,seed):
 return int(hashlib.sha256(canonical({'master':c['trial_master_seed'],'task':c['task_id'],'stage':role,
  'original_fixed_stage_seed':int(seed),'reader_index':0}).encode()).hexdigest()[:8],16)%2147483647
def financial_bounds(body,config):
 p=FIN/'continuous_core_v3.py';n=next(x for x in ast.parse(p.read_text('utf-8-sig')).body if isinstance(x,ast.FunctionDef) and x.name=='bounds')
 ns={'canonical':canonical,'D':Decimal,'GateRejected':RuntimeError};exec(compile(ast.Module(body=[n],type_ignores=[]),str(p)+'::pure_bounds','exec'),ns)
 return ns['bounds'](body,config)
def checked_contract(path):
 c=read(path);p=read(HERE/'protocol251_SOURCE.json')
 if c['method']!=METHOD or c['task_id'] not in p['task_order'] or c['trial_id'] not in p['trial_ids']:raise RuntimeError('EXP251_FIXED_TASK_TRIAL')
 if c['trial_master_seed']!=p['trial_master_seeds'][p['trial_ids'].index(c['trial_id'])]:raise RuntimeError('EXP251_REPEAT_IDENTITY')
 expected=(HERE/'runs'/METHOD/c['task_id']/c['trial_id']).resolve()
 if Path(c['output_root']).resolve()!=expected:raise RuntimeError('EXP251_INDEPENDENT_NAMESPACE')
 for label in ('public_contract','public_test_scope_contract','current_C0_observation','current_C0_parent_terminal','finance_configuration','method_source_seal'):
  r=c[label]
  if sha(r['path'])!=r['sha256']:raise RuntimeError('EXP251_BOUND_INPUT_DRIFT '+label)
 verify_source_seal(c['method_source_seal']['path'])
 parent=read(c['current_C0_parent_terminal']['path'])
 if parent.get('task_id')!=c['task_id'] or parent.get('error') is not None or parent.get('exit_code')!=0 or parent['stop_receipt'].get('all_owned_descendants_terminated') is not True:raise RuntimeError('EXP251_CURRENT_C0_PARENT_STOP')
 public,common=shared_modules();config=read(c['finance_configuration']['path']);supp,decoded=common.supplement(config,c['task_id'])
 if c['finance_phase']!=PHASE or PHASE not in config['phases']:raise RuntimeError('EXP251_FINANCE_PHASE_NOT_REGISTERED')
 if supp['current_masked_scope_SHA256']!=c['public_test_scope_contract']['sha256'] or supp['fresh_C0_observation_SHA256']!=c['current_C0_observation']['sha256'] or supp['fresh_C0_parent_terminal_SHA256']!=c['current_C0_parent_terminal']['sha256']:raise RuntimeError('EXP251_COMMON_CURRENT_C0_WITNESS')
 return c,expected,config,public,common,supp,decoded

class BoundaryReady(BaseException):pass
class BudgetError(RuntimeError):pass

def verify_parent_completed(completed):
 r=read(completed);p=Path(r['parent_supervision_path'])
 if sha(p)!=r['parent_supervision_SHA256']:raise RuntimeError('EXP251_NATIVE_PARENT_DRIFT')
 v=read(p)
 if v.get('error') is not None or v.get('exit_code')!=0 or v['stop_receipt'].get('all_owned_descendants_terminated') is not True:raise RuntimeError('EXP251_NATIVE_PARENT_UNKNOWN')
 return r

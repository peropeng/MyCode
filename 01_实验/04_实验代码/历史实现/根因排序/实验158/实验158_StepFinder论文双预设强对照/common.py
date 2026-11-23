"""Exp158 isolated writes; all previous valid assets remain read only."""
import datetime,hashlib,json,os,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
E=Path(__file__).resolve().parent;W=E.parents[1]
ROOT=Path('D:/Code/毕设/graduate-thesis-experiments')
E153=ROOT/'工作区/1007-exp153-global-context/实验/实验153_候选条件全轨迹上下文'
E134=ROOT/'工作区/1006-exp134-event-relation/实验/实验134_状态动作表示与关系排序'
E136=ROOT/'工作区/1006-exp136-ab-mechanism/实验/实验136_AB性能与机制确认'
E138=ROOT/'工作区/1006-exp138-aftraj-matched/实验/实验138_AFTraj同数据外折四基线比较'
API=ROOT/'工作区/1005-exp132-paper-three/实验/实验132_论文驱动三案归因对比/engineering_v2/api'
PYTHON=ROOT/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'
ARMS=('SF_ALG_PAPER50','SF_HC_PAPER50')
PRIMARY='LOCKED_153_AB_GLOBAL'
PLAN_SHA='317fec81697a4e75e45e070fb551194e0d24ebb119deca8458405b5d2d5f38f1'
E154=ROOT/'工作区/1007-exp154-mechanism-controls/实验/实验154_固定主模型的机制强对照'
CONTEXT_ARMS=('AB_GLOBAL','AB_LOCAL','AB_STATIC','AB_VALUE_PERM')
E155=ROOT/'工作区/1007-exp155-fixed-replication/实验/实验155_固定方法三种子分组复验'
E156=ROOT/'工作区/1007-exp156-position-diagnostics/实验/实验156_固定模型位置角色强对照'
E157=ROOT/'工作区/1007-exp157-split-stability/实验/实验157_固定模型数据划分敏感性'
SOURCE_SEEDS=(20261006,20261007,20261008);AF_SEEDS=(20260816,20260817,20260818)
SELECTED='SF_INNERVAL_PRESET_SELECT'
PROFILES={
 'SF_ALG_PAPER50':{'parameters':277633,'lr':.001,'alpha':.1,'beta':.9,'gamma':.4,'lambda_temporal':.9,'scales':[1,2],'max_epochs':50,'patience':10},
 'SF_HC_PAPER50':{'parameters':277633,'lr':.00001,'alpha':.3,'beta':.1,'gamma':.75,'lambda_temporal':.02,'scales':[1,2],'max_epochs':50,'patience':10}}
COHORTS=('coding363','coding170','math155','agentic1467')
EXPECTED_BACKEND={'deterministic_algorithms':True,'cudnn_deterministic':True,'cudnn_benchmark':False,'matmul_allow_tf32':False,'cudnn_allow_tf32':False,'num_threads':4}
DEADLINE=datetime.datetime(2026,10,7,2,0,tzinfo=datetime.timezone.utc).timestamp()
NO_LONG_START=datetime.datetime(2026,10,7,1,30,tzinfo=datetime.timezone.utc).timestamp()
NO_NEW_TEST=datetime.datetime(2026,10,7,1,58,tzinfo=datetime.timezone.utc).timestamp()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def check_hashes(items):
 for p,h in items.items():
  if sha(p)!=h:raise RuntimeError('Frozen asset changed: '+p)
def _output(p):
 p=Path(p).resolve()
 if not p.is_relative_to(E.resolve()):raise ValueError('Exp158 writes only')
 p.parent.mkdir(parents=True,exist_ok=True);return p
def write_new(p,x):
 p=_output(p)
 with p.open('x',encoding='utf-8') as f:f.write(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
def atomic(p,x):
 p=_output(p);tmp=p.with_name(p.name+f'.{os.getpid()}.{time.monotonic_ns()}.tmp')
 with tmp.open('x',encoding='utf-8') as f:f.write(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
 for attempt in range(101):
  try:os.replace(tmp,p);return
  except PermissionError:
   if attempt==100:raise
   time.sleep(.02)
def append(p,x):
 p=_output(p)
 with p.open('a',encoding='utf-8') as f:f.write(canonical(x)+'\n');f.flush()
def status(phase,**extra):
 state=read(E/'checkpoint.json');state.update(at_utc=now(),phase=phase,current_pid=None if phase.endswith(('_SEALED','_COMPLETE','_STOP')) else os.getpid(),current_command=' '.join(sys.argv))
 state.update(extra)
 for k in state['counters']:
  if k in extra:state['counters'][k]=extra[k]
 atomic(E/'checkpoint.json',state);atomic(E/'execution_state.json',state)
def remaining():return max(0.,DEADLINE-time.time())
def require_time(new_long_task=False,new_test=False):
 if remaining()<=0:raise TimeoutError('ABSOLUTE_EXPERIMENT_DEADLINE_10_BEIJING')
 if new_long_task and time.time()>=NO_LONG_START:raise TimeoutError('NO_NEW_LONG_EXPERIMENT_AFTER0930')
 if new_test and time.time()>=NO_NEW_TEST:raise TimeoutError('NO_NEW_TEST_AFTER0958')

def prediction_path(scope,arm,seed=None):
 if scope not in (*COHORTS,'AF') or arm not in ARMS:raise ValueError('Frozen158 scope/profile required')
 return E/'results'/scope/(arm+('_ensemble' if seed is None else '_'+str(seed))+'.json')

def fold_prediction_path(arm,seed,outer):return E/'results/AF/folds'/arm/f'{seed}_{outer}.json'

def selection_prediction_path(scope,seed=None):
 if scope not in (*COHORTS,'AF'):raise ValueError('Frozen158 scope required')
 return E/'results/selected'/scope/(SELECTED+('_ensemble' if seed is None else '_'+str(seed))+'.json')

def locked_prediction_path(scope):return E153/'results'/scope/'AB_GLOBAL_ensemble.json'

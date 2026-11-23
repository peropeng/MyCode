"""Exp153 isolated outputs, fixed asset references and absolute deadline."""
import datetime,hashlib,json,os,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
E=Path(__file__).resolve().parent;W=E.parents[1]
ROOT=Path('D:/Code/毕设/graduate-thesis-experiments')
E134=ROOT/'工作区/1006-exp134-event-relation/实验/实验134_状态动作表示与关系排序'
E136=ROOT/'工作区/1006-exp136-ab-mechanism/实验/实验136_AB性能与机制确认'
E137=ROOT/'工作区/1006-exp137-scope-stress/实验/实验137_冻结模型范围压力核验'
E138=ROOT/'工作区/1006-exp138-aftraj-matched/实验/实验138_AFTraj同数据外折四基线比较'
E142=ROOT/'工作区/1006-exp142-agentic-transfer/实验/实验142_冻结模型跨任务域核验/v2'
E143=ROOT/'工作区/1006-exp143-directed-multiscale/实验/实验143_有向多尺度关系核验'
API=ROOT/'工作区/1005-exp132-paper-three/实验/实验132_论文驱动三案归因对比/engineering_v2/api'
PYTHON=ROOT/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'
ARMS=('AB_GLOBAL','AB_LOCAL','AB_STATIC','AB_VALUE_PERM','AB_REF','SF_REF')
CONTEXT_ARMS=ARMS[:4]
SOURCE_SEEDS=(20261006,20261007,20261008);AF_SEEDS=(20260816,20260817,20260818)
COHORTS=('coding363','coding170','math155','agentic1467')
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
 if not p.is_relative_to(E.resolve()):raise ValueError('Exp153 writes only')
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

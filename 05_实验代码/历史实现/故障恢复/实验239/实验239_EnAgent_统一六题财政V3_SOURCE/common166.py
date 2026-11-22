"""Exp224 isolated outputs; original algorithm/data are absolute read-only inputs."""
import datetime,hashlib,importlib.util,json,os,sys,time
from flow_bounds239 import check_open,deadline_for,finite_seconds
from pathlib import Path
sys.dont_write_bytecode=True
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
E=Path(__file__).resolve().parent
W=E.parents[1]
ROOT=E.parents[3]
OLD=ROOT/'工作区/1008-exp183-fixed12-complete-main/实验/实验183_固定十二题完整恢复与排序对照'
READINESS=ROOT/'工作区/1008-2320-baseline-main/baseline2025_common_readiness'
TRANSPORT=E/'flash_io239.py'
PYTHON=ROOT/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'
E150=ROOT/'工作区/1006-exp150-unified-recovery/实验/实验150_统一任务排序与恢复'
E153=ROOT/'工作区/1007-exp153-global-context/实验/实验153_候选条件全轨迹上下文'
METHODS=('AGENTLESS_FSE2025_4L4P4T_FLASH','G_PROGRESSIVE_SEMANTIC_FLASH','BASELINE2026_PENDING_ROOT_ID')
TIME_AUTHORITY=E/'protocol225.json'
_time_protocol=json.loads(TIME_AUTHORITY.read_text('utf-8-sig'))
if _time_protocol['deadline']!={'hard_utc':None,'no_new_utc':None}:raise RuntimeError('OLD_FIXED_GLOBAL_WINDOW_NOT_ALLOWED')
DEADLINE=NO_TEST=None
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def lines(p):return [json.loads(x) for x in Path(p).read_text('utf-8-sig').splitlines() if x.strip()]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,x):
 p=Path(p).resolve();assert p.is_relative_to(E.resolve()),'EXP224_WRITE_SCOPE'
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.'+str(os.getpid())+'.tmp')
 tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n','utf-8');os.replace(tmp,p)
def append(p,x):
 p=Path(p).resolve();assert p.is_relative_to(E.resolve()),'EXP224_WRITE_SCOPE'
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('a',encoding='utf-8') as f:f.write(canonical(x)+'\n');f.flush()
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def closure_paths():return (read(TIME_AUTHORITY)['closure_flag'],E/'STOP_REQUESTED.json')
def request_closed():return any(Path(p).exists() for p in closure_paths())
def require_open():check_open(closure_paths())
def parent_flow_deadline():
 value=os.environ.get('EXP239_FLOW_DEADLINE_MONOTONIC')
 return None if value is None else float(value)
def flow_deadline_for(start,seconds):return deadline_for(start,seconds,parent_flow_deadline())
def remaining():
 if request_closed():return 0.
 boundary=parent_flow_deadline()
 return float('inf') if boundary is None else max(0.,boundary-time.monotonic())
def authorization():
 from control235 import authorization as focused_authorization
 return focused_authorization()

def load_replay():
 run=module('exp224_immutable150',E150/'common150.py').load_replay()
 raw=module('exp224_original_raw_projection',OLD/'raw_source166.py');old=run.export_input
 def export(task):
  prefix=read(Path(task)/'visible/source_prefix.json')
  value=raw.export_input(task) if 'raw_row_index' in prefix else old(task)
  mf=read(Path(task)/'task_manifest.json')
  if 'public_regression_tests' in mf:value.update(public_regression_tests=list(mf['public_regression_tests']),public_regression_initially_passed=True)
  return value
 run.export_input=export
 return run
def status(phase,**fields):save(E/'execution_checkpoint224.json',{'at_utc':now(),'phase':phase,'pid':os.getpid(),**fields})

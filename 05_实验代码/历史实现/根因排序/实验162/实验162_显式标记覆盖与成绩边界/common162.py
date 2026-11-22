"""Only fixed public turn substring masks, then already sealed score caches."""
import csv,datetime,hashlib,json,math,os,sys,time
from collections import Counter,defaultdict
from pathlib import Path
sys.dont_write_bytecode=True
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
E=Path(__file__).resolve().parent;W=E.parents[1];ROOT=Path('D:/Code/毕设/graduate-thesis-experiments')
PYTHON=ROOT/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'
E161=ROOT/'工作区/1007-exp161-task-proximity/实验/实验161_公开任务近似与泛化边界'
E160=ROOT/'工作区/1007-exp160-cached-variation/实验/实验160_固定候选方差与预算诊断'
PLAN_SHA='b445de9c6642b100747db2a1f209cd479ea2cc397f0e1d77f398af0fe945e3d3'
COHORTS=('coding363','coding170','math155','agentic1467');PARTITIONS=('original153','split_A','split_B','split_C')
METHODS=('G','SF_OLD','AB_OLD','ALG50','HC50');MARKERS={'primary':'_attacked_solution.py','secondary':'attacked'};FIELDS=('content','action','thought');GROUPS=('present','absent')
DEADLINE=datetime.datetime(2026,10,7,2,tzinfo=datetime.timezone.utc).timestamp()
PHASE='PUBLIC_MASK';PUBLIC_ALLOWED={E161/'frozen_public_manifest.json'};SCORE_ALLOWED=set();READS={}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def require_time():
 if time.time()>=DEADLINE:raise TimeoutError('ABSOLUTE10BEIJING_STOP')
def allow_public(paths):
 for path in paths:
  p=Path(path).resolve()
  if p.suffix!='.json' or p.name!='public_records.json' or not p.is_relative_to(ROOT/'工作区'):raise ValueError('Only four161referenced public target records')
  PUBLIC_ALLOWED.add(p)
def allowed(path):
 p=Path(path).resolve()
 if p.suffix not in ('.json','.csv','.py'):raise ValueError('No binary/model/tensor reads')
 if p.is_relative_to(E) or p in PUBLIC_ALLOWED:return p
 if PHASE=='SCORED_CACHE' and p in SCORE_ALLOWED:return p
 raise ValueError('Phase-restricted162 read denied:'+str(p))
def sha(path):
 p=allowed(path);h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def read(path):
 p=allowed(path);b=p.read_bytes();h=hashlib.sha256(b).hexdigest();key=str(p);r=READS.setdefault(key,{'sha256':h,'bytes':len(b),'read_calls':0,'phase':PHASE})
 if r['sha256']!=h:raise RuntimeError('Immutable input changed:'+key)
 r['read_calls']+=1;return json.loads(b.decode('utf-8-sig'))
def check_hashes(items):
 for path,h in items.items():
  require_time()
  if sha(path)!=h:raise RuntimeError('Frozen input changed:'+path)
def output(path):
 p=Path(path).resolve()
 if not p.is_relative_to(E):raise ValueError('162 writes only')
 p.parent.mkdir(parents=True,exist_ok=True);return p
def write_new(path,value):
 with output(path).open('x',encoding='utf-8') as f:f.write(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def atomic(path,value):
 p=output(path);tmp=p.with_name(p.name+f'.{os.getpid()}.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n','utf-8');os.replace(tmp,p)
def write_csv(path,rows):
 with output(path).open('x',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def status(phase,**extra):
 p=E/'checkpoint.json';j=json.loads(p.read_text('utf-8-sig'));j.update(at_utc=now(),phase=phase,current_pid=os.getpid(),**extra);atomic(p,j)
def enter_score_phase():
 global PHASE
 seal=read(E/'marker_masks_sealed.json')
 if not seal['all2155_public_marker_masks_fixed_before_Gold_scores']:raise RuntimeError('All2155 public marker masks andcases must precede scoring')
 check_hashes(seal['artifacts']);check_hashes(seal['sources']);PHASE='SCORED_CACHE'
 SCORE_ALLOWED.update(p.resolve() for p in (E160/'cell_manifest.json',E160/'evaluation_cached_Gold.json',E160/'frozen_input_manifest.json',E160/'main_decision_packet.json',E160/'final_execution_audit.json',E160/'parent_reference_metadata.json'))
 return seal
def allow_score_inputs(paths):
 if PHASE!='SCORED_CACHE':raise RuntimeError('No Gold/pred helpers in public mask phase')
 for path in paths:
  p=Path(path).resolve()
  if p.suffix!='.json' or not p.is_relative_to(ROOT/'工作区'):raise ValueError('Only referenced existing ensemble JSON')
  SCORE_ALLOWED.add(p)

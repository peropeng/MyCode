"""Phase-separated pure text/cache analysis; text stage cannot read any score cache."""
import csv,datetime,hashlib,json,math,os,re,sys,time,unicodedata
from collections import Counter,defaultdict
from pathlib import Path
sys.dont_write_bytecode=True
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
E=Path(__file__).resolve().parent;W=E.parents[1];ROOT=Path('D:/Code/毕设/graduate-thesis-experiments')
PYTHON=ROOT/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'
PLAN_SHA='7c86cc73a84bcbec778160f82e5e74684c6c28b86ced6ab176111581b3285c4c'
E153=ROOT/'工作区/1007-exp153-global-context/实验/实验153_候选条件全轨迹上下文'
E156=ROOT/'工作区/1007-exp156-position-diagnostics/实验/实验156_固定模型位置角色强对照'
E157=ROOT/'工作区/1007-exp157-split-stability/实验/实验157_固定模型数据划分敏感性'
E160=ROOT/'工作区/1007-exp160-cached-variation/实验/实验160_固定候选方差与预算诊断'
COHORTS=('coding363','coding170','math155','agentic1467');PARTITIONS=('original153','split_A','split_B','split_C')
METHODS=('G','SF_OLD','AB_OLD','ALG50','HC50')
BINS=('[0,0.2)','[0.2,0.5)','[0.5,0.8)','[0.8,1]','UNKNOWN')
DEADLINE=datetime.datetime(2026,10,7,2,tzinfo=datetime.timezone.utc).timestamp()
PHASE='PUBLIC_TEXT';PUBLIC_ALLOWED={E153/'protocol.json',E156/'protocol.json',E157/'protocol.json'};SCORE_ALLOWED=set();READS={}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def require_time():
 if time.time()>=DEADLINE:raise TimeoutError('ABSOLUTE10BEIJING_STOP')
def allow_public(paths):
 for path in paths:
  p=Path(path).resolve()
  if p.suffix!='.json' or p.name!='public_records.json' or not p.is_relative_to(ROOT/'工作区'):raise ValueError('Exact protocol-referenced public task metadata only')
  PUBLIC_ALLOWED.add(p)
def allowed(path):
 p=Path(path).resolve()
 if p.suffix not in ('.json','.csv','.py'):raise ValueError('No model/tensor/binary reads')
 if p.is_relative_to(E) or p in PUBLIC_ALLOWED:return p
 if PHASE=='SCORED_CACHE' and p in SCORE_ALLOWED:return p
 raise ValueError('Phase-restricted read denied:'+str(p))
def sha(path):
 p=allowed(path);h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def read(path):
 p=allowed(path);b=p.read_bytes();h=hashlib.sha256(b).hexdigest();key=str(p)
 r=READS.setdefault(key,{'sha256':h,'bytes':len(b),'read_calls':0,'phase':PHASE})
 if r['sha256']!=h:raise RuntimeError('Immutable input changed:'+key)
 r['read_calls']+=1;return json.loads(b.decode('utf-8-sig'))
def check_hashes(values):
 for path,h in values.items():
  require_time()
  if sha(path)!=h:raise RuntimeError('Frozen phase input changed:'+path)
def output(path):
 p=Path(path).resolve()
 if not p.is_relative_to(E):raise ValueError('Exp161 only writes own artifacts')
 p.parent.mkdir(parents=True,exist_ok=True);return p
def write_new(path,value):
 p=output(path)
 with p.open('x',encoding='utf-8') as f:f.write(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def atomic(path,value):
 p=output(path);tmp=p.with_name(p.name+f'.{os.getpid()}.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n','utf-8');os.replace(tmp,p)
def write_csv(path,rows):
 with output(path).open('x',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def status(phase,**extra):
 p=E/'checkpoint.json';j=json.loads(p.read_text('utf-8-sig'));j.update(at_utc=now(),phase=phase,current_pid=os.getpid(),**extra);atomic(p,j)
def enter_score_phase():
 global PHASE
 seal=read(E/'text_proximity_sealed.json')
 if not seal['complete_all2155_targets_614_sources_and_fixed_cases_before_scores']:raise RuntimeError('All public-text nearest neighbors/bins/case choices must precede cache scoring')
 check_hashes(seal['artifacts']);PHASE='SCORED_CACHE'
 # Parent160 is authorized only after the public-text result/case seal is verified.
 SCORE_ALLOWED.update(p.resolve() for p in (E160/'cell_manifest.json',E160/'evaluation_cached_Gold.json',E160/'frozen_input_manifest.json',E160/'main_decision_packet.json',E160/'final_execution_audit.json',E160/'parent_reference_metadata.json'))
 return seal
def allow_score_inputs(paths):
 if PHASE!='SCORED_CACHE':raise RuntimeError('No prediction/Gold cache helper in text phase')
 for path in paths:
  p=Path(path).resolve()
  if p.suffix!='.json' or not p.is_relative_to(ROOT/'工作区'):raise ValueError('Only explicitly referenced sealed prediction JSON')
  SCORE_ALLOWED.add(p)
def lexical(task):
 if not isinstance(task,str):return {'status':'UNKNOWN','tokens':(),'shingles':set(),'normalized_full':None,'raw_chars':None}
 norm=unicodedata.normalize('NFKC',task).casefold();tokens=tuple(re.findall(r'\w+',norm,flags=re.UNICODE))
 if not tokens:return {'status':'UNKNOWN','tokens':tokens,'shingles':set(),'normalized_full':' '.join(norm.split()),'raw_chars':len(task)}
 shingles={tokens[i:i+5] for i in range(len(tokens)-4)} if len(tokens)>=5 else {tokens}
 return {'status':'SHORT' if len(tokens)<5 else 'NORMAL','tokens':tokens,'shingles':shingles,'normalized_full':' '.join(norm.split()),'raw_chars':len(task)}
def similarity_bin(intersection,union):
 if intersection is None or not union:return 'UNKNOWN'
 if intersection*5<union:return BINS[0]
 if intersection*2<union:return BINS[1]
 if intersection*5<union*4:return BINS[2]
 return BINS[3]

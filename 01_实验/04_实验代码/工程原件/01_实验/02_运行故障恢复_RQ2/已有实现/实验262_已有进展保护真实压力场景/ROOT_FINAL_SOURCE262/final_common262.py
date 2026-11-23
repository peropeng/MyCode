"""ROOT-only final namespace: no work on import, separate output and source."""
import ast,copy,datetime,hashlib,importlib.util,json,os,sys,time,types
from pathlib import Path
sys.dont_write_bytecode=True
SOURCE=Path(__file__).resolve().parent;H=SOURCE.parent;E=H
R=ROOT=Path('D:/Code/毕设/graduate-thesis-experiments');OLD=R/'工作区/1011-our19';COMMON=R/'工作区/1010-unified-six'
CONTROLLER=Path('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')
IDENTITY_SOURCE=SOURCE/'physical_identity249.py'
FINAL_WORKER_SOURCE=SOURCE/'final262_ROOT_ONLY.py'
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def owned(p):
 p=Path(p).resolve()
 if not p.is_relative_to(H.resolve()):raise RuntimeError('EXP262_FINAL_ROOT_WRITE_SCOPE')
 return p
def save(p,v):
 p=owned(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.'+str(os.getpid())+'.tmp')
 with tmp.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def intent(p,v):
 p=owned(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(canonical(v)+'\n');f.flush();os.fsync(f.fileno())
def ref(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def checked(r):
 if sha(r['path'])!=r['sha256']:raise RuntimeError('EXP262_FINAL_BOUND_ASSET_DRIFT:'+r['path'])
 return read(r['path'])
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

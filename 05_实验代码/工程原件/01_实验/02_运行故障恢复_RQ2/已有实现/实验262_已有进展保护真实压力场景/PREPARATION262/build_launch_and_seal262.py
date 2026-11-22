"""Static preparation wrapper construction; does not create owner or T0."""
import ast,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;H=P.parent;R=Path('D:/Code/毕设/graduate-thesis-experiments')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
base=R/'工作区/1012-exp260-paired-recovery-postreview/实验/实验260_排序与当前反馈共同恢复/resource_v2/SOURCE/launch260.py'
t=base.read_text('utf-8-sig').replace('EXP260','EXP262').replace('Exp260','Exp262').replace('environment260.py','environment262.py').replace('ROOT_RESUME260.json','ROOT_RESUME262.json').replace('ROOT_RESUMED260.json','ROOT_RESUMED262.json').replace('PARENT_TERMINAL260.json','PARENT_TERMINAL262.json').replace("c['control']","c['policy']")
start=t.index('from common260 import *');end=t.index('\n\nclass LaunchGuard:',start)
imports='''from stage_entry262 import authority, read, sha, ref, PYTHON as CONTROLLER, SITE as CONTROLLER_SITE, H
import copy,datetime,hashlib,importlib.util,json,os,sys,time
from pathlib import Path
SOURCE=H/'SOURCE';E=H;ROOT=Path('D:/Code/毕设/graduate-thesis-experiments')
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def owned(p):
 p=Path(p).resolve()
 if not p.is_relative_to(H):raise RuntimeError('EXP262_HELD_OWNER_WRITE_SCOPE')
 return p
def save(p,v):
 p=owned(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.'+str(os.getpid())+'.tmp')
 with tmp.open('x',encoding='utf-8',newline='\\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def jobs_module(guard):
 bridge=types.ModuleType('common166');bridge.__dict__.update(Path=Path,json=json,os=os,sys=sys,time=time,ROOT=ROOT,E=H,save=save,read=read,sha=sha,now=now,canonical=canonical,authorization=guard.check)
 sys.modules['common166']=bridge;p=SOURCE/'native_executor242_prospective.py';spec=importlib.util.spec_from_file_location('_exp262_actual_held_jobs',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
'''
t=t[:start]+imports+t[end:]
start=t.index('class LaunchGuard:');end=t.index('\n\ndef main():',start)
t=t[:start]+'''class LaunchGuard:
    def __init__(self,contract,grant,grant_path):self.contract=contract;self.grant=grant;self.grant_path=grant_path;self.grant_sha=sha(grant_path)
    def check(self,*args,**kwargs):
        if sha(self.grant_path)!=self.grant_sha or any(Path(p).exists() for p in self.grant['root_stop_paths']):raise RuntimeError('EXP262_PREPARATION_GRANT_CHANGED_OR_ROOT_STOP')
        if time.time()>=datetime.datetime.fromisoformat('2026-10-12T23:29:05+08:00').timestamp():raise RuntimeError('EXP262_WINDOW_STOP')
        seal=read(self.contract['method_source_seal']['path'])
        if sha(self.contract['method_source_seal']['path'])!=self.contract['method_source_seal']['sha256']:raise RuntimeError('EXP262_HELD_SOURCE_SEAL_DRIFT')
        for p,h in seal['sources'].items():
            if sha(p)!=h:raise RuntimeError('EXP262_HELD_RUNTIME_SOURCE_DRIFT')
        return True
'''+t[end:]
start=t.index('    p=argparse.ArgumentParser()');end=t.index("    out=owned(c['output_root'])",start)
t=t[:start]+'''    p=argparse.ArgumentParser();p.add_argument('--root-preparation-grant',required=True);p.add_argument('--trial',required=True);p.add_argument('--condition',required=True);p.add_argument('--policy',required=True);p.add_argument('--finance-grant',required=True);p.add_argument('--whole-grant',required=True);p.add_argument('--suspend-timeout',type=int,default=600);p.add_argument('--owner-directory',default='Root_owner600')
    args=p.parse_args();g,c,slot=authority(args.root_preparation_grant,args.trial,args.condition);args.contract=slot['contract']['path']
    if args.owner_directory!='Root_owner600' or args.suspend_timeout!=600:raise RuntimeError('EXP262_EXACT_FIRST_OWNER_READY600_REQUIRED')
'''+t[end:]
t=t.replace('guard=LaunchGuard(c);h=helper();jobs=h.load_jobs(guard);k=jobs.api()','guard=LaunchGuard(c,g,args.root_preparation_grant);jobs=jobs_module(guard);k=jobs.api()')
ast.parse(t);(P/'launch262.py').write_text(t,'utf-8')
sources={str(p.resolve()):sha(p) for p in [P/'stage_entry262.py',P/'launch262.py']}
controller=Path('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')
seal={'schema':'EXP262-closed-preparation-and-physical-paused-primary-seal/1','SOURCE_ONLY':True,'sources':sources,'dependencies':{str(controller):sha(controller)},'public_inputs_SHA256':{str(H/'SOURCE_SEAL262_CALLER_FINAL_FALSE.json'):sha(H/'SOURCE_SEAL262_CALLER_FINAL_FALSE.json')},'no_actual_PREPARATION_body_T0_owner_POST_native':True}
sealpath=P/'SOURCE_SEAL262_PREPARATION_FALSE.json';save(sealpath,seal)
save(P/'ROOT_PREPARATION_GRANT262_TEMPLATE_FALSE.json',{'schema':'EXP262-Root-real-preparation-only/1','preparation_authorized':False,'model_authorized':False,'native_authorized':False,'finance_authorized':False,'private_authorized':False,'task_id':'getmoto__moto-7081','trial_id':'trial1','allowed_order':['SET','COUNT','O_ONLY'],'preparation_source_seal':ref(sealpath),'caller_source_seal':ref(H/'SOURCE_SEAL262_CALLER_FINAL_FALSE.json'),'independent_sampling_plan':None,'finance_amendment':None,'amendment_registered_receipt':None,'group_policy':None,'fresh_predeclared_trial':True,'old_flow_resume_authorized':False,'lease_end_UTC':'2026-10-12T23:29:05+08:00','root_stop_paths':[],'window_T0':'2026-10-12T19:29:05+08:00','window_deadline':'2026-10-12T23:29:05+08:00','never_grants_POST_or_native_by_itself':True,'physical_primary_paused_lease_seconds':600})
print(json.dumps({'SOURCE_ONLY':True,'preparation_seal':ref(sealpath),'preparation_grant_template':ref(P/'ROOT_PREPARATION_GRANT262_TEMPLATE_FALSE.json'),'physical_owner_T0_POST_native':0}))

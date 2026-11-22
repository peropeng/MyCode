"""Generated-test scope v2: no experiment-directory read root, full open audit."""
import json,os,sys,threading
from pathlib import Path

def inside(path,root):
 try:path.relative_to(root);return True
 except ValueError:return False

class Policy:
 def __init__(self,envelope,entry_file,site_paths=None):
  self.source=Path(envelope['source_root']).resolve();self.frozen=Path(envelope['frozen_root']).resolve()
  self.out=Path(envelope['output']).resolve();self.entry=Path(entry_file).resolve();self.experiment=self.entry.parent
  self.log=self.out/'generated_scope_events.jsonl'
  self.trusted_files={self.experiment/name for name in ('product_entry241.py','generated_scope_v2_241.py',
   'winjob241.py','contracts241.py','supervision_classification241.py')}
  self.trusted_files.update(Path(envelope['harness']).resolve()/name for name in ('sitecustomize.py','qualify.py','qualification_plugin.py'))
  self.library_roots={Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve()}
  for item in sys.path if site_paths is None else site_paths:
   if item and 'site-packages' in Path(item).parts:
    p=Path(item).resolve()
    if not inside(p,self.experiment):self.library_roots.add(p)
  for item in envelope.get('dependency_paths',[]):
   p=Path(item).resolve()
   if inside(p,self.experiment):raise PermissionError('SCOPE_V2_EXPERIMENT_NOT_PRODUCT_DEPENDENCY')
   self.library_roots.add(p)
 def path(self,value):return Path(os.fsdecode(value)).resolve()
 def read_decision(self,path):
  if inside(path,self.frozen):return False,'FROZEN_TEST_READ'
  if inside(path,self.out):return True,'CURRENT_NATIVE_OUTPUT'
  if path in self.trusted_files:return True,'EXACT_TRUSTED_PY_FILE'
  if inside(path,self.source):
   if set(path.relative_to(self.source).parts)&{'test','tests','test-data','.git'}:return False,'SOURCE_TEST_OR_VCS_READ'
   return True,'CURRENT_BUSINESS_SOURCE'
  if inside(path,self.experiment):return False,'EXPERIMENT_ARTIFACT_READ'
  if any(inside(path,p) for p in self.library_roots):return True,'ACTUAL_PRODUCT_LIBRARY'
  return False,'OUTSIDE_DECLARED_PRODUCT_SCOPE'
 def write_decision(self,path):
  if path==self.log:return False,'TRUSTED_SCOPE_LOG_IMMUTABLE_TO_GENERATED_CODE'
  if inside(path,self.out):return True,'CURRENT_NATIVE_OUTPUT'
  return False,'WRITE_OUTSIDE_CURRENT_NATIVE_OUTPUT'
 def mutation_decision(self,event,path):
  if event in ('os.link','os.symlink'):return False,'LINK_OPERATION_FORBIDDEN'
  return self.write_decision(path)

def install(envelope,entry_file):
 policy=Policy(envelope,entry_file);guard=threading.local();guard.logging=False
 policy.out.mkdir(parents=True,exist_ok=True)
 def record(event):
  guard.logging=True
  try:
   with policy.log.open('a',encoding='utf-8') as f:f.write(json.dumps(event,ensure_ascii=False,sort_keys=True)+'\n')
  finally:guard.logging=False
 record({'event':'SCOPE_V2_INSTALL','scope_version':2,'records_python_open_audit_events_from_install':True,
  'native_C_layer_or_arbitrary_malicious_code_coverage_not_claimed':True,
  'no_experiment_directory_root':True,'trusted_files':sorted(map(str,policy.trusted_files)),
  'library_roots':sorted(map(str,policy.library_roots)),'current_native_output':str(policy.out)})
 def audit(event,values):
  if getattr(guard,'logging',False):return
  if event=='open':
   value=values[0];flags=values[2] or 0;mode=values[1] or ''
   write=any(c in str(mode) for c in ('w','a','x','+')) or bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
   if not isinstance(value,(str,bytes,os.PathLike)):
    record({'event':'open','path_or_descriptor':str(value),'write':write,'allowed':False,'reason':'UNRESOLVED_DESCRIPTOR'})
    raise PermissionError('SCOPE_V2_UNRESOLVED_OPEN_DESCRIPTOR')
   if os.fsdecode(value).casefold()==os.devnull.casefold():
    record({'event':'open','path':os.devnull,'write':write,'allowed':True,'reason':'OS_NULL_DEVICE'});return
   path=policy.path(value);allowed,reason=policy.write_decision(path) if write else policy.read_decision(path)
   record({'event':'open','path':str(path),'write':write,'flags':flags,'mode':str(mode),'allowed':allowed,'reason':reason})
   if not allowed:raise PermissionError('SCOPE_V2_'+reason)
  elif event in ('os.listdir','os.scandir','os.chdir'):
   path=policy.path(values[0] if values and values[0] is not None else os.getcwd())
   allowed,reason=policy.read_decision(path)
   record({'event':event,'path':str(path),'allowed':allowed,'reason':reason})
   if not allowed:raise PermissionError('SCOPE_V2_'+reason)
  elif event in ('os.link','os.symlink'):
   paths=[str(policy.path(value)) for value in values[:2] if isinstance(value,(str,bytes,os.PathLike))]
   record({'event':event,'paths':paths,'allowed':False,'reason':'LINK_OPERATION_FORBIDDEN'})
   raise PermissionError('SCOPE_V2_LINK_OPERATION_FORBIDDEN')
  elif event in ('os.remove','os.rmdir','os.mkdir','os.rename','os.chmod','os.truncate','os.utime','os.chown','os.lchown'):
   if values and not isinstance(values[0],(str,bytes,os.PathLike)):
    record({'event':event,'path_or_descriptor':str(values[0]),'allowed':False,'reason':'UNRESOLVED_MUTATION_DESCRIPTOR'})
    raise PermissionError('SCOPE_V2_UNRESOLVED_MUTATION_DESCRIPTOR')
   for value in (values[:2] if event=='os.rename' else values[:1]):
    if isinstance(value,(str,bytes,os.PathLike)):
     path=policy.path(value);allowed,reason=policy.mutation_decision(event,path)
     record({'event':event,'path':str(path),'allowed':allowed,'reason':reason})
     if not allowed:raise PermissionError('SCOPE_V2_'+reason)
  elif event in ('subprocess.Popen','os.system','socket.connect','socket.bind'):
   record({'event':event,'allowed':False,'reason':'PROCESS_OR_NETWORK_BOUNDARY'})
   raise PermissionError('SCOPE_V2_PROCESS_OR_NETWORK_BOUNDARY')
 sys.addaudithook(audit)
 return policy

"""Generated native Python audit scope; no hook installation on module import."""
import json,os,sys,threading,atexit
from pathlib import Path

def inside(path,root):
 try:path.relative_to(root);return True
 except ValueError:return False

class Policy:
 def __init__(self,envelope,library_paths=None):
  self.source=Path(envelope['source_root']).resolve();self.frozen=Path(envelope['frozen_root']).resolve()
  self.out=Path(envelope['output']).resolve();self.experiment=Path(envelope['experiment_root']).resolve()
  self.log=self.out/'generated_scope_events.jsonl'
  self.trusted_files=frozenset(Path(p).resolve() for p in envelope['trusted_files'])
  libs={Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve()}
  for item in sys.path if library_paths is None else library_paths:
   if item and 'site-packages' in Path(item).parts:libs.add(Path(item).resolve())
  if any(inside(p,self.experiment) or inside(p,self.frozen) for p in libs):
   raise PermissionError('SCOPE_V3_ARTIFACT_NOT_PRODUCT_DEPENDENCY')
  self.library_roots=frozenset(libs)
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

MUTATIONS={'os.remove','os.rmdir','os.mkdir','os.rename','os.chmod','os.truncate','os.utime','os.chown','os.lchown'}
DIR_FD_POSITIONS={'os.remove':(1,),'os.rmdir':(1,),'os.mkdir':(2,),'os.rename':(2,3),'os.chmod':(2,),'os.utime':(3,),'os.chown':(3,),'os.lchown':(3,)}

def decisions(policy,event,values):
 """Pure decision records for covered events; no file contents are opened here."""
 if event=='open':
  value=values[0];flags=values[2] or 0;mode=values[1] or ''
  write=any(c in str(mode) for c in ('w','a','x','+')) or bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
  if not isinstance(value,(str,bytes,os.PathLike)):
   return [{'event':event,'path_or_descriptor':str(value),'write':write,'allowed':False,'reason':'UNRESOLVED_DESCRIPTOR'}]
  if os.fsdecode(value).casefold()==os.devnull.casefold():
   return [{'event':event,'path':os.devnull,'write':write,'allowed':True,'reason':'OS_NULL_DEVICE'}]
  path=policy.path(value);allowed,reason=policy.write_decision(path) if write else policy.read_decision(path)
  return [{'event':event,'path':str(path),'write':write,'flags':flags,'mode':str(mode),'allowed':allowed,'reason':reason}]
 if event in ('os.listdir','os.scandir','os.chdir'):
  value=values[0] if values and values[0] is not None else os.getcwd()
  if not isinstance(value,(str,bytes,os.PathLike)):
   return [{'event':event,'path_or_descriptor':str(value),'allowed':False,'reason':'UNRESOLVED_DESCRIPTOR'}]
  path=policy.path(value);allowed,reason=policy.read_decision(path)
  return [{'event':event,'path':str(path),'allowed':allowed,'reason':reason}]
 if event in ('os.link','os.symlink'):
  return [{'event':event,'paths':[str(policy.path(v)) for v in values[:2] if isinstance(v,(str,bytes,os.PathLike))],'allowed':False,'reason':'LINK_OPERATION_FORBIDDEN'}]
 if event in MUTATIONS:
  if any(pos<len(values) and values[pos] not in (None,-1) for pos in DIR_FD_POSITIONS.get(event,())):
   return [{'event':event,'allowed':False,'reason':'UNRESOLVED_DIRECTORY_DESCRIPTOR'}]
  paths=values[:2] if event=='os.rename' else values[:1]
  records=[]
  for value in paths:
   if not isinstance(value,(str,bytes,os.PathLike)):
    records.append({'event':event,'path_or_descriptor':str(value),'allowed':False,'reason':'UNRESOLVED_MUTATION_DESCRIPTOR'})
   else:
    path=policy.path(value);allowed,reason=policy.mutation_decision(event,path)
    records.append({'event':event,'path':str(path),'allowed':allowed,'reason':reason})
  return records
 if event in ('subprocess.Popen','os.system','socket.connect','socket.bind'):
  return [{'event':event,'allowed':False,'reason':'PROCESS_OR_NETWORK_BOUNDARY'}]
 return []

def install(envelope):
 policy=Policy(envelope);guard=threading.local();guard.logging=False
 policy.out.mkdir(parents=True,exist_ok=True)
 # Hold one observer-owned handle before installing the hook. Generated opens,
 # renames, truncates, chmods and removals of this log are denied by the policy.
 stream=policy.log.open('a',encoding='utf-8')
 def record(row):
  guard.logging=True
  try:stream.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n');stream.flush()
  finally:guard.logging=False
 record({'event':'SCOPE_V3_INSTALL','records_covered_python_events_from_install':True,'scope_version':3,
  'native_C_layer_or_arbitrary_malicious_code_coverage_not_claimed':True,'whole_experiment_root_not_allowed':True,
  'current_native_output':str(policy.out),'current_business_source':str(policy.source),'frozen_denied_root':str(policy.frozen),
  'trusted_files':sorted(map(str,policy.trusted_files)),'library_roots':sorted(map(str,policy.library_roots))})
 def audit(event,values):
  if getattr(guard,'logging',False):return
  rows=decisions(policy,event,values)
  for row in rows:record(row)
  if any(not row['allowed'] for row in rows):raise PermissionError('SCOPE_V3_'+next(row['reason'] for row in rows if not row['allowed']))
 sys.addaudithook(audit)
 def finish():
  record({'event':'SCOPE_V3_CLOSE','observer_log_close':True});stream.close()
 atexit.register(finish)
 # The active policy and logger remain closure-local, not an actor-visible module
 # global. This is covered Python auditing, not a general malicious-code sandbox.

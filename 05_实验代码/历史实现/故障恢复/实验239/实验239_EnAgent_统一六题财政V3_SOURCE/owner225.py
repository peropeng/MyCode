"""Owned public clone and real suspended/Job Git Bash deployment callbacks."""
from common166 import *
import copy,ctypes,re,shlex,subprocess,threading
from ctypes import wintypes as w
from bridge225 import Bridge175,IllegalTool,EngineeringError
import winjob225 as jobs

CERT='.public_projection_certificate'
class Bridge(Bridge175):
 def __init__(self,env):
  self.env=env;self.owned=Path(env.out).resolve();self.initial=env.business_files()
  self.original_paths=set(self.initial)|{CERT};self.protected={CERT}
  self.certificate=canonical({'business_inventory':{p:hashlib.sha256(t.encode()).hexdigest() for p,t in sorted(self.initial.items())},'projection':'common_public_business_source_only','private_or_test_source':False}).encode()
  self.receipts=[];self.engineering_error=None;self.directory_views_filtered=True;self._immutable=self._asset_state();self._number=0
 def export(self):
  root=self.env.export_business_tree('common_public_C0')
  (root/CERT).write_bytes(self.certificate)
  return root
 def _clone_business(self,root):
  root=self._root(root);result={}
  if not (root/CERT).is_file() or (root/CERT).read_bytes()!=self.certificate:self._fatal('PUBLIC_PROJECTION_CERTIFICATE_DRIFT')
  for p in root.rglob('*'):
   if p.is_symlink():raise IllegalTool('SYMLINK_IN_ACTOR_CLONE')
   if not p.is_file():continue
   rel=p.relative_to(root).as_posix()
   if rel==CERT or '.git' in p.relative_to(root).parts or '__pycache__' in p.parts or '.pytest_cache' in p.parts or self._generated(rel):continue
   if not self._business(rel):raise IllegalTool('UNDECLARED_NONBUSINESS_ADDITION '+rel)
   result[rel]=p.read_text('utf-8')
  if not set(self.initial)<=set(result):raise IllegalTool('DELETING_ORIGINAL_BUSINESS_FILES_NOT_SUPPORTED')
  return result
 def path_map(self,root,value):
  return value.replace('/workspace/repo',Path(root).as_posix())
 def neutral(self,root,value):
  if not isinstance(value,str):return value
  posix=Path(root).as_posix();bash_posix='/'+posix[0].lower()+posix[2:] if len(posix)>2 and posix[1]==':' else posix
  value=value.replace(str(root),'/workspace/repo').replace(posix,'/workspace/repo').replace(bash_posix,'/workspace/repo')
  # Git Bash quotes non-ASCII bytes in failed paths using ANSI-C fragments. The
  # known ASCII tail still uniquely identifies only this owned actor root.
  tail=Path(root).relative_to(E).as_posix()
  value=re.sub(r'(?:[A-Za-z]:|/[a-z])/[^\n\"]*?/'+re.escape(tail),'/workspace/repo',value)
  from common_environment224 import neutral
  return neutral(value,self.env)
 def native_command(self,root,command):
  text=command.strip()
  # A source-generated simple cd prefix has the same CWD as the guarded root.
  match=re.match(r'^cd\s+(.+?)\s*&&\s*(.*)$',text,re.S)
  if match:
   target=shlex.split(match.group(1));assert len(target)==1
   self._path(root,target[0]);text=match.group(2).strip()
  try:tokens=shlex.split(text,posix=True)
  except ValueError:return None
  if tokens and tokens[0] in {'python','python3','python.exe','pytest','pytest_owned_generated'}:
   answer=super().command_runner(root,text)
   return {k:self.neutral(root,v) for k,v in answer.items()}
  return None
 def command_guard(self,root,command):
  self._check_assets();self.env._require();root=self._root(root)
  if any(c in command for c in ('`','$','\x00','\r','\n')):raise IllegalTool('SHELL_SUBSTITUTION_OR_MULTILINE_NOT_ALLOWED')
  lexer=shlex.shlex(command,posix=True,punctuation_chars=';&|<>');lexer.whitespace_split=True
  tokens=list(lexer);segments=[];current=[]
  for token in tokens:
   if token in ('&&','|',';'):
    if not current:raise IllegalTool('EMPTY_SHELL_SEGMENT')
    segments.append(current);current=[]
   elif token in ('&','||','>','>>','<','<<','2>','>&'):raise IllegalTool('SHELL_REDIRECTION_OR_BACKGROUND_NOT_ALLOWED')
   else:current.append(token)
  if current:segments.append(current)
  allowed={'pwd','cd','ls','cat','head','tail','grep','rg','find','sed','wc','sort','uniq','git','printf','echo','test'}
  for part in segments:
   if not part or part[0] not in allowed:raise IllegalTool('UNDECLARED_SHELL_PROGRAM '+str(part[:1]))
   op=part[0]
   if op=='git' and (len(part)<2 or part[1] not in {'diff','status','ls-files','show'}):raise IllegalTool('GIT_WRITE_OR_EXTERNAL_HISTORY_NOT_ALLOWED')
   if op=='git' and part[1]=='show' and any(x not in ('HEAD','--stat','--name-only','--oneline') for x in part[2:]):raise IllegalTool('ONLY_PUBLIC_C0_HEAD_ALLOWED')
   if op=='find' and any(x in part for x in ('-exec','-execdir','-delete','-ok','-okdir','-fprint','-fprintf','-fls')):raise IllegalTool('FIND_PROCESS_OR_WRITE_NOT_ALLOWED')
   if op=='sed' and any(x=='-i' or x.startswith('--in-place') or re.search(r'(^|;)\s*[we]\s',x) for x in part[1:]):raise IllegalTool('SED_WRITE_OR_PROCESS_NOT_ALLOWED')
   if op=='rg' and any(x.split('=',1)[0] in {'--pre','--pre-glob','--files-from'} for x in part):raise IllegalTool('RG_EXTERNAL_PROCESS_NOT_ALLOWED')
   if op=='cd':
    if len(part)!=2:raise IllegalTool('CD_REQUIRES_EXACT_PUBLIC_DIRECTORY')
    self._path(root,part[1])
   for value in part[1:]:
    if re.search(r'(^|[/\\])\.\.([/\\]|$)',value) or '\\' in value:raise IllegalTool('SHELL_PATH_TRAVERSAL')
    if re.match(r'^[A-Za-z]:[/\\]',value) or value.startswith('/'):
     self._path(root,value)
  self._record('real_git_bash_command_guard',{'root':str(root),'command':command,'allowed':True,'business_only_clone':True})
  return True

class OwnedProcess:
 def __init__(self,process,kernel,job,name,owner):
  self.process=process;self.k=kernel;self.job=job;self.name=name;self.owner=owner;self.closed=False
  self.pid=process.pid;self.stdin=process.stdin;self.stdout=process.stdout;self.stderr=process.stderr
 def poll(self):return self.process.poll()
 def kill(self):
  if not self.closed:self.k.TerminateJobObject(self.job,225)
 def wait(self,timeout=None):
  code=self.process.wait(timeout)
  if not self.closed:
   active=jobs.pids(self.k,self.job)
   if active:self.k.TerminateJobObject(self.job,225)
   deadline=time.monotonic()+3
   while jobs.pids(self.k,self.job) and time.monotonic()<deadline:time.sleep(.02)
   remaining_pids=jobs.pids(self.k,self.job)
   if remaining_pids:raise EngineeringError('OWN_GIT_BASH_JOB_NOT_EMPTY')
   self.k.CloseHandle(self.job);self.closed=True
   self.owner.env.record('actual_git_bash_owned_stop',{'PID':self.pid,'specific_named_Job':self.name,'exit_code':code,'own_Job_empty_before_close':True,'descendants_stopped':bool(active),'short_lived_unobserved_children':'UNKNOWN'})
  return code

class ShellOwner:
 def __init__(self,bridge):self.bridge=bridge;self.env=bridge.env;self.processes=[]
 def launch(self,root,argv,untrusted_env):
  self.env._require();protocol=authorization();maximum=protocol['budget'].get('max_git_bash_roots_per_flow',8)
  if len(self.processes)>=maximum:raise EngineeringError('DECLARED_GIT_BASH_ROOT_CAP')
  allowed={'SystemRoot','SYSTEMROOT','WINDIR','COMSPEC','PATHEXT','PATH','TEMP','TMP','NUMBER_OF_PROCESSORS','PROCESSOR_ARCHITECTURE','MSYSTEM'}
  child_env={k:v for k,v in untrusted_env.items() if k in allowed}
  child_env['HOME']=str(root);child_env['USERPROFILE']=str(root);child_env['PYTHONDONTWRITEBYTECODE']='1';child_env['PYTHONNOUSERSITE']='1'
  child_env['PYTHONPATH']='';child_env['GIT_CONFIG_NOSYSTEM']='1';child_env['GIT_CONFIG_GLOBAL']=os.devnull
  child_env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='core.longpaths',GIT_CONFIG_VALUE_0='true')
  name='Exp225_'+str(os.getpid())+'_'+str(len(self.processes));k=jobs.kernel();j=k.CreateJobObjectW(None,name)
  if not j:raise EngineeringError('CREATE_OWN_GIT_BASH_JOB_FAILED')
  limits=jobs.Extended();limits.BasicLimitInformation.LimitFlags=0x2000
  if not k.SetInformationJobObject(j,9,ctypes.byref(limits),ctypes.sizeof(limits)):raise EngineeringError('SET_OWN_JOB_FAILED')
  p=None
  try:
   p=subprocess.Popen(argv,cwd=root,env=child_env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',errors='replace',bufsize=1,creationflags=0x00000004|0x08000000)
   h=w.HANDLE(int(p._handle))
   if not k.AssignProcessToJobObject(j,h):raise EngineeringError('ASSIGN_SUSPENDED_SHELL_FAILED')
   birth=jobs.birth(k,h,j,p.pid);expected=Path(argv[0]).resolve()
   if Path(birth['OS_image_QueryFullProcessImageName']).resolve()!=expected:raise EngineeringError('GIT_BASH_PHYSICAL_IMAGE_MISMATCH')
   self.env.record('actual_git_bash_birth_before_resume',{'birth':birth,'specific_named_Job':name,'argv':argv,'suspended_assigned_before_resume':True,'environment_keys':sorted(child_env),'credential_values_exposed':False})
   nt=ctypes.WinDLL('ntdll');nt.NtResumeProcess.argtypes=[w.HANDLE];nt.NtResumeProcess.restype=ctypes.c_long
   if nt.NtResumeProcess(h)!=0:raise EngineeringError('RESUME_SHELL_FAILED')
   owned=OwnedProcess(p,k,j,name,self);self.processes.append(owned);return owned
  except BaseException:
   k.TerminateJobObject(j,225)
   if p is not None:p.wait(3)
   k.CloseHandle(j);raise
 def close(self):
  for p in self.processes:
   if not p.closed:p.kill();p.wait(3)

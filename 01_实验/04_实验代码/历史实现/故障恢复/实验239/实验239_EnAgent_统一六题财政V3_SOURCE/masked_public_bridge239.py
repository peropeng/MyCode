"""Current-business + immutable Root public test/support projection for EnAgent."""
from common166 import *
import re,shlex
from bridge225 import IllegalTool,EngineeringError
import native_masked_public239 as public

def masked_bridge(base):
 class MaskedPublicBridge(base):
  def __init__(self,env):
   super().__init__(env)
   p=authorization();self.masked_scope=public.load_scope(p,env.task_id)
   permission=p['public_goal_ordinary_oracle_contract']
   if sha(permission)!=p['public_goal_ordinary_oracle_contract_sha256']:raise EngineeringError('ORIGINAL_PUBLIC_ORACLE_PERMISSION_DRIFT')
   oracle=next(x for x in read(permission)['tasks'] if x['task_id']==env.task_id)
   if set(oracle['target_nodes'])!=set(env.recovery_goal_nodes) or set(oracle['ordinary_nodes'])!=set(env.public_regression_nodes) or Path(oracle['trusted_native_oracle_root']).resolve()!=Path(env._paths['frozen']).resolve():raise EngineeringError('ORIGINAL_PUBLIC_GOAL_ORDINARY_SELECTOR_DRIFT')
   if not oracle['same_four_methods'] or oracle['private_hidden_feedback_to_model'] or oracle['new_Gold_read']:raise EngineeringError('PUBLIC_ORACLE_BOUNDARY_NOT_COMMON')
   self.masked_supports=public.support_inventory(self.masked_scope,self.initial)
   self.original_paths.update(self.masked_supports);self.protected.update(self.masked_supports)
   self._masked_pool=None
   expected=read(p['shared_pack_references'][env.task_id]['path'])['c0_business_paths_sha256']
   actual={r:sha(env.repo_root/r) for r in self.initial}
   if actual!=expected:raise EngineeringError('MASKED_PROJECTION_CURRENT_C0_SOURCE_SHA_DRIFT')
   self.initial_raw_SHA256=actual
   self.certificate=canonical({'business_inventory':actual,'projection':'current-business-and-immutable-masked-public-test-support','masked_public_scope_SHA256':self.masked_scope['scope_contract_SHA256'],'immutable_support_manifest_SHA256':digest(self.masked_supports),'original_test_or_private_git_blobs_included':False}).encode()
  def export(self):
   root=super().export()
   # Historical text exporter normalizes line endings. Restore the exact C0
   # bytes before author git snapshots; the approved public view never replaces
   # business files with its unedited origin version.
   for rel in self.initial:(root/rel).write_bytes((self.env.repo_root/rel).read_bytes())
   public.materialize_support(root,self.masked_scope,self.initial_raw_SHA256)
   (root/'.public_projection_certificate').write_bytes(self.certificate)
   self._record('masked_public_support_materialized',{'scope_SHA256':self.masked_scope['scope_contract_SHA256'],'immutable_support_files':len(self.masked_supports),'test_py_files':len(self.masked_scope['public_test_py_files_SHA256']),'all_C0_bytes_exact':True,'original_unmasked_or_private_git_copied':False})
   return root
  def _clone_business(self,root):
   root=self._root(root);public.verify_actor(root,self.initial,self.masked_supports);result={}
   if not (root/'.public_projection_certificate').is_file() or (root/'.public_projection_certificate').read_bytes()!=self.certificate:self._fatal('PUBLIC_PROJECTION_CERTIFICATE_DRIFT')
   for path in root.rglob('*'):
    if path.is_symlink():raise IllegalTool('SYMLINK_IN_ACTOR_CLONE')
    if not path.is_file():continue
    rel=path.relative_to(root).as_posix()
    if rel in self.masked_supports or rel=='.public_projection_certificate' or '.git' in path.relative_to(root).parts or '__pycache__' in path.parts or '.pytest_cache' in path.parts or self._generated(rel):continue
    if not self._business(rel):raise IllegalTool('UNDECLARED_NONBUSINESS_ADDITION '+rel)
    result[rel]=path.read_text('utf-8')
   if not set(self.initial)<=set(result):raise IllegalTool('DELETING_ORIGINAL_BUSINESS_FILES_NOT_SUPPORTED')
   return result
  def visible_paths(self,root,directory):
   root=self._root(root);_,directory,_=self._path(root,directory)
   values=set(super().visible_paths(root,directory))
   for rel in self.masked_supports:
    path=root/rel
    if path.is_relative_to(directory):
     values.add(str(path));values.update(str(p) for p in path.parents if p.is_relative_to(directory))
   return sorted(v for v in values if len(Path(v).relative_to(directory).parts)<=2)
  def edit_guard(self,root,path,command):
   root,p,rel=self._path(root,path);public.verify_actor(root,self.initial,self.masked_supports)
   if rel in self.masked_supports:
    if command!='view':raise IllegalTool('MASKED_PUBLIC_TESTS_AND_SUPPORT_ARE_IMMUTABLE')
    self._check_assets();self._record('masked_public_view_read',{'path':rel,'scope_SHA256':self.masked_scope['scope_contract_SHA256'],'file_SHA256':self.masked_supports[rel]});return True
   return super().edit_guard(root,path,command)
  def command_guard(self,root,command):
   public.verify_actor(self._root(root),self.initial,self.masked_supports)
   if re.search(r'(^|[\s/\\])\.git([/\\\s]|$)',command):raise IllegalTool('DIRECT_GIT_BLOB_READ_UNAVAILABLE')
   lexer=shlex.shlex(command,posix=True,punctuation_chars=';&|<>');lexer.whitespace_split=True
   parts=list(lexer)
   # Reader flags must not smuggle external paths or a file-writing operation.
   # Author git commands used internally remain unchanged; only actor Bash is
   # constrained to this freshly initialized, masked C0 repository.
   banned={'--output','-o','--ext-diff','--textconv','--no-index','--git-dir','--work-tree','--pathspec-from-file','--ignore-file','--exclude-from','--include-from','--pre','--files-from'}
   if any(x.split('=',1)[0] in banned for x in parts):raise IllegalTool('READER_FILE_WRITE_OR_EXTERNAL_INPUT_OPTION')
   for value in parts:
    if '=' in value:
     option,embedded=value.split('=',1)
     if embedded.startswith('/') or re.match(r'^[A-Za-z]:[/\\]',embedded):self._path(root,embedded)
   for i,value in enumerate(parts):
    if value=='sed':
     tail=[]
     for v in parts[i+1:]:
      if v in {'|','&&',';'}:break
      if not v.startswith('-'):tail.append(v)
     if not tail or not re.fullmatch(r'(?:\d+|\$)(?:,(?:\d+|\$))?\s*[pdq]',tail[0]):raise IllegalTool('SED_REQUIRES_READONLY_NUMERIC_LINE_SELECTION')
    if value=='uniq':
     # uniq may write its second filename. Keep its stdout form only.
     tail=[]
     for v in parts[i+1:]:
      if v in {'|','&&',';'}:break
      if not v.startswith('-'):tail.append(v)
     if len(tail)>1:raise IllegalTool('UNIQ_OUTPUT_FILE_UNAVAILABLE')
   return super().command_guard(root,command)
  def _public_owner_check(self):
   from winjob225 import self_identity
   name=os.environ.get('EXP225_V2_PARENT_JOB')
   if not name:raise EngineeringError('MASKED_NATIVE_REQUIRES_OWNED_PARENT_JOB')
   return self_identity(name)
  def masked_native(self,root,targets=None,collect_only=False,label='masked_public'):
   self._clone_business(root)
   return public.execute(self.env,root,self.masked_scope,targets,collect_only=collect_only,label=label,protocol=authorization(),owner_check=self._public_owner_check)
  def initial_regression_pool(self,root,ordinary_ids):
   # Author tester receives the actual repository C0 PASS pool plus the same
   # explicit ordinary obligations. No file is assigned a PASS by inventory.
   record=self.masked_native(root,None,label='initial_full_repository_PASS_pool')
   if record['known'] is not True:raise EngineeringError('INITIAL_MASKED_REPOSITORY_PASS_POOL_UNKNOWN '+record['status'])
   self._masked_pool={n:record['pytest']['outcomes'][n]['status'] for n in record['pytest']['collected']}
   ordinary=super().public_runner(root,ordinary_ids)
   combined=dict(ordinary)
   for node,status in self._masked_pool.items():combined[node]='PASS' if status=='passed' else 'FAIL'
   # Skip/error/fail nodes are not fed to tester as initially passing tests.
   return combined
  def public_runner(self,root,ids):
   if not ids:return {}
   ordinary=[n for n in ids if n in self.env.public_regression_nodes]
   extra=[n for n in ids if n not in ordinary]
   answer=super().public_runner(root,ordinary) if ordinary else {}
   if extra:
    record=self.masked_native(root,extra,label='author_retained_public_repository_regression')
    if record['known'] is not True:raise EngineeringError('MASKED_PUBLIC_REGRESSION_NATIVE_UNKNOWN')
    outcomes=record['pytest']['outcomes']
    if set(outcomes)!=set(extra):raise EngineeringError('MASKED_PUBLIC_REQUESTED_LEAF_COVERAGE_UNKNOWN')
    answer.update({n:'PASS' if outcomes[n]['status']=='passed' else 'FAIL' for n in extra})
   return answer
  def command_runner(self,root,command):
   from tool_compat_v3 import split_native_tokens,split_native_invocation
   if split_native_invocation(command) is not None:
    tokens=split_native_tokens(command);op,args=tokens[0],tokens[1:]
    if op in {'python','python3','python.exe'} and args[:2]==['-m','pytest']:op,args='pytest',args[2:]
    if op=='pytest':
     args=[self._normalize_native_arg(root,x) for x in args if x not in {'-q','-v','-vv','-s'}]
     if args and all(x.split('::',1)[0] in self.masked_scope['public_test_py_files_SHA256'] for x in args):
      record=self.masked_native(root,args,label='actor_masked_repository_test_request')
      execution=record['execution'];log=Path(execution['log']).read_text('utf-8',errors='replace')
      if not record['known']:self._fatal('MASKED_PUBLIC_ACTOR_NATIVE_UNKNOWN '+record['status'])
      return {'returncode':int(execution['exit_code']),'stdout':self.neutral(root,log),'stderr':''}
   return super().command_runner(root,command)
  def native_command(self,root,command):
   mapped=self._mapped_invocation(root,command)
   if mapped is None:return None
   answer=self.command_runner(root,shlex.join(mapped));return {k:self.neutral(root,v) for k,v in answer.items()}
 return MaskedPublicBridge

"""Owned path adapters only; generated code executes through existing guarded native API."""
import re,shlex
from pathlib import Path
from alias_projection import PublishedAliasProjection
from entry235 import Bridge235
from bridge225 import IllegalTool
from tool_compat_v3 import split_native_invocation

class ScopedBridgeV3(PublishedAliasProjection,Bridge235):
 def _generated(self,rel):
  parts=Path(rel).parts
  if not parts or rel in self.original_paths or 'repo/'+rel in self.original_paths:return False
  if '.git' in parts or any(p in {'tests','test','test-data'} for p in parts):return False
  explicit=any(p in self.GENERATED_DIRS for p in parts)
  root_script=(len(parts)==1 and bool(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_-]*\.py',parts[0]))
               and parts[0] not in {'sitecustomize.py','usercustomize.py','conftest.py','setup.py'})
  return explicit or root_script

 def _generated_argument(self,root,arg):
  try:_,_,rel=self._path(root,arg);return self._generated(rel)
  except IllegalTool:return False

 def _normalize_native_arg(self,root,arg):
  arg=self._project_alias_path(root,arg)
  prefix=self._root(root).as_posix()+'/'
  return arg[len(prefix):] if arg.startswith(prefix) else arg

 def _mapped_invocation(self,root,command):
  invocation=split_native_invocation(command)
  if invocation is None:return None
  cd,program=invocation
  if cd is not None:
   _,directory,_=self._path(root,cd)
   if directory!=self._root(root):raise IllegalTool('NATIVE_CD_MUST_BE_CURRENT_REPOSITORY')
  op,args=program[0],program[1:]
  if op in {'python','python3','python.exe'} and len(args)==2 and args[0]=='-c':
   mapped=[op,'-c',args[1]]  # Python code is data; no path replacement inside it.
  else:
   mapped=[op,*[super(ScopedBridgeV3,self).path_map(root,a) for a in args]]
  return mapped

 def path_map(self,root,value):
  if not isinstance(value,str):return super().path_map(root,value)
  invocation=self._mapped_invocation(root,value)
  if invocation is not None:return shlex.join(invocation)
  return super().path_map(root,value)

 def native_command(self,root,command):
  mapped=self._mapped_invocation(root,command)
  if mapped is None:return None
  answer=super().command_runner(root,shlex.join(mapped))
  return {k:self.neutral(root,v) for k,v in answer.items()}

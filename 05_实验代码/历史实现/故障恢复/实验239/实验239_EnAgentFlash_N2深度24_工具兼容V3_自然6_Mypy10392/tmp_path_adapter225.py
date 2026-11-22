"""Map declared POSIX /tmp into each actor's existing generated-test boundary."""
from pathlib import Path
import re
from bridge_v2_225 import Bridge as OriginalBridge
from bridge225 import IllegalTool

class Bridge(OriginalBridge):
 def tmp_directory(self,root):
  root=self._root(root);target=root/'generated_tests'/'_posix_tmp'
  if target.is_symlink() or (root/'generated_tests').is_symlink():raise IllegalTool('TMP_SYMLINK_NOT_ALLOWED')
  target.mkdir(parents=True,exist_ok=True)
  return target
 def mapped_tmp(self,root,value):
  rel=value[5:] if value.startswith('/tmp/') else ''
  if any(x in ('..','.git') or x.startswith('.') for x in rel.split('/') if x):raise IllegalTool('TMP_TRAVERSAL_OR_PROTECTED_PATH')
  directory=self.tmp_directory(root);target=directory/rel
  if not target.resolve().is_relative_to(directory.resolve()) or target.is_symlink():raise IllegalTool('TMP_OUTSIDE_ISOLATED_GENERATED_ROOT')
  target.parent.mkdir(parents=True,exist_ok=True)
  return target.as_posix()
 def path_map(self,root,value):
  if value=='/tmp' or value.startswith('/tmp/'):return self.mapped_tmp(root,value)
  # Same transform precedes original editor validation and original bash parser.
  value=re.sub(r'(?<![A-Za-z0-9_./\\])/tmp(?:/[A-Za-z0-9_./-]+)?',lambda m:self.mapped_tmp(root,m.group()),value)
  return super().path_map(root,value)
 def neutral(self,root,value):
  if isinstance(value,str):
   target=(Path(root)/'generated_tests'/'_posix_tmp')
   posix=target.as_posix();bash='/'+posix[0].lower()+posix[2:] if len(posix)>2 and posix[1]==':' else posix
   for physical in (str(target),posix,bash):value=value.replace(physical,'/tmp')
  return super().neutral(root,value)

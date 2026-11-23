"""Exact owned runtime traceback prefix mapping; no broad redaction or actions."""
import os
from pathlib import Path
from tmp_path_adapter225 import Bridge as OriginalBridge

def neutral_relative_traceback(value,repo_root,frozen_root):
 if not isinstance(value,str):return value
 relative=os.path.relpath(Path(repo_root).resolve(),Path(frozen_root).resolve())
 if not relative.startswith('..'+os.sep):
  raise RuntimeError('EXPECTED_OWN_RUNTIME_RELATIVE_TO_FROZEN_ROOT')
 for prefix in dict.fromkeys((relative,relative.replace('\\','/'))):
  value=value.replace(prefix,'/workspace/repo')
 return value

class Bridge(OriginalBridge):
 def neutral(self,root,value):
  value=super().neutral(root,value)
  repo_root=Path(self.env.repo_root).resolve()
  if not repo_root.is_relative_to(Path(self.env.active).resolve()):
   raise RuntimeError('TRACEBACK_REPO_OUTSIDE_OWN_NATIVE_RUNTIME')
  return neutral_relative_traceback(value,repo_root,self.env._paths['frozen'])

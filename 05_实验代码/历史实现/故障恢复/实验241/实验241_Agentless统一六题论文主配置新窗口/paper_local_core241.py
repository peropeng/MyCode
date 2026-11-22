"""Original CST skeleton/global locations; existing safe diff wrapper retained."""
from pathlib import Path
import importlib.util
from agentless_bridge.local_core166 import structure,context,normalized_patch
from agentless_bridge import official_core166 as official
ORIGINAL_SOURCE=Path('D:\\Code\\毕设\\graduate-thesis-experiments\\工作区\\1003-diagnosis-investigation\\exp132_review\\final_window_1745\\agentless_primary\\official_source')
def load(name,rel):
 spec=importlib.util.spec_from_file_location(name,ORIGINAL_SOURCE/rel);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
_cst=load('paper_original_cst_skeleton241','agentless/util/compress_file.py')
_globals=load('paper_original_cst_globalvar241','agentless/util/parse_global_var.py')
official.parse_global_var_from_code=_globals.parse_global_var_from_code
skeleton=_cst.get_skeleton

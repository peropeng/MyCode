"""Scoped absolute original-source loading, with independent output namespace."""
from common166 import *
import types
SOURCES={}
def original(name, filename, replacements=()):
 path=OLD/filename;raw=path.read_text('utf-8-sig');SOURCES[str(path)]=sha(path)
 for a,b in replacements:
  assert a in raw,('ORIGINAL_TRANSPORT_ANCHOR_MISSING',filename,a);raw=raw.replace(a,b)
 m=types.ModuleType(name);m.__file__=str(path);m.__package__='';sys.modules[name]=m
 exec(compile(raw,str(path),'exec'),m.__dict__)
 return m
def load():
 if 'environment166' in sys.modules:return sys.modules['environment166'],sys.modules.get('flash_environment178')
 original('schema165','schema165.py')
 original('raw_source166','raw_source166.py')
 # Core dependency path is read-only; all runtime E/save functions come from224.
 bridge=types.ModuleType('agentless_bridge');bridge.__path__=[str(OLD/'agentless_bridge')];bridge.__package__='agentless_bridge';sys.modules['agentless_bridge']=bridge
 env=original('environment166','environment166.py',[("guard=E/'repro_guard'",'guard=Path('+repr(str(OLD/'repro_guard'))+')'),('self.native_calls>=32','self.native_calls>=63'),('self.native_calls<32','self.native_calls<63')])
 original('native_lane178','native_lane178.py')
 original('public_projection181','public_projection181.py')
 # Local module supplies the common semantic query and immutable vector references.
 import retrieval178
 flash=original('flash_environment178','flash_environment178.py')
 original('ranked_repair178','ranked_repair178.py')
 original('agentless178','agentless178.py')
 return env,flash
def bind_namespace(output_root):
 """Call once in a separate worker process, before constructing any Environment."""
 root=Path(output_root).resolve();assert root.is_relative_to(ROOT/'工作区')
 import common166
 common166.E=root;common166.W=root.parents[1]
 common166.TIME_AUTHORITY=root/('protocol225.json' if root.name.startswith('实验225_') else 'protocol224.json')
 for name in ('environment166','flash_environment178','retrieval178','common_environment224'):
  if name in sys.modules:sys.modules[name].E=root
 return root

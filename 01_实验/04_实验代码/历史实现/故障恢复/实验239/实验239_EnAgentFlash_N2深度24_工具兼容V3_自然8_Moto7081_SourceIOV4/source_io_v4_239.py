"""Static literal read chains; unchanged legacy AST and actual runtime scope apply."""
import ast,json,hashlib,importlib.util
from pathlib import Path,PurePosixPath
from tool_compat_v3 import check_python_source as original_check,IllegalTool

def _bindings_open(tree):
 for n in ast.walk(tree):
  if isinstance(n,ast.Name) and n.id=='open' and isinstance(n.ctx,(ast.Store,ast.Del)):return True
  if isinstance(n,ast.arg) and n.arg=='open':return True
  if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and n.name=='open':return True
  if isinstance(n,ast.ExceptHandler) and n.name=='open':return True
  if isinstance(n,(ast.Import,ast.ImportFrom)) and any((a.asname or (a.name.split('.')[0] if isinstance(n,ast.Import) else a.name))=='open' for a in n.names):return True
  if hasattr(ast,'MatchAs') and isinstance(n,(ast.MatchAs,ast.MatchStar)) and n.name=='open':return True
  if hasattr(ast,'MatchMapping') and isinstance(n,ast.MatchMapping) and n.rest=='open':return True
 return False

BUSINESS_METADATA=frozenset({'__file__','VERSION','__version__','__name__'})
SYS_METADATA=frozenset({'version','version_info','executable'})
OBSERVATION_PREFIX='_EA239_SOURCEIO_V4_'
OBSERVATION_FILE='source_io_v4_readonly_observations.jsonl'
OBSERVATION_CODE='''import builtins as _EA239_SOURCEIO_V4_builtins
import os as _EA239_SOURCEIO_V4_os
import json as _EA239_SOURCEIO_V4_json
import hashlib as _EA239_SOURCEIO_V4_hashlib
def _EA239_SOURCEIO_V4_observe(kind, target, value, read_mode=None, effective_encoding=None):
    row = {'kind': kind, 'target': target, 'value_type': _EA239_SOURCEIO_V4_builtins.type(value).__name__}
    if kind == 'literal_read':
        row.update(read_mode=read_mode, effective_encoding=effective_encoding)
    if _EA239_SOURCEIO_V4_builtins.isinstance(value, (_EA239_SOURCEIO_V4_builtins.str, _EA239_SOURCEIO_V4_builtins.bytes)):
        data = value.encode('utf-8') if _EA239_SOURCEIO_V4_builtins.isinstance(value, _EA239_SOURCEIO_V4_builtins.str) else value
        row.update(value_bytes=_EA239_SOURCEIO_V4_builtins.len(data), value_sha256=_EA239_SOURCEIO_V4_hashlib.sha256(data).hexdigest())
    if kind != 'literal_read':
        row['actual_value_repr'] = _EA239_SOURCEIO_V4_builtins.repr(value)
    path = _EA239_SOURCEIO_V4_os.path.join(_EA239_SOURCEIO_V4_os.environ['EXP166_REPRO_OUTPUT'], 'source_io_v4_readonly_observations.jsonl')
    with _EA239_SOURCEIO_V4_builtins.open(path, 'a', encoding='utf-8') as stream:
        stream.write(_EA239_SOURCEIO_V4_json.dumps(row, ensure_ascii=False, sort_keys=True) + '\\n')
    return value
def _EA239_SOURCEIO_V4_read(target, mode, encoding_given, encoding):
    if encoding_given:
        stream = _EA239_SOURCEIO_V4_builtins.open(target, mode, encoding=encoding)
    else:
        stream = _EA239_SOURCEIO_V4_builtins.open(target, mode)
    try:
        value = stream.read()
        effective_encoding = _EA239_SOURCEIO_V4_builtins.getattr(stream, 'encoding', None)
    finally:
        stream.close()
    return _EA239_SOURCEIO_V4_observe('literal_read', target, value, mode, effective_encoding)
'''

def _module_bindings(tree,business_sources):
 origins={}
 for relative in business_sources:
  path=PurePosixPath(relative)
  if path.suffix!='.py' or path.is_absolute() or '..' in path.parts:continue
  parts=path.parts[:-1] if path.name=='__init__.py' else (*path.parts[:-1],path.stem)
  origins.setdefault('.'.join(parts),[]).append(relative)
 known={name for name,paths in origins.items() if len(paths)==1};bindings={};sys_names=set()
 for n in ast.walk(tree):
  if isinstance(n,ast.Import):
   for a in n.names:
    bound=a.asname or a.name.split('.')[0]
    actual=a.name if a.asname else a.name.split('.')[0]
    if a.name=='sys':sys_names.add(bound);bindings.setdefault(bound,[]).append('sys')
    elif actual in known:bindings.setdefault(bound,[]).append(actual)
  elif isinstance(n,ast.ImportFrom):
   if (n.module or '').split('.')[0]=='sys':raise IllegalTool('SOURCE_IO_V4_SYS_DIRECT_PUBLIC_METADATA_ONLY')
   if n.level==0:
    for a in n.names:
     actual=(n.module or '')+'.'+a.name
     if actual in known:bindings.setdefault(a.asname or a.name,[]).append(actual)
 return bindings,sys_names

def _unshadowed(tree,names,bindings):
 imported={name:0 for name in names}
 for n in ast.walk(tree):
  if isinstance(n,(ast.Import,ast.ImportFrom)):
   for a in n.names:
    bound=a.asname or (a.name.split('.')[0] if isinstance(n,ast.Import) else a.name)
    if bound in imported:imported[bound]+=1
 if any(len(bindings.get(name,[]))!=1 or imported[name]!=1 for name in names):raise IllegalTool('SOURCE_IO_V4_METADATA_BINDING_AMBIGUOUS')
 for n in ast.walk(tree):
  if isinstance(n,ast.Name) and n.id in names and isinstance(n.ctx,(ast.Store,ast.Del)):raise IllegalTool('SOURCE_IO_V4_METADATA_BINDING_REASSIGNED')
  if isinstance(n,ast.arg) and n.arg in names:raise IllegalTool('SOURCE_IO_V4_METADATA_BINDING_REASSIGNED')
  if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and n.name in names:raise IllegalTool('SOURCE_IO_V4_METADATA_BINDING_REASSIGNED')
  if isinstance(n,ast.ExceptHandler) and n.name in names:raise IllegalTool('SOURCE_IO_V4_METADATA_BINDING_REASSIGNED')
  if hasattr(ast,'MatchAs') and isinstance(n,(ast.MatchAs,ast.MatchStar)) and n.name in names:raise IllegalTool('SOURCE_IO_V4_METADATA_BINDING_REASSIGNED')
  if hasattr(ast,'MatchMapping') and isinstance(n,ast.MatchMapping) and n.rest in names:raise IllegalTool('SOURCE_IO_V4_METADATA_BINDING_REASSIGNED')

def _read_path(value,business_sources,aliases,actor_root,native_source_root):
 relative=None
 for alias in ('repo',*aliases):
  prefix='/workspace/'+alias+'/'
  if value.startswith(prefix):
   tail=value[len(prefix):]
   if '\\' in tail or ':' in tail or any(p in {'.','..'} for p in tail.split('/')):raise IllegalTool('SOURCE_IO_V4_PUBLISHED_ALIAS_TRAVERSAL')
   relative=tail;break
 if relative is None:
  path=Path(value)
  if path.is_absolute():
   try:relative=path.resolve().relative_to(Path(actor_root).resolve()).as_posix()
   except ValueError:pass
  else:
   posix=PurePosixPath(value)
   if not posix.is_absolute() and '..' not in posix.parts:relative=posix.as_posix()
 if relative in business_sources:
  return (Path(native_source_root)/relative).as_posix()
 # Unknown literal paths are deliberately not widened into the business root.
 # Their original meaning is retained for the actual native Scope guard.
 return value

def check_source_io(code,*,business_sources,aliases,actor_root,native_source_root):
 if len(code.encode('utf-8'))>32768:raise IllegalTool('GENERATED_SCRIPT_BYTE_BOUND')
 tree=ast.parse(code);parents={id(c):p for p in ast.walk(tree) for c in ast.iter_child_nodes(p)}
 for n in ast.walk(tree):
  name=n.id if isinstance(n,ast.Name) else n.arg if isinstance(n,ast.arg) else n.name if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef,ast.ExceptHandler)) else (n.asname or n.name.split('.')[0]) if isinstance(n,ast.alias) else ''
  name=name or ''
  if name.startswith(OBSERVATION_PREFIX):raise IllegalTool('SOURCE_IO_V4_OBSERVER_BINDING_RESERVED')
  if hasattr(ast,'MatchAs') and isinstance(n,(ast.MatchAs,ast.MatchStar)) and (n.name or '').startswith(OBSERVATION_PREFIX):raise IllegalTool('SOURCE_IO_V4_OBSERVER_BINDING_RESERVED')
  if hasattr(ast,'MatchMapping') and isinstance(n,ast.MatchMapping) and (n.rest or '').startswith(OBSERVATION_PREFIX):raise IllegalTool('SOURCE_IO_V4_OBSERVER_BINDING_RESERVED')
 bindings,sys_names=_module_bindings(tree,business_sources)
 metadata={};metadata_names=set(sys_names)
 for n in ast.walk(tree):
  if isinstance(n,ast.Attribute) and isinstance(n.value,ast.Name):
   name=n.value.id
   if name in sys_names:
    if n.attr not in SYS_METADATA or not isinstance(n.ctx,ast.Load):raise IllegalTool('SOURCE_IO_V4_SYS_METADATA_WHITELIST_REQUIRED')
    metadata[id(n)]=True
   elif name in bindings and n.attr in BUSINESS_METADATA:
    if not isinstance(n.ctx,ast.Load):raise IllegalTool('SOURCE_IO_V4_BUSINESS_METADATA_READONLY')
    metadata[id(n)]=True;metadata_names.add(name)
  if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Load) and n.id in sys_names:
   parent=parents.get(id(n))
   if not (isinstance(parent,ast.Attribute) and parent.value is n and parent.attr in SYS_METADATA):raise IllegalTool('SOURCE_IO_V4_BARE_SYS_OR_NONMETADATA_USAGE')
 _unshadowed(tree,metadata_names,bindings)
 calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='open']
 if not calls and not metadata and not sys_names:return original_check(code,business_sources=business_sources)
 if calls and _bindings_open(tree):raise IllegalTool('SOURCE_IO_V4_BUILTIN_OPEN_REBOUND')
 replacements={};checked=[]
 for n in calls:
  if not 1<=len(n.args)<=2 or any(isinstance(a,ast.Starred) for a in n.args):raise IllegalTool('SOURCE_IO_V4_STATIC_LITERAL_READ_REQUIRED')
  if not isinstance(n.args[0],ast.Constant) or not isinstance(n.args[0].value,str) or not n.args[0].value or '\x00' in n.args[0].value:raise IllegalTool('SOURCE_IO_V4_STATIC_LITERAL_PATH_REQUIRED')
  kw={}
  for k in n.keywords:
   if k.arg not in {'mode','encoding'} or k.arg in kw or not isinstance(k.value,ast.Constant) or not isinstance(k.value.value,str):raise IllegalTool('SOURCE_IO_V4_CONSTANT_MODE_ENCODING_ONLY')
   kw[k.arg]=k.value.value
  if len(n.args)==2:
   if 'mode' in kw or not isinstance(n.args[1],ast.Constant) or not isinstance(n.args[1].value,str):raise IllegalTool('SOURCE_IO_V4_CONSTANT_MODE_REQUIRED')
   mode=n.args[1].value
  else:mode=kw.get('mode','r')
  if mode not in {'r','rt','rb'}:raise IllegalTool('SOURCE_IO_V4_READONLY_MODE_REQUIRED')
  attribute=parents.get(id(n));read=parents.get(id(attribute))
  if not (isinstance(attribute,ast.Attribute) and attribute.value is n and attribute.attr=='read' and isinstance(read,ast.Call) and read.func is attribute and not read.args and not read.keywords):raise IllegalTool('SOURCE_IO_V4_DIRECT_READ_CHAIN_REQUIRED')
  replacements[id(read)]=True;checked.append((n,n.args[0].value))
 class Sanitized(ast.NodeTransformer):
  def visit_Call(self,n):
   if id(n) in replacements:return ast.copy_location(ast.Constant('SOURCE_IO_V4_STATIC_READ_CONTENT'),n)
   return self.generic_visit(n)
  def visit_Attribute(self,n):
   if id(n) in metadata:return ast.copy_location(ast.Constant('SOURCE_IO_V4_READONLY_PUBLIC_METADATA'),n)
   return self.generic_visit(n)
  def visit_Import(self,n):
   n.names=[a for a in n.names if a.name!='sys']
   return n if n.names else ast.copy_location(ast.Pass(),n)
 # The existing guard checks every remaining import/name/attribute/call. Only
 # fully validated read chains and readonly metadata are neutral for that check.
 sanitized=Sanitized().visit(tree);ast.fix_missing_locations(sanitized)
 original_check(ast.unparse(sanitized),business_sources=business_sources)
 # Parse again: the validation tree was sanitized, while actual code retains
 # genuine builtin open/read and changes only a declared business path literal.
 execution=ast.parse(code)
 # The witness returns the actual value unchanged and writes only a native-
 # output receipt. It prints nothing and cannot grant a semantic test marker.
 class Witness(ast.NodeTransformer):
  def wrap(self,node,kind,target):
   return ast.copy_location(ast.Call(ast.Name(OBSERVATION_PREFIX+'observe',ast.Load()),[ast.Constant(kind),ast.Constant(target),node],[]),node)
  def visit_Attribute(self,n):
   if isinstance(n.value,ast.Name):
    name=n.value.id
    if name in sys_names and n.attr in SYS_METADATA:return self.wrap(n,'sys_metadata',n.attr)
    if name in bindings and n.attr in BUSINESS_METADATA:return self.wrap(n,'module_metadata',bindings[name][0]+'.'+n.attr)
   return self.generic_visit(n)
  def visit_Call(self,n):
   if isinstance(n.func,ast.Attribute) and n.func.attr=='read' and isinstance(n.func.value,ast.Call) and isinstance(n.func.value.func,ast.Name) and n.func.value.func.id=='open':
    original=n.func.value.args[0].value
    mapped=_read_path(original,business_sources,aliases,actor_root,native_source_root)
    call=n.func.value;keywords={k.arg:k.value.value for k in call.keywords}
    mode=call.args[1].value if len(call.args)==2 else keywords.get('mode','r')
    return ast.copy_location(ast.Call(ast.Name(OBSERVATION_PREFIX+'read',ast.Load()),[ast.Constant(mapped),ast.Constant(mode),ast.Constant('encoding' in keywords),ast.Constant(keywords.get('encoding'))],[]),n)
   return self.generic_visit(n)
 execution=Witness().visit(execution);ast.fix_missing_locations(execution)
 prefix=ast.parse(OBSERVATION_CODE).body
 offset=1 if execution.body and isinstance(execution.body[0],ast.Expr) and isinstance(execution.body[0].value,ast.Constant) and isinstance(execution.body[0].value.value,str) else 0
 while offset<len(execution.body) and isinstance(execution.body[offset],ast.ImportFrom) and execution.body[offset].module=='__future__':offset+=1
 execution.body[offset:offset]=prefix
 return ast.unparse(execution)+'\n'

def source_io_bridge(base):
 class SourceIOV4(base):
  def _check_python(self,code,root):
   checked=check_source_io(code,business_sources=self._clone_business(root),aliases=self.public_aliases(),actor_root=self._root(root),native_source_root=self.env.repo_root)
   tree=ast.parse(code)
   surface=any((isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='open') or (isinstance(n,ast.Import) and any(a.name=='sys' for a in n.names)) or (isinstance(n,ast.Attribute) and n.attr=='__file__') for n in ast.walk(tree))
   if surface:
    if not hasattr(self,'_source_io_checked_scripts'):self._source_io_checked_scripts={}
    self._source_io_checked_scripts[hashlib.sha256(checked.encode('utf-8')).hexdigest()]=checked
   return checked
  def _guarded_readonly_helper_observation(self,record):
   if record.get('generated_script_sha256') not in getattr(self,'_source_io_checked_scripts',{}):return None
   if not all(record.get(k) is True for k in ('executed','guard_loaded','business_state_unchanged','frozen_tests_unchanged')) or record.get('timeout') is not False:return None
   if type(record.get('exit_code')) is not int or record.get('stop_receipt',{}).get('all_owned_descendants_terminated') is not True:return None
   output=Path(record.get('cwd','')).resolve();script=output/'generated_test.py';scopepath=output/'generated_scope_events.jsonl'
   if not output.is_relative_to(Path(self.env.out).resolve()) or not script.is_file() or not scopepath.is_file():return None
   if hashlib.sha256(script.read_bytes()).hexdigest()!=record['generated_script_sha256']:return None
   if record.get('argv')!=[str(self.env._paths['python']),'-B',str(script)]:return None
   rows=[json.loads(s) for s in scopepath.read_text('utf-8-sig').splitlines() if s.strip()]
   if len(rows)<2 or rows[0].get('event')!='SCOPE_V3_INSTALL' or rows[-1].get('event')!='SCOPE_V3_CLOSE':return None
   first=rows[0]
   if Path(first['current_business_source']).resolve()!=Path(self.env.repo_root).resolve() or Path(first['current_native_output']).resolve()!=output or Path(first['frozen_denied_root']).resolve()!=Path(self.env._paths['frozen']).resolve():return None
   if first.get('whole_experiment_root_not_allowed') is not True or first.get('records_covered_python_events_from_install') is not True:return None
   guarded=Path(__file__).parent/'repro_guard225/scope_guard_v3.py'
   spec=importlib.util.spec_from_file_location('ea239_sourceio_v4_scope_replay',guarded);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
   policy=module.Policy.__new__(module.Policy)
   policy.source=Path(first['current_business_source']).resolve();policy.out=output;policy.frozen=Path(first['frozen_denied_root']).resolve();policy.experiment=Path(__file__).parent.resolve();policy.log=scopepath
   policy.trusted_files=frozenset(Path(p).resolve() for p in first['trusted_files']);policy.library_roots=frozenset(Path(p).resolve() for p in first['library_roots'])
   for row in rows[1:-1]:
    event=row.get('event')
    if event in ('open','os.listdir','os.scandir','os.chdir'):
     if 'path' not in row:
      expected=(False,'UNRESOLVED_DESCRIPTOR')
     elif row['path'].casefold()=='nul':expected=(True,'OS_NULL_DEVICE')
     elif event=='open' and row.get('write'):expected=policy.write_decision(Path(row['path']).resolve())
     else:expected=policy.read_decision(Path(row['path']).resolve())
    elif event in ('os.link','os.symlink'):expected=(False,'LINK_OPERATION_FORBIDDEN')
    elif event in module.MUTATIONS:
     expected=policy.write_decision(Path(row['path']).resolve()) if 'path' in row else (False,row.get('reason'))
     if 'path' not in row and row.get('reason') not in {'UNRESOLVED_DIRECTORY_DESCRIPTOR','UNRESOLVED_MUTATION_DESCRIPTOR'}:return None
    elif event in ('subprocess.Popen','os.system','socket.connect','socket.bind'):expected=(False,'PROCESS_OR_NETWORK_BOUNDARY')
    else:return None
    if (row.get('allowed'),row.get('reason'))!=expected:return None
   denied=[r for r in rows[1:-1] if r.get('allowed') is False]
   error_lines=record.get('stderr','').strip().splitlines()
   last_error=error_lines[-1] if error_lines else ''
   boundary_negative=bool(denied) and (record['exit_code']==0 or last_error in {'PermissionError: SCOPE_V3_'+r['reason'] for r in denied})
   witness=output/OBSERVATION_FILE;observations=[];proof=[]
   if witness.is_file():
    observations=[json.loads(s) for s in witness.read_text('utf-8-sig').splitlines() if s.strip()]
    if not any(r.get('event')=='open' and r.get('write') and r.get('allowed') is True and r.get('path')==str(witness) for r in rows):return None
    current=self.env.business_files()
    for observation in observations:
     if observation.get('kind')=='literal_read':
      target=Path(observation.get('target','')).resolve()
      try:relative=target.relative_to(Path(self.env.repo_root).resolve()).as_posix()
      except ValueError:continue
      if relative in current and observation.get('value_type') in {'str','bytes'} and type(observation.get('value_bytes')) is int and observation['value_bytes']>=0 and len(observation.get('value_sha256',''))==64:
       if not any(r.get('event')=='open' and not r.get('write') and r.get('allowed') is True and r.get('path')==str(target) for r in rows):return None
       mode=observation.get('read_mode');encoding=observation.get('effective_encoding')
       if mode=='rb' and observation['value_type']=='bytes' and encoding is None:
        actual_value=target.read_bytes()
       elif mode in {'r','rt'} and observation['value_type']=='str' and isinstance(encoding,str) and encoding:
        # Native open(..., newline=None, errors='strict') text semantics, followed
        # by the witness UTF-8 encoding. Default encoding is observed on native
        # stream.encoding, never guessed from the controller's locale.
        try:actual_value=target.read_bytes().decode(encoding).replace('\r\n','\n').replace('\r','\n').encode('utf-8')
        except (LookupError,UnicodeError):return None
       else:return None
       if observation['value_bytes']!=len(actual_value) or observation['value_sha256']!=hashlib.sha256(actual_value).hexdigest():return None
       proof.append({**observation,'actual_current_file_value_sha256_verified':True,'actual_current_file_value_bytes_verified':True})
     elif observation.get('kind')=='sys_metadata' and observation.get('target') in SYS_METADATA and isinstance(observation.get('actual_value_repr'),str):proof.append(observation)
   if not boundary_negative and (record['exit_code']!=0 or not proof):return None
   # Environment166.run_reproduction writes this exact key; helper stdout
   # cannot claim a reproduction marker even when no-product-import caused the
   # original semantic_marker to be None. Raw MODEL_REPRODUCTION_INVALID stays.
   if 'semantic_marker' not in record or record['semantic_marker'] is not None:return None
   if not isinstance(record.get('stdout'),str):return None
   if any(line.strip() in {'Issue reproduced','Issue resolved','Other issues'} for line in record['stdout'].splitlines()):return None
   return {'generated_script_sha256':record['generated_script_sha256'],'actual_product_python':record['argv'][0],'actual_native_output':str(output),'actual_current_source':str(self.env.repo_root),'scope_log_path':str(scopepath),'scope_log_sha256':hashlib.sha256(scopepath.read_bytes()).hexdigest(),'scope_rows':len(rows),'all_covered_scope_decisions_replayed':True,'actual_readonly_operation_witnesses':proof,'operation_witness_path':str(witness) if witness.is_file() else None,'operation_witness_sha256':hashlib.sha256(witness.read_bytes()).hexdigest() if witness.is_file() else None,'real_scope_boundary_negative':bool(boundary_negative),'actual_scope_denials':denied,'actual_imports_NOT_fabricated':True,'semantic_marker_NOT_granted':True,'goal_ordinary_final_private_acceptance_UNCHANGED':True,'raw_native_record_NOT_modified':True,'tool_observation_only':True}
  def _valid(self,record,generated=False):
   if generated and not record.get('actual_product_imports'):
    evidence=self._guarded_readonly_helper_observation(record)
    if evidence is not None:
     self._record('observer_sourceio_v4_guarded_readonly_helper_tool_observation',evidence);return
   return super()._valid(record,generated)
 return SourceIOV4

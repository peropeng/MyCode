"""Pure parser and AST guard; no imports of actor modules or host execution."""
import ast, shlex
from pathlib import PurePosixPath
class ToolCompatibilityError(ValueError):pass
IllegalTool=ToolCompatibilityError

NATIVE_PROGRAMS={'python','python3','python.exe','pytest','pytest_owned_generated'}
FORBIDDEN_IMPORTS={'os','subprocess','shutil','socket','requests','urllib','ctypes','importlib','pathlib','builtins','sys'}
FORBIDDEN_NAMES={'open','exec','eval','compile','__import__','globals','locals','getattr','setattr','delattr'}
FORBIDDEN_ATTRIBUTES={'open','read_text','read_bytes','write_text','write_bytes','unlink','remove','rmdir','rmtree','mkdir','makedirs','chdir','system','popen','Popen','exec','eval','load','save','loadtxt','fromfile','memmap'}

def _tokens(command):
 lexer=shlex.shlex(command,posix=True,punctuation_chars=';&|<>')
 lexer.whitespace_split=True;lexer.commenters=''
 return list(lexer)

def _outside_controls(command):
 """Reject shell controls only outside quotes; actor Python never reaches a shell."""
 quote=None;escaped=False
 for char in command:
  if char=='\x00':raise IllegalTool('NATIVE_NUL_COMMAND')
  if escaped:
   if char in '\n\r' and quote is None:raise IllegalTool('NATIVE_OUTSIDE_QUOTED_NEWLINE')
   escaped=False;continue
  if char=='\\' and quote!='\x27':escaped=True;continue
  if quote is not None:
   if char==quote:quote=None
   continue
  if char in ('\x27','\x22'):quote=char;continue
  if char in ('\n','\r',';','|','<','>','`','$'):
   raise IllegalTool('NATIVE_UNQUOTED_SHELL_CONTROL')
 if quote is not None:raise IllegalTool('NATIVE_UNBALANCED_QUOTE')

def split_native_invocation(command):
 """Return (optional cd directory, exact program tokens), or None for readonly Bash."""
 if len(command.encode('utf-8'))>65536:raise IllegalTool('NATIVE_COMMAND_BYTE_BOUND')
 tokens=_tokens(command)
 if not tokens:return None
 prefix=None
 if tokens[0]=='cd' and len(tokens)>=4 and tokens[2]=='&&':
  prefix=tokens[1];program=tokens[3:]
 else:program=tokens
 if not program or program[0] not in NATIVE_PROGRAMS:return None
 _outside_controls(command)
 if any(t in {'&&','&','||','|',';','>','>>','<','<<','>&','&>'} for t in program):
  raise IllegalTool('NATIVE_EXTRA_SHELL_SEGMENT')
 return prefix,program

def split_native_tokens(command):
 invocation=split_native_invocation(command)
 if invocation is None or invocation[0] is not None:raise IllegalTool('NATIVE_EXPECTS_SINGLE_PROGRAM')
 return invocation[1]

def business_module_classes(business_sources,requested_modules):
 """Resolve only classes actually declared in the current legal business inventory."""
 known={}
 for relative,source in business_sources.items():
  path=PurePosixPath(relative)
  if path.suffix!='.py' or path.is_absolute() or '..' in path.parts:continue
  parts=path.parts[:-1] if path.name=='__init__.py' else (*path.parts[:-1],path.stem)
  module='.'.join(parts)
  if module not in requested_modules:continue
  tree=ast.parse(source)
  declarations={};other_bindings=set()
  def bindings(node):
   if isinstance(node,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)):return {node.name}
   if isinstance(node,(ast.Import,ast.ImportFrom)):
    return {a.asname or (a.name.split('.')[0] if isinstance(node,ast.Import) else a.name) for a in node.names}
   result=set()
   if isinstance(node,ast.Name) and isinstance(node.ctx,(ast.Store,ast.Del)):result.add(node.id)
   if isinstance(node,ast.ExceptHandler) and node.name:result.add(node.name)
   for child in ast.iter_child_nodes(node):result.update(bindings(child))
   return result
  for node in tree.body:
   if isinstance(node,ast.ClassDef):declarations[node.name]=declarations.get(node.name,0)+1
   else:other_bindings.update(bindings(node))
  known[module]={name for name,count in declarations.items() if count==1 and name not in other_bindings}
 return known

def check_python_source(code,*,business_sources):
 if len(code.encode('utf-8'))>32768:raise IllegalTool('GENERATED_SCRIPT_BYTE_BOUND')
 tree=ast.parse(code)
 parents={id(child):parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
 requested={n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom) and n.level==0 and n.module}
 classes=business_module_classes(business_sources,requested)
 pure_load_bindings=set();import_bindings={}
 for node in ast.walk(tree):
  if isinstance(node,(ast.Import,ast.ImportFrom)):
   names=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module or '']
   if any(name.split('.')[0] in FORBIDDEN_IMPORTS for name in names):
    raise IllegalTool('GENERATED_SCRIPT_IMPORT_NOT_ALLOWLISTED')
   if isinstance(node,ast.ImportFrom) and any(a.name=='*' for a in node.names):
    raise IllegalTool('GENERATED_SCRIPT_WILDCARD_IMPORT_NOT_ALLOWED')
   for alias in node.names:
    bound=alias.asname or (alias.name.split('.')[0] if isinstance(node,ast.Import) else alias.name)
    import_bindings.setdefault(bound,[]).append((node.module if isinstance(node,ast.ImportFrom) else '',alias.name))
   if isinstance(node,ast.ImportFrom) and node.level==0:
    pure_load_bindings.update(a.asname or a.name for a in node.names if a.name in classes.get(node.module,set()))
 if any(len(import_bindings.get(name,[]))!=1 for name in pure_load_bindings):
  raise IllegalTool('PURE_BUSINESS_CLASS_BINDING_AMBIGUOUS')
 for node in ast.walk(tree):
  rebound=(isinstance(node,ast.Name) and isinstance(node.ctx,(ast.Store,ast.Del)) and node.id in pure_load_bindings)
  rebound=rebound or (isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and node.name in pure_load_bindings)
  rebound=rebound or (isinstance(node,ast.arg) and node.arg in pure_load_bindings)
  rebound=rebound or (isinstance(node,ast.ExceptHandler) and node.name in pure_load_bindings)
  if hasattr(ast,'MatchAs'):rebound=rebound or (isinstance(node,(ast.MatchAs,ast.MatchStar)) and node.name in pure_load_bindings)
  if hasattr(ast,'MatchMapping'):rebound=rebound or (isinstance(node,ast.MatchMapping) and node.rest in pure_load_bindings)
  if rebound:raise IllegalTool('PURE_BUSINESS_CLASS_BINDING_REASSIGNED')
  if isinstance(node,ast.Name) and isinstance(node.ctx,ast.Load):
   if node.id in FORBIDDEN_NAMES or (node.id.startswith('__') and node.id!='__name__'):
    raise IllegalTool('GENERATED_SCRIPT_DYNAMIC_OR_REFLECTIVE_NAME_NOT_ALLOWED')
  if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in FORBIDDEN_NAMES:
   raise IllegalTool('GENERATED_SCRIPT_UNBOUNDED_FILESYSTEM_OR_DYNAMIC_EXECUTION')
  if isinstance(node,ast.Attribute):
   if node.attr in {'__version__','__name__'} and isinstance(node.ctx,ast.Load):continue
   parent=parents.get(id(node))
   pure_load=(node.attr=='load' and isinstance(node.value,ast.Name) and node.value.id in pure_load_bindings
              and isinstance(parent,ast.Call) and parent.func is node)
   if pure_load:continue
   if node.attr.startswith('__') or node.attr in FORBIDDEN_ATTRIBUTES:
    raise IllegalTool('GENERATED_SCRIPT_EXTERNAL_IO_OR_REFLECTION_NOT_ALLOWED')
 return code

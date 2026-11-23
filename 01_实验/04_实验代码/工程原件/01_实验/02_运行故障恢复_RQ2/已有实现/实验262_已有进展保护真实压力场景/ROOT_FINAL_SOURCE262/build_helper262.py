"""Adapt only namespace and identity SOURCE lookup; no native/private IO."""
import ast,hashlib,json
from pathlib import Path
S=Path(__file__).resolve().parent;R=Path('D:/Code/毕设/graduate-thesis-experiments');P249=R/'工作区/1012-exp249-prospective-confirmation/实验/实验249_固定顺序新任务共同确认'
p=P249/'native249_ROOT_MASK_V3_CAPACITY.py';tree=ast.parse(p.read_text('utf-8-sig'));names={'load_jobs','stopped','parent_member','supervise','load_original_probe','identity_prefix','wrap_native_argv','verify_measured_identity'};nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];assert len(nodes)==len(names)
class IdentitySource(ast.NodeTransformer):
 def visit_Call(self,node):
  self.generic_visit(node)
  if ast.unparse(node)=='Path(__file__).resolve()':return ast.Name(id='FINAL_WORKER_SOURCE',ctx=ast.Load())
  return node
 def visit_BinOp(self,node):
  self.generic_visit(node)
  if isinstance(node.op,ast.Div) and isinstance(node.left,ast.Name) and node.left.id=='E' and isinstance(node.right,ast.Constant) and node.right.value=='physical_identity249.py':return ast.Name(id='IDENTITY_SOURCE',ctx=ast.Load())
  return node
nodes=[IdentitySource().visit(n) for n in nodes]
code='"""Original held Jobs/probe/identity helper; E=output, IDENTITY_SOURCE=code."""\nimport argparse,contextlib,ctypes,subprocess\nfrom final_common262 import *\n'+ast.unparse(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])))+'\n'
ast.parse(code);(S/'root_helper262.py').write_text(code,'utf-8')
identity=P249/'physical_identity249.py';(S/'physical_identity249.py').write_bytes(identity.read_bytes())
print(json.dumps({'SOURCE_ONLY':True,'original_helper':str(p),'helper_SHA256':hashlib.sha256((S/'root_helper262.py').read_bytes()).hexdigest(),'identity_raw_SHA256':hashlib.sha256(identity.read_bytes()).hexdigest(),'SOURCE_identity_and_output_E_separate':True,'native_private_calls':0}))

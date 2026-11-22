"""Compile the exact strict224 public codec/body functions, without old runtime."""
import ast,collections,copy,hashlib,json,re
from contracts241 import *
SOURCE=ROOT/'工作区/1008-2320-exp224-flash-common/实验/实验224_二十三题Flash完整共同恢复比较'
AL=ROOT/'工作区/1008-exp183-fixed12-complete-main/实验/实验183_固定十二题完整恢复与排序对照'

def original_functions(path,names):
 tree=ast.parse(Path(path).read_text('utf-8-sig'))
 rows=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
 if {n.name for n in rows}!=set(names):raise EngineeringUnknown('ORIGINAL_SYMBOLS_NOT_FOUND')
 exec(compile(ast.Module(body=rows,type_ignores=[]),str(path),'exec'),globals())

original_functions(SOURCE/'publicpack_v2_224.py',{'model_pack','render'})
original_functions(SOURCE/'environment_v2_224.py',{'body_v2','initial_index_v2'})
original_functions(AL/'audit183/new_public_contract_preflight.py',{'semantic_index'})

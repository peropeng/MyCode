"""Copy only declared public algorithm/native source; no old state/results."""
import ast, hashlib, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=Path('D:/Code/毕设/graduate-thesis-experiments')
SHARED=ROOT/'工作区/1012-exp249-prospective-confirmation/实验/实验249_固定顺序新任务共同确认/method_sources'
AL246=ROOT/'工作区/1011-exp246-agentless-unbudgeted/实验/实验246_Agentless论文完整配置无外部预算'
PUBLIC224=ROOT/'工作区/1008-2320-exp224-flash-common/实验/实验224_二十三题Flash完整共同恢复比较'
AL183=ROOT/'工作区/1008-exp183-fixed12-complete-main/实验/实验183_固定十二题完整恢复与排序对照'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
mapping={}
def copy(source,relative,expected=None):
 source=Path(source);dest=HERE/relative
 if expected is not None and sha(source)!=expected:raise RuntimeError('SOURCE_SHA_DRIFT '+str(source))
 data=source.read_bytes();dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists() and dest.read_bytes()!=data:raise RuntimeError('EXISTING_COPY_DIFFERS '+str(dest))
 if not dest.exists():dest.write_bytes(data)
 mapping[str(dest)]={'source':str(source),'source_SHA256':sha(source),'copy_SHA256':sha(dest),'byte_exact':True}
 for_copy = None

for source,entry in read(SHARED/'AGENTLESS_ORIGINAL_SOURCE_MAP249.json')['files'].items():
 relative=Path(source).relative_to(SHARED/'agentless_core')
 copy(source,Path('agentless_core')/relative,entry['copy_SHA256'])
copy(PUBLIC224/'retrieval178.py','agentless_core/retrieval178.py')
for name in ('contracts241.py','winjob241.py','supervision_classification241.py','product_entry241.py',
             'generated_scope_v2_241.py','guarded_reproduction_invalid_SOURCE.py'):
 copy(AL246/name,Path('native_core')/name)
copy(SHARED/'AGENTLESS_PUBLIC_DENSE_BINDINGS249_SOURCE.json','PUBLIC_DENSE_BINDINGS251_SOURCE.json')
copy(SHARED/'PUBLIC_SOURCE_BINDINGS249.json','PUBLIC_SOURCE_BINDINGS249_REFERENCE.json')

functions=[];function_sources={}
for source,names in ((PUBLIC224/'publicpack_v2_224.py',{'model_pack','render'}),
                     (PUBLIC224/'environment_v2_224.py',{'body_v2','initial_index_v2'}),
                     (AL183/'audit183/new_public_contract_preflight.py',{'semantic_index'})):
 text=source.read_text('utf-8-sig');tree=ast.parse(text)
 nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
 if {n.name for n in nodes}!=names:raise RuntimeError('ORIGINAL_SYMBOLS_MISSING')
 functions.extend(ast.get_source_segment(text,n) for n in nodes)
 function_sources[str(source)]={'SHA256':sha(source),'exact_function_symbols':sorted(names)}
prefix='"""Exact original public body/codec functions; no old runtime import."""\nimport collections,copy,hashlib,json,re\n\ndef canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(\",\",\":\"),allow_nan=False)\ndef digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()\n'
target=HERE/'public_body251.py';data=(prefix+'\n\n'.join(functions)+'\n').encode()
if target.exists() and target.read_bytes()!=data:raise RuntimeError('BODY_DERIVATIVE_ALREADY_DIFFERS')
if not target.exists():target.write_bytes(data)
save(HERE/'COPIED_SOURCE_MAP251.json',{'schema':'EXP251-public-full-Agentless-source-copy/1','files':mapping,
 'public_body_exact_function_sources':function_sources,'public_body_path':str(target),'public_body_SHA256':sha(target),
 'original_parameters':'4 fine location sets x10 patches,40 reproductions; full filter/normalization/vote',
 'old_responses_candidates_selection_or_private_copied':False,'model_native_private_finance':0})
print(json.dumps({'copies':len(mapping),'public_body_SHA256':sha(target),'source_only':True},ensure_ascii=False))

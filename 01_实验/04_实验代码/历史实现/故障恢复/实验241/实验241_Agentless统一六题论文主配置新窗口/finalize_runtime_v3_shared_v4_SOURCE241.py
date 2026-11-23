"""Finalize SOURCE/SHA references only. No native/provider/qualification execution."""
from pathlib import Path
import ast,datetime,hashlib,json
E=Path(__file__).resolve().parent;D=E/'runtime_v3_SOURCE';R=Path('D:/Code/毕设/graduate-thesis-experiments');W=R/'工作区/1010-unified-six'
SHARED=R/'工作区/1009-exp239-enagent-flash-auto/实验/实验239_EnAgent_统一六题财政V3_SOURCE/shared_native_v4_SOURCE'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
expected={'native_masked_public239.py':'e69ce16f05a5f95734a2b0cbb253389da83b4bf1257623a840ada2cee12366d3','guard_v4/sitecustomize.py':'0a3f9870c3fd58797798485d3b1ea4e36faf2d15e0cba89dd772c003da900b7c','guard_v4/runner.py':'fe2f3fecfd3d9d12a985c965364df6515d99097ce0367457d71b10e112f623f1'}
for rel,h in expected.items():assert sha(SHARED/rel)==h
seal=read(D/'SOURCE_SEAL.json')
seal['sources']={p:h for p,h in seal['sources'].items() if 'shared_native_v3_SOURCE' not in p}
for p in D.glob('*.py'):ast.parse(p.read_text('utf-8-sig'));seal['sources'][str(p)]=sha(p)
for rel,h in expected.items():seal['sources'][str(SHARED/rel)]=h
provenance=read(E/'PAPER_CORE_SOURCE_PROVENANCE241.json')
for p,h in provenance['CST_original_sources_sha256'].items():assert sha(p)==h;seal['sources'][p]=h
old=read(E/'SOURCE_ONLY_CURRENT_MANIFEST241.json')
for p,h in old['original20purefunctions_and15prompts_SHA'].items():assert sha(p)==h;seal['sources'][p]=h
AL=R/'工作区/1008-exp183-fixed12-complete-main/实验/实验183_固定十二题完整恢复与排序对照'
seal['sources'][str(AL/'agentless_bridge/dense166.py')]=sha(AL/'agentless_bridge/dense166.py')
save(D/'SOURCE_SEAL.json',seal)
for case in (D/'candidate').iterdir():
 p=read(case/'protocol.SOURCE_ONLY.json')
 p['shared_public_helper']={'path':str(SHARED/'native_masked_public239.py'),'sha256':expected['native_masked_public239.py']}
 p['masked_native_guard_directory']=str(SHARED/'guard_v4')
 p['shared_native_startup']='same helper -S explicit site.main; preserve supplied -c argv; actual held/self physical proof before product import'
 save(case/'protocol.SOURCE_ONLY.json',p)
 for file in case.glob('*.false.template.json'):
  g=read(file);g.update(source_seal_sha256=digest(seal),protocol_sha256=digest(p),protocol_raw_sha256=sha(case/'protocol.SOURCE_ONLY.json'));save(file,g)
ready=read(D/'SOURCE_READY_RUNTIME_V3_FALSE.json')
ready.update(at_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_seal_sha256=digest(seal),source_seal_raw_sha256=sha(D/'SOURCE_SEAL.json'),
 shared_helper_guard_runner_SHA={str(SHARED/rel):h for rel,h in expected.items()},shared_native_version='v4 global startup/log compatibility same Root frozen guard',
 physical_identity_write_root='same owned per-native output directory, never actor source',
 actual_mechanical_native_POST_private=0,root_actual_shared_v4_mechanical_pending=True,
 author_scientific_result_not_claimed_from_AST=True,independent_final_Root_only_after_author_STOP=True)
assert sha(D/'agentless_paper_main241.py')==sha(E/'source_runtime_v1/agentless_paper_main241.py')
save(D/'SOURCE_READY_RUNTIME_V3_FALSE.json',ready)
print(canonical({'directory':str(D),'seal_digest':digest(seal),'seal_rawSHA':sha(D/'SOURCE_SEAL.json'),'sharedv4_exact3':True,'allgrantsfalse':True,'experiments0':True}))

"""Complete zero-model preparation seals; latest root fiscal source/config included."""
import ast,datetime,sys
from pathlib import Path
sys.dont_write_bytecode=True
from contracts241 import *
from public_v2_241 import AL,SOURCE

def main():
 manifest=read(HERE/'AUTHOR_SOURCE_MANIFEST241.json')
 for path,h in manifest['sources'].items():
  if sha(path)!=h:raise EngineeringUnknown('ORIGINAL_AUTHOR_OR_STRICT_V2_SOURCE_DRIFT '+path)
 for p in HERE.glob('*.py'):ast.parse(p.read_text('utf-8-sig'))
 core_ast=ast.parse((AL/'agentless178.py').read_text('utf-8-sig'))
 run=next(n for n in core_ast.body if isinstance(n,ast.FunctionDef) and n.name=='run')
 calls=[getattr(n.func,'attr',getattr(n.func,'id',None)) for n in ast.walk(run) if isinstance(n,ast.Call)]
 loops=[ast.get_source_segment((AL/'agentless178.py').read_text('utf-8-sig'),n.iter) for n in ast.walk(run) if isinstance(n,ast.For)]
 if 'range(4)' not in loops or '(0.,.8,.8,.8)' not in ''.join(loops):raise EngineeringUnknown('FOUR_CORE_SAMPLE_LOOPS_NOT_FOUND')
 for name in ('apply_patch','run_reproduction','run_regression','select'):
  if name not in calls:raise EngineeringUnknown('CORE_NATIVE_SELECTION_STEP_MISSING '+name)
 save(HERE/'CORE_AST_BINDING241.json',{'method_sha256':sha(AL/'agentless178.py'),'official_pin':SOURCE_PIN,
  'original_four_location_and_four_reproduction_loops':True,'original_step_calls':calls,'original_loop_iterators':loops,
  'exact_author_prompt_bytes_sha256':sha(AL/'agentless_bridge/official_prompts166.json'),
  'official_parser_vote_normalization_sha256':sha(AL/'agentless_bridge/official_core166.py'),
  'core_not_rewritten':True,'generation_native_private_ledger_write':0})
 for task in read(HERE/'PREPARED241.json')['tasks']:
  base=HERE/'candidate'/task;s=read(base/'source_seal.json');sources=s['sources']
  for name in ('resume_transport.py','continuous_core_v2.py'):
   p=ROOT/'工作区/1009-research-resume/finance'/name;sources[str(p)]=sha(p)
  for p in HERE.glob('*.py'):sources[str(p)]=sha(p)
  sources.update(read(base/'public_contract.json')['harness_sources'])
  s['inputs'][str(HERE/'finance_config241.json')]=sha(HERE/'finance_config241.json')
  s['inputs'][str(HERE/'CORE_AST_BINDING241.json')]=sha(HERE/'CORE_AST_BINDING241.json')
  for path,h in {**sources,**s['inputs']}.items():
   if sha(path)!=h:raise EngineeringUnknown('PREPARED_SOURCE_INPUT_DRIFT '+path)
  save(base/'source_seal.json',s)
  g=read(base/'root_grant.template.json');g.update(source_seal_sha256=digest(s),protocol_sha256=digest(read(base/'protocol.json')))
  save(base/'root_grant.template.json',g)
 print(canonical({'source_seals_ready':True,'science_grants_false':True,'AST_original4L4P4T_PASS':True,'generation_native_private_ledger_write':0}))
if __name__=='__main__':main()

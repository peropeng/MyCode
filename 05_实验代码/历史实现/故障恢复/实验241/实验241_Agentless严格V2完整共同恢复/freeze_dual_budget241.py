"""Actual pre-spawn counter boundary fixtures plus prospective protocol seals."""
import ast,datetime
from contracts241 import *
from owner241 import Owner

def fixture():
 own=Owner.__new__(Owner);own.protocol={'budget':{'native_roots_total':90,'product_native_roots_total':64}}
 own.native_roots=64;own.native_calls=63;own.native_root_kinds={'controller':1,'pytest':63};own._native_kind='pytest'
 own.reserve_native()
 if own.native_roots!=65 or own.native_root_kinds['pytest']!=64:raise EngineeringUnknown('64TH_PRODUCT_NOT_RESERVED')
 before=(own.native_roots,own.native_calls,dict(own.native_root_kinds))
 try:own.reserve_native()
 except DeclaredBudgetEnd:pass
 else:raise EngineeringUnknown('65TH_PRODUCT_NOT_REJECTED_BEFORE_SPAWN')
 if before!=(own.native_roots,own.native_calls,own.native_root_kinds):raise EngineeringUnknown('REJECTED_PRODUCT_MUTATED_COUNTER')
 own._native_kind='helper';own.native_roots=90
 try:own.reserve_native()
 except EngineeringUnknown as error:
  if 'RESOURCE_CENSORED' not in str(error):raise
 else:raise EngineeringUnknown('ALL_OS90_NOT_RESOURCE_UNKNOWN')
 tree=ast.parse((HERE/'winjob241.py').read_text('utf-8-sig'))
 execute=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='execute')
 reserve=min(n.lineno for n in ast.walk(execute) if isinstance(n,ast.Call) and getattr(n.func,'attr',None)=='reserve_native')
 birth=min(n.lineno for n in ast.walk(execute) if isinstance(n,ast.Call) and getattr(n.func,'attr',None)=='CreateJobObjectW')
 if reserve>=birth:raise EngineeringUnknown('REAL_RUNNER_RESERVES_ONLY_AFTER_OS_CREATE')
 return {'64th_product_allowed_and_counted':True,'65th_product_pre_spawn_rejected_without_counter_mutation':True,
  'all_OS90_guard_is_engineering_resource_unknown':True,'reserve_before_CreateJobObjectW_in_actual_runner':True,
  'fixture_spawned_processes':0,'actual_native_C0_and_generated_qualification_reused':True}

def main():
 receipt=fixture();save(HERE/'DUAL_NATIVE_BUDGET_FIXTURE241.json',receipt)
 ready=read(HERE/'READY_ROOT241.json')
 sources=read(HERE/'SOURCE_MANIFEST241.json')['sources'];sources.update({str(p):sha(p) for p in HERE.glob('*.py')})
 manifest=read(HERE/'SOURCE_MANIFEST241.json');manifest.update(sources=sources,own_sources={str(p):sha(p) for p in HERE.glob('*.py')})
 save(HERE/'SOURCE_MANIFEST241.json',manifest)
 for row in ready['cases']:
  base=HERE/'candidate'/row['task_id'];p=read(base/'protocol.json')
  p['budget']['product_native_roots_total']=64
  p.update(historical_source_protocol_only=True,root_protocol_current_science_authorization=False,
   current_scientific_authority='Only new matching root actual grant/current deadlines/global continuous financial registration; old root_protocol is common public input provenance only',
   native_count_objects={'common_budget':'64 actual product/generated/pytest/coverage roots including final private pytest, reserved before OS spawn',
    'deployment_guard':'90 all_OS controller/evaluator/helper/product roots; exhaustion=EngineeringUnknown resource censor, never method0'},
   dual_native_counter_fixture=str(HERE/'DUAL_NATIVE_BUDGET_FIXTURE241.json'))
  save(base/'protocol.json',p);s=read(base/'source_seal.json');s['sources']=sources
  for path in list(s['inputs']):
   if inside(path,HERE):s['inputs'][path]=sha(path)
  s['inputs'][str(HERE/'DUAL_NATIVE_BUDGET_FIXTURE241.json')]=sha(HERE/'DUAL_NATIVE_BUDGET_FIXTURE241.json')
  save(base/'source_seal.json',s);g=read(base/'root_grant.template.json')
  g.update(protocol_sha256=digest(p),protocol_raw_sha256=sha(base/'protocol.json'),source_seal_sha256=digest(s));save(base/'root_grant.template.json',g)
  row['source_seal_sha256']=digest(s)
 ready.update(maximum_common_budget=read(ready['cases'][0]['protocol'])['budget'],dual_native_budget=receipt,
  native64_common_90_resource_only=True,source_count=len(sources),utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 save(HERE/'READY_ROOT241.json',ready)
 for row in ready['cases']:
  s=read(row['source_seal'])
  for path,h in {**s['sources'],**s['inputs']}.items():
   if sha(path)!=h:raise EngineeringUnknown('FINAL_DUAL_BUDGET_SEAL_DRIFT '+path)
 print(canonical({'DUAL_NATIVE_FIXTURE_PASS':True,'READY_ROOT241':str(HERE/'READY_ROOT241.json'),
  'sources':len(sources),'seals':{r['task_id']:r['source_seal_sha256'] for r in ready['cases']},'science_grants_false':True}))
if __name__=='__main__':main()

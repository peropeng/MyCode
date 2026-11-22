"""One authorized global startup repair. No old science replay or model calls."""
from pathlib import Path
import ast,hashlib,json,datetime,copy
E=Path(__file__).resolve().parent;OLD=E/'runtime_v6_MECHANICAL_SOURCE';D=E/'runtime_v7_SOURCE'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
def source(n,t):ast.parse(t);(D/n).write_text(t,'utf-8')
if D.exists():raise RuntimeError('V7_GLOBAL_SOURCE_ONCE_NO_OVERWRITE')
D.mkdir()
for f in OLD.glob('*.py'):source(f.name,f.read_text('utf-8-sig'))
save(D/'PAPER_CORE_SOURCE_PROVENANCE241.json',read(OLD/'PAPER_CORE_SOURCE_PROVENANCE241.json'))
t=(D/'owner241.py').read_text('utf-8')
a="bootstrap=\"import site,sys,runpy;site.main();sys.argv=sys.argv[1:];runpy.run_path(sys.argv[0],run_name='__main__')\""
b="bootstrap=\"import site,sys,runpy;site.main();sys.argv=sys.argv[1:];from pathlib import Path;sys.path.insert(0,str(Path(sys.argv[0]).resolve().parent));runpy.run_path(sys.argv[0],run_name='__main__')\""
assert t.count(a)==1;t=t.replace(a,b);source('owner241.py',t)
t=(D/'product_entry241.py').read_text('utf-8')
a="identity=self_identity(os.environ['PATCHPILOT_JOB'],envelope['expected_physical_python'])"
b=a+"\n    identity.update(actual_sys_executable=sys.executable,actual_sys_prefix=sys.prefix,actual_sys_base_prefix=sys.base_prefix)"
assert t.count(a)==1;t=t.replace(a,b);source('product_entry241.py',t)
assert sha(D/'agentless_paper_main241.py')==sha(OLD/'agentless_paper_main241.py')
entry='''"""One existing public script as deployment input only. No SCI/API/private."""
import argparse,json
from contracts241 import *
from environment241 import Environment241
def main():
 a=argparse.ArgumentParser()
 for n in ('protocol','grant','seal','contract'):a.add_argument('--'+n,required=True)
 a.add_argument('mode');x=a.parse_args();env=Environment241(x.protocol,x.grant,x.seal,x.contract);env.initialize()
 result={'schema':'AL241-v7-single-generated-startup-deployment-qualification/1','scientific_result':False,'API_POSTs':0,'private':0,'fee_CNY':'0'}
 try:
  p=Path(env.protocol['single_public_generated_script']);assert sha(p)==env.protocol['single_public_generated_script_sha256']
  raw=env.run_reproduction(p.read_text('utf-8'),env.initial_snapshot,'V7_DEPLOYMENT_ONLY_NOT_SCIENTIFIC_REPRO')
  result.update(status='KNOWN_DEPLOYMENT_NATIVE_EXECUTED',raw_native=raw,actual_product_identity=raw['native_record'].get('actual_product_python_identity'),
   script_origin=str(p),script_origin_sha256=sha(p),old_scientific_output_not_replayed_as_method_result=True)
 except BaseException as error:
  result.update(status='DEPLOYMENT_UNKNOWN',error={'type':type(error).__name__,'message':str(error)},unknown=env.unknown)
 save(env.output_root/'V7_STARTUP_MECHANICAL_RESULT.json',result,scope=env.output_root)
if __name__=='__main__':main()
'''
source('entry_startup_v7_241.py',entry)
# Same owned parent runner, a single deployment-only child entry.
t=(D/'supervisor_runtime_v3_241.py').read_text('utf-8').replace("str(HERE/'entry_runtime_v3_241.py'),x.mode","str(HERE/'entry_startup_v7_241.py'),x.mode")
source('supervisor_startup_v7_241.py',t)
p=read(OLD/'protocol.MECHANICAL.release.json')
script=next((OLD/'science_once_six/getmoto__moto-5406/actor_flow/generated_native').glob('*/generated_test.py'))
p.update(masked_native_owner_root=str(D),core_source=str(D/'agentless_paper_main241.py'),
 output_root=str(D/'single_startup_qualification5406/actor_flow'),supervision_output_root=str(D/'single_startup_qualification5406/supervision'),
 single_public_generated_script=str(script),single_public_generated_script_sha256=sha(script),
 generation_native_startup_only=True,source_directory_front_insert_matches_original_direct_script=True,
 no_C0_ABI_collection_fixture_or_new_science_run=True,source_only=False,execution_authorized=True)
save(D/'protocol.STARTUP_MECHANICAL.release.json',p)
old_seal=read(OLD/'SOURCE_SEAL.json')
external={p:h for p,h in old_seal['sources'].items() if not Path(p).is_relative_to(OLD)}
seal={'schema':'AL241-v7-single-global-startup-source-seal/1','author_pin':old_seal['author_pin'],'sources':{str(f):sha(f) for f in D.glob('*.py')},'inputs':{**old_seal['inputs'],str(script):sha(script)}}
seal['sources'].update(external);save(D/'SOURCE_SEAL.json',seal)
g=read(OLD/'ROOT_MECHANICAL_GRANT.actual.json')
g.update(new_start_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_seal_sha256=digest(seal),
 protocol_sha256=digest(p),protocol_raw_sha256=sha(D/'protocol.STARTUP_MECHANICAL.release.json'),
 delegation_evidence='Root explicitly allows one <=5min global startup repair and one0API0private generated-native deployment qualification using existing public script, never old scientific continuation',max_wall_seconds=300)
save(D/'ROOT_STARTUP_MECHANICAL_GRANT.actual.json',g)
save(D/'STARTUP_FIX_SOURCE_PROVENANCE241.json',{'unique_failure':'-S/-c runpy lacks automatic script directory sys.path[0]; ModuleNotFoundError winjob241 before selfproof',
 'changed_global_startup':{'old_owner_sha':sha(OLD/'owner241.py'),'new_owner_sha':sha(D/'owner241.py')},
 'additional_actual_self_metadata':['actual_sys_executable','actual_sys_prefix','actual_sys_base_prefix'],
 'old_science_T1_unchanged_UNKNOWN_no_retry':True,'model_core40patch40repro_sameSHA':sha(D/'agentless_paper_main241.py'),
 'shared_v6_guard_and_permissions_unchanged':True,'all_six_same_global_generated_bootstrap':True,'model_generation_private_false':True,
 'new_start':g['new_start_UTC'],'max300':True,'seal_digest':digest(seal)})
print(canonical({'directory':str(D),'start':g['new_start_UTC'],'seal':digest(seal),'model_false':g['model_generation_authorized'],'private_false':g['private_acceptance_authorized'],'one_native_qualification_only':True}))

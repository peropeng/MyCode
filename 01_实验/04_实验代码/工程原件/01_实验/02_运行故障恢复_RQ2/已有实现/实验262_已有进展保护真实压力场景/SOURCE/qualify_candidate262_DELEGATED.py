"""One Root-authorized actual G/O observation. Default closed, no model IO."""
import argparse,ast,copy,datetime,hashlib,importlib.util,json,os,sys,time,types
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent.parent;ROOT=Path('D:/Code/毕设/graduate-thesis-experiments')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def save(p,x):
 p=Path(p).resolve();assert p.is_relative_to(H);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(canonical(x)+'\n','utf-8')
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def checked(ref):assert sha(ref['path'])==ref['sha256'],'BOUND_SHA_DRIFT';return read(ref['path'])
def exclusive(path,value):
 with Path(path).open('x',encoding='utf-8') as f:f.write(canonical(value)+'\n');f.flush();os.fsync(f.fileno())
def execute(grant_path):
 gp=Path(grant_path);g=read(gp);gh=sha(gp);ready=checked(g['ready']);state=checked(ready['partial_state']);output=Path(ready['native_output']).resolve()
 def gate():
  assert sha(gp)==gh and g['schema']=='Root-EXP262-once-native-only/1' and g['root_authorized'] is True and g['native_authorized'] is True
  assert all(g[k] is False for k in ('model_authorized','private_authorized','finance_authorized')) and g['maximum_new_original_G_O_native']==1
  assert time.time()<datetime.datetime.fromisoformat(g['lease_end_UTC']).timestamp() and not any(Path(p).exists() for p in g['root_stop_paths'])
 gate();seal=checked(g['source_seal'])
 for p,h in {**seal['sources'],**seal.get('dependencies',{}),**seal.get('public_inputs_SHA256',{})}.items():assert sha(p)==h,'SOURCE_OR_INPUT_DRIFT'
 assert ready['task_id']=='getmoto__moto-7081' and output.is_relative_to(H/'runs') and ready['maximum_new_original_G_O_native']==1
 assert ready['exact_nodes']==read(H/'NATIVE_READY262_FALSE.json')['exact_nodes'],'ORIGINAL_GO_SCOPE_ONLY'
 assert set(state['business_SHA256'])==set(read(H/'PARTIAL_BUSINESS_STATE.json')['business_SHA256']),'EXACT_861_LEGAL_BUSINESS_SCOPE'
 assert not output.exists(),'ONCE_NATIVE_STARTED_OR_COMPLETE_NO_RETRY'
 repo=Path(state['source_root']).resolve();assert repo.is_relative_to(H/'runs') and {p:sha(repo/p) for p in state['business_SHA256']}==state['business_SHA256']
 for spec in ready['source_assets'].values():assert sha(spec['path'])==spec['sha256'],'RUNTIME_ASSET_DRIFT'
 output.mkdir(parents=True);exclusive(output/'NATIVE_INTENT.json',{'Root_grant_SHA256':gh,'state_SHA256':ready['partial_state']['sha256'],'exact_nodes':ready['exact_nodes'],'model_private_finance':0})
 # The original probe only sees the declared 3 G and 1 O. Guard/plugin are
 # external frozen assets; neither actor nor this SOURCE copies test bodies.
 q=module('_exp262_original_qualifier',Path(ready['asset_root'])/'qualify.py');original=Path(ready['source_assets']['original_probe']['path']);tree=ast.parse(original.read_text('utf-8-sig'));nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('assess_probe','probe')];assert len(nodes)==2
 run=types.ModuleType('_exp262_original_probe');run.__file__=str(original);run.__dict__.update(Path=Path,ast=ast,time=time,qualify=q,load=read,write=save,read_jsonl=lambda p:[json.loads(v) for v in Path(p).read_text('utf-8').splitlines() if v.strip()]);exec(compile(ast.Module(body=nodes,type_ignores=[]),str(original),'exec'),run.__dict__)
 bridge=types.ModuleType('common166');bridge.__dict__.update(Path=Path,json=json,os=os,sys=sys,time=time,ROOT=ROOT,E=H,save=save,read=read,sha=sha,now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat(),canonical=canonical,authorization=gate,MAX_ALL_OS_ROOTS=2,MAX_PRODUCT_NATIVE_ROOTS=1,NATIVE_TIMEOUT_SECONDS=300);sys.modules['common166']=bridge
 jobs=module('_exp262_original_exact_jobs',H/'SOURCE/native_executor242_prospective.py');jobs.OS_ROOT_RESERVATIONS=1;jobs.PRODUCT_ROOT_RESERVATIONS=0
 events=[];env=types.SimpleNamespace(run=run,package='moto',record=lambda k,v:events.append({'stage':k,'evidence':v}));jobs.install(env)
 capacity=module('_exp262_original_capacity',H/'SOURCE/native_capacity_v10.py');capacity.install(env)
 scheduler=module('_exp262_shared_native_lane',ROOT/'工作区/1010-unified-six/native_four_slots_v5_SOURCE.py');schedule=read(ROOT/'工作区/1010-unified-six/ROOT_COMMON_NATIVE_SCHEDULING_V5_FOUR_SOURCE.json')
 with scheduler.native_lane(schedule['lock_path'],'moto',gate,lambda v:events.append({'stage':'shared_four_slots','evidence':v})):
  gate();result=run.probe(repo.parent,Path(ready['frozen_tests']),ready['exact_nodes'],output/'actual_G_O',Path(ready['native_interpreter']),'moto',time.monotonic()+min(300,datetime.datetime.fromisoformat(g['lease_end_UTC']).timestamp()-time.time()))
 assert result.get('completed_guarded_coverage') is True and result.get('guard_loaded') is True and result.get('business_state_unchanged') is True and result.get('frozen_tests_unchanged') is True,'CANDIDATE_NATIVE_COMPLETE_GUARDED_SOURCE_FROZEN_REQUIRED'
 assert {p:sha(repo/p) for p in state['business_SHA256']}==state['business_SHA256'],'NATIVE_CHANGED_PARTIAL_BUSINESS'
 guard=module('_exp262_unmodified_progress_guard',H/'SOURCE/ours_core/progress_guard240.py');ordinary={n:result['pytest']['outcomes'][n] for n in ready['ordinary']};validation={'native_record':result,'outcomes':ordinary};observed=guard.observe(validation,ready['goals'],ready['ordinary'])
 currentP=sorted(observed['goal_pass']);qualified=observed['ordinary_pass']
 save(output/'NATIVE_TRANSPORT_EVIDENCE.json',events)
 value={'schema':'EXP262-current-exposed-partial-start-actual-observation/1','current_qualified_partial_START':qualified,'task_id':ready['task_id'],'business_inventory_SHA256':state['business_inventory_SHA256'],'business_SHA256':state['business_SHA256'],'native_record_ref':{'path':str(output/'actual_G_O/run.json'),'sha256':sha(output/'actual_G_O/run.json')},'current_P':currentP,'current_ordinary_all_pass':observed['ordinary_pass'],'public_validation':observed['complete_validation'],'historical_partial_pressure_only_not_new_C0':True,'actual_product_identity_and_Job_STOP_in_native_record':True,'one_original_G_O_native':True,'model_private_finance_ledger_write':0}
 value.update(task_id=ready['task_id'],policy=ready['policy'],trial_id=ready['trial_id'],candidate_source_inventory_SHA256=state['business_inventory_SHA256'],public_native_path=str(output/'actual_G_O/run.json'),public_native_SHA256=sha(output/'actual_G_O/run.json'));save(output/'ROOT_COMPLETED_PUBLIC.json',value);print(canonical({'candidate_original_GO_complete':True,'complete':str(output/'ROOT_COMPLETED_PUBLIC.json')}))
def main():
 p=argparse.ArgumentParser();p.add_argument('--root-grant');a=p.parse_args()
 if not a.root_grant:print(canonical({'SOURCE_ONLY':True,'default_closed':True,'model_native_private_finance_ledger_write':0}));return
 execute(a.root_grant)
if __name__=='__main__':main()

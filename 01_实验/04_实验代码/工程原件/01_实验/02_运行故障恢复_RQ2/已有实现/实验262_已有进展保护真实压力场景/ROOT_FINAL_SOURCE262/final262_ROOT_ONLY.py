"""Separate Root-only once final; selectors opened only in true-granted worker."""
import argparse
from final_common262 import *
import root_helper262 as helper

class FinalGrant:
 def __init__(self,path):
  self.path=Path(path).resolve();self.sha256=sha(self.path);self.value=read(self.path);self.ready=checked(self.value['ready']);self.check(full=True)
 def check(self,full=False):
  g=self.value;r=self.ready
  if sha(self.path)!=self.sha256 or any(g.get(k) is not True for k in ('root_authorized','native_authorized','private_authorized','once_private_authorized','no_feedback_to_model')):raise RuntimeError('EXP262_INDEPENDENT_FINAL_DEFAULT_CLOSED_OR_CHANGED')
  if any(g.get(k) is not False for k in ('model_authorized','finance_authorized')) or g.get('maximum_new_private_native')!=1:raise RuntimeError('EXP262_FINAL_ONCE_PRIVATE_ONLY_REQUIRED')
  if g.get('candidate_source_inventory_SHA256')!=r['candidate_source_inventory_SHA256'] or any(g.get(k)!=r[k] for k in ('task_id','trial_id','policy')):raise RuntimeError('EXP262_FINAL_EXACT_SELECTED_SOURCE_TRIAL_REQUIRED')
  if time.time()>=datetime.datetime.fromisoformat(g['lease_end_UTC']).timestamp() or any(Path(p).exists() for p in g['root_stop_paths']):raise RuntimeError('EXP262_FINAL_LEASE_OR_ROOT_STOP')
  if Path(r['native_output']).resolve()!=H/'final_private_ROOT'/r['trial_id']/r['policy']:raise RuntimeError('EXP262_FINAL_OUTPUT_NAMESPACE')
  if full:
   seal=checked(g['native_source_seal'])
   for p,h in {**seal['sources'],**seal['dependencies'],**seal['public_inputs_SHA256']}.items():
    if sha(p)!=h:raise RuntimeError('EXP262_FINAL_SOURCE_INPUT_DRIFT:'+p)
   for k in ('public_terminal','public_completed','public_parent_stop','frozen_selection','science_T0','selected_business_source','method_contract','current_pressure_public_contract','current_public_scope','Root_current_qualified_partial_start','Root_qualified_runtime_acceptance','original_product_identity'):checked(r[k])
   terminal=checked(r['public_terminal']);public=checked(r['public_completed']);parent=checked(r['public_parent_stop']);source=checked(r['selected_business_source']);selection=checked(r['frozen_selection'])
   hashes={p:hashlib.sha256(t.encode()).hexdigest() for p,t in source.items()}
   if terminal['status']!='COMPLETED' or terminal.get('error') is not None or terminal['final_snapshot']!=selection['selected_snapshot'] or hashes!=selection['candidate_source_sha256'] or digest(hashes)!=r['candidate_source_inventory_SHA256']:raise RuntimeError('EXP262_FINAL_IMMUTABLE_PUBLIC_SELECTION_DRIFT')
   if parent.get('exit_code')!=0 or parent.get('error') is not None or not parent['stop_receipt']['all_owned_descendants_terminated'] or parent['stop_receipt']['job_active_processes_after_termination']!=0:raise RuntimeError('EXP262_FINAL_PUBLIC_PARENT_NOT_CLOSED')
   native=checked({'path':public['public_native_path'],'sha256':public['public_native_SHA256']})
   c=checked(r['method_contract']);nodes=c['goal_nodes']+c['ordinary_nodes']
   if native.get('requested_nodes')!=nodes or not native.get('passed') or not native.get('completed_guarded_coverage') or any(native['pytest']['outcomes'][n]['status']!='passed' for n in nodes):raise RuntimeError('EXP262_FINAL_REAL_PUBLIC_GO4_PASS_REQUIRED')
   if g.get('original_private_manifest')!=r['Root_only_original_isolation_manifest'] or g.get('current_identity_receipt')!=r['original_product_identity'] or g.get('qualified_runtime_policy')!=r['Root_qualified_runtime_acceptance']:raise RuntimeError('EXP262_FINAL_ORIGINAL_PRIVATE_METADATA_RUNTIME_REQUIRED')
   if g.get('current_process_clock_policy')!='ROOT_ORIGINAL_CLOCK_EXPLICITLY_ADMITTED':raise RuntimeError('EXP262_FINAL_ORIGINAL_CURRENT_NATIVE_CLOCK_EXPLICIT_ROOT_ADMISSION_REQUIRED')
  return True

def worker(grant,jobs):
 r=grant.ready;g=grant.value;out=Path(r['native_output']);
 if not helper.parent_member(jobs,g['parent_owned_job_name']):raise RuntimeError('EXP262_FINAL_ROOT_WORKER_NOT_OWN_JOB')
 intent(out/'NATIVE_INTENT_ROOT_ONLY.json',{'UTC':now(),'Root_grant_SHA256':grant.sha256,'selected_inventory':r['candidate_source_inventory_SHA256'],'one_private_native_only_no_rerun':True})
 c=checked(r['current_pressure_public_contract']);state=checked(r['frozen_selection']);source=checked(r['selected_business_source']);identity=checked(r['original_product_identity']);expected=identity['product_identity'];python=Path(c['logical_product_python'])
 if sha(python)!=identity['logical_product_python_SHA256'] or sha(python.parent.parent/'pyvenv.cfg')!=identity['pyvenv_cfg_SHA256'] or sha(expected['actual_OS_image'])!=expected['actual_OS_image_SHA256']:raise RuntimeError('EXP262_FINAL_CURRENT_NATIVE_BINARY_OR_PHYSICAL_IDENTITY_DRIFT')
 active=out/'runtime';repo=active/'repo';repo.mkdir(parents=True,exist_ok=False)
 for rel,text in source.items():
  path=(repo/rel).resolve()
  if not path.is_relative_to(repo.resolve()) or not rel.startswith('moto/') or not rel.endswith('.py') or any(x in ('test','tests','.git') for x in Path(rel).parts):raise RuntimeError('EXP262_FINAL_BUSINESS_SCOPE_ONLY')
  path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(text.encode('utf-8'))
 if {p:sha(repo/p) for p in source}!=state['candidate_source_sha256'] or set(source)!=set(c['c0_business_paths_sha256']):raise RuntimeError('EXP262_FINAL_EXACT_861_BUSINESS_MATERIALIZATION_REQUIRED')
 run=helper.load_original_probe(c);events=[];env=types.SimpleNamespace(run=run,package='moto',record=lambda k,v:events.append({'stage':k,'value':v}));jobs.install(env)
 capacity=module('_exp262_final_original_capacity',H/'SOURCE/native_capacity_v10.py');capacity.NATIVE_TIMEOUT_SECONDS=300;capacity.install(env)
 execute=run.qualify.execute
 def measured(argv,cwd,log,timeout=300,env=None):
  receipt=Path(log).with_name('ACTUAL_PRODUCT_SELF262.json');actual=helper.wrap_native_argv(argv,receipt,grant,expected['actual_OS_image']);value=execute(actual,cwd,log,timeout,env)
  value['actual_product_identity']=helper.verify_measured_identity(value,receipt,expected,grant);value['actual_product_identity_SHA256']=sha(receipt);value['original_semantic_argv']=list(map(str,argv));return value
 run.qualify.execute=measured
 # Root-only private isolation metadata is opened only after true once grant,
 # immutable selection and actual parent STOP checks. No private test body read.
 manifest=checked(r['Root_only_original_isolation_manifest']);nodes=manifest['hidden_preservation_tests']
 if manifest['task_id']!=r['task_id'] or not nodes or len(nodes)!=len(set(nodes)) or digest(nodes)!=g['original_private_nodes_SHA256'] or Path(manifest['frozen_tests']['path']).resolve()!=Path(c['frozen_public_test_root']).resolve():raise RuntimeError('EXP262_ORIGINAL_PRIVATE_SELECTORS_FROZEN_ROOT_REQUIRED')
 scheduler=module('_exp262_final_shared_four',COMMON/'native_four_slots_v5_SOURCE.py');schedule=read(COMMON/'ROOT_COMMON_NATIVE_SCHEDULING_V5_FOUR_SOURCE.json')
 with scheduler.native_lane(schedule['lock_path'],'moto',grant.check,lambda v:events.append({'stage':'V5_four_slots','value':v})):
  grant.check(full=True);remaining=datetime.datetime.fromisoformat(g['lease_end_UTC']).timestamp()-time.time();result=run.probe(active,Path(c['frozen_public_test_root']),nodes,out/'actual_private_ROOT_ONLY',python,'moto',time.monotonic()+min(300,max(.1,remaining)))
 known=bool(result.get('completed_guarded_coverage') and result.get('guard_loaded') and result.get('business_state_unchanged') and result.get('frozen_tests_unchanged') and not result.get('timeout') and result.get('exact_test_coverage') and result.get('requested_nodes')==nodes and result['stop_receipt'].get('all_owned_descendants_terminated') is True)
 if {p:sha(repo/p) for p in source}!=state['candidate_source_sha256']:raise RuntimeError('EXP262_FINAL_PRIVATE_NATIVE_CHANGED_SELECTED_BUSINESS')
 save(out/'ROOT_ONLY_NATIVE_TRANSPORT_EVIDENCE.json',events)
 save(out/'WORKER_COMPLETED_PRIVATE_ROOT_ONLY.json',{'task_id':r['task_id'],'trial_id':r['trial_id'],'policy':r['policy'],'candidate_source_inventory_SHA256':r['candidate_source_inventory_SHA256'],'private_known':known,'private_passed':bool(result.get('passed')) if known else None,'private_native_record':ref(out/'actual_private_ROOT_ONLY/run.json'),'actual_product_identity':result.get('actual_product_identity'),'Root_grant_SHA256':grant.sha256,'private_native_calls':1,'no_private_feedback_to_model_or_later_repeat':True,'model_POST_finance':0})

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',default='final');p.add_argument('--task',default='getmoto__moto-7081');p.add_argument('--root-grant');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if not a.root_grant:print(canonical({'SOURCE_ONLY':True,'default_closed':True,'native_private_model_finance':0}));return
 grant=FinalGrant(a.root_grant);jobs=helper.load_jobs(grant)
 if a.worker:worker(grant,jobs);return
 out=Path(grant.ready['native_output']);helper.supervise(a,grant,out,jobs)
 parent=read(out/'PARENT_TERMINAL249.json');value=read(out/'WORKER_COMPLETED_PRIVATE_ROOT_ONLY.json');value.update(parent_supervision=ref(out/'PARENT_TERMINAL249.json'),all_owned_Job_STOP=parent['stop_receipt'],natural_success=value['private_passed'] if value['private_known'] else None,independent_acceptance_known=value['private_known'],final_completed_UTC=now())
 start=checked(grant.ready['science_T0']);elapsed=time.monotonic()-start['monotonic'];value['elapsed_seconds_from_real_trial_T0']=elapsed;value['fixed_resource_success']=bool(value['natural_success']) if value['private_known'] and elapsed<=1800 else False if elapsed>1800 else None;value['fixed_endpoint_from_same_trajectory']=True
 save(out/'ROOT_FINAL_ACCEPTANCE.json',value);print(canonical({'status':'INDEPENDENT_FINAL_RETURNED_AND_PARENT_STOPPED','Root_only_receipt':str(out/'ROOT_FINAL_ACCEPTANCE.json'),'private_feedback_to_model':False}),flush=True)
if __name__=='__main__':main()

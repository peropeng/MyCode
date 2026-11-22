"""Per-index actual qualification seal; scientific grant remains false."""
import argparse,ast,datetime,sys
sys.dont_write_bytecode=True
from contracts241 import *
from public_v2_241 import AL

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--task',required=True);parser.add_argument('--namespace',default='mechanical_native')
 args=parser.parse_args();base=HERE/'candidate'/args.task;qualified=HERE/args.namespace/args.task
 if (base/'READY_CASE241.json').exists():raise EngineeringUnknown('CASE_READY_ONCE')
 m=read(qualified/'mechanical_receipt.json');stop=read(qualified/'parent_stop_receipt.json')
 if (m.get('actual_initial_goal_completed')!=0 or m.get('actual_initial_goal_blocked')!=5 or m.get('actual_native_public_C0_target_failed') is not False
     or m.get('initial_qualification_v2_observer',{}).get('certificate_sha256')!='51500f02d6d9ee4410fa6e6b05350f43e8fd94fc0a65ce73657e984f59ab9fce'):
  raise EngineeringUnknown('INITIAL_V2_SHARED_C0_OBSERVER_REQUIRED')
 if m.get('actual_generated_scope_version')!=2 or not m.get('all_scope_probe_events_individually_reconciled'):
  raise EngineeringUnknown('ACTUAL_SCOPE_V2_PROBE_EVENT_RECONCILIATION_REQUIRED')
 if (m['status']!='PASS_ACTUAL_RUNTIME_MECHANICAL_NOT_METHOD_SUCCESS' or m['model_API_private_ledger_writes']!=0
  or not all(m.get(k) for k in ('actual_initial_goal_collection_blocked','actual_ordinary_C0_passed','actual_transport_constructor',
   'actual_single_atomic_wrapper_chain','actual_finance_readonly_validate','actual_artifact_scope_inside_write_and_outside_rejection','exact_C0_unchanged'))
  or stop['exit_code']!=0 or stop['timeout'] or not all(stop['stop_receipt'].get(k) for k in ('root_stopped','own_Job_empty_before_close','descendants_stopped'))):
  raise EngineeringUnknown('ACTUAL_QUALIFICATION_OR_STOP_MISSING')
 c=read(qualified/'public_contract_physical_qualified.json');old=read(base/'public_contract.json')
 a=dict(c);b=dict(old);a.pop('physical_product_python_expected');b.pop('physical_product_python_expected')
 if a!=b:raise EngineeringUnknown('PUBLIC_CONTRACT_CHANGED')
 save(base/'public_contract.json',c);p=read(base/'protocol.json')
 p.update(mechanical241={'receipt':str(qualified/'mechanical_receipt.json'),'sha256':sha(qualified/'mechanical_receipt.json'),
  'parent_stop':str(qualified/'parent_stop_receipt.json'),'parent_stop_sha256':sha(qualified/'parent_stop_receipt.json')},
  first_request_bound=m['first_body_bounds'],first_body_sha256=m['complete_first_body_sha256'],
  original_method_core_sha256=sha(AL/'agentless178.py'),mechanical_only_actual_runtime_PASS=True)
 save(base/'protocol.json',p)
 save(base/'first_body.json',{'body':m['complete_unclipped_first_body'],'body_sha256':m['complete_first_body_sha256'],
  'bounds':m['first_body_bounds'],'actual_original_author_first_stage_no_reader_tools':True})
 prior=read(base/'source_seal.json');sources=prior['sources'];inputs=prior['inputs']
 for f in HERE.glob('*.py'):ast.parse(f.read_text('utf-8-sig'));sources[str(f)]=sha(f)
 sources.update(m['actual_controller_dependencies'])
 profiles={}
 for f in (qualified/'owned_flow').glob('**/actual_runtime_profile.json'):
  v=read(f);profiles[str(f)]=v;sources[str(f)]=sha(f)
  for info in v['actual_modules'].values():sources[info['path']]=info['sha256']
 for f in [qualified/'mechanical_receipt.json',qualified/'parent_stop_receipt.json',qualified/'public_contract_physical_qualified.json']:
  sources[str(f)]=sha(f)
 for f in [qualified/'scope_v2_receipt.json',Path(m['actual_scope_v2_probe']['event_log'])]:sources[str(f)]=sha(f)
 save(base/'RUNTIME_QUALIFICATION241.json',{'task_id':args.task,'actual_profiles':profiles,
  'physical_product':m['product_identity'],'no_generic_CP312_product_injection':p['product_dependency_paths']==[],
  'same_public_ref_python_frozen_tests':True,'qualification_is_not_method_success':True})
 for path in list(inputs):
  if inside(path,HERE):inputs[path]=sha(path)
 for f in [base/'first_body.json',base/'RUNTIME_QUALIFICATION241.json']:inputs[str(f)]=sha(f)
 for path,h in {**sources,**inputs}.items():
  if sha(path)!=h:raise EngineeringUnknown('ACTUAL_SOURCE_INPUT_DRIFT '+path)
 seal={'schema':'Agentless241-source-input-seal/1','author_pin':SOURCE_PIN,'sources':sources,'inputs':inputs,'prepared_only':True}
 save(base/'source_seal.json',seal);g=read(base/'root_grant.template.json')
 g.update(protocol_sha256=digest(p),protocol_raw_sha256=sha(base/'protocol.json'),source_seal_sha256=digest(seal),
  neutral_mechanical_qualification_sha256=sha(qualified/'mechanical_receipt.json'),neutral_parent_stop_sha256=sha(qualified/'parent_stop_receipt.json'),
  parent_controller_job_qualified=True,controller_physical_python_expected=m['controller_identity']['actual_OS_image_GetModuleFileName'],
  product_physical_python_expected=m['product_identity']['actual_OS_image_GetModuleFileName'])
 save(base/'root_grant.template.json',g)
 argv=[g['controller_physical_python_expected'],'-X','utf8','-B',str(HERE/'supervisor_initial_v2_241.py')]
 for name,filename in [('protocol','protocol.json'),('grant','root_grant.actual.json'),('seal','source_seal.json'),('contract','public_contract.json')]:
  argv+=['--'+name,str(base/filename)]
 value={'schema':'Agentless241-READY-per-natural-index-false-grant/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'task_id':args.task,'natural_index':p['natural_index'],'phase':FINANCE_PHASE,'source_count':len(sources),
  'protocol':str(base/'protocol.json'),'false_grant':str(base/'root_grant.template.json'),'public_contract':str(base/'public_contract.json'),
  'source_seal':str(base/'source_seal.json'),'source_seal_sha256':digest(seal),'supervisor_argv':argv,
  'actual_mechanical_elapsed_seconds':stop['seconds'],'first_body_bounds':m['first_body_bounds'],
  'generated_scope_version':2,'actual_scope_probe_receipt':str(qualified/'scope_v2_receipt.json'),
  'all_actual_scope_events_individually_reconciled':True,
  'all_qualification_jobs_STOP':True,'original_core_sha256':sha(AL/'agentless178.py'),'all_science_grants_false':True,
  'POST_private_ledger_writes':0,'pilot_oldMain_results_not_merged':True}
 save(base/'READY_CASE241.json',value)
 print(canonical({k:value[k] for k in ('task_id','natural_index','source_count','first_body_bounds','all_science_grants_false')}))
if __name__=='__main__':main()

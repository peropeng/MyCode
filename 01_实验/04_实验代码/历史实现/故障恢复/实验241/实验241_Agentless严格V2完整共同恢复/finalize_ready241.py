"""Freeze actual qualification/body/runtime sources; all scientific grants false."""
import ast,datetime,sys
from decimal import Decimal
from pathlib import Path
sys.dont_write_bytecode=True
from contracts241 import *
from public_v2_241 import AL

TASKS=['Project-MONAI__MONAI-2238','Project-MONAI__MONAI-5093']
QUAL={'Project-MONAI__MONAI-2238':'mechanical_single_fix_verified','Project-MONAI__MONAI-5093':'mechanical_native'}
def main():
 if (HERE/'READY_ROOT241.json').exists():raise EngineeringUnknown('READY_FREEZE_ONLY_ONCE')
 author=read(HERE/'AUTHOR_SOURCE_MANIFEST241.json')
 for path,h in author['sources'].items():
  if sha(path)!=h:raise EngineeringUnknown('ORIGINAL_AUTHOR_SOURCE_DRIFT')
 for p in HERE.glob('*.py'):ast.parse(p.read_text('utf-8-sig'))
 sources=dict(read(HERE/'candidate'/TASKS[0]/'source_seal.json')['sources'])
 sources.update({str(p):sha(p) for p in HERE.glob('*.py')})
 for name in ('resume_transport.py','continuous_core_v2.py'):
  p=ROOT/'工作区/1009-research-resume/finance'/name;sources[str(p)]=sha(p)
 prepared=[]
 for task in TASKS:
  base=HERE/'candidate'/task;qualified=HERE/QUAL[task]/task;m=read(qualified/'mechanical_receipt.json');stop=read(qualified/'parent_stop_receipt.json')
  if (m['status']!='PASS_ACTUAL_RUNTIME_MECHANICAL_NOT_METHOD_SUCCESS' or m['model_API_private_ledger_writes']!=0
      or not all(m.get(k) for k in ('actual_native_public_C0_target_failed','actual_ordinary_C0_passed','actual_transport_constructor',
       'actual_single_atomic_wrapper_chain','actual_finance_readonly_validate','actual_artifact_scope_inside_write_and_outside_rejection','exact_C0_unchanged'))
      or stop['exit_code']!=0 or stop['timeout']
      or not all(stop['stop_receipt'].get(k) for k in ('root_stopped','own_Job_empty_before_close','descendants_stopped'))):
   raise EngineeringUnknown('ACTUAL_RUNTIME_QUALIFICATION_OR_STOP_MISSING')
  c=read(qualified/'public_contract_physical_qualified.json');old=read(base/'public_contract.json')
  a=dict(c);b=dict(old);a.pop('physical_product_python_expected');b.pop('physical_product_python_expected')
  if a!=b:raise EngineeringUnknown('PUBLIC_CONTRACT_CHANGED')
  save(base/'public_contract.json',c);p=read(base/'protocol.json')
  p.update(mechanical241={'receipt':str(qualified/'mechanical_receipt.json'),'sha256':sha(qualified/'mechanical_receipt.json'),
   'parent_stop':str(qualified/'parent_stop_receipt.json'),'parent_stop_sha256':sha(qualified/'parent_stop_receipt.json')},
   original_method_core_sha256=sha(AL/'agentless178.py'),first_request_bound=m['first_body_bounds'],
   first_body_sha256=m['complete_first_body_sha256'],mechanical_only_actual_runtime_PASS=True)
  save(base/'protocol.json',p)
  save(base/'first_body.json',{'body':m['complete_unclipped_first_body'],'body_sha256':m['complete_first_body_sha256'],
   'bounds':m['first_body_bounds'],'captured_from_actual_unchanged_author_stage_prompt':True,'no_reader_tools':True})
  sources.update(m['actual_controller_dependencies']);sources.update(c['harness_sources'])
  for name in ('mechanical_receipt.json','parent_stop_receipt.json','public_contract_physical_qualified.json'):
   sources[str(qualified/name)]=sha(qualified/name)
  prepared.append((task,base,p,c,m,stop))
 source_manifest={'schema':'Agentless241-actual-source-manifest/1','official_pin':SOURCE_PIN,'author_core_unchanged':True,
  'sources':sources,'own_sources':{str(p):sha(p) for p in HERE.glob('*.py')},'actual_mechanical_and_actual_imported_dependencies_sealed':True}
 for path,h in sources.items():
  if sha(path)!=h:raise EngineeringUnknown('SEALED_SOURCE_DRIFT '+path)
 save(HERE/'SOURCE_MANIFEST241.json',source_manifest);cases=[]
 for task,base,p,c,m,stop in prepared:
  prior=read(base/'source_seal.json');inputs=dict(prior['inputs'])
  for path in list(inputs):
   if inside(path,HERE):inputs[path]=sha(path)
   elif sha(path)!=inputs[path]:raise EngineeringUnknown('SHARED_PUBLIC_INPUT_DRIFT')
  for path in [base/'first_body.json',HERE/'SOURCE_MANIFEST241.json']:
   inputs[str(path)]=sha(path)
  seal={'schema':'Agentless241-source-input-seal/1','author_pin':SOURCE_PIN,'sources':sources,'inputs':inputs,'prepared_only':True}
  save(base/'source_seal.json',seal);g=read(base/'root_grant.template.json')
  g.update(protocol_sha256=digest(p),protocol_raw_sha256=sha(base/'protocol.json'),source_seal_sha256=digest(seal),
   neutral_mechanical_qualification_sha256=sha(Path(p['mechanical241']['receipt'])),neutral_parent_stop_sha256=sha(Path(p['mechanical241']['parent_stop'])),
   parent_controller_job_qualified=True,controller_physical_python_expected=m['controller_identity']['actual_OS_image_GetModuleFileName'],
   product_physical_python_expected=m['product_identity']['actual_OS_image_GetModuleFileName'])
  save(base/'root_grant.template.json',g)
  argv=[g['controller_physical_python_expected'],'-X','utf8','-B',str(HERE/'supervisor241.py')]
  for name in ('protocol','grant','seal','contract'):
   path=base/{'protocol':'protocol.json','grant':'root_grant.actual.json','seal':'source_seal.json','contract':'public_contract.json'}[name]
   argv+=['--'+name,str(path)]
  cases.append({'task_id':task,'protocol':str(base/'protocol.json'),'false_grant':str(base/'root_grant.template.json'),
   'public_contract':str(base/'public_contract.json'),'source_seal':str(base/'source_seal.json'),'source_seal_sha256':digest(seal),
   'supervisor_argv':argv,'new_actual_mechanical_elapsed_seconds':stop['seconds'],'first_body_bounds':m['first_body_bounds'],
   'complete_first_request_bytes':len(canonical(m['complete_unclipped_first_body']).encode()),'original_core_SHA256':sha(AL/'agentless178.py'),
   'mechanical_root_count':m['native_roots'],'actual_product_reproduction_and_ordinary_and_dense':True,'all_qualification_jobs_STOP':True})
 first_sum=sum(Decimal(c['first_body_bounds']['global_reserve']) for c in cases)
 config=read(HERE/'finance_config241.json')
 save(HERE/'READY_ROOT241.json',{'schema':'Agentless241-READY-false-science-grant/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'experiment':241,'write_root':str(HERE),'phase':FINANCE_PHASE,'phase_cap_CNY':config['phases'][FINANCE_PHASE]['cap_CNY'],
  'cases':cases,'source_count':len(sources),'first_both_request_peak_bound_sum_CNY':str(first_sum),'full_method_worst_cost_guaranteed':False,
  'max_author_model_requests_without_added_reader':16,'generic_complete_common_budget_upper_CNY':'33.947648',
  'maximum_common_budget':read(cases[0]['protocol'])['budget'],'old_complete_AL6of7_main21_results_retained':True,
  'original_AL4L4P4T_no_core_prompt_parser_vote_normalization_change':True,'all_model_input_history_and_edits_same_exact_pack':True,
  'source_public_model_only_no_private_nodes':True,'science_POST':0,'private':0,'finance_ledger_writes':0,
  'scientific_grants_false':True,'after_root_release_entry':'exact absolute supervisor_argv; automatic evaluator process only after author immutable selection and own Job STOP; same original900',
  'one_mechanical_repair_window':{'first_error_utc':'2026-10-09T16:17:29.312451+00:00','last_FIX_PASS_before_first_plus300':True,
   'failures_preserved':['mechanical_native/Project-MONAI__MONAI-2238','mechanical_single_fix/Project-MONAI__MONAI-2238','mechanical_single_fix_final/Project-MONAI__MONAI-2238']}})
 print(canonical({'READY_ROOT241':str(HERE/'READY_ROOT241.json'),'source_count':len(sources),'first_sum_CNY':str(first_sum),'science_grants_false':True}))
if __name__=='__main__':main()

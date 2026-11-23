"""One independent mechanical continuation, pending explicit root release."""
from common166 import *
import copy,traceback
from decimal import Decimal
from common_environment224 import CommonEnvironment
from resume_prefix224 import ExactPublicPrefix,install
import bootstrap224
def main():
 release=E/'mechanical_release224.json'
 assert release.exists() and read(release).get('root_authorized'),'NO_MECHANICAL_CONTINUATION_POST_UNTIL_ROOT_RELEASE'
 refs={r['task_id']:r for r in read(E/'data/selected_task_bindings.json')['tasks']};method='AGENTLESS_FSE2025_4L4P4T_FLASH'
 original_seal=read(E/'runtime_seal224.json')
 for p,h in original_seal['inputs'].items():assert sha(p)==h,'C0_INPUT_OR_ORIGINAL_SOURCE_CHANGED '+p
 save(E/'mechanical_v2/runtime_seal224_v2.json',{'at_utc':now(),'sources':{str(p):sha(p) for p in E.glob('*.py')},'original_runtime_seal_sha256':sha(E/'runtime_seal224.json'),'inputs':original_seal['inputs'],'only_reader_argument_error_transport_repaired':True,'same_original_seed_temperatures_core_C0_and_budget':True,'old_UNKNOWN_and_costs_retained':True,'root_release':str(release),'root_release_sha256':sha(release)})
 for tid in read(E/'protocol224.json')['pilot_ids']:
  ref=copy.deepcopy(refs[tid]);ref['_output_namespace']='mechanical_v2/recovery';ref['_native_namespace']='mechanical_v2/native_active';out=E/ref['_output_namespace']/tid/method
  assert not (out/'result.json').exists(),'MECHANICAL_CONTINUATION_ALREADY_OBSERVED_NO_SECOND_RETRY'
  original=E/'recovery'/tid/method;old=read(original/'result.json');assert old['status']=='ENGINEERING_UNKNOWN' and old['error']['message']=='UNKNOWN_OR_NONPUBLIC_FAILURE_NODE'
  bank=ExactPublicPrefix(original);uninstall=install(bank);env=None
  try:
   env=CommonEnvironment(ref,method);env.finance_phase='Round2320Pilot';result=sys.modules['agentless178'].run(env);full=env.finalize(result)
  except Exception as error:full={'task_id':tid,'method':method,'status':'ENGINEERING_UNKNOWN','success':None,'error':{'type':type(error).__name__,'message':str(error)},'traceback':traceback.format_exc(),'runtime_core':{},'LLM_calls':getattr(env,'calls',0),'public_native_calls':getattr(env,'native_calls',0),'hidden_acceptance_calls':0}
  finally:uninstall()
  receipts=[read(p) for p in out.glob('llm/*_finance_receipt.json')];settled=[r for r in receipts if r['status']=='SETTLED'];new_cost=sum((Decimal(r['usage_peak_cost_CNY']) for r in settled),Decimal(0))
  full.update(scientific_method='AGENTLESS_FSE2025',stratum=ref['stratum'],mechanical_lineage_from=str(original/'result.json'),old_incomplete_engineering_observation_retained=True,exact_prefix_reused_calls=len(bank.reused),reused_original_finance_ordinals=[r['original_finance_ordinal'] for r in bank.reused],new_paid_API=len(settled),new_fees_CNY=str(new_cost),fees_CNY=str(Decimal(old['fees_CNY'])+new_cost),cost_counting='Original prefix costs plus new settled calls, original ledger charged once; source UNKNOWN remains diagnostic only.',finance_phase='Round2320Pilot',complete_core=bool(full.get('runtime_core',{}).get('complete')))
  save(out/'result.json',full);append(E/'mechanical_v2/completed224_v2.jsonl',{k:full.get(k) for k in ('task_id','status','success','complete_core','exact_prefix_reused_calls','new_paid_API','new_fees_CNY','fees_CNY','LLM_calls','public_native_calls','hidden_acceptance_calls')});print(canonical({k:full.get(k) for k in ('task_id','status','success','complete_core','exact_prefix_reused_calls','new_paid_API','new_fees_CNY','fees_CNY')}),flush=True)
 save(E/'mechanical_v2/finished224_v2.json',{'at_utc':now(),'same_two_pilot_cases_once_lineage_complete':True,'no_automatic_main_unlock':True})
if __name__=='__main__':main()

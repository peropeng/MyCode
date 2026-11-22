"""Fixed23 queue; initial2 same-config pilot, main only after root unlock."""
from common166 import *
import copy,traceback
from decimal import Decimal
from common_environment224 import CommonEnvironment
import bootstrap224
LABELS={'AGENTLESS_FSE2025':'AGENTLESS_FSE2025_4L4P4T_FLASH','OURS_G153_PROGRESSIVE_SEMANTIC':'G_PROGRESSIVE_SEMANTIC_FLASH'}
def prepare_seal():
 p=authorization();data=read(E/'data/selected_task_bindings.json');order=data['task_order'];assert order==p['task_order'] and len(order)==len(set(order))==23
 sources={str(x):sha(x) for x in E.glob('*.py')};sources.update(bootstrap224.SOURCES)
 for path in (TRANSPORT,ROOT/'工作区/1008-2320-baseline-main/resource/round_finance_config.json',E150/'common150.py',ROOT/'工作区/1002-exp129-expanded-baselines/实验/实验129_扩展基线与恢复证据/executor/run.py',ROOT/'实验/实验127_完整恢复方法可行性/stage2/recovery.py'):sources[str(path)]=sha(path)
 inputs={str(E/'data/selected_task_bindings.json'):sha(E/'data/selected_task_bindings.json'),str(E/'data/public_inputs.jsonl'):sha(E/'data/public_inputs.jsonl'),str(E/'data/common_spec224.json'):sha(E/'data/common_spec224.json'),str(TIME_AUTHORITY):sha(TIME_AUTHORITY)}
 for r in data['tasks']:
  seal=read(r['binding_seal']);assert sha(r['binding_seal'])==r['ready_sha256'];inputs[r['binding_seal']]=r['ready_sha256'];inputs.update(seal['sha256'])
  if r.get('G_frozen_plan'):inputs[r['G_frozen_plan']]=sha(r['G_frozen_plan'])
 for path,h in inputs.items():assert sha(path)==h,'FROZEN_INPUT_DRIFT '+path
 seal={'at_utc':now(),'sources':sources,'inputs':inputs,'fixed_task_order':order,'methods':list(LABELS),'original_cores_readonly':True,'pilot_2_in_main_once':True,'no_reverse_random':True}
 save(E/'runtime_seal224.json',seal);return seal
def check_seal(seal):
 for path,h in {**seal['sources'],**seal['inputs']}.items():assert sha(path)==h,'FROZEN_SOURCE_OR_INPUT_DRIFT '+path
def one(ref,label,phase):
 out=E/'recovery'/ref['task_id']/LABELS[label]
 if (out/'result.json').exists():raise RuntimeError('FIXED_FLOW_ALREADY_OBSERVED_NO_RERUN')
 env=None
 try:
  env=CommonEnvironment(copy.deepcopy(ref),LABELS[label]);env.finance_phase=phase
  if label=='AGENTLESS_FSE2025':result=sys.modules['agentless178'].run(env)
  else:result=sys.modules['ranked_repair178'].run(env)
  full=env.finalize(result)
 except Exception as error:
  full={'task_id':ref['task_id'],'method':LABELS[label],'status':'ENGINEERING_UNKNOWN','success':None,'error':{'type':type(error).__name__,'message':str(error)},'traceback':traceback.format_exc(),'LLM_calls':getattr(env,'calls',0),'output_tokens':getattr(env,'out_tokens',0),'public_native_calls':getattr(env,'native_calls',0),'hidden_acceptance_calls':0,'runtime_core':{},'stage_ledger':getattr(env,'stage_ledger',[])}
 receipts=[read(p) for p in out.glob('llm/*_finance_receipt.json')];settled=[r for r in receipts if r['status']=='SETTLED']
 full.update(scientific_method=label,stratum=ref['stratum'],finance_phase=phase,paid_API=len(settled),fees_CNY=str(sum((Decimal(r['usage_peak_cost_CNY']) for r in settled),Decimal(0))),common_spec_sha256=sha(E/'data/common_spec224.json'),first_pass_can_count_main_once=True)
 save(out/'result.json',full);save(E/'slots'/ref['task_id']/(label+'.json'),full)
 brief={k:full.get(k) for k in ('task_id','scientific_method','stratum','status','success','fees_CNY','paid_API','LLM_calls','public_native_calls','hidden_acceptance_calls')};brief['complete_core']=bool(full.get('runtime_core',{}).get('complete'));append(E/'completed224.jsonl',brief);print(canonical(brief),flush=True);return full
def main():
 protocol=authorization();seal=prepare_seal();data=read(E/'data/selected_task_bindings.json');refs={r['task_id']:r for r in data['tasks']};saved=[]
 for tid in protocol['pilot_ids']:
  for label in LABELS:
   check_seal(seal);saved.append(one(refs[tid],label,'Round2320Pilot'))
 save(E/'pilot_completed224.json',{'at_utc':now(),'status':'ACTUAL_FIRST2_FOUR_FLOWS_OBSERVED','flows':len(saved),'complete_core':sum(bool(r.get('runtime_core',{}).get('complete')) for r in saved),'known_successes':sum(r.get('success') is True for r in saved),'unknown':sum(r.get('success') is None for r in saved),'no_automatic_Main_unlock':True})
 status('PILOT_COMPLETE_WAIT_ROOT_MAIN_UNLOCK',completed=len(saved))
if __name__=='__main__':main()

"""One fully original author4L4P4T run, then STOP before separate evaluator."""
import argparse,traceback
from contracts241 import *
from environment241 import Environment241

def main():
 parser=argparse.ArgumentParser()
 for name in ('protocol','grant','seal','contract'):parser.add_argument('--'+name,required=True)
 args=parser.parse_args();env=Environment241(args.protocol,args.grant,args.seal,args.contract)
 try:
  env.initialize();raw=env.core.run(env)
  save(env.output_root/'author_raw_result.json',raw,scope=env.output_root)
  if env.unknown:result={**raw,'status':'ENGINEERING_UNKNOWN','success':None,'unknown':env.unknown}
  elif env.budget_end or raw.get('status')=='BUDGET_CENSORED':
   result={**raw,'status':'BUDGET_CENSORED','success':None,'budget_end':env.budget_end}
  elif raw.get('engineering_outcome_unknown') or raw.get('status') in ('ENGINEERING_UNKNOWN','CONTEXT_UNKNOWN','NOT_RUN'):
   result={**raw,'success':None}
  else:result=env.finalize_selection(raw)
 except DeclaredBudgetEnd as error:
  env.latch_unknown(error,'AUTHOR_BUDGET_EXIT');result={'status':'BUDGET_CENSORED','success':None,'budget_end':env.budget_end,'runtime_core':{'complete':False}}
 except BaseException as error:
  env.latch_unknown(error,'AUTHOR_CONTROLLER_EXIT');result={'status':'ENGINEERING_UNKNOWN','success':None,'unknown':env.unknown,
   'traceback':traceback.format_exc(),'runtime_core':{'complete':False}}
 result.update(task_id=env.task_id,method=METHOD,experiment=241,version='STRICT224_V2_AUTHOR_DIRECT_PUBLICPACK_NEW_DEPLOYMENT241',
  historically_exposed_task=True,LLM_calls=env.calls,output_tokens=env.out_tokens,native_roots=env.native_roots,native_root_kinds=env.native_root_kinds,
  product_test_roots=sum(env.native_root_kinds.get(k,0) for k in ('pytest','generated','generated_pytest','coverage')),
  all_OS_native_roots=env.native_roots,product_native_roots=sum(env.native_root_kinds.get(k,0) for k in ('pytest','generated','generated_pytest','coverage')),
  hidden_acceptance_calls=0,author_core_sha256=sha(__import__('public_v2_241').AL/'agentless178.py'),author_algorithm_unchanged=True,
  old224_results_not_spliced=True,no_extra_reader_selfloop=True,selected_before_private=bool((env.output_root/'immutable_selection.json').exists()))
 save(env.output_root/'result.json',result,scope=env.output_root)
 print(canonical({k:result.get(k) for k in ('task_id','status','success','LLM_calls','output_tokens','native_roots','runtime_core')}))
if __name__=='__main__':main()

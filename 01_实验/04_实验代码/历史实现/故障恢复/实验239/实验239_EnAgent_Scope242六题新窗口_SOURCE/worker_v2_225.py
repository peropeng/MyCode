"""One independent full EnAgent task; private observer only after selection."""
from common166 import *
import argparse,asyncio,copy,traceback
from decimal import Decimal
PEER=ROOT/'工作区/1008-2320-exp224-flash-common/实验/实验224_二十三题Flash完整共同恢复比较'
OLD175=ROOT/'工作区/1008-exp175-enagent-feasibility/实验/实验175_EnAgent正式论文完整小试'
sys.path.append(str(PEER))
from common_environment224 import CommonEnvironment,TOOLS
import bootstrap224
bootstrap224.bind_namespace(E)
from owner225 import Bridge,ShellOwner,CERT
from bridge_v2_225 import Bridge
from backend_v2_225 import Transport
import enagent_gitbash_shim as shim
import controller225
from budget_policy225 import classify as classify_termination
METHOD='ENAGENT_ICSE2026_N3_FLASH_SCOPE242'
from v2_control225 import verify as verify_v2,load_pack,VERSION,V


def add_shared_readers(core,bridge):
 class Reader(core.Tool):
  name=''
  def get_name(self):return self.name
  def get_description(self):return next(t['function']['description'] for t in TOOLS if t['function']['name']==self.name)
  def get_parameters(self):
   definition=next(t['function']['parameters'] for t in TOOLS if t['function']['name']==self.name)
   return [core.NS.ToolParameter(name=k,type=v['type'],description=k,required=k in definition.get('required',[])) for k,v in definition['properties'].items()]
  async def execute(self,args):
   root=core.current().root
   try:
    args={k:v for k,v in args.items() if v is not None}
    if self.name=='read_current_source':
     path=args['path'].removeprefix('/workspace/repo/').removeprefix('repo/')
     _,physical,rel=bridge._path(root,path)
     if not bridge._business(rel):raise ValueError('NONBUSINESS_OR_PRIVATE_SOURCE')
     text=physical.read_text('utf-8');rows=text.splitlines(keepends=True);start=args.get('start_line',1);end=args.get('end_line',len(rows))
     if type(start)!=int or type(end)!=int or start<1 or end<start or end>len(rows):raise ValueError('INVALID_EXPLICIT_RANGE')
     value={'path':rel,'start_line':start,'end_line':end,'total_lines':len(rows),'complete_requested_text':''.join(rows[start-1:end]),'whole_source_sha256':hashlib.sha256(text.encode()).hexdigest(),'no_silent_clipping':True}
    elif self.name=='list_current_sources':value={'paths':sorted(bridge._clone_business(root)),'complete':True}
    else:value=bridge.env.reader_call(self.name,args)
    bridge.env.record('actual_shared_public_reader225',{'name':self.name,'arguments':copy.deepcopy(args),'output_sha256':digest(value),'current_actor_source':True})
    return core.ToolExecResult(output=canonical(value),error_code=0)
   except (ValueError,OSError) as exc:return core.ToolExecResult(error=str(exc),error_code=1)
 for name in ('read_full_failure','read_current_source','list_current_sources','read_public_history'):
  cls=type('Shared_'+name,(Reader,),{'name':name});core.NS.tools_registry[name]=cls
 def parse(answer,finish_reason,session):
  names={'str_replace_based_edit_tool','bash','read_full_failure','read_current_source','list_current_sources','read_public_history'}
  tools=[core.NS.tools_registry[name](model_provider='openai') for name in names]
  results=asyncio.run(core.ToolExecutor(tools).sequential_tool_call(answer.tool_calls or []))
  if not results:raise RuntimeError('SELECTOR_NEITHER_VALID_SELECTION_NOR_TOOL_CALL')
  return [core.LLMMessage(role='user',content=r.result or r.error or '',tool_result=r) for r in results]
 core.NS.parse_tool_response=parse
 original_selector_init=core.SelectorAgent.__init__
 def selector_init(self,**kwargs):
  original_selector_init(self,**kwargs)
  self.tools.extend(core.NS.tools_registry[name](model_provider='openai') for name in ('read_full_failure','read_current_source','list_current_sources','read_public_history'))
 core.SelectorAgent.__init__=selector_init

def run(task_id,phase):
 protocol=verify_v2(task_id,phase);refs={r['task_id']:r for r in read(PEER/'data/selected_task_bindings.json')['tasks']}
 ref=copy.deepcopy(refs[task_id]);ref['_output_namespace']=protocol['output_namespace'];ref['_native_namespace']=protocol['native_namespace']
 pub,pack,pack_ref=load_pack(task_id)
 if ref['input_digest']!=pack_ref['input_digest']:raise RuntimeError('V2_CURRENT_C0_BINDING_DIFFERS_FROM_SHARED_PACK')
 out=E/ref['_output_namespace']/task_id/METHOD;out.mkdir(parents=True,exist_ok=True)
 if (out/'audited_result.json').exists():raise RuntimeError('NO_REPEATED_ACTUAL_FLOW')
 from winjob225 import self_identity
 parent_job=os.environ.get('EXP225_V2_PARENT_JOB')
 if not parent_job:raise RuntimeError('V2_WORKER_REQUIRES_OWN_SUPERVISOR_PARENT_JOB')
 save(out/'worker_started.json',{'at_utc':now(),'PID':os.getpid(),'phase':phase,'task_id':task_id,'method':METHOD,'actual_own_parent_Job_identity':self_identity(parent_job)})
 env=None;bridge=None;owner=None;core_result=None
 try:
  env=CommonEnvironment(ref,METHOD);env.finance_phase=phase
  from native_guard_compat225 import install as install_generated_guard
  install_generated_guard(env)
  limits=protocol['budget'];env.deadline=min(env.started+limits['flow_wall_seconds'],env.started+remaining());env.search_deadline=env.deadline-limits.get('final_reserve_seconds',90)
  core=module('exp225_frozen_enagent',OLD175/'enagent_native.py')
  bridge=Bridge(env);owner=ShellOwner(bridge)
  shim.install(core,command_guard=bridge.command_guard,shell_launcher=owner.launch,record=lambda value:env.record('source_Git_Bash_deployment225',value),product_python=lambda root:env._paths['python'],timeout=limits.get('shell_timeout_seconds',45),native_command=bridge.native_command,path_map=bridge.path_map,neutral_output=bridge.neutral)
  add_shared_readers(core,bridge)
  initial=bridge.export();business=sorted(bridge.initial)
  from actor_tool_contract_v3 import ACTOR_TOOL_CONTRACT
  issue=pub.render(pack)+'\n'+ACTOR_TOOL_CONTRACT+'\nResolve the observed current public failure and preserve already passing ordinary behavior. The working repository is /workspace/repo. Complete business source is available through the original author tools and common readers. Original tests are observer-owned; run only declared public nodes or your own generated scripts.'
  env.record('V2_same_direct_public_pack225',{'input_version':VERSION,'pack_sha256':pack_ref['sha256'],'semantic_sha256':pack_ref['semantic_sha256'],'registry_sha256':protocol['shared_registry_sha256'],'full_original_public_history_materialized':True,'V1_candidates_responses_not_reused':True})

  spec={'ensemble_size':int(limits['enagent_ensemble_size']),'initial_repo':str(initial),'business_paths':business,'business_sha256':core.digest(initial,business),'protected_paths':[CERT],'public_test_ids':list(env.public_regression_nodes),'issue':issue,'model':'deepseek-flash','temperature':.7,'selector_temperature':.2,'coder_max_steps':limits['enagent_coder_max_steps'],'selector_max_turn':limits['enagent_selector_max_turn']}
  save(out/'frozen_public_spec.json',spec)
  save(out/'source_receipt225.json',{'core_mapping':core.mapping(),'parent_mapping_N3_description_historical_not_runtime':True,'actual_wrapper_configuration':{'N':int(limits['enagent_ensemble_size']),'coder_max_steps':limits['enagent_coder_max_steps'],'selector_vote_max':int(limits['enagent_ensemble_size']),'selector_max_turn':limits['enagent_selector_max_turn']},'shim_sha256':sha(E/'enagent_gitbash_shim.py'),'controller_sha256':sha(E/'controller225.py'),'backend_sha256':sha(E/'backend225.py'),'owner_sha256':sha(E/'owner225.py'),'common_environment_sha256':sha(PEER/'common_environment224.py'),'common_business_projection_only':True,'original_oracle_keys_forbidden':True,'core_temperatures':{'coder':.7,'tester':0.,'selector':.2}})
  env.flow_configuration_sealed=True
  work=bridge.owned/'w'
  core_result=controller225.run(core,spec,work,lambda stage,index,root:Transport(env,stage,index,root,bridge),bridge)
  final=bridge.snapshot_clone(work/('coder_'+str(core_result['selected_candidate_id'])),'original_EnAgent_selected_patch')
  env.select(final,{'selected_candidate_id':core_result['selected_candidate_id'],'actual_votes':core_result['actual_votes'],'private_used':False})
  result={'status':'COMPLETED','method':METHOD,'final_snapshot':final,'enagent_core_result':core_result,'runtime_core':{'complete':True,'actual_independent_generators':int(limits['enagent_ensemble_size']),'actual_nonempty_candidates':core_result['generated_candidates'],'actual_votes':core_result['actual_votes'],'retained_public_regressions':core_result['retained_public_regressions'],'unique_after_prune':core_result['unique_after_prune']}}
  full=env.finalize(result)
 except Exception as exc:
  error={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()};text=error['type']+' '+error['message']
  termination=classify_termination(exc,env,protocol['budget'],no_new_epoch=NO_TEST,hard_epoch=DEADLINE)
  semantic=isinstance(exc,controller225.NormalGenerationFailure)
  if semantic:termination={'status':'MODEL_SEMANTIC_FAILURE','success':False,'stop_queue':False,'evaluation_status':'KNOWN_FAIL','budget_scope':'NORMAL_THREE_GENERATORS_EMPTY_POOL'}
  full={'task_id':task_id,'method':METHOD,**termination,'error':error,'runtime_core':{'complete':False,'actual_partial_core':core_result},'public_acceptance_known':False,'final_hidden_known':False,'hidden_acceptance_calls':0,'LLM_calls':getattr(env,'calls',0),'output_tokens':getattr(env,'out_tokens',0),'public_native_calls':getattr(env,'native_calls',0),'partial_generations_retained':True,'private_not_run_for_incomplete_controller':True}
  if isinstance(exc,controller225.NormalGenerationFailure):
   summary=read(work/'generation_summary.json')
   full['runtime_core']={'complete':summary['actual_independent_attempts']==int(limits['enagent_ensemble_size']),'actual_independent_generators':summary['actual_independent_attempts'],'termination':'ORIGINAL_EMPTY_POOL_AFTER_CONFIGURED_N','tester_and_selector_not_reached_no_candidates':True,'generation_rows':summary['rows']}
  save(out/'failed_before_final_acceptance.json',full)
 finally:
  if owner:owner.close()
 receipts=[read(f) for f in out.glob('llm/*_finance_receipt.json')]
 fees=sum((Decimal(r['usage_peak_cost_CNY']) for r in receipts),Decimal(0))
 full['fees_CNY']=str(fees);full['paid_API']=len(receipts);full['invoice_CNY']=None;full['usage_fee_is_peak_upper_not_invoice']=True
 full['complete_actual_nonzero']=bool(full.get('runtime_core',{}).get('complete') and full.get('success') is True and full.get('public_acceptance_known') and full.get('final_hidden_known') and full.get('hidden_acceptance_calls')==1 and full.get('changed_business_files',0)>0)
 full['real_Git_Bash_roots']=len(owner.processes) if owner else 0;full['all_own_shell_Jobs_closed']=all(p.closed for p in owner.processes) if owner else True
 full.update(input_version=VERSION,shared_pack_sha256=pack_ref['sha256'],shared_semantic_sha256=pack_ref['semantic_sha256'],finance_phase=phase,V1_scores_not_mixed=True)
 save(out/'audited_result.json',full);save(out/'result.json',full)
 print(canonical({'task_id':task_id,'status':full['status'],'success':full['success'],'complete_actual_nonzero':full['complete_actual_nonzero'],'LLM_calls':full['LLM_calls'],'fees_CNY':full['fees_CNY']}),flush=True)
 return full

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--task',required=True);parser.add_argument('--phase',choices=['Round2320Pilot'],default='Round2320Pilot');args=parser.parse_args();run(args.task,args.phase)

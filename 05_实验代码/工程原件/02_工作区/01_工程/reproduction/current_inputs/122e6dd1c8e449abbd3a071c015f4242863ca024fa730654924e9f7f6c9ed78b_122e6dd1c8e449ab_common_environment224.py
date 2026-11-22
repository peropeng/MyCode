"""Common actual public readers, physical C0/patches and Flash transport."""
from common166 import *
import copy,re
from contextlib import contextmanager
import bootstrap224
Base,Flash=bootstrap224.load()
_index_module=module('exp224_pure_semantic_index',OLD/'audit183/new_public_contract_preflight.py')
semantic_index=_index_module.semantic_index
TOOLS=[{'type':'function','function':{'name':'read_full_failure','description':'Read complete observed public failure for an exact node or public_record reference emitted by feedback. No clipping. All node statuses/phases/errors remain accessible.','parameters':{'type':'object','properties':{'node':{'type':'string'}},'required':['node'],'additionalProperties':False}}},
 {'type':'function','function':{'name':'read_current_source','description':'Read complete current business file or an explicit line interval. Business source only; tests and references forbidden.','parameters':{'type':'object','properties':{'path':{'type':'string'},'start_line':{'type':'integer','minimum':1},'end_line':{'type':'integer','minimum':1}},'required':['path'],'additionalProperties':False}}},
 {'type':'function','function':{'name':'list_current_sources','description':'List all legal current business source paths, without host paths.','parameters':{'type':'object','properties':{},'additionalProperties':False}}}]
TOOLS.append({'type':'function','function':{'name':'read_public_history','description':'Read the complete observed original public execution prefix, or one original source message index. No future suffix or hidden results.','parameters':{'type':'object','properties':{'source_message_index':{'type':'integer','minimum':0}},'additionalProperties':False}}})
TRANSPORT_FIELDS={'argv','cwd','seconds','pid','parent_pid','at_utc','label','method','task_id','snapshot','snapshot_sha256','inventory_sha256','log','log_sha256','guard_events','product_import','actual_product_imports','guard','node_selection_transport','stop_receipt','process_birth','runner_creation_time100ns','elapsed_seconds','queue_wait_seconds','path'}
def neutral(value,env):
 if isinstance(value,str):
  for original,virtual in ((str(env.repo_root),'/workspace/repo'),(str(env._paths['frozen']),'/public-tests'),(str(env.active),'/workspace'),(str(env.out),'/public-feedback')):
   value=value.replace(original,virtual).replace(original.replace('\\','/'),virtual)
  return value
 if isinstance(value,list):return [neutral(x,env) for x in value]
 if isinstance(value,dict):return {k:neutral(v,env) for k,v in value.items() if k not in TRANSPORT_FIELDS}
 return value
class CommonEnvironment(Flash.FlashEnvironment):
 def __init__(self,ref,method):
  super().__init__(ref,method)
  self._full_public_failures=copy.deepcopy(self.initial_public_feedback)
  self.initial_public_feedback=semantic_index(neutral(self._full_public_failures,self))
  self.task['failure_feedback']=copy.deepcopy(self.initial_public_feedback)
  self.goal='Recover the observed public failure and preserve already passing ordinary behavior. Original issue background: '+self.task['task']
  self.retrieval_query=__import__('retrieval178').public_query(self.task)
  self.public_spec={'task_id':self.task_id,'stratum':ref['stratum'],'goal':self.goal,'public_goal_nodes':list(self.recovery_goal_nodes),'ordinary_nodes':list(self.public_regression_nodes),'source_root':'/workspace/repo','initial_failure':self.initial_public_feedback,'reader_tools':copy.deepcopy(TOOLS)}
  self.reader_calls=[];self._public_feedback_store={};self.finance_phase='Round2320Pilot'
  self.experiment_key='Exp225' if Path(__import__('common166').E).name.startswith('实验225_') else 'Exp224'
  self._initial_public_captured_output=None
  if ref['stratum']=='original_issue_continuation' and self._manifest.get('archived_original_native_result'):
   observed=read(self._manifest['archived_original_native_result'])
   self._initial_public_captured_output={'stdout':observed.get('stdout',''),'stderr':observed.get('stderr','')}
   text=self._initial_public_captured_output['stdout']+'\n'+self._initial_public_captured_output['stderr']
   exact_errors=list(dict.fromkeys(x for x in text.splitlines() if re.match(r'^E\s',x) or re.match(r'^[A-Za-z_][A-Za-z_.]*(?:Error|Exception|Exit):',x)))
   self.initial_public_feedback['captured_public_error_lines']=neutral(exact_errors,self)
   self.task['failure_feedback']=copy.deepcopy(self.initial_public_feedback)
   self.public_spec['initial_failure']=copy.deepcopy(self.initial_public_feedback)
  self.record('common_public_contract224',{'stratum':ref['stratum'],'same_C0_goal_ordinary_private_across_methods':True,'public_input_digest':ref['input_digest'],'real_full_failure_reader':True,'full_source_reader':True,'arm_names_in_public_shell_or_reader':False})
 def _path(self,value,allow_dir=False):
  if isinstance(value,str) and value.startswith('/workspace/repo/'):value='repo/'+value[len('/workspace/repo/'):]
  if self.package!='conans':return super()._path(value,allow_dir)
  if not isinstance(value,str) or '\\' in value or ':' in value:raise ValueError('NONCANONICAL_BUSINESS_PATH')
  value=value.removeprefix('/workspace/repo/').removeprefix('repo/')
  if value.startswith('/workspace/'):
   root=value[len('/workspace/'):].split('/')[0]
   if root not in self.workspace_aliases:raise ValueError('UNKNOWN_WORKSPACE_NAMESPACE')
   value=value[len('/workspace/'+root+'/'):]
  if any(x in ('','.','..') for x in value.split('/')):raise ValueError('PATH_TRAVERSAL')
  p=(self.repo_root/value).resolve()
  if not p.is_relative_to(self.repo_root.resolve()) or value.split('/')[0] not in ('conan','conans') or any(x in ('test','tests') for x in value.split('/')):raise ValueError('PROTECTED_OR_NONBUSINESS_PATH')
  if not allow_dir and not self._core.is_business('repo/'+value):raise ValueError('PROTECTED_OR_NONBUSINESS_PATH')
  return p
 def business_files(self):
  roots=('conans','conan') if self.package=='conans' else (self.package,)
  return {p.relative_to(self.repo_root).as_posix():p.read_text('utf-8') for root in roots for p in (self.repo_root/root).rglob('*.py') if self._core.is_business('repo/'+p.relative_to(self.repo_root).as_posix())}
 def reader_call(self,name,args):
  if name=='read_full_failure':
   node=args['node']
   if node in self._public_feedback_store:
    value={'reference':node,'complete_public_feedback':neutral(copy.deepcopy(self._public_feedback_store[node]),self),'no_clipping':True}
   elif node in self._full_public_failures:
    value={'node':node,'complete_observed_public_failure':neutral(copy.deepcopy(self._full_public_failures[node]),self),'no_clipping':True}
    if self._initial_public_captured_output:value['complete_captured_public_output']=neutral(self._initial_public_captured_output,self)
   else:raise ValueError('UNKNOWN_OR_NONPUBLIC_FAILURE_NODE')
  elif name=='read_current_source':
   path=args['path'].removeprefix('/workspace/repo/').removeprefix('repo/');text=self.read_file(path);rows=text.splitlines(keepends=True)
   start=args.get('start_line',1);end=args.get('end_line',len(rows))
   if type(start)!=int or type(end)!=int or start<1 or end<start or end>len(rows):raise ValueError('INVALID_EXPLICIT_SOURCE_LINE_RANGE')
   value={'path':path,'start_line':start,'end_line':end,'total_lines':len(rows),'complete_requested_text':''.join(rows[start-1:end]),'whole_source_sha256':hashlib.sha256(text.encode()).hexdigest(),'no_silent_clipping':True}
  elif name=='list_current_sources':value={'paths':sorted(self.business_files()),'complete':True}
  elif name=='read_public_history':
   records=copy.deepcopy(self._full_messages)
   if 'source_message_index' in args:
    records=[m for m in records if m.get('source_message_index')==args['source_message_index']]
    if not records:raise ValueError('UNKNOWN_OR_FUTURE_PUBLIC_SOURCE_INDEX')
   value={'original_public_messages':neutral(records,self),'complete_requested_history':True,'future_or_private_results':False}
  else:raise ValueError('UNKNOWN_COMMON_PUBLIC_READER')
  self.reader_calls.append({'name':name,'arguments':copy.deepcopy(args),'output_sha256':digest(value)})
  self.record('actual_public_reader224',self.reader_calls[-1]);return value
 def _messages(self,messages):
  out=copy.deepcopy(messages)
  for m in out:
   if not isinstance(m.get('content'),str):continue
   try:p=json.loads(m['content'])
   except ValueError:p=None
   if isinstance(p,dict):
    if 'initial_public_failure' in p:p['initial_public_failure']=copy.deepcopy(self.initial_public_feedback)
    if 'latest_public_feedback' in p:p['latest_public_feedback']=self._compact_public(p['latest_public_feedback'])
    m['content']=canonical(p)
   m['content']=neutral(m['content'],self)
  if out and out[0].get('role')=='system':out[0]['content']+=' Complete original failure details and all current business files are available through the shared public reader tools. Use them whenever the displayed evidence is insufficient. Paths are virtual. Shared readonly masked public test list/read tools are permitted. Edit business files only. Original unmasked tests, independent final tests and reference files are forbidden.'
  return out
 def _compact_public(self,value):
  if isinstance(value,list):return [self._compact_public(x) for x in value]
  if not isinstance(value,dict):return neutral(value,self)
  result={k:self._compact_public(v) for k,v in value.items() if k not in TRANSPORT_FIELDS and k not in ('stdout','stderr')}
  if isinstance(value.get('pytest'),dict) and isinstance(value['pytest'].get('outcomes'),dict):
   outcomes=value['pytest']['outcomes'];self._full_public_failures.update(copy.deepcopy({n:v for n,v in outcomes.items() if v.get('status')!='passed'}))
   result['pytest']['outcomes']=semantic_index(neutral(outcomes,self))
  if value.get('stdout') or value.get('stderr'):
   ident='public_record_'+str(len(self._public_feedback_store));self._public_feedback_store[ident]=copy.deepcopy(value)
   # All raw public outputs remain readable; display exact error lines once.
   text=str(value.get('stdout',''))+'\n'+str(value.get('stderr',''))
   errors=list(dict.fromkeys(x for x in text.splitlines() if re.match(r'^E\s',x) or re.match(r'^[A-Za-z_][A-Za-z_.]*(?:Error|Exception|Exit):',x)))
   result['public_output_error_lines']=neutral(errors,self);result['full_public_feedback_ref']=ident
  return result
 def run_shell(self,command,working_directory=None):
  if isinstance(working_directory,str) and working_directory.startswith('/workspace/repo'):
   working_directory=str(self.repo_root/working_directory[len('/workspace/repo'):].lstrip('/'))
  result=super().run_shell(command,working_directory);return neutral(result,self)
 @contextmanager
 def native_lane(self,final=False):
  authorization()
  with super().native_lane(final=final):yield
 def _public_native(self,nodes,snapshot,label):
  authorization()
  return super()._public_native(nodes,snapshot,label)
 def run_reproduction(self,code,snapshot=None,label='reproduction'):
  authorization()
  return super().run_reproduction(code,snapshot,label)
 def llm(self,role,messages,temperature,seed,max_tokens,schema=None,tools=None):
  protocol=authorization();self._require()
  limits=protocol['budget'];caps=limits.get('role_output_caps',{})
  group=('agentless_localize' if role in ('agentless_suspicious_files','agentless_irrelevant_folders','agentless_related_elements','agentless_fine_locations') else 'agentless_regression_or_vote' if role=='agentless_regression_exclusion' else 'ours_patch' if role.startswith('ranked_repair') else role)
  cap=int(caps.get(group,Flash.OUTPUT_LIMITS.get(role,16384)));assert 1<=cap<=16384
  messages=self._messages(messages);all_tools=copy.deepcopy(tools or [])+copy.deepcopy(TOOLS)
  transport=module('exp224_shared_flash_transport',TRANSPORT)
  for reader_round in range(int(limits.get('max_reader_rounds',12))+1):
   if self.calls>=limits['max_model_calls_per_flow'] or self.out_tokens+cap>limits['max_output_tokens_per_flow']:raise Base.BudgetError('COMMON_FLOW_CALL_OR_OUTPUT_CAP')
   actual_seed=int(hashlib.sha256(canonical({'master':limits.get('master_seed',20261008),'task':self.task_id,'method':self.method,'stage':role,'original_fixed_stage_seed':int(seed),'reader_index':reader_round}).encode()).hexdigest()[:8],16)%2147483647
   body={'model':'deepseek-flash','messages':messages,'thinking':{'type':'disabled'},'temperature':temperature,'seed':actual_seed,'max_tokens':cap,'stream':False,'tools':all_tools,'tool_choice':'auto'}
   if schema:body['response_format']={'type':'json_object'}
   self.calls+=1
   response=transport.generate(self,body,self.experiment_key+'/'+self.method+'/'+self.task_id+'/'+role,phase=self.finance_phase)
   usage=response['usage'];self.out_tokens+=usage['completion_tokens'];message=response['choices'][0]['message'];finish=response['choices'][0].get('finish_reason')
   self.record('Flash_actual_response224',{'role':role,'call_ordinal':self.calls,'usage':usage,'seed':actual_seed,'original_fixed_stage_seed':seed,'master_seed':limits.get('master_seed',20261008),'reader_index':reader_round,'temperature':temperature,'finish_reason':finish,'finance_receipt':response.get('_finance_receipt',{}),'phase':self.finance_phase})
   if finish=='length':self.truncated_responses.append(self.calls)
   calls=message.get('tool_calls') or []
   if not calls:return {'content':message.get('content') or '', 'message':message,'tool_calls':[],'usage':usage,'call_ordinal':self.calls,'finish_reason':finish,'output_truncated':finish=='length','finance_receipt':response.get('_finance_receipt',{})}
   if any(c['function']['name'] not in ('read_full_failure','read_current_source','list_current_sources','read_public_history') for c in calls):
    return {'content':message.get('content') or '', 'message':message,'tool_calls':calls,'usage':usage,'call_ordinal':self.calls,'finish_reason':finish,'output_truncated':finish=='length'}
   messages.append(message)
   for c in calls:
    try:result=self.reader_call(c['function']['name'],json.loads(c['function']['arguments']))
    except (ValueError,KeyError,TypeError) as reader_error:
     result={'status':'PUBLIC_READER_ARGUMENT_ERROR','error':type(reader_error).__name__,'message':str(reader_error),'requested_tool':c['function']['name'],'correct_public_failure_node_ids':sorted(self._full_public_failures) if c['function']['name']=='read_full_failure' else None,'protected_or_nonexistent_contents_not_returned':True}
     self.record('public_reader_argument_error224',{'tool':c['function']['name'],'arguments':c['function']['arguments'],'result':result,'ordinary_tool_error_returned_to_model':True})
    messages.append({'role':'tool','tool_call_id':c['id'],'content':canonical(result)})
  raise Base.BudgetError('COMMON_PUBLIC_READER_ROUND_CAP')
 def finalize(self,result):
  authorization()
  return super().finalize(result)

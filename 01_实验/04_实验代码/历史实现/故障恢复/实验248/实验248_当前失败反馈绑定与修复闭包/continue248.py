"""Resume pure scientific state from exact settled responses and public witnesses.

No model POST, native process, private read or financial ledger write occurs here.
The original core determines candidates, admission and natural terminal choice.
"""
import argparse, ast, copy, difflib, hashlib, inspect, json, types
from pathlib import Path
import prepare248 as p

class NeedNative(BaseException):pass
class NeedReader(BaseException):pass

class Continue(p.Replay):
 def __init__(self,index,ref):
  super().__init__(index,ref)
  self.old_request_count=0  # A changed mechanism body cannot reuse old responses.
  self.old_app_count=len(self.app_queue)
  self.forward=p.HERE/'forward'/str(index);self.forward.mkdir(parents=True,exist_ok=True)
  self.forward_records=[]
  protocol=p.read(p.OLD/'protocol240.json')
  ref=protocol['public_test_scope_contract'];assert p.sha(ref['path'])==ref['sha256']
  scopes=p.read(ref['path']);self.scope=next(r for r in scopes['tasks'] if r['task_id']==self.task_id)
  all_view={**self.scope['business_and_support_files_in_view'],**self.scope['public_test_py_files_SHA256']}
  self.supports={k:v for k,v in all_view.items() if k not in self.files}
  assert p.digest({**p.source_sha(self),**self.supports})==self.initial_snapshot['inventory_sha256']
  self.original_files=copy.deepcopy(self.files)
  self.workspace_aliases=p.read(self.oldout/'input.json')['public_workspace_namespace_aliases']
  common_source=(p.OLD/'ancestor_sources/common_environment224.py').read_text('utf-8-sig')
  common_tree=ast.parse(common_source)
  neutral_node=next(n for n in common_tree.body if isinstance(n,ast.FunctionDef) and n.name=='neutral')
  neutral_scope={'TRANSPORT_FIELDS':p.assignment(p.OLD/'ancestor_sources/common_environment224.py','TRANSPORT_FIELDS')}
  exec(compile(ast.Module(body=[neutral_node],type_ignores=[]),'original_neutral224','exec'),neutral_scope)
  self.neutral=neutral_scope['neutral']
  self.future_apps=0
  root_projection=p.projection
  self.extra_roots=[(self.forward/'native_runtime','/workspace'),(self.forward/'public_native','/public-feedback')]
  p.namespace['projection']=types.SimpleNamespace(project=lambda value,roots:root_projection.project(value,roots+self.extra_roots))
 def checkpoint_boundary(self,status,state):
  super().checkpoint_boundary(status,state)
  original=self.original_files
  self.checkpoint['complete_snapshot_recovery']={'C0_business_source':original,
    'all_snapshot_business_deltas':{ident:{path:text for path,text in files.items() if original.get(path)!=text}
       for ident,files in self.snap_files.items()},'all_snapshot_diffs':self.snap_diffs,
    'current_snapshot':self.current_snapshot,'accepted_snapshot':state.get('accepted_snapshot'),
    'selected_final_snapshot':state.get('final'),'best_key':state.get('best_key')}
  self.checkpoint['new_forward_settled_requests']=copy.deepcopy(self.forward_records)
  self.checkpoint['unknown_or_inflight_native_or_model_must_not_rerun']=True
  p.save(self.out/'checkpoint.json',self.checkpoint)
 def _body(self,role,messages,temperature,seed,max_tokens,reader_index=0,tools=None):
  destination=self.out;p.namespace['save']=lambda path,value:p.save(destination/Path(path).relative_to(self.oldout),value)
  self.out=self.oldout
  try:body=self.body(role,messages,temperature,seed,max_tokens,reader_index,tools)
  finally:self.out=destination
  return p.common.inject(body,p.config,self.task_id)
 def _ready(self,body,role,attempt,reader_index):
  target=self.forward/'ready'/f'call{self.calls:03d}'
  bounds=p.bounds_namespace['bounds'](body,p.config)
  p.save(target/'FIRST_UNPOST_BODY.json',body)
  p.save(target/'FIRST_UNPOST_READY.json',{'task':self.task_id,'attempt':attempt,'reader_index':reader_index,'body_SHA256':p.digest(body),
    'input_upper':bounds['input_bound'],'output_reservation':bounds['max_tokens'],'full_peak_reserve_CNY':bounds['global_reserve'],
    'full_unchanged_original_financial_bounds':bounds,'canonical_bytes':len(p.canonical(body).encode()),'POST':0,'new_native':0,'private_reads':0,
    'finance_configuration_SHA256':p.sha(p.COMMON/'FINANCE_CONFIG_CONTINUE.json'),'bounds_source_SHA256':p.sha(p.FIN/'continuous_core_v3.py')})
  state=copy.deepcopy(p.clean(self.checkpoint));state['cursor']['calls']=self.calls-1
  state.update(status='FIRST_NEW_BODY_READY_NOT_POSTED',prepared_body=body,reader_index=reader_index,
    phase_role=role,prior_forward_responses=self.forward_records)
  p.save(target/'checkpoint.json',state)
  p.save(self.forward/'STATUS.json',{'status':'MODEL_READY','task':self.task_id,'ready_dir':str(target),'call':self.calls,
      'attempt':attempt,'reader_index':reader_index,'body_SHA256':p.digest(body),'no_model_or_native_in_this_process':True})
  raise p.Ready()
 def llm(self,role,messages,temperature,seed,max_tokens,schema=None,tools=None):
  if self.calls<self.old_request_count:return super().llm(role,messages,temperature,seed,max_tokens,schema,tools)
  current=copy.deepcopy(messages);reader_index=0
  while True:
   self.calls+=1;body=self._body(role,current,temperature,seed,max_tokens,reader_index,tools)
   initial=self.out/'new_generation/llm'/f'{self.calls:03d}'
   later=self.forward/'ready'/f'call{self.calls:03d}'/'new_generation/llm'/f'{self.calls:03d}'
   stem=initial if Path(str(initial)+'_response.json').exists() else later
   response_path=Path(str(stem)+'_response.json');receipt_path=Path(str(stem)+'_finance_receipt.json')
   if not response_path.exists():self._ready(body,role,self.checkpoint['attempt'],reader_index)
   receipt=p.read(receipt_path);request=p.read(str(stem)+'_request.json')
   assert receipt['status']=='SETTLED','unsettled/unknown request cannot be resumed or resent'
   assert p.digest(body)==request['body_SHA256'] and body==request['body'],'new settled complete body drift'
   response=p.read(response_path);usage=response['usage'];self.out_tokens+=usage['completion_tokens']
   self.forward_records.append({'body_SHA256':p.digest(body),'response_path':str(response_path),'response_SHA256':p.sha(response_path),
      'receipt':receipt,'exact_complete_body_match':True,'call':self.calls})
   message=response['choices'][0]['message'];finish=response['choices'][0].get('finish_reason')
   if not message.get('tool_calls'):
    return {'content':message.get('content') or '', 'message':message,'usage':usage,'call_ordinal':self.calls,'finish_reason':finish}
   # Reader continuation carries the exact prior request/response and same stage
   # seed; it is not an additional same-prefix sample.
   current=[copy.deepcopy(m) for m in body['messages'] if not str(m.get('content','')).startswith(p.common.TAG)]
   current.append(copy.deepcopy(message))
   for call in message['tool_calls']:
    name=call['function']['name']
    try:value=self.reader(name,json.loads(call['function']['arguments']))
    except (ValueError,KeyError,TypeError) as error:
     value={'status':'PUBLIC_READER_ARGUMENT_ERROR','message':str(error),'correct_public_failure_node_ids':sorted(self.initial_public_feedback),
       'protected_contents_not_returned':True}
    if name in ('read_full_failure','read_public_history'):
     value=p.projection.project(value,[(self.repo_root,'/workspace/repo'),(self._paths['frozen'],'/public-tests'),(self.active,'/workspace'),(self.oldout,'/public-feedback')]+self.extra_roots)
     value,_=p.feedback_codec242.encode(value)
    current.append({'role':'tool','tool_call_id':call['id'],'content':p.canonical(value)})
    p.save(self.forward/'tool_boundaries'/f'{self.calls:03d}_{call["id"]}.json',{'messages':current,'source_sha256':p.source_sha(self),'tool':call,'output':value})
   reader_index+=1
 def reader(self,name,args):
  semantic=p.codec.decode(self.pack)
  if name=='read_full_failure':
   node=args['node']
   if node not in self.initial_public_feedback:raise ValueError('UNKNOWN_OR_NONPUBLIC_FAILURE_NODE')
   value={'node':node,'complete_observed_public_failure':copy.deepcopy(self.initial_public_feedback[node]),'no_clipping':True}
   if semantic.get('original_public_captured_output'):value['complete_captured_public_output']=semantic['original_public_captured_output']
   return self.neutral(value,self)
  if name=='read_public_history':
   records=copy.deepcopy(semantic['public_history'])
   if 'source_message_index' in args:
    records=[m for m in records if m.get('source_message_index')==args['source_message_index']]
    if not records:raise ValueError('UNKNOWN_OR_FUTURE_PUBLIC_SOURCE_INDEX')
   return {'original_public_messages':self.neutral(records,self),'complete_requested_history':True,'future_or_private_results':False}
  if name=='list_current_sources':return {'paths':sorted(self.files),'complete':True}
  if name=='list_public_masked_tests':return {'paths':sorted(self.scope['public_test_py_files_SHA256']),'readonly':True,'complete':True,'scope_SHA256':p.read(p.OLD/'protocol240.json')['public_test_scope_contract']['sha256']}
  if name not in ('read_current_source','read_public_masked_test'):raise ValueError('UNKNOWN_COMMON_PUBLIC_READER')
  rel=args['path'].removeprefix('/workspace/repo/').removeprefix('repo/')
  if name=='read_current_source':
   actual=rel
   if actual.startswith('/workspace/'):
    alias=actual[len('/workspace/'):].split('/')[0]
    if alias not in self.workspace_aliases:raise ValueError('UNKNOWN_WORKSPACE_NAMESPACE')
    actual=actual[len('/workspace/'+alias+'/'):]
   text=self.files[actual];source_sha=hashlib.sha256(text.encode()).hexdigest()
  else:
   expected=self.scope['public_test_py_files_SHA256'][rel];file=Path(self.scope['public_source_repo_view'])/rel
   if p.sha(file)!=expected:raise ValueError('IMMUTABLE_PUBLIC_MASKED_TEST_DRIFT')
   text=file.read_text('utf-8');source_sha=expected
  rows=text.splitlines(keepends=True);start=args.get('start_line',1);end=args.get('end_line',len(rows))
  if type(start)!=int or type(end)!=int or not 1<=start<=end<=len(rows):raise ValueError('INVALID_EXPLICIT_SOURCE_LINE_RANGE')
  value={'path':rel,'start_line':start,'end_line':end,'total_lines':len(rows),'complete_requested_text':''.join(rows[start-1:end]),'whole_source_sha256':source_sha,'no_silent_clipping':True}
  if name=='read_public_masked_test':value.update(readonly=True)
  return value
 def apply_patch(self,edits,label,from_snapshot=None):
  if self.app_queue:return super().apply_patch(edits,label,from_snapshot)
  self.future_apps+=1;before=copy.deepcopy(self.files);errors=[]
  try:
   for edit in edits:
    path=edit['path'].removeprefix('repo/')
    if path not in self.files or self.files[path].count(edit['old'])!=1:raise ValueError('SEARCH_NOT_UNIQUE_OR_MISSING')
    self.files[path]=self.files[path].replace(edit['old'],edit['new'],1)
  except Exception as error:errors=[type(error).__name__+': '+str(error)];self.files=before
  hashes=p.source_sha(self);initial={k:hashlib.sha256(v.encode()).hexdigest() for k,v in self.original_files.items()}
  changed={k:v for k,v in hashes.items() if v!=initial[k]};ident='exp248_'+str(self.checkpoint['attempt'])
  snap={'id':ident,'label':label,'inventory_sha256':p.digest({**hashes,**self.supports}),'diff':changed,'archive_path':str(self.forward/'snapshots'/ident)}
  diff=[]
  for rel,h in sorted(changed.items()):
   patch=''.join(difflib.unified_diff(self.original_files[rel].splitlines(True),self.files[rel].splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
   diff.append({'path':'repo/'+rel,'before_sha256':initial[rel],'after_sha256':h,'unified_diff':patch})
  self.snap_files[ident]=copy.deepcopy(self.files);self.snap_diffs[ident]=diff;self.current_snapshot=snap
  p.save(self.forward/'snapshots'/ident/'snapshot.json',snap)
  p.save(self.forward/'snapshots'/ident/'business_source.json',self.files)
  return {'candidate_id':self.old_app_count+self.future_apps-1,'snapshot':copy.deepcopy(snap),
    'legal':{'legal':not errors,'changed_business_files':sorted(changed),'forbidden_changed_files':[],'frozen_tests_unchanged':True},
    'apply_errors':errors,'raw_diff':diff,'edits':copy.deepcopy(edits),'independent_original_root':False}
 def run_regression(self,snapshot,label):
  if self.public_queue:return super().run_regression(snapshot,label)
  attempt=self.checkpoint['attempt'];out=self.forward/'public_native'/f'attempt{attempt}'
  completed=out/'COMPLETED_PUBLIC.json'
  if not completed.exists():
   if (out/'SUPERVISOR_STARTED.json').exists() or (out/'NATIVE_INTENT.json').exists():
    p.save(self.forward/'STATUS.json',{'status':'PUBLIC_NATIVE_INFLIGHT_OR_UNKNOWN_NO_RERUN','task':self.task_id,'attempt':attempt,'native_output':str(out)})
    raise NeedNative()
   state=inspect.currentframe().f_back.f_locals;self.checkpoint_boundary('PUBLIC_NATIVE_READY',state)
   protocol=p.read(p.OLD/'protocol240.json');reference=protocol['public_goal_ordinary_oracle_contract']
   assert p.sha(reference['path'])==reference['sha256'];oracle=next(x for x in p.read(reference['path'])['tasks'] if x['task_id']==self.task_id)
   ready={'task_id':self.task_id,'index':self.index,'attempt':attempt,'candidate_snapshot':snapshot,
      'candidate_source_sha256':p.source_sha(self),'business_source_file':str(self.forward/'snapshots'/snapshot['id']/'business_source.json'),
      'business_source_file_SHA256':p.sha(self.forward/'snapshots'/snapshot['id']/'business_source.json'),
      'goal_nodes':oracle['target_nodes'],'ordinary_nodes':oracle['ordinary_nodes'],'ref':self.ref,
      'original_masked_scope':protocol['public_test_scope_contract'],'original_oracle_contract':reference,
      'original_runtime_contract':protocol,'native_output':str(out),'new_native':0,'private':0,'model':0}
   p.save(out/'NATIVE_READY.json',ready);p.save(out/'checkpoint.json',self.checkpoint)
   p.save(self.forward/'STATUS.json',{'status':'PUBLIC_NATIVE_READY','task':self.task_id,'attempt':attempt,'ready_path':str(out/'NATIVE_READY.json')})
   raise NeedNative()
  supervision=out/'SUPERVISION.json'
  if not supervision.exists():
   p.save(self.forward/'STATUS.json',{'status':'PUBLIC_NATIVE_PARENT_STOP_PENDING_NO_RERUN','task':self.task_id,'attempt':attempt})
   raise NeedNative()
  stop=p.read(supervision)
  assert stop['exit_code']==0 and stop['error'] is None and stop['stop_receipt']['all_owned_descendants_terminated'] is True,'public native parent STOP unknown'
  record=p.read(completed)
  assert record['task_id']==self.task_id and record['candidate_source_sha256']==p.source_sha(self)
  assert record['candidate_snapshot']['inventory_sha256']==snapshot['inventory_sha256']
  assert p.sha(record['public_native_path'])==record['public_native_SHA256']
  self._native_witness_by_inventory[p.digest(p.source_sha(self))]=record['public_native_SHA256']
  self.native_calls+=1;probe=p.read(record['public_native_path']);ordinary={n:{**probe['pytest']['outcomes'][n],'outcome':probe['pytest']['outcomes'][n]['status']} for n in self.public_regression_nodes}
  failures=sum(v['status']!='passed' for v in ordinary.values())
  return {'passed':failures==0,'failure_count':failures,'outcomes':ordinary,'status':'GUARDED_ORDINARY_REGRESSION',
     'native_record':{**probe,'path':record['public_native_path']},'public_goal_not_added_to_paper_ranking':True}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--index',required=True,type=int);args=parser.parse_args()
 tasks=p.read(p.COMMON/'COMMON_CONTRACT_SOURCE.json')['task_order'];ref=next(r for r in p.read(p.OLD/'selected_task_bindings240.json')['tasks'] if r['task_id']==tasks[args.index])
 env=Continue(args.index,ref)
 try:
  result=p.core.run(env)
  p.save(env.forward/'PUBLIC_ONLY_NATURAL_TERMINAL.json',result)
  p.save(env.forward/'SELECTED_BUSINESS_SOURCE.json',env.files)
  p.save(env.forward/'STATUS.json',{'status':'ENGINEERING_UNKNOWN' if result.get('error') else 'PUBLIC_ONLY_NATURAL_TERMINAL','task':env.task_id,
    'first_public_pass_attempt':result.get('first_public_pass_attempt'),'error':result.get('error'),'requires_separate_once_final_acceptance':True})
 except (NeedNative,p.Ready):pass
 finally:p.save(env.forward/'PUBLIC_REPLAY_RECORDS.json',env.rows);p.save(env.forward/'EXACT_NEW_REPLAY.json',env.forward_records)
 print(p.canonical(p.read(env.forward/'STATUS.json')),flush=True)
if __name__=='__main__':main()

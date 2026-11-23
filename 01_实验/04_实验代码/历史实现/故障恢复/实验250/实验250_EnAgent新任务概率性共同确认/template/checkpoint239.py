"""Atomic actor state and exact-once model/tool journals. No actions on import."""
import ast,copy,dataclasses,hashlib,json,os,re,time
from pathlib import Path

class UnsafeResume(RuntimeError):pass
def plain(x):
 if dataclasses.is_dataclass(x):return {k:plain(v) for k,v in dataclasses.asdict(x).items()}
 if isinstance(x,dict):return {str(k):plain(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [plain(v) for v in x]
 if hasattr(x,'value'):return plain(x.value)
 if isinstance(x,Path):return str(x)
 if x is None or type(x) in (str,int,float,bool):return x
 raise UnsafeResume('UNSERIALIZABLE_MUTABLE_ACTOR_STATE '+type(x).__name__)
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def atomic(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.'+str(os.getpid())+'.tmp')
 with tmp.open('w',encoding='utf-8',newline='\n') as f:f.write(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def validate_rel(rel):
 if not isinstance(rel,str) or '\\' in rel or ':' in rel or any(x in ('','.','..') for x in rel.split('/')):raise UnsafeResume('NONCANONICAL_CHECKPOINT_PATH')
 return rel
def inventory(root):
 root=Path(root).resolve();out={}
 for p in sorted(root.rglob('*')):
  if p.is_symlink():raise UnsafeResume('SYMLINK_CHECKPOINT')
  if p.is_file() and not {'__pycache__','.pytest_cache'}&set(p.parts):out[p.relative_to(root).as_posix()]=sha(p)
 return out

class Store:
 def __init__(self,path,work,env,lineage):
  self.path=Path(path);self.work=Path(work);self.env=env;self.lineage=lineage;self.context=None;self.active_selector=None
  self.path.mkdir(parents=True,exist_ok=True);self.sequence=0;self.state={};self.lease_started=float(os.environ.get('EXP239_LEASE_STARTED_MONOTONIC',time.monotonic()))
  pointer=self.path/'LATEST.json'
  if pointer.exists():
   ref=read(pointer);p=self.path/'states'/ref['file'];assert sha(p)==ref['SHA256'],'CHECKPOINT_POINTER_DRIFT'
   self.state=read(p);self.sequence=ref['sequence'];assert self.state['task_id']==env.task_id
  else:
   self.state={'schema':'EnAgent-atomic-selector-state/1','task_id':env.task_id,'phase':'SELECTOR_NEXT_MODEL','vote_index':lineage['selector_vote_index'],'next_turn':lineage['next_selector_transport_turn'],'votes':lineage['completed_votes'],'history':lineage['resume_client_history_before_next_model'],'incoming':[],'tool_results':{},'editor_undo_state':lineage['editor_undo_state'],'bash_cwd':'.','old_lineage_SHA256':sha(Path(lineage['_lineage_path'])),'first_original_unsent_body_not_yet_checked':True}
 def accounting(self):
  before=self.lineage['science_old_active_elapsed_seconds']+getattr(self.env,'_prior_resume_active_elapsed',0)
  return {'LLM_request_intents':self.env.calls,'output_tokens':self.env.out_tokens,'public_native_calls':self.env.native_calls,'product_native_roots':getattr(self.env,'_product_native_roots',0),'science_original_T0_monotonic':self.lineage['science_original_T0_monotonic'],'total_elapsed_seconds':max(0,time.monotonic()-self.lineage['science_original_T0_monotonic']),'active_elapsed_before_current_lease':before,'active_elapsed_seconds':before+max(0,time.monotonic()-self.lease_started),'old_settled_API_calls':self.lineage['old_settled_API_calls'],'old_owned_OS_roots':self.lineage['old_owned_OS_roots'],'execution_lease_started_monotonic':self.lease_started,'execution_lease_deadline_monotonic':self.env.deadline}
 def tool_state(self):
  if self.context is None:return
  editor=getattr(self.context,'_source_editor_with_undo',None)
  if editor is not None:
   self.state['editor_undo_state']={Path(k).resolve().relative_to(Path(self.context.root).resolve()).as_posix():list(v) for k,v in editor._file_history.items()}
 def commit(self,phase=None):
  if phase:self.state['phase']=phase
  self.tool_state();self.state['accounting']=self.accounting();self.state['blob_inventory']={}
  blobs=self.path/'blobs';blobs.mkdir(exist_ok=True)
  # Completed coder/tester clones are immutable lineage inputs. Only selector
  # can mutate in this continuation, so snapshot it at every boundary.
  for short,h in inventory(self.work/'selector').items():
   rel='selector/'+short;src=self.work/validate_rel(rel);target=blobs/h
   if not target.exists():
    raw=src.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=h:raise UnsafeResume('CLONE_CHANGED_DURING_CHECKPOINT')
    tmp=target.with_name(h+'.'+str(os.getpid())+'.tmp');tmp.write_bytes(raw);os.replace(tmp,target)
   if sha(target)!=h:raise UnsafeResume('CHECKPOINT_BLOB_DRIFT')
   self.state['blob_inventory'][rel]=h
  self.sequence+=1;name=f'{self.sequence:06d}.json';p=self.path/'states'/name
  atomic(p,self.state);atomic(self.path/'LATEST.json',{'sequence':self.sequence,'file':name,'SHA256':sha(p),'phase':self.state['phase']})
 def restore_work(self):
  mapping=self.state.get('blob_inventory')
  if not mapping:return
  self.work.mkdir(parents=True,exist_ok=True)
  # Only files from this resumed owner are reverted. Historical owner is never written.
  for p in (self.work/'selector').rglob('*'):
   if p.is_symlink():raise UnsafeResume('SYMLINK_CURRENT_OWNER')
   if p.is_file() and not {'__pycache__','.pytest_cache'}&set(p.parts) and p.relative_to(self.work).as_posix() not in mapping:p.unlink()
  for rel,h in mapping.items():
   source=self.path/'blobs'/h
   if sha(source)!=h:raise UnsafeResume('CHECKPOINT_BLOB_DRIFT')
   target=self.work/validate_rel(rel);target.parent.mkdir(parents=True,exist_ok=True)
   # Git object files copied from the saved clone are read-only on Windows.
   # Identical immutable bytes need no write; restore only actual changes.
   if target.exists() and sha(target)==h:continue
   tmp=target.with_name(target.name+'.restore.'+str(os.getpid())+'.tmp');tmp.write_bytes(source.read_bytes())
   if target.exists():target.chmod(target.stat().st_mode|0o200)
   os.replace(tmp,target)
  actual={'selector/'+k:v for k,v in inventory(self.work/'selector').items()}
  if actual!=mapping:raise UnsafeResume('CHECKPOINT_RESTORE_BYTES_DIFFER')
 def recover_uncertain_model(self):
  if self.state['phase']!='MODEL_INTENT':return
  n=self.state['model_attempt_ordinal'];response=self.env.out/'llm'/f'{n:03d}_response.json';receipt=self.env.out/'llm'/f'{n:03d}_finance_receipt.json';request=self.env.out/'llm'/f'{n:03d}_request.json'
  if not (response.exists() and receipt.exists() and request.exists()):raise UnsafeResume('MODEL_INFLIGHT_OR_UNKNOWN_NO_AUTOMATIC_RESEND')
  r=read(receipt);raw=read(response);q=read(request)
  if r.get('status')!='SETTLED' or q.get('body_SHA256')!=r.get('body_SHA256'):raise UnsafeResume('MODEL_UNKNOWN_RECEIPT_NO_AUTOMATIC_RESEND')
  before=self.state['counters_before_model'];self.env.calls=max(before['LLM_request_intents'],n);self.env.out_tokens=before['output_tokens']+raw['usage']['completion_tokens']
  self.state['raw_response']=raw;self.state['receipt_SHA256']=sha(receipt);self.state['history']=self.state['model_payload']['messages'];self.state['incoming']=[];self.commit('MODEL_SETTLED_RESPONSE')

def llm_messages(core,values):
 result=[]
 for value in values:
  v=copy.deepcopy(value);tool=v.pop('tool_result',None)
  if tool is not None:v['tool_result']=core.ToolResult(**tool)
  result.append(core.LLMMessage(**v))
 return result

def install(core,store):
 """Only resume locals and durable hooks differ; original loop decisions stay AST exact."""
 old_tool=core.ToolExecutor.execute_tool_call
 async def safe_tool(executor,call):
  s=store.state;key=call.call_id
  if s.get('inflight_tool'):raise UnsafeResume('TOOL_INFLIGHT_NO_AUTOMATIC_REEXECUTION')
  if key in s.get('tool_results',{}):return core.ToolResult(**s['tool_results'][key])
  s['inflight_tool']=plain(call);store.commit('TOOL_INTENT')
  value=await old_tool(executor,call)
  s['tool_results'][key]=plain(value);s.pop('inflight_tool',None);store.commit('TOOLS_RESPONSE_PENDING')
  if call.name=='bash' and value.success and store.bridge._mapped_invocation(core.current().root,call.arguments.get('command','')) is None:
   command=call.arguments.get('command','')
   # The source guard forbids variables, substitution, functions and traversal.
   # Track allowed cd effects; all other shell state is the unchanged source env.
   import shlex
   lexer=shlex.shlex(command,posix=True,punctuation_chars=';&|<>');lexer.whitespace_split=True;segments=[];part=[]
   for token in lexer:
    if token in ('&&','|',';'):segments.append(part);part=[]
    else:part.append(token)
   segments.append(part)
   for part in segments:
    if part and part[0]=='cd' and len(part)==2 and value.success:
     _,mapped,_=store.bridge._path(core.current().root,part[1]);s['bash_cwd']=mapped.resolve().relative_to(Path(core.current().root).resolve()).as_posix()
  store.commit('TOOLS_RESPONSE_PENDING');return value
 core.ToolExecutor.execute_tool_call=safe_tool
 def before(selector,turn,messages):
  store.active_selector=selector;store.context=core.current();store.state['next_turn']=turn-1
 def after_tools(selector,turn,messages):
  store.state.update(next_turn=turn,history=copy.deepcopy(selector.llm_client.history),incoming=[plain(x) for x in messages],tool_results={});store.commit('SELECTOR_NEXT_MODEL')
 core.NS.__dict__.update(_resume_turn=lambda selector:store.state['next_turn'],_resume_messages=lambda selector:llm_messages(core,store.state.get('incoming',[])),_checkpoint_before=before,_checkpoint_after_tools=after_tools)
 path=core.TRAE/'evaluation/patch_selection/trae_selector/selector_agent.py';tree=ast.parse(path.read_text('utf-8-sig'));cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='SelectorAgent');fn=copy.deepcopy(next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='run'))
 changes=[]
 class Hooks(ast.NodeTransformer):
  def visit_Assign(self,node):
   if len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id=='turn' and isinstance(node.value,ast.Constant) and node.value.value==0:
    changes.append('initialize turn from committed original cursor');node.value=ast.parse('_resume_turn(self)',mode='eval').body
   elif len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id=='messages' and isinstance(node.value,ast.Attribute) and node.value.attr=='initial_messages':
    changes.append('initialize messages from committed input');node.value=ast.parse('_resume_messages(self)',mode='eval').body
   if len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id=='llm_response':
    changes.append('durable model boundary');return [ast.parse('_checkpoint_before(self,turn,messages)').body[0],node]
   return node
  def visit_Expr(self,node):
   # Original bottom-of-loop print is reached after every nonterminal response,
   # including a matched status whose Result clause is absent.
   if isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='print' and any(isinstance(x,ast.Constant) and isinstance(x.value,str) and 'System Response(' in x.value for arg in node.value.args if isinstance(arg,ast.JoinedStr) for x in arg.values):
    changes.append('durable completed nonterminal model/tool step');return [node,ast.parse('_checkpoint_after_tools(self,turn,messages)').body[0]]
   return node
 fn=Hooks().visit(fn);ast.fix_missing_locations(fn);assert len(changes)==4,changes
 exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(path)+'[checkpoint-hooks]', 'exec'),core.NS.__dict__)
 core.SelectorAgent.run=core.NS.run
 return {'source':str(path),'original_source_SHA256':sha(path),'only_AST_changes':changes,'matching_selection_regex_fallback_voting_and_tool_actions_unchanged':True}

def checkpoint_transport(base,store):
 class DurableTransport(base):
  def request(self,payload):
   s=store.state
   if s.get('phase') in ('MODEL_SETTLED_RESPONSE','TOOLS_RESPONSE_PENDING'):
    if digest(payload)!=digest(s['model_payload']):raise UnsafeResume('SETTLED_RESPONSE_PAYLOAD_MISMATCH_NO_REPOST')
    # The paid response consumed this original transport turn. Replaying it
    # must preserve the next request seed without changing paid accounting.
    self.turn=int(s['next_turn'])+1
    return copy.deepcopy(s['raw_response'])
   if s.get('phase') in ('MODEL_INTENT','TOOL_INTENT'):raise UnsafeResume('INFLIGHT_STATE_NO_NEW_POST')
   s.update(model_payload=copy.deepcopy(payload),history=copy.deepcopy(payload['messages']),incoming=[],model_attempt_ordinal=self.env.calls+1,counters_before_model=store.accounting(),tool_results={})
   store.commit('MODEL_INTENT')
   try:raw=super().request(payload)
   except BaseException as error:
    # A finance gate before reservation/POST is an unsent intent. Unknowns
    # preserve the unresolved intent and full hold; never treat them as retryable.
    if 'GateRejected' in type(error).__name__ or self.env.calls<s['model_attempt_ordinal']:
     s['known_unsent_error']={'type':type(error).__name__,'message':str(error)};store.commit('MODEL_NOT_POSTED')
    raise
   receipt=self.env.out/'llm'/f'{self.env.calls:03d}_finance_receipt.json'
   if not receipt.exists() or read(receipt).get('status')!='SETTLED':raise UnsafeResume('SETTLED_RECEIPT_REQUIRED_BEFORE_SAFE_MODEL_COMMIT')
   s.update(raw_response=copy.deepcopy(raw),receipt_SHA256=sha(receipt));store.commit('MODEL_SETTLED_RESPONSE');return raw
 return DurableTransport

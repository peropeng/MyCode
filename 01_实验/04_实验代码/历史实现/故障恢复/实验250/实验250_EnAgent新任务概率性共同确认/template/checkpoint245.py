"""Durable model/tool and original agent-loop boundaries for every role."""
import ast,copy,dataclasses,enum,hashlib,json,os,shlex,time,threading
from pathlib import Path
from common166 import E,read,sha,digest,authorization
from checkpoint239 import UnsafeResume,atomic,inventory
ACTIVE=None;CORE=None
_ENDPOINT_LOCK=threading.RLock()
def packed(x):
 if dataclasses.is_dataclass(x):return {'$class':type(x).__name__,'fields':{f.name:packed(getattr(x,f.name)) for f in dataclasses.fields(x)}}
 if isinstance(x,enum.Enum):return {'$enum':type(x).__name__,'value':x.value}
 if isinstance(x,Path):return {'$path':str(x)}
 if isinstance(x,dict):return {str(k):packed(v) for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [packed(v) for v in x]
 if x is None or type(x) in (str,int,float,bool):return x
 raise UnsafeResume('UNSERIALIZABLE_ACTOR_STATE '+type(x).__name__)
def unpacked(x):
 if isinstance(x,list):return [unpacked(v) for v in x]
 if isinstance(x,dict):
  if '$class' in x:return getattr(CORE.NS,x['$class'])(**{k:unpacked(v) for k,v in x['fields'].items()})
  if '$enum' in x:return getattr(CORE.NS,x['$enum'])(x['value'])
  if '$path' in x:return Path(x['$path'])
  return {k:unpacked(v) for k,v in x.items()}
 return x
def observe_endpoint(env):
 clock=read(E/'checkpoints'/env.task_id/'GENESIS.json');elapsed=time.monotonic()-clock['original_T0_monotonic'];path=E/'checkpoints'/env.task_id/'BUDGET_ENDPOINT_OBSERVATION.json'
 if not path.exists() and (elapsed>=1800 or env.calls>=128 or env.out_tokens>=131072):atomic(path,{'observation_only':True,'stop_unbounded_trajectory':False,'at_monotonic':time.monotonic(),'elapsed_seconds':elapsed,'calls':env.calls,'output_tokens':env.out_tokens,'native':env.native_calls,'budget_seconds':1800,'budget_calls':128,'budget_outputs':131072,'complete_accepted_repair_observed':False,'budget_endpoint_failure_if_no_once_final_acceptance_before_threshold':True,'partial_checkpoint_path':str(ACTIVE.path/'LATEST.json') if ACTIVE else None})
def start_endpoint_timer(env):
 def wait_then_observe():
  remaining=max(0,env.started+1800-time.monotonic());threading.Event().wait(remaining)
  with _ENDPOINT_LOCK:observe_endpoint(env)
 threading.Thread(target=wait_then_observe,name='budget-observer-only245',daemon=True).start()
def accounting(env):
 observe_endpoint(env);return {'LLM_request_intents':env.calls,'output_tokens':env.out_tokens,'public_native_calls':env.native_calls,'product_native_roots':getattr(env,'_product_native_roots',0),'original_T0_monotonic':env.started,'total_elapsed_seconds':time.monotonic()-env.started}
class Stage:
 def __init__(self,env,role,index,root,bridge):
  self.env,self.role,self.index,self.root,self.bridge=env,role,index,Path(root),bridge;self.context=None;self.path=E/'checkpoints'/env.task_id/(role+'_'+str(index));self.sequence=0;self.state={'phase':'NEXT_MODEL','next_transport_turn':0,'history':[],'tool_results':{},'bash_cwd':'.','step_number':1}
  pointer=self.path/'LATEST.json'
  if pointer.exists():
   ref=read(pointer);file=self.path/'states'/ref['file'];assert sha(file)==ref['SHA256'];self.state=read(file);self.sequence=ref['sequence']
  if self.state['phase'] in ('MODEL_INTENT','TOOL_INTENT'):raise UnsafeResume('UNKNOWN_OR_INFLIGHT_ROLE_BOUNDARY_NO_AUTOMATIC_RESEND')
 def tool_state(self):
  if self.context is None:return
  editor=getattr(self.context,'_source_editor_with_undo',None)
  if editor is not None:self.state['editor_undo_state']={Path(k).resolve().relative_to(self.root.resolve()).as_posix():list(v) for k,v in editor._file_history.items()}
  agent=getattr(self,'agent',None)
  if agent is not None:
   self.state['thinking_tool_state']={t.name:{k:packed(getattr(t,k)) for k in ('thought_history','branches') if hasattr(t,k)} for t in agent._tools if t.name=='sequentialthinking'}
 def commit(self,phase=None):
  if phase:self.state['phase']=phase
  self.tool_state();self.state['accounting']=accounting(self.env);self.state['blob_inventory']={};blobs=self.path/'blobs';blobs.mkdir(parents=True,exist_ok=True)
  if self.root.exists():
   for rel,h in inventory(self.root).items():
    source=self.root/rel;target=blobs/h
    if not target.exists():
     raw=source.read_bytes()
     if hashlib.sha256(raw).hexdigest()!=h:raise UnsafeResume('CLONE_CHANGED_DURING_ATOMIC_BLOB_SNAPSHOT')
     tmp=target.with_name(h+'.'+str(os.getpid())+'.tmp')
     with tmp.open('wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
     os.replace(tmp,target)
    if sha(target)!=h:raise UnsafeResume('ROLE_CHECKPOINT_BLOB_DRIFT')
    self.state['blob_inventory'][rel]=h
  self.sequence+=1;name=f'{self.sequence:06d}.json';atomic(self.path/'states'/name,self.state);atomic(self.path/'LATEST.json',{'sequence':self.sequence,'file':name,'SHA256':sha(self.path/'states'/name),'phase':self.state['phase']});atomic(E/'checkpoints'/self.env.task_id/'GLOBAL_ACCOUNTING.json',self.state['accounting'])
 def restore(self):
  if 'blob_inventory' not in self.state:return
  self.root.mkdir(parents=True,exist_ok=True);mapping=self.state['blob_inventory']
  for x in self.root.rglob('*'):
   if x.is_symlink():raise UnsafeResume('ROLE_SYMLINK_REFUSED')
   if x.is_file() and not {'__pycache__','.pytest_cache'}&set(x.parts) and x.relative_to(self.root).as_posix() not in mapping:x.unlink()
  for rel,h in mapping.items():
   source=self.path/'blobs'/h;assert sha(source)==h;target=self.root/rel;target.parent.mkdir(parents=True,exist_ok=True)
   if target.exists() and sha(target)==h:continue
   tmp=target.with_name(target.name+'.restore.tmp');tmp.write_bytes(source.read_bytes())
   if target.exists():target.chmod(target.stat().st_mode|0o200)
   os.replace(tmp,target)
  if inventory(self.root)!=mapping:raise UnsafeResume('ROLE_RESTORE_BYTES_DIFFER')
 def bind(self,agent,client,context):
  global ACTIVE
  ACTIVE=self;self.context=context;self.agent=agent;self.restore();client.history=copy.deepcopy(self.state['history'])
  editor=getattr(context,'_source_editor_with_undo',None)
  if editor is not None:
   from collections import defaultdict
   editor._file_history=defaultdict(list,{self.root/rel:list(values) for rel,values in self.state.get('editor_undo_state',{}).items()})
  if agent is not None:
   for t in agent._tools:
    for k,v in self.state.get('thinking_tool_state',{}).get(t.name,{}).items():setattr(t,k,unpacked(v))
def transport(base,stage):
 class Durable(base):
  def request(self,payload):
   s=stage.state
   if s['phase'] in ('MODEL_SETTLED_RESPONSE','TOOLS_RESPONSE_PENDING'):
    if digest(payload)!=digest(s['model_payload']):raise UnsafeResume('CACHED_ROLE_PAYLOAD_DIFFERS_NO_POST')
    self.turn=s['request_transport_turn']+1;return copy.deepcopy(s['raw_response'])
   if s['phase'] in ('MODEL_INTENT','TOOL_INTENT'):raise UnsafeResume('INFLIGHT_MODEL_OR_TOOL_NO_POST')
   s.update(model_payload=copy.deepcopy(payload),request_transport_turn=self.turn,model_attempt_ordinal=self.env.calls+1,tool_results={});stage.commit('MODEL_INTENT')
   try:raw=super().request(payload)
   except BaseException as error:
    if 'GateRejected' in type(error).__name__ or self.env.calls<s['model_attempt_ordinal']:s['known_unsent_error']={'type':type(error).__name__,'error':str(error)};stage.commit('MODEL_NOT_POSTED')
    raise
   receipt=self.env.out/'llm'/f'{self.env.calls:03d}_finance_receipt.json'
   if not receipt.exists() or read(receipt).get('status')!='SETTLED':raise UnsafeResume('PAID_RECEIPT_REQUIRED_BEFORE_REPLAY')
   s.update(raw_response=copy.deepcopy(raw),receipt_SHA256=sha(receipt));stage.commit('MODEL_SETTLED_RESPONSE');return raw
 return Durable
def install(core):
 global CORE
 CORE=core;old=core.ToolExecutor.execute_tool_call
 async def safe(executor,call):
  st=ACTIVE;s=st.state;key=call.call_id
  if s.get('inflight_tool'):raise UnsafeResume('TOOL_INFLIGHT_NO_AUTOMATIC_REEXECUTION')
  if key in s.get('tool_results',{}):return core.ToolResult(**s['tool_results'][key])
  s['inflight_tool']=packed(call);st.commit('TOOL_INTENT');value=await old(executor,call);s['tool_results'][key]=dataclasses.asdict(value);s.pop('inflight_tool',None);st.commit('TOOLS_RESPONSE_PENDING')
  if call.name=='bash' and value.success and st.bridge._mapped_invocation(core.current().root,call.arguments.get('command','')) is None:
   lex=shlex.shlex(call.arguments.get('command',''),posix=True,punctuation_chars=';&|<>');lex.whitespace_split=True;parts=[];part=[]
   for token in lex:
    if token in ('&&','|',';'):parts.append(part);part=[]
    else:part.append(token)
   parts.append(part)
   for part in parts:
    if part and part[0]=='cd' and len(part)==2 and value.success:
     _,mapped,_=st.bridge._path(st.root,part[1]);s['bash_cwd']=mapped.resolve().relative_to(st.root.resolve()).as_posix()
  st.commit('TOOLS_RESPONSE_PENDING');return value
 async def checked_safe(executor,call):
  try:return await safe(executor,call)
  except BaseException as error:ACTIVE.env._generation_fatal=error;raise
 core.ToolExecutor.execute_tool_call=checked_safe
 sessionclass=core.NS._BashSession;original_start=sessionclass.start
 async def restored_start(session):
  fresh=not session._started;await original_start(session)
  if fresh and ACTIVE is not None and Path(session.root).resolve()==ACTIVE.root.resolve():
   rel=ACTIVE.state.get('bash_cwd','.')
   if rel not in ('','.'):
    path=(ACTIVE.root/rel).resolve()
    if not path.is_relative_to(ACTIVE.root.resolve()) or not path.is_dir():raise UnsafeResume('SAVED_PERSISTENT_CWD_NOT_OWNED')
    answer=await session.run('cd '+shlex.quote(path.as_posix()))
    if answer.error_code!=0:raise UnsafeResume('SAVED_PERSISTENT_CWD_RESTORE_FAILED')
    ACTIVE.env.record('checkpoint_saved_Bash_cwd_restored245',{'cwd':rel,'same_owned_role_clone':True,'new_model_call':False})
 sessionclass.start=restored_start
 def coder_messages(agent):return unpacked(ACTIVE.state.get('incoming',packed(agent._initial_messages)))
 def coder_execution(task):return unpacked(ACTIVE.state['execution']) if 'execution' in ACTIVE.state else core.NS.AgentExecution(task=task,steps=[])
 def before(agent,step,messages,execution):
  if ACTIVE.state['phase'] not in ('MODEL_SETTLED_RESPONSE','TOOLS_RESPONSE_PENDING'):
   ACTIVE.state.update(history=copy.deepcopy(agent._llm_client.history),incoming=packed(messages),execution=packed(execution),step_number=step.step_number,next_transport_turn=agent._llm_client.transport.turn);ACTIVE.commit('NEXT_MODEL')
 def after(agent,step,messages,execution):
  if getattr(ACTIVE.env,'_generation_fatal',None) is not None or ACTIVE.state['phase'] in ('MODEL_INTENT','TOOL_INTENT','MODEL_NOT_POSTED'):
   ACTIVE.commit();return
  ACTIVE.state.update(history=copy.deepcopy(agent._llm_client.history),incoming=packed(messages),execution=packed(execution),step_number=step.step_number+1,next_transport_turn=agent._llm_client.transport.turn,tool_results={});ACTIVE.commit('ROLE_COMPLETED' if execution.agent_state==core.NS.AgentState.COMPLETED else 'NEXT_MODEL')
 path=core.TRAE/'trae_agent/agent/base_agent.py';tree=ast.parse(path.read_text('utf-8-sig'));cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='BaseAgent');fn=copy.deepcopy(next(x for x in cls.body if isinstance(x,ast.AsyncFunctionDef) and x.name=='execute_task'));changes=[]
 class Hooks(ast.NodeTransformer):
  def visit_Assign(self,node):
   if len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
    name=node.targets[0].id
    if name=='execution':node.value=ast.parse('_245_coder_execution(self._task)',mode='eval').body;changes.append('resume typed execution')
    if name=='messages':node.value=ast.parse('_245_coder_messages(self)',mode='eval').body;changes.append('resume exact incoming')
    if name=='step_number' and isinstance(node.value,ast.Constant) and node.value.value==1:node.value=ast.parse('_245_coder_step()',mode='eval').body;changes.append('resume original internal step')
    if name=='messages' and isinstance(node.value,ast.Await):node.value=node.value;changes.pop();return [ast.parse('_245_before(self,step,messages,execution)').body[0],node]
   return node
  def visit_Expr(self,node):
   if isinstance(node.value,ast.Await) and isinstance(node.value.value,ast.Call) and getattr(node.value.value.func,'attr',None)=='_finalize_step':return [node,ast.parse('_245_after(self,step,messages,execution)').body[0]]
   return node
 # The awaited assignment must retain the author's original _run_llm_step call.
 class CorrectHooks(Hooks):
  def visit_Assign(self,node):
   if len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id=='messages' and isinstance(node.value,ast.Await):return [ast.parse('_245_before(self,step,messages,execution)').body[0],node]
   return super().visit_Assign(node)
 core.NS.__dict__.update(_245_coder_execution=coder_execution,_245_coder_messages=coder_messages,_245_coder_step=lambda:ACTIVE.state['step_number'],_245_before=before,_245_after=after)
 fn=CorrectHooks().visit(fn);assert len(changes)==3,changes;exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(path)+'[durable-hooks245]','exec'),core.NS.__dict__);core.BaseAgent.execute_task=core.NS.execute_task
 selectorpath=core.TRAE/'evaluation/patch_selection/trae_selector/selector_agent.py';tree=ast.parse(selectorpath.read_text('utf-8-sig'));cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='SelectorAgent');fn=copy.deepcopy(next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='run'))
 def selector_before(agent,turn,messages):
  if ACTIVE.state['phase'] not in ('MODEL_SETTLED_RESPONSE','TOOLS_RESPONSE_PENDING'):ACTIVE.state.update(history=copy.deepcopy(agent.llm_client.history),incoming=packed(messages),next_transport_turn=turn-1);ACTIVE.commit('NEXT_MODEL')
 def selector_after(agent,turn,messages):ACTIVE.state.update(history=copy.deepcopy(agent.llm_client.history),incoming=packed(messages),next_transport_turn=turn,tool_results={});ACTIVE.commit('NEXT_MODEL')
 class SelectorHooks(ast.NodeTransformer):
  def visit_Assign(self,node):
   if len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
    n=node.targets[0].id
    if n=='turn' and isinstance(node.value,ast.Constant) and node.value.value==0:node.value=ast.parse('_245_selector_turn()',mode='eval').body
    if n=='messages' and isinstance(node.value,ast.Attribute) and node.value.attr=='initial_messages':node.value=ast.parse('_245_selector_messages(self)',mode='eval').body
    if n=='llm_response':return [ast.parse('_245_selector_before(self,turn,messages)').body[0],node]
   return node
  def visit_Expr(self,node):
   if isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='print' and any(isinstance(x,ast.Constant) and isinstance(x.value,str) and 'System Response(' in x.value for arg in node.value.args if isinstance(arg,ast.JoinedStr) for x in arg.values):return [node,ast.parse('_245_selector_after(self,turn,messages)').body[0]]
   return node
 core.NS.__dict__.update(_245_selector_turn=lambda:ACTIVE.state['next_transport_turn'],_245_selector_messages=lambda agent:unpacked(ACTIVE.state.get('incoming',packed(agent.initial_messages))),_245_selector_before=selector_before,_245_selector_after=selector_after)
 fn=SelectorHooks().visit(fn);exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(selectorpath)+'[durable-hooks245]','exec'),core.NS.__dict__);core.SelectorAgent.run=core.NS.run
 return {'original_sources':[str(path),str(selectorpath)],'N3_C200_S30_control_conditions_unchanged':True,'coder_resume_initializer_changes':changes,'model_tool_atomic_boundaries_all_roles':True}

"""EnAgent source-preserving native wiring. No network unless explicitly injected.

Upstream MIT source is loaded by AST from the frozen Trae artifact. The original
Trae/Selector agent loops and prompts execute; only host/provider wrappers change.
The live runner must supply its own guarded command/test/edit callbacks.
"""
from __future__ import annotations
import ast, asyncio, contextlib, dataclasses, hashlib, io, json, os, re
import shlex, shutil, subprocess, sys, threading, time, tokenize, types, urllib.request, queue
from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
from pathlib import Path
from types import SimpleNamespace
from typing import Union, TypeAlias, override

HERE=Path(__file__).resolve().parent
SOURCES=Path('D:/Code/毕设/graduate-thesis-experiments/工作区/1003-diagnosis-investigation/exp132_review/review_2245/source_review/software')
TRAE=SOURCES/'Trae-EnAgent'
AGENTLESS=SOURCES/'EnAgentAgentlessSource'
PIN='e839e559ac61bdd0e057c375dd1dee391fee797d'
if subprocess.run(['git','-C',str(TRAE),'rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip()!=PIN:
    raise RuntimeError('upstream source pin drift')
sys.path.insert(0,str(next((HERE/'vendor').glob('unidiff-*.whl'))))
from unidiff import PatchSet
SOURCE_MAP=[]
NS=types.ModuleType('enagent_frozen_core')
sys.modules[NS.__name__]=NS
NS.__dict__.update({k:v for k,v in globals().items() if not k.startswith('__')})

def source(rel,names):
    path=TRAE/rel
    tree=ast.parse(path.read_text(encoding='utf8'))
    nodes=[]
    for n in tree.body:
        name=getattr(n,'name',None)
        if isinstance(n,(ast.Assign,ast.AnnAssign)):
            targets=n.targets if isinstance(n,ast.Assign) else [n.target]
            name=next((t.id for t in targets if isinstance(t,ast.Name)),None)
        if name in names:
            nodes.append(n)
            SOURCE_MAP.append({'source':str(path),'file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'symbol':name,'line':n.lineno,'end':n.end_lineno,'AST_exact':True})
    missing=set(names)-{getattr(n,'name',None) or next((t.id for t in (n.targets if isinstance(n,ast.Assign) else [n.target]) if isinstance(t,ast.Name)),None) for n in nodes}
    if missing: raise RuntimeError(f'missing original symbols: {missing}')
    module=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)]+nodes,type_ignores=[])
    exec(compile(ast.fix_missing_locations(module),str(path),'exec'),NS.__dict__)

source('trae_agent/tools/base.py',['ToolError','ToolExecResult','ToolResult','ToolCallArguments','ToolCall','ToolParameter','Tool','ToolExecutor'])
source('trae_agent/utils/llm_clients/llm_basics.py',['LLMMessage','LLMUsage','LLMResponse'])
source('trae_agent/agent/agent_basics.py',['AgentStepState','AgentState','AgentStep','AgentExecution','AgentError'])
source('trae_agent/prompt/agent_prompt.py',['TRAE_AGENT_SYSTEM_PROMPT'])
source('trae_agent/agent/base_agent.py',['BaseAgent'])
source('trae_agent/agent/trae_agent.py',['TraeAgent'])
source('trae_agent/tools/sequential_thinking_tool.py',['ThoughtData','SequentialThinkingTool'])
source('trae_agent/tools/task_done_tool.py',['TaskDoneTool'])
source('trae_agent/tools/edit_tool.py',['EditToolSubCommands','SNIPPET_LINES','TextEditorTool'])
source('evaluation/patch_selection/trae_selector/selector_agent.py',['CandidatePatch','build_system_prompt','SelectorAgent'])
source('evaluation/patch_selection/trae_selector/utils.py',['remove_comments_from_line','clean_patch'])
globals().update({k:NS.__dict__[k] for k in ['Tool','ToolResult','ToolCall','ToolExecResult','ToolExecutor','LLMMessage','LLMUsage','LLMResponse','TraeAgent','BaseAgent','SelectorAgent','CandidatePatch','clean_patch']})

class BudgetError(RuntimeError): pass

class Ledger:
    def __init__(self,path,max_calls=100,max_output_tokens=65536):
        self.path=Path(path);self.max_calls=max_calls;self.max_output_tokens=max_output_tokens
        self.calls=0;self.output_tokens=0;self.events=[]
    def append(self,**event):
        self.events.append(event)
        with self.path.open('a',encoding='utf8') as f:f.write(json.dumps(event,ensure_ascii=False,default=str)+'\n')
    def reserve(self):
        if self.calls>=self.max_calls or self.output_tokens>=self.max_output_tokens:raise BudgetError('shared budget exhausted')
        self.calls+=1

class OpenAICompatible:
    """No retries and no implicit account discovery. Caller owns budget/endpoint."""
    def __init__(self,base_url,model,key,ledger,*,enable_network=False,timeout=45,max_tokens=1024,before_request=None,after_response=None):
        self.url=base_url.rstrip('/')+'/chat/completions';self.model=model;self.key=key
        self.ledger=ledger;self.enabled=enable_network;self.timeout=timeout;self.max_tokens=max_tokens
        self.before_request=before_request;self.after_response=after_response
    def request(self,payload):
        if not self.enabled:raise RuntimeError('network disabled; fake transport only')
        if not self.before_request or not self.after_response:
            raise RuntimeError('live transport requires shared RMB reservation/commit callbacks')
        self.ledger.reserve()
        cap=min(self.max_tokens,self.ledger.max_output_tokens-self.ledger.output_tokens)
        if cap<=0:raise BudgetError('output budget exhausted')
        payload=payload|{'model':self.model,'max_tokens':cap}
        reservation=self.before_request(payload) # caller reserves worst-case RMB BEFORE sending
        body=json.dumps(payload,ensure_ascii=False).encode('utf8')
        self.ledger.append(kind='model_request',sequence=self.ledger.calls,payload=payload,payload_sha256=hashlib.sha256(body).hexdigest())
        request=urllib.request.Request(self.url,data=body,headers={'Authorization':'Bearer '+self.key,'Content-Type':'application/json'})
        start=time.monotonic()
        try:
            with urllib.request.urlopen(request,timeout=self.timeout) as r:response=json.load(r)
        except Exception as e:
            self.ledger.append(kind='model_error',sequence=self.ledger.calls,error=type(e).__name__,elapsed=time.monotonic()-start)
            self.after_response(reservation,None,e)
            raise
        usage=response.get('usage',{});self.ledger.output_tokens+=int(usage.get('completion_tokens',0))
        self.ledger.append(kind='model_response',sequence=self.ledger.calls,response=response,elapsed=time.monotonic()-start)
        self.after_response(reservation,response,None)
        return response

class NativeClient:
    def __init__(self,transport):self.transport=transport;self.history=[]
    def set_trajectory_recorder(self,recorder):pass
    def chat(self,messages,config,tools=None,reuse_history=True):
        incoming=[]
        for m in messages:
            if m.tool_result:
                t=m.tool_result;incoming.append({'role':'tool','tool_call_id':t.call_id,'content':str(t.result or '')+('\nError: '+t.error if t.error else '')})
            elif m.tool_call:
                t=m.tool_call;incoming.append({'role':'assistant','tool_calls':[{'id':t.call_id,'type':'function','function':{'name':t.name,'arguments':json.dumps(t.arguments)}}]})
            else:incoming.append({'role':m.role,'content':m.content or ''})
        self.history=self.history+incoming if reuse_history else incoming
        payload={'messages':self.history.copy(),'temperature':config.temperature,'top_p':config.top_p}
        if tools:payload['tools']=[{'type':'function','function':t.json_definition()} for t in tools]
        raw=self.transport.request(payload)
        choice=raw['choices'][0];message=choice['message'];self.history.append(message)
        calls=[]
        for call in message.get('tool_calls') or []:
            f=call['function'];args=json.loads(f['arguments']) if isinstance(f.get('arguments'),str) else f.get('arguments',{})
            calls.append(ToolCall(name=f['name'],call_id=call['id'],arguments=args,id=call['id']))
        u=raw.get('usage',{})
        return LLMResponse(content=message.get('content') or '',usage=LLMUsage(input_tokens=int(u.get('prompt_tokens',0)),output_tokens=int(u.get('completion_tokens',0))),model=raw.get('model'),finish_reason=choice.get('finish_reason'),tool_calls=calls or None)

ACTIVE=threading.local()
def current():return ACTIVE.context
def llm_factory(config):return NativeClient(current().transport)

class GuardedPersistentCmd:
    """Optional Windows session wrapper; validates EVERY command before dispatch.

    The unique experiment owner supplies the same legality/resource guard used
    for other methods. No shell or target is started by importing this module.
    """
    def __init__(self,root,command_guard,timeout=45):
        if os.name!='nt':raise RuntimeError('this optional shell wrapper is Windows-only')
        self.root=Path(root);self.guard=command_guard;self.timeout=timeout;self.number=0;self.output=queue.Queue()
        self.process=subprocess.Popen(['cmd.exe','/q','/v:on'],cwd=self.root,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf8',errors='replace',bufsize=1,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        threading.Thread(target=self._reader,daemon=True).start()
        self.execute('chcp 65001 >nul')
    def _reader(self):
        for line in self.process.stdout:self.output.put(line)
        self.output.put(None)
    def execute(self,command):
        self.guard(self.root,command)
        self.number+=1;marker=f'__ENAGENT_NATIVE_{self.number}_{time.monotonic_ns()}__'
        self.process.stdin.write(command+'\n'+f'echo {marker} !errorlevel!\n');self.process.stdin.flush()
        out=[];end=time.monotonic()+self.timeout
        while True:
            try:line=self.output.get(timeout=max(0.01,end-time.monotonic()))
            except queue.Empty:
                self.close();raise TimeoutError('native shell wall budget exceeded')
            if line is None:raise RuntimeError('native shell ended without a result marker')
            if marker in line:
                suffix=line.split(marker,1)[1].strip()
                if re.fullmatch(r'-?\d+',suffix):return {'returncode':int(suffix),'stdout':''.join(out),'stderr':''}
            out.append(line)
    def close(self):
        if self.process.poll() is None:self.process.kill()
        try:self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:pass

class NativeBash(Tool):
    def get_name(self):return 'bash'
    def get_description(self):return 'Execute a real command through the guarded native shell. Windows uses cmd.exe. Working directory is the current independent repository.'
    def get_parameters(self):return [NS.ToolParameter(name='command',type='string',description='Native shell command'),NS.ToolParameter(name='restart',type='boolean',description='Reset command session',required=False)]
    async def execute(self,arguments):
        command=str(arguments.get('command',''))
        if not command:return ToolExecResult(error='missing command',error_code=1)
        result=current().command_runner(current().root,command)
        current().check_protected()
        return ToolExecResult(output=result['stdout'],error=result.get('stderr'),error_code=result['returncode'])

class GuardedEditor(NS.TextEditorTool):
    def validate_path(self,command,path):
        super().validate_path(command,path)
        current().edit_guard(current().root,path,command)
    async def _view(self,path,view_range=None):
        if path.is_dir():
            paths=[str(p) for p in sorted(path.rglob('*')) if len(p.relative_to(path).parts)<=2 and not any(x.startswith('.') for x in p.relative_to(path).parts)]
            return ToolExecResult(output='\n'.join(paths))
        return await super()._view(path,view_range)

class Recorder:
    def __init__(self,path):self.path=Path(path)
    def record_llm_interaction(self,*a,**kw):pass  # raw provider requests/responses are in shared ledger
    def finalize_recording(self,*a,**kw):pass

def native_base_init(self,agent_config,docker_config=None,docker_keep=True):
    if docker_config:raise RuntimeError('native adapter does not accept Docker configuration')
    self._llm_client=llm_factory(agent_config.model);self._model_config=agent_config.model
    self._max_steps=agent_config.max_steps;self._initial_messages=[];self._task=''
    self._tools=[NS.tools_registry[n](model_provider='openai') for n in agent_config.tools]
    self.docker_keep=True;self.docker_manager=None;self._tool_caller=ToolExecutor(self._tools)
    self._cli_console=None;self._trajectory_recorder=None

def native_diff(self):
    return git(self.project_path,'diff','--no-ext-diff','--binary','HEAD')

class NativeSession:
    def __init__(self,context):self.context=context
    def execute(self,command,timeout=60):
        if command=='git reset --hard HEAD':
            self.context.restore();return 'reset to sealed FAILED snapshot'
        return self.context.command_runner(self.context.root,command)['stdout']
    def close(self):pass

class NativeSandbox:
    def __init__(self,context):self.context=context
    def get_session(self):return NativeSession(self.context)

def native_parse_tool_response(answer,finish_reason,session):
    results=asyncio.run(ToolExecutor([GuardedEditor(model_provider='openai'),NativeBash(model_provider='openai')]).sequential_tool_call(answer.tool_calls or []))
    if not results:raise RuntimeError('selector returned neither valid selection nor tool call')
    return [LLMMessage(role='user',content=r.result or r.error or '',tool_result=r) for r in results]

NS.__dict__.update({'maybe_truncate':lambda text,**kw:text[:16000],'run':None,
 'LLMClient':llm_factory,'TrajectoryRecorder':Recorder,'parse_tool_response':native_parse_tool_response,
 'tools_registry':{'str_replace_based_edit_tool':GuardedEditor,'bash':NativeBash,'sequentialthinking':NS.SequentialThinkingTool,'task_done':NS.TaskDoneTool},
 'TraeAgentToolNames':['str_replace_based_edit_tool','bash','sequentialthinking','task_done']})
BaseAgent.__init__=native_base_init
TraeAgent.get_git_diff=native_diff

def git(root,*args):
    p=subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True,encoding='utf8',errors='replace',timeout=30)
    if p.returncode:raise RuntimeError(p.stderr)
    return p.stdout

def digest(root,paths):
    return hashlib.sha256(json.dumps([(x,hashlib.sha256((Path(root)/x).read_bytes()).hexdigest()) for x in sorted(paths)],separators=(',',':')).encode()).hexdigest()

class Context:
    def __init__(self,root,transport,command_runner,edit_guard,protected,initial):
        self.root=Path(root);self.transport=transport;self.command_runner=command_runner;self.edit_guard=edit_guard
        self.protected=protected;self.initial=initial
        self.protected_hashes={p:hashlib.sha256((self.root/p).read_bytes()).hexdigest() for p in protected}
    def check_protected(self):
        for p,h in self.protected_hashes.items():
            if hashlib.sha256((self.root/p).read_bytes()).hexdigest()!=h:raise RuntimeError('protected public test edited')
    def restore(self):
        git(self.root,'reset','--hard','HEAD');self.check_protected()
        if digest(self.root,self.initial['business_paths'])!=self.initial['business_sha256']:raise RuntimeError('reset did not restore sealed FAILED state')

def snapshot_copy(src,dst,business_paths,expected_sha):
    if digest(src,business_paths)!=expected_sha:raise RuntimeError('initial FAILED state drift')
    shutil.copytree(src,dst,ignore=shutil.ignore_patterns('.git','__pycache__','.pytest_cache'))
    git(dst,'init');git(dst,'config','user.name','EnAgent isolated gate');git(dst,'config','user.email','enagent-gate@invalid.local')
    git(dst,'config','core.autocrlf','false');git(dst,'config','core.eol','lf')
    (Path(dst)/'.git/info/attributes').write_text('* -text\n',encoding='utf8')
    git(dst,'add','.');git(dst,'commit','-m','sealed FAILED initial snapshot')
    if digest(dst,business_paths)!=expected_sha:raise RuntimeError('snapshot copy drift')

def forbidden_keys(value):
    if isinstance(value,dict):
        for k,v in value.items():
            if k.lower() in {'success_id','hidden','hidden_result','gold','gold_patch','fail_to_pass','pass_to_pass','label'}:raise ValueError('forbidden evaluator field: '+k)
            forbidden_keys(v)
    elif isinstance(value,list):
        for v in value:forbidden_keys(v)

def regression_prompt(issue,passing):
    tree=ast.parse((AGENTLESS/'select_regression_tests.py').read_text(encoding='utf8'))
    node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='select_tests_prompt_template' for t in n.targets))
    return ast.literal_eval(node.value).format(problem_statement=issue,passing_tests='\n'.join(passing)).strip()

def run_enagent(spec,workdir,transport_factory,command_runner,public_runner,edit_guard):
    """Live integration API. All command/test/edit callbacks are mandatory guards.

    No final acceptance oracle is accepted. N is fixed3, all stage requests share
    the caller-owned ledger. This function has not been run on a real target.
    """
    forbidden_keys(spec)
    workdir=Path(workdir);workdir.mkdir(parents=True,exist_ok=False)
    initial={'business_paths':spec['business_paths'],'business_sha256':spec['business_sha256']}
    cfg=SimpleNamespace(model=spec['model'],temperature=spec.get('temperature',0.7),top_p=1.,parallel_tool_calls=False,model_provider=SimpleNamespace(provider='openai'))
    acfg=SimpleNamespace(model=cfg,max_steps=spec.get('coder_max_steps',40),tools=['str_replace_based_edit_tool','bash','sequentialthinking','task_done'],mcp_servers_config=None,allow_mcp_servers=[])
    candidates=[]
    for i in range(3):
        root=workdir/f'coder_{i}'
        snapshot_copy(spec['initial_repo'],root,spec['business_paths'],spec['business_sha256'])
        ACTIVE.context=Context(root,transport_factory('coder',i,root),command_runner,edit_guard,spec['protected_paths'],initial)
        agent=TraeAgent(acfg)
        agent.new_task('Resolve issue',extra_args={'project_path':str(root),'issue':spec['issue'],'must_patch':'true'})
        execution=asyncio.run(agent.execute_task());ACTIVE.context.check_protected()
        if not execution.success:raise RuntimeError(f'coder {i} did not complete: {execution.final_result}')
        changed=[p for p in git(root,'diff','--name-only','HEAD').splitlines() if p in spec['business_paths']]
        patch=agent.remove_patches_to_tests(agent.get_git_diff())
        if not patch.strip():raise RuntimeError('no actual generated patch')
        candidates.append({'id':i,'patch':patch,'files':{p:(root/p).read_bytes() for p in changed},'normalized':clean_patch(patch),'steps':len(execution.steps),'initial_sha256':spec['business_sha256']})
    tester_root=workdir/'tester_initial';snapshot_copy(spec['initial_repo'],tester_root,spec['business_paths'],spec['business_sha256'])
    test_ids=spec['public_test_ids']
    baseline=public_runner(tester_root,test_ids)
    if set(baseline)!=set(test_ids):raise RuntimeError('public runner omitted test outcome')
    passing=[k for k in test_ids if baseline[k]=='PASS']
    if not passing:raise RuntimeError('no executable initially passing public regression tests')
    tester=NativeClient(transport_factory('tester',0,tester_root))
    tester_cfg=SimpleNamespace(**(vars(cfg)|{'temperature':0.0}))
    resp=tester.chat([LLMMessage(role='user',content=regression_prompt(spec['issue'],passing))],tester_cfg)
    excluded=set(resp.content.strip().splitlines())
    retained=[k for k in passing if k not in excluded]
    if not retained:raise RuntimeError('all public regression tests excluded; core gate unknown')
    for c in candidates:
        root=workdir/f"regression_{c['id']}";snapshot_copy(spec['initial_repo'],root,spec['business_paths'],spec['business_sha256'])
        for p,b in c['files'].items():(root/p).write_bytes(b)
        outcomes=public_runner(root,retained)
        if set(outcomes)!=set(retained):raise RuntimeError('regression runner omitted test outcome')
        if any(x not in {'PASS','FAIL'} for x in outcomes.values()):raise RuntimeError('unknown engineering regression outcome')
        c['regression_failures']=[k for k,v in outcomes.items() if v!='PASS']
    passing_candidates=[c for c in candidates if not c['regression_failures']]
    pruned=passing_candidates or candidates # original all-failed fallback
    unique=[];seen=set()
    for c in pruned:
        if c['normalized'] not in seen:unique.append(c);seen.add(c['normalized'])
    if not unique:raise RuntimeError('no candidates after original prune/dedup')
    selector_root=workdir/'selector';snapshot_copy(spec['initial_repo'],selector_root,spec['business_paths'],spec['business_sha256'])
    candidate_list=[CandidatePatch(c['id'],c['patch'],c['normalized'],not c['regression_failures'],None) for c in unique]
    votes=[]
    selector_cfg=SimpleNamespace(**(vars(cfg)|{'temperature':spec.get('selector_temperature',0.2)}))
    actual_count=len(candidates)
    if actual_count!=3:raise RuntimeError('whole-core N3 did not produce three candidates')
    for vote in range(actual_count):
        ACTIVE.context=Context(selector_root,transport_factory('selector',vote,selector_root),command_runner,edit_guard,spec['protected_paths'],initial)
        agent=SelectorAgent(llm_config=selector_cfg,sandbox=NativeSandbox(ACTIVE.context),project_path=str(selector_root),issue_description=spec['issue'],trajectory_file_name=str(workdir/f'vote_{vote}.json'),candidate_list=candidate_list,max_turn=spec.get('selector_max_turn',15))
        chosen,patch=agent.run();ACTIVE.context.check_protected();votes.append(chosen)
        if max(Counter(votes).values())>actual_count/2:break
    counts=Counter(votes);chosen=counts.most_common(1)[0][0]
    picked=next(c for c in unique if c['id']==chosen)
    result={'status':'CORE_FINISHED_FINAL_ACCEPTANCE_NOT_RUN','selected_candidate_id':chosen,'patch':picked['patch'],'generated_candidates':actual_count,'voter_upper_bound':actual_count,'actual_votes':votes,'initial_business_sha256':spec['business_sha256'],'public_initial_outcomes':baseline,'retained_public_regressions':retained,'candidate_regression_failures':{str(c['id']):c['regression_failures'] for c in candidates},'unique_after_prune':len(unique),'candidate_steps':[c['steps'] for c in candidates],'hidden_reads':0,'target_validation':False}
    (workdir/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    return result

def mapping():
    return {'original_repo_sha':PIN,'adapter_path':str(Path(__file__).resolve()),'adapter_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_to_adapter':SOURCE_MAP,'unchanged_core':['BaseAgent.execute_task/_run_llm_step/_tool_call_handler/_finalize_step','TraeAgent.new_task/execute_task/complete detection/prompts','SelectorAgent.__init__/run/build_system_prompt','original ToolExecutor and text editing operations','original clean_patch and test exclusion prompt'],
    'mechanical_adaptations':['BaseAgent initialization omits optional MCP/CKG/UI/Docker infrastructure','OpenAI Responses API wrapper becomes direct OpenAI-compatible chat/completions with full incremental history and real tool results','Docker selector session→caller-guarded native environment; parse_tool_response tool CLI→same ToolExecutor','working-tree diff pinned to failed snapshot HEAD rather than commit-only diff','public tester receives explicit frozen public IDs/runner instead of benchmark test_patch directives','no evaluator wrappers and no success_id input; correct N=3 actual generated candidates, 3 max selector votes','JSON editor optional tool omitted; original view/create/insert/str_replace +bash+sequentialthinking+task_done remain','Native shell metadata identifies Windows cmd; real runner owns persistent command/session and legality guard'],
    'unverified':['No DeepSeek endpoint/model call made','Caller guard integration, timeout/process isolation and total RMB reservation are mandatory before first target','No original pipeline effect claimed by synthetic smoke'],
    'minimal_dependencies':['Python3.12+','Git','vendored unidiff0.7.5(14kBwheel, no installation)','live target product interpreter plus guarded callbacks from unique experiment owner']}

if __name__=='__main__':
    print(json.dumps(mapping(),ensure_ascii=False,indent=2))

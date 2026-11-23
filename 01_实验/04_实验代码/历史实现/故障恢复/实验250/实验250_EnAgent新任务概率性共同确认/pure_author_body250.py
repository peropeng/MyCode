"""Evaluate only original class metadata/new_task; no subprocess/model/tool run."""
import ast, asyncio, contextlib, dataclasses, enum, functools, importlib.util, json, sys, types, typing
from abc import ABC,abstractmethod
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=Path('D:/Code/毕设/graduate-thesis-experiments')
TRAE=ROOT/'工作区/1003-diagnosis-investigation/exp132_review/review_2245/source_review/software/Trae-EnAgent'

def load_module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec)
 sys.modules[name]=value;spec.loader.exec_module(value);return value

def original_payload(issue,publicpack_text):
 ns=types.ModuleType('_pure250_original_tool_metadata');sys.modules[ns.__name__]=ns
 ns.__dict__.update(ast=ast,asyncio=asyncio,contextlib=contextlib,dataclass=dataclasses.dataclass,field=dataclasses.field,
  Enum=enum.Enum,ABC=ABC,abstractmethod=abstractmethod,Counter=Counter,Path=Path,override=typing.override,
  cached_property=functools.cached_property,Union=typing.Union,TypeAlias=typing.TypeAlias,maybe_truncate=lambda text,**kw:text[:16000])
 def source(rel,names):
  path=TRAE/rel;nodes=[]
  for node in ast.parse(path.read_text('utf-8-sig')).body:
   name=getattr(node,'name',None)
   if isinstance(node,(ast.Assign,ast.AnnAssign)):
    name=next((getattr(t,'id',None) for t in (node.targets if isinstance(node,ast.Assign) else [node.target])),None)
   if name in names:nodes.append(node)
  code=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),*nodes],type_ignores=[])
  exec(compile(ast.fix_missing_locations(code),str(path),'exec'),ns.__dict__)
 source('trae_agent/tools/base.py',['ToolError','ToolExecResult','ToolResult','ToolCallArguments','ToolCall','ToolParameter','Tool','ToolExecutor'])
 source('trae_agent/utils/llm_clients/llm_basics.py',['LLMMessage','LLMUsage','LLMResponse'])
 source('trae_agent/agent/agent_basics.py',['AgentStepState','AgentState','AgentStep','AgentExecution','AgentError'])
 source('trae_agent/prompt/agent_prompt.py',['TRAE_AGENT_SYSTEM_PROMPT'])
 source('trae_agent/agent/base_agent.py',['BaseAgent'])
 source('trae_agent/agent/trae_agent.py',['TraeAgent'])
 source('trae_agent/tools/sequential_thinking_tool.py',['ThoughtData','SequentialThinkingTool'])
 source('trae_agent/tools/task_done_tool.py',['TaskDoneTool'])
 source('trae_agent/tools/edit_tool.py',['EditToolSubCommands','SNIPPET_LINES','TextEditorTool'])
 context=types.SimpleNamespace(root=Path('/workspace/repo'))
 class EmptySession:
  def __init__(self,context=None):self.context=context
 ns.tools_registry={'sequentialthinking':ns.SequentialThinkingTool,'task_done':ns.TaskDoneTool}
 core=types.SimpleNamespace(NS=ns,Tool=ns.Tool,TRAE=TRAE,source=source,current=lambda:context,NativeSession=EmptySession)
 shim=load_module('_pure250_existing_source_shim',HERE/'template/enagent_gitbash_shim.py')
 def forbidden(*a,**kw):raise AssertionError('PURE_BODY_MUST_NOT_EXECUTE_SHELL_OR_TOOL')
 shim.install(core,command_guard=forbidden,shell_launcher=forbidden,record=lambda row:None)
 # Keep the source worker's reader parameter/name/description construction exactly.
 common=ast.parse((HERE/'template/common_environment224.py').read_text('utf-8-sig'))
 defs=[n for n in common.body if isinstance(n,ast.Assign) and any(getattr(t,'id',None)=='TOOLS' for t in n.targets)
  or isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and getattr(n.value.func.value,'id',None)=='TOOLS']
 reader_ns={'TOOLS':None};exec(compile(ast.Module(body=defs,type_ignores=[]),'source_common_tools','exec'),reader_ns)
 view=ast.parse((HERE/'template/budget_public_view.py').read_text('utf-8-sig'))
 view_ns={'read_public_view':types.SimpleNamespace()}
 toolassign=[n for n in view.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Attribute) and getattr(t.value,'id',None)=='read_public_view' and t.attr=='tool' for t in n.targets)]
 exec(compile(ast.Module(body=toolassign,type_ignores=[]),'source_masked_reader_tool','exec'),view_ns)
 reader_tools=reader_ns['TOOLS']+[view_ns['read_public_view'].tool]
 class Reader(ns.Tool):
  name=''
  def get_name(self):return self.name
  def get_description(self):return next(t['function']['description'] for t in reader_tools if t['function']['name']==self.name)
  def get_parameters(self):
   definition=next(t['function']['parameters'] for t in reader_tools if t['function']['name']==self.name)
   return [ns.ToolParameter(name=k,type=v['type'],description=k,required=k in definition.get('required',[])) for k,v in definition['properties'].items()]
  async def execute(self,args):forbidden()
 for name in ('read_full_failure','read_current_source','list_current_sources','read_public_history','read_public_test_view'):
  ns.tools_registry[name]=type('Shared_'+name,(Reader,),{'name':name})
 names=['str_replace_based_edit_tool','bash','sequentialthinking','task_done','read_full_failure','read_current_source','list_current_sources','read_public_history','read_public_test_view']
 tools=[ns.tools_registry[name](model_provider='openai') for name in names]
 agent=ns.TraeAgent.__new__(ns.TraeAgent)
 agent._tools=tools;agent.docker_config=None;agent._trajectory_recorder=None
 agent.new_task('Resolve issue',extra_args={'project_path':'/workspace/repo','issue':issue,'must_patch':'true'})
 messages=[{'role':message.role,'content':message.content or ''} for message in agent._initial_messages]
 if not any(publicpack_text in str(m.get('content','')) for m in messages):
  messages.insert(1 if messages and messages[0]['role']=='system' else 0,{'role':'user','content':publicpack_text})
 return {'messages':messages,'temperature':.5,'top_p':1.,'tools':[{'type':'function','function':tool.json_definition()} for tool in tools]}

"""Source-preserving EnAgent tool deployment seam; never starts a model or task.

The caller must inject a command guard and its owned process launcher. The source
coder/selector loops, pruning and voting are outside this module and unchanged.
"""
from __future__ import annotations
import ast
import asyncio
from collections import defaultdict
from dataclasses import dataclass, fields, replace
import datetime as dt
import hashlib
import os
from pathlib import Path
import queue
import shlex
import threading
import time
import types
from typing import Literal, get_args

BASH = Path('C:/Program Files/Git/bin/bash.exe')

def install(core, *, command_guard, shell_launcher, record, product_python=None, timeout=45, native_command=None, path_map=None, neutral_output=None):
    """Install into a separately loaded native core namespace, never edit old files.

    command_guard(root, command) authorizes EVERY actual command.
    shell_launcher(root, argv, env) returns a PIPE-based owned Popen-like handle;
      live execution must provide its declared suspended/Job/identity launcher.
    product_python(root) returns the declared product interpreter, if provided.
    record(dict) stores deployment events in the NEW experiment output only.
    """
    if not callable(command_guard) or not callable(shell_launcher) or not callable(record):
        raise TypeError('Explicit owner guard, launcher and recorder are mandatory')
    if not BASH.is_file():
        raise RuntimeError('Existing Git Bash executable absent; no automatic install')
    source_rows = []

    def note(**values):
        record({'at_utc':dt.datetime.now(dt.timezone.utc).isoformat(), **values})

    class OwnedGitSession:
        def __init__(self):
            self.context = core.current()
            self.root = Path(self.context.root)
            self._started = False
            self._timed_out = False
            self.process = None
            self.queues = [queue.Queue(), queue.Queue()]

        async def start(self):
            if self._started:
                return
            env = os.environ.copy()
            prefix = ['C:/Program Files/Git/usr/bin', 'C:/Program Files/Git/mingw64/bin']
            if product_python is not None:
                interpreter = Path(product_python(self.root)).resolve()
                if not interpreter.is_file():
                    raise RuntimeError('Declared product interpreter missing')
                prefix.insert(0, str(interpreter.parent))
            env['PATH'] = ';'.join(prefix) + ';' + env.get('PATH', '')
            self.process = shell_launcher(self.root, [str(BASH),'--noprofile','--norc'], env)
            if any(getattr(self.process, name, None) is None for name in ('stdin','stdout','stderr')):
                raise RuntimeError('Owner launcher must supply separate real stdin/stdout/stderr pipes')
            for stream,q in zip((self.process.stdout,self.process.stderr),self.queues):
                def reader(stream=stream,q=q):
                    for line in stream:
                        q.put(line)
                    q.put(None)
                threading.Thread(target=reader,daemon=True).start()
            self._started = True
            note(event='git_bash_started', root=str(self.root), PID=self.process.pid,
                 original_BashTool_control=True, existing_executable=str(BASH))

        async def run(self, command):
            if path_map is not None:
                command=path_map(self.root,command)
            if native_command is not None:
                answer=native_command(self.root,command)
                if answer is not None:
                    return core.NS.ToolExecResult(output=answer['stdout'],error=answer.get('stderr') or None,error_code=answer['returncode'])
            if self._timed_out:
                raise RuntimeError('Git Bash timed out; original restart is required')
            if self.process is None or self.process.poll() is not None:
                return core.NS.ToolExecResult(error='Git Bash exited; tool must be restarted',error_code=-1)
            command_guard(self.root, command)
            marker = '__ENAGENT_GIT_' + str(time.monotonic_ns()) + '__'
            suffix = '\n__enagent_exit=$?\nprintf "' + marker + ' %s\\n" "$__enagent_exit"\nprintf "' + marker + '\\n" >&2\n'
            self.process.stdin.write(command + suffix)
            self.process.stdin.flush()
            end = time.monotonic() + timeout
            pieces = [[],[]]
            codes = []
            try:
                for index,q in enumerate(self.queues):
                    while True:
                        line = q.get(timeout=max(0.01,end-time.monotonic()))
                        if line is None:
                            raise RuntimeError('Git Bash EOF before complete stdout/stderr marker')
                        if marker in line:
                            before,after = line.split(marker,1)
                            pieces[index].append(before)
                            if index == 0:
                                codes.append(int(after.strip()))
                            break
                        pieces[index].append(line)
            except queue.Empty as exc:
                self._timed_out = True
                raise RuntimeError('Git Bash owner wall timeout; restart required') from exc
            stdout,stderr = [''.join(part) for part in pieces]
            # Match the source tool's removal of one final newline.
            stdout = stdout[:-1] if stdout.endswith('\n') else stdout
            stderr = stderr[:-1] if stderr.endswith('\n') else stderr
            note(event='git_bash_result', root=str(self.root), PID=self.process.pid,
                 command=command, returncode=codes[0], stdout=stdout, stderr=stderr)
            if neutral_output is not None:
                stdout,stderr=neutral_output(self.root,stdout),neutral_output(self.root,stderr)
            return core.NS.ToolExecResult(output=stdout,error=stderr or None,error_code=codes[0])

        async def stop(self):
            if self.process is None:
                return
            if self.process.poll() is None:
                self.process.stdin.write('exit\n')
                self.process.stdin.flush()
                try:
                    self.process.wait(timeout=3)
                except Exception:
                    self.process.kill()
                    self.process.wait(timeout=3)
            self.process.wait(timeout=3)
            note(event='git_bash_stopped', root=str(self.root), PID=self.process.pid,
                 returncode=self.process.poll(), owned_handle_only=True)

    core.NS._BashSession = OwnedGitSession
    core.source('trae_agent/tools/bash_tool.py',['BashTool'])
    SourceBash = core.NS.BashTool

    def source_bash(context, provider='openai'):
        if not hasattr(context,'_source_git_bash'):
            context._source_git_bash = SourceBash(model_provider=provider)
        return context._source_git_bash

    class BashProxy(core.Tool):
        def __init__(self,model_provider=None):
            super().__init__(model_provider)
            self.context = core.current()
        def get_name(self):
            return 'bash'
        def get_description(self):
            return ('Run real commands in the existing Git Bash within the current independent repository. '
                    'State persists across calls. stdout, stderr, exit status and restart are real. '
                    'Use the declared product Python and available native tools; deployment commands '
                    'remain subject to the common owner resource and path guard.')
        def get_parameters(self):
            return source_bash(self.context,self.model_provider).get_parameters()
        async def execute(self,arguments):
            answer = await source_bash(self.context,self.model_provider).execute(arguments)
            self.context.check_protected()
            return answer
        async def close(self):
            if hasattr(self.context,'_source_git_bash'):
                return await self.context._source_git_bash.close()

    # The author selector's packaged editor contains UndoEdit; main editor does not.
    # Load that complete class and result types byte-for-byte via AST, with only
    # filesystem validation and directory-shell deployment callbacks replaced.
    editor_dir = core.TRAE/'evaluation/patch_selection/trae_selector/tools/tools'
    edns = {'__name__':'enagent_author_packaged_editor', 'dataclass':dataclass,
            'fields':fields,'replace':replace,'defaultdict':defaultdict,'Path':Path,
            'Literal':Literal,'get_args':get_args,'SNIPPET_LINES':4,
            'maybe_truncate':core.NS.maybe_truncate}
    module = types.ModuleType(edns['__name__'])
    import sys
    sys.modules[module.__name__] = module
    module.__dict__.update(edns)
    edns = module.__dict__
    for filename,names in [('base.py',{'ToolResult','CLIResult','ToolError'}),
                           ('edit.py',{'Command','EditTool'})]:
        path = editor_dir/filename
        nodes = []
        for node in ast.parse(path.read_text(encoding='utf-8')).body:
            name = getattr(node,'name',None)
            if isinstance(node,ast.Assign):
                name = next((t.id for t in node.targets if isinstance(t,ast.Name)),None)
            if name in names:
                nodes.append(node)
                source_rows.append({'source':str(path),'symbol':name,'start':node.lineno,
                    'end':node.end_lineno,'SHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'AST_exact':True})
        code = ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),*nodes],type_ignores=[])
        exec(compile(ast.fix_missing_locations(code),str(path),'exec'),edns)

    async def editor_shell(command):
        context = core.current()
        # Only normalize the Windows path inside the source-generated find command.
        if command.startswith('find ') and ' -maxdepth ' in command:
            path,tail = command[5:].split(' -maxdepth ',1)
            command = 'find ' + shlex.quote(Path(path).as_posix()) + ' -maxdepth ' + tail
        source = source_bash(context)
        if source._session is None:
            source._session = OwnedGitSession()
            await source._session.start()
        answer = await source._session.run(command)
        return answer.error_code,answer.output or '',answer.error or ''
    edns['run'] = editor_shell
    SourceEditor = edns['EditTool']

    class ProtectedSourceEditor(SourceEditor):
        def validate_path(self,command,path):
            super().validate_path(command,path)
            context = core.current()
            context.edit_guard(context.root,path,command)

        def write_file(self,path,file):
            # Only the Windows write boundary varies; author content operations
            # and exact model arguments above this method remain unchanged.
            try:
                existing=path.is_file();before=path.read_bytes() if existing else b''
                without_crlf=before.replace(b'\r\n',b'')
                mixed=(b'\r\n' in before and (b'\n' in without_crlf or b'\r' in without_crlf)) or (b'\r' in without_crlf)
                if mixed:
                    note(event='original_editor_mixed_newline_fallback',path=str(path),original_behavior_preserved=True)
                    return SourceEditor.write_file(self,path,file)
                newline='\r\n' if b'\r\n' in before else '\n'
                path.write_text(file,newline=newline)
                note(event='windows_editor_newline_transport',path=str(path),existing=existing,newline_profile='CRLF' if newline=='\r\n' else 'LF',model_content_not_changed=True,author_content_operation_unchanged=True)
            except Exception as exc:
                raise edns['ToolError'](f'Ran into {exc} while trying to write to {path}') from None

    class EditorProxy(core.Tool):
        def __init__(self,model_provider=None):
            super().__init__(model_provider)
            self.context = core.current()
            if not hasattr(self.context,'_source_editor_with_undo'):
                self.context._source_editor_with_undo = ProtectedSourceEditor()
        def get_name(self):
            return 'str_replace_based_edit_tool'
        def get_description(self):
            return (core.NS.TextEditorTool(model_provider=self.model_provider).get_description()
                    + '\nUse command=undo_edit to undo the most recent edit to a file in this session.')
        def get_parameters(self):
            parameters = core.NS.TextEditorTool(model_provider=self.model_provider).get_parameters()
            for parameter in parameters:
                if parameter.name == 'command':
                    parameter.enum = list(get_args(edns['Command']))
                    parameter.description = 'Allowed commands: ' + ', '.join(parameter.enum)
            return parameters
        async def execute(self,arguments):
            try:
                arguments=dict(arguments)
                if path_map is not None and isinstance(arguments.get('path'),str):
                    arguments['path']=path_map(self.context.root,arguments['path'])
                answer = await self.context._source_editor_with_undo(**arguments)
                self.context.check_protected()
                output=neutral_output(self.context.root,answer.output) if neutral_output is not None and answer.output else answer.output
                error=neutral_output(self.context.root,answer.error) if neutral_output is not None and answer.error else answer.error
                return core.NS.ToolExecResult(output=output,error=error,
                                               error_code=1 if answer.error else 0)
            except edns['ToolError'] as exc:
                return core.NS.ToolExecResult(error=str(exc),error_code=1)

    OldSession = core.NativeSession
    class ClosingNativeSession(OldSession):
        def close(self):
            if hasattr(self.context,'_source_git_bash'):
                asyncio.run(self.context._source_git_bash.close())

    core.NativeBash = BashProxy
    core.GuardedEditor = EditorProxy
    core.NativeSession = ClosingNativeSession
    core.NS.tools_registry['bash'] = BashProxy
    core.NS.tools_registry['str_replace_based_edit_tool'] = EditorProxy
    note(event='source_preserving_Git_Bash_shim_installed',actual_model=0,
         preserved=['Original BashTool.execute/parameters/restart','Original packaged EditTool including UndoEdit',
                    'Original ToolExecutor','Context-local persistent tools','Original selector session close'],
         source_editor_mapping=source_rows)
    return {'BashProxy':BashProxy,'EditorProxy':EditorProxy,'editor_source_mapping':source_rows}

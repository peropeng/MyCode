"""Physical public callbacks for EnAgent; no execution or provider calls on import."""
import ast
import copy
import hashlib
import json
import re
import shlex
from pathlib import Path

from environment166 import EngineeringError


class IllegalTool(ValueError):
    pass


class Bridge175:
    GENERATED_DIRS = {'generated_tests', 'tmp_tests', 'tests_tmp', 'enagent_tests',
                      'self_generated_tests', '.enagent_tests'}

    def __init__(self, env):
        self.env = env
        self.owned = Path(env.out).resolve()
        self.initial = env.business_files()
        self.original_paths = set(env._original)
        self.protected = self.original_paths - set(self.initial)
        if not self.protected:
            raise EngineeringError('NONEMPTY_ORIGINAL_PROTECTED_PATH_CERTIFICATE_REQUIRED')
        self.receipts = []
        self.engineering_error = None
        self.directory_views_filtered = False
        self._immutable = self._asset_state()
        self._number = 0

    def _record(self, stage, value):
        self.receipts.append({'stage': stage, **copy.deepcopy(value)})
        self.env.record('enagent_bridge_' + stage, value)

    def _fatal(self, reason):
        self.engineering_error = str(reason)
        self._record('engineering_unknown', {'reason': self.engineering_error})
        raise EngineeringError(self.engineering_error)

    def raise_if_failed(self):
        """Transport must call this before paying again if ToolExecutor swallowed a tool error."""
        if self.engineering_error:
            raise EngineeringError(self.engineering_error)

    def _asset_state(self):
        q = self.env.run.qualify
        inventories = {'frozen': q.inventory(self.env._paths['frozen']),
                       'old_template': q.inventory(self.env._paths['template'])}
        seal = self.env.ref.get('binding_seal')
        if seal:
            bindings = json.loads(Path(seal).read_text('utf-8-sig')).get('sha256', {})
            inventories['bound_assets'] = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
                                          for p in bindings}
            if any(inventories['bound_assets'][p] != expected for p, expected in bindings.items()):
                raise EngineeringError('BOUND_ORIGINAL_ASSET_SHA_DRIFT')
        return hashlib.sha256(json.dumps(inventories, sort_keys=True,
                                         separators=(',', ':')).encode()).hexdigest()

    def _check_assets(self):
        self.raise_if_failed()
        actual = self._asset_state()
        if actual != self._immutable:
            self._fatal('ORIGINAL_SOURCE_OR_FROZEN_ASSET_DRIFT')
        return actual

    def _root(self, root):
        supplied = Path(root)
        if supplied.is_symlink():
            raise IllegalTool('SYMLINK_CLONE_ROOT')
        root = supplied.resolve()
        if root == self.owned or not root.is_relative_to(self.owned) or not root.is_dir():
            raise IllegalTool('ROOT_OUTSIDE_OWNED_ADAPTER_CLONES')
        return root

    def _path(self, root, path):
        root = self._root(root); p = Path(path)
        p = p if p.is_absolute() else root / p
        if p.is_symlink():
            raise IllegalTool('SYMLINK_TOOL_PATH')
        p = p.resolve()
        if not p.is_relative_to(root):
            raise IllegalTool('TOOL_PATH_OUTSIDE_CLONE')
        return root, p, p.relative_to(root).as_posix()

    def _generated(self, rel):
        parts = Path(rel).parts
        return (rel not in self.original_paths and '.git' not in parts
                and (any(p in self.GENERATED_DIRS for p in parts)
                     or bool(re.fullmatch(r'test_[^/]+\.py', parts[-1] if parts else ''))))

    def _business(self, rel):
        return (not self._generated(rel) and rel not in self.protected
                and self.env._core.is_business('repo/' + rel))

    def visible_paths(self, root, directory):
        """Use in the mechanical directory-view wrapper instead of raw rglob output."""
        root, directory, _ = self._path(root, directory)
        visible = set()
        for p in directory.rglob('*'):
            if not p.is_file() or p.is_symlink():
                continue
            rel = p.relative_to(root).as_posix()
            if self._business(rel) or self._generated(rel):
                visible.add(p)
                for parent in p.parents:
                    if parent == directory:
                        break
                    if parent.is_relative_to(directory):
                        visible.add(parent)
        return [str(p) for p in sorted(visible) if len(p.relative_to(directory).parts) <= 2]

    def edit_guard(self, root, path, command):
        before = self._check_assets()
        try:
            root, p, rel = self._path(root, path)
            if command not in {'view', 'create', 'str_replace', 'insert', 'undo_edit'}:
                raise IllegalTool('EDITOR_COMMAND_NOT_ALLOWLISTED')
            if command == 'view' and p.is_dir():
                if not self.visible_paths(root, p):
                    raise IllegalTool('DIRECTORY_HAS_NO_VISIBLE_BUSINESS_OR_OWN_GENERATED_TEST')
                if not self.directory_views_filtered:
                    raw = [x for x in p.rglob('*') if len(x.relative_to(p).parts) <= 2
                           and not any(s.startswith('.') for s in x.relative_to(p).parts)]
                    allowed = set(self.visible_paths(root, p))
                    if any(str(x) not in allowed for x in raw):
                        raise IllegalTool('UNFILTERED_DIRECTORY_VIEW_WOULD_EXPOSE_PROTECTED_NAMES')
            elif not (self._business(rel) or self._generated(rel)):
                raise IllegalTool('ORIGINAL_TEST_PRIVATE_REFERENCE_OR_NONBUSINESS_PATH')
            self._record('edit_guard', {'root': str(root), 'path': rel, 'command': command,
                                         'allowed': True, 'immutable_sha256': before})
            return True
        finally:
            self._check_assets()

    def _clone_business(self, root):
        root = self._root(root); result = {}
        for p in root.rglob('*'):
            if p.is_symlink():
                raise IllegalTool('SYMLINK_IN_ACTOR_CLONE')
            if not p.is_file():
                continue
            rel = p.relative_to(root).as_posix()
            if '.git' in p.relative_to(root).parts:
                continue
            if rel in self.protected:
                expected = self.env._original[rel]
                if hashlib.sha256(p.read_bytes()).hexdigest() != expected:
                    self._fatal('ACTOR_MODIFIED_ORIGINAL_PROTECTED_FILE ' + rel)
                continue
            if self._generated(rel) or '__pycache__' in p.parts or '.pytest_cache' in p.parts:
                continue
            if not self._business(rel):
                raise IllegalTool('UNDECLARED_NONBUSINESS_ADDITION ' + rel)
            result[rel] = p.read_text('utf-8')
        if not set(self.initial) <= set(result):
            raise IllegalTool('DELETING_ORIGINAL_BUSINESS_FILES_IS_NOT_SUPPORTED_BY_PATCH_ABI')
        # Deleted protected assets are illegal even if not seen by rglob.
        if any(not (root / p).is_file() for p in self.protected):
            self._fatal('ACTOR_DELETED_ORIGINAL_PROTECTED_FILE')
        return result

    def snapshot_clone(self, root, label):
        before = self._check_assets(); current = self._clone_business(root); edits = []
        for rel, text in current.items():
            if rel not in self.initial:
                edits.append({'path': 'repo/' + rel, 'file_text': text})
            elif text != self.initial[rel]:
                if not self.initial[rel]:
                    raise IllegalTool('EMPTY_INITIAL_BUSINESS_FILE_CANNOT_USE_EXACT_SEARCH_ABI')
                edits.append({'path': 'repo/' + rel, 'old': self.initial[rel], 'new': text})
        if edits:
            row = self.env.apply_patch(edits, label, from_snapshot=self.env.initial_snapshot)
            legal = row.get('legal', {})
            if not legal.get('legal') or row.get('apply_errors'):
                self._fatal('ACTOR_BUSINESS_DIFF_PHYSICAL_APPLICATION_FAILED')
            snapshot = row['snapshot']
        else:
            self.env.restore(self.env.initial_snapshot); snapshot = copy.deepcopy(self.env.initial_snapshot)
        self._check_assets()
        actual = self.env.business_files()
        if actual != current:
            self._fatal('CLONE_TO_ENV_BUSINESS_BYTES_DO_NOT_MATCH')
        self._record('clone_materialization', {'root': str(self._root(root)), 'label': label,
                                               'changed_business_paths': [e['path'] for e in edits],
                                               'snapshot': snapshot, 'immutable_sha256': before,
                                               'tests_git_generated_scripts_excluded': True})
        return copy.deepcopy(snapshot)

    def _valid(self, record, generated=False):
        good = (record.get('executed') and record.get('guard_loaded')
                and record.get('business_state_unchanged') and record.get('frozen_tests_unchanged')
                and not record.get('timeout') and isinstance(record.get('exit_code'), int))
        good = good and (bool(record.get('actual_product_imports')) if generated
                         else bool(record.get('exact_test_coverage')))
        if not good:
            self._fatal('GENERATED_OR_PUBLIC_NATIVE_CERTIFICATE_UNKNOWN')

    def public_runner(self, root, ids):
        before = self._check_assets(); ids = list(ids)
        if not set(ids) <= set(self.env.public_regression_nodes):
            raise IllegalTool('PUBLIC_RUNNER_ONLY_ACCEPTS_FROZEN_ORDINARY_IDS')
        original = self.env.snapshot('bridge_public_entry'); self._number += 1
        try:
            snapshot = self.snapshot_clone(root, 'enagent_public_clone_' + str(self._number))
            result = self.env.run_regression(snapshot=snapshot, nodes=ids,
                                             label='enagent_public_' + str(self._number))
            native = result.get('native_record', {}); self._valid(native)
            outcomes = result.get('outcomes', {}); answer = {}
            for node in ids:
                status = outcomes.get(node, {}).get('status')
                if status not in {'passed', 'failed', 'error'}:
                    self._fatal('ORDINARY_PUBLIC_NODE_OUTCOME_UNKNOWN ' + node)
                answer[node] = 'PASS' if status == 'passed' else 'FAIL'
            self._record('public_runner', {'root': str(root), 'requested_ordinary_ids': ids,
                                          'ordinary_results_only': answer, 'native_record': native,
                                          'empty_only_if_caller_requested_empty': not ids,
                                          'immutable_sha256': before})
            return answer
        finally:
            self.env.restore(original); self._check_assets()

    def _generated_code(self, root, path):
        root, p, rel = self._path(root, path)
        if not self._generated(rel) or not p.is_file():
            raise IllegalTool('GENERATED_TEST_MUST_BE_NEW_OWNED_CLONE_FILE')
        return p.read_text('utf-8')

    def _check_python(self, code):
        tree = ast.parse(code)
        forbidden = {'os', 'subprocess', 'shutil', 'socket', 'requests', 'urllib',
                     'ctypes', 'importlib', 'pathlib', 'builtins', 'sys'}
        for n in ast.walk(tree):
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in n.names] if isinstance(n, ast.Import) else [n.module or '']
                if any(x.split('.')[0] in forbidden for x in names):
                    raise IllegalTool('GENERATED_SCRIPT_IMPORT_NOT_ALLOWLISTED')
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in {
                    'open', 'exec', 'eval', 'compile', '__import__', 'globals', 'locals',
                    'getattr', 'setattr', 'delattr'}:
                raise IllegalTool('GENERATED_SCRIPT_UNBOUNDED_FILESYSTEM_OR_DYNAMIC_EXECUTION')
            if isinstance(n, ast.Attribute) and (n.attr.startswith('__') or n.attr in {
                    'open', 'read_text', 'read_bytes', 'write_text', 'write_bytes', 'unlink',
                    'remove', 'rmdir', 'rmtree', 'mkdir', 'makedirs', 'chdir', 'system',
                    'popen', 'Popen', 'exec', 'eval', 'load', 'save', 'loadtxt', 'fromfile', 'memmap'}):
                raise IllegalTool('GENERATED_SCRIPT_EXTERNAL_IO_OR_REFLECTION_NOT_ALLOWED')
        return code

    def command_runner(self, root, command):
        before = self._check_assets(); original = self.env.snapshot('bridge_command_entry')
        self._number += 1
        try:
            root = self._root(root)
            # Parse tokens, never pass actor command text to a shell.
            tokens = shlex.split(command, posix=True)
            if not tokens or any(c in command for c in ('\n', '\r', '&&', '||', '`')):
                raise IllegalTool('COMPOUND_OR_EMPTY_COMMAND_NOT_ALLOWED')
            op = tokens[0]; snapshot = self.snapshot_clone(root, 'enagent_command_' + str(self._number))
            generated = False; pytest_generated = False; code = None
            if op in {'python', 'python3', 'python.exe'}:
                args = tokens[1:]
                if len(args) == 2 and args[0] == '-c':
                    code = self._check_python(args[1]); generated = True
                elif len(args) == 1:
                    code = self._check_python(self._generated_code(root, args[0])); generated = True
                elif len(args) >= 2 and args[:2] == ['-m', 'pytest']:
                    op = 'pytest'; tokens = ['pytest', *args[2:]]
                else:
                    raise IllegalTool('PYTHON_COMMAND_NOT_ALLOWLISTED')
            if op in {'pytest', 'pytest_owned_generated'} and not generated:
                args = [t for t in tokens[1:] if t not in {'-q', '-v', '-vv', '-s'}]
                if len(args) == 1 and self._generated(Path(args[0]).as_posix()):
                    code = self._check_python(self._generated_code(root, args[0])); generated = True; pytest_generated = True
                elif all(a in self.env.public_regression_nodes or a in self.env.recovery_goal_nodes for a in args):
                    result = self.env.run_regression(snapshot=snapshot,
                                                     label='enagent_command_public_' + str(self._number))
                    native = result.get('native_record', {}); self._valid(native)
                    log = Path(native['log']).read_text('utf-8', errors='replace')
                    answer = {'returncode': int(native['exit_code']), 'stdout': log, 'stderr': ''}
                else:
                    raise IllegalTool('PYTEST_REQUIRES_FROZEN_PUBLIC_IDS_OR_OWN_GENERATED_TEST')
            elif op in {'pwd', 'ls', 'cat', 'head', 'tail', 'grep', 'rg', 'find'}:
                if any(t.split('=', 1)[0] in {'--pre', '--pre-glob', '--files-from'} for t in tokens):
                    raise IllegalTool('READONLY_COMMAND_EXTERNAL_PROCESS_OR_PATH_LIST_OPTION')
                result = self.env.run_readonly_shell(command)
                if result.get('status') == 'READONLY_SHELL_REJECTED':
                    raise IllegalTool('READONLY_SHELL_BOUNDARY_REJECTED')
                answer = {'returncode': int(result.get('exit_code', 1)),
                          'stdout': result.get('stdout', ''), 'stderr': result.get('stderr', '')}
            elif not generated and op not in {'pytest', 'pytest_owned_generated'}:
                raise IllegalTool('COMMAND_NOT_IN_MECHANICAL_ALLOWLIST')
            if generated:
                if pytest_generated:
                    code += '\nif __name__ == "__main__":\n import pytest\n raise SystemExit(pytest.main([__file__, "-q", "-p", "no:cacheprovider"]))\n'
                result = self.env.run_reproduction(code, snapshot=snapshot,
                                                   label='enagent_generated_' + str(self._number))
                self._valid(result.get('native_record', {}), generated=True)
                answer = {'returncode': int(result['exit_code']), 'stdout': result.get('stdout', ''),
                          'stderr': result.get('stderr', '')}
                self._record('generated_native', {'root': str(root), 'command': command,
                                                  'native_record': result['native_record'],
                                                  'marker_not_invented': True})
            self._record('command', {'root': str(root), 'command': command, 'actual_result': answer,
                                     'immutable_sha256': before})
            return answer
        except (IllegalTool, SyntaxError, ValueError) as exc:
            answer = {'returncode': 2, 'stdout': '', 'stderr': 'ToolError: ' + str(exc)}
            self._record('command_rejected', {'command': command, 'actual_result': answer})
            return answer
        finally:
            self.env.restore(original); self._check_assets()

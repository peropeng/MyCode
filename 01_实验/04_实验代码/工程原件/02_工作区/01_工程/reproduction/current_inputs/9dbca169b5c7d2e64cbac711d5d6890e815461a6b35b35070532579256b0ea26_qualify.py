"""Expand genuine editor-prefix regressions under frozen repository-native tests.

No source shell commands or official repair patches are executed. Every task,
attempt, environment failure and exact edit replay is retained. Selection is
fixed by qualification_protocol.json, never by any diagnostic method outcome.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
MAIN = WORKTREE.parents[1]
OLD = MAIN / '实验/实验127_完整恢复方法可行性'
SCRATCH = WORKTREE / 'scratch/recovery'
PACKAGES = {'getmoto/moto': 'moto', 'pydantic/pydantic': 'pydantic', 'python/mypy': 'mypy',
            'dask/dask': 'dask', 'Project-MONAI/MONAI': 'monai', 'pandas-dev/pandas': 'pandas',
            'conan-io/conan': 'conans', 'iterative/dvc': 'dvc'}
PYCACHE_PARTS = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.hypothesis'}
_codec_spec = importlib.util.spec_from_file_location('exp129_source_codec', Path(__file__).with_name('source_codec.py'))
CODEC = importlib.util.module_from_spec(_codec_spec)
_codec_spec.loader.exec_module(CODEC)


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inventory(root):
    return {p.relative_to(root).as_posix(): sha(p.read_bytes()) for p in sorted(Path(root).rglob('*'))
            if p.is_file() and not set(p.parts).intersection(PYCACHE_PARTS)}


def blob(data):
    if data is None:
        return None
    key = sha(data)
    path = HERE / 'blobs' / key
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return {'sha256': key, 'bytes': len(data), 'blob': f'blobs/{key}'}


def safe_path(root, rel):
    path = (root / rel).resolve()
    if not path.is_relative_to(root.resolve()) or '.git' in path.parts:
        raise ValueError('path outside candidate state')
    return path


def business(rel, package):
    return rel.startswith(f'repo/{package}/') and rel.endswith('.py') and not any(v in rel.split('/') for v in ('test', 'tests'))


def test_path(path):
    return (path.startswith(('tests/', 'test-data/', 'mypy/test/', 'conans/test/'))
            or '/tests/' in path or path == 'conftest.py')


def execute(argv, cwd, log, timeout=120, env=None):
    started = time.monotonic()
    if env is None:
        env = {k: os.environ[k] for k in ('SystemRoot', 'WINDIR', 'SYSTEMDRIVE', 'PATH', 'TEMP', 'TMP', 'USERPROFILE', 'LOCALAPPDATA') if k in os.environ}
    try:
        p = subprocess.run([str(v) for v in argv], cwd=cwd, env=env, capture_output=True, timeout=timeout)
        output, code, timed_out = p.stdout + b'\n[STDERR]\n' + p.stderr, p.returncode, False
    except subprocess.TimeoutExpired as error:
        output, code, timed_out = (error.stdout or b'') + b'\n[TIMEOUT]\n' + (error.stderr or b''), None, True
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_bytes(output)
    return {'argv': [str(v) for v in argv], 'cwd': str(cwd), 'exit_code': code, 'timeout': timed_out,
            'seconds': time.monotonic() - started, 'log': str(log), 'log_sha256': sha(output)}


def choose_python(task):
    if task.get('native_interpreter_override'):
        return Path(task['native_interpreter_override'])
    repo = task['repository']
    if repo == 'getmoto/moto':
        return MAIN / '工作区/0922-recovery-audit/.venv/Scripts/python.exe'
    if repo == 'pydantic/pydantic':
        config = subprocess.run(['git', '-C', task['repo_path'], 'show', task['base_commit'] + ':pyproject.toml'],
                                capture_output=True, check=True).stdout.decode()
        version = re.search(r'pydantic-core==([\d.]+)', config).group(1)
        return SCRATCH / f'envs/pydantic-{version}/Scripts/python.exe'
    if repo == 'iterative/dvc':
        return SCRATCH / f'envs/dvc-{task["task_id"].rsplit("-", 1)[-1]}/Scripts/python.exe'
    return SCRATCH / f'envs/{PACKAGES[repo]}/Scripts/python.exe'


def isolated_env(root, repo, frozen, output, python, package):
    for name in ('home', 'tmp'):
        (root / name).mkdir(exist_ok=True)
    aws = root / 'home/empty_aws_config'
    aws.write_bytes(b'')
    env = {k: os.environ[k] for k in ('SystemRoot', 'WINDIR', 'SYSTEMDRIVE') if k in os.environ}
    env.update({'PATH': str(python.parent) + os.pathsep + str(Path(os.environ.get('SystemRoot', 'C:/Windows')) / 'System32'),
                'HOME': str(root / 'home'), 'USERPROFILE': str(root / 'home'), 'APPDATA': str(root / 'home'),
                'LOCALAPPDATA': str(root / 'home'), 'TEMP': str(root / 'tmp'), 'TMP': str(root / 'tmp'),
                'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONNOUSERSITE': '1',
                'PYTHONPATH': os.pathsep.join((str(HERE), str(repo), str(frozen))),
                'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1', 'AWS_ACCESS_KEY_ID': 'testing', 'AWS_SECRET_ACCESS_KEY': 'testing',
                'AWS_SECURITY_TOKEN': 'testing', 'AWS_SESSION_TOKEN': 'testing', 'AWS_DEFAULT_REGION': 'us-east-1',
                'AWS_EC2_METADATA_DISABLED': 'true', 'AWS_CONFIG_FILE': str(aws), 'AWS_SHARED_CREDENTIALS_FILE': str(aws),
                'BOTO_CONFIG': str(aws), 'NO_PROXY': '*', 'CUDA_VISIBLE_DEVICES': '-1', 'OMP_NUM_THREADS': '1',
                'MKL_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'EXP129_FROZEN_ROOT': str(frozen),
                'EXP129_SOURCE_ROOT': str(repo), 'EXP129_PACKAGE': package,
                'EXP129_GUARD_EVENTS': str(output / 'guard_events.jsonl'), 'EXP129_GUARD_READY': str(output / 'guard_ready.json'),
                'EXP129_OUTCOMES': str(output / 'outcomes.json'), 'MYPY_TEST_PREFIX': str(frozen),
                'HYPOTHESIS_STORAGE_DIRECTORY': str(root / 'tmp/hypothesis'), 'PYTHONHASHSEED': '0'})
    return env


def probe(root, frozen, nodes, output, python, package, deadline, collect=False):
    root, frozen, output = root.resolve(), frozen.resolve(), output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    if time.monotonic() >= deadline:
        return {'status': 'qualification_time_budget_exhausted', 'executed': False}
    env = isolated_env(root, root / 'repo', frozen, output, python, package)
    args = [python, '-m', 'pytest', '-p', 'qualification_plugin', '-p', 'no:cacheprovider', '-q',
            '--disable-warnings', '--import-mode=importlib', '--continue-on-collection-errors',
            '-o', 'addopts=', '--rootdir', frozen]
    if package in ('mypy', 'conans', 'dvc'):
        # Historical mypy data collectors require pytest 6.x. Plain assertion
        # execution avoids that pytest version's Python 3.11 rewrite AST gap.
        args.append('--assert=plain')
    if collect:
        args.append('--collect-only')
        args += nodes
    else:
        # Windows CreateProcess has a ~32K command-line limit. Keep exact node
        # identity and order in an immutable per-probe selector read by plugin.
        selector = output / 'selected_nodes.json'
        write(selector, nodes)
        env['EXP129_SELECTED_NODES'] = str(selector)
        args += list(dict.fromkeys(n.split('::')[0] for n in nodes))
    before, frozen_before = inventory(root / 'repo'), inventory(frozen)
    run = execute(args, frozen, output / 'pytest.log', min(120, max(0.1, deadline - time.monotonic())), env)
    run.update(executed=True, guard_loaded=(output / 'guard_ready.json').exists(),
               business_state_unchanged=before == inventory(root / 'repo'),
               frozen_tests_unchanged=frozen_before == inventory(frozen),
               pytest=read(output / 'outcomes.json') if (output / 'outcomes.json').exists() else {},
               requested_nodes=nodes, phase='collection' if collect else 'native_test')
    if (output / 'guard_events.jsonl').exists():
        run['guard_events'] = [json.loads(s) for s in (output / 'guard_events.jsonl').read_text('utf-8').splitlines()]
    write(output / 'run.json', run)
    return run


def prepare(task, root, evidence, test_patch):
    repo = root / 'repo'
    commands = [('clone', ['git', 'clone', '--shared', '--no-checkout', task['repo_path'], repo], root),
                ('checkout', ['git', '-c', 'core.autocrlf=false', 'checkout', '--detach', task['base_commit']], repo)]
    for name, command, cwd in commands:
        result = execute(command, cwd, evidence / f'{name}.log')
        if result['exit_code'] != 0:
            raise RuntimeError('Git preparation failed: ' + name)
    frozen = root / 'frozen_tests'
    shutil.copytree(repo, frozen, ignore=shutil.ignore_patterns('.git', '__pycache__', '.pytest_cache'))
    # Frozen copy has package-shaped test directories. It is NOT a product import source.
    changed = re.findall(r'^\+\+\+ b/(.+)$', test_patch, re.M)
    if not changed or any(not test_path(p) for p in changed):
        raise RuntimeError('Official test_patch contains non-test or unsupported paths')
    patch_path = evidence / 'official_test_patch.diff'
    patch_path.write_bytes(test_patch.encode())
    before = inventory(frozen)
    for name, command in [('frozen_git_init', ['git', 'init', frozen]),
                          ('apply_test', ['git', '-C', frozen, 'apply', patch_path]),
                          ('reverse_test_check', ['git', '-C', frozen, 'apply', '--reverse', '--check', patch_path])]:
        result = execute(command, root, evidence / f'{name}.log')
        if result['exit_code'] != 0:
            raise RuntimeError('Frozen test preparation failed: ' + name)
    after = inventory(frozen)
    actual = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    if set(actual) != set(changed):
        raise RuntimeError('Official test patch changed unexpected files')
    write(evidence / 'test_patch_application.json', {'expected': changed, 'actual': actual, 'test_patch_sha256': sha(test_patch.encode())})
    write(evidence / 'frozen_test_inventory.json', after)
    return frozen, after


def canonical_replace(before, after):
    """Normalize actual insert/undo into an exact, uniquely anchored delta."""
    if before == after:
        raise ValueError('No effective change')
    left = 0
    while left < min(len(before), len(after)) and before[left] == after[left]:
        left += 1
    right = 0
    while right < min(len(before) - left, len(after) - left) and before[-1 - right] == after[-1 - right]:
        right += 1
    stop = len(before) - right
    a, b = left, stop
    while not before[a:b] or before.count(before[a:b]) != 1:
        a = max(0, a - 32)
        b = min(len(before), b + 32)
        if a == 0 and b == len(before):
            break
    old = before[a:b]
    new = before[a:left] + after[left:len(after) - right if right else len(after)] + before[stop:b]
    if not old or before.count(old) != 1 or before.replace(old, new, 1) != after:
        raise RuntimeError('Could not represent actual edit as a unique exact text replacement')
    return {'old_str': old, 'new_str': new, 'context_character_count': len(old)}


def apply_call(root, call, history, messages):
    if call['path_scope'] == 'repository':
        rel = 'repo/' + call['repository_relative_path']
    elif call['path_scope'] == 'workspace_external_to_repository':
        rel = 'workspace/' + call['parameters']['path'].removeprefix('/workspace/')
    else:
        raise RuntimeError('Unsupported edit path scope ' + call['path_scope'])
    path = safe_path(root, rel)
    before = path.read_bytes() if path.is_file() else None
    record = {'call_id': call['call_id'], 'call_index': call['call_index'], 'message_index': call['message_index'],
              'state_path': rel, 'source_command': call['command'], 'source_parameters': call['parameters'],
              'serialized_parameters': call.get('serialized_parameters', call['parameters']),
              'parameter_codec': call.get('parameter_codec', 'legacy_raw'),
              'source_outcome': call['source_edit_outcome'], 'before': blob(before)}
    if call['source_edit_outcome'] == 'explicitly_rejected':
        record.update(status='observed_rejected_no_delta', after=record['before'])
        return record
    command, params = call['command'], call['parameters']
    if command == 'undo_edit':
        index = call.get('response_message_index')
        response = str(messages[index].get('content', '')) if index is not None else ''
        if not re.search(r'undone|undo.*success', response, re.I) or re.search(r'no.*edit history|error:', response, re.I):
            raise RuntimeError('Undo source response does not establish successful undo')
        if not history.get(rel):
            raise RuntimeError('Undo has no faithfully reconstructed file history')
        after = history[rel].pop()
        if before is None or after is None:
            raise RuntimeError('Undo of creation/deletion needs separate file-existence replay semantics')
        replacement = canonical_replace(before.decode(), after.decode())
        effective = {'old_str': replacement['old_str'], 'new_str': replacement['new_str']}
        record.update(command='str_replace', original_parameters=effective,
                      normalization='actual source undo reconstructed from file-local history; unique exact replacement',
                      canonical_context_characters=replacement['context_character_count'])
    else:
        if call['source_edit_outcome'] != 'reported_success':
            raise RuntimeError('Missing/unclassified source edit outcome at call ' + str(call['call_index']))
        if command == 'create':
            if before is not None:
                raise RuntimeError('Create target already exists')
            after = params['file_text'].encode()
            record.update(command='create', original_parameters=params)
        elif command == 'str_replace':
            old = params['old_str']
            if before is None or not old or before.decode().count(old) != 1:
                raise RuntimeError('Recorded old_str is missing or nonunique at call ' + str(call['call_index']))
            after = before.decode().replace(old, params.get('new_str', ''), 1).encode()
            record.update(command='str_replace', original_parameters=params)
        elif command == 'insert':
            if before is None:
                raise RuntimeError('Insert target missing')
            text = before.decode()
            lines = text.split('\n')
            line = int(params['insert_line'])
            if line < 0 or line > len(lines):
                raise RuntimeError('Recorded insert line outside file')
            after = '\n'.join(lines[:line] + params['new_str'].split('\n') + lines[line:]).encode()
            replacement = canonical_replace(text, after.decode())
            record.update(command='str_replace', original_parameters={'old_str': replacement['old_str'], 'new_str': replacement['new_str']},
                          normalization='actual line insertion after insert_line; unique exact replacement',
                          canonical_context_characters=replacement['context_character_count'])
        else:
            raise RuntimeError('Unsupported editor command ' + command)
        history.setdefault(rel, []).append(before)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(after)
    record.update(status='applied_exact_recorded_edit', after=blob(after))
    return record


def apply_literal_shell(root, call, task, messages):
    """Rebuild only proven literal echo writes to nonbusiness public scripts.

    This does not run a shell. Shell expansion and business-file writes are
    rejected, and the original successful command/response remains evidence.
    """
    command = call['command'].strip()
    if not re.match(r'^echo\s+[\"\']', command):
        return None
    if '$' in command or '`' in command:
        raise RuntimeError('Literal echo contains shell expansion syntax')
    tokens = shlex.split(command, posix=True)
    if len(tokens) != 4 or tokens[0] != 'echo' or tokens[2] != '>':
        raise RuntimeError('Unsupported echo write form; exact literal reconstruction unavailable')
    raw_path = tokens[3]
    parts = raw_path.split('/')
    inside = len(parts) > 3 and parts[1] == 'workspace' and parts[2].startswith(task['repository'].replace('/', '__') + '__')
    if inside:
        rel = 'repo/' + '/'.join(parts[3:])
    elif raw_path.startswith('/workspace/'):
        rel = 'workspace/' + raw_path.removeprefix('/workspace/')
    else:
        raise RuntimeError('Literal echo target is outside known public workspace')
    if business(rel, PACKAGES[task['repository']]):
        raise RuntimeError('Shell business writes are outside strict editor replay scope')
    index = call.get('response_message_index')
    response = str(messages[index].get('content', '')) if index is not None else ''
    if 'Command finished with exit code 0' not in response:
        raise RuntimeError('Literal echo success is not established by source response')
    path = safe_path(root, rel)
    before = path.read_bytes() if path.is_file() else None
    after = (tokens[1] + '\n').encode()
    record = {'call_id': call['call_id'], 'call_index': call['call_index'], 'message_index': call['message_index'],
              'state_path': rel, 'source_command': 'execute_bash', 'source_parameters': call['parameters'],
              'serialized_parameters': call.get('serialized_parameters', call['parameters']),
              'parameter_codec': call.get('parameter_codec', 'legacy_raw'),
              'source_outcome': 'recorded shell exit 0', 'before': blob(before),
              'normalization': 'literal POSIX echo without -e; no shell execution or substitutions; nonbusiness file only'}
    if before == after:
        record.update(status='observed_success_no_delta', after=record['before'])
        return record
    if before is None:
        record.update(command='create', original_parameters={'file_text': after.decode()})
    else:
        replacement = canonical_replace(before.decode(), after.decode())
        record.update(command='str_replace', original_parameters={k: replacement[k] for k in ('old_str', 'new_str')})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(after)
    record.update(status='applied_exact_recorded_edit', after=blob(after))
    return record


def environment_failure(detail, edit, package):
    if any(s in detail for s in ('EXP129 native-test guard blocked', 'Unable to locate credentials', 'NoRegionError',
                                  'EndpointConnectionError', 'fixture ', 'DLL load failed', 'binary incompatibility')):
        return True
    missing = re.search(r"ModuleNotFoundError: No module named ['\"]([^'\"]+)", detail)
    if missing:
        return not (missing.group(1).startswith(package + '.') and missing.group(1) in edit['original_parameters'].get('new_str', ''))
    return False


def source_failures(run, selected_nodes, prior_pass, edit, package):
    failures = {}
    for node, outcome in run.get('pytest', {}).get('outcomes', {}).items():
        if node in prior_pass and outcome.get('status') in ('failed', 'error') and not environment_failure(outcome.get('detail', ''), edit, package):
            failures[node] = {'kind': 'native_test_' + outcome['status'], 'outcome': outcome}
    # A selected, formerly passing native test may fail to collect because an
    # actual source edit causes a product syntax/name/import error. This is a
    # failed test command, not an invented executed assertion. Keep that mode.
    for error in run.get('pytest', {}).get('collection_errors', []):
        detail = error['detail']
        source_file = edit['state_path'].removeprefix('repo/').replace('/', '\\')
        product_trace = source_file in detail.replace('/', '\\')
        causal_error = any(s in detail for s in ('SyntaxError', 'IndentationError', 'NameError', 'ModuleNotFoundError', 'ImportError'))
        if not product_trace or not causal_error or environment_failure(detail, edit, package):
            continue
        for node in selected_nodes:
            if node in prior_pass and node.split('::')[0] == error['nodeid'].split('::')[0]:
                failures[node] = {'kind': 'native_test_collection_error', 'outcome': error}
    return failures


def resolve_node(node, available, indices):
    if node in available:
        return [node]
    matches = [n for n in available if n.startswith(node)]
    if matches:
        return matches
    base, marker, parameter = node.partition('[')
    if not marker or not parameter.endswith(']'):
        return []
    parameter = parameter[:-1]
    parts = parameter.split('-')
    constraints, pattern = {}, []
    for part in parts:
        match = re.fullmatch(r'([A-Za-z_]\w*?)(\d+)', part)
        if match:
            name, index = match.group(1), int(match.group(2))
            if any(name in v for k, v in indices.items() if k.startswith(base + '[')):
                constraints[name] = index
                pattern.append('.+?')
                continue
        pattern.append(re.escape(part))
    if not constraints:
        return []
    identity_pattern = re.compile('^' + '-'.join(pattern) + '$')
    return [n for n in available if n.startswith(base + '[')
            and all(indices.get(n, {}).get(k) == v for k, v in constraints.items())
            and identity_pattern.fullmatch(n.partition('[')[2][:-1])]


def make_manifest(task, calls, ledger, root, frozen, chosen, messages, python, evidence=None):
    evidence = Path(evidence) if evidence is not None else HERE / 'tasks' / task['task_id']
    visible = evidence / 'visible'
    visible.mkdir(exist_ok=False)
    call = next(c for c in calls if c['call_index'] == chosen['cutoff_call_index'])
    end = call['response_message_index'] if call['response_message_index'] is not None else call['message_index']
    feedback = {n: chosen['failures'][n]['outcome'] for n in chosen['visible_target_tests']}
    write(visible / 'source_prefix.json', {'task_id': task['task_id'], 'sft_index': task['sft_index'],
          'messages': messages[:end + 1], 'cutoff_message_index': end,
          'new_failure_observation': {'origin': 'Exp129 fixed-native-test prefix scan', 'visible_target_feedback': feedback}})
    write(visible / 'edits.json', chosen['edits'])
    # Selected prefix may precede a subsequently observed repair. Restore its
    # exact recorded bytes before exposing the single fixed task state.
    all_paths = {r['state_path'] for r in ledger['replay'] if r.get('status') == 'applied_exact_recorded_edit'}
    first = {}
    for r in ledger['replay']:
        if r.get('status') == 'applied_exact_recorded_edit':
            first.setdefault(r['state_path'], r['before'])
    final = dict(first)
    for r in chosen['edits']:
        final[r['state_path']] = r['after']
    for rel in all_paths:
        path = safe_path(root, rel)
        ref = final.get(rel)
        if ref is None:
            if path.exists():
                path.unlink()
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((HERE / ref['blob']).read_bytes())
    frozen_inventory = read(evidence / 'frozen_test_inventory.json')
    manifest = {'schema': 'Exp129-qualified-task/1.0', 'task_id': task['task_id'], 'repository': task['repository'],
                'package': PACKAGES[task['repository']], 'checkpoint': ledger['checkpoint'],
                'asset_root': str(HERE), 'qualification_evidence': str(evidence), 'guard_source_root': str(HERE),
                'failure_prefix': {'call_index': chosen['cutoff_call_index'], 'message_index': end, 'source_prefix': 'visible/source_prefix.json'},
                'initial_regression_call_index': chosen['initial_regression_call_index'],
                'post_regression_business_edits': chosen['post_regression_business_edits'],
                'source_is_historical_moto_reference': task['task_id'] in ('getmoto__moto-5134', 'getmoto__moto-5286', 'getmoto__moto-6352'),
                'visible_target_tests': chosen['visible_target_tests'], 'hidden_preservation_tests': chosen['hidden_preservation_tests'],
                'qualification_preceding_pass_evidence': chosen['prior_pass_witness'],
                'target_failure_modes': {n: chosen['failures'][n]['kind'] for n in chosen['visible_target_tests']},
                'frozen_tests': {'path': str(frozen), 'inventory': 'frozen_test_inventory.json', 'inventory_sha256': sha((evidence / 'frozen_test_inventory.json').read_bytes())},
                'runtime_source_root': str(root / 'repo'), 'native_interpreter': str(python),
                'qualification_is_new_observation': True, 'not_original_agent_test_execution': True,
                'original_issue_repair_is_not_the_target': True, 'official_reference_patch_used': False,
                'protocol_sha256': ledger['protocol_sha256'],
                'parameter_codec': ledger.get('parameter_codec', 'legacy_raw'),
                'qualification_protocol_path': str(task.get('qualification_protocol_path', HERE / 'qualification_protocol.json')),
                'method_forbidden': ['future messages/edits', 'preceding pass or culprit labels', 'official reference patch', 'hidden preservation feedback'],
                'environment_substitution': 'Recorded shell commands are accounted but not executed; fixed native test interpreter imports exact reconstructed product source.'}
    write(evidence / 'task_manifest.json', manifest)
    write(evidence / 'failure_modified_state.json', {r['state_path']: r['after'] for r in chosen['edits']})
    write(evidence / 'failure_repo_inventory.json', inventory(root / 'repo'))
    if inventory(frozen) != frozen_inventory:
        raise RuntimeError('Frozen test bytes drifted while sealing state')


def qualify(task, test_patch, messages, attempt='v1', budget=600):
    tid, package = task['task_id'], PACKAGES[task['repository']]
    root = SCRATCH / 'qualification' / attempt / tid
    evidence = HERE / 'tasks' / tid
    if evidence.exists():
        evidence = HERE / 'attempts' / attempt / tid
    root.mkdir(parents=True, exist_ok=False)
    evidence.mkdir(parents=True, exist_ok=False)
    for filename in ('qualify.py', 'source_codec.py', 'qualification_plugin.py', 'sitecustomize.py', 'qualification_protocol.json'):
        source = HERE / filename
        if source.is_file():
            destination = evidence / 'execution_source' / filename
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())
    started = time.monotonic()
    deadline = started + budget
    call_file = Path(task.get('call_mapping_path', OLD / 'call_mapping.jsonl'))
    calls = [json.loads(s) for s in call_file.read_text('utf-8').splitlines() if json.loads(s)['task_id'] == tid]
    ledger = {'task_id': tid, 'repository': task['repository'], 'attempt': attempt, 'status': 'running',
              'checkpoint': {'base_commit': task['base_commit'], 'base_tree': task['base_tree']['stdout'], 'source_repo': task['repo_path']},
              'replay': [], 'probes': [], 'shell_accounting': [], 'prefix_candidates': [],
              'api_calls': 0, 'official_reference_patch_used': False, 'qualification_budget_seconds': budget,
              'parameter_codec': CODEC.CODEC_ID,
              'protocol_sha256': sha(Path(task.get('qualification_protocol_path', HERE / 'qualification_protocol.json')).read_bytes())}
    chosen = None
    try:
        # Uniform representation-level inverse before any matching or tests.
        # Unsupported serialized values block the task; no fallback stripping.
        calls = [CODEC.decode_call(call) for call in calls]
        python = choose_python(task)
        ledger['native_interpreter'] = str(python)
        if not python.exists():
            raise FileNotFoundError('Prepared native interpreter unavailable: ' + str(python))
        frozen, frozen_hashes = prepare(task, root, evidence, test_patch)
        official = list(dict.fromkeys(task['FAIL_TO_PASS'] + task['PASS_TO_PASS']))
        files = list(dict.fromkeys(n.split('::')[0] for n in official))
        supplements = [p for p in ('mypy/test/testgraph.py', 'mypy/test/testutil.py') if package == 'mypy' and (frozen / p).is_file()]
        collection = probe(root, frozen, list(dict.fromkeys(files + supplements)), evidence / 'probes/collection', python, package, deadline, True)
        ledger['probes'].append(collection)
        if collection.get('exit_code') != 0 or not collection.get('guard_loaded') or not collection.get('business_state_unchanged'):
            raise RuntimeError('Initial environment or collection blocked; inspect collection log')
        available = collection['pytest']['collected']
        mapping, resolutions = {}, []
        for node in official:
            matches = resolve_node(node, available, collection['pytest'].get('collected_parameter_indices', {}))
            resolutions.append({'original_swegym_node': node, 'candidate_collected_nodes': matches,
                                'unique': len(matches) == 1, 'whole_parameter_group_expanded': False,
                                'resolution_mode': 'exact' if node in available else 'unique_prefix' if any(n.startswith(node) for n in available) else 'named_parameter_indices_and_static_display',
                                'collected_parameter_indices': {n: collection['pytest'].get('collected_parameter_indices', {}).get(n, {}) for n in matches},
                                'selected_from_test_outcomes': False})
            write(evidence / 'node_mapping_audit.json', {'resolution_before_prefix_outcomes': True, 'nodes': resolutions})
            if len(matches) != 1:
                raise RuntimeError(f'Nonunique or unavailable official node {node}: {len(matches)} matches')
            mapping[node] = matches[0]
        extra = []
        for file in supplements:
            extra += sorted(n for n in available if n.split('::')[0] == file)[:20]
        selected = list(dict.fromkeys(list(mapping.values()) + extra))
        preservation_pool = set(mapping[n] for n in task['PASS_TO_PASS']) | set(extra)
        write(evidence / 'frozen_test_selection.json', {'official_mapping': mapping, 'supplemental_native_nodes': extra,
              'all_selected_nodes': selected, 'selection_before_prefix_outcomes': True,
              'nodeid_resolution': 'exact, unique prefix, or same named callspec parameter indices and unchanged nongenerated parameter display'})
        baseline = probe(root, frozen, selected, evidence / 'probes/base', python, package, deadline)
        ledger['probes'].append(baseline)
        if baseline.get('timeout') or not baseline.get('guard_loaded') or not baseline.get('business_state_unchanged'):
            raise RuntimeError('Base native tests blocked or timed out')
        prior = {n: {'probe': 'base', 'last_call_index': -1} for n, r in baseline['pytest'].get('outcomes', {}).items() if r.get('status') == 'passed'}
        if not preservation_pool.intersection(prior):
            raise RuntimeError('No passing fixed native preservation baseline')
        ledger['baseline_passed_nodes'] = sorted(prior)
        history, initial, after_count = {}, None, 0
        for call in calls:
            if time.monotonic() >= deadline:
                raise RuntimeError('Qualification task time budget exhausted')
            if call['function'] == 'execute_bash':
                literal = apply_literal_shell(root, call, task, messages)
                if literal is not None:
                    ledger['replay'].append(literal)
                    write(evidence / 'replay_audit.json', ledger['replay'])
                ledger['shell_accounting'].append({'call_index': call['call_index'], 'command': call['command'],
                                                  'handling': 'literal nonbusiness script write reconstructed without shell' if literal is not None else 'not executed; source observation/environment command retained; fixed native probe replaces execution'})
                continue
            if not call['state_edit_attempt']:
                continue
            edit = apply_call(root, call, history, messages)
            ledger['replay'].append(edit)
            write(evidence / 'replay_audit.json', ledger['replay'])
            if edit['status'] != 'applied_exact_recorded_edit' or not business(edit['state_path'], package):
                continue
            label = f'after_call_{call["call_index"]:03d}'
            current = probe(root, frozen, selected, evidence / 'probes' / label, python, package, deadline)
            ledger['probes'].append(current)
            if not current.get('business_state_unchanged') or not current.get('frozen_tests_unchanged'):
                raise RuntimeError('Native tests changed product source or frozen test bytes')
            outcomes = current.get('pytest', {}).get('outcomes', {})
            failures = source_failures(current, selected, prior, edit, package)
            passing = {n for n, r in outcomes.items() if r.get('status') == 'passed'}
            preserved = sorted(passing.intersection(prior))
            preserved_native = passing.intersection(prior).intersection(preservation_pool)
            candidate = {'call_index': call['call_index'], 'regressed_tests': sorted(failures),
                         'preserved_native_count': len(preserved_native), 'guard_loaded': current.get('guard_loaded'),
                         'timeout': current.get('timeout'), 'qualification_met': bool(failures and preserved_native and current.get('guard_loaded') and not current.get('timeout'))}
            ledger['prefix_candidates'].append(candidate)
            if initial is None and candidate['qualification_met']:
                initial = {'call_index': call['call_index'], 'targets': set(failures), 'preservation': set(preserved),
                           'witness': copy.deepcopy(prior)}
                after_count = 0
            elif initial is not None:
                after_count += 1
            if initial is not None:
                still_failing = sorted(initial['targets'].intersection(failures))
                still_preserved = sorted(initial['preservation'].intersection(passing))
                qualifies_extended = still_failing and preservation_pool.intersection(still_preserved) and current.get('guard_loaded') and not current.get('timeout')
                if qualifies_extended:
                    chosen = {'initial_regression_call_index': initial['call_index'], 'cutoff_call_index': call['call_index'],
                              'post_regression_business_edits': after_count, 'visible_target_tests': still_failing,
                              'hidden_preservation_tests': sorted(passing.intersection(prior)), 'failures': copy.deepcopy(failures),
                              'prior_pass_witness': {n: initial['witness'][n] for n in still_failing},
                              'edits': copy.deepcopy([r for r in ledger['replay'] if r['status'] == 'applied_exact_recorded_edit'])}
                if not still_failing or after_count >= 2:
                    break
            for node in passing:
                prior[node] = {'probe': label, 'last_call_index': call['call_index']}
            write(evidence / 'qualification_ledger.json', ledger)
        if chosen is not None:
            # A repaired later prefix is inspection evidence only, never input.
            make_manifest(task, calls, ledger, root, frozen, chosen, messages, python, evidence)
            ledger['status'] = 'qualified'
            ledger['evidence_directory'] = str(evidence)
            ledger['selected_state'] = {k: v for k, v in chosen.items() if k not in ('edits', 'failures')}
        else:
            ledger['status'] = 'not_qualified_no_fixed_regression_with_native_preservation'
    except Exception as error:
        ledger.update(status='blocked', blocker=f'{type(error).__name__}: {error}')
        if chosen is not None:
            ledger['qualified_candidate_before_block'] = {k: v for k, v in chosen.items() if k not in ('edits', 'failures')}
            write(evidence / 'selected_state_pending_recovery.json', chosen)
    ledger['elapsed_seconds'] = time.monotonic() - started
    write(evidence / 'qualification_ledger.json', ledger)
    write(evidence / 'replay_audit.json', ledger['replay'])
    print(json.dumps({k: ledger.get(k) for k in ('task_id', 'status', 'blocker', 'elapsed_seconds')}, ensure_ascii=False), flush=True)
    return ledger


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tasks', nargs='+')
    parser.add_argument('--repository')
    parser.add_argument('--population', type=Path)
    parser.add_argument('--attempt', default='v1')
    parser.add_argument('--budget', type=float, default=600)
    args = parser.parse_args()
    import pyarrow.parquet as pq
    population = read(args.population if args.population else OLD / 'task_ledger.json')
    if args.repository:
        population = [r for r in population if r['repository'] == args.repository]
    if args.tasks:
        population = [r for r in population if r['task_id'] in args.tasks]
    # Explicit projection excludes official repair patch and any responsibility fields.
    metadata = {r['instance_id']: r['test_patch'] for r in pq.read_table(MAIN / '工作区/0922-recovery-audit/swegym.parquet',
                                                                      columns=['instance_id', 'test_patch']).to_pylist()}
    messages = pq.read_table(population[0]['sft_path'], columns=['messages']).to_pylist() if population else []
    for task in population:
        qualify(task, metadata[task['task_id']], messages[task['sft_index']]['messages'], args.attempt, args.budget)


if __name__ == '__main__':
    main()

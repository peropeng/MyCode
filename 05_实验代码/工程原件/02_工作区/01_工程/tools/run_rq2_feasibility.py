"""Finish the frozen EnAgent Dask selection without running any model again.

The archived AOrchestra pilot and Agentless/ours selections are already complete.
This entry only validates the EnAgent immutable business choice and performs
its missing independent acceptance. Private test material stays in the worker;
stdout contains scalar outcomes only. Original archives are never rewritten.
"""
from __future__ import annotations

import argparse
import ast
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback
import types
import urllib.request
import zipfile

ENGINE = Path(__file__).resolve().parents[1]
INPUTS = ENGINE / '.rebuild/paper-inputs'
EA = INPUTS / 'retained-experiments/rq2/experiment250/实验/实验250_EnAgent新任务概率性共同确认'
AOR = INPUTS / 'experiment261/CONTINUE_AFTER_USER2335'
TASK = 'dask__dask-9378'
TRIAL = EA / 'deployments' / TASK / 'trial1'
SELECTION = TRIAL / 'leases/lease_001/f' / TASK / 'ENAGENT_ICSE2026_FULL_N3_C200_S30_CONFIRMATION'
TASK_INPUT = INPUTS / 'rq2-experiment129/recovery/dask_lane/tasks' / TASK
HARNESS = INPUTS / 'rq2-experiment129/executor/rounds/06/harness' / TASK
OUT = ENGINE / '.rebuild/rq2-feasibility/enagent-dask-trial1'
BASE_COMMIT = '8b95f983c232c1bd628e9cba0695d3ef229d290b'
PATCH_SHA = '7ea58fb7fdaf7bf74a6de2160e4d4bf3c63a66fb45196e7f6114c8dbf8f613e5'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temporary, path)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def inventory(folder):
    return {p.relative_to(folder).as_posix(): sha(p) for p in Path(folder).rglob('*')
            if p.is_file() and not set(p.parts) & {'.git', '__pycache__', '.pytest_cache'}}


def public_preflight():
    contract = read(AOR / 'SCI_R7/ROOT_AUTHOR_RELEASE/contract.json')
    original = read(INPUTS / 'retained-experiments/rq2/experiment249/实验/实验249_固定顺序新任务共同确认/contracts' / TASK / 'public_contract.json')
    for key in ('task_id', 'input_digest', 'c0_business_paths_sha256', 'frozen_inventory',
                'public_target_nodes', 'ordinary_nodes'):
        if contract[key] != original[key]:
            raise RuntimeError('COMMON_INPUT_DRIFT:' + key)
    own_binding = read(TRIAL / 'selected_task_bindings240.json')['tasks'][0]
    if (own_binding['task_id'] != TASK or own_binding['input_digest'] != contract['input_digest']
            or own_binding['public_regression_nodes'] != contract['ordinary_nodes']):
        raise RuntimeError('ENAGENT_OWN_PUBLIC_BINDING_DRIFT')
    initial = read(SELECTION / 'snapshots/s0000/snapshot.json')
    if initial['inventory_sha256'] != digest(contract['template_inventory']):
        raise RuntimeError('ENAGENT_ACTUAL_INITIAL_SOURCE_NOT_COMMON_C0')
    flow = read(TRIAL / 'checkpoints' / TASK / 'FLOW_STATE.json')
    observed = flow['native_done']['initial_pass_baseline']['result']
    if (set(observed) != set(contract['public_target_nodes'] + contract['ordinary_nodes'])
            or not all(observed[n] == 'FAIL' for n in contract['public_target_nodes'])
            or not all(observed[n] == 'PASS' for n in contract['ordinary_nodes'])):
        raise RuntimeError('ENAGENT_ACTUAL_INITIAL_PUBLIC_G_O_MISMATCH')
    terminal = read(SELECTION / 'selected_await_external_private.json')
    snapshot = read(SELECTION / 'snapshots/s0334/snapshot.json')
    before = read(SELECTION / 'selection_before_hidden.json')
    if terminal['status'] != 'SELECTED_AWAIT_EXTERNAL_PRIVATE' or terminal['author_done'] is not True:
        raise RuntimeError('ENAGENT_NOT_NATURALLY_SELECTED')
    if terminal['final_snapshot'] != snapshot or before['snapshot'] != snapshot or not before['selected_before_hidden']:
        raise RuntimeError('ENAGENT_SELECTION_WITNESS_DRIFT')
    if terminal['enagent_core_result']['status'] != 'CORE_FINISHED_FINAL_ACCEPTANCE_NOT_RUN':
        raise RuntimeError('ENAGENT_ORIGINAL_COMPLETE_CORE_REQUIRED')
    stopped = read(TRIAL / 'supervision' / TASK / 'supervision.json')
    if stopped['status'] != 'STOPPED' or not stopped['all_owned_descendants_stopped'] or not stopped['own_Job_empty_before_close']:
        raise RuntimeError('ORIGINAL_ACTOR_STOP_NOT_COMPLETE')
    business = inventory(SELECTION / 'immutable_business_selection')
    if set(business) != set(contract['c0_business_paths_sha256']) or len(business) != 119:
        raise RuntimeError('ENAGENT_BUSINESS_SCOPE_DRIFT')
    changes = {p: h for p, h in business.items() if contract['c0_business_paths_sha256'][p] != h}
    if changes != snapshot['diff']:
        raise RuntimeError('ENAGENT_FROZEN_CHOICE_CHANGED')
    complete = {**contract['template_inventory'], **business}
    if digest(complete) != snapshot['inventory_sha256']:
        raise RuntimeError('ENAGENT_ORIGINAL_WHOLE_SNAPSHOT_MISMATCH')
    return contract, terminal, business, complete


def _safe_file(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or '\\' in relative or ':' in relative:
        raise RuntimeError('UNSAFE_FROZEN_PATH')
    return path


def _write_verified(root, relative, data, expected):
    if hashlib.sha256(data).hexdigest() != expected:
        raise RuntimeError('ORIGINAL_BYTES_NOT_RECOVERED')
    target = _safe_file(root, relative)
    if target.exists() and sha(target) != expected:
        raise RuntimeError('EXISTING_RESTORATION_CHANGED')
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_bytes(data)


def restore_original_trees(contract, business, whole):
    """Restore original bytes by recorded hashes, never synthesize test bodies."""
    candidate, frozen = OUT / 'runtime/repo', OUT / 'frozen_tests'
    candidate.mkdir(parents=True, exist_ok=True)
    frozen.mkdir(parents=True, exist_ok=True)
    wanted = set(whole.values()) | set(contract['frozen_inventory'].values())
    content = {}
    archive_path = AOR / 'RAW_CLOSED_ARTIFACT_ARCHIVE/SCI_R7_raw.zip'
    with zipfile.ZipFile(archive_path) as archive:
        for item in archive.infolist():
            if item.is_dir():
                continue
            data = archive.read(item)
            key = hashlib.sha256(data).hexdigest()
            if key in wanted:
                content.setdefault(key, data)
    for root in (INPUTS / 'rq2-experiment129/recovery/blobs', INPUTS / 'rq2-experiment129/recovery/dask_lane/blobs'):
        for key in wanted - set(content):
            path = root / key
            if path.is_file() and sha(path) == key:
                content[key] = path.read_bytes()
    for relative, expected in business.items():
        data = (SELECTION / 'immutable_business_selection' / relative).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise RuntimeError('SELECTED_SOURCE_CHANGED_DURING_MATERIALIZATION')
        content[expected] = data
    # The only unavailable original is the official masked-array test file.
    # Restore the pinned upstream version and apply the preserved official diff,
    # then require the original frozen digest before it can participate in tests.
    relative = 'dask/array/tests/test_masked.py'
    test_hash = contract['frozen_inventory'][relative]
    base_file = OUT / 'upstream_base_test_masked.bin'
    if not base_file.exists():
        url = f'https://raw.githubusercontent.com/dask/dask/{BASE_COMMIT}/{relative}'
        with urllib.request.urlopen(url, timeout=90) as response:
            base_file.write_bytes(response.read())
    if sha(base_file) != contract['template_inventory'][relative]:
        raise RuntimeError('ORIGINAL_UPSTREAM_TEST_BYTES_CHANGED')
    content[sha(base_file)] = base_file.read_bytes()
    if test_hash not in content:
        source = OUT / 'upstream_original'
        path = _safe_file(source, relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_bytes(base_file.read_bytes())
        patch = TASK_INPUT / 'official_test_patch.diff'
        if sha(patch) != PATCH_SHA:
            raise RuntimeError('ORIGINAL_OFFICIAL_PATCH_CHANGED')
        if sha(path) != test_hash:
            # Isolate git-apply from the enclosing thesis worktree: otherwise
            # Git silently skips paths outside this nested current directory.
            subprocess.run(['git', 'init', '--quiet', str(source)], check=True, capture_output=True)
            result = subprocess.run(['git', '-C', str(source), 'apply', '--whitespace=nowarn', str(patch)],
                                    capture_output=True, timeout=30)
            (OUT / 'original_test_restoration.log').write_bytes(result.stdout + result.stderr)
            if result.returncode or sha(path) != test_hash:
                raise RuntimeError('ORIGINAL_TEST_RESTORATION_NOT_EXACT')
        content[test_hash] = path.read_bytes()
    for root, expected_map in ((frozen, contract['frozen_inventory']), (candidate, whole)):
        for relative, expected in expected_map.items():
            if expected not in content:
                raise RuntimeError('REQUIRED_ORIGINAL_FILE_MISSING:' + relative)
            _write_verified(root, relative, content[expected], expected)
        if inventory(root) != expected_map:
            raise RuntimeError('RESTORED_FULL_INVENTORY_MISMATCH')
    return candidate.parent, frozen


def original_probe():
    qualifier = module('_rq2_feasibility_original_qualifier', HARNESS / 'qualify.py')
    original = INPUTS / 'rq2-experiment129/executor/run.py'
    tree = ast.parse(original.read_text(encoding='utf-8-sig'))
    names = {'assess_probe', 'probe'}
    definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    if {node.name for node in definitions} != names:
        raise RuntimeError('ORIGINAL_PROBE_SOURCE_LAYOUT_CHANGED')
    result = types.ModuleType('_rq2_feasibility_original_probe')
    result.__dict__.update(Path=Path, ast=ast, time=time, qualify=qualifier, load=read,
                           write=write, read_jsonl=lambda p: [json.loads(v) for v in Path(p).read_text(encoding='utf-8-sig').splitlines() if v])
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(original), 'exec'), result.__dict__)
    return result


class CurrentAcceptanceOwner:
    def __init__(self):
        self.started = time.monotonic()
        self.protocol = {'budget': {'flow_wall_seconds': 900, 'native_timeout_seconds': 300}}
        self.calls = 0
        self.unknown = None

    def require_action(self, kind, allow_no_new=False):
        if kind not in ('native', 'observe') or self.unknown or self.time_left() <= 0:
            raise RuntimeError('CURRENT_INDEPENDENT_ACCEPTANCE_SCOPE')

    def reserve_native(self):
        self.calls += 1
        if self.calls > 2:
            raise RuntimeError('ONE_PUBLIC_ONE_PRIVATE_ACCEPTANCE_ONLY')

    def time_left(self):
        return max(0, 900 - (time.monotonic() - self.started))

    def latch_unknown(self, error, stage):
        self.unknown = {'type': type(error).__name__, 'stage': stage, 'message': str(error)}

    def record(self, value):
        with (OUT / 'supervision.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(value, ensure_ascii=False) + '\n')


def worker(python, attempt):
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    contract, terminal, business, whole = public_preflight()
    active, frozen = restore_original_trees(contract, business, whole)
    current = OUT / 'native_attempts' / attempt
    current.mkdir(parents=True, exist_ok=True)
    binding = {'candidate_inventory': digest(whole), 'frozen_inventory': digest(contract['frozen_inventory']),
               'logical_python': str(Path(python).resolve()), 'launcher_sha256': sha(python),
               'runtime_config_sha256': sha(Path(python).parent.parent / 'pyvenv.cfg'),
               'qualifier_sha256': sha(INPUTS / 'rq2-experiment129/executor/rounds/06/harness/dask__dask-9378/qualify.py'),
               'probe_source_sha256': sha(INPUTS / 'rq2-experiment129/executor/run.py')}
    if (current / 'admission.json').exists():
        if read(current / 'admission.json') != binding:
            raise RuntimeError('EXISTING_ATTEMPT_INPUT_BINDING_CHANGED')
    else:
        write(current / 'admission.json', binding)
    sys.path.insert(0, str(AOR))
    winjob = module('_rq2_feasibility_original_winjob', AOR / 'winjob_pp.py')
    owner = CurrentAcceptanceOwner()
    probe = original_probe()

    def execute(argv, cwd, log, timeout=300, env=None):
        value = winjob.JobRunner(owner).execute(argv, cwd, log, timeout=min(300, timeout), env=env)
        stop = value['stop_receipt']
        value['stop_receipt'] = {**stop, 'root_process_stopped': stop['root_stopped'],
                                 'all_owned_descendants_terminated': bool(stop['own_Job_empty_before_close'] and stop['descendants_stopped'])}
        return value

    probe.qualify.execute = execute
    fresh = []

    def once(nodes, name):
        target = current / name
        if target.exists():
            receipt = target / 'run.json'
            if not receipt.is_file():
                raise RuntimeError('PRIOR_PROBE_DISPATCH_UNKNOWN_NO_AUTOMATIC_REEXECUTION')
            result = read(receipt)
            if (result.get('requested_nodes') != nodes or not result.get('completed_guarded_coverage')
                    or not result.get('stop_receipt', {}).get('all_owned_descendants_terminated')):
                raise RuntimeError('PRIOR_PROBE_INCOMPLETE_REVIEW_MECHANICAL_CAUSE')
            return result
        fresh.append(name)
        return probe.probe(active, frozen, nodes, target, Path(python), 'dask', time.monotonic() + 300)
    public_nodes = list(dict.fromkeys(contract['public_target_nodes'] + contract['ordinary_nodes']))
    public = once(public_nodes, 'public_acceptance')
    public_known = bool(public['completed_guarded_coverage'] and public['stop_receipt']['all_owned_descendants_terminated'])
    outcomes = public.get('pytest', {}).get('outcomes', {})
    goals_pass = public_known and all(outcomes[n]['status'] == 'passed' for n in contract['public_target_nodes'])
    ordinary_pass = public_known and all(outcomes[n]['status'] == 'passed' for n in contract['ordinary_nodes'])
    # This is the first read of private selector metadata, in a child process
    # without any model credentials/client. Never expose names or raw logs.
    original_final = INPUTS / 'retained-experiments/rq2/experiment251/实验/实验251_Agentless完整参数新任务共同确认/final_acceptance_SOURCE/private_ROOT/AGENTLESS_FULL' / TASK / 'trial1'
    selector_source = original_final / 'actual_private_ROOT_ONLY/selected_nodes.json'
    private_nodes = read(selector_source)
    if not private_nodes or len(private_nodes) != len(set(private_nodes)):
        raise RuntimeError('ORIGINAL_INDEPENDENT_SCOPE_UNAVAILABLE')
    trusted = read(original_final / 'WORKER_COMPLETED_PRIVATE_ROOT_ONLY.json')
    if digest(private_nodes) != trusted['original_private_scope_SHA256']:
        raise RuntimeError('ORIGINAL_INDEPENDENT_SCOPE_CHANGED')
    private = None
    if public_known and goals_pass and ordinary_pass:
        private = once(private_nodes, 'independent_acceptance_ROOT_ONLY')
    private_known = bool(private and private['completed_guarded_coverage'] and private['stop_receipt']['all_owned_descendants_terminated'])
    private_pass = bool(private and private['passed']) if private_known else None
    if inventory(active / 'repo') != whole or inventory(frozen) != contract['frozen_inventory']:
        raise RuntimeError('FINAL_CANDIDATE_OR_FROZEN_TEST_BYTES_CHANGED')
    scalar = {'method': 'EnAgent', 'task_id': TASK, 'trial_id': 'trial1', 'public_known': public_known,
              'goal_passed': bool(goals_pass) if public_known else None,
              'ordinary_passed': bool(ordinary_pass) if public_known else None,
              'independent_acceptance_known': private_known, 'private_passed': private_pass,
              'natural_success': (False if public_known and not (goals_pass and ordinary_pass)
                                  else bool(private_pass) if private_known else None),
              'old_fixed30_resource_success': False, 'old_30minute_record_unchanged': True,
              'selected_business_count': len(business), 'original_selection_unchanged': True,
              'private_feedback_to_method': False, 'new_model_requests': 0,
              'actual_independent_acceptance_runs': int(private is not None),
              'current_physical_attempt': attempt, 'fresh_product_native_runs_this_invocation': len(fresh),
              'current_acceptance_elapsed_seconds': time.monotonic() - started,
              'prior_author_elapsed_seconds': terminal['elapsed_seconds'],
              'prior_model_requests': terminal['LLM_calls'], 'prior_output_tokens': terminal['output_tokens'],
              'private_scope_source': 'restored original Agentless selected_nodes.json, bound to original Root scope certificate',
              'original_independent_scope_exactly_preserved': True,
              'original_166_full_manifest_recovered': False,
              'migration_runtime': True, 'runtime_byte_identity_to_archived_environment_claimed': False,
              'all_owned_processes_stopped': not owner.unknown and all(
                  r['stop_receipt']['all_owned_descendants_terminated'] for r in (public, private) if r)}
    write(OUT / 'SCALAR_RESULT.json', scalar)
    return scalar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('preflight', 'prepare', 'run', '_prepare', '_worker'))
    parser.add_argument('--python', type=Path, required=True)
    parser.add_argument('--attempt', default='attempt001')
    args = parser.parse_args()
    if not args.attempt.replace('_', '').replace('-', '').isalnum():
        parser.error('attempt must be a plain name')
    if args.command == 'preflight':
        _, terminal, business, _ = public_preflight()
        print(json.dumps({'candidate_business_files': len(business), 'selected_candidate_unchanged': True,
                          'author_natural_terminal': True, 'prior_model_requests': terminal['LLM_calls'],
                          'runtime_exists': args.python.is_file(), 'next': 'independent acceptance only'}, ensure_ascii=False))
        return
    if args.command == '_worker':
        try:
            scalar = worker(args.python.resolve(), args.attempt)
            print(json.dumps(scalar, ensure_ascii=False))
        except BaseException as error:
            frames = [{'line': f.lineno, 'function': f.name} for f in traceback.extract_tb(error.__traceback__)
                      if Path(f.filename).resolve() == Path(__file__).resolve()]
            write(OUT / 'DIAGNOSTIC_PUBLIC.json', {'status': 'ENGINEERING_UNKNOWN',
                  'error_type': type(error).__name__, 'framework_frames': frames,
                  'model_requests': 0, 'private_details_exposed': False})
            raise
        return
    if args.command == '_prepare':
        contract, _, business, whole = public_preflight()
        OUT.mkdir(parents=True, exist_ok=True)
        active, frozen = restore_original_trees(contract, business, whole)
        if inventory(active / 'repo') != whole or inventory(frozen) != contract['frozen_inventory']:
            raise RuntimeError('PREPARED_INPUT_BYTES_DO_NOT_MATCH_ORIGINAL')
        write(OUT / 'PREPARED_PUBLIC_SCALARS.json', {'selected_business_files': len(business),
              'whole_selected_snapshot_matches': True, 'frozen_test_inventory_matches': True,
              'private_tests_executed': 0, 'API_requests': 0})
        return
    if (OUT / 'SCALAR_RESULT.json').exists():
        print(json.dumps(read(OUT / 'SCALAR_RESULT.json'), ensure_ascii=False))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    child = {k: os.environ[k] for k in ('SystemRoot', 'WINDIR', 'SYSTEMDRIVE', 'PATH', 'TEMP', 'TMP') if k in os.environ}
    child.update(PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    with (OUT / 'worker_ROOT_ONLY.log').open('ab') as log:
        result = subprocess.run([sys.executable, '-X', 'utf8', str(Path(__file__).resolve()), '_prepare' if args.command == 'prepare' else '_worker', '--python', str(args.python.resolve()), '--attempt', args.attempt],
                                cwd=ENGINE, env=child, stdout=log, stderr=subprocess.STDOUT, timeout=1000,
                                creationflags=0x08000000 if os.name == 'nt' else 0)
    if result.returncode:
        print(json.dumps(read(OUT / 'DIAGNOSTIC_PUBLIC.json') if (OUT / 'DIAGNOSTIC_PUBLIC.json').exists() else
                         {'status': 'INDEPENDENT_ACCEPTANCE_ENGINEERING_UNKNOWN', 'model_requests': 0,
                          'raw_log_retained_ROOT_ONLY': str(OUT / 'worker_ROOT_ONLY.log')}))
        raise SystemExit(result.returncode)
    print(json.dumps(read(OUT / ('PREPARED_PUBLIC_SCALARS.json' if args.command == 'prepare' else 'SCALAR_RESULT.json')), ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()

"""Independent ROOT acceptance of a sealed public-only control selection.

The controller prints scalars only. Private selectors, native logs and individual
outcomes remain in a credential-free child and ROOT-only output directory.
Neither this entry nor its worker imports a model client. A completed acceptance
is reused; an unresolved dispatch is never automatically repeated.

For 5516 the original EnAgent ROOT certificate is byte-bound by the original
fixed-five report. Other tasks require --scope-binding JSON with task_id,
certificate_path and certificate_sha256. The certificate must contain its actual
raw_native_result.requested_nodes and a completed guarded ROOT result; a merely
declared test count or unbound manifest is never accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ENGINE = Path(__file__).resolve().parents[1]
INPUTS = ENGINE / '.rebuild/paper-inputs'
BASE = ENGINE / '.rebuild/rq2-controls'
sys.path.insert(0, str(ENGINE / 'src'))
from thesis_recovery.rq2_control_env import digest, inventory, native_callback, read, save, sha

FIXED_FIVE = INPUTS / 'experiment244/evidence/工作区/1011-five-continue/FULLRUN_FIXED_FIVE_COMPARISON.json'
FIXED_FIVE_SHA = 'd18628729f5f5ef8f5e4c2fed92d618f31f15fc476d575595a76f5f706e0e0fc'
ROOT_5516 = INPUTS / ('experiment244/evidence/工作区/1011-five-continue/'
    'enagent_checkpoint_pathfix_SOURCE/root_final_runtime_assets_SOURCE/'
    'run/getmoto__moto-5516/result.json')


class AdmissionError(RuntimeError):
    """Fixed public reason code, with no private content in its message."""


def require(value, code):
    if not value:
        raise AdmissionError(code)


def safe(root, relative):
    root = Path(root).resolve()
    require(isinstance(relative, str) and relative and '\\' not in relative
            and ':' not in relative, 'UNSAFE_RELATIVE_PATH')
    path = (root / relative).resolve()
    require(path.is_relative_to(root), 'PATH_OUTSIDE_ROOT')
    return path


def plain(value):
    return bool(value and value.replace('_', '').replace('-', '').isalnum())


def paths(args, spec):
    require(plain(spec['task_id']) and plain(args.trial), 'INVALID_TASK_OR_TRIAL')
    run = BASE / 'runs' / spec['task_id'] / args.trial / args.condition
    out = BASE / 'private_ROOT' / spec['task_id'] / args.trial / args.condition
    return run, out


def public_admission(args):
    """Verify public immutable selection; do not access a private selector."""
    spec = read(args.case)
    run, out = paths(args, spec)
    require(not (run / 'producer.lock').exists(), 'METHOD_ACTOR_NOT_STOPPED')
    result = read(run / 'RESULT.json')
    require(result.get('status') == 'COMPLETED', 'METHOD_TERMINAL_NOT_COMPLETE')
    require(result.get('condition') == args.condition and result.get('trial') == args.trial,
            'METHOD_RESULT_IDENTITY_CHANGED')
    require(not result.get('hidden_calls_in_adapter') and not result.get('new_Gold'),
            'METHOD_PRIVATE_BOUNDARY_CHANGED')
    selection = read(run / 'SELECTED_PUBLIC_ONLY.json')
    require(selection == result.get('selection') and selection.get('uses_hidden') is False,
            'SELECTION_WITNESS_CHANGED')
    snapshot = result['final_snapshot']
    require(snapshot == selection.get('snapshot'), 'FINAL_SELECTION_CHANGED')
    archive = Path(snapshot['archive_path']).resolve()
    require(archive.is_relative_to((run / 'snapshots').resolve()), 'SNAPSHOT_OUTSIDE_RUN')
    snapshot_witness = archive / 'snapshot.json'
    if snapshot['id'] == 'C0' and not snapshot_witness.exists():
        # The adapter persists C0 business bytes and its condition binding, but
        # only writes snapshot.json for generated candidates.
        require(snapshot.get('diff') == {} and snapshot.get('label') == 'current_condition_C0',
                'INITIAL_SNAPSHOT_WITNESS_CHANGED')
    else:
        require(read(snapshot_witness) == snapshot, 'SNAPSHOT_WITNESS_CHANGED')
    texts = read(archive / 'business_source.json')
    require(texts == read(run / 'selected_business_source.json'), 'SELECTED_SOURCE_CHANGED')
    require(set(texts) == set(spec['business_hashes']) and all(isinstance(v, str) for v in texts.values()),
            'SELECTED_BUSINESS_SCOPE_CHANGED')
    selected = {p: hashlib.sha256(v.encode('utf-8')).hexdigest() for p, v in texts.items()}
    selected_witness = selection['reason']['terminal_guard']['selected_source_sha256']
    require(selected == selected_witness, 'SELECTED_HASH_WITNESS_CHANGED')
    support = {p: h for p, h in spec.get('support_hashes', {}).items() if p not in selected}
    whole = {**support, **selected}
    require(digest(whole) == snapshot['inventory_sha256'], 'FINAL_WHOLE_SNAPSHOT_CHANGED')
    require({p: h for p, h in selected.items() if h != spec['business_hashes'][p]} == snapshot['diff'],
            'FINAL_DIFF_CHANGED')
    original = read(spec['original_contract'])
    require(original['task_id'] == spec['task_id'] and
            original['c0_business_paths_sha256'] == spec['business_hashes'], 'COMMON_C0_CHANGED')
    require(original['frozen_inventory'] == spec['frozen_inventory'], 'ORIGINAL_FROZEN_INVENTORY_CHANGED')
    require(original['public_target_nodes'] == spec['goal_nodes'] and
            original['ordinary_nodes'] == spec['ordinary_nodes'], 'COMMON_PUBLIC_SCOPE_CHANGED')
    require(all(original['template_inventory'].get(p) == h for p, h in support.items()),
            'ORIGINAL_SUPPORT_CHANGED')
    require(inventory(Path(spec['frozen_root'])) == spec['frozen_inventory'], 'FROZEN_BYTES_CHANGED')
    for relative, expected in support.items():
        require(sha(safe(spec['support_root'], relative)) == expected, 'SUPPORT_BYTES_CHANGED')
    if snapshot['id'] == 'C0':
        require(selected == spec['business_hashes'], 'INITIAL_SELECTED_SOURCE_CHANGED')
    witness_files = [args.case, run / 'RESULT.json', run / 'SELECTED_PUBLIC_ONLY.json',
                     run / 'selected_business_source.json',
                     archive / 'business_source.json', Path(spec['original_contract'])]
    if snapshot_witness.exists():
        witness_files.append(snapshot_witness)
    binding = {'task_id': spec['task_id'], 'trial': args.trial, 'condition': args.condition,
               'files': {str(Path(p).resolve()): sha(p) for p in witness_files},
               'selected_business_sha256': digest(selected), 'whole_inventory_sha256': digest(whole),
               'frozen_inventory_sha256': digest(spec['frozen_inventory']),
               'python': str(Path(spec['python']).resolve()), 'launcher_sha256': sha(spec['python']),
               'runtime_config_sha256': sha(Path(spec['python']).parent.parent / 'pyvenv.cfg'),
               'qualifier_sha256': sha(Path(spec['native_harness']) / 'qualify.py'),
               'plugin_sha256': sha(Path(spec['native_harness']) / 'qualification_plugin.py'),
               'probe_source_sha256': sha(INPUTS / 'rq2-experiment129/executor/run.py'),
               'job_runner_sha256': sha(INPUTS / 'experiment261/CONTINUE_AFTER_USER2335/winjob_pp.py'),
               'adapter_sha256': sha(ENGINE / 'src/thesis_recovery/rq2_control_env.py'),
               'acceptance_script_sha256': sha(__file__),
               'scope_binding_sha256': sha(args.scope_binding) if args.scope_binding else None}
    return spec, run, out, texts, selected, support, whole, binding


def original_scope(spec, args):
    """Only called inside the child, after the method's immutable selection."""
    task = spec['task_id']
    if args.scope_binding:
        binding = read(args.scope_binding)
        require(binding.get('task_id') == task, 'ORIGINAL_SCOPE_TASK_MISMATCH')
        certificate = Path(binding['certificate_path'])
        expected = binding.get('certificate_sha256')
        require(isinstance(expected, str) and len(expected) == 64, 'ORIGINAL_SCOPE_CERTIFICATE_UNBOUND')
        chain = {'kind': 'explicit_original_ROOT_certificate', 'binding_file': str(args.scope_binding.resolve()),
                 'binding_file_sha256': sha(args.scope_binding)}
    else:
        require(task == 'getmoto__moto-5516', 'ORIGINAL_HASH_BOUND_SCOPE_REQUIRED')
        require(sha(FIXED_FIVE) == FIXED_FIVE_SHA, 'ORIGINAL_REPORT_CHANGED')
        row = next(v for v in read(FIXED_FIVE)['rows'] if v['task_id'] == task)
        expected = row['ENAGENT']['final_result_SHA256']
        certificate = ROOT_5516
        chain = {'kind': 'original_244_EnAgent_actual_ROOT_requested_nodes',
                 'anchor_path': str(FIXED_FIVE), 'anchor_sha256': FIXED_FIVE_SHA,
                 'anchor_row_task': task, 'anchor_method': 'ENAGENT'}
    require(sha(certificate) == expected, 'ORIGINAL_ROOT_CERTIFICATE_CHANGED')
    cert = read(certificate)
    if cert.get('task_id') is None and args.scope_binding:
        anchor = Path(binding['terminal_packet_path'])
        require(sha(anchor) == binding['terminal_packet_sha256'], 'ORIGINAL_TERMINAL_PACKET_CHANGED')
        packet = read(anchor)
        suffix = '/' + task + '/' + '/'.join(certificate.as_posix().split('/' + task + '/', 1)[1:])
        require(packet.get('task_id') == task and packet.get('complete') is True
                and str(packet.get('raw_external_result', '')).replace('\\', '/').endswith(suffix),
                'ORIGINAL_SCOPE_TASK_ANCHOR_MISMATCH')
        chain['terminal_packet_path'] = str(anchor)
        chain['terminal_packet_sha256'] = sha(anchor)
    else:
        require(cert.get('task_id') == task, 'ORIGINAL_SCOPE_TASK_MISMATCH')
    require(cert.get('status') == 'COMPLETE_EXTERNAL_ONCE_PRIVATE'
            and cert.get('private_attempts') == 1, 'ORIGINAL_ROOT_CERTIFICATE_INCOMPLETE')
    raw = cert['raw_native_result']
    require(raw.get('executed') and raw.get('guard_loaded') and raw.get('business_state_unchanged')
            and raw.get('frozen_tests_unchanged') and not raw.get('timeout'),
            'ORIGINAL_ROOT_COVERAGE_UNKNOWN')
    old_stop = raw.get('stop_receipt', {})
    require(old_stop.get('all_owned_descendants_terminated') or
            (old_stop.get('root_stopped') and old_stop.get('descendants_stopped')
             and old_stop.get('own_Job_empty_before_close')),
            'ORIGINAL_ROOT_STOP_UNKNOWN')
    nodes = raw.get('requested_nodes')
    require(isinstance(nodes, list) and nodes and all(isinstance(v, str) for v in nodes)
            and len(nodes) == len(set(nodes)), 'ORIGINAL_ACTUAL_SCOPE_UNAVAILABLE')
    public = set(spec['goal_nodes'] + spec['ordinary_nodes'])
    require(public.issubset(nodes), 'ORIGINAL_AND_CURRENT_PUBLIC_SCOPE_DIFFER')
    private = [n for n in nodes if n not in public]
    require(private, 'ORIGINAL_INDEPENDENT_SCOPE_EMPTY')
    chain.update(certificate_path=str(certificate), certificate_sha256=expected,
                 actual_nodes_sha256=digest(nodes), private_nodes_sha256=digest(private),
                 scope_exactly_reused=True, missing_scope_hash_fallback_used=False)
    return nodes, private, chain


def copy_runtime(out, spec, texts, support, whole):
    repo = out / 'runtime/repo'
    frozen = out / 'frozen_tests'
    for root, expected_map in ((repo, whole), (frozen, spec['frozen_inventory'])):
        root.mkdir(parents=True, exist_ok=True)
        for relative, expected in expected_map.items():
            target = safe(root, relative)
            if target.exists():
                require(sha(target) == expected, 'ROOT_EXISTING_BYTES_CHANGED')
                continue
            if root == repo and relative in texts:
                raw = texts[relative].encode('utf-8')
            else:
                origin = spec['support_root'] if root == repo else spec['frozen_root']
                raw = safe(origin, relative).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == expected, 'ROOT_SOURCE_BYTES_CHANGED')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        require(inventory(root) == expected_map, 'ROOT_MATERIALIZED_INVENTORY_CHANGED')
    return repo.parent, frozen


def worker(args):
    spec, run, out, texts, selected, support, whole, admission = public_admission(args)
    out.mkdir(parents=True, exist_ok=True)
    nodes, private, chain = original_scope(spec, args)
    admission['original_scope_binding'] = chain
    bound = out / 'ADMISSION_ROOT_ONLY.json'
    if bound.exists():
        require(read(bound) == admission, 'PREVIOUS_ACCEPTANCE_BINDING_CHANGED')
    else:
        save(bound, admission)
    completed = out / 'SCALAR_RESULT.json'
    if completed.exists():
        require(inventory(out / 'runtime/repo') == whole and
                inventory(out / 'frozen_tests') == spec['frozen_inventory'],
                'COMPLETED_ROOT_RUNTIME_CHANGED')
        return read(completed)
    active, frozen = copy_runtime(out, spec, texts, support, whole)
    if args.command == '_prepare':
        scalar = {'task_id': spec['task_id'], 'condition': args.condition, 'trial': args.trial,
                  'prepared': True, 'selected_source_unchanged': True,
                  'original_independent_scope_exactly_preserved': True,
                  'new_model_requests': 0, 'new_cost_CNY': 0, 'task_tests_run': 0}
        save(out / 'PREPARED_SCALARS.json', scalar)
        return scalar
    request = out / 'DISPATCH_ROOT_ONLY.json'
    probe_dir = out / 'independent_acceptance_ROOT_ONLY'
    request_binding = {'admission_sha256': sha(bound), 'requested_nodes_sha256': digest(nodes)}
    if request.exists():
        require(read(request) == request_binding, 'PREVIOUS_DISPATCH_BINDING_CHANGED')
        require((probe_dir / 'run.json').is_file(), 'UNRESOLVED_NATIVE_DISPATCH_NO_REEXECUTION')
        result = read(probe_dir / 'run.json')
        fresh = 0
    else:
        require(not probe_dir.exists(), 'PREVIOUS_NATIVE_NAMESPACE_EXISTS')
        save(request, request_binding)
        callback = native_callback(spec, out)
        result = callback(active, frozen, nodes, probe_dir, Path(spec['python']),
                          spec['package'], time.monotonic() + 300)
        fresh = 1
    require(result.get('requested_nodes') == nodes, 'ROOT_ACTUAL_SCOPE_CHANGED')
    stop = result.get('stop_receipt', {})
    stopped = bool(stop.get('root_process_stopped') and stop.get('all_owned_descendants_terminated')
                   and stop.get('own_Job_empty_before_close') and stop.get('owned_job_closed')
                   and stop.get('post_return_named_job_absent'))
    outcomes = result.get('pytest', {}).get('outcomes', {})
    stable = inventory(active / 'repo') == whole and inventory(frozen) == spec['frozen_inventory']
    stable = stable and inventory(Path(spec['frozen_root'])) == spec['frozen_inventory']
    stable = stable and all(sha(p) == h for p, h in admission['files'].items())
    exact = set(outcomes) == set(nodes) and not result.get('pytest', {}).get('collection_errors')
    known = bool(result.get('completed_guarded_coverage') and stopped and stable and exact)
    def passed(group):
        return all(outcomes[n].get('status') == 'passed' for n in group) if known else None
    goal, ordinary, independent = passed(spec['goal_nodes']), passed(spec['ordinary_nodes']), passed(private)
    success = bool(goal and ordinary and independent and result.get('exit_code') == 0) if known else None
    scalar = {'task_id': spec['task_id'], 'trial': args.trial, 'condition': args.condition,
              'status': 'COMPLETE_INDEPENDENT_ACCEPTANCE' if known else 'ENGINEERING_UNKNOWN',
              'known': known, 'goal_passed': goal, 'ordinary_passed': ordinary,
              'private_passed': independent, 'success': success, 'all_owned_processes_stopped': stopped,
              'selected_source_unchanged': stable, 'original_independent_scope_exactly_preserved': True,
              'historical_baseline_information_permission_differs': True,
              'migration_runtime': True, 'runtime_byte_identity_to_archived_environment_claimed': False,
              'private_feedback_to_method': False, 'new_model_requests': 0, 'new_cost_CNY': 0,
              'fresh_native_runs_this_invocation': fresh, 'actual_independent_acceptance_runs': 1}
    save(completed, scalar)
    return scalar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('preflight', 'prepare', 'run', '_worker', '_prepare'))
    parser.add_argument('--case', type=Path, required=True)
    parser.add_argument('--condition', choices=('SOURCE3', 'REVERSE', 'SOURCE3_NO_ADDITIONAL_CONTEXT_V2',
                                              'SOURCE3_MATCHED_NONEDGE_CONTEXT'), required=True)
    parser.add_argument('--trial', default='trial1')
    parser.add_argument('--scope-binding', type=Path)
    args = parser.parse_args()
    if args.command in ('_worker', '_prepare'):
        spec = read(args.case)
        _, out = paths(args, spec)
        try:
            scalar = worker(args)
            print(json.dumps(scalar, ensure_ascii=False))
        except BaseException as error:
            # No exception text or native frames can disclose private node IDs.
            diagnostic = {'status': 'ENGINEERING_UNKNOWN', 'known': False, 'success': None,
                          'goal_passed': None, 'ordinary_passed': None, 'private_passed': None,
                          'all_owned_processes_stopped': None,
                          'reason': str(error) if isinstance(error, AdmissionError) else type(error).__name__,
                          'new_model_requests': 0, 'new_cost_CNY': 0,
                          'private_details_exposed': False}
            save(out / 'DIAGNOSTIC_SCALARS.json', diagnostic)
            print(json.dumps(diagnostic, ensure_ascii=False))
            raise SystemExit(1)
        return
    spec, run, out, _, selected, _, _, _ = public_admission(args)
    if args.command == 'preflight':
        print(json.dumps({'task_id': spec['task_id'], 'condition': args.condition, 'trial': args.trial,
                          'sealed_public_selection_verified': True, 'selected_business_count': len(selected),
                          'private_selector_read': False, 'task_tests_run': 0,
                          'new_model_requests': 0, 'new_cost_CNY': 0}, ensure_ascii=False))
        return
    out.mkdir(parents=True, exist_ok=True)
    lock = out / 'acceptance.lock'
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        with os.fdopen(descriptor, 'w') as stream:
            stream.write(str(os.getpid()))
        # Deliberate allowlist: no API/model credentials are inherited by worker.
        child_env = {k: os.environ[k] for k in ('SystemRoot', 'WINDIR', 'SYSTEMDRIVE', 'PATH', 'TEMP', 'TMP')
                     if k in os.environ}
        child_env.update(PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
        argv = [sys.executable, '-X', 'utf8', '-B', str(Path(__file__).resolve()),
                '_prepare' if args.command == 'prepare' else '_worker', '--case', str(args.case.resolve()),
                '--condition', args.condition, '--trial', args.trial]
        if args.scope_binding:
            argv += ['--scope-binding', str(args.scope_binding.resolve())]
        with (out / 'worker_ROOT_ONLY.log').open('ab') as log:
            child = subprocess.run(argv, cwd=ENGINE, env=child_env, stdout=log, stderr=subprocess.STDOUT,
                                   timeout=900, creationflags=0x08000000 if os.name == 'nt' else 0)
        target = out / ('DIAGNOSTIC_SCALARS.json' if child.returncode else
                        'SCALAR_RESULT.json' if (out / 'SCALAR_RESULT.json').exists() else
                        'PREPARED_SCALARS.json')
        value = read(target) if target.is_file() else {'status': 'ENGINEERING_UNKNOWN', 'known': False,
                 'success': None, 'new_model_requests': 0, 'new_cost_CNY': 0}
        print(json.dumps(value, ensure_ascii=False))
        if child.returncode:
            raise SystemExit(child.returncode)
    finally:
        lock.unlink()


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()

"""Frozen native recovery executor for all five methods and three rule controls.

No model client lives here. Qualification metadata is visible only to this
evaluator; method inputs are exported from the public prefix separately.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import random
import shutil
import sys
import time
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import HERE, MAIN, WORKTREE, PRIOR, module, load, read_jsonl, sha, utc, write_json, digest

BASE = Path(__file__).resolve().parent
qualify = module('exp129_executor_qualification', HERE / 'recovery/qualify.py')
prior = module('exp129_prior_adapter', PRIOR / 'recovery/adapter.py')
METHODS = ('all_at_once', 'binary_search', 'sdbl', 'stepfinder', 'ours', 'random', 'last_action', 'no_recovery')


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')


def load_core(asset_root, package):
    source = MAIN / '实验/实验127_完整恢复方法可行性/stage2/recovery.py'
    names = {'blob_bytes', 'safe_path', 'apply_edit', 'provenance', 'closure', 'candidate_plans', 'materialize', 'snapshot'}
    tree = ast.parse(source.read_text('utf-8-sig'))
    selected = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    if {node.name for node in selected} != names:
        raise ValueError('Original replay interface changed')
    scope = {'STAGE1': Path(asset_root), 'Path': Path, 'hashlib': hashlib, 'shutil': shutil,
             'write': write, 'is_business': lambda rel: qualify.business(rel, package)}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(source), 'exec'), scope)
    return SimpleNamespace(**{name: scope[name] for name in names}, is_business=scope['is_business'], source_sha256=sha(source))


def ordering(prediction, method, steps, task_id):
    if method == 'no_recovery':
        return [], {'native_diagnostic_order': [], 'fallback_order': [], 'order_source': 'no intervention'}
    if method in ('random', 'last_action'):
        order = list(range(steps - 1, -1, -1))
        if method == 'random':
            seed = int(hashlib.sha256(('20261002:' + task_id).encode()).hexdigest(), 16)
            random.Random(seed).shuffle(order)
        return order, {'native_diagnostic_order': order, 'fallback_order': [], 'order_source': method}
    value = prediction.get('predicted_step')
    if type(value) is not int or value not in range(steps):
        raise ValueError('Invalid predicted step')
    if method in ('ours', 'stepfinder'):
        rank = prediction.get('ranking')
        if not isinstance(rank, list) or any(type(v) is not int for v in rank) or sorted(rank) != list(range(steps)) or rank[0] != value:
            raise ValueError('Native full ranking must be a complete permutation headed by predicted_step')
        return rank, {'native_diagnostic_order': rank, 'fallback_order': [], 'order_source': 'native full ranking'}
    if prediction.get('ranking') not in (None, []):
        raise ValueError('Single-step method cannot present an invented ranking')
    fallback = [s for s in range(steps - 1, -1, -1) if s != value]
    return [value] + fallback, {'native_diagnostic_order': [value], 'fallback_order': fallback,
                              'order_source': 'native single-step then shared reverse-time fallback'}


def assess_probe(run, nodes):
    outcomes = run.get('pytest', {}).get('outcomes', {})
    exact = set(outcomes) == set(nodes)
    stable = bool(run.get('business_state_unchanged') and run.get('frozen_tests_unchanged'))
    guarded = bool(run.get('guard_loaded'))
    count = sum(outcomes.get(node, {}).get('status') == 'passed' for node in nodes)
    valid = bool(run.get('executed') and exact and stable and guarded and not run.get('timeout'))
    return {**run, 'passed': bool(valid and count == len(nodes) and run.get('exit_code') == 0),
            'exact_test_coverage': exact, 'passed_count': count, 'expected_test_count': len(nodes),
            'completed_guarded_coverage': valid, 'reward': count / len(nodes) if valid and nodes else None,
            'status': 'completed' if valid else 'incomplete_or_failed_native_probe'}


def probe(root, frozen, nodes, out, python, package, deadline):
    plugin_tree = ast.parse((qualify.HERE / 'qualification_plugin.py').read_text('utf-8-sig'))
    json_selector = any(isinstance(node, ast.Constant) and node.value == 'EXP129_SELECTED_NODES' for node in ast.walk(plugin_tree))
    if json_selector:
        run = qualify.probe(root, frozen, nodes, out, python, package, deadline)
        run['node_selection_transport'] = 'JSON via explicitly supported frozen plugin'
    else:
        # Original qualification transport: exact node IDs on the command line.
        # Old per-repository plugins must never silently ignore a JSON selector.
        root, frozen, out = root.resolve(), frozen.resolve(), out.resolve()
        out.mkdir(parents=True, exist_ok=False)
        if time.monotonic() >= deadline:
            run = {'executed': False, 'status': 'time_budget_exhausted'}
        else:
            env = qualify.isolated_env(root, root / 'repo', frozen, out, python, package)
            argv = [python, '-m', 'pytest', '-p', 'qualification_plugin', '-p', 'no:cacheprovider', '-q',
                    '--disable-warnings', '--import-mode=importlib', '--continue-on-collection-errors',
                    '-o', 'addopts=', '--rootdir', frozen]
            if package == 'mypy':
                argv.append('--assert=plain')
            argv += nodes
            before, frozen_before = qualify.inventory(root / 'repo'), qualify.inventory(frozen)
            run = qualify.execute(argv, frozen, out / 'pytest.log', min(120, max(.1, deadline - time.monotonic())), env)
            run.update(executed=True, guard_loaded=(out / 'guard_ready.json').exists(),
                       business_state_unchanged=before == qualify.inventory(root / 'repo'),
                       frozen_tests_unchanged=frozen_before == qualify.inventory(frozen),
                       pytest=load(out / 'outcomes.json') if (out / 'outcomes.json').exists() else {},
                       requested_nodes=nodes, phase='native_test', node_selection_transport='original exact CLI node IDs')
            if (out / 'guard_events.jsonl').exists():
                run['guard_events'] = read_jsonl(out / 'guard_events.jsonl')
    result = assess_probe(run, nodes)
    write(out / 'run.json', result)
    return result


def legal_state(core, root, original, frozen, frozen_inventory):
    current = qualify.inventory(root / 'repo')
    changed = sorted(p for p in set(original) | set(current) if original.get(p) != current.get(p))
    forbidden = [p for p in changed if not core.is_business('repo/' + p)]
    frozen_unchanged = qualify.inventory(frozen) == frozen_inventory
    return {'legal': not forbidden and frozen_unchanged, 'changed_business_files': changed,
            'forbidden_changed_files': forbidden, 'frozen_tests_unchanged': frozen_unchanged}


def resources(task):
    task = Path(task).resolve()
    manifest = load(task / 'task_manifest.json')
    asset_root = Path(manifest.get('asset_root', task.parents[1])).resolve()
    paths = {'template': Path(manifest['runtime_source_root']), 'frozen': Path(manifest['frozen_tests']['path']),
             'python': Path(manifest['native_interpreter']), 'asset_root': asset_root}
    for path in paths.values():
        if not path.exists():
            raise FileNotFoundError(path)
    return manifest, paths


def preflight(task, runtime):
    task = Path(task).resolve()
    manifest, paths = resources(task)
    core = load_core(paths['asset_root'], manifest['package'])
    prefix, edits = load(task / 'visible/source_prefix.json'), load(task / 'visible/edits.json')
    mapping = prior.step_mapping(prefix, edits)
    graph = core.provenance(edits)
    plans, invalid, business = core.candidate_plans(list(range(len(mapping) - 1, -1, -1)), mapping, edits, graph)
    frozen_inventory = load(task / manifest['frozen_tests']['inventory'])
    if qualify.inventory(paths['frozen']) != frozen_inventory:
        raise ValueError('Frozen native tests drifted')
    replay = core.materialize(paths['template'], Path(runtime).resolve(), edits, [])
    if qualify.inventory(replay) != qualify.inventory(paths['template']):
        raise ValueError('Strict replay mismatch')
    return {'task_id': manifest['task_id'], 'status': 'ready', 'created_utc': utc(),
            'task_path': str(task), 'asset_root': str(paths['asset_root']), 'manifest_sha256': sha(task / 'task_manifest.json'),
            'input_hashes': {p: sha(task / p) for p in ('visible/source_prefix.json', 'visible/edits.json')},
            'strict_replay_exact': True, 'frozen_tests_exact': True, 'steps': len(mapping),
            'business_edits': len(business), 'candidate_count': len(plans), 'invalid_roots': invalid,
            'dependency_graph': graph, 'candidate_plans': plans, 'core_sha256': core.source_sha256,
            'visible_test_count': len(manifest['visible_target_tests']), 'protection_test_count': len(manifest['hidden_preservation_tests'])}


def export_input(task):
    """Only visible/source_prefix is read; no task manifest, culprit or hidden test."""
    path = Path(task).resolve() / 'visible/source_prefix.json'
    prefix = load(path)
    messages = [{k: msg[k] for k in ('role', 'content', 'tool_calls', 'thought', 'name') if k in msg} for msg in prefix['messages']]
    steps = []
    for mi, msg in enumerate(messages):
        if msg.get('role') != 'assistant':
            continue
        body = str(msg.get('content') or '')
        calls = [{'function': f.group(1).strip(), 'parameters': {k.strip(): v for k, v in prior.PARAM.findall(f.group(2))}}
                 for f in prior.FUNC.finditer(body)]
        calls.extend(msg.get('tool_calls') or [])
        observations = []
        for follow in messages[mi + 1:]:
            if follow.get('role') == 'assistant':
                break
            if follow.get('role') in ('user', 'tool', 'function'):
                observations.append(str(follow.get('content') or ''))
        steps.append({'step': len(steps), 'role': 'role_0', 'agent': 'role_0',
                      'content': prior.FUNC.sub('', body).strip(), 'action': json.dumps(calls, ensure_ascii=False),
                      'thought': str(msg.get('thought') or ''), 'observation': '\n\n'.join(observations),
                      'source_message_index': mi})
    first = next(m.get('content', '') for m in messages if m.get('role') == 'user')
    match = prior.re.search(r'<pr_description>(.*?)</pr_description>', first, prior.re.S)
    return {'sample_id': Path(task).name, 'instance_id': Path(task).name, 'task': match.group(1).strip() if match else first,
            'messages': messages, 'steps': steps, 'turns': steps, 'step_index_base': 0,
            'failure_feedback': prefix.get('new_failure_observation', {}).get('visible_target_feedback', {}),
            'diagnostic_step_count': len(steps), 'source_prefix_sha256': sha(path),
            'failure_observation_origin': 'Exp129 newly run fixed-native-test qualification probe',
            'dataset': 'SWE-Gym task with OpenHands public trajectory',
            'evaluation_scope': 'qualified intermediate development failure state; restore pre-existing functionality',
            'gold_or_reference_patch_included': False}


def validate_prediction_input(prediction, method, sample):
    if prediction.get('sample_id') != sample['sample_id']:
        raise ValueError('Prediction sample identity differs')
    if method in ('random', 'last_action', 'no_recovery'):
        return
    if method in ('ours', 'stepfinder'):
        expected = hashlib.sha256(json.dumps(sample['turns'], sort_keys=True).encode()).hexdigest()
        if prediction.get('input_turns_sha256') != expected:
            raise ValueError('Native prediction comes from another visible prefix')
    elif prediction.get('input_sha256') != digest(sample):
        raise ValueError('Generated prediction comes from another visible input')


def verify_execution_binding(task, harness):
    if harness is None:
        raise ValueError('Frozen per-task execution harness is required')
    harness = Path(harness).resolve()
    round_root = harness.parents[1]
    seal = load(round_root / 'execution_seal.json')
    for name in ('qualify.py', 'sitecustomize.py', 'qualification_plugin.py', 'source_codec.py'):
        path = harness / name
        if seal['sha256'].get(path.relative_to(round_root).as_posix()) != sha(path):
            raise ValueError('Frozen execution harness changed')
    if sha(BASE / 'run.py') != seal['executor_sha256']:
        raise ValueError('Executor code changed after execution seal')
    original = load(round_root / 'seal.json')
    refs = [row for row in original['tasks'] if Path(row['task_path']).resolve() == Path(task).resolve()]
    if len(refs) != 1 or sha(Path(task) / 'READY.json') != refs[0]['ready_sha256']:
        raise ValueError('Qualified state is not bound to this round')
    ready = load(Path(task) / 'READY.json')
    for name, value in ready['sha256'].items():
        if sha(Path(task) / name) != value:
            raise ValueError('Qualified state drifted: ' + name)
    sample = export_input(task)
    if digest(sample) != refs[0]['input_digest']:
        raise ValueError('Visible input changed since diagnosis round was frozen')
    return harness, sample


def run_task(task, prediction, method, out, runtime, harness=None):
    global qualify
    harness, sample = verify_execution_binding(task, harness)
    validate_prediction_input(prediction, method, sample)
    qualify = module('exp129_frozen_execution_qualification', harness / 'qualify.py')
    qualify.HERE = harness
    started = time.monotonic()
    task, out, runtime = Path(task).resolve(), Path(out).resolve(), Path(runtime).resolve()
    out.mkdir(parents=True, exist_ok=False)
    write(out / 'prediction.json', prediction)
    tid = task.name
    elapsed = prediction.get('diagnostic_elapsed_seconds')
    if not isinstance(elapsed, (int, float)) or isinstance(elapsed, bool) or not math.isfinite(elapsed) or elapsed < 0:
        raise ValueError('Actual finite diagnostic timing is required for recovery')
    if method not in METHODS or prediction.get('sample_id', tid) != tid:
        raise ValueError('Method/task mismatch')
    if any(v in str(prediction.get('prediction_source', '')).lower() for v in ('mock', 'synthetic', 'fixture', 'simulat')):
        raise ValueError('Artificial predictions are forbidden')
    result = {'schema': 'Exp129-recovery/1.0', 'sample_id': tid, 'method': method, 'created_utc': utc(),
              'diagnostic_elapsed_seconds': elapsed, 'environment_budget': 6, 'test_timeout_seconds': 120,
              'joint_time_budget_seconds': 900, 'api_calls_in_recovery': 0, 'status': 'initializing',
              'success': None, 'candidate_submissions': 0, 'hidden_acceptance_calls': 0,
              'no_final_state': True, 'preservation_acceptance_completed': False, 'preservation_failure': None}
    attempts, finalroot, final_visible = [], None, None
    try:
        manifest, paths = resources(task)
        core = load_core(paths['asset_root'], manifest['package'])
        prefix, edits = load(task / 'visible/source_prefix.json'), load(task / 'visible/edits.json')
        mapping, graph = prior.step_mapping(prefix, edits), core.provenance(edits)
        native_ok = prediction.get('status') in ('completed', 'success', 'ok')
        attempted = bool(prediction.get('generation_attempted') or prediction.get('submitted_request_count') or prediction.get('call_ids') or prediction.get('status') == 'invalid_output')
        diagnostic_invalid = method not in ('random', 'last_action', 'no_recovery') and not native_ok and attempted
        if method not in ('random', 'last_action', 'no_recovery') and not native_ok and not diagnostic_invalid:
            raise ValueError('Diagnosis was not actually completed')
        result['diagnostic_outcome_status'] = prediction.get('status')
        order, provenance = ordering(prediction, 'no_recovery' if diagnostic_invalid else method, len(mapping), tid)
        plans, invalid, business = core.candidate_plans(order, mapping, edits, graph)
        for plan in plans:
            plan['ordering_source'] = ('native_full_ranking' if method in ('ours', 'stepfinder') else
                                       'native_prediction' if plan['step'] == prediction.get('predicted_step') else
                                       'rule_control' if method in ('random', 'last_action') else 'reverse_time_fallback')
        write(out / 'candidate_plans.json', {'plans': plans, 'mapping': mapping, 'dependency_graph': graph, 'invalid_roots': invalid, **provenance})
        all_plans, _, _ = core.candidate_plans(list(range(len(mapping))), mapping, edits, graph)
        result.update(assistant_steps=len(mapping), distinct_legal_candidates=len(all_plans), business_edit_count=len(business),
                      post_regression_business_edits=manifest.get('post_regression_business_edits'), core_sha256=core.source_sha256,
                      task_manifest_sha256=sha(task / 'task_manifest.json'), **provenance)
        result['execution_harness_sha256'] = {name: sha(qualify.HERE / name) for name in ('qualify.py', 'sitecustomize.py', 'qualification_plugin.py', 'source_codec.py')}
        deadline = started + 900 - elapsed
        search_deadline = deadline - min(120, max(0, (deadline - time.monotonic()) / 2))
        original = qualify.inventory(paths['template'])
        frozen_inventory = load(task / manifest['frozen_tests']['inventory'])
        if qualify.inventory(paths['frozen']) != frozen_inventory:
            raise ValueError('Frozen tests drifted')
        runtime.mkdir(parents=True, exist_ok=False)
        replay = core.materialize(paths['template'], runtime / 'initial_replay', edits, [])
        if qualify.inventory(replay) != original:
            raise ValueError('Full replay mismatch')
        result['failed_prefix_exact_replay'] = True
        finalroot = runtime / 'initial_replay'
        if method == 'no_recovery' or diagnostic_invalid:
            final_visible = probe(finalroot, paths['frozen'], manifest['visible_target_tests'], out / 'unchanged_visible', paths['python'], manifest['package'], search_deadline)
        else:
            for ordinal, plan in enumerate(plans[:6], 1):
                if time.monotonic() >= search_deadline:
                    break
                row = {'submission': ordinal, **plan, 'omitted_edit_count': len(plan['omitted_edit_ids']),
                       'retained_edit_count': len(edits) - len(plan['omitted_edit_ids'])}
                attempts.append(row)
                cs = time.monotonic()
                root = runtime / f'candidate_{ordinal:02d}'
                try:
                    core.materialize(paths['template'], root, edits, plan['omitted_edit_ids'])
                    row['materialized'] = True
                    finalroot, final_visible = root, None
                    row['legal_edit_check'] = legal_state(core, root, original, paths['frozen'], frozen_inventory)
                    if not row['legal_edit_check']['legal']:
                        raise ValueError('Illegal changes')
                    final_visible = probe(root, paths['frozen'], manifest['visible_target_tests'], out / f'candidate_{ordinal:02d}/visible', paths['python'], manifest['package'], search_deadline)
                    row['visible_probe'] = final_visible
                    core.snapshot(root, edits, out / f'candidate_{ordinal:02d}')
                except Exception as error:
                    row.setdefault('materialized', False)
                    row.update(error=f'{type(error).__name__}: {error}', failure_phase='probe_or_snapshot' if row['materialized'] else 'materialization')
                row['candidate_total_seconds'] = time.monotonic() - cs
                write(out / 'attempts.json', attempts)
                if final_visible and final_visible.get('passed'):
                    break
        # Final selection is already frozen; hidden results never enter search.
        hidden = probe(finalroot, paths['frozen'], manifest['hidden_preservation_tests'], out / 'final_preservation', paths['python'], manifest['package'], deadline)
        legality = legal_state(core, finalroot, original, paths['frozen'], frozen_inventory)
        core.snapshot(finalroot, edits, out / 'final_state')
        write(out / 'final_state/full_repo_inventory.json', qualify.inventory(finalroot / 'repo'))
        selected = next((row for row in reversed(attempts) if row.get('materialized')), None)
        result.update(status='diagnosis_invalid' if diagnostic_invalid else 'completed', no_final_state=False,
                      visible_pass=bool(final_visible and final_visible.get('passed')), preservation_pass=hidden['passed'],
                      hidden_acceptance_calls=int(hidden.get('executed', False)),
                      preservation_acceptance_completed=hidden['completed_guarded_coverage'],
                      preservation_failure=(not hidden['passed']) if hidden['completed_guarded_coverage'] else None,
                      final_legal_edit_check=legality, final_submission=selected['submission'] if selected else 0,
                      omitted_edit_count=selected['omitted_edit_count'] if selected else 0,
                      retained_edit_count=selected['retained_edit_count'] if selected else len(edits),
                      success=bool(final_visible and final_visible.get('passed') and hidden['passed'] and legality['legal']))
        if diagnostic_invalid:
            result['success'] = False
        # Incomplete collection can itself be caused by a submitted source edit;
        # it remains an unsuccessful submission, never a success-based exclusion.
    except Exception as error:
        result.update(status='blocked_environment_or_input', reason=f'{type(error).__name__}: {error}')
    result.update(candidate_submissions=len(attempts), recovery_executed=finalroot is not None,
                  recovery_evaluable=result['success'] is not None, execution_elapsed_seconds=time.monotonic() - started,
                  joint_elapsed_seconds=elapsed + time.monotonic() - started,
                  first_visible_pass_submission=next((row['submission'] for row in attempts if row.get('visible_probe', {}).get('passed')), None))
    write(out / 'attempts.json', attempts)
    write(out / 'result.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('preflight', 'export', 'run'))
    parser.add_argument('--task', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--runtime', type=Path)
    parser.add_argument('--method', choices=METHODS)
    parser.add_argument('--predictions', type=Path)
    parser.add_argument('--harness', type=Path)
    args = parser.parse_args()
    if args.command == 'preflight':
        value = preflight(args.task, args.runtime)
        write_json(args.out, value)
    elif args.command == 'export':
        value = export_input(args.task)
        write_json(args.out, value)
    else:
        if args.method in ('random', 'last_action', 'no_recovery'):
            prediction = {'sample_id': args.task.name, 'status': 'completed', 'diagnostic_elapsed_seconds': 0.0, 'prediction_source': 'fixed_rule_control'}
        else:
            matches = [row for row in read_jsonl(args.predictions) if row.get('sample_id') == args.task.name and row.get('method') == args.method]
            if len(matches) != 1:
                raise ValueError('Expected one real method prediction')
            prediction = matches[0]
        value = run_task(args.task, prediction, args.method, args.out, args.runtime, args.harness)
    print(json.dumps({k: value[k] for k in ('sample_id', 'task_id', 'method', 'status', 'success', 'candidate_submissions', 'execution_elapsed_seconds') if k in value}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()

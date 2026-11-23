"""Pure full OURS248 method on a new task/trial, paused at model/native boundaries.

Original core/body/relations/current-failure/SET source bytes are unchanged.
Exact settled requests and public witnesses replay only within this new trial.
"""
import argparse
import ast
import copy
import difflib
import inspect
import types
from decimal import Decimal
from trial_runtime249 import *
from shared_public249 import load_public_task
import shared_input249

CORE_ROOT = HERE / 'ours_core'
sys.path.insert(0, str(CORE_ROOT))
import ranked_repair248 as core
import relations248
import current_feedback248
import feedback_codec242
import publicpack_v2_224 as codec
import shared_projection224 as projection
from progress_guard240 import RepairProgressGuard, source_sha


class BoundaryReady(BaseException): pass


def assignment(path, name):
    namespace = {}
    for node in ast.parse(Path(path).read_text('utf-8-sig')).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), namespace)
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and isinstance(node.value.func.value, ast.Name) and node.value.func.value.id == name:
            exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), namespace)
    return namespace[name]


def original_body():
    namespace = {'copy': copy, 'json': json, 'hashlib': hashlib, 'canonical': canonical, 'digest': digest, 'save': save,
        'projection': projection, 'relations240': relations248, 'current_feedback248': current_feedback248,
        'codec': codec, 'feedback_codec242': feedback_codec242,
        'shared': types.SimpleNamespace(TOOLS=assignment(OLD / 'ancestor_sources/common_environment224.py', 'TOOLS')),
        'masked_boundary242': types.SimpleNamespace(TOOLS=assignment(OLD / 'masked_boundary242.py', 'TOOLS'))}
    exec(compile((CORE_ROOT / 'body248.py').read_text('utf-8-sig'), str(CORE_ROOT / 'body248.py'), 'exec'), namespace)
    return namespace['body']


def financial_bounds(body, config):
    path = FIN / 'continuous_core_v3.py'
    node = next(n for n in ast.parse(path.read_text('utf-8-sig')).body if isinstance(n, ast.FunctionDef) and n.name == 'bounds')
    namespace = {'canonical': canonical, 'D': Decimal, 'GateRejected': RuntimeError}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path) + '::pure_bounds', 'exec'), namespace)
    return namespace['bounds'](body, config)


class Environment:
    def __init__(self, contract_path):
        self.contract_path = Path(contract_path).resolve()
        self.contract, self.out, self.config, self.shared_current_C0_supplement, self.shared_current_C0_decoded = checked_contract(contract_path, 'OURS248_FULL')
        verify_source_seal(self.contract['method_source_seal']['path'])
        if sha(self.contract['method_source_seal']['path']) != self.contract['method_source_seal']['sha256']:
            raise RuntimeError('EXP249_METHOD_SOURCE_SEAL_DRIFT')
        data = load_public_task(self.contract['task_id'], self.contract['public_contract']['path'])
        self.task_id = data['task_id']; self.ref = data['public_ref']; self.pack = data['pack']; self.semantic = data['semantic']
        self.method = core.METHODS[0]; self.rows = []; self.calls = 0; self.native_calls = 0; self.out_tokens = 0
        self.rejected_history = []; self.snap_files = {}; self.snap_diffs = {}; self.forward_records = []; self.checkpoint = {}
        self.arm = 'FULL_CLOSURE_SET'; self.context_mode = 'RELATION'; self.closure_enabled = True; self.state_admission_mode = 'PROGRESS_SET'
        c = data['contract']; self.public_contract = c
        scope = read(self.contract['public_test_scope_contract']['path'])
        self.scope = next(v for v in scope['tasks'] if v['task_id'] == self.task_id)
        origin = Path(self.scope['public_source_repo_view'])
        self.files = {rel: (origin / rel).read_bytes().decode('utf-8') for rel in c['c0_business_paths_sha256']}
        if source_sha(self) != c['c0_business_paths_sha256']: raise RuntimeError('EXP249_NEW_TRIAL_C0_NOT_EXACT')
        self.original_files = copy.deepcopy(self.files); self._failure_anchor_initial_files = copy.deepcopy(self.files)
        all_view = {**self.scope['business_and_support_files_in_view'], **self.scope['public_test_py_files_SHA256']}
        self.supports = {p: h for p, h in all_view.items() if p not in self.files}
        self.repo_root = self.out / 'current_actor' / 'repo'; self.active = self.repo_root.parent
        self._paths = {'frozen': Path(c['frozen_public_test_root'])}
        self.initial_public_feedback = copy.deepcopy(self.semantic['failure_feedback'])
        self._encoded_initial_public_failure = copy.deepcopy(self.pack['semantic_structure']['failure_feedback'])
        self._initial_public_captured_output = copy.deepcopy(self.semantic.get('original_public_captured_output'))
        self.task = {'failure_feedback': copy.deepcopy(self.initial_public_feedback)}
        self.goal = 'Recover the observed public failure and preserve initially-passing public ordinary behavior. Original issue background: ' + self.semantic['original_issue']
        self.public_regression_nodes = list(c['ordinary_nodes']); self.recovery_goal_nodes = list(c['public_target_nodes'])
        self.initial_snapshot = {'id': 'C0', 'label': 'new_trial_C0', 'inventory_sha256': digest({**source_sha(self), **self.supports}),
                                 'diff': {}, 'archive_path': str(self.out / 'snapshots/C0')}
        self.current_snapshot = copy.deepcopy(self.initial_snapshot)
        self.snap_files['C0'] = copy.deepcopy(self.files); self.snap_diffs['C0'] = []
        obs = read(self.contract['current_C0_observation']['path'])
        self.initial_validation = copy.deepcopy(obs['current_incumbent_public_feedback'])
        if 'public_validation' in self.initial_validation: self.initial_validation = self.initial_validation['public_validation']
        if obs['actual_C0_source_SHA256'] != source_sha(self): raise RuntimeError('EXP249_NEW_C0_FEEDBACK_SOURCE_DRIFT')
        guard = RepairProgressGuard.begin(self, self.initial_validation)
        self._Root_C0_unprojected_feedback = core._public_feedback(guard.current_public_feedback(source_sha(self)))
        if self._Root_C0_unprojected_feedback != self.shared_current_C0_decoded:
            raise RuntimeError('EXP249_METHOD_AND_SHARED_COMMON_C0_OBJECT_DIFFER')
        witness = self.shared_current_C0_supplement['current_C0_native_record_SHA256']
        self._native_witness_by_inventory = {digest(source_sha(self)): witness}
        self.protocol_origin = self.out / 'PUBLIC_RUNTIME_CONTRACT.json'
        save(self.protocol_origin, {'task_order': read(E249 / 'protocol249_SOURCE.json')['task_order'],
            'public_test_scope_contract': copy.deepcopy(self.contract['public_test_scope_contract']),
            'original_G_O_only': True, 'actor_unmasked_test_or_Git_reads': False})
        t0 = self.out / 'SCIENCE_T0_TRIAL_PREPARATION_STARTED.json'
        self.original_started = read(t0) if t0.exists() else {'actual_POST_not_started': True, 'preparation_only': True}
        self.body_function = original_body()

    def business_files(self): return self.files
    def read_file(self, path): return self.files[path]
    def initial_guard_observation(self): return copy.deepcopy(self.initial_validation)
    def source_evidence(self): return core._source_evidence(self)
    def diff(self): return copy.deepcopy(self.snap_diffs[self.current_snapshot['id']])
    def snapshot(self, label=None): return copy.deepcopy(self.current_snapshot)
    def restore(self, snapshot):
        self.current_snapshot = copy.deepcopy(snapshot); self.files = copy.deepcopy(self.snap_files[snapshot['id']])
    def select(self, snapshot, reason):
        self.restore(snapshot)
        return {'snapshot': copy.deepcopy(snapshot), 'reason': copy.deepcopy(reason), 'uses_hidden': False,
                'new_trial_exact_public_only_selection': True}
    def record(self, stage, data): self.rows.append({'stage': stage, 'evidence': copy.deepcopy(data)})

    def checkpoint_boundary(self, status, state):
        guard = state.get('admission')
        self.checkpoint = {'schema': 'EXP249-complete-OURS-safe-boundary/1', 'status': status, 'UTC': now(),
            'method': 'OURS248_FULL', 'task_id': self.task_id, 'trial_id': self.contract['trial_id'],
            'trial_master_seed': self.contract['trial_master_seed'], 'attempt': state.get('attempt'),
            'messages': copy.deepcopy(state.get('messages')), 'seed': state.get('seed'),
            'core_locals': {k: copy.deepcopy(state.get(k)) for k in ('ledger', 'candidates', 'history', 'public_events', 'first_pass', 'best_key',
                'initial_source', 'accepted_snapshot', 'final', 'current', 'calls', 'parsed', 'applied', 'public_runs', 'done')},
            'state_admission': copy.deepcopy(vars(guard)) if guard else None,
            'cursor': {'calls': self.calls, 'native': self.native_calls, 'output_tokens': self.out_tokens},
            'C0_business_source': copy.deepcopy(self.original_files),
            'all_snapshot_business_deltas': {ident: {p: text for p, text in files.items() if self.original_files.get(p) != text} for ident, files in self.snap_files.items()},
            'all_snapshot_diffs': copy.deepcopy(self.snap_diffs), 'current_snapshot': copy.deepcopy(self.current_snapshot),
            'current_business_source_SHA256': source_sha(self), 'native_witness_by_inventory': copy.deepcopy(self._native_witness_by_inventory),
            'complete_settled_request_response_provenance': copy.deepcopy(self.forward_records),
            'original_science_started': self.original_started, 'fresh_contract_SHA256': sha(self.contract_path),
            'source_seal_SHA256': self.contract['method_source_seal']['sha256'],
            'unknown_or_inflight_model_native_never_reissued': True, 'POST_native_private_finance_in_this_entry': 0}
        save(self.out / 'checkpoint.json', self.checkpoint)

    def body(self, role, messages, temperature, seed, max_tokens, reader_index=0, tools=None):
        body = self.body_function(self, role, messages, temperature, seed, max_tokens, reader_index, tools)
        body = current_feedback248.finish_body(self, body)
        body['seed'] = trial_seed(self.contract, role, seed, reader_index)
        return shared_input249.inject(body, self.config, self.task_id)

    def llm(self, role, messages, temperature, seed, max_tokens, schema=None, tools=None):
        current = copy.deepcopy(messages); reader_index = 0
        while True:
            self.calls += 1
            body = self.body(role, current, temperature, seed, max_tokens, reader_index, tools)
            slot = self.out / 'calls' / ('call' + str(self.calls).zfill(3))
            response_path = slot / 'new_generation' / 'llm' / (str(self.calls).zfill(3) + '_response.json')
            receipt_path = response_path.with_name(str(self.calls).zfill(3) + '_finance_receipt.json')
            request_path = response_path.with_name(str(self.calls).zfill(3) + '_request.json')
            if not response_path.exists():
                state_file = slot / 'DISPATCH_STATE.json'
                if state_file.exists():
                    state = read(state_file)
                    save(self.out / 'STATUS.json', {'status': 'MODEL_INFLIGHT_OR_UNKNOWN_NO_RESEND', 'dispatch_state': state['status'],
                         'task_id': self.task_id, 'trial_id': self.contract['trial_id'], 'call': self.calls})
                    raise BoundaryReady()
                bounds = financial_bounds(body, self.config)
                ready = {'schema': 'EXP249-exact-single-model-ready/1', 'method': 'OURS248_FULL', 'task_id': self.task_id,
                    'trial_id': self.contract['trial_id'], 'attempt': self.checkpoint['attempt'], 'reader_index': reader_index,
                    'call_ordinal': self.calls, 'role': role, 'body_SHA256': digest(body), 'canonical_bytes': len(canonical(body).encode()),
                    'full_peak_reserve_CNY': bounds['global_reserve'], 'full_original_financial_bounds': bounds,
                    'finance_configuration': self.contract['finance_configuration'], 'finance_phase': self.contract['finance_phase'],
                    'contract_path': str(self.contract_path), 'contract_SHA256': sha(self.contract_path),
                    'method_source_seal': self.contract['method_source_seal'], 'trial_output_root': str(self.out),
                    'maximum_new_requests': 1, 'old_other_trial_response_reuse': False, 'model_native_private_finance': 0}
                save(slot / 'FIRST_UNPOST_BODY.json', body); save(slot / 'FIRST_UNPOST_READY.json', ready)
                checkpoint = copy.deepcopy(self.checkpoint); checkpoint['cursor']['calls'] = self.calls - 1
                checkpoint.update(prepared_body=body, complete_current_messages=body['messages'], current_reader_index=reader_index,
                    status='EXACT_REQUEST_READY_NOT_POSTED')
                save(slot / 'checkpoint.json', checkpoint)
                save(self.out / 'STATUS.json', {'status': 'MODEL_READY_NOT_POSTED', 'method': 'OURS248_FULL', 'task_id': self.task_id,
                    'trial_id': self.contract['trial_id'], 'call': self.calls, 'attempt': self.checkpoint['attempt'],
                    'ready_dir': str(slot), 'body_SHA256': digest(body), 'actual_model_generation': 0})
                raise BoundaryReady()
            receipt = read(receipt_path); request = read(request_path)
            if receipt.get('status') != 'SETTLED' or request.get('body_SHA256') != digest(body) or request.get('body') != body:
                raise RuntimeError('EXP249_EXACT_COMPLETE_SETTLED_REPLAY_REQUIRED')
            response = read(response_path); usage = response['usage']; self.out_tokens += usage['completion_tokens']
            self.forward_records.append({'call': self.calls, 'body_SHA256': digest(body), 'response_path': str(response_path),
                'response_SHA256': sha(response_path), 'receipt_path': str(receipt_path), 'receipt_SHA256': sha(receipt_path),
                'same_method_task_trial_only': True})
            message = response['choices'][0]['message']; finish = response['choices'][0].get('finish_reason')
            if not message.get('tool_calls'):
                return {'content': message.get('content') or '', 'message': message, 'usage': usage,
                        'call_ordinal': self.calls, 'finish_reason': finish}
            current = [copy.deepcopy(m) for m in body['messages'] if not str(m.get('content', '')).startswith(shared_input249.TAG)]
            current.append(copy.deepcopy(message))
            for call in message['tool_calls']:
                name = call['function']['name']
                try: value = self.reader(name, json.loads(call['function']['arguments']))
                except (ValueError, KeyError, TypeError) as exc:
                    value = {'status': 'PUBLIC_READER_ARGUMENT_ERROR', 'message': str(exc),
                             'correct_public_failure_node_ids': sorted(self.initial_public_feedback), 'protected_contents_not_returned': True}
                if name in ('read_full_failure', 'read_public_history'):
                    value = projection.project(value, [(self.repo_root, '/workspace/repo'), (self._paths['frozen'], '/public-tests'),
                                (self.active, '/workspace'), (self.out, '/public-feedback')])
                    value, _ = feedback_codec242.encode(value)
                current.append({'role': 'tool', 'tool_call_id': call['id'], 'content': canonical(value)})
                save(self.out / 'tool_boundaries' / (str(self.calls).zfill(3) + '_' + call['id'] + '.json'),
                     {'complete_messages': current, 'source_SHA256': source_sha(self), 'tool': call, 'output': value,
                      'no_original_unmasked_test_or_private_read': True})
            reader_index += 1

    def reader(self, name, args):
        if name == 'read_full_failure':
            node = args['node']
            if node not in self.initial_public_feedback: raise ValueError('UNKNOWN_OR_NONPUBLIC_FAILURE_NODE')
            value = {'node': node, 'complete_observed_public_failure': copy.deepcopy(self.initial_public_feedback[node]), 'no_clipping': True}
            if self._initial_public_captured_output: value['complete_captured_public_output'] = self._initial_public_captured_output
            return value
        if name == 'read_public_history':
            records = copy.deepcopy(self.semantic['public_history'])
            if 'source_message_index' in args:
                records = [v for v in records if v.get('source_message_index') == args['source_message_index']]
                if not records: raise ValueError('UNKNOWN_OR_FUTURE_PUBLIC_SOURCE_INDEX')
            return {'original_public_messages': records, 'complete_requested_history': True, 'future_or_private_results': False}
        if name == 'list_current_sources': return {'paths': sorted(self.files), 'complete': True}
        if name == 'list_public_masked_tests': return {'paths': sorted(self.scope['public_test_py_files_SHA256']), 'readonly': True,
            'complete': True, 'scope_SHA256': self.contract['public_test_scope_contract']['sha256']}
        if name not in ('read_current_source', 'read_public_masked_test'): raise ValueError('UNKNOWN_COMMON_PUBLIC_READER')
        rel = args['path'].removeprefix('/workspace/repo/').removeprefix('repo/')
        if name == 'read_current_source':
            text = self.files[rel]; source = hashlib.sha256(text.encode()).hexdigest()
        else:
            source = self.scope['public_test_py_files_SHA256'][rel]; path = Path(self.scope['public_source_repo_view']) / rel
            if sha(path) != source: raise RuntimeError('EXP249_IMMUTABLE_MASKED_TEST_DRIFT')
            text = path.read_bytes().decode('utf-8')
        rows = text.splitlines(keepends=True); start = args.get('start_line', 1); end = args.get('end_line', len(rows))
        if type(start) != int or type(end) != int or not 1 <= start <= end <= len(rows): raise ValueError('INVALID_EXPLICIT_SOURCE_LINE_RANGE')
        return {'path': rel, 'start_line': start, 'end_line': end, 'total_lines': len(rows), 'complete_requested_text': ''.join(rows[start - 1:end]),
                'whole_source_sha256': source, 'no_silent_clipping': True, 'readonly': name == 'read_public_masked_test'}

    def apply_patch(self, edits, label, from_snapshot=None):
        before = copy.deepcopy(self.files); errors = []
        try:
            for edit in edits:
                path = edit['path'].removeprefix('repo/')
                if path not in self.files or self.files[path].count(edit['old']) != 1: raise ValueError('SEARCH_NOT_UNIQUE_OR_MISSING')
                self.files[path] = self.files[path].replace(edit['old'], edit['new'], 1)
        except Exception as exc:
            errors = [type(exc).__name__ + ': ' + str(exc)]; self.files = before
        hashes = source_sha(self); initial = {p: hashlib.sha256(t.encode()).hexdigest() for p, t in self.original_files.items()}
        changed = {p: h for p, h in hashes.items() if h != initial[p]}; ident = 'attempt' + str(self.checkpoint['attempt'])
        snap = {'id': ident, 'label': label, 'inventory_sha256': digest({**hashes, **self.supports}),
                'diff': changed, 'archive_path': str(self.out / 'snapshots' / ident)}
        diff = [{'path': 'repo/' + rel, 'before_sha256': initial[rel], 'after_sha256': hashes[rel],
                 'unified_diff': ''.join(difflib.unified_diff(self.original_files[rel].splitlines(True), self.files[rel].splitlines(True),
                                                             fromfile='a/' + rel, tofile='b/' + rel))} for rel in sorted(changed)]
        self.snap_files[ident] = copy.deepcopy(self.files); self.snap_diffs[ident] = diff; self.current_snapshot = snap
        save(self.out / 'snapshots' / ident / 'snapshot.json', snap)
        save(self.out / 'snapshots' / ident / 'business_source.json', self.files)
        return {'candidate_id': self.checkpoint['attempt'] - 1, 'snapshot': copy.deepcopy(snap),
                'legal': {'legal': not errors, 'changed_business_files': sorted(changed), 'forbidden_changed_files': [], 'frozen_tests_unchanged': True},
                'apply_errors': errors, 'raw_diff': diff, 'edits': copy.deepcopy(edits), 'independent_original_root': False}

    def run_regression(self, snapshot, label):
        attempt = self.checkpoint['attempt']; out = self.out / 'native_requests' / ('attempt' + str(attempt))
        completed = out / 'COMPLETED_PUBLIC.json'
        if not completed.exists():
            self.checkpoint_boundary('PUBLIC_NATIVE_READY', inspect.currentframe().f_back.f_locals)
            ready = {'schema': 'EXP249-exact-candidate-original-G-O-native-ready/1', 'method': 'OURS248_FULL',
                'task_id': self.task_id, 'trial_id': self.contract['trial_id'], 'attempt': attempt,
                'candidate_snapshot': snapshot, 'candidate_source_sha256': source_sha(self),
                'business_source_file': str(self.out / 'snapshots' / snapshot['id'] / 'business_source.json'),
                'business_source_file_SHA256': sha(self.out / 'snapshots' / snapshot['id'] / 'business_source.json'),
                'goal_nodes': self.recovery_goal_nodes, 'ordinary_nodes': self.public_regression_nodes,
                'public_test_scope_contract': self.contract['public_test_scope_contract'],
                'public_contract': self.contract['public_contract'], 'method_contract_path': str(self.contract_path),
                'method_contract_SHA256': sha(self.contract_path), 'native_output': str(out),
                'only_original_G_O_no_private': True, 'model_native_private_finance': 0}
            if (out / 'NATIVE_INTENT.json').exists() or (out / 'SUPERVISOR_STARTED_ONCE.json').exists():
                status = 'PUBLIC_NATIVE_INFLIGHT_OR_UNKNOWN_NO_RERUN'
            else:
                save(out / 'NATIVE_READY.json', ready); save(out / 'checkpoint.json', self.checkpoint); status = 'PUBLIC_NATIVE_READY'
            save(self.out / 'STATUS.json', {'status': status, 'task_id': self.task_id, 'trial_id': self.contract['trial_id'],
                 'attempt': attempt, 'ready_path': str(out / 'NATIVE_READY.json')})
            raise BoundaryReady()
        receipt = read(completed); parent_path = Path(receipt['parent_supervision_path'])
        if sha(parent_path) != receipt['parent_supervision_SHA256']: raise RuntimeError('EXP249_CANDIDATE_PARENT_STOP_DRIFT')
        parent = read(parent_path)
        if parent.get('error') is not None or parent.get('exit_code') != 0 or parent['stop_receipt'].get('all_owned_descendants_terminated') is not True:
            raise RuntimeError('EXP249_CANDIDATE_PUBLIC_PARENT_STOP_UNKNOWN')
        if receipt['task_id'] != self.task_id or receipt['trial_id'] != self.contract['trial_id'] or receipt['candidate_source_sha256'] != source_sha(self) or receipt['candidate_snapshot']['inventory_sha256'] != snapshot['inventory_sha256']:
            raise RuntimeError('EXP249_CANDIDATE_PUBLIC_WITNESS_SOURCE_DRIFT')
        path = receipt['public_native_path']
        if sha(path) != receipt['public_native_SHA256']: raise RuntimeError('EXP249_CANDIDATE_PUBLIC_NATIVE_RECORD_DRIFT')
        probe = read(path); self.native_calls += 1
        self._native_witness_by_inventory[digest(source_sha(self))] = receipt['public_native_SHA256']
        ordinary = {n: {**probe['pytest']['outcomes'][n], 'outcome': probe['pytest']['outcomes'][n]['status']} for n in self.public_regression_nodes}
        failures = sum(v['status'] != 'passed' for v in ordinary.values())
        return {'passed': failures == 0, 'failure_count': failures, 'outcomes': ordinary, 'status': 'GUARDED_ORDINARY_REGRESSION',
                'native_record': {**probe, 'path': path}, 'public_goal_not_added_to_paper_ranking': True}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--contract', required=True); args = parser.parse_args()
    # Root's later explicit clock rule counts real trial preparation, including
    # current binding checks, ranking-source reconstruction and first-body work.
    declared = read(args.contract)
    if declared.get('clock_policy') != 'START_AT_FIRST_REAL_TRIAL_PREPARATION':
        raise RuntimeError('EXP249_CURRENT_ROOT_TRIAL_CLOCK_RULE_REQUIRED')
    out = Path(declared['output_root']).resolve()
    expected = (HERE / 'runs' / 'OURS248_FULL' / declared['task_id'] / declared['trial_id']).resolve()
    if out != expected or not out.is_relative_to(HERE.resolve()):
        raise RuntimeError('EXP249_TRIAL_CLOCK_OUTPUT_SCOPE')
    t0 = out / 'SCIENCE_T0_TRIAL_PREPARATION_STARTED.json'
    if not t0.exists():
        t0.parent.mkdir(parents=True, exist_ok=True)
        with t0.open('x', encoding='utf-8') as stream:
            json.dump({'schema': 'EXP249-real-trial-preparation-T0/1', 'at_UTC': now(),
                'method': 'OURS248_FULL', 'task_id': declared['task_id'], 'trial_id': declared['trial_id'],
                'contract_SHA256': sha(args.contract), 'real_preparation_time_included': True,
                'first_POST_time_recorded_separately': True, 'existing_RQ1_reuse_cost_disclosed_separately': True,
                'old_protocol_POST_only_rule_superseded_by_later_explicit_Root_clock_instruction': True}, stream, ensure_ascii=False, indent=2)
            stream.flush(); os.fsync(stream.fileno())
    env = Environment(args.contract)
    try:
        result = core.run(env)
        save(env.out / 'PUBLIC_ONLY_NATURAL_TERMINAL.json', result); save(env.out / 'SELECTED_BUSINESS_SOURCE.json', env.files)
        save(env.out / 'STATUS.json', {'status': 'ENGINEERING_UNKNOWN' if result.get('error') else 'PUBLIC_ONLY_NATURAL_TERMINAL',
             'task_id': env.task_id, 'trial_id': env.contract['trial_id'], 'error': result.get('error'),
             'requires_separate_once_independent_final_acceptance': True, 'model_native_private_finance_in_entry': 0})
    except BoundaryReady:
        pass
    finally:
        save(env.out / 'PUBLIC_REPLAY_RECORDS.json', env.rows); save(env.out / 'EXACT_SETTLED_REPLAY.json', env.forward_records)
    print(canonical(read(env.out / 'STATUS.json')), flush=True)


if __name__ == '__main__': main()

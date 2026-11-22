"""Portable public-only adapter for frozen ranked repair and order controls.

The frozen generator, evidence construction, feedback binding, source expansion
and goal-identity guard are reused. Native callbacks execute public G/O only.
Completed responses and candidate probes are replayed locally on restart.
"""
from __future__ import annotations

import ast
import copy
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import types

ENGINE = Path(__file__).resolve().parents[2]
CORE = ENGINE / 'src/thesis_recovery/frozen/recovery'
INPUTS = ENGINE / '.rebuild/paper-inputs'
SOURCE = ENGINE.parents[1] / '01_实验/02_运行故障恢复_RQ2/已有实现/实验262_已有进展保护真实压力场景/SOURCE'


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    with temp.open('w', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def inventory(root):
    root = Path(root)
    return {p.relative_to(root).as_posix(): sha(p) for p in root.rglob('*')
            if p.is_file() and not set(p.parts) & {'.git', '__pycache__', '.pytest_cache'}}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_frozen():
    # Existing core modules import one another by their archived public names.
    if str(CORE) not in sys.path:
        sys.path.insert(0, str(CORE))
    import ranked_repair248 as core
    import relations248
    import current_feedback248
    import feedback_codec242
    import publicpack_v2_224
    import shared_projection224
    current = types.ModuleType('_rq2_controls_current_feedback_public_prefix')
    path = CORE / 'current_feedback248.py'
    exec(compile(path.read_text(encoding='utf-8-sig'), str(path), 'exec'), current.__dict__)
    current.masked_goal_calls = lambda env: public_prefix_calls(env, current)
    # Retain the original static provider/consumer algorithm while accurately
    # labelling the now narrower provenance; no masked test file is opened.
    import failure_anchors248
    anchors = types.SimpleNamespace()
    original_retrieve = failure_anchors248.retrieve
    def retrieve(*args, **kwargs):
        audit, providers, consumers = original_retrieve(*args, **kwargs)
        audit['schema'] = 'current-capture-and-already-public-prefix-static-anchors/1'
        audit['test_source_shared'] = False
        for row in consumers:
            if row.get('anchor_origin') == 'declared_public_Goal_masked_AST_call_name':
                row['anchor_origin'] = 'already_public_Goal_failure_prefix_call_name'
        return audit, providers, consumers
    anchors.retrieve = retrieve
    relations = types.ModuleType('_rq2_controls_relations_public_prefix')
    path = CORE / 'relations248.py'
    exec(compile(path.read_text(encoding='utf-8-sig'), str(path), 'exec'), relations.__dict__)
    relations.failure_anchors240 = anchors
    return types.SimpleNamespace(core=core, relations=relations, current=current,
          feedback=feedback_codec242, codec=publicpack_v2_224, projection=shared_projection224)


def public_prefix_calls(env, feedback):
    """Only parse the Goal prefix already displayed by public native failure."""
    calls, audit = [], []
    for node in env.recovery_goal_nodes:
        name = node.rsplit('::', 1)[-1].split('[', 1)[0]
        target, provenance = feedback.captured_goal_prefix(env, node, name)
        row = {'Goal_node': node, 'status': 'NO_ALREADY_PUBLIC_FUNCTION_PREFIX',
               'source': 'already-public failure prefix', 'test_source_read': False,
               'complete_test_function_claim': False}
        if target is not None:
            row.update(status='ALREADY_PUBLIC_FAILURE_PREFIX_AST', **provenance)
            for call in feedback.goal_body_calls(target):
                function = call.func
                method = function.attr if isinstance(function, ast.Attribute) else function.id if isinstance(function, ast.Name) else None
                if method:
                    calls.append({'method_name': method, 'Goal_node': node, 'call_line': call.lineno,
                         'source': 'already-public failure prefix', 'AST_source_status': row['status'],
                         'test_source_read': False, 'complete_test_function_claim': False,
                         'static_possible_reference': True, 'causal_claim': False})
        audit.append(row)
    return calls, audit


def original_public_tools():
    paths = [INPUTS / 'retained-experiments/rq2/experiment224/实验/实验224_二十三题Flash完整共同恢复比较/common_environment224.py',
             ENGINE / 'reproduction/current_inputs/4d04869664a84240130723a7efc71285ccf06b93500018d81b3153612abe5bac_4d04869664a84240_masked_boundary242.py']
    groups = []
    for path in paths:
        tree = ast.parse(path.read_text(encoding='utf-8-sig'))
        values = [n.value for n in tree.body if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == 'TOOLS' for t in n.targets)]
        if len(values) != 1: raise ValueError('Original readonly tool declaration missing')
        groups.append(ast.literal_eval(values[0]))
    return groups


def _tool(name, description, properties, required=()):
    return {'type': 'function', 'function': {'name': name, 'description': description,
        'parameters': {'type': 'object', 'properties': properties, 'required': list(required), 'additionalProperties': False}}}


PUBLIC_TOOLS = [
    _tool('list_current_sources', 'List every legal current business source path.', {}),
    _tool('read_current_source', 'Read an exact range of current business source.',
          {'path': {'type': 'string'}, 'start_line': {'type': 'integer'}, 'end_line': {'type': 'integer'}}, ('path',)),
    _tool('read_public_history', 'Read complete original public history, optionally by source index.',
          {'source_message_index': {'type': 'integer'}}),
    _tool('read_full_failure', 'Read a complete already-public initial failure.', {'node': {'type': 'string'}}, ('node',)),
    _tool('list_public_masked_tests', 'List the shared readonly masked public tests.', {}),
    _tool('read_public_masked_test', 'Read an exact range of an authorized masked public test.',
          {'path': {'type': 'string'}, 'start_line': {'type': 'integer'}, 'end_line': {'type': 'integer'}}, ('path',)),
]


def body_function(frozen):
    shared_tools, masked_tools = original_public_tools()
    shared_tools = shared_tools + [next(t for t in PUBLIC_TOOLS if t['function']['name'] == 'read_public_history')]
    namespace = {'copy': copy, 'json': json, 'hashlib': hashlib, 'canonical': canonical,
                 'digest': digest, 'save': save, 'ast': ast, 'Path': Path,
                 'projection': frozen.projection, 'relations240': frozen.relations,
                 'current_feedback248': frozen.current, 'codec': frozen.codec,
                 'feedback_codec242': frozen.feedback,
                 'shared': types.SimpleNamespace(TOOLS=shared_tools),
                 'masked_boundary242': types.SimpleNamespace(TOOLS=[])}
    path = CORE / 'body248.py'
    exec(compile(path.read_text(encoding='utf-8-sig'), str(path), 'exec'), namespace)
    return namespace['body']


class PendingModelRequest(RuntimeError):
    pass


class PublicNativeUnknown(RuntimeError):
    pass


def wrap_public_validation(result, ordinary_nodes):
    ordinary = {n: {**copy.deepcopy(result['pytest']['outcomes'][n]),
                   'outcome': result['pytest']['outcomes'][n]['status']} for n in ordinary_nodes}
    return {'passed': all(v['status'] == 'passed' for v in ordinary.values()),
            'failure_count': sum(v['status'] != 'passed' for v in ordinary.values()),
            'outcomes': ordinary, 'status': 'GUARDED_ORDINARY_REGRESSION',
            'native_record': copy.deepcopy(result), 'public_goal_not_added_to_paper_ranking': True}


class ControlEnvironment:
    """One new scientific condition; archives remain readonly.

    A client implements generate_body(body, sample_id=..., stage=...,
    remaining_seconds=...) with a durable body-bound completed-response cache
    and no automatic resubmission of unknown requests. Native is a callback
    (active, frozen, nodes, output, python, package, deadline) -> original probe.
    """
    def __init__(self, case, condition, trial='trial1', *, client=None, native=None, output=None):
        self.spec = read(case) if isinstance(case, (str, Path)) else copy.deepcopy(case)
        if condition not in ('SOURCE3', 'REVERSE'):
            raise ValueError('Only SOURCE3 and exact reverse chronology are frozen for this comparison')
        self.frozen = load_frozen()
        self.task_id = self.spec['task_id']
        self.condition, self.trial = condition, trial
        self.method = self.frozen.core.METHODS[0 if condition == 'SOURCE3' else 1]
        self.out = Path(output or ENGINE / '.rebuild/rq2-controls/runs' / self.task_id / trial / condition).resolve()
        if not self.out.is_relative_to(ENGINE.resolve()):
            raise ValueError('Run output must remain inside the engineering workspace')
        self.out.mkdir(parents=True, exist_ok=True)
        self.client, self.native = client, native
        self.information_policy = self.spec.get('information_policy', 'TEST_SOURCE_NOT_SHARED')
        if self.information_policy != 'TEST_SOURCE_NOT_SHARED':
            raise ValueError('This new paired protocol does not share any test source')
        self.call_sequence = self.calls = self.native_calls = self.out_tokens = 0
        self.rows, self.rejected_history, self.forward_records = [], [], []
        self.checkpoint = {}
        self.started = time.monotonic()
        self.wall_budget = self.spec.get('wall_budget_seconds', 1800)
        self.clock = read(self.out / 'SCIENCE_CLOCK.json') if (self.out / 'SCIENCE_CLOCK.json').exists() else None
        if self.clock and self.clock['budget_seconds'] != self.wall_budget:
            raise ValueError('Existing condition budget changed')
        self.arm, self.context_mode, self.closure_enabled = 'FULL_CURRENT_CONTEXT', 'RELATION', True
        self.state_admission_mode = self.spec.get('state_admission_mode', 'PROGRESS_SET')
        self.repo_root = self.out / 'current_actor/repo'
        self.active = self.repo_root.parent
        self._paths = {'frozen': Path(self.spec['frozen_root']).resolve()}
        self.files = {p: (Path(self.spec['business_root']) / p).read_bytes().decode('utf-8')
                      for p in self.spec['business_hashes']}
        if self.source_hashes() != self.spec['business_hashes']:
            raise ValueError('C0 business source differs from the frozen selection')
        self.original_files = copy.deepcopy(self.files)
        self._failure_anchor_initial_files = copy.deepcopy(self.files)
        self.supports = {p: h for p, h in self.spec.get('support_hashes', {}).items() if p not in self.files}
        self.support_root = Path(self.spec.get('support_root', self.spec['public_view']))
        self.scope = {'task_id': self.task_id, 'public_source_repo_view': self.spec['public_view'],
                      'public_test_py_files_SHA256': {}}
        for p, expected in self.supports.items():
            if sha(self.support_root / p) != expected:
                raise ValueError('Native-only support differs from frozen source: ' + p)
        if inventory(self._paths['frozen']) != self.spec['frozen_inventory']:
            raise ValueError('Frozen native test/reference inventory changed')
        self.ref = copy.deepcopy(self.spec['ref'])
        self.ref['G_frozen_plan'] = self.spec['ranking_plan']
        self.pack = read(self.spec['pack'])
        self.semantic = self.frozen.codec.decode(self.pack)
        self.public_regression_nodes = list(self.spec['ordinary_nodes'])
        self.recovery_goal_nodes = list(self.spec['goal_nodes'])
        initial = self.spec['initial_validation']
        self.initial_validation = read(initial) if isinstance(initial, str) else copy.deepcopy(initial)
        if 'native_record' not in self.initial_validation:
            self.initial_validation = wrap_public_validation(self.initial_validation, self.public_regression_nodes)
        self.initial_public_feedback = {node: copy.deepcopy(value) for node, value in
                self.initial_validation['native_record']['pytest']['outcomes'].items()
                if node in self.recovery_goal_nodes and value['status'] != 'passed'}
        self.task = {'failure_feedback': copy.deepcopy(self.initial_public_feedback)}
        self._encoded_initial_public_failure = copy.deepcopy(self.pack['semantic_structure']['failure_feedback'])
        self._initial_public_captured_output = copy.deepcopy(self.semantic.get('original_public_captured_output'))
        self.goal = 'Recover the observed public failure and preserve initially-passing public behavior. Original issue background: ' + self.semantic['original_issue']
        self.initial_snapshot = {'id': 'C0', 'label': 'current_condition_C0',
             'inventory_sha256': digest({**self.source_hashes(), **self.supports}), 'diff': {},
             'archive_path': str(self.out / 'snapshots/C0')}
        self.current_snapshot = copy.deepcopy(self.initial_snapshot)
        self.snap_files = {'C0': copy.deepcopy(self.files)}
        self.snap_diffs = {'C0': []}
        self.protocol_origin = self.out / 'PUBLIC_RUNTIME_CONTRACT.json'
        scope_path = self.out / 'PUBLIC_SCOPE.json'
        save(scope_path, {'tasks': [self.scope]})
        save(self.protocol_origin, {'public_test_scope_contract': {'path': str(scope_path), 'sha256': sha(scope_path)}})
        guard = self.frozen.core.RepairProgressGuard.begin(self, self.initial_validation)
        self._Root_C0_unprojected_feedback = self.frozen.core._public_feedback(guard.current_public_feedback(self.source_hashes()))
        self.shared_current_C0_decoded = copy.deepcopy(self._Root_C0_unprojected_feedback)
        self._native_witness_by_inventory = {digest(self.source_hashes()): digest(self.initial_validation['native_record'])}
        self._body = body_function(self.frozen)
        self.binding = {'task': self.task_id, 'condition': condition, 'trial': trial,
              'case': digest(self.spec), 'complete_pack': sha(self.spec['pack']),
              'ranking_plan': sha(self.spec['ranking_plan']),
              'frozen_core': {p.name: sha(p) for p in CORE.glob('*.py')},
              'public_tools': digest(original_public_tools()[0] + [next(t for t in PUBLIC_TOOLS if t['function']['name'] == 'read_public_history')]),
              'information_policy': self.information_policy, 'max_attempts': 3, 'max_output_tokens': 16384,
              'temperature': 0.0, 'state_admission_mode': self.state_admission_mode}
        binding_path = self.out / 'CONDITION_BINDING.json'
        if binding_path.exists() and read(binding_path) != self.binding:
            raise ValueError('Existing condition/code/input changed; do not merge scientific states')
        save(binding_path, self.binding)
        save(self.out / 'snapshots/C0/business_source.json', self.files)

    def source_hashes(self):
        return {p: hashlib.sha256(text.encode()).hexdigest() for p, text in sorted(self.files.items())}

    def time_left(self):
        if self.clock:
            elapsed = max(0., time.time() - self.clock['wall_start'],
                          time.monotonic() - self.clock['monotonic_start'])
        else:
            elapsed = time.monotonic() - self.started
        return max(0., self.wall_budget - elapsed)

    def business_files(self): return self.files
    def read_file(self, path): return self.files[path]
    def initial_guard_observation(self): return copy.deepcopy(self.initial_validation)
    def source_evidence(self): return self.frozen.core._source_evidence(self)
    def snapshot(self, label=None): return copy.deepcopy(self.current_snapshot)
    def diff(self): return copy.deepcopy(self.snap_diffs[self.current_snapshot['id']])

    def restore(self, snapshot):
        self.current_snapshot = copy.deepcopy(snapshot)
        self.files = copy.deepcopy(self.snap_files[snapshot['id']])

    def select(self, snapshot, reason):
        self.restore(snapshot)
        result = {'snapshot': copy.deepcopy(snapshot), 'reason': copy.deepcopy(reason), 'uses_hidden': False}
        save(self.out / 'SELECTED_PUBLIC_ONLY.json', result)
        save(self.out / 'selected_business_source.json', self.files)
        return result

    def record(self, stage, data):
        self.rows.append({'stage': stage, 'evidence': copy.deepcopy(data)})
        save(self.out / 'PUBLIC_STAGE_RECORDS.json', self.rows)

    def checkpoint_boundary(self, status, state):
        self.checkpoint = {'status': status, 'attempt': state.get('attempt'),
            'condition_binding': digest(self.binding), 'current_snapshot': self.current_snapshot,
            'business_source_hashes': self.source_hashes(), 'calls_returned': self.calls,
            'call_sequence': self.call_sequence, 'native_fresh': self.native_calls,
            'public_state_admission': state['admission'].summary() if state.get('admission') else None}
        save(self.out / 'CHECKPOINT.json', self.checkpoint)

    def body(self, role, messages, temperature, seed, max_tokens, reader_index=0, tools=None):
        value = self._body(self, role, messages, temperature, seed, max_tokens, reader_index, tools)
        value = self.frozen.current.finish_body(self, value)
        value['tools'] = [tool for tool in value['tools'] if tool['function']['name'] not in
                          ('list_public_masked_tests', 'read_public_masked_test')]
        for message in value['messages']:
            if message.get('role') == 'system' and isinstance(message.get('content'), str):
                message['content'] = message['content'].replace(
                    'You may list and read the shared readonly masked public tests through the supplied tools.',
                    'Test source is not shared. Use only the already-public execution feedback and current business source.')
        policy = {'schema': 'RQ2_TEST_SOURCE_NOT_SHARED/1', 'test_source_shared': False,
                  'native_support_and_frozen_roots_are_not_model_readers': True,
                  'Goal_API_hints_source': 'already-public native failure prefix only',
                  'legacy_masked_named_metadata_keys': 'compatibility keys, not evidence of a test source read',
                  'difference_from_old_baselines': 'Old masked source permission is unavailable; this paired protocol denies all test-source reads in both arms.'}
        if not any(isinstance(m.get('content'), str) and '"schema":"RQ2_TEST_SOURCE_NOT_SHARED/1"' in m['content'] for m in value['messages']):
            index = 1 if value['messages'] and value['messages'][0].get('role') == 'system' else 0
            value['messages'].insert(index, {'role': 'user', 'content': canonical(policy)})
        return value

    def llm(self, role, messages, temperature, seed, max_tokens, schema=None, tools=None):
        current, reader_index = copy.deepcopy(messages), 0
        while True:
            if self.time_left() <= 0 or self.call_sequence >= self.spec.get('max_model_requests', 128):
                raise RuntimeError('BudgetExhausted: current condition model/time bound')
            self.call_sequence += 1
            body = self.body(role, current, temperature, seed, max_tokens, reader_index, tools)
            stage = f'{self.condition}/{self.trial}/attempt{self.checkpoint["attempt"]}/tool{reader_index}'
            slot = self.out / 'calls' / str(self.call_sequence).zfill(3)
            request = {'stage': stage, 'sample_id': self.task_id, 'body': body, 'body_sha256': digest(body)}
            request_path, response_path = slot / 'request.json', slot / 'response.json'
            if request_path.exists() and read(request_path) != request:
                raise PendingModelRequest('Previously prepared request body changed; no automatic resend')
            save(request_path, request)
            replayed = response_path.exists()
            if replayed:
                response = read(response_path)
            else:
                if self.client is None:
                    raise PendingModelRequest('Exact provider request prepared; no client attached')
                # The client owns durable unknown-outcome reconciliation. It must
                # return its prior response or reject, never automatically rePOST.
                save(slot / 'dispatch.json', {'stage': stage, 'body_sha256': digest(body), 'status': 'client_owned_durable_dispatch'})
                response = self.client.generate_body(body, sample_id=self.task_id, stage=stage,
                                                     remaining_seconds=self.time_left())
                save(response_path, response)
            self.calls += 1
            self.out_tokens += (response.get('usage') or {}).get('completion_tokens', 0)
            if self.out_tokens > self.spec.get('max_output_tokens_total', 131072):
                raise RuntimeError('BudgetExhausted: cumulative output token bound')
            message = copy.deepcopy(response.get('message') or {'role': 'assistant', 'content': response.get('content', response.get('text', ''))})
            if response.get('tool_calls') and not message.get('tool_calls'):
                message['tool_calls'] = response['tool_calls']
            self.forward_records.append({'call': self.call_sequence, 'body_sha256': digest(body),
                    'response_sha256': sha(response_path), 'local_response_replayed': replayed,
                    'request_id': response.get('request_id')})
            save(self.out / 'RESPONSE_PROVENANCE.json', self.forward_records)
            if not message.get('tool_calls'):
                return {'content': message.get('content') or '', 'message': message,
                        'usage': response.get('usage') or {}, 'finish_reason': response.get('finish_reason'),
                        'call_ordinal': self.call_sequence}
            current = copy.deepcopy(body['messages'])
            current.append(message)
            for call in message['tool_calls']:
                name = call['function']['name']
                try:
                    value = self.reader(name, json.loads(call['function']['arguments']))
                except (ValueError, KeyError, TypeError, PermissionError) as exc:
                    value = {'status': 'PUBLIC_READER_ARGUMENT_ERROR', 'error': type(exc).__name__}
                current.append({'role': 'tool', 'tool_call_id': call['id'], 'content': canonical(value)})
            reader_index += 1

    def reader(self, name, args):
        if name in ('list_public_masked_tests', 'read_public_masked_test'):
            raise PermissionError('TEST_SOURCE_NOT_SHARED')
        if name == 'list_current_sources': return {'paths': sorted(self.files), 'complete': True}
        if name == 'read_full_failure':
            node = args['node']
            if node not in self.initial_public_feedback: raise ValueError('Not an authorized public failure')
            return {'node': node, 'complete_observed_public_failure': self.initial_public_feedback[node], 'no_clipping': True}
        if name == 'read_public_history':
            records = copy.deepcopy(self.semantic['public_history'])
            if 'source_message_index' in args:
                records = [x for x in records if x.get('source_message_index') == args['source_message_index']]
                if not records: raise ValueError('Unknown public source index')
            return {'original_public_messages': records, 'complete_requested_history': True, 'future_or_private_results': False}
        if name == 'list_public_masked_tests': return {'paths': sorted(self.scope['public_test_py_files_SHA256']), 'readonly': True}
        if name not in ('read_current_source', 'read_public_masked_test'): raise ValueError('Unknown readonly tool')
        rel = args['path'].removeprefix('/workspace/repo/').removeprefix('repo/')
        if name == 'read_current_source':
            text = self.files[rel]
        else:
            expected = self.scope['public_test_py_files_SHA256'][rel]
            path = Path(self.scope['public_source_repo_view']) / rel
            if sha(path) != expected: raise ValueError('Masked public source changed')
            text = path.read_bytes().decode('utf-8')
        rows = text.splitlines(keepends=True)
        start, end = args.get('start_line', 1), args.get('end_line', len(rows))
        if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(rows):
            raise ValueError('Invalid exact source line range')
        return {'path': rel, 'start_line': start, 'end_line': end, 'total_lines': len(rows),
                'complete_requested_text': ''.join(rows[start - 1:end]), 'whole_source_sha256': hashlib.sha256(text.encode()).hexdigest(),
                'readonly': name == 'read_public_masked_test'}

    def apply_patch(self, edits, label, from_snapshot=None):
        before = copy.deepcopy(self.files)
        errors = []
        try:
            for edit in edits:
                path = edit['path'].removeprefix('repo/')
                if path not in self.files or not edit['old'] or self.files[path].count(edit['old']) != 1:
                    raise ValueError('SEARCH_NOT_UNIQUE_OR_MISSING')
                self.files[path] = self.files[path].replace(edit['old'], edit['new'], 1)
        except Exception as exc:
            self.files = before
            errors = [type(exc).__name__ + ': ' + str(exc)]
        hashes = self.source_hashes()
        changed = {p: h for p, h in hashes.items() if h != self.spec['business_hashes'][p]}
        ident = 'attempt' + str(self.checkpoint['attempt'])
        snap = {'id': ident, 'label': label, 'inventory_sha256': digest({**hashes, **self.supports}),
                'diff': changed, 'archive_path': str(self.out / 'snapshots' / ident)}
        diff = [{'path': 'repo/' + p, 'before_sha256': self.spec['business_hashes'][p], 'after_sha256': hashes[p],
                 'unified_diff': ''.join(difflib.unified_diff(self.original_files[p].splitlines(True), self.files[p].splitlines(True),
                                                            fromfile='a/' + p, tofile='b/' + p))} for p in sorted(changed)]
        self.current_snapshot = snap
        self.snap_files[ident], self.snap_diffs[ident] = copy.deepcopy(self.files), diff
        save(self.out / 'snapshots' / ident / 'snapshot.json', snap)
        save(self.out / 'snapshots' / ident / 'business_source.json', self.files)
        return {'snapshot': snap, 'legal': {'legal': not errors, 'changed_business_files': sorted(changed),
                'forbidden_changed_files': [], 'frozen_tests_unchanged': True}, 'apply_errors': errors, 'raw_diff': diff}

    def _materialize(self):
        self.repo_root.mkdir(parents=True, exist_ok=True)
        for p, text in self.files.items():
            target = (self.repo_root / p).resolve()
            if not target.is_relative_to(self.repo_root.resolve()): raise ValueError('Business path escaped')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(text.encode('utf-8'))
        for p, expected in {**self.supports, **self.scope['public_test_py_files_SHA256']}.items():
            if p in self.files: continue
            source = self.support_root / p
            if sha(source) != expected: raise ValueError('Public support source changed')
            target = (self.repo_root / p).resolve()
            if not target.is_relative_to(self.repo_root.resolve()): raise ValueError('Public support path escaped')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())

    def run_regression(self, snapshot, label):
        if self.native is None: raise PublicNativeUnknown('No public native evaluator attached')
        self._materialize()
        nodes = list(dict.fromkeys(self.recovery_goal_nodes + self.public_regression_nodes))
        folder = self.out / 'native' / ('attempt' + str(self.checkpoint['attempt']))
        binding = {'source': self.source_hashes(), 'nodes': nodes, 'frozen': digest(self.spec['frozen_inventory']),
                   'python': str(Path(self.spec['python']).resolve())}
        input_path, completed = folder / 'request.json', folder / 'completed.json'
        if input_path.exists() and read(input_path) != binding:
            raise PublicNativeUnknown('Previously prepared native input changed')
        if completed.exists():
            result = read(completed)
        else:
            if input_path.exists():
                raise PublicNativeUnknown('Unresolved native dispatch; reconcile before any reexecution')
            save(input_path, binding)
            self.native_calls += 1
            result = self.native(self.active, self._paths['frozen'], nodes, folder / 'probe',
                        Path(self.spec['python']), self.spec['package'], time.monotonic() + min(300, self.time_left()))
            save(completed, result)
        expected = self.source_hashes()
        actual = {p: sha(self.repo_root / p) for p in expected}
        if actual != expected or inventory(self._paths['frozen']) != self.spec['frozen_inventory']:
            raise PublicNativeUnknown('Native changed business or frozen bytes')
        self._native_witness_by_inventory[digest(expected)] = digest(result)
        ordinary = {n: {**copy.deepcopy(result['pytest']['outcomes'][n]), 'outcome': result['pytest']['outcomes'][n]['status']}
                    for n in self.public_regression_nodes}
        return {'passed': all(v['status'] == 'passed' for v in ordinary.values()),
                'failure_count': sum(v['status'] != 'passed' for v in ordinary.values()),
                'outcomes': ordinary, 'status': 'GUARDED_ORDINARY_REGRESSION',
                'native_record': result, 'public_goal_not_added_to_paper_ranking': True}

    def run(self):
        completed = self.out / 'RESULT.json'
        if completed.exists() and read(completed)['status'] not in ('ENGINEERING_UNKNOWN', 'BUDGET_CENSORED'):
            return read(completed)
        lock = self.out / 'producer.lock'
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        try:
            with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
                stream.write(canonical({'pid': os.getpid(), 'created_wall': time.time(), 'condition_binding': digest(self.binding)}))
            if self.clock is None:
                self.clock = {'wall_start': time.time(), 'monotonic_start': time.monotonic(),
                              'budget_seconds': self.wall_budget, 'old_experiment_deadline_inherited': False}
                save(self.out / 'SCIENCE_CLOCK.json', self.clock)
            result = self.frozen.core.run(self)
            result['condition'] = self.condition
            result['trial'] = self.trial
            result['replay_provenance'] = self.forward_records
            result['private_evaluation'] = 'NOT_EXECUTED_BY_THIS_ADAPTER'
            result['adapter_protocol'] = {'information_policy': self.information_policy,
                 'new_test_source_file_reads_granted_to_model': False,
                 'native_support_is_model_visible': False,
                 'Goal_AST_hints': 'already-public failure prefixes only',
                 'archived_frozen_core_and_body_bytes_unchanged': True,
                 'identical_archived_complete_method_replication_claimed': False,
                 'core_declared_prompt_hash_is_unadapted_source_not_final_HTTP_body': True}
            save(completed, result)
            return result
        finally:
            lock.unlink()


def observe_case(spec, *, output=None, native=None):
    """One common public C0 observation. No model, private selector or Gold."""
    out = Path(output or ENGINE / '.rebuild/rq2-controls/qualification' / spec['task_id']).resolve()
    if not out.is_relative_to(ENGINE.resolve()): raise ValueError('Qualification output outside engineering root')
    out.mkdir(parents=True, exist_ok=True)
    binding = {'source': spec['business_hashes'], 'support': spec.get('support_hashes', {}),
               'nodes': list(dict.fromkeys(spec['goal_nodes'] + spec['ordinary_nodes'])),
               'frozen': spec['frozen_inventory'], 'python': str(Path(spec['python']).resolve())}
    request, completed = out / 'request.json', out / 'completed.json'
    if request.exists() and read(request) != binding: raise PublicNativeUnknown('Common C0 observation binding changed')
    if completed.exists(): return read(completed), completed
    if request.exists(): raise PublicNativeUnknown('Unresolved common C0 dispatch; review before reexecution')
    repo = out / 'active/repo'
    repo.mkdir(parents=True, exist_ok=True)
    for relative, expected in {**spec.get('support_hashes', {}), **spec['business_hashes']}.items():
        origin = Path(spec['business_root'] if relative in spec['business_hashes'] else spec['public_view']) / relative
        raw = origin.read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected: raise ValueError('Common C0 original bytes changed')
        target = (repo / relative).resolve()
        if not target.is_relative_to(repo.resolve()): raise ValueError('C0 materialization path escaped')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    save(request, binding)
    callback = native or native_callback(spec, out)
    result = callback(repo.parent, Path(spec['frozen_root']), binding['nodes'], out / 'probe',
                      Path(spec['python']), spec['package'], time.monotonic() + 300)
    wrapped = wrap_public_validation(result, spec['ordinary_nodes'])
    save(completed, wrapped)
    return wrapped, completed


class PublicProbeOwner:
    def __init__(self, output):
        self.output = Path(output); self.started = time.monotonic(); self.unknown = None
        self.protocol = {'budget': {'flow_wall_seconds': 1800, 'native_timeout_seconds': 300}}
    def require_action(self, kind, allow_no_new=False):
        if kind not in ('native', 'observe') or self.unknown or self.time_left() <= 0:
            raise RuntimeError('Only current-task public native execution is allowed')
    def reserve_native(self): pass
    def time_left(self): return max(0., 1800 - (time.monotonic() - self.started))
    def latch_unknown(self, error, stage): self.unknown = {'type': type(error).__name__, 'stage': stage}
    def record(self, value):
        self.output.mkdir(parents=True, exist_ok=True)
        with (self.output / 'owned_job_events.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(canonical(value) + '\n')


def native_callback(spec, output):
    """Reuse original qualification guard and owned-Job STOP; no test names invented."""
    harness = Path(spec['native_harness'])
    qualifier = load_module('_rq2_controls_qualifier', harness / 'qualify.py')
    path = INPUTS / 'rq2-experiment129/executor/run.py'
    tree = ast.parse(path.read_text(encoding='utf-8-sig'))
    names = {'assess_probe', 'probe'}
    definitions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    if {n.name for n in definitions} != names: raise ValueError('Original probe definitions changed')
    ns = {'Path': Path, 'ast': ast, 'time': time, 'qualify': qualifier, 'load': read, 'write': save,
          'read_jsonl': lambda p: [json.loads(v) for v in Path(p).read_text(encoding='utf-8-sig').splitlines() if v]}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(path), 'exec'), ns)
    aor = INPUTS / 'experiment261/CONTINUE_AFTER_USER2335'
    sys.path.insert(0, str(aor))
    job = load_module('_rq2_controls_winjob', aor / 'winjob_pp.py')
    owner = PublicProbeOwner(output)
    def execute(argv, cwd, log, timeout=300, env=None):
        import ctypes
        value = job.JobRunner(owner).execute(argv, cwd, log, timeout=min(300, timeout), env=env)
        stop = value['stop_receipt']
        # Original JobRunner closes its last Job handle in finally. Verify the
        # named object is actually gone before satisfying the frozen guard's
        # stronger owned_job_closed predicate; do not merely rename a field.
        kernel = job.kernel()
        remaining_handle = kernel.OpenJobObjectW(4, False, value['Job'])
        missing_error = ctypes.get_last_error()
        if remaining_handle:
            kernel.CloseHandle(remaining_handle)
            raise PublicNativeUnknown('Owned Job still exists after original runner returned')
        if missing_error != 2:
            raise PublicNativeUnknown('Owned Job closure could not be independently verified')
        value['stop_receipt'] = {**stop, 'root_process_stopped': stop['root_stopped'],
             'all_owned_descendants_terminated': bool(stop['own_Job_empty_before_close'] and stop['descendants_stopped']),
             'owned_job_closed': True, 'post_return_named_job_absent': True}
        return value
    qualifier.execute = execute
    return ns['probe']


def observe_case(spec, *, output=None, native=None):
    """Execute/reuse the single common C0 public observation before any model.

    An unresolved prior native dispatch is retained and blocks automatic repeat.
    No independent selector or private result is read by this function.
    """
    out = Path(output or ENGINE / '.rebuild/rq2-controls/qualification' / spec['task_id']).resolve()
    if not out.is_relative_to(ENGINE.resolve()): raise ValueError('C0 output outside engineering workspace')
    out.mkdir(parents=True, exist_ok=True)
    active, repo = out / 'active', out / 'active/repo'
    expected = {**spec['business_hashes'], **spec.get('support_hashes', {}), **spec['public_test_py_files_SHA256']}
    for relative, expected_hash in expected.items():
        source_root = spec['business_root'] if relative in spec['business_hashes'] else spec.get('support_root', spec['public_view'])
        source = Path(source_root) / relative
        if sha(source) != expected_hash: raise ValueError('Common C0 source bytes changed: ' + relative)
        target = (repo / relative).resolve()
        if not target.is_relative_to(repo.resolve()): raise ValueError('Unsafe C0 relative source path')
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and sha(target) != expected_hash: raise ValueError('Existing common C0 materialization changed')
        if not target.exists(): target.write_bytes(source.read_bytes())
    frozen = Path(spec['frozen_root'])
    if inventory(frozen) != spec['frozen_inventory']: raise ValueError('Frozen C0 test inventory changed')
    nodes = list(dict.fromkeys(spec['goal_nodes'] + spec['ordinary_nodes']))
    binding = {'source': expected, 'nodes': nodes, 'frozen': digest(spec['frozen_inventory']),
               'python': str(Path(spec['python']).resolve())}
    pending, completed = out / 'request.json', out / 'initial_validation.json'
    if pending.exists() and read(pending) != binding: raise PublicNativeUnknown('Common C0 observation binding changed')
    if completed.exists(): return read(completed), completed
    if pending.exists(): raise PublicNativeUnknown('Prior C0 native dispatch unresolved; review before rerun')
    save(pending, binding)
    native = native or native_callback(spec, out)
    result = native(active, frozen, nodes, out / 'probe', Path(spec['python']), spec['package'], time.monotonic() + 300)
    if not result.get('completed_guarded_coverage') or not result.get('stop_receipt', {}).get('all_owned_descendants_terminated'):
        save(out / 'incomplete_public_observation.json', result)
        raise PublicNativeUnknown('Common C0 native coverage or STOP is unknown')
    wrapped = wrap_public_validation(result, spec['ordinary_nodes'])
    save(completed, wrapped)
    return wrapped, completed

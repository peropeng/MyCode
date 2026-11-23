"""Independent V2 input adapter; AL has direct author text, no added reader loop."""
from common166 import *
import copy
import re
import common_environment224 as shared
from fresh_entry224 import FreshEnvironment
from publicpack_v2_224 import V, decode, model_pack, render
ROOT_V2_PROTOCOL = ROOT / '工作区/1008-2320-baseline-main/frozen_v2_author_direct_publicpack_protocol.json'
ROOT_V2_SHA = '55bb1e0094138384850b5624f7ab85dfa204753c57ca4f2eb6b69bc63b5a8a07'


def initial_index_v2(pack):
    # Do not expand old semantic_index in every author problem_statement.
    # All exact node/status/phase/E-lines remain in the same reversible pack.
    decode(pack)
    return {'schema': 'V2-exact-common-public-pack-reference/1',
            'semantic_sha256': pack['decoded_semantic_sha256'],
            'failure_feedback_reference': ['semantic_structure', 'failure_feedback'],
            'captured_public_output_reference': ['semantic_structure', 'original_public_captured_output'],
            'read_rule': 'Resolve every $public_text_lines list in the common pack against unique_exact_lines, concatenating in order. All node IDs, statuses, phases and exact error/source lines are retained; no truncation or summary.'}


def authorize_v2():
    protocol = read(V / 'protocol_v2.json')
    grant_path = V / 'root_calibration_grant_v2.json'
    runtime = read(ROOT / '工作区/1008-2320-baseline-main/coordination/runtime_release.json')
    if runtime.get('root_runtime_ready') is not True or runtime.get('comparison_version') != 'V2_AUTH_DIRECT_PUBLICPACK' or not grant_path.exists():
        raise RuntimeError('V2_ROOT_RELEASE_AND_EXPLICIT_PILOT_GRANT_REQUIRED_NO_POST_NATIVE')
    grant = read(grant_path)
    assert grant.get('root_authorized') is True and grant.get('version') == protocol['version']
    assert grant.get('phase') == 'Round2320Pilot', 'V2_NO_BORROWING_MAIN'
    assert grant.get('source_seal_sha256') == sha(V / 'source_seal_v2.json'), 'V2_SEAL_GRANT_DRIFT'
    assert grant.get('pack_registry_sha256') == sha(V / 'pack_registry_v2.json'), 'V2_PACK_GRANT_DRIFT'
    root_v2_path = ROOT_V2_PROTOCOL.resolve()
    assert root_v2_path.is_relative_to(ROOT / '工作区/1008-2320-baseline-main'), 'V2_ROOT_PROTOCOL_SCOPE'
    assert sha(root_v2_path) == grant['root_v2_protocol_sha256'] == runtime.get('root_v2_protocol_sha256') == ROOT_V2_SHA, 'V2_ROOT_PROTOCOL_GRANT_DRIFT'
    assert read(root_v2_path)['version'] == protocol['version'], 'V2_ROOT_PROTOCOL_VERSION_DRIFT'
    assert protocol['source_root_protocol_sha256'] == sha(protocol['source_root_protocol'])
    if time.time() >= NO_TEST: raise RuntimeError('NO_NEW_V2_AFTER_AUTHORIZED_CUTOFF')
    for path, expected in read(V / 'source_seal_v2.json')['sealed_files'].items():
        assert sha(path) == expected, 'V2_SEALED_FILE_DRIFT ' + path
    return protocol


def body_v2(role, messages, temperature, seed, cap, task_id, method, pack, schema=None, tools=None, reader_index=0):
    # The same complete pack is pre-materialized in every arm's request.
    materialized = copy.deepcopy(messages)
    # Fixed pack prefix permits provider caching without dropping any evidence.
    # The original author request stays last, preserving its output instruction.
    insert_at = 1 if materialized and materialized[0].get('role') == 'system' else 0
    materialized.insert(insert_at, {'role': 'user', 'content': render(pack)})
    actual_seed = int(hashlib.sha256(canonical({'master': 20261008, 'task': task_id, 'method': method,
                      'stage': role, 'original_fixed_stage_seed': int(seed), 'reader_index': reader_index}).encode()).hexdigest()[:8], 16) % 2147483647
    body = {'model': 'deepseek-flash', 'messages': materialized, 'thinking': {'type': 'disabled'},
            'temperature': temperature, 'seed': actual_seed, 'max_tokens': cap, 'stream': False}
    if schema: body['response_format'] = {'type': 'json_object'}
    if tools: body.update(tools=copy.deepcopy(tools), tool_choice='auto')
    return body


class EnvironmentV2(FreshEnvironment):
    def __init__(self, ref, method):
        authorize_v2()
        super().__init__(ref, method)
        self.pack = read(V / 'packs' / (self.task_id + '.json'))
        decoded = decode(self.pack)
        assert self.pack['input_digest'] == ref['input_digest']
        actual = {p: sha(self.repo_root / p) for p in self.business_files()}
        assert actual == self.pack['c0_business_paths_sha256'], 'V2_C0_BUSINESS_SOURCE_DRIFT'
        self.finance_phase = 'Round2320Pilot'
        self._full_public_failures = copy.deepcopy(decoded['failure_feedback'])
        self._initial_public_captured_output = decoded.get('original_public_captured_output')
        self.initial_public_feedback = initial_index_v2(self.pack)
        self.goal = 'Recover the observed public failure and preserve already passing ordinary behavior. Original issue background: ' + decoded['original_issue']
        self.task['failure_feedback'] = copy.deepcopy(self.initial_public_feedback)
        self.public_spec['initial_failure'] = copy.deepcopy(self.initial_public_feedback)
        self.record('V2_AUTH_DIRECT_PUBLICPACK', {'pack_sha256': sha(V / 'packs' / (self.task_id + '.json')),
                    'semantic_sha256': self.pack['decoded_semantic_sha256'], 'exact_public_roundtrip': True,
                    'same_pack_all_arms': True, 'independent_v1_outputs': True,
                    'AL_added_reader_loop_removed': True, 'original_shared_rights_preserved': True})

    def _require(self):
        authorize_v2()
        return super()._require()

    def llm(self, role, messages, temperature, seed, max_tokens, schema=None, tools=None):
        if self.finance_fatal: raise RuntimeError('V2_FINANCE_FATAL_NO_MORE_POST')
        protocol = authorize_v2(); self._require()
        is_al = role.startswith('agentless_')
        if is_al and role in ('agentless_patch', 'agentless_reproduction'):
            self.restore(self.initial_snapshot)
            actual = {p: hashlib.sha256(t.encode()).hexdigest() for p, t in self.business_files().items()}
            assert actual == self._independent_C0_hashes, 'V2_INDEPENDENT_C0_RESTORE_DRIFT'
            self.record('v2_independent_C0_restored', {'role': role, 'business_digest': digest(actual)})
        group = ('agentless_localize' if role in ('agentless_suspicious_files', 'agentless_irrelevant_folders', 'agentless_related_elements', 'agentless_fine_locations')
                 else 'agentless_regression_or_vote' if role == 'agentless_regression_exclusion'
                 else 'ours_patch' if role.startswith('ranked_repair') else role)
        cap = int(protocol['budget']['role_output_caps'].get(group, shared.Flash.OUTPUT_LIMITS.get(role, 16384)))
        current = shared.neutral(copy.deepcopy(messages), self) if is_al else self._messages(messages)
        # AL stages already receive original tree/skeleton/fine context and use
        # SEARCH/REPLACE. Preserve other arms' legal reader rights, bounded only
        # by the common whole-flow budget, never a new per-stage reader cap.
        attached = [] if is_al else copy.deepcopy(tools or []) + copy.deepcopy(shared.TOOLS)
        transport = module('exp224_v2_shared_transport', TRANSPORT)
        reader_index = 0
        while True:
            self._require()
            if self.calls >= 64 or self.out_tokens + cap > 65536:
                raise shared.Base.BudgetError('COMMON_FLOW_CALL_OR_OUTPUT_CAP')
            body = body_v2(role, current, temperature, seed, cap, self.task_id, self.method, self.pack, schema, attached, reader_index)
            self.record('v2_actual_body_preflight', {'role': role, 'body_sha256': digest(body),
                        'serialized_body_utf8_bytes': len(canonical(body).encode()), 'reader_index': reader_index,
                        'AL_no_reader_tools': is_al, 'pack_semantic_sha256': self.pack['decoded_semantic_sha256']})
            self.calls += 1
            try: response = transport.generate(self, body, 'Exp224/V2_AUTH_DIRECT_PUBLICPACK/' + self.method + '/' + self.task_id + '/' + role, phase='Round2320Pilot')
            except Exception as error:
                if type(error).__name__.startswith('Finance'):
                    self.finance_fatal = {'type': type(error).__name__, 'message': str(error), 'at_utc': now()}
                    self.record('finance_fatal224', self.finance_fatal)
                raise
            usage = response['usage']; self.out_tokens += usage['completion_tokens']
            message = response['choices'][0]['message']; finish = response['choices'][0].get('finish_reason')
            self.record('Flash_actual_response224', {'role': role, 'call_ordinal': self.calls, 'usage': usage,
                        'seed': body['seed'], 'original_fixed_stage_seed': seed, 'reader_index': reader_index,
                        'temperature': temperature, 'finish_reason': finish, 'version': protocol['version']})
            if finish == 'length': self.truncated_responses.append(self.calls)
            tc = message.get('tool_calls') or []
            if not tc or is_al or any(c['function']['name'] not in ('read_full_failure', 'read_current_source', 'list_current_sources', 'read_public_history') for c in tc):
                return {'content': message.get('content') or '', 'message': message, 'tool_calls': tc,
                        'usage': usage, 'call_ordinal': self.calls, 'finish_reason': finish,
                        'output_truncated': finish == 'length', 'finance_receipt': response.get('_finance_receipt', {})}
            current.append(message)
            for call in tc:
                try: result = self.reader_call(call['function']['name'], json.loads(call['function']['arguments']))
                except (ValueError, KeyError, TypeError) as error:
                    result = {'status': 'PUBLIC_READER_ARGUMENT_ERROR', 'message': str(error),
                              'correct_public_failure_node_ids': sorted(self._full_public_failures), 'protected_contents_not_returned': True}
                current.append({'role': 'tool', 'tool_call_id': call['id'], 'content': canonical(result)})
            reader_index += 1


# The existing Common wrappers use this module global before every native action.
# This rebinding occurs only in a new isolated V2 process; V1 bytes remain intact.
shared.authorization = authorize_v2

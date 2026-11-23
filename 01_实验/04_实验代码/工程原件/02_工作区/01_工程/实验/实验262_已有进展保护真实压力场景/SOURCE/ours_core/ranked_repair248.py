"""Matched progressive public edit evidence with cumulative semantic repair.

Ranking and generation are unchanged; only public state admission differs. Final private acceptance belongs to
the environment; this adapter reads public edit bindings and public feedback.
"""
import copy
import difflib
import hashlib
import json
import random
import time
from public_projection181 import project_feedback, project_payload
from pathlib import Path
from progress_guard240 import RepairProgressGuard, source_sha, restore_exact

METHODS = (
    'G_PROGRESSIVE_SEMANTIC_FLASH',
    'REVERSE_PROGRESSIVE_SEMANTIC_FLASH',
    'RANDOM_PROGRESSIVE_SEMANTIC_FLASH',
)
MAX_ATTEMPTS = 3
MAX_OUTPUT_TOKENS = 16384
MAX_EVIDENCE_ITEM_BYTES = 128 * 1024
SYSTEM_PROMPT = (
    'You are recovering a failed repository-editing agent. Preserve existing '
    'correct changes. Use the task goal, actual public failure, current business '
    'source and supplied ordered public edit evidence to make the smallest '
    'necessary semantic correction, including missing definitions or inconsistent '
    'call interfaces. The evidence list expands across attempts; use public native '
    'feedback and the current cumulative code state. You may edit any listed legal '
    'business path. Return only JSON with rationale and edits:[{path,old,new}]. '
    'old must match one unique exact current business span. You may list and read '
    'the shared readonly masked public tests through the supplied tools. Do not edit tests, '
    'inspect private/reference files, or use issue-specific constants. Never '
    'claim success without native execution.'
)
OLD_PLANS = Path(
    'D:/Code/毕设/graduate-thesis-experiments/工作区/1007-exp166-four-paper-baselines/'
    '实验/实验166_四项正式论文基线快速整体验证/frozen_plans'
)


class SourceEvidenceError(RuntimeError):
    pass


class ContextEvidenceUnknown(SourceEvidenceError):
    pass


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _bytes(value):
    return len(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))


def _diff(before, after, path):
    return ''.join(difflib.unified_diff(
        before.splitlines(True), after.splitlines(True),
        fromfile=path + ':before', tofile=path + ':after', n=5))


def _context(before, after, current):
    """The same actual-code context rule for every evidence item in every arm."""
    lines = current.splitlines()
    ranges = []
    for tag, a, b, c, d in difflib.SequenceMatcher(
            None, before.splitlines(), after.splitlines()).get_opcodes():
        if tag != 'equal':
            ranges.append((max(0, c - 30), min(len(lines), max(c + 1, d) + 30)))
    if not ranges:
        ranges = [(0, min(len(lines), 80))]
    merged = []
    for left, right in sorted(ranges):
        if merged and left <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(right, merged[-1][1]))
        else:
            merged.append((left, right))
    return [{'start_line': a + 1, 'end_line': b, 'text': '\n'.join(lines[a:b])}
            for a, b in merged]


def _refresh(item, env):
    before, after = item['_before'], item['_after']
    current = env.read_file(item['path'])
    public = {k: v for k, v in item.items() if not k.startswith('_')}
    public.update(current_sha256=_sha(current.encode('utf-8')),
                  after_current_diff=_diff(after, current, item['path']),
                  current_file_context=_context(before, after, current))
    sizes = {
        'before_after_diff_bytes': len(public['before_after_diff'].encode('utf-8')),
        'after_current_diff_bytes': len(public['after_current_diff'].encode('utf-8')),
        'current_context_text_bytes': sum(len(b['text'].encode('utf-8'))
                                          for b in public['current_file_context']),
        'serialized_evidence_bytes': _bytes(public),
    }
    return public, sizes


def _source_evidence(env):
    began = time.monotonic()
    files = env.business_files()
    mapping = env.ref['mapping']
    by_step = {r['step']: r for r in mapping}
    ordinals = list(range(len(mapping)))
    if sorted(by_step) != ordinals or len(by_step) != len(mapping):
        raise SourceEvidenceError('INCOMPLETE_OR_DUPLICATE_ORIGINAL_ORDINAL_MAPPING')
    receipt = {'method': env.method, 'original_ordinal_count': len(mapping),
               'no_new_encoding_fit_forward_or_Gold': True,
               'code_context_rule': 'Actual 30-line changed-span context, merged; no clipping',
               'max_evidence_item_bytes': MAX_EVIDENCE_ITEM_BYTES}
    if env.method == METHODS[0]:
        rank_path = Path(env.ref.get('G_frozen_plan', OLD_PLANS / env.task_id / 'OURS_G153_VBR.json'))
        rank_bytes = rank_path.read_bytes()
        frozen = json.loads(rank_bytes.decode('utf-8-sig'))
        order = frozen['complete_original_ordinal_order']
        if sorted(order) != ordinals or len(order) != len(ordinals):
            raise SourceEvidenceError('G_ORDER_DOES_NOT_MATCH_COMPLETE_ORIGINAL_STEP_MAPPING')
        receipt.update(order_source='Frozen complete G original ordinal order',
                       G_frozen_plan=str(rank_path), G_frozen_plan_sha256=_sha(rank_bytes))
    elif env.method == METHODS[1]:
        order = sorted(ordinals, reverse=True)
        receipt['order_source'] = 'All original ordinals in descending order'
    elif env.method == METHODS[2]:
        seed_text = 'Exp178|randomorder|' + env.task_id
        seed_hex = hashlib.sha256(seed_text.encode('utf-8')).hexdigest()
        order = ordinals.copy()
        random.Random(int(seed_hex, 16)).shuffle(order)
        receipt.update(order_source='Fixed shuffled complete original ordinal list',
                       order_seed_text=seed_text, order_seed_sha256=seed_hex,
                       order_seed=int(seed_hex, 16))
    else:
        raise ValueError('EXP178_RANKED_REPAIR_METHOD_IDENTITY_MISMATCH')
    receipt['complete_original_ordinal_order'] = order
    edits_path = Path(env.ref['task_path']) / 'visible/edits.json'
    edits_bytes = edits_path.read_bytes()
    edits = json.loads(edits_bytes.decode('utf-8-sig'))
    by_id = {e['call_id']: e for e in edits}
    if len(by_id) != len(edits):
        raise SourceEvidenceError('DUPLICATE_VISIBLE_EDIT_CALL_ID')
    assets = Path(env.ref['asset_root'])
    blob_cache = {}

    def blob(binding):
        if binding is None:
            return ''
        key = (binding['blob'], binding['sha256'])
        if key not in blob_cache:
            raw = (assets / binding['blob']).read_bytes()
            if _sha(raw) != binding['sha256']:
                raise SourceEvidenceError('PUBLIC_EDIT_BLOB_SHA_DRIFT')
            blob_cache[key] = raw.decode('utf-8')
        return blob_cache[key]

    all_evidence = []
    all_bindings = []
    seen = set()
    skipped = []
    for step in order:
        for call_id in by_step[step]['successful_edit_ids']:
            if call_id in seen:
                continue
            seen.add(call_id)
            edit = by_id.get(call_id)
            if edit is None:
                raise SourceEvidenceError('PUBLIC_EDIT_ID_MISSING_FROM_BOUND_VISIBLE_EDITS')
            path = edit['state_path'].removeprefix('repo/')
            if path not in files:
                skipped.append({'step': step, 'call_id': call_id, 'reason': 'OUTSIDE_CURRENT_LEGAL_BUSINESS_PATHS'})
                continue
            before, after = blob(edit.get('before')), blob(edit.get('after'))
            if before == after:
                skipped.append({'step': step, 'call_id': call_id, 'reason': 'NO_ACTUAL_BEFORE_AFTER_CHANGE'})
                continue
            item = {'step': step, 'call_id': call_id, 'path': path,
                    'before_sha256': _sha(before.encode('utf-8')),
                    'after_sha256': _sha(after.encode('utf-8')),
                    'before_after_diff': _diff(before, after, path),
                    '_before': before, '_after': after}
            public, sizes = _refresh(item, env)
            all_evidence.append(item)
            all_bindings.append({'step': step, 'call_id': call_id, 'path': path,
                                 'before_sha256': item['before_sha256'],
                                 'after_sha256': item['after_sha256'],
                                 'current_sha256': public['current_sha256'],
                                 'before_after_diff_sha256': _sha(public['before_after_diff'].encode('utf-8')),
                                 'after_current_diff_sha256': _sha(public['after_current_diff'].encode('utf-8')),
                                 **sizes})
    selected = all_evidence[:MAX_ATTEMPTS]
    receipt.update(visible_edits_sha256=_sha(edits_bytes),
                   all_legal_successful_edit_bindings=all_bindings,
                   all_legal_successful_edit_count=len(all_evidence),
                   selected_evidence_ids=[e['call_id'] for e in selected],
                   selected_evidence_steps=[e['step'] for e in selected],
                   skipped_public_edits=skipped, ranking_used=bool(selected),
                   no_legal_ranked_edit_fallback=not selected,
                   missing_evidence_not_fabricated=True,
                   source_seconds=time.monotonic() - began)
    return receipt, selected


def _parse_patch(response, files):
    raw = response.get('content', '') if isinstance(response, dict) else response
    data = json.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get('rationale'), str):
        raise ValueError('RATIONALE_STRING_REQUIRED')
    edits = data.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('NONEMPTY_EDITS_ARRAY_REQUIRED')
    normalized = []
    for edit in edits:
        if not isinstance(edit, dict) or not all(isinstance(edit.get(k), str) for k in ('path', 'old', 'new')):
            raise ValueError('PATH_OLD_NEW_STRINGS_REQUIRED')
        path = edit['path'].replace('\\', '/').removeprefix('repo/')
        if path not in files or not edit['old'] or edit['old'] == edit['new']:
            raise ValueError('EXISTING_BUSINESS_PATH_AND_NONEMPTY_NONIDENTICAL_SPAN_REQUIRED')
        normalized.append({'path': 'repo/' + path, 'old': edit['old'], 'new': edit['new']})
    return data['rationale'], normalized


def _known_public(result):
    native = result.get('native_record', {})
    if native.get('known_public_product_collection_failure'):
        if not (native.get('executed') and native.get('guard_loaded') and native.get('business_state_unchanged')
                and native.get('frozen_tests_unchanged') and not native.get('timeout')
                and native.get('original_certified_failure_rule_reused')
                and native.get('all_matched_syntax_source_bytes_unchanged_from_initial')
                and native.get('matched_public_goal_nodes')):
            raise SourceEvidenceError('PUBLIC_CERTIFIED_SOURCE_FAILURE_GUARD_UNKNOWN')
        return False, len(native['matched_public_goal_nodes'])
    if not (native.get('executed') and native.get('guard_loaded') and native.get('business_state_unchanged')
            and native.get('frozen_tests_unchanged') and native.get('exact_test_coverage')
            and not native.get('timeout')):
        raise SourceEvidenceError('PUBLIC_NATIVE_GUARD_OR_COVERAGE_UNKNOWN')
    outcomes = native.get('pytest', {}).get('outcomes', {})
    if not outcomes:
        raise SourceEvidenceError('PUBLIC_NATIVE_OUTCOMES_MISSING')
    failures = sum(v.get('status') != 'passed' for v in outcomes.values())
    return native.get('passed') is True, failures


def _public_feedback(value):
    return project_feedback(value)


def _changed_lines(diff):
    return sum(sum(s.startswith(('+', '-')) and not s.startswith(('+++', '---'))
                   for s in d.get('unified_diff', '').splitlines()) for d in diff)


def run(env):
    if env.method not in METHODS:
        raise ValueError('EXP178_RANKED_REPAIR_METHOD_IDENTITY_MISMATCH')
    ledger, candidates, history = [], [], []
    calls = parsed = applied = public_runs = 0
    current = copy.deepcopy(env.initial_snapshot)
    final = copy.deepcopy(current)
    status, error, selection, evidence = 'COMPLETED', None, None, None
    first_pass = None
    initial_failure = copy.deepcopy(env.task.get('failure_feedback', {}))
    public_events = []
    initial_failed_nodes = sum(isinstance(v, dict) and v.get('status') in ('failed', 'error')
                               for v in initial_failure.values()) if isinstance(initial_failure, dict) else 0
    best_key = (initial_failed_nodes, 0, 0) if initial_failed_nodes else None
    initial_calls = getattr(env, 'calls', 0)
    admission = None
    accepted_snapshot = copy.deepcopy(current)
    terminal_guard = None
    done = {'source_evidence': False, 'actual_generation': False, 'legal_application': False,
            'guarded_public_validation': False, 'public_only_selection': False}

    def record(stage, data):
        ledger.append({'stage': stage, **copy.deepcopy(data)})
        env.record('ranked_repair178_' + stage, data)

    def output_failure(row, message, truncated=False):
        row.update(outcome='OUTPUT_TRUNCATED_UNKNOWN' if truncated else 'MODEL_SEMANTIC_FAILURE',
                   output_error=message, normal_model_semantic_failure=not truncated)
        public_events.append({'attempt': row['attempt'], 'model_output_error': message,
                              'output_truncated': truncated})
        record('output_failure', row)

    try:
        admission = RepairProgressGuard.begin(env)
        best_key = (admission.failed_count, 0, 0)
        initial_goal_pass = sorted(admission.incumbent['goal_pass'])
        initial_source = copy.deepcopy(admission.incumbent_source)
        record('state_admission_initialized', admission.summary())
        evidence, selected = _source_evidence(env)
        done['source_evidence'] = True
        record('source_evidence', evidence)
        for attempt in range(1, MAX_ATTEMPTS + 1):
            restore_exact(env, current, admission.incumbent_source)
            files = env.business_files()
            ordered, byte_rows = [], []
            for item in selected[:attempt]:
                public, sizes = _refresh(item, env)
                ordered.append(public)
                byte_rows.append({'call_id': item['call_id'], **sizes})
            row = {'attempt': attempt, 'evidence_ids': [v['call_id'] for v in ordered],
                   'evidence_steps': [v['step'] for v in ordered],
                   'evidence_count': len(ordered), 'evidence_item_bytes': byte_rows,
                   'ranking_used': bool(ordered), 'output_truncated': False,
                   'parsed': False, 'applied': False, 'valid_public': False,
                   'public_passed': None}
            history.append(row)
            if any(v['serialized_evidence_bytes'] > MAX_EVIDENCE_ITEM_BYTES for v in byte_rows):
                row['outcome'] = 'CONTEXT_EVIDENCE_UNKNOWN'
                record('context_unknown', row)
                raise ContextEvidenceUnknown('PUBLIC_EVIDENCE_ITEM_EXCEEDS_128_KIB_NO_CLIPPING')
            if not ordered:
                # No synthetic edit, rank, or call id; the same full source fallback
                # is available to all arms and explicitly remains unranked.
                ordered = [{'no_legal_edit_evidence': True, 'ranking_used': False,
                            'current_business_source': files}]
                fallback_bytes = _bytes(ordered[0])
                row['fallback_source_bytes'] = fallback_bytes
                if fallback_bytes > MAX_EVIDENCE_ITEM_BYTES:
                    row['outcome'] = 'CONTEXT_EVIDENCE_UNKNOWN'
                    record('context_unknown', row)
                    raise ContextEvidenceUnknown('PUBLIC_SOURCE_FALLBACK_EXCEEDS_128_KIB_NO_CLIPPING')
            current_diff = env.diff()
            payload = {'ordered_public_edit_evidence': ordered, 'goal': env.goal,
                       'initial_public_failure': _public_feedback(initial_failure),
                       'latest_public_feedback': {
                           'complete_attempt_feedback': copy.deepcopy(public_events),
                           'current_incumbent_public_feedback': _public_feedback(
                               admission.current_public_feedback(source_sha(env)))},
                       'current_business_diff': current_diff,
                       'legal_paths': sorted(files), 'attempt': attempt}
            payload, projection_audit = project_payload(payload)
            env.record('public_projection181', {'attempt': attempt, **projection_audit})
            messages = [{'role': 'system', 'content': SYSTEM_PROMPT},
                        {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)}]
            seed_text = 'Exp178|repair|' + env.task_id + '|' + str(attempt)
            seed = int(hashlib.sha256(seed_text.encode('utf-8')).hexdigest()[:8], 16) % 2147483647
            row.update(seed=seed, seed_text=seed_text, temperature=0.0,
                       max_output_tokens=MAX_OUTPUT_TOKENS,
                       prompt_utf8_bytes=sum(len(v['content'].encode('utf-8')) for v in messages),
                       current_business_diff_bytes=_bytes(current_diff),
                       payload_sha256=_sha(messages[1]['content'].encode('utf-8')))
            record('attempt_input', row)
            env.checkpoint_boundary("MODEL_READY", locals())
            calls += 1
            try:
                response = env.llm('ranked_repair178_semantic_correction', messages, 0.0, seed,
                                   MAX_OUTPUT_TOKENS, schema={'type': 'object'})
            except Exception as output_error:
                if type(output_error).__name__ != 'ModelOutputError':
                    raise
                truncated = any(token in str(output_error).upper() for token in ('LENGTH', 'TRUNCAT'))
                row['output_truncated'] = truncated
                done['actual_generation'] = True
                output_failure(row, str(output_error), truncated)
                continue
            done['actual_generation'] = True
            content = response.get('content', '') if isinstance(response, dict) else response
            truncated = isinstance(response, dict) and response.get('finish_reason') == 'length'
            row.update(output_truncated=bool(truncated),
                       finish_reason=response.get('finish_reason') if isinstance(response, dict) else None,
                       response_content_sha256=_sha(content.encode('utf-8')),
                       response_utf8_bytes=len(content.encode('utf-8')),
                       call_ordinal=response.get('call_ordinal') if isinstance(response, dict) else None,
                       usage=response.get('usage', {}) if isinstance(response, dict) else {})
            record('generation', row)
            try:
                rationale, edits = _parse_patch(response, files)
            except (ValueError, TypeError, KeyError) as parse_error:
                output_failure(row, str(parse_error), bool(truncated))
                continue
            parsed += 1
            row.update(parsed=True, parsed_complete_json=True,
                       truncated_prefix_usable_complete_json=bool(truncated))
            incumbent = copy.deepcopy(current)
            incumbent_source = copy.deepcopy(admission.incumbent_source)
            application = env.apply_patch(edits, 'ranked_repair178_cumulative_' + str(attempt),
                                          from_snapshot=current)
            legal = application.get('legal', {})
            legal = legal.get('legal') if isinstance(legal, dict) else legal
            if legal is not True or application.get('apply_errors') or not application.get('snapshot'):
                restore_exact(env, current, incumbent_source)
                row.update(outcome='APPLICATION_FAILURE',
                           application_errors=application.get('apply_errors', []))
                public_events.append({'attempt': attempt,
                                      'application_errors': application.get('apply_errors', []),
                                      'previous_legal_snapshot_retained': True})
                record('application_failure', row)
                continue
            current = copy.deepcopy(application['snapshot'])
            applied += 1
            row['applied'] = True
            done['legal_application'] = True
            record('candidate', {'attempt': attempt, 'rationale': rationale, 'application': application})
            native_before = getattr(env, 'native_calls', 0)
            validation = env.run_regression(snapshot=current, label='ranked_repair178_public_' + str(attempt))
            public_runs += 1
            row['physical_native_calls'] = getattr(env, 'native_calls', 0) - native_before
            candidate_source = source_sha(env)
            decision = admission.consider(validation, candidate_source)
            if decision['accepted']:
                accepted_snapshot = copy.deepcopy(current)
            passed, failures = _known_public(validation)
            done['guarded_public_validation'] = True
            row.update(valid_public=True, public_passed=passed, public_failure_count=failures,
                       outcome='PUBLIC_PASS' if passed else 'PUBLIC_FAILURE',
                       normal_model_semantic_failure=not passed and not truncated,
                       physical_native_calls=getattr(env, 'native_calls', 0) - native_before)
            # The complete real public result is retained. Host branch identity
            # paths are metadata, not public feedback content supplied to the model.
            projected_validation=_public_feedback(validation)
            from public_projection181 import sha as feedback_sha
            env.record('feedback_projection181', {'attempt':attempt,'raw_feedback_sha256':feedback_sha(validation),'projected_feedback_sha256':feedback_sha(projected_validation),'raw_feedback_retained_in_ordinary_regression_record':True,'raw_public_nodes_sha256':feedback_sha(validation.get('native_record',{}).get('pytest',{}).get('outcomes',{})),'projected_public_nodes_sha256':feedback_sha(projected_validation.get('native_record',{}).get('pytest',{}).get('outcomes',{}))})
            public_events.append({'attempt': attempt, 'public_validation': projected_validation,
                'observed_business_inventory_sha256': hashlib.sha256(json.dumps(
                    {p: hashlib.sha256(t.encode()).hexdigest() for p, t in sorted(env.business_files().items())},
                    ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()})
            # Only complete actual public outcomes can admit a candidate state.
            row['state_admission'] = copy.deepcopy(decision)
            row['guard_rejected'] = not decision['accepted']
            record('public_state_admission', decision)
            if not decision['accepted']:
                rejected_snapshot = copy.deepcopy(current)
                restore_exact(env, incumbent, incumbent_source)
                current = copy.deepcopy(incumbent)
                public_events[-1].update(
                    historical_rejected_attempt=True,
                    rejected_candidate_inventory_sha256=rejected_snapshot['inventory_sha256'],
                    current_incumbent_inventory_sha256=current['inventory_sha256'],
                    candidate_observation_is_not_current_state=True,
                    recovery='Rejected by public state-admission predicate; incumbent restored exactly')
                env.rejected_history.append(copy.deepcopy(public_events[-1]))
                record('public_guard_rejected_and_incumbent_restored', {
                    'attempt': attempt, 'rejected_snapshot': rejected_snapshot,
                    'restored_incumbent': current, 'actual_restored_business_source_sha256': source_sha(env),
                    'state_admission': decision, 'private_reads': 0,
                    'next_input_requires_actual_restored_SHA': True})
                continue
            candidate = {'attempt': attempt, 'snapshot': copy.deepcopy(current),
                         'public_passed': passed, 'public_failure_count': failures,
                         'changed_lines': _changed_lines(env.diff()), 'public_validation': validation,
                         'new_physical_native_calls': row['physical_native_calls'],
                         'evidence_ids': row['evidence_ids'], 'output_truncated': bool(truncated),
                         'actual_goal_PASS': sorted(decision['candidate_actual_goal_PASS']),
                         'business_source_sha256': copy.deepcopy(candidate_source)}
            candidates.append(candidate)
            record('public_validation', candidate)
            key = (failures, candidate['changed_lines'], attempt)
            if best_key is None or key < best_key:
                best_key, final = key, copy.deepcopy(current)
            if passed:
                first_pass = attempt
                final = copy.deepcopy(current)
                break
        if first_pass is None and any(r['output_truncated'] for r in history):
            status = 'OUTPUT_TRUNCATED_UNKNOWN'
        elif not candidates:
            status = 'MODEL_SEMANTIC_FAILURE'
        # Filter the old quality choice by the final protected identity set.
        # C0 is eligible only when its actual observed PASS set still covers F.
        if admission.mode == 'PROGRESS_SET':
            observed = [{'attempt': 0, 'snapshot': copy.deepcopy(env.initial_snapshot),
                'public_failure_count': len(env.recovery_goal_nodes)-len(initial_goal_pass),
                'changed_lines': 0, 'actual_goal_PASS': initial_goal_pass,
                'business_source_sha256': initial_source}] + candidates
            eligible = [row for row in observed
                if admission.frontier <= set(row['actual_goal_PASS'])]
            if not eligible:
                raise SourceEvidenceError('EXP242_NO_TERMINAL_SNAPSHOT_COVERS_FINAL_FRONTIER')
            picked = min(eligible, key=lambda row: (row['public_failure_count'],
                row['changed_lines'], row['attempt']))
            final = copy.deepcopy(picked['snapshot'])
            best_key = (picked['public_failure_count'], picked['changed_lines'], picked['attempt'])
            restore_exact(env, final, picked['business_source_sha256'])
            terminal_guard = {'final_protected_goal_set': sorted(admission.frontier),
                'selected_actual_goal_PASS': picked['actual_goal_PASS'],
                'selected_source_sha256': picked['business_source_sha256'],
                'selected_observation_attempt': picked['attempt'],
                'eligible_observed_snapshot_count': len(eligible),
                'final_frontier_preserved': True, 'extra_native_or_private': 0}
            record('terminal_frontier_eligible_selection', terminal_guard)
        selection = env.select(final, {
            'rule': 'First full PASS; SET terminal snapshots must cover final F; then minimum public failures, changed lines, earliest attempt',
            'terminal_guard': copy.deepcopy(terminal_guard),
            'selected_key': best_key, 'uses_hidden': False})
        if terminal_guard is not None:
            restore_exact(env, final, terminal_guard['selected_source_sha256'])
        else:
            env.restore(final)
        done['public_only_selection'] = True
        record('selection', {'selection': selection, 'key': best_key, 'uses_hidden': False})
    except Exception as exc:
        name = type(exc).__name__
        status = ('BUDGET_CENSORED' if 'Budget' in name or 'Budget' in str(exc) or name == 'FinanceGateRejected'
                  else 'MODEL_SEMANTIC_FAILURE' if name == 'ModelOutputError'
                  else 'CONTEXT_EVIDENCE_UNKNOWN' if isinstance(exc, ContextEvidenceUnknown)
                  else 'ENGINEERING_UNKNOWN')
        error = {'type': name, 'message': str(exc)}
        record('failure', {'status': status, 'error': error})
        try:
            if admission is not None and admission.mode == 'PROGRESS_SET':
                final = copy.deepcopy(accepted_snapshot)
                restore_exact(env, final, admission.incumbent_source)
            else:
                env.restore(final)
        except Exception as restore_error:
            status = 'ENGINEERING_UNKNOWN'
            error['restore_error'] = str(restore_error)
    return {'method': env.method, 'status': status, 'final_snapshot': final,
            'selection': selection, 'stage_ledger': ledger, 'error': error,
            'source_evidence': evidence, 'candidates': candidates, 'attempt_history': history,
            'first_public_pass_attempt': first_pass,
            'runtime_core': {'complete': all(done.values()), 'actual_stages': done,
                             'scheduled_generation_attempts': calls,
                             'actual_generation_requests': max(0, getattr(env, 'calls', 0) - initial_calls),
                             'actual_returned_model_responses': sum(r['stage'] == 'generation' for r in ledger),
                             'actual_parsed_patches': parsed, 'actual_valid_applications': applied,
                             'actual_public_validation_calls': public_runs,
                             'actual_physical_candidate_native_calls': sum(r.get('physical_native_calls', 0) for r in history),
                             'max_generation_attempts': MAX_ATTEMPTS,
                             'max_output_tokens_per_generation': MAX_OUTPUT_TOKENS,
                             'progressive_evidence_counts': [r['evidence_count'] for r in history],
                             'evidence_ids_by_attempt': [r['evidence_ids'] for r in history],
                             'evidence_bytes_by_attempt': [r['evidence_item_bytes'] for r in history],
                             'first_public_pass_attempt': first_pass,
                             'source_seconds': evidence.get('source_seconds') if evidence else None,
                             'attempt_history': history, 'cumulative_legal_edits': True,
                             'shared_neutral_prompt': True,
                             'shared_prompt_sha256': _sha(SYSTEM_PROMPT.encode('utf-8')),
                             'output_truncated_attempts': [r['attempt'] for r in history if r['output_truncated']],
                             'no_API_retries': True, 'no_evidence_clipping': True,
                             'public_state_admission': admission.summary() if admission else None,
                             'terminal_frontier_selection': terminal_guard},
            'declared_method_failure_known': status in ('MODEL_SEMANTIC_FAILURE', 'BUDGET_EXHAUSTED'),
            'engineering_outcome_unknown': status in ('ENGINEERING_UNKNOWN', 'CONTEXT_EVIDENCE_UNKNOWN',
                                                       'OUTPUT_TRUNCATED_UNKNOWN'),
            'hidden_calls_in_adapter': 0, 'new_Gold': 0, 'new_encoding': 0,
            'new_training': 0, 'new_ranker_forward': 0}

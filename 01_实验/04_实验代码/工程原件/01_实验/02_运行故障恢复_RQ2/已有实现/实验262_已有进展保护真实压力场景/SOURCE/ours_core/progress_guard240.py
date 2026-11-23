"""Public state admission only: no generation, native execution, private IO, or finance."""
import copy
import hashlib
import json
from pathlib import Path

MODES = ('PROGRESS_SET', 'ORDINARY_GUARD', 'COUNT_TNR')
KNOWN = {'passed', 'failed', 'error'}


class ProgressObservationUnknown(RuntimeError):
    pass


class ProgressRestoreUnknown(RuntimeError):
    pass


def _digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def source_sha(env):
    files = env.business_files()
    if not isinstance(files, dict) or not files or not all(
            isinstance(p, str) and isinstance(text, str) for p, text in files.items()):
        raise ProgressObservationUnknown('PROGRESS_ACTUAL_BUSINESS_SOURCE_UNKNOWN')
    return {p: hashlib.sha256(text.encode('utf-8')).hexdigest()
            for p, text in sorted(files.items())}


def restore_exact(env, snapshot, expected_source):
    try:
        env.restore(snapshot)
        actual = source_sha(env)
    except Exception as exc:
        raise ProgressRestoreUnknown('PROGRESS_INCUMBENT_RESTORE_FAILED: '+str(exc)) from exc
    if actual != expected_source:
        raise ProgressRestoreUnknown('PROGRESS_INCUMBENT_RESTORE_SOURCE_SHA_MISMATCH')
    return actual


def observe(validation, goals, ordinary):
    goals, ordinary = set(goals), set(ordinary)
    if not goals or goals & ordinary:
        raise ProgressObservationUnknown('PROGRESS_PUBLIC_NODE_DECLARATION_UNKNOWN')
    native = validation.get('native_record', {})
    required = ('executed', 'guard_loaded', 'business_state_unchanged',
                'frozen_tests_unchanged', 'exact_test_coverage', 'completed_guarded_coverage')
    if not all(native.get(k) is True for k in required) or native.get('timeout') is not False:
        raise ProgressObservationUnknown('PROGRESS_FULL_COMPLETED_GUARDED_COVERAGE_UNKNOWN')
    if native.get('known_public_product_collection_failure'):
        raise ProgressObservationUnknown('PROGRESS_CANDIDATE_UNCOLLECTED_GOAL_IS_UNKNOWN')
    expected = goals | ordinary
    requested = native.get('requested_nodes', [])
    outcomes = native.get('pytest', {}).get('outcomes', {})
    if (len(requested) != len(expected) or set(requested) != expected
            or set(outcomes) != expected
            or any(not isinstance(v, dict) or v.get('status') not in KNOWN
                   for v in outcomes.values())):
        raise ProgressObservationUnknown('PROGRESS_GOAL_OR_ORDINARY_IDENTITY_COVERAGE_UNKNOWN')
    if native.get('pytest', {}).get('requested_but_uncollected_nodes'):
        raise ProgressObservationUnknown('PROGRESS_UNCOLLECTED_PUBLIC_NODE_UNKNOWN')
    passed_count = sum(v['status'] == 'passed' for v in outcomes.values())
    if (native.get('expected_test_count') != len(expected)
            or native.get('passed_count') != passed_count
            or native.get('passed') is not (passed_count == len(expected))):
        raise ProgressObservationUnknown('PROGRESS_NATIVE_RESULT_COUNT_INCOHERENT')
    stop = native.get('stop_receipt', {})
    if not all(stop.get(k) is True for k in (
            'owned_job_closed', 'root_process_stopped', 'all_owned_descendants_terminated')):
        raise ProgressObservationUnknown('PROGRESS_PUBLIC_NATIVE_STOP_UNKNOWN')
    derived_ordinary = {n: copy.deepcopy(outcomes[n]) for n in sorted(ordinary)}
    ordinary_result = validation.get('outcomes', {})
    if set(ordinary_result) != ordinary or any(
            ordinary_result[n].get('status') != outcomes[n]['status'] for n in ordinary):
        raise ProgressObservationUnknown('PROGRESS_ORDINARY_RESULT_INCOHERENT')
    # Canonical ordinary-regression wrapper, using complete untouched native data.
    # Runtime C0 reuse and direct native callbacks must render the same first body.
    complete = copy.deepcopy(validation)
    complete['native_record'] = copy.deepcopy(native)
    if native.get('log'):
        complete['native_record']['path'] = str(Path(native['log']).with_name('run.json'))
    complete['outcomes'] = {
        n: {**copy.deepcopy(outcomes[n]), 'outcome': outcomes[n]['status']}
        for n in sorted(ordinary)}
    ordinary_failures = sum(outcomes[n]['status'] != 'passed' for n in ordinary)
    complete['passed'] = ordinary_failures == 0
    complete['failure_count'] = ordinary_failures
    complete.setdefault('status', 'GUARDED_ORDINARY_REGRESSION')
    complete.setdefault('public_goal_not_added_to_paper_ranking', True)
    goal_pass = {n for n in goals if outcomes[n]['status'] == 'passed'}
    return {'goal_pass': goal_pass, 'failed_goals': len(goals - goal_pass),
            'ordinary_pass': all(outcomes[n]['status'] == 'passed' for n in ordinary),
            'ordinary_outcomes': derived_ordinary, 'complete_validation': complete}


class RepairProgressGuard:
    def __init__(self, mode, goals, ordinary, initial_validation, initial_source):
        if mode not in MODES:
            raise ValueError('PROGRESS_UNKNOWN_ARM')
        self.mode, self.goals, self.ordinary = mode, tuple(goals), tuple(ordinary)
        initial = observe(initial_validation, self.goals, self.ordinary)
        if not initial['ordinary_pass']:
            raise ProgressObservationUnknown('PROGRESS_C0_ORDINARY_NOT_INITIAL_PASS')
        # The new version protects actually observed C0 goal PASS identities.
        self.frontier = set(initial['goal_pass']) if mode == 'PROGRESS_SET' else set()
        self.initial_goal_pass = set(initial['goal_pass'])
        self.incumbent = initial
        self.incumbent_source = copy.deepcopy(initial_source)
        self.failed_count = initial['failed_goals']
        self.accepted_count = 0
        self.rejected_count = 0

    @classmethod
    def begin(cls, env, validation=None):
        initial = env.initial_guard_observation() if validation is None else validation
        return cls(env.state_admission_mode, env.recovery_goal_nodes,
                   env.public_regression_nodes, initial, source_sha(env))

    def consider(self, validation, candidate_source):
        observed = observe(validation, self.goals, self.ordinary)
        ordinary_ok = observed['ordinary_pass']
        if self.mode == 'PROGRESS_SET':
            rule_ok = self.frontier <= observed['goal_pass']
        elif self.mode == 'COUNT_TNR':
            rule_ok = observed['failed_goals'] <= self.failed_count
        else:
            rule_ok = True
        decision = {'mode': self.mode, 'accepted': bool(ordinary_ok and rule_ok),
                    'ordinary_all_PASS': ordinary_ok,
                    'previous_protected_goal_set': sorted(self.frontier),
                    'candidate_actual_goal_PASS': sorted(observed['goal_pass']),
                    'previous_incumbent_failed_goal_count': self.failed_count,
                    'candidate_failed_goal_count': observed['failed_goals'],
                    'candidate_business_source_sha256': copy.deepcopy(candidate_source),
                    'candidate_business_inventory_sha256': _digest(candidate_source),
                    'private_reads_or_native_runs_from_guard': 0}
        if decision['accepted']:
            self.incumbent = observed
            self.incumbent_source = copy.deepcopy(candidate_source)
            self.failed_count = observed['failed_goals']
            if self.mode == 'PROGRESS_SET':
                self.frontier |= observed['goal_pass']
            self.accepted_count += 1
        else:
            self.rejected_count += 1
        decision['current_protected_goal_set'] = sorted(self.frontier)
        decision['current_incumbent_failed_goal_count'] = self.failed_count
        decision['current_incumbent_source_sha256'] = copy.deepcopy(self.incumbent_source)
        decision['current_incumbent_inventory_sha256'] = _digest(self.incumbent_source)
        return decision

    def current_public_feedback(self, actual_source):
        if actual_source != self.incumbent_source:
            raise ProgressObservationUnknown('PROGRESS_CURRENT_FEEDBACK_SOURCE_SHA_MISMATCH')
        return {'public_validation': copy.deepcopy(self.incumbent['complete_validation']),
                'goal_actual_PASS_nodes': sorted(self.incumbent['goal_pass']),
                'ordinary_actual_outcomes': copy.deepcopy(self.incumbent['ordinary_outcomes']),
                'observed_business_inventory_sha256': _digest(actual_source),
                'observation_is_current_accepted_incumbent': True,
                'all_public_coverage_actual_complete_guarded': True}

    def summary(self):
        return {'mode': self.mode, 'protected_goal_set': sorted(self.frontier),
                'incumbent_failed_goal_count': self.failed_count,
                'incumbent_source_inventory_sha256': _digest(self.incumbent_source),
                'accepted_candidate_count': self.accepted_count,
                'rejected_candidate_count': self.rejected_count,
                'initial_goal_PASS_from_complete_C0': sorted(self.initial_goal_pass),
                'initial_frontier_seeded_from_actual_C0': self.mode == 'PROGRESS_SET',
                'observations_not_private': True}

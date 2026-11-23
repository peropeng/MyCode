"""Reconcile completed multi-edit controls from public records and ROOT scalars.

This reader never opens private selectors, raw native outputs or ROOT logs.
It performs no model requests and no task execution.
"""
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import json
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE / 'src'))
from thesis_recovery.rq2_control_env import read, save, sha

BASE = ENGINE / '.rebuild/rq2-controls'
TASKS = ['getmoto__moto-5516', 'getmoto__moto-7081', 'getmoto__moto-6212']
CONDITIONS = ['SOURCE3', 'REVERSE', 'SOURCE3_NO_ADDITIONAL_CONTEXT_V2',
              'SOURCE3_MATCHED_NONEDGE_CONTEXT']


def main():
    config = read(ENGINE / 'manifests/rq2_control_execution.json')
    for name, expected in config['code_bindings'].items():
        assert sha(ENGINE / name) == expected, name
    ledger = [read(p) for p in sorted((BASE / 'api/calls').glob('*.json'))
              if not p.name.endswith('.response.json')]
    assert ledger and all(row['status'] == 'completed' for row in ledger)
    rows = []
    for task in TASKS:
        for condition in CONDITIONS:
            run = BASE / 'runs' / task / 'trial1' / condition
            result = run / 'RESULT.json'
            if not result.exists():
                continue
            data = read(result)
            scalar_path = BASE / 'private_ROOT' / task / 'trial1' / condition / 'SCALAR_RESULT.json'
            scalar = read(scalar_path)
            assert data['status'] == 'COMPLETED' and scalar['known']
            assert scalar['all_owned_processes_stopped'] and scalar['selected_source_unchanged']
            assert scalar['original_independent_scope_exactly_preserved']
            assert not data['hidden_calls_in_adapter'] and not data['new_Gold']
            calls = [v for v in ledger if v['sample_id'] == task and v['stage'].startswith(condition + '/trial1/')]
            attempts = []
            for a in data['attempt_history']:
                snapshot = run / 'snapshots' / ('attempt' + str(a['attempt'])) / 'snapshot.json'
                candidate = read(snapshot) if snapshot.exists() else {}
                admission = a.get('state_admission', {})
                attempts.append({'attempt': a['attempt'], 'evidence_steps': a['evidence_steps'],
                    'parsed': a.get('parsed'), 'applied': a.get('applied'),
                    'public_passed': a.get('public_passed'),
                    'state_accepted': admission.get('accepted'),
                    'protected_before_count': len(admission.get('previous_protected_goal_set', [])),
                    'goal_pass_count': len(admission.get('candidate_actual_goal_PASS', [])),
                    'candidate_changed_paths_from_C0': list(candidate.get('diff', {}))})
            costs = {k: str(sum((Decimal(v['receipt'][k]) for v in calls), Decimal(0)))
                     for k in ['cost_lower_cny', 'cost_upper_cny']}
            usage = {k: sum(v['receipt']['usage'].get(k, 0) for v in calls)
                     for k in ['prompt_tokens', 'completion_tokens', 'prompt_cache_hit_tokens', 'prompt_cache_miss_tokens']}
            nonedge = [read(p) for p in sorted((run / 'relations').glob('*_nonedge_match.json'))]
            rows.append({'task_id': task, 'condition': condition, 'trial': 'trial1',
                'status': data['status'], 'success': scalar['success'],
                'goal_passed': scalar['goal_passed'], 'ordinary_passed': scalar['ordinary_passed'],
                'independent_acceptance_passed': scalar['private_passed'],
                'first_public_pass_attempt': data['first_public_pass_attempt'],
                'final_snapshot_id': data['final_snapshot']['id'],
                'final_changed_paths_from_C0': list(data['final_snapshot']['diff']),
                'model_requests': len(calls), 'usage': usage, 'estimated_cost_cny': costs,
                'attempts': attempts, 'nonedge_source_budget_audit': nonedge,
                'sources': {str(p.relative_to(ENGINE)): sha(p) for p in [result, scalar_path, run / 'SELECTED_PUBLIC_ONLY.json']},
                'private_feedback_to_method': False, 'original_independent_scope_exactly_preserved': True})
    assert len(rows) == 8 and sum(v['model_requests'] for v in rows) == len(ledger) == 16
    for condition in ['SOURCE3', 'REVERSE']:
        group = [v for v in rows if v['condition'] == condition]
        assert len(group) == 3 and all(v['success'] for v in group)
    primary = {condition: {'successes': sum(v['success'] for v in rows if v['condition'] == condition),
                            'total': sum(v['condition'] == condition for v in rows)}
               for condition in ['SOURCE3', 'REVERSE']}
    full = next(v for v in rows if v['task_id'].endswith('5516') and v['condition'] == 'SOURCE3')
    ablations = [v for v in rows if v['condition'] not in primary]
    assert full['success'] and all(not v['success'] for v in ablations)
    usage_totals = {k: sum(v['receipt']['usage'].get(k, 0) for v in ledger)
                    for k in ['prompt_tokens', 'completion_tokens', 'prompt_cache_hit_tokens', 'prompt_cache_miss_tokens']}
    costs = {k: str(sum((Decimal(v['receipt'][k]) for v in ledger), Decimal(0)))
             for k in ['cost_lower_cny', 'cost_upper_cny']}
    report = {'schema': 'rq2.multi-edit-controls.audit/1', 'at_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'Exposed development cases; preliminary feasibility, not independent confirmation or final thesis results',
        'independent_problems': 3, 'completed_new_flows': 8, 'paired_primary': primary,
        'sorting_minus_reverse_uplift_percentage_points': '0.00',
        'rows': rows, 'current_generation_usage': {'submitted': len(ledger), 'completed': len(ledger),
            'unresolved': 0, **usage_totals, **costs,
            'cost_basis': 'Official peak upper / idle lower estimate, not a per-request invoice'},
        'additional_prePOST_engineering_attempts': [{'condition': 'SOURCE3_NO_ADDITIONAL_CONTEXT',
            'status': 'ENGINEERING_UNKNOWN', 'new_model_requests': 0,
            'reason': 'Frozen finish_body required feedback/source binding before any HTTP body dispatch',
            'counted_as_method_failure': False}],
        'historical_baselines_rerun': 0, 'new_training': 0,
        'same_new_primary_conditions': ['C0', 'complete public history', 'public G/O', 'no test-source readers',
            'current-source readers', 'generation backend and sampling parameters', 'three attempts',
            'owned native process guard', 'original task-specific independent scope'],
        'goal_progress_opportunity': {'initially_passed_goals': 0,
            'candidate_updates_after_first_all_goal_pass': 0,
            'identity_protection_increment_established': False},
        'historical_comparison_limits': ['Old completed Agentless/EnAgent records reused at their original budgets and permissions',
            'Current no-test-source permission differs; no strict uplift against old complete methods computed',
            'AOrchestra is untested on these three cases; its completed Dask case is kept separate'],
        'module_decisions': {'ranking_order': 'No increment seen; retain as candidate, do not freeze as proven recovery contribution',
            'current_public_feedback_source_package': 'Retain as development mainline: pressure case 1/1 with package vs 0/1 for each two bounded controls',
            'static_relation_specificity': 'Not established against targeted traceback/API-name retrieval; nonedge is a negative control',
            'goal_identity_protection': 'Safety behavior retained; contribution not established by these cases'},
        'validation': {'control_adapter_tests': 7, 'API_accounting_tests': 3, 'scope_admission_tests': 4,
            'all_passed': True, 'real_independent_acceptance_runs': 8,
            'all_completed_actor_and_acceptance_locks_absent': not list((BASE / 'runs').glob('*/*/*/producer.lock'))
                and not list((BASE / 'private_ROOT').glob('*/*/*/acceptance.lock'))}}
    save(ENGINE / 'verification/rq2_multi_edit_control_audit.json', report)
    print(json.dumps({'completed_flows': len(rows), 'paired_primary': primary,
                      'model_requests': len(ledger), **usage_totals, **costs}, ensure_ascii=False))


if __name__ == '__main__':
    main()

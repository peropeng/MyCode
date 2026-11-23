"""Add-only independent AL/G admission; original source and algorithm unchanged."""
from common166 import *
import ast, inspect
from decimal import Decimal
import main_environment_v2_224 as base

PIN = base.V / 'independent_main_source_pin_v2.json'
GRANT = base.V / 'root_independent_main_grant_v2.json'
FIRST = 'Project-MONAI__MONAI-2238'
FIRST_SHA = {
 'AGENTLESS_FSE2025_4L4P4T_FLASH':'a870684150e9594bebdc4897fba232435f8308b06914ea0aa3d2225f98dba436',
 'G_PROGRESSIVE_SEMANTIC_FLASH':'6385787c505b1ce3bd44e3f33b44fabc44103a2ad0d076edf6a6656a07a53a9f'}
GATE = "        assert grant.get('V2_EnAgent_complete_nonzero_root_accepted') is True, 'MAIN_BIG_QUEUE_REQUIRES_ACTUAL_V2_ENAGENT'"

def additional_admission(grant):
    assert grant.get('both_AL_G_actual_V2_complete_nonzero_accepted') is True
    assert grant.get('independent_controller_pin_sha256') == sha(PIN)
    assert grant.get('selected_first_results_sha256') == FIRST_SHA
    assert 0 <= int(grant['allowed_through_index']) <= 2, 'INDEPENDENT_INITIAL_THROUGH2_ONLY'
    for path, expected in read(PIN)['new_sources'].items():
        assert sha(path) == expected, 'INDEPENDENT_CONTROLLER_DRIFT '+path
    assert sha(base.PIN) == read(PIN)['original_main_source_pin_sha256'] == 'e1ac41adb2f8b1c3abf22dc77ce5e310a71926c97318b0d7f8854cd659dd9429'
    for method, expected in FIRST_SHA.items():
        out = base.V / 'main/recovery' / FIRST / method
        assert sha(out/'result.json') == expected
        r = read(out/'result.json')
        assert r['version'] == base.MAIN_VERSION and r['task_id'] == FIRST and r['method'] == method
        assert r['status'] == 'COMPLETED' and r['success'] is True and r['runtime_core']['complete'] is True
        assert r['final_snapshot']['diff'] and r['final_legal_edit_check']['legal'] is True
        assert r['final_legal_edit_check']['frozen_tests_unchanged'] is True
        assert r['public_acceptance_known'] is True and r['final_hidden_known'] is True
        assert r['public_native_calls'] > 0 and r['hidden_acceptance_calls'] == 1
        assert r['within_900_seconds'] is True and r['LLM_calls'] <= 64 and r['output_tokens'] <= 65536
        receipts = [read(p) for p in out.glob('llm/*_finance_receipt.json')]
        assert len(receipts) == r['new_paid_API'] and all(x['status']=='SETTLED' for x in receipts)
        assert sum((Decimal(x['usage_peak_cost_CNY']) for x in receipts),Decimal(0)) == Decimal(r['new_fees_CNY'])
    # Root closes only this lane's original Jobs before replacing its workers.
    for mode in ('main-agentless','main-ours'):
        old = read(base.V / ('supervision_'+mode+'_v2main.json'))
        assert old['status'] == 'STOPPED' and old['job_closed_all_owned_descendants_terminated'] is True

def build_authorizer():
    source = inspect.getsource(base.authorize_main)
    assert source.count(GATE) == 1, 'EXACT_SCHEDULING_GATE_ANCHOR_REQUIRED'
    original = ast.parse(source); changed = ast.parse(source.replace(GATE, '        additional_admission(grant)'))
    # Only one assertion body changes; all surrounding admission checks stay.
    original_if = [n for n in ast.walk(original) if isinstance(n,ast.If) and ast.unparse(n.test)=='through > 0']
    changed_if = [n for n in ast.walk(changed) if isinstance(n,ast.If) and ast.unparse(n.test)=='through > 0']
    assert len(original_if)==len(changed_if)==1
    original_if[0].body=changed_if[0].body
    assert ast.dump(original)==ast.dump(changed)
    scope = dict(base.__dict__); scope.update(GRANT=GRANT, additional_admission=additional_admission)
    exec(compile(changed,str(E/'main_environment_v2_224.py'),'exec'),scope)
    original_check = scope['authorize_main']
    def authorized():
        result = original_check()
        additional_admission(read(GRANT))  # Includes index0 and every delegated request.
        return result
    return authorized

def install():
    authorized = build_authorizer()
    base.authorize_main = authorized
    base.GRANT = GRANT
    return authorized

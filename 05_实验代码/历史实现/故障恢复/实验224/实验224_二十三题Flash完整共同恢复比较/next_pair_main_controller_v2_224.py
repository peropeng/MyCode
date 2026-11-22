"""Exact old external-censor acknowledgement; future fixed Main11/12 only."""
from common166 import *
import ast_safe_main_controller_v2_224 as parent
import scoped_main_controller_v2_224 as scoped
from dense_wall_guard_proposal224 import prepared_scope
V=parent.V;PIN=V/'next_pair_main_source_pin_v2.json';GRANT=V/'root_next_pair_main_grant_v2.json'
OLD_ACK=scoped.exact_next_ack

def external_ack(mode,index,result,grant=None):
    grant=read(GRANT) if grant is None else grant
    if mode!='main-agentless' or index!=10:return OLD_ACK(mode,index,result,grant)
    out=V/'main/recovery/getmoto__moto-5406/AGENTLESS_FSE2025_4L4P4T_FLASH'
    if result.get('error')!={'type':'ExternalCaseDeadline','message':'LOCAL_DENSE_ENCODING_INCOMPLETE_AT_ORIGINAL_900_SECOND_BOUNDARY'}:
        return OLD_ACK(mode,index,result,grant)
    ack=grant.get('external_case_deadline_next_ack',{})
    assert ack.get('root_explicit_next_only') is True and ack.get('continue_from_index')==11
    assert ack.get('original_result_sha256')==sha(out/'result.json')
    assert result['status']=='BUDGET_CENSORED' and result['success'] is None and result.get('finance_fatal') is False
    assert result['external_termination_provenance'] and result['public_native_calls']==result['hidden_acceptance_calls']==0
    assert scoped.settled_result(out,result) and result['new_paid_API']==2
    stop=V/'moto5406_external_deadline_stop_v2.json'
    assert ack.get('external_stop_receipt_sha256')==sha(stop)==result['external_stop_receipt_sha256']
    proof=read(stop);assert proof['status']=='STOPPED' and all(proof['process_handles_signaled'])
    assert ack.get('keep_original_null') is True and ack.get('no_resumption_or_reroll') is True
    return True

def build_authorizer():
    parent.GRANT=GRANT;scoped.exact_next_ack=external_ack
    old=parent.build_authorizer()
    def authorized():
        result=old();grant=read(GRANT)
        assert grant.get('next_fixed_main11_12_root_accepted') is True and 11<=int(grant['allowed_through_index'])<=12
        assert grant.get('next_pair_controller_pin_sha256')==sha(PIN)
        assert grant.get('dense_existing_clock_batch_guard_root_accepted') is True
        for p,h in {**read(PIN)['new_sources'],**read(PIN)['read_only_inputs']}.items():assert sha(p)==h
        return result
    return authorized

def install():
    authorized=build_authorizer();base=parent.parent.parent.parent.parent.base
    base.authorize_main=authorized;base.GRANT=GRANT
    parent.parent.install_transport_factory()
    official=sys.modules['agentless_bridge.official_core166']
    official.is_just_new_function=parent.safe_new_function(official.is_just_new_function)
    core=sys.modules['agentless178'];original=core.run
    def run(env):
        from agentless_bridge import dense166
        with prepared_scope(dense166,env):return original(env)
    core.run=run
    return authorized

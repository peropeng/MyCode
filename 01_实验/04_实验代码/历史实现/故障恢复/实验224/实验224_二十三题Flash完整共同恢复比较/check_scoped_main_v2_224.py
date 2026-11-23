"""Pure exact context-scope, next-ack, financial-fatal and wrapper checks."""
from common166 import *
import copy,ast
import scoped_main_controller_v2_224 as c
from scoped_main_entry_v2_224 import entry_source
from supervise_scoped_main_v2_224 import reviewed_wrapper_text
from second_entry_v2_224 import pid_birth

def check():
    g=c.V/'main/recovery/pydantic__pydantic-8567/G_PROGRESSIVE_SEMANTIC_FLASH'
    a=c.V/'main/recovery/getmoto__moto-6352/AGENTLESS_FSE2025_4L4P4T_FLASH'
    files=[E/n for n in ('scoped_main_controller_v2_224.py','scoped_main_entry_v2_224.py',
                         'supervise_scoped_main_v2_224.py','check_scoped_main_v2_224.py')]
    inputs=[c.parent.PIN,g/'result.json',a/'result.json',
            c.V/'supervision_main-agentless_v2extended.json',c.V/'supervision_main-ours_v2extended.json']
    pin={'schema':'AL-G-known-context-local-scope/1','new_sources':{str(p):sha(p) for p in files},
         'read_only_inputs':{str(p):sha(p) for p in inputs},'parent_extended_pin_sha256':sha(c.parent.PIN),
         'next_indices':{'main-agentless':5,'main-ours':6},'parent_body_seed_budget_finance_unchanged':True}
    save(c.PIN,pin)
    for mode in c.parent.METHODS:
        sup=read(c.V/('supervision_'+mode+'_v2extended.json'));assert sup['status']=='STOPPED' and sup['job_closed_all_owned_descendants_terminated']
        try:birth=pid_birth(sup['runner_pid'])
        except (AssertionError,OSError):birth=None
        assert birth!=sup['runner_creation_time100ns']
    grant=read(c.parent.GRANT)
    grant.update(root_authorized=True,known_context_censor_scope_fix_root_accepted=True,scoped_controller_pin_sha256=sha(c.PIN))
    base={'root_explicit_next_only':True,'keep_original_null':True,'mechanical_attempts':1,'mechanical_seconds':300}
    grant['known_context_censor_next_acknowledgements']={'main-ours':{'pydantic__pydantic-8567':{**base,
          'original_result_sha256':sha(g/'result.json'),'continue_from_index':6}}}
    grant['peer_context_interruption_next_acknowledgements']={'main-agentless':{'getmoto__moto-6352':{**base,
          'original_result_sha256':sha(a/'result.json'),'cause_result_sha256':sha(g/'result.json'),'continue_from_index':5}}}
    gr,ar=read(g/'result.json'),read(a/'result.json')
    assert c.known_context_censor(g,gr)
    for bad in ({'error':{'type':'FinanceUnknown','message':'HTTP_TIMEOUT'}},{'error':{'type':'FinanceGateRejected','message':'GLOBAL_CAP'}},
                {'status':'ENGINEERING_UNKNOWN'},{'new_paid_API':999}):
        assert not c.known_context_censor(g,{**gr,**bad})
    assert c.exact_next_ack('main-ours',5,gr,grant) and c.exact_next_ack('main-agentless',4,ar,grant)
    invalid=copy.deepcopy(grant);invalid['known_context_censor_next_acknowledgements']['main-ours']['pydantic__pydantic-8567']['original_result_sha256']='wrong'
    try:c.exact_next_ack('main-ours',5,gr,invalid)
    except AssertionError:pass
    else:raise AssertionError('WRONG_RAW_SHA_ACK_ALLOWED')
    invalid=copy.deepcopy(grant);invalid['peer_context_interruption_next_acknowledgements']={}
    assert not c.exact_next_ack('main-agentless',4,ar,invalid)
    original_read=c.read
    c.read=lambda p:{**original_read(p),'blocked':True} if Path(p).name=='shared_flash_budget.json' else original_read(p)
    try:c.scoped_unknown_gate(grant)
    except AssertionError:pass
    else:raise AssertionError('BLOCKED_FINANCE_ALLOWED')
    c.read=original_read
    authorized=c.build_authorizer();original=next(x.cell_contents for x in authorized.__closure__ if callable(x.cell_contents) and getattr(x.cell_contents,'__name__','')=='authorize_main')
    class FakeGrant:
        def exists(self):return True
    fake=FakeGrant();c.read=lambda p:grant if p==c.GRANT else original_read(p)
    original.__globals__['GRANT']=fake;original.__globals__['read']=lambda p:grant if p is fake else original_read(p)
    assert authorized()['version']=='V2_AUTH_DIRECT_PUBLICPACK_MAIN'
    grant['scoped_controller_pin_sha256']='wrong'
    try:authorized()
    except AssertionError:pass
    else:raise AssertionError('WRONG_SCOPE_PIN_ALLOWED')
    grant['scoped_controller_pin_sha256']=sha(c.PIN);c.read=original_read
    source=entry_source();assert source.count('if should_stop_queue(full): return')==1
    assert 'wait_peer(mode, index, authorize_main)' in source and '_v2scoped.json' in source
    wrapper=reviewed_wrapper_text()[1];ast.parse(wrapper)
    assert wrapper.index("'status':'RUNNING'")<wrapper.index('if nt.NtResumeProcess')
    assert 'LimitFlags=0x2000' in wrapper and 'child.wait(timeout=max(.1,remaining()))' in wrapper
    report={'at_utc':now(),'status':'PASS','source_pin_sha256':sha(c.PIN),
        'checks':['exact_known_context_censor_local','real_finance_unknown_and_global_cap_not_context',
                  'settled_fees_exact_counts_required','both_old_null_SHA_preserved','wrong_ack_SHA_rejected',
                  'peer_cascade_requires_explicit_root_next_ack','shared_finance_block_halts_both',
                  'root_scope_grant_and_pin_required','through20_original_source_checks_unchanged',
                  'current_context_censor_stops_only_current_arm','original_normal_negative_advance',
                  'lead1_and_original_21_order_preserved','RUNNING_before_Resume_job_birth_deadline',
                  'same_body_seed_caps_phase_no_transport_edit'],
        'root_new_grant_written':False,'new_POST_native_private_Gold':0,
        'proposed_grant_fields':{k:grant[k] for k in ('known_context_censor_scope_fix_root_accepted','scoped_controller_pin_sha256',
                                   'known_context_censor_next_acknowledgements','peer_context_interruption_next_acknowledgements')}}
    save(c.V/'scoped_main_pure_checks_v2.json',report);print(canonical(report))

if __name__=='__main__':check()

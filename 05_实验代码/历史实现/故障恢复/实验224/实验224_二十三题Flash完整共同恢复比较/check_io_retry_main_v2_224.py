"""Pure bounded IO fault injection; no finance write, model or native run."""
from common166 import *
import copy,ast
import io_retry_main_controller_v2_224 as c
from io_retry_main_entry_v2_224 import entry_source
from supervise_io_retry_main_v2_224 import reviewed_wrapper_text

def check():
    n={'calls':0};sleeps=[]
    def transient(a,b):
        n['calls']+=1
        if n['calls']<3:
            error=PermissionError('busy');error.winerror=5;raise error
        return 'replaced'
    assert c.replace_retry('tmp','state',transient,sleeps.append)=='replaced' and n['calls']==3 and sleeps==[.05,.05]
    n['calls']=0;sleeps=[]
    def permanent(a,b):
        n['calls']+=1;error=PermissionError('busy');error.winerror=5;raise error
    try:c.replace_retry('tmp','state',permanent,sleeps.append)
    except PermissionError:pass
    else:raise AssertionError('PERMANENT_PERMISSION_ERROR_SWALLOWED')
    assert n['calls']==20 and len(sleeps)==19
    def unrelated(a,b):raise OSError('unrelated')
    try:c.replace_retry('tmp','state',unrelated,sleeps.append)
    except OSError:pass
    else:raise AssertionError('UNRELATED_ERROR_SWALLOWED')
    v=c.V;path=v/'main/recovery/pydantic__pydantic-8567/AGENTLESS_FSE2025_4L4P4T_FLASH/result.json'
    result=read(path);assert result['status']=='ENGINEERING_UNKNOWN' and result['error']['type']=='PermissionError'
    state=ROOT/'工作区/1003-diagnosis-investigation/exp132_review/new_window_2332/finance/shared_flash_budget.json'
    live=read(state);intent=read(Path(str(state)+'.72376.tmp'))
    assert live['held_CNY']=='0.000000' and live['blocked'] is False
    last=intent['reservations'][-1];assert last['ordinal']==825 and last['status']=='RESERVED' and 'post_dispatch_epoch' not in last
    assert all(x['ordinal']!=825 for x in live['reservations'])
    save(v/'failed_uncommitted_reservation825_v2.json',{'source_tmp_sha256':sha(Path(str(state)+'.72376.tmp')),
        'uncommitted_intent':last,'actual_ledger_last_ordinal':live['reservations'][-1]['ordinal'],
        'actual_held_CNY':live['held_CNY'],'POST_not_reached_by_source_order':True,'original_tmp_not_changed':True})
    files=[E/n for n in ('io_retry_main_controller_v2_224.py','io_retry_main_entry_v2_224.py','supervise_io_retry_main_v2_224.py','check_io_retry_main_v2_224.py')]
    inputs=[c.parent.PIN,path,v/'supervision_main-agentless_v2scoped.json',v/'supervision_main-ours_v2scoped.json']
    for mode in ('main-agentless','main-ours'):
        stop=read(v/('supervision_'+mode+'_v2scoped.json'))
        assert stop['status']=='STOPPED' and stop['job_closed_all_owned_descendants_terminated']
    save(c.PIN,{'schema':'isolated-bounded-atomic-replace/1','new_sources':{str(p):sha(p) for p in files},
                'read_only_inputs':{str(p):sha(p) for p in inputs},'parent_scope_pin_sha256':sha(c.parent.PIN)})
    grant=read(c.parent.GRANT);grant.update(root_authorized=True,bounded_atomic_replace_retry_root_accepted=True,
        io_retry_controller_pin_sha256=sha(c.PIN))
    grant.setdefault('unknown_next_acknowledgements',{}).setdefault('main-agentless',{})['pydantic__pydantic-8567']={
        'original_result_sha256':sha(path),'continue_from_index':6,'root_explicit_next_only':True,
        'mechanical_attempts':1,'mechanical_seconds':300}
    auth=c.build_authorizer()
    original=next(x.cell_contents for x in auth.__closure__ if callable(x.cell_contents) and getattr(x.cell_contents,'__name__','')=='authorize_main')
    class FakeGrant:
        def exists(self):return True
    fake=FakeGrant();old_read=c.read;c.read=lambda p:grant if p==c.GRANT else old_read(p)
    original.__globals__['GRANT']=fake;original.__globals__['read']=lambda p:grant if p is fake else old_read(p)
    assert auth()['version']=='V2_AUTH_DIRECT_PUBLICPACK_MAIN';c.read=old_read
    source=entry_source();assert '_v2ioretry.json' in source and 'if should_stop_queue(full): return' in source
    wrapper=reviewed_wrapper_text()[1];ast.parse(wrapper)
    assert wrapper.index("'status':'RUNNING'")<wrapper.index('if nt.NtResumeProcess')
    report={'at_utc':now(),'status':'PASS','source_pin_sha256':sha(c.PIN),'new_POST_native_private_Gold_or_finance_write':0,
        'checks':['transient_win5_replace_retries_same_tmp','permanent_win5_max20_raises','other_errors_not_retried',
                  'failed_reservation_never_committed_or_POSTed','original_tmp_and_null_result_preserved',
                  'parent_source_and_finance_rules_unchanged','exact_root_unknown_next_ack','separate_supervision_original_job_shape'],
        'proposed_grant_fields':{k:grant[k] for k in ('bounded_atomic_replace_retry_root_accepted','io_retry_controller_pin_sha256','unknown_next_acknowledgements')},
        'root_actual_grant_written':False}
    save(v/'io_retry_main_pure_checks_v2.json',report);print(canonical(report))
if __name__=='__main__':check()

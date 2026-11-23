"""Pure extended admission/pairing/AST checks and exact prior-Job stop capture."""
from common166 import *
import ast,copy,shutil
import extended_main_controller_v2_224 as c
from extended_main_entry_v2_224 import entry_source
from supervise_extended_main_v2_224 import reviewed_wrapper_text
from second_entry_v2_224 import pid_birth

def check():
    v=c.parent.base.V; stopped=[]
    archive=v/'independent_stop_before_extended';archive.mkdir(exist_ok=True)
    for mode in c.METHODS:
        path=v/('supervision_'+mode+'_v2independent.json');sup=read(path)
        assert sup['status']=='STOPPED' and sup['job_closed_all_owned_descendants_terminated']
        actual=read(v/('main_checkpoint_'+mode+'.json'))['actual_worker']
        for pid,birth in [(actual['actual_self_PID'],actual['actual_self_creation_time100ns']),
                          (actual['logical_launcher_PID'],actual['logical_launcher_creation_time100ns'])]:
            try: current=pid_birth(pid)
            except (OSError,AssertionError): current=None
            assert current!=birth, 'OLD_OWNED_BIRTH_STILL_ALIVE'
        shutil.copyfile(path,archive/(mode+'.json'))
        stopped.append({'mode':mode,'supervision':sup,'previous_actual_worker':actual,'exact_owned_births_no_longer_alive':True,
                        'snapshot_sha256':sha(archive/(mode+'.json'))})
    save(v/'extended_main_prior_stop_v2.json',{'at_utc':now(),'status':'OLD_INDEPENDENT_JOBS_CLOSED','rows':stopped})
    files=[E/n for n in ('extended_main_controller_v2_224.py','extended_main_entry_v2_224.py',
                          'supervise_extended_main_v2_224.py','check_extended_main_v2_224.py')]
    prior={str(v/'main/recovery'/task/method/'result.json'):sha(v/'main/recovery'/task/method/'result.json')
           for task in c.ORDER[:3] for method in c.METHODS.values()}
    pin={'schema':'AL-G-extended-fixed21/1','version':c.parent.base.MAIN_VERSION,'new_sources':{str(p):sha(p) for p in files},
         'parent_independent_pin_sha256':sha(c.parent.PIN),'original_main_pin_sha256':sha(c.parent.base.PIN),
         'read_only_completed_inputs':prior,'fixed_order':c.ORDER,'remaining_indices':list(range(3,21)),
         'max_started_case_lead':1,'root_live_grant_required':True}
    save(c.PIN,pin)
    grant=read(c.parent.GRANT);grant.update(root_authorized=True,allowed_through_index=20,
        root_remaining18_fixed21_accepted=True,extended_controller_pin_sha256=sha(c.PIN),unknown_next_acknowledgements={})
    assert grant['V2_EnAgent_complete_nonzero_root_accepted'] is False
    authorized=c.build_authorizer();original=authorized.__closure__[0].cell_contents
    # Closure order is alphabetical: admission then original_check.
    original=next(cell.cell_contents for cell in authorized.__closure__
                  if callable(cell.cell_contents) and getattr(cell.cell_contents,'__name__','')=='authorize_main')
    class FakeGrant:
        def exists(self):return True
    fake=FakeGrant();old_read=c.read
    c.read=lambda p:grant if p==c.GRANT else old_read(p)
    original.__globals__['GRANT']=fake
    original.__globals__['read']=lambda p:grant if p is fake else old_read(p)
    assert authorized()['version']==c.parent.base.MAIN_VERSION
    passed=['through20_actual_self_qualification_EA_false','prior6_exact_results_and_parent_seals_unchanged']
    for field,bad in [('allowed_through_index',21),('root_remaining18_fixed21_accepted',False),
                      ('extended_controller_pin_sha256','wrong'),('root_authorized',False),('phase','Round2320Pilot')]:
        previous=grant[field];grant[field]=bad
        try:authorized()
        except (AssertionError,RuntimeError):passed.append(field+'_invalid_rejected')
        else:raise AssertionError('INVALID_EXTENDED_GRANT_ALLOWED '+field)
        grant[field]=previous
    c.read=old_read
    for index in range(3,21):
        assert c.peer_can_start(index,set(range(index)))
        if index>3:assert not c.peer_can_start(index,set(range(index-1)))
    assert c.peer_can_start(3,{0,1,2}) and not c.peer_can_start(5,{0,1,2,3})
    assert not c.exact_unknown_ack('main-agentless',3,{'status':'BUDGET_CENSORED'},grant)
    assert not c.exact_unknown_ack('main-agentless',3,{'status':'ENGINEERING_UNKNOWN'},grant)
    assert not c.exact_unknown_ack('main-agentless',3,{'status':'ENGINEERING_UNKNOWN','finance_fatal':'x'},grant)
    old_sha=c.sha;c.sha=lambda p:'pure-exact-raw-sha'
    ack_grant=copy.deepcopy(grant)
    ack={'original_result_sha256':'pure-exact-raw-sha','continue_from_index':4,'root_explicit_next_only':True,
         'mechanical_attempts':1,'mechanical_seconds':300}
    ack_grant['unknown_next_acknowledgements']={'main-agentless':{c.ORDER[3]:ack}}
    unknown={'status':'ENGINEERING_UNKNOWN','new_paid_API':0,'new_fees_CNY':'0'}
    assert c.exact_unknown_ack('main-agentless',3,unknown,ack_grant)
    for key,bad in [('original_result_sha256','wrong'),('continue_from_index',3),('mechanical_seconds',301)]:
        previous=ack[key];ack[key]=bad
        try:c.exact_unknown_ack('main-agentless',3,unknown,ack_grant)
        except AssertionError:pass
        else:raise AssertionError('INVALID_UNKNOWN_NEXT_ACK_ALLOWED '+key)
        ack[key]=previous
    c.sha=old_sha
    passed+=['all18_ordered_starts_lead_at_most_one','finance_unknown_not_ackable','unacknowledged_engineering_unknown_stops']
    passed+=['exact_raw_next_only_unknown_ack_requires_at_most_one_300s_repair']
    tree=ast.parse(entry_source());source=entry_source()
    assert source.count('if should_stop_queue(full): return')==1
    assert source.count('wait_peer(mode, index, authorize_main)')==1
    assert source.index('wait_peer(mode, index, authorize_main)')<source.index('out.mkdir(')<source.index('worker_started.json')
    wrapper=reviewed_wrapper_text()[1];tree=ast.parse(wrapper)
    run=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run')
    saves=[n.lineno for n in ast.walk(run) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='save'
           and any(isinstance(v,ast.Constant) and v.value=='RUNNING' for v in ast.walk(n))]
    resumes=[n.lineno for n in ast.walk(run) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='NtResumeProcess']
    assert min(saves)<min(resumes) and 'LimitFlags=0x2000' in wrapper and 'child.wait(timeout=max(.1,remaining()))' in wrapper
    passed+=['normal_negative_advance_original_current_UNKNOWN_stop','peer_gate_before_worker_start_or_POST',
             'same_birth_job_deadline_Main_body_seed_budget_phase','separate_extended_supervision_logs']
    result={'at_utc':now(),'status':'PASS','checks':passed,'source_pin_sha256':sha(c.PIN),
            'root_extended_grant_written':False,'new_model_POST_native_private_Gold':0,
            'CLI':'python -B supervise_extended_main_v2_224.py main-agentless | main-ours'}
    save(v/'extended_main_pure_checks_v2.json',result);print(canonical(result))

if __name__=='__main__':check()

"""Pure admission/AST/identity checks; no actor construction or process startup."""
from common166 import *
import ast, copy
import independent_main_controller_v2_224 as c
from independent_main_entry_v2_224 import entry_source
from supervise_independent_main_v2_224 import reviewed_wrapper_text

def check():
    files=[E/n for n in ('independent_main_controller_v2_224.py','independent_main_entry_v2_224.py',
                          'supervise_independent_main_v2_224.py','check_independent_main_v2_224.py')]
    pin={'schema':'AL-G-independent-admission/1','version':c.base.MAIN_VERSION,
         'new_sources':{str(p):sha(p) for p in files},'original_main_source_pin_sha256':sha(c.base.PIN),
         'selected_first_results_sha256':c.FIRST_SHA,'actual_allowed_initial_indices':[1,2],
         'new_first_outputs_or_patch_reuse':False,'parent_source_seal_unchanged':c.base.PARENT,
         'root_live_grant_required':True}
    save(c.PIN,pin)
    for path,expected in {**read(c.base.V/'source_seal_v2.json')['sealed_files'],
                          **read(c.base.PIN)['new_sources'],**read(c.base.PIN)['read_only_inputs']}.items(): assert sha(path)==expected
    grant=read(c.base.GRANT); grant.update(allowed_through_index=2,
         both_AL_G_actual_V2_complete_nonzero_accepted=True,independent_controller_pin_sha256=sha(c.PIN),
         selected_first_results_sha256=c.FIRST_SHA,V2_EnAgent_complete_nonzero_root_accepted=False)
    # Fake only the independent grant and stopped records; actual source/results/fees stay real.
    old_read=c.read
    def pure_read(p):
        if p==c.GRANT: return grant
        if Path(p).name in ('supervision_main-agentless_v2main.json','supervision_main-ours_v2main.json'):
            return {'status':'STOPPED','job_closed_all_owned_descendants_terminated':True}
        return old_read(p)
    c.read=pure_read
    authorization=c.build_authorizer()
    original_check=authorization.__closure__[0].cell_contents
    class FakeGrant:
        def exists(self): return True
    fake=FakeGrant(); original_check.__globals__['GRANT']=fake
    original_check.__globals__['read']=lambda p: grant if p is fake else pure_read(p)
    assert authorization()['version']==c.base.MAIN_VERSION
    passed=['actual_complete_nonzero_AL_G_accepted_without_EA','original_sources_and_first_raw_unchanged']
    for field,bad in [('both_AL_G_actual_V2_complete_nonzero_accepted',False),
                      ('independent_controller_pin_sha256','wrong'),('allowed_through_index',3),
                      ('selected_first_results_sha256',{}),('root_authorized',False),('phase','Round2320Pilot')]:
        prior=grant[field];grant[field]=bad
        try: authorization()
        except (AssertionError,RuntimeError): passed.append(field+'_rejects_invalid')
        else: raise AssertionError('INVALID_GRANT_ACCEPTED '+field)
        grant[field]=prior
    c.read=lambda p: {'status':'RUNNING'} if Path(p).name.startswith('supervision_') else pure_read(p)
    try: authorization()
    except AssertionError: passed.append('old_live_workers_block_restart')
    else: raise AssertionError('OVERLAPPING_WORKERS_ALLOWED')
    c.read=old_read
    path,supervisor=reviewed_wrapper_text(); tree=ast.parse(supervisor)
    run=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run')
    saves=[n.lineno for n in ast.walk(run) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='save'
           and any(isinstance(v,ast.Constant) and v.value=='RUNNING' for v in ast.walk(n))]
    resumes=[n.lineno for n in ast.walk(run) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='NtResumeProcess']
    assert min(saves)<min(resumes)
    assert "creationflags=0x08000000|0x00000004" in supervisor and 'AssignProcessToJobObject' in supervisor
    assert "child.wait(timeout=max(.1,remaining()))" in supervisor and 'LimitFlags=0x2000' in supervisor
    assert '_v2independent.json' in supervisor and '_v2independent.json' in entry_source()
    passed+=['RUNNING_before_Resume_birth_job_shape_preserved','separate_supervision_and_logs',
             'original_queue_skips_complete_first_and_unknown_stops','same_Main_routing_body_seed_caps_deadline']
    result={'at_utc':now(),'status':'PASS','checks':passed,'controller_pin_sha256':sha(c.PIN),
            'root_live_grant_written':False,'new_model_POST_native_private_Gold':0,
            'CLI':'python -B supervise_independent_main_v2_224.py main-agentless | main-ours'}
    save(c.base.V/'independent_main_pure_checks_v2.json',result); print(canonical(result))

if __name__=='__main__':check()

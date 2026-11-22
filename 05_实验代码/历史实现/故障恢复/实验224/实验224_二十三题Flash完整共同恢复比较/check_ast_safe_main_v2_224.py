"""Pure parser fallback check, without methods, native, POST or financial mutation."""
from common166 import *
import ast
import ast_safe_main_controller_v2_224 as c
from ast_safe_main_entry_v2_224 import entry_source
def check():
    calls=[]
    original=lambda old,new:calls.append((old,new)) or 'original-unchanged'
    safe=c.safe_new_function(original)
    assert safe('x=1','x=2')=='original-unchanged' and calls==[('x=1','x=2')]
    assert safe('for x in xs:\n','for x in xs:\n    pass\n') is False
    try:safe('for x in xs:\n','for x in xs:\n')
    except SyntaxError:pass
    else:raise AssertionError('INVALID_NEW_CODE_ACCEPTED')
    path=c.V/'main/recovery/python__mypy-10392/AGENTLESS_FSE2025_4L4P4T_FLASH/result.json'
    result=read(path);assert result['success'] is None and result['error']['type']=='IndentationError'
    files=[E/n for n in ('ast_safe_main_controller_v2_224.py','ast_safe_main_entry_v2_224.py','supervise_ast_safe_main_v2_224.py','check_ast_safe_main_v2_224.py')]
    inputs=[c.parent.PIN,path,c.V/'supervision_main-agentless_v2ioretry.json',c.V/'supervision_main-ours_v2ioretry.json']
    for mode in ('main-agentless','main-ours'):
        s=read(c.V/('supervision_'+mode+'_v2ioretry.json'))
        assert s['status']=='STOPPED' and s['job_closed_all_owned_descendants_terminated']
    save(c.PIN,{'schema':'official-normalization-invalid-old-AST-fallback/1','new_sources':{str(p):sha(p) for p in files},'read_only_inputs':{str(p):sha(p) for p in inputs}})
    grant=read(c.parent.GRANT);grant.update(invalid_old_C0_AST_fallback_root_accepted=True,ast_safe_controller_pin_sha256=sha(c.PIN))
    grant.setdefault('unknown_next_acknowledgements',{}).setdefault('main-agentless',{})['python__mypy-10392']={
        'original_result_sha256':sha(path),'continue_from_index':7,'root_explicit_next_only':True,'mechanical_attempts':1,'mechanical_seconds':300}
    auth=c.build_authorizer()
    io_auth=next(x.cell_contents for x in auth.__closure__ if callable(x.cell_contents))
    original=next(x.cell_contents for x in io_auth.__closure__ if callable(x.cell_contents) and getattr(x.cell_contents,'__name__','')=='authorize_main')
    class FakeGrant:
        def exists(self):return True
    fake=FakeGrant();real_read=c.read;c.read=lambda p:grant if p==c.GRANT else real_read(p)
    io_auth.__globals__['read']=lambda p:grant if p==c.GRANT else real_read(p)
    original.__globals__['GRANT']=fake;original.__globals__['read']=lambda p:grant if p is fake else real_read(p)
    assert auth()['version']=='V2_AUTH_DIRECT_PUBLICPACK_MAIN';c.read=real_read
    ast.parse(entry_source())
    report={'at_utc':now(),'status':'PASS','source_pin_sha256':sha(c.PIN),
            'checks':['valid_old_AST_original_helper_identical','invalid_old_valid_new_full_context_diff_retained',
                      'invalid_new_still_rejected','old_null_SHA_kept','old_jobs_closed','full_parent_admission_and_exact_root_ack_PASS',
                      'original_fixed_queue_body_seed_caps_unchanged'],
            'proposed_grant_fields':{k:grant[k] for k in ('invalid_old_C0_AST_fallback_root_accepted','ast_safe_controller_pin_sha256','unknown_next_acknowledgements')},
            'new_POST_native_private_Gold_finance_write':0,'root_new_grant_written':False}
    save(c.V/'ast_safe_main_pure_checks_v2.json',report);print(canonical(report))
if __name__=='__main__':check()

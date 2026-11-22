"""Syntax-broken old C0 retains official normalized text diff; new syntax remains checked."""
from common166 import *
import ast,inspect
import io_retry_main_controller_v2_224 as parent
V=parent.V;PIN=V/'ast_safe_main_source_pin_v2.json';GRANT=V/'root_ast_safe_main_grant_v2.json'

def safe_new_function(original):
    def checked(old,new):
        try:ast.parse(old)
        except SyntaxError:
            ast.parse(new)  # Invalid model code is never accepted by this fallback.
            return False  # Keep the official full-context normalized text diff.
        return original(old,new)
    return checked

def build_authorizer():
    scope=dict(parent.__dict__);scope['GRANT']=GRANT
    exec(compile(ast.parse(inspect.getsource(parent.build_authorizer)),str(E/'io_retry_main_controller_v2_224.py'),'exec'),scope)
    old=scope['build_authorizer']()
    def authorize():
        result=old();grant=read(GRANT)
        assert grant.get('invalid_old_C0_AST_fallback_root_accepted') is True
        assert grant.get('ast_safe_controller_pin_sha256')==sha(PIN)
        pin=read(PIN)
        for p,h in {**pin['new_sources'],**pin['read_only_inputs']}.items():assert sha(p)==h
        for mode in ('main-agentless','main-ours'):
            s=read(V/('supervision_'+mode+'_v2ioretry.json'))
            assert s['status']=='STOPPED' and s['job_closed_all_owned_descendants_terminated'] is True
        return result
    return authorize

def install():
    authorized=build_authorizer();base=parent.parent.parent.parent.base
    base.authorize_main=authorized;base.GRANT=GRANT
    parent.install_transport_factory()
    official=sys.modules['agentless_bridge.official_core166']
    official.is_just_new_function=safe_new_function(official.is_just_new_function)
    return authorized

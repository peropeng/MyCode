"""Isolated bounded atomic replace retry; no HTTP retry or finance rule change."""
from common166 import *
import ast,inspect
import scoped_main_controller_v2_224 as parent

V=parent.V;PIN=V/'io_retry_main_source_pin_v2.json';GRANT=V/'root_io_retry_main_grant_v2.json'
def replace_retry(source,target,replace=os.replace,sleep=time.sleep):
    for attempt in range(20):
        try:return replace(source,target)
        except PermissionError as error:
            if getattr(error,'winerror',None)!=5 or attempt==19:raise
            sleep(.05)

def patched_atomic(module):
    source=inspect.getsource(module.atomic);anchor='os.replace(tmp,path)'
    assert source.count(anchor)==1
    scope=dict(module.__dict__);scope['replace_retry']=replace_retry
    exec(compile(ast.parse(source.replace(anchor,'replace_retry(tmp,path)')),str(module.__file__),'exec'),scope)
    return scope['atomic']

def install_transport_factory():
    base=parent.parent.parent.base;original=base._original_module
    def loader(name,path):
        m=original(name,path)
        if Path(path).resolve()==Path(TRANSPORT).resolve() and not getattr(m,'atomic_replace_retry_installed',False):
            old_init=m.LegacyIO.__init__
            def init(io):
                old_init(io);io.m.atomic=patched_atomic(io.m)
            m.LegacyIO.__init__=init;m.atomic_replace_retry_installed=True
        return m
    base._original_module=loader

def build_authorizer():
    old=parent.build_authorizer()
    original=next(x.cell_contents for x in old.__closure__ if callable(x.cell_contents) and getattr(x.cell_contents,'__name__','')=='authorize_main')
    admission=next(x.cell_contents for x in old.__closure__ if callable(x.cell_contents) and getattr(x.cell_contents,'__name__','')=='admission')
    original.__globals__['GRANT']=GRANT
    def authorize():
        result=original();grant=read(GRANT);admission(grant)
        assert grant.get('bounded_atomic_replace_retry_root_accepted') is True
        assert grant.get('io_retry_controller_pin_sha256')==sha(PIN)
        pin=read(PIN)
        for p,h in {**pin['new_sources'],**pin['read_only_inputs']}.items():assert sha(p)==h
        for mode in parent.parent.METHODS:
            stop=read(V/('supervision_'+mode+'_v2scoped.json'))
            assert stop['status']=='STOPPED' and stop['job_closed_all_owned_descendants_terminated'] is True
        return result
    return authorize

def install():
    authorized=build_authorizer();base=parent.parent.parent.base
    base.authorize_main=authorized;base.GRANT=GRANT
    install_transport_factory()
    return authorized

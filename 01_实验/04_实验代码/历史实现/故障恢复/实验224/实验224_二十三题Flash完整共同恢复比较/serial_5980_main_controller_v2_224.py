"""Only fixed next Main5980: exact prior-null ack and full request serialization."""
from common166 import *
import ast,inspect,msvcrt,errno
from decimal import Decimal
import next_pair_main_controller_v2_224 as parent
from audit_next_pair_budget_censor_v2_224 import shared_json
V=parent.V;PIN=V/'serial_5980_main_source_pin_v2.json';GRANT=V/'root_serial_5980_main_grant_v2.json'
OLD_ACK=parent.OLD_ACK

def known_prepost_cap(out,result):
    n=result.get('LLM_calls',0)
    return (result.get('status')=='BUDGET_CENSORED' and result.get('success') is None and
            result.get('error')=={'type':'FinanceGateRejected','message':'GLOBAL_OR_PHASE_CAP'} and
            (result.get('finance_fatal') or {}).get('message')=='GLOBAL_OR_PHASE_CAP' and
            parent.scoped.settled_result(out,result) and (out/'llm'/('%03d_request.json'%n)).exists() and
            not (out/'llm'/('%03d_http_response.json'%n)).exists() and not (out/'llm'/('%03d_finance_receipt.json'%n)).exists())

def exact_ack(mode,index,result,grant=None):
    grant=read(GRANT) if grant is None else grant
    if index!=11:return parent.external_ack(mode,index,result,grant)
    out=V/'main/recovery/getmoto__moto-6387'/parent.scoped.parent.METHODS[mode]
    ack=grant.get('known_prepost6387_next_only_ack',{})
    assert ack.get('root_explicit_next_only') is True and ack.get('continue_from_index')==12
    assert ack.get('keep_both_original_null') is True and ack.get('no_replay_or_reroll') is True
    assert ack['results_sha256'][mode]==sha(out/'result.json') and result['success'] is None
    cause=V/'main/recovery/getmoto__moto-6387/G_PROGRESSIVE_SEMANTIC_FLASH/result.json';g=read(cause)
    assert known_prepost_cap(cause.parent,g) and g['new_paid_API']==0 and g['new_fees_CNY']=='0'
    if mode=='main-ours':return True
    assert result['status']=='ENGINEERING_UNKNOWN' and result.get('finance_fatal') is None
    assert result['error']=={'type':'RuntimeError','message':'REAL_UNKNOWN_REQUIRES_EXACT_ROOT_NEXT_ACK main-ours getmoto__moto-6387'}
    assert parent.scoped.settled_result(out,result) and result['new_paid_API']==1
    return True

def current_cap_arm_local(grant):
    ledger=shared_json(ROOT/'工作区/1003-diagnosis-investigation/exp132_review/new_window_2332/finance/shared_flash_budget.json')
    assert ledger.get('blocked') is False,'SHARED_FINANCIAL_UNKNOWN_BLOCKS_BOTH'
    for mode,method in parent.scoped.parent.METHODS.items():
        for index,task in enumerate(parent.scoped.parent.ORDER):
            path=V/'main/recovery'/task/method/'result.json'
            if not path.exists():continue
            r=read(path)
            if not parent.scoped.should_stop_queue(r):continue
            if parent.scoped.known_context_censor(path.parent,r):continue
            if index==12 and task=='getmoto__moto-5980' and known_prepost_cap(path.parent,r):continue
            if exact_ack(mode,index,r,grant):continue
            raise RuntimeError('REAL_UNKNOWN_REQUIRES_EXACT_ROOT_NEXT_ACK '+mode+' '+task)

def build_authorizer():
    scope=dict(parent.__dict__);scope.update(GRANT=GRANT,external_ack=exact_ack)
    exec(compile(ast.parse(inspect.getsource(parent.build_authorizer)),str(E/'next_pair_main_controller_v2_224.py'),'exec'),scope)
    parent.scoped.scoped_unknown_gate=current_cap_arm_local
    old=scope['build_authorizer']()
    def authorize():
        r=old();g=read(GRANT)
        assert int(g['allowed_through_index'])==12 and g.get('fixed_5980_serial_requests_root_accepted') is True
        assert g.get('serial_5980_controller_pin_sha256')==sha(PIN)
        for p,h in {**read(PIN)['new_sources'],**read(PIN)['read_only_inputs']}.items():assert sha(p)==h
        return r
    return authorize

def serial_factory(base):
    original=base._original_module
    def loader(name,path):
        m=original(name,path)
        if Path(path).resolve()!=Path(TRANSPORT).resolve():return m
        delegate=m.generate
        def generate(env,body,role,phase='Round2320Pilot'):
            assert env.task_id=='getmoto__moto-5980' and phase=='Round2320Main'
            started=time.monotonic();lockpath=V/'5980_model_request_serial.lock'
            with lockpath.open('a+b') as handle:
                handle.seek(0,2)
                if handle.tell()==0:handle.write(b'\0');handle.flush()
                acquired=False
                try:
                    while not acquired:
                        env._require();handle.seek(0)
                        try:msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1);acquired=True
                        except OSError as error:
                            if error.errno not in (errno.EACCES,errno.EAGAIN,errno.EDEADLK):raise
                            time.sleep(.05)
                    io=m.LegacyIO()
                    while True:
                        env._require()
                        with io.lock(time.monotonic()+env.time_left()):s=shared_json(io.m.STATE)
                        assert s.get('blocked') is False,'SHARED_FINANCIAL_UNKNOWN_BLOCKS_BOTH'
                        pending=[r for r in s['reservations'] if r['status']=='RESERVED' or str(r['status']).startswith('UNKNOWN')]
                        if any(str(r['status']).startswith('UNKNOWN') or time.time()>r.get('lease_expires_epoch',float('inf')) or not m.alive(r) for r in pending):
                            raise m.Unknown('UNPRICED_OR_EXPIRED_HOLD_DURING_SERIAL_WAIT')
                        if Decimal(s['held_CNY'])==0:break
                        time.sleep(.05)
                    append(V/'5980_serial_model_request_events.jsonl',{'at_utc':now(),'role':role,'PID':os.getpid(),'lock_wait_seconds':time.monotonic()-started,'original_body_sha256':m.digest(body),'held_before_delegate':'0','delegate_called_once':True})
                    return delegate(env,body,role,phase=phase)
                finally:
                    if acquired:handle.seek(0);msvcrt.locking(handle.fileno(),msvcrt.LK_UNLCK,1)
        m.generate=generate;return m
    base._original_module=loader

def install():
    authorized=build_authorizer();base=parent.parent.parent.parent.parent.parent.base
    base.authorize_main=authorized;base.GRANT=GRANT
    parent.parent.parent.install_transport_factory()
    official=sys.modules['agentless_bridge.official_core166'];official.is_just_new_function=parent.parent.safe_new_function(official.is_just_new_function)
    core=sys.modules['agentless178'];old=core.run
    def run(env):
        from agentless_bridge import dense166
        with parent.prepared_scope(dense166,env):return old(env)
    core.run=run;serial_factory(base);return authorized

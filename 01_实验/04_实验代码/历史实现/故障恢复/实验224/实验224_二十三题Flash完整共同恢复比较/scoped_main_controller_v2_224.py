"""Known pre-POST context censor is arm-local; real unknown remains global."""
from common166 import *
import inspect,ast
from decimal import Decimal
import extended_main_controller_v2_224 as parent
from budget_semantics224 import should_stop_queue

V=parent.parent.base.V
PIN=V/'scoped_main_source_pin_v2.json'
GRANT=V/'root_scoped_main_grant_v2.json'
TAIL='    # Both arms stop for any unacknowledged engineering or financial unknown.\n'

def settled_result(out,result):
    receipts=[read(p) for p in out.glob('llm/*_finance_receipt.json')]
    return (all(x.get('status')=='SETTLED' for x in receipts) and len(receipts)==result.get('new_paid_API') and
            sum((Decimal(x['usage_peak_cost_CNY']) for x in receipts),Decimal(0))==Decimal(result.get('new_fees_CNY','-1')))

def known_context_censor(out,result):
    return (result.get('status')=='BUDGET_CENSORED' and result.get('success') is None and
            result.get('error')=={'type':'FinanceGateRejected','message':'CONTEXT_BOUND'} and
            (result.get('finance_fatal') or {}).get('type')=='FinanceGateRejected' and
            (result.get('finance_fatal') or {}).get('message')=='CONTEXT_BOUND' and
            result.get('hidden_acceptance_calls')==0 and settled_result(out,result))

def exact_next_ack(mode,index,result,grant=None):
    grant=read(GRANT) if grant is None else grant
    out=V/'main/recovery'/parent.ORDER[index]/parent.METHODS[mode]
    if known_context_censor(out,result):
        ack=grant.get('known_context_censor_next_acknowledgements',{}).get(mode,{}).get(parent.ORDER[index],{})
        if not ack:return False
    elif (result.get('status')=='ENGINEERING_UNKNOWN' and result.get('finance_fatal') is None and
          result.get('error')=={'type':'RuntimeError','message':'PEER_OR_SELF_UNKNOWN_REQUIRES_EXACT_ROOT_NEXT_ACK main-ours pydantic__pydantic-8567'}):
        ack=grant.get('peer_context_interruption_next_acknowledgements',{}).get(mode,{}).get(parent.ORDER[index],{})
        if not ack:return False
        cause=V/'main/recovery/pydantic__pydantic-8567/G_PROGRESSIVE_SEMANTIC_FLASH/result.json'
        assert ack.get('cause_result_sha256')==sha(cause)
        assert known_context_censor(cause.parent,read(cause)) and settled_result(out,result)
    else:return parent.exact_unknown_ack(mode,index,result,grant)
    assert ack.get('original_result_sha256')==sha(out/'result.json')
    assert ack.get('continue_from_index')==index+1 and ack.get('root_explicit_next_only') is True
    assert ack.get('keep_original_null') is True and result.get('success') is None
    assert 0<=ack.get('mechanical_attempts',99)<=1 and 0<=ack.get('mechanical_seconds',999)<=300
    return True

def scoped_unknown_gate(grant):
    ledger=read(ROOT/'工作区/1003-diagnosis-investigation/exp132_review/new_window_2332/finance/shared_flash_budget.json')
    assert ledger.get('blocked') is False, 'SHARED_FINANCIAL_UNKNOWN_BLOCKS_BOTH'
    for mode,method in parent.METHODS.items():
        for index,task in enumerate(parent.ORDER):
            path=V/'main/recovery'/task/method/'result.json'
            if not path.exists():continue
            result=read(path)
            if should_stop_queue(result):
                if known_context_censor(path.parent,result):continue  # Current healthy peer transaction is unaffected.
                if exact_next_ack(mode,index,result,grant):continue
                raise RuntimeError('REAL_UNKNOWN_REQUIRES_EXACT_ROOT_NEXT_ACK '+mode+' '+task)

def prefix_admission():
    source=inspect.getsource(parent.extended_admission)
    assert source.count(TAIL)==1
    prefix=source.split(TAIL)[0]+'    scoped_unknown_gate(grant)\n'
    scope=dict(parent.__dict__);scope['scoped_unknown_gate']=scoped_unknown_gate
    exec(compile(ast.parse(prefix),str(E/'extended_main_controller_v2_224.py'),'exec'),scope)
    return scope['extended_admission']

def build_authorizer():
    old=parent.build_authorizer()
    original=next(cell.cell_contents for cell in old.__closure__ if callable(cell.cell_contents) and
                  getattr(cell.cell_contents,'__name__','')=='authorize_main')
    previous=original.__globals__['additional_admission']
    delegate=previous.__closure__[0].cell_contents
    prefix=prefix_admission()
    def admission(grant):
        prefix(grant,delegate)
        assert grant.get('known_context_censor_scope_fix_root_accepted') is True
        assert grant.get('scoped_controller_pin_sha256')==sha(PIN)
        pin=read(PIN)
        for path,expected in {**pin['new_sources'],**pin['read_only_inputs']}.items():assert sha(path)==expected
        assert sha(parent.PIN)==pin['parent_extended_pin_sha256']=='bf8ee25be343397e5cd3c1a33cd123a13d0e9ff7645e5416706e3b465c6e851d'
        for mode in parent.METHODS:
            stopped=read(V/('supervision_'+mode+'_v2extended.json'))
            assert stopped['status']=='STOPPED' and stopped['job_closed_all_owned_descendants_terminated'] is True
    original.__globals__.update(GRANT=GRANT,additional_admission=admission)
    def authorize():
        result=original();admission(read(GRANT));return result
    return authorize

def wait_peer(mode,index,authorize):return parent.wait_peer(mode,index,authorize)

def install():
    authorized=build_authorizer()
    parent.parent.base.authorize_main=authorized;parent.parent.base.GRANT=GRANT
    return authorized

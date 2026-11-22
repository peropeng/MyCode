"""Add-only through20 and paired scheduling; no algorithm or model-body edits."""
from common166 import *
import ast, inspect
from decimal import Decimal
import independent_main_controller_v2_224 as parent
from budget_semantics224 import should_stop_queue

PIN=parent.base.V/'extended_main_source_pin_v2.json'
GRANT=parent.base.V/'root_extended_main_grant_v2.json'
ORDER=read(parent.base.PIN)['task_order']
METHODS={'main-agentless':'AGENTLESS_FSE2025_4L4P4T_FLASH','main-ours':'G_PROGRESSIVE_SEMANTIC_FLASH'}
CURRENT={'mode':None,'index':None}
LIMIT="    assert 0 <= int(grant['allowed_through_index']) <= 2, 'INDEPENDENT_INITIAL_THROUGH2_ONLY'"

def exact_unknown_ack(mode,index,result,grant=None):
    grant=read(GRANT) if grant is None else grant
    if result.get('status')!='ENGINEERING_UNKNOWN' or result.get('finance_fatal'): return False
    if (result.get('error') or {}).get('type','').startswith('Finance'): return False
    out=parent.base.V/'main/recovery'/ORDER[index]/METHODS[mode]
    ack=grant.get('unknown_next_acknowledgements',{}).get(mode,{}).get(ORDER[index],{})
    if not ack: return False
    assert ack.get('original_result_sha256')==sha(out/'result.json')
    assert ack.get('continue_from_index')==index+1 and ack.get('root_explicit_next_only') is True
    assert 0<=ack.get('mechanical_attempts',99)<=1 and 0<=ack.get('mechanical_seconds',999)<=300
    receipts=[read(p) for p in out.glob('llm/*_finance_receipt.json')]
    assert all(x['status']=='SETTLED' for x in receipts), 'UNKNOWN_FINANCIAL_RECEIPTS_CANNOT_ACK'
    assert len(receipts)==result.get('new_paid_API')
    assert sum((Decimal(x['usage_peak_cost_CNY']) for x in receipts),Decimal(0))==Decimal(result.get('new_fees_CNY','-1'))
    return True

def peer_can_start(index,peer_started_indices):
    return index<=3 or index-1 in peer_started_indices

def extended_admission(grant,limit_delegate):
    limit_delegate(grant)
    assert grant.get('root_remaining18_fixed21_accepted') is True
    assert grant.get('extended_controller_pin_sha256')==sha(PIN)
    assert sha(parent.PIN)==read(PIN)['parent_independent_pin_sha256']=='42892e14e9d9d1a4563e0777dbdf6c370efa8ca6a095291a20de1016070849c1'
    for path,expected in {**read(PIN)['new_sources'],**read(PIN)['read_only_completed_inputs']}.items():
        assert sha(path)==expected, 'EXTENDED_SOURCE_OR_PRIOR_RESULT_DRIFT '+path
    for mode in METHODS:
        stop=read(parent.base.V/('supervision_'+mode+'_v2independent.json'))
        assert stop['status']=='STOPPED' and stop['job_closed_all_owned_descendants_terminated'] is True
    # Both arms stop for any unacknowledged engineering or financial unknown.
    for mode,method in METHODS.items():
        for index,task in enumerate(ORDER):
            path=parent.base.V/'main/recovery'/task/method/'result.json'
            if path.exists():
                result=read(path)
                if should_stop_queue(result) and not exact_unknown_ack(mode,index,result,grant):
                    raise RuntimeError('PEER_OR_SELF_UNKNOWN_REQUIRES_EXACT_ROOT_NEXT_ACK '+mode+' '+task)

def build_authorizer():
    source=inspect.getsource(parent.additional_admission)
    assert source.count(LIMIT)==1
    changed=source.replace(LIMIT,"    assert 0 <= int(grant['allowed_through_index']) <= 20, 'EXTENDED_FIXED21_THROUGH20_ONLY'")
    scope=dict(parent.__dict__)
    exec(compile(ast.parse(changed),str(E/'independent_main_controller_v2_224.py'),'exec'),scope)
    delegate=scope['additional_admission']
    previous_admission,previous_grant=parent.additional_admission,parent.GRANT
    try:
        parent.additional_admission=lambda grant:extended_admission(grant,delegate)
        parent.GRANT=GRANT
        authorized=parent.build_authorizer()
    finally:
        parent.additional_admission,parent.GRANT=previous_admission,previous_grant
    # Authorizer's additional admission function is captured in its cloned globals;
    # the unconditional index0 check in the parent wrapper receives the new one too.
    original_check=authorized.__closure__[0].cell_contents
    admission=original_check.__globals__['additional_admission']
    def authorize():
        result=original_check()
        admission(read(GRANT))
        return result
    return authorize

def wait_peer(mode,index,authorize):
    CURRENT.update(mode=mode,index=index)
    peer=next(x for x in METHODS if x!=mode)
    while True:
        authorize()
        starts={n for n,task in enumerate(ORDER) if (parent.base.V/'main/recovery'/task/METHODS[peer]/'worker_started.json').exists()}
        if peer_can_start(index,starts): return
        save(parent.base.V/('extended_checkpoint_'+mode+'.json'),
             {'at_utc':now(),'phase':'WAIT_PEER_MAX_LEAD_ONE','task_index':index,'task_id':ORDER[index],
              'peer_mode':peer,'no_POST_native_in_boundary_wait':True})
        if time.time()>=NO_TEST: raise RuntimeError('EXTENDED_PEER_WAIT_GLOBAL_CUTOFF')
        time.sleep(1)

def install():
    authorized=build_authorizer()
    parent.base.authorize_main=authorized;parent.base.GRANT=GRANT
    return authorized

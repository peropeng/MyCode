"""Apply the explicit phase-only budget amendment after the original guard stop.

The immutable v1 runner, protocol, parsers and API guards are reused unchanged.
No import, validation or --check operation sends metadata or generation requests.
"""
from decimal import Decimal
import copy
import os
import sys
from shared import *
import run_paid

OLD_SHA='1180005ac1e9c2d6795dd98e28ce4a8e1886ea27061afd076810f004d584833c'
NEW_SHA='631db0c63332f09f54cd092bedbbf3a21da3ca56d18abdca9c653e3b6b23a093'
AMENDMENT_SHA='e1c1d1ddcfd17827109eea8e803c2abe5e4940a4a73f91c0cf00e76bd1d7b7c3'
V1=T/'authorization_v1.json'
V2=T/'authorization_v2_0320.json'
AMENDMENT=T/'budget_amendment_0320.json'
NATIVE_CLIENT=run_paid.SameEpochContinuationClient

def verify_amendment():
    p=verify()
    if Path(p['authorization_file']).resolve()!=V1.resolve():raise RuntimeError('original_authorization_binding_changed')
    if sha(V1)!=OLD_SHA or sha(V2)!=NEW_SHA or sha(AMENDMENT)!=AMENDMENT_SHA:raise RuntimeError('budget_amendment_source_changed')
    old=read(V1);new=read(V2);decision=read(AMENDMENT)
    expected=copy.deepcopy(old)
    expected['existing_account_funding_amendment']['fixed_bucket_caps_CNY']['EXP134_CONFIRMATION']='3.20'
    expected['exp134_confirmation_budget']['cap_CNY']='3.20'
    revision=new['exp134_phase_bucket_amendment_0320']
    expected['exp134_phase_bucket_amendment_0320']=revision
    if expected!=new:raise RuntimeError('amendment_changes_more_than_two_caps_and_receipt')
    if revision['source_sha256']!=AMENDMENT_SHA or revision['prior_authorization_sha256']!=OLD_SHA:raise RuntimeError('amendment_chain_binding_changed')
    if decision['new_phase_cap_CNY']!='3.20' or decision['old_phase_cap_CNY']!='2.25' or decision['scientific_changes'] is not False:raise RuntimeError('phase_only_decision_required')
    if new['exp134_confirmation_budget']['anchor_epoch_usage_CNY']!='14.12824334':raise RuntimeError('stage_cost_anchor_changed')
    if new['existing_account_funding_amendment']['new_additional_spending_hardcap_CNY']!='14.16':raise RuntimeError('global_cost_cap_changed')
    if Decimal(new['balance_floor_cny'])+Decimal(new['balance_safety_margin_cny'])!=Decimal('1.02'):raise RuntimeError('real_account_floor_changed')
    return p

def require_original_guard_stop():
    state=read(E/'execution_state.json')
    if state['phase']!='EXP134_CONFIRMATION_BUDGET_OR_TECHNICAL_STOP' or state.get('current_pid') is not None:raise RuntimeError('live_runner_must_not_be_interrupted')
    if 'resource_budget_abstention:EXP134_CONFIRMATION:' not in (state.get('recent_error') or ''):raise RuntimeError('only_original_phase_bucket_stop_qualified')
    if state.get('unsettled_requests')!=0:raise RuntimeError('unknown_charge_blocks_amended_resume')
    if (API/'producer.lock').exists() or (API/'budget.lock').exists():raise RuntimeError('existing_request_or_producer_owner_blocks_resume')
    if (T/'prediction_seal.json').exists():raise RuntimeError('complete_scope_must_not_run_again')

class AmendedClient(NATIVE_CLIENT):
    def __init__(self,authorization_file,output,**kwargs):
        verify_amendment()
        require_original_guard_stop()
        if Path(authorization_file).resolve()!=V1.resolve() or Path(output).resolve()!=API.resolve():raise RuntimeError('runner_binding_changed')
        super().__init__(V2,output,**kwargs)
        if self.unresolved_upper()!=0 or self.halt.exists():raise RuntimeError('unknown_or_halted_request_cannot_resume')
        lock=API/'budget.lock'
        fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as f:
                json.dump({'pid':os.getpid(),'at_utc':now(),'purpose':'Exp134-phase-budget-amendment'},f)
                f.flush();os.fsync(f.fileno())
            self.calls=lines(self.ledger)
            if self.unresolved_upper()!=0:raise RuntimeError('unknown_request_during_amendment')
            old_rows=[r for r in self.calls if r.get('event')=='exp134_confirmation_budget_amendment_0320']
            if old_rows and any(r.get('new_authorization_sha256')!=NEW_SHA or r.get('amendment_sha256')!=AMENDMENT_SHA for r in old_rows):raise RuntimeError('amendment_ledger_binding_changed')
            if not old_rows:
                self._append({'event':'exp134_confirmation_budget_amendment_0320','timestamp':now(),
                    'old_authorization_sha256':OLD_SHA,'new_authorization_sha256':NEW_SHA,'amendment_sha256':AMENDMENT_SHA,
                    'original_protocol_sha256':sha(T/'protocol.json'),'resume_adapter_sha256':sha(Path(__file__)),
                    'original_stage_anchor_CNY':'14.12824334','old_cap_CNY':'2.25','new_cap_CNY':'3.20',
                    'global_additional_hardcap_CNY':'14.16','account_floor_plus_margin_CNY':'1.02',
                    'ledger_prefix_sha256_before_amendment':sha(self.ledger),'spending_at_application_CNY':str(self.spent_upper()),
                    'scientific_changes':False,'new_epoch':False,'historical_charge_refund':False,'paid_slots_resampled':False})
        finally:lock.unlink()
        atomic(T/'budget_amendment_application.json',{'at_utc':now(),'applied':True,'authorization_sha256':NEW_SHA,
            'amendment_sha256':AMENDMENT_SHA,'protocol_sha256_unchanged':sha(T/'protocol.json'),
            'resume_adapter_sha256':sha(Path(__file__)),'whole_scope_before_scoring_required':True})

def check():
    verify_amendment()
    client=NATIVE_CLIENT.__new__(NATIVE_CLIENT)
    client.config=read(V2)
    # Exercise the inherited branch/global guard at both authorization boundaries.
    anchor=Decimal('14.12824334')
    client.spent_upper=lambda:anchor+Decimal('3.19')
    near=client._amended_budget_remaining(Decimal('6.87'))
    client.spent_upper=lambda:anchor+Decimal('3.20')
    cap=client._amended_budget_remaining(Decimal('6.87'))
    client.spent_upper=lambda:Decimal('3.36788720')+Decimal('14.16')
    global_cap=client._whole_pool_budget_remaining(Decimal('6.87'))
    if near!=Decimal('1.03') or cap!=Decimal('1.02') or global_cap!=Decimal('1.02'):raise RuntimeError('inherited_budget_boundary_check_failed')
    receipt={'at_utc':now(),'original_frozen_files_verified':True,'authorization_changes':'two phase cap fields plus explicit receipt only',
        'old_authorization_sha256':OLD_SHA,'new_authorization_sha256':NEW_SHA,'amendment_sha256':AMENDMENT_SHA,
        'adapter_sha256':sha(Path(__file__)),'near_stage_cap_remaining_including_floor_CNY':str(near),
        'at_stage_cap_remaining_including_floor_CNY':str(cap),'at_global_cap_remaining_including_floor_CNY':str(global_cap),
        'metadata_requests':0,'generation_requests':0,'fresh_Gold_accesses':0,'active_runner_unchanged':True}
    write(T/'budget_amendment_check.json',receipt)
    print(canonical(receipt),flush=True)

if __name__=='__main__':
    if sys.argv[1:]==['--check']:check()
    elif not sys.argv[1:]:
        run_paid.SameEpochContinuationClient=AmendedClient
        run_paid.main()
    else:raise ValueError('only_optional_check_argument_supported')

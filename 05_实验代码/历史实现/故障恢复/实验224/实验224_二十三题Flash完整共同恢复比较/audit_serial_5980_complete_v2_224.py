"""Read-only evidence: serialization, exact paid calls, null and full success."""
from common166 import *
import ctypes
from ctypes import wintypes as w
from decimal import Decimal
from publicpack_v2_224 import V
from audit_next_pair_budget_censor_v2_224 import shared_json
from second_entry_v2_224 import pid_birth
def original_dead(pid,expected):
    k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];k.OpenProcess.restype=w.HANDLE
    k.WaitForSingleObject.argtypes=[w.HANDLE,w.DWORD];k.CloseHandle.argtypes=[w.HANDLE]
    h=k.OpenProcess(0x1000|0x100000,False,pid)
    if not h:
        assert ctypes.get_last_error()==87
        return True
    try:return pid_birth(pid)!=expected or k.WaitForSingleObject(h,0)==0
    finally:k.CloseHandle(h)
def main():
    rows=[]
    for mode,method in (('main-agentless','AGENTLESS_FSE2025_4L4P4T_FLASH'),('main-ours','G_PROGRESSIVE_SEMANTIC_FLASH')):
        out=V/'main/recovery/getmoto__moto-5980'/method;r=read(out/'result.json');receipts=[read(p) for p in out.glob('llm/*_finance_receipt.json')]
        assert all(x['status']=='SETTLED' for x in receipts) and len(receipts)==r['new_paid_API']==1
        assert sum((Decimal(x['usage_peak_cost_CNY']) for x in receipts),Decimal(0))==Decimal(r['new_fees_CNY'])
        s=read(V/('supervision_'+mode+'_v2serial5980.json'));worker=read(out/'worker_started.json')['actual_worker']
        assert s['status']=='STOPPED' and s['job_closed_all_owned_descendants_terminated']
        assert original_dead(worker['actual_self_PID'],worker['actual_self_creation_time100ns']) and original_dead(s['runner_pid'],s['runner_creation_time100ns'])
        native=[read(p) for p in out.rglob('*.process.json')]
        assert all(x['root_PID_birth_verified'] and x['stop_receipt']['all_owned_descendants_terminated'] for x in native)
        if mode=='main-ours':assert r['success'] is True and r['runtime_core']['complete'] is True and r['hidden_acceptance_calls']==1
        else:assert r['success'] is None and r['error']=={'type':'FinanceGateRejected','message':'GLOBAL_OR_PHASE_CAP'}
        requests=[read(p) for p in sorted(out.glob('llm/*_request.json'))]
        rows.append({**{k:r.get(k) for k in ('task_id','method','status','success','LLM_calls','new_paid_API','new_fees_CNY','elapsed_seconds','public_native_calls','hidden_acceptance_calls')},'request_full_reserves_CNY':[x['bounds']['global_reserve'] for x in requests],'result_sha256':sha(out/'result.json'),'actual_worker':worker,'all_Job_roots_and_descendants_closed':True,'native_physical_roots':len(native),'complete_core':r.get('runtime_core',{}).get('complete')})
    events=lines(V/'5980_serial_model_request_events.jsonl');assert len(events)==3 and all(x['held_before_delegate']=='0' and x['delegate_called_once'] for x in events)
    for event in events:
        method=event['role'].split('/')[2]
        out=V/'main/recovery/getmoto__moto-5980'/method
        assert any(read(p)['body_SHA256']==event['original_body_sha256'] for p in out.glob('llm/*_request.json'))
    ledger=shared_json(ROOT/'工作区/1003-diagnosis-investigation/exp132_review/new_window_2332/finance/shared_flash_budget.json')
    p=ledger['pilots']['Round2320Main'];finance={'Global':{k:ledger[k] for k in ('cap_CNY','spent_CNY','held_CNY','blocked')},'Main':{k:p[k] for k in ('cap_CNY','spent_CNY','held_CNY')}}
    report={'at_utc':now(),'rows':rows,'serialized_request_events':events,'exact_original_bodies_match_saved_requests':True,'finance_snapshot':finance,'paired_known':False,'paired_outcome':None,'old6387_nulls_and_fixed21_preserved':True,'future13_started':False,'interpretation':'Ours completed true; AL second single request no longer fits the unchanged global cap after both first costs settled. This is an incomplete budget-censored pair, not a win over AL. Serialization prevents temporary own in-flight reserve conflicts; it does not expand the8 cap or reprice usage.','new_model_native_Gold_finance_writes_for_audit':0}
    save(V/'serial_5980_actual_final_audit_v2.json',report)
    print(canonical({'at_utc':report['at_utc'],'rows':[{k:r[k] for k in ('status','success','new_fees_CNY','public_native_calls','hidden_acceptance_calls')} for r in rows],'finance':finance}))
if __name__=='__main__':main()

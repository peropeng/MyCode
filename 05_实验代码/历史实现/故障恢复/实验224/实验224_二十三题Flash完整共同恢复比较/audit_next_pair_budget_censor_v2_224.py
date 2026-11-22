"""Read-only exact paid/denied calls and stopped Jobs; shared ledger is share7."""
from common166 import *
import ctypes
from ctypes import wintypes as w
from decimal import Decimal
from publicpack_v2_224 import V
def shared_json(path):
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.CreateFileW.argtypes=[w.LPCWSTR,w.DWORD,w.DWORD,ctypes.c_void_p,w.DWORD,w.DWORD,w.HANDLE];k.CreateFileW.restype=w.HANDLE
    k.GetFileSizeEx.argtypes=[w.HANDLE,ctypes.POINTER(ctypes.c_longlong)];k.ReadFile.argtypes=[w.HANDLE,ctypes.c_void_p,w.DWORD,ctypes.POINTER(w.DWORD),ctypes.c_void_p];k.CloseHandle.argtypes=[w.HANDLE]
    h=k.CreateFileW(str(path),0x80000000,7,None,3,0,None);assert h and h!=ctypes.c_void_p(-1).value
    try:
        length=ctypes.c_longlong();assert k.GetFileSizeEx(h,ctypes.byref(length))
        data=ctypes.create_string_buffer(length.value);done=w.DWORD();assert k.ReadFile(h,data,length.value,ctypes.byref(done),None) and done.value==length.value
        return json.loads(data.raw.decode('utf-8-sig'))
    finally:k.CloseHandle(h)
def main():
    rows=[]
    for mode,method in (('main-agentless','AGENTLESS_FSE2025_4L4P4T_FLASH'),('main-ours','G_PROGRESSIVE_SEMANTIC_FLASH')):
        out=V/'main/recovery/getmoto__moto-6387'/method;r=read(out/'result.json');start=read(out/'worker_started.json')
        receipts=[read(p) for p in out.glob('llm/*_finance_receipt.json')]
        assert all(x['status']=='SETTLED' for x in receipts)
        assert len(receipts)==r['new_paid_API'] and sum((Decimal(x['usage_peak_cost_CNY']) for x in receipts),Decimal(0))==Decimal(r['new_fees_CNY'])
        request=read(out/'llm/001_request.json');stop=read(V/('supervision_'+mode+'_v2nextpair.json'))
        assert stop['status']=='STOPPED' and stop['job_closed_all_owned_descendants_terminated']
        assert r['success'] is None and r['public_native_calls']==r['hidden_acceptance_calls']==0
        rows.append({'mode':mode,'task_id':r['task_id'],'status':r['status'],'success':None,'error':r['error'],'paid_POSTs':r['new_paid_API'],'new_fees_CNY':r['new_fees_CNY'],'request_bounds':request['bounds'],'body_sha256':request['body_SHA256'],'result_sha256':sha(out/'result.json'),'worker':start['actual_worker'],'all_owned_Jobs_closed':True,'next12_started':(V/'main/recovery/getmoto__moto-5980'/method/'worker_started.json').exists()})
    assert rows[1]['error']=={'type':'FinanceGateRejected','message':'GLOBAL_OR_PHASE_CAP'} and rows[1]['paid_POSTs']==0
    ledger=shared_json(ROOT/'工作区/1003-diagnosis-investigation/exp132_review/new_window_2332/finance/shared_flash_budget.json')
    finance={k:ledger.get(k) for k in ('cap_CNY','spent_CNY','held_CNY','blocked','last_valid_balance_CNY')}
    total=sum((Decimal(x['request_bounds']['global_reserve']) for x in rows),Decimal(0))
    report={'at_utc':now(),'rows':rows,'initial_two_request_full_reserve_CNY':str(total),'root_release_spent_CNY':'7.18214210','root_release_available_CNY':'0.81785790','parallel_two_first_requests_cannot_fit_even_without_other_holds':total>Decimal('.81785790'),'live_finance_read_share_flags':'FILE_SHARE_READ|WRITE|DELETE','live_finance_snapshot':finance,'interpretation':'Known pre-POST cap refusal; no unpriced own call. Peer interruption retained null. Do not reroll either index11 terminal or treat it as model failure. Fixed12 is unstarted; a future exact next-only grant/namespace and serialized request scheduling are needed within the same8cap/body/output/seed/clock. Financial rules and ledger remain untouched.','new_model_native_private_Gold_for_audit':0,'shared_finance_writes':0}
    save(V/'next_pair_moto6387_budget_censor_audit_v2.json',report)
    print(canonical({k:report[k] for k in ('at_utc','initial_two_request_full_reserve_CNY','parallel_two_first_requests_cannot_fit_even_without_other_holds','live_finance_snapshot')}))
if __name__=='__main__':main()

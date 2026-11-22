"""Read-only terminal stop/censoring evidence; no method replay or model calls."""
from common166 import *
from publicpack_v2_224 import V
from second_entry_v2_224 import pid_birth

def export():
    archive=V/'extended_actual_stop';archive.mkdir(exist_ok=True)
    identities=[]
    methods={'main-agentless':'AGENTLESS_FSE2025_4L4P4T_FLASH','main-ours':'G_PROGRESSIVE_SEMANTIC_FLASH'}
    for mode,method in methods.items():
        p=V/('supervision_'+mode+'_v2extended.json');s=read(p)
        assert s['status']=='STOPPED' and s['job_closed_all_owned_descendants_terminated'] is True
        actual=read(V/'main/recovery/getmoto__moto-5286'/method/'worker_started.json')['actual_worker']
        for pid,birth in [(actual['actual_self_PID'],actual['actual_self_creation_time100ns']),
                          (actual['logical_launcher_PID'],actual['logical_launcher_creation_time100ns'])]:
            try:current=pid_birth(pid)
            except (AssertionError,OSError):current=None
            assert current!=birth
        (archive/(mode+'.json')).write_bytes(p.read_bytes())
        identities.append({'mode':mode,'supervision':s,'actual_worker':actual,'owned_births_no_longer_alive':True,
                           'snapshot_sha256':sha(archive/(mode+'.json'))})
    g=V/'main/recovery/pydantic__pydantic-8567/G_PROGRESSIVE_SEMANTIC_FLASH'
    a=V/'main/recovery/getmoto__moto-6352/AGENTLESS_FSE2025_4L4P4T_FLASH'
    events=[json.loads(line) for line in (g/'stage_ledger.jsonl').read_text('utf-8-sig').splitlines()]
    preflight=[x for x in events if x['stage']=='v2_actual_body_preflight'][-1]
    response=[x for x in events if x['stage']=='Flash_actual_response224'][-1]
    last=read(g/'llm/055_request.json')
    assert read(g/'result.json')['error']=={'type':'FinanceGateRejected','message':'CONTEXT_BOUND'}
    ledger=read(ROOT/'工作区/1003-diagnosis-investigation/exp132_review/new_window_2332/finance/shared_flash_budget.json')
    report={'at_utc':now(),'status':'BOTH_EXTENDED_JOBS_STOPPED_CONTEXT_CENSORED_RAW_PRESERVED',
            'stops':identities,'unknown_result_sha256':{'main-ours':sha(g/'result.json'),'main-agentless':sha(a/'result.json')},
            'first_error_utc':'2026-10-08T22:01:15.058154+00:00',
            'rejected_request_preflight':preflight,'last_accepted_actual_usage':response['evidence']['usage'],
            'last_accepted_body_messages':len(last['body']['messages']),
            'last_accepted_local_bound':last['bounds'],
            'local_guard_formula':'size=canonical(body).UTF8bytes+4096*len(messages)+2048; CONTEXT_BOUND if size+max_tokens>1048576',
            'cause_fact':'Local conservative context guard refused before reservation/POST; not a provider failure response',
            'unverified':'Rejected body actual token count has not been measured; no context-contract or reservation-rule change deployed',
            'financial_state':{k:ledger.get(k) for k in ('spent_CNY','held_CNY','blocked','cap_CNY','floor_CNY')},
            'interpretation':'Both unknowns stay null. AL current task interrupted by peer-unknown gate, not a method failure. No retry/reroll.',
            'continuation_block':'Existing extended entry cannot acknowledge BUDGET_CENSORED/FinanceGateRejected context refusal; root must review a concrete new overlay before continuation',
            'new_model_POST_native_private_Gold_for_export':0}
    for directory in (g,a):
        receipts=[read(p) for p in directory.glob('llm/*_finance_receipt.json')]
        assert all(r['status']=='SETTLED' for r in receipts)
        for p in directory.rglob('*.process.json'):
            proc=read(p);assert proc['root_PID_birth_verified'] and proc['stop_receipt']['all_owned_descendants_terminated']
    save(V/'extended_main_context_stop_evidence_v2.json',report)
    print(canonical({k:report[k] for k in ('status','unknown_result_sha256','financial_state','new_model_POST_native_private_Gold_for_export')}))

if __name__=='__main__':export()

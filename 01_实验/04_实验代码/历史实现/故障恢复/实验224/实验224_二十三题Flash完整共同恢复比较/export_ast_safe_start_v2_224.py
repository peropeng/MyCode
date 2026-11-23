"""Read-only exact live birth and first settled Main request evidence."""
from common166 import *
from publicpack_v2_224 import V
from second_entry_v2_224 import pid_birth

def export():
    pairs=[('main-agentless','python__mypy-11134','AGENTLESS_FSE2025_4L4P4T_FLASH'),
           ('main-ours','getmoto__moto-7081','G_PROGRESSIVE_SEMANTIC_FLASH')]
    rows=[]
    for mode,task,method in pairs:
        out=V/'main/recovery'/task/method
        sup=read(V/('supervision_'+mode+'_v2astsafe.json'))
        worker=read(out/'worker_started.json');actual=worker['actual_worker']
        assert sup['status']=='RUNNING' and sup['job_kill_on_close'] and sup['suspended_until_assigned_to_job']
        assert pid_birth(actual['actual_self_PID'])==actual['actual_self_creation_time100ns']
        assert pid_birth(actual['logical_launcher_PID'])==actual['logical_launcher_creation_time100ns']
        assert sup['runner_creation_time100ns']==actual['logical_launcher_creation_time100ns']
        receipt_path=next(p for p in sorted(out.glob('llm/*_finance_receipt.json')) if read(p)['status']=='SETTLED')
        receipt=read(receipt_path)
        stem=receipt_path.name.removesuffix('_finance_receipt.json')
        request=read(out/'llm'/(stem+'_request.json'))
        rows.append({'mode':mode,'task_id':task,'actual_worker':actual,'supervision':sup,'first_receipt_sha256':sha(receipt_path),
                     'first_receipt_status':receipt['status'],'first_fee_CNY':receipt['usage_peak_cost_CNY'],
                     'first_request_sha256':sha(out/'llm'/(stem+'_request.json')),'body_SHA256':request['body_SHA256'],
                     'actual_registered_phase':receipt.get('pilot'),'exact_birth_verified_live':True})
    report={'at_utc':now(),'status':'ACTUAL_AST_SAFE_TWO_ARMS_LIVE_FIRST_SETTLED_REQUESTS','source_pin_sha256':sha(V/'ast_safe_main_source_pin_v2.json'),
            'grant_sha256':sha(V/'root_ast_safe_main_grant_v2.json'),'rows':rows,'new_POST_native_private_Gold_for_audit':0}
    save(V/'ast_safe_actual_start_first_receipts_v2.json',report)
    print(canonical({'status':report['status'],'at_utc':report['at_utc'],'rows':[{'mode':r['mode'],'PID':r['actual_worker']['actual_self_PID'],
                     'first_fee_CNY':r['first_fee_CNY'],'phase':r['actual_registered_phase']} for r in rows]}))
if __name__=='__main__':export()

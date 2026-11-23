"""Source/terminal review only, with no simulation, model or native calls."""
from common166 import *
import ast,ctypes
from ctypes import wintypes
from publicpack_v2_224 import V
from second_entry_v2_224 import pid_birth
def original_alive(pid,expected):
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD];kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    handle=kernel.OpenProcess(0x1000|0x100000,False,pid)
    if not handle:
        assert ctypes.get_last_error()==87,'ORIGINAL_PROCESS_QUERY_UNKNOWN'
        return False
    try:
        return pid_birth(pid)==expected and kernel.WaitForSingleObject(handle,0)==258
    finally:kernel.CloseHandle(handle)
def main():
    names=('next_pair_main_controller_v2_224.py','next_pair_main_entry_v2_224.py','supervise_next_pair_main_v2_224.py','prepare_next_pair_main_v2_224.py','dense_wall_guard_proposal224.py')
    sources={str(E/n):sha(E/n) for n in names}
    for n in names:ast.parse((E/n).read_text('utf-8-sig'))
    order=read(V/'main_addendum_source_pin_v2.json')['task_order'];assert len(order)==21
    assert order[11:13]==['getmoto__moto-6387','getmoto__moto-5980']
    inputs={};results={}
    for mode,method in (('main-agentless','AGENTLESS_FSE2025_4L4P4T_FLASH'),('main-ours','G_PROGRESSIVE_SEMANTIC_FLASH')):
        stop=V/('supervision_'+mode+'_v2astsafe.json');s=read(stop)
        assert s['status']=='STOPPED' and s['job_closed_all_owned_descendants_terminated']
        assert not original_alive(s['runner_pid'],s['runner_creation_time100ns']),'OLD_ACTUAL_LAUNCHER_STILL_ALIVE'
        inputs[str(stop)]=sha(stop)
        for index,task in enumerate(order[:11]):
            p=V/'main/recovery'/task/method/'result.json';assert p.exists()
            inputs[str(p)]=sha(p);results[mode+':'+str(index)]={'task_id':task,'success':read(p)['success'],'sha256':sha(p)}
        for task in order[11:13]:
            out=V/'main/recovery'/task/method
            assert not (out/'worker_started.json').exists() and not (out/'result.json').exists(),'NEXT_FIXED_CASE_ALREADY_STARTED'
    reviewed=0
    for name in ('source_seal_v2.json','main_addendum_source_pin_v2.json','independent_main_source_pin_v2.json',
                 'extended_main_source_pin_v2.json','scoped_main_source_pin_v2.json','io_retry_main_source_pin_v2.json',
                 'ast_safe_main_source_pin_v2.json','moto5406_external_deadline_stop_v2.json','dense_wall_guard_proposal_pure_checks_v2.json'):
        p=V/name;inputs[str(p)]=sha(p)
        spec=read(p)
        for section in ('sealed_files','read_only_original_specs','new_sources','read_only_inputs','read_only_completed_inputs'):
            for source,expected in spec.get(section,{}).items():
                if isinstance(expected,str) and len(expected)==64:
                    assert sha(source)==expected,'ORIGINAL_PIN_SOURCE_DRIFT '+source
                    reviewed+=1
    pin=read(V/'ast_safe_main_source_pin_v2.json')
    for p,h in {**pin['new_sources'],**pin['read_only_inputs']}.items():assert sha(p)==h
    save(V/'next_pair_main_source_pin_v2.json',{'schema':'fixed_main21_next11_12/1','new_sources':sources,'read_only_inputs':inputs,'task_order_unchanged':order,'only_future_indices':[11,12],'all_previous_terminal_results':results})
    grant=read(V/'root_ast_safe_main_grant_v2.json');grant.update(root_authorized=False,allowed_through_index=12,
        administrative_frontier_reason='Prepared fixed original Main indices11/12 only; reserve actual fees until fresh Root grant. Previous terminal observations are never resumed or rerolled.',
        next_fixed_main11_12_root_accepted=True,next_pair_controller_pin_sha256=sha(V/'next_pair_main_source_pin_v2.json'),
        dense_existing_clock_batch_guard_root_accepted=True,external_case_deadline_next_ack={
            'root_explicit_next_only':True,'continue_from_index':11,'original_result_sha256':sha(V/'main/recovery/getmoto__moto-5406/AGENTLESS_FSE2025_4L4P4T_FLASH/result.json'),
            'external_stop_receipt_sha256':sha(V/'moto5406_external_deadline_stop_v2.json'),'keep_original_null':True,'no_resumption_or_reroll':True})
    save(V/'root_next_pair_main_grant_PROPOSAL_v2.json',grant)
    from next_pair_main_entry_v2_224 import entry_source
    ast.parse(entry_source())
    report={'at_utc':now(),'status':'SOURCE_PREPARED_NO_MODEL_NATIVE','pin_sha256':sha(V/'next_pair_main_source_pin_v2.json'),'next':order[11:13],
            'new_sources':sources,'old_AST_pin_sha256':sha(V/'ast_safe_main_source_pin_v2.json'),'previous_terminals':results,
            'no_old_terminal_reroll':True,'original_body_seed_64calls_65536output_900seconds_unchanged':True,
            'dense_guard':'Existing c147cf... five checked proposal, future only, existing env._require around exact encoder batches; no new tests/simulation loops.',
            'root_actual_grant_required':str(V/'root_next_pair_main_grant_v2.json'),'original_sealed_source_or_shared_finance_writes':0,'new_model_API_native_private_Gold':0}
    report['original_nested_pin_source_hashes_reviewed']=reviewed
    save(V/'next_pair_main_handoff_v2.json',report);print(canonical({k:report[k] for k in ('at_utc','status','pin_sha256','next')}))
if __name__=='__main__':main()

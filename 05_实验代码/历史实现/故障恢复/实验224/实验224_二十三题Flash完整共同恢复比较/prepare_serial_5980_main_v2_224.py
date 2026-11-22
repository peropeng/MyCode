from common166 import *
import ast
from publicpack_v2_224 import V
def main():
    names=('serial_5980_main_controller_v2_224.py','serial_5980_main_entry_v2_224.py','supervise_serial_5980_main_v2_224.py','prepare_serial_5980_main_v2_224.py','audit_next_pair_budget_censor_v2_224.py')
    sources={str(E/n):sha(E/n) for n in names}
    for n in names:ast.parse((E/n).read_text('utf-8-sig'))
    inputs={str(V/'next_pair_main_source_pin_v2.json'):sha(V/'next_pair_main_source_pin_v2.json')}
    for p,h in {**read(V/'next_pair_main_source_pin_v2.json')['new_sources'],**read(V/'next_pair_main_source_pin_v2.json')['read_only_inputs']}.items():assert sha(p)==h
    results={}
    for mode,method in (('main-agentless','AGENTLESS_FSE2025_4L4P4T_FLASH'),('main-ours','G_PROGRESSIVE_SEMANTIC_FLASH')):
        stop=V/('supervision_'+mode+'_v2nextpair.json');s=read(stop);assert s['status']=='STOPPED' and s['job_closed_all_owned_descendants_terminated']
        inputs[str(stop)]=sha(stop);p=V/'main/recovery/getmoto__moto-6387'/method/'result.json';inputs[str(p)]=sha(p);results[mode]=sha(p)
        out=V/'main/recovery/getmoto__moto-5980'/method;assert not (out/'worker_started.json').exists() and not (out/'result.json').exists()
    save(V/'serial_5980_main_source_pin_v2.json',{'schema':'fixed5980_serial_full_model_request/1','new_sources':sources,'read_only_inputs':inputs})
    g=read(V/'root_next_pair_main_grant_v2.json');g.update(root_authorized=False,allowed_through_index=12,fixed_5980_serial_requests_root_accepted=True,
        serial_5980_controller_pin_sha256=sha(V/'serial_5980_main_source_pin_v2.json'),known_prepost6387_next_only_ack={'root_explicit_next_only':True,'continue_from_index':12,'keep_both_original_null':True,'no_replay_or_reroll':True,'results_sha256':results})
    save(V/'root_serial_5980_main_grant_PROPOSAL_v2.json',g)
    from serial_5980_main_entry_v2_224 import entry_source
    ast.parse(entry_source())
    report={'at_utc':now(),'pin_sha256':sha(V/'serial_5980_main_source_pin_v2.json'),'status':'READY_PREPARED_NOT_EXECUTED','fixed_only_index':12,'task_id':'getmoto__moto-5980','old6387_result_sha256':results,
            'API_policy':'One dedicated cross-process byte0 under own file spans pre-reserve to original full settlement; wait original clock and wait held0 before original admission; same body/seed/caps/price; original generate called once/no HTTP retries. No shared transport file changes.',
            'current5980_known_cap_policy':'Known pre-POST cap with rejected request and no HTTP/receipt stays null/own stop while healthy peer may finish; real unpriced/global unknown still stops both. No future13 admission.',
            'new_model_API_native_Gold_finance_writes':0,'actual_root_grant_required':str(V/'root_serial_5980_main_grant_v2.json')}
    save(V/'serial_5980_main_handoff_v2.json',report);print(canonical(report))
if __name__=='__main__':main()

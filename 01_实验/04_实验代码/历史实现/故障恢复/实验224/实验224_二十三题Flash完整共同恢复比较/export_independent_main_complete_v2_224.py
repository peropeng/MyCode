"""Final read-only process and completed-results export using exact Win32 births."""
from common166 import *
from publicpack_v2_224 import V
from second_entry_v2_224 import pid_birth

def export():
    identities=[]
    for mode in ('main-agentless','main-ours'):
        point=read(V/('main_checkpoint_'+mode+'.json'))
        assert point['phase']=='WAIT_ROOT_PAIRED_WINDOW' and point['task_index']==3
        assert point['no_POST_native_in_boundary_wait'] is True
        actual=point['actual_worker']
        assert pid_birth(actual['actual_self_PID'])==actual['actual_self_creation_time100ns']
        assert pid_birth(actual['logical_launcher_PID'])==actual['logical_launcher_creation_time100ns']
        sup=read(V/('supervision_'+mode+'_v2independent.json'))
        assert sup['status']=='RUNNING' and sup['runner_pid']==actual['logical_launcher_PID']
        assert sup['runner_creation_time100ns']==actual['logical_launcher_creation_time100ns']
        assert sup['job_kill_on_close'] and sup['suspended_until_assigned_to_job']
        identities.append({'mode':mode,'actual_worker':actual,'supervisor_PID':sup['supervisor_pid'],
                           'status':'RUNNING_AT_INDEX3_BOUNDARY','exact_Win32_births_verified':True})
    observation=read(V/'independent_main_observation_v2.json')
    assert len(observation['rows'])==4 and all(r['success'] is True and r['complete'] is True for r in observation['rows'])
    result={'at_utc':now(),'status':'GRANTED_TWO_NEW_CASES_COMPLETE','actual_new_results':4,'actual_new_successes':4,
            'observation':observation,'identities':identities,'root_grant_sha256':sha(V/'root_independent_main_grant_v2.json'),
            'controller_pin_sha256':sha(V/'independent_main_source_pin_v2.json'),'first_outputs_rerun':0,
            'next_index3_not_started':not (V/'main/recovery/getmoto__moto-5286').exists(),
            'new_POST_native_private_Gold_for_audit':0}
    assert result['next_index3_not_started'] is True
    save(V/'independent_main_two_case_complete_v2.json',result)
    print(canonical({k:result[k] for k in ('status','actual_new_results','actual_new_successes','next_index3_not_started')}))

if __name__=='__main__':export()

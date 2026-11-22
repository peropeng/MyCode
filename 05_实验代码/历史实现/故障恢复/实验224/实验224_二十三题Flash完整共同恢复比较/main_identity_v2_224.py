"""Reuse root-verified direct/venv-redirect identity helpers without file changes."""
import os
from second_entry_v2_224 import current_birth, actual_parent_pid, pid_birth


def verify_worker(supervisor):
    assert supervisor['status'] == 'RUNNING' and supervisor['job_kill_on_close'] and supervisor['suspended_until_assigned_to_job'], 'MAIN_OWNED_PARENT_JOB_REQUIRED'
    actual = os.getpid(); actual_birth = current_birth()
    launcher = supervisor['runner_pid']; expected = supervisor['runner_creation_time100ns']
    parent = actual_parent_pid()
    if launcher == actual:
        assert expected == actual_birth, 'MAIN_DIRECT_SELF_BIRTH_MISMATCH'
    else:
        assert parent == launcher and pid_birth(launcher) == expected, 'MAIN_REDIRECT_PARENT_BIRTH_MISMATCH'
    return {'actual_self_PID': actual, 'actual_self_creation_time100ns': actual_birth,
            'logical_launcher_PID': launcher, 'logical_launcher_creation_time100ns': expected,
            'actual_parent_PID': parent, 'direct_or_redirect_lineage_verified': True,
            'identity_implementation': 'Unchanged root-reviewed second-task helpers'}

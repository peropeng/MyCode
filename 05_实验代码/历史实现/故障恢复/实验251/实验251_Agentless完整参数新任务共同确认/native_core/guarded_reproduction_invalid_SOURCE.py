"""Pure classification of completed guarded scripts; grants no new permission."""
import os
from collections import Counter

class ScopeEvidenceUnknown(RuntimeError):pass

def classify(native,scope_rows,guard_loaded,state_stable,frozen_stable,expected_image,current_output):
    def need(value,reason):
        if not value:raise ScopeEvidenceUnknown(reason)
    need(native.get('executed') is True and native.get('timeout') is False and type(native.get('exit_code')) is int,
         'GENERATED_ACTUAL_EXECUTION_OR_FINITE_EXIT_UNKNOWN')
    identity=native.get('actual_product_python_identity',{})
    need(identity.get('before_product_import') is True and identity.get('IsProcessInJob_specific_own_Job') is True
         and identity.get('specific_named_Job')==native.get('Job')
         and os.path.normcase(os.path.realpath(identity.get('actual_OS_image_GetModuleFileName','')))==os.path.normcase(os.path.realpath(expected_image)),
         'GENERATED_PHYSICAL_SELF_IDENTITY_OR_SPECIFIC_JOB_UNKNOWN')
    stop=native.get('stop_receipt',{})
    need(all(stop.get(k) is True for k in ('root_stopped','own_Job_empty_before_close','descendants_stopped',
         'assigned_root_verified_member','root_process_stopped','all_owned_descendants_terminated'))
         and stop.get('job_active_processes_after_termination')==0,'GENERATED_ACTUAL_STOP_UNKNOWN')
    need(guard_loaded is True and state_stable is True and frozen_stable is True,
         'GENERATED_GUARD_OR_SOURCE_FROZEN_STATE_UNKNOWN')
    need(isinstance(scope_rows,list) and bool(scope_rows) and scope_rows[0].get('event')=='SCOPE_V2_INSTALL'
         and scope_rows[0].get('no_experiment_directory_root') is True
         and os.path.normcase(os.path.realpath(scope_rows[0].get('current_native_output','')))==os.path.normcase(os.path.realpath(current_output)),
         'GENERATED_ACTUAL_SCOPE_AUDIT_HEADER_UNKNOWN')
    operations=scope_rows[1:]
    need(all(type(row.get('allowed')) is bool and isinstance(row.get('event'),str)
         and isinstance(row.get('reason'),str) for row in operations),'GENERATED_SCOPE_OPERATION_EVIDENCE_MALFORMED')
    denials=[row for row in operations if row['allowed'] is False]
    return {'known_completed_guarded_script':True,'known_guard_refusal_invalid':bool(denials),
        'scope_denials_retained':True,'scope_denial_count':len(denials),
        'scope_denial_reason_counts':dict(Counter(row['event']+':'+row['reason'] for row in denials)),
        'no_permission_expanded':True,'guard_refusal_never_issue_reproduced_or_resolved':bool(denials)}

"""Bind Root-published masked public scope to a closed current-C0 grant."""
import argparse
from common_current_C0 import *
from audit_public_mask_SOURCE import public_mask_audit

def main():
 p=argparse.ArgumentParser();p.add_argument('--task',choices=TASKS,required=True);a=p.parse_args()
 _,c=binding(a.task);scope_path=E/'public_views'/a.task/'COMMON_MASKED_PUBLIC_TEST_SCOPE249.json'
 scope=read(scope_path);audit=public_mask_audit(c,scope)
 g=read(E/'grant_templates'/(a.task+'.current_C0.pending_mask.false.json'))
 if any(g.get(k) is not False for k in ('root_authorized','native_authorized','model_authorized','private_execution_authorized','finance_authorized')):raise RuntimeError('NEXT_C0_FALSE_TEMPLATE_ONLY')
 g.update(masked_scope_SHA256=sha(scope_path),masked_channel_qualification_nodes=audit['masked_channel_qualification_nodes'],Root_auxiliary_channel_only_original_O_retained=audit['auxiliary_channel_only_original_G_O_unchanged'],after_mask_binding_required=False)
 out=E/'after_mask_SOURCE'/a.task;target=out/'CURRENT_C0_AFTER_MASK_BOUND_FALSE.json'
 if target.exists() and read(target)!=g:raise RuntimeError('NEXT_C0_BOUND_TEMPLATE_ALREADY_FROZEN')
 if not target.exists():save(target,g)
 save(out/'PUBLIC_MASK_STATIC_AUDIT.json',audit)
 print(canonical({'status':'CURRENT_C0_AFTER_MASK_SOURCE_BOUND_FALSE','false_grant':str(target),'sha256':sha(target),'actual_calls':0}),flush=True)

if __name__=='__main__':main()

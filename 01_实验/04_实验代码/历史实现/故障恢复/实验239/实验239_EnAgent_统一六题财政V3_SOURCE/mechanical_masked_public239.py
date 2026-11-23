"""Pending Root-only mechanical entry: full masked collect, one leaf, full body.

This source file is not execution authorization. One finite300s supervisor owns
all processes, no model response/private execution/finance IO is permitted.
"""
from common166 import *
import copy
import control235,entry_sourceio_v4_239

def main():
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--task',required=True);args=a.parse_args()
 control235.start_mechanical();control235.verify(args.task,control235.PHASE)
 control235.MECHANICAL_NAMESPACE='masked_qualification_'+args.task+'_'+str(os.getpid())
 from process_budget239 import install_process_creation_guard
 install_process_creation_guard()
 worker=entry_sourceio_v4_239.install()
 ref=copy.deepcopy(next(v for v in read(worker.PEER/'data/selected_task_bindings.json')['tasks'] if v['task_id']==args.task))
 ref.update(_output_namespace=control235.MECHANICAL_NAMESPACE+'/f',_native_namespace=control235.MECHANICAL_NAMESPACE+'/n')
 env=worker.CommonEnvironment(ref,'ENAGENT_MASKED_PUBLIC_MECHANICAL_NO_MODEL')
 install_process_creation_guard(env)
 bridge=worker.Bridge(env);initial=bridge.export()
 core=worker.module('exp239_masked_mechanical_core',worker.OLD175/'enagent_native.py')
 root=bridge.owned/'masked_public_actor';business=sorted(bridge.initial)
 core.snapshot_copy(initial,root,business,core.digest(initial,business))
 collection=bridge.masked_native(root,None,collect_only=True,label='full_masked_collection')
 nodes=collection.get('pytest',{}).get('collected',[])
 leaf=None
 if nodes:
  # Deterministic first leaf, irrespective of outcome; not a chosen victory.
  leaf=bridge.masked_native(root,[nodes[0]],label='first_collected_public_leaf')
 from mechanical239 import Capture,BodyCaptured
 import backend225
 original=backend225.module
 backend225.module=lambda name,path:Capture if Path(path).resolve()==TRANSPORT.resolve() else original(name,path)
 control235.MECHANICAL_NAMESPACE+='body_capture'
 try:worker.run(args.task,control235.PHASE)
 except BodyCaptured:captured=True
 else:raise RuntimeError('MASKED_QUALIFICATION_FIRST_BODY_NOT_CAPTURED')
 record={'schema':'EnAgent239-masked-public-method-qualification/1','task':args.task,'complete_public_collection_known':collection['known'],'first_leaf_actual_result_known':leaf['known'] if leaf else None,'first_leaf_not_invented_if_collection_empty':True,'collection_record':collection,'first_public_leaf_record':leaf,'full_actual_first_body_capture':captured,'actual_C0_PASS_pool':None,'whole_pool_PASS_qualification_not_claimed_from_collect':True,'POSTs':0,'private':0,'finance_IO':0,'Root_independent_review_still_required':True}
 save(E/'MASKED_PUBLIC_MECHANICAL239.json',record)
 print(canonical({'task':args.task,'collection_known':collection['known'],'leaf_known':leaf['known'] if leaf else None,'POSTs_private':0,'first_body':captured}),flush=True)
if __name__=='__main__':main()

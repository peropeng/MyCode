"""Same Agentless dense retrieval core; public query uses unique complete errors."""
from common166 import *
def public_query(task):
 feedback=task.get('failure_feedback',{})
 if isinstance(feedback,dict) and feedback.get('schema')=='public-failure-index-with-exact-node-reader/1':
  errors=feedback['errors']
 else:
  from common_environment224 import semantic_index
  errors=semantic_index(feedback)['errors']
 return 'Restore the observed failure while preserving passing behavior. Original issue background: '+str(task['task'])+'\nAll distinct observed public errors:\n'+canonical(errors)
def retrieve(files,query,ref,allowed):
 from agentless_bridge import dense166
 directory=E/'retrieval';directory.mkdir(parents=True,exist_ok=True)
 prior=OLD/'retrieval178/vectors'
 target=directory/'vectors';target.mkdir(exist_ok=True)
 reused=0
 for p in prior.glob('*.npy'):
  dest=target/p.name
  if not dest.exists():os.link(p,dest);reused+=1
 # Dense prepare verifies text/hash identity; new vectors are separately counted.
 path,cache=dense166.prepare(files,query,directory,'public_common_query224',device='cpu',batch_size=4)
 result,evidence=dense166.retrieve(files,query,path,allowed)
 evidence.update(old_exact_vector_hardlinks=reused,actual_new_encoding_texts=cache['encoder_new_texts'],query_policy='complete original issue and all distinct observed exact error signatures; every node detail is readable',new_training=False)
 return result,evidence

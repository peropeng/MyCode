"""Lossless semantic public feedback projection; raw process records stay on disk."""
import copy, hashlib, json, re
TRANSPORT = frozenset(('argv','cwd','seconds','pid','parent_pid','runner_pid','supervisor_pid','at_utc','label','method','task_id','snapshot','snapshot_sha256','inventory_sha256','log','log_sha256','guard_events','product_import','actual_product_imports','guard','node_selection_transport','node_selection_json','stop_receipt','process_birth','runner_creation_time100ns','elapsed_seconds','queue_wait_seconds'))
def canonical(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def sha(x): return hashlib.sha256(canonical(x).encode()).hexdigest()
def project_feedback(value):
 if isinstance(value,list): return [project_feedback(x) for x in value]
 if not isinstance(value,dict): return value
 result={k:project_feedback(v) for k,v in value.items() if k not in TRANSPORT}
 if isinstance(result.get('native_record'),dict):
  all_nodes=result['native_record'].get('pytest',{}).get('outcomes',{})
  subset=result.get('outcomes',{})
  if subset and all(n in all_nodes and all(all_nodes[n].get(k)==v for k,v in row.items() if k!='outcome') for n,row in subset.items()):
   result['ordinary_node_refs']=list(subset)
   del result['outcomes']
 return result
def semantic_leaves(value):
 out=[]
 if isinstance(value,dict):
  for k,v in value.items():
   if k in TRANSPORT: continue
   if k in ('detail','error','errors','stderr','stdout','traceback','status','outcome','when','collection_errors','actual_failures'):
    out.append((k,sha(v)))
   out.extend(semantic_leaves(v))
 elif isinstance(value,list):
  for v in value: out.extend(semantic_leaves(v))
 return out
def project_payload(payload):
 raw=copy.deepcopy(payload); new=copy.deepcopy(payload)
 initial=project_feedback(raw.get('initial_public_failure',{})); new['initial_public_failure']=initial
 goal=str(raw.get('goal',''))
 marker='\nObserved current public recovery failure: '
 if marker in goal:
  background, duplicate=goal.split(marker,1)
  assert sha(json.loads(duplicate))==sha(raw['initial_public_failure'])
  new['goal']=background
 latest=new.get('latest_public_feedback',{})
 if 'initial_public_failure' in latest:
  assert sha(latest['initial_public_failure'])==sha(raw['initial_public_failure'])
  del latest['initial_public_failure']
 if 'complete_attempt_feedback' in latest:
  latest['complete_attempt_feedback']=project_feedback(latest['complete_attempt_feedback'])
 new['latest_public_feedback']=latest
 # All semantic leaves in each original feedback survive the projection verbatim.
 before=semantic_leaves(raw.get('initial_public_failure',{}))+semantic_leaves(raw.get('latest_public_feedback',{}))
 after=semantic_leaves(initial)+semantic_leaves(latest)
 assert set(before)<=set(after), 'PUBLIC_SEMANTIC_LEAF_REMOVED'
 displayed=set()
 for item in new.get('ordered_public_edit_evidence',[]):
  if isinstance(item,dict) and isinstance(item.get('path'),str): displayed.add(item['path'])
 for item in new.get('current_business_diff',[]):
  if isinstance(item,dict) and isinstance(item.get('path'),str): displayed.add(item['path'].removeprefix('repo/'))
 text=canonical(initial).replace('\\','/')
 for p in new.get('legal_paths',[]):
  if p in text: displayed.add(p)
 legal=new.get('legal_paths',[])
 if displayed:
  new['legal_paths']=sorted(displayed.intersection(legal))
  new['business_path_permission']='Displayed paths have current source, edit, or public error evidence. Other existing business paths remain legally editable; backend permissions are unchanged.'
 audit={'raw_sha256':sha(raw),'projected_sha256':sha(new),'raw_utf8_bytes':len(canonical(raw).encode()),'projected_utf8_bytes':len(canonical(new).encode()),'semantic_leaf_hashes_preserved':True,'semantic_hashes_before':sorted(set(before)),'semantic_hashes_after':sorted(set(after)),'removed_process_fields':sorted(TRANSPORT),'duplicate_initial_feedback_removed':True,'backend_business_permissions_unchanged':True,'original_legal_path_count':len(legal),'displayed_legal_path_count':len(new.get('legal_paths',[])),'no_error_source_or_edit_parameter_string_clipping':True}
 return new,audit
def project_saved_messages(messages):
 new=copy.deepcopy(messages)
 for row in new:
  if row.get('role')!='user': continue
  try: value=json.loads(row.get('content',''))
  except (TypeError,ValueError): continue
  if isinstance(value,dict) and 'ordered_public_edit_evidence' in value:
   value,_=project_payload(value);row['content']=json.dumps(value,ensure_ascii=False)
 return new

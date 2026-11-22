"""Static public edit evidence audit, without repair generation or execution."""
import ast,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def blob(root,binding):
 if binding is None:return ''
 raw=(root/binding['blob']).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==binding['sha256'],'PUBLIC_BLOB_SHA_DRIFT'
 return raw.decode('utf-8')
def symbols(text):
 try:tree=ast.parse(text)
 except SyntaxError as error:return {'parse_status':'SYNTAX_ERROR','line':error.lineno,'message':error.msg}
 functions={};assigned=set();loaded=set()
 def walk(node,prefix=''):
  for child in ast.iter_child_nodes(node):
   if isinstance(child,ast.ClassDef):walk(child,prefix+child.name+'.')
   elif isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef)):
    functions[prefix+child.name]=ast.dump(child.args,include_attributes=False)
    walk(child,prefix+child.name+'.')
   else:walk(child,prefix)
 walk(tree)
 for node in ast.walk(tree):
  if isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name) and node.value.id=='self':
   (assigned if isinstance(node.ctx,ast.Store) else loaded).add(node.attr)
 return {'parse_status':'PARSED','functions':functions,'assigned_self_attributes':sorted(assigned),'loaded_self_attributes':sorted(loaded)}
def main():
 refs=read(E/'data/selected_task_bindings.json')['tasks'];out=[]
 for ref in refs:
  edits=read(Path(ref['task_path'])/'visible/edits.json');rows=[]
  for edit in edits:
   path=edit['state_path'].removeprefix('repo/')
   if not path.endswith('.py') or any(part in ('tests','test') for part in path.split('/')):continue
   before=blob(Path(ref['asset_root']),edit.get('before'));after=blob(Path(ref['asset_root']),edit.get('after'))
   if before==after:continue
   b=symbols(before);a=symbols(after)
   row={'call_id':edit['call_id'],'business_path':path,'before_sha256':hashlib.sha256(before.encode()).hexdigest(),'after_sha256':hashlib.sha256(after.encode()).hexdigest(),'before_parse':b['parse_status'],'after_parse':a['parse_status']}
   if b['parse_status']==a['parse_status']=='PARSED':
    bf=b['functions'];af=a['functions']
    removed=set(b['assigned_self_attributes'])-set(a['assigned_self_attributes'])
    row.update(removed_functions=sorted(bf.keys()-af.keys()),added_functions=sorted(af.keys()-bf.keys()),
               changed_function_signatures=sorted(k for k in bf.keys()&af.keys() if bf[k]!=af[k]),
               removed_self_assignments=sorted(removed),
               removed_assignment_still_read=sorted(removed&set(a['loaded_self_attributes'])))
   else:row['parse_failure']={k:v for k,v in (a if a['parse_status']!='PARSED' else b).items() if k in ('line','message')}
   rows.append(row)
  out.append({'task_id':ref['task_id'],'stratum':ref['stratum'],'public_edits':rows})
 report={'schema':'Exp224-public-interface-source-audit/1','scope':'Verified public before/after blobs only; syntactic candidates, not causal proof or repair answers',
         'distinct_tasks':len(out),'rows':out,'model_generation':0,'native_execution':0,'new_private_or_gold':0,
         'tasks_with_changed_signatures':sum(any(r.get('changed_function_signatures') for r in t['public_edits']) for t in out),
         'tasks_with_removed_assignment_still_read':sum(any(r.get('removed_assignment_still_read') for r in t['public_edits']) for t in out)}
 p=E/'audit224/public_interface_source_audit224.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({k:report[k] for k in ('distinct_tasks','tasks_with_changed_signatures','tasks_with_removed_assignment_still_read','model_generation','native_execution','new_private_or_gold')}))
 print(json.dumps([{'task_id':t['task_id'],'signals':[r for r in t['public_edits'] if r.get('removed_assignment_still_read') or r.get('changed_function_signatures')]} for t in out if any(r.get('removed_assignment_still_read') or r.get('changed_function_signatures') for r in t['public_edits'])],ensure_ascii=False))
if __name__=='__main__':main()

"""Reconcile closed ScopeV2 Python events, without private/result content reads."""
import argparse,ast,datetime
from contracts241 import *
SG=HERE.parent/'实验241_Agentless新确认集21_生成测试ScopeV2'

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--task',required=True);args=parser.parse_args()
 task=args.task;flow=SG/'runs'/task/METHOD;supervision=SG/'supervision'/task
 stop=read(supervision/'parent_stop_receipt.json')
 if not all(stop['stop_receipt'].get(k) for k in ('root_stopped','own_Job_empty_before_close','descendants_stopped')):
  raise EngineeringUnknown('AUDIT_ONLY_CLOSED_SCOPE_V2_AUTHOR')
 scope_module=module('audit_closed_scope_policy241',SG/'generated_scope_v2_241.py')
 rows=[];problems=[]
 for script in sorted((flow/'generated_native').glob('*/generated_test.py')):
  out=script.parent;log=out/'generated_scope_events.jsonl';envelope=read(out/'entry_envelope.json')
  events=[json.loads(x) for x in log.read_text('utf-8').splitlines() if x.strip()] if log.is_file() else []
  if not events or events[0].get('event')!='SCOPE_V2_INSTALL':
   problems.append({'script':str(script),'reason':'SCOPE_INSTALL_EVENT_ABSENT'});continue
  head=events[0];policy=object.__new__(scope_module.Policy)
  policy.source=Path(envelope['source_root']).resolve();policy.frozen=Path(envelope['frozen_root']).resolve()
  policy.out=out.resolve();policy.entry=SG/'product_entry241.py';policy.experiment=SG.resolve();policy.log=log.resolve()
  policy.trusted_files={Path(p).resolve() for p in head['trusted_files']}
  policy.library_roots={Path(p).resolve() for p in head['library_roots']}
  required={SG/name for name in ('product_entry241.py','generated_scope_v2_241.py','winjob241.py','contracts241.py','supervision_classification241.py')}
  required.update(Path(envelope['harness']).resolve()/name for name in ('sitecustomize.py','qualify.py','qualification_plugin.py'))
  if policy.trusted_files!=required or any(scope_module.inside(p,SG.resolve()) for p in policy.library_roots):
   problems.append({'script':str(script),'reason':'TRUSTED_FILES_OR_LIBRARY_ROOT_CHANGED'})
  open_events=[e for e in events if e.get('event')=='open'];denied=[];allowed_sensitive=[]
  for e in open_events:
   if e.get('reason')=='OS_NULL_DEVICE':continue
   if e.get('path'):
    path=Path(e['path']).resolve();allowed,reason=policy.write_decision(path) if e['write'] else policy.read_decision(path)
    if e['allowed']!=allowed or e['reason']!=reason:
     problems.append({'script':str(script),'reason':'OPEN_DECISION_NOT_RECONCILED','event':e})
    if not e['allowed']:denied.append(e)
    if e['allowed'] and not e['write'] and any(mark in str(path) for mark in ('external_once_private','immutable_selection','selection_before_private','stage_ledger.jsonl')):
     allowed_sensitive.append(e)
   elif e.get('allowed') is not False:problems.append({'script':str(script),'reason':'UNRESOLVED_OPEN_ALLOWED','event':e})
  for e in events[1:]:
   event=e.get('event')
   if event=='open':continue
   if event in ('os.listdir','os.scandir','os.chdir') and e.get('path'):
    allowed,reason=policy.read_decision(Path(e['path']).resolve())
   elif event in ('os.remove','os.rmdir','os.mkdir','os.rename','os.chmod','os.truncate','os.utime','os.chown','os.lchown') and e.get('path'):
    allowed,reason=policy.mutation_decision(event,Path(e['path']).resolve())
   elif event in ('os.link','os.symlink'):
    allowed,reason=False,'LINK_OPERATION_FORBIDDEN'
   elif event in ('subprocess.Popen','os.system','socket.connect','socket.bind'):
    allowed,reason=False,'PROCESS_OR_NETWORK_BOUNDARY'
   elif e.get('path_or_descriptor'):
    allowed,reason=False,e['reason']
   else:
    problems.append({'script':str(script),'reason':'UNRECOGNIZED_PYTHON_SCOPE_EVENT','event':e});continue
   if e.get('allowed')!=allowed or e.get('reason')!=reason:
    problems.append({'script':str(script),'reason':'NONOPEN_DECISION_NOT_RECONCILED','event':e})
  if allowed_sensitive:problems.append({'script':str(script),'reason':'SENSITIVE_ARTIFACT_READ_ALLOWED','events':allowed_sensitive})
  code=script.read_text('utf-8-sig');tree=ast.parse(code);fs=[];literal=[]
  for n in ast.walk(tree):
   if isinstance(n,ast.Call) and getattr(n.func,'attr',getattr(n.func,'id',None)) in ('open','read_text','read_bytes','walk','glob','rglob','exec','eval','run_path'):
    fs.append({'line':n.lineno,'call':ast.get_source_segment(code,n)})
   if isinstance(n,ast.Constant) and isinstance(n.value,str) and any(mark in n.value for mark in ('external_once_private','immutable_selection','stage_ledger.jsonl')):
    literal.append({'line':n.lineno,'literal':n.value})
  rows.append({'script':str(script),'script_sha256':sha(script),'scope_event_log':str(log),'scope_event_log_sha256':sha(log),
   'actual_python_open_events':len(open_events),'allowed_open_events':sum(e['allowed'] for e in open_events),'denied_open_events':denied,
   'all_recorded_nonopen_python_scope_events_reconciled':True,'actual_recorded_python_scope_events':len(events)-1,
   'allowed_sensitive_artifact_read_events':allowed_sensitive,'direct_fs_dynamic_calls':fs,'sensitive_artifact_literals':literal,
   'exact_trusted_files_and_recorded_library_roots_reconciled':True})
 value={'schema':'Agentless241-ScopeV2-closed-case-Python-information-admission/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'task_id':task,'scope_version':2,'status':'PASS_OBSERVED_PYTHON_SCOPE_EVENTS' if not problems and rows else 'UNKNOWN_SCOPE_EVENT_ADMISSION',
  'executed_generated_scripts':rows,'problems':problems,'actual_python_open_events':sum(r['actual_python_open_events'] for r in rows),
  'allowed_sensitive_artifact_read_events':sum(len(r['allowed_sensitive_artifact_read_events']) for r in rows),
  'no_whole_experiment_directory_read_root_in_actual_headers':not problems,
  'scope1_two_case_unknown_never_backfilled':True,'private_contents_read_by_auditor':0,
  'coverage_limit':'Actual Python audit-hook events and inspected generated code only; not all native C reads or arbitrary malicious-code bypasses',
  'closed_actor_required':True,'source':str(SG/'generated_scope_v2_241.py'),'source_sha256':sha(SG/'generated_scope_v2_241.py')}
 save(SG/'candidate'/task/'INFORMATION_ADMISSION_SCOPE_V2_241.json',value,scope=SG)
 print(canonical({k:value[k] for k in ('task_id','status','actual_python_open_events','allowed_sensitive_artifact_read_events')}))
if __name__=='__main__':main()

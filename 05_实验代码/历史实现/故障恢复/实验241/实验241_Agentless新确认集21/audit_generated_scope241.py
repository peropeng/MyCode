"""Inspect generated code and existing guard evidence, never private contents."""
import ast,datetime
from contracts241 import *

TASKS=('dask__dask-9378','getmoto__moto-5072')
ARTIFACT_MARKERS=('external_once_private','immutable_selection','selection_before_private','stage_ledger.jsonl','result.json','/llm/','\\llm\\')

def script_audit(path):
 source=path.read_text('utf-8-sig');tree=ast.parse(source);calls=[];imports=[];literal=[]
 for n in ast.walk(tree):
  if isinstance(n,(ast.Import,ast.ImportFrom)):
   imports.append({'line':n.lineno,'module':n.module if isinstance(n,ast.ImportFrom) else [a.name for a in n.names]})
  if isinstance(n,ast.Call):
   name=getattr(n.func,'attr',getattr(n.func,'id',None))
   if name in ('open','read','read_text','read_bytes','listdir','scandir','walk','glob','rglob','getenv','environ','eval','exec','run_path'):
    calls.append({'line':n.lineno,'call':ast.get_source_segment(source,n)})
  if isinstance(n,ast.Constant) and isinstance(n.value,str) and any(k in n.value for k in ARTIFACT_MARKERS):
   literal.append({'line':n.lineno,'literal':n.value})
 return {'path':str(path),'sha256':sha(path),'imports':imports,'filesystem_or_dynamic_calls':calls,
  'sensitive_artifact_literal_references':literal,'static_no_literal_reference_does_not_prove_no_dynamic_read':True}

def main():
 cases=[]
 for task in TASKS:
  flow=HERE/'runs'/task/METHOD;stages=[json.loads(x) for x in (flow/'stage_ledger.jsonl').read_text('utf-8').splitlines() if x.strip()]
  physical=[script_audit(p) for p in sorted((flow/'generated_native').glob('*/generated_test.py'))]
  originals=[v['evidence'] for v in stages if v['stage']=='original_reproduction']
  original_rows=[]
  for i,row in enumerate(originals):
   code=row.get('code','');h=hashlib.sha256(code.encode()).hexdigest()
   original_rows.append({'sample':row.get('sample',i),'generated_code_sha256':h,'generated_code_nonempty':bool(code),
    'matching_executed_script_paths':[r['path'] for r in physical if r['sha256']==h]})
  guard_events={};event_counts={}
  for p in sorted(flow.glob('generated_native/*/guard_events.jsonl')):
   events=[json.loads(x) for x in p.read_text('utf-8').splitlines() if x.strip()];guard_events[str(p)]=events
   for event in events:event_counts[event.get('event','missing')]=event_counts.get(event.get('event','missing'),0)+1
  envelope_paths=list(flow.glob('generated_native/*/entry_envelope.json'))
  certificates=[]
  for p in envelope_paths:
   env=read(p);certificates.append({'envelope':str(p),'mode':env['mode'],'guard':env['harness_guard'],
    'guard_sha256':sha(env['harness_guard']),'entry_sha256':sha(HERE/'product_entry241.py'),
    'output':env['output'],'source':env['source_root'],'frozen':env['frozen_root']})
  suspicious=[r for r in physical if r['sensitive_artifact_literal_references']]
  cases.append({'task_id':task,'author_reproduction_model_samples':len(originals),'original_samples':original_rows,
   'executed_generated_script_count':len(physical),'executed_generated_scripts':physical,'guard_events':guard_events,
   'guard_event_counts':event_counts,'native_envelopes':certificates,
   'actual_sensitive_read_events_detected':[],
   'all_filesystem_read_attempts_audited':False,'actual_private_selected_patch_or_prior_response_read_status':'UNKNOWN_NO_ALLOWED_OPEN_EVENT_COVERAGE',
   'static_sensitive_artifact_reference_scripts':suspicious,
   'current_completed_composite_test_outcomes_retained_separately':True,
   'not_relabeling_scope_unknown_as_algorithm_failure_or_no_read':True})
 value={'schema':'Agentless241-generated-read-scope-retrospective-audit/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'cases':cases,'old_entry_source':str(HERE/'product_entry241.py'),'old_entry_sha256':sha(HERE/'product_entry241.py'),
  'actual_weakness':'generated read allow list includes HERE, which contains other cases private results, selected patches and raw responses',
  'old_guard_events_log_only_refused_operations_not_all_allowed_reads':True,
  'hard_isolation_established_for_old_two_cases':False,
  'actual_sensitive_access_observed':False,'absence_of_actual_sensitive_access_proven':False,
  'overall_access_status':'UNKNOWN_EVENT_COVERAGE_INCOMPLETE',
  'old_raw_results_sources_seals_grants_preserved':True,'scientific_reruns':0,'private_contents_read_by_auditor':0,
  'next_index_science_paused_pending_new_scope_deployment':True}
 save(HERE/'GENERATED_SCOPE_AUDIT241.json',value)
 print(canonical({'cases':[{k:c[k] for k in ('task_id','author_reproduction_model_samples','executed_generated_script_count',
  'guard_event_counts','actual_private_selected_patch_or_prior_response_read_status')} for c in cases],
  'hard_isolation_established':False,'overall_access_status':value['overall_access_status']}))
if __name__=='__main__':main()

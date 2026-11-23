"""Freeze public coordinates, fit-ID gates, old cached references and five rules."""
from common import *

def prepare():
 require_time(new_long_task=True)
 if sha(E/'approved_plan.json')!=PLAN_SHA:raise RuntimeError('Frozen156 plan changed')
 plan=read(E/'approved_plan.json');parents=plan['parents'];p155=read(E155/'protocol.json');p153=read(E153/'protocol.json')
 for folder,name,key in [(E153,'main_decision_packet.json','packet153_sha256'),(E154,'main_decision_packet.json','packet154_sha256'),
  (E155,'main_decision_packet.json','packet155_sha256'),(E155,'protocol.json','protocol155_sha256'),
  (E155,'training/all_models_sealed.json','modelseal155_sha256'),(E155,'results/all_predictions_sealed.json','predseal155_sha256')]:
  if sha(folder/name)!=parents[key]:raise RuntimeError('Frozen parent changed:'+str(folder/name))
 # Weight/embedding bytes are not read by this entirely analytical experiment.
 # Their immutable manifests are protected; prior output/ledger/public bytes are checked directly.
 guarded={q:h for q,h in p155['protected_old_files_sha256'].items() if Path(q).suffix.lower() in ('.json','.jsonl','.py','.toml')}
 model_manifests={}
 for folder in (E153,E154,E155):
  if read(folder/'final_execution_audit.json')['status']!='PASS':raise RuntimeError('Complete valid parent only')
  for name in ('protocol.json','main_decision_packet.json','comparison.json','compact_summary.json','final_execution_audit.json','resource_audit.json','initialization_audit.json','training/all_models_sealed.json','results/all_predictions_sealed.json'):
   guarded[str(folder/name)]=sha(folder/name)
  guarded.update(read(folder/'results/all_predictions_sealed.json')['files'])
  model_manifests[str(folder/'training/all_models_sealed.json')]=sha(folder/'training/all_models_sealed.json')
 check_hashes(guarded)
 source_path=E134/'data/public_records.json';AF_path=E138/'data/public_records.json'
 source=read(source_path)['records'];af=read(AF_path)['records'];by={r['sample_id']:r for r in source};afby={r['sample_id']:r for r in af}
 fits=p153['source_ids']['train'];vals=p153['source_ids']['validation']
 if (len(fits),len(vals),len(af),len(afby),len({r['task_group'] for r in af}))!=(492,122,731,731,716):raise RuntimeError('Fixed original denominators changed')
 if set(fits)&set(vals) or not set(fits+vals)<=set(by):raise RuntimeError('Original source fit/val gate mismatch')
 AF=[r for r in p153['af_schedule'] if r['arm']=='AB_GLOBAL']
 if len(AF)!=15 or set(r['seed'] for r in AF)!=set(AF_SEEDS):raise RuntimeError('Exactly original3 schedules and15 outer folds')
 for seed in AF_SEEDS:
  ids=[s for r in AF if r['seed']==seed for s in r['held_ids']]
  if len(ids)!=731 or len(set(ids))!=731:raise RuntimeError('Original3 OOF schedules must cover every record once')
 for row in AF:
  if set(row['refit_ids'])&set(row['held_ids']) or {afby[s]['task_group'] for s in row['refit_ids']}&{afby[s]['task_group'] for s in row['held_ids']}:raise RuntimeError('Complete held groups excluded from prior fits')
 table_paths=[str(E/'fits/source'/(c+'.json')) for c in PRIORS]
 table_paths += [str(E/'fits/AF'/c/f"{r['seed']}_{r['outer']}.json") for c in PRIORS for r in AF]
 input_files={str(E/'approved_plan.json'):sha(E/'approved_plan.json'),str(source_path):sha(source_path),str(AF_path):sha(AF_path),
  str(E134/'data/selected_train_labels.private.json'):sha(E134/'data/selected_train_labels.private.json'),str(E138/'data/development_labels.private.json'):sha(E138/'data/development_labels.private.json')}
 for spec in p155['target_cohorts'].values():
  input_files[spec['public_records']]=sha(spec['public_records']);input_files[spec['label_source']]=spec['label_source_sha256']
 p={'at_utc':now(),'schema':'Exp156-five-fixed-analytic-rules-locked-neural-cache/1.0','experiment':'Exp156','approved_plan_sha256':PLAN_SHA,
  'primary':PRIMARY,'controls':list(CONTROLS),'priors':list(PRIORS),'locked_model_views':list(VIEWS),'view_slugs':VIEW_SLUGS,
  'source_public_records':str(source_path),'source_fit_ids':fits,'source_validation_ids':vals,
  'source_training_label_source':{'path':str(E134/'data/selected_train_labels.private.json'),'key':'target_ordinal','schema':'labels list sample_id→target_ordinal'},
  'target_cohorts':p155['target_cohorts'],'AF_public_records':str(AF_path),'AF_label_source':str(E138/'data/development_labels.private.json'),
  'AF_schedule':AF,'AF_seeds':list(AF_SEEDS),'fit_table_paths':table_paths,'expected_analytic_fit_tables':32,
  'baseline_parameters':{'relative_bins':10,'smoothing':1,'group_record_fit_weight':'1 / records in current fit task group','tie':'descending exact candidate probability then original ordinal ascending; deterministic rules keep their explicit complete order'},
  'rule_sources_sha256':{str(E/n):sha(E/n) for n in ('common.py','rules156.py','prepare156.py','predict156.py')},
  'inputs':input_files,'protected_old_files_sha256':guarded,'unchanged_neural_weight_manifests_sha256':model_manifests,
  'no_neural_weight_or_embedding_deserialization_or_bytes_used_by_rules':True,'neural_weight_manifests_protected_instead_of_loading_weight_bytes':True,
  'model_seal_rule':'No new neural model or training; all32 count fits recorded with fit-ID gates before control inference',
  'prediction_seal_rule':'All18816 unique new rankings/61JSON files sealed before evaluator Gold/old output decode',
  'expected_new_ranker_outputs':18816,'source_new_outputs':10775,'AF_new_outputs':8041,'expected_prediction_files':61,
  'new_optimization_training':0,'new_neural_models':0,'new_neural_forward':0,'new_encoder':0,'new_API':0,'new_downloads':0,'new_Gold':0,'new_independent_tasks':0,'fee_CNY':'0','deadline':DEADLINE}
 write_new(E/'protocol.json',p)
 s={'at_utc':now(),'experiment':'Exp156','phase':'PROTOCOL_SEALED','owner_chat_id':'01a10cf5-0721-7002-83b8-766a60389490','source_chat_id':'01a0b043-b3d8-77f0-be9d-5eee0fed25b0',
  'worktree':str(W),'branch':'exp/1007-exp156-position-diagnostics','approved_plan_sha256':PLAN_SHA,'plan_fully_read':True,'context_window_id':'01a112bb-e049-7fb2-a809-63217141e900',
  'deadline_beijing':'2026-10-07T10:00:00+08:00','expected_new_ranker_outputs':18816,'expected_analytic_fit_tables':32,'ETA_initial_total_minutes':[20,40],
  'counters':{'new_analytic_count_fit_tables':0,'new_ranker_outputs':0,'new_optimization_training':0,'new_neural_models':0,'new_model_forward':0,'new_encoder':0,'new_API':0,'new_downloads':0,'new_Gold':0,'new_independent_tasks':0,'fee_CNY':'0'},
  'science_owner':'root','next':'Small artificial rule checks; predict156.py32 count tables and18816rankings→allseals→evaluate→diagnostics→finalize'}
 write_new(E/'checkpoint.json',s);write_new(E/'execution_state.json',s)
 print(canonical({'Exp156':'protocol_sealed','fit_tables':32,'expected_outputs':18816,'protected_old_public_prediction_ledger_code_files':len(guarded),'new_neural_forward':0}),flush=True)
if __name__=='__main__':prepare()

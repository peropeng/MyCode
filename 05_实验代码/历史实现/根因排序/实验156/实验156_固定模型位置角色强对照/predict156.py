"""32 exact analytical fit tables, then all18816 control ranks before scoring."""
from fractions import Fraction
from common import *
from rules156 import fit_table,predict_rule

def save(path,value):
 if path.exists():
  if read(path)!=value:raise RuntimeError('Existing analytic prediction changed:'+str(path))
 else:write_new(path,value)

def verify_protocol():
 p=read(E/'protocol.json')
 if p['approved_plan_sha256']!=PLAN_SHA or tuple(p['controls'])!=CONTROLS:raise RuntimeError('Frozen rule protocol changed')
 check_hashes(p['rule_sources_sha256']);check_hashes(p['inputs']);check_hashes(p['protected_old_files_sha256'])
 return p

def run():
 require_time(new_long_task=True);p=verify_protocol()
 if read(E/'fixtures/rule_test_receipt.json')['status']!='PASS':raise RuntimeError('Necessary artificial rule checks failed')
 source=read(p['source_public_records'])['records'];by={r['sample_id']:r for r in source}
 allowed=set(p['source_fit_ids']);label_rows=read(p['source_training_label_source']['path'])['labels']
 # Select IDs before reading the target value; no source122 validation labels enter a prior.
 labels={r['sample_id']:r[p['source_training_label_source']['key']] for r in label_rows if r['sample_id'] in allowed}
 if set(labels)!=allowed:raise RuntimeError('Source492 fit-only label gate mismatch')
 tables={};receipts=[]
 for control in PRIORS:
  path=E/'fits/source'/(control+'.json')
  if path.exists():table=read(path)
  else:
   table=fit_table(control,p['source_fit_ids'],p['source_validation_ids'],by,labels,{'suite':'source','label_source':p['source_training_label_source']['path'],'label_source_sha256':sha(p['source_training_label_source']['path']),'source122_validation_label_values_consumed':0})
   write_new(path,table)
  if table['fit_ids']!=p['source_fit_ids'] or table['held_ids']!=p['source_validation_ids']:raise RuntimeError('Source fit table gate changed')
  tables['source',control]=table;receipts.append({'path':str(path),'sha256':sha(path),'suite':'source','control':control,'fit_ids_sha256':table['fit_ids_sha256'],'held_ids_sha256':table['held_ids_sha256'],'fit_record_count':table['fit_record_count'],'fit_group_count':table['fit_group_count']})
 del labels,label_rows,by,source
 af=read(p['AF_public_records'])['records'];afby={r['sample_id']:r for r in af};af_ids=[r['sample_id'] for r in af]
 all_labels=read(p['AF_label_source'])['labels']
 for control in PRIORS:
  for row in p['AF_schedule']:
   require_time();path=E/'fits/AF'/control/f"{row['seed']}_{row['outer']}.json"
   if path.exists():table=read(path)
   else:
    gate=set(row['refit_ids']);fit_labels={sid:all_labels[sid] for sid in row['refit_ids'] if sid in gate}
    table=fit_table(control,row['refit_ids'],row['held_ids'],afby,fit_labels,{'suite':'AF','seed':row['seed'],'outer':row['outer'],'original_manifest_sha256':row['original_manifest_sha256'],'label_source':p['AF_label_source'],'label_source_sha256':sha(p['AF_label_source']),'fit_groups':row['refit_groups'],'held_groups':row['held_groups'],'shared_AF_label_file_parsed':True,'fit_label_values_gated_before_statistics':True})
    write_new(path,table)
   if table['fit_ids']!=row['refit_ids'] or table['held_ids']!=row['held_ids']:raise RuntimeError('AF fit table gate changed')
   tables[control,row['seed'],row['outer']]=table;receipts.append({'path':str(path),'sha256':sha(path),'suite':'AF','control':control,'seed':row['seed'],'outer':row['outer'],'fit_ids_sha256':table['fit_ids_sha256'],'held_ids_sha256':table['held_ids_sha256'],'fit_record_count':table['fit_record_count'],'fit_group_count':table['fit_group_count']})
 del all_labels
 if len(receipts)!=32 or {r['path'] for r in receipts}!=set(p['fit_table_paths']):raise RuntimeError('All32 count fits required')
 receipt={'at_utc':now(),'status':'PASS','analytic_count_fit_tables':32,'tables':receipts,'all32_fit_ID_gates':True,'held_labels_consumed_by_corresponding_table':0,'source122_validation_labels_used':0,'fit_group_weight_total_equals_group_count':True,'new_optimization_training':0,'new_neural_models':0,'new_neural_forward':0,'AF_label_access':'Shared731 label file parsed; each table only looks up refit_ids; currentheld values never consumed by that table','protocol_sha256':sha(E/'protocol.json')}
 save(E/'fit_isolation_receipt.json',receipt)
 status('ALL32_ANALYTIC_FITS_SEALED',new_analytic_count_fit_tables=32,next='Generate all18816 control outputs before evaluator target/oldscore decode')
 files={};count=0;source_files={};AF_files={};cohorts={}
 for cohort in COHORTS:
  spec=p['target_cohorts'][cohort];public=read(spec['public_records'])['records'];ids=spec['sample_ids']
  if [r['sample_id'] for r in public]!=ids or len(ids)!=spec['n']:raise RuntimeError('Complete original source order required')
  for control in CONTROLS:
   require_time();table=tables.get(('source',control));out={r['sample_id']:predict_rule(control,r,table) for r in public}
   path=control_prediction_path(cohort,control)
   save(path,{'predictions':out,'cohort':cohort,'control':control,'protocol_sha256':sha(E/'protocol.json'),'target_labels_joined':0,'fit_table_sha256':sha(E/'fits/source'/(control+'.json')) if table else None,'rule_inputs':'Candidate count, original ordinal and exact public role only; no content/thought/action/embedding/weights'})
   source_files[str(path)]=sha(path);files[str(path)]=sha(path);count+=len(ids)
   status('PREDICTIONS_RUNNING',current_cohort=cohort,current_control=control,new_ranker_outputs=count,target_label_values_joined=0)
  cohorts[cohort]={'n':len(ids),'outputs':5*len(ids),'sample_ids':ids}
 if count!=10775:raise RuntimeError('Exact10775 source outputs required')
 save(E/'results/source_predictions_sealed.json',{'at_utc':now(),'files':source_files,'outputs':10775,'cohorts':cohorts,'protocol_sha256':sha(E/'protocol.json'),'fit_receipt_sha256':sha(E/'fit_isolation_receipt.json'),'target_labels_joined':0})
 for control in CONTROLS[:3]:
  out={r['sample_id']:predict_rule(control,r) for r in af};path=control_prediction_path('AF',control)
  save(path,{'predictions':out,'cohort':'AF','control':control,'protocol_sha256':sha(E/'protocol.json'),'target_labels_joined':0,'generated_once_not_per_fold':True})
  AF_files[str(path)]=sha(path);files[str(path)]=sha(path);count+=len(af_ids)
 for control in PRIORS:
  seed_outputs=[]
  for seed in AF_SEEDS:
   joined={}
   for row in p['AF_schedule']:
    if row['seed']!=seed:continue
    require_time();table=tables[control,seed,row['outer']];out={sid:predict_rule(control,afby[sid],table) for sid in row['held_ids']}
    if set(joined)&set(out):raise RuntimeError('OOF duplicate record')
    joined.update(out);path=E/'results/AF/folds'/control/f"{seed}_{row['outer']}.json"
    save(path,{'predictions':out,'cohort':'AF','control':control,'seed':seed,'outer':row['outer'],'protocol_sha256':sha(E/'protocol.json'),'fit_table_sha256':sha(E/'fits/AF'/control/f"{seed}_{row['outer']}.json"),'held_ids_sha256':digest(row['held_ids']),'target_labels_joined':0})
    AF_files[str(path)]=sha(path);files[str(path)]=sha(path);count+=len(out)
   if set(joined)!=set(af_ids):raise RuntimeError('Complete731 OOF ranks per original schedule required')
   path=control_prediction_path('AF',control,seed)
   save(path,{'predictions':joined,'cohort':'AF','control':control,'seed':seed,'protocol_sha256':sha(E/'protocol.json'),'exactly_one_OOF_per_record':True,'joined_entries_not_new_outputs':731,'target_labels_joined':0})
   AF_files[str(path)]=sha(path);files[str(path)]=sha(path);seed_outputs.append(joined)
  averaged={}
  for sid in af_ids:
   exact=[]
   for i in range(len(afby[sid]['turns'])):
    exact.append(sum((Fraction(o[sid]['probability_exact'][i]['numerator'],o[sid]['probability_exact'][i]['denominator']) for o in seed_outputs),Fraction())/3)
   # Exact arithmetic for the specified probability mean; float output is its display representation.
   probabilities=[float(v) for v in exact]
   order=sorted(range(len(exact)),key=lambda i:(-exact[i],i))
   averaged[sid]={'probabilities':probabilities,'probability_exact':[{'numerator':v.numerator,'denominator':v.denominator} for v in exact],'order':order,'chosen_step':order[0],'predicted_role':afby[sid]['turns'][order[0]]['role'],'valid':True,'native_complete_ranking':True,'original_zero_based_ordinals':True,'candidate_count':len(exact)}
  path=control_prediction_path('AF',control)
  save(path,{'predictions':averaged,'cohort':'AF','control':control,'seeds':list(AF_SEEDS),'all3_fixed_schedules_retained':True,'protocol_sha256':sha(E/'protocol.json'),'target_labels_joined':0,'shared_by_both155_blocks_without_new_outputs':True})
  AF_files[str(path)]=sha(path);files[str(path)]=sha(path);count+=len(af_ids)
 if count!=18816 or len(files)!=61:raise RuntimeError('Exactly18816 unique ranks/61files required')
 save(E/'results/AF_predictions_sealed.json',{'at_utc':now(),'files':AF_files,'outputs':8041,'records':731,'groups':716,'native_deterministic_rule_outputs':2193,'native_prior_OOF_outputs':4386,'prior_ensemble_outputs':1462,'OOF_join_JSON_copy_entries_not_new_outputs':4386,'protocol_sha256':sha(E/'protocol.json'),'target_labels_joined':0})
 check_hashes(p['protected_old_files_sha256'])
 save(E/'results/all_predictions_sealed.json',{'at_utc':now(),'all_fixed_outputs_sealed':True,'outputs':18816,'source_outputs':10775,'AF_outputs':8041,'files':files,'prediction_files':61,'analytic_fit_tables':32,'protocol_sha256':sha(E/'protocol.json'),'fit_receipt_sha256':sha(E/'fit_isolation_receipt.json'),'source_seal_sha256':sha(E/'results/source_predictions_sealed.json'),'AF_seal_sha256':sha(E/'results/AF_predictions_sealed.json'),'target_labels_joined':0,'new_neural_forward':0})
 status('ALL_PREDICTIONS_SEALED',new_analytic_count_fit_tables=32,new_ranker_outputs=18816,next='evaluate156.py then diagnostics156.py thenfinalize156.py')
 print(canonical({'Exp156':'all_analytic_predictions_sealed','count_fit_tables':32,'new_outputs':18816,'JSON_files':61,'neural_forward':0}),flush=True)
if __name__=='__main__':run()

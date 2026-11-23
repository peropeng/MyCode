"""Pure saved-artifact dimension/provenance audit; scientific interpretation stays with root."""
from common161 import *
from evaluate161 import CODE_FILES,demand

def run():
 require_time();seal=enter_score_phase();codes=read(E/'evaluation_code_seal.json');receipt=read(E/'score_receipt.json');join=read(E/'score_join_started.json')
 metric=read(E/'stratified_cached_metrics.json');pairs=read(E/'pairedcounts.json');packet=read(E/'main_decision_packet.json');bins=read(E/'bin_membership.json');texts=read(E/'public_texts.json')
 score_reads=read(E/'score_read_manifest.json');lexical_counts=read(E/'lexical_counts.json');errors=[]
 def check(ok,name):
  if not ok:errors.append(name)
 check(sha(E/'approved_plan.json')==PLAN_SHA,'approved_plan_hash')
 check(codes['sources']=={str(E/name):sha(E/name) for name in CODE_FILES},'frozen_evaluation_sources')
 sh=sha(E/'text_proximity_sealed.json');ch=sha(E/'evaluation_code_seal.json')
 check(receipt['status']=='PASS' and receipt['text_proximity_seal_sha256']==join['text_proximity_seal_sha256']==packet['text_proximity_seal_sha256']==sh,'text_seal_score_packet_chain')
 check(receipt['evaluation_code_seal_sha256']==join['evaluation_code_seal_sha256']==ch,'evaluation_code_join_receipt_chain')
 check((E/'text_proximity_sealed.json').stat().st_mtime_ns<(E/'evaluation_code_seal.json').stat().st_mtime_ns
       <=(E/'score_join_started.json').stat().st_mtime_ns<(E/'score_receipt.json').stat().st_mtime_ns,'all_public_text_nearest_bins_cases_before_cached_Gold_scores')
 check(all(Path(path).stat().st_mtime_ns<(E/'text_proximity_sealed.json').stat().st_mtime_ns for path in seal['artifacts']),'all_lexical_artifacts_precede_text_seal')
 allow_score_inputs(receipt['source_prediction_files']);check_hashes({path:ref['sha256'] for path,ref in receipt['source_prediction_files'].items()})
 check_hashes(receipt['historical_reference_metadata_verbatim_reference'])
 check(receipt['cached_Gold_sha256']==sha(E160/'evaluation_cached_Gold.json') and receipt['parent160_frozen_input_manifest_sha256']==sha(E160/'frozen_input_manifest.json'),'unchanged_parent160_cached_gold_manifest')
 expected_metric={(c,p,b,m) for c in COHORTS for p in PARTITIONS for b in BINS for m in METHODS}
 expected_pairs={(c,p,b,m) for c in COHORTS for p in PARTITIONS for b in BINS for m in METHODS[1:]}
 mby={(r['cohort'],r['partition'],r['bin'],r['method']):r for r in metric['rows']};pby={(r['cohort'],r['partition'],r['bin'],r['other']):r for r in pairs['rows']}
 full={(r['cohort'],r['partition'],r['method']):r for r in metric['full_scope_parent_matches']}
 check(len(metric['rows'])==len(mby)==400 and set(mby)==expected_metric,'complete400rows_with_all_empty_bins')
 check(len(pairs['rows'])==len(pby)==320 and set(pby)==expected_pairs,'complete320paired_rows')
 check(len(full)==len(metric['full_scope_parent_matches'])==80,'complete80full_scope_parent_matches')
 for cohort in COHORTS:
  ids=texts['cohorts'][cohort]['ids'];check(len(ids)==texts['cohorts'][cohort]['n'],'full_original_cohort:'+cohort)
  for partition in PARTITIONS:
   bmap=bins['cohorts'][cohort]['partitions'][partition]['fit'];allids=[sid for b in BINS for sid in bmap[b]]
   check(len(allids)==len(set(allids))==len(ids) and set(allids)==set(ids),'bins_complete_original_denominator:'+cohort+'/'+partition)
   for method in METHODS:
    whole=full[cohort,partition,method];rows=[mby[cohort,partition,b,method] for b in BINS]
    check(sum(r['n'] for r in rows)==whole['n']==len(ids) and sum(r['hits'] for r in rows)==whole['hits'] and sum(r['invalid'] for r in rows)==whole['invalid'],'partition_metric_counts:'+cohort+'/'+partition+'/'+method)
    for key in ('Top1','MRR','Top3'):
     value=math.fsum(r[key]*r['n'] for r in rows if r['n'])/len(ids)
     check(math.isclose(value,whole[key],abs_tol=1e-12,rel_tol=0.),'partition_weighted_rate:'+cohort+'/'+partition+'/'+method+'/'+key)
    for row in rows:
     check(row['n']==len(bmap[row['bin']]) and row['empty_bin']==(row['n']==0),'empty_and_nonempty_bin_identity')
     if row['n']==0:check(row['hits']==row['invalid']==0 and all(row[k] is None for k in ('Top1','MRR','Top3')),'empty_bin0_NA_retained')
   for b in BINS:
    for method in METHODS[1:]:
     row=pby[cohort,partition,b,method];g=mby[cohort,partition,b,'G'];other=mby[cohort,partition,b,method]
     check(row['n']==g['n']==other['n'] and row['G_hits']==g['hits'] and row['other_hits']==other['hits'],'paired_scope_and_hits')
     check(row['G_only_correct']-row['other_only_correct']==g['hits']-other['hits'] and sum(row[k] for k in ('G_only_correct','other_only_correct','both_correct','both_wrong'))==row['n'],'paired_cell_accounting')
     if row['n']==0:check(all(row[k] is None for k in ('Top1_difference','MRR_difference','Top3_difference')),'empty_paired_rates_NA')
 for filename,rows in [('stratified_cached_metrics.csv',metric['rows']),('pairedcounts.csv',pairs['rows'])]:
  with (E/filename).open(encoding='utf-8-sig',newline='') as stream:saved=list(csv.DictReader(stream))
  check(len(saved)==len(rows),'CSV_row_count:'+filename)
 check(receipt['cases_public_raw_task_recheck']['count']<=24 and all(r['raw_task_recomputed'] for r in receipt['cases_public_raw_task_recheck']['cases']),'all_fixed_public_cases_raw_task_rechecked')
 check(receipt['preserve_old_statistical_families_and_FAILs_without_changes'] and receipt['preserve156_exact_zero_original_definition'],'original_old_statistics_FAILs_exact_zero_preserved')
 check(score_reads['all_prediction_JSON_files_read_once'] and score_reads['source_ensemble_prediction_files']==len(receipt['source_prediction_files'])==80,'80existing_ensemble_prediction_files_read_once')
 check(all(r['phase']=='SCORED_CACHE' for path,r in score_reads['inputs'].items() if path.startswith(str(E160)) or path in receipt['source_prediction_files']),'Gold_score_inputs_only_after_verified_public_text_seal')
 resource={'at_utc':now(),'experiment':'Exp161','public_task_texts':2769,'source_pool_metadata_texts':614,'historical_target_tasks_diagnosed':2155,'exact_pair_candidates':1323170,
           'actual_lexical_counts_saved':lexical_counts,'not_multiplied_by4_partitions5methods_or400rows':True,'cached_existing_ensemble_files':80,'cached_full_scope_rows':80,
           'stratified_rows':400,'paired_rows':320,'fixed_public_case_rechecks':receipt['cases_public_raw_task_recheck']['count'],'initial_public_text_lexical_transform_calls':2769,'additional_case_direct_lexical_transform_calls':2*receipt['cases_public_raw_task_recheck']['count'],
           'new_training':0,'new_models':0,'new_model_loads':0,'new_model_constructors':0,'new_forwards':0,'new_ranker_outputs':0,'new_derived_ranking_views':0,
           'new_neural_encoder_texts':0,'new_neural_encoder_batches':0,'new_native_test_processes':0,'new_recovery_candidates':0,'new_API':0,'new_downloads':0,'new_Gold':0,'new_independent_tasks':0,
           'new_p_CI_bootstrap':0,'fee_CNY':'0','score_read_manifest_sha256':sha(E/'score_read_manifest.json'),'text_proximity_seal_sha256':sh}
 write_new(E/'resource_audit.json',resource)
 packet.update(status='PASS' if not errors else 'FAIL',final_execution_audit_status='PASS' if not errors else 'FAIL',all_empty_bins_and_original_full_denominators_kept=not errors,
               all_public_case_checks_and_parent_metric_reproduction_PASS=not errors,resource_audit_sha256=sha(E/'resource_audit.json'),scientific_interpretation_owner='root')
 atomic(E/'main_decision_packet.json',packet)
 compact={k:v for k,v in packet.items() if k!='cached_reference_paths_sha256'};compact.update(errors=errors)
 write_new(E/'compact_summary.json',compact)
 names=('stratified_cached_metrics.json','stratified_cached_metrics.csv','pairedcounts.json','pairedcounts.csv','score_receipt.json','score_read_manifest.json','resource_audit.json','main_decision_packet.json','compact_summary.json')
 write_new(E/'final_execution_audit.json',{'at_utc':now(),'experiment':'Exp161','status':'PASS' if not errors else 'FAIL','errors':errors,'text_proximity_seal_sha256':sh,
           'evaluation_code_seal_sha256':ch,'all400metric320paired80parentmatches_and_fixed_publiccases_verified':not errors,'text_seal_precedes_all_cached_Gold_score_joins':not errors,
           'no_new_scientific_statistics_predictions_or_independent_tasks':True,'no_automatic_contamination_leakage_or_semantic_duplicate_conclusion':True,
           'artifacts':{str(E/name):sha(E/name) for name in names}})
 status('EXP161_COMPLETE_PASS' if not errors else 'EXP161_FINAL_AUDIT_FAIL_STOP',stratified_rows=400,paired_rows=320,new_models_or_predictions=0,fee_CNY='0',next='root interprets lexical scope and pre-score cases')
 if errors:raise RuntimeError('EXP161_FINAL_AUDIT_FAILED:'+','.join(errors))
 print(canonical({'Exp161_final':'PASS','metric_rows':400,'paired_rows':320,'new_compute':0}))

if __name__=='__main__':run()

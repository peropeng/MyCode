"""Audit saved masks/groups/original cached totals without new scientific inference."""
from common162 import *
from evaluate162 import CODE_FILES
def run():
 require_time();seal=enter_score_phase();receipt=read(E/'score_receipt.json');code=read(E/'evaluation_code_seal.json');joined=read(E/'score_join_started.json');masks=read(E/'marker_masks.json')
 metric=read(E/'cached_stratified_metrics.json');pairs=read(E/'pairedcounts.json');positions=read(E/'Gold_position.json');cases=read(E/'case_export.json');selected=read(E/'public_case_selection.json');packet=read(E/'main_decision_packet.json');reads=read(E/'score_read_manifest.json');errors=[]
 def check(ok,name):
  if not ok:errors.append(name)
 sh=sha(E/'marker_masks_sealed.json');ch=sha(E/'evaluation_code_seal.json')
 check(sha(E/'approved_plan.json')==PLAN_SHA and code['sources']=={str(E/n):sha(E/n) for n in CODE_FILES},'approved_and_frozen_evaluation_sources')
 check(receipt['status']=='PASS' and joined['marker_masks_seal_sha256']==receipt['marker_masks_seal_sha256']==packet['marker_masks_seal_sha256']==sh
       and receipt['evaluation_code_seal_sha256']==joined['evaluation_code_seal_sha256']==ch,'public_mask_code_score_Gold_chain')
 check((E/'marker_masks_sealed.json').stat().st_mtime_ns<(E/'evaluation_code_seal.json').stat().st_mtime_ns<=(E/'score_join_started.json').stat().st_mtime_ns<(E/'score_receipt.json').stat().st_mtime_ns,'all_masks_and_publiccases_sealed_before_Gold_scorejoin')
 check(all(Path(p).stat().st_mtime_ns<(E/'marker_masks_sealed.json').stat().st_mtime_ns for p in seal['artifacts']),'all_public_mask_artifacts_before_seal')
 allow_score_inputs(receipt['prediction_files']);check_hashes({p:r['sha256'] for p,r in receipt['prediction_files'].items()});check_hashes(receipt['historical_reference_metadata_paths_sha256'])
 check(receipt['cached_Gold_sha256']==sha(E160/'evaluation_cached_Gold.json') and receipt['parent160_frozen_input_manifest_sha256']==sha(E160/'frozen_input_manifest.json'),'unchanged160cache_and_manifest')
 mby={(r['cohort'],r['partition'],r['group'],r['method']):r for r in metric['rows']};pby={(r['cohort'],r['partition'],r['group'],r['other']):r for r in pairs['rows']};full={(r['cohort'],r['partition'],r['method']):r for r in metric['full_scope_parent_matches']}
 check(len(metric['rows'])==len(mby)==160 and set(mby)=={(c,p,g,m) for c in COHORTS for p in PARTITIONS for g in GROUPS for m in METHODS},'complete160primaryonly_metricrows')
 check(len(pairs['rows'])==len(pby)==128 and set(pby)=={(c,p,g,m) for c in COHORTS for p in PARTITIONS for g in GROUPS for m in METHODS[1:]},'complete128primaryonly_pairrows')
 check(len(full)==len(metric['full_scope_parent_matches'])==80,'all80parent_fullscope_totals')
 for c in COHORTS:
  ids=masks['cohorts'][c]['ids'];groups=metric['groups'][c]
  flat=groups['present']+groups['absent'];check(len(flat)==len(set(flat))==len(ids) and set(flat)==set(ids),'all_original_cohort_groups:'+c)
  for p in PARTITIONS:
   for m in METHODS:
    rs=[mby[c,p,g,m] for g in GROUPS];whole=full[c,p,m]
    check(sum(r['n'] for r in rs)==whole['n']==len(ids) and sum(r['hits'] for r in rs)==whole['hits'] and sum(r['invalid'] for r in rs)==whole['invalid'],'group_totals:'+c+'/'+p+'/'+m)
    for k in ('Top1','MRR','Top3'):check(math.isclose(math.fsum(r[k]*r['n'] for r in rs if r['n'])/len(ids),whole[k],rel_tol=0.,abs_tol=1e-12),'group_weighted_'+k)
    for r in rs:
     check(r['n']==len(groups[r['group']]) and r['empty_group']==(r['n']==0),'group_membership_and_empty')
     if not r['n']:check(r['hits']==r['invalid']==0 and all(r[k] is None for k in ('Top1','MRR','Top3')),'empty0_NA_kept')
   for g in GROUPS:
    for m in METHODS[1:]:
     r=pby[c,p,g,m];a=mby[c,p,g,'G'];b=mby[c,p,g,m]
     check(r['n']==a['n']==b['n'] and r['G_hits']==a['hits'] and r['other_hits']==b['hits'] and r['G_only_correct']-r['other_only_correct']==a['hits']-b['hits']
           and sum(r[k] for k in ('G_only_correct','other_only_correct','both_correct','both_wrong'))==r['n'],'paired_count_identity')
 check(len(positions['rows'])==4310 and len({(r['sample_id'],r['marker']) for r in positions['rows']})==4310 and len(positions['coverage'])==8,'two_marker4310Gold_rows8summaries')
 by={r['sample_id']:r for r in masks['rows']}
 for r in positions['rows']:
  m=by[r['sample_id']]['markers'][r['marker']];target=r['original_Gold_ordinal'];first=m['first_matched_ordinal'];rel='no_match' if first is None else 'before' if first<target else 'same' if first==target else 'after'
  check(r['gold_has_marker']==(target in m['matched_turn_ordinals']) and r['first_marker_relative_to_Gold']==rel and r['single_matched_turn_is_Gold']==(len(m['matched_turn_ordinals'])==1 and target in m['matched_turn_ordinals']),'Gold_relative_mask_positions')
  check(r['encoded_input_visibility']==r['model_causal_usage']=='UNKNOWN','no_visibility_or_causal_inference')
 for row in positions['coverage']:
  rs=[r for r in positions['rows'] if r['cohort']==row['cohort'] and r['marker']==row['marker']]
  check(row['n']==len(rs)==masks['cohorts'][row['cohort']]['n'] and sum(row['first_marker_relative_to_Gold_counts'].values())==row['n']
        and row['gold_has_marker']==sum(r['gold_has_marker'] for r in rs) and row['single_matched_turn_is_Gold']==sum(r['single_matched_turn_is_Gold'] for r in rs),'all_Gold_coverage_full_denominators')
 check([r['sample_id'] for r in cases['cases']]==[r['sample_id'] for r in selected['cases']] and cases['public_case_selection_sha256']==sha(E/'public_case_selection.json'),'fixed_prescore_case_IDs_unchanged')
 for r in cases['cases']:check(r['markers']==by[r['sample_id']]['markers'] and r['encoded_input_visibility']==r['model_causal_usage']=='UNKNOWN','case_original_windows_mask_and_UNKNOWN_usage')
 for filename,n in [('cached_stratified_metrics.csv',160),('pairedcounts.csv',128),('Gold_position.csv',4310)]:
  with (E/filename).open(encoding='utf-8-sig',newline='') as f:check(sum(1 for _ in csv.DictReader(f))==n,'CSV_full_rows:'+filename)
 check(reads['all_prediction_JSON_files_read_once'] and reads['source_prediction_files']==len(receipt['prediction_files'])==80,'80old_ensemble_JSONs_read_once')
 check(all(r['phase']=='SCORED_CACHE' for p,r in reads['inputs'].items() if p.startswith(str(E160)) or p in receipt['prediction_files']),'cached_Gold_score_inputs_after_publicseal')
 resource={'at_utc':now(),'experiment':'Exp162','historical_target_tasks':2155,'source_training_texts':0,'actual_public_scan_counts':masks['scan_counts'],'marker_groups_not_new_independent_tasks':True,
           'cached_metric_rows':160,'paired_rows':128,'full_original_parent_matches':80,'Gold_position_descriptive_rows_not_independent_tasks':4310,'Gold_coverage_rows':8,'fixed_public_case_count':cases['count'],
           'new_training':0,'new_models':0,'new_model_loads':0,'new_model_constructors':0,'new_forwards':0,'new_neural_encoder':0,'new_ranker_outputs':0,'new_derived_rank_outputs':0,
           'new_native_tests':0,'new_recovery_candidates':0,'new_API':0,'new_downloads':0,'new_Gold':0,'new_independent_tasks':0,'new_p_CI_bootstrap':0,'fee_CNY':'0','encoded_input_visibility':'UNKNOWN','model_causal_usage':'UNKNOWN'}
 repair=read(E/'public_mask_engineering_repair.json');passes=1+repair['discarded_complete_public_scan_passes']
 resource.update(public_mask_engineering_repair=repair,discarded_public_scan_passes=passes-1,physical_public_scan_passes=passes,
                 physical_cumulative_task_record_views_scanned=2155*passes,
                 physical_cumulative_classical_scan_counts={k:masks['scan_counts'][k]*passes for k in ('turns','expected_turn_fields','actual_string_fields_casefolded','raw_characters_casefolded','casefolded_characters','classical_marker_substring_field_scans')},
                 cumulative_counts_include_discarded_complete_public_pass_inferred_from_failure_location=True,unique_original_tasks_still2155=True)
 write_new(E/'resource_audit.json',resource);packet.update(status='PASS' if not errors else 'FAIL',final_execution_audit_status='PASS' if not errors else 'FAIL',all_original_denominators_and_emptygroups_kept=not errors,scientific_interpretation_owner='root');atomic(E/'main_decision_packet.json',packet)
 write_new(E/'compact_summary.json',{**packet,'errors':errors})
 names=('cached_stratified_metrics.json','cached_stratified_metrics.csv','pairedcounts.json','pairedcounts.csv','Gold_position.json','Gold_position.csv','case_export.json','score_receipt.json','score_read_manifest.json','resource_audit.json','main_decision_packet.json','compact_summary.json')
 write_new(E/'final_execution_audit.json',{'at_utc':now(),'experiment':'Exp162','status':'PASS' if not errors else 'FAIL','errors':errors,'marker_masks_seal_sha256':sh,'evaluation_code_seal_sha256':ch,
           'all_primary_groups_original_parent_totals_Goldmaskpositions_prescorecases_andUNKNOWNusage_verified':not errors,'no_new_model_rank_statistical_or_independent_task_claim':True,'artifacts':{str(E/n):sha(E/n) for n in names}})
 status('EXP162_COMPLETE_PASS' if not errors else 'EXP162_FINAL_AUDIT_FAIL_STOP',new_models_or_predictions=0,fee_CNY='0',next='root interprets andremainsidle;10Beijing hardstop')
 if errors:raise RuntimeError('EXP162_FINAL_AUDIT_FAILED:'+','.join(errors))
 print(canonical({'Exp162_final':'PASS','new_compute':0}))
if __name__=='__main__':run()

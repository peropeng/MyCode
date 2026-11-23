"""Join only existing sealed ensembles after the complete public lexical seal."""
from common161 import *

CODE_FILES=('evaluate161.py','finalize161.py','common161.py')
CACHE={}

def demand(ok,message):
 if not ok:raise RuntimeError(message)

def once(path):
 key=str(Path(path).resolve())
 if key not in CACHE:CACHE[key]=read(path)
 return CACHE[key]

def cached_outcomes(predictions,ids,gold):
 demand(set(predictions)==set(ids),'Complete historical original target IDs required')
 out={}
 for sid in ids:
  p=predictions[sid];g=gold[sid];n=g['raw_steps'];target=g['original_Gold_ordinal']
  demand(type(n) is int and n>0 and type(target) is int and 0<=target<n,'Original cached Gold coordinates required')
  order=p.get('order',p.get('ranking'));valid=p.get('valid') is True;step=p.get('chosen_step',p.get('predicted_step'))
  demand(isinstance(order,list) and len(order)==n and all(type(x) is int for x in order) and sorted(order)==list(range(n)), 'Cached complete original-coordinate ranking required')
  if valid:demand(type(step) is int and 0<=step<n and order[0]==step,'Cached chosen step/order mismatch')
  rank=order.index(target)+1
  out[sid]={'Top1':int(valid and step==target),'MRR':1/rank if valid else 0.,'Top3':int(valid and rank<=3),'invalid':int(not valid)}
 return out

def metrics(out,ids):
 n=len(ids);hits=sum(out[s]['Top1'] for s in ids)
 return {'n':n,'hits':hits,'Top1':hits/n if n else None,'MRR':math.fsum(out[s]['MRR'] for s in ids)/n if n else None,
         'Top3':sum(out[s]['Top3'] for s in ids)/n if n else None,'invalid':sum(out[s]['invalid'] for s in ids),'empty_bin':n==0}

def paired(main,other,ids):
 n=len(ids);rescued=sum(main[s]['Top1']==1 and other[s]['Top1']==0 for s in ids);damaged=sum(main[s]['Top1']==0 and other[s]['Top1']==1 for s in ids)
 return {'n':n,'G_hits':sum(main[s]['Top1'] for s in ids),'other_hits':sum(other[s]['Top1'] for s in ids),
         'G_only_correct':rescued,'other_only_correct':damaged,'both_correct':sum(main[s]['Top1']==other[s]['Top1']==1 for s in ids),
         'both_wrong':sum(main[s]['Top1']==other[s]['Top1']==0 for s in ids),
         'Top1_difference':(rescued-damaged)/n if n else None,'MRR_difference':math.fsum(main[s]['MRR']-other[s]['MRR'] for s in ids)/n if n else None,
         'Top3_difference':sum(main[s]['Top3']-other[s]['Top3'] for s in ids)/n if n else None,'empty_bin':n==0,'descriptive_only':True}

def expected_match(actual,expected):
 demand(actual['n']==expected.get('n',expected.get('records')) and actual['hits']==expected['hits'],'Existing full ensemble denominator/hits differ from parent')
 for key in ('Top1','MRR','Top3'):
  demand(expected.get(key) is not None and math.isclose(actual[key],expected[key],abs_tol=1e-12,rel_tol=0.), 'Existing full ensemble '+key+' differs from parent')
 demand(actual['invalid']==expected.get('invalid_predictions',expected.get('invalid')),'Existing full ensemble invalid count differs from parent')

def public_checks():
 texts=once(E/'public_texts.json');near=once(E/'nearest_neighbors.json');bins=once(E/'bin_membership.json');counts=once(E/'lexical_counts.json');cases=once(E/'case_export.json')
 sources={r['sample_id']:r for r in texts['sources']};targets={r['sample_id']:r for r in texts['targets']};rows=near['rows'];by={r['sample_id']:r for r in rows}
 demand(len(sources)==len(texts['sources'])==614 and len(targets)==len(texts['targets'])==len(rows)==len(by)==2155,'Complete614source2155target lexical scope required')
 demand(set(by)==set(targets) and set(texts['partitions'])==set(PARTITIONS),'Full target IDs and four predefined partitions required')
 for part,p in texts['partitions'].items():
  demand((len(p['fit_ids']),len(p['val_ids']))==(492,122) and not set(p['fit_ids'])&set(p['val_ids']) and set(p['fit_ids'])|set(p['val_ids'])==set(sources),'Same614 pool partition membership required')
 for cohort in COHORTS:
  ids=texts['cohorts'][cohort]['ids'];demand(len(ids)==texts['cohorts'][cohort]['n'] and all(targets[s]['cohort']==cohort for s in ids),'Public original cohort coordinates required')
  for part in PARTITIONS:
   fitbins=bins['cohorts'][cohort]['partitions'][part]['fit'];demand(set(fitbins)==set(BINS),'All fixed five fit-only bins required')
   flat=[s for bin_name in BINS for s in fitbins[bin_name]]
   demand(len(flat)==len(set(flat))==len(ids) and set(flat)==set(ids),'All fit-only bins must partition the unchanged full cohort')
   for bin_name in BINS:
    demand(all(by[s]['by_partition'][part]['fit_bin']==bin_name for s in fitbins[bin_name]),'Saved fit bins disagree with saved nearest-neighbor table')
 demand(any('pair' in str(k).casefold() and type(v) is int and v==1323170 for k,v in counts.items()),'Actual all2155×614 lexical pair count required')
 saved_cases=cases['cases'];demand(len(saved_cases)<=24,'Fixed pre-score similarity case cap24 exceeded')
 checked=[]
 for case in saved_cases:
  t=case.get('target_sample_id',case.get('target',{}).get('sample_id'));s=case.get('source_sample_id',case.get('source',{}).get('sample_id'))
  demand(t in targets and s in sources,'Pre-score case original source/target identity required')
  a,b=lexical(targets[t]['task']),lexical(sources[s]['task']);demand(a['shingles'] and b['shingles'],'UNKNOWN task cannot supply a duplicate case')
  inter=len(a['shingles']&b['shingles']);union=len(a['shingles']|b['shingles']);neighbor=by[t]['pool_top3'][0]
  demand(neighbor['source_sample_id']==s and neighbor['intersection']==inter and neighbor['union']==union,'Raw public case exact shingle intersection/union mismatch')
  demand(math.isclose(neighbor['jaccard'],inter/union,rel_tol=0.,abs_tol=1e-15)
         and math.isclose(neighbor['containment'],inter/min(len(a['shingles']),len(b['shingles'])),rel_tol=0.,abs_tol=1e-15),'Raw public case Jaccard/containment mismatch')
  for key,lex in (('exact_full_text',a['normalized_full']==b['normalized_full']),('token_sequence_equal',a['tokens']==b['tokens'])):
   if key in neighbor:demand(neighbor[key]==lex,'Raw public case '+key+' mismatch')
  if 'target_task' in case:demand(case['target_task']==targets[t]['task'],'Fixed target case text changed')
  if 'source_task' in case:demand(case['source_task']==sources[s]['task'],'Fixed source case text changed')
  checked.append({'target_sample_id':t,'source_sample_id':s,'intersection':inter,'union':union,'jaccard':inter/union,'raw_task_recomputed':True})
 return texts,bins,counts,{'count':len(checked),'cases':checked,'new_Gold_or_model_reads':0,'no_automatic_contamination_leakage_or_semantic_duplicate_judgment':True}

def run():
 require_time();demand(sha(E/'approved_plan.json')==PLAN_SHA,'Frozen161 plan changed')
 demand(not (E/'score_join_started.json').exists(),'Cached score join already started')
 seal=enter_score_phase();textseal_sha=sha(E/'text_proximity_sealed.json')
 required=('public_texts.json','nearest_neighbors.json','bin_membership.json','lexical_counts.json','case_export.json')
 artifacts={str(Path(path).resolve()):h for path,h in seal['artifacts'].items()}
 demand(all(str((E/name).resolve()) in artifacts for name in required),'Whole public lexical artifacts must be sealed before score join')
 public=once(E/'frozen_public_manifest.json');allow_public(path for path in public['inputs'] if Path(path).name=='public_records.json');check_hashes(public['inputs'])
 texts,bins,counts,case_check=public_checks()
 codes={str(E/name):sha(E/name) for name in CODE_FILES}
 write_new(E/'evaluation_code_seal.json',{'at_utc':now(),'experiment':'Exp161','sources':codes,'approved_plan_sha256':PLAN_SHA,'text_proximity_seal_sha256':textseal_sha,
           'bins':list(BINS),'methods':list(METHODS),'partitions':list(PARTITIONS),'stratified_rows':400,'paired_rows':320,'new_p_CI_bootstrap':0})
 write_new(E/'score_join_started.json',{'at_utc':now(),'phase':'SCORED_CACHE','text_proximity_seal_sha256':textseal_sha,'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json'),
           'all2155nearest_bins_and_fixed_cases_complete_before_join':True,'target_Gold_or_scores_read_by_evaluator_before_textseal':0})
 demand((E/'text_proximity_sealed.json').stat().st_mtime_ns<(E/'score_join_started.json').stat().st_mtime_ns,'Text proximity seal must precede cached Gold/score join')
 frozen=once(E160/'frozen_input_manifest.json');protected={str(Path(path).resolve()):h for path,h in {**frozen['inputs'],**frozen['prepared']}.items()}
 def protected_once(path):
  key=str(Path(path).resolve());demand(key in protected and sha(path)==protected[key],'Cached source absent from unchanged160 input seal:'+key);return once(path)
 cells=protected_once(E160/'cell_manifest.json');evaluation=protected_once(E160/'evaluation_cached_Gold.json');gold=evaluation['gold']
 selected=[r for r in cells['axis1'] if r['seed'] is None];by_part={r['partition']:r for r in selected}
 demand(len(selected)==len(by_part)==4 and set(by_part)==set(PARTITIONS),'Exactly four existing complete3seed ensemble views required')
 paths=[r['sources'][method]['predictions'][cohort] for r in selected for method in METHODS for cohort in COHORTS];allow_score_inputs(paths)
 metricrows=[];pairrows=[];fullrows=[];source_refs={}
 for cohort in COHORTS:
  ids=texts['cohorts'][cohort]['ids'];demand(ids==evaluation['cohorts'][cohort]['ids'] and len(ids)==evaluation['cohorts'][cohort]['n'],'Unchanged cached source Gold/public cohort IDs required')
  public_target_by={r['sample_id']:r for r in texts['targets'] if r['cohort']==cohort}
  demand(all(gold[s]['raw_steps']==public_target_by[s]['original_candidate_count'] and gold[s]['task_group']==public_target_by[s]['task_group'] for s in ids),'Cached original candidate coordinates/task groups must match frozen public identity')
  for partition in PARTITIONS:
   cell=by_part[partition];outcomes={};fitbins=bins['cohorts'][cohort]['partitions'][partition]['fit']
   for method in METHODS:
    source=cell['sources'][method];path=source['predictions'][cohort];saved=protected_once(path)
    demand(saved['arm']==source['arm'] and saved['seeds']==[20261006,20261007,20261008],'Existing native complete3seed method identity required')
    out=cached_outcomes(saved['predictions'],ids,gold);whole=metrics(out,ids);expected_match(whole,source['expected_metrics'][cohort]);outcomes[method]=out
    source_refs[str(Path(path).resolve())]={'sha256':sha(path),'parent':source['parent'],'arm':source['arm'],'condition':source['condition']}
    fullrows.append({'cohort':cohort,'partition':partition,'method':method,**whole,'parent_expected_metrics':source['expected_metrics'][cohort],'matched_parent_complete_ensemble':True})
    for bin_name in BINS:metricrows.append({'cohort':cohort,'partition':partition,'similarity_scope':'fit_only','bin':bin_name,'method':method,**metrics(out,fitbins[bin_name]),'descriptive_only':True})
   for bin_name in BINS:
    for method in METHODS[1:]:pairrows.append({'cohort':cohort,'partition':partition,'similarity_scope':'fit_only','bin':bin_name,'main':'G','other':method,**paired(outcomes['G'],outcomes[method],fitbins[bin_name])})
 demand((len(metricrows),len(pairrows),len(fullrows),len(source_refs))==(400,320,80,80),'Complete400metric320paired80fullscope source rows required')
 common={'at_utc':now(),'experiment':'Exp161','text_proximity_seal_sha256':textseal_sha,'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json'),
         'bins':list(BINS),'empty_bins_kept_zero_n_and_null_rate':True,'descriptive_only':True,'new_p_CI_bootstrap':0,'new_rankings_ensembles_or_fusion':0}
 write_new(E/'stratified_cached_metrics.json',{**common,'rows':metricrows,'full_scope_parent_matches':fullrows,'rows_count':400,'full_scope_rows':80})
 write_csv(E/'stratified_cached_metrics.csv',metricrows);write_new(E/'pairedcounts.json',{**common,'rows':pairrows,'rows_count':320});write_csv(E/'pairedcounts.csv',pairrows)
 references={str(path):sha(path) for path in (E160/'parent_reference_metadata.json',E160/'main_decision_packet.json',E160/'final_execution_audit.json')}
 packet160=once(E160/'main_decision_packet.json');audit160=once(E160/'final_execution_audit.json');demand(audit160['status']=='PASS','Prior160 final execution audit must remain PASS')
 demand(sha(E160/'main_decision_packet.json')==once(E/'approved_plan.json')['parents']['packet160_sha256'],'Frozen prior160 packet binding changed')
 receipt={**common,'status':'PASS','source_prediction_files':source_refs,'parent160_frozen_input_manifest_sha256':sha(E160/'frozen_input_manifest.json'),
          'cached_Gold_sha256':sha(E160/'evaluation_cached_Gold.json'),'cached_Gold_tasks':2155,'new_Gold':0,'cases_public_raw_task_recheck':case_check,
          'historical_reference_metadata_verbatim_reference':references,'preserve_old_statistical_families_and_FAILs_without_changes':True,
          'preserve156_exact_zero_original_definition':True,'cached_source_ensemble_files':80,'full_scope_rows':80,'stratified_rows':400,'paired_rows':320,'no_automatic_scientific_judgment':True}
 write_new(E/'score_receipt.json',receipt)
 write_new(E/'score_read_manifest.json',{'at_utc':now(),'experiment':'Exp161','phase':'SCORED_CACHE','inputs':READS,'unique_read_files':len(READS),
          'all_prediction_JSON_files_read_once':all(READS[path]['read_calls']==1 for path in source_refs),'source_ensemble_prediction_files':80,
          'text_proximity_seal_sha256':textseal_sha,'no_raw_Gold_AF_model_or_tensor_file_reads':True,'new_model_constructor_forward_ranking_or_gold':0})
 write_new(E/'main_decision_packet.json',{'at_utc':now(),'experiment':'Exp161','status':'EVALUATION_COMPLETE_PENDING_FINAL_MECHANICAL_AUDIT','kind':'posthoc_lexical_proximity_cached_stratification',
          'source_targets':2155,'source_pool_texts':614,'public_task_texts':2769,'exact_pair_candidates':1323170,'partitions':list(PARTITIONS),'bins':list(BINS),'methods':list(METHODS),
          'stratified_rows':400,'paired_rows':320,'full_scope_original_parent_matches':80,'fixed_public_cases_rechecked':case_check['count'],
          'text_proximity_seal_sha256':textseal_sha,'score_receipt_sha256':sha(E/'score_receipt.json'),'cached_reference_paths_sha256':references,
          'original_statistics_families_FAILs_AF_limits_and156_exact_zero_preserved':True,'new_p_CI_bootstrap':0,'new_models_rankings_or_independent_tasks':0,
          'does_not_automatically_establish_contamination_leakage_or_semantic_identity':True,'scientific_interpretation_owner':'root','fee_CNY':'0'})
 status('EXP161_CACHED_SCORE_COMPLETE',stratified_rows=400,paired_rows=320,next='finalize161.py; root owns interpretation')
 print(canonical({'Exp161_score':'COMPLETE','metric_rows':400,'paired_rows':320,'new_compute':0}))

if __name__=='__main__':run()

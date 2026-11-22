"""Describe fixed public marker masks using existing sealed ensemble outcomes only."""
from common162 import *
CODE_FILES=('evaluate162.py','finalize162.py','common162.py')
CACHE={}
def demand(ok,message):
 if not ok:raise RuntimeError(message)
def once(path):
 key=str(Path(path).resolve())
 if key not in CACHE:CACHE[key]=read(path)
 return CACHE[key]
def outcomes(pred,ids,gold):
 demand(set(pred)==set(ids),'Full original target ID scope required')
 out={}
 for s in ids:
  g=gold[s];p=pred[s];n=g['raw_steps'];target=g['original_Gold_ordinal'];order=p.get('order',p.get('ranking'));step=p.get('chosen_step',p.get('predicted_step'));valid=p.get('valid') is True
  demand(type(target) is int and 0<=target<n and isinstance(order,list) and len(order)==n and all(type(x) is int for x in order) and sorted(order)==list(range(n)),'Existing complete original candidate coordinates required')
  if valid:demand(type(step) is int and order[0]==step,'Existing chosen step/order mismatch')
  rank=order.index(target)+1;out[s]={'Top1':int(valid and step==target),'MRR':1/rank if valid else 0.,'Top3':int(valid and rank<=3),'invalid':int(not valid)}
 return out
def metrics(out,ids):
 n=len(ids);hits=sum(out[s]['Top1'] for s in ids)
 return {'n':n,'hits':hits,'Top1':hits/n if n else None,'MRR':math.fsum(out[s]['MRR'] for s in ids)/n if n else None,'Top3':sum(out[s]['Top3'] for s in ids)/n if n else None,'invalid':sum(out[s]['invalid'] for s in ids),'empty_group':n==0}
def paired(a,b,ids):
 n=len(ids);pos=sum(a[s]['Top1']==1 and b[s]['Top1']==0 for s in ids);neg=sum(a[s]['Top1']==0 and b[s]['Top1']==1 for s in ids)
 return {'n':n,'G_hits':sum(a[s]['Top1'] for s in ids),'other_hits':sum(b[s]['Top1'] for s in ids),'G_only_correct':pos,'other_only_correct':neg,
         'both_correct':sum(a[s]['Top1']==b[s]['Top1']==1 for s in ids),'both_wrong':sum(a[s]['Top1']==b[s]['Top1']==0 for s in ids),
         'Top1_difference':(pos-neg)/n if n else None,'MRR_difference':math.fsum(a[s]['MRR']-b[s]['MRR'] for s in ids)/n if n else None,'Top3_difference':sum(a[s]['Top3']-b[s]['Top3'] for s in ids)/n if n else None,'descriptive_only':True}
def expected_match(actual,expected):
 demand(actual['n']==expected.get('n',expected.get('records')) and actual['hits']==expected['hits'],'Full existing ensemble denominator/hits differ from parent')
 for k in ('Top1','MRR','Top3'):demand(expected.get(k) is not None and math.isclose(actual[k],expected[k],rel_tol=0.,abs_tol=1e-12),'Existing full ensemble '+k+' mismatch')
 demand(actual['invalid']==expected.get('invalid_predictions',expected.get('invalid')),'Existing full ensemble invalid count mismatch')
def run():
 require_time();demand(sha(E/'approved_plan.json')==PLAN_SHA and not (E/'score_join_started.json').exists(),'Changed plan or already started score join')
 seal=enter_score_phase();sh=sha(E/'marker_masks_sealed.json');masks=once(E/'marker_masks.json');selection=once(E/'public_case_selection.json')
 demand(masks['markers']==MARKERS and len(masks['rows'])==2155,'Exact fixed markers and full2155 masks required')
 by={r['sample_id']:r for r in masks['rows']};demand(len(by)==2155 and set(masks['cohorts'])==set(COHORTS),'Complete unique original masks/cohorts required')
 paths={r['source_path'] for r in masks['rows']};demand(len(paths)==4,'Only four target public record sources required');allow_public(paths)
 public_hashes={path:sha(path) for path in paths}
 for r in masks['rows']:
  demand(public_hashes[r['source_path']]==r['source_sha256'],'Frozen public mask source changed')
  for marker in MARKERS:
   m=r['markers'][marker];ordinals=m['matched_turn_ordinals']
   demand(ordinals==sorted(set(ordinals)) and all(type(v) is int and 0<=v<r['n_turns'] for v in ordinals)
          and m['present']==bool(ordinals) and m['matched_turn_count']==len(ordinals),'Original marker turn coordinates or union count mismatch')
   demand(m['first_matched_ordinal']==(ordinals[0] if ordinals else None) and m['last_matched_ordinal']==(ordinals[-1] if ordinals else None),'Fixed first/last descriptive mask positions mismatch')
 codes={str(E/n):sha(E/n) for n in CODE_FILES}
 write_new(E/'evaluation_code_seal.json',{'at_utc':now(),'sources':codes,'approved_plan_sha256':PLAN_SHA,'marker_masks_seal_sha256':sh,'groups':list(GROUPS),'methods':list(METHODS),'markers':MARKERS,'cached_metric_rows':160,'paired_rows':128,'new_p_CI_bootstrap':0})
 write_new(E/'score_join_started.json',{'at_utc':now(),'marker_masks_seal_sha256':sh,'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json'),'all2155_masks_and_case_IDs_sealed_before_Gold_scores':True,'preseal_target_Gold_or_score_reads_by_evaluator':0})
 demand((E/'marker_masks_sealed.json').stat().st_mtime_ns<(E/'score_join_started.json').stat().st_mtime_ns,'All masks/case choices must precede cached Gold join')
 frozen=once(E160/'frozen_input_manifest.json');protected={str(Path(p).resolve()):h for p,h in {**frozen['inputs'],**frozen['prepared']}.items()}
 def protected_once(path):
  key=str(Path(path).resolve());demand(key in protected and sha(path)==protected[key],'Cached input absent from unchanged160 seal:'+key);return once(path)
 cells=protected_once(E160/'cell_manifest.json');evaluation=protected_once(E160/'evaluation_cached_Gold.json');gold=evaluation['gold'];frames=[r for r in cells['axis1'] if r['seed'] is None];framesby={r['partition']:r for r in frames}
 demand(len(frames)==len(framesby)==4 and set(framesby)==set(PARTITIONS),'Four existing3seed ensemble frames required')
 predpaths=[r['sources'][m]['predictions'][c] for r in frames for m in METHODS for c in COHORTS];allow_score_inputs(predpaths)
 public={}
 for path in paths:
  records=once(path)['records'];public.update({r['sample_id']:r for r in records})
 demand(set(public)==set(by)==set(gold),'Same complete2155 original public/Gold/mask IDs required')
 goldrows=[];coverage=[];metricrows=[];pairrows=[];fullrows=[];sources={};groupids={}
 for cohort in COHORTS:
  ids=masks['cohorts'][cohort]['ids'];demand(ids==evaluation['cohorts'][cohort]['ids'] and len(ids)==masks['cohorts'][cohort]['n'],'Original complete cohort IDs required')
  groupids[cohort]={group:[s for s in ids if by[s]['markers']['primary']['present']==(group=='present')] for group in GROUPS}
  for s in ids:
   r=by[s];g=gold[s];record=public[s];demand(r['n_turns']==g['raw_steps']==len(record['turns']) and r['task_group']==record['task_group'] and g.get('task_group',r['task_group'])==r['task_group'],'Original candidate count/taskgroup binding mismatch')
   target=g['original_Gold_ordinal'];demand(type(target) is int and 0<=target<r['n_turns'],'Original cached Gold coordinate required')
   for marker in MARKERS:
    m=r['markers'][marker];first=m['first_matched_ordinal'];relation='no_match' if first is None else 'before' if first<target else 'same' if first==target else 'after'
    goldrows.append({'sample_id':s,'cohort':cohort,'marker':marker,'marker_substring':MARKERS[marker],'n_turns':r['n_turns'],'original_Gold_ordinal':target,
                     'original_Gold_role':record['turns'][target]['role'],'gold_has_marker':target in m['matched_turn_ordinals'],'first_marker_relative_to_Gold':relation,
                     'single_matched_turn_is_Gold':m['matched_turn_count']==1 and target in m['matched_turn_ordinals'],'matched_turn_count':m['matched_turn_count'],
                     'encoded_input_visibility':'UNKNOWN','model_causal_usage':'UNKNOWN','descriptive_only':True})
  for marker in MARKERS:
   rs=[r for r in goldrows if r['cohort']==cohort and r['marker']==marker]
   coverage.append({'cohort':cohort,'marker':marker,'n':len(ids),'gold_has_marker':sum(r['gold_has_marker'] for r in rs),'single_matched_turn_is_Gold':sum(r['single_matched_turn_is_Gold'] for r in rs),
                    'first_marker_relative_to_Gold_counts':{rel:sum(r['first_marker_relative_to_Gold']==rel for r in rs) for rel in ('before','same','after','no_match')},'encoded_input_visibility':'UNKNOWN','model_causal_usage':'UNKNOWN'})
  for partition in PARTITIONS:
   cell=framesby[partition];outs={}
   for method in METHODS:
    source=cell['sources'][method];path=source['predictions'][cohort];saved=protected_once(path)
    demand(saved['arm']==source['arm'] and saved['seeds']==[20261006,20261007,20261008],'Existing native3seed method identity required')
    out=outcomes(saved['predictions'],ids,gold);whole=metrics(out,ids);expected_match(whole,source['expected_metrics'][cohort]);outs[method]=out
    sources[str(Path(path).resolve())]={'sha256':sha(path),'parent':source['parent'],'arm':source['arm'],'condition':source['condition']}
    fullrows.append({'cohort':cohort,'partition':partition,'method':method,**whole,'matched_original_parent':True})
    for group in GROUPS:metricrows.append({'cohort':cohort,'partition':partition,'marker':'primary','group':group,'method':method,**metrics(out,groupids[cohort][group]),'descriptive_only':True})
   for group in GROUPS:
    for method in METHODS[1:]:pairrows.append({'cohort':cohort,'partition':partition,'marker':'primary','group':group,'main':'G','other':method,**paired(outs['G'],outs[method],groupids[cohort][group])})
 demand((len(metricrows),len(pairrows),len(fullrows),len(goldrows),len(coverage),len(sources))==(160,128,80,4310,8,80),'Full160metric128pair80parent4310Gold8coverage dimensions required')
 cases=[]
 for case in selection['cases']:
  s=case['sample_id'];demand(s in by,'Fixed pre-Gold case ID required');r=by[s];g=gold[s];record=public[s]
  cases.append({**case,'task_group':r['task_group'],'record_id':r.get('record_id'),'task_identity':r.get('task_identity'),
                'original_Gold_ordinal':g['original_Gold_ordinal'],'original_Gold_role':record['turns'][g['original_Gold_ordinal']]['role'],
                'n_turns':r['n_turns'],'markers':r['markers'],'source_path':r['source_path'],'source_sha256':r['source_sha256'],
                'encoded_input_visibility':'UNKNOWN','model_causal_usage':'UNKNOWN','selection_fixed_before_Gold_or_scores':True})
 flags={'marker_masks_seal_sha256':sh,'descriptive_only':True,'secondary_performance_stratification':False,'new_p_CI_bootstrap':0,'no_marker_rule_predictions_or_modelcausal_claim':True}
 write_new(E/'cached_stratified_metrics.json',{**flags,'rows':metricrows,'full_scope_parent_matches':fullrows,'groups':groupids,'rows_count':160});write_csv(E/'cached_stratified_metrics.csv',metricrows)
 write_new(E/'pairedcounts.json',{**flags,'rows':pairrows,'rows_count':128});write_csv(E/'pairedcounts.csv',pairrows)
 write_new(E/'Gold_position.json',{**flags,'rows':goldrows,'coverage':coverage,'rows_count':4310,'summary_count':8});write_csv(E/'Gold_position.csv',goldrows)
 write_new(E/'case_export.json',{**flags,'public_case_selection_sha256':sha(E/'public_case_selection.json'),'cases':cases,'count':len(cases),'fixed_cases_not_selected_by_score':True})
 refs={str(path):sha(path) for path in (E160/'parent_reference_metadata.json',E160/'main_decision_packet.json',E160/'final_execution_audit.json')};demand(once(E160/'final_execution_audit.json')['status']=='PASS','Parent160 audit must remain PASS')
 write_new(E/'score_receipt.json',{'at_utc':now(),'status':'PASS',**flags,'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json'),'prediction_files':sources,'cached_Gold_sha256':sha(E160/'evaluation_cached_Gold.json'),
           'parent160_frozen_input_manifest_sha256':sha(E160/'frozen_input_manifest.json'),'historical_reference_metadata_paths_sha256':refs,'original_families_FAILs_AF_limits_preserved_via_verbatim_parent_reference':True,
           'cached_metric_rows':160,'paired_rows':128,'full_parent_matches':80,'Gold_position_rows':4310,'Gold_coverage_rows':8,'new_Gold':0,'new_rankings_or_predictions':0})
 write_new(E/'score_read_manifest.json',{'at_utc':now(),'phase':'SCORED_CACHE','inputs':READS,'source_prediction_files':80,'all_prediction_JSON_files_read_once':all(READS[p]['read_calls']==1 for p in sources),'source_training_texts':0,'new_model_tensor_binary_or_raw_Gold_reads':0})
 write_new(E/'main_decision_packet.json',{'at_utc':now(),'experiment':'Exp162','status':'SCORE_COMPLETE_PENDING_FINAL_AUDIT','historical_target_tasks':2155,'markers':MARKERS,'groups':list(GROUPS),
           'cached_metric_rows':160,'paired_rows':128,'full_parent_matches':80,'Gold_position_rows':4310,'Gold_coverage':coverage,'fixed_case_count':len(cases),'marker_masks_seal_sha256':sh,
           'score_receipt_sha256':sha(E/'score_receipt.json'),'historical_reference_metadata_paths_sha256':refs,'encoded_input_visibility':'UNKNOWN','model_causal_usage':'UNKNOWN',
           'no_new_p_CI_bootstrap_or_marker_rule_output':True,'scientific_interpretation_owner':'root','fee_CNY':'0'})
 status('EXP162_SCORE_COMPLETE',metric_rows=160,paired_rows=128,next='finalize162.py thenroot interprets andremainsidle')
 print(canonical({'Exp162_score':'COMPLETE','metric_rows':160,'paired_rows':128,'new_compute':0}))
if __name__=='__main__':run()

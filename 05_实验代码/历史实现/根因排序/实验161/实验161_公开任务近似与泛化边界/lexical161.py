"""All exact source-target lexical candidates, score-blind bins and examples."""
from functools import cmp_to_key
from common161 import *

def better(a,b):
 if b is None:return True
 delta=a['intersection']*b['union']-b['intersection']*a['union']
 return delta>0 or (delta==0 and a['source_sample_id']<b['source_sample_id'])
def pair_record(target,source,ta,sa,inter):
 union=len(ta['shingles'])+len(sa['shingles'])-inter
 return {'source_sample_id':source['sample_id'],'source_task_group':source['task_group'],'intersection':inter,'union':union,'jaccard':inter/union,
  'containment':inter/min(len(ta['shingles']),len(sa['shingles'])),'target_token_count':len(ta['tokens']),'source_token_count':len(sa['tokens']),
  'target_shingle_count':len(ta['shingles']),'source_shingle_count':len(sa['shingles']),
  'target_to_source_token_length_ratio':len(ta['tokens'])/len(sa['tokens']),'min_to_max_token_length_ratio':min(len(ta['tokens']),len(sa['tokens']))/max(len(ta['tokens']),len(sa['tokens'])),
  'exact_full_text':ta['normalized_full']==sa['normalized_full'],'token_sequence_equal':ta['tokens']==sa['tokens'],
  'candidate_near_Jaccard_at_least08':inter*5>=union*4,'source_path':source['source_path'],'source_sha256':source['source_sha256']}

def run():
 require_time();pub=read(E/'public_texts.json');frozen=read(E/'frozen_public_manifest.json');allow_public(frozen['public_paths'].values());check_hashes(frozen['inputs'])
 if sha(E/'public_texts.json')!=frozen['public_texts_sha256']:raise RuntimeError('Frozen public task data changed')
 sources=sorted(pub['sources'],key=lambda r:r['sample_id']);targets=pub['targets'];source_by={s['sample_id']:s for s in sources};target_by={s['sample_id']:s for s in targets}
 if (len(sources),len(targets))!=(614,2155):raise RuntimeError('Full614x2155 scope required')
 source_lex=[lexical(s['task']) for s in sources];target_lex={t['sample_id']:lexical(t['task']) for t in targets};index=defaultdict(list)
 for i,lex in enumerate(source_lex):
  for shingle in lex['shingles']:index[shingle].append(i)
 memberships={p:{s:('fit' if s in set(ids['fit_ids']) else 'val') for s in source_by} for p,ids in pub['partitions'].items()}
 rows=[];pair_candidates=0;exact_pairs=0;unknown_pairs=0;intersection_hits=0;started=time.monotonic();full_text_pairs=0;token_equal_pairs=0;near_pairs=0
 per_cohort={c:{'target_tasks':pub['cohorts'][c]['n'],'exact_full_text_pairs':0,'token_sequence_equal_pairs':0,'Jaccard_at_least08_candidate_pairs':0,'targets_any_exact_full_text':0,'targets_any_token_sequence_equal':0,'targets_any_Jaccard_at_least08':0,'UNKNOWN_targets':0} for c in COHORTS}
 for ti,target in enumerate(targets):
  require_time();ta=target_lex[target['sample_id']];cohort=target['cohort'];row={'sample_id':target['sample_id'],'cohort':cohort,'task_group':target['task_group'],'status':ta['status'],'target_token_count':len(ta['tokens']),'target_shingle_count':len(ta['shingles']),'pool_top3':[],'pool_bin':'UNKNOWN','by_partition':{p:{'fit':None,'val':None,'fit_bin':'UNKNOWN','val_bin':'UNKNOWN'} for p in PARTITIONS},'exact_full_text_source_ids':[],'token_sequence_equal_source_ids':[],'near_candidate_source_ids':[]}
  counts=[0]*614
  for shingle in ta['shingles']:
   for i in index.get(shingle,()):counts[i]+=1;intersection_hits+=1
  for i,source in enumerate(sources):
   pair_candidates+=1;sa=source_lex[i]
   if ta['status']=='UNKNOWN' or sa['status']=='UNKNOWN':unknown_pairs+=1;continue
   exact_pairs+=1;inter=counts[i];candidate=pair_record(target,source,ta,sa,inter)
   if candidate['exact_full_text']:row['exact_full_text_source_ids'].append(source['sample_id']);full_text_pairs+=1;per_cohort[cohort]['exact_full_text_pairs']+=1
   if candidate['token_sequence_equal']:row['token_sequence_equal_source_ids'].append(source['sample_id']);token_equal_pairs+=1;per_cohort[cohort]['token_sequence_equal_pairs']+=1
   if candidate['candidate_near_Jaccard_at_least08']:row['near_candidate_source_ids'].append(source['sample_id']);near_pairs+=1;per_cohort[cohort]['Jaccard_at_least08_candidate_pairs']+=1
   best=row['pool_top3']
   if len(best)<3 or better(candidate,best[-1]):
    position=0
    while position<len(best) and not better(candidate,best[position]):position+=1
    best.insert(position,candidate)
    if len(best)>3:best.pop()
   for partition in PARTITIONS:
    member=memberships[partition][source['sample_id']]
    if better(candidate,row['by_partition'][partition][member]):row['by_partition'][partition][member]=candidate
  if row['pool_top3']:
   best=row['pool_top3'][0];row['pool_bin']=similarity_bin(best['intersection'],best['union'])
  else:per_cohort[cohort]['UNKNOWN_targets']+=1
  for partition,v in row['by_partition'].items():
   for member in ('fit','val'):
    best=v[member];v[member+'_bin']=similarity_bin(best['intersection'],best['union']) if best else 'UNKNOWN'
  for key,idskey in (('targets_any_exact_full_text','exact_full_text_source_ids'),('targets_any_token_sequence_equal','token_sequence_equal_source_ids'),('targets_any_Jaccard_at_least08','near_candidate_source_ids')):per_cohort[cohort][key]+=bool(row[idskey])
  rows.append(row)
  if (ti+1)%200==0:status('EXACT_LEXICAL_PAIRS_RUNNING',targets_completed=ti+1,pair_candidates_completed=pair_candidates,exact_Jaccard_pairs_completed=exact_pairs,elapsed_lexical_seconds=time.monotonic()-started)
 if pair_candidates!=1323170 or exact_pairs+unknown_pairs!=pair_candidates or len(rows)!=2155:raise RuntimeError('Full1323170 conceptual pairs/2155targets required')
 by_id={r['sample_id']:r for r in rows};bins={'at_utc':now(),'bins':list(BINS),'cohorts':{}}
 for cohort,spec in pub['cohorts'].items():
  ids=spec['ids'];table={'pool':{b:[] for b in BINS},'partitions':{p:{member:{b:[] for b in BINS} for member in ('fit','val')} for p in PARTITIONS}}
  for sid in ids:
   row=by_id[sid];table['pool'][row['pool_bin']].append(sid)
   for p in PARTITIONS:
    for member in ('fit','val'):table['partitions'][p][member][row['by_partition'][p][member+'_bin']].append(sid)
  if sum(len(v) for v in table['pool'].values())!=len(ids) or any(sum(len(v) for v in table['partitions'][p][m].values())!=len(ids) for p in PARTITIONS for m in ('fit','val')):raise RuntimeError('Whole-bin denominators changed')
  bins['cohorts'][cohort]=table
 def case_cmp(a,b):
  av,bv=a['pool_top3'][0],b['pool_top3'][0];delta=av['intersection']*bv['union']-bv['intersection']*av['union']
  if delta:return -1 if delta>0 else 1
  ak,bk=(a['sample_id'],av['source_sample_id']),(b['sample_id'],bv['source_sample_id'])
  return (ak>bk)-(ak<bk)
 cases=[]
 for cohort in COHORTS:
  candidates=sorted((r for r in rows if r['cohort']==cohort and r['pool_top3']),key=cmp_to_key(case_cmp))[:6]
  for row in candidates:
   neighbor=row['pool_top3'][0];target=target_by[row['sample_id']];source=source_by[neighbor['source_sample_id']]
   cases.append({'cohort':cohort,'target_sample_id':target['sample_id'],'source_sample_id':source['sample_id'],'target_task':target['task'],'source_task':source['task'],
    'target_identity':{k:target[k] for k in ('sample_id','task_group','record_id','domain','source_split','source_member','source_row','question_ID')},
    'source_identity':{k:source[k] for k in ('sample_id','task_group','record_id','domain','source_split','source_member','source_row','question_ID')},
    'similarity':neighbor,'source_membership_by_partition':{p:memberships[p][source['sample_id']] for p in PARTITIONS},
    'target_source_path':target['source_path'],'target_source_sha256':target['source_sha256'],'source_source_path':source['source_path'],'source_source_sha256':source['source_sha256'],
    'selection':'highest pool Jaccard, exact ratio; targetID then sourceID ties;6 distinct target per cohort before Gold or score access',
    'Gold_or_model_scores_used_for_selection':0,'automatic_semantic_duplicate_or_leakage_verdict':'NOT_PERFORMED_ROOT_INTERPRETS'})
 counts={'at_utc':now(),'public_task_texts':2769,'source_pool_metadata_texts':614,'historical_target_tasks':2155,'conceptual_pair_candidates':pair_candidates,'exact_Jaccard_pairs_computed':exact_pairs,'UNKNOWN_pair_candidates':unknown_pairs,
  'source_text_status_counts':dict(Counter(r['status'] for r in source_lex)),'target_text_status_counts':dict(Counter(r['status'] for r in target_lex.values())),
  'exact_full_text_pairs':full_text_pairs,'token_sequence_equal_pairs':token_equal_pairs,'Jaccard_at_least08_candidate_pairs':near_pairs,'cohorts':per_cohort,
  'inverted_index_unique_shingles':len(index),'inverted_index_exact_intersection_increment_events':intersection_hits,'all_zero_intersection_candidates_included_by_same_ID_tie':True,
  'elapsed_lexical_seconds':time.monotonic()-started,'new_neural_encoder_texts':0,'targetGold_model_score_reads':0,'all_nearest_ties_compared_by_integer_cross_product_then_source_ID':True,
  'definitions_separate_no_automatic_duplicate_or_leakage_claim':True,'original156_exact0_identity_not_redefined':True}
 write_new(E/'nearest_neighbors.json',{'at_utc':now(),'rows':rows,'targets':2155,'source_pool':614,'pool_top3_per_known_target':True,'full_614_and_fit492_val122_each_partition':True,'sourceTask_only':True,'new_model_scores_or_Gold_access':0})
 write_new(E/'bin_membership.json',bins);write_new(E/'lexical_counts.json',counts);write_new(E/'case_export.json',{'at_utc':now(),'cases':cases,'case_count':len(cases),'case_selection_before_Gold_or_scores':True,'root_interprets_full_public_task_pairs':True})
 write_new(E/'public_text_stage_read_manifest.json',{'at_utc':now(),'phase':'PUBLIC_TEXT','inputs':READS,'all_reads_public_protocol_or_own_public_text_only':True,'parent160_or_Gold_or_model_score_reads':0,'complete_text_outputs_before_score_join':True})
 artifacts={str(E/n):sha(E/n) for n in ('nearest_neighbors.json','bin_membership.json','lexical_counts.json','case_export.json','public_text_stage_read_manifest.json','public_texts.json','frozen_public_manifest.json')}
 write_new(E/'text_proximity_sealed.json',{'at_utc':now(),'status':'PASS','complete_all2155_targets_614_sources_and_fixed_cases_before_scores':True,'public_texts':2769,'source_pool':614,'target_tasks':2155,'pair_candidates':1323170,'cases':len(cases),'artifacts':artifacts,'public_manifest_sha256':sha(E/'frozen_public_manifest.json'),'public_rules_sha256':frozen['rules_sha256'],'lexical_sources':{str(E/n):sha(E/n) for n in ('common161.py','prepare161.py','lexical161.py')},'targetGold_or_model_scores_read':0})
 status('ALL_PUBLIC_TEXT_PROXIMITY_BINS_AND_CASES_SEALED',pair_candidates_completed=1323170,targets_completed=2155,case_count=len(cases),next='Now permit score-cache child to inspect160schema; evaluate161 only after publicsealverified thenfinalize161')
 print(canonical({'Exp161':'public_text_results_sealed','pairs':pair_candidates,'targets':2155,'sources':614,'cases':len(cases),'elapsed_seconds':time.monotonic()-started,'Gold_or_score_reads':0}),flush=True)

if __name__=='__main__':run()

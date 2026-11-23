"""Freeze only public task fields and four exact614-pool memberships."""
from common161 import *

def prepare():
 require_time()
 if time.time()>=datetime.datetime(2026,10,7,1,25,tzinfo=datetime.timezone.utc).timestamp():raise TimeoutError('NO_NEW_WHOLE_EXP161_AFTER0925')
 if sha(E/'approved_plan.json')!=PLAN_SHA:raise RuntimeError('Frozen161 plan changed')
 plan=read(E/'approved_plan.json');p153=read(E153/'protocol.json');p157=read(E157/'protocol.json')
 original=p153['source_ids'];union=set(original['train'])|set(original['validation'])
 if (len(original['train']),len(original['validation']),len(union))!=(492,122,614) or set(original['train'])&set(original['validation']):raise RuntimeError('Original492/122 source membership invalid')
 partitions={'original153':{'fit_ids':original['train'],'val_ids':original['validation']}}
 for block in PARTITIONS[1:]:
  ids=p157['source_splits'][block]['ids']
  if len(ids['train'])!=492 or len(ids['validation'])!=122 or set(ids['train'])&set(ids['validation']) or set(ids['train'])|set(ids['validation'])!=union:raise RuntimeError('All four partitions must use exactsame614 source pool')
  partitions[block]={'fit_ids':ids['train'],'val_ids':ids['validation']}
 paths={'source':p157['source_public_records'],**{c:p153['target_cohorts'][c]['public_records'] for c in COHORTS}}
 allow_public(paths.values());inputs={str(E/'approved_plan.json'):PLAN_SHA,str(E153/'protocol.json'):sha(E153/'protocol.json'),str(E157/'protocol.json'):sha(E157/'protocol.json')};sources=[];targets=[];cohorts={}
 for scope,path in paths.items():
  inputs[str(Path(path))]=sha(path);records=read(path)['records'];seen=set()
  for rec in records:
   sid=rec['sample_id']
   if sid in seen:raise RuntimeError('Duplicate public identity')
   seen.add(sid)
   if scope=='source' and sid not in union:continue
   entry={k:rec.get(k) for k in ('sample_id','task_group','record_id','domain','source_split','source_member','source_row','question_ID','task')}
   entry.update(cohort=scope,source_path=str(Path(path)),source_sha256=inputs[str(Path(path))],original_candidate_count=len(rec['turns']),task_field_only_used_for_lexical_similarity=True)
   (sources if scope=='source' else targets).append(entry)
  if scope=='source':
   if {r['sample_id'] for r in sources}!=union:raise RuntimeError('All614 frozen source pool public task identities required')
  else:
   expected=p153['target_cohorts'][scope];actual=[r['sample_id'] for r in targets if r['cohort']==scope]
   if actual!=expected['sample_ids'] or len(actual)!=expected['n']:raise RuntimeError('Entire original source target domain required')
   cohorts[scope]={'ids':actual,'n':len(actual),'public_records':str(Path(path)),'public_records_sha256':inputs[str(Path(path))]}
 if (len(sources),len(targets),len({r['sample_id'] for r in sources+targets}))!=(614,2155,2769):raise RuntimeError('Exactly2769 distinct public text identities required')
 public={'at_utc':now(),'sources':sources,'targets':targets,'partitions':partitions,'cohorts':cohorts,'source_metadata_texts':614,'historical_target_tasks':2155,'public_task_texts':2769,'task_field_only_no_turn_text_tokens':True,'new_Gold_or_model_score_reads':0}
 write_new(E/'public_texts.json',public)
 rules={'normalization':'NFKC then casefold','tokens':"re.findall(r'\\w+',text,flags=re.UNICODE)",'shingle_width':5,'short1to4':'one fulltoken tuple','zero_tokens':'UNKNOWN never duplicate','similarity':'exact integer intersection/union Jaccard','containment':'intersection/min(shingle counts)','nearest_tie':'source_sample_id lexicographic','bins':list(BINS),'main_partition_binning':'fit492_only','case_rule':'6 distinct targets per cohort by highest full614 poolJaccard, ties targetID then sourceID before score access'}
 write_new(E/'frozen_public_manifest.json',{'at_utc':now(),'experiment':'Exp161','approved_plan_sha256':PLAN_SHA,'inputs':inputs,'public_paths':paths,'public_texts_sha256':sha(E/'public_texts.json'),'rules':rules,'rules_sha256':digest(rules),'partitions_sha256':digest(partitions),'source_ids_sha256':digest(sorted(union)),'target_ids_sha256':digest([r['sample_id'] for r in targets]),'public_text_phase_only':True,'targetGold_model_scores_read':0,'start_before0925_pass':True})
 checkpoint={'at_utc':now(),'experiment':'Exp161','phase':'PUBLIC_TEXT_INPUTS_RULES_IDS_SEALED','approved_plan_sha256':PLAN_SHA,'worktree':str(W),'expected_source_pool':614,'expected_targets':2155,'expected_public_texts':2769,'expected_pair_candidates':1323170,'deadline_utc':'2026-10-07T02:00:00Z','text_stage_targetGold_or_score_reads':0,'all_new_model_neural_rank_Gold_API_fee':0,'next':'lexical161 allpairs then allnearest/bins/cases seal; onlyafterthat enter scorecache phase'}
 write_new(E/'checkpoint.json',checkpoint);write_new(E/'prepare_public_read_manifest.json',READS)
 print(canonical({'Exp161':'public_inputs_sealed','sources':614,'targets':2155,'texts':2769,'expected_pairs':1323170,'source_path_resolved_from157_protocol_153_membership':True}),flush=True)

if __name__=='__main__':prepare()

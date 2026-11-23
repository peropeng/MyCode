"""Fixed casefold substring masks from all public target turns, no score access."""
from common162 import *

def occurrences(raw,folded,marker):
 offsets=[];at=0
 while True:
  index=folded.find(marker,at)
  if index<0:break
  offsets.append(index);at=index+len(marker)
 windows=[];mapping=None
 if offsets and len(raw)!=len(folded):mapping=[i for i,ch in enumerate(raw) for unused in ch.casefold()]
 for index in offsets[:2]:
  start=mapping[index] if mapping is not None else index;end=mapping[index+len(marker)-1]+1 if mapping is not None else index+len(marker)
  left=max(0,start-120);right=min(len(raw),end+120)
  windows.append({'original_start':start,'original_end':end,'window_start':left,'window_end':right,'text':raw[left:right],'from_original_public_string':True,'before_char_limit':120,'after_char_limit':120})
 return {'occurrences':len(offsets),'windows':windows,'window_policy':'first<=2 nonoverlapping occurrences per marker/turn/field, raw original chars±120'}

def run():
 require_time();start=read(E/'start_receipt.json')
 if not start['started_before0940']:raise RuntimeError('SHORT162_NOT_STARTED_BEFORE0940')
 if sha(E/'approved_plan.json')!=PLAN_SHA:raise RuntimeError('Frozen162 plan changed')
 old=read(E161/'frozen_public_manifest.json');paths={c:old['public_paths'][c] for c in COHORTS};allow_public(paths.values())
 inputs={str(E/'approved_plan.json'):PLAN_SHA,str(E/'start_receipt.json'):sha(E/'start_receipt.json'),str(E161/'frozen_public_manifest.json'):sha(E161/'frozen_public_manifest.json')}
 rows=[];cohorts={};counts={'tasks':0,'turns':0,'expected_turn_fields':0,'actual_string_fields_casefolded':0,'non_string_or_missing_fields':0,'raw_characters_casefolded':0,'casefolded_characters':0,'classical_marker_substring_field_scans':0,'marker_string_lengths':{k:len(v) for k,v in MARKERS.items()},'source_training_texts':0};started=time.monotonic()
 for cohort in COHORTS:
  path=paths[cohort]
  if old['inputs'].get(path)!=sha(path):raise RuntimeError('Original161 public target source changed')
  inputs[path]=sha(path);public=read(path)['records'];ids=[]
  for rec in public:
   require_time();sid=rec['sample_id'];ids.append(sid);turns=rec['turns'];counts['tasks']+=1;counts['turns']+=len(turns)
   row={'sample_id':sid,'cohort':cohort,'task_group':rec['task_group'],'record_id':rec.get('record_id'),'n_turns':len(turns),'task_identity':{k:rec.get(k) for k in ('sample_id','record_id','task_group','domain','source_split','source_member','source_row','question_ID')},'source_path':path,'source_sha256':inputs[path],'markers':{k:{'present':False,'matched_turn_ordinals':[],'first_matched_ordinal':None,'last_matched_ordinal':None,'matched_turn_count':0,'total_occurrences':0,'role_counts':{},'matches':[]} for k in MARKERS},'actual_encoded_input_visibility':'UNKNOWN','model_causal_marker_usage':'UNKNOWN'}
   for ordinal,turn in enumerate(turns):
    per_marker={k:{} for k in MARKERS}
    for field in FIELDS:
     counts['expected_turn_fields']+=1;raw=turn.get(field)
     if not isinstance(raw,str):counts['non_string_or_missing_fields']+=1;continue
     folded=raw.casefold();counts['actual_string_fields_casefolded']+=1;counts['raw_characters_casefolded']+=len(raw);counts['casefolded_characters']+=len(folded)
     for marker,label in MARKERS.items():
      counts['classical_marker_substring_field_scans']+=1;found=occurrences(raw,folded,label)
      if found['occurrences']:per_marker[marker][field]=found
    for marker,fields in per_marker.items():
     if not fields:continue
     obj=row['markers'][marker];occ=sum(v['occurrences'] for v in fields.values());role=turn.get('role')
     obj['matches'].append({'ordinal':ordinal,'role':role,'fields':fields,'occurrences_total':occ});obj['matched_turn_ordinals'].append(ordinal);obj['total_occurrences']+=occ
   for marker,obj in row['markers'].items():
    obj['matched_turn_count']=len(obj['matched_turn_ordinals']);obj['present']=bool(obj['matched_turn_ordinals']);obj['first_matched_ordinal']=obj['matched_turn_ordinals'][0] if obj['present'] else None;obj['last_matched_ordinal']=obj['matched_turn_ordinals'][-1] if obj['present'] else None
    obj['role_counts']=dict(Counter(str(m['role']) for m in obj['matches']));obj['matched_turn_proportion']=obj['matched_turn_count']/len(turns) if turns else None
   rows.append(row)
  if len(ids)!=len(set(ids)):raise RuntimeError('Duplicate target public identities')
  cohorts[cohort]={'ids':ids,'n':len(ids),'source_path':path,'source_sha256':inputs[path],'total_turns':sum(r['n_turns'] for r in rows if r['cohort']==cohort)}
  status('PUBLIC_MARKER_MASKS_RUNNING',cohort_completed=cohort,tasks_completed=len(rows),turns_scanned=counts['turns'])
 if (len(rows),counts['tasks'],len({r['sample_id'] for r in rows}))!=(2155,2155,2155):raise RuntimeError('All2155 original target IDs required')
 expected={'coding363':363,'coding170':170,'math155':155,'agentic1467':1467}
 if {c:cohorts[c]['n'] for c in COHORTS}!=expected:raise RuntimeError('Full original source domain denominators required')
 coverage=[]
 for cohort in COHORTS:
  current=[r for r in rows if r['cohort']==cohort]
  for marker in MARKERS:
   present=[r for r in current if r['markers'][marker]['present']];roles=Counter();fields=Counter();occ=0;matched=0
   for row in current:
    obj=row['markers'][marker];roles.update(obj['role_counts']);occ+=obj['total_occurrences'];matched+=obj['matched_turn_count']
    for hit in obj['matches']:fields.update(hit['fields'].keys())
   coverage.append({'cohort':cohort,'marker':marker,'literal':MARKERS[marker],'n_tasks':len(current),'present_tasks':len(present),'absent_tasks':len(current)-len(present),'task_coverage':len(present)/len(current),'total_turns':cohorts[cohort]['total_turns'],'matched_turns':matched,'turn_coverage':matched/cohorts[cohort]['total_turns'],'total_occurrences':occ,'matched_roles_turn_counts':dict(roles),'matched_field_turn_counts':dict(fields),'mean_per_task_matched_turn_proportion':math.fsum(r['markers'][marker]['matched_turn_proportion'] or 0. for r in current)/len(current),'task_marker_pairs_not_independent_task_counts':True})
 selected=[]
 for cohort in COHORTS:
  chosen=sorted((r for r in rows if r['cohort']==cohort and r['markers']['primary']['present']),key=lambda r:r['sample_id'])[:2]
  for row in chosen:selected.append({'sample_id':row['sample_id'],'cohort':cohort,'selection':'lexicographic_first<=2_primary_present_per_cohort_before_Gold_scores','source_path':row['source_path'],'source_sha256':row['source_sha256']})
 origin=[r for r in rows if r['sample_id'].endswith('Algorithm_13500_I:000517')]
 if len(origin)>1:raise RuntimeError('Observed origin must have unique identity')
 if origin and origin[0]['sample_id'] not in {r['sample_id'] for r in selected}:
  row=origin[0];selected.append({'sample_id':row['sample_id'],'cohort':row['cohort'],'selection':'fixed_observed_origin_not_selected_by_score','source_path':row['source_path'],'source_sha256':row['source_sha256']})
 rules={'normalization':'casefold only each originalturn string','markers':MARKERS,'fields':list(FIELDS),'union':'any matching content/action/thought within original ordinal','windows':'first<=2 permarker/turn/field original raw substrings±120 chars','no_metadata_scans':True,'no_marker_rule_predictions':True,'case_order':'source_sample_id lexicographic first<=2 primary present percohort plusfixedobservedorigin'}
 frozen={'at_utc':now(),'experiment':'Exp162','inputs':inputs,'public_paths':paths,'cohorts':cohorts,'source161_public_manifest_sha256':inputs[str(E161/'frozen_public_manifest.json')],'rules':rules,'rules_sha256':digest(rules),'source_training_texts_read':0,'Gold_or_score_reads_before_masks':0}
 write_new(E/'frozen_public_manifest.json',frozen);write_new(E/'marker_masks.json',{'at_utc':now(),'rows':rows,'cohorts':cohorts,'scan_counts':counts,'markers':MARKERS,'fields':list(FIELDS),'all2155tasks_retained':True,'Gold_or_score_reads':0,'metadata_paths_IDs_not_scanned_as_marker_features':True,'no_generated_marker_model_predictions_or_rankings':True})
 write_new(E/'public_coverage.json',{'at_utc':now(),'rows':coverage,'scan_counts':counts,'coverage_rows':8,'task_union_acrossmarkers_not_new_independent_tasks':True,'Gold_or_score_reads':0})
 write_new(E/'public_case_selection.json',{'at_utc':now(),'cases':selected,'case_count':len(selected),'observed_origin_status':'FOUND' if origin else 'NOT_IN_SCOPE','observed_origin_id':origin[0]['sample_id'] if origin else None,'all_selected_before_Gold_or_model_scores':True})
 write_new(E/'public_mask_read_manifest.json',{'at_utc':now(),'phase':'PUBLIC_MASK','inputs':READS,'source_training_texts_read':0,'Gold_or_score_reads_before_seal':0,'elapsed_substring_seconds':time.monotonic()-started})
 artifacts={str(E/n):sha(E/n) for n in ('frozen_public_manifest.json','marker_masks.json','public_coverage.json','public_case_selection.json','public_mask_read_manifest.json','start_receipt.json')}
 write_new(E/'marker_masks_sealed.json',{'at_utc':now(),'status':'PASS','all2155_public_marker_masks_fixed_before_Gold_scores':True,'artifacts':artifacts,'sources':{str(E/n):sha(E/n) for n in ('common162.py','marker162.py')},'target_tasks':2155,'case_count':len(selected),'public_rules_sha256':digest(rules),'Gold_or_scores_read_before_seal':0,'source_training_texts_read':0})
 status('ALL_PUBLIC_MARKER_MASKS_AND_CASES_SEALED',targets_completed=2155,next='Onlynow permit cache-scorephase and codeagent actualschema reads; evaluate162 thenfinalize162')
 print(canonical({'Exp162':'public_masks_sealed','tasks':2155,'turns':counts['turns'],'fields':counts['actual_string_fields_casefolded'],'substring_field_scans':counts['classical_marker_substring_field_scans'],'cases':len(selected),'Gold_or_score_reads':0}),flush=True)

if __name__=='__main__':run()

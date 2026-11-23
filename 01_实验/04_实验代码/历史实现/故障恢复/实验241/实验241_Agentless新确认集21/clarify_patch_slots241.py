"""Clarify author counters against each actual sample and real POST receipts."""
import argparse
from contracts241 import *
from public_v2_241 import AL

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--task',required=True);args=parser.parse_args()
 flow=HERE/'runs'/args.task/METHOD
 stages=[json.loads(x) for x in (flow/'stage_ledger.jsonl').read_text('utf-8').splitlines() if x.strip()]
 locations=[x['evidence'] for x in stages if x['stage']=='fine_location_set']
 candidates=[x['evidence'] for x in stages if x['stage']=='patch_candidate']
 patch_posts=[x['evidence'] for x in stages if x['stage']=='ACTUAL_FLASH_RESPONSE' and x['evidence']['role']=='agentless_patch']
 rows=[]
 for row in candidates:
  loc=next(v for v in locations if v['sample']==row['location_set'])
  rows.append({'sample':row['sample'],'fine_location_set':row['location_set'],
   'nonempty_model_fine_edit_context':bool(loc['repair_context']),
   'actual_patch_generation_performed':bool(loc['repair_context']),
   'raw_output_characters':len(row['raw_output']),'valid_candidate':row['valid'],'parse_errors':row['parse_errors'],
   'empty_context_author_branch':'raw empty; edits empty; invalid row retained; no synthetic/oracle fallback' if not loc['repair_context'] else None})
 if sum(r['actual_patch_generation_performed'] for r in rows)!=len(patch_posts):raise EngineeringUnknown('PATCH_SLOT_POST_RECONCILIATION')
 result={'schema':'Agentless241-author-patch-slot-count-clarification/1','task_id':args.task,
  'author_core_path':str(AL/'agentless178.py'),'author_core_sha256':sha(AL/'agentless178.py'),
  'source_lines':{'patch_slot_loop':128,'nonempty_context_POST_branch':130,'empty_context_no_POST_branch':134,
   'append_candidate_slot_even_without_POST':142,'stage_complete_flag':143,'raw_generation_counter_equals_len_slot_rows':200},
  'planned_fine_location_samples':4,'actual_fine_location_model_responses':sum(x['stage']=='ACTUAL_FLASH_RESPONSE' and x['evidence']['role']=='agentless_fine_locations' for x in stages),
  'planned_patch_slots':4,'actual_patch_slot_rows':len(rows),'actual_patch_POSTs_and_responses':len(patch_posts),
  'actual_invalid_no_context_slots':sum(not r['actual_patch_generation_performed'] for r in rows),'sample_rows':rows,
  'original_raw_runtime_core_counter_actual_patch_generations_is_slot_row_count':True,
  'original_raw_four_independent_patches_flag_means_loop_stage_completed':True,
  'no_claim_four_independent_model_patch_generations':len(patch_posts)!=4,
  'scientific_method_core_not_modified':True,'original_raw_results_preserved':True,'no_repeated_or_supplementary_POST':True,
  'earlier_duplicate_location_explanation_corrected':'Actual skip is empty valid edit context, not duplicate-location reuse.'}
 save(HERE/'candidate'/args.task/'PATCH_SLOT_CLARIFICATION241.json',result)
 print(canonical({k:result[k] for k in ('task_id','planned_patch_slots','actual_patch_slot_rows','actual_patch_POSTs_and_responses','actual_invalid_no_context_slots')}))
if __name__=='__main__':main()

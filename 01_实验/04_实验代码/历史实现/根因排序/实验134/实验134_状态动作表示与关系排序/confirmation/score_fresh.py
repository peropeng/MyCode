"""All-cohort sealed-only scoring; parses exactly selected fresh label rows once."""
from shared import *
import paired_stats
import re

def main():
    p=verify();seal=read(T/'prediction_seal.json')
    if seal['protocol_sha256']!=sha(T/'protocol.json') or seal['predictions_sha256']!=sha(T/'predictions.json'):raise RuntimeError('whole_confirmation_prediction_seal_changed')
    records=read(T/'fresh_public_records.json')['records'];rows=read(T/'predictions.json')['records']
    if [r['sample_id'] for r in rows]!=p['sample_ids'] or len(rows)!=p['n_independent_tasks'] or any(set(r['conditions'])!=set(CONDITIONS) for r in rows):raise RuntimeError('all_scheduled_tasks_conditions_required_before_Gold')
    if seal['total_scheduled_rows']!=len(rows)*len(CONDITIONS):raise RuntimeError('all_scheduled_row_count_mismatch')
    public={r['sample_id']:r for r in records}
    for row in rows:
        if row['public_record_sha256']!=digest(public[row['sample_id']]):raise RuntimeError('sealed_public_record_changed')
    vault=ROOT/'工作区/1005-exp132-paper-three/scratch/exp132/agentracer_private_step_labels.jsonl'
    if sha(vault)!=p['source_private_mapping_sha256']:raise RuntimeError('private_original_mapping_source_changed')
    if (T/'comparison.json').exists():raise RuntimeError('confirmation_already_scored_no_repeated_selection')
    wanted={r['record_id']:r['sample_id'] for r in records};gold={}
    with vault.open('rb') as f:
        for line in f:
            identity=re.search(rb'"record_id"\s*:\s*"([^"\\]+)"',line)
            if not identity or identity.group(1).decode('utf-8') not in wanted:continue
            mapped=__import__('json').loads(line);sid=wanted[mapped['record_id']]
            if sid in gold:raise RuntimeError('duplicate_selected_original_label')
            gold[sid]=mapped['zero_based_public_ordinal']
    if set(gold)!=set(public):raise RuntimeError('selected_fresh_labels_missing')
    outcomes={c:[] for c in CONDITIONS};per_task=[]
    for row in rows:
        sid=row['sample_id'];record=public[sid];target=gold[sid]
        if type(target) is not int or not 0<=target<len(record['turns']):raise RuntimeError('original_Gold_outside_raw_trajectory')
        for condition,pred in row['conditions'].items():
            valid=pred.get('valid') is True;step=pred.get('chosen_step') if valid else None
            if valid and (type(step) is not int or not 0<=step<len(record['turns'])):raise RuntimeError('native_prediction_outside_original_ordinals')
            hit=bool(valid and step==target);outcomes[condition].append(int(hit))
            order=pred.get('order');complete=pred.get('native_complete_ranking') is True and isinstance(order,list) and sorted(order)==list(range(len(record['turns'])))
            per_task.append({'sample_id':sid,'record_id':record['record_id'],'task_group':row['task_group'],'domain':record['domain'],
                'condition':condition,'valid':valid,'chosen_step':step,'exact_original_step_hit':hit,
                'role_hit':bool(valid and pred.get('predicted_role')==record['turns'][target]['role']),
                'MRR':1/(order.index(target)+1) if complete and valid else None,
                'Top3':target in order[:3] if complete and valid else None,
                'native_complete_ranking':complete,'failure':pred.get('error'),
                'original_Gold_and_predicted_ordinals_unchanged':True})
    def metric(condition,domain=None):
        selected=[r for r in per_task if r['condition']==condition and (domain is None or r['domain']==domain)]
        n=len(selected);hits=sum(r['exact_original_step_hit'] for r in selected)
        return {'n_independent_tasks':n,'hits':hits,'exact_step_Top1':hits/n if n else None,
            'valid_predictions':sum(r['valid'] for r in selected),'invalid_predictions':sum(not r['valid'] for r in selected),
            'role_accuracy':sum(r['role_hit'] for r in selected)/n if n else None,
            'MRR':sum(r['MRR'] for r in selected)/n if n and all(r['MRR'] is not None for r in selected) else None,
            'Top3':sum(r['Top3'] for r in selected)/n if n and all(r['Top3'] is not None for r in selected) else None,
            'single_choice_MRR_not_fabricated':True}
    table={c:metric(c) for c in CONDITIONS};domains={d:{c:metric(c,d) for c in CONDITIONS} for d in ('coding','math')}
    primary=paired_stats.family({'B__vs__'+c:(outcomes['B'],outcomes[c]) for c in PRIMARY_COMPARATORS},13)
    secondary=paired_stats.family({right+'__vs__'+left:(outcomes[right],outcomes[left]) for left,right in SECONDARY_PAIRS},9)
    strongest_hits=max(table[c]['hits'] for c in PRIMARY_COMPARATORS);strongest=[c for c in PRIMARY_COMPARATORS if table[c]['hits']==strongest_hits]
    result={'at_utc':now(),'schema':'Exp134-frozen-B-complete-fresh-confirmation-score/1.0','primary_method':'B','n_independent_tasks':len(records),
        'conditions_scheduled':len(CONDITIONS),'all_scheduled_rows':len(per_task),'condition_table':table,'domain_table':domains,
        'all13_primary_comparator_Holm':primary,'secondary9_component_Holm':secondary,'all3_seed_conditions_fully_reported':True,
        'strongest_predeclared_baseline_or_control':strongest,'strongest_comparator_hits':strongest_hits,
        'B_hits':table['B']['hits'],'B_point_leads_all_predeclared_comparators':table['B']['hits']>strongest_hits,
        'B_reliable_lead_all_comparators':all(r['statistically_supported_lead'] for r in primary.values()),
        'per_task_outcomes':per_task,'invalids_kept_in_full_denominator':True,'all_predictions_sealed_before_labels':True,
        'primary_B_not_replaced_by_secondary_winner':True,'projection_controls_not_own_innovation':True,
        'metric_target':'agreement with released original annotation, not executed proof of persistent causal failure',
        'model_seal_sha256':p['model_seal_sha256'],'protocol_sha256':sha(T/'protocol.json'),'prediction_seal_sha256':sha(T/'prediction_seal.json'),
        'execution_resource':read(T/'execution_receipt.json')}
    write(T/'comparison.json',result)
    write(T/'Gold_evaluation_receipt.json',{'at_utc':now(),'selected_fresh_labels_used':len(gold),'unselected_label_values_parsed':0,
        'whole_scope_verified_before_labels':True,'comparison_sha256':sha(T/'comparison.json'),'original_annotation_target_unchanged':True})
    packet={'at_utc':now(),'phase_complete':True,'overall_research_complete':False,'primary':'B','n':len(records),
        'ensemble_and_baselines':{c:table[c] for c in ARMS+PAID+tuple(PROJECTED)+PRIORS},
        'strongest_comparators':strongest,'B_hits':table['B']['hits'],'strongest_hits':strongest_hits,
        'B_point_lead':result['B_point_leads_all_predeclared_comparators'],'B_reliable_lead':result['B_reliable_lead_all_comparators'],
        'primary_family':primary,'secondary_components':secondary,'model_parameters':read(E/'training_protocol.json')['parameters'],
        'full_comparison':str(T/'comparison.json'),'execution_resource':result['execution_resource'],
        'minimum_required_main_decision':'Interpret complete saved evidence and determine opening summary or further scientific design; executor does not declare broad dominance'}
    write(T/'main_decision_packet.json',packet)
    CORE.status('EXP134_CONFIRMATION_SCORED_AWAITING_MAIN_INTERPRETATION',current_pid=None,current_command=None,
        fresh_confirmation={'completed_tasks':len(records),'total_tasks':len(records),'scored_tasks':len(records),'selected_fresh_labels_used':len(records)},
        confirmation_comparison=str(T/'comparison.json'),confirmation_decision_packet=str(T/'main_decision_packet.json'),
        primary_B_hits=table['B']['hits'],strongest_comparator_hits=strongest_hits,strongest_comparators=strongest,
        next_executable_command='Main chat interprets exact paired evidence; no new scientific actions scheduled')
    print(canonical({'fresh_tasks_scored':len(records),'B_hits':table['B']['hits'],'baseline_and_control_hits':{c:table[c]['hits'] for c in PRIMARY_COMPARATORS},
        'B_point_lead_all':result['B_point_leads_all_predeclared_comparators'],'B_reliable_lead_all':result['B_reliable_lead_all_comparators']}),flush=True)

if __name__=='__main__':main()

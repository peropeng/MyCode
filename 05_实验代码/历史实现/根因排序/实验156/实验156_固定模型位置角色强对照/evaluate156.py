"""Locked cached neural views versus five fixed position/role controls."""
import csv
import math
from fractions import Fraction
from collections import defaultdict
import numpy as np
from common import *
import paired_stats156 as statistics

EVALUATION_FILES=("evaluate156.py","finalize156.py","paired_stats156.py")
FAMILY_KEYS=tuple(f"{VIEW_SLUGS[v]}_{scope}_AB_GLOBAL_vs_{c}" for v in VIEWS for scope in ("coding363","AF716") for c in CONTROLS)
AF_LABEL_ACCESS_SCOPE={"fit":"Each prior consumes only its current refit IDs after mainline fit-ID gating; all731 labels share the historical file", "evaluation":"This evaluator joins target labels only after all18816 new outputs are sealed"}


def demand(ok, message):
    if not ok:
        raise RuntimeError(message)

def public_by(path, ids):
    records = read(path)['records']
    demand([r['sample_id'] for r in records]==ids, 'Original public ID/order scope changed')
    by = {r['sample_id']:r for r in records}
    demand(len(by)==len(ids), 'Duplicate public sample IDs')
    return by

def outcome(sid, pred, record, target, condition, legacy=False):
    n = len(record['turns'])
    demand(type(target) is int and 0<=target<n, 'Original Gold ordinal out of range')
    valid = pred.get('valid') is True
    step = pred.get('chosen_step', pred.get('predicted_step')) if valid else None
    order = pred.get('order',pred.get('ranking'))
    full = isinstance(order,list) and len(order)==n and all(type(x) is int for x in order) and sorted(order)==list(range(n))
    if valid:
        demand(type(step) is int and 0<=step<n, 'Chosen step outside original zero-based coordinates')
        if not legacy:
            demand(full and pred.get('native_complete_ranking') is True and order[0]==step, 'Current valid prediction needs full original-coordinate rank')
        elif full:
            demand(order[0]==step, 'Historical native rank/chosen step mismatch')
    role = record['turns'][step]['role'] if valid else None
    if pred.get('predicted_role') is not None and valid:
        demand(pred['predicted_role']==role, 'Predicted role not derived from public chosen step')
    rr = 1/(order.index(target)+1) if valid and full else 0. if not valid and not legacy else None
    top3 = bool(target in order[:3]) if valid and full else False if not valid and not legacy else None
    return {'sample_id':sid,'task_group':record['task_group'],'record_id':record.get('record_id'),
            'condition':condition,'raw_steps':n,'valid':valid,'chosen_step':step,
            'original_Gold_ordinal':target,'Top1':int(valid and step==target),
            'exact_original_step_hit':bool(valid and step==target),
            'role_hit':bool(valid and role==record['turns'][target]['role']),
            'MRR':rr,'Top3':top3,'native_complete_ranking':full,
            'failure':pred.get('error',pred.get('source_status')) if not valid else None}

def summary(rows):
    n = len(rows)
    grouped = defaultdict(list)
    for row in rows:
        grouped[row['task_group']].append(row)
    metrics = {}
    group_metrics = {}
    for metric in ('Top1','MRR','Top3'):
        available = n>0 and all(r[metric] is not None for r in rows)
        metrics[metric] = sum(float(r[metric]) for r in rows)/n if available else None
        group_metrics[metric] = sum(sum(float(r[metric]) for r in rs)/len(rs) for rs in grouped.values())/len(grouped) if available else None
    return {'n':n,'records':n,'groups':len(grouped),'available':bool(n),
            'hits':sum(r['Top1'] for r in rows), 'raw_record_hits':sum(r['Top1'] for r in rows),
            'Top1':metrics['Top1'],'exact_step_Top1':metrics['Top1'],'MRR':metrics['MRR'],'Top3':metrics['Top3'],
            'record_equal':metrics,'group_equal':group_metrics,
            'valid_predictions':sum(r['valid'] for r in rows),'invalid_predictions':sum(not r['valid'] for r in rows),
            'native_complete_rank_predictions':sum(r['native_complete_ranking'] for r in rows),
            'role_accuracy':sum(r['role_hit'] for r in rows)/n if n else None,
            'all_failures_kept_in_original_denominator':True,
            'unavailable_rank_metrics_are_null_not_fabricated':True}

def source_gold(p,label_files):
    wanted = defaultdict(set)
    for spec in p['target_cohorts'].values():
        wanted[spec['label_source']].update(spec['sample_ids'])
    cache = {}
    for path,ids in wanted.items():
        spec = next(v for v in p['target_cohorts'].values() if v['label_source']==path)
        demand(sha(path)==spec['label_source_sha256'], 'Historical source Gold binding changed')
        saved = read(path)
        demand(not saved.get('errors'), 'Saved original annotation mapping errors')
        rows = saved['labels']
        cache[path] = {r['sample_id']:r[spec['label_key']] for r in rows}
        demand(len(cache[path])==len(rows) and ids<=set(cache[path]), 'Original annotation IDs missing/duplicate')
        label_files[path] = sha(path)
    return cache

def metadata_prefix(path,wanted):
    """Decode only top-level reference fields, stopping before giant outcome copies."""
    decoder = json.JSONDecoder();buffer = '';position = 0;result = {}
    with Path(path).open(encoding='utf-8-sig') as stream:
        def more():
            nonlocal buffer,position
            chunk = stream.read(65536)
            demand(bool(chunk), 'Incomplete historical comparison metadata')
            buffer = buffer[position:]+chunk;position = 0
        def space():
            nonlocal position
            while True:
                while position<len(buffer) and buffer[position].isspace():
                    position += 1
                if position<len(buffer):
                    return
                more()
        def value():
            nonlocal position
            space()
            while True:
                try:
                    v,end = decoder.raw_decode(buffer,position);position = end;return v
                except json.JSONDecodeError:
                    more()
        space();demand(buffer[position]=='{','Historical comparison must be an object');position += 1
        while set(result)!=set(wanted):
            key = value();space();demand(buffer[position]==':','Historical metadata missing colon');position += 1
            demand(key not in ('per_task_outcomes','new_control_per_task_outcomes','reused153_per_task_outcomes'),
                   'Required historical metadata must precede giant outcome fields')
            v = value()
            if key in wanted:
                result[key] = v
            if set(result)==set(wanted):
                break
            space();demand(buffer[position]==',','Historical required reference field missing');position += 1
    return result

def counterexamples(main,other,ids,by,gold,main_name,other_name):
    rows = []
    for sid in ids:
        a,b = main[sid],other[sid]
        if a['Top1']==b['Top1']:
            continue
        rows.append({'sample_id':sid,'task_group':by[sid]['task_group'],'record_id':by[sid].get('record_id'),
                     'original_Gold_ordinal':gold[sid],'main_method':main_name,'other_method':other_name,
                     'main_chosen_step':a['chosen_step'],'other_chosen_step':b['chosen_step'],
                     'main_hit':bool(a['Top1']),'other_hit':bool(b['Top1']),
                     'status':'rescued' if a['Top1'] else 'damaged','public_record_sha256':digest(by[sid])})
    return {'rescued_records':sum(r['status']=='rescued' for r in rows),'damaged_records':sum(r['status']=='damaged' for r in rows),
            'records':rows,'descriptive_only':True,'direction':'Locked cached model view minus named simple control',
            'AF_duplicate_records_not_independent_groups':True}

def compact_pairs(family):
    return {k:{field:v for field,v in row.items() if field!='paired_group_differences'} for k,row in family.items()}


def expected_prediction_files(p):
    paths = {control_prediction_path(scope,c) for scope in COHORTS for c in CONTROLS}
    paths |= {control_prediction_path('AF',c) for c in CONTROLS}
    paths |= {control_prediction_path('AF',c,s) for c in PRIORS for s in AF_SEEDS}
    paths |= {E/'results/AF/folds'/c/f"{r['seed']}_{r['outer']}.json" for c in PRIORS for r in p['AF_schedule']}
    return {str(path.resolve()) for path in paths}


def fit_table_schedule(p):
    for control in PRIORS:
        yield control,'source',None,None,p['source_fit_ids'],p['source_validation_ids'],E/'fits/source'/(control+'.json')
        for row in p['AF_schedule']:
            yield control,'AF',row['seed'],row['outer'],row['refit_ids'],row['held_ids'],E/'fits/AF'/control/f"{row['seed']}_{row['outer']}.json"


def verify_seals():
    """Require every unique new output before reading target or cached score objects."""
    global_path = E/'results/all_predictions_sealed.json'
    demand(global_path.is_file(), 'ALL18816_NEW_CONTROL_OUTPUTS_SEALED_REQUIRED_BEFORE_EVALUATION')
    demand(sha(E/'approved_plan.json')==PLAN_SHA,'Approved156 plan changed')
    p = read(E/'protocol.json');ph = sha(E/'protocol.json')
    demand(p['primary']==PRIMARY and p['approved_plan_sha256']==PLAN_SHA and tuple(p['controls'])==CONTROLS
           and tuple(p['priors'])==PRIORS and tuple(p['locked_model_views'])==VIEWS and p['view_slugs']==VIEW_SLUGS,
           'Locked156 primary/controls/views changed')
    demand((p['expected_new_ranker_outputs'],p['source_new_outputs'],p['AF_new_outputs'],p['expected_prediction_files'],p['expected_analytic_fit_tables'])
           ==(18816,10775,8041,61,32), 'All original analytic fits/outputs required')
    demand(len(p['source_fit_ids'])==492 and len(p['source_validation_ids'])==122
           and not set(p['source_fit_ids'])&set(p['source_validation_ids']), 'Source492-only fit and excluded122 validation required')
    demand(tuple(p['AF_seeds'])==AF_SEEDS and len(p['AF_schedule'])==15
           and {(r['seed'],r['outer']) for r in p['AF_schedule']}=={(s,o) for s in AF_SEEDS for o in range(5)},
           'Exactly original3 AF schedules/15 folds required')
    demand(p['baseline_parameters']['relative_bins']==10 and p['baseline_parameters']['smoothing']==1,
           'Fixed10 bins/+1 smoothing required')
    for field in ('rule_sources_sha256','inputs','protected_old_files_sha256','unchanged_neural_weight_manifests_sha256'):
        check_hashes(p[field])
    zero_fields = ('new_optimization_training','new_neural_models','new_neural_forward','new_encoder','new_API','new_downloads','new_Gold','new_independent_tasks')
    demand(all(p[k]==0 for k in zero_fields) and p['fee_CNY']=='0' and p['no_neural_weight_or_embedding_deserialization_or_bytes_used_by_rules'],
           'Entire156 analytic-only/no new neural compute contract required')
    fit = read(E/'fit_isolation_receipt.json');all_seal = read(global_path)
    source,AF = read(E/'results/source_predictions_sealed.json'),read(E/'results/AF_predictions_sealed.json')
    demand(fit['status']=='PASS' and fit['analytic_count_fit_tables']==32 and len(fit['tables'])==32
           and fit['all32_fit_ID_gates'] and fit['held_labels_consumed_by_corresponding_table']==fit['source122_validation_labels_used']==0
           and fit['fit_group_weight_total_equals_group_count'] and fit['protocol_sha256']==ph,
           'All32 actual fit tables and held/validation label isolation required')
    table_hashes = {str(Path(r['path']).resolve()):r['sha256'] for r in fit['tables']}
    demand(set(table_hashes)=={str(Path(path).resolve()) for path in p['fit_table_paths']}
           =={str(path.resolve()) for *_,path in fit_table_schedule(p)}, 'Exact32 frozen fit table paths required')
    check_hashes(table_hashes)
    for control,suite,seed,outer,fit_ids,held_ids,path in fit_table_schedule(p):
        table = read(path)
        demand(table['control']==control and table['suite']==suite and table.get('seed')==seed and table.get('outer')==outer
               and table['fit_ids']==table['consumed_label_ids']==fit_ids and table['held_ids']==held_ids
               and table['fit_ids_sha256']==table['consumed_label_ids_sha256']==digest(fit_ids)
               and table['held_ids_sha256']==digest(held_ids) and not set(fit_ids)&set(held_ids), 'Exact fit-ID gate/table identity required')
        demand(table['fit_ID_gate'] and table['held_label_values_used_for_fit']==table['validation_or_target_based_parameter_selection']==0
               and table['new_optimization_training']==table['new_neural_models']==0 and table['smoothing']==1
               and table['relative_bins']==(10 if control==PRIORS[1] else None), 'Prior parameter/held-isolation contract changed')
    demand(all_seal['all_fixed_outputs_sealed'] and (all_seal['outputs'],all_seal['source_outputs'],all_seal['AF_outputs'],all_seal['prediction_files'],all_seal['analytic_fit_tables'])
           ==(18816,10775,8041,61,32),'Complete18816 new output seal required')
    demand(all_seal['protocol_sha256']==source['protocol_sha256']==AF['protocol_sha256']==ph
           and all_seal['fit_receipt_sha256']==source['fit_receipt_sha256']==sha(E/'fit_isolation_receipt.json')
           and all_seal['source_seal_sha256']==sha(E/'results/source_predictions_sealed.json')
           and all_seal['AF_seal_sha256']==sha(E/'results/AF_predictions_sealed.json'), 'Fit/protocol/source/AF/global seal chain broken')
    demand(all_seal['target_labels_joined']==source['target_labels_joined']==AF['target_labels_joined']==0
           and all_seal['new_neural_forward']==0, 'Premature target evaluator joins or new neural forward marker')
    demand((source['outputs'],AF['outputs'],AF['records'],AF['groups'],AF['native_deterministic_rule_outputs'],AF['native_prior_OOF_outputs'],AF['prior_ensemble_outputs'],AF['OOF_join_JSON_copy_entries_not_new_outputs'])
           ==(10775,8041,731,716,2193,4386,1462,4386), 'Native/ensemble/OOF-copy accounting changed')
    files = {str(Path(path).resolve()):h for path,h in all_seal['files'].items()}
    demand(len(files)==61 and set(files)==expected_prediction_files(p)
           and files=={**{str(Path(path).resolve()):h for path,h in source['files'].items()},
                      **{str(Path(path).resolve()):h for path,h in AF['files'].items()}}, 'Exactly20 source/41 AF sealed JSON files required')
    check_hashes(files)
    demand((E/'protocol.json').stat().st_mtime_ns<=min(Path(path).stat().st_mtime_ns for path in table_hashes)
           and max(Path(path).stat().st_mtime_ns for path in table_hashes)<=(E/'fit_isolation_receipt.json').stat().st_mtime_ns<=min(Path(path).stat().st_mtime_ns for path in files)
           <=global_path.stat().st_mtime_ns,'Freeze/fit/all-inference/global-seal chronology violated')
    parents = read(E/'approved_plan.json')['parents']
    for root,key in [(E153,'packet153_sha256'),(E154,'packet154_sha256'),(E155,'packet155_sha256')]:
        demand(sha(root/'main_decision_packet.json')==parents[key], 'Immutable parent decision packet changed')
    return p,{'all':all_seal,'source':source,'AF':AF,'fit':fit}


def freeze_evaluation():
    value = {'at_utc':now(),'experiment':'Exp156','primary':PRIMARY,'underlying_locked_primary':'AB_GLOBAL','approved_plan_sha256':PLAN_SHA,
             'sources':{str(E/name):sha(E/name) for name in EVALUATION_FILES},'protocol_sha256':sha(E/'protocol.json'),
             'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),'joint_Holm30':list(FAMILY_KEYS),
             'all30_tests_kept_including_duplicate_AF_controls':True,'bootstrap_seed':statistics.BOOTSTRAP_SEED,'bootstrap_draws':statistics.BOOTSTRAP_DRAWS,
             'supported_lead':'difference>0 and Holm<.05 and familyCI lower>0','family_binary_interval_alpha':statistics.ALPHA/30,
             'old_SF_p_values_reference_only_no_new_SF_p_test':True,'no_old_score_or_target_Gold_parse_by_this_evaluator_before18816_seal':True,
             'AF_label_access_scope':AF_LABEL_ACCESS_SCOPE,'new_neural_compute':0}
    path = E/'evaluation_code_seal.json'
    if path.exists():
        old = read(path)
        demand({k:v for k,v in old.items() if k!='at_utc'}=={k:v for k,v in value.items() if k!='at_utc'}, 'Frozen156 evaluator changed')
    else:
        write_new(path,value)


def verify_prediction_payloads(p,source_by,AF_ids,AF_by):
    ph = sha(E/'protocol.json')
    for scope in COHORTS:
        ids = p['target_cohorts'][scope]['sample_ids']
        for control in CONTROLS:
            saved = read(control_prediction_path(scope,control));prediction_contract(saved,ids,source_by[scope],control)
            demand(saved['cohort']==scope and saved['protocol_sha256']==ph and saved['target_labels_joined']==0,
                   'Source prediction payload protocol/target gate changed')
            if control in PRIORS:
                table_path = E/'fits/source'/(control+'.json');table = read(table_path)
                demand(saved['fit_table_sha256']==sha(table_path), 'Source control/fitted count binding changed')
                demand(all(v['fit_ids_sha256']==table['fit_ids_sha256'] and v['count_table_sha256']==digest(table)
                           for v in saved['predictions'].values()), 'Source native prior/count-table identity changed')
            else:
                demand(saved['fit_table_sha256'] is None,'Deterministic control must not fit')
    for control in CONTROLS[:3]:
        saved = read(control_prediction_path('AF',control));prediction_contract(saved,AF_ids,AF_by,control)
        demand(saved['protocol_sha256']==ph and saved['target_labels_joined']==0 and saved['generated_once_not_per_fold'],
               'AF deterministic control must generate once without target joins')
    for control in PRIORS:
        for seed in AF_SEEDS:
            joined = {}
            for row in p['AF_schedule']:
                if row['seed']!=seed:
                    continue
                saved = read(E/'results/AF/folds'/control/f"{seed}_{row['outer']}.json")
                table_path = E/'fits/AF'/control/f"{seed}_{row['outer']}.json";table = read(table_path)
                prediction_contract(saved,row['held_ids'],AF_by,control)
                demand(saved['seed']==seed and saved['outer']==row['outer'] and saved['protocol_sha256']==ph
                       and saved['fit_table_sha256']==sha(table_path) and saved['held_ids_sha256']==digest(row['held_ids'])
                       and saved['target_labels_joined']==0 and not set(joined)&set(saved['predictions']), 'AF fold fit/held/protocol gate changed')
                demand(all(v['fit_ids_sha256']==table['fit_ids_sha256'] and v['count_table_sha256']==digest(table)
                           for v in saved['predictions'].values()), 'AF native prior/count-table identity changed')
                joined.update(saved['predictions'])
            saved = read(control_prediction_path('AF',control,seed))
            demand(saved['control']==control and saved['seed']==seed and saved['protocol_sha256']==ph and saved['target_labels_joined']==0
                   and saved['exactly_one_OOF_per_record'] and saved['joined_entries_not_new_outputs']==731
                   and set(joined)==set(AF_ids) and joined==saved['predictions'],'AF seed join must be an unchanged copy of nativefold outputs')
        saved = read(control_prediction_path('AF',control))
        prediction_contract(saved,AF_ids,AF_by,control)
        demand(saved['protocol_sha256']==ph and saved['target_labels_joined']==0 and saved['shared_by_both155_blocks_without_new_outputs'],
               'AF prior ensemble shared once across cached views')


def prediction_contract(saved,ids,by,control):
    demand(saved['control']==control and set(saved['predictions'])==set(ids), 'Complete original control scope required')
    for sid,pred in saved['predictions'].items():
        if pred.get('valid') is not True:
            continue
        n = len(by[sid]['turns']);order = pred['order'];prob = pred['probabilities']
        demand(type(pred['chosen_step']) is int and sorted(order)==list(range(n)) and order[0]==pred['chosen_step']
               and pred['native_complete_ranking'] is True, 'Current native original-coordinate complete rank required')
        demand(len(prob)==n and all(type(v) in (float,int) and math.isfinite(v) and 0<=v<=1 for v in prob)
               and abs(math.fsum(prob)-1)<1e-12, 'Control probability normalization changed')


def score_controls(scope,ids,by,gold):
    table,rows,canonical_values,raw,all_outcomes = {},{},{},{},[]
    for control in CONTROLS:
        variants = (None,) if scope!='AF' or control not in PRIORS else tuple(AF_SEEDS)+(None,)
        seed_predictions = []
        for seed in variants:
            name = control if seed is None else control+'/seed_'+str(seed)
            saved = read(control_prediction_path(scope,control,seed));prediction_contract(saved,ids,by,control)
            predictions = saved['predictions']
            if seed is not None:
                demand(saved['seed']==seed, 'AF prior original schedule seed changed')
                seed_predictions.append(predictions)
            elif scope=='AF' and control in PRIORS:
                demand(saved['seeds']==list(AF_SEEDS) and saved['all3_fixed_schedules_retained'], 'Exactly3 prior OOF schedules required')
                for sid,pred in predictions.items():
                    allvalid = all(v[sid]['valid'] for v in seed_predictions)
                    demand(pred['valid']==allvalid, 'AF prior ensemble invalid handling changed')
                    if allvalid:
                        exact = [sum((Fraction(v[sid]['probability_exact'][i]['numerator'],v[sid]['probability_exact'][i]['denominator'])
                                      for v in seed_predictions),Fraction())/3 for i in range(len(by[sid]['turns']))]
                        prob = [float(v) for v in exact]
                        encoded = [{'numerator':v.numerator,'denominator':v.denominator} for v in exact]
                        demand(all(abs(x-y)<=1e-15 for x,y in zip(prob,pred['probabilities'])) and encoded==pred['probability_exact']
                               and sorted(range(len(prob)),key=lambda i:(-exact[i],i))==pred['order'],
                               'AF prior saved3-schedule mean and exact tie-safe rank changed')
            values = {sid:outcome(sid,predictions[sid],by[sid],gold[sid],name) for sid in ids}
            for row in values.values():
                row.update(cohort=scope,new156_control_output=True,control=control,original_schedule_seed=seed)
            table[name],rows[name] = summary(list(values.values())),list(values.values())
            all_outcomes.extend(values.values())
            if seed is None:
                canonical_values[control],raw[control] = values,predictions
    return table,rows,canonical_values,raw,all_outcomes


def control_coverage(ids,by,values):
    present = {s:any(t['role'].strip().casefold()=='engineer' for t in by[s]['turns']) for s in ids}
    length_one = sum(len(by[s]['turns'])==1 for s in ids)
    return {'records':len(ids),'groups':len({by[s]['task_group'] for s in ids}),
            'Engineer_present_records':sum(present.values()),'Engineer_absent_records':sum(not v for v in present.values()),
            'single_candidate_records':length_one,'roles_only_strip_casefold_exact_engineer':True,
            'AF_anonymous_role_not_reverse_mapped':True,
            'per_control':{c:{'whole_scope_predictions':len(values[c]),'valid':sum(values[c][s]['valid'] for s in ids),
                              'invalid_kept':sum(not values[c][s]['valid'] for s in ids),
                              'native_complete_rankings':sum(values[c][s]['native_complete_ranking'] for s in ids),
                              'FIRST_fallback_records':sum(not v for v in present.values()) if c=='FIRST_ENGINEER' else None,
                              'original_full_denominator':len(ids)} for c in CONTROLS}}


def duplicate_controls(ids,predictions):
    rows = []
    fields = ('valid','chosen_step','order','probabilities')
    for index,left in enumerate(CONTROLS):
        for right in CONTROLS[index+1:]:
            if all(all(predictions[left][sid].get(k)==predictions[right][sid].get(k) for k in fields) for sid in ids):
                rows.append({'left':left,'right':right,'records':len(ids),'native_output_fields_identical':list(fields),
                             'all30_prespecified_tests_retained_conservatively':True})
    return rows


def view_summary(parent,scope,view,arm):
    if view==VIEWS[0]:
        return parent['source_cohorts'][scope]['condition_table'][arm] if scope!='AF' else parent['AF']['all731_record_equal_and716_group_equal'][arm]
    block = 'block_A' if view==VIEWS[1] else 'block_B'
    name = arm+'/'+block
    return parent['source_cohorts'][scope]['condition_table'][name] if scope!='AF' else parent['AF']['all731_record_equal_and716_group_equal'][name]


def score_views(scope,ids,by,gold,old153,old155):
    main_table,SF_table,main_values,SF_values = {},{},{},{}
    for view in VIEWS:
        parent = old153 if view==VIEWS[0] else old155
        for arm,table,values in [('AB_GLOBAL',main_table,main_values),('SF_REF',SF_table,SF_values)]:
            saved = read(view_prediction_path(scope,view,arm));predictions = saved['predictions']
            demand(saved['arm']==arm and set(predictions)==set(ids) and saved['all3_fixed_seeds_retained']
                   and len(saved['seeds'])==3, 'Fixed cached neural view scope changed')
            if view==VIEWS[0]:
                demand(saved['seeds']==list(SOURCE_NEURAL_153_SEEDS if scope!='AF' else AF_NEURAL_153_SEEDS), 'Original153 fixed triple changed')
            else:
                block = 'block_A' if view==VIEWS[1] else 'block_B'
                expected = SOURCE_NEURAL_155_SEEDS if scope!='AF' else AF_NEURAL_155_SEEDS
                demand(saved['replication_block']==block and saved['seeds']==list(expected[:3] if block=='block_A' else expected[3:]),
                       'Original155 fixed block changed')
            rows = {s:outcome(s,predictions[s],by[s],gold[s],view if arm=='AB_GLOBAL' else view.replace('AB_GLOBAL','SF_REF')) for s in ids}
            result = summary(list(rows.values()))
            demand(result==view_summary(parent,scope,view,arm), 'Cached neural metrics/original coordinates changed')
            for row in rows.values():
                row.update(cohort=scope,reused_cached_neural_output=True,locked_view=view,underlying_arm=arm)
            table[view],values[view] = result,rows
    return main_table,SF_table,main_values,SF_values


def add_csv(rows,scope,table,unit,new_control):
    for method,item in table.items():
        rows.append({'scope':scope,'method':method,'unit':unit,'new_control_output':new_control,**item[unit],
                     'records':item['records'],'groups':item['groups'],'hits':item['hits'],'invalid':item['invalid_predictions']})


def parent_metadata():
    old153 = metadata_prefix(E153/'comparison.json',{'primary','source_cohorts','AF','core_Holm3','mechanism_joint_Holm8',
                                                      'historical_references_preserving_original_method_identity'})
    old154 = metadata_prefix(E154/'comparison.json',{'primary','locked_parent_method','source_cohorts','AF','mechanism_joint_Holm8',
                                                      'cached153_original_baseline_conclusion'})
    old155 = metadata_prefix(E155/'comparison.json',{'primary','source_cohorts','AF','core_joint_Holm8','mechanism_joint_Holm8',
                                                      'seed_and_block_stability','same_development_two_block_replication'})
    demand(old153['primary']==old155['primary']=='AB_GLOBAL' and old154['locked_parent_method']=='AB_GLOBAL',
           'Original underlying parent primary identity must stayAB_GLOBAL; reference aliases may differ')
    packets = {name:read(root/'main_decision_packet.json') for name,root in [('Exp153',E153),('Exp154',E154),('Exp155',E155)]}
    return old153,old154,old155,packets


def run():
    p,seals = verify_seals()
    demand(not (E/'comparison.json').exists() and not (E/'label_join_started.json').exists(), 'Frozen156 evaluator already started')
    freeze_evaluation()
    source_public = {scope:public_by(p['target_cohorts'][scope]['public_records'],p['target_cohorts'][scope]['sample_ids']) for scope in COHORTS}
    af_public = read(p['AF_public_records'])['records'];af_ids = [r['sample_id'] for r in af_public];af_by = {r['sample_id']:r for r in af_public}
    demand(len(af_ids)==len(af_by)==731 and len({r['task_group'] for r in af_public})==716, 'OriginalAF731/716 required')
    verify_prediction_payloads(p,source_public,af_ids,af_by)
    write_new(E/'label_join_started.json',{'at_utc':now(),'all18816_new_outputs_sealed':True,'new_Gold':0,
              'approved_plan_sha256':PLAN_SHA,'protocol_sha256':sha(E/'protocol.json'),
              'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),
              'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json'),'AF_label_access_scope':AF_LABEL_ACCESS_SCOPE})
    old153,old154,old155,packets = parent_metadata()
    labels = {};source_labels = source_gold(p,labels)
    source_results,new_outcomes,eval_scopes,changes,csvrows = {},[],{}, {},[]
    for scope in COHORTS:
        spec = p['target_cohorts'][scope];ids,by = spec['sample_ids'],source_public[scope]
        demand(len(ids)==spec['n'] and len({r['task_group'] for r in by.values()})==len(ids), 'Original independent source tasks required')
        gold = {s:source_labels[spec['label_source']][s] for s in ids}
        control_table,rows,controls,raw,outcomes = score_controls(scope,ids,by,gold)
        view_table,SF_table,views,SF_views = score_views(scope,ids,by,gold,old153,old155)
        new_outcomes.extend(outcomes)
        eval_scopes[scope] = {'ids':ids,'gold':gold,'controls':controls,'views':views,'SF_views':SF_views}
        for view in VIEWS:
            for control in CONTROLS:
                key = f'{VIEW_SLUGS[view]}_{scope}_AB_GLOBAL_vs_{control}'
                changes[key] = counterexamples(views[view],controls[control],ids,by,gold,view,'Exp156/'+control)
        source_results[scope] = {'n':len(ids),'groups':len(ids),'controls':control_table,'locked_model_views':view_table,
                                'cached_SF_views_reference_only':SF_table,'control_coverage':control_coverage(ids,by,controls),
                                'duplicate_control_outputs':duplicate_controls(ids,raw)}
        add_csv(csvrows,scope,control_table,'record_equal',True);add_csv(csvrows,scope,view_table,'record_equal',False)
        add_csv(csvrows,scope,{view.replace('AB_GLOBAL','SF_REF'):v for view,v in SF_table.items()},'record_equal',False)
    af_label_path = Path(p['AF_label_source']);af_gold = read(af_label_path)['labels'];labels[str(af_label_path)] = sha(af_label_path)
    demand(set(af_gold)==set(af_ids), 'Original AF annotation scope changed')
    af_table,af_rows,controls,raw,outcomes = score_controls('AF',af_ids,af_by,af_gold)
    view_table,SF_table,views,SF_views = score_views('AF',af_ids,af_by,af_gold,old153,old155)
    new_outcomes.extend(outcomes);eval_scopes['AF'] = {'ids':af_ids,'gold':af_gold,'controls':controls,'views':views,'SF_views':SF_views}
    fixed = old153['AF']['fixed120_sample_ids']
    demand(fixed==old154['AF']['fixed120_sample_ids']==old155['AF']['fixed120_sample_ids'] and len(fixed)==len(set(fixed))==120
           and set(fixed)<=set(af_ids) and len({af_by[s]['task_group'] for s in fixed})==120, 'Original fixed120 independent groups required')
    fixed_set = set(fixed)
    fixed_controls = {name:summary([r for r in rs if r['sample_id'] in fixed_set]) for name,rs in af_rows.items()}
    fixed_views = {name:summary([values[s] for s in fixed]) for name,values in views.items()}
    fixed_SF = {name:summary([values[s] for s in fixed]) for name,values in SF_views.items()}
    for view in VIEWS:
        for scope,ids in [('AF731',af_ids),('AF120',fixed)]:
            for control in CONTROLS:
                changes[f'{VIEW_SLUGS[view]}_{scope}_AB_GLOBAL_vs_{control}'] = counterexamples(views[view],controls[control],ids,af_by,af_gold,view,'Exp156/'+control)
    AF = {'records':731,'groups':716,'fixed120_sample_ids':fixed,'controls_all731_record_and716_group':af_table,'controls_fixed120':fixed_controls,
          'locked_views_all731_record_and716_group':view_table,'locked_views_fixed120':fixed_views,
          'cached_SF_views_all731_record_and716_group_reference_only':SF_table,'cached_SF_views_fixed120_reference_only':fixed_SF,
          'control_coverage':control_coverage(af_ids,af_by,controls),'duplicate_control_outputs':duplicate_controls(af_ids,raw),
          'prior_three_OOF_schedules_scored_once_and_reused_for_all_views':True,'no_A_B_duplicate_new_control_output_count':True,
          'cached_original_fixed120_AA_Binary_SDBL_SF_reference_only':old153['AF']['original_fixed120_cached_four'],
          'other611_AA_outputs':None}
    for scope,unit in [('AF731','record_equal'),('AF716','group_equal'),('AF120','record_equal')]:
        ctable,vtable,stable = (fixed_controls,fixed_views,fixed_SF) if scope=='AF120' else (af_table,view_table,SF_table)
        add_csv(csvrows,scope,ctable,unit,True);add_csv(csvrows,scope,vtable,unit,False)
        add_csv(csvrows,scope,{view.replace('AB_GLOBAL','SF_REF'):v for view,v in stable.items()},unit,False)
    draws = statistics.bootstrap_indices(716);family = {}
    coding = eval_scopes['coding363'];ids = coding['ids']
    for view in VIEWS:
        for control in CONTROLS:
            family[f'{VIEW_SLUGS[view]}_coding363_AB_GLOBAL_vs_{control}'] = statistics.binary_family_row(
                [coding['views'][view][s]['Top1'] for s in ids],[coding['controls'][control][s]['Top1'] for s in ids],30)
            family[f'{VIEW_SLUGS[view]}_AF716_AB_GLOBAL_vs_{control}'] = statistics.group_pair(views[view],controls[control],af_ids,af_by,30,draws)
    family = statistics.family(family,30)
    demand(set(family)==set(FAMILY_KEYS) and len(new_outcomes)==18816,'All30 fixed comparisons and18816 current control outcomes required')
    parent_reference = {'original_underlying_primary':'AB_GLOBAL','new156_primary_alias':PRIMARY,'reference_only_no_new_neural_output_or_old_SF_p_test':True,
                        'original153_metadata':old153,'original154_metadata':old154,'original155_metadata':old155,'original_decision_packets':packets}
    bindings = {str(root/name):sha(root/name) for root in (E153,E154,E155) for name in ('comparison.json','main_decision_packet.json')}
    evaluation_outcomes = {'at_utc':now(),'experiment':'Exp156','approved_plan_sha256':PLAN_SHA,
                           'protocol_sha256':sha(E/'protocol.json'),'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),
                           'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json'),'scopes':eval_scopes,
                           'new_control_outputs':18816,'new_neural_outputs':0,'historical_exposed_development_only':True}
    write_new(E/'evaluation_outcomes.json',evaluation_outcomes)
    result = {'at_utc':now(),'experiment':'Exp156','schema':'Exp156-fixed-neural-views-position-role-controls/1.0','primary':PRIMARY,
              'underlying_locked_primary':'AB_GLOBAL','source_cohorts':source_results,'AF':AF,'joint_Holm30':family,
              'all30_prespecified_tests_retained_including_identical_AF_controls':True,'paired_control_changes':changes,
              'new_control_per_task_outcomes':new_outcomes,'cached_parent_original_references':parent_reference,
              'new_ranker_outputs':18816,'new_analytic_count_fit_tables':32,'new_neural_outputs':0,'new_Gold':0,
              'all_original_denominators_and_annotation_coordinates_retained':True,'AF_label_access_scope':AF_LABEL_ACCESS_SCOPE,
              'source_AF_views_not_pooled_no_best_control_selection':True,'original_SF_comparisons_reference_only_no_new_p':True,
              'scope':'Simple control diagnostics against fixed cached views on exposed historical development; no new independent data',
              'metric_target':'Original released ordinal agreement; ruling out these controls is not semantic or causal mechanism proof',
              'protocol_sha256':sha(E/'protocol.json'),'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),
              'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json'),'evaluation_outcomes_sha256':sha(E/'evaluation_outcomes.json'),
              'label_files_sha256':labels,'historical_reference_files_sha256':bindings}
    write_new(E/'comparison.json',result)
    with (E/'metrics.csv').open('x',encoding='utf-8-sig',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=list(csvrows[0]));writer.writeheader();writer.writerows(csvrows)
    packet = {'at_utc':now(),'experiment':'Exp156','primary':PRIMARY,'underlying_locked_primary':'AB_GLOBAL','stage_complete':True,
              'overall_research_complete':False,'source_denominators':{c:source_results[c]['n'] for c in COHORTS},
              'source_control_hits':{c:{a:source_results[c]['controls'][a]['hits'] for a in CONTROLS} for c in COHORTS},
              'source_fixed_view_hits':{c:{v:source_results[c]['locked_model_views'][v]['hits'] for v in VIEWS} for c in COHORTS},
              'AF_control_731record_metrics':{c:af_table[c]['record_equal'] for c in CONTROLS},
              'AF_control_716group_metrics':{c:af_table[c]['group_equal'] for c in CONTROLS},
              'AF_control_fixed120_hits':{c:fixed_controls[c]['hits'] for c in CONTROLS},
              'AF_fixed_view_731record_metrics':{v:view_table[v]['record_equal'] for v in VIEWS},
              'AF_fixed_view_716group_metrics':{v:view_table[v]['group_equal'] for v in VIEWS},
              'AF_fixed_view_fixed120_hits':{v:fixed_views[v]['hits'] for v in VIEWS},'joint_Holm30':compact_pairs(family),
              'paired_change_counts':{k:{field:value for field,value in rec.items() if field!='records'} for k,rec in changes.items()},
              'control_coverage':{**{c:source_results[c]['control_coverage'] for c in COHORTS},'AF':AF['control_coverage']},
              'duplicate_AF_controls_preserved_in_family30':AF['duplicate_control_outputs'],
              'cached_parent_original_references':parent_reference,'old_primary_identities_and_prior_scores_unmodified':True,
              'new_analytic_count_fit_tables':32,'new_ranker_outputs':18816,'new_neural_models_optimization_forward_encoder_API_download_Gold_independent_unit':0,
              'fee_CNY':'0','scope':result['scope'],'decision_owner':'root','comparison':str(E/'comparison.json'),
              'evaluation_outcomes':str(E/'evaluation_outcomes.json'),'metrics':str(E/'metrics.csv'),
              'interpretation':['Report positive and negative differences against all five controls and every fixed model view',
                                'Unsupported difference does not establish equivalence; controls are not promoted to primary',
                                'This analysis reuses exposed development and rules out only these specific simpler alternatives']}
    write_new(E/'main_decision_packet.json',packet)
    status('EVALUATION_COMPLETE',new_ranker_outputs=18816,target_label_values_joined=2886,target_outputs_scored=18816,
           next='diagnostics156.py cached strata/consistency/overlap/mechanicalcases then finalize156.py')
    print(canonical({'Exp156':'evaluation_complete','new_outputs':18816,'joint_tests':30,'new_neural_forward':0}),flush=True)


if __name__=='__main__':
    run()

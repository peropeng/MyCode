"""This evaluator joins target labels after108 models/69264 outputs are sealed."""
import csv
import math
from collections import defaultdict
import numpy as np
from common import *
import paired_stats153 as statistics

PRIMARY = 'AB_GLOBAL'
MECHANISMS = ('AB_REF', 'AB_LOCAL', 'AB_STATIC', 'AB_VALUE_PERM')
CORE_KEYS = ('coding363_AB_GLOBAL_vs_SF_REF', 'AF120_AB_GLOBAL_vs_SF_REF', 'AF120_AB_GLOBAL_vs_cached_AA')
MECHANISM_KEYS = tuple(f'{scope}_AB_GLOBAL_vs_{arm}' for scope in ('coding363', 'AF716') for arm in MECHANISMS)
E144 = ROOT/'工作区/1006-exp144-domain-balanced/实验/实验144_同数据域适配与基线比较'
E145 = ROOT/'工作区/1006-exp145-content-normalization/实验/实验145_内容尺度与中心化核验'
EVALUATION_FILES = ('evaluate153.py', 'finalize153.py', 'paired_stats153.py')
AF_LABEL_ACCESS_SCOPE = {
    'training_label_load':'data153.af_inputs loads all731 preexisting exposed AF labels before training; this is not deferred until the prediction seal',
    'loss_and_epoch_selection':'Only the current fit IDs enter loss and current validation IDs enter epoch selection; refit uses current refit IDs',
    'current_outer_held_labels_used_for_loss_or_epoch_selection':0,
    'evaluation_join_scope':'Post-seal target evaluation label decodes/joins by this evaluator; no claim that the whole experiment never parsed AF labels before prediction sealing'}


def demand(ok, message):
    if not ok:
        raise RuntimeError(message)


def expected_prediction_files(p):
    paths = {E/'results'/c/f'{a}_{v}.json' for c in COHORTS for a in ARMS for v in tuple(SOURCE_SEEDS)+('ensemble',)}
    paths |= {E/'results/AF'/f'{a}_{v}.json' for a in ARMS for v in tuple(AF_SEEDS)+('ensemble',)}
    paths |= {E/'results/AF/folds'/r['arm']/f"{r['seed']}_{r['outer']}.json" for r in p['af_schedule']}
    return {str(x.resolve()) for x in paths}


def verify_seals():
    """No target annotation/old prediction decoding anywhere in this gate."""
    global_path = E/'results/all_predictions_sealed.json'
    demand(global_path.is_file(), 'ALL_PREDICTIONS_SEALED_REQUIRED_BEFORE_ANY_TARGET_LABEL_JOIN')
    p = read(E/'protocol.json')
    demand(p['primary']==PRIMARY and tuple(p['arms'])==ARMS, 'Frozen primary/six arms changed')
    demand(tuple(p['source_seeds'])==SOURCE_SEEDS and tuple(p['AF_seeds'])==AF_SEEDS, 'All fixed seeds required')
    demand(p['approved_plan_sha256']==sha(E/'approved_plan.json'), 'Approved plan changed')
    for field in ('training_sources', 'inputs', 'initializations', 'protected_old_files_sha256'):
        check_hashes(p[field])
    ms = read(E/'training/all_models_sealed.json')
    ps = read(global_path)
    source = read(E/'results/source_predictions_sealed.json')
    af = read(E/'results/AF_predictions_sealed.json')
    ph, mh = sha(E/'protocol.json'), sha(E/'training/all_models_sealed.json')
    demand(ms['all_fixed_models_sealed'] and ms['final_models']==108 and ms['optimization_stages']==198 and ms['protocol_sha256']==ph, '108 fitted models/198 stages not sealed')
    wanted_models = {('source', a, s, None) for a in ARMS for s in SOURCE_SEEDS}
    wanted_models |= {('AF', r['arm'], r['seed'], r['outer']) for r in p['af_schedule']}
    got = {(r['suite'], r['arm'], r['seed'], r.get('outer')) for r in ms['models']}
    demand(len(ms['models'])==108 and got==wanted_models, 'Fitted models differ from exact fixed schedule')
    for r in ms['models']:
        demand(r['stage']==('source_fit' if r['suite']=='source' else 'refit'), 'Initial/selection checkpoint cannot count as final fitted model')
        demand(r['protocol_sha256']==ph and r['held_labels_used_for_selection']==0 and r['scaler_fit_only'], 'Fitted model training/scaler contract violated')
        demand(Path(r['checkpoint']).resolve().is_relative_to((E/'training').resolve()), 'Final model outside Exp153')
        demand(sha(r['checkpoint'])==r['checkpoint_sha256'], 'Sealed fitted checkpoint changed')
    demand(ps['all_fixed_outputs_sealed'] and (ps['outputs'], ps['source_outputs'], ps['AF_outputs'])==(69264,51720,17544), 'All fixed rank outputs required')
    demand(ps['target_labels_joined']==source['target_labels_joined']==af['target_labels_joined']==0 and ms['target_scores_computed']==0, 'Premature target evaluation score/join marker')
    demand(ps['source_seal_sha256']==sha(E/'results/source_predictions_sealed.json') and ps['AF_seal_sha256']==sha(E/'results/AF_predictions_sealed.json'), 'Suite prediction seal changed')
    demand(source['protocol_sha256']==af['protocol_sha256']==ph and source['model_seal_sha256']==af['model_seal_sha256']==mh, 'Protocol/model/prediction seal chain broken')
    wanted_files = expected_prediction_files(p)
    files = {str(Path(q).resolve()): h for q,h in ps['files'].items()}
    demand(len(files)==210 and set(files)==wanted_files, '210 complete seed/ensemble/fold files required')
    demand(files=={**{str(Path(q).resolve()):h for q,h in source['files'].items()}, **{str(Path(q).resolve()):h for q,h in af['files'].items()}}, 'Global/suite sealed file sets differ')
    check_hashes(files)
    demand((source['outputs'],af['outputs'],af['records'],af['groups'])==(51720,17544,731,716), 'Fixed denominators/output totals changed')
    demand((E/'protocol.json').stat().st_mtime_ns <= (E/'training/all_models_sealed.json').stat().st_mtime_ns
           <= min(Path(q).stat().st_mtime_ns for q in files)
           <= global_path.stat().st_mtime_ns, 'Freeze/weights/predictions chronology violated')
    return p, ms, ps


def freeze_evaluation(p, ms, ps):
    sources = {str(E/name):sha(E/name) for name in EVALUATION_FILES}
    spec = {'at_utc':now(), 'schema':'Exp153-prespecified-evaluation/1.0', 'primary':PRIMARY,
            'sources':sources, 'protocol_sha256':sha(E/'protocol.json'),
            'model_seal_sha256':sha(E/'training/all_models_sealed.json'),
            'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),
            'core_Holm3':list(CORE_KEYS), 'mechanism_joint_Holm8':list(MECHANISM_KEYS),
            'binary_interval':'Exp143 stable exact-binomial paired interval; ordinary95% and Bonferroni family confidence',
            'AF_group_unit':'within-group record mean, then716 independent groups; exact rational weighted sign-flip',
            'AF_group_interval':'Exp138 paired5000 group bootstrap percentile, ordinary95% and Bonferroni nominal levels; no exact coverage claim',
            'bootstrap_seed':statistics.BOOTSTRAP_SEED, 'bootstrap_draws':statistics.BOOTSTRAP_DRAWS,
            'target_evaluation_label_decodes_by_this_evaluator_before_seal':0,
            'AF_label_access_scope':AF_LABEL_ACCESS_SCOPE, 'new_Gold':0, 'no_target_arm_or_seed_selection':True}
    path = E/'evaluation_code_seal.json'
    if path.exists():
        old = read(path)
        demand({k:v for k,v in old.items() if k!='at_utc'}=={k:v for k,v in spec.items() if k!='at_utc'}, 'Frozen evaluation implementation changed')
    else:
        write_new(path,spec)
    return read(path)


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


def structure_metadata(feature_path, ids, by):
    import torch
    full = torch.load(feature_path,map_location='cpu',weights_only=False)['records']
    info = {}
    for sid in ids:
        entry = full[sid]
        raw = entry['raw_structure']
        demand(tuple(raw.shape)==(len(by[sid]['turns']),23), 'Fixed public structure dimension changed')
        pairs = entry.get('observed_state_action_links')
        demand(isinstance(pairs,list), 'Frozen observed pair metadata missing')
        n = len(by[sid]['turns'])
        direct = [set() for _ in range(n)]
        for index,valid in entry['adjacency']:
            for i,(sources,flags) in enumerate(zip(index.tolist(),valid.tolist())):
                for j,flag in zip(sources,flags):
                    if flag>0:
                        demand(0<=j<n,'Original local adjacency outside record')
                        direct[i].add(j)
        reach = [{i}|direct[i]|{k for j in direct[i] for k in direct[j]} for i in range(n)]
        info[sid] = {'structured_payload_absent':not bool((raw[:,3:17]>0).any()),
                     'explicit_action_and_thought_absent':not bool((raw[:,1:3]>0).any()),
                     'zero_observed_state_action_pairs':len(pairs)==0,
                     'observed_state_action_pairs':len(pairs),
                     'single_observed_role':len({t['role'] for t in by[sid]['turns']})==1,
                     'length':n,'value_permutation_single_candidate_degenerate':n==1,
                     'LOCAL_has_nonlocal_keys_excluded':any(len(keys)<n for keys in reach),
                     'LOCAL_restricted_queries':sum(len(keys)<n for keys in reach),
                     'LOCAL_allowed_query_key_pairs':sum(len(keys) for keys in reach),
                     'GLOBAL_allowed_query_key_pairs':n*n}
    del full
    return info


def control_coverage(meta):
    nodes=sum(v['length'] for v in meta.values())
    return {'records':len(meta),'value_permutation_n1_identity_records':sum(v['value_permutation_single_candidate_degenerate'] for v in meta.values()),
            'LOCAL_mask_identical_to_GLOBAL_records':sum(not v['LOCAL_has_nonlocal_keys_excluded'] for v in meta.values()),
            'LOCAL_excludes_some_GLOBAL_keys_records':sum(v['LOCAL_has_nonlocal_keys_excluded'] for v in meta.values()),
            'candidate_queries':nodes,'LOCAL_restricted_candidate_queries':sum(v['LOCAL_restricted_queries'] for v in meta.values()),
            'LOCAL_allowed_query_key_pairs':sum(v['LOCAL_allowed_query_key_pairs'] for v in meta.values()),
            'GLOBAL_allowed_query_key_pairs':sum(v['GLOBAL_allowed_query_key_pairs'] for v in meta.values()),
            'public_graph_only_no_Gold_or_model_forward':True,'descriptive_availability_not_learned_attention_or_causal_effect':True,
            'all_degenerate_and_mask_identical_records_kept_in_full_denominator':True}


def strata(rows_by_condition, ids, by, meta):
    axes = {
        'structured_payload':lambda s:'absent' if meta[s]['structured_payload_absent'] else 'present',
        'explicit_action_thought':lambda s:'both_absent' if meta[s]['explicit_action_and_thought_absent'] else 'present',
        'observed_event_pairs':lambda s:'zero' if meta[s]['zero_observed_state_action_pairs'] else 'nonzero',
        'observed_role_count':lambda s:'single_role' if meta[s]['single_observed_role'] else 'multiple_roles',
        'length':lambda s:'1-8' if meta[s]['length']<=8 else '9-16' if meta[s]['length']<=16 else '17-plus',
        'domain':lambda s:by[s].get('domain','unknown')}
    result = {}
    for axis, classify in axes.items():
        buckets = defaultdict(set)
        for sid in ids:
            buckets[str(classify(sid))].add(sid)
        result[axis] = {bucket:{condition:summary([r for r in rows if r['sample_id'] in members])
                              for condition,rows in rows_by_condition.items() if '/seed_' not in condition}
                        for bucket,members in sorted(buckets.items())}
    return {'descriptive_only':True,
            'structured_payload_absent_definition':'All original raw_structure columns3:17 (JSON/array/object/nesting/tool flags) zero; temporal/role/content channels may still exist',
            'event_rule_not_general_A_mechanism_evidence':True,
            'single_role_accuracy_has_no_actor_discrimination':True,'tables':result}


def counterexample_rows(main, other, ids, by, gold, other_name):
    rows = []
    for sid in ids:
        a,b = main[sid],other[sid]
        if a['Top1']==b['Top1']:
            continue
        rows.append({'sample_id':sid,'task_group':by[sid]['task_group'],'record_id':by[sid].get('record_id'),
                     'original_Gold_ordinal':gold[sid],'main_method':PRIMARY,'other_method':other_name,
                     'main_chosen_step':a['chosen_step'],'other_chosen_step':b['chosen_step'],
                     'main_hit':bool(a['Top1']),'other_hit':bool(b['Top1']),
                     'status':'rescued' if a['Top1'] else 'damaged','public_record_sha256':digest(by[sid])})
    return {'rescued_records':sum(r['status']=='rescued' for r in rows),
            'damaged_records':sum(r['status']=='damaged' for r in rows),'records':rows,
            'AF_duplicates_remain_named_records_and_are_not_independent_group_counts':True}


def score_predictions(folder, seeds, ids, by, gold, cohort):
    table, rows_by_condition, ensembles = {}, {}, {}
    for arm in ARMS:
        seed_preds = []
        for variant in tuple(seeds)+('ensemble',):
            condition = arm if variant=='ensemble' else arm+'/seed_'+str(variant)
            saved = read(folder/f'{arm}_{variant}.json')
            demand(saved['arm']==arm, 'Prediction arm header differs from filename')
            if variant=='ensemble':
                demand(saved['all3_fixed_seeds_retained'] and saved['seeds']==list(seeds), 'Exactly all3 fixed ensemble seeds required')
            else:
                demand(saved['seed']==variant, 'Prediction seed header differs from filename')
            predictions = saved['predictions']
            demand(set(predictions)==set(ids), 'No dropped/missing prediction allowed')
            rows = [outcome(s,predictions[s],by[s],gold[s],condition) for s in ids]
            for row in rows:
                row['cohort'] = cohort
            table[condition],rows_by_condition[condition] = summary(rows),rows
            if variant!='ensemble':
                seed_preds.append(predictions)
            else:
                for sid,v in predictions.items():
                    allvalid = all(x[sid]['valid'] for x in seed_preds)
                    demand(v['valid']==allvalid, 'Ensemble invalid seed handling changed')
                    if allvalid:
                        prob = np.mean([x[sid]['probabilities'] for x in seed_preds],axis=0,dtype=np.float64).tolist()
                        demand(prob==v['probabilities'] and sorted(range(len(prob)),key=lambda i:(-prob[i],i))==v['order'], 'Ensemble must retain all3 fixed softmaxes/order')
                ensembles[arm] = {r['sample_id']:r for r in rows}
    return table,rows_by_condition,ensembles


def binary_conditions(saved):
    if 'predictions' in saved:
        return saved['predictions']
    return {r['sample_id']:r['conditions'] for r in saved['records']}


def historical_source(cohort, spec, ids, by, gold, main, examples, bindings):
    old_path = Path(spec['historical_predictions'])
    demand(sha(old_path)==spec['historical_predictions_sha256'], 'Bound original historical predictions changed')
    old = binary_conditions(read(old_path))
    demand(set(old)==set(ids), 'Original historical scope differs')
    requested = ('AB','B','StepFinder')+tuple(f'{a}/seed_{s}' for a in ('AB','B','StepFinder') for s in SOURCE_SEEDS)
    result = {'original_134_136_137_142_pipeline':{},'Exp143':{},'Exp144_145_different_training_population_SF':{}}
    original_stage = 'Exp136' if cohort=='coding363' else 'Exp137' if cohort in ('coding170','math155') else 'Exp142'
    for method in requested:
        if not all(method in old[s] for s in ids):
            result['original_134_136_137_142_pipeline'][method] = {'available':False,'reason':'No complete original saved condition; not created now'}
            continue
        rows = [outcome(s,old[s][method],by[s],gold[s],method,legacy=True) for s in ids]
        result['original_134_136_137_142_pipeline'][method] = {'original_stage':original_stage,'original_primary':'AB',
            'method':method,'role':'original primary' if method=='AB' else 'historical reference/control',
            'same_current_matched_baseline':False,'summary':summary(rows),'source':str(old_path),'source_sha256':sha(old_path)}
        if '/seed_' not in method:
            examples[f'{cohort}_AB_GLOBAL_vs_historical_{original_stage}_{method}'] = counterexample_rows(main,{r['sample_id']:r for r in rows},ids,by,gold,original_stage+'/'+method)
    bindings[str(old_path)] = sha(old_path)
    legacy_seal_path = E143/'results/prediction_seal.json'
    legacy_seal = read(legacy_seal_path)
    bindings[str(legacy_seal_path)] = sha(legacy_seal_path)
    for arm in ('AB_DILATED9','AB_REF','StepFinder','AB_DILATED9_NO_CONTENT','AB_DUP9','AB_DIR1_9','AB_DILATED9_PERM'):
        for variant in tuple(SOURCE_SEEDS)+('ensemble',):
            path = E143/'results'/cohort/f'{arm}_{variant}.json'
            name = arm if variant=='ensemble' else arm+'/seed_'+str(variant)
            demand(str(path) in legacy_seal['files'] and sha(path)==legacy_seal['files'][str(path)], 'Original143 reference seal changed')
            preds = read(path)['predictions']
            demand(set(preds)==set(ids), 'Original143 reference denominator changed')
            rows = [outcome(s,preds[s],by[s],gold[s],name,legacy=True) for s in ids]
            result['Exp143'][name] = {'original_primary':'AB_DILATED9','method':name,
                'role':'original primary' if arm=='AB_DILATED9' else 'historical reference/control',
                'current_matched_baseline':False,'summary':summary(rows),'source':str(path),'source_sha256':sha(path)}
            bindings[str(path)] = sha(path)
            if variant=='ensemble':
                examples[f'{cohort}_AB_GLOBAL_vs_historical143_{arm}'] = counterexample_rows(main,{r['sample_id']:r for r in rows},ids,by,gold,'Exp143/'+arm)
    # Source coding/math IDs overlap the144/145 held sets. Their supervised
    # training population differs; agentic294 is never substituted for1467.
    if cohort!='agentic1467':
        for arm in ('SF_POOL','SF_BAL'):
            path = E144/'results'/cohort/f'{arm}_ensemble.json'
            if not path.exists():
                result['Exp144_145_different_training_population_SF'][arm] = {'available':False,'reason':'Historical file absent'}
                continue
            seal_path = E144/'results/prediction_seal.json'
            old_seal = read(seal_path)
            demand(str(path) in old_seal['files'] and sha(path)==old_seal['files'][str(path)], 'Historical144 SF reference seal changed')
            bindings[str(seal_path)] = sha(seal_path)
            preds = read(path)['predictions']
            demand(set(preds)==set(ids), 'Historical144 coding/math scope changed')
            rows = [outcome(s,preds[s],by[s],gold[s],arm,legacy=True) for s in ids]
            result['Exp144_145_different_training_population_SF'][arm] = {'original_Exp144_primary':'DILATED_BAL',
                'original_Exp145_primary':'DILATED_CONTENT_RMS','method':arm,'role':'SF reference, not original primary',
                'training_population_differs_from_153_source492':True,'current_matched_baseline':False,
                'summary':summary(rows),'source':str(path),'source_sha256':sha(path)}
            bindings[str(path)] = sha(path)
            examples[f'{cohort}_AB_GLOBAL_vs_historical144_{arm}'] = counterexample_rows(main,{r['sample_id']:r for r in rows},ids,by,gold,'Exp144/'+arm)
    else:
        result['Exp144_145_different_training_population_SF']['availability'] = {'available_on_same1467':False,
            'reason':'Original144/145 agentic294 is a different denominator/training population; no replacement/pooling',
            'approved_historical_summary_only':'agentic294 old SF_POOL155/SF_BAL161; not compared to1467 Top1'}
    return result


def af_cached_and_history(ids, fixed, by, gold, main, examples, bindings, cached):
    cache_table, cache_values = {}, {}
    for method, preds in cached['predictions'].items():
        demand(set(preds)==set(fixed), 'Fixed120 cached baseline denominator changed')
        values = {}
        for sid in fixed:
            pred = preds[sid]
            row = outcome(sid,pred,by[sid],gold[sid],'cached_'+method,legacy=True)
            demand(row['Top1']==pred['step_accuracy'], 'Original cached correctness/original ordinal changed')
            if method=='stepfinder' and row['MRR'] is None:
                row['MRR'] = pred['full_MRR']
            if method!='stepfinder':
                demand(pred.get('ranking') is None and pred.get('full_MRR') is None, 'Single-choice AA/Binary/SDBL must not acquire fabricated ranks')
                row['MRR'],row['Top3'] = None,None
            values[sid] = row
        cache_values[method] = values
        cache_table[method] = {'summary':summary(list(values.values())), 'original_stage':'Exp129 cache preserved by Exp138',
                              'ranking_available':method=='stepfinder', 'new_requests':0,
                              'available_only_on_fixed120':True,'other611_AA_outputs':None}
        examples['AF120_AB_GLOBAL_vs_cached_'+method] = counterexample_rows(main,values,fixed,by,gold,'cached/'+method)
    demand(set(cache_table)=={'all_at_once','binary_search','sdbl','stepfinder'}, 'All four original cached methods required')
    old_seal_path = E138/'results/all_oof_and_ensembles_sealed.json'
    old_seal = read(old_seal_path)
    old_protocol = read(E138/'protocol.json')
    history = {}
    for arm in old_protocol['arms']:
        for variant in tuple(AF_SEEDS)+('ensemble',):
            path = E138/'results'/(f'ensemble_{arm}.json' if variant=='ensemble' else f'OOF_{arm}_{variant}.json')
            demand(str(path) in old_seal['files'] and sha(path)==old_seal['files'][str(path)], 'Historical138 OOF/ensemble seal changed')
            preds = read(path)['predictions']
            demand(set(preds)==set(ids), 'Historical138 all731 required')
            name = arm if variant=='ensemble' else arm+'/seed_'+str(variant)
            rows = [outcome(s,preds[s],by[s],gold[s],name,legacy=True) for s in ids]
            history[name] = {'original_primary':old_protocol['primary'],'role':'original primary' if arm==old_protocol['primary'] else 'historical reference/control',
                             'all731_record_and716_group':summary(rows),
                             'fixed120':summary([r for r in rows if r['sample_id'] in set(fixed)]),
                             'source':str(path),'source_sha256':sha(path),'current_matched_baseline':False}
            bindings[str(path)] = sha(path)
            if variant=='ensemble':
                examples['AF731_AB_GLOBAL_vs_historical138_'+arm] = counterexample_rows(main,{r['sample_id']:r for r in rows},ids,by,gold,'Exp138/'+arm)
    bindings[str(old_seal_path)] = sha(old_seal_path)
    return cache_table,cache_values,history


def source_gold(p, label_files):
    wanted = defaultdict(set)
    for spec in p['target_cohorts'].values():
        wanted[spec['label_source']].update(spec['sample_ids'])
    cache = {}
    for path, allowed in wanted.items():
        spec = next(r for r in p['target_cohorts'].values() if r['label_source']==path)
        demand(sha(path)==spec['label_source_sha256'], 'Saved historical annotation hash changed')
        saved = read(path)
        demand(not saved.get('errors'), 'Historical annotation mapping errors')
        rows = saved['labels']
        cache[path] = {r['sample_id']:r[spec['label_key']] for r in rows}
        demand(len(cache[path])==len(rows) and allowed<=set(cache[path]), 'Saved original annotation scope missing/duplicate')
        label_files[path] = sha(path)
    return cache


def verify_current_prediction_payloads(p, model_seal, af_ids):
    def probability_contract(predictions):
        for v in predictions.values():
            if v.get('valid') is not True:
                continue
            prob = v.get('probabilities')
            order = v.get('order')
            demand(isinstance(prob,list) and isinstance(order,list) and len(prob)==len(order)>0
                   and all(type(x) in (int,float) and math.isfinite(x) and 0<=x<=1 for x in prob)
                   and abs(math.fsum(prob)-1)<1e-5, 'Native softmax probability shape/normalization changed')
    fitted = {(r['suite'],r['arm'],r['seed'],r.get('outer')):r for r in model_seal['models']}
    ph = sha(E/'protocol.json')
    for cohort in COHORTS:
        ids = p['target_cohorts'][cohort]['sample_ids']
        for arm in ARMS:
            for seed in SOURCE_SEEDS:
                saved = read(E/'results'/cohort/f'{arm}_{seed}.json')
                demand(saved['protocol_sha256']==ph and saved['target_labels_decoded']==0
                       and saved['arm']==arm and saved['seed']==seed and saved['cohort']==cohort
                       and saved['checkpoint_sha256']==fitted['source',arm,seed,None]['checkpoint_sha256']
                       and set(saved['predictions'])==set(ids), 'Source held output/model binding changed')
                probability_contract(saved['predictions'])
    for arm in ARMS:
        for seed in AF_SEEDS:
            joined = {}
            for r in p['af_schedule']:
                if r['arm']!=arm or r['seed']!=seed:
                    continue
                saved = read(E/'results/AF/folds'/arm/f"{seed}_{r['outer']}.json")
                demand(saved['checkpoint_sha256']==fitted['AF',arm,seed,r['outer']]['checkpoint_sha256']
                       and saved['protocol_sha256']==ph and saved['held_labels_joined']==0
                       and saved['inference_batches_sha256']==r['inference_batches_sha256'], 'AF held output/model/batch binding changed')
                out = saved['predictions']
                probability_contract(out)
                demand(set(out)==set(r['held_ids']) and not set(joined)&set(out), 'AF OOF held scope duplicated or changed')
                joined.update(out)
            saved_seed = read(E/'results/AF'/f'{arm}_{seed}.json')
            demand(set(joined)==set(af_ids) and joined==saved_seed['predictions']
                   and saved_seed['arm']==arm and saved_seed['seed']==seed
                   and saved_seed['old_dev_labels_joined']==0 and saved_seed['exactly_one_OOF_per_record'], 'AF joined seed must preserve exact fold outputs')


def run():
    p,model_seal,prediction_seal = verify_seals()
    demand(not (E/'comparison.json').exists() and not (E/'label_join_started.json').exists(), 'Evaluation already started; do not silently rescore/change frozen evaluation')
    evaluation_seal = freeze_evaluation(p,model_seal,prediction_seal)
    af_public = read(E138/'data/public_records.json')['records']
    af_ids = [r['sample_id'] for r in af_public]
    af_by = {r['sample_id']:r for r in af_public}
    demand(len(af_ids)==731 and len(af_by)==731 and len({r['task_group'] for r in af_public})==716, 'Fixed AF731/716 public scope changed')
    verify_current_prediction_payloads(p,model_seal,af_ids)
    write_new(E/'label_join_started.json',{'at_utc':now(),'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),
              'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json'),'all69264_outputs_sealed':True,
              'label_join_scope':'Target evaluation joins by this evaluator only','AF_label_access_scope':AF_LABEL_ACCESS_SCOPE,
              'only_original_exposed_annotation_files':True,'new_Gold':0})
    label_files = {}
    labelcache = source_gold(p,label_files)
    cohorts,allout,vectors,examples,history = {},[],{},{},{}
    bindings = {}
    csvrows = []
    for cohort in COHORTS:
        spec = p['target_cohorts'][cohort]
        ids = spec['sample_ids']
        by = public_by(spec['public_records'],ids)
        demand(len(ids)==spec['n'] and len({by[s]['task_group'] for s in ids})==len(ids), 'Source independent task denominator changed')
        gold = {s:labelcache[spec['label_source']][s] for s in ids}
        table,rows,ens = score_predictions(E/'results'/cohort,SOURCE_SEEDS,ids,by,gold,cohort)
        meta = structure_metadata(spec['feature_source'],ids,by)
        cohorts[cohort] = {'n':len(ids),'group_count':len(ids),'condition_table':table,
                           'descriptive_strata':strata(rows,ids,by,meta),
                           'structure_counts':{k:sum(v[k] for v in meta.values()) for k in ('structured_payload_absent','explicit_action_and_thought_absent','zero_observed_state_action_pairs','single_observed_role')},
                           'observed_state_action_pairs':sum(v['observed_state_action_pairs'] for v in meta.values()),'control_coverage':control_coverage(meta),
                           'all_seeds':list(SOURCE_SEEDS),'source_training_population':'original492 train/122 validation; targets never fitted'}
        for condition,rs in rows.items():
            allout.extend(rs)
            csvrows.append({'cohort':cohort,'condition':condition,'scope':'record_equal',**table[condition]['record_equal'],
                            'n_records':len(ids),'n_groups':len(ids),'hits':table[condition]['hits'],'invalid':table[condition]['invalid_predictions']})
        for arm in ARMS:
            vectors[cohort,arm] = [ens[arm][s]['Top1'] for s in ids]
        for other in ARMS[1:]:
            examples[cohort+'_AB_GLOBAL_vs_'+other] = counterexample_rows(ens[PRIMARY],ens[other],ids,by,gold,other)
        history[cohort] = historical_source(cohort,spec,ids,by,gold,ens[PRIMARY],examples,bindings)
    af_label_path = E138/'data/development_labels.private.json'
    af_gold = read(af_label_path)['labels']
    label_files[str(af_label_path)] = sha(af_label_path)
    demand(set(af_gold)==set(af_ids), 'Original AF731 annotation scope changed')
    af_table,af_rows,af_ens = score_predictions(E/'results/AF',AF_SEEDS,af_ids,af_by,af_gold,'AF731')
    cached_path = E138/'data/cached120.json'
    cached = read(cached_path)
    bindings[str(cached_path)] = sha(cached_path)
    fixed = [r['sample_id'] for r in cached['manifest']]
    demand(len(fixed)==len(set(fixed))==120 and set(fixed)<=set(af_ids)
           and len({af_by[s]['task_group'] for s in fixed})==120, 'Original fixed120 must remain120 independent groups')
    for item in cached['manifest']:
        row = af_by[item['sample_id']]
        demand(item['record_id']==row['record_id'] and item['task_group']==row['task_group']
               and item['source_conv_id']==row['source_conv_id'], 'Original fixed120 IDs changed')
        for method,preds in cached['predictions'].items():
            expected_input = item['turns_sha256_exp124'] if method=='stepfinder' else item['input_sha256']
            demand(preds[item['sample_id']]['source_input_hash']==expected_input, 'Original cached120 raw input binding changed')
    fixed_table = {c:summary([r for r in rs if r['sample_id'] in set(fixed)]) for c,rs in af_rows.items()}
    cache_table,cache_values,af_history = af_cached_and_history(af_ids,fixed,af_by,af_gold,af_ens[PRIMARY],examples,bindings,cached)
    af_meta = structure_metadata(E138/'features/development_features.pt',af_ids,af_by)
    AF = {'records':731,'independent_groups':716,'fixed120_sample_ids':fixed,'fixed120_new_models':fixed_table,
          'all731_record_equal_and716_group_equal':af_table,'original_fixed120_cached_four':cache_table,
          'original_Exp138_all_seed_and_ensemble_references':af_history,
          'descriptive_strata':strata(af_rows,af_ids,af_by,af_meta),
          'structure_counts':{k:sum(v[k] for v in af_meta.values()) for k in ('structured_payload_absent','explicit_action_and_thought_absent','zero_observed_state_action_pairs','single_observed_role')},
          'observed_state_action_pairs':sum(v['observed_state_action_pairs'] for v in af_meta.values()),'control_coverage':control_coverage(af_meta),
          'AF_event_residual_cannot_be_claimed_tested_if_pairs_zero':True,'remaining611_paid_AA_outputs':None}
    for condition,rs in af_rows.items():
        allout.extend(rs)
        for name,scope in [('full731','record_equal'),('full716','group_equal'),('fixed120','record_equal')]:
            item = fixed_table[condition] if name=='fixed120' else af_table[condition]
            csvrows.append({'cohort':'AF','condition':condition,'scope':name+'/'+scope,**item[scope],
                            'n_records':item['records'],'n_groups':item['groups'],'hits':item['hits'],'invalid':item['invalid_predictions']})
    for other in ARMS[1:]:
        examples['AF731_AB_GLOBAL_vs_'+other] = counterexample_rows(af_ens[PRIMARY],af_ens[other],af_ids,af_by,af_gold,other)
    core = {CORE_KEYS[0]:statistics.binary_family_row(vectors['coding363',PRIMARY],vectors['coding363','SF_REF'],3),
            CORE_KEYS[1]:statistics.binary_family_row([af_ens[PRIMARY][s]['Top1'] for s in fixed],[af_ens['SF_REF'][s]['Top1'] for s in fixed],3),
            CORE_KEYS[2]:statistics.binary_family_row([af_ens[PRIMARY][s]['Top1'] for s in fixed],[cache_values['all_at_once'][s]['Top1'] for s in fixed],3)}
    core = statistics.family(core,3)
    draws = statistics.bootstrap_indices(716)
    mechanisms = {}
    for other in MECHANISMS:
        mechanisms['coding363_AB_GLOBAL_vs_'+other] = statistics.binary_family_row(vectors['coding363',PRIMARY],vectors['coding363',other],8)
        mechanisms['AF716_AB_GLOBAL_vs_'+other] = statistics.group_pair(af_ens[PRIMARY],af_ens[other],af_ids,af_by,8,draws)
    mechanisms = statistics.family(mechanisms,8)
    demand(set(core)==set(CORE_KEYS) and set(mechanisms)==set(MECHANISM_KEYS), 'Exactly prespecified Holm3/Holm8 required')
    demand(len(allout)==69264, 'All69264 outcomes/invalid denominators required')
    result = {'at_utc':now(),'schema':'Exp153-candidate-conditioned-global-context-fixed-development/1.0',
              'primary':PRIMARY,'source_cohorts':cohorts,'AF':AF,'core_Holm3':core,'mechanism_joint_Holm8':mechanisms,
              'historical_references_preserving_original_method_identity':history,'per_task_outcomes':allout,
              'all6arms_all3seeds_and_softmax_mean_ensembles':True,'all69264_predictions_sealed_before_target_evaluation_joins_by_this_evaluator':True,
              'source4_cohorts_and_AF_not_pooled':True,'no_best_seed_or_control_promoted_to_primary':True,
              'invalid_predictions_keep_full_denominators':True,'new_Gold':0,'historical_source_label_joins':2155,'historical_AF_label_joins':731,
              'label_join_counts_scope':'Target evaluation joins by this evaluator only','AF_label_access_scope':AF_LABEL_ACCESS_SCOPE,
              'scope':'Fixed readout feasibility on already exposed historical development; separate source and nested AF training populations',
              'metric_target':'Agreement with original released zero-based step annotations; attention is not verified causal dependency/inheritance',
              'protocol_sha256':sha(E/'protocol.json'),'model_seal_sha256':sha(E/'training/all_models_sealed.json'),
              'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json')}
    write_new(E/'comparison.json',result)
    write_new(E/'paired_counterexamples.json',{'at_utc':now(),'records_by_pair':examples,'comparison_sha256':sha(E/'comparison.json'),
              'rescued_damaged_definition':'Per original record correctness changed; AF group inference separately averages duplicate records'})
    with (E/'metrics.csv').open('x',encoding='utf-8-sig',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=list(csvrows[0]))
        writer.writeheader();writer.writerows(csvrows)
    write_new(E/'Gold_evaluation_receipt.json',{'at_utc':now(),'label_join_started_at_utc':read(E/'label_join_started.json')['at_utc'],
              'all69264_outputs_sealed_before_first_target_evaluation_join_by_this_evaluator':True,'source_label_joins':2155,'AF_old_dev_label_joins':731,
              'label_join_counts_scope':'Target evaluation joins by this evaluator only','AF_label_access_scope':AF_LABEL_ACCESS_SCOPE,
              'new_raw_or_unexposed_label_values':0,'authorTEST600_or_unapproved_reserve_read':False,
              'label_files_sha256':label_files,'historical_reference_files_sha256':bindings,
              'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json'),'comparison_sha256':sha(E/'comparison.json')})
    compact_mechanisms = {k:{field:value for field,value in row.items() if field!='paired_group_differences'} for k,row in mechanisms.items()}
    packet = {'at_utc':now(),'experiment':'Exp153','stage_complete':True,'overall_research_complete':False,'primary':PRIMARY,
              'scope':result['scope'],'source_ensemble_hits':{c:{a:cohorts[c]['condition_table'][a]['hits'] for a in ARMS} for c in COHORTS},
              'source_denominators':{c:cohorts[c]['n'] for c in COHORTS},
              'AF_fixed120_ensemble_hits':{a:fixed_table[a]['hits'] for a in ARMS},
              'AF_full731_record_metrics':{a:af_table[a]['record_equal'] for a in ARMS},
              'AF_full716_group_equal_metrics':{a:af_table[a]['group_equal'] for a in ARMS},
              'AF_cached_four':cache_table,'core_Holm3':core,'mechanism_joint_Holm8':compact_mechanisms,
              'historical_references':history,'historical_138_reference_summaries':af_history,
              'structure_strata_are_only_descriptive':True,'original_all_failures_and_coordinates_retained':True,
              'all_198_stages_108_fitted_models_69264_outputs_sealed':True,'parameters':p['parameters'],
              'new_encoder_API_download_Gold_independent_task':0,'fee_CNY':'0','decision_owner':'root',
              'interpretation_rules':['GLOBAL only remains primary; LOCAL/STATIC similar gains cannot prove candidate-conditioned nonlocal selection',
                                      'Higher than current matched SF alone is not continuous improvement over historical B/DILATED9/strong SF',
                                      'Preserve every negative and cross-cohort degradation; do not pool the two training suites or select favorable subsets'],
              'comparison':str(E/'comparison.json'),'counterexamples':str(E/'paired_counterexamples.json'),'metrics':str(E/'metrics.csv')}
    write_new(E/'main_decision_packet.json',packet)
    status('EVALUATION_COMPLETE',target_label_values_joined=2886,target_outputs_scored=69264,
           next='finalize153.py verifies198 stages including90 selection receipts; root owns scientific decision')
    print(canonical({'Exp153':'evaluation_complete','primary':PRIMARY,'source_hits':packet['source_ensemble_hits'],
                     'AF120_hits':packet['AF_fixed120_ensemble_hits'],'new_Gold':0}),flush=True)


if __name__=='__main__':
    run()

"""Three frozen data-split repetitions; all seed ranks and denominators retained."""
import csv
import math
from collections import defaultdict
from fractions import Fraction
from statistics import mean,stdev,median
import numpy as np
from common import *
import paired_stats157 as statistics

EVALUATION_FILES=("evaluate157.py","finalize157.py","paired_stats157.py")
CORE_KEYS=tuple(f"{b}_{scope}_AB_GLOBAL_vs_SF_REF" for b in BLOCKS for scope in ("coding363","AF716"))
MECHANISM_KEYS=tuple(f"{b}_{scope}_AB_GLOBAL_vs_AB_REF" for b in BLOCKS for scope in ("coding363","AF716"))
AF_LABEL_ACCESS_SCOPE={"training":"The exposed AF731 label file is parsed by the trainer; only current fit/validation IDs enter loss/selection; outer held values excluded", "evaluation":"This evaluator joins target labels only after all103896 new outputs are sealed"}


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
            'records':rows,'descriptive_only':True,'direction':'New157 splitGLOBAL minus named reference',
            'AF_duplicate_records_not_independent_groups':True}

def fraction_payload(v):
    return {'value':float(v),'numerator':v.numerator,'denominator':v.denominator}

def exact_accuracy(values,ids,by,group_equal):
    if not group_equal:
        return Fraction(sum(values[s]['Top1'] for s in ids),len(ids))
    groups = defaultdict(list)
    for sid in ids:
        groups[by[sid]['task_group']].append(sid)
    return sum((Fraction(sum(values[s]['Top1'] for s in ss),len(ss)) for ss in groups.values()),Fraction())/len(groups)

def dispersion(values):
    return {'n':len(values),'mean':mean(values),'sample_SD':stdev(values),'minimum':min(values),
            'maximum':max(values),'median':median(values)}

def compact_pairs(family):
    return {k:{field:v for field,v in row.items() if field!='paired_group_differences'} for k,row in family.items()}


def expected_prediction_files(p):
    paths = {prediction_path(c,a,b,s) for c in COHORTS for a in ARMS for b in BLOCKS for s in tuple(SOURCE_SEEDS)+(None,)}
    paths |= {prediction_path('AF',a,b,s) for a in ARMS for b in BLOCKS for s in tuple(AF_SEEDS)+(None,)}
    paths |= {fold_prediction_path(r['arm'],r['replication_block'],r['seed'],r['outer']) for r in p['af_schedule']}
    return {str(q.resolve()) for q in paths}


def scheduled_stages(p):
    for row in p['source_schedule']+[{'suite':'AF',**r} for r in p['af_schedule']]:
        suite = row['suite'];block = row['replication_block']
        folder = E/'training'/suite/row['arm']/block/(str(row['seed']) if suite=='source' else f"{row['seed']}_{row['outer']}")
        schedules = [('source_fit',row['fit_ids'],row['validation_ids'])] if suite=='source' else [
                    ('selection',row['selection_fit_ids'],row['validation_ids']),('refit',row['refit_ids'],[])]
        for stage,fit_ids,validation_ids in schedules:
            yield row,stage,fit_ids,validation_ids,folder/(stage+'.json')


def verify_seals():
    """Require the entire three-split run before target or old score decode."""
    global_path = E/'results/all_predictions_sealed.json'
    demand(global_path.is_file(),'ALL103896_NEW_OUTPUTS_SEALED_REQUIRED_BEFORE_TARGET_OR_OLD_SCORE_PARSE')
    demand(sha(E/'approved_plan.json')==PLAN_SHA,'Approved157 plan changed')
    p = read(E/'protocol.json');ph = sha(E/'protocol.json')
    demand(p['primary']==PRIMARY and p['approved_plan_sha256']==PLAN_SHA and tuple(p['arms'])==ARMS and tuple(p['blocks'])==BLOCKS
           and tuple(p['source_seeds'])==SOURCE_SEEDS and tuple(p['AF_seeds'])==AF_SEEDS,
           'Exact3arms3splitblocks/original3seeds required')
    demand(p['source_blocks']=={b:list(SOURCE_SEEDS) for b in BLOCKS} and p['AF_blocks']=={b:list(AF_SEEDS) for b in BLOCKS},
           'Each split must retain only its original3 seeds')
    demand((p['expected_optimization_stages'],p['expected_final_models'],p['expected_outputs'],p['expected_prediction_files'])==(297,162,103896,315)
           and len(p['source_schedule'])==27 and len(p['af_schedule'])==135 and len(p['initializations'])==54
           and len(p['initialization_records'])==162 and len(p['scaler_fit_specs'])==297,'Exact297stage/162model/54INITIAL-reference schedule required')
    demand(p['runtime_backend_policy']==EXPECTED_BACKEND and p['parameters']=={'AB_GLOBAL':337457,'SF_REF':277633,'AB_REF':300593},
           'Fixed original architectures/runtime required')
    for field in ('training_sources','inputs','initializations','protected_old_files_sha256'):
        check_hashes(p[field])
    split = read(E/'split_seal.json')
    demand(split['status']=='PASS' and split['approved_plan_sha256']==PLAN_SHA and split['splits_sha256']==sha(E/'splits.json')
           and p['split_seal_sha256']==sha(E/'split_seal.json') and split['all_source614_and_AF716_memberships_frozen_before_any_training'],
           'All source/AF assignments must be frozen before training')
    models,predictions = read(E/'training/all_models_sealed.json'),read(global_path)
    source,AF = read(E/'results/source_predictions_sealed.json'),read(E/'results/AF_predictions_sealed.json')
    mh = sha(E/'training/all_models_sealed.json')
    demand(models['all_fixed_models_sealed'] and (models['optimization_stages'],models['final_models'])==(297,162)
           and models['protocol_sha256']==ph and models['target_scores_computed']==0,'All162 models and297 actual optimization stages required')
    expected = {('source',a,b,s,None) for a in ARMS for b in BLOCKS for s in SOURCE_SEEDS}
    expected |= {('AF',a,b,s,o) for a in ARMS for b in BLOCKS for s in AF_SEEDS for o in range(5)}
    fitted = {(r['suite'],r['arm'],r['replication_block'],r['seed'],r.get('outer')):r for r in models['models']}
    references = {(r['suite'],r['arm'],r['replication_block'],r['seed'],r.get('outer')):r for r in p['initialization_records']}
    demand(len(models['models'])==len(fitted)==len(references)==162 and set(fitted)==set(references)==expected,
           'All162 exact new fitted model/initial-reference identities required')
    actual_final,stages,updates = {},0,0
    for row,stage,fit_ids,val_ids,path in scheduled_stages(p):
        rec = read(path);key = row['suite'],row['arm'],row['replication_block'],row['seed'],row.get('outer');initial = references[key]
        demand((rec['suite'],rec['arm'],rec['replication_block'],rec['seed'],rec.get('outer'),rec['stage'])==(*key,stage),
               'Actual new stage identity changed')
        demand(rec['protocol_sha256']==ph and rec['runtime_backend_policy']==EXPECTED_BACKEND and rec['scaler_fit_only']
               and rec['held_labels_used_for_selection']==0 and rec['fit_ids_sha256']==rec['scaler_fit_ids_sha256']==digest(fit_ids)
               and rec['validation_ids_sha256']==digest(val_ids),'Stage fit/validation/scaler/runtime contract changed')
        demand(Path(rec['initialization_path']).resolve()==Path(initial['path']).resolve()==Path(row['initialization_path']).resolve()
               and rec['initialization_sha256']==initial['sha256'] and rec['initialization_state_digest']==initial['state_digest']
               and rec['initialization_training_rng_digest']==initial['training_rng_digest']
               and rec['actual_canonical_training_RNG_restored'] and rec['trained_parent_weight_loads']==rec['invalid_runtime_asset_loads']==0,
               'Every stage must restore only the exact valid153 canonical INITIAL/RNG')
        demand(Path(rec['checkpoint']).resolve().is_relative_to((E/'training').resolve())
               and 'invalid_runtime' not in rec['checkpoint'] and sha(rec['checkpoint'])==rec['checkpoint_sha256'],
               'New157 valid fitted checkpoint required')
        if stage in ('source_fit','refit'):
            actual_final[key] = rec
        stages += 1;updates += rec['updates']
    demand(stages==297 and updates==models['optimizer_updates'] and actual_final==fitted,
           'All297 actual receipts/updates and162 final model seal must match')
    source_models,AF_models = read(E/'training/source_models_sealed.json'),read(E/'training/AF_models_sealed.json')
    demand(source_models['all27_sealed'] and AF_models['all135_sealed'] and (source_models['stages'],AF_models['stages'])==(27,270)
           and source_models['protocol_sha256']==AF_models['protocol_sha256']==ph
           and source_models['models']+AF_models['models']==models['models'],'Suite/final model seals differ')
    demand(predictions['all_fixed_outputs_sealed'] and (predictions['outputs'],predictions['source_outputs'],predictions['AF_outputs'])==(103896,77580,26316),
           'All103896 unique newly fixed outputs required')
    demand(predictions['prediction_files']==315 and predictions['protocol_sha256']==ph and predictions['model_seal_sha256']==mh,
           'Global output count/protocol/model seal binding changed')
    demand(predictions['target_labels_joined']==source['target_labels_joined']==AF['target_labels_joined']==0,
           'Premature157 evaluator target label join marker')
    demand(predictions['source_seal_sha256']==sha(E/'results/source_predictions_sealed.json')
           and predictions['AF_seal_sha256']==sha(E/'results/AF_predictions_sealed.json')
           and source['protocol_sha256']==AF['protocol_sha256']==ph and source['model_seal_sha256']==AF['model_seal_sha256']==mh,
           'New protocol/model/source/AF/global prediction seal chain broken')
    files = {str(Path(q).resolve()):h for q,h in predictions['files'].items()}
    demand(len(files)==315 and set(files)==expected_prediction_files(p)
           and files=={**{str(Path(q).resolve()):h for q,h in source['files'].items()},
                      **{str(Path(q).resolve()):h for q,h in AF['files'].items()}},'Exactly144 source/171 AF sealed prediction files required')
    check_hashes(files)
    demand((source['outputs'],AF['outputs'],AF['records'],AF['groups'])==(77580,26316,731,716),'Original source/AF output denominators required')
    demand(source['all_source_output_files']==144 and source['all_blocks_retained'] and AF['all_blocks_retained']
           and (AF['native_OOF_outputs'],AF['ensemble_outputs'],AF['joined_copy_entries_not_new_outputs'])==(19737,6579,19737),
           'All split blocks and native/ensemble/OOF-copy counts required')
    demand((E/'split_seal.json').stat().st_mtime_ns<=(E/'protocol.json').stat().st_mtime_ns<=(E/'training/all_models_sealed.json').stat().st_mtime_ns
           <=min(Path(q).stat().st_mtime_ns for q in files)<=global_path.stat().st_mtime_ns,'Splits/freeze/train/predict chronology violated')
    parents = read(E/'approved_plan.json')['parents']
    for root,key in ((E153,'packet153_sha256'),(E155,'packet155_sha256'),(E156,'packet156_sha256')):
        demand(sha(root/'main_decision_packet.json')==parents[key],'Original immutable parent packet changed')
    return p,models,predictions


def freeze_evaluation():
    value = {'at_utc':now(),'experiment':'Exp157','primary':PRIMARY,'approved_plan_sha256':PLAN_SHA,
             'sources':{str(E/n):sha(E/n) for n in EVALUATION_FILES},'protocol_sha256':sha(E/'protocol.json'),
             'model_seal_sha256':sha(E/'training/all_models_sealed.json'),'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),
             'core_joint_Holm6':list(CORE_KEYS),'mechanism_joint_Holm6':list(MECHANISM_KEYS),'families_separate':True,
             'bootstrap_seed':statistics.BOOTSTRAP_SEED,'bootstrap_draws':statistics.BOOTSTRAP_DRAWS,
             'supported_lead':'difference>0 and ownHolm<.05 and ownfamilyCI lower>0',
             'split_consistency':'All3 directions positive reported separately from all3 complete support flags; same exposed units',
             'no_seed_split_selection_no9_model_ensemble_no_p_or_sample_pooling':True,'old155_5pp_rule_not_redefined_or_overwritten':True,
             'no_new156_prior_fit_or_control_prediction':True,'AF_label_access_scope':AF_LABEL_ACCESS_SCOPE,
             'target_evaluation_label_decodes_by_this_evaluator_before_all_new_global_seals':0}
    path = E/'evaluation_code_seal.json'
    if path.exists():
        old = read(path)
        demand({k:v for k,v in old.items() if k!='at_utc'}=={k:v for k,v in value.items() if k!='at_utc'},'Frozen157 evaluator changed')
    else:
        write_new(path,value)


def verify_prediction_payloads(p,models,AF_ids):
    ph = sha(E/'protocol.json')
    fitted = {(r['suite'],r['arm'],r['replication_block'],r['seed'],r.get('outer')):r for r in models['models']}
    for cohort in COHORTS:
        ids = p['target_cohorts'][cohort]['sample_ids']
        for arm in ARMS:
            for block in BLOCKS:
                for seed in SOURCE_SEEDS:
                    saved = read(prediction_path(cohort,arm,block,seed))
                    demand(saved['arm']==arm and saved['replication_block']==block and saved['seed']==seed
                           and saved['cohort']==cohort and saved['protocol_sha256']==ph and saved['target_labels_decoded']==0
                           and saved['checkpoint_sha256']==fitted['source',arm,block,seed,None]['checkpoint_sha256']
                           and set(saved['predictions'])==set(ids),'Source seed model/split/protocol payload binding changed')
                    probability_contract(saved['predictions'])
                saved = read(prediction_path(cohort,arm,block))
                demand(saved['arm']==arm and saved['replication_block']==block and saved['cohort']==cohort
                       and saved['seeds']==list(SOURCE_SEEDS) and saved['all3_fixed_seeds_retained']
                       and saved['target_labels_decoded']==0 and saved['protocol_sha256']==ph and saved['no_cross_split_ensemble']
                       and set(saved['predictions'])==set(ids),'Source split3-seed ensemble binding changed')
    for arm in ARMS:
        for block in BLOCKS:
            for seed in AF_SEEDS:
                joined = {}
                for row in p['af_schedule']:
                    if (row['arm'],row['replication_block'],row['seed'])!=(arm,block,seed):
                        continue
                    saved = read(fold_prediction_path(arm,block,seed,row['outer']));out = saved['predictions']
                    demand(saved['protocol_sha256']==ph and saved['replication_block']==block
                           and saved['checkpoint_sha256']==fitted['AF',arm,block,seed,row['outer']]['checkpoint_sha256']
                           and saved['held_labels_joined']==0 and saved['inference_batches_sha256']==row['inference_batches_sha256']
                           and set(out)==set(row['held_ids']) and not set(joined)&set(out),'AF native fold/model/held/split binding changed')
                    probability_contract(out);joined.update(out)
                saved = read(prediction_path('AF',arm,block,seed))
                demand(saved['arm']==arm and saved['replication_block']==block and saved['seed']==seed
                       and saved['exactly_one_OOF_per_record'] and saved['old_dev_labels_joined']==0
                       and saved['protocol_sha256']==ph and saved['joined_entries_not_new_outputs']==731
                       and set(joined)==set(AF_ids) and saved['predictions']==joined,'AF seed join must match its new native fold outputs')
            saved = read(prediction_path('AF',arm,block))
            demand(saved['arm']==arm and saved['replication_block']==block and saved['seeds']==list(AF_SEEDS)
                   and saved['all3_fixed_seeds_retained'] and saved['exactly_one_OOF_per_record_per_seed']
                   and saved['old_dev_labels_joined']==0 and saved['protocol_sha256']==ph and saved['no_cross_split_ensemble']
                   and set(saved['predictions'])==set(AF_ids),'AF split3-seed ensemble binding changed')


def probability_contract(predictions):
    for v in predictions.values():
        if v.get('valid') is not True:
            continue
        prob,order = v.get('probabilities'),v.get('order')
        demand(isinstance(prob,list) and isinstance(order,list) and len(prob)==len(order)>0
               and all(type(x) in (int,float) and math.isfinite(x) and 0<=x<=1 for x in prob)
               and abs(math.fsum(prob)-1)<1e-5,'Native softmax shape/normalization changed')


def score_folder(scope,seeds,ids,by,gold):
    table,rows_by,values = {},{},{}
    for block in BLOCKS:
        for arm in ARMS:
            seed_predictions = []
            for seed in tuple(seeds)+(None,):
                name = arm+'/'+block+('/seed_'+str(seed) if seed is not None else '')
                saved = read(prediction_path(scope,arm,block,seed));predictions = saved['predictions']
                demand(saved['arm']==arm and saved['replication_block']==block and set(predictions)==set(ids),
                       'Complete original cohort/arm/stressblock required')
                if seed is None:
                    demand(saved['all3_fixed_seeds_retained'] and saved['seeds']==list(seeds),'Exactly all3 original seeds in each split ensemble required')
                    for sid,pred in predictions.items():
                        allvalid = all(v[sid]['valid'] for v in seed_predictions)
                        demand(pred['valid']==allvalid,'Prespecified3-seed invalid handling changed')
                        if allvalid:
                            prob = np.mean([v[sid]['probabilities'] for v in seed_predictions],axis=0,dtype=np.float64).tolist()
                            demand(prob==pred['probabilities'] and sorted(range(len(prob)),key=lambda i:(-prob[i],i))==pred['order'],
                                   'Saved ensemble must contain only its block3 softmax means/rank')
                else:
                    demand(saved['seed']==seed,'Saved original seed header changed')
                    seed_predictions.append(predictions)
                rs = [outcome(s,predictions[s],by[s],gold[s],name) for s in ids]
                for r in rs:
                    r.update(cohort=scope,replication_block=block,training_seed=seed,
                             ensemble_seeds=list(seeds) if seed is None else None,new157_output=True)
                table[name],rows_by[name] = summary(rs),rs
                values[arm,block,seed] = {r['sample_id']:r for r in rs}
    return table,rows_by,values


def fixed_strata(rows_by,ids,by,gold):
    """Reuse the descriptive156 axes; no stratum changes a full-scope comparison."""
    def length(n):
        return '[1,4]' if n<=4 else '[5,8]' if n<=8 else '[9,16]' if n<=16 else '[17,32]' if n<=32 else '[33,+inf]'
    axes = {'length':lambda s:length(len(by[s]['turns'])),
            'Gold_relative_position':lambda s:str(0 if len(by[s]['turns'])==1 else min(3,(4*gold[s])//(len(by[s]['turns'])-1))),
            'domain':lambda s:str(by[s].get('domain') or 'UNKNOWN'),
            'source_member':lambda s:str(by[s].get('source_member') or 'UNKNOWN'),
            'Engineer_present':lambda s:str(any(t['role'].strip().casefold()=='engineer' for t in by[s]['turns']))}
    tables = {}
    for axis,classification in axes.items():
        buckets = defaultdict(set)
        for sid in ids:
            buckets[classification(sid)].add(sid)
        tables[axis] = {label:{condition:summary([r for r in rows if r['sample_id'] in members])
                              for condition,rows in rows_by.items() if '/seed_' not in condition}
                       for label,members in sorted(buckets.items())}
    return {'descriptive_only':True,'axes_inherited_from156_no_threshold_search':True,
            'whole_scope_claims_not_replaced_by_selected_strata':True,'source_member_missing_is_UNKNOWN_no_inferred_family':True,'tables':tables}


def split_sensitivity(values,ids,by,seeds,scope,group_equal=False):
    result = {'scope':scope,'unit':'group_equal' if group_equal else 'record_equal','n_records':len(ids),
              'n_groups':len({by[s]['task_group'] for s in ids}),'blocks':list(BLOCKS),'original_seeds':list(seeds),
              'all3seeds_per_block_metrics':{},'paired_differences':{},'descriptive_only':True,
              'splits_and_seed_repetitions_not_new_independent_tasks':True,'no9_model_ensemble_no_best_split_or_seed_selection':True,
              'old155_5pp_practical_rule_is_not_recalculated_or_replaced':True}
    unit = 'group_equal' if group_equal else 'record_equal'
    for arm in ARMS:
        result['all3seeds_per_block_metrics'][arm] = {}
        for block in BLOCKS:
            stats = [summary([values[arm,block,s][sid] for sid in ids]) for s in seeds]
            result['all3seeds_per_block_metrics'][arm][block] = {
                'seed_rows':[{'seed':seed,**stat} for seed,stat in zip(seeds,stats)],
                'ensemble':summary([values[arm,block,None][sid] for sid in ids]),
                'seed_dispersion':{metric:dispersion([stat[unit][metric] for stat in stats]) for metric in ('Top1','MRR','Top3')},
                'invalid_prediction_dispersion':dispersion([stat['invalid_predictions'] for stat in stats])}
    for other in ('SF_REF','AB_REF'):
        block_differences = {block:exact_accuracy(values[PRIMARY,block,None],ids,by,group_equal)
                            -exact_accuracy(values[other,block,None],ids,by,group_equal) for block in BLOCKS}
        seed_rows = []
        for seed in seeds:
            ds = {b:exact_accuracy(values[PRIMARY,b,seed],ids,by,group_equal)-exact_accuracy(values[other,b,seed],ids,by,group_equal) for b in BLOCKS}
            seed_rows.append({'seed':seed,'all3_split_paired_Top1_differences':{b:fraction_payload(d) for b,d in ds.items()},
                              'minimum_difference':fraction_payload(min(ds.values())),'maximum_difference':fraction_payload(max(ds.values())),
                              'positive_splits':sum(d>0 for d in ds.values()),'ties':sum(d==0 for d in ds.values()),'negative_splits':sum(d<0 for d in ds.values())})
        result['paired_differences'][PRIMARY+'_vs_'+other] = {
            'all3_split_ensemble_differences':{b:fraction_payload(d) for b,d in block_differences.items()},
            'minimum_split_difference':fraction_payload(min(block_differences.values())),
            'maximum_split_difference':fraction_payload(max(block_differences.values())),
            'all3_split_directions_positive':all(d>0 for d in block_differences.values()),
            'positive_splits':sum(d>0 for d in block_differences.values()),'ties':sum(d==0 for d in block_differences.values()),
            'negative_splits':sum(d<0 for d in block_differences.values()),'same_original_seed_across3_splits':seed_rows,
            'other_rank_metric_ensemble_differences':{metric:{block:summary([values[PRIMARY,block,None][s] for s in ids])[unit][metric]
                                                                    -summary([values[other,block,None][s] for s in ids])[unit][metric] for block in BLOCKS}
                                                      for metric in ('MRR','Top3')}}
    return result


def same_task_split_patterns(values,ids,by,gold,scope):
    rows = []
    for sid in ids:
        mains = {b:values[PRIMARY,b,None][sid] for b in BLOCKS}
        rows.append({'sample_id':sid,'task_group':by[sid]['task_group'],'record_id':by[sid].get('record_id'),
                     'original_Gold_ordinal':gold[sid],
                     'GLOBAL_Top1_by_split':{b:v['Top1'] for b,v in mains.items()},
                     'GLOBAL_chosen_step_by_split':{b:v['chosen_step'] for b,v in mains.items()},
                     'SF_Top1_by_split':{b:values['SF_REF',b,None][sid]['Top1'] for b in BLOCKS},
                     'AB_REF_Top1_by_split':{b:values['AB_REF',b,None][sid]['Top1'] for b in BLOCKS},
                     'GLOBAL_correctness_changes_across_splits':len({v['Top1'] for v in mains.values()})>1})
    return {'scope':scope,'records':rows,'changed_correctness_records':sum(r['GLOBAL_correctness_changes_across_splits'] for r in rows),
            'all_records_retained':True,'AF_duplicate_records_not_independent_units':True,'descriptive_only':True}


def af_outer_results(values,p,by):
    result = []
    for row in p['af_schedule']:
        if row['arm']!=PRIMARY:
            continue
        block,seed,ids = row['replication_block'],row['seed'],row['held_ids']
        summaries = {arm:summary([values[arm,block,seed][sid] for sid in ids]) for arm in ARMS}
        result.append({'replication_block':block,'seed':seed,'outer':row['outer'],'n_records':len(ids),'n_groups':len({by[s]['task_group'] for s in ids}),
                       'condition_table':summaries,
                       'paired_group_equal_Top1_differences':{other:fraction_payload(exact_accuracy(values[PRIMARY,block,seed],ids,by,True)
                                                                                  -exact_accuracy(values[other,block,seed],ids,by,True)) for other in ('SF_REF','AB_REF')},
                       'descriptive_only':True,'outer_folds_not_independent_seed_or_task_replicates':True})
    demand(len(result)==45,'All3blocks3seeds5outer descriptive outcomes required')
    return result


def parent_metadata():
    original153 = metadata_prefix(E153/'comparison.json',{'primary','source_cohorts','AF','core_Holm3','mechanism_joint_Holm8',
                                                         'historical_references_preserving_original_method_identity'})
    original155 = metadata_prefix(E155/'comparison.json',{'primary','source_cohorts','AF','core_joint_Holm8','mechanism_joint_Holm8',
                                                         'seed_and_block_stability','same_development_two_block_replication'})
    original156 = metadata_prefix(E156/'comparison.json',{'primary','underlying_locked_primary','source_cohorts','AF','joint_Holm30'})
    demand(original153['primary']==original155['primary']==original156['underlying_locked_primary']==PRIMARY,
           'Original parent underlying primary identity changed')
    packets = {label:read(root/'main_decision_packet.json') for label,root in [('Exp153',E153),('Exp155',E155),('Exp156',E156)]}
    return original153,original155,original156,packets


def add_csv(rows,cohort,table,scope,unit):
    for name,stat in table.items():
        rows.append({'cohort':cohort,'condition':name,'scope':scope+'/'+unit,**stat[unit],
                     'records':stat['records'],'groups':stat['groups'],'hits':stat['hits'],'invalid':stat['invalid_predictions']})


def run():
    p,models,predictions = verify_seals()
    demand(not (E/'comparison.json').exists() and not (E/'label_join_started.json').exists(),'Frozen157 scoring already started')
    freeze_evaluation()
    AF_public = read(E138/'data/public_records.json')['records'];AF_ids = [r['sample_id'] for r in AF_public];AF_by = {r['sample_id']:r for r in AF_public}
    demand(len(AF_ids)==len(AF_by)==731 and len({r['task_group'] for r in AF_public})==716,'OriginalAF731/716 full scope required')
    verify_prediction_payloads(p,models,AF_ids)
    write_new(E/'label_join_started.json',{'at_utc':now(),'all103896_new_outputs_sealed':True,'new_Gold':0,
              'protocol_sha256':sha(E/'protocol.json'),'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),
              'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json'),'AF_label_access_scope':AF_LABEL_ACCESS_SCOPE})
    old153,old155,old156,packets = parent_metadata()
    labels = {};label_cache = source_gold(p,labels)
    source_results,outcomes,csvrows,changes,sensitivity,patterns,source_values = {},[],[],{},{},{},{}
    for scope in COHORTS:
        spec = p['target_cohorts'][scope];ids = spec['sample_ids'];by = public_by(spec['public_records'],ids)
        demand(len(ids)==spec['n'] and len({r['task_group'] for r in by.values()})==len(ids),'Original independent source task denominator required')
        gold = {sid:label_cache[spec['label_source']][sid] for sid in ids}
        table,rows,values = score_folder(scope,SOURCE_SEEDS,ids,by,gold);source_values[scope] = values
        source_results[scope] = {'n':len(ids),'groups':len(ids),'condition_table':table,'descriptive_strata':fixed_strata(rows,ids,by,gold),
                                 'historical156_simple_controls_reference_only':old156['source_cohorts'][scope]['controls'],
                                 'historical156_prior_fit_membership':'Original134492 train members, not matched to the new157 source split',
                                 'historical156_deterministic_rules_same_identity':True,
                                 'old153_all_conditions_and_stronger_method_identities':old153['source_cohorts'][scope],
                                 'old155_all6seeds_2blocks_and_old_control_references':old155['source_cohorts'][scope],
                                 'historical_references_preserving_original_method_identity':old153['historical_references_preserving_original_method_identity'][scope]}
        sensitivity[scope] = split_sensitivity(values,ids,by,SOURCE_SEEDS,scope)
        patterns[scope] = same_task_split_patterns(values,ids,by,gold,scope)
        for block in BLOCKS:
            for other in ('SF_REF','AB_REF'):
                changes[f'{scope}_{block}_AB_GLOBAL_vs_{other}'] = counterexamples(values[PRIMARY,block,None],values[other,block,None],ids,by,gold,
                                                                                   'Exp157/'+PRIMARY+'/'+block,'Exp157/'+other+'/'+block)
        for rs in rows.values():
            outcomes.extend(rs)
        add_csv(csvrows,scope,table,scope,'record_equal')
    AF_gold_path = E138/'data/development_labels.private.json';AF_gold = read(AF_gold_path)['labels'];labels[str(AF_gold_path)] = sha(AF_gold_path)
    demand(set(AF_gold)==set(AF_ids),'Original731 AF annotation scope required')
    AF_table,AF_rows,AF_values = score_folder('AF',AF_SEEDS,AF_ids,AF_by,AF_gold)
    fixed = old153['AF']['fixed120_sample_ids']
    demand(fixed==old155['AF']['fixed120_sample_ids']==old156['AF']['fixed120_sample_ids'] and len(fixed)==len(set(fixed))==120
           and set(fixed)<=set(AF_ids) and len({AF_by[s]['task_group'] for s in fixed})==120,'Exactly original fixed120 independent groups required')
    fixed_set = set(fixed);fixed_table = {name:summary([r for r in rs if r['sample_id'] in fixed_set]) for name,rs in AF_rows.items()}
    for scope,group_equal,ids in [('AF731',False,AF_ids),('AF716',True,AF_ids),('AF120',False,fixed)]:
        sensitivity[scope] = split_sensitivity(AF_values,ids,AF_by,AF_SEEDS,scope,group_equal)
    patterns['AF731'] = same_task_split_patterns(AF_values,AF_ids,AF_by,AF_gold,'AF731')
    AF = {'records':731,'groups':716,'fixed120_sample_ids':fixed,'all731_record_equal_and716_group_equal':AF_table,'fixed120':fixed_table,
          'all45_outer_results_descriptive':af_outer_results(AF_values,p,AF_by),
          'descriptive_strata':fixed_strata(AF_rows,AF_ids,AF_by,AF_gold),
          'cached_original_fixed120_AA_Binary_SDBL_SF_reference_only':old153['AF']['original_fixed120_cached_four'],
          'historical138_original_all_seed_and_ensemble_references':old153['AF']['original_Exp138_all_seed_and_ensemble_references'],
          'historical156_simple_controls_reference_only':old156['AF']['controls_all731_record_and716_group'],
          'historical156_simple_controls_fixed120_reference_only':old156['AF']['controls_fixed120'],
          'historical156_priors_use_old_folds_are_not_matched157_priors':True,'new156_prior_fits_or_predictions':0,
          'old153_all_conditions':old153['AF'],'old155_all6seeds_2blocks_and_old_control_references':old155['AF'],'other611_AA_outputs':None}
    for block in BLOCKS:
        for scope,ids in [('AF731',AF_ids),('AF120',fixed)]:
            for other in ('SF_REF','AB_REF'):
                changes[f'{scope}_{block}_AB_GLOBAL_vs_{other}'] = counterexamples(AF_values[PRIMARY,block,None],AF_values[other,block,None],ids,AF_by,AF_gold,
                                                                                 'Exp157/'+PRIMARY+'/'+block,'Exp157/'+other+'/'+block)
    for rs in AF_rows.values():
        outcomes.extend(rs)
    add_csv(csvrows,'AF',AF_table,'AF731','record_equal');add_csv(csvrows,'AF',AF_table,'AF716','group_equal')
    add_csv(csvrows,'AF',fixed_table,'AF120','record_equal')
    draws = statistics.bootstrap_indices(716);core,mechanism = {},{}
    coding = source_values['coding363'];coding_ids = p['target_cohorts']['coding363']['sample_ids']
    for block in BLOCKS:
        for field,other in [(core,'SF_REF'),(mechanism,'AB_REF')]:
            field[f'{block}_coding363_AB_GLOBAL_vs_{other}'] = statistics.binary_family_row([coding[PRIMARY,block,None][s]['Top1'] for s in coding_ids],
                                                                                          [coding[other,block,None][s]['Top1'] for s in coding_ids],6)
            field[f'{block}_AF716_AB_GLOBAL_vs_{other}'] = statistics.group_pair(AF_values[PRIMARY,block,None],AF_values[other,block,None],AF_ids,AF_by,6,draws)
    core,mechanism = statistics.family(core,6),statistics.family(mechanism,6)
    demand(set(core)==set(CORE_KEYS) and set(mechanism)==set(MECHANISM_KEYS) and len(outcomes)==103896,
           'Exactly two separateHolm6 families and103896 new scored outputs required')
    agreement = {kind:{scope:{'all3_split_directions_positive':all(family[f'{b}_{scope}_AB_GLOBAL_vs_{other}']['difference']>0 for b in BLOCKS),
                              'all3_splits_statistically_supported':all(family[f'{b}_{scope}_AB_GLOBAL_vs_{other}']['statistically_supported_lead'] for b in BLOCKS),
                              'interpretation_scope':'Same exposed development units across three prespecified split perturbations; no independent data confirmation'}
                       for scope in ('coding363','AF716')}
                 for kind,family,other in [('core',core,'SF_REF'),('mechanism',mechanism,'AB_REF')]}
    original_references = {'reference_only_old_p_values_unchanged':True,'original153_metadata':old153,'original155_metadata':old155,
                           'original156_metadata':old156,'original_decision_packets':packets,
                           'old155_5pp_practical_rule_and_original_FAIL_identity_preserved':True,
                           'simple156_priors_not_refit_or_claimed_matched_to_new157_partitions':True}
    result = {'at_utc':now(),'experiment':'Exp157','schema':'Exp157-three-fixed-data-splits-original-three-seeds/1.0','primary':PRIMARY,
              'source_cohorts':source_results,'AF':AF,'core_joint_Holm6':core,'mechanism_joint_Holm6':mechanism,
              'split_sensitivity':sensitivity,'same_task_cross_split_patterns':patterns,'paired_counterexamples':changes,
              'same_development_split_agreement':agreement,'cached_parent_original_references':original_references,
              'per_task_outcomes':outcomes,'new_ranker_outputs':103896,'source_AF_blocks_not_pooled':True,
              'all3_original_seeds_in_each3split_ensemble':True,'no9_model_ensemble_no_best_split_or_seed_selection':True,
              'invalid_predictions_keep_original_denominators':True,'AF_label_access_scope':AF_LABEL_ACCESS_SCOPE,'new_Gold':0,
              'scope':'Fixed initialization/model split sensitivity on exposed historical development; no new independent data',
              'metric_target':'Original released zero-based ordinal agreement; data partition sensitivity is not causal/semantic mechanism proof',
              'protocol_sha256':sha(E/'protocol.json'),'model_seal_sha256':sha(E/'training/all_models_sealed.json'),
              'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json')}
    write_new(E/'comparison.json',result)
    write_new(E/'paired_counterexamples.json',{'at_utc':now(),'records_by_pair':changes,'same_task_cross_split_patterns':patterns,
              'comparison_sha256':sha(E/'comparison.json'),'descriptive_only':True,'AF_record_changes_not_independent_group_counts':True})
    write_new(E/'split_sensitivity.json',{'at_utc':now(),'scopes':sensitivity,'all45_AF_outer_results':AF['all45_outer_results_descriptive'],
              'source_split_membership':p['source_splits'],'same_development_split_agreement':agreement,
              'comparison_sha256':sha(E/'comparison.json'),'no155_5pp_rule_replacement':True})
    write_new(E/'strata.json',{'at_utc':now(),'source':{c:source_results[c]['descriptive_strata'] for c in COHORTS},
              'AF':AF['descriptive_strata'],'comparison_sha256':sha(E/'comparison.json'),'descriptive_only':True})
    with (E/'metrics.csv').open('x',encoding='utf-8-sig',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=list(csvrows[0]));writer.writeheader();writer.writerows(csvrows)
    reference_hashes = {str(root/n):sha(root/n) for root in (E153,E155,E156) for n in ('comparison.json','main_decision_packet.json')}
    write_new(E/'Gold_evaluation_receipt.json',{'at_utc':now(),'all103896_new_outputs_sealed_before_this_evaluator_target_join':True,
              'historical_source_label_joins':2155,'AF_old_dev_label_joins':731,'new_Gold':0,'AF_label_access_scope':AF_LABEL_ACCESS_SCOPE,
              'label_files_sha256':labels,'historical_reference_files_sha256':reference_hashes,'comparison_sha256':sha(E/'comparison.json'),
              'authorTEST600_or_unapproved_reserve_read':False})
    packet = {'at_utc':now(),'experiment':'Exp157','primary':PRIMARY,'stage_complete':True,'overall_research_complete':False,'scope':result['scope'],
              'source_denominators':{c:source_results[c]['n'] for c in COHORTS},
              'source_split_ensemble_hits':{c:{b:{a:source_results[c]['condition_table'][a+'/'+b]['hits'] for a in ARMS} for b in BLOCKS} for c in COHORTS},
              'AF_split_fixed120_hits':{b:{a:fixed_table[a+'/'+b]['hits'] for a in ARMS} for b in BLOCKS},
              'AF_split_731record_metrics':{b:{a:AF_table[a+'/'+b]['record_equal'] for a in ARMS} for b in BLOCKS},
              'AF_split_716group_metrics':{b:{a:AF_table[a+'/'+b]['group_equal'] for a in ARMS} for b in BLOCKS},
              'core_joint_Holm6':compact_pairs(core),'mechanism_joint_Holm6':compact_pairs(mechanism),
              'same_development_split_agreement':agreement,'split_sensitivity':sensitivity,
              'paired_change_counts':{k:{field:v for field,v in rec.items() if field!='records'} for k,rec in changes.items()},
              'original153_155_156_references_only':original_references,'old155_5pp_practical_FAIL_not_overwritten':True,
              'source_split_membership':p['source_splits'],'new_optimization_stages':297,'new_final_fitted_models':162,'new_ranker_outputs':103896,
              'canonical_old_INITIAL_references_not_new_fitted_models':54,'parameters':p['parameters'],
              'new_encoder_API_download_Gold_independent_task':0,'fee_CNY':'0','decision_owner':'root',
              'comparison':str(E/'comparison.json'),'counterexamples':str(E/'paired_counterexamples.json'),'sensitivity':str(E/'split_sensitivity.json'),
              'interpretation':['All three split repetitions and original three seeds retained; no best split or nine-model ensemble',
                                'Direction/statistical agreement refers to the same exposed units; split repetitions do not multiply independent tasks',
                                'Original153 primary and155/156 results remain their original identities; controls are not promoted to primary']}
    write_new(E/'main_decision_packet.json',packet)
    status('EVALUATION_COMPLETE',new_ranker_outputs=103896,target_label_values_joined=2886,target_outputs_scored=103896,
           next='finalize157.py exact297stage/162model/54INITIAL/315predictionfile resource and final audit; root interprets')
    print(canonical({'Exp157':'evaluation_complete','new_outputs':103896,'core_tests':6,'mechanism_tests':6}),flush=True)


if __name__=='__main__':
    run()

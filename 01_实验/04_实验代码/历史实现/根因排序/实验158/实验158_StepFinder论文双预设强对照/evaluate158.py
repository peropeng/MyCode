"""Fixed153 GLOBAL versus two paper presets and validation-selected SF alias."""
import csv
import math
from collections import defaultdict
import numpy as np
from common import *
import paired_stats158 as statistics

EVALUATION_FILES=("evaluate158.py","finalize158.py","paired_stats158.py")
NATIVE_ARMS=('SF_ALG_PAPER50','SF_HC_PAPER50')
SELECTED_ARM='SF_INNERVAL_PRESET_SELECT'
ALL_BASELINES=NATIVE_ARMS+(SELECTED_ARM,)
CORE_KEYS=tuple(f'{scope}_LOCKED153_GLOBAL_vs_{SELECTED_ARM}' for scope in ('coding363','AF716','AF120'))
PRESET_KEYS=tuple(f'{scope}_LOCKED153_GLOBAL_vs_{arm}' for scope in ('coding363','AF716') for arm in NATIVE_ARMS)
AF_LABEL_ACCESS_SCOPE={"training":"Only current fit/validation AF labels enter loss/epoch/preset selection; all731 exposed labels share one historical file", "evaluation":"Evaluator target joins follow all native and derived output seals; no earlier training label parse absence claim"}


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
            'records':rows,'descriptive_only':True,'direction':'Locked153 GLOBAL minus named preset/selected reference',
            'AF_duplicate_records_not_independent_groups':True}

def compact_pairs(family):
    return {k:{field:v for field,v in row.items() if field!='paired_group_differences'} for k,row in family.items()}


def best_validation(receipt):
    row = next(r for r in receipt['history'] if r['epoch']==receipt['selected_epoch'])
    return {'Top1':row['validation']['Top1'],'MRR':row['validation']['MRR'],
            'selected_epoch':receipt['selected_epoch'],'group_equal':row['validation']['group_equal']}


def chosen_preset(receipts):
    metrics = {arm:best_validation(receipts[arm]) for arm in NATIVE_ARMS}
    winner = max(NATIVE_ARMS,key=lambda arm:(metrics[arm]['Top1'],metrics[arm]['MRR'],-NATIVE_ARMS.index(arm)))
    return winner,metrics


def cap_metadata(receipt):
    history = receipt['history'];last = history[-1]
    has_validation = 'validation' in last
    return {'suite':receipt['suite'],'arm':receipt['arm'],'seed':receipt['seed'],'outer':receipt.get('outer'),
            'stage':receipt['stage'],'selected_epoch':receipt['selected_epoch'],'completed_epochs':receipt['completed_epochs'],
            'max_epochs':50,'patience':10,'reached50_epoch_cap':receipt['completed_epochs']==50,
            'selected_epoch_is50':receipt['selected_epoch']==50,
            'final_epoch_improved_validation_best':last.get('improved') if has_validation else None,
            'validation_still_improving_when_cap_reached':receipt['completed_epochs']==50 and bool(last.get('improved')) if has_validation else None,
            'last_validation_stagnant_epochs':last.get('stagnant') if has_validation else None,
            'refit_uses_fixed_selected_epoch_not_new_validation_search':not has_validation,
            'descriptive_only_no_epoch_extension':True}


def baseline_prediction_path(scope,arm,seed=None):
    return selection_prediction_path(scope,seed) if arm==SELECTED_ARM else prediction_path(scope,arm,seed)


def scheduled_stages(p):
    for row in p['source_schedule']+[{'suite':'AF',**r} for r in p['af_schedule']]:
        folder = E/'training'/row['suite']/row['arm']/(str(row['seed']) if row['suite']=='source' else f"{row['seed']}_{row['outer']}")
        stages = [('source_fit',row['fit_ids'],row['validation_ids'])] if row['suite']=='source' else [
                 ('selection',row['selection_fit_ids'],row['validation_ids']),('refit',row['refit_ids'],[])]
        for stage,fit_ids,val_ids in stages:
            yield row,stage,fit_ids,val_ids,folder/(stage+'.json')


def expected_prediction_files(p):
    native = {prediction_path(c,a,s) for c in COHORTS for a in NATIVE_ARMS for s in tuple(SOURCE_SEEDS)+(None,)}
    native |= {prediction_path('AF',a,s) for a in NATIVE_ARMS for s in tuple(AF_SEEDS)+(None,)}
    native |= {fold_prediction_path(r['arm'],r['seed'],r['outer']) for r in p['af_schedule']}
    derived = {selection_prediction_path(c,s) for c in COHORTS for s in tuple(SOURCE_SEEDS)+(None,)}
    derived |= {selection_prediction_path('AF',s) for s in tuple(AF_SEEDS)+(None,)}
    return {str(q.resolve()) for q in native},{str(q.resolve()) for q in derived}


def profile_contract(rec):
    arm = rec['arm'];profile = PROFILES[arm]
    demand(rec['actual_preset_configuration']==profile and rec['actual_model_configuration']==
           {k:profile[k] for k in ('parameters','alpha','beta','gamma','scales')},'Actual restored model nonlearned preset attributes changed')
    demand(rec['actual_lr']==profile['lr'] and rec['actual_weight_decay']==.00001 and rec['lambda_temporal']==profile['lambda_temporal']
           and rec['max_epochs']==50 and rec['patience']==10,'Actual optimizer/lambda/50epoch/10patience configuration changed')


def verify_validation_choices(p,models):
    path = E/'validation_selection_decisions.json';seal_path = E/'validation_selection_sealed.json'
    choices,seal = read(path),read(seal_path);ph,mh = sha(E/'protocol.json'),sha(E/'training/all_models_sealed.json')
    demand(choices['status']=='FROZEN' and choices['name']==SELECTED_ARM
           and (choices['decision_count'],choices['source_decisions'],choices['AF_decisions'])==(18,3,15)
           and choices['protocol_sha256']==seal['protocol_sha256']==ph and choices['model_seal_sha256']==seal['model_seal_sha256']==mh
           and seal['status']=='PASS' and seal['decisions_sha256']==sha(path) and seal['selection_code_sha256']==sha(E/'select158.py')
           and seal['all18_validation_only_choices_sealed'] and seal['target_labels_joined']==choices['target_scores_or_target_labels_consumed']==0
           and choices['held_correctness_never_used_for_preset_choice'] and choices['no_new_optimization_or_neural_forward'],
           'Complete18 validation-only decisions must be sealed before target prediction/evaluation')
    by = {(r['suite'],r['seed'],r.get('outer')):r for r in choices['decisions']}
    expected = {('source',s,None) for s in SOURCE_SEEDS}|{('AF',s,o) for s in AF_SEEDS for o in range(5)}
    demand(len(choices['decisions'])==len(by)==18 and set(by)==expected,'Exactly3source+15AF preset decisions required')
    fitted = {(r['suite'],r['arm'],r['seed'],r.get('outer')):r for r in models['models']}
    for (suite,seed,outer),decision in by.items():
        demand(set(decision['options'])==set(NATIVE_ARMS),'Exactly the2 complete presets may enter validation selection')
        receipts = {}
        for arm in NATIVE_ARMS:
            folder = E/'training'/suite/arm/(str(seed) if suite=='source' else f'{seed}_{outer}')
            stage_path = folder/('source_fit.json' if suite=='source' else 'selection.json')
            rec = read(stage_path);receipts[arm] = rec;option = decision['options'][arm];final = fitted[suite,arm,seed,outer]
            epoch = next(row for row in rec['history'] if row['epoch']==rec['selected_epoch'])
            demand(option['validation_metric']==epoch['validation'] and option['selected_epoch']==rec['selected_epoch']
                   and Path(option['validation_stage_path']).resolve()==stage_path.resolve() and option['validation_stage_sha256']==sha(stage_path)
                   and option['validation_ids_sha256']==rec['validation_ids_sha256'] and option['preset_configuration']==PROFILES[arm]
                   and option['final_checkpoint']==final['checkpoint'] and option['final_checkpoint_sha256']==final['checkpoint_sha256'],
                   'Preset choice option must reference only its actual best inner-validation checkpoint')
            expected_sources = {c:str(prediction_path(c,arm,seed)) for c in COHORTS} if suite=='source' else {'AF':str(fold_prediction_path(arm,seed,outer))}
            demand(option['native_prediction_sources']==expected_sources,'Chosen native output source paths changed')
        winner,metrics = chosen_preset(receipts)
        tied = all(metrics[NATIVE_ARMS[0]][k]==metrics[NATIVE_ARMS[1]][k] for k in ('Top1','MRR'))
        demand(receipts[NATIVE_ARMS[0]]['validation_ids_sha256']==receipts[NATIVE_ARMS[1]]['validation_ids_sha256']
               and decision['chosen_preset']==winner and decision['complete_metric_tie']==tied
               and decision['target_or_held_outcomes_consumed']==0,'Only matched inner-val Top1/MRR with tieALG may choose a preset')
    return choices


def verify_seals():
    """Require36 weights,18 val choices,23088 native and11544 derived views first."""
    global_path = E/'results/all_predictions_sealed.json'
    demand(global_path.is_file(),'ALL23088_NATIVE_AND11544_DERIVED_OUTPUTS_SEALED_REQUIRED_BEFORE_TARGET_OR_OLD_SCORE_PARSE')
    demand(sha(E/'approved_plan.json')==PLAN_SHA,'Approved158 plan changed')
    p = read(E/'protocol.json');ph = sha(E/'protocol.json')
    demand(p['primary']==PRIMARY and p['approved_plan_sha256']==PLAN_SHA and tuple(p['arms'])==NATIVE_ARMS
           and p['profiles']==PROFILES==read(E/'approved_plan.json')['new_baseline_arms'] and p['selected_baseline_name']==SELECTED_ARM==SELECTED
           and tuple(p['source_seeds'])==SOURCE_SEEDS and tuple(p['AF_seeds'])==AF_SEEDS,'Fixed2complete paper presets/original3seeds/selected alias required')
    demand((p['expected_optimization_stages'],p['expected_final_models'],p['expected_outputs'],p['expected_prediction_files'],
            p['expected_derived_selection_view_records'],p['expected_derived_selection_files'])==(66,36,23088,70,11544,20)
           and len(p['source_schedule'])==6 and len(p['af_schedule'])==30 and len(p['scaler_fit_specs'])==66
           and len(p['initializations'])==18 and len(p['initialization_records'])==36,'Exact66stage/36model/18INITIAL/native-derived schedule required')
    demand(p['runtime_backend_policy']==EXPECTED_BACKEND and p['max_epochs']==50 and p['patience']==10
           and p['weight_decay']==.00001 and p['batch']==16 and p['clip']==1.
           and p['lr_by_preset']=={a:PROFILES[a]['lr'] for a in NATIVE_ARMS} and p['frozen_primary_forward_or_fit_new']==0,
           'Complete paper training presets and immutable cached main required')
    for field in ('training_sources','inputs','initializations','protected_old_files_sha256'):check_hashes(p[field])
    models = read(E/'training/all_models_sealed.json');mh = sha(E/'training/all_models_sealed.json')
    demand(models['all_fixed_models_sealed'] and (models['optimization_stages'],models['final_models'])==(66,36)
           and models['protocol_sha256']==ph and models['target_scores_computed']==0,'All36 new models and66 actual stages required')
    expected = {('source',a,s,None) for a in NATIVE_ARMS for s in SOURCE_SEEDS}
    expected |= {('AF',a,s,o) for a in NATIVE_ARMS for s in AF_SEEDS for o in range(5)}
    fitted = {(r['suite'],r['arm'],r['seed'],r.get('outer')):r for r in models['models']}
    initial = {(r['suite'],r['arm'],r['seed'],r.get('outer')):r for r in p['initialization_records']}
    demand(len(models['models'])==len(fitted)==len(initial)==36 and set(fitted)==set(initial)==expected,'All36 exact fitted preset identities required')
    final,stages,updates = {},0,0
    for row,stage,fit_ids,val_ids,path in scheduled_stages(p):
        rec = read(path);key = row['suite'],row['arm'],row['seed'],row.get('outer');original = initial[key]
        demand((rec['suite'],rec['arm'],rec['seed'],rec.get('outer'),rec['stage'])==(*key,stage),'Actual preset stage identity changed')
        profile_contract(rec)
        demand(rec['protocol_sha256']==ph and rec['runtime_backend_policy']==EXPECTED_BACKEND and rec['scaler_fit_only']
               and rec['held_labels_used_for_selection']==0 and rec['fit_ids_sha256']==rec['scaler_fit_ids_sha256']==digest(fit_ids)
               and rec['validation_ids_sha256']==digest(val_ids),'Preset stage fit/val/scaler/runtime changed')
        demand(Path(rec['initialization_path']).resolve()==Path(row['initialization_path']).resolve()==Path(original['path']).resolve()
               and rec['initialization_sha256']==original['sha256'] and rec['initialization_state_digest']==original['state_digest']
               and rec['initialization_training_rng_digest']==original['training_rng_digest'] and rec['actual_canonical_training_RNG_restored']
               and rec['trained_parent_weight_loads']==rec['invalid_runtime_asset_loads']==0,'Exact valid oldSF INITIAL and actual training RNG restoration required')
        demand(Path(rec['checkpoint']).resolve().is_relative_to((E/'training').resolve()) and 'invalid_runtime' not in rec['checkpoint']
               and sha(rec['checkpoint'])==rec['checkpoint_sha256'],'Own new preset checkpoint binding required')
        if stage in ('source_fit','refit'):final[key] = rec
        stages += 1;updates += rec['updates']
    demand(stages==66 and updates==models['optimizer_updates'] and final==fitted,'All66 actual receipts and36 fitted model seals must match')
    sm,am = read(E/'training/source_models_sealed.json'),read(E/'training/AF_models_sealed.json')
    demand(sm['all6_sealed'] and am['all30_sealed'] and (sm['stages'],am['stages'])==(6,60)
           and sm['protocol_sha256']==am['protocol_sha256']==ph and sm['models']+am['models']==models['models'],'Source/AF/all model seal chain broken')
    choices = verify_validation_choices(p,models)
    all_seal = read(global_path);native = read(E/'results/native_predictions_sealed.json');derived = read(E/'results/derived_selection_views_sealed.json')
    source,AF = read(E/'results/source_predictions_sealed.json'),read(E/'results/AF_predictions_sealed.json')
    demand(all_seal['all_fixed_outputs_sealed'] and all_seal['all_derived_views_sealed']
           and (all_seal['outputs'],all_seal['source_outputs'],all_seal['AF_outputs'],all_seal['derived_selection_view_records'],
                all_seal['prediction_files'],all_seal['derived_prediction_files'])==(23088,17240,5848,11544,70,20),
           'All23088 native and11544 derived views must seal separately without34632 new native claim')
    demand(all_seal['protocol_sha256']==native['protocol_sha256']==derived['protocol_sha256']==source['protocol_sha256']==AF['protocol_sha256']==ph
           and all_seal['model_seal_sha256']==native['model_seal_sha256']==source['model_seal_sha256']==AF['model_seal_sha256']==mh
           and all_seal['selection_seal_sha256']==native['selection_seal_sha256']==derived['selection_seal_sha256']==sha(E/'validation_selection_sealed.json'),
           'All weights/choices/native/derived protocol bindings required')
    demand(all_seal['native_prediction_seal_sha256']==derived['native_prediction_seal_sha256']==sha(E/'results/native_predictions_sealed.json')
           and all_seal['derived_selection_seal_sha256']==sha(E/'results/derived_selection_views_sealed.json')
           and native['source_seal_sha256']==sha(E/'results/source_predictions_sealed.json')
           and native['AF_seal_sha256']==sha(E/'results/AF_predictions_sealed.json'),'Native/derived/source/AF seal chain broken')
    demand(native['all_fixed_outputs_sealed'] and (native['outputs'],native['source_outputs'],native['AF_outputs'],native['prediction_files'],
           native['model_scoring_record_outputs'],native['three_seed_ensemble_outputs'])==(23088,17240,5848,70,17316,5772),
           'Exact native record/ensemble output accounting required')
    demand(derived['status']=='PASS' and derived['all_derived_views_sealed'] and derived['name']==SELECTED_ARM
           and (derived['derived_view_records'],derived['source_derived_records'],derived['AF_derived_records'],derived['derived_files'])==(11544,8620,2924,20)
           and derived['selection_decisions_sha256']==sha(E/'validation_selection_decisions.json')
           and derived['derived_function_source_sha256']==sha(E/'predict158.py') and derived['new_neural_forward']==derived['new_optimization_training']==0,
           'Exactly20 derived reuse files and0new forward/fit required')
    demand(all(v['target_labels_joined']==0 for v in (all_seal,native,derived,source,AF)),'Premature158 target evaluation join marker')
    files = {str(Path(q).resolve()):h for q,h in all_seal['files'].items()};aliases = {str(Path(q).resolve()):h for q,h in all_seal['derived_files'].items()}
    expected_native,expected_derived = expected_prediction_files(p)
    demand(set(files)==expected_native and set(aliases)==expected_derived and len(files)==70 and len(aliases)==20
           and files=={str(Path(q).resolve()):h for q,h in native['files'].items()}
           and aliases=={str(Path(q).resolve()):h for q,h in derived['files'].items()}
           and files=={**{str(Path(q).resolve()):h for q,h in source['files'].items()},**{str(Path(q).resolve()):h for q,h in AF['files'].items()}},
           'Exact native70/derived20 file sets; no additional derived AFfold files allowed')
    check_hashes(files);check_hashes(aliases)
    demand((AF['outputs'],AF['records'],AF['groups'],AF['native_OOF_outputs'],AF['ensemble_outputs'],AF['joined_copy_entries_not_new_outputs'])==(5848,731,716,4386,1462,4386),
           'AF full731/716 and native/OOF-copy accounting required')
    demand((E/'protocol.json').stat().st_mtime_ns<=(E/'training/all_models_sealed.json').stat().st_mtime_ns
           <=(E/'validation_selection_sealed.json').stat().st_mtime_ns<=min(Path(q).stat().st_mtime_ns for q in files)
           and (E/'results/native_predictions_sealed.json').stat().st_mtime_ns<=min(Path(q).stat().st_mtime_ns for q in aliases)
           <=(E/'results/derived_selection_views_sealed.json').stat().st_mtime_ns<=global_path.stat().st_mtime_ns,
           'Weights→val-only decisions→native→derived→global chronology violated')
    parent = read(E/'approved_plan.json')['parents']
    demand(sha(E153/'main_decision_packet.json')==parent['packet153_sha256'] and sha(E157/'main_decision_packet.json')==parent['packet157_sha256'],
           'Original locked main/stronger157 reference identities changed')
    return p,models,{'all':all_seal,'native':native,'derived':derived,'source':source,'AF':AF},choices


def freeze_evaluation():
    value = {'at_utc':now(),'experiment':'Exp158','primary':PRIMARY,'underlying_locked_primary':'AB_GLOBAL','approved_plan_sha256':PLAN_SHA,
             'sources':{str(E/n):sha(E/n) for n in EVALUATION_FILES},'protocol_sha256':sha(E/'protocol.json'),
             'model_seal_sha256':sha(E/'training/all_models_sealed.json'),'choices_seal_sha256':sha(E/'validation_selection_sealed.json'),
             'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),'main_joint_Holm3':list(CORE_KEYS),'preset_joint_Holm4':list(PRESET_KEYS),
             'families_separate':True,'bootstrap_seed':statistics.BOOTSTRAP_SEED,'bootstrap_draws':statistics.BOOTSTRAP_DRAWS,
             'supported_lead':'difference>0 and ownHolm<.05 and ownfamilyCI lower>0',
             'new_native_outputs':23088,'derived_views_not_new_native_outputs':11544,'no_new_main_or_derived_forward_or_fit':True,
             'val_only_choices_sealed_before_any_targetscore_or_prediction':True,'old_p_values_and155_5ppFAIL_preserved':True,
             'paper50_10_opponent_budget_vs_cached40_8_main_is_not_equal_training_cost':True,'AF_label_access_scope':AF_LABEL_ACCESS_SCOPE,
             'target_Gold_or_old_score_decodes_by_this_evaluator_before_all_native_and_derived_global_seals':0}
    path = E/'evaluation_code_seal.json'
    if path.exists():
        old = read(path)
        demand({k:v for k,v in old.items() if k!='at_utc'}=={k:v for k,v in value.items() if k!='at_utc'},'Frozen158 evaluator changed')
    else:write_new(path,value)


def probability_contract(predictions):
    for pred in predictions.values():
        if pred.get('valid') is not True:continue
        prob,order = pred.get('probabilities'),pred.get('order')
        demand(isinstance(prob,list) and isinstance(order,list) and len(prob)==len(order)>0
               and all(type(v) in (float,int) and math.isfinite(v) and 0<=v<=1 for v in prob)
               and abs(math.fsum(prob)-1)<1e-5,'Complete native probability shape/normalization changed')


def verify_prediction_payloads(p,models,choices,AF_ids):
    ph,dh = sha(E/'protocol.json'),sha(E/'validation_selection_decisions.json')
    fitted = {(r['suite'],r['arm'],r['seed'],r.get('outer')):r for r in models['models']}
    selected = {(r['suite'],r['seed'],r.get('outer')):r for r in choices['decisions']}
    for scope in COHORTS:
        ids = p['target_cohorts'][scope]['sample_ids']
        for arm in NATIVE_ARMS:
            for seed in SOURCE_SEEDS:
                saved = read(prediction_path(scope,arm,seed))
                demand(saved['arm']==arm and saved['seed']==seed and saved['cohort']==scope and saved['preset_configuration']==PROFILES[arm]
                       and saved['protocol_sha256']==ph and saved['checkpoint_sha256']==fitted['source',arm,seed,None]['checkpoint_sha256']
                       and saved['target_labels_decoded']==0 and set(saved['predictions'])==set(ids),'Native source profile/model binding changed')
                probability_contract(saved['predictions'])
            ensemble = read(prediction_path(scope,arm))
            demand(ensemble['arm']==arm and ensemble['cohort']==scope and ensemble['seeds']==list(SOURCE_SEEDS) and ensemble['all3_fixed_seeds_retained']
                   and ensemble['preset_configuration']==PROFILES[arm] and ensemble['protocol_sha256']==ph and ensemble['target_labels_decoded']==0
                   and set(ensemble['predictions'])==set(ids),'Native source preset ensemble binding changed')
        arms,sources = [],{}
        for seed in SOURCE_SEEDS:
            arm = selected['source',seed,None]['chosen_preset'];arms.append(arm);source = prediction_path(scope,arm,seed)
            saved = read(selection_prediction_path(scope,seed));original = read(source)
            demand(saved['arm']==SELECTED_ARM and saved['seed']==seed and saved['chosen_preset']==arm
                   and Path(saved['native_source_path']).resolve()==source.resolve() and saved['native_source_sha256']==sha(source)
                   and saved['selection_decisions_sha256']==dh and saved['protocol_sha256']==ph
                   and saved['derived_selection_view'] and saved['new_neural_forward']==saved['new_optimization_training']==saved['target_labels_joined']==0
                   and saved['predictions']==original['predictions'],'Source derived seed must be exactly the validation-chosen native prediction')
            sources[str(source)] = sha(source)
        saved = read(selection_prediction_path(scope));same = len(set(arms))==1
        demand(saved['chosen_preset_by_seed']==dict(zip(map(str,SOURCE_SEEDS),arms)) and saved['native_source_files_sha256']==sources
               and saved['selection_decisions_sha256']==dh and saved['protocol_sha256']==ph and saved['arm']==SELECTED_ARM
               and saved['seeds']==list(SOURCE_SEEDS) and saved['all3_fixed_seeds_retained'] and saved['derived_selection_view']
               and saved['new_neural_forward']==saved['new_optimization_training']==saved['target_labels_joined']==0
               and saved['existing_preset_ensemble_identity']==same,'Derived source ensemble choice sources/config binding changed')
        if same:
            source = prediction_path(scope,arms[0])
            demand(Path(saved['identity_source_path']).resolve()==source.resolve() and saved['identity_source_sha256']==sha(source)
                   and saved['predictions']==read(source)['predictions'],'Identical existing preset source ensemble must stay an identity reference')
    for arm in NATIVE_ARMS:
        for seed in AF_SEEDS:
            joined = {}
            for row in p['af_schedule']:
                if (row['arm'],row['seed'])!=(arm,seed):continue
                saved = read(fold_prediction_path(arm,seed,row['outer']));out = saved['predictions']
                demand(saved['arm']==arm and saved['seed']==seed and saved['outer']==row['outer'] and saved['preset_configuration']==PROFILES[arm]
                       and saved['protocol_sha256']==ph and saved['checkpoint_sha256']==fitted['AF',arm,seed,row['outer']]['checkpoint_sha256']
                       and saved['inference_batches_sha256']==row['inference_batches_sha256'] and saved['held_labels_joined']==0
                       and set(out)==set(row['held_ids']) and not set(joined)&set(out),'Native AF preset/model/held binding changed')
                probability_contract(out);joined.update(out)
            saved = read(prediction_path('AF',arm,seed))
            demand(saved['arm']==arm and saved['seed']==seed and saved['protocol_sha256']==ph and saved['preset_configuration']==PROFILES[arm]
                   and saved['exactly_one_OOF_per_record'] and saved['joined_entries_not_new_outputs']==731 and saved['old_dev_labels_joined']==0
                   and set(joined)==set(AF_ids) and saved['predictions']==joined,'Native AF joined copies must exactly match fold outputs')
        saved = read(prediction_path('AF',arm))
        demand(saved['arm']==arm and saved['seeds']==list(AF_SEEDS) and saved['all3_fixed_seeds_retained'] and saved['exactly_one_OOF_per_record_per_seed']
               and saved['preset_configuration']==PROFILES[arm] and saved['protocol_sha256']==ph and saved['old_dev_labels_joined']==0
               and set(saved['predictions'])==set(AF_ids),'Native AF preset ensemble binding changed')
    all_arms,all_sources = [],{}
    for seed in AF_SEEDS:
        joined,sources,arms = {},{},{}
        for outer in range(5):
            arm = selected['AF',seed,outer]['chosen_preset'];all_arms.append(arm);arms[str(outer)] = arm
            source = fold_prediction_path(arm,seed,outer);out = read(source)['predictions']
            demand(not set(joined)&set(out),'Derived AF selected OOF folds collide');joined.update(out);sources[str(source)] = sha(source)
        all_sources.update(sources);saved = read(selection_prediction_path('AF',seed))
        demand(saved['arm']==SELECTED_ARM and saved['seed']==seed and saved['chosen_preset_by_outer']==arms and saved['native_fold_source_files_sha256']==sources
               and saved['selection_decisions_sha256']==dh and saved['protocol_sha256']==ph and saved['exactly_one_OOF_per_record']
               and saved['derived_selection_view'] and saved['new_neural_forward']==saved['new_optimization_training']==saved['target_labels_joined']==0
               and set(joined)==set(AF_ids) and saved['predictions']==joined,'Derived AF OOF must use only its15 presealed choices, no task-specific selection')
    saved = read(selection_prediction_path('AF'));same = len(set(all_arms))==1
    demand(saved['arm']==SELECTED_ARM and saved['seeds']==list(AF_SEEDS) and saved['all3_fixed_seeds_retained']
           and saved['exactly_one_OOF_per_record_per_seed'] and saved['native_fold_source_files_sha256']==all_sources
           and saved['selection_decisions_sha256']==dh and saved['protocol_sha256']==ph and saved['derived_selection_view']
           and saved['new_neural_forward']==saved['new_optimization_training']==saved['target_labels_joined']==0
           and saved['existing_preset_ensemble_identity']==same,'Derived AF ensemble source/decision binding changed')
    if same:
        source = prediction_path('AF',all_arms[0])
        demand(Path(saved['identity_source_path']).resolve()==source.resolve() and saved['identity_source_sha256']==sha(source)
               and saved['predictions']==read(source)['predictions'],'Identical native AF preset ensemble must remain an identity reference')


def score_native_and_selected(scope,seeds,ids,by,gold):
    table,rows,values = {},{},{}
    for arm in ALL_BASELINES:
        seed_predictions = []
        for seed in tuple(seeds)+(None,):
            path = baseline_prediction_path(scope,arm,seed);saved = read(path);predictions = saved['predictions']
            name = arm if seed is None else arm+'/seed_'+str(seed)
            demand(saved['arm']==arm and set(predictions)==set(ids),'Whole original baseline arm/cohort required')
            if seed is None:
                demand(saved['all3_fixed_seeds_retained'] and saved['seeds']==list(seeds),'All3 original fixed seeds required')
                for sid,pred in predictions.items():
                    allvalid = all(v[sid]['valid'] for v in seed_predictions)
                    demand(pred['valid']==allvalid,'Fixed3-seed invalid handling changed')
                    if allvalid:
                        prob = np.mean([v[sid]['probabilities'] for v in seed_predictions],axis=0,dtype=np.float64).tolist()
                        demand(prob==pred['probabilities'] and sorted(range(len(prob)),key=lambda i:(-prob[i],i))==pred['order'],
                               'Saved ensemble must use all3 original seeds only')
            else:
                demand(saved['seed']==seed,'Saved original seed header changed');seed_predictions.append(predictions)
            rs = [outcome(s,predictions[s],by[s],gold[s],name) for s in ids]
            for row in rs:
                row.update(cohort=scope,training_seed=seed,new158_native_output=arm in NATIVE_ARMS,
                           derived_selection_view=arm==SELECTED_ARM,extra_model_forward_for_derived_view=0)
            table[name],rows[name] = summary(rs),rs
            values[arm,seed] = {r['sample_id']:r for r in rs}
    return table,rows,values


def cached_locked_global(scope,seeds,ids,by,gold,expected):
    table,rows,values = {},{},{}
    for seed in tuple(seeds)+(None,):
        variant = 'ensemble' if seed is None else str(seed)
        saved = read(E153/'results'/scope/f'AB_GLOBAL_{variant}.json')
        demand(saved['arm']=='AB_GLOBAL' and set(saved['predictions'])==set(ids),'Locked153 originalGLOBAL scope changed')
        if seed is None:
            demand(saved['all3_fixed_seeds_retained'] and saved['seeds']==list(seeds),'Original153 three-seed identity changed')
        else:
            demand(saved['seed']==seed,'Original153 seed identity changed')
        old_name = 'AB_GLOBAL' if seed is None else 'AB_GLOBAL/seed_'+str(seed)
        name = PRIMARY if seed is None else PRIMARY+'/seed_'+str(seed)
        rs = [outcome(s,saved['predictions'][s],by[s],gold[s],name) for s in ids]
        demand(summary(rs)==expected[old_name],'Locked153 original metric/annotation-coordinate identity changed')
        for row in rs:
            row.update(cohort=scope,reused_locked153_output=True,underlying_original_arm='AB_GLOBAL',new158_model_forward=0)
        table[name],rows[name],values[seed] = summary(rs),rs,{r['sample_id']:r for r in rs}
    return table,rows,values


def descriptive_strata(rows,ids,by,gold):
    axes = {'length':lambda s:'[1,4]' if len(by[s]['turns'])<=4 else '[5,8]' if len(by[s]['turns'])<=8 else '[9,16]' if len(by[s]['turns'])<=16 else '[17,32]' if len(by[s]['turns'])<=32 else '[33,+inf]',
            'Gold_relative_position':lambda s:str(0 if len(by[s]['turns'])==1 else min(3,(4*gold[s])//(len(by[s]['turns'])-1))),
            'domain':lambda s:str(by[s].get('domain') or 'UNKNOWN'),
            'source_member':lambda s:str(by[s].get('source_member') or 'UNKNOWN'),
            'Engineer_present':lambda s:str(any(t['role'].strip().casefold()=='engineer' for t in by[s]['turns']))}
    tables = {}
    for axis,classify in axes.items():
        buckets = defaultdict(set)
        for sid in ids:buckets[classify(sid)].add(sid)
        tables[axis] = {bucket:{name:summary([r for r in rs if r['sample_id'] in members]) for name,rs in rows.items() if '/seed_' not in name}
                       for bucket,members in sorted(buckets.items())}
    return {'descriptive_only':True,'axes_inherited156_no_new_threshold_search':True,'tables':tables,'full_scope_p_families_not_replaced':True}


def parent_metadata():
    old153 = metadata_prefix(E153/'comparison.json',{'primary','source_cohorts','AF','core_Holm3','mechanism_joint_Holm8',
                                                     'historical_references_preserving_original_method_identity'})
    old155 = metadata_prefix(E155/'comparison.json',{'primary','source_cohorts','AF','core_joint_Holm8','mechanism_joint_Holm8',
                                                     'seed_and_block_stability','same_development_two_block_replication'})
    old156 = metadata_prefix(E156/'comparison.json',{'primary','underlying_locked_primary','source_cohorts','AF','joint_Holm30'})
    old157 = metadata_prefix(E157/'comparison.json',{'primary','source_cohorts','AF','core_joint_Holm6','mechanism_joint_Holm6',
                                                     'split_sensitivity','same_development_split_agreement'})
    demand(old153['primary']==old155['primary']==old157['primary']==old156['underlying_locked_primary']=='AB_GLOBAL',
           'Underlying original parent primary identity changed')
    packets = {name:read(root/'main_decision_packet.json') for name,root in [('Exp153',E153),('Exp155',E155),('Exp156',E156),('Exp157',E157)]}
    return old153,old155,old156,old157,packets


def add_csv(rows,cohort,table,scope,unit,kind):
    for name,value in table.items():
        rows.append({'cohort':cohort,'condition':name,'scope':scope+'/'+unit,'output_kind':kind(name),**value[unit],
                     'records':value['records'],'groups':value['groups'],'hits':value['hits'],'invalid':value['invalid_predictions']})


def run():
    p,models,seals,choices = verify_seals()
    demand(not (E/'comparison.json').exists() and not (E/'label_join_started.json').exists(),'Frozen158 scoring already started')
    freeze_evaluation()
    AF_public = read(E138/'data/public_records.json')['records'];AF_ids = [r['sample_id'] for r in AF_public];AF_by = {r['sample_id']:r for r in AF_public}
    demand(len(AF_ids)==len(AF_by)==731 and len({r['task_group'] for r in AF_public})==716,'OriginalAF731/716 required')
    verify_prediction_payloads(p,models,choices,AF_ids)
    write_new(E/'label_join_started.json',{'at_utc':now(),'all23088_native_and11544_derived_outputs_sealed':True,'new_Gold':0,
              'protocol_sha256':sha(E/'protocol.json'),'model_seal_sha256':sha(E/'training/all_models_sealed.json'),
              'choices_seal_sha256':sha(E/'validation_selection_sealed.json'),'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),
              'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json'),'AF_label_access_scope':AF_LABEL_ACCESS_SCOPE})
    old153,old155,old156,old157,packets = parent_metadata()
    labels = {};source_labels = source_gold(p,labels)
    source_results,native_outcomes,derived_outcomes,cached_outcomes,changes,csvrows,source_values = {},[],[],[],{},[],{}
    kind = lambda name:'cached153_original' if name.startswith(PRIMARY) else 'derived_validation_selected' if name.startswith(SELECTED_ARM) else 'new_native_preset'
    for scope in COHORTS:
        spec = p['target_cohorts'][scope];ids = spec['sample_ids'];by = public_by(spec['public_records'],ids)
        demand(len(ids)==spec['n'] and len({r['task_group'] for r in by.values()})==len(ids),'Whole independent original source tasks required')
        gold = {s:source_labels[spec['label_source']][s] for s in ids}
        table,rows,values = score_native_and_selected(scope,SOURCE_SEEDS,ids,by,gold)
        old_table,old_rows,locked = cached_locked_global(scope,SOURCE_SEEDS,ids,by,gold,old153['source_cohorts'][scope]['condition_table'])
        source_values[scope] = {'baselines':values,'locked':locked}
        for arm in ALL_BASELINES:
            changes[f'{scope}_LOCKED153_GLOBAL_vs_{arm}'] = counterexamples(locked[None],values[arm,None],ids,by,gold,PRIMARY,arm)
        source_results[scope] = {'n':len(ids),'groups':len(ids),'new_preset_and_derived_condition_table':table,'locked153_GLOBAL':old_table,
                                 'descriptive_strata':descriptive_strata({**rows,**old_rows},ids,by,gold),
                                 'original153_all_conditions_and_historical_stronger_references':old153['source_cohorts'][scope],
                                 'original155_all6seeds_2blocks_reference_only':old155['source_cohorts'][scope],
                                 'original156_simple_controls_reference_only':old156['source_cohorts'][scope],
                                 'original157_all3split_3seeds_stronger_SF_including_agentic363':old157['source_cohorts'][scope],
                                 'older_method_identities':old153['historical_references_preserving_original_method_identity'][scope]}
        for name,rs in rows.items():
            (derived_outcomes if name.startswith(SELECTED_ARM) else native_outcomes).extend(rs)
        for rs in old_rows.values():cached_outcomes.extend(rs)
        add_csv(csvrows,scope,{**table,**old_table},scope,'record_equal',kind)
    AF_gold_path = E138/'data/development_labels.private.json';AF_gold = read(AF_gold_path)['labels'];labels[str(AF_gold_path)] = sha(AF_gold_path)
    demand(set(AF_gold)==set(AF_ids),'Original AF annotation scope required')
    AF_table,AF_rows,AF_values = score_native_and_selected('AF',AF_SEEDS,AF_ids,AF_by,AF_gold)
    locked_table,locked_rows,locked_AF = cached_locked_global('AF',AF_SEEDS,AF_ids,AF_by,AF_gold,old153['AF']['all731_record_equal_and716_group_equal'])
    fixed = old153['AF']['fixed120_sample_ids']
    demand(fixed==old155['AF']['fixed120_sample_ids']==old156['AF']['fixed120_sample_ids']==old157['AF']['fixed120_sample_ids']
           and len(fixed)==len(set(fixed))==120 and set(fixed)<=set(AF_ids) and len({AF_by[s]['task_group'] for s in fixed})==120,
           'Exactly original fixed120 independent groups required')
    fixed_set = set(fixed)
    fixed_table = {name:summary([r for r in rs if r['sample_id'] in fixed_set]) for name,rs in AF_rows.items()}
    fixed_locked = {name:summary([r for r in rs if r['sample_id'] in fixed_set]) for name,rs in locked_rows.items()}
    for arm in ALL_BASELINES:
        for scope,ids in [('AF731',AF_ids),('AF120',fixed)]:
            changes[f'{scope}_LOCKED153_GLOBAL_vs_{arm}'] = counterexamples(locked_AF[None],AF_values[arm,None],ids,AF_by,AF_gold,PRIMARY,arm)
    for name,rs in AF_rows.items():
        (derived_outcomes if name.startswith(SELECTED_ARM) else native_outcomes).extend(rs)
    for rs in locked_rows.values():cached_outcomes.extend(rs)
    AF = {'records':731,'groups':716,'fixed120_sample_ids':fixed,'new_presets_and_derived_all731_record_and716_group':AF_table,
          'new_presets_and_derived_fixed120':fixed_table,'locked153_GLOBAL_all731record716group':locked_table,'locked153_GLOBAL_fixed120':fixed_locked,
          'original_fixed120_AA_Binary_SDBL_SF_reference_only':old153['AF']['original_fixed120_cached_four'],
          'original153_all_conditions':old153['AF'],'original155_all6seeds_2blocks':old155['AF'],
          'original156_simple_controls':old156['AF'],'original157_all3split_3seeds_stronger_SF':old157['AF'],
          'descriptive_strata':descriptive_strata({**AF_rows,**locked_rows},AF_ids,AF_by,AF_gold),'other611_AA_outputs':None}
    add_csv(csvrows,'AF',{**AF_table,**locked_table},'AF731','record_equal',kind)
    add_csv(csvrows,'AF',{**AF_table,**locked_table},'AF716','group_equal',kind)
    add_csv(csvrows,'AF',{**fixed_table,**fixed_locked},'AF120','record_equal',kind)
    draws = statistics.bootstrap_indices(716);coding = source_values['coding363'];ids = p['target_cohorts']['coding363']['sample_ids']
    core = {CORE_KEYS[0]:statistics.binary_family_row([coding['locked'][None][s]['Top1'] for s in ids],[coding['baselines'][SELECTED_ARM,None][s]['Top1'] for s in ids],3),
            CORE_KEYS[1]:statistics.group_pair(locked_AF[None],AF_values[SELECTED_ARM,None],AF_ids,AF_by,3,draws),
            CORE_KEYS[2]:statistics.binary_family_row([locked_AF[None][s]['Top1'] for s in fixed],[AF_values[SELECTED_ARM,None][s]['Top1'] for s in fixed],3)}
    presets = {}
    for arm in NATIVE_ARMS:
        presets[f'coding363_LOCKED153_GLOBAL_vs_{arm}'] = statistics.binary_family_row([coding['locked'][None][s]['Top1'] for s in ids],[coding['baselines'][arm,None][s]['Top1'] for s in ids],4)
        presets[f'AF716_LOCKED153_GLOBAL_vs_{arm}'] = statistics.group_pair(locked_AF[None],AF_values[arm,None],AF_ids,AF_by,4,draws)
    core,presets = statistics.family(core,3),statistics.family(presets,4)
    demand(set(core)==set(CORE_KEYS) and set(presets)==set(PRESET_KEYS) and (len(native_outcomes),len(derived_outcomes),len(cached_outcomes))==(23088,11544,11544),
           'ExactHolm3/Holm4 and native/derived/cached output counts required')
    original = {'reference_only_old_p_and_primary_identities_unchanged':True,'original153':old153,'original155':old155,'original156':old156,'original157':old157,
                'original_decision_packets':packets,'old155_5pp_practical_FAIL_not_redefined':True,
                'no_stronger_old_SF_omitted_including_agentic157_363':True,'no_new_primary_neural_model_or_forward':True}
    result = {'at_utc':now(),'experiment':'Exp158','schema':'Exp158-paper-preset-SF-and-inner-validation-selection/1.0','primary':PRIMARY,
              'underlying_locked_primary':'AB_GLOBAL','source_cohorts':source_results,'AF':AF,'main_joint_Holm3':core,'preset_joint_Holm4':presets,
              'preset_selection_decisions':choices,'native_preset_per_task_outcomes':native_outcomes,'derived_selection_per_task_outcomes':derived_outcomes,
              'cached153_GLOBAL_per_task_outcomes':cached_outcomes,'paired_counterexamples':changes,'cached_parent_original_references':original,
              'new_native_ranker_outputs':23088,'derived_selection_view_records_not_new_ranker_outputs':11544,'cached153_GLOBAL_records_not_new_outputs':11544,
              'validation_selected_preset_not_best_target_preset':True,'native_and_derived_scopes_not_pooled':True,
              'all_source4_AF731_716_120_full_denominators':True,'old_AA_rank_metrics_not_fabricated':True,'AF_label_access_scope':AF_LABEL_ACCESS_SCOPE,
              'paper50_10_opponent_budget_exceeds_locked_ours40_8_no_equal_training_cost_claim':True,'new_Gold':0,
              'scope':'Fixed cached153 main versus full paper SF presets and validation-selected baseline on exposed historical development',
              'metric_target':'Original released zero-based ordinal agreement; strong baseline comparison is not independent data or causal mechanism confirmation',
              'protocol_sha256':sha(E/'protocol.json'),'model_seal_sha256':sha(E/'training/all_models_sealed.json'),
              'choices_seal_sha256':sha(E/'validation_selection_sealed.json'),'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),
              'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json')}
    write_new(E/'comparison.json',result)
    write_new(E/'paired_counterexamples.json',{'at_utc':now(),'records_by_pair':changes,'comparison_sha256':sha(E/'comparison.json'),'descriptive_only':True})
    with (E/'metrics.csv').open('x',encoding='utf-8-sig',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=list(csvrows[0]));writer.writeheader();writer.writerows(csvrows)
    references = {str(root/n):sha(root/n) for root in (E153,E155,E156,E157) for n in ('comparison.json','main_decision_packet.json')}
    write_new(E/'Gold_evaluation_receipt.json',{'at_utc':now(),'all23088_native_plus11544_derived_views_sealed_before_this_evaluator_target_join':True,
              'historical_source_label_joins':2155,'AF_old_dev_label_joins':731,'new_Gold':0,'label_files_sha256':labels,
              'historical_reference_files_sha256':references,'AF_label_access_scope':AF_LABEL_ACCESS_SCOPE,
              'comparison_sha256':sha(E/'comparison.json'),'authorTEST600_or_unapproved_reserve_read':False})
    packet = {'at_utc':now(),'experiment':'Exp158','primary':PRIMARY,'underlying_locked_primary':'AB_GLOBAL','stage_complete':True,'overall_research_complete':False,
              'source_denominators':{c:source_results[c]['n'] for c in COHORTS},
              'source_locked153_ensemble_hits':{c:source_results[c]['locked153_GLOBAL'][PRIMARY]['hits'] for c in COHORTS},
              'source_new_baseline_ensemble_hits':{c:{a:source_results[c]['new_preset_and_derived_condition_table'][a]['hits'] for a in ALL_BASELINES} for c in COHORTS},
              'AF_locked153_fixed120_hits':fixed_locked[PRIMARY]['hits'],'AF_new_baseline_fixed120_hits':{a:fixed_table[a]['hits'] for a in ALL_BASELINES},
              'AF_locked153_731record_metrics':locked_table[PRIMARY]['record_equal'],'AF_locked153_716group_metrics':locked_table[PRIMARY]['group_equal'],
              'AF_new_baseline_731record_metrics':{a:AF_table[a]['record_equal'] for a in ALL_BASELINES},
              'AF_new_baseline_716group_metrics':{a:AF_table[a]['group_equal'] for a in ALL_BASELINES},
              'main_joint_Holm3':compact_pairs(core),'preset_joint_Holm4':compact_pairs(presets),'validation_selection_decisions':choices,
              'cached_parent_original_references':original,'all_stronger_old_SF_including_agentic363_preserved':True,
              'paired_change_counts':{k:{field:v for field,v in rec.items() if field!='records'} for k,rec in changes.items()},
              'new_optimization_stages':66,'new_final_fitted_models':36,'canonical_old_SF_INITIAL_references':18,
              'new_native_ranker_outputs':23088,'derived_selection_view_records_not_new_outputs':11544,'new_primary_model_training_forward':0,
              'paper50_10_baseline_vs_locked40_8_ours_training_budget_is_intentionally_unequal':True,'new_encoder_API_download_Gold_independent_task':0,
              'fee_CNY':'0','scope':result['scope'],'decision_owner':'root','comparison':str(E/'comparison.json'),'counterexamples':str(E/'paired_counterexamples.json'),
              'interpretation':['Keep both paper presets and the validation-only selected view even when their target ordering differs',
                                'Selected baseline uses only validation metrics; derived view does not add inference or model fits',
                                'Scope-specific supported leads do not establish all-domain/all-baseline or global-mechanism superiority']}
    write_new(E/'main_decision_packet.json',packet)
    status('EVALUATION_COMPLETE',new_ranker_outputs=23088,derived_selection_view_records=11544,target_label_values_joined=2886,
           next='finalize158.py66stage/config/RNG/validation-choice/native-derived accounting audit; root interprets')
    print(canonical({'Exp158':'evaluation_complete','native_new_outputs':23088,'derived_views':11544,'main_tests':3,'preset_tests':4}),flush=True)


if __name__=='__main__':
    run()

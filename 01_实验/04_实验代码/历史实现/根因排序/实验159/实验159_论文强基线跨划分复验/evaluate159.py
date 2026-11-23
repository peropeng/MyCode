"""Source-only paper preset replication on three frozen157 split blocks."""
import csv,math
from collections import defaultdict
import numpy as np
from common import *
import paired_stats159 as statistics

NATIVE_ARMS=("SF_ALG_PAPER50","SF_HC_PAPER50")
SELECTED_ARM="SF_INNERVAL_PRESET_SELECT"
ALL_BASELINES=NATIVE_ARMS+(SELECTED_ARM,)
EVALUATION_FILES=("evaluate159.py","finalize159.py","paired_stats159.py")
CORE_KEYS=tuple(f"{b}_coding363_GLOBAL_vs_{SELECTED_ARM}" for b in BLOCKS)
PRESET_KEYS=tuple(f"{b}_coding363_GLOBAL_vs_{a}" for b in BLOCKS for a in NATIVE_ARMS)


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
            'records':rows,'descriptive_only':True,'direction':'Read-only157 splitGLOBAL minus named preset/selected reference',
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

def profile_contract(rec):
    arm = rec['arm'];profile = PROFILES[arm]
    demand(rec['actual_preset_configuration']==profile and rec['actual_model_configuration']==
           {k:profile[k] for k in ('parameters','alpha','beta','gamma','scales')},'Actual restored model nonlearned preset attributes changed')
    demand(rec['actual_lr']==profile['lr'] and rec['actual_weight_decay']==.00001 and rec['lambda_temporal']==profile['lambda_temporal']
           and rec['max_epochs']==50 and rec['patience']==10,'Actual optimizer/lambda/50epoch/10patience configuration changed')

def probability_contract(predictions):
    for pred in predictions.values():
        if pred.get('valid') is not True:continue
        prob,order = pred.get('probabilities'),pred.get('order')
        demand(isinstance(prob,list) and isinstance(order,list) and len(prob)==len(order)>0
               and all(type(v) in (float,int) and math.isfinite(v) and 0<=v<=1 for v in prob)
               and abs(math.fsum(prob)-1)<1e-5,'Complete native probability shape/normalization changed')

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


def scheduled_stages(p):
    for row in p['source_schedule']:
        path=E/'training/source'/row['replication_block']/row['arm']/str(row['seed'])/'source_fit.json'
        yield row,row['fit_ids'],row['validation_ids'],path


def baseline_path(scope,arm,block,seed=None):
    return selection_prediction_path(scope,block,seed) if arm==SELECTED_ARM else prediction_path(scope,arm,block,seed)


def expected_files():
    native={str(prediction_path(c,a,b,s).resolve()) for c in COHORTS for a in NATIVE_ARMS for b in BLOCKS for s in (*SOURCE_SEEDS,None)}
    derived={str(selection_prediction_path(c,b,s).resolve()) for c in COHORTS for b in BLOCKS for s in (*SOURCE_SEEDS,None)}
    return native,derived


def verify_prediction_runtime():
    path=E/'prediction_runtime_receipt.json';sealpath=E/'prediction_runtime_entry_sealed.json'
    rec,seal=read(path),read(sealpath);entry=E/'predict159_runtime_entry.py'
    demand(rec['status']=='PASS' and rec['protocol_sha256']==seal['protocol_sha256']==sha(E/'protocol.json')
           and Path(rec['entry_path']).resolve()==Path(seal['entry_path']).resolve()==entry.resolve()
           and rec['entry_sha256']==seal['entry_sha256']==sha(entry) and rec['entry_seal_sha256']==sha(sealpath)
           and rec['prediction_source_sha256']==seal['prediction_source_sha256']==sha(E/'predict159.py'), 'Independent frozen runtime entry/source/protocol chain required')
    demand(rec['actual_runtime_backend_policy']==rec['expected_runtime_backend_policy']==EXPECTED_BACKEND
           and rec['torch_default_dtype']=='torch.float32' and rec['initialization_seed_for_inference_only']==0
           and rec['prediction_outputs_before_entry']==rec['target_label_values_before_entry']==rec['new_model_fits_or_forwards_for_policy_restoration']==0
           and rec['frozen_training_or_prediction_sources_modified'] is False,'Actual6 inference flags/FP32 restored before outputs without extra forward or source changes')
    demand(seal['experiment']=='Exp159' and seal['frozen_scientific_content_and_model_training_unchanged']
           and seal['actual_runtime_policy_restored_before_any_prediction'] and seal['new_Gold']==0
           and seal['new_or_discarded_fits_predictions_before_repair']==0
           and sealpath.stat().st_mtime_ns<path.stat().st_mtime_ns
           <(E/'results/native_predictions_sealed.json').stat().st_mtime_ns,'Runtime restoration must precede native seal')
    if (E/'label_join_started.json').exists():
        demand(path.stat().st_mtime_ns<(E/'label_join_started.json').stat().st_mtime_ns,'Runtime restoration must precede Gold and old-score join')
    return rec


def verify_choices(p,models):
    choices=read(E/'validation_selection_decisions.json');seal=read(E/'validation_selection_sealed.json')
    demand(seal['all9_validation_only_choices_sealed'] and seal['target_labels_joined']==0 and seal['status']=='PASS'
           and seal['decisions_sha256']==sha(E/'validation_selection_decisions.json') and seal['protocol_sha256']==sha(E/'protocol.json')
           and seal['model_seal_sha256']==sha(E/'training/all_models_sealed.json') and seal['selection_code_sha256']==sha(E/'select159.py'), 'Nine validation choices must be sealed')
    rows=choices['decisions'];by={(r['replication_block'],r['seed']):r for r in rows}
    demand(len(rows)==len(by)==9 and set(by)=={(b,s) for b in BLOCKS for s in SOURCE_SEEDS},'Exact3split3seed choices required')
    fitted={(r['replication_block'],r['arm'],r['seed']):r for r in models['models']}
    for (block,seed),decision in by.items():
        receipts={}
        demand(decision['suite']=='source' and decision.get('outer') is None and set(decision['options'])==set(NATIVE_ARMS),'Source-only complete preset options required')
        for arm in NATIVE_ARMS:
            path=E/'training/source'/block/arm/str(seed)/'source_fit.json';rec=read(path);receipts[arm]=rec;option=decision['options'][arm]
            metric=next(r['validation'] for r in rec['history'] if r['epoch']==rec['selected_epoch'])
            demand(option['validation_metric']==metric and option['selected_epoch']==rec['selected_epoch']
                   and Path(option['validation_stage_path']).resolve()==path.resolve() and option['validation_stage_sha256']==sha(path)
                   and option['validation_ids_sha256']==rec['validation_ids_sha256'] and option['preset_configuration']==PROFILES[arm]
                   and option['final_checkpoint']==fitted[block,arm,seed]['checkpoint']
                   and option['final_checkpoint_sha256']==fitted[block,arm,seed]['checkpoint_sha256'],'Choice must use actual sealed inner validation')
        winner,metrics=chosen_preset(receipts)
        tied=all(metrics[NATIVE_ARMS[0]][k]==metrics[NATIVE_ARMS[1]][k] for k in ('Top1','MRR'))
        demand(decision['chosen_preset']==winner and decision['complete_metric_tie']==tied and decision['target_or_held_outcomes_consumed']==0
               and receipts[NATIVE_ARMS[0]]['validation_ids_sha256']==receipts[NATIVE_ARMS[1]]['validation_ids_sha256'],'Validation-only Top1/MRR tieALG required')
    return choices


def verify_seals():
    path=E/'results/all_predictions_sealed.json'
    demand(path.is_file(),'ALL51720_NATIVE_PLUS25860_DERIVED_SEALED_REQUIRED_BEFORE_GOLD_OLD_SCORE_PARSE')
    demand(sha(E/'approved_plan.json')==PLAN_SHA,'Approved159 plan changed')
    p=read(E/'protocol.json');ph=sha(E/'protocol.json')
    demand(p['primary']==PRIMARY and tuple(p['arms'])==NATIVE_ARMS and p['profiles']==PROFILES and tuple(p['source_seeds'])==SOURCE_SEEDS
           and len(p['source_schedule'])==18 and len(p['initializations'])==3 and len(p['initialization_records'])==18,'Exact source-only profiles/schedule/INITIAL binding required')
    demand(tuple(p['blocks'])==BLOCKS and p['af_schedule']==[] and p['new_AF_training']==0 and p['no_new_AF_training']
           and p['runtime_backend_policy']==EXPECTED_BACKEND and p['max_epochs']==50 and p['patience']==10
           and p['weight_decay']==.00001 and p['clip']==1. and p['batch']==16,'Fixed source-only3split paper/runtime budget required')
    for field in ('training_sources','inputs','initializations','protected_old_files_sha256'):check_hashes(p[field])
    model=read(E/'training/all_models_sealed.json');mh=sha(E/'training/all_models_sealed.json')
    demand(model['all_fixed_models_sealed'] and (model['optimization_stages'],model['final_models'])==(18,18)
           and model['protocol_sha256']==ph and model['target_scores_computed']==0,'All18 models/stages required')
    fitted={(r['replication_block'],r['arm'],r['seed']):r for r in model['models']}
    initial={(r['replication_block'],r['arm'],r['seed']):r for r in p['initialization_records']}
    wanted={(b,a,s) for b in BLOCKS for a in NATIVE_ARMS for s in SOURCE_SEEDS}
    demand(len(model['models'])==len(fitted)==len(initial)==18 and set(fitted)==set(initial)==wanted,'All18 exact split/preset/seed model identities required')
    updates=0
    for row,fit,val,stagepath in scheduled_stages(p):
        rec=read(stagepath);key=row['replication_block'],row['arm'],row['seed'];ref=initial[key]
        profile_contract(rec)
        demand(rec==fitted[key] and rec['suite']=='source' and rec['stage']=='source_fit' and rec['replication_block']==row['replication_block']
               and rec['fit_ids_sha256']==rec['scaler_fit_ids_sha256']==digest(fit) and rec['validation_ids_sha256']==digest(val)
               and rec['protocol_sha256']==ph and rec['runtime_backend_policy']==EXPECTED_BACKEND and rec['scaler_fit_only']
               and rec['held_labels_used_for_selection']==0,'Every actual sourcefit/scaler/runtime must match its frozen split')
        demand(Path(rec['initialization_path']).resolve()==Path(row['initialization_path']).resolve()==Path(ref['path']).resolve()
               and rec['initialization_sha256']==ref['sha256'] and rec['initialization_state_digest']==ref['state_digest']
               and rec['initialization_training_rng_digest']==ref['training_rng_digest'] and rec['actual_canonical_training_RNG_restored']
               and rec['trained_parent_weight_loads']==rec['invalid_runtime_asset_loads']==0,'Canonical153-via157 SF INITIAL/RNG only')
        demand(Path(rec['checkpoint']).resolve().is_relative_to((E/'training').resolve()) and sha(rec['checkpoint'])==rec['checkpoint_sha256'],'Own fitted checkpoint hash required')
        updates+=rec['updates']
    demand(updates==model['optimizer_updates'],'Actual18-stage optimizer update count required')
    choices=verify_choices(p,model)
    allseal=read(path);native=read(E/'results/native_predictions_sealed.json');derived=read(E/'results/derived_selection_views_sealed.json')
    demand(allseal['all_fixed_outputs_sealed'] and allseal['all_derived_views_sealed']
           and (allseal['outputs'],allseal['derived_selection_view_records'],allseal['prediction_files'],allseal['derived_prediction_files'])==(51720,25860,96,48),
           'All96native/48derived files and separate51720/25860 counts required')
    demand(derived['protocol_sha256']==ph and derived['model_seal_sha256']==mh and derived['prediction_files']==48
           and derived['outputs']==25860 and native['prediction_files']==96,'Derived48/native96 manifest exact binding required')
    demand(allseal['protocol_sha256']==native['protocol_sha256']==derived['protocol_sha256']==ph
           and allseal['model_seal_sha256']==native['model_seal_sha256']==mh
           and allseal['selection_seal_sha256']==native['selection_seal_sha256']==derived['selection_seal_sha256']==sha(E/'validation_selection_sealed.json')
           and allseal['native_prediction_seal_sha256']==derived['native_prediction_seal_sha256']==sha(E/'results/native_predictions_sealed.json')
           and allseal['derived_selection_seal_sha256']==sha(E/'results/derived_selection_views_sealed.json'),'Models/choices/native/derived chain broken')
    demand(native['all_fixed_outputs_sealed'] and native['outputs']==51720 and native['model_scoring_record_outputs']==38790
           and native['three_seed_ensemble_outputs']==12930 and derived['all_derived_views_sealed'] and derived['derived_selection_view_records']==25860
           and derived['new_neural_forward']==derived['new_model_fit']==0
           and all(v['target_labels_joined']==0 for v in (allseal,native,derived)),'Native/derived accounting or premature target join')
    nf,df=expected_files();files={str(Path(q).resolve()):h for q,h in allseal['files'].items()};aliases={str(Path(q).resolve()):h for q,h in allseal['derived_files'].items()}
    demand(set(files)==nf and set(aliases)==df and files=={str(Path(q).resolve()):h for q,h in native['files'].items()}
           and aliases=={str(Path(q).resolve()):h for q,h in derived['files'].items()},'Exact96native48derived file sets required')
    check_hashes(files);check_hashes(aliases)
    verify_prediction_runtime()
    demand((E/'prediction_runtime_receipt.json').stat().st_mtime_ns<min(Path(q).stat().st_mtime_ns for q in files),'Runtime receipt must precede every native output file')
    demand((E/'protocol.json').stat().st_mtime_ns<=(E/'training/all_models_sealed.json').stat().st_mtime_ns
           <=(E/'validation_selection_sealed.json').stat().st_mtime_ns<=min(Path(q).stat().st_mtime_ns for q in files)
           and (E/'results/native_predictions_sealed.json').stat().st_mtime_ns<=min(Path(q).stat().st_mtime_ns for q in aliases)
           <=(E/'results/derived_selection_views_sealed.json').stat().st_mtime_ns<=path.stat().st_mtime_ns,'Protocol/weights/choices/native/derived chronology')
    return p,model,{'all':allseal,'native':native,'derived':derived},choices


def freeze_evaluation():
    value={'at_utc':now(),'experiment':'Exp159','primary':PRIMARY,'sources':{str(E/n):sha(E/n) for n in EVALUATION_FILES},
           'protocol_sha256':sha(E/'protocol.json'),'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),
           'main_joint_Holm3':list(CORE_KEYS),'preset_joint_Holm6':list(PRESET_KEYS),'bootstrap_seed':statistics.BOOTSTRAP_SEED,
           'bootstrap_draws':statistics.BOOTSTRAP_DRAWS,'old_p_and155_5ppFAIL_preserved':True,'native51720_derived25860_separate':True}
    path=E/'evaluation_code_seal.json'
    if path.exists():
        old=read(path);demand({k:v for k,v in old.items() if k!='at_utc'}=={k:v for k,v in value.items() if k!='at_utc'},'Frozen evaluator changed')
    else:write_new(path,value)


def score_scope(scope,block,ids,by,gold,old157,choices,models):
    table,rows,values={}, {}, {}
    choice={(r['replication_block'],r['seed']):r['chosen_preset'] for r in choices['decisions']}
    fitted={(r['replication_block'],r['arm'],r['seed']):r for r in models['models']}
    ph=sha(E/'protocol.json');dh=sha(E/'validation_selection_decisions.json')
    for arm in (*ALL_BASELINES,'AB_GLOBAL'):
        preds=[]
        for seed in (*SOURCE_SEEDS,None):
            locked=arm=='AB_GLOBAL';path=locked_prediction_path(scope,block,seed) if locked else baseline_path(scope,arm,block,seed)
            saved=read(path);out=saved['predictions'];name=(PRIMARY if locked else arm)+'/'+block+('/seed_'+str(seed) if seed is not None else '')
            demand(saved['arm']==arm and saved['replication_block']==block and set(out)==set(ids),'Whole original scope/arm/split required')
            if not locked:
                demand(saved['protocol_sha256']==ph,'Current baseline protocol changed')
                if arm in NATIVE_ARMS:
                    demand(saved['preset_configuration']==PROFILES[arm] and saved['target_labels_decoded']==0,'Native preset/target gate changed')
                    if seed is not None:demand(saved['checkpoint_sha256']==fitted[block,arm,seed]['checkpoint_sha256'],'Native fitted model binding changed')
                else:
                    demand(saved['selection_decisions_sha256']==dh and saved['derived_selection_view']
                           and saved['new_neural_forward']==saved['new_optimization_training']==saved['target_labels_joined']==0,'Derived view decisions and0 extra forward/fit required')
            probability_contract(out)
            if seed is None:
                demand(saved['seeds']==list(SOURCE_SEEDS) and (arm==SELECTED_ARM or saved['all3_fixed_seeds_retained']),'Fixed3seed ensemble required')
                if arm==SELECTED_ARM:
                    arms=[choice[block,s] for s in SOURCE_SEEDS];sources={str(prediction_path(scope,a,block,s)):sha(prediction_path(scope,a,block,s)) for s,a in zip(SOURCE_SEEDS,arms)}
                    same=len(set(arms))==1
                    demand(saved['chosen_preset_by_seed']==dict(zip(map(str,SOURCE_SEEDS),arms)) and saved['native_source_files_sha256']==sources
                           and saved['identity_to_complete_native_preset_ensemble']==same,'Derived ensemble exact9 sealed choices/source hashes required')
                    if same:
                        source=prediction_path(scope,arms[0],block)
                        demand(Path(saved['identity_native_source_path']).resolve()==source.resolve() and saved['identity_native_source_sha256']==sha(source)
                               and out==read(source)['predictions'],'Derived native identity must remain unchanged')
                for sid,v in out.items():
                    if v['valid']:
                        prob=np.mean([x[sid]['probabilities'] for x in preds],axis=0,dtype=np.float64).tolist()
                        demand(prob==v['probabilities'] and sorted(range(len(prob)),key=lambda i:(-prob[i],i))==v['order'],'Saved fixed3mean/order changed')
            else:
                demand(saved['seed']==seed,'Original seed required');preds.append(out)
                if arm==SELECTED_ARM:
                    native=prediction_path(scope,saved['chosen_preset'],block,seed)
                    demand(saved['chosen_preset']==choice[block,seed] and Path(saved['native_source_path']).resolve()==native.resolve()
                           and saved['predictions']==read(native)['predictions'] and saved['native_source_sha256']==sha(native),'Derived seed must reuse validation-chosen native file')
            rs=[outcome(s,out[s],by[s],gold[s],name) for s in ids]
            if locked:
                original='AB_GLOBAL/'+block+('/seed_'+str(seed) if seed is not None else '')
                demand(summary(rs)==old157['source_cohorts'][scope]['condition_table'][original],'Read-only157 GLOBAL original metrics must stay unchanged')
            for r in rs:r.update(cohort=scope,replication_block=block,training_seed=seed,new_native=arm in NATIVE_ARMS,derived=arm==SELECTED_ARM,cached_ours=locked)
            table[name],rows[name],values[arm,seed]=summary(rs),rs,{r['sample_id']:r for r in rs}
    return table,rows,values


def paired_row(main,other,ids,size,draws):
    row=statistics.binary_family_row([main[s]['Top1'] for s in ids],[other[s]['Top1'] for s in ids],size)
    for metric in ('MRR','Top3'):
        diff=np.asarray([float(main[s][metric])-float(other[s][metric]) for s in ids],dtype=np.float64)
        row[metric]={'difference':float(diff.mean()),'paired_task_bootstrap95_interval':np.quantile(diff[draws].mean(1),[.025,.975]).tolist(),
                     'bootstrap_draws':statistics.BOOTSTRAP_DRAWS,'bootstrap_seed':statistics.BOOTSTRAP_SEED,'descriptive_only':True}
    return row


def run():
    p,models,seals,choices=verify_seals();demand(not (E/'comparison.json').exists() and not (E/'label_join_started.json').exists(),'159 scoring already started')
    freeze_evaluation();write_new(E/'label_join_started.json',{'at_utc':now(),'all_native_and_derived_sealed':True,'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),
                  'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json'),'target_Gold_or_oldscore_decodes_before_seal_by_evaluator':0})
    old157=metadata_prefix(E157/'comparison.json',{'primary','source_cohorts','core_joint_Holm6','mechanism_joint_Holm6','split_sensitivity','same_development_split_agreement'})
    old153=metadata_prefix(E153/'comparison.json',{'primary','source_cohorts','core_Holm3','historical_references_preserving_original_method_identity'})
    old155=metadata_prefix(E155/'comparison.json',{'primary','source_cohorts','core_joint_Holm8','mechanism_joint_Holm8','seed_and_block_stability'})
    old158=metadata_prefix(E158/'comparison.json',{'primary','underlying_locked_primary','source_cohorts','main_joint_Holm3','preset_joint_Holm4'})
    demand(old157['primary']==old153['primary']==old155['primary']==old158['underlying_locked_primary']=='AB_GLOBAL','Old underlying primary identity changed')
    labels={};gold_cache=source_gold(p,labels);results,native,derived,cached,changes,csvrows,vectors={},[],[],[],{},[],{}
    for scope in COHORTS:
        spec=p['target_cohorts'][scope];ids=spec['sample_ids'];by=public_by(spec['public_records'],ids);gold={s:gold_cache[spec['label_source']][s] for s in ids}
        demand(len(ids)==spec['n'] and len({r['task_group'] for r in by.values()})==len(ids),'Full independent original source task denominator required')
        blocks={}
        for block in BLOCKS:
            table,rows,values=score_scope(scope,block,ids,by,gold,old157,choices,models);vectors[scope,block]=values
            blocks[block]={'condition_table':table,'descriptive_strata':descriptive_strata(rows,ids,by,gold)}
            for arm in ALL_BASELINES:changes[f'{scope}_{block}_GLOBAL_vs_{arm}']=counterexamples(values['AB_GLOBAL',None],values[arm,None],ids,by,gold,PRIMARY+'/'+block,arm+'/'+block)
            for name,rs in rows.items():
                (cached if name.startswith(PRIMARY) else derived if name.startswith(SELECTED_ARM) else native).extend(rs)
                stat=table[name];csvrows.append({'cohort':scope,'replication_block':block,'condition':name,**stat['record_equal'],'records':stat['records'],'groups':stat['groups'],'hits':stat['hits'],'invalid':stat['invalid_predictions']})
        results[scope]={'n':len(ids),'groups':len({r['task_group'] for r in by.values()}),'blocks':blocks,
                        'old157_SF_REF_AB_REF_and_GLOBAL_all_seed_split_tables':old157['source_cohorts'][scope],
                        'old153_all_references':old153['source_cohorts'][scope],'old155_all_references':old155['source_cohorts'][scope],
                        'old158_original_split_complete_paper_presets_and_selected':old158['source_cohorts'][scope],
                        'older_stronger_method_identities':old153['historical_references_preserving_original_method_identity'][scope]}
    ids=p['target_cohorts']['coding363']['sample_ids'];draws=statistics.bootstrap_indices(len(ids));core,presets={},{}
    for block in BLOCKS:
        values=vectors['coding363',block]
        core[f'{block}_coding363_GLOBAL_vs_{SELECTED_ARM}']=paired_row(values['AB_GLOBAL',None],values[SELECTED_ARM,None],ids,3,draws)
        for arm in NATIVE_ARMS:presets[f'{block}_coding363_GLOBAL_vs_{arm}']=paired_row(values['AB_GLOBAL',None],values[arm,None],ids,6,draws)
    core,presets=statistics.family(core,3),statistics.family(presets,6)
    demand(set(core)==set(CORE_KEYS) and set(presets)==set(PRESET_KEYS) and (len(native),len(derived),len(cached))==(51720,25860,25860),'Exact families/native-derived-cached counts required')
    references={'old153':old153,'old155':old155,'old157':old157,'old158':old158,'old_p_and155FAIL_not_changed':True,'all_old_stronger_SF_including_agentic363_retained':True}
    result={'at_utc':now(),'experiment':'Exp159','primary':PRIMARY,'source_cohorts':results,'main_joint_Holm3':core,'preset_joint_Holm6':presets,
            'native_per_task_outcomes':native,'derived_per_task_outcomes':derived,'cached157_ours_per_task_outcomes':cached,'validation_choices':choices,
            'native_outputs':51720,'derived_records_not_new_outputs':25860,'new_AF_training':0,'cached_references':references,
            'all4source_full_denominators':True,'no_best_target_preset_or_split_no9modelensemble':True,'old155_5ppFAIL_preserved':True,
            'protocol_sha256':sha(E/'protocol.json'),'model_seal_sha256':sha(E/'training/all_models_sealed.json'),'choices_seal_sha256':sha(E/'validation_selection_sealed.json'),
            'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json')}
    write_new(E/'comparison.json',result);write_new(E/'paired_counterexamples.json',{'records_by_pair':changes,'comparison_sha256':sha(E/'comparison.json'),'descriptive_only':True})
    with (E/'metrics.csv').open('x',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(csvrows[0]));writer.writeheader();writer.writerows(csvrows)
    write_new(E/'Gold_evaluation_receipt.json',{'at_utc':now(),'labels_sha256':labels,'old_reference_files_sha256':{str(r/'comparison.json'):sha(r/'comparison.json') for r in (E153,E155,E157,E158)},
             'comparison_sha256':sha(E/'comparison.json'),'target_joins':2155,'new_Gold':0,'all_native_and_derived_before_join':True})
    packet={'at_utc':now(),'experiment':'Exp159','primary':PRIMARY,'source_denominators':{c:results[c]['n'] for c in COHORTS},
            'ensemble_hits':{c:{b:{a:results[c]['blocks'][b]['condition_table'][(PRIMARY if a=='AB_GLOBAL' else a)+'/'+b]['hits'] for a in (*ALL_BASELINES,'AB_GLOBAL')} for b in BLOCKS} for c in COHORTS},
            'main_joint_Holm3':compact_pairs(core),'preset_joint_Holm6':compact_pairs(presets),'validation_choices':choices,'cached_references':references,
            'paired_change_counts':{k:{f:v for f,v in r.items() if f!='records'} for k,r in changes.items()},'new_valid_stages':18,'new_models':18,'native_outputs':51720,
            'derived_not_new_outputs':25860,'new_cached_ours_forward':0,'source_only_no_AF_claim':True,'paper50_10_vs_cached157_40_8_budget_unequal':True,
            'old_p_155FAIL_and_strongerSF363_preserved':True,'fee_CNY':'0','decision_owner':'root','comparison':str(E/'comparison.json')}
    write_new(E/'main_decision_packet.json',packet);status('EVALUATION_COMPLETE',new_ranker_outputs=51720,derived_selection_view_records=25860,target_label_values_joined=2155,
             next='finalize159.py mechanical resource/final audit only; root owns interpretation')


if __name__=='__main__':run()

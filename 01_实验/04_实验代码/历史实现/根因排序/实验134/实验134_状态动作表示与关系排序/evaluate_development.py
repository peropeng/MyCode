"""Once-only exposed32 diagnostic AFTER all15 model checkpoints are sealed."""
import argparse
from collections import Counter
import json
import os
import re
import sys
import time
sys.dont_write_bytecode=True
import numpy as np
import torch
from common import *
import models
import train
import prepare_features

OLD133=ROOT/'工作区/1006-exp133-state-action/实验/实验133_状态动作选择性核验'
OLD132=ROOT/'工作区/1005-exp132-paper-three'

def scoped_exposed_gold(records):
    vault=OLD132/'scratch/exp132/agentracer_private_step_labels.jsonl'
    mapping_sha=read(OLD132/'实验/实验132_论文驱动三案归因对比/engineering_v2/interface_repair_v5/results/protocol.json')['old_private_mapping_sha256']
    if sha(vault)!=mapping_sha:raise RuntimeError('immutable_old_mapping_changed')
    wanted={r['record_id']:r['sample_id'] for r in records};gold={}
    with vault.open('rb') as f:
        for line in f:
            match=re.search(rb'"record_id"\s*:\s*"([^"\\]+)"',line)
            if not match or match.group(1).decode() not in wanted:continue
            row=json.loads(line);sid=wanted[row['record_id']]
            if sid in gold:raise RuntimeError('duplicate_exposed32_label')
            gold[sid]=row['zero_based_public_ordinal']
    if set(gold)!=set(wanted.values()):raise RuntimeError('exposed32_label_missing')
    return gold

def changes(left,right,labels):
    sid=list(labels);rescue=[s for s in sid if left[s]['chosen_step']!=labels[s] and right[s]['chosen_step']==labels[s]]
    corruption=[s for s in sid if left[s]['chosen_step']==labels[s] and right[s]['chosen_step']!=labels[s]]
    return {'n':len(sid),'left_wrong_right_rescued':len(rescue),'left_right_right_corrupted':len(corruption),
        'net_rescue_minus_corruption':len(rescue)-len(corruption),'rescue_sample_ids':rescue,'corruption_sample_ids':corruption}

def run():
    modelseal=read(E/'training/model_seal.json')
    if not modelseal['all15_fixed_runs_frozen'] or len(modelseal['models'])!=15:raise RuntimeError('all15_model_freeze_required_before_old32')
    protocol,_,training_labels,training_ids,training_public,scaler=train.inputs()
    for receipt in modelseal['models']:
        if sha(receipt['checkpoint'])!=receipt['checkpoint_sha256']:raise RuntimeError('frozen_checkpoint_changed')
    oldprotocol=read(OLD133/'development/protocol.json');public_path=OLD133/'development/public_fixture.json'
    if sha(public_path)!=oldprotocol['public_fixture_sha256']:raise RuntimeError('immutable_old32_public_fixture_changed')
    fixtures=read(public_path)['records'];records=[f['record'] for f in fixtures]
    if len(records)!=32 or [r['sample_id'] for r in records]!=oldprotocol['cohort_sample_ids']:raise RuntimeError('fixed_exposed32_mismatch')
    status('EXP134_EXPOSED32_LABEL_FREE_INFERENCE',exposed_development_tasks_total=32,exposed32_labels_accessed=0,
        next_executable_command='evaluate_development.py run (exact checkpoints frozen; no new test pool)')
    path=E/'features/exposed32_features.pt'
    if not path.exists():prepare_features.build(records,'exposed32_features.pt',allow_old_cache=True)
    if sha(path)!=read(path.with_suffix('.receipt.json'))['feature_file_sha256']:raise RuntimeError('exposed32_feature_seal_changed')
    features=torch.load(path,map_location='cpu',weights_only=False)['records'];ids=[r['sample_id'] for r in records]
    by={r['sample_id']:r for r in records};device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    seeds={};ensembles={};start=time.monotonic()
    predictions_path=E/'development/predictions.json'
    if not predictions_path.exists():
        for arm in ARMS:
            seeds[arm]={}
            for seed in SEEDS:
                receipt=next(r for r in modelseal['models'] if r['arm']==arm and r['seed']==seed)
                checkpoint=torch.load(receipt['checkpoint'],map_location='cpu',weights_only=False)
                model=models.create(arm).to(device);model.load_state_dict(checkpoint['state_dict'])
                seeds[arm][str(seed)]=train.predict(model,arm,ids,features,scaler,device);del model;torch.cuda.empty_cache()
            ensembles[arm]={}
            for sid in ids:
                probabilities=np.mean([seeds[arm][str(seed)][sid]['probabilities'] for seed in SEEDS],axis=0).tolist()
                order=sorted(range(len(probabilities)),key=lambda i:(-probabilities[i],i))
                ensembles[arm][sid]={'probabilities':probabilities,'order':order,'chosen_step':order[0],'valid':True}
        original_events,_=prepare_features.load_original_events();controls={}
        for fixture in fixtures:
            record=fixture['record'];sid=record['sample_id'];order=fixture['A_order'];a=order[0]
            for name,pred in fixture['cached_baselines'].items():controls.setdefault(name+'_ORIGINAL_CACHED',{})[sid]=pred
            aa=fixture['cached_baselines']['AA'];aa_choice=aa.get('chosen_step') if aa.get('valid') else None
            for name,step in original_events.controls(record,fixture['packet'],a,aa_choice).items():
                controls.setdefault(name,{})[sid]=original_events.ranked_prediction(step,order,zero_API=True)
            controls.setdefault('A_ORIGINAL_SOURCE_FROZEN',{})[sid]=original_events.ranked_prediction(a,order)
        write_new(predictions_path,{'at_utc':now(),'seed_predictions':seeds,'ensemble_predictions':ensembles,
            'controls':controls,'sample_ids':ids,'new_unexposed_Gold_access':0,'models_seal_sha256':sha(E/'training/model_seal.json')})
        write_new(E/'development/prediction_seal.json',{'at_utc':now(),'predictions_sha256':sha(predictions_path),
            'models_seal_sha256':sha(E/'training/model_seal.json'),'protocol_sha256':sha(E/'training_protocol.json'),
            'exposed32_tasks':32,'all15_models_frozen_before_diagnostics':True,'labels_used_during_predictions':0})
    seal=read(E/'development/prediction_seal.json')
    if seal['predictions_sha256']!=sha(predictions_path) or seal['models_seal_sha256']!=sha(E/'training/model_seal.json'):raise RuntimeError('prediction_seal_changed')
    if (E/'development/comparison.json').exists():raise RuntimeError('once_only_diagnostic_already_scored')
    predictions=read(predictions_path);labels=scoped_exposed_gold(records)
    def safe_metric(preds):
        valid={sid:p for sid,p in preds.items() if p.get('valid') is True and p.get('chosen_step') is not None}
        result={'n':32,'hits':sum(p['chosen_step']==labels[sid] for sid,p in valid.items()),'valid':len(valid),'invalid':32-len(valid)}
        result['exact_step_accuracy']=result['hits']/32
        result['domain']={d:{'n':sum(by[sid]['domain']==d for sid in ids),
            'hits':sum(p['chosen_step']==labels[sid] and by[sid]['domain']==d for sid,p in valid.items())} for d in ('coding','math')}
        return result
    table={arm:{'ensemble':train.metrics(predictions['ensemble_predictions'][arm],labels,by),
        'seeds':{str(seed):train.metrics(predictions['seed_predictions'][arm][str(seed)],labels,by) for seed in SEEDS}} for arm in ARMS}
    control_table={name:safe_metric(preds) for name,preds in predictions['controls'].items()}
    pairs={'A_vs_N':('N','A'),'B_vs_N':('N','B'),'AB_vs_N':('N','AB'),'AB_vs_A':('A','AB'),
        'AB_vs_B':('B','AB'),'AB_vs_retrained_StepFinder':('StepFinder','AB')}
    ablation={name:changes(predictions['ensemble_predictions'][a],predictions['ensemble_predictions'][b],labels) for name,(a,b) in pairs.items()}
    validation=read(E/'training/validation_comparison.json')
    validation_predictions=read(E/'training/validation_ensemble_predictions.json')['predictions']
    validation_labels={sid:training_labels[sid] for sid in training_ids['validation']}
    validation_changes={name:changes(validation_predictions[a],validation_predictions[b],validation_labels) for name,(a,b) in pairs.items()}
    event_controls,_=prepare_features.load_original_events();validation_priors={}
    for sid in training_ids['validation']:
        record=training_public[sid];packet=event_controls.representation(record)
        for name,step in event_controls.controls(record,packet,0,None).items():
            if name.startswith('PRI_'):validation_priors.setdefault(name,{})[sid]=step
    validation_control_table={name:{'n':len(validation_labels),'hits':sum(step==validation_labels[sid] for sid,step in values.items()),
        'exact_step_accuracy':sum(step==validation_labels[sid] for sid,step in values.items())/len(validation_labels),
        'zero_API':True} for name,values in validation_priors.items()}
    result={'at_utc':now(),'schema':'Exp134-same-data-supervised-exposed32-development/1.0','scope':'already exposed32 development only; not independent confirmation',
        'table':table,'original_cached_and_zero_API_controls':control_table,'component_changes':ablation,
        'validation_table':validation['table'],'validation_component_changes':validation_changes,'validation_zero_API_controls':validation_control_table,
        'parameter_counts':protocol['parameters'],'model_seal_sha256':sha(E/'training/model_seal.json'),
        'prediction_seal_sha256':sha(E/'development/prediction_seal.json'),'all3_seeds_reported':True,'ensemble_rule':'fixed mean of all3 per-trajectory softmax',
        'supervised_adaptation_not_mixed_with_prior_zero_shot_claims':True,'selected_already_exposed_test_labels_used':32,'unexposed_test_label_values_used':0,
        'original_annotation_target_and_raw_ordinals_unchanged':True,'AA_projection_is_separately_named_control_not_ours':True,
        'paid_API_calls':0,'inference_elapsed_seconds':time.monotonic()-start}
    write_new(E/'development/comparison.json',result)
    write_new(E/'development/Gold_evaluation_receipt.json',{'at_utc':now(),'already_exposed32_labels_used':32,'unexposed_test_labels_used':0,
        'all_models_and_predictions_sealed_before_labels':True,'comparison_sha256':sha(E/'development/comparison.json')})
    packet={'at_utc':now(),'phase_complete':'local supervised validation and exposed32 diagnostics','overall_research_complete':False,
        'validation':validation['table'],'validation_component_changes':validation_changes,'validation_zero_API_controls':validation_control_table,
        'exposed32':table,'controls':control_table,'component_changes':ablation,
        'parameters':protocol['parameters'],'models_seal':str(E/'training/model_seal.json'),'model_hashes':modelseal['models'],
        'encoder_receipts':[str(E/'features/train_validation_features.receipt.json'),str(E/'features/exposed32_features.receipt.json')],
        'paid_API_calls':0,'balance_CNY':'4.55','reserved_confirmation_CNY':'2.25','remaining_unexposed_pool_protected':True,
        'minimum_required_main_decision':'Review validation and frozen development evidence, then decide whether and which method to freeze for new32 same-cohort four-baseline confirmation; do not choose a best seed',
        'ready_local_models_for_new_public_cohort':True,'fresh_labels_accessed':0}
    write_new(E/'main_decision_packet.json',packet)
    status('EXP134_LOCAL_STAGE_SCORED_AWAITING_MAIN_DECISION',exposed_development_tasks_complete=32,exposed_development_tasks_total=32,
        already_exposed32_labels_accessed=32,completed_training_runs=15,total_training_runs=15,current_pid=None,current_command=None,
        comparison=str(E/'development/comparison.json'),main_decision_packet=str(E/'main_decision_packet.json'),
        next_executable_command='Main chat supplies exact fresh protocol/scientific continuation; no automatic fresh-label reads')
    print(canonical({'exposed32_ensemble_hits':{a:v['ensemble']['hits'] for a,v in table.items()},
        'validation_ensemble_hits':{a:v['ensemble']['hits'] for a,v in validation['table'].items()},'component':ablation,'paid_API_calls':0}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('run',));args=parser.parse_args();run()

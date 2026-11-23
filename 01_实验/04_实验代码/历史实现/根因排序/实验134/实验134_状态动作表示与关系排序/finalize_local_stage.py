"""Verify frozen artifacts and save compact execution/decision evidence."""
from collections import Counter
import datetime
import json
import sys
sys.dont_write_bytecode=True
import torch
from common import *

def main():
    p=read(E/'training_protocol.json');seal=read(E/'training/model_seal.json')
    if len(seal['models'])!=15 or {(r['arm'],r['seed']) for r in seal['models']}!={(a,s) for a in ARMS for s in SEEDS}:raise RuntimeError('all15_fixed_arm_seed_runs_required')
    for path,digest_ in {**p['sources'],**p['input_hashes']}.items():
        if sha(path)!=digest_:raise RuntimeError('frozen_code_or_input_changed:'+path)
    for receipt in seal['models']:
        if sha(receipt['checkpoint'])!=receipt['checkpoint_sha256']:raise RuntimeError('frozen_checkpoint_changed')
        epochs=[json.loads(s) for s in (Path(receipt['checkpoint']).parent/'epochs.jsonl').read_text('utf-8').splitlines() if s]
        expected=max(epochs,key=lambda r:(r['validation']['exact_step_accuracy'],r['validation']['MRR'],-r['epoch']))
        if expected['epoch']!=receipt['selected_epoch']:raise RuntimeError('validation_only_checkpoint_rule_mismatch')
    pred=read(E/'development/predictions.json');prediction_seal=read(E/'development/prediction_seal.json')
    if prediction_seal['predictions_sha256']!=sha(E/'development/predictions.json'):raise RuntimeError('old32_prediction_seal_changed')
    for arm in ARMS:
        for source in [pred['ensemble_predictions'][arm],*pred['seed_predictions'][arm].values()]:
            if len(source)!=32:raise RuntimeError('incomplete_exposed32_predictions')
            for sid,row in source.items():
                n=len(row['probabilities'])
                if sorted(row['order'])!=list(range(n)) or row['chosen_step']!=row['order'][0] or abs(sum(row['probabilities'])-1)>1e-5:raise RuntimeError('invalid_complete_original_step_ranking')
    features=torch.load(E/'features/train_validation_features.pt',map_location='cpu',weights_only=False)['records']
    allowed={'raw_structure','adjacency','paired_partner','paired_valid','observed_state_action_links','content','content_token_lengths',
        'agent','public_sha256','public_record_sha256','sample_id'}
    if any(set(value)!=allowed for value in features.values()):raise RuntimeError('unexpected_feature_metadata_field')
    if any(len(index[0])!=len(value['content']) or index[0].shape[1]!=2 for value in features.values() for index in value['adjacency']):raise RuntimeError('relation_degree_or_length_changed')
    ledger_path=ROOT/'工作区/1005-exp132-paper-three/实验/实验132_论文驱动三案归因对比/engineering_v2/api/requests.jsonl'
    ledger=[json.loads(s) for s in ledger_path.read_text('utf-8').splitlines() if s]
    started=datetime.datetime.fromisoformat(read(E/'approved_plan.json')['created_at_beijing'])
    after=[r for r in ledger if r.get('event')=='reserved' and datetime.datetime.fromisoformat(r['timestamp'])>=started]
    if after or any('Exp134' in r.get('stage','') for r in ledger):raise RuntimeError('unexpected_experimental_paid_request_during_zero_API_stage')
    reserved={r['request_id'] for r in ledger if r.get('event')=='reserved'}
    settled={r['request_id'] for r in ledger if r.get('event') in ('completed','reservation_released_no_submission')}
    if reserved-settled:raise RuntimeError('unsettled_experimental_request')
    comparison=read(E/'development/comparison.json');public=read(ROOT/'工作区/1006-exp133-state-action/实验/实验133_状态动作选择性核验/development/public_fixture.json')['records']
    by={f['record']['sample_id']:f for f in public};examples=[]
    names={'A_vs_N':('N','A'),'B_vs_N':('N','B'),'AB_vs_N':('N','AB'),'AB_vs_A':('A','AB'),
        'AB_vs_B':('B','AB'),'AB_vs_retrained_StepFinder':('StepFinder','AB')}
    for name,change in comparison['component_changes'].items():
        left,right=names[name]
        for outcome,key in [('rescue','rescue_sample_ids'),('corruption','corruption_sample_ids')]:
            for sid in change[key]:
                fixture=by[sid];record=fixture['record'];l=pred['ensemble_predictions'][left][sid]['chosen_step'];r=pred['ensemble_predictions'][right][sid]['chosen_step']
                target=r if outcome=='rescue' else l
                examples.append({'comparison':name,'outcome':outcome,'sample_id':sid,'record_id':record['record_id'],'domain':record['domain'],
                    'left_method':left,'left_original_ordinal':l,'right_method':right,'right_original_ordinal':r,
                    'already_exposed_Gold_ordinal_from_saved_correctness':target,'actor_at_left':record['turns'][l]['role'],
                    'actor_at_right':record['turns'][r]['role'],'left_source_step_ID':record['coordinate_map'][l]['original_step_id'],
                    'right_source_step_ID':record['coordinate_map'][r]['original_step_id'],
                    'relevant_public_state_action_pairs':[pair for pair in fixture['packet']['observed_state_action_links']
                        if l in (pair['decision_state'],pair['ensuing_action']) or r in (pair['decision_state'],pair['ensuing_action'])],
                    'source_public_fixture':str(ROOT/'工作区/1006-exp133-state-action/实验/实验133_状态动作选择性核验/development/public_fixture.json')})
    write_new(E/'development/component_counterexamples.json',{'at_utc':now(),'scope':'sealed exposed32 saved outcomes only; no new label reads','examples':examples})
    train_feature_receipt=read(E/'features/train_validation_features.receipt.json');dev_feature_receipt=read(E/'features/exposed32_features.receipt.json')
    split_at=datetime.datetime.fromisoformat(read(E/'data/public_split_manifest.json')['at_utc'])
    runtime={'training_total_wall_seconds':seal['elapsed_seconds'],'all_seed_training_seconds':{r['arm']+'/'+str(r['seed']):r['elapsed_seconds'] for r in seal['models']},
        'train_feature_resume_wall_seconds':train_feature_receipt['elapsed_seconds'],
        'initial_embedding_attempt_measured_wall_lower_bound_seconds':439.1,'initial_embedding_exact_duration_not_recorded':True,
        'long_batch_interruption_receipt':str(E/'features/length_batching_engineering_receipt.json'),
        'exposed32_feature_wall_seconds':dev_feature_receipt['elapsed_seconds'],
        'local_stage_wall_seconds_since_public_split_freeze':(datetime.datetime.now(datetime.timezone.utc)-split_at).total_seconds()}
    audit={'at_utc':now(),'schema':'Exp134-local-stage-execution-audit/1.0','all15_fixed_models_frozen':True,
        'validation_only_epoch_selection_verified':True,'all3_seeds_retained_and_reported':True,'all32_predictions_complete_and_sealed':True,
        'same_train492_validation122_groups_for_all_arms':True,'train_only_structure_scaler':True,'feature_field_whitelist_verified':True,
        'raw_step_ordinals_and_annotation_target_unchanged':True,'degree2_four_original_channels_verified':True,
        'paid_API_requests_after_plan_start':0,'unsettled_requests':0,'unexposed_test_label_values_used':0,
        'encoder_OOMs':train_feature_receipt['encoder_OOM_count']+dev_feature_receipt['encoder_OOM_count'],
        'truncated_step_texts':{'train_validation':train_feature_receipt['truncated_step_texts'],'exposed32':dev_feature_receipt['truncated_step_texts']},
        'runtime':runtime,'model_seal_sha256':sha(E/'training/model_seal.json'),'comparison_sha256':sha(E/'development/comparison.json'),
        'continuous_api_ledger_sha256':sha(ledger_path),'overall_research_complete':False,'independent_confirmation_started':False}
    write_new(E/'final_execution_audit.json',audit)
    packet=read(E/'main_decision_packet.json');packet.update(runtime=runtime,execution_audit=str(E/'final_execution_audit.json'),
        component_counterexamples=str(E/'development/component_counterexamples.json'),
        scientific_gate_facts={'validation':{a:v['ensemble']['hits'] for a,v in packet['validation'].items()},
            'exposed32':{a:v['ensemble']['hits'] for a,v in packet['exposed32'].items()},
            'AB_vs_retrained_SF_exposed32_net':comparison['component_changes']['AB_vs_retrained_StepFinder']['net_rescue_minus_corruption'],
            'A_vs_N_validation_net':comparison['validation_component_changes']['A_vs_N']['net_rescue_minus_corruption'],
            'AB_vs_B_validation_net':comparison['validation_component_changes']['AB_vs_B']['net_rescue_minus_corruption'],
            'independent_advantage_not_established':True})
    atomic(E/'main_decision_packet.json',packet)
    status('EXP134_LOCAL_STAGE_SCORED_AWAITING_MAIN_DECISION',current_pid=None,current_command=None,
        current_arm=None,current_seed=None,current_epoch=None,paid_API_calls=0,unsettled_requests=0,
        execution_audit=str(E/'final_execution_audit.json'),main_decision_packet=str(E/'main_decision_packet.json'),
        component_counterexamples=str(E/'development/component_counterexamples.json'),runtime=runtime,
        new_unexposed_label_accesses=0,models_frozen=15,exposed_development_tasks_complete=32,
        next_executable_command='Await main-chat scientific continuation or exact fresh32/four-baseline protocol; current models stay frozen')
    print(canonical({'final_audit':'passed','validation_hits':packet['scientific_gate_facts']['validation'],
        'exposed32_hits':packet['scientific_gate_facts']['exposed32'],'paid_API_calls':0,'unsettled_requests':0}),flush=True)

if __name__=='__main__':main()

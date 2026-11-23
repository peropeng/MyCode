"""Freeze complete fresh cohort/conditions/scorer and same-ledger funding."""
from decimal import Decimal
import sys
from shared import *

def main():
    check=read(T/'contract_check.json');scope=read(T/'public_scope_seal.json');decision=read(T/'approved_decision.json')
    if sha(T/'fresh_public_records.json')!=scope['public_records_sha256'] or sha(T/'fresh_sample_manifest.json')!=scope['manifest_sha256']:raise RuntimeError('fresh_public_scope_changed')
    inherited=read(ROOT/'工作区/1006-exp133-state-action/实验/实验133_状态动作选择性核验/authorization_development.json')
    ledger=lines(API/'requests.jsonl');epoch='Exp132-20261005-three-paper-plans'
    reserved={r['request_id']:Decimal(r['reserved_cny']) for r in ledger if r.get('event')=='reserved' and r.get('epoch_id')==epoch}
    closed={r['request_id']:Decimal(r['cost_upper_cny']) for r in ledger if r.get('event')=='completed' and r.get('epoch_id')==epoch}
    released={r['request_id'] for r in ledger if r.get('event')=='reservation_released_no_submission'}
    if set(reserved)-set(closed)-released:raise RuntimeError('prior_unknown_charge_blocks_fresh')
    anchor=sum(closed.values(),Decimal(0));auth=dict(inherited)
    auth['allowed_sample_ids']=[r['sample_id'] for r in read(T/'fresh_public_records.json')['records']]
    auth['balance_floor_cny']='1.00';auth['balance_safety_margin_cny']='0.02'
    auth['existing_account_funding_amendment']=dict(inherited['existing_account_funding_amendment'])
    auth['existing_account_funding_amendment']['fixed_bucket_caps_CNY']={
        **inherited['existing_account_funding_amendment']['fixed_bucket_caps_CNY'],'EXP134_CONFIRMATION':'2.25'}
    auth['exp134_confirmation_budget']={'cap_CNY':'2.25','anchor_epoch_usage_CNY':str(anchor),
        'root_decision_sha256':sha(T/'approved_decision.json'),'account_floor_plus_margin_CNY':'1.02',
        'reallocation_needs_root_stage_amendment':True,'new_epoch':False,'prior_costs_refunded':False}
    write(T/'authorization_v1.json',auth)
    files=[T/name for name in ('shared.py','select_public.py','paid_methods.py','paired_stats.py','paired_statistics_reference.py',
        'check_contract.py','freeze_protocol.py','predict_local.py','run_paid.py','score_fresh.py','approved_decision.json',
        'fresh_public_records.json','fresh_sample_manifest.json','public_scope_seal.json','historical_exposure_ledger.json','contract_check.json',
        'authorization_v1.json','inherited_ledger.jsonl','closed_v1_ledger_prefix.jsonl')]
    files.extend(p for p in RES.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    files.extend([E/'training_protocol.json',E/'training/model_seal.json',E/'common.py',E/'models.py',E/'train.py',E/'prepare_features.py'])
    files.extend(Path(r['checkpoint']) for r in read(E/'training/model_seal.json')['models'])
    files.extend([ROOT/'工作区/1006-exp133-state-action/实验/实验133_状态动作选择性核验/method.py',
        ROOT/'工作区/1006-exp133-state-action/实验/实验133_状态动作选择性核验/development_v2/method.py'])
    records=read(T/'fresh_public_records.json')['records']
    protocol={'at_utc':now(),'schema':'Exp134-fixed-B-full-fresh-confirmation/1.0','primary':'B','n_independent_tasks':len(records),
        'conditions':list(CONDITIONS),'primary_comparators':list(PRIMARY_COMPARATORS),'primary_family_tests':13,
        'secondary_component_pairs':[list(x) for x in SECONDARY_PAIRS],'secondary_family_tests':9,
        'seeds':list(SEEDS),'ensemble':'all3 per-trajectory softmax means; no best-seed selection',
        'paid_condition_rotation':list(PAID),'sample_ids':[r['sample_id'] for r in records],
        'schedule':[{'sample_id':r['sample_id'],'conditions':list(CONDITIONS),'paid_order':list(PAID)} for r in records],
        'frozen_files':{str(p):sha(p) for p in files},'authorization_file':str(T/'authorization_v1.json'),
        'funding_anchor_epoch_usage_CNY':str(anchor),'phase_upper_CNY':'2.25','shared_api_ledger':str(API/'requests.jsonl'),
        'shared_ledger_initial_sha256':sha(API/'requests.jsonl'),'single_original_epoch_unchanged':True,
        'model_seal_sha256':decision['model_seal_sha256'],'source_private_mapping_sha256':read(ROOT/'工作区/1005-exp132-paper-three/实验/实验132_论文驱动三案归因对比/metadata/agentracer_exact_step_qualification.json')['private_label_vault_sha256'],
        'baseline_caps':{'AA':2048,'Binary_each_decision':128,'SDBL_scope':2048,'SDBL_localization':2048,'AA_STRUCTURED':1200},
        'baseline_parser':'pinned native parsers; exact public actor plus parenthesized qualifier normalized; native strings and ordinals retained',
        'no_fabricated_fullrank_for_single_choice':True,'original_and_projection_conditions_separate':True,
        'no_labels_until_all_scheduled_rows_sealed':True,'no_generated_resampling_or_midscore':True,
        'budget_failure':'stop complete queue; preserve exact next request/reservation and all missing tasks/conditions for root reallocation',
        'unknown_failure':'stop, preserve full unresolved reservation; no automatic reissue','fresh_Gold_accesses':0}
    write(T/'protocol.json',protocol)
    CORE.status('EXP134_CONFIRMATION_PROTOCOL_FROZEN',fresh_confirmation={'completed_tasks':0,'total_tasks':len(records),'unexposed_test_label_accesses':0},
        paid_API_calls=0,confirmation_protocol=str(T/'protocol.json'),next_executable_command='confirmation/predict_local.py then confirmation/run_paid.py')
    print(canonical({'fresh_confirmation_frozen':len(records),'conditions_each':len(CONDITIONS),'scheduled_rows':len(records)*len(CONDITIONS),
        'primary_comparisons':len(PRIMARY_COMPARATORS),'phase_cap_CNY':'2.25'}),flush=True)

if __name__=='__main__':main()

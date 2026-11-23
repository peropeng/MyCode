"""Mechanical18fit/config/9choice/native-derived accounting audit only."""
import ast,math
from collections import Counter,defaultdict
from common import *
from evaluate159 import verify_seals,verify_prediction_runtime,scheduled_stages,CORE_KEYS,PRESET_KEYS,EVALUATION_FILES,NATIVE_ARMS,ALL_BASELINES,SELECTED_ARM,cap_metadata


def lines(path):
    return [json.loads(r) for r in Path(path).read_text('utf-8-sig').splitlines() if r.strip()] if Path(path).exists() else []


def run():
    p,models,seals,choices=verify_seals();comparison=read(E/'comparison.json');packet=read(E/'main_decision_packet.json')
    runtime=verify_prediction_runtime()
    code=read(E/'evaluation_code_seal.json');joined=read(E/'label_join_started.json');Gold=read(E/'Gold_evaluation_receipt.json');errors=[]
    def check(ok,name):
        if not ok:errors.append(name)
    check(code['sources']=={str(E/n):sha(E/n) for n in EVALUATION_FILES},'frozen_evaluation_sources')
    check(comparison['primary']==packet['primary']==PRIMARY,'Read-only157_splitGLOBAL_primary_identity')
    check(comparison['protocol_sha256']==sha(E/'protocol.json') and comparison['model_seal_sha256']==sha(E/'training/all_models_sealed.json')
          and comparison['choices_seal_sha256']==sha(E/'validation_selection_sealed.json')
          and comparison['prediction_seal_sha256']==joined['prediction_seal_sha256']==sha(E/'results/all_predictions_sealed.json')
          and comparison['evaluation_code_seal_sha256']==joined['evaluation_code_seal_sha256']==sha(E/'evaluation_code_seal.json')
          and Gold['comparison_sha256']==sha(E/'comparison.json'),'protocol_model_choices_native_derived_Gold_chain')
    check((E/'results/all_predictions_sealed.json').stat().st_mtime_ns<=(E/'evaluation_code_seal.json').stat().st_mtime_ns
          <=(E/'label_join_started.json').stat().st_mtime_ns<=(E/'comparison.json').stat().st_mtime_ns,'all144native_derived_files_precede_Gold_and_oldscore_join')
    check((E/'prediction_runtime_receipt.json').stat().st_mtime_ns<(E/'results/native_predictions_sealed.json').stat().st_mtime_ns
          <(E/'label_join_started.json').stat().st_mtime_ns,'Actual6flag_inference_restoration_before_native_and_Gold')
    for field,keys,size in [('main_joint_Holm3',CORE_KEYS,3),('preset_joint_Holm6',PRESET_KEYS,6)]:
        check(set(comparison[field])==set(keys) and set(code[field])==set(keys),'exact_separate_'+field)
        for key,row in comparison[field].items():
            check(row['family_tests']==size and row['statistically_supported_lead']==
                  (row['difference']>0 and row['holm_adjusted_p']<.05 and row['familywise_difference_interval'][0]>0),'complete_supported_lead_rule:'+key)
    check((len(comparison['native_per_task_outcomes']),len(comparison['derived_per_task_outcomes']),len(comparison['cached157_ours_per_task_outcomes']))
          ==(51720,25860,25860),'native_derived_cached_counts_separate')
    check(comparison['old155_5ppFAIL_preserved'] and comparison['no_best_target_preset_or_split_no9modelensemble']
          and comparison['cached_references']['all_old_stronger_SF_including_agentic363_retained'],'old_p_FAIL_strongSF_and_all_splits_preserved')
    for path,h in {**Gold['labels_sha256'],**Gold['old_reference_files_sha256']}.items():check(sha(path)==h,'unchanged_original_annotation_reference:'+path)
    old=read(E157/'protocol.json');check(p['source_splits']==old['source_splits'],'Exact157_source_splits_not153_membership')
    stages,hashes,histories,caps=[],{},[],[];scalers=defaultdict(set);updates=0
    parent_rows={(r['replication_block'],r['seed']):r for r in old['source_schedule'] if r['arm']=='SF_REF'}
    for row,fit,val,path in scheduled_stages(p):
        rec=read(path);hashes[str(path)]=sha(path);block=row['replication_block'];arm=row['arm'];seed=row['seed'];prior=parent_rows[block,seed]
        check(fit==prior['fit_ids']==old['source_splits'][block]['ids']['train'] and val==prior['validation_ids']==old['source_splits'][block]['ids']['validation']
              and (len(fit),len(val))==(492,122) and not set(fit)&set(val),'Exact157_split_fit_val_IDs:'+str((block,arm,seed)))
        check(Path(row['initialization_path']).resolve()==Path(prior['initialization_path']).resolve()
              and Path(row['initialization_path']).name=='initial.pt' and 'invalid' not in row['initialization_path'].casefold(),'Canonical157_reference_to153_SF_INITIAL')
        check(rec['completed_epochs']==len(rec['history']) and 1<=rec['completed_epochs']<=50
              and [r['epoch'] for r in rec['history']]==list(range(1,rec['completed_epochs']+1)),'Complete_max50_history:'+str(path))
        check(rec['updates']==sum(r['updates'] for r in rec['history']) and all(r['updates']==31 for r in rec['history']),
              '31batch_updates_per492fit_epoch:'+str(path))
        best=max(rec['history'],key=lambda r:(r['validation']['Top1'],r['validation']['MRR'],-r['epoch']))
        check(best['epoch']==rec['selected_epoch'] and all(r['validation']['group_equal'] is False for r in rec['history']),
              'Validation_only_Top1_MRR_earliest_checkpoint')
        cap=cap_metadata(rec);cap['replication_block']=block;caps.append(cap)
        check(rec['hit_epoch_cap']==cap['reached50_epoch_cap'] and rec['selected_epoch_at_cap']==cap['selected_epoch_is50']
              and rec['last_epoch_validation_improved']==cap['final_epoch_improved_validation_best'],'Actual_cap_still_improving_metadata')
        scalers[block].add(rec['scaler_mean_sha256']);updates+=rec['updates'];histories.extend(rec['history'])
        stages.append({k:rec[k] for k in ('suite','replication_block','arm','seed','outer','stage','selected_epoch','completed_epochs','updates','checkpoint','checkpoint_sha256',
            'scaler_fit_ids_sha256','scaler_mean_sha256','initialization_path','initialization_sha256','initialization_state_digest','initialization_training_rng_digest',
            'actual_canonical_training_RNG_restored','actual_model_configuration','actual_preset_configuration','actual_lr','actual_weight_decay','lambda_temporal',
            'max_epochs','patience','runtime_backend_policy','elapsed_seconds')})
    check(len(stages)==len(models['models'])==18 and updates==models['optimizer_updates'] and updates<=27900,'18_actual_fit_models_and_max27900_updates')
    check(set(scalers)==set(BLOCKS) and all(len(v)==1 for v in scalers.values()),'Same_split492_fit_nodes_same_scaler_across6matched_models')
    initial=read(E/'initialization_audit.json');refs=p['initialization_records'];unique=set();signatures={}
    check(initial['status']=='PASS' and initial['records']==refs and len(refs)==18 and len(p['initializations'])==3,'18_preset_references9split_seed_pairs3physical_initials')
    for rec in refs:
        path=Path(rec['path']).resolve();unique.add(str(path));key=rec['seed']
        check(path==(E153/'training/source/SF_REF'/str(rec['seed'])/'initial.pt').resolve() and sha(path)==rec['sha256']
              and rec['valid_153_INITIAL_only'] and rec['trained_parent_weight_loads']==rec['invalid_runtime_asset_loads']==0,'Only_valid153_INITIAL_via157_not_trained_warmstart')
        sig=(str(path),rec['sha256'],rec['state_digest'],canonical(rec['training_rng_digest']))
        if key in signatures:check(signatures[key]==sig,'All_splits_and_both_presets_share_exact_seed_INITIAL_RNG')
        signatures[key]=sig
    check(len(unique)==len(signatures)==3,'Exactly3_unique_canonical_initials_no_new_states')
    inherited=p['inherited_preset_fixture'];check(sha(inherited['path'])==inherited['sha256'],'Inherited158_fixture_hash')
    fixture=read(inherited['path']);check(fixture['status']=='PASS' and fixture['protocol_sha256']==inherited['source_protocol_sha256']
                                       and inherited['rerun_fixture_or_neural_tests']==0,'158_4PASS_fixture_reference_only_not_new159_test_cost')
    necessary=read(E/'necessary_binding_receipt.json');binding=read(E/'split_binding_audit.json')
    check(necessary['status']==binding['status']=='PASS' and necessary['protocol_sha256']==sha(E/'protocol.json')
          and necessary['all18_rows_match_original157_split_initial_and_seed'] and necessary['unique_physical_initial_files']==3
          and necessary['split_seed_preset_pairs']==9 and necessary['new_neural_forward_or_training_for_checks']==0
          and necessary['new_Gold_values_or_old_scores']==0,'Necessary159_metadata_binding_check_no_new_neural_test')
    check(binding['source_splits']==p['source_splits'] and binding['source_splits_sha256']==digest(p['source_splits'])
          and binding['parent157_protocol_sha256']==sha(E157/'protocol.json'),'Exact157_split_binding_audit_chain')
    prep_path=E/'preparation_engineering_repairs.json';prep_repair=read(prep_path) if prep_path.exists() else None
    if prep_repair is not None:
        check(prep_repair['resolved'] and prep_repair['phase']=='BEFORE_PROTOCOL_SEAL_AND_ANY_TRAINING'
              and prep_repair['new_optimization_stages']==prep_repair['neural_forward']==prep_repair['real_initial_loads_before_error']==prep_repair['target_label_values']==0
              and prep_repair['fee_CNY']=='0' and prep_path.stat().st_mtime_ns<(E/'protocol.json').stat().st_mtime_ns,
              'Preprotocol_preparation_error_resolved_without_training_or_initial_load_cost')
    # Validate the unchanged real source lambda entry by its frozen AST, without running a model.
    src=(E/'models159.py').read_text('utf-8');tree=ast.parse(src);loss=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='loss')
    lam=[k.value for n in ast.walk(loss) if isinstance(n,ast.Call) for k in n.keywords if k.arg=='lambda_temporal']
    check(len(lam)==1 and ast.get_source_segment(src,lam[0])=="PROFILES[arm]['lambda_temporal']",'Actual_source_loss_preset_lambda_dynamic_no_extra_forward')
    failures=lines(E/'training/errors.jsonl');partial=sum(r.get('updates_in_partial_epoch',0) for r in failures);events=lines(E/'physical_generation_events.jsonl')
    physical=sum(r.get('outputs',0) for r in events);records=sum(r.get('neural_model_record_scores',0) for r in events)
    check(physical>=51720 and records>=38790,'Native_physical_generation_record_score_coverage')
    check(any(r.get('derived_view_records')==25860 and r.get('new_neural_forward')==0 for r in events),'Derived_zero_extra_forward_event')
    resource={'at_utc':now(),'experiment':'Exp159','new_valid_optimization_stages':18,'new_final_fitted_models':18,'new_AF_training':0,
              'new_optimizer_updates':updates,'recorded_discarded_partial_updates':partial,'physical_updates_including_recorded_partials':updates+partial,
              'recorded_started_stage_executions':18+len(failures),'recorded_training_errors':failures,'training_elapsed_seconds':models['elapsed_seconds'],
              'completed_epoch_elapsed_seconds':sum(r['epoch_total_seconds'] for r in histories),'training_batch_forwards':updates,
              'validation_batch_forwards':8*len(histories),'native_target_model_batch_forwards':18*sum(math.ceil(p['target_cohorts'][c]['n']/16) for c in COHORTS),
              'new_model_scoring_record_outputs':38790,'new_three_seed_ensemble_outputs':12930,'new_native_ranker_outputs':51720,
              'derived_selection_view_records_not_new_ranker_outputs':25860,'cached_ours_records_not_new_outputs':25860,
              'native_files':96,'derived_files':48,'derived_or_cached_ours_new_forward_or_model_fit':0,'physical_native_generations':physical,
              'physical_model_scoring_records':records,'physical_generation_events':events,'canonical_initial_unique_files':3,'split_seed_initial_pairs':9,
              'preset_initial_reference_rows':18,'new_initial_states':0,'actual_profile_optimizer_lambda50_10_runtime_rng_scaler_verified':not errors,
              'actual18_stage_receipts':stages,'stage_receipt_sha256':hashes,'cap_and_still_improving_rows':caps,'choices':choices,
              'inherited158_fixture_reference':inherited,'new159_fixture_tests':0,'old_fixture_physical_cost_not_new159':True,
              'necessary159_metadata_binding_receipt':necessary,'split_binding_audit_sha256':sha(E/'split_binding_audit.json'),
              'preprotocol_preparation_repair_not_training_failure':prep_repair,
              'preprotocol_preparation_path_errors':int(prep_repair is not None),'preprotocol_preparation_discarded_training_or_prediction_outputs':0,
              'independently_sealed_prediction_runtime_entry_receipt':runtime,'prediction_runtime_entry_seal_sha256':sha(E/'prediction_runtime_entry_sealed.json'),
              'runtime_policy_restoration_new_fit_forward_or_discarded_prediction':0,
              'paper50_10_baseline_budget_above_cached157_40_8_not_equal_training_cost':True,'old_p_155FAIL_and_stronger_refs_preserved':True,
              'new_encoder':0,'new_API':0,'new_downloads':0,'new_Gold':0,'new_independent_tasks':0,'fee_CNY':'0'}
    write_new(E/'resource_audit.json',resource)
    packet.update(execution_audit_status='PASS' if not errors else 'FAIL',stage_execution_accounting={'valid':18,'started':18+len(failures),'updates':updates,'discarded_partials':partial},
                  cap_and_still_improving_rows=caps,all_actual_profile_choice_native_derived_bindings_verified=not errors)
    atomic(E/'main_decision_packet.json',packet)
    compact={k:packet[k] for k in ('experiment','primary','source_denominators','ensemble_hits','main_joint_Holm3','preset_joint_Holm6','stage_execution_accounting','decision_owner')}
    compact.update(status='PASS' if not errors else 'FAIL',errors=errors,native_outputs=51720,derived_not_new_outputs=25860,new_models=18,new_AF_training=0,fee_CNY='0')
    write_new(E/'compact_summary.json',compact)
    names=('comparison.json','main_decision_packet.json','compact_summary.json','metrics.csv','paired_counterexamples.json','Gold_evaluation_receipt.json','resource_audit.json')
    audit={'at_utc':now(),'experiment':'Exp159','status':'PASS' if not errors else 'FAIL','errors':errors,'primary':PRIMARY,
           'all18fits18models9choices3initials96native48derived_fullsource_scopes_verified':not errors,
           'all_actual_profile50_10_loss_lambda_runtime_INITIAL_rng_fit_scaler_bindings_verified':not errors,
           'mainHolm3_presetHolm6_complete_support_rule_and_5000taskbootstrap_retained':not errors,
           'allGold_and_oldscore_joins_follow_native_and_derived_fullseal':not errors,
           'cached157_ours_no_forward_old153155158_and_agenticSF363_p_FAIL_references_preserved':not errors,
           'source_only_no_new_AF_training_or_independent_task_claim':True,'native_derived_and_invalid_physical_consumption_separate':True,
           'protocol_sha256':sha(E/'protocol.json'),'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),
           'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json'),'artifacts':{str(E/n):sha(E/n) for n in names}}
    write_new(E/'final_execution_audit.json',audit);status('EXP159_COMPLETE' if not errors else 'EXP159_FINAL_AUDIT_ERROR_STOP',completed_optimization_stages=18,
             final_models=18,optimizer_updates=updates,new_ranker_outputs=51720,derived_selection_view_records=25860,fee_CNY='0',next='root interprets source-only preset replication')
    if errors:raise RuntimeError('FINAL159_EXECUTION_AUDIT_FAILED:'+','.join(errors))


if __name__=='__main__':run()

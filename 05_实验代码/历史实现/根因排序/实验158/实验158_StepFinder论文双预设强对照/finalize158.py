"""Audit two complete SF paper presets and a validation-only derived alias."""
import ast
import math
from collections import Counter,defaultdict
from common import *
from evaluate158 import verify_seals,scheduled_stages,CORE_KEYS,PRESET_KEYS,EVALUATION_FILES,NATIVE_ARMS,SELECTED_ARM,ALL_BASELINES,cap_metadata


def lines(path):
    return [json.loads(row) for row in Path(path).read_text('utf-8-sig').splitlines() if row.strip()] if Path(path).exists() else []


def loss_configuration_audit(check):
    source = (E/'models158.py').read_text('utf-8-sig');grouped = (E/'data158.py').read_text('utf-8-sig')
    st,gt = ast.parse(source),ast.parse(grouped)
    source_function = next(n for n in st.body if isinstance(n,ast.FunctionDef) and n.name=='loss')
    group_function = next(n for n in gt.body if isinstance(n,ast.FunctionDef) and n.name=='grouped_loss')
    source_lambda = [keyword.value for node in ast.walk(source_function) if isinstance(node,ast.Call)
                     for keyword in node.keywords if keyword.arg=='lambda_temporal']
    check(len(source_lambda)==1 and ast.get_source_segment(source,source_lambda[0])=="PROFILES[arm]['lambda_temporal']",
          'source_loss_dynamic_complete_preset_lambda')
    group_terms = [node for node in ast.walk(group_function) if isinstance(node,ast.BinOp) and isinstance(node.op,ast.Mult)]
    check(any(ast.get_source_segment(grouped,node.left)=="PROFILES[arm]['lambda_temporal']" for node in group_terms),
          'AF_group_loss_dynamic_complete_preset_lambda')
    return {'source_model_loss_sha256':sha(E/'models158.py'),'AF_group_loss_sha256':sha(E/'data158.py'),
            'both_lambda_branches_use_full_frozen_preset':True,'no_new_loss_forward_or_framework_check_by_finalizer':True}


def initial_references(p,check):
    initial = read(E/'initialization_audit.json')
    references = p['initialization_records'];signatures = {};paths = set()
    check(initial['status']=='PASS' and initial['records']==references and len(references)==36 and len(p['initializations'])==18,
          '36_new_final_models_reference18_old_SF_canonical_INITIAL_states')
    check(initial['unique_canonical153_SF_INITIAL_files']==18 and initial['final_training_references']==36
          and initial['canonical_INITIAL_state_and_RNG_digests_verified'] and initial['new_initializations_created']==0
          and initial['trained_parent_weight_loads']==initial['invalid_runtime_asset_loads']==0
          and initial['actual_nonlearned_preset_attributes_checked_by_every_stage_after_state_load']
          and initial['runtime_backend_policy']==EXPECTED_BACKEND,'actual_canonical_SF_reference_provenance_configuration_restoration_receipt')
    for row in references:
        suite,arm,seed,outer = row['suite'],row['arm'],row['seed'],row.get('outer')
        path = Path(row['path']).resolve();paths.add(str(path))
        expected = E153/'training'/suite/'SF_REF'/(str(seed) if suite=='source' else f'{seed}_{outer}')/'initial.pt'
        check(path==expected.resolve() and 'invalid' not in str(path).casefold() and sha(path)==p['initializations'][str(path)],
              'valid_canonical153_SF_INITIAL_only_not_trained_or_invalid_weight:'+str((suite,arm,seed,outer)))
        check(row['parent_arm']=='SF_REF' and row['valid_153_INITIAL_only'] and row['trained_parent_weight_loads']==row['invalid_runtime_asset_loads']==0
              and row['canonical_seed']==row['initialization_seed'] and row['parameter_count']==277633
              and row['preset_configuration']==PROFILES[arm], 'preset_reference_matches_complete_profile_original_SF_state:'+str((suite,arm,seed,outer)))
        key = suite,seed,outer
        fingerprint = str(path),row['sha256'],row['state_digest'],canonical(row['training_rng_digest'])
        if key in signatures:
            check(signatures[key]==fingerprint,'two_paper_presets_share_exact_learned_INITIAL_and_training_rng:'+str(key))
        signatures[key] = fingerprint
    check(len(paths)==len(signatures)==18,'exact3source15AF_unique_canonical_SF_INITIAL_references')
    return {'old_canonical_SF_INITIAL_files':18,'new_initializations_or_new_primary_models':0,'new_final_model_reference_rows':36,
            'two_presets_share_learned_initial_weights_rng_configuration_only_differs':True,
            'no_extra_weight_deserialization_or_model_forward_by_evaluation_finalizer':True,'metadata':initial}


def original_schedule_audit(p,check):
    old = read(E153/'protocol.json');original_AF = {(r['seed'],r['outer']):r for r in old['af_schedule'] if r['arm']=='SF_REF'}
    for row in p['source_schedule']:
        check(row['fit_ids']==old['source_ids']['train'] and row['validation_ids']==old['source_ids']['validation'],
              'source_original492train122val_not157_split:'+row['arm']+'/'+str(row['seed']))
    fields = ('selection_fit_ids','validation_ids','refit_ids','held_ids','inner_fit_groups','validation_groups','refit_groups','held_groups',
              'validation_fold','initialization_seed','inference_batches_sha256')
    for row in p['af_schedule']:
        previous = original_AF[row['seed'],row['outer']]
        check(all(row[field]==previous[field] for field in fields),'exact_original153_AF_partition_and_order_not157:'+row['arm']+'/'+str(row['seed'])+'/'+str(row['outer']))
        check(not set(row['refit_groups'])&set(row['held_groups']) and not set(row['inner_fit_groups'])&set(row['validation_groups'])
              and set(row['inner_fit_groups'])|set(row['validation_groups'])==set(row['refit_groups']),
              'original_complete_group_nested_fit_val_held_isolation')
    return {'source_fit_ids_sha256':digest(old['source_ids']['train']),'source_validation_ids_sha256':digest(old['source_ids']['validation']),
            'all30_AF_pairs_original153_lists_order_and_batches':True,'new157_partitions_not_used':True}


def run():
    p,models,seals,choices = verify_seals();errors = []
    def check(ok,name):
        if not ok:errors.append(name)
    comparison,packet = read(E/'comparison.json'),read(E/'main_decision_packet.json')
    evaluation,joined,Gold = read(E/'evaluation_code_seal.json'),read(E/'label_join_started.json'),read(E/'Gold_evaluation_receipt.json')
    check(evaluation['sources']=={str(E/n):sha(E/n) for n in EVALUATION_FILES},'frozen_evaluation_three_sources')
    check(comparison['primary']==packet['primary']==PRIMARY and comparison['underlying_locked_primary']==packet['underlying_locked_primary']=='AB_GLOBAL',
          'locked153_original_main_identity_not_new_ours')
    check(comparison['protocol_sha256']==joined['protocol_sha256']==sha(E/'protocol.json')
          and comparison['model_seal_sha256']==joined['model_seal_sha256']==sha(E/'training/all_models_sealed.json')
          and comparison['choices_seal_sha256']==joined['choices_seal_sha256']==sha(E/'validation_selection_sealed.json')
          and comparison['prediction_seal_sha256']==joined['prediction_seal_sha256']==sha(E/'results/all_predictions_sealed.json'),
          'protocol_models_choices_native_derived_evaluator_chain')
    check(comparison['evaluation_code_seal_sha256']==joined['evaluation_code_seal_sha256']==sha(E/'evaluation_code_seal.json')
          and Gold['comparison_sha256']==sha(E/'comparison.json'),'evaluation_Gold_comparison_chain')
    check((E/'results/all_predictions_sealed.json').stat().st_mtime_ns<=(E/'evaluation_code_seal.json').stat().st_mtime_ns
          <=(E/'label_join_started.json').stat().st_mtime_ns<=(E/'comparison.json').stat().st_mtime_ns,
          'all_native_and_derived_seals_precede_this_evaluator_target_or_oldscore_parse')
    for field,keys,size in [('main_joint_Holm3',CORE_KEYS,3),('preset_joint_Holm4',PRESET_KEYS,4)]:
        check(set(comparison[field])==set(keys) and set(evaluation[field])==set(keys),'exact_separate_'+field)
        for key,row in comparison[field].items():
            check(row['family_tests']==size and row['statistically_supported_lead']==
                  (row['difference']>0 and row['holm_adjusted_p']<.05 and row['familywise_difference_interval'][0]>0),
                  'unchanged_complete_supported_lead_rule:'+key)
            if key.startswith('AF716_'):
                check((row['n_records'],row['n_independent_task_groups'],row['duplicate_records_above_group_count'])==(731,716,15),
                      'AF716_exact_group_mean_unit:'+key)
    check((len(comparison['native_preset_per_task_outcomes']),len(comparison['derived_selection_per_task_outcomes']),
           len(comparison['cached153_GLOBAL_per_task_outcomes']))==(23088,11544,11544),'native_derived_cached_records_separate_no34632_new_native_claim')
    for scope in COHORTS:
        table = comparison['source_cohorts'][scope]['new_preset_and_derived_condition_table']
        expected = set(ALL_BASELINES)|{a+'/seed_'+str(s) for a in ALL_BASELINES for s in SOURCE_SEEDS}
        check(set(table)==expected and all(v['n']==p['target_cohorts'][scope]['n'] for v in table.values()),
              'all_source3baseline3seeds_ensemble_original_full_denominator:'+scope)
    AF_expected = set(ALL_BASELINES)|{a+'/seed_'+str(s) for a in ALL_BASELINES for s in AF_SEEDS}
    check((comparison['AF']['records'],comparison['AF']['groups'],len(comparison['AF']['fixed120_sample_ids']))==(731,716,120)
          and set(comparison['AF']['new_presets_and_derived_all731_record_and716_group'])
          ==set(comparison['AF']['new_presets_and_derived_fixed120'])==AF_expected,'AF731_716_120_all_presets_and_selected_seeds_ensembles')
    check(comparison['validation_selected_preset_not_best_target_preset'] and comparison['native_and_derived_scopes_not_pooled']
          and comparison['cached_parent_original_references']['old155_5pp_practical_FAIL_not_redefined']
          and comparison['cached_parent_original_references']['no_stronger_old_SF_omitted_including_agentic157_363'],
          'validation_only_choice_oldp_5ppfail_and_strongerSF363_preserved')
    for path,h in {**Gold['label_files_sha256'],**Gold['historical_reference_files_sha256']}.items():
        check(sha(path)==h,'original_label_or_parent_reference_bytes_unchanged:'+path)
    loss = loss_configuration_audit(check);initial = initial_references(p,check);schedule = original_schedule_audit(p,check)
    stages,stage_hashes,histories,final_paths,cap_rows = [],{},[],set(),[]
    selected,scalers = {},defaultdict(set);validation_batches = 0
    for row,stage,fit_ids,val_ids,path in scheduled_stages(p):
        rec = read(path);stage_hashes[str(path)] = sha(path);key = row['suite'],row['arm'],row['seed'],row.get('outer')
        check(rec['completed_epochs']==len(rec['history']) and 1<=rec['completed_epochs']<=50
              and [r['epoch'] for r in rec['history']]==list(range(1,rec['completed_epochs']+1)), 'complete50epoch_stage_history:'+str(path))
        batches = math.ceil(len(fit_ids)/16) if row['suite']=='source' else math.ceil(len(row['inner_fit_groups'] if stage=='selection' else row['refit_groups'])/16)
        check(rec['updates']==sum(r['updates'] for r in rec['history']) and all(r['updates']==batches for r in rec['history']),
              'paper_batch16_original_tasks_or_complete_groups_updates:'+str(path))
        scaler_key = ('source',) if row['suite']=='source' else ('AF',row['seed'],row['outer'],stage)
        scalers[scaler_key].add(rec['scaler_mean_sha256'])
        if val_ids:
            best = max(rec['history'],key=lambda r:(r['validation']['Top1'],r['validation']['MRR'],-r['epoch']))
            check(best['epoch']==rec['selected_epoch'] and all(r['validation']['group_equal']==(row['suite']=='AF') for r in rec['history']),
                  'validation_only_epoch_Top1_MRR_earliest_original_unit:'+str(path))
            selected[key] = rec['selected_epoch'];validation_batches += math.ceil(len(val_ids)/16)*len(rec['history'])
        else:
            check(rec['selected_epoch']==selected[key]==rec['completed_epochs'],'fresh_refit_exact_selected_preset_epoch:'+str(path))
        cap = cap_metadata(rec);cap_rows.append(cap)
        check(rec['hit_epoch_cap']==cap['reached50_epoch_cap'] and rec['selected_epoch_at_cap']==cap['selected_epoch_is50']
              and rec['last_epoch_validation_improved']==cap['final_epoch_improved_validation_best'],'actual_epoch_cap_and_last_improvement_metadata:'+str(path))
        if stage in ('source_fit','refit'):final_paths.add(str(Path(rec['checkpoint']).resolve()))
        stages.append({k:rec[k] for k in ('suite','arm','seed','outer','stage','selected_epoch','completed_epochs','updates','checkpoint','checkpoint_sha256',
                                        'scaler_fit_ids_sha256','scaler_mean_sha256','initialization_path','initialization_sha256','initialization_state_digest',
                                        'initialization_training_rng_digest','actual_canonical_training_RNG_restored','actual_model_configuration',
                                        'actual_preset_configuration','actual_lr','actual_weight_decay','lambda_temporal','max_epochs','patience',
                                        'runtime_backend_policy','elapsed_seconds')})
        histories.extend(rec['history'])
    updates = sum(row['updates'] for row in stages);stage_counts = Counter(row['stage'] for row in stages)
    check(len(stages)==66 and dict(stage_counts)=={'source_fit':6,'selection':30,'refit':30}
          and updates==models['optimizer_updates'] and len(models['models'])==36
          and final_paths=={str(Path(row['checkpoint']).resolve()) for row in models['models']},'actual66stage36finalmodels_updates_accounting')
    check(len(scalers)==31 and all(len(v)==1 for v in scalers.values()),'matched_original_fit_IDs_equal_scaler_digest_across_both_presets')
    fixture = read(E/'fixtures/preset_test_receipt.json')
    check(fixture['status']=='PASS' and fixture['protocol_sha256']==sha(E/'protocol.json') and fixture['approved_plan_sha256']==PLAN_SHA,
          'necessary_small_preset_loss_and_validation_choice_fixture_pass')
    check(all(sha(E/n)==h for n,h in fixture['source_sha256'].items()),'necessary_preset_fixture_frozen_source_hashes')
    fixture_cost = fixture.get('physical_cumulative_compute_counters',fixture.get('compute_counters',{}))
    check(all(fixture_cost.get(k)==0 for k in ('neural_forwards','GPU_forwards','backward_calls','optimizer_updates',
                                              'real_weight_loads','real_Gold_values','old_score_values')),
          'fixture_only_synthetic_CPU_configuration_loss_and_selector_checks')
    failure_events = lines(E/'training/errors.jsonl');partial = sum(row.get('updates_in_partial_epoch',0) for row in failure_events)
    generation = lines(E/'physical_generation_events.jsonl')
    physical_native = sum(row.get('outputs',0) for row in generation)
    physical_neural_records = sum(row.get('neural_model_record_scores',0) for row in generation)
    source_native,source_ensemble = 6*2155,2*2155;AF_native,AF_ensemble = sum(len(r['held_ids']) for r in p['af_schedule']),2*731
    check((source_native+source_ensemble,AF_native+AF_ensemble,source_native+AF_native,source_ensemble+AF_ensemble)==(17240,5848,17316,5772),
          'exact_native_record_and_three_seed_ensemble_output_accounting')
    check(physical_native>=23088 and physical_neural_records>=17316,'recorded_physical_native_rank_generation_and_model_record_score_coverage')
    forward_batches = 6*sum(math.ceil(p['target_cohorts'][c]['n']/16) for c in COHORTS)+sum(math.ceil(len(r['held_ids'])/16) for r in p['af_schedule'])
    per_profile = {suite:{arm:{str(seed):{'stages':[r for r in stages if (r['suite'],r['arm'],r['seed'])==(suite,arm,seed)],
                                         'updates':sum(r['updates'] for r in stages if (r['suite'],r['arm'],r['seed'])==(suite,arm,seed)),
                                         'AF_folds_descriptive_not_independent_seeds':suite=='AF'}
                              for seed in (SOURCE_SEEDS if suite=='source' else AF_SEEDS)} for arm in NATIVE_ARMS}
                   for suite in ('source','AF')}
    resource = {'at_utc':now(),'experiment':'Exp158','new_valid_optimization_stages':66,'new_stage_counts':dict(stage_counts),'new_final_fitted_models':36,
                'unique_parent_SF_canonical_INITIAL_references_not_new_models':18,'new_initial_states_or_ours_models':0,
                'new_optimizer_updates_completed_schedule':updates,'recorded_discarded_partial_optimizer_updates':partial,
                'physical_optimizer_updates_including_recorded_discarded_partials':updates+partial,
                'recorded_started_stage_executions':66+len(failure_events),'recorded_training_failures':failure_events,
                'new_completed_training_epochs':len(histories),'new_training_elapsed_seconds':models['elapsed_seconds'],
                'new_stage_elapsed_seconds':sum(r['elapsed_seconds'] for r in stages),
                'all_completed_epoch_elapsed_seconds_including_saved_resume_history':sum(r['epoch_total_seconds'] for r in histories),
                'new_training_batch_forwards_completed_schedule':updates,'new_validation_batch_forwards':validation_batches,
                'new_native_target_model_batch_forwards':forward_batches,'new_native_model_scoring_record_outputs':17316,
                'new_native_three_seed_ensemble_outputs':5772,'new_native_ranker_outputs':23088,'source_native_new_outputs':17240,'AF_native_new_outputs':5848,
                'AF_seed_joined_JSON_copy_entries_not_new_outputs':AF_native,
                'derived_validation_selected_view_records_not_new_ranker_outputs':11544,'derived_source_view_records':8620,'derived_AF_view_records':2924,
                'new_model_forward_or_fit_for_derived_selection_view':0,'native_prediction_JSON_files':70,'derived_prediction_JSON_files':20,
                'cached153_ours_records_not_new_outputs':11544,'new_primary_ours_training_or_forward':0,
                'paper_baseline50_10_vs_locked_ours40_8_training_cost_not_equalized':True,'complete_frozen_profiles':PROFILES,
                'all66_actual_model_optimizer_lambda_runtime_INITIAL_and_scaler_bindings_verified':not errors,
                'epoch_cap_and_still_improving_metadata':cap_rows,'epoch_cap_count_sourcefit_or_selection':sum(r['reached50_epoch_cap'] for r in cap_rows if r['stage']!='refit'),
                'still_improving_at_cap_sourcefit_or_selection':sum(bool(r['validation_still_improving_when_cap_reached']) for r in cap_rows if r['stage']!='refit'),
                'validation_only_preset_choice_decisions':choices,'validation_selection_seal_sha256':sha(E/'validation_selection_sealed.json'),
                'initial_reference_audit':initial,'original_source_AF_schedule_audit':schedule,'both_loss_lambda_configuration_audit':loss,
                'necessary_small_preset_fixture_receipt':fixture,'fixture_physical_cumulative_counters':fixture_cost,
                'new66_stage_receipts':stages,'stage_receipt_sha256':stage_hashes,'per_suite_profile_seed_epochs_and_updates':per_profile,
                'physical_native_and_derived_generation_events_separately_preserved':generation,
                'recorded_physical_native_output_generations':physical_native,'recorded_physical_model_scoring_record_outputs':physical_neural_records,
                'derived_views_declared_zero_neural_forward_by_separate_manifest':seals['derived'],
                'old153155156157_fits_predictions_failures_and_5ppFAIL_not_charged_or_rewritten':True,
                'new_encoder':0,'new_API':0,'new_downloads':0,'new_Gold':0,'new_independent_tasks':0,'fee_CNY':'0',
                'scope':'Two complete paper SF presets plus validation-only reuse view; immutable153 main and old references stay cached'}
    write_new(E/'resource_audit.json',resource)
    packet.update(execution_audit_status='PASS' if not errors else 'FAIL',all66_actual_preset_RUNTIME_INITIAL_scaler_and_validation_choice_bindings_verified=not errors,
                  epoch_cap_and_still_improving_metadata=cap_rows,per_suite_profile_seed_selected_epochs_updates=per_profile,
                  new_stage_execution_accounting={'valid_completed':66,'recorded_started':66+len(failure_events),'new_errors':len(failure_events),
                                                  'new_optimizer_updates':updates,'recorded_discarded_partial_updates':partial},
                  native_vs_derived_accounting={'new_native':23088,'derived_not_new_neural_output':11544,'cached_ours_not_new':11544,
                                                'native_files':70,'derived_files':20,'new_ours_or_derived_model_forward':0})
    atomic(E/'main_decision_packet.json',packet)
    keys = ('experiment','primary','underlying_locked_primary','scope','source_denominators','source_locked153_ensemble_hits','source_new_baseline_ensemble_hits',
            'AF_locked153_fixed120_hits','AF_new_baseline_fixed120_hits','AF_locked153_716group_metrics','AF_new_baseline_716group_metrics',
            'main_joint_Holm3','preset_joint_Holm4','all_stronger_old_SF_including_agentic363_preserved','new_stage_execution_accounting','native_vs_derived_accounting','decision_owner')
    compact = {k:packet[k] for k in keys}
    compact.update(at_utc=now(),execution_audit_status='PASS' if not errors else 'FAIL',errors=errors,new_valid_stages=66,new_final_fitted_models=36,
                   unique_old_SF_INITIAL_references=18,new_native_ranker_outputs=23088,derived_selection_views_not_new_outputs=11544,
                   sourcefit_selection_epoch_cap_count=resource['epoch_cap_count_sourcefit_or_selection'],
                   validation_still_improving_at_cap_count=resource['still_improving_at_cap_sourcefit_or_selection'],fee_CNY='0')
    write_new(E/'compact_summary.json',compact)
    artifact_names = ('comparison.json','main_decision_packet.json','compact_summary.json','resource_audit.json','paired_counterexamples.json','Gold_evaluation_receipt.json','metrics.csv')
    audit = {'at_utc':now(),'experiment':'Exp158','primary':PRIMARY,'status':'PASS' if not errors else 'FAIL','errors':errors,
             'all66_actual_stages36models18INITIALreferences_profiles50_10_losslambda_runtime_verified':not errors,
             'all18_validation_only_preset_choices_sealed_before_native_predictions_or_targetscore':not errors,
             'all23088_native_plus11544derived_views70native20derivedfiles_verified_without_count_inflation':not errors,
             'all_source4_AF731record716group_fixed120_allpresets_selected_and_locked_ours_seeds_ensembles_retained':not errors,
             'mainHolm3_and_presetHolm4_separate_complete_support_rule_unchanged':not errors,
             'old_primary_original_p_5ppFAIL_and_stronger_SF363_references_preserved':not errors,
             'paper_baseline_budget_intentionally_higher_than_cached_ours_no_equal_cost_claim':True,
             'no_new_ours_or_selected_alias_training_or_forward':not errors,
             'no_best_target_preset_choice_no_new_encoder_API_download_Gold_independent_tasks':not errors,
             'epoch_cap_and_last_validation_improvement_reported_without_extension_or_new_preset':not errors,
             'no_AA_rank_fabrication_no_authorTEST600_or_unapproved_reserve':True,
             'protocol_sha256':sha(E/'protocol.json'),'model_seal_sha256':sha(E/'training/all_models_sealed.json'),
             'choices_seal_sha256':sha(E/'validation_selection_sealed.json'),'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),
             'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json'),'artifacts':{str(E/name):sha(E/name) for name in artifact_names}}
    write_new(E/'final_execution_audit.json',audit)
    status('EXP158_COMPLETE' if not errors else 'EXP158_FINAL_AUDIT_ERROR_STOP',completed_optimization_stages=66,final_models=36,
           optimizer_updates=updates,new_ranker_outputs=23088,derived_selection_view_records=11544,fee_CNY='0',
           next='root interprets fixed-main versus complete stronger paper SF presets; no new profile/model substitution')
    print(canonical({'Exp158':'finalized','status':audit['status'],'new_stages':66,'new_models':36,'native_outputs':23088,'derived_views':11544}),flush=True)
    if errors:raise RuntimeError('FINAL158_EXECUTION_AUDIT_FAILED:'+','.join(errors))


if __name__=='__main__':run()

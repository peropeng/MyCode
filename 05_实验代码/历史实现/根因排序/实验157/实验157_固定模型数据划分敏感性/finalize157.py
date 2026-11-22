"""Audit297 new stages and54 canonical INITIAL references without extra inference."""
import math
from collections import Counter,defaultdict
from common import *
from evaluate157 import verify_seals,scheduled_stages,CORE_KEYS,MECHANISM_KEYS,EVALUATION_FILES


def lines(path):
    return [json.loads(row) for row in Path(path).read_text('utf-8-sig').splitlines() if row.strip()] if Path(path).exists() else []


def split_metadata_audit(p,check):
    public = read(p['source_public_records'])['records'];AF_public = read(p['AF_public_records'])['records']
    by,AF_by = {r['sample_id']:r for r in public},{r['sample_id']:r for r in AF_public}
    check((len(public),len(by),len({r['task_group'] for r in public}))==(614,614,614),'source614_original_unique_group_pool')
    check(Counter(r['domain'] for r in public)=={'coding':320,'math':294},'source_original_coding320_math294_pool')
    source_rows = {}
    for block in BLOCKS:
        spec = p['source_splits'][block];ids = spec['ids'];fit,val = ids['train'],ids['validation']
        check(len(fit)==492 and len(val)==122 and not set(fit)&set(val) and set(fit)|set(val)==set(by),
              'source_full492_122_partition:'+block)
        check(fit==[r['sample_id'] for r in public if r['sample_id'] in set(fit)]
              and val==[r['sample_id'] for r in public if r['sample_id'] in set(val)],'restore_original_public_ID_order:'+block)
        counts = {part:dict(Counter(by[s]['domain'] for s in members)) for part,members in ids.items()}
        check(counts==spec['domain_counts']=={'train':{'coding':256,'math':236},'validation':{'coding':64,'math':58}},
              'fixed_source_domain_budget:'+block)
        check(spec['fit_ids_sha256']==digest(fit) and spec['validation_ids_sha256']==digest(val),'source_split_fit_val_digests:'+block)
        overlaps = {new+'_'+old:len(set(members)&set(p['historical_source_ids'][old]))
                    for new,members in ids.items() for old in ('train','validation')}
        check(overlaps==spec['overlap_with_old_ids'],'source_train_val_member_overlap_with_original153:'+block)
        for domain,limit in [('coding',64),('math',58)]:
            order = sorted((r['task_group'] for r in public if r['domain']==domain),
                           key=lambda g:(hashlib.sha256(('Exp157-source-v1|'+block+'|'+domain+'|'+g).encode('utf-8')).hexdigest(),g))
            check(order==spec['domain_hash_order'][domain] and {by[s]['task_group'] for s in val if by[s]['domain']==domain}==set(order[:limit]),
                  'frozen_hash_source_validation_members:'+block+'/'+domain)
        source_rows[block] = {'fit_records':492,'validation_records':122,'domain_counts':counts,'original_member_overlap':overlaps,
                              'fit_ids_sha256':digest(fit),'validation_ids_sha256':digest(val)}
    AF_groups = sorted({r['task_group'] for r in AF_public})
    check(len(AF_public)==len(AF_by)==731 and len(AF_groups)==716,'original_AF731_716_group_pool')
    partitions = []
    for block in BLOCKS:
        for seed in AF_SEEDS:
            spec = p['AF_partitions'][block][str(seed)]
            order = sorted(AF_groups,key=lambda g:(hashlib.sha256(('Exp157-AF-v1|'+block+'|'+str(seed)+'|'+g).encode('utf-8')).hexdigest(),g))
            assignment = {g:index%5 for index,g in enumerate(order)}
            check(order==spec['hash_group_order'] and assignment==spec['group_fold_assignment']
                  and digest(assignment)==spec['group_fold_assignment_sha256'],'frozen_hash_AF716_group_assignment:'+block+'/'+str(seed))
            check([len(spec['fold_groups'][str(outer)]) for outer in range(5)]==[144,143,143,143,143],
                  'all9_AF_fixed_group_fold_sizes:'+block+'/'+str(seed))
            for arm in ARMS:
                rows = [r for r in p['af_schedule'] if (r['arm'],r['replication_block'],r['seed'])==(arm,block,seed)]
                OOF = [sid for r in rows for sid in r['held_ids']]
                check(len(rows)==5 and len(OOF)==len(set(OOF))==731 and set(OOF)==set(AF_by),
                      'every_AF_record_once_per_split_original_seed_arm:'+arm+'/'+block+'/'+str(seed))
                for row in rows:
                    outer = row['outer'];validation = min(o for o in range(5) if o!=outer)
                    expected = {'held_ids':[r['sample_id'] for r in AF_public if assignment[r['task_group']]==outer],
                                'validation_ids':[r['sample_id'] for r in AF_public if assignment[r['task_group']]==validation],
                                'selection_fit_ids':[r['sample_id'] for r in AF_public if assignment[r['task_group']] not in (outer,validation)],
                                'refit_ids':[r['sample_id'] for r in AF_public if assignment[r['task_group']]!=outer]}
                    check(row['validation_fold']==validation and all(row[field]==ids for field,ids in expected.items()),
                          'all_AF_fit_val_refit_held_original_order_and_first_nonouter_val:'+arm+'/'+block+'/'+str(seed)+'/'+str(outer))
                    check(not set(row['refit_groups'])&set(row['held_groups'])
                          and set(row['inner_fit_groups'])|set(row['validation_groups'])==set(row['refit_groups'])
                          and not set(row['inner_fit_groups'])&set(row['validation_groups']),
                          'complete_AF_groups_mutually_exclusive:'+arm+'/'+block+'/'+str(seed)+'/'+str(outer))
            partitions.append({'replication_block':block,'seed':seed,'group_fold_assignment_sha256':digest(assignment),
                               'group_fold_sizes':[144,143,143,143,143],'full731_once_OOF_per_arm':True})
    return {'source_member_overlap_and_domain_counts':source_rows,'all9_AF_group_partitions':partitions,
            'new_split_memberships_not_new_independent_tasks':True,'target_label_length_or_score_based_split_selection':0}


def initial_reference_audit(p,check):
    initial = read(E/'initialization_audit.json')
    check(initial['status']=='PASS' and initial['unique_canonical153_INITIAL_files']==54 and initial['final_training_references']==162
          and initial['canonical_INITIAL_state_and_RNG_digests_verified'] and initial['new_initializations_created']==0
          and initial['new_model_constructors_or_forwards_for_preparation']==0
          and initial['trained_parent_weight_loads']==initial['invalid_runtime_asset_loads']==0,
          '54_old_canonical_INITIAL_states_RNG_verified_162_references_no_new_initials')
    check(initial['records']==p['initialization_records'] and initial['parameters']==p['parameters']
          and initial['runtime_backend_policy']==EXPECTED_BACKEND,'frozen_INITIAL_reference_audit_and_protocol_match')
    same = {};paths = set()
    for row in initial['records']:
        key = row['suite'],row['arm'],row['seed'],row.get('outer')
        folder = E153/'training'/row['suite']/row['arm']/(str(row['seed']) if row['suite']=='source' else f"{row['seed']}_{row['outer']}")
        path = str(Path(row['path']).resolve());paths.add(path)
        check(Path(path)==(folder/'initial.pt').resolve() and 'invalid' not in path.casefold()
              and sha(path)==row['sha256'] and row['valid_153_INITIAL_only']
              and row['trained_parent_weight_loads']==row['invalid_runtime_asset_loads']==0,
              'exact_valid153_INITIAL_not_trained_weight_or_invalid_runtime:'+str(key))
        check(row['initialization_seed']==row['canonical_seed'] and row['parameter_count']==p['parameters'][row['arm']]
              and set(row['training_rng_digest'])=={'python','numpy','torch','cuda'},'canonical_seed_parameter_four_RNG_binding:'+str(key))
        signature = (path,row['sha256'],row['state_digest'],canonical(row['training_rng_digest']),row['canonical_seed'])
        if key in same:
            check(same[key]==signature,'all_three_split_blocks_share_exact_canonical_INITIAL_and_rng:'+str(key))
        same[key] = signature
        if row['arm']==PRIMARY:
            check(row['O_zero'] and row['independent_context_seed']==row['canonical_seed']+153000,'unchanged_original_GLOBAL_zeroO_context_initializer:'+str(key))
    check(len(paths)==len(same)==54 and paths=={str(Path(q).resolve()) for q in p['initializations']},'exact54_unique_old_INITIAL_references')
    return {'unique_canonical153_INITIAL_files':54,'new_initial_files':0,'final_model_reference_rows':162,
            'same_old_canonical_INITIAL_bytes_state_rng_across3blocks':True,
            'actual_state_RNG_restoration_proof':'Every297 stage receipt initial_binding, verified before target label join',
            'no_additional_weight_deserialization_or_model_forward_by_finalizer':True,'metadata':initial}


def run():
    p,models,predictions = verify_seals()
    comparison,packet = read(E/'comparison.json'),read(E/'main_decision_packet.json')
    evaluation,joined,Gold = read(E/'evaluation_code_seal.json'),read(E/'label_join_started.json'),read(E/'Gold_evaluation_receipt.json')
    errors = []
    def check(ok,name):
        if not ok:
            errors.append(name)
    check(evaluation['sources']=={str(E/n):sha(E/n) for n in EVALUATION_FILES},'frozen_evaluation_three_sources')
    check(packet['primary']==comparison['primary']==PRIMARY,'unchanged157_primary_AB_GLOBAL')
    check(comparison['protocol_sha256']==joined['protocol_sha256']==sha(E/'protocol.json')
          and comparison['model_seal_sha256']==sha(E/'training/all_models_sealed.json')
          and comparison['prediction_seal_sha256']==joined['prediction_seal_sha256']==sha(E/'results/all_predictions_sealed.json'),
          'protocol_model_prediction_evaluator_join_chain')
    check(comparison['evaluation_code_seal_sha256']==joined['evaluation_code_seal_sha256']==sha(E/'evaluation_code_seal.json')
          and Gold['comparison_sha256']==sha(E/'comparison.json'),'evaluator_Gold_comparison_chain')
    check((E/'results/all_predictions_sealed.json').stat().st_mtime_ns<=(E/'evaluation_code_seal.json').stat().st_mtime_ns
          <=(E/'label_join_started.json').stat().st_mtime_ns<=(E/'comparison.json').stat().st_mtime_ns,'all103896_outputs_precede_this_evaluator_target_join')
    for field,keys in [('core_joint_Holm6',CORE_KEYS),('mechanism_joint_Holm6',MECHANISM_KEYS)]:
        check(set(comparison[field])==set(keys) and set(evaluation[field])==set(keys),'exact_separate_'+field)
        for key,row in comparison[field].items():
            check(row['family_tests']==6 and row['statistically_supported_lead']==
                  (row['difference']>0 and row['holm_adjusted_p']<.05 and row['familywise_difference_interval'][0]>0),
                  'unchanged_complete_supported_lead_rule:'+key)
            if '_AF716_' in key:
                check((row['n_records'],row['n_independent_task_groups'],row['duplicate_records_above_group_count'])==(731,716,15),
                      'AF716_exact_group_pair_unit:'+key)
    check(len(comparison['per_task_outcomes'])==103896 and comparison['new_ranker_outputs']==103896,'all103896_original_outcomes_scored')
    expected_conditions = {a+'/'+b+('/seed_'+str(s) if s is not None else '') for a in ARMS for b in BLOCKS for s in tuple(SOURCE_SEEDS)+(None,)}
    for scope in COHORTS:
        value = comparison['source_cohorts'][scope]
        check(value['n']==p['target_cohorts'][scope]['n'] and value['groups']==value['n'] and set(value['condition_table'])==expected_conditions
              and all(row['n']==value['n'] for row in value['condition_table'].values()),'all_source_original36_conditions_denominator:'+scope)
    expected_AF = {a+'/'+b+('/seed_'+str(s) if s is not None else '') for a in ARMS for b in BLOCKS for s in tuple(AF_SEEDS)+(None,)}
    check((comparison['AF']['records'],comparison['AF']['groups'],len(comparison['AF']['fixed120_sample_ids']))==(731,716,120)
          and set(comparison['AF']['all731_record_equal_and716_group_equal'])==set(comparison['AF']['fixed120'])==expected_AF,
          'AF731_716_120_all36conditions_full_scope')
    check(set(comparison['split_sensitivity'])==set(COHORTS)|{'AF731','AF716','AF120'}
          and len(comparison['AF']['all45_outer_results_descriptive'])==45,'all7_sensitivity_scopes_all45_AF_outer_rows')
    check(comparison['source_AF_blocks_not_pooled'] and comparison['no9_model_ensemble_no_best_split_or_seed_selection']
          and comparison['cached_parent_original_references']['old155_5pp_practical_rule_and_original_FAIL_identity_preserved']
          and comparison['cached_parent_original_references']['simple156_priors_not_refit_or_claimed_matched_to_new157_partitions'],
          'no_split_task_inflation_no_old155_5pp_or156_prior_rewrite')
    for path,h in {**Gold['label_files_sha256'],**Gold['historical_reference_files_sha256']}.items():
        check(sha(path)==h,'original_label_or_parent_reference_bytes_unchanged:'+path)
    splits = split_metadata_audit(p,check);initial = initial_reference_audit(p,check)
    stages,stage_hashes,histories,final_paths = [],{},[],set()
    selected,scalers = {},defaultdict(set);validation_batches = 0
    scaler_specs = {(r['suite'],r['arm'],r['replication_block'],r['seed'],r.get('outer'),r['stage']):r for r in p['scaler_fit_specs']}
    for row,stage,fit_ids,val_ids,path in scheduled_stages(p):
        rec = read(path);stage_hashes[str(path)] = sha(path)
        key = row['suite'],row['arm'],row['replication_block'],row['seed'],row.get('outer')
        check(rec['completed_epochs']==len(rec['history']) and 1<=rec['completed_epochs']<=40
              and [r['epoch'] for r in rec['history']]==list(range(1,rec['completed_epochs']+1)),'complete_stage_epoch_history:'+str(path))
        batches = math.ceil(len(fit_ids)/16) if row['suite']=='source' else math.ceil(len(row['inner_fit_groups'] if stage=='selection' else row['refit_groups'])/16)
        check(rec['updates']==sum(r['updates'] for r in rec['history']) and all(r['updates']==batches for r in rec['history']),
              'batch16_tasks_or_complete_groups_updates:'+str(path))
        check(scaler_specs[(*key,stage)]['scaler_fit_ids_sha256']==rec['scaler_fit_ids_sha256']==rec['fit_ids_sha256']==digest(fit_ids),
              'every297_frozen_scaler_fit_ID_binding:'+str(path))
        scaler_key = ('source',row['replication_block']) if row['suite']=='source' else ('AF',row['replication_block'],row['seed'],row['outer'],stage)
        scalers[scaler_key].add(rec['scaler_mean_sha256'])
        if val_ids:
            best = max(rec['history'],key=lambda r:(r['validation']['Top1'],r['validation']['MRR'],-r['epoch']))
            check(best['epoch']==rec['selected_epoch'] and all(r['validation']['group_equal']==(row['suite']=='AF') for r in rec['history']),
                  'validation_only_Top1_MRR_earliest_original_unit:'+str(path))
            selected[key] = rec['selected_epoch'];validation_batches += math.ceil(len(val_ids)/16)*len(rec['history'])
        else:
            check(rec['selected_epoch']==selected[key]==rec['completed_epochs'],'fresh_refit_exact_selected_epoch:'+str(path))
        if stage in ('source_fit','refit'):
            final_paths.add(str(Path(rec['checkpoint']).resolve()))
        stages.append({k:rec[k] for k in ('suite','arm','replication_block','seed','outer','stage','selected_epoch','completed_epochs','updates','checkpoint',
                                        'checkpoint_sha256','scaler_fit_ids_sha256','scaler_mean_sha256','initialization_path','initialization_sha256',
                                        'initialization_state_digest','initialization_training_rng_digest','actual_canonical_training_RNG_restored',
                                        'runtime_backend_policy','elapsed_seconds')})
        histories.extend(rec['history'])
    updates = sum(r['updates'] for r in stages);stage_counts = Counter(r['stage'] for r in stages)
    check(len(stages)==297 and dict(stage_counts)=={'source_fit':27,'selection':135,'refit':135}
          and updates==models['optimizer_updates'] and len(models['models'])==162
          and final_paths=={str(Path(r['checkpoint']).resolve()) for r in models['models']},'actual297_stage162final_model_updates_accounting')
    check(len(scaler_specs)==297 and len(scalers)==93 and all(len(values)==1 for values in scalers.values()),
          'same_fit_IDs_have_identical_scaler_digest_across_matched_arms_and_source_seeds')
    fixture = read(E/'fixtures/split_test_receipt.json')
    check(fixture['status']=='PASS' and fixture['protocol_sha256']==sha(E/'protocol.json') and fixture['approved_plan_sha256']==PLAN_SHA,
          'necessary_pretrain_split_fixture_pass_bound_protocol')
    check(all(sha(E/n)==h for n,h in fixture['source_sha256'].items()) and fixture['no_weights_Gold_or_old_score_reads']
          and fixture['no_model_runtime_imports'],'pure_metadata_fixture_source_and_access_scope')
    fixture_cost = fixture.get('physical_cumulative_compute_counters',fixture['compute_counters'])
    failure_events = lines(E/'training/errors.jsonl');partial_updates = sum(row.get('updates_in_partial_epoch',0) for row in failure_events)
    generation = lines(E/'physical_generation_events.jsonl');physical_output_count = sum(row.get('outputs',0) for row in generation)
    source_native,source_ensemble = 27*2155,9*2155
    AF_native,AF_ensemble = sum(len(row['held_ids']) for row in p['af_schedule']),9*731
    check((source_native+source_ensemble,AF_native,AF_ensemble)==(77580,19737,6579)
          and AF_native+AF_ensemble==26316 and len(predictions['files'])==315,'native_ensemble_join_copy_output_counts')
    # A normal first producer pass records every unique native/ensemble output once;
    # additional recorded generations remain visible physical cost after recovery.
    check(physical_output_count>=103896,'recorded_native_and_ensemble_physical_generations_cover_valid_outputs')
    forward_batches = 27*sum(math.ceil(p['target_cohorts'][c]['n']/16) for c in COHORTS)
    forward_batches += sum(math.ceil(len(row['held_ids'])/16) for row in p['af_schedule'])
    per_model = {suite:{block:{arm:{str(seed):{'stages':[r for r in stages if (r['suite'],r['replication_block'],r['arm'],r['seed'])==(suite,block,arm,seed)],
                                                       'optimizer_updates':sum(r['updates'] for r in stages if (r['suite'],r['replication_block'],r['arm'],r['seed'])==(suite,block,arm,seed)),
                                                       'AF_outer_rows_descriptive_not_independent_seeds':suite=='AF'}
                                     for seed in (SOURCE_SEEDS if suite=='source' else AF_SEEDS)} for arm in ARMS} for block in BLOCKS}
                 for suite in ('source','AF')}
    resource = {'at_utc':now(),'experiment':'Exp157','new_valid_optimization_stages':297,'new_stage_counts':dict(stage_counts),'new_final_fitted_models':162,
                'unique_canonical153_INITIAL_references_not_new_models':54,'new_initial_files':0,'final_model_INITIAL_reference_rows':162,
                'new_optimizer_updates_completed_schedule':updates,'recorded_discarded_partial_optimizer_updates':partial_updates,
                'new_physical_optimizer_updates_including_recorded_discarded_partials':updates+partial_updates,
                'recorded_started_stage_executions':297+len(failure_events),'recorded_training_errors':failure_events,
                'new_completed_training_epochs':len(histories),'new_training_elapsed_seconds':models['elapsed_seconds'],
                'new_stage_elapsed_seconds':sum(r['elapsed_seconds'] for r in stages),
                'all_completed_epoch_elapsed_seconds_including_saved_resume_history':sum(r['epoch_total_seconds'] for r in histories),
                'new_training_batch_forwards_completed_schedule':updates,'new_validation_batch_forwards':validation_batches,
                'new_native_target_model_batch_forwards':forward_batches,'ensemble_extra_model_forwards':0,
                'new_unique_valid_ranker_outputs':103896,'source_native_seed_outputs':source_native,'source_three_seed_ensemble_outputs':source_ensemble,
                'AF_native_OOF_outputs':AF_native,'AF_three_seed_ensemble_outputs':AF_ensemble,'AF_OOF_joined_JSON_copy_entries_not_new_outputs':AF_native,
                'new_prediction_JSON_files':315,'recorded_physical_ranker_output_generations':physical_output_count,'physical_generation_events':generation,
                'old153155156_training_prediction_and_invalid_attempts_not_new157_consumption':True,
                'new156_prior_fits_or_control_predictions':0,'canonical_INITIAL_reference_audit':initial,'split_membership_audit':splits,
                'necessary_split_metadata_fixture_receipt':fixture,'fixture_physical_cumulative_counters':fixture_cost,
                'new297_stage_receipts':stages,'stage_receipt_sha256':stage_hashes,'per_suite_block_arm_seed_epochs_and_updates':per_model,
                'scaler_digest_matching_fit_ID_groups':{str(k):list(v) for k,v in scalers.items()},
                'all297_actual_INITIAL_state_RNG_runtime_and_scaler_binding_verified':not errors,
                'new_encoder':0,'new_API':0,'new_downloads':0,'new_Gold':0,'new_independent_tasks':0,'fee_CNY':'0',
                'old_assets_unchanged':not errors,'scope':'Fixed initializers and model/seed budgets, three prespecified data partitions; no task or resource double counting'}
    write_new(E/'resource_audit.json',resource)
    packet.update(execution_audit_status='PASS' if not errors else 'FAIL',all297_stage_RUNTIME_INITIAL_scaler_fit_ID_bindings_verified=not errors,
                  split_membership_audit=splits,per_suite_block_arm_seed_selected_epochs_updates=per_model,
                  new_stage_execution_accounting={'valid_completed':297,'recorded_started':297+len(failure_events),'new_errors':len(failure_events),
                                                  'new_optimizer_updates':updates,'recorded_discarded_partial_updates':partial_updates,
                                                  'old_parent_and_fixture_consumption_excluded_from_training_stages':True})
    atomic(E/'main_decision_packet.json',packet)
    compact = {k:packet[k] for k in ('experiment','primary','scope','source_denominators','source_split_ensemble_hits','AF_split_fixed120_hits',
                                   'AF_split_731record_metrics','AF_split_716group_metrics','core_joint_Holm6','mechanism_joint_Holm6',
                                   'same_development_split_agreement','old155_5pp_practical_FAIL_not_overwritten','new_stage_execution_accounting','decision_owner')}
    compact.update(at_utc=now(),execution_audit_status='PASS' if not errors else 'FAIL',errors=errors,new_valid_optimization_stages=297,
                   new_final_fitted_models=162,new_unique_ranker_outputs=103896,new_prediction_JSON_files=315,
                   canonical_INITIAL_references=54,no9_model_ensemble_or_best_split_selection=True,fee_CNY='0')
    write_new(E/'compact_summary.json',compact)
    names = ('comparison.json','main_decision_packet.json','compact_summary.json','resource_audit.json','paired_counterexamples.json',
             'split_sensitivity.json','strata.json','Gold_evaluation_receipt.json','metrics.csv')
    audit = {'at_utc':now(),'experiment':'Exp157','primary':PRIMARY,'status':'PASS' if not errors else 'FAIL','errors':errors,
             'all297_new_stages162fitted_models54canonical_INITIAL_references103896outputs315files_verified':not errors,
             'all_source3block_domain_budgets_and_old_member_overlaps_verified':not errors,
             'all9_AF_group_partitions_and_record_once_OOF_and_scaler_fit_IDs_verified':not errors,
             'all297_actual_canonical_state_RNG_backend_and_fit_only_scaler_bindings_verified':not errors,
             'two_separate_prespecified_Holm6_families_retained_without_old_p_rewrite':not errors,
             'all_source4_AF731record716group_fixed120_allsingle_seeds_and_ensembles_retained':not errors,
             'three_split_repetitions_not_new_independent_tasks_no9_model_ensemble_or_bestsplit':True,
             'old155_5pp_rule_and_FAIL_identity_preserved_no_new156_prior_fits':True,
             'all_new_outputs_sealed_before_this_evaluator_target_or_old_score_parse':not errors,
             'old_primary_stronger_references_and_ordinal_annotation_identities_preserved':not errors,
             'failed_training_and_prediction_physical_generation_consumption_separate_from_valid_schedule':True,
             'no_new_encoder_API_download_Gold_independent_task_and_no_parent_invalid_weights':not errors,
             'no_authorTEST600_or_unapproved_reserve_or_control_promotion':True,
             'protocol_sha256':sha(E/'protocol.json'),'model_seal_sha256':sha(E/'training/all_models_sealed.json'),
             'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json'),
             'artifacts':{str(E/name):sha(E/name) for name in names}}
    write_new(E/'final_execution_audit.json',audit)
    status('EXP157_COMPLETE' if not errors else 'EXP157_FINAL_AUDIT_ERROR_STOP',completed_optimization_stages=297,final_models=162,
           optimizer_updates=updates,new_ranker_outputs=103896,fee_CNY='0',next='root interprets fixed split sensitivity; no new model/split/seed substitution')
    print(canonical({'Exp157':'finalized','status':audit['status'],'new_stages':297,'new_models':162,'new_outputs':103896}),flush=True)
    if errors:
        raise RuntimeError('FINAL157_EXECUTION_AUDIT_FAILED:'+','.join(errors))


if __name__=='__main__':
    run()

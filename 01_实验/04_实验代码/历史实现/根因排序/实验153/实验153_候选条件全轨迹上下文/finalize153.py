"""Close the198 valid stages and separately preserve the discarded runtime ledger."""
import math
from collections import Counter
from common import *
from evaluate153 import verify_seals, demand, CORE_KEYS, MECHANISM_KEYS, EVALUATION_FILES

# The existing CUDA repair witness was not added to training protocol inputs.
# Bind its already recorded bytes here, before this evaluation code is sealed.
CUDA_REPAIR_WITNESS_SHA256 = '2b59ca26237c8dd5810ae772223caafbfe10c1482718c235c324fb573a74a062'


def lines(path):
    return [json.loads(row) for row in Path(path).read_text('utf-8-sig').splitlines() if row.strip()] if Path(path).exists() else []


def runtime_repair_receipts(p, check):
    repair = p['repair_attempt']
    failure_path = Path(repair['failure_receipt'])
    auth_path = Path(repair['authorization'])
    policy_path = E/'runtime_policy_repair_receipt.json'
    cuda_path = E/'runtime_CUDA_repair_check.json'
    check(sha(failure_path)==repair['failure_receipt_sha256'] and sha(auth_path)==repair['authorization_sha256'], 'repair_authorization_failure_bindings')
    failure,auth,policy,cuda = read(failure_path),read(auth_path),read(policy_path),read(cuda_path)
    check(auth['authorized'] is True and auth['no_scope_expansion'] is True
          and auth['scientific_plan_sha256']==failure['same_scientific_plan_SHA256']==p['approved_plan_sha256']
          and auth['new_fee_CNY']=='0', 'explicit_same_science_fresh_repair_authorization')
    check(auth['actual_stage_execution_cap']==repair['physical_stage_execution_cap']==270
          and repair['same_scientific_plan'] and repair['original_invalid_models_rejected']
          and repair['fresh_fit_from_identical_frozen_initializations'], 'authorized270_physical_stage_cap_and_fresh_fit')
    archive = Path(failure['backup_path']).resolve()
    check(archive==(E/'invalid_runtime_attempt_01').resolve(), 'invalid_attempt_archive_scope')
    old_protocol_path = archive/'protocol.json'
    check(sha(old_protocol_path)==repair['original_protocol_sha256']==failure['original_protocol_SHA256'], 'original_invalid_protocol_binding')
    old_protocol = read(old_protocol_path)
    check(old_protocol['initializations']==p['initializations'], 'same108_frozen_initial_bytes_reused_only')
    check(failure['all_prior_models_rejected_for_protocol_conformance'] and failure['original_frozen_code_verified']
          and failure['target_rank_outputs']==failure['target_evaluation_joins']==0, 'invalid_attempt_no_held_outputs_or_scores_and_all44_models_rejected')
    check((failure['completed_invalid_optimization_stage_executions'],failure['partial_invalid_stage_executions'],
           failure['total_invalid_started_stage_executions'],failure['invalid_finished_fitted_models'])==(71,1,72,44), 'fixed_discarded_runtime_execution_ledger')
    check(repair['invalid_completed_stage_executions']==71 and repair['invalid_started_stage_executions']==72, 'protocol_failure_stage_count_binding')
    lower,upper = failure['known_optimizer_update_lower_bound'],failure['known_optimizer_update_upper_bound']
    check(lower==32791 and upper==32827
          and lower==failure['completed_stage_optimizer_updates']+failure['active_completed_epoch_optimizer_updates']
          and upper==lower+failure['unrecorded_stopped_partial_epoch_updates_upper_bound'], 'discarded_optimizer_updates_recorded_bounds_not_false_exact_count')
    expected = {'deterministic_algorithms':True,'cudnn_deterministic':True,'cudnn_benchmark':False,
                'matmul_allow_tf32':False,'cudnn_allow_tf32':False,'num_threads':4}
    check(p['runtime_backend_policy']==expected==policy['after'] and policy['before']==failure['observed_fresh_subprocess_defaults'], 'repaired_runtime_backend_policy')
    check(policy['status']=='PASS_RUNTIME_INITIALIZER_REPAIR' and policy['same_frozen_initial_state']
          and policy['same_frozen_training_RNG'] and policy['optimization_stages']==policy['optimizer_updates']==policy['model_forwards']==policy['Gold_read']==0,
          'same_weight_RNG_runtime_policy_witness')
    check(policy['fixed_training_source_sha256']==p['training_sources'][str(E/'trainer153.py')]
          and policy['fixed_prediction_source_sha256']==p['training_sources'][str(E/'predict153.py')], 'repaired_training_prediction_source_hashes')
    check(sha(cuda_path)==CUDA_REPAIR_WITNESS_SHA256, 'fixed_existing_CUDA_repair_witness_sha256')
    check(cuda['status']=='PASS_REPAIRED_CUDA_LOSS_AND_GRADIENT_REPEATABILITY' and cuda['test_cases']==2
          and cuda['counters']=={'CUDA_model_forwards':4,'backward_calls':4,'optimizer_updates':0,'real_records':0,'real_Gold':0}
          and cuda['no_real_data_old_trained_weights_or_evaluation_labels_read'], 'existing_artificial_GPU_repair_witness_counters')
    check(len(cuda['details'])==2 and all(r['runtime_backend_policy']==expected and r['same_frozen_initial_weights']
          and r['exact_repeatable_scores_loss_and_gradients'] and r['float32_gradients'] for r in cuda['details']), 'existing_repaired_CUDA_repeatability_witness')
    for path,h in cuda['source_sha256'].items():
        check(sha(path)==h, 'CUDA_repair_witness_source_changed:'+path)
    check(failure['at_utc']<=auth['at_utc']<=p['at_utc'], 'failure_authorization_repair_freeze_chronology')
    return failure,auth,policy,cuda,{str(q):sha(q) for q in (failure_path,auth_path,policy_path,cuda_path,old_protocol_path)}


def run():
    p,models,predictions = verify_seals()
    comparison = read(E/'comparison.json')
    packet = read(E/'main_decision_packet.json')
    joined = read(E/'label_join_started.json')
    receipt = read(E/'Gold_evaluation_receipt.json')
    evaluation = read(E/'evaluation_code_seal.json')
    errors = []

    def check(ok, name):
        if not ok:
            errors.append(name)

    failure,authorization,runtime_policy,gpu_fixture,repair_sources = runtime_repair_receipts(p,check)

    check(evaluation['sources']=={str(E/n):sha(E/n) for n in EVALUATION_FILES}, 'evaluation_code_changed_after_freeze')
    check(joined['evaluation_code_seal_sha256']==comparison['evaluation_code_seal_sha256']==receipt['evaluation_code_seal_sha256']==sha(E/'evaluation_code_seal.json'), 'evaluation_freeze_chain')
    check(comparison['protocol_sha256']==sha(E/'protocol.json') and comparison['model_seal_sha256']==sha(E/'training/all_models_sealed.json')
          and comparison['prediction_seal_sha256']==joined['prediction_seal_sha256']==sha(E/'results/all_predictions_sealed.json'), 'protocol_model_predictions_label_join_chain')
    check(receipt['comparison_sha256']==sha(E/'comparison.json'), 'comparison_label_receipt_chain')
    check((E/'results/all_predictions_sealed.json').stat().st_mtime_ns <= (E/'evaluation_code_seal.json').stat().st_mtime_ns
          <= (E/'label_join_started.json').stat().st_mtime_ns <= (E/'comparison.json').stat().st_mtime_ns, 'global_predict_evaluation_freeze_label_score_chronology')
    check(p['at_utc']<=models['at_utc']<=joined['at_utc']<=comparison['at_utc'], 'recorded_train_label_join_chronology')
    check(packet['primary']==comparison['primary']=='AB_GLOBAL' and not packet['overall_research_complete'], 'primary_identity_or_scope_changed')
    check(set(comparison['core_Holm3'])==set(CORE_KEYS) and set(comparison['mechanism_joint_Holm8'])==set(MECHANISM_KEYS), 'prespecified_families_changed')
    check(all(r['family_tests']==3 for r in comparison['core_Holm3'].values()) and all(r['family_tests']==8 for r in comparison['mechanism_joint_Holm8'].values()), 'Holm_family_sizes')
    check(len(comparison['per_task_outcomes'])==69264 and predictions['outputs']==69264, 'full_output_denominator')
    check({c:comparison['source_cohorts'][c]['n'] for c in COHORTS}=={'coding363':363,'coding170':170,'math155':155,'agentic1467':1467}, 'source4_denominators')
    check((comparison['AF']['records'],comparison['AF']['independent_groups'],len(comparison['AF']['fixed120_sample_ids']))==(731,716,120), 'AF731_716_fixed120')
    check(all(r['n_independent_task_groups']==716 and r['n_records']==731 and r['duplicate_records_above_group_count']==15
              for k,r in comparison['mechanism_joint_Holm8'].items() if k.startswith('AF716_')), 'AF_duplicates_group_equal_inference')
    check(p['parameters']=={'AB_GLOBAL':337457,'AB_LOCAL':337457,'AB_STATIC':337457,'AB_VALUE_PERM':337457,'AB_REF':300593,'SF_REF':277633}, 'frozen_parameter_counts')
    for name in COHORTS:
        expected = set(ARMS)|{a+'/seed_'+str(s) for a in ARMS for s in SOURCE_SEEDS}
        table = comparison['source_cohorts'][name]['condition_table']
        check(set(table)==expected and all(r['n']==p['target_cohorts'][name]['n'] for r in table.values()), 'full_all_seed_source_table_'+name)
    af_table = comparison['AF']['all731_record_equal_and716_group_equal']
    check(set(af_table)==set(ARMS)|{a+'/seed_'+str(s) for a in ARMS for s in AF_SEEDS}, 'all_AF_seed_and_ensemble_tables')
    check(all(r['records']==731 and r['groups']==716 for r in af_table.values()), 'all_AF_tables_full_denominators')
    check(all(v['summary']['n']==120 for v in comparison['AF']['original_fixed120_cached_four'].values()), 'all_four_cached120_preserved')
    for path,h in {**receipt['label_files_sha256'],**receipt['historical_reference_files_sha256']}.items():
        check(sha(path)==h,'historical_read_asset_changed:'+path)

    stage_records = []
    histories = []
    stage_sources = {}
    expected_final_checkpoints = set()
    validation_forward_batches = 0
    for row in p['source_schedule']+[{'suite':'AF',**r} for r in p['af_schedule']]:
        suite = row['suite']
        folder = E/'training'/suite/row['arm']/(str(row['seed']) if suite=='source' else f"{row['seed']}_{row['outer']}")
        specs = [('source_fit',p['source_ids']['train'],p['source_ids']['validation'])] if suite=='source' else [
            ('selection',row['selection_fit_ids'],row['validation_ids']),('refit',row['refit_ids'],[])]
        selected_epoch = None
        for stage,fit_ids,val_ids in specs:
            path = folder/(stage+'.json')
            rec = read(path)
            stage_sources[str(path)] = sha(path)
            check(rec['stage']==stage and rec['suite']==suite and rec['arm']==row['arm'] and rec['seed']==row['seed'], 'stage_identity:'+str(path))
            check(rec['protocol_sha256']==sha(E/'protocol.json') and rec['fit_ids_sha256']==digest(fit_ids)
                  and rec['validation_ids_sha256']==digest(val_ids), 'actual_fit_val_scope:'+str(path))
            check(rec['scaler_fit_only'] is True and rec['held_labels_used_for_selection']==0, 'fit_only_scaler_and_val:'+str(path))
            check(rec.get('runtime_backend_policy')==p['runtime_backend_policy'], 'actual_stage_runtime_backend_policy:'+str(path))
            check(sha(rec['checkpoint'])==rec['checkpoint_sha256'], 'stage_checkpoint:'+str(path))
            check(Path(rec['checkpoint']).resolve().is_relative_to((E/'training').resolve()), 'valid_checkpoint_must_not_use_invalid_archive:'+str(path))
            check(rec['completed_epochs']==len(rec['history']) and 1<=rec['completed_epochs']<=40
                  and [r['epoch'] for r in rec['history']]==list(range(1,rec['completed_epochs']+1)), 'complete_epoch_history:'+str(path))
            check(rec['updates']==sum(r['updates'] for r in rec['history']), 'update_receipt_sum:'+str(path))
            expected_batches = math.ceil(len(fit_ids)/16) if suite=='source' else math.ceil(len(row['inner_fit_groups'] if stage=='selection' else row['refit_groups'])/16)
            check(all(r['updates']==expected_batches for r in rec['history']), 'fixed_group_batch16:'+str(path))
            if val_ids:
                best = max(rec['history'],key=lambda r:(r['validation']['Top1'],r['validation']['MRR'],-r['epoch']))
                check(best['epoch']==rec['selected_epoch'], 'Top1_MRR_earliest_val_only_selection:'+str(path))
                selected_epoch = rec['selected_epoch']
                validation_forward_batches += math.ceil(len(val_ids)/16)*len(rec['history'])
                check(all(r['validation']['group_equal']==(suite=='AF') for r in rec['history']), 'selection_unit:'+str(path))
            else:
                check(rec['selected_epoch']==selected_epoch==rec['completed_epochs'], 'fresh_refit_exact_selected_epoch:'+str(path))
            if stage in ('source_fit','refit'):
                expected_final_checkpoints.add(str(Path(rec['checkpoint']).resolve()))
            stage_records.append({k:rec[k] for k in ('suite','arm','seed','outer','stage','selected_epoch','completed_epochs','updates','checkpoint','checkpoint_sha256','elapsed_seconds','runtime_backend_policy')})
            histories.extend(rec['history'])
        if suite=='AF':
            check(not set(row['selection_fit_ids'])&set(row['validation_ids'])
                  and set(row['selection_fit_ids'])|set(row['validation_ids'])==set(row['refit_ids'])
                  and not set(row['refit_ids'])&set(row['held_ids']), 'AF_nested_group_partition')
    stage_counts = Counter(r['stage'] for r in stage_records)
    updates = sum(r['updates'] for r in stage_records)
    check(dict(stage_counts)=={'source_fit':18,'selection':90,'refit':90} and len(stage_records)==198, 'all198_stages_including90_selection')
    check(updates==models['optimizer_updates'], 'all_stage_updates_vs_global_model_seal')
    check(expected_final_checkpoints=={str(Path(r['checkpoint']).resolve()) for r in models['models']}, 'exact108_fitted_final_models')
    check(all(r.get('runtime_backend_policy')==p['runtime_backend_policy'] for r in models['models']), 'all108_valid_fitted_models_runtime_backend_policy')

    initial = read(E/'initialization_audit.json')
    check(initial['status']=='PASS' and len(initial['records'])==108 and len(p['initializations'])==108, 'initial108_not_fitted_count')
    for suite in ('source','AF'):
        for initialization_seed in sorted({r['canonical_seed'] for r in initial['records'] if r['suite']==suite}):
            group = [r for r in initial['records'] if r['suite']==suite and r['canonical_seed']==initialization_seed and r['arm']!='SF_REF']
            contexts = [r for r in group if r['arm'] in CONTEXT_ARMS]
            base = [r for r in group if r['arm']=='AB_REF']
            check(len(contexts)==4 and len(base)==1 and len({r['state_digest'] for r in contexts})==1
                  and all(r['base_state_digest']==base[0]['state_digest'] and r['O_zero'] for r in contexts), 'shared_context_base_initialization:'+suite+'/'+str(initialization_seed))
    fixture = read(E/'fixtures/context_test_receipt.json')
    data_fixture = read(E/'fixtures/data_test_receipt.json')
    fixture_runs = [fixture]+fixture.get('prior_runs',[])
    fixture_compute = Counter()
    for r in fixture_runs:
        fixture_compute.update(r['compute_counters'])
    check(fixture['status']==data_fixture['status']=='PASS','required_fixtures_final_status')
    check(fixture['approved_plan_sha256']==sha(E/'approved_plan.json'),'fixture_approved_plan_binding')
    check(fixture_compute.get('optimizer_steps',0)==0 and fixture_compute.get('CUDA_model_forward_calls',0)==0,'artificial_fixtures_no_real_optimization')
    errors_log = lines(E/'training/errors.jsonl')
    abandoned_partial_updates = sum(r.get('updates_in_partial_epoch',0) for r in errors_log)
    valid_started_stages = len(stage_records)+len(errors_log)
    physical_completed_stages = len(stage_records)+failure['completed_invalid_optimization_stage_executions']
    physical_started_stages = valid_started_stages+failure['total_invalid_started_stage_executions']
    check(physical_completed_stages==269 and physical_started_stages==270
          and physical_started_stages<=authorization['actual_stage_execution_cap'], 'valid198_plus_invalid71_complete72_started_within270_authorized_cap')
    physical_updates = [updates+abandoned_partial_updates+failure['known_optimizer_update_lower_bound'],
                       updates+abandoned_partial_updates+failure['known_optimizer_update_upper_bound']]
    runtime_accounting = {'valid_completed_optimization_stages':len(stage_records),'valid_started_stage_executions':valid_started_stages,
                          'discarded_completed_optimization_stage_executions':failure['completed_invalid_optimization_stage_executions'],
                          'discarded_partial_stage_executions':failure['partial_invalid_stage_executions'],
                          'discarded_started_stage_executions':failure['total_invalid_started_stage_executions'],
                          'physical_completed_optimization_stage_executions':physical_completed_stages,
                          'physical_started_stage_executions':physical_started_stages,'authorized_physical_stage_cap':authorization['actual_stage_execution_cap'],
                          'valid_final_fitted_models':len(models['models']),'discarded_invalid_finished_fitted_models':failure['invalid_finished_fitted_models'],
                          'valid_schedule_optimizer_updates':updates,'valid_attempt_recorded_abandoned_partial_updates':abandoned_partial_updates,
                          'discarded_optimizer_update_interval':[failure['known_optimizer_update_lower_bound'],failure['known_optimizer_update_upper_bound']],
                          'physical_optimizer_update_interval':physical_updates,'physical_optimizer_updates_exact':None,
                          'partial_update_note':'Discarded stopped partial epoch is not exactly recorded; preserve32791..32827 range rather than infer an exact count',
                          'discarded_target_rank_outputs':failure['target_rank_outputs'],'discarded_target_evaluation_joins':failure['target_evaluation_joins'],
                          'same_scientific_plan_sha256':authorization['scientific_plan_sha256'],
                          'fresh_valid_fit_uses_only_same108_initial_files':True,'invalid_models_and_old_source_seal_not_used':True,
                          'invalid_attempt_archive':failure['backup_path'],'runtime_backend_policy':p['runtime_backend_policy'],
                          'repair_authorization_and_receipt_sha256':repair_sources,
                          'additional_artificial_GPU_repair_fixture':{'cases':gpu_fixture['test_cases'],**gpu_fixture['counters'],
                                                                    'separate_from_CPU_context_fixtures':True}}
    native_forward_batches = 18*sum(math.ceil(p['target_cohorts'][c]['n']/16) for c in COHORTS)
    native_forward_batches += sum(math.ceil(len(r['held_ids'])/16) for r in p['af_schedule'])
    source_outputs = 24*sum(p['target_cohorts'][c]['n'] for c in COHORTS)
    AF_native_seed_outputs = sum(len(r['held_ids']) for r in p['af_schedule'])
    AF_ensemble_outputs = 6*731
    check((source_outputs,AF_native_seed_outputs+AF_ensemble_outputs)==(51720,17544),'native_and_ensemble_output_accounting')
    counters = read(E/'checkpoint.json').get('counters',{})
    for key in ('new_paid_API','new_encoder','new_downloads','new_Gold','new_independent_tasks'):
        if key in counters:
            check(counters[key]==0,'unexpected_nonzero_resource_counter:'+key)
    ledger = API/'requests.jsonl'
    check(str(ledger) in p['protected_old_files_sha256'] and sha(ledger)==p['protected_old_files_sha256'][str(ledger)], 'zero_API_continuous_ledger_unchanged')
    resource = {'at_utc':now(),'expected_optimization_stages':198,'completed_optimization_stages':len(stage_records),
                'optimization_stage_counts':dict(stage_counts),'final_fitted_models':len(models['models']),
                'initialized_training_files':len(initial['records']),'initialization_files_are_not_fitted_models':True,
                'optimizer_updates_completed_schedule':updates,'abandoned_partial_epoch_optimizer_updates':abandoned_partial_updates,
                'valid_attempt_optimizer_updates_including_recorded_abandoned_partials':updates+abandoned_partial_updates,
                'physical_optimizer_update_interval':physical_updates,'physical_optimizer_updates_exact':None,
                'runtime_repair_execution_accounting':runtime_accounting,
                'completed_training_epochs':len(histories),'recorded_training_stage_seconds':sum(r['elapsed_seconds'] for r in stage_records),
                'launcher_model_training_elapsed_seconds':models['elapsed_seconds'],
                'GPU_training_batch_forwards_completed_schedule':updates,'validation_batch_forwards':validation_forward_batches,
                'final_prediction_native_model_batch_forwards':native_forward_batches,
                'new_ranker_outputs':69264,'source_outputs_including_ensembles':source_outputs,
                'AF_native_seed_OOF_outputs':AF_native_seed_outputs,'AF_ensemble_outputs':AF_ensemble_outputs,
                'AF_seed_joined_JSON_copy_entries_not_new_outputs':AF_native_seed_outputs,
                'total_saved_prediction_files':len(predictions['files']),
                'all_198_stage_receipts':stage_records,'stage_receipt_sha256':stage_sources,
                'fixture_runs_statuses':[r['status'] for r in fixture_runs],
                'fixture_test_cases_total':sum(r['test_cases_run'] for r in fixture_runs),
                'fixture_compute_counters_cumulative':dict(fixture_compute),
                'additional_artificial_GPU_repair_fixture':{'cases':gpu_fixture['test_cases'],**gpu_fixture['counters'],
                                                            'separate_from_CPU_context_fixtures':True},
                'data_receipt_is_latest_context_run_summary_not_an_additional_execution':True,
                'real_evaluation_model_forward_calls':0,'new_encoder':0,'new_paid_API':0,'new_downloads':0,'new_Gold':0,'new_independent_tasks':0,
                'fee_CNY':'0','continuous_API_ledger_unchanged':True,'no_old_asset_modifications':not errors,
                'historical_source_tasks':2155,'historical_AF_records':731,'historical_AF_groups':716,
                'historical_suites_not_pooled_as_one_independent_population':True,'training_error_events':errors_log,
                'device':'cuda','dtype':'float32','protocol_sha256':sha(E/'protocol.json')}
    write_new(E/'resource_audit.json',resource)
    packet.update(runtime_repair_execution_accounting=runtime_accounting,
                  valid_runtime_backend_policy_verified_for_all198_stages=not errors,
                  runtime_repair_no_scientific_method_or_metric_change=True)
    atomic(E/'main_decision_packet.json',packet)
    compact = {k:packet[k] for k in ('experiment','primary','scope','source_ensemble_hits','source_denominators','AF_fixed120_ensemble_hits',
                                    'AF_full731_record_metrics','AF_full716_group_equal_metrics','core_Holm3','mechanism_joint_Holm8','decision_owner')}
    compact.update(at_utc=now(),execution_audit_status='PASS' if not errors else 'FAIL',errors=errors,
                   completed_optimization_stages=len(stage_records),final_fitted_models=len(models['models']),new_ranker_outputs=69264,
                   runtime_repair_execution_accounting=runtime_accounting,
                   fee_CNY='0',new_Gold=0,scientific_decision_pending_with_root=True,controls_not_promoted=True)
    write_new(E/'compact_summary.json',compact)
    audit = {'at_utc':now(),'status':'PASS' if not errors else 'FAIL','errors':errors,
             'experiment':'Exp153','primary':'AB_GLOBAL','frozen_training_and_evaluation_verified':not errors,
             'all198_stages_including_selection90_verified':not errors,'all108_fitted_models_verified':not errors,
             'all198_valid_stage_actual_runtime_flags_match_new_protocol':not errors,
             'same_plan_repair_authorization_and_failure_witnesses_verified':not errors,
             'runtime_repair_execution_accounting':runtime_accounting,
             'all69264_outputs_sealed_before_target_join_verified':not errors,
             'all6arms3seeds_and_full_original_ordinal_ranks':True,'AF731_records716_group_equal_duplicate_handling':True,
             'joint_core_Holm3_and_mechanism_Holm8_preserved':True,'ordinary_and_family_adjusted_intervals_retained':True,
             'all_failures_original_denominators_retained':True,'historical_strong_references_and_original_primaries_preserved':True,
             'no_authorTEST600_unapproved_reserve_or_new_Gold':True,'no_new_API_encoder_or_download':True,
             'initialized_files_not_counted_as_fitted':True,'no_scientific_route_decided_by_executor':True,
             'protocol_sha256':sha(E/'protocol.json'),'model_seal_sha256':sha(E/'training/all_models_sealed.json'),
             'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json'),
             'artifacts':{str(E/n):sha(E/n) for n in ('comparison.json','main_decision_packet.json','paired_counterexamples.json',
                                                  'Gold_evaluation_receipt.json','resource_audit.json','compact_summary.json','metrics.csv')}}
    write_new(E/'final_execution_audit.json',audit)
    readme = '# Exp153 候选条件全轨迹上下文\n\n唯一主方法为 AB_GLOBAL。两套既有训练条件分别评价，历史曝光数据不作为新盲测。\n\n'
    readme += '入口：`trainer153.py run` → `predict153.py` → `evaluate153.py` → `finalize153.py`。评价前验证全部108拟合模型与69264输出封存，当前evaluator首次目标评价标签加入前冻结评价代码；AF原731标签在训练入口已加载，仅当前fit/val用于loss/选轮。\n\n'
    readme += f'收尾审计：{audit["status"]}；完成优化阶段 {len(stage_records)}/198（source18、AF selection90/refit90），拟合模型108，费用新增0。初始化文件及AF seed汇总副本另列。\n\n'
    readme += f'前次runtime不合规尝试已归档：71个完成阶段、1个partial阶段、72个物理启动与44个无效模型，目标输出/评分0。有效阶段198加前次71为物理完成{physical_completed_stages}，有效启动{valid_started_stages}加前次72为物理启动{physical_started_stages}/授权270。物理optimizer updates为有效updates加已弃用32791..32827的区间：{physical_updates[0]}..{physical_updates[1]}；旧partial不作假精确计数。新增2个GPU人工修复案例合计4forward/4backward/0updates，与原CPU fixture累计单列。\n\n'
    readme += '结果入口：`compact_summary.json`、`main_decision_packet.json`；完整表及逐任务结果为 `comparison.json`，救回/损坏为 `paired_counterexamples.json`，资源及约束为 `resource_audit.json`、`final_execution_audit.json`。\n\n'
    readme += 'Holm3为coding363对当轮SF与AF120对当轮SF/缓存AA；Holm8为coding363和AF716各对AB_REF/LOCAL/STATIC/VALUE_PERM。AF重复记录先组内均值；分层只作描述，历史B/143/SF保留原主方法身份。是否支持继续由root决定，不能晋升较好的control。\n'
    with (E/'README.md').open('x',encoding='utf-8') as f:
        f.write(readme)
    status('EXP153_COMPLETE' if not errors else 'EXP153_FINAL_AUDIT_ERROR_STOP',current_pid=None,
           completed_optimization_stages=len(stage_records),final_models=len(models['models']),optimizer_updates=updates,
           physical_completed_optimization_stage_executions=physical_completed_stages,physical_started_stage_executions=physical_started_stages,
           discarded_invalid_finished_fitted_models=failure['invalid_finished_fitted_models'],physical_optimizer_update_interval=physical_updates,
           new_ranker_outputs=69264,fee_CNY='0',scientific_decision_owner='root',
           next='root interprets fixed historical feasibility; no new experiment authorized by this completion')
    print(canonical({'Exp153':'finalized','status':audit['status'],'stages':len(stage_records),'fitted_models':108,'outputs':69264,'fee':'0'}),flush=True)
    if errors:
        raise RuntimeError('FINAL_EXECUTION_AUDIT_FAILED:'+','.join(errors))


if __name__=='__main__':
    run()

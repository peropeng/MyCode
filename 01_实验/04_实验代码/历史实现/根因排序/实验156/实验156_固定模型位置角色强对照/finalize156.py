"""Audit analytical count fits and cached diagnostics; no neural assets load."""
import ast
from collections import Counter,defaultdict
from fractions import Fraction
from common import *
from evaluate156 import verify_seals,fit_table_schedule,FAMILY_KEYS,EVALUATION_FILES


def lines(path):
    return [json.loads(row) for row in Path(path).read_text('utf-8-sig').splitlines() if row.strip()] if Path(path).exists() else []


def exact(v):
    return Fraction(v['numerator'],v['denominator'])


def analytic_fit_audit(p,fit_receipt,check):
    source = read(p['source_public_records'])['records'];AF = read(p['AF_public_records'])['records']
    by = {'source':{r['sample_id']:r for r in source},'AF':{r['sample_id']:r for r in AF}}
    records = [];receipt_by_path = {str(Path(r['path']).resolve()):r for r in fit_receipt['tables']}
    AF_schedule = {(r['seed'],r['outer']):r for r in p['AF_schedule']}
    for control,suite,seed,outer,fit_ids,held_ids,path in fit_table_schedule(p):
        saved = read(path);public = by[suite]
        groups = Counter(public[s]['task_group'] for s in fit_ids)
        held_groups = {public[s]['task_group'] for s in held_ids}
        histogram = {int(k):exact(v) for k,v in saved['histogram_exact'].items()}
        check(saved['group_record_counts']==dict(groups) and saved['fit_record_count']==len(fit_ids)
              and saved['fit_group_count']==len(groups),'original_fit_record_and_group_weights:'+str(path))
        check(exact(saved['total_fit_weight_exact'])==sum(histogram.values(),Fraction())==len(groups)
              and all(v>0 for v in histogram.values()),'each_complete_fit_group_total_exact_weight1:'+str(path))
        check(not set(groups)&held_groups and saved['label_source_sha256']==p['inputs'][saved['label_source']],
              'fit_held_groups_disjoint_original_label_bytes:'+str(path))
        if control==PRIORS[1]:
            check(set(histogram)<=set(range(10)) and saved['relative_bins']==10,'fixed10_relative_bins:'+str(path))
        else:
            check(all(0<=k<max(len(public[s]['turns']) for s in fit_ids) for k in histogram),'original_absolute_target_position_range:'+str(path))
        if suite=='source':
            check(saved['source122_validation_label_values_consumed']==0 and saved['fit_ids']==p['source_fit_ids']
                  and saved['held_ids']==p['source_validation_ids'] and len(fit_ids)==492 and len(held_ids)==122,
                  'source492_fit_only_122_validation_excluded:'+str(path))
        else:
            row = AF_schedule[seed,outer]
            check(saved['original_manifest_sha256']==row['original_manifest_sha256'] and saved['fit_groups']==row['refit_groups']
                  and saved['held_groups']==row['held_groups'] and set(saved['fit_groups'])==set(groups)
                  and set(saved['held_groups'])==held_groups,'exact_original_AF_refit_held_partition:'+str(path))
            check(saved['shared_AF_label_file_parsed'] and saved['fit_label_values_gated_before_statistics'],
                  'AF_shared_file_read_with_corresponding_refit_value_gate:'+str(path))
        rec = receipt_by_path[str(path.resolve())]
        check(rec['fit_ids_sha256']==saved['fit_ids_sha256'] and rec['held_ids_sha256']==saved['held_ids_sha256']
              and rec['fit_record_count']==len(fit_ids) and rec['fit_group_count']==len(groups),'fit_receipt_matches_actual_table:'+str(path))
        records.append({'suite':suite,'control':control,'seed':seed,'outer':outer,'path':str(path),'sha256':sha(path),
                        'fit_records':len(fit_ids),'fit_groups':len(groups),'held_records':len(held_ids),'held_groups':len(held_groups),
                        'consumed_label_ids_sha256':saved['consumed_label_ids_sha256'],'fit_ID_gate':saved['fit_ID_gate'],
                        'held_label_values_used_for_fit':saved['held_label_values_used_for_fit'],
                        'validation_or_target_based_parameter_selection':saved['validation_or_target_based_parameter_selection'],
                        'total_fit_weight_exact':saved['total_fit_weight_exact']})
    check(len(records)==32 and Counter(r['suite'] for r in records)=={'source':2,'AF':30},'exact_source2_AF30_analytic_tables')
    return records


def analytic_code_audit(p,check):
    inspected = {str(E/n) for n in ('rules156.py','prepare156.py','predict156.py','evaluate156.py','paired_stats156.py','diagnostics156.py','finalize156.py')}
    forbidden_imports = []
    for path in inspected:
        tree = ast.parse(Path(path).read_text('utf-8-sig'),filename=path)
        for node in ast.walk(tree):
            names = [a.name for a in node.names] if isinstance(node,ast.Import) else [node.module or ''] if isinstance(node,ast.ImportFrom) else []
            for name in names:
                if name.split('.')[0] in ('torch','tensorflow','transformers','pickle'):
                    forbidden_imports.append(path+':'+name)
    check(not forbidden_imports,'analytic_scripts_have_no_neural_weight_deserializer_or_framework_import')
    return {'inspected_source_sha256':{path:sha(path) for path in sorted(inspected)},'forbidden_imports':forbidden_imports,
            'static_code_binding_evidence_only_not_OS_level_GPU_monitor':True}


def diagnostic_audit(p,outcomes,check):
    path = E/'diagnostics_static_checkpoint.json';diagnostic = read(path)
    check(diagnostic['phase']=='CACHE_DIAGNOSTICS_COMPLETE' and diagnostic['status']=='PASS',
          'all_required_cached_diagnostics_complete_before_finalization')
    results = diagnostic['results_sha256'];check_hashes(results)
    expected_top = {E/'strata.json',E/'cache_consistency.json',E/'exact_task_overlap.json',E/'case_evidence/index.json'}
    check({str(q.resolve()) for q in expected_top}<={str(Path(q).resolve()) for q in results},'all_required_cached_diagnostic_outputs_hashed')
    inputs = diagnostic['input_hashes'];check_hashes(inputs)
    check_hashes(diagnostic['code_sha256']);check_hashes(diagnostic['old_and_current_accessed_files_sha256'])
    required_inputs = {str((E/'approved_plan.json').resolve()):PLAN_SHA,
                       str((E/'protocol.json').resolve()):sha(E/'protocol.json'),
                       str((E/'results/all_predictions_sealed.json').resolve()):sha(E/'results/all_predictions_sealed.json'),
                       str((E/'evaluation_outcomes.json').resolve()):sha(E/'evaluation_outcomes.json')}
    normalized_inputs = {str(Path(q).resolve()):h for q,h in inputs.items()}
    check(all(normalized_inputs.get(q)==h for q,h in required_inputs.items()),'diagnostic_input_plan_protocol_newseal_outcome_chain')
    expected_scopes = {c:{'records':p['target_cohorts'][c]['n'],'groups':p['target_cohorts'][c]['n']} for c in COHORTS}
    expected_scopes['AF'] = {'records':731,'groups':716}
    check(diagnostic['scopes']==expected_scopes,'diagnostics_all_original5_scopes_and_AF_duplicate_unit')
    for q in expected_top:
        value = read(q)
        check(value['experiment']=='Exp156' and value['status']=='COMPLETE' and value['approved_plan_sha256']==PLAN_SHA
              and value['protocol_sha256']==sha(E/'protocol.json') and value['prediction_seal_sha256']==sha(E/'results/all_predictions_sealed.json')
              and value['evaluation_outcomes_sha256']==sha(E/'evaluation_outcomes.json') and value['descriptive_only'],
              'descriptive_diagnostic_artifact_chain:'+q.name)
    cases = read(E/'case_evidence/index.json')
    selected = cases['selected_groups']
    groups = [row['task_group'] if isinstance(row,dict) else row for row in selected]
    check(len(groups)<=18 and len(groups)==len(set(groups)),'at_most18_unique_task_groups_without_pool_topup')
    check(diagnostic['case_groups']==cases['selected_count']==len(groups),'diagnostic_case_group_count_matches_index')
    check(cases['case_salt']=='Exp156-case-v1|' and cases['scope_order']==['coding363','AF','math155']
          and cases['category_order']==['C1','C2','C3','C4'] and cases['maximum_cases']==18
          and cases['across_scope_task_group_deduplication'] and cases['no_replacement_for_short_pools']
          and cases['AF_case_eligibility_uses_exact_group_mean_1_or_0_and_C3_inequality'], 'fixed_case_salt_order_and_exact_AF_group_rule')
    check(all(diagnostic['new_compute'].get(k)==0 for k in ('new_model_forward','new_optimization_training','new_neural_models',
                                                          'new_encoder','new_API','new_downloads','new_Gold','new_independent_tasks','new_ranker_outputs'))
          and diagnostic['new_compute']['fee_CNY']=='0','cached_diagnostics_have_zero_new_compute')
    used,ordered_groups = set(),[]
    for pool in cases['pools']:
        order = pool['eligible_groups_hash_order']
        expected_order = sorted(order,key=lambda g:(hashlib.sha256(('Exp156-case-v1|'+g).encode('utf-8')).hexdigest(),g))
        unused = [g for g in order if g not in used];chosen = unused[:2]
        check(order==expected_order and pool['quota']==2 and pool['selected_groups']==chosen
              and pool['selected_count']==len(chosen) and pool['eligible_unused_groups']==len(unused)
              and pool['no_replacement_for_short_pool'], 'salted_case_first2_unused_groups_without_topup:'+pool['scope']+'/'+pool['category'])
        ordered_groups.extend(chosen);used.update(chosen)
    check(ordered_groups==groups and len(cases['pools'])==9,'fixed_case_selection_order_all9_pools')
    indexed_paths = {str(Path(row['path']).resolve()):row for row in selected}
    case_paths = [q for q in results if Path(q).parent.resolve()==(E/'case_evidence').resolve() and Path(q).name!='index.json']
    check(len(case_paths)==len(groups),'one_representative_public_record_per_selected_group')
    for q in case_paths:
        case = read(q)
        check(case['experiment']=='Exp156' and case['approved_plan_sha256']==PLAN_SHA
              and case['task_group'] in set(groups) and case['descriptive_only'],'case_artifact_group_plan_binding:'+q)
        entry = indexed_paths[str(Path(q).resolve())];scope,group = entry['scope'],entry['task_group']
        item = outcomes['scopes'][scope]
        members = sorted(sid for sid in item['ids'] if item['views'][VIEWS[0]][sid]['task_group']==group)
        sid = entry['representative_sample_id']
        check(bool(members) and sid==members[0]==case['representative_sample_id'] and case['scope']==scope
              and case['case_category']==entry['category'] and entry['sha256']==sha(q)
              and entry['case_sort_sha256']==hashlib.sha256(('Exp156-case-v1|'+group).encode('utf-8')).hexdigest(),
              'case_original_group_lexmin_record_hash_and_category:'+q)
        rates = {kind:{name:Fraction(sum(values[s]['Top1'] for s in members),len(members)) for name,values in item[kind].items()}
                 for kind in ('views','SF_views','controls')}
        eligible = {'C1':all(v==1 for v in rates['views'].values()) and all(v==0 for v in rates['SF_views'].values()),
                    'C2':all(v==0 for v in rates['views'].values()) and all(v==1 for v in rates['SF_views'].values()),
                    'C3':len(set(rates['views'].values()))>1,
                    'C4':all(v==1 for v in rates['views'].values()) and any(v==1 for v in rates['controls'].values())}
        if scope=='math155':
            qualification = cases['all_group_eligibility_details'][scope][group]
            eligible['MATH_SHARED_GLOBAL_NO_CONTENT'] = rates['views'][VIEWS[0]]==1 and exact(qualification['NO_CONTENT_group_correct_rate'])==1
        check(eligible[entry['category']],'selected_case_actual_exact_group_eligibility:'+q)
        check(case['Gold_original_ordinal']==item['gold'][sid] and case['public_record']['sample_id']==sid
              and case['public_record']['task_group']==group and case['turns']==case['public_record']['turns']
              and case['coordinate_map']==case['public_record']['coordinate_map']
              and len(case['turns'])==len(case['coordinate_map'])==item['views'][VIEWS[0]][sid]['raw_steps'],
              'full_original_public_case_coordinates_and_Gold:'+q)
        check(len(case['cached_and_new_control_predictions'])==77
              and case['original_predictions_exported_without_score_or_rank_fabrication']
              and case['mechanical_evidence_only_no_root_cause_interpretation']
              and case['selected_explanatory_cases_are_not_independent_statistical_denominators'],
              'case_all72_cached_and5_current_native_predictions_no_rootcause_interpretation:'+q)
    return diagnostic,{'case_groups':groups,'case_files':case_paths,'scopes':expected_scopes,'results_sha256':results,
                       'mechanical_rule':'SHA256(Exp156-case-v1|group) ascending, C1/C2 exactgroup1/0, C3 three means differ; lexmin record; at most18; no topup',
                       'not_independent_statistical_denominator':True}


def run():
    p,seals = verify_seals();errors = []
    def check(ok,name):
        if not ok:
            errors.append(name)
    comparison,packet,outcomes = read(E/'comparison.json'),read(E/'main_decision_packet.json'),read(E/'evaluation_outcomes.json')
    evaluation,joined = read(E/'evaluation_code_seal.json'),read(E/'label_join_started.json')
    check(evaluation['sources']=={str(E/n):sha(E/n) for n in EVALUATION_FILES},'frozen_evaluation_three_sources')
    check(outcomes['experiment']=='Exp156' and comparison['primary']==packet['primary']==PRIMARY
          and comparison['underlying_locked_primary']==packet['underlying_locked_primary']=='AB_GLOBAL','locked156_alias_preserves_original_underlying153_primary')
    check(comparison['protocol_sha256']==joined['protocol_sha256']==outcomes['protocol_sha256']==sha(E/'protocol.json')
          and comparison['prediction_seal_sha256']==joined['prediction_seal_sha256']==outcomes['prediction_seal_sha256']==sha(E/'results/all_predictions_sealed.json'),
          'protocol_prediction_evaluator_outcome_chain')
    check(comparison['evaluation_code_seal_sha256']==joined['evaluation_code_seal_sha256']==outcomes['evaluation_code_seal_sha256']==sha(E/'evaluation_code_seal.json')
          and comparison['evaluation_outcomes_sha256']==sha(E/'evaluation_outcomes.json'),'code_seal_outcome_comparison_chain')
    check(outcomes['approved_plan_sha256']==evaluation['approved_plan_sha256']==PLAN_SHA and outcomes['new_neural_outputs']==0,
          'plan_binding_no_new_cached_neural_outputs')
    check((E/'results/all_predictions_sealed.json').stat().st_mtime_ns<=(E/'evaluation_code_seal.json').stat().st_mtime_ns
          <=(E/'label_join_started.json').stat().st_mtime_ns<=min((E/'evaluation_outcomes.json').stat().st_mtime_ns,(E/'comparison.json').stat().st_mtime_ns),
          'all18816_new_outputs_precede_this_evaluator_target_or_old_score_join')
    family = comparison['joint_Holm30']
    check(set(family)==set(FAMILY_KEYS) and len(family)==30 and set(evaluation['joint_Holm30'])==set(FAMILY_KEYS),
          'exact_prespecified3views_2scopes_5controls_jointHolm30')
    check(comparison['all30_prespecified_tests_retained_including_identical_AF_controls']
          and comparison['original_SF_comparisons_reference_only_no_new_p'],'keep_duplicate_controls_and_originalSF_only_reference')
    for key,row in family.items():
        check(row['family_tests']==30 and row['statistically_supported_lead']==
              (row['difference']>0 and row['holm_adjusted_p']<.05 and row['familywise_difference_interval'][0]>0),
              'unchanged_supported_lead_rule:'+key)
        if '_AF716_' in key:
            check((row['n_records'],row['n_independent_task_groups'],row['duplicate_records_above_group_count'])==(731,716,15),
                  'AF716_exact_within_group_mean_pair_unit:'+key)
    check(len(comparison['new_control_per_task_outcomes'])==18816 and comparison['new_ranker_outputs']==18816,
          'all18816_unique_new_control_outputs_scored')
    expected_scopes = set(COHORTS)|{'AF'}
    check(set(outcomes['scopes'])==expected_scopes,'evaluation_outcome5scope_diagnostic_contract')
    for scope,spec in outcomes['scopes'].items():
        expected_records = 731 if scope=='AF' else p['target_cohorts'][scope]['n']
        check(len(spec['ids'])==len(set(spec['ids']))==len(spec['gold'])==expected_records
              and set(spec['controls'])==set(CONTROLS) and set(spec['views'])==set(spec['SF_views'])==set(VIEWS),
              'complete5controls_3locked_3SF_views_original_ids:'+scope)
        check(all(set(values)==set(spec['ids']) for field in ('controls','views','SF_views') for values in spec[field].values()),
              'whole_original_scope_no_drop:'+scope)
    check({c:comparison['source_cohorts'][c]['n'] for c in COHORTS}=={'coding363':363,'coding170':170,'math155':155,'agentic1467':1467},
          'all_source4_original_denominators')
    check((comparison['AF']['records'],comparison['AF']['groups'],len(comparison['AF']['fixed120_sample_ids']))==(731,716,120),'AF731_716_120_full_scope')
    AF_conditions = set(CONTROLS)|{c+'/seed_'+str(s) for c in PRIORS for s in AF_SEEDS}
    check(set(comparison['AF']['controls_all731_record_and716_group'])==set(comparison['AF']['controls_fixed120'])==AF_conditions,
          'all3det_6OOF_2ensemble_prior_tables')
    for path,h in {**comparison['label_files_sha256'],**comparison['historical_reference_files_sha256']}.items():
        check(sha(path)==h,'original_label_or_cached_reference_bytes_changed:'+path)
    fits = analytic_fit_audit(p,seals['fit'],check);code = analytic_code_audit(p,check)
    diagnostics,cases = diagnostic_audit(p,outcomes,check)
    fixture = read(E/'fixtures/rule_test_receipt.json')
    check(fixture['status']=='PASS','necessary_artificial_position_role_rule_fixture_pass')
    check(fixture['approved_plan_sha256']==PLAN_SHA and all(sha(E/n)==h for n,h in fixture['source_sha256'].items())
          and fixture['new_real_ranker_outputs']==0,'artificial_rule_fixture_frozen_sources_and_no_real_rank_outputs')
    fixture_counters = fixture.get('physical_cumulative_compute_counters',fixture.get('compute_counters',{}))
    check(all(fixture_counters.get(k,0)==0 for k in ('model_forward_calls','neural_model_forwards','backward_calls','optimizer_updates','new_neural_forward',
                                                    'trained_parent_weight_loads','real_records','real_Gold')),
          'rule_fixture_has_no_neural_forward_or_realGold')
    # Physical generation events, when present, remain separate from the valid unique output count.
    physical = lines(E/'physical_generation_events.jsonl');errors_log = lines(E/'errors.jsonl')
    invalid_generation = [{'path':str(q),'sha256':sha(q),'receipt':read(q)} for q in E.glob('invalid*generation*.json')]
    resource = {'at_utc':now(),'experiment':'Exp156','new_analytic_count_fit_tables':32,'analytic_fit_table_counts':{'source':2,'AF':30},
                'actual_fit_tables_and_ID_isolation':fits,'fit_isolation_receipt_sha256':sha(E/'fit_isolation_receipt.json'),
                'new_unique_valid_ranker_outputs':18816,'source_new_ranker_outputs':10775,'AF_new_ranker_outputs':8041,
                'AF_deterministic_rule_outputs_generated_once':2193,'AF_native_prior_OOF_outputs':4386,'AF_three_schedule_ensemble_outputs':1462,
                'AF_seed_joined_JSON_copy_entries_not_new_outputs':4386,'new_prediction_JSON_files':61,
                'cached153_154_155_neural_inference_and_training_consumption_newly_charged':0,
                'A_B_reuse_of_same_prior_outputs_not_new_generation':True,'fit_tables_are_count_statistics_not_optimization_models':True,
                'new_optimization_training':0,'new_neural_models':0,'new_neural_weight_or_embedding_deserializations':0,
                'new_model_forward':0,'new_neural_forward':0,'new_encoder':0,'new_API':0,'new_downloads':0,'new_Gold':0,'new_independent_tasks':0,'fee_CNY':'0',
                'fixture_receipt':fixture,'necessary_artificial_rule_fixture_physical_counters':fixture_counters,
                'recorded_physical_generation_events':physical,'recorded_local_failures':errors_log,
                'recorded_invalid_generation_receipts':invalid_generation,
                'valid_unique_outputs_not_substituted_for_recorded_failed_physical_generation':True,
                'analytic_source_audit':code,'diagnostic_output_hashes':diagnostics['results_sha256'],
                'cached_diagnostics_elapsed_seconds':diagnostics['elapsed_seconds'],
                'cached_prediction_file_read_events':diagnostics['existing_prediction_file_read_events'],
                'cached_prediction_rows_parsed_not_new_ranker_outputs':diagnostics['existing_prediction_rows_parsed'],
                'diagnostic_cases':cases,'all_immutable_old_public_prediction_ledger_sources_hash_verified':not errors,
                'scope':'Analytical rule ranks plus cached diagnostics; no model/GPU training or inference and no old resource double charge'}
    write_new(E/'resource_audit.json',resource)
    packet.update(execution_audit_status='PASS' if not errors else 'FAIL',
                  all32_analytic_fit_ID_gates_verified=not errors,all18816_new_rankings_and61files_verified=not errors,
                  cached_diagnostics_complete=not errors,mechanical_case_group_count=len(cases['case_groups']),
                  cached_diagnostics={'strata':str(E/'strata.json'),'consistency':str(E/'cache_consistency.json'),
                                      'exact_overlap':str(E/'exact_task_overlap.json'),'case_index':str(E/'case_evidence/index.json')},
                  new_neural_compute_and_weight_deserialization=0,resource_audit=str(E/'resource_audit.json'))
    atomic(E/'main_decision_packet.json',packet)
    keys = ('experiment','primary','underlying_locked_primary','scope','source_denominators','source_control_hits','source_fixed_view_hits',
            'AF_control_731record_metrics','AF_control_716group_metrics','AF_control_fixed120_hits','AF_fixed_view_716group_metrics',
            'AF_fixed_view_fixed120_hits','joint_Holm30','duplicate_AF_controls_preserved_in_family30','decision_owner')
    compact = {k:packet[k] for k in keys}
    compact.update(at_utc=now(),execution_audit_status='PASS' if not errors else 'FAIL',errors=errors,new_analytic_count_fit_tables=32,
                   new_ranker_outputs=18816,new_prediction_JSON_files=61,mechanical_case_group_count=len(cases['case_groups']),
                   cached_diagnostics=packet['cached_diagnostics'],new_neural_compute=0,new_Gold=0,fee_CNY='0')
    write_new(E/'compact_summary.json',compact)
    artifact_names = ('comparison.json','metrics.csv','evaluation_outcomes.json','main_decision_packet.json','compact_summary.json',
                      'resource_audit.json','diagnostics_static_checkpoint.json')
    artifacts = {str(E/name):sha(E/name) for name in artifact_names};artifacts.update(diagnostics['results_sha256'])
    final = {'at_utc':now(),'experiment':'Exp156','primary':PRIMARY,'status':'PASS' if not errors else 'FAIL','errors':errors,
             'all32_count_fit_tables_actual_fit_ID_and_held_isolation_verified':not errors,
             'all18816_unique_rankings61prediction_files_and_no_OOF_copy_inflation_verified':not errors,
             'all_source4_AF731record716group120_denominators_and_original_coordinates_retained':not errors,
             'all30_prespecified_view_control_tests_retained_with_duplicate_disclosure':not errors,
             'all_strata_consistency_exact_overlap_mechanical_cases_complete_hash_verified':not errors,
             'at_most18_unique_case_groups_lexmin_public_representative':not errors,
             'old_primary_identities_scores_p_values_and_stronger_references_preserved':not errors,
             'target_evaluator_Gold_and_cached_score_parse_follows_all_new_rankings_seal':not errors,
             'no_new_neural_training_model_forward_weight_deserialization_encoder_API_download_Gold_independent_unit':not errors,
             'exact_text_overlap_not_automatically_Gold_identity_or_leakage_no_fuzzy_or_new_embedding':True,
             'case_export_descriptive_not_independent_statistical_denominator_or_self_explained_root_cause':True,
             'no_authorTEST600_unapproved_reserve_no_control_promoted_to_primary':True,
             'protocol_sha256':sha(E/'protocol.json'),'prediction_seal_sha256':sha(E/'results/all_predictions_sealed.json'),
             'evaluation_code_seal_sha256':sha(E/'evaluation_code_seal.json'),'artifacts':artifacts}
    write_new(E/'final_execution_audit.json',final)
    status('EXP156_COMPLETE' if not errors else 'EXP156_FINAL_AUDIT_ERROR_STOP',new_analytic_count_fit_tables=32,new_ranker_outputs=18816,
           new_optimization_training=0,new_neural_models=0,new_model_forward=0,new_Gold=0,fee_CNY='0',
           next='root interprets all fixed simple controls and cached diagnostics; no neural model or scientific variant substitution')
    print(canonical({'Exp156':'finalized','status':final['status'],'fit_tables':32,'new_outputs':18816,'case_groups':len(cases['case_groups']),'new_neural_compute':0}),flush=True)
    if errors:
        raise RuntimeError('FINAL156_EXECUTION_AUDIT_FAILED:'+','.join(errors))


if __name__=='__main__':
    run()

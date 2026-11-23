"""Agentless FSE2025 paper main sampling and repository passing-regression pipeline.

All generation, physical patches and native validation use the shared environment.
Real semantic retrieval uses exact public-code cache and original frequency combine.
"""
import ast,copy,hashlib,json
from collections import Counter
from pathlib import Path
from agentless_bridge import official_core166 as official
from paper_local_core241 import structure,skeleton,context,normalized_patch
from retrieval178 import retrieve

METHOD='AGENTLESS_FSE2025_PAPER_MAIN_4L40P40T_FLASH_QWEN_EMBED_ADAPTED'
E=Path(__file__).resolve().parent
PROMPTS=json.loads((Path('D:\\Code\\毕设\\graduate-thesis-experiments\\工作区\\1008-exp183-fixed12-complete-main\\实验\\实验183_固定十二题完整恢复与排序对照')/'agentless_bridge/official_prompts166.json').read_text('utf-8'))
STAGES=('suspicious_files','irrelevant_folders','dense_retrieval','file_combine','related_elements','fine_locations',
        'forty_independent_patches','forty_original_reproductions','normalized_test_vote','paper_repo_regression_selection',
        'candidate_regression_reproduction','normalized_patch_vote')

class ModelSemanticFailure(ValueError):pass
class CoreUnavailable(RuntimeError):pass

def seed(task_id,role,ordinal):return int(hashlib.sha256(f'Exp166|Agentless|{task_id}|{role}|{ordinal}'.encode()).hexdigest()[:8],16)
def status_error(error):
    text=type(error).__name__+': '+str(error)
    if 'CONTEXT' in text:return 'CONTEXT_UNKNOWN'
    if any(code in text for code in ('NO_NEW','GLOBAL_DEADLINE','EXTERNAL_STOP','DEADLINE_INTERRUPTED')):return 'NOT_RUN'
    if type(error).__module__.split('.')[0] in ('requests','urllib3','httpx','http','urllib'):return 'ENGINEERING_UNKNOWN'
    if isinstance(error,ModelSemanticFailure) or type(error).__name__=='ModelOutputError':return 'MODEL_SEMANTIC_FAILURE'
    if type(error).__name__ in ('BudgetError','FinanceGateRejected') or 'BUDGET' in text:return 'BUDGET_CENSORED'
    return 'ENGINEERING_UNKNOWN'

def passing_nodes(result,allowed):
    outcomes=result.get('outcomes',{})
    if isinstance(outcomes,dict):
        passed=[]
        for node,value in outcomes.items():
            state=value.get('outcome',value.get('status')) if isinstance(value,dict) else value
            if str(state).lower() in ('passed','pass'):passed.append(node)
        if outcomes:return [n for n in allowed if n in passed]
    elif isinstance(outcomes,list):
        passed=[x.get('nodeid',x.get('node')) for x in outcomes if str(x.get('outcome',x.get('status',''))).lower() in ('passed','pass')]
        if outcomes:return [n for n in allowed if n in passed]
    return list(allowed) if result.get('passed') is True else []

def native_known(result):
    native=result.get('native_record') or {}
    status=str(result.get('status','')).upper()
    if status in ('ENGINEERING_UNKNOWN','ENGINEERING_ERROR','GUARD_FAILURE','GUARD_NOT_LOADED','NOT_RUN','TIMEOUT','ERROR','UNKNOWN'):
        raise CoreUnavailable('PUBLIC_NATIVE_UNKNOWN:'+status)
    if native.get('guard_loaded') is False:raise CoreUnavailable('PUBLIC_NATIVE_GUARD_NOT_LOADED')
    return result

def raw_edits(raw,files,intervals,business_paths=None):
    """Execute original SEARCH/REPLACE parser, without eval or arbitrary shell."""
    errors=[];edits=[];changed={};illegal_attempts=[];syntax_failure=False
    business_paths=set(files) if business_paths is None else set(business_paths)
    blocks=official.extract_python_blocks(raw)
    commands=official.split_edit_multifile_commands(blocks,diff_format=True)
    for quoted,items in commands.items():
        try:
            path=ast.literal_eval(quoted)
            if path not in files:
                if path not in business_paths:
                    # No private read. Submit the model's attempted path to the
                    # common guard so an illegal file cannot silently disappear.
                    illegal_attempts.append({'path':path,'old':'__UNRESOLVED_MODEL_SEARCH_SPAN__','new':'__INVALID_OUTSIDE_BUSINESS_ATTEMPT__'})
                raise ValueError('GENERATED_FILE_NOT_IN_PUBLIC_CONTEXT')
            if not intervals.get(path):raise ValueError('GENERATED_FILE_WITHOUT_LEGAL_MODEL_LOCATION')
            new=official.parse_diff_edit_commands(items,files[path],copy.deepcopy(intervals[path]))
            if new==files[path] or not new.strip():raise ValueError('NO_APPLIED_SEARCH_REPLACE_CHANGE')
            ast.parse(new)
            changed[path]=new;edits.append({'path':path,'old':files[path],'new':new})
        except Exception as error:
            syntax_failure=syntax_failure or isinstance(error,SyntaxError)
            errors.append({'file':quoted,'error':type(error).__name__+': '+str(error),'source_valid_subset_preserved':not isinstance(error,SyntaxError)})
    if not edits:errors.append({'error':'NO_VALID_MODEL_SEARCH_REPLACE_EDIT'})
    # Original _post_process retains successfully parsed files; its caller's
    # check_syntax rejects the whole candidate if any emitted code is invalid.
    if syntax_failure:return [],{},errors
    return edits+illegal_attempts,changed,errors

def run(env):
    env.require_paper_main_current_binding()
    ledger=[];done={stage:False for stage in STAGES};calls=[];patches=[];tests=[];selected_test=None;selected_patch=None
    base=copy.deepcopy(env.initial_snapshot);final=base;status='COMPLETED';selection={};failure=None
    def record(stage,evidence):
        row={'stage':stage,**copy.deepcopy(evidence)};ledger.append(row);env.record(stage,row);return row
    def request(role,prompt,temperature=0,max_tokens=300,ordinal=0):
        if env.time_left()<=0:raise CoreUnavailable('NO_NEW_METHOD_GLOBAL_DEADLINE')
        response=env.llm('agentless_'+role,[{'role':'system','content':'You are a helpful assistant. Only the supplied public business source and public test interfaces are available. Fixed tests, private tests and references are immutable; never access them.'},{'role':'user','content':prompt}],temperature,seed(env.task_id,role,ordinal),max_tokens)
        if not isinstance(response.get('content'),str):raise ModelSemanticFailure('MODEL_TEXT_CONTENT_REQUIRED')
        row={'role':role,'ordinal':ordinal,'temperature':temperature,'seed':seed(env.task_id,role,ordinal),'prompt_utf8_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
             'raw_output':response['content'],'usage':response.get('usage',{}),'call_ordinal':response.get('call_ordinal'),'finish_reason':response.get('finish_reason')}
        calls.append(row);record('llm',row);return response['content']
    try:
        files={p:v for p,v in env.business_files().items() if p.endswith('.py')}
        if not files:raise CoreUnavailable('NO_PUBLIC_BUSINESS_PYTHON_SOURCE')
        tree=structure(files);repo_tree=official.show_project_structure(tree).strip();problem=env.goal+'\nObserved current public recovery failure: '+json.dumps(env.initial_public_feedback,ensure_ascii=False,sort_keys=True)
        raw=request('suspicious_files',PROMPTS['obtain_relevant_files_prompt'].format(problem_statement=problem,structure=repo_tree).strip())
        found=official.correct_file_paths(raw.strip().split('\n'),[(p,[]) for p in files]);done['suspicious_files']=True
        record('suspicious_files',{'found_files':found,'available_public_files':len(files),'original_repo_tree_sha256':hashlib.sha256(repo_tree.encode()).hexdigest()})
        raw=request('irrelevant_folders',PROMPTS['obtain_irrelevant_files_prompt'].format(problem_statement=problem,structure=repo_tree).strip(),max_tokens=2048)
        irrelevant=[x for x in raw.strip().split('\n') if x.endswith('/') or x.endswith('.py')]
        allowed=[p for p in files if not any(p.startswith(x) for x in irrelevant)];done['irrelevant_folders']=True
        record('irrelevant_folders',{'model_selected_irrelevant':irrelevant,'remaining_files':allowed,'filter_uses_public_names_only':True})
        retrieved,evidence=retrieve(files,env.retrieval_query,env.retrieval_cache,allowed);done['dense_retrieval']=True;record('dense_retrieval',evidence)
        votes=Counter()
        for path in found[:3]:votes[path]+=1
        for path in retrieved[:3]:votes[path]+=1
        combined=[path for path,count in votes.most_common()][:3];done['file_combine']=True
        record('file_combine',{'LLM_top3':found[:3],'embedding_top3':retrieved[:3],'Counter_occurrences':dict(votes),'combined_top3':combined,'ties':'Insertion order: LLM first then retrieval'})
        if not combined:raise ModelSemanticFailure('NO_COMBINED_PUBLIC_FILE_CANDIDATES')
        selected_files={p:files[p] for p in combined}
        skeletons=''.join(PROMPTS['file_content_in_block_template'].format(file_name=p,file_content=skeleton(code)) for p,code in selected_files.items())
        raw=request('related_elements',PROMPTS['obtain_relevant_functions_and_vars_from_compressed_files_prompt_more'].format(problem_statement=problem,file_contents=skeletons))
        coarse=official.extract_locs_for_files(official.extract_code_blocks(raw),combined);done['related_elements']=True
        record('related_elements',{'model_locations':coarse,'skeleton_source':'Original libcst get_skeleton with class/module comments and fields retained; no oracle','source_file_sha256':{p:hashlib.sha256(code.encode()).hexdigest() for p,code in selected_files.items()}})
        coarse_context,coarse_ranges=context(coarse,selected_files,10,False)
        location_sets=[]
        for location_sample in range(4):
            raw=request('fine_locations',PROMPTS['obtain_relevant_code_combine_top_n_prompt'].format(problem_statement=problem,file_contents=coarse_context),temperature=.8,ordinal=location_sample)
            fine=official.extract_locs_for_files(official.extract_code_blocks(raw),combined)
            repair_context,intervals=context(fine,selected_files,10,True)
            location_sets.append({'sample':location_sample,'fine':fine,'context':repair_context,'intervals':intervals})
            record('fine_location_set',{'sample':location_sample,'fine_locations':fine,'repair_context_intervals':intervals,'context_each_side':10,'repair_context':repair_context,'original_sampling_temperature':.8})
        done['fine_locations']=True
        record('fine_locations',{'location_set_count':len(location_sets),'coarse_context_intervals':coarse_ranges,'fine_location_sets':location_sets,'four_independent_location_sets_retained':True})
        for location_id,location in enumerate(location_sets):
            for patch_ordinal in range(10):
                sample=patch_ordinal*4+location_id
                temperature=0. if patch_ordinal==0 else .8;intervals=location['intervals'];repair_context=location['context']
                if repair_context:
                    patch_prompt=PROMPTS['repair_prompt_combine_topn_cot_diff'].format(problem_statement=problem,repair_relevant_file_instruction=PROMPTS['repair_relevant_file_instruction'],content=repair_context).strip()
                    raw=request('patch',patch_prompt,temperature,1024,sample)
                    edits,changed,parse_errors=raw_edits(raw,selected_files,intervals,business_paths=set(files))
                else:
                    raw='';edits=[];changed={};parse_errors=[{'error':'NO_VALID_MODEL_FINE_EDIT_LOCATION_FOR_THIS_LOCATION_SET','no_synthetic_patch_or_oracle_location':True}]
                row={'sample':sample,'location_set':location['sample'],'patch_ordinal_in_location':patch_ordinal,'temperature':temperature,'raw_output':raw,'edits':edits,'parse_errors':parse_errors,'valid':False,'normalized_patch':''}
                if edits:
                    env.restore(base);applied=env.apply_patch(edits,'agentless_independent_patch_'+str(sample));row['application']=applied
                    legal=applied.get('legal');legal=legal.get('legal') if isinstance(legal,dict) else legal
                    if legal is True and not applied.get('apply_errors') and applied.get('snapshot'):
                        row['snapshot']=applied['snapshot'];row['normalized_patch']=normalized_patch(env.task_id,selected_files,changed,list(changed));row['valid']=bool(row['normalized_patch'].strip())
                patches.append(row);record('patch_candidate',row)
        done['forty_independent_patches']=True
        test_prompt=PROMPTS['generate_tests_prompt_template'].format(problem_statement=problem).strip()
        for sample,temperature in enumerate([0.]+[.8]*39):
            raw=request('reproduction',test_prompt,temperature,1024,sample);code=official.extract_first_code_block(raw)
            row={'sample':sample,'temperature':temperature,'raw_output':raw,'code':code,'verified':False,'normalized_test':''}
            if code:
                try:ast.parse(code)
                except SyntaxError as error:row['parse_error']=str(error)
                else:
                    env.restore(base);result=native_known(env.run_reproduction(code,snapshot=base,label='agentless_original_reproduction_'+str(sample)));row['native']=result
                    row['verified']=result.get('reproduced') is True and result.get('resolved') is not True
                    row['normalized_test']=official.normalize_test(code)
            else:row['parse_error']='MODEL_REPRODUCTION_PYTHON_BLOCK_REQUIRED'
            tests.append(row);record('original_reproduction',row)
        done['forty_original_reproductions']=True
        verified=[t for t in tests if t['verified'] and t['normalized_test'].strip()]
        test_votes=Counter(t['normalized_test'] for t in verified)
        if verified:selected_test=max(verified,key=lambda t:(test_votes[t['normalized_test']],-t['sample']))
        done['normalized_test_vote']=True
        record('normalized_test_vote',{'verified_test_samples':[t['sample'] for t in verified],'occurrence_counts':dict(test_votes),'selected_sample':selected_test['sample'] if selected_test else None,'none_verified_official_fallback':not verified,'ties':'Earliest actual independent sample'})
        ordinary=list(env.paper_public_repository_regression_nodes)
        if not ordinary:raise CoreUnavailable('ROOT_FROZEN_LEGAL_REPOSITORY_TEST_POOL_NOT_AVAILABLE')
        env.restore(base);base_regression=native_known(env.run_paper_repository_regression(snapshot=base,nodes=ordinary,label='agentless_current_repository_passing_discovery'));passing=passing_nodes(base_regression,ordinary)
        exclude_raw=request('regression_exclusion',PROMPTS['select_tests_prompt_template'].format(problem_statement=problem,passing_tests='\n'.join(passing)).strip(),max_tokens=1024) if passing else ''
        excluded=exclude_raw.strip().split('\n') if exclude_raw else [];retained=[n for n in passing if n not in excluded];done['paper_repo_regression_selection']=True
        record('paper_repo_regression_selection',{'original_native':base_regression,'original_passing_tests':passing,'LLM_excluded':excluded,'retained_regression':retained,'empty_model_selection_not_filled_from_hidden':not retained})
        for row in patches:
            if not row['valid']:continue
            env.restore(row['snapshot'])
            regression=native_known(env.run_paper_repository_regression(snapshot=row['snapshot'],nodes=retained,label='agentless_candidate_regression_'+str(row['sample']))) if retained else {'passed':True,'failure_count':0,'status':'EMPTY_LLM_SELECTED_REGRESSION_SET','native_record':{'executed':False}}
            row['regression']=regression;row['regression_failure_count']=int(regression.get('failure_count',0 if regression.get('passed') else len(retained)))
            if selected_test:
                repro=native_known(env.run_reproduction(selected_test['code'],snapshot=row['snapshot'],label='agentless_candidate_reproduction_'+str(row['sample'])))
                row['reproduction']=repro;row['reproduction_resolved']=repro.get('resolved') is True
            else:row['reproduction_resolved']=None
            record('candidate_validation',{'sample':row['sample'],'snapshot':row['snapshot'],'ordinary_regression':row['regression'],'selected_reproduction':row.get('reproduction'),'uses_hidden':False})
        done['candidate_regression_reproduction']=True
        valid=sorted([p for p in patches if p['valid'] and 'regression_failure_count' in p],key=lambda p:p['sample'])
        min_failures=min((p['regression_failure_count'] for p in valid),default=None)
        regression_best=[p for p in valid if p['regression_failure_count']==min_failures]
        reproduction_best=[p for p in regression_best if p.get('reproduction_resolved') is True] if selected_test else []
        eligible=reproduction_best if reproduction_best else regression_best
        patch_votes=Counter(p['normalized_patch'] for p in eligible)
        if eligible:
            selected_patch=max(eligible,key=lambda p:(patch_votes[p['normalized_patch']],-p['sample']));final=selected_patch['snapshot']
        else:status='MODEL_SEMANTIC_FAILURE'
        done['normalized_patch_vote']=True
        reason={'rule':'Minimum ordinary regression failures; selected reproduction resolved when any; else official regression fallback; normalized AST patch occurrence then earliest sample',
                'minimum_regression_failures':min_failures,'eligible_samples':[p['sample'] for p in eligible],'patch_occurrences':dict(patch_votes),'selected_sample':selected_patch['sample'] if selected_patch else None,
                'no_verified_reproduction_fallback':selected_test is None,'none_reproduction_passes_fallback':selected_test is not None and not reproduction_best,'uses_hidden':False}
        selection=env.select(final,reason);env.restore(final);record('normalized_patch_vote',{**reason,'selection':selection})
    except Exception as error:
        status=status_error(error);failure={'type':type(error).__name__,'message':str(error)};record('failure',{'status':status,'error':failure,'scientific_stages_completed':done})
        try:env.restore(final)
        except Exception as restore_error:status='ENGINEERING_UNKNOWN';record('restore_failure',{'error':str(restore_error)})
    complete=all(done.values())
    return {'method':METHOD,'status':status,'final_snapshot':final,'selection':selection,'stage_ledger':ledger,'error':failure,
            'runtime_core':{'complete':complete,'actual_stages':done,'expected_independent_patch_generations':40,'actual_patch_generations':len(patches),'actual_valid_patches':sum(bool(p['valid']) for p in patches),
                            'expected_independent_reproduction_generations':40,'actual_reproduction_generations':len(tests),'actual_verified_reproductions':sum(bool(t['verified']) for t in tests),
                            'actual_selected_reproduction_sample':selected_test['sample'] if selected_test else None,'actual_model_response_calls':len(calls),
                            'actual_candidate_regression_runs':sum('regression' in p and bool(p['regression'].get('native_record',{}).get('executed',True)) for p in patches),
                            'actual_candidate_reproduction_runs':sum('reproduction' in p for p in patches),'real_dense_retrieval_connected':done['dense_retrieval']},
            'implementation_qualification':implementation_receipt(),
            'declared_method_failure_known':status in ('MODEL_SEMANTIC_FAILURE','BUDGET_EXHAUSTED'),
            'engineering_outcome_unknown':status in ('ENGINEERING_UNKNOWN','CONTEXT_UNKNOWN','NOT_RUN'),
            'paper_main_sampling_configuration':True,'samples':'Four temp0.8 location sets; 10 patches per set: greedy + 9temp0.8; 40 reproduction tests: greedy +39temp0.8; regression from fresh legal repository passing tests and LLM exclusions; original normalization/filter/vote' ,'hidden_calls_in_adapter':0,'new_Gold':0}

def implementation_receipt():
    receipt=json.loads((E/'PAPER_CORE_SOURCE_PROVENANCE241.json').read_text('utf-8'))
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==receipt['current_core_sha256']
    return {'status':'SOURCE_ONLY_PAPER_MAIN_PENDING_NEW_ACTUAL_QUALIFICATION','official_commit':'5ce5888b9f149beaace393957a55ea8ee46c9f71','fine_location_sets':4,'patches_per_location':10,'reproduction_samples':40,'original_normalization_prompts_vote_preserved':True,'fresh_repository_passing_regression_required':True,'embedding_backend_adaptation':'local Qwen3-Embedding-0.6B instead of paper OpenAI text-embedding-3-small','old_4L4P4T_results_not_reused':True}

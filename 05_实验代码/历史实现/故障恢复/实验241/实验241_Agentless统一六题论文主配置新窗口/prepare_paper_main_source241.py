from pathlib import Path
import json,ast,hashlib,difflib
E=Path(r'D:/Code/毕设/graduate-thesis-experiments/工作区/1010-exp241-agentless-common/实验/实验241_Agentless统一六题论文主配置新窗口');AL=Path(r'D:/Code/毕设/graduate-thesis-experiments/工作区/1008-exp183-fixed12-complete-main/实验/实验183_固定十二题完整恢复与排序对照');ORIG=Path(r'D:/Code/毕设/graduate-thesis-experiments/工作区/1003-diagnosis-investigation/exp132_review/final_window_1745/agentless_primary/official_source')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,v):(E/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
old=(AL/'agentless178.py').read_text('utf-8-sig');new=old
new=new.replace('from agentless_bridge.local_core166 import structure,skeleton,context,normalized_patch','from paper_local_core241 import structure,skeleton,context,normalized_patch')
new=new.replace("METHOD='AGENTLESS_FSE2025_4L4P4T_FLASH'","METHOD='AGENTLESS_FSE2025_PAPER_MAIN_4L40P40T_FLASH_QWEN_EMBED_ADAPTED'")
new=new.replace("PROMPTS=json.loads((E/'agentless_bridge/official_prompts166.json').read_text('utf-8'))","PROMPTS=json.loads((Path("+repr(str(AL))+ ")/'agentless_bridge/official_prompts166.json').read_text('utf-8'))")
new=new.replace('four_independent_patches','forty_independent_patches').replace('four_original_reproductions','forty_original_reproductions').replace('ordinary_regression_selection','paper_repo_regression_selection')
new=new.replace("ledger=[];done={stage:False for stage in STAGES}","env.require_paper_main_current_binding()\n    ledger=[];done={stage:False for stage in STAGES}")
start=new.index('        for sample,location in enumerate(location_sets):');end=new.index("        done['forty_independent_patches']=True",start)
block=new[start:end];block=block.replace('        for sample,location in enumerate(location_sets):','        for location_id,location in enumerate(location_sets):\n            for patch_ordinal in range(10):\n                sample=patch_ordinal*4+location_id')
lines=block.splitlines();rebuilt=lines[:3]+['    '+line for line in lines[3:]]
block='\n'.join(rebuilt)+'\n';block=block.replace('temperature=0.;intervals=', 'temperature=0. if patch_ordinal==0 else .8;intervals=').replace('raw=request(\'patch\',patch_prompt,temperature,16384,sample)','raw=request(\'patch\',patch_prompt,temperature,1024,sample)').replace("'location_set':location['sample'],'temperature'", "'location_set':location['sample'],'patch_ordinal_in_location':patch_ordinal,'temperature'")
new=new[:start]+block+new[end:]
new=new.replace('enumerate((0.,.8,.8,.8))','enumerate([0.]+[.8]*39)').replace("request('reproduction',test_prompt,temperature,8192,sample)","request('reproduction',test_prompt,temperature,1024,sample)")
new=new.replace("ordinary=list(env.public_regression_nodes)","ordinary=list(env.paper_public_repository_regression_nodes)")
new=new.replace("if not ordinary:raise CoreUnavailable('NO_PREQUALIFIED_PUBLIC_ORDINARY_REGRESSION')","if not ordinary:raise CoreUnavailable('ROOT_FROZEN_LEGAL_REPOSITORY_TEST_POOL_NOT_AVAILABLE')")
new=new.replace("native_known(env.run_regression(snapshot=base,nodes=ordinary,label='agentless_original_ordinary_regression'))","native_known(env.run_paper_repository_regression(snapshot=base,nodes=ordinary,label='agentless_current_repository_passing_discovery'))")
new=new.replace("native_known(env.run_regression(snapshot=row['snapshot'],nodes=retained,label='agentless_candidate_regression_'+str(row['sample'])))","native_known(env.run_paper_repository_regression(snapshot=row['snapshot'],nodes=retained,label='agentless_candidate_regression_'+str(row['sample'])))")
new=new.replace("valid=[p for p in patches if p['valid'] and 'regression_failure_count' in p]","valid=sorted([p for p in patches if p['valid'] and 'regression_failure_count' in p],key=lambda p:p['sample'])")
new=new.replace("'expected_independent_patch_generations':4","'expected_independent_patch_generations':40").replace("'expected_independent_reproduction_generations':4","'expected_independent_reproduction_generations':40")
new=new.replace("'original_complete_core_preserved':True,'samples':'Four fine-location sets at temp0.8; one greedy patch per set; four tests: greedy plus three temp0.8; lower budget curve point than original4x10patch+40tests'","'paper_main_sampling_configuration':True,'samples':'Four temp0.8 location sets; 10 patches per set: greedy + 9temp0.8; 40 reproduction tests: greedy +39temp0.8; regression from fresh legal repository passing tests and LLM exclusions; original normalization/filter/vote' ")
new=new.replace("'source_file_sha256'", "'source_file_sha256'").replace("'skeleton_source':'AST class/function/global-variable skeleton; original libcst dependency unavailable; no oracle'","'skeleton_source':'Original libcst get_skeleton with class/module comments and fields retained; no oracle'")
pos=new.index('def implementation_receipt():')
new=new[:pos]+'''def implementation_receipt():
    receipt=json.loads((E/'PAPER_CORE_SOURCE_PROVENANCE241.json').read_text('utf-8'))
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==receipt['current_core_sha256']
    return {'status':'SOURCE_ONLY_PAPER_MAIN_PENDING_NEW_ACTUAL_QUALIFICATION','official_commit':'5ce5888b9f149beaace393957a55ea8ee46c9f71','fine_location_sets':4,'patches_per_location':10,'reproduction_samples':40,'original_normalization_prompts_vote_preserved':True,'fresh_repository_passing_regression_required':True,'embedding_backend_adaptation':'local Qwen3-Embedding-0.6B instead of paper OpenAI text-embedding-3-small','old_4L4P4T_results_not_reused':True}
'''
new=new.replace('"""Agentless FSE2025 complete-core local adaptation, four location sets, four patches/four tests under shared budget.','"""Agentless FSE2025 paper main sampling and repository passing-regression pipeline.')
ast.parse(new);(E/'agentless_paper_main241.py').write_text(new,'utf-8')
local='''"""Original CST skeleton/global locations; existing safe diff wrapper retained."""
from pathlib import Path
import importlib.util
from agentless_bridge.local_core166 import structure,context,normalized_patch
from agentless_bridge import official_core166 as official
ORIGINAL_SOURCE=Path('''+repr(str(ORIG))+''')
def load(name,rel):
 spec=importlib.util.spec_from_file_location(name,ORIGINAL_SOURCE/rel);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
_cst=load('paper_original_cst_skeleton241','agentless/util/compress_file.py')
_globals=load('paper_original_cst_globalvar241','agentless/util/parse_global_var.py')
official.parse_global_var_from_code=_globals.parse_global_var_from_code
skeleton=_cst.get_skeleton
'''
ast.parse(local);(E/'paper_local_core241.py').write_text(local,'utf-8')
newsha=sha(E/'agentless_paper_main241.py');save('PAPER_CORE_SOURCE_PROVENANCE241.json',{'schema':'Agentless241-paper-main-source-derivative/1','status':'SOURCE_ONLY_NO_EXECUTION','original_old_core':str(AL/'agentless178.py'),'original_old_core_sha256':sha(AL/'agentless178.py'),'official_commit':'5ce5888b9f149beaace393957a55ea8ee46c9f71','formal_pdf_sha256':'e780f7ccaa72815c259b3d3810e467eb9abe02f804010eded52b4babda121301','current_core_sha256':newsha,'method_fields':'4location*10patch=40;1greedy+39sample reproduction tests40','original_symbols_and_prompts_read':35,'unchanged_symbols_prompts':str(AL/'agentless_bridge/source_symbol_map166.json'),'algorithm_regression_hook':'fresh legal repository passlist -> LLM exclusion -> candidate suite, never ordinary proxy','native_test_pool_binding_currently_pending_Root':True,'CST_original_sources_sha256':{str(ORIG/r):sha(ORIG/r) for r in ('agentless/util/compress_file.py','agentless/util/parse_global_var.py')},'candidate_vote_order':'patch ordinal first then location, same official rerank _load_results interleave','actual_model_encoder_native_private_fiscal':0})
(E/'review/DIFF_FROM_OLD4L4P4T_TO_PAPER_MAIN241.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='old_adapted_4L4P4T',tofile='new_paper_main40P40T_repoRegression')),'utf-8')
print(json.dumps({'new_core':str(E/'agentless_paper_main241.py'),'sha256':newsha,'sampling40_40':True,'new_real_repository_regression_calls':True,'original_CST_skeleton':True,'AST_pass':True,'executions':0},ensure_ascii=False,separators=(',',':')))

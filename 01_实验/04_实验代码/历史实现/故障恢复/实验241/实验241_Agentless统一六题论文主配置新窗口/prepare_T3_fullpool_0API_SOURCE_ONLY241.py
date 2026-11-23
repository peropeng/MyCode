from pathlib import Path
import ast,json,hashlib,datetime
E=Path(__file__).resolve().parent;V=E/'runtime_v8_SOURCE';Q=V/'FULLPOOL_T3_5980_SOURCE_ONLY'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
def source(n,t):ast.parse(t);(Q/n).write_text(t,'utf-8')
assert not Q.exists();Q.mkdir()
entry='''"""Future ONE0API full legal public C0 passing pool; no scientific model run."""
import sys
from pathlib import Path
V=Path(__file__).resolve().parent.parent
sys.dont_write_bytecode=True;sys.path.insert(0,str(V))
import argparse,json,collections
from contracts241 import *
from environment241 import Environment241
def main():
 a=argparse.ArgumentParser()
 for n in ('protocol','grant','seal','contract'):a.add_argument('--'+n,required=True)
 a.add_argument('mode');x=a.parse_args();env=Environment241(x.protocol,x.grant,x.seal,x.contract);env.initialize()
 result={'schema':'AL241-T3-v8-full-default-legal-public-C0-pool-feasibility/1','scientific_result':False,'model_API_POSTs':0,'private':0,'fiscal_write_or_fee_CNY':0,'task_id':env.task_id,'whole_pool_required_not_ordinary_proxy':True,'qualification_only_not_science_cache':True}
 try:
  env.require_paper_main_current_binding();nodes=list(env.paper_public_repository_regression_nodes)
  expected=sorted(p for p in env.masked_scope['public_test_py_files_SHA256'] if Path(p).name.startswith('test_') or Path(p).name.endswith('_test.py'))
  if nodes!=expected or not nodes:raise EngineeringUnknown('EXACT_ALL_DEFAULT_MASKED_PUBLIC_TEST_FILES_REQUIRED')
  result.update(default_legal_test_files=nodes,default_file_count=len(nodes))
  native=env.run_paper_repository_regression(snapshot=env.initial_snapshot,nodes=nodes,label='QUALIFICATION_ONLY_FULL_C0_PASS_POOL')
  outcomes=native['outcomes'];passing=[n for n,v in outcomes.items() if str(v.get('status',v.get('outcome'))).lower() in ('passed','pass')]
  result.update(status='FULL_POOL_COMPLETE_KNOWN',known=True,raw_full_pool=native,actual_C0_PASS_pool=passing,leaf_status_counts=dict(collections.Counter(v.get('status',v.get('outcome')) for v in outcomes.values())),full_fail_error_skipped_outcomes_retained=True,private_hidden_input=False)
 except BaseException as error:
  result.update(status='FULL_POOL_UNKNOWN',known=False,error={'type':type(error).__name__,'message':str(error)},unknown=env.unknown,actual_C0_PASS_pool=None,partial_passes_not_promoted_to_full_pool=True)
 save(env.output_root/'FULLPOOL_T3_ZERO_API_RESULT241.json',result,scope=env.output_root)
if __name__=='__main__':main()
'''
source('entry_fullpool_T3_241.py',entry)
t=(V/'supervisor_runtime_v3_241.py').read_text('utf-8')
t=t.replace('import argparse,os,time','import argparse,os,time,sys\nfrom pathlib import Path\nsys.dont_write_bytecode=True\nsys.path.insert(0,str(Path(__file__).resolve().parent.parent))')
t=t.replace("str(HERE/'entry_runtime_v3_241.py'),x.mode","str(Path(__file__).resolve().parent/'entry_fullpool_T3_241.py'),x.mode")
source('supervisor_fullpool_T3_241.py',t)
p=read(V/'science_release_candidate_FALSE/getmoto__moto-5980/protocol.SOURCE_ONLY.json')
p.update(execution_authorized=False,source_only=True,native_authorized=False,model_generation_authorized=False,once_private_authorized=False,private_authorized=False,
 output_root=str(Q/'qualification_once/actor_flow'),supervision_output_root=str(Q/'qualification_once/supervision'),
 mechanical_only_delegated_Root_authority=True,scientific_generation_and_private_prohibited=True,
 qualification_full_default_public_C0_PASS_pool_only=True,model_4L40P40repro_not_run=True,no_ordinary_single_node_proxy=True,
 previously_collected_or_partial_pool_not_reused=True,qualifying_record_not_auto_science_cache=True)
save(Q/'protocol.FULLPOOL_MECHANICAL.pending.false.json',p)
g=read(V/'ROOT_MASKED_MECHANICAL_GRANT.false.template.json');g.update(task_id='getmoto__moto-5980',root_authorized=False,native_authorized=False,model_generation_authorized=False,finance_authorized=False,private_acceptance_authorized=False,once_private_evaluation_authorized=False,parent_controller_job_qualified=False,new_start_UTC=None,protocol_sha256=digest(p),protocol_raw_sha256=sha(Q/'protocol.FULLPOOL_MECHANICAL.pending.false.json'),neutral_mechanical_qualification_sha256=sha(V/'V8_ACTUAL_MASKED_IMPORT_QUALIFICATION_PASS241.json'),source_seal_sha256=None,max_wall_seconds=300,delegation_evidence='Root authorizes SOURCE-only future one T3 full public C0 pool0API qualification; actual native/finance/model/private allFALSE until independent review',one_launch_only=True)
s=read(V/'SOURCE_SEAL.json');seal={'schema':'AL241-v8-T3-fullpool-only-independent-qualification-source-seal/1','author_pin':s['author_pin'],'sources':{**s['sources'],**{str(f):sha(f) for f in Q.glob('*.py')}},'inputs':{**s['inputs'],str(Q/'protocol.FULLPOOL_MECHANICAL.pending.false.json'):sha(Q/'protocol.FULLPOOL_MECHANICAL.pending.false.json'),str(V/'V8_ACTUAL_MASKED_IMPORT_QUALIFICATION_PASS241.json'):sha(V/'V8_ACTUAL_MASKED_IMPORT_QUALIFICATION_PASS241.json')}}
save(Q/'SOURCE_SEAL_FULLPOOL_T3.json',seal);g['source_seal_sha256']=digest(seal);save(Q/'ROOT_FULLPOOL_MECHANICAL_GRANT.false.template.json',g)
cmd=[g['controller_physical_python_expected'],'-X','utf8','-B',str(Q/'supervisor_fullpool_T3_241.py'),'mechanical','--protocol',str(Q/'protocol.FULLPOOL_MECHANICAL.release.json'),'--grant',str(Q/'ROOT_FULLPOOL_MECHANICAL_GRANT.actual.json'),'--seal',str(Q/'SOURCE_SEAL_FULLPOOL_T3.json'),'--contract',p['public_contract']]
root=Path('D:/Code/毕设/graduate-thesis-experiments/工作区/1003-diagnosis-investigation/exp132_review/final_window_1745/agentless_primary/official_source')
def evidence(path,first,last):
 text=path.read_text('utf-8-sig').splitlines();return {'path':str(path),'sha256':sha(path),'lines':[{'line':i,'text':text[i-1]} for i in range(first,last+1)]}
cache={'schema':'AL241-paper-passing-tests-input-interface-SOURCE-evidence/1','official_commit':'5ce5888b9f149beaace393957a55ea8ee46c9f71','official_saved_PASS_pool_input_interface_exists':True,'official_format':{'instance_id':'task ID','tests_passing_in_original_repo':'list of actual passed selectors'},'official_pipeline':'run_regression_tests.py blank patches/apply_model_patch=False -> save_passing_tests JSONL -> select_regression_tests.py --passing_tests reads same JSONL -> LLM exclusion -> candidate regressions','source_evidence':[evidence(root/'README_swebench.md',240,264),evidence(root/'agentless/test/run_regression_tests.py',34,71),evidence(root/'agentless/test/run_regression_tests.py',188,214),evidence(root/'agentless/test/select_regression_tests.py',141,155),evidence(V/'agentless_paper_main241.py',166,175)],'current_v8_adapter_has_science_PASS_pool_cache_input':False,'current_v8_science_hook':'Unconditionally run_paper_repository_regression(snapshot=base,nodes=ordinary) at stage168; no qualification-cache loader installed','may_reuse_qualification_automatically_or_outside_science_clock':False,'same_science_clock_possible_only_with_separately_frozen_original_input_binding_and_complete_known_record':True,'conditions_if_future_Root_authorizes':['Exact same task/current C0 business SHA/support/source/protocol/physical runtime/complete collected leaf coverage and stopped trusted process','Only complete known actual PASS outcomes; failed/error/skipped remain observed and not PASS; UNKNOWN/partial pool never accepted','Original3600 scientific clock and native-root/native-time accounting must include initial full pool acquisition; do not reset clock or erase qualification costs','Pre-model single global source freeze around original --passing_tests input interface; retain LLM exclusion and all candidate regression/reproduction/votes','Root must explicitly choose and review this binding; no new cache algorithm or source patch implemented by this SOURCE task'],'no_cache_algorithm_implementation':True,'no_cache_file_generated_or_consumed_for_science':True,'no_scientific_result':True}
save(Q/'PAPER_ORIGINAL_PASS_POOL_INPUT_CACHE_SOURCE_EVIDENCE241.json',cache)
ready={'schema':'AL241-future-T3-fullpool-0API-only-SOURCE-ready/1','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'task_id':'getmoto__moto-5980','source_directory':str(Q),'existing_v8_product_source_not_modified':True,'sealed_source_digest':digest(seal),'sealed_source_rawSHA256':sha(Q/'SOURCE_SEAL_FULLPOOL_T3.json'),'new_entry_SHA256':sha(Q/'entry_fullpool_T3_241.py'),'new_supervisor_SHA256':sha(Q/'supervisor_fullpool_T3_241.py'),'all_native_model_finance_private_grants_FALSE':True,'actual_native_model_fiscal_private':0,'future_ONE_command_after_Root_new_grant_only':cmd,'actual_parent_cap':300,'actual_native_cap':90,'full_default_legal_public_files_only':True,'fullpool_complete_known_required_for_qualification_PASS':True,'normal_fail_error_skipped_retained':True,'ordinary_single_node_proxy_not_used':True,'original_full_science_4L40P40repro_candidate_regression_voting_3600_unchanged':True,'paper_original_PASS_pool_cache_source_evidence':str(Q/'PAPER_ORIGINAL_PASS_POOL_INPUT_CACHE_SOURCE_EVIDENCE241.json'),'no_automatic_cache_reuse_or_paid_expansion':True,'all_six_science_FALSE':True}
save(Q/'FULLPOOL_T3_READY_ALL_FALSE241.json',ready)
drift=[p for k in ['sources','inputs'] for p,h in seal[k].items() if sha(p)!=h];assert not drift
v8drift=[p for k in ['sources','inputs'] for p,h in s[k].items() if sha(p)!=h];assert not v8drift
print(json.dumps({'ready':str(Q/'FULLPOOL_T3_READY_ALL_FALSE241.json'),'readySHA':sha(Q/'FULLPOOL_T3_READY_ALL_FALSE241.json'),'seal_digest':digest(seal),'seal_rawSHA':sha(Q/'SOURCE_SEAL_FULLPOOL_T3.json'),'sources':len(seal['sources']),'inputs':len(seal['inputs']),'allfalse':True,'v8drift':v8drift,'official_cache_interface':True,'v8_auto_cache':False},ensure_ascii=False))
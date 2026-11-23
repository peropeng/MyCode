"""Prospective scope deployment audit packet before owned native qualification."""
import ast,datetime
from contracts241 import *
from public_v2_241 import AL
def main():
 old=HERE.parent/'实验241_Agentless新确认集21';sources={str(p):sha(p) for p in HERE.glob('*.py')}
 for p in HERE.glob('*.py'):ast.parse(p.read_text('utf-8-sig'))
 unchanged={name:sha(HERE/name)==sha(old/name) for name in ('contracts241.py','owner241.py','winjob241.py','public_v2_241.py',
  'flash_transport241.py','supervisor241.py','external_once_private241.py')}
 if not all(unchanged.values()):raise EngineeringUnknown('UNPLANNED_DEPLOYMENT_OR_AUTHOR_BOUNDARY_CHANGE')
 if sha(AL/'agentless178.py')!='6093b9aecb0f9d7801c385d2fb5f16727bd2bb51c77822b5d95329d248a4e062':raise EngineeringUnknown('AUTHOR_SHA')
 value={'schema':'Agentless241-generated-scope-v2-prospective-plan/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'write_root':str(HERE),'scope_version':2,'science_grants_false':True,'next_natural_index':2,'next_task':'getmoto__moto-5134',
  'changed_files':{'product_entry241.py':'replace experiment-directory allow root with exact trusted-file policy; install before legacy guard; preserve original native acceptance',
   'generated_scope_v2_241.py':'exact5deployment py+3existing harness py files; current source/library roots/current native out only; Python open/list/mutate hook decision logs; link/symlink refused; chmod/truncate/utime/chown by write scope; no broad E/harness root',
   'environment241.py':'classify propagated SCOPE_V2 refusal via existing EngineeringUnknown path, no author decision change',
   'prepare_confirm241.py':'versioned deployment scope and result column; same natural21, old first2 remain separate'},
  'unchanged_critical_boundaries':unchanged,'author_algorithm_sha256':sha(AL/'agentless178.py'),
  'fixed_author_parameters':'unchanged four fine samples, one greedy patch each nonempty context, four reproduction samples, original pruning/normalization/voting; no new reader',
  'all_sources':sources,'pure_fixture':str(HERE/'PURE_SCOPE_V2_241.json'),
  'owned_zero_model_mechanical_plan':[
   'Root reviews exact source packet. Prepare task Moto5134 false grant/readonly full scoped finance constructor; no API or private evaluator.',
   'Use original task ref actual product Python and frozen nodes, owned physical self identity before candidate import; reproduce C0 targetFAILordinaryPASS.',
   'Run original harmless import+Other issues generated support, require scope log begins before any allowed read and actual expected product origins.',
   'Run trusted mechanical generated scope probe: read synthetic same/other-case private, selected patch and prior response artifacts plus finance config; each must deny before open and be logged.',
   'Probe may read exact trusted contracts.py/current business __init__.py/write-read own native scratch; reject audit-log overwrite, synthetic link/symlink into out, chmod/truncate of synthetic outside artifact. No actual private contents targeted.',
   'Reconcile all permitted and denied probe events by path/write/reason, verify known synthetic bytes unchanged and every owned Job stopped. Do not read actual private contents.',
   'Preserve any first failure; at most one mechanical repair within five minutes, else version2 deployment unknown/no science. Only after root seal/grant may index2 science begin.'],
  'coverage_limit':'Audited Python entry/API and actual hook/probe/execute events; no blanket coverage of native C-layer or arbitrary malicious code',
  'old_scope1_results_seals_grants_raw_unmodified':True,'old_scope1_isolation_unknown_not_relabelled_as_no_read':True,
  'no_rerun_old_first2':True,'no_new_gold_models_or_recharge':True,'model_POST_private_ledger_writes':0}
 save(HERE/'SCOPE_V2_PROSPECTIVE_PLAN241.json',value)
 print(canonical({'scope_plan':str(HERE/'SCOPE_V2_PROSPECTIVE_PLAN241.json'),'source_count':len(sources),'all_science_grants_false':True}))
if __name__=='__main__':main()

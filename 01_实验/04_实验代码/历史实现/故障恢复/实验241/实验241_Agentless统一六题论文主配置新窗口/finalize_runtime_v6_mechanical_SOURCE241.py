"""Freeze same shared v6. No process/provider/native/finance/qualification run."""
from pathlib import Path
import ast,hashlib,json,datetime
E=Path(__file__).resolve().parent;OLD=E/'runtime_v3_SOURCE';D=E/'runtime_v6_MECHANICAL_SOURCE'
R=Path('D:/Code/毕设/graduate-thesis-experiments');W=R/'工作区/1010-unified-six'
S=R/'工作区/1009-exp239-enagent-flash-auto/实验/实验239_EnAgent_统一六题财政V3_SOURCE/shared_native_v6_SOURCE'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
expected={'native_masked_public239.py':'c9ae11202b62df8d37957ff2c54df2c3e03bbbf421a7c0169f074d2533a0a44e','guard_v6/sitecustomize.py':'ccdb46a19f1462af56459b7cd5046b1c45226decf476f2297f0d052ca7ad8cdb','guard_v6/runner.py':'69924843fd8e30ca6891ca44cebf5b69405e0c2191d17db8d0df9b4b22e29e2e'}
for rel,h in expected.items():assert sha(S/rel)==h
old_seal=read(OLD/'SOURCE_SEAL.json');external={p:h for p,h in old_seal['sources'].items() if not Path(p).is_relative_to(OLD) and 'shared_native_v' not in p}
for p,h in external.items():assert sha(p)==h
sources={str(p):sha(p) for p in D.glob('*.py')}
for p in D.glob('*.py'):ast.parse(p.read_text('utf-8-sig'))
sources.update(external);sources.update({str(S/rel):h for rel,h in expected.items()})
assert sha(D/'agentless_paper_main241.py')==sha(OLD/'agentless_paper_main241.py')
inputs=old_seal['inputs']
for p,h in inputs.items():assert sha(p)==h
seal={'schema':'Agentless241-single-mechanical-v6-current-source-seal/1','author_pin':old_seal['author_pin'],'sources':sources,'inputs':inputs,'science_and_private_authorized':False}
save(D/'SOURCE_SEAL.json',seal)
p=read(D/'protocol.MECHANICAL.pending.json')
p.update(execution_authorized=True,source_only=False,native_authorized=True,model_generation_authorized=False,
 shared_public_helper={'path':str(S/'native_masked_public239.py'),'sha256':expected['native_masked_public239.py']},
 shared_v6_SHA_pending=False,mechanical_exact_full_test_file_selection_from_shared_helper=True,
 method_and_percase_parameters_unmodified=True,only_fixed_optional_platform_observer_classified_by_Root=True)
save(D/'protocol.MECHANICAL.release.json',p)
g=read(D/'ROOT_MECHANICAL_GRANT.pending.false.json')
g.update(root_authorized=True,native_authorized=True,model_generation_authorized=False,private_acceptance_authorized=False,
 parent_controller_job_qualified=True,source_seal_sha256=digest(seal),protocol_sha256=digest(p),protocol_raw_sha256=sha(D/'protocol.MECHANICAL.release.json'),
 new_start_UTC=None,launch_authorized_only_after_Root_v6_narrow_leaf_PASS=True,
 delegation_evidence='Root task explicitly authorizes this Agent to prepare native-only mechanical grant and perform one first-task MECHANICAL_ZERO_POST <=300s; wait Root v6 PASS before launch')
save(D/'ROOT_MECHANICAL_GRANT.prepared_NOT_STARTED.json',g)
command=[g['controller_physical_python_expected'],'-X','utf8','-B',str(D/'supervisor_runtime_v3_241.py'),'mechanical',
 '--protocol',str(D/'protocol.MECHANICAL.release.json'),'--grant',str(D/'ROOT_MECHANICAL_GRANT.actual.json'),
 '--seal',str(D/'SOURCE_SEAL.json'),'--contract',p['public_contract']]
save(D/'READY_MECHANICAL_WAIT_ROOT_V6_PASS.json',{'at_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_seal_digest':digest(seal),'source_seal_rawSHA':sha(D/'SOURCE_SEAL.json'),
 'shared_v6_exact_SHA':expected,'command':command,'only_native_mechanical_grant_true_model_private_false':True,'new_start_not_set_no_run':True,
 'Root_v6_narrow_leaf_PASS_pending':True,'old_source_core_and_data_unchanged':True,'one_mechanical_launch_then_stop_no_retry':True,'actual_API_native_ledger_private':0})
print(canonical({'seal':digest(seal),'rawseal':sha(D/'SOURCE_SEAL.json'),'ready':str(D/'READY_MECHANICAL_WAIT_ROOT_V6_PASS.json'),'wait_ROOT_PASS':True,'actual_experiment_calls':0}))

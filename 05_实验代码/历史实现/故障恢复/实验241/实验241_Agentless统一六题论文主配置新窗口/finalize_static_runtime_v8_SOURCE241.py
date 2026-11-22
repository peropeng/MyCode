from pathlib import Path
import ast,json,hashlib,importlib.util,sys,datetime
E=Path(__file__).resolve().parent;D=E/'runtime_v8_SOURCE';R=Path('D:/Code/毕设/graduate-thesis-experiments');W=R/'工作区/1010-unified-six'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
p=read(D/'protocol.MASKED_MECHANICAL.pending.false.json');c=read(p['public_contract'])
script="""from tests.test_cloudfront import cloudfront_test_scaffolding as scaffold
import moto.cloudfront.models
from pathlib import Path
import json
assert callable(scaffold.example_distribution_config)
envelope=json.loads((Path(__file__).parent/'entry_envelope.json').read_text('utf-8'))
source=Path(envelope['source_root']);private=Path(envelope['frozen_root'])
negatives={
 'outside':Path("""+repr(str(E/'GENERATED_SCOPE_CONTRACT_READONLY_AUDIT241.json'))+"""),
 'unmasked_original_source':Path("""+repr(c['template'])+""")/'tests'/'__scope_negative_never_read__',
 'private_original_root':private/'__scope_negative_never_read__',
 'unmapped_actor_file':source/'tests'/'__scope_negative_never_read__',
 'VCS':source/'.git'/'HEAD',
}
for name,path in negatives.items():
 try:
  with path.open('rb'):pass
 except PermissionError:continue
 raise RuntimeError('NEGATIVE_SCOPE_CONTROL_NOT_DENIED:'+name)
try:
 with (source/'tests'/'__init__.py').open('ab'):pass
except PermissionError:pass
else:raise RuntimeError('MASKED_TEST_WRITE_MUST_BE_DENIED')
print('Other issues')
"""
ast.parse(script);(D/'masked_helper_business_DEPLOYMENT_ONLY.py').write_text(script,'utf-8')
p['single_masked_generated_script_sha256']=sha(D/'masked_helper_business_DEPLOYMENT_ONLY.py');save(D/'protocol.MASKED_MECHANICAL.pending.false.json',p)
# Static policy decision fault injection; no install/audithook/native/model.
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('_READONLY_STATIC_V8_POLICY',D/'generated_scope_v2_241.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
scope=read(W/'COMMON_MASKED_PUBLIC_TEST_SCOPE.json');row=next(t for t in scope['tasks'] if t['task_id']=='getmoto__moto-5406')
allfiles=dict(row['business_and_support_files_in_view']);allfiles.update(row['public_test_py_files_SHA256'])
business={r:allfiles[r] for r in c['c0_business_paths_sha256']};supports={r:h for r,h in allfiles.items() if r not in business};root=Path(row['public_source_repo_view']).resolve()
env={'source_root':str(root),'frozen_root':c['frozen_public_test_root'],'output':str(D/'STATIC_ONLY_NO_NATIVE_OUTPUT'),'harness':c['harness'],'dependency_paths':[],'business_SHA256':business,'masked_support_SHA256':supports}
policy=m.Policy(env,D/'product_entry241.py');cases=[]
for name,path,allowed in [('masked_package',root/'tests/__init__.py',True),('masked_helper',root/'tests/test_cloudfront/cloudfront_test_scaffolding.py',True),('business',root/'moto/cloudfront/models.py',True),('masked_directory',root/'tests/test_cloudfront',True),('outside',E/'GENERATED_SCOPE_CONTRACT_READONLY_AUDIT241.json',False),('original_unmasked',Path(c['template'])/'tests/__scope_negative_never_read__',False),('original_private',Path(c['frozen_public_test_root'])/'__scope_negative_never_read__',False),('unmapped_actor',root/'tests/__scope_negative_never_read__',False),('VCS',root/'.git/HEAD',False)]:
 actual,reason=policy.read_decision(path.resolve());assert actual is allowed,(name,actual,reason);cases.append({'name':name,'allow':actual,'reason':reason,'path':str(path)})
write=policy.write_decision(root/'tests/__init__.py');assert write[0] is False;cases.append({'name':'masked_write','allow':write[0],'reason':write[1]})
bad=dict(env);bad['masked_support_SHA256']=dict(supports);bad['masked_support_SHA256']['tests/__init__.py']='0'*64
try:m.Policy(bad,D/'product_entry241.py')
except PermissionError as exc:cases.append({'name':'manifest_SHA_fault','denied':True,'reason':str(exc)})
else:raise RuntimeError('SHA_FAULT_NOT_DETECTED')
bad=dict(env);bad['masked_support_SHA256']=dict(supports);bad['masked_support_SHA256']['../escaped']='0'*64
try:m.Policy(bad,D/'product_entry241.py')
except PermissionError as exc:cases.append({'name':'manifest_path_escape_fault','denied':True,'reason':str(exc)})
else:raise RuntimeError('PATH_FAULT_NOT_DETECTED')
audit={'schema':'AL241-v8-static-policy-fault-injection-only/1','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_checks_passed':True,'native_runs_or_product_executions':0,'API_POST_or_fiscal_or_private':0,'install_or_audithook_called':False,'unmasked_private_contents_read':False,'cases':cases,'manifest_business_count':len(business),'manifest_masked_support_count':len(supports),'future_native_negative_controls_in_sealed_script':['outside','unmasked_original_source','private_original_root','unmapped_actor_file','VCS','masked_test_write'],'model_core_unchanged':sha(D/'agentless_paper_main241.py')==sha(E/'runtime_v7_SOURCE/agentless_paper_main241.py')}
save(D/'STATIC_POLICY_FAULT_INJECTION_PASS241.json',audit)
seal=read(D/'SOURCE_SEAL.json');seal['sources'][str(D/'masked_helper_business_DEPLOYMENT_ONLY.py')]=sha(D/'masked_helper_business_DEPLOYMENT_ONLY.py');seal['inputs'][str(D/'protocol.MASKED_MECHANICAL.pending.false.json')]=sha(D/'protocol.MASKED_MECHANICAL.pending.false.json');seal['inputs'][str(D/'STATIC_POLICY_FAULT_INJECTION_PASS241.json')]=sha(D/'STATIC_POLICY_FAULT_INJECTION_PASS241.json');save(D/'SOURCE_SEAL.json',seal)
g=read(D/'ROOT_MASKED_MECHANICAL_GRANT.false.template.json');g.update(protocol_sha256=digest(p),protocol_raw_sha256=sha(D/'protocol.MASKED_MECHANICAL.pending.false.json'),source_seal_sha256=digest(seal));save(D/'ROOT_MASKED_MECHANICAL_GRANT.false.template.json',g)
for out in (D/'science_release_candidate_FALSE').iterdir():
 g=read(out/'ROOT_SCIENCE_GRANT.false.template.json');g['source_seal_sha256']=digest(seal);save(out/'ROOT_SCIENCE_GRANT.false.template.json',g)
ready=read(D/'SOURCE_READY_ALL_FALSE241.json');ready.update(source_seal_digest=digest(seal),source_seal_raw_sha256=sha(D/'SOURCE_SEAL.json'),static_policy_fault_injection_PASS_SHA256=sha(D/'STATIC_POLICY_FAULT_INJECTION_PASS241.json'),exact_current_manifests_required_for_generated_modes=['generated','generated_pytest','coverage','flake8'],native_future_script_SHA256=sha(D/'masked_helper_business_DEPLOYMENT_ONLY.py'),native_negative_controls_still_false=True)
save(D/'SOURCE_READY_ALL_FALSE241.json',ready);print(json.dumps({'ready':str(D/'SOURCE_READY_ALL_FALSE241.json'),'seal_digest':digest(seal),'seal_rawSHA':sha(D/'SOURCE_SEAL.json'),'static_checks':len(cases),'all_PASS':True,'native_API_private_ledger':0,'all_grants_false':True,'UTC':audit['UTC']},ensure_ascii=False))
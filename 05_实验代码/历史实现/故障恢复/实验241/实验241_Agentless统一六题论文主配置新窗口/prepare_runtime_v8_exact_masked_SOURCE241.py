from pathlib import Path
import ast,hashlib,json,copy,datetime,importlib.util,sys
E=Path(__file__).resolve().parent;O=E/'runtime_v7_SOURCE';D=E/'runtime_v8_SOURCE'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
def source(n,t):ast.parse(t);(D/n).write_text(t,'utf-8')
assert not D.exists();D.mkdir()
for f in O.glob('*.py'):source(f.name,f.read_text('utf-8-sig'))
save(D/'PAPER_CORE_SOURCE_PROVENANCE241.json',read(O/'PAPER_CORE_SOURCE_PROVENANCE241.json'))
t=(D/'owner241.py').read_text('utf-8')
a="        save(envelope,{'mode':mode,'argv_tail':argv[1:]"
b="""        current_business={};current_support={}
        if mode in ('generated','generated_pytest','coverage','flake8'):
            current_business=self.actor_business_inventory()
            current_support=dict(self.masked_supports)
            self.shared_public.verify_actor(self.repo_root,current_business,current_support)
            if any(sha(self.repo_root/rel)!=h for rel,h in current_business.items()):
                raise EngineeringUnknown('CURRENT_GENERATED_BUSINESS_BINDING_DRIFT')
        save(envelope,{'task_id':self.task_id,'business_SHA256':current_business,
                       'masked_support_SHA256':current_support,
                       'scope_contract_SHA256':self.protocol['public_test_scope_contract']['sha256'],
                       'mode':mode,'argv_tail':argv[1:]"""
assert t.count(a)==1;t=t.replace(a,b);source('owner241.py',t)
t=(D/'generated_scope_v2_241.py').read_text('utf-8').replace('import json,os,sys,threading','import json,os,sys,threading,hashlib')
a="  self.library_roots={Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve()}"
b="""  business=envelope.get('business_SHA256');supports=envelope.get('masked_support_SHA256')
  if not isinstance(business,dict) or not business or not isinstance(supports,dict) or not supports:
   raise PermissionError('SCOPE_V8_EXACT_CURRENT_BUSINESS_AND_MASKED_SUPPORT_REQUIRED')
  if set(business)&set(supports):raise PermissionError('SCOPE_V8_OVERLAPPING_MANIFESTS')
  self.allowed_files={};self.allowed_directories={self.source}
  for rel,expected in {**business,**supports}.items():
   rp=Path(rel)
   if not isinstance(rel,str) or rp.is_absolute() or '..' in rp.parts or '.git' in rp.parts or ':' in rel or '\\\\' in rel:
    raise PermissionError('SCOPE_V8_ILLEGAL_MANIFEST_PATH')
   path=(self.source/rp).resolve()
   if not inside(path,self.source) or path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
    raise PermissionError('SCOPE_V8_CURRENT_MANIFEST_FILE_DRIFT')
   self.allowed_files[path]=expected
   parent=path.parent
   while inside(parent,self.source):
    self.allowed_directories.add(parent)
    if parent==self.source:break
    parent=parent.parent
  self.library_roots={Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve()}"""
assert t.count(a)==1;t=t.replace(a,b)
a="""  if inside(path,self.source):
   if set(path.relative_to(self.source).parts)&{'test','tests','test-data','.git'}:return False,'SOURCE_TEST_OR_VCS_READ'
   return True,'CURRENT_BUSINESS_SOURCE'"""
b="""  if inside(path,self.source):
   if '.git' in path.relative_to(self.source).parts:return False,'SOURCE_VCS_READ'
   if path in self.allowed_files or path in self.allowed_directories:return True,'CURRENT_BUSINESS_OR_IMMUTABLE_MASKED_PUBLIC_VIEW'
   return False,'UNDECLARED_ACTOR_FILE_OR_GIT_BLOB'"""
assert t.count(a)==1;t=t.replace(a,b);source('generated_scope_v2_241.py',t)
entry='''"""Future one0API masked helper/business deployment qualification only."""
import argparse,json
from contracts241 import *
from environment241 import Environment241
def main():
 a=argparse.ArgumentParser()
 for n in ('protocol','grant','seal','contract'):a.add_argument('--'+n,required=True)
 a.add_argument('mode');x=a.parse_args();env=Environment241(x.protocol,x.grant,x.seal,x.contract);env.initialize()
 script=env.protocol['single_masked_generated_script'];assert sha(script)==env.protocol['single_masked_generated_script_sha256']
 result={'schema':'AL241-v8-exact-masked-generated-import-mechanical/1','API_POSTs':0,'private':0,'fee_CNY':'0','scientific_result':False}
 try:
  raw=env.run_reproduction(Path(script).read_text('utf-8'),env.initial_snapshot,'V8_MASKED_HELPER_DEPLOYMENT_ONLY')
  result.update(status='KNOWN_DEPLOYMENT_NATIVE_EXECUTED',raw_native=raw,actual_product_identity=raw['native_record'].get('actual_product_python_identity'))
 except BaseException as error:result.update(status='DEPLOYMENT_UNKNOWN',error={'type':type(error).__name__,'message':str(error)})
 save(env.output_root/'V8_MASKED_IMPORT_MECHANICAL_RESULT.json',result,scope=env.output_root)
if __name__=='__main__':main()
'''
source('entry_masked_v8_241.py',entry)
source('supervisor_masked_v8_241.py',(D/'supervisor_runtime_v3_241.py').read_text('utf-8').replace("str(HERE/'entry_runtime_v3_241.py'),x.mode","str(HERE/'entry_masked_v8_241.py'),x.mode"))
# Script references only approved masked helper/package and public business module.
script="""from tests.test_cloudfront import cloudfront_test_scaffolding as scaffold
import moto.cloudfront.models
assert callable(scaffold.example_distribution_config)
print('Other issues')
"""
(D/'masked_helper_business_DEPLOYMENT_ONLY.py').write_text(script,'utf-8')
oldseal=read(O/'SOURCE_SEAL.json');inputs=dict(oldseal['inputs'])
oldscript=read(O/'protocol.STARTUP_MECHANICAL.release.json')['single_public_generated_script'];inputs.pop(oldscript,None)
params=[];commands={}
for task in read(O/'science_release_candidate_FALSE/getmoto__moto-6387/protocol.SOURCE_ONLY.json')['task_order']:
 p=read(O/'science_release_candidate_FALSE'/task/'protocol.SOURCE_ONLY.json')
 p.update(core_source=str(D/'agentless_paper_main241.py'),masked_native_owner_root=str(D),output_root=str(D/'science_once_six'/task/'actor_flow'),supervision_output_root=str(D/'science_once_six'/task/'supervision'),execution_authorized=False,source_only=True,native_authorized=False,model_generation_authorized=False,once_private_authorized=False,private_authorized=False,generated_scope_exact_business_and_masked_support=True,old_science_T1_T2_not_retried_or_continued=True,full_pool_zero_API_qualification_required_before_future_paid=True)
 out=D/'science_release_candidate_FALSE'/task;save(out/'protocol.SOURCE_ONLY.json',p);inputs[str(out/'protocol.SOURCE_ONLY.json')]=sha(out/'protocol.SOURCE_ONLY.json');params.append((task,p,out))
p=copy.deepcopy(params[0][1]);p.update(output_root=str(D/'single_masked_import_qualification5406/actor_flow'),supervision_output_root=str(D/'single_masked_import_qualification5406/supervision'),single_masked_generated_script=str(D/'masked_helper_business_DEPLOYMENT_ONLY.py'),single_masked_generated_script_sha256=sha(D/'masked_helper_business_DEPLOYMENT_ONLY.py'))
save(D/'protocol.MASKED_MECHANICAL.pending.false.json',p);inputs[str(D/'protocol.MASKED_MECHANICAL.pending.false.json')]=sha(D/'protocol.MASKED_MECHANICAL.pending.false.json')
seal={'schema':'AL241-v8-exact-current-masked-generated-source-only-seal/1','author_pin':oldseal['author_pin'],'sources':{str(f):sha(f) for f in D.glob('*.py')},'inputs':inputs}
seal['sources'].update({p:h for p,h in oldseal['sources'].items() if not Path(p).is_relative_to(O)});save(D/'SOURCE_SEAL.json',seal)
g=read(O/'ROOT_STARTUP_MECHANICAL_GRANT.actual.json');g.update(root_authorized=False,native_authorized=False,model_generation_authorized=False,private_acceptance_authorized=False,new_start_UTC=None,parent_controller_job_qualified=False,protocol_sha256=digest(p),protocol_raw_sha256=sha(D/'protocol.MASKED_MECHANICAL.pending.false.json'),source_seal_sha256=digest(seal),delegation_evidence='Root authorizes only future global SOURCE correction/staticfaultinjection; actual native qualification remains false until new Root grant',neutral_mechanical_qualification_sha256=None)
save(D/'ROOT_MASKED_MECHANICAL_GRANT.false.template.json',g)
for task,p,out in params:
 q=read(O/'science_release_candidate_FALSE'/task/'ROOT_SCIENCE_GRANT.false.template.json');q.update(root_authorized=False,native_authorized=False,model_generation_authorized=False,private_acceptance_authorized=False,new_start_UTC=None,source_seal_sha256=digest(seal),protocol_sha256=digest(p),protocol_raw_sha256=sha(out/'protocol.SOURCE_ONLY.json'),neutral_mechanical_qualification_sha256=None,Root_v8_actual_masked_and_full_pool_acceptance_pending=True)
 save(out/'ROOT_SCIENCE_GRANT.false.template.json',q)
assert sha(D/'agentless_paper_main241.py')==sha(O/'agentless_paper_main241.py')
ready={'schema':'AL241-v8-future-source-ready-all-false/1','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_seal_digest':digest(seal),'source_seal_raw_sha256':sha(D/'SOURCE_SEAL.json'),'single_source_for_all_six':True,'source_changes_only':['owner241.py exactcurrentbusiness+maskedSupport envelope','generated_scope_v2_241.py exactmanifest whitelist instead of blanket tests denial'],'core4L40P40repro_votes_caps_same_sha':sha(D/'agentless_paper_main241.py'),'actual_model_native_ledger_private':0,'all_grants_false':True,'prior_live_PP_EA_shared_v6_and_AL_v7_unchanged':True,'one_future_zero_API_mechanical_candidate_FALSE':[g['controller_physical_python_expected'],'-X','utf8','-B',str(D/'supervisor_masked_v8_241.py'),'mechanical','--protocol',str(D/'protocol.MASKED_MECHANICAL.release.json'),'--grant',str(D/'ROOT_MASKED_MECHANICAL_GRANT.actual.json'),'--seal',str(D/'SOURCE_SEAL.json'),'--contract',p['public_contract']],'full_pool_0API_required_before_paid':True}
# Ensure candidate contract matches5406, not last science loop task.
ready['one_future_zero_API_mechanical_candidate_FALSE'][-1]=params[0][1]['public_contract']
save(D/'SOURCE_READY_ALL_FALSE241.json',ready);print(json.dumps(ready,ensure_ascii=False))
"""Pure path decisions; no native/model/private execution."""
from contracts241 import *
from generated_scope_v2_241 import Policy
TASK='getmoto__moto-5134'
def main():
 c=read(HERE/'candidate'/TASK/'public_contract.json');out=HERE/'pure_scope_native_output'
 source=HERE/'pure_scope_business/repo'
 env={'source_root':str(source),'frozen_root':c['frozen_public_test_root'],'output':str(out),
  'harness':c['harness'],'dependency_paths':[]}
 policy=Policy(env,HERE/'product_entry241.py',site_paths=[])
 rows=[]
 checks=[('current_output_read',out/'generated_test.py',True,False),('current_output_write',out/'created.txt',True,True),
  ('exact_trusted_entry',HERE/'product_entry241.py',True,False),
  ('trusted_scope_helper',HERE/'generated_scope_v2_241.py',True,False),
  ('trusted_file_write_forbidden',HERE/'contracts241.py',False,True),
  ('experiment_root_forbidden',HERE,False,False),('finance_json_forbidden',HERE/'finance_config241.json',False,False),
  ('same_case_private_forbidden',HERE/'runs'/TASK/METHOD/'external_once_private/result.json',False,False),
  ('other_case_private_forbidden',HERE/'runs/dask__dask-9378'/METHOD/'external_once_private/result.json',False,False),
  ('previous_selected_patch_forbidden',HERE.parent/'实验241_Agentless新确认集21/runs/dask__dask-9378'/METHOD/'immutable_selection/dask/__init__.py',False,False),
  ('previous_response_forbidden',HERE/'runs'/TASK/METHOD/'llm/response.json',False,False),
  ('untrusted_experiment_py_forbidden',HERE/'packet_case241.py',False,False),
  ('frozen_test_forbidden',Path(c['frozen_public_test_root'])/'tests/test_scope.txt',False,False),
  ('business_source_read',source/'moto/__init__.py',True,False),('business_source_write_forbidden',source/'moto/__init__.py',False,True),
  ('business_test_read_forbidden',source/'moto/tests/test_scope.py',False,False),
  ('audit_log_write_forbidden',out/'generated_scope_events.jsonl',False,True)]
 for name,p,expected,write in checks:
  p=p.resolve();actual,reason=policy.write_decision(p) if write else policy.read_decision(p)
  rows.append({'case':name,'path':str(p),'write':write,'expected':expected,'actual':actual,'reason':reason})
  if actual!=expected:raise EngineeringUnknown('PURE_SCOPE_DECISION_FAILED '+name)
 for event,path,expected in [('os.link',out/'link_destination.txt',False),('os.symlink',out/'symlink_destination.txt',False),
  ('os.chmod',HERE/'finance_config241.json',False),('os.truncate',HERE/'finance_config241.json',False),
  ('os.chmod',out/'scratch.txt',True),('os.truncate',out/'scratch.txt',True)]:
  actual,reason=policy.mutation_decision(event,path.resolve())
  rows.append({'case':event,'path':str(path),'expected':expected,'actual':actual,'reason':reason})
  if actual!=expected:raise EngineeringUnknown('PURE_SCOPE_MUTATION_FAILED '+event)
 save(HERE/'PURE_SCOPE_V2_241.json',{'scope_version':2,'status':'PURE_DECISIONS_PASS_NOT_NATIVE_QUALIFICATION','cases':rows,
  'policy_sha256':sha(HERE/'generated_scope_v2_241.py'),'POST_private_native_roots':0,
  'actual_native_mechanical_still_required':True})
 print(canonical({'pure_scope':'PASS','cases':len(rows),'native_model_private':0}))
if __name__=='__main__':main()

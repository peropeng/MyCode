"""New natural cohort, unchanged author core, public metadata only; no POST."""
import datetime,sys
sys.dont_write_bytecode=True
from contracts241 import *
PILOT=HERE.parent/'实验241_Agentless严格V2完整共同恢复'
PROSPECTIVE=ROOT/'结论/20261009_复盘再实验/新确认集与共同预算_前瞻.json'

def main():
 if (HERE/'PREPARED241.json').exists():raise EngineeringUnknown('PREPARE_ONCE')
 cohort=read(PROSPECTIVE);tasks=cohort['new_main_order']
 original=read(PILOT/'candidate/Project-MONAI__MONAI-2238/protocol.json')
 inherited=read(PILOT/'candidate/Project-MONAI__MONAI-2238/source_seal.json')['sources']
 sources={p:sha(p) for p in inherited if not inside(p,PILOT) and not any(inside(p,d) for d in original['product_dependency_paths'])}
 for p in HERE.glob('*.py'):sources[str(p)]=sha(p)
 copied={str(PILOT/p.name):sha(PILOT/p.name) for p in HERE.glob('*.py') if (PILOT/p.name).is_file()}
 for index,task in enumerate(tasks):
  base=HERE/'candidate'/task;c=prepare_public_contract(task,base/'public_contract.json')
  p={k:v for k,v in original.items() if k not in ('mechanical241','first_request_bound','first_body_sha256',
   'mechanical_only_actual_runtime_PASS','root_release_authority','dual_native_counter_fixture')}
  p.update(schema='Agentless241-new-natural-confirmation-protocol/1',task_id=task,finance_phase=FINANCE_PHASE,
   results_column='AGENTLESS_FSE2025_NEW_CONFIRM21_SCOPEV2_241',execution_authorized=False,prepared_only=True,
   root_release_utc=None,output_root=str(HERE/'runs'/task/METHOD),supervision_output_root=str(HERE/'supervision'/task),
   public_contract=str(base/'public_contract.json'),finance_config=str(HERE/'finance_config241.json'),
   shared_transport=str(HERE/'flash_transport241.py'),product_dependency_paths=[],declared_shared_phase_cap_CNY='1.50',
   selection_order=tasks,cohort_name=cohort['new_cohort_name'],natural_index=index,
   pilot_results_not_merged=True,old_Main21_not_merged=True,prospective_protocol=str(PROSPECTIVE),
   prospective_protocol_sha256=sha(PROSPECTIVE),qualification='fresh owned per-task C0 plus generated scope v2 probes; root release per natural index',
   generated_scope_version=2,generated_scope_source=str(HERE/'generated_scope_v2_241.py'),
   old_scope1_results_never_replaced_or_rerun=True)
  save(base/'protocol.json',p)
  inputs={str(base/'protocol.json'):sha(base/'protocol.json'),str(base/'public_contract.json'):sha(base/'public_contract.json'),
   p['root_protocol']:p['root_protocol_sha256'],c['registry']:c['registry_sha256'],c['pack']:c['pack_sha256'],
   c['source_inventory_reference']:c['source_inventory_reference_sha256'],str(PROSPECTIVE):sha(PROSPECTIVE),
   str(HERE/'AUTHOR_SOURCE_MANIFEST241.json'):sha(HERE/'AUTHOR_SOURCE_MANIFEST241.json'),
   str(HERE/'finance_config241.json'):sha(HERE/'finance_config241.json')}
  task_sources=dict(sources);task_sources.update(c['harness_sources'])
  product_venv=Path(c['logical_product_python']).parent.parent
  for f in [product_venv/'pyvenv.cfg',Path(c['logical_product_python']),*list((product_venv/'Lib/site-packages').glob('*.pth'))]:
   if f.is_file():task_sources[str(f)]=sha(f)
  save(base/'source_seal.json',{'schema':'Agentless241-source-input-seal/1','author_pin':SOURCE_PIN,
   'sources':task_sources,'inputs':inputs,'prepared_only':True})
  save(base/'root_grant.template.json',{'schema':'Agentless241-root-grant/1','root_authorized':False,'model_generation_authorized':False,
   'task_id':task,'finance_phase':FINANCE_PHASE,'registry_sha256':REGISTRY_SHA,'protocol_sha256':digest(p),
   'protocol_raw_sha256':sha(base/'protocol.json'),'source_seal_sha256':digest(read(base/'source_seal.json')),
   'neutral_mechanical_qualification_sha256':None,'neutral_parent_stop_sha256':None,
   'parent_controller_job_qualified':False,'controller_physical_python_expected':None,'product_physical_python_expected':None,
   'once_private_evaluation_authorized':False,'qualification_only':True})
 save(HERE/'PREPARED241.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tasks':tasks,
  'phase':FINANCE_PHASE,'pilot_readonly':True,'source_copy_provenance':copied,'all_science_grants_false':True,
  'removed_unused_generic_CP312_product_dependencies':True,'POST_private_ledger_write':0})
 print(canonical({'prepared':len(tasks),'first':tasks[0],'science_grants_false':True}))
if __name__=='__main__':main()

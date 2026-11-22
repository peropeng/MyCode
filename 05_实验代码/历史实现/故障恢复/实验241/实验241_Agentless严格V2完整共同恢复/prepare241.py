"""Prepare the independent 241 facade and the unchanged author method inputs."""
import ast,datetime,hashlib,json,shutil,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
PP=ROOT/'工作区/1009-exp227-patchpilot-full/实验/实验238_晚间Flash完整PatchPilot两题小试'
AL=ROOT/'工作区/1008-exp183-fixed12-complete-main/实验/实验183_固定十二题完整恢复与排序对照'
SOURCE224=ROOT/'工作区/1008-2320-exp224-flash-common/实验/实验224_二十三题Flash完整共同恢复比较'
TASKS=['Project-MONAI__MONAI-2238','Project-MONAI__MONAI-5093']
PIN='5ce5888b9f149beaace393957a55ea8ee46c9f71'
PHASE='AgentlessPilot24120261010';METHOD='AGENTLESS_FSE2025_4L4P4T_FLASH'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
 p=Path(p);p.resolve().relative_to(HERE);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
def put(p,s):(HERE/p).write_bytes(s.encode('utf-8'))
def main():
 if (HERE/'PREPARED241.json').exists():raise RuntimeError('PREPARE_ONCE')
 renames={'contracts_pp.py':'contracts241.py','owner_pp.py':'owner241.py','winjob_pp.py':'winjob241.py',
  'product_entry_pp.py':'product_entry241.py','physical_self_probe_pp.py':'physical_self_probe241.py',
  'scoped_finance_artifacts_pp.py':'scoped_finance_artifacts241.py','bounded_atomic_retry227.py':'bounded_atomic_retry241.py',
  'shared_json_read_pp.py':'shared_json_read241.py','supervision_classification_new230.py':'supervision_classification241.py'}
 provenance={}
 for old,new in renames.items():
  p=PP/old;provenance[str(p)]=sha(p);s=p.read_text('utf-8-sig')
  for a,b in renames.items():s=s.replace(a,b).replace(a.removesuffix('.py'),b.removesuffix('.py'))
  s=s.replace('PATCHPILOT_FLASH_EVENING238',METHOD).replace('PatchPilotEvening23820261009',PHASE)
  s=s.replace('PatchPilotEvening238-root-grant/1','Agentless241-root-grant/1')
  s=s.replace('84ec3d3fbc34269078f9f9b62b9d390947344944',PIN)
  if old=='owner_pp.py':
   s=s.split('    async def async_flash_request',1)[0]
   s=s.replace("any('patchpilot' in x.lower()", "any('agentless' in x.lower()")
  put(new,s)
 # Snapshot/regression facade does not import any PatchPilot author algorithm.
 core_paths=[AL/'agentless178.py',AL/'agentless_source_derivative178.json',AL/'agentless_bridge/official_core166.py',
  AL/'agentless_bridge/local_core166.py',AL/'agentless_bridge/dense166.py',AL/'agentless_bridge/official_prompts166.json',
  SOURCE224/'retrieval178.py',SOURCE224/'environment_v2_224.py',SOURCE224/'publicpack_v2_224.py',
  SOURCE224/'shared_projection224.py',AL/'audit183/new_public_contract_preflight.py',
  ROOT/'工作区/0922-exp124-ranking-baselines/third_party/StepFinder/Q3Emb.py']
 save(HERE/'AUTHOR_SOURCE_MANIFEST241.json',{'official_pin':PIN,'method_sha256':sha(AL/'agentless178.py'),
  'sources':{str(p):sha(p) for p in core_paths},'unchanged_4L4P4T':True,'no_PatchPilot_author_core_imported':True,
  'method':'FSE2025 Agentless unchanged source derivative from strict224 V2; original40P40T not claimed'})
 inherited=read(PP/'candidate_absolute_v2'/TASKS[0]/'source_seal.json')['sources']
 shared={p:h for p,h in inherited.items() if not Path(p).is_relative_to(PP) and 'original' not in Path(p).parts}
 shared.update({str(p):sha(p) for p in core_paths})
 for task in TASKS:
  base=HERE/'candidate'/task;c=read(PP/'candidate_absolute_v2'/task/'public_contract.json');c['source_pin']=PIN;c['physical_product_python_expected']=None
  save(base/'public_contract.json',c);p=read(PP/'candidate_absolute_v2'/task/'protocol.json')
  for key in ['author_parameters','mechanical238','previous_launch_unknown_preserved','previous_launch_failure','only_mechanical_change','mechanical_fix_limit','fresh_actual_body_bounds','first_body_path','first_body_sha256','reused_actual_public_mechanical']:
   p.pop(key,None)
  p.update(schema='Agentless241-independent-strictV2-prospective-protocol/1',experiment=241,method=METHOD,results_column='AGENTLESS_FSE2025_V2_RESUME241',
   source_pin=PIN,finance_phase=PHASE,execution_authorized=False,prepared_only=True,root_release_utc=None,
   output_root=str(HERE/'runs'/task/METHOD),supervision_output_root=str(HERE/'supervision'/task),
   public_contract=str(base/'public_contract.json'),shared_transport=str(HERE/'flash_transport241.py'),finance_config=str(HERE/'finance_config241.json'),
   declared_shared_phase_cap_CNY='0.50',qualification='fresh actual 241 mechanical required; historically exposed tasks; old224 results remain separate',
   original_sources_readonly=str(AL),model_resource={'model':'deepseek-flash','thinking':{'type':'disabled'},'context_limit':1048576,
    'original_decoder':'Exact strict224 body_v2 and author current request last; plain text no added reader selfloop','forced_tool_call':False,'transport_retry':False},
   author_core={'fine_location_sets':4,'patches_per_location':1,'reproduction_tests':4,'fine_temperature':0.8,'patch_temperature':0.0,
    'reproduction_temperatures':[0.0,0.8,0.8,0.8],'original_parser_prompts_vote_normalization_retained':True},
   original_all_OS_roots_budget_definition='90 all owned controller/product/helper roots, private evaluator and final product roots included',
   deadline={'no_new_utc':'2026-10-10T03:40:00Z','hard_utc':'2026-10-10T04:00:00Z'})
  save(base/'protocol.json',p)
  save(base/'root_grant.template.json',{'schema':'Agentless241-root-grant/1','root_authorized':False,'model_generation_authorized':False,
   'task_id':task,'finance_phase':PHASE,'registry_sha256':p['registry_sha256'],'protocol_sha256':None,'protocol_raw_sha256':sha(base/'protocol.json'),
   'source_seal_sha256':None,'neutral_mechanical_qualification_sha256':None,'neutral_parent_stop_sha256':None,
   'parent_controller_job_qualified':False,'controller_physical_python_expected':None,'product_physical_python_expected':None,
   'once_private_evaluation_authorized':False,'qualification_only':True})
  inputs={str(base/'protocol.json'):sha(base/'protocol.json'),str(base/'public_contract.json'):sha(base/'public_contract.json'),
   p['root_protocol']:p['root_protocol_sha256'],c['registry']:c['registry_sha256'],c['pack']:c['pack_sha256'],
   c['source_inventory_reference']:c['source_inventory_reference_sha256'],str(HERE/'AUTHOR_SOURCE_MANIFEST241.json'):sha(HERE/'AUTHOR_SOURCE_MANIFEST241.json')}
  save(base/'source_seal.json',{'schema':'Agentless241-source-input-seal/1','author_pin':PIN,'sources':shared,'inputs':inputs,'prepared_only':True})
 save(HERE/'PREPARED241.json',{'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tasks':TASKS,'source_copy_provenance':provenance,
  'author_core_manifest':str(HERE/'AUTHOR_SOURCE_MANIFEST241.json'),'no_generation_native_private_ledger_write':True})
 print(json.dumps({'prepared':str(HERE),'author_original_files':len(core_paths),'generation':0}))
if __name__=='__main__':main()

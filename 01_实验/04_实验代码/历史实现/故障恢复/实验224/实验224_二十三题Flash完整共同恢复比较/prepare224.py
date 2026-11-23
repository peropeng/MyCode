"""Normalize23 public C0 contracts without generation, native, or new Gold."""
from common166 import *
import copy,shutil
SOURCE=READINESS/'new_public_contract_preflight/expanded_observed_failure23_manifest.json'
G191=ROOT/'工作区/1008-exp191-public-rank-output-interface/实验/实验191_十五题公开排序与约束输出接口资格/ranking/plans'
COHORT=ROOT/'工作区/1003-diagnosis-investigation/exp132_review/new_window_2332/exp189_exact_existing_public_cohort.json'
def inventory(root):
 ignore={'.git','__pycache__','.pytest_cache','.mypy_cache','.hypothesis'}
 return {p.relative_to(root).as_posix():sha(p) for p in sorted(Path(root).rglob('*')) if p.is_file() and not ignore.intersection(p.parts)}
def main():
 source=read(SOURCE);cohort={r['task_id']:r for r in read(COHORT)['cohort']};run=load_replay();rows=[];samples=[];g=[]
 for spec in source['tasks']:
  tid=spec['task_id'];ref=copy.deepcopy(spec['binding']);stratum='original_issue_continuation' if spec['new_runner_normalization_needed'] else 'agent_induced_regression'
  if spec['new_runner_normalization_needed']:
   task=E/'normalized_tasks'/tid;old_task=Path(ref['task_path']);prefix=read(old_task/'visible/source_prefix.json');edits=read(old_task/'visible/edits.json')
   prefix['new_failure_observation']={'origin':'Exp224 wider observed failure contract; archived healthy public native, original selected tests unchanged','visible_target_feedback':spec['terminal_native_public_proof']['observed_failed'],'native_public_proof_sha256':spec['terminal_native_public_proof']['probe_sha256']}
   save(task/'visible/source_prefix.json',prefix);save(task/'visible/edits.json',edits)
   original=cohort[tid]['binding'];mf={'schema':'Exp224-public-observed-failure-task/1','task_id':tid,'repository':tid.rsplit('-',1)[0].replace('__','/'),'package':ref['package'],
    'checkpoint':{k:original[k] for k in ('source_repo','base_commit','base_tree')},'asset_root':ref['asset_root'],'runtime_source_root':ref['template'],'native_interpreter':ref['python'],
    'frozen_tests':{'path':ref['frozen_tests'],'inventory':'frozen_test_inventory.json'},'visible_target_tests':spec['public_goal_nodes'],'public_regression_tests':spec['public_ordinary_nodes'],
    'hidden_preservation_tests':spec['future_preservation_nodes'],'target_failure_modes':{n:'native_test_failed' for n in spec['public_goal_nodes']},
    'qualification_preceding_pass_evidence':spec['terminal_native_public_proof']['observed_passed'],'failure_prefix':{'message_index':spec['cutoff'],'source_prefix':'visible/source_prefix.json'},'official_reference_patch_used':False,'parameter_codec':'RAW-json.loads-no-transformation/1',
    'wider_original_issue_continuation_contract':True,'archived_original_native_result':spec['terminal_native_public_proof']['probe'],'stratum':stratum}
   save(task/'task_manifest.json',mf);inv=inventory(Path(ref['template']));finv=inventory(Path(ref['frozen_tests']));save(task/'source_inventory.json',{'template':inv,'frozen_tests':finv});save(task/'frozen_test_inventory.json',finv)
   ref.update(task_path=str(task),saved_source_inventory=str(task/'source_inventory.json'),binding_kind='Exp166_qualified_state',source_round='Exp224_existing_original_issue_failure')
   sample=run.export_input(task);mapping=[{'step':i,'message_index':t['source_message_index'],'successful_edit_ids':[e['call_id'] for e in edits if e['message_index']==t['source_message_index']]} for i,t in enumerate(sample['turns'])]
   run.qualify=run.module('exp224_original_qualify_'+tid.replace('-','_'),Path(ref['harness'])/'qualify.py')
   core=run.load_core(ref['asset_root'],ref['package']);graph=core.provenance(edits);plans,invalid,business=core.candidate_plans(list(range(len(mapping)-1,-1,-1)),mapping,edits,graph)
   ref.update(mapping=mapping,dependency_graph=graph,candidate_pool=len(plans),business_edits=len(business),steps=len(mapping),invalid_roots=invalid,
    input_digest=digest(sample),input_turns_sha256=hashlib.sha256(json.dumps(sample['turns'],sort_keys=True).encode()).hexdigest(),candidate_budget=9,public_regression_nodes=spec['public_ordinary_nodes'],
    copy_estimate={'bytes':sum((Path(ref['template'])/p).stat().st_size for p in inv),'files':len(inv)})
   seals={str(task/n):sha(task/n) for n in ('task_manifest.json','visible/source_prefix.json','visible/edits.json','source_inventory.json','frozen_test_inventory.json')}
   for p in Path(ref['harness']).glob('*.py'):seals[str(p)]=sha(p)
   save(task/'READY224.json',{'status':'READY','schema':'Exp224-existing-public-C0-metadata-seal/1','sha256':seals,'new_native_runs':0,'original_public_native_healthy':True,'current_source_sha_reverified_before_normalization':True})
   ref.update(binding_seal=str(task/'READY224.json'),ready_sha256=sha(task/'READY224.json'))
  else:
   assert sha(ref['binding_seal'])==ref['ready_sha256'];sample=run.export_input(Path(ref['task_path']))
   old_digest=hashlib.sha256(json.dumps(sample,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
   prior_projection={k:v for k,v in sample.items() if k not in ('public_regression_tests','public_regression_initially_passed')}
   prior_digest=hashlib.sha256(json.dumps(prior_projection,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
   assert ref['input_digest'] in (digest(sample),old_digest,prior_digest),'EXISTING_PUBLIC_INPUT_DRIFT '+tid
   ref['original_qualification_input_digest']=ref['input_digest'];ref['input_digest']=digest(sample)
  assert set(spec['public_goal_nodes']).isdisjoint(spec['public_ordinary_nodes'])
  mf=read(Path(ref['task_path'])/'task_manifest.json');assert set(mf['visible_target_tests'])==set(spec['public_goal_nodes']);assert set(mf['public_regression_tests'])==set(spec['public_ordinary_nodes'])
  ref.update(stratum=stratum,candidate_budget=9,public_regression_nodes=spec['public_ordinary_nodes'],retrieval_cache=str(E/'retrieval'))
  p=G191/tid/'OURS_G153_VBR.json'
  if p.exists():
   plan=read(p);assert plan['input_turns_sha256']==ref['input_turns_sha256'];assert sorted(plan['complete_original_ordinal_order'])==list(range(len(ref['mapping'])))
   assert plan['mapping_digest']==digest(ref['mapping']);ref['G_frozen_plan']=str(p);g.append({'task_id':tid,'status':'EXACT_INPUT_AND_MAPPING_FROZEN_G153_REUSE','path':str(p),'sha256':sha(p)})
  else:g.append({'task_id':tid,'status':'NEEDS_ACTUAL_SAME15_MODEL_INFERENCE_NO_SYNTHETIC_ORDER'})
  rows.append(ref);samples.append(sample)
  status('NORMALIZING23_PUBLIC_C0',completed=len(rows),task_id=tid)
 assert len(rows)==len({r['task_id'] for r in rows})==23
 save(E/'data/selected_task_bindings.json',{'tasks':rows,'task_order':[r['task_id'] for r in rows],'strata':{'agent_induced_regression':15,'original_issue_continuation':8},'source':str(SOURCE),'source_sha256':sha(SOURCE)})
 (E/'data/public_inputs.jsonl').write_text(''.join(canonical(r)+'\n' for r in samples),'utf-8')
 save(E/'data/common_spec224.json',{'task_order':[r['task_id'] for r in rows],'pilot_first2':[r['task_id'] for r in rows[:2]],'tasks':[{k:r[k] for k in ('task_id','task_path','template','frozen_tests','python','stratum','input_digest','binding_seal','ready_sha256')}|{'public_goal_nodes':read(Path(r['task_path'])/'task_manifest.json')['visible_target_tests'],'ordinary_nodes':read(Path(r['task_path'])/'task_manifest.json')['public_regression_tests'],'private_nodes':read(Path(r['task_path'])/'task_manifest.json')['hidden_preservation_tests']} for r in rows],'same_C0_goal_ordinary_private_all_methods':True,'new_native_API_Gold':0})
 save(E/'ranking/G153_available224.json',{'existing_exact':sum(x['status'].startswith('EXACT') for x in g),'missing':sum(x['status'].startswith('NEEDS') for x in g),'rows':g,'new_encoder_ranker_training_counts':0})
 print(canonical({'phase':'PREPARED23','G_existing':sum(x['status'].startswith('EXACT') for x in g),'pilot_first2':[r['task_id'] for r in rows[:2]]}))
if __name__=='__main__':main()

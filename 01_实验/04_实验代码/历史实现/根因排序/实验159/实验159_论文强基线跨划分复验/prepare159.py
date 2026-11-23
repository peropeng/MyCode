"""Freeze exact three157 source splits and two fully validated paper presets."""
import torch
from common import *
import models159 as models

def prepare():
 require_time(new_long_task=True)
 if sha(E/'approved_plan.json')!=PLAN_SHA:raise RuntimeError('Frozen159 plan changed')
 plan=read(E/'approved_plan.json');old=read(E157/'protocol.json');parent158=read(E158/'protocol.json')
 if plan['baseline_presets']!=PROFILES or tuple(plan['source_data']['split_blocks'])!=BLOCKS:raise RuntimeError('Frozen profiles/splits mismatch')
 if sha(E157/'protocol.json')!=plan['parents']['protocol157_sha256'] or sha(E157/'main_decision_packet.json')!=plan['parents']['packet157_sha256']:raise RuntimeError('Parent157 changed')
 if read(E158/'final_execution_audit.json')['status']!='PASS' or sha(E158/'main_decision_packet.json')!='3247fc6257b6a8cf7d5a0db3ad632add832ee47f224ebfddac554f70ce86d3d1':raise RuntimeError('Root-accepted158 complete required')
 guarded={}
 for root in (E153,E155,E156,E157,E158):
  previous=read(root/'protocol.json');guarded.update(previous['protected_old_files_sha256'])
  if read(root/'final_execution_audit.json')['status']!='PASS':raise RuntimeError('Complete valid old assets required')
  for field in ('training_sources','inputs','initializations'):guarded.update(previous.get(field,{}))
  for name in ('protocol.json','main_decision_packet.json','comparison.json','compact_summary.json','final_execution_audit.json','resource_audit.json','initialization_audit.json','training/all_models_sealed.json','results/all_predictions_sealed.json','validation_selection_sealed.json','validation_selection_decisions.json'):
   path=root/name
   if path.is_file():guarded[str(path)]=sha(path)
  if (root/'training/all_models_sealed.json').exists():
   for rec in read(root/'training/all_models_sealed.json')['models']:guarded[rec['checkpoint']]=rec['checkpoint_sha256']
  outputs=read(root/'results/all_predictions_sealed.json');guarded.update(outputs['files']);guarded.update(outputs.get('derived_files',{}))
 check_hashes(guarded)
 source=[];records=[];initials={};loaded={};bindings=[]
 for block in BLOCKS:
  ids=old['source_splits'][block]['ids']
  if (len(ids['train']),len(ids['validation']))!=(492,122) or set(ids['train'])&set(ids['validation']):raise RuntimeError('Exact disjoint157 split size required')
  for arm in ARMS:
   for seed in SOURCE_SEEDS:
    template=next(r for r in old['source_schedule'] if (r['replication_block'],r['arm'],r['seed'])==(block,'SF_REF',seed))
    if template['fit_ids']!=ids['train'] or template['validation_ids']!=ids['validation']:raise RuntimeError('Original157 row membership mismatch')
    row={**template,'arm':arm,'parent_initial_arm':'SF_REF','parent_157_protocol_sha256':sha(E157/'protocol.json'),'preset_configuration':PROFILES[arm]};source.append(row)
    path=Path(row['initialization_path']);h=old['initializations'][str(path)]
    expected=E153/'training/source/SF_REF'/str(seed)/'initial.pt'
    if path.resolve()!=expected.resolve() or sha(path)!=h or 'invalid' in str(path).casefold():raise RuntimeError('Only exact157 referenced valid canonical INITIAL allowed')
    if str(path) not in loaded:
     ck=torch.load(path,map_location='cpu',weights_only=False);state=ck['state_dict'];info=ck['info'];sig=models.state_digest(state);rngsig=models.rng_digest(ck['training_rng'])
     if sig!=info['state_digest'] or info['canonical_seed']!=row['initialization_seed'] or sum(v.numel() for v in state.values())!=277633:raise RuntimeError('INITIAL state/RNG/parameters mismatch')
     loaded[str(path)]={'state_digest':sig,'training_rng_digest':rngsig,'canonical_seed':info['canonical_seed'],'parameter_count':277633};del ck,state
    initials[str(path)]=h
    records.append({'suite':'source','arm':arm,'seed':seed,'outer':None,'replication_block':block,'initialization_seed':row['initialization_seed'],'path':str(path),'sha256':h,**loaded[str(path)],'parent_arm':'SF_REF','parent_157_protocol_sha256':sha(E157/'protocol.json'),'valid_153_INITIAL_only':True,'trained_parent_weight_loads':0,'invalid_runtime_asset_loads':0,'preset_configuration':PROFILES[arm]})
    bindings.append({'block':block,'arm':arm,'seed':seed,'fit_ids_sha256':digest(row['fit_ids']),'validation_ids_sha256':digest(row['validation_ids']),'initialization_path':str(path),'initialization_sha256':h,'parent157_match':True})
 if (len(source),len(records),len(initials))!=(18,18,3):raise RuntimeError('Exact18source fit references/3 physical initials required')
 inherited={'path':str(E158/'fixtures/preset_test_receipt.json'),'sha256':sha(E158/'fixtures/preset_test_receipt.json'),'status':'PASS','source_protocol_sha256':sha(E158/'protocol.json'),'rerun_fixture_or_neural_tests':0}
 fixture=read(inherited['path'])
 if fixture['status']!='PASS' or fixture['protocol_sha256']!=inherited['source_protocol_sha256']:raise RuntimeError('Inherited158 fixture invalid')
 for name in ('context_base.py',):
  if sha(E/name)!=sha(E158/name):raise RuntimeError('Exact inherited implementation required:'+name)
 if (E/'models159.py').read_text('utf-8')!=(E158/'models158.py').read_text('utf-8').replace('models158','models159').replace('Exp158','Exp159').replace('Frozen158','Frozen159'):raise RuntimeError('Preset model/loss changed')
 if any(sha(q)!=sha(E158/'sources'/q.name) for q in (E/'sources').glob('*.py')):raise RuntimeError('Inherited vendor changed')
 init={'at_utc':now(),'status':'PASS','records':records,'unique_canonical153_INITIAL_files':3,'unique_canonical157_SF_INITIAL_files':3,'split_seed_initial_row_references':9,'final_training_references':18,'canonical_INITIAL_state_and_RNG_digests_verified':True,'new_initializations_created':0,'new_model_constructors_or_forwards_for_preparation':0,'trained_parent_weight_loads':0,'invalid_runtime_asset_loads':0,'runtime_backend_policy':EXPECTED_BACKEND}
 write_new(E/'initialization_audit.json',init)
 write_new(E/'split_binding_audit.json',{'at_utc':now(),'status':'PASS','source_splits':old['source_splits'],'row_bindings':bindings,'source_splits_sha256':digest(old['source_splits']),'parent157_protocol_sha256':sha(E157/'protocol.json'),'same_initial_and_RNG_per_split_seed_for_both_presets':True,'new_source_partition_or_AF_training':0})
 prepared={'at_utc':now(),'status':'READY','experiment':'Exp159','approved_plan_sha256':PLAN_SHA,'primary':PRIMARY,'arms':list(ARMS),'profiles':PROFILES,'blocks':list(BLOCKS),'source_splits':old['source_splits'],'source_schedule':source,'af_schedule':[],'source_seeds':list(SOURCE_SEEDS),'target_cohorts':old['target_cohorts'],'source_public_records':old['source_public_records'],'source_training_features':old['source_training_features'],'source_training_labels':old['source_training_labels'],'protected_old_files_sha256':guarded,'inherited_preset_fixture':inherited,'initializations':initials,'initialization_records':records,'unique_canonical_initial_files':3,'split_seed_initial_row_references':9,'parameters':{a:277633 for a in ARMS},'max_epochs':50,'patience':10,'batch':16,'device':'cuda','dtype':'float32','runtime_backend_policy':EXPECTED_BACKEND,'expected_optimization_stages':18,'expected_final_models':18,'expected_outputs':51720,'expected_prediction_files':96,'expected_derived_selection_view_records':25860,'expected_derived_selection_files':48,'new_model_scoring_record_outputs':38790,'new_three_seed_ensemble_outputs':12930,'new_AF_training':0,'new_encoder_API_download_Gold_independent_tasks':0,'fee_CNY':'0','deadline':DEADLINE}
 write_new(E/'prepared_inputs.json',prepared)
 names=('common.py','context_base.py','models159.py','data159.py','prepare159.py','trainer159.py','predict159.py','select159.py')
 sources={str(E/n):sha(E/n) for n in names};sources.update({str(q):sha(q) for q in (E/'sources').glob('*.py')})
 inputs={str(E/n):sha(E/n) for n in ('approved_plan.json','prepared_inputs.json','initialization_audit.json','split_binding_audit.json')}
 for key in ('source_public_records','source_training_features','source_training_labels'):inputs[prepared[key]]=sha(prepared[key])
 inputs[inherited['path']]=inherited['sha256']
 protocol={**prepared,'schema':'Exp159-frozen157-source-three-splits-two-paper-presets/1.0','training_sources':sources,'inputs':inputs,'optimizer':'AdamW','weight_decay':.00001,'clip':1.,'lr_by_preset':{a:PROFILES[a]['lr'] for a in ARMS},'source_loss':'Exact158 StepFinder CE+profile.lambda_temporal*temporal','selection':'valTop1 then MRR then earliest epoch; preset complete tie ALG','model_seal_rule':'18source models→9valchoices seal→51720native+25860derived seals→targetlabeljoin','parent157_protocol_sha256':sha(E157/'protocol.json'),'parent158_protocol_sha256':sha(E158/'protocol.json'),'only_original157_source_partitions':True,'no_new_AF_training':True}
 write_new(E/'protocol.json',protocol)
 counters={k:0 for k in ('completed_optimization_stages','optimizer_updates','final_models','new_ranker_outputs','derived_selection_view_records','new_encoder','new_API','new_downloads','new_Gold','new_independent_tasks')};counters['fee_CNY']='0'
 checkpoint={'at_utc':now(),'experiment':'Exp159','phase':'PROTOCOL_SPLITS_INITIALS_SEALED','owner_chat_id':'01a10cf5-0721-7002-83b8-766a60389490','source_chat_id':'01a0b043-b3d8-77f0-be9d-5eee0fed25b0','context_window_id':'01a113b4-f8c1-7fe2-a8a8-cab15eca2b59','worktree':str(W),'branch':'exp/1007-exp159-author-preset-splits','approved_plan_sha256':PLAN_SHA,'plan_fully_read':True,'deadline_beijing':'2026-10-07T10:00:00+08:00','expected_optimization_stages':18,'expected_final_models':18,'expected_outputs':51720,'expected_derived_view_records':25860,'counters':counters,'science_owner':'root','next':'small static split/initial/count/family bindings audit, train18, choice9, native51720/derived25860seals, Holm3/6, finalize'}
 write_new(E/'checkpoint.json',checkpoint);write_new(E/'execution_state.json',checkpoint)
 print(canonical({'Exp159':'protocol_sealed','stages':18,'models':18,'initial_files':3,'initial_row_pairs':9,'protected_old_files':len(guarded),'protocol_sha256':sha(E/'protocol.json')}),flush=True)

if __name__=='__main__':prepare()

"""Freeze original153 members, two complete profiles and18 valid SF INITIAL files."""
import torch
from common import *
import models158 as models

def prepare():
 require_time(new_long_task=True)
 if sha(E/'approved_plan.json')!=PLAN_SHA:raise RuntimeError('Approved158 plan changed')
 plan=read(E/'approved_plan.json');parents=plan['parents'];old=read(E153/'protocol.json')
 if plan['new_baseline_arms']!=PROFILES:raise RuntimeError('Complete frozen ALG/HC profiles required')
 for root,name,key in ((E153,'main_decision_packet.json','packet153_sha256'),(E157,'main_decision_packet.json','packet157_sha256'),
  (E157,'protocol.json','protocol157_sha256'),(E157,'training/all_models_sealed.json','modelseal157_sha256'),(E157,'results/all_predictions_sealed.json','predseal157_sha256')):
  if sha(root/name)!=parents[key]:raise RuntimeError('Immutable158 parent binding changed')
 guarded={}
 for root in (E153,E155,E156,E157):
  previous=read(root/'protocol.json')
  if read(root/'final_execution_audit.json')['status']!='PASS':raise RuntimeError('Only complete valid parents allowed')
  guarded.update(previous['protected_old_files_sha256'])
  for field in ('training_sources','rule_sources_sha256','inputs','initializations'):guarded.update(previous.get(field,{}))
  for name in ('protocol.json','main_decision_packet.json','comparison.json','compact_summary.json','final_execution_audit.json','resource_audit.json','initialization_audit.json','training/all_models_sealed.json','results/all_predictions_sealed.json'):
   path=root/name
   if path.is_file():guarded[str(path)]=sha(path)
  if (root/'training/all_models_sealed.json').exists():
   for rec in read(root/'training/all_models_sealed.json')['models']:guarded[rec['checkpoint']]=rec['checkpoint_sha256']
  guarded.update(read(root/'results/all_predictions_sealed.json')['files'])
 check_hashes(guarded)
 original_initials={(r['suite'],r['arm'],r['seed'],r['outer']):r for r in read(E153/'initialization_audit.json')['records']}
 source=[];AF=[];scaler_specs=[]
 for arm in ARMS:
  for seed in SOURCE_SEEDS:
   template=next(r for r in old['source_schedule'] if r['arm']=='SF_REF' and r['seed']==seed)
   initial=original_initials['source','SF_REF',seed,None]
   row={**template,'arm':arm,'parent_initial_arm':'SF_REF','initialization_path':initial['path'],
        'fit_ids':old['source_ids']['train'],'validation_ids':old['source_ids']['validation'],'preset_configuration':PROFILES[arm]}
   source.append(row);scaler_specs.append({'suite':'source','arm':arm,'seed':seed,'outer':None,'stage':'source_fit','scaler_fit_ids_sha256':digest(row['fit_ids'])})
  for seed in AF_SEEDS:
   for outer in range(5):
    template=next(r for r in old['af_schedule'] if r['arm']=='SF_REF' and r['seed']==seed and r['outer']==outer)
    initial=original_initials['AF','SF_REF',seed,outer]
    row={**template,'arm':arm,'parent_initial_arm':'SF_REF','initialization_path':initial['path'],'preset_configuration':PROFILES[arm]}
    AF.append(row)
    for stage,ids in (('selection',row['selection_fit_ids']),('refit',row['refit_ids'])):
     scaler_specs.append({'suite':'AF','arm':arm,'seed':seed,'outer':outer,'stage':stage,'scaler_fit_ids_sha256':digest(ids)})
 if (len(source),len(AF),len(scaler_specs))!=(6,30,66):raise RuntimeError('Exact6source30AFpairs66stages required')
 initials={};loaded={};records=[]
 for row in source+[{'suite':'AF',**r} for r in AF]:
  path=Path(row['initialization_path']);h=old['initializations'][str(path)]
  if sha(path)!=h or 'invalid' in str(path).casefold():raise RuntimeError('Only valid153 INITIAL allowed')
  if str(path) not in loaded:
   ck=torch.load(path,map_location='cpu',weights_only=False);state=ck['state_dict'];info=ck['info']
   sig=models.state_digest(state);rngsig=models.rng_digest(ck['training_rng'])
   if sig!=info['state_digest'] or info['canonical_seed']!=row['initialization_seed'] or sum(v.numel() for v in state.values())!=277633:raise RuntimeError('Exact SF INITIAL state/RNG/parameters required')
   loaded[str(path)]={'state_digest':sig,'training_rng_digest':rngsig,'canonical_seed':info['canonical_seed'],'parameter_count':277633}
   del ck,state
  initials[str(path)]=h
  records.append({'suite':row['suite'],'arm':row['arm'],'seed':row['seed'],'outer':row.get('outer'),'initialization_seed':row['initialization_seed'],
   'path':str(path),'sha256':h,**loaded[str(path)],'parent_arm':'SF_REF','valid_153_INITIAL_only':True,'trained_parent_weight_loads':0,
   'invalid_runtime_asset_loads':0,'preset_configuration':PROFILES[row['arm']]})
 if (len(initials),len(records))!=(18,36):raise RuntimeError('18 canonicalSF states/36 finalmodel references required')
 write_new(E/'initialization_audit.json',{'at_utc':now(),'status':'PASS','records':records,'unique_canonical153_SF_INITIAL_files':18,
  'final_training_references':36,'canonical_INITIAL_state_and_RNG_digests_verified':True,'new_initializations_created':0,
  'new_model_constructors_or_forwards_for_preparation':0,'trained_parent_weight_loads':0,'invalid_runtime_asset_loads':0,
  'actual_nonlearned_preset_attributes_checked_by_every_stage_after_state_load':True,'runtime_backend_policy':EXPECTED_BACKEND})
 prepared={'at_utc':now(),'status':'READY','experiment':'Exp158','approved_plan_sha256':PLAN_SHA,'primary':PRIMARY,'arms':list(ARMS),'profiles':PROFILES,
  'selected_baseline_name':SELECTED,'source_ids':old['source_ids'],'source_schedule':source,'af_schedule':AF,'scaler_fit_specs':scaler_specs,
  'target_cohorts':old['target_cohorts'],'source_seeds':list(SOURCE_SEEDS),'AF_seeds':list(AF_SEEDS),'parameters':{a:277633 for a in ARMS},
  'source_public_records':str(E134/'data/public_records.json'),'AF_public_records':str(E138/'data/public_records.json'),
  'source_training_features':old['source_training_features'],'AF_training_features':old['AF_training_features'],
  'source_training_labels':str(E134/'data/selected_train_labels.private.json'),'AF_training_labels':str(E138/'data/development_labels.private.json'),
  'protected_old_files_sha256':guarded,'max_epochs':50,'patience':10,'batch_tasks_or_complete_groups':16,
  'expected_optimization_stages':66,'expected_final_models':36,'expected_outputs':23088,'expected_prediction_files':70,
  'source_target_outputs':17240,'AF_target_outputs':5848,'new_model_scoring_record_outputs':17316,'new_three_seed_ensemble_outputs':5772,
  'expected_derived_selection_view_records':11544,'expected_derived_selection_files':20,'runtime_backend_policy':EXPECTED_BACKEND,
  'only_original153_partitions_no157_splits':True,'aggregation':'Each preset original3seed softmaxmean; derived validation-selected original3seed mean; no new native forward for selection',
  'new_encoder_API_download_Gold_independent_tasks':0,'fee_CNY':'0','no_target_evaluation_label_joins_before_all_new_predictions_and_derived_views_sealed':True}
 write_new(E/'prepared_inputs.json',prepared)
 names=('common.py','context_base.py','models158.py','data158.py','prepare158.py','trainer158.py','predict158.py','select158.py')
 training_sources={str(E/n):sha(E/n) for n in names};training_sources.update({str(q):sha(q) for q in (E/'sources').glob('*.py')})
 inputs={str(E/n):sha(E/n) for n in ('approved_plan.json','prepared_inputs.json','initialization_audit.json')}
 for key in ('source_public_records','AF_public_records','source_training_features','AF_training_features','source_training_labels','AF_training_labels'):
  inputs[prepared[key]]=sha(prepared[key])
 protocol={**prepared,'schema':'Exp158-locked153-primary-author-two-preset-strong-baseline/1.0','training_sources':training_sources,'inputs':inputs,
  'initializations':initials,'initialization_records':records,'unique_canonical_initial_files':18,'device':'cuda','dtype':'float32',
  'batch':16,'optimizer':'AdamW','weight_decay':.00001,'clip':1.,'lr_by_preset':{a:PROFILES[a]['lr'] for a in ARMS},
  'source_loss':'Original StepFinder CE+profile.lambda_temporal*native scalar temporal loss',
  'AF_loss':'Original per-record CE+profile.lambda_temporal*per-record temporal, groupmean before batchmean',
  'selection':'Top1 then MRR then earliest epoch; preset tie ALG; inner validation only',
  'model_seal_rule':'all36models/66stages→18validation choices seal→all23088native outputs and11544derived views seal→target evaluation',
  'frozen_primary_forward_or_fit_new':0,'deadline':DEADLINE}
 write_new(E/'protocol.json',protocol)
 checkpoint={'at_utc':now(),'experiment':'Exp158','phase':'PROTOCOL_AND_ORIGINAL_IDS_AND_INITIAL_REFERENCES_SEALED',
  'owner_chat_id':'01a10cf5-0721-7002-83b8-766a60389490','source_chat_id':'01a0b043-b3d8-77f0-be9d-5eee0fed25b0',
  'context_window_id':'01a11331-eb00-78f1-afb1-95fa109cf366','worktree':str(W),'branch':'exp/1007-exp158-author-preset-baseline',
  'approved_plan_sha256':PLAN_SHA,'plan_fully_read':True,'deadline_beijing':'2026-10-07T10:00:00+08:00','ETA_initial_total_minutes':[30,55],
  'expected_optimization_stages':66,'expected_final_models':36,'expected_outputs':23088,'expected_derived_view_records':11544,'current_pid':None,
  'counters':{'completed_optimization_stages':0,'optimizer_updates':0,'final_models':0,'new_ranker_outputs':0,'derived_selection_view_records':0,
   'new_encoder':0,'new_API':0,'new_downloads':0,'new_Gold':0,'new_independent_tasks':0,'fee_CNY':'0'},
  'science_owner':'root','next':'Necessary preset/lambda/val-only fixture once, thentrain66/36→validationchoicesseal→native23088+derived11544seals→Holm3/4→audit'}
 write_new(E/'checkpoint.json',checkpoint);write_new(E/'execution_state.json',checkpoint)
 print(canonical({'Exp158':'protocol_prepared','source_fits':6,'AF_pairs':30,'stages':66,'final_models':36,'initial_files':18,
                  'profiles':PROFILES,'protected_old_files':len(guarded)}),flush=True)

if __name__=='__main__':prepare()

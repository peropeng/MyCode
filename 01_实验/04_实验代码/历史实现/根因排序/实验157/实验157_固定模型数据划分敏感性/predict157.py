"""Complete original ranks for every sealed split/model, without target Gold joins."""
import gc
import numpy as np
import torch
from common import *
import models157 as models
from trainer157 import verify_protocol,predict,backend_policy,EXPECTED_BACKEND

def save(path,value):
 if path.exists():
  if read(path)!=value:raise RuntimeError('Existing prediction changed: '+str(path))
 else:write_new(path,value)

def ensemble(ids,predictions):
 out={}
 if len(predictions)!=3:raise RuntimeError('Exactly original3 seeds per split required')
 for sid in ids:
  if not all(v[sid]['valid'] for v in predictions):raise RuntimeError('All fixed seeds required')
  prob=np.mean([v[sid]['probabilities'] for v in predictions],axis=0,dtype=np.float64).tolist()
  order=sorted(range(len(prob)),key=lambda i:(-prob[i],i))
  out[sid]={'probabilities':prob,'order':order,'chosen_step':order[0],'valid':True,'native_complete_ranking':True}
 return out

def load_model(rec,device):
 if sha(rec['checkpoint'])!=rec['checkpoint_sha256']:raise RuntimeError('Sealed model changed')
 ck=torch.load(rec['checkpoint'],map_location='cpu',weights_only=False)
 model=models.create(rec['arm']).to(device);model.load_state_dict(ck['state_dict'])
 return model,(ck['scaler_mean'],ck['scaler_std'])

def run():
 require_time(new_long_task=True);p=verify_protocol();models.seed_all(0)
 if backend_policy()!=EXPECTED_BACKEND:raise RuntimeError('Frozen inference backend policy not active')
 seal=read(E/'training/all_models_sealed.json')
 if not seal['all_fixed_models_sealed'] or seal['final_models']!=162 or seal['optimization_stages']!=297:raise RuntimeError('All162 sealed final models required')
 device=torch.device('cuda')
 source={(r['arm'],r['replication_block'],r['seed']):r for r in seal['models'] if r['suite']=='source'}
 AF={(r['arm'],r['replication_block'],r['seed'],r['outer']):r for r in seal['models'] if r['suite']=='AF'}
 files={};count=0;cohorts={};started=time.monotonic();ph=sha(E/'protocol.json')
 for cohort in COHORTS:
  ref=p['target_cohorts'][cohort];ids=ref['sample_ids'];public=read(ref['public_records'])['records'];by={r['sample_id']:r for r in public}
  if [r['sample_id'] for r in public]!=ids or len(ids)!=ref['n']:raise RuntimeError('Original source cohort changed')
  full=torch.load(ref['feature_source'],map_location='cpu',weights_only=False)['records'];data={s:full[s] for s in ids};del full
  for arm in ARMS:
   for block in BLOCKS:
    predictions=[]
    for seed in SOURCE_SEEDS:
     rec=source[arm,block,seed];path=prediction_path(cohort,arm,block,seed)
     if path.exists():
      saved=read(path)
      if saved['checkpoint_sha256']!=rec['checkpoint_sha256'] or saved['protocol_sha256']!=ph or saved['replication_block']!=block:raise RuntimeError('Existing source binding changed')
      out=saved['predictions']
     else:
      model,scaler=load_model(rec,device);out=predict(model,arm,ids,data,scaler,device)
      for sid,v in out.items():v['predicted_role']=by[sid]['turns'][v['chosen_step']]['role']
      save(path,{'predictions':out,'cohort':cohort,'arm':arm,'seed':seed,'replication_block':block,
       'checkpoint_sha256':rec['checkpoint_sha256'],'protocol_sha256':ph,'target_labels_decoded':0,'original_ordinal_ranks':True})
      append(E/'physical_generation_events.jsonl',{'at_utc':now(),'kind':'SOURCE_NATIVE_OUTPUTS','path':str(path),'outputs':len(ids),'cached_read':False})
      del model;gc.collect();torch.cuda.empty_cache()
     if set(out)!=set(ids):raise RuntimeError('Source predictions incomplete')
     predictions.append(out);files[str(path)]=sha(path);count+=len(ids)
     status('PREDICTIONS_RUNNING',current_cohort=cohort,current_arm=arm,current_block=block,current_seed=seed,new_ranker_outputs=count,target_label_values_joined=0)
    averaged=ensemble(ids,predictions)
    for sid,v in averaged.items():v['predicted_role']=by[sid]['turns'][v['chosen_step']]['role']
    path=prediction_path(cohort,arm,block);existed=path.exists()
    save(path,{'predictions':averaged,'cohort':cohort,'arm':arm,'replication_block':block,'seeds':list(SOURCE_SEEDS),
     'all3_fixed_seeds_retained':True,'target_labels_decoded':0,'protocol_sha256':ph,'no_cross_split_ensemble':True})
    if not existed:append(E/'physical_generation_events.jsonl',{'at_utc':now(),'kind':'SOURCE_THREE_SEED_ENSEMBLE','path':str(path),'outputs':len(ids),'cached_read':False})
    files[str(path)]=sha(path);count+=len(ids)
  cohorts[cohort]={'n':len(ids),'sample_ids':ids,'outputs':36*len(ids),'folder':str(E/'results'/cohort)};del data;gc.collect()
  print(canonical({'Exp157':'cohort_predictions_saved','cohort':cohort,'outputs':36*len(ids),'target_Gold_joined':0}),flush=True)
 if count!=77580 or len(files)!=144:raise RuntimeError('Exactly77580 source outputs/144files required')
 source_seal={'files':files.copy(),'outputs':count,'cohorts':cohorts,'protocol_sha256':ph,'model_seal_sha256':sha(E/'training/all_models_sealed.json'),
  'target_labels_joined':0,'all_seeds_retained':True,'all_blocks_retained':True,'all_source_output_files':144}
 save(E/'results/source_predictions_sealed.json',source_seal)
 data=torch.load(p['AF_training_features'],map_location='cpu',weights_only=False)['records']
 public=read(p['AF_public_records'])['records'];by={r['sample_id']:r for r in public};ids=[r['sample_id'] for r in public];af_files={}
 for arm in ARMS:
  for block in BLOCKS:
   seed_predictions=[]
   for seed in AF_SEEDS:
    joined={}
    for r in p['af_schedule']:
     if r['arm']!=arm or r['replication_block']!=block or r['seed']!=seed:continue
     rec=AF[arm,block,seed,r['outer']];path=fold_prediction_path(arm,block,seed,r['outer'])
     if path.exists():
      saved=read(path)
      if saved['checkpoint_sha256']!=rec['checkpoint_sha256'] or saved['protocol_sha256']!=ph:raise RuntimeError('AF existing model binding changed')
      out=saved['predictions']
     else:
      model,scaler=load_model(rec,device);out=predict(model,arm,r['held_ids'],data,scaler,device)
      for sid,v in out.items():v['predicted_role']=by[sid]['turns'][v['chosen_step']]['role']
      save(path,{'predictions':out,'arm':arm,'replication_block':block,'seed':seed,'outer':r['outer'],
       'checkpoint_sha256':rec['checkpoint_sha256'],'protocol_sha256':ph,'inference_batches_sha256':r['inference_batches_sha256'],'held_labels_joined':0})
      append(E/'physical_generation_events.jsonl',{'at_utc':now(),'kind':'AF_NATIVE_FOLD_OUTPUTS','path':str(path),'outputs':len(out),'cached_read':False})
      del model;gc.collect();torch.cuda.empty_cache()
     if set(out)!=set(r['held_ids']) or set(joined)&set(out):raise RuntimeError('AF OOF scope collision')
     joined.update(out);af_files[str(path)]=sha(path);count+=len(out)
    if set(joined)!=set(ids):raise RuntimeError('Each AFrecord exactly one OOF per splitseed required')
    path=prediction_path('AF',arm,block,seed)
    save(path,{'predictions':joined,'arm':arm,'replication_block':block,'seed':seed,'exactly_one_OOF_per_record':True,
     'old_dev_labels_joined':0,'protocol_sha256':ph,'joined_entries_not_new_outputs':731})
    af_files[str(path)]=sha(path);seed_predictions.append(joined)
    status('PREDICTIONS_RUNNING',current_cohort='AF731',current_arm=arm,current_block=block,current_seed=seed,new_ranker_outputs=count,target_label_values_joined=0)
   averaged=ensemble(ids,seed_predictions)
   for sid,v in averaged.items():v['predicted_role']=by[sid]['turns'][v['chosen_step']]['role']
   path=prediction_path('AF',arm,block);existed=path.exists()
   save(path,{'predictions':averaged,'arm':arm,'replication_block':block,'seeds':list(AF_SEEDS),'all3_fixed_seeds_retained':True,
    'exactly_one_OOF_per_record_per_seed':True,'old_dev_labels_joined':0,'protocol_sha256':ph,'no_cross_split_ensemble':True})
   if not existed:append(E/'physical_generation_events.jsonl',{'at_utc':now(),'kind':'AF_THREE_SEED_ENSEMBLE','path':str(path),'outputs':len(ids),'cached_read':False})
   af_files[str(path)]=sha(path);count+=len(ids)
   print(canonical({'Exp157':'AF_OOF_saved','arm':arm,'block':block,'records':731,'target_Gold_joined':0}),flush=True)
 if count!=103896 or len(af_files)!=171:raise RuntimeError('Exactly103896 total outputs/171AFfiles required')
 save(E/'results/AF_predictions_sealed.json',{'files':af_files,'outputs':26316,'records':731,'groups':716,'protocol_sha256':ph,
  'model_seal_sha256':sha(E/'training/all_models_sealed.json'),'target_labels_joined':0,'all_seeds_retained':True,'all_blocks_retained':True,
  'native_OOF_outputs':19737,'ensemble_outputs':6579,'joined_copy_entries_not_new_outputs':19737})
 save(E/'results/all_predictions_sealed.json',{'files':{**files,**af_files},'protocol_sha256':ph,'model_seal_sha256':sha(E/'training/all_models_sealed.json'),
  'source_seal_sha256':sha(E/'results/source_predictions_sealed.json'),'AF_seal_sha256':sha(E/'results/AF_predictions_sealed.json'),
  'outputs':103896,'source_outputs':77580,'AF_outputs':26316,'prediction_files':315,'all_fixed_outputs_sealed':True,'target_labels_joined':0,'elapsed_seconds':time.monotonic()-started})
 status('ALL_PREDICTIONS_SEALED',new_ranker_outputs=103896,current_cohort=None,current_arm=None,current_block=None,current_seed=None,next='evaluate157.py after allblocks/allmodels/allpredictions seals thenfinalaudit')

if __name__=='__main__':run()

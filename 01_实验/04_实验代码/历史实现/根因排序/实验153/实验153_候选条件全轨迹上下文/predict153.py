"""Complete original-coordinate ranks from all sealed models, without Gold joins."""
import gc
import numpy as np
import torch
from common import *
import context_models as models
from trainer153 import verify_protocol,predict,backend_policy,EXPECTED_BACKEND

def save(path,value):
 if path.exists():
  if read(path)!=value:raise RuntimeError('Existing prediction changed: '+str(path))
 else:write_new(path,value)
def ensemble(ids,predictions):
 out={}
 for sid in ids:
  if not all(v[sid]['valid'] for v in predictions):raise RuntimeError('All fixed seeds required')
  prob=np.mean([v[sid]['probabilities'] for v in predictions],axis=0,dtype=np.float64).tolist()
  order=sorted(range(len(prob)),key=lambda i:(-prob[i],i));out[sid]={'probabilities':prob,'order':order,'chosen_step':order[0],'valid':True,'native_complete_ranking':True}
 return out
def load_model(rec,device):
 if sha(rec['checkpoint'])!=rec['checkpoint_sha256']:raise RuntimeError('Sealed model changed')
 ck=torch.load(rec['checkpoint'],map_location='cpu',weights_only=False);model=models.create(rec['arm']).to(device);model.load_state_dict(ck['state_dict'])
 return model,(ck['scaler_mean'],ck['scaler_std'])
def run():
 require_time(new_long_task=True);p=verify_protocol();models.seed_all(0)
 if backend_policy()!=EXPECTED_BACKEND:raise RuntimeError('Frozen inference backend policy not active')
 seal=read(E/'training/all_models_sealed.json')
 if not seal['all_fixed_models_sealed'] or seal['final_models']!=108 or seal['optimization_stages']!=198:raise RuntimeError('All108 sealed final models required')
 device=torch.device('cuda');source={(r['arm'],r['seed']):r for r in seal['models'] if r['suite']=='source'};AF={(r['arm'],r['seed'],r['outer']):r for r in seal['models'] if r['suite']=='AF'}
 files={};count=0;cohorts={};started=time.monotonic()
 for cohort in COHORTS:
  ref=p['target_cohorts'][cohort];ids=ref['sample_ids'];public=read(ref['public_records'])['records'];by={r['sample_id']:r for r in public}
  if [r['sample_id'] for r in public]!=ids or len(ids)!=ref['n']:raise RuntimeError('Fixed source cohort changed')
  full=torch.load(ref['feature_source'],map_location='cpu',weights_only=False)['records'];data={s:full[s] for s in ids};del full
  for arm in ARMS:
   predictions=[]
   for seed in SOURCE_SEEDS:
    rec=source[arm,seed];path=E/'results'/cohort/f'{arm}_{seed}.json'
    if path.exists():
     saved=read(path)
     if saved['checkpoint_sha256']!=rec['checkpoint_sha256'] or saved['protocol_sha256']!=sha(E/'protocol.json'):raise RuntimeError('Existing seed binding changed')
     out=saved['predictions']
    else:
     model,scaler=load_model(rec,device);out=predict(model,arm,ids,data,scaler,device)
     for sid,v in out.items():v['predicted_role']=by[sid]['turns'][v['chosen_step']]['role']
     save(path,{'predictions':out,'cohort':cohort,'arm':arm,'seed':seed,'checkpoint_sha256':rec['checkpoint_sha256'],'protocol_sha256':sha(E/'protocol.json'),'target_labels_decoded':0,'original_ordinal_ranks':True})
     del model;gc.collect();torch.cuda.empty_cache()
    if set(out)!=set(ids):raise RuntimeError('Source predictions incomplete')
    predictions.append(out);files[str(path)]=sha(path);count+=len(ids)
    status('PREDICTIONS_RUNNING',current_cohort=cohort,current_arm=arm,current_seed=seed,new_ranker_outputs=count,target_label_values_joined=0)
   averaged=ensemble(ids,predictions)
   for sid,v in averaged.items():v['predicted_role']=by[sid]['turns'][v['chosen_step']]['role']
   path=E/'results'/cohort/f'{arm}_ensemble.json';save(path,{'predictions':averaged,'cohort':cohort,'arm':arm,'all3_fixed_seeds_retained':True,'seeds':list(SOURCE_SEEDS),'target_labels_decoded':0})
   files[str(path)]=sha(path);count+=len(ids)
  cohorts[cohort]={'n':len(ids),'sample_ids':ids,'outputs':24*len(ids),'folder':str(E/'results'/cohort)};del data;gc.collect()
  print(canonical({'Exp153':'cohort_predictions_saved','cohort':cohort,'outputs':24*len(ids),'target_Gold_joined':0}),flush=True)
 if count!=51720:raise RuntimeError('Expected51720 source outputs')
 source_seal={'files':files.copy(),'outputs':count,'cohorts':cohorts,'protocol_sha256':sha(E/'protocol.json'),'model_seal_sha256':sha(E/'training/all_models_sealed.json'),'target_labels_joined':0,'all_seeds_retained':True}
 save(E/'results/source_predictions_sealed.json',source_seal)
 data=torch.load(E138/'features/development_features.pt',map_location='cpu',weights_only=False)['records'];public=read(E138/'data/public_records.json')['records'];by={r['sample_id']:r for r in public};ids=[r['sample_id'] for r in public];af_files={}
 for arm in ARMS:
  seed_predictions=[]
  for seed in AF_SEEDS:
   joined={}
   for r in p['af_schedule']:
    if r['arm']!=arm or r['seed']!=seed:continue
    rec=AF[arm,seed,r['outer']];path=E/'results/AF/folds'/arm/f"{seed}_{r['outer']}.json"
    if path.exists():
     saved=read(path)
     if saved['checkpoint_sha256']!=rec['checkpoint_sha256']:raise RuntimeError('AF prediction model binding changed')
     out=saved['predictions']
    else:
     model,scaler=load_model(rec,device);out=predict(model,arm,r['held_ids'],data,scaler,device)
     for sid,v in out.items():v['predicted_role']=by[sid]['turns'][v['chosen_step']]['role']
     save(path,{'predictions':out,'checkpoint_sha256':rec['checkpoint_sha256'],'protocol_sha256':sha(E/'protocol.json'),'inference_batches_sha256':r['inference_batches_sha256'],'held_labels_joined':0})
     del model;gc.collect();torch.cuda.empty_cache()
    if set(out)!=set(r['held_ids']) or set(joined)&set(out):raise RuntimeError('AF OOF scope collision')
    joined.update(out);af_files[str(path)]=sha(path);count+=len(out)
   if set(joined)!=set(ids):raise RuntimeError('AF every record must appear once per seed')
   path=E/'results/AF'/f'{arm}_{seed}.json';save(path,{'predictions':joined,'arm':arm,'seed':seed,'exactly_one_OOF_per_record':True,'old_dev_labels_joined':0});af_files[str(path)]=sha(path);seed_predictions.append(joined)
   status('PREDICTIONS_RUNNING',current_cohort='AF731',current_arm=arm,current_seed=seed,new_ranker_outputs=count,target_label_values_joined=0)
  averaged=ensemble(ids,seed_predictions)
  for sid,v in averaged.items():v['predicted_role']=by[sid]['turns'][v['chosen_step']]['role']
  path=E/'results/AF'/f'{arm}_ensemble.json';save(path,{'predictions':averaged,'arm':arm,'seeds':list(AF_SEEDS),'all3_fixed_seeds_retained':True,'exactly_one_OOF_per_record_per_seed':True,'old_dev_labels_joined':0});af_files[str(path)]=sha(path);count+=len(ids)
  print(canonical({'Exp153':'AF_OOF_saved','arm':arm,'records':731,'target_Gold_joined':0}),flush=True)
 if count!=69264:raise RuntimeError('Expected69264 total ranker outputs')
 save(E/'results/AF_predictions_sealed.json',{'files':af_files,'outputs':17544,'records':731,'groups':716,'protocol_sha256':sha(E/'protocol.json'),'model_seal_sha256':sha(E/'training/all_models_sealed.json'),'target_labels_joined':0,'all_seeds_retained':True})
 save(E/'results/all_predictions_sealed.json',{'files':{**files,**af_files},'source_seal_sha256':sha(E/'results/source_predictions_sealed.json'),'AF_seal_sha256':sha(E/'results/AF_predictions_sealed.json'),'outputs':69264,'source_outputs':51720,'AF_outputs':17544,'all_fixed_outputs_sealed':True,'target_labels_joined':0,'elapsed_seconds':time.monotonic()-started})
 status('ALL_PREDICTIONS_SEALED',new_ranker_outputs=69264,current_cohort=None,current_arm=None,current_seed=None,next='evaluate153.py complete saved comparisons and resource/final audits')

if __name__=='__main__':run()

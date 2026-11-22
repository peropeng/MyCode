"""Two native preset predictions, then validation-selected views without forward."""
import gc
import numpy as np
import torch
from common import *
import models159 as models
from trainer159 import verify_protocol,predict,backend_policy,EXPECTED_BACKEND

def save(path,value):
 if path.exists():
  if read(path)!=value:raise RuntimeError('Existing frozen output changed: '+str(path))
 else:write_new(path,value)

def ensemble(ids,predictions):
 if len(predictions)!=3:raise RuntimeError('Exactly3 original seeds required')
 out={}
 for sid in ids:
  if not all(v[sid]['valid'] for v in predictions):raise RuntimeError('All three valid seeds required')
  prob=np.mean([v[sid]['probabilities'] for v in predictions],axis=0,dtype=np.float64).tolist()
  order=sorted(range(len(prob)),key=lambda i:(-prob[i],i))
  out[sid]={'probabilities':prob,'order':order,'chosen_step':order[0],'valid':True,'native_complete_ranking':True}
 return out

def add_roles(out,by):
 for sid,v in out.items():v['predicted_role']=by[sid]['turns'][v['chosen_step']]['role']
 return out

def load_model(rec,device):
 if sha(rec['checkpoint'])!=rec['checkpoint_sha256']:raise RuntimeError('Sealed model changed')
 ck=torch.load(rec['checkpoint'],map_location='cpu',weights_only=False);model=models.create(rec['arm']).to(device)
 model.load_state_dict(ck['state_dict']);models.require_model_configuration(model,rec['arm'])
 return model,(ck['scaler_mean'],ck['scaler_std'])

def derive_selected(p,decisions,native):
 if native['outputs']!=51720 or len(native['files'])!=96:raise RuntimeError('All96native files required')
 choice={(r['replication_block'],r['seed']):r for r in decisions['decisions']};files={};count=0;identity=[];dh=sha(E/'validation_selection_decisions.json');ph=sha(E/'protocol.json')
 for scope in COHORTS:
  ref=p['target_cohorts'][scope];ids=ref['sample_ids'];by={r['sample_id']:r for r in read(ref['public_records'])['records']}
  for block in BLOCKS:
   seeds=[];arms=[];sources={}
   for seed in SOURCE_SEEDS:
    arm=choice[block,seed]['chosen_preset'];source=prediction_path(scope,arm,block,seed);out=read(source)['predictions'];seeds.append(out);arms.append(arm);sources[str(source)]=sha(source)
    path=selection_prediction_path(scope,block,seed)
    save(path,{'predictions':out,'cohort':scope,'replication_block':block,'arm':SELECTED,'seed':seed,'chosen_preset':arm,'native_source_path':str(source),'native_source_sha256':sha(source),'protocol_sha256':ph,'selection_decisions_sha256':dh,'derived_selection_view':True,'new_neural_forward':0,'new_optimization_training':0,'target_labels_joined':0})
    files[str(path)]=sha(path);count+=len(ids)
   same=len(set(arms))==1;identity_source=prediction_path(scope,arms[0],block) if same else None
   out=read(identity_source)['predictions'] if same else add_roles(ensemble(ids,seeds),by);path=selection_prediction_path(scope,block)
   save(path,{'predictions':out,'cohort':scope,'replication_block':block,'arm':SELECTED,'seeds':list(SOURCE_SEEDS),'chosen_preset_by_seed':dict(zip(map(str,SOURCE_SEEDS),arms)),'native_source_files_sha256':sources,'protocol_sha256':ph,'selection_decisions_sha256':dh,'derived_selection_view':True,'new_neural_forward':0,'new_optimization_training':0,'target_labels_joined':0,'identity_to_complete_native_preset_ensemble':same,'identity_native_source_path':str(identity_source) if same else None,'identity_native_source_sha256':sha(identity_source) if same else None})
   files[str(path)]=sha(path);count+=len(ids)
   identity.append({'cohort':scope,'block':block,'identity_to_complete_native_preset_ensemble':same,'preset':arms[0] if same else None})
 if count!=25860 or len(files)!=48:raise RuntimeError('Exactly25860derived entries/48files required')
 seal={'at_utc':now(),'files':files,'outputs':25860,'derived_selection_view_records':25860,'prediction_files':48,'all_derived_views_sealed':True,'new_neural_forward':0,'new_model_fit':0,'target_labels_joined':0,'protocol_sha256':ph,'model_seal_sha256':sha(E/'training/all_models_sealed.json'),'selection_seal_sha256':sha(E/'validation_selection_sealed.json'),'native_prediction_seal_sha256':sha(E/'results/native_predictions_sealed.json'),'identity_references':identity}
 save(E/'results/derived_selection_views_sealed.json',seal)
 append(E/'physical_generation_events.jsonl',{'at_utc':now(),'kind':'DERIVED_SELECTION_VIEWS','outputs':0,'derived_view_records':25860,'neural_model_record_scores':0,'new_neural_forward':0})
 return seal

def run():
 require_time(new_long_task=True);p=verify_protocol();m=read(E/'training/all_models_sealed.json');decisions=read(E/'validation_selection_decisions.json');cs=read(E/'validation_selection_sealed.json')
 if (m['optimization_stages'],m['final_models'])!=(18,18) or not m['all_fixed_models_sealed']:raise RuntimeError('Complete18models required')
 if not cs['all9_validation_only_choices_sealed'] or cs['decisions_sha256']!=sha(E/'validation_selection_decisions.json') or cs['target_labels_joined']!=0:raise RuntimeError('All9val choices seal required')
 models_by={(r['replication_block'],r['arm'],r['seed']):r for r in m['models']};device=torch.device('cuda');files={};count=0;started=time.monotonic();ph=sha(E/'protocol.json')
 for scope in COHORTS:
  ref=p['target_cohorts'][scope];ids=ref['sample_ids'];public=read(ref['public_records'])['records'];by={r['sample_id']:r for r in public}
  if [r['sample_id'] for r in public]!=ids:raise RuntimeError('Original target IDs/order changed')
  full=torch.load(ref['feature_source'],map_location='cpu',weights_only=False)['records'];data={s:full[s] for s in ids};del full
  for block in BLOCKS:
   for arm in ARMS:
    seeds=[]
    for seed in SOURCE_SEEDS:
     rec=models_by[block,arm,seed];path=prediction_path(scope,arm,block,seed)
     if path.exists():out=read(path)['predictions']
     else:
      model,scaler=load_model(rec,device);out=add_roles(predict(model,arm,ids,data,scaler,device),by)
      save(path,{'predictions':out,'cohort':scope,'replication_block':block,'arm':arm,'seed':seed,'preset_configuration':PROFILES[arm],'checkpoint_sha256':rec['checkpoint_sha256'],'protocol_sha256':ph,'target_labels_decoded':0,'original_ordinal_ranks':True})
      append(E/'physical_generation_events.jsonl',{'at_utc':now(),'kind':'SOURCE_NATIVE_OUTPUTS','path':str(path),'outputs':len(ids),'neural_model_record_scores':len(ids)});del model;gc.collect();torch.cuda.empty_cache()
     if set(out)!=set(ids):raise RuntimeError('Complete target outputs required')
     seeds.append(out);files[str(path)]=sha(path);count+=len(ids)
     status('PREDICTIONS_RUNNING',current_cohort=scope,current_block=block,current_arm=arm,current_seed=seed,new_ranker_outputs=count,target_label_values_joined=0)
    path=prediction_path(scope,arm,block);existed=path.exists();out=add_roles(ensemble(ids,seeds),by)
    save(path,{'predictions':out,'cohort':scope,'replication_block':block,'arm':arm,'seeds':list(SOURCE_SEEDS),'preset_configuration':PROFILES[arm],'all3_fixed_seeds_retained':True,'protocol_sha256':ph,'target_labels_decoded':0})
    if not existed:append(E/'physical_generation_events.jsonl',{'at_utc':now(),'kind':'SOURCE_PRESET_ENSEMBLE','path':str(path),'outputs':len(ids),'neural_model_record_scores':0})
    files[str(path)]=sha(path);count+=len(ids)
  del data;gc.collect()
 if count!=51720 or len(files)!=96:raise RuntimeError('Exactly51720native entries/96files required')
 native={'at_utc':now(),'files':files,'outputs':51720,'prediction_files':96,'model_scoring_record_outputs':38790,'three_seed_ensemble_outputs':12930,'all_fixed_outputs_sealed':True,'target_labels_joined':0,'protocol_sha256':ph,'model_seal_sha256':sha(E/'training/all_models_sealed.json'),'selection_seal_sha256':sha(E/'validation_selection_sealed.json')}
 save(E/'results/native_predictions_sealed.json',native);derived=derive_selected(p,decisions,native)
 save(E/'results/all_predictions_sealed.json',{'at_utc':now(),'files':files,'derived_files':derived['files'],'outputs':51720,'derived_selection_view_records':25860,'prediction_files':96,'derived_prediction_files':48,'all_fixed_outputs_sealed':True,'all_derived_views_sealed':True,'target_labels_joined':0,'protocol_sha256':ph,'model_seal_sha256':sha(E/'training/all_models_sealed.json'),'selection_seal_sha256':sha(E/'validation_selection_sealed.json'),'native_prediction_seal_sha256':sha(E/'results/native_predictions_sealed.json'),'derived_selection_seal_sha256':sha(E/'results/derived_selection_views_sealed.json'),'elapsed_seconds':time.monotonic()-started})
 status('ALL_PREDICTIONS_SEALED',new_ranker_outputs=51720,derived_selection_view_records=25860,target_label_values_joined=0,next='evaluate159 then finalize159')
 print(canonical({'Exp159':'native_and_derived_sealed','new_native_outputs':51720,'derived_views':25860,'target_labels_joined':0}),flush=True)

if __name__=='__main__':run()

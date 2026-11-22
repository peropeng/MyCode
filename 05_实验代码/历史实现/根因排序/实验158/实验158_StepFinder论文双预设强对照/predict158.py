"""Two native preset predictions, then validation-selected views without forward."""
import gc
import numpy as np
import torch
from common import *
import models158 as models
from trainer158 import verify_protocol,predict,backend_policy,EXPECTED_BACKEND

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

def derive_selected(p,decisions,native_seal):
 """Only JSON reads and probability means; never creates or runs a model."""
 if native_seal['outputs']!=23088 or not native_seal['all_fixed_outputs_sealed']:raise RuntimeError('All native preset outputs required before derived views')
 dh=sha(E/'validation_selection_decisions.json');ph=sha(E/'protocol.json');choice={(r['suite'],r['seed'],r['outer']):r for r in decisions['decisions']}
 files={};count=0;identity=[]
 for scope in COHORTS:
  ref=p['target_cohorts'][scope];ids=ref['sample_ids'];by={r['sample_id']:r for r in read(ref['public_records'])['records']};seeds=[];sources={}
  arms=[]
  for seed in SOURCE_SEEDS:
   arm=choice['source',seed,None]['chosen_preset'];arms.append(arm);source=prediction_path(scope,arm,seed)
   saved=read(source);out=saved['predictions'];sources[str(source)]=sha(source);seeds.append(out)
   path=selection_prediction_path(scope,seed)
   save(path,{'predictions':out,'cohort':scope,'arm':SELECTED,'seed':seed,'chosen_preset':arm,'native_source_path':str(source),
    'native_source_sha256':sha(source),'protocol_sha256':ph,'selection_decisions_sha256':dh,'derived_selection_view':True,
    'new_neural_forward':0,'new_optimization_training':0,'target_labels_joined':0})
   files[str(path)]=sha(path);count+=len(ids)
  same=len(set(arms))==1;identity_source=prediction_path(scope,arms[0]) if same else None
  out=read(identity_source)['predictions'] if same else add_roles(ensemble(ids,seeds),by)
  path=selection_prediction_path(scope)
  save(path,{'predictions':out,'cohort':scope,'arm':SELECTED,'seeds':list(SOURCE_SEEDS),'chosen_preset_by_seed':dict(zip(map(str,SOURCE_SEEDS),arms)),
   'native_source_files_sha256':sources,'all3_fixed_seeds_retained':True,'protocol_sha256':ph,'selection_decisions_sha256':dh,
   'derived_selection_view':True,'new_neural_forward':0,'new_optimization_training':0,'target_labels_joined':0,
   'existing_preset_ensemble_identity':same,'identity_source_path':str(identity_source) if same else None,
   'identity_source_sha256':sha(identity_source) if same else None})
  if same:identity.append({'scope':scope,'path':str(path),'identity_source_path':str(identity_source),'sha256':sha(identity_source)})
  files[str(path)]=sha(path);count+=len(ids)*1
 public=read(p['AF_public_records'])['records'];ids=[r['sample_id'] for r in public];by={r['sample_id']:r for r in public};seeds=[];allarms=[];all_sources={}
 for seed in AF_SEEDS:
  joined={};sources={};arms={}
  for outer in range(5):
   arm=choice['AF',seed,outer]['chosen_preset'];allarms.append(arm);arms[str(outer)]=arm;source=fold_prediction_path(arm,seed,outer)
   out=read(source)['predictions']
   if set(joined)&set(out):raise RuntimeError('Selected fold OOF collision')
   joined.update(out);sources[str(source)]=sha(source);all_sources.update(sources)
  if set(joined)!=set(ids):raise RuntimeError('Selected AF complete731 OOF required')
  seeds.append(joined);path=selection_prediction_path('AF',seed)
  save(path,{'predictions':joined,'arm':SELECTED,'seed':seed,'chosen_preset_by_outer':arms,'native_fold_source_files_sha256':sources,
   'exactly_one_OOF_per_record':True,'protocol_sha256':ph,'selection_decisions_sha256':dh,'derived_selection_view':True,
   'new_neural_forward':0,'new_optimization_training':0,'target_labels_joined':0})
  files[str(path)]=sha(path);count+=len(ids)
 same=len(set(allarms))==1;identity_source=prediction_path('AF',allarms[0]) if same else None
 out=read(identity_source)['predictions'] if same else add_roles(ensemble(ids,seeds),by);path=selection_prediction_path('AF')
 save(path,{'predictions':out,'arm':SELECTED,'seeds':list(AF_SEEDS),'native_fold_source_files_sha256':all_sources,'all3_fixed_seeds_retained':True,
  'exactly_one_OOF_per_record_per_seed':True,'protocol_sha256':ph,'selection_decisions_sha256':dh,'derived_selection_view':True,
  'new_neural_forward':0,'new_optimization_training':0,'target_labels_joined':0,'existing_preset_ensemble_identity':same,
  'identity_source_path':str(identity_source) if same else None,'identity_source_sha256':sha(identity_source) if same else None})
 if same:identity.append({'scope':'AF','path':str(path),'identity_source_path':str(identity_source),'sha256':sha(identity_source)})
 files[str(path)]=sha(path);count+=len(ids)
 if count!=11544 or len(files)!=20:raise RuntimeError('Exactly11544 derived records/20files required')
 manifest={'at_utc':now(),'experiment':'Exp158','name':SELECTED,'status':'PASS','files':files,'derived_view_records':11544,
  'source_derived_records':8620,'AF_derived_records':2924,'derived_files':20,'all_derived_views_sealed':True,
  'protocol_sha256':ph,'selection_decisions_sha256':dh,'selection_seal_sha256':sha(E/'validation_selection_sealed.json'),
  'native_prediction_seal_sha256':sha(E/'results/native_predictions_sealed.json'),'new_neural_forward':0,'new_optimization_training':0,
  'target_labels_joined':0,'existing_preset_ensemble_identities':identity,'derived_function_source_sha256':sha(E/'predict158.py')}
 save(E/'results/derived_selection_views_sealed.json',manifest);return manifest

def run():
 require_time(new_long_task=True);p=verify_protocol();models.seed_all(0)
 if backend_policy()!=EXPECTED_BACKEND:raise RuntimeError('Frozen inference backend flags absent')
 m=read(E/'training/all_models_sealed.json');choices=read(E/'validation_selection_decisions.json');cs=read(E/'validation_selection_sealed.json')
 if not m['all_fixed_models_sealed'] or (m['optimization_stages'],m['final_models'])!=(66,36):raise RuntimeError('All66stages36models required')
 if not cs['all18_validation_only_choices_sealed'] or cs['decisions_sha256']!=sha(E/'validation_selection_decisions.json') or cs['target_labels_joined']!=0:raise RuntimeError('All validation choices sealed before native predictions required')
 device=torch.device('cuda');source={(r['arm'],r['seed']):r for r in m['models'] if r['suite']=='source'}
 AF={(r['arm'],r['seed'],r['outer']):r for r in m['models'] if r['suite']=='AF'};files={};count=0;cohorts={};started=time.monotonic();ph=sha(E/'protocol.json')
 for scope in COHORTS:
  ref=p['target_cohorts'][scope];ids=ref['sample_ids'];public=read(ref['public_records'])['records'];by={r['sample_id']:r for r in public}
  if [r['sample_id'] for r in public]!=ids:raise RuntimeError('Original source cohort changed')
  full=torch.load(ref['feature_source'],map_location='cpu',weights_only=False)['records'];data={s:full[s] for s in ids};del full
  for arm in ARMS:
   seeds=[]
   for seed in SOURCE_SEEDS:
    rec=source[arm,seed];path=prediction_path(scope,arm,seed)
    if path.exists():out=read(path)['predictions']
    else:
     model,scaler=load_model(rec,device);out=add_roles(predict(model,arm,ids,data,scaler,device),by)
     save(path,{'predictions':out,'cohort':scope,'arm':arm,'seed':seed,'preset_configuration':PROFILES[arm],
      'checkpoint_sha256':rec['checkpoint_sha256'],'protocol_sha256':ph,'target_labels_decoded':0,'original_ordinal_ranks':True})
     append(E/'physical_generation_events.jsonl',{'at_utc':now(),'kind':'SOURCE_NATIVE_OUTPUTS','path':str(path),'outputs':len(ids),'neural_model_record_scores':len(ids)})
     del model;gc.collect();torch.cuda.empty_cache()
    if set(out)!=set(ids):raise RuntimeError('Complete source outputs required')
    seeds.append(out);files[str(path)]=sha(path);count+=len(ids)
    status('PREDICTIONS_RUNNING',current_cohort=scope,current_arm=arm,current_seed=seed,new_ranker_outputs=count,target_label_values_joined=0)
   path=prediction_path(scope,arm);existed=path.exists();out=add_roles(ensemble(ids,seeds),by)
   save(path,{'predictions':out,'cohort':scope,'arm':arm,'seeds':list(SOURCE_SEEDS),'preset_configuration':PROFILES[arm],
    'all3_fixed_seeds_retained':True,'protocol_sha256':ph,'target_labels_decoded':0})
   if not existed:append(E/'physical_generation_events.jsonl',{'at_utc':now(),'kind':'SOURCE_PRESET_ENSEMBLE','path':str(path),'outputs':len(ids),'neural_model_record_scores':0})
   files[str(path)]=sha(path);count+=len(ids)
  cohorts[scope]={'n':len(ids),'sample_ids':ids,'outputs':8*len(ids)};del data;gc.collect()
 if count!=17240 or len(files)!=32:raise RuntimeError('17240 source native ranks/32files required')
 save(E/'results/source_predictions_sealed.json',{'files':files.copy(),'outputs':17240,'cohorts':cohorts,'protocol_sha256':ph,
  'model_seal_sha256':sha(E/'training/all_models_sealed.json'),'target_labels_joined':0,'all_seeds_retained':True})
 data=torch.load(p['AF_training_features'],map_location='cpu',weights_only=False)['records'];public=read(p['AF_public_records'])['records']
 ids=[r['sample_id'] for r in public];by={r['sample_id']:r for r in public};af_files={}
 for arm in ARMS:
  seeds=[]
  for seed in AF_SEEDS:
   joined={}
   for row in p['af_schedule']:
    if row['arm']!=arm or row['seed']!=seed:continue
    rec=AF[arm,seed,row['outer']];path=fold_prediction_path(arm,seed,row['outer'])
    if path.exists():out=read(path)['predictions']
    else:
     model,scaler=load_model(rec,device);out=add_roles(predict(model,arm,row['held_ids'],data,scaler,device),by)
     save(path,{'predictions':out,'arm':arm,'seed':seed,'outer':row['outer'],'preset_configuration':PROFILES[arm],
      'checkpoint_sha256':rec['checkpoint_sha256'],'protocol_sha256':ph,'inference_batches_sha256':row['inference_batches_sha256'],'held_labels_joined':0})
     append(E/'physical_generation_events.jsonl',{'at_utc':now(),'kind':'AF_NATIVE_FOLD_OUTPUTS','path':str(path),'outputs':len(out),'neural_model_record_scores':len(out)})
     del model;gc.collect();torch.cuda.empty_cache()
    if set(out)!=set(row['held_ids']) or set(joined)&set(out):raise RuntimeError('Native AF OOF collision')
    joined.update(out);af_files[str(path)]=sha(path);count+=len(out)
   if set(joined)!=set(ids):raise RuntimeError('Every native AF record once per presetseed required')
   path=prediction_path('AF',arm,seed)
   save(path,{'predictions':joined,'arm':arm,'seed':seed,'preset_configuration':PROFILES[arm],'exactly_one_OOF_per_record':True,
    'old_dev_labels_joined':0,'protocol_sha256':ph,'joined_entries_not_new_outputs':731})
   af_files[str(path)]=sha(path);seeds.append(joined)
  path=prediction_path('AF',arm);existed=path.exists();out=add_roles(ensemble(ids,seeds),by)
  save(path,{'predictions':out,'arm':arm,'seeds':list(AF_SEEDS),'preset_configuration':PROFILES[arm],'all3_fixed_seeds_retained':True,
   'exactly_one_OOF_per_record_per_seed':True,'old_dev_labels_joined':0,'protocol_sha256':ph})
  if not existed:append(E/'physical_generation_events.jsonl',{'at_utc':now(),'kind':'AF_PRESET_ENSEMBLE','path':str(path),'outputs':len(ids),'neural_model_record_scores':0})
  af_files[str(path)]=sha(path);count+=len(ids)
 if count!=23088 or len(af_files)!=38:raise RuntimeError('23088 native ranks/38AFfiles required')
 save(E/'results/AF_predictions_sealed.json',{'files':af_files,'outputs':5848,'records':731,'groups':716,'protocol_sha256':ph,
  'model_seal_sha256':sha(E/'training/all_models_sealed.json'),'target_labels_joined':0,'all_seeds_retained':True,
  'native_OOF_outputs':4386,'ensemble_outputs':1462,'joined_copy_entries_not_new_outputs':4386})
 native={'at_utc':now(),'files':{**files,**af_files},'outputs':23088,'source_outputs':17240,'AF_outputs':5848,'prediction_files':70,
  'model_scoring_record_outputs':17316,'three_seed_ensemble_outputs':5772,'all_fixed_outputs_sealed':True,'target_labels_joined':0,
  'protocol_sha256':ph,'model_seal_sha256':sha(E/'training/all_models_sealed.json'),'selection_seal_sha256':sha(E/'validation_selection_sealed.json'),
  'source_seal_sha256':sha(E/'results/source_predictions_sealed.json'),'AF_seal_sha256':sha(E/'results/AF_predictions_sealed.json')}
 save(E/'results/native_predictions_sealed.json',native);derived=derive_selected(p,choices,native)
 save(E/'results/all_predictions_sealed.json',{'at_utc':now(),'files':native['files'],'derived_files':derived['files'],'outputs':23088,
  'derived_selection_view_records':11544,'source_outputs':17240,'AF_outputs':5848,'prediction_files':70,'derived_prediction_files':20,
  'all_fixed_outputs_sealed':True,'all_derived_views_sealed':True,'target_labels_joined':0,'protocol_sha256':ph,
  'model_seal_sha256':sha(E/'training/all_models_sealed.json'),'selection_seal_sha256':sha(E/'validation_selection_sealed.json'),
  'native_prediction_seal_sha256':sha(E/'results/native_predictions_sealed.json'),'derived_selection_seal_sha256':sha(E/'results/derived_selection_views_sealed.json'),
  'elapsed_seconds':time.monotonic()-started})
 status('ALL_PREDICTIONS_SEALED',new_ranker_outputs=23088,derived_selection_view_records=11544,target_label_values_joined=0,
  next='evaluate158.py onlyafterbothnativeandderivedseals; frozenprimaryreadonly thenfinalize158.py')
 print(canonical({'Exp158':'native_and_derived_sealed','new_native_outputs':23088,'derived_views':11544,'target_labels_joined':0}),flush=True)

if __name__=='__main__':run()

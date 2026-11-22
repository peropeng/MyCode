"""Exact cached inputs and fit-only transforms; no target scoring here."""
from collections import defaultdict
import torch
import torch.nn.functional as F
from common import *
import context_models as models

def scaler_for(data,ids):
 values=torch.cat([data[s]['raw_structure'] for s in ids]);mean=values.mean(0);std=values.std(0,unbiased=False)
 return mean,torch.where(std<1e-6,torch.ones_like(std),std)
def mean_by_group(values,ids,by):
 grouped=defaultdict(list)
 for sid,v in zip(ids,values):grouped[by[sid]['task_group']].append(v)
 return torch.stack([torch.stack(v).mean() for v in grouped.values()]).mean()
def grouped_loss(model,arm,batch,labels,by):
 if arm=='SF_REF':
  h=model.tfe(batch['content'],batch['mask']);h=model.asi(h,batch['agent'],batch['mask'])
  logits,_=model.scoring(h,batch['mask']);targets=torch.tensor([labels[s] for s in batch['ids']],device=logits.device)
  ce=F.cross_entropy(logits.masked_fill(~batch['mask'],-1e9),targets,reduction='none')
  pred=model.scoring.temporal_head(h[:,:-1]);target=h[:,1:].detach();mask=batch['mask'][:,1:].unsqueeze(-1).float()
  temporal=((pred*mask-target*mask)**2).sum((1,2))/(mask.sum((1,2))+1e-6)
  values=ce+.9*temporal
 else:
  scores,_=models.forward(model,arm,batch)
  values=[F.cross_entropy(s[None],torch.tensor([labels[sid]],device=s.device)) for sid,s in zip(batch['ids'],scores)]
 return mean_by_group(values,batch['ids'],by)

def source_inputs():
 public=read(E134/'data/public_records.json')['records'];by={r['sample_id']:r for r in public}
 labels={r['sample_id']:r['target_ordinal'] for r in read(E134/'data/selected_train_labels.private.json')['labels']}
 ids={split:[r['sample_id'] for r in public if r['optimization_split']==split and r['sample_id'] in labels] for split in ('train','validation')}
 data=torch.load(E134/'features/train_validation_features.pt',map_location='cpu',weights_only=False)['records']
 if (len(ids['train']),len(ids['validation']),len(data),len(labels))!=(492,122,614,614):raise RuntimeError('Exact source492/122 mismatch')
 if set(data)!=set(labels) or set(by[s]['task_group'] for s in ids['train'])&set(by[s]['task_group'] for s in ids['validation']):raise RuntimeError('Source groups/features mismatch')
 return data,labels,ids,by,scaler_for(data,ids['train'])
def af_inputs():
 public=read(E138/'data/public_records.json')['records'];by={r['sample_id']:r for r in public}
 data=torch.load(E138/'features/development_features.pt',map_location='cpu',weights_only=False)['records']
 labels=read(E138/'data/development_labels.private.json')['labels']
 if len(data)!=731 or len({r['task_group'] for r in public})!=716 or set(data)!=set(labels) or set(data)!=set(by):raise RuntimeError('AF731/716 scope mismatch')
 return data,labels,by
def af_schedule(public,folds):
 schedule=[]
 for arm in ARMS:
  for seed in AF_SEEDS:
   for fold in folds[str(seed)]:
    row={'arm':arm,'seed':seed,**fold}
    for name,groupkey in [('selection_fit_ids','inner_fit_groups'),('validation_ids','validation_groups'),('refit_ids','refit_groups'),('held_ids','held_groups')]:
     groups=set(fold[groupkey]);row[name]=[r['sample_id'] for r in public if r['task_group'] in groups]
    if set(row['selection_fit_ids'])&set(row['validation_ids']) or set(row['refit_ids'])&set(row['held_ids']):raise RuntimeError('AF nested leakage')
    if set(row['selection_fit_ids'])|set(row['validation_ids'])!=set(row['refit_ids']) or len(row['held_ids'])+len(row['refit_ids'])!=731:raise RuntimeError('AF incomplete partition')
    row['inference_batches_sha256']=digest([row['held_ids'][i:i+16] for i in range(0,len(row['held_ids']),16)])
    schedule.append(row)
 if len(schedule)!=90:raise RuntimeError('AF schedule must contain90 pairs')
 for arm in ARMS:
  for seed in AF_SEEDS:
   ids=[sid for r in schedule if r['arm']==arm and r['seed']==seed for sid in r['held_ids']]
   if len(ids)!=731 or len(set(ids))!=731:raise RuntimeError('Every AF record must have exactly1 OOF output per seed')
 return schedule

def prepare():
 require_time(new_long_task=True)
 if read(E/'approved_plan.json')['primary']!='AB_GLOBAL':raise RuntimeError('Frozen primary changed')
 source_p=read(E134/'training_protocol.json');protected={**source_p['sources'],**source_p['input_hashes']}
 af_p=read(E138/'protocol.json');protected.update(af_p['sources']);protected.update(af_p['inputs'])
 for root in (E136,E137,E138,E142,E143):
  for name in ('main_decision_packet.json','final_execution_audit.json','comparison.json','resource_audit.json'):
   p=root/name
   if p.exists():protected[str(p)]=sha(p)
 for root in (E134,E143):
  seal=root/'training/model_seal.json'
  if seal.exists():
   protected[str(seal)]=sha(seal)
   for r in read(seal).get('models',[]):
    p=Path(r['checkpoint']);protected[str(p)]=sha(p)
 protected[str(API/'requests.jsonl')]=sha(API/'requests.jsonl');check_hashes(protected)
 data,labels,ids,by,scaler=source_inputs();public=read(E138/'data/public_records.json')['records'];folds=read(E138/'data/folds.json')
 schedule=af_schedule(public,folds);old_schedule=af_p['schedule']
 for row in schedule:
  base='StepFinder' if row['arm']=='SF_REF' else 'AB'
  old=next(r for r in old_schedule if r['arm']==base and r['seed']==row['seed'] and r['outer']==row['outer'])
  for key in ('selection_fit_ids','validation_ids','refit_ids','held_ids','initialization_seed','inference_batches_sha256'):
   if row[key]!=old[key]:raise RuntimeError('Original AF nested schedule changed: '+key)
 target_sources=read(E143/'data/cohort_sources.json')
 for cohort in COHORTS:
  ref=target_sources[cohort]
  for key,hashkey in [('feature_source','feature_source_sha256'),('label_source','label_source_sha256'),('historical_predictions','historical_predictions_sha256')]:
   protected[ref[key]]=ref[hashkey]
  protected[ref['public_records']]=sha(ref['public_records']);protected[ref['manifest']]=sha(ref['manifest'])
 check_hashes(protected)
 base={'at_utc':now(),'status':'INPUTS_AND_FIXED_SCHEDULE_READY','approved_plan_sha256':sha(E/'approved_plan.json'),
  'source_ids':ids,'source_schedule':[{'suite':'source','arm':a,'seed':s,'initialization_seed':s} for a in ARMS for s in SOURCE_SEEDS],
  'af_schedule':schedule,'target_cohorts':target_sources,'source_training_features':str(E134/'features/train_validation_features.pt'),
  'AF_training_features':str(E138/'features/development_features.pt'),'protected_old_files_sha256':protected,
  'arms':list(ARMS),'source_seeds':list(SOURCE_SEEDS),'AF_seeds':list(AF_SEEDS),'max_epochs':40,'patience':8,'batch_tasks_or_complete_groups':16,
  'source_epoch_order_rule':'Random(seed*100+epoch) shuffles original492 IDs','AF_epoch_order_rule':'Random(initialization_seed*100+epoch) shuffles sorted complete groups',
  'source_training_rng':'Original134 RNG after canonical model creation; added context constructor restores exact originalAB RNG; SF original independent constructor RNG',
  'selection':'source122 Top1/MRR/earliest; AF inner group-equal Top1/MRR/earliest','AF_scaler':'Fit-only3fold selection; fit-only4fold fresh refit, no held nodes',
  'source_scaler':'original492 node statistics only','parameters':{a:sum(p.numel() for p in models.create(a).parameters()) for a in ARMS},
  'independent_context_initialization_seed_offset':153000,'float32_no_amp_no_tf32':True,'single_GPU_training_process':True,
  'source_target_outputs':51720,'AF_target_outputs':17544,'max_optimization_stages':198,'final_models':108,
  'new_encoder_API_download_Gold_independent_task':0,'no_target_label_join_before_both_prediction_seals':True,
  'deadline_utc':'2026-10-07T02:00:00Z','deadline_beijing':'2026-10-07T10:00:00+08:00'}
 if base['parameters']!={'AB_GLOBAL':337457,'AB_LOCAL':337457,'AB_STATIC':337457,'AB_VALUE_PERM':337457,'AB_REF':300593,'SF_REF':277633}:raise RuntimeError('Wrong parameter counts')
 atomic(E/'prepared_inputs.json',base)
 status('INPUTS_PREPARED',next='Behaviorfixtures and initialization/code/schedule freeze; then all198 stages and108 models.')
 print(canonical({'source_train492_val122':True,'AF_90_selection_refit_pairs':len(schedule),'old_protected_assets':len(protected),'parameters':base['parameters']}),flush=True)

if __name__=='__main__':prepare()

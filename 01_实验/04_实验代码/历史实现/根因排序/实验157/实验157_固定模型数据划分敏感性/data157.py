"""Exact cached inputs and fit-only transforms; no target scoring here."""
from collections import defaultdict
import torch
import torch.nn.functional as F
from common import *
import models157 as models

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
 return data,labels,ids,by
def af_inputs():
 public=read(E138/'data/public_records.json')['records'];by={r['sample_id']:r for r in public}
 data=torch.load(E138/'features/development_features.pt',map_location='cpu',weights_only=False)['records']
 labels=read(E138/'data/development_labels.private.json')['labels']
 if len(data)!=731 or len({r['task_group'] for r in public})!=716 or set(data)!=set(labels) or set(data)!=set(by):raise RuntimeError('AF731/716 scope mismatch')
 return data,labels,by

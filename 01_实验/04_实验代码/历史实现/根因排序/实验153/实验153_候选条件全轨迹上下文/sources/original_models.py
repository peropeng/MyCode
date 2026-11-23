"""Owned event residual and Exp130 relations; StepFinder stays independent."""
import sys
import torch
from torch import nn
import torch.nn.functional as F
from common import E
sys.path.insert(0,str(E/'sources'))
from owned_exp130_model import RelationLayer
from stepfinder_model import StepFinder,compute_loss as stepfinder_loss

class EventResidual(nn.Module):
    def __init__(self):
        super().__init__()
        self.projections=nn.ModuleList([nn.Linear(257,183) for _ in range(2)])
        self.gates=nn.ModuleList([nn.Linear(257,1) for _ in range(2)])
    def forward(self,x,partner,valid):
        content=x[:,:128];update=torch.zeros_like(x)
        for direction in range(2):
            linked=content[partner[:,direction]];flag=valid[:,direction:direction+1]
            evidence=torch.cat([linked,linked-content,flag],-1)
            update=update+F.gelu(self.projections[direction](evidence))*torch.sigmoid(self.gates[direction](evidence))*flag
        return x+update

class NodeLayer(nn.Module):
    def __init__(self,hidden,dropout):
        super().__init__()
        self.ff=nn.Sequential(nn.Linear(hidden,hidden),nn.GELU(),nn.Dropout(dropout),nn.Linear(hidden,hidden))
        self.norm=nn.LayerNorm(hidden);self.dropout=nn.Dropout(dropout)
    def forward(self,h,adj):return self.norm(h+self.dropout(self.ff(h)))

class Ranker(nn.Module):
    def __init__(self,arm,hidden=96,dropout=.15):
        super().__init__()
        if arm not in ('N','A','B','AB'):raise ValueError('owned_factorial_arm_required')
        self.arm=arm;self.event=EventResidual() if arm in ('A','AB') else None
        self.project=nn.Sequential(nn.Linear(183,hidden),nn.GELU(),nn.Dropout(dropout))
        layer=RelationLayer if arm in ('B','AB') else NodeLayer
        self.layers=nn.ModuleList([layer(hidden,dropout) for _ in range(2)])
        self.head=nn.Sequential(nn.Linear(4*hidden,hidden),nn.GELU(),nn.Dropout(dropout),nn.Linear(hidden,1))
    def forward(self,x,adj,task_index,lengths,partner,paired_valid):
        if self.event is not None:x=self.event(x,partner,paired_valid)
        initial=self.project(x);h=initial
        for layer in self.layers:h=layer(h,adj)
        membership=F.one_hot(task_index,num_classes=len(lengths)).to(h.dtype)
        mean=(membership.T@h)/lengths[:,None];context=mean[task_index]
        return self.head(torch.cat([h,initial,context,h-context],-1)).squeeze(-1)

def create(arm):return StepFinder() if arm=='StepFinder' else Ranker(arm)

def collate(ids,features,scaler,device):
    entries=[features[sid] for sid in ids];lengths=[len(r['content']) for r in entries]
    offsets=[];total=0
    for n in lengths:offsets.append(total);total+=n
    x=[];partners=[];valid=[];adj=[([],[]) for _ in range(4)]
    mean,std=scaler
    for entry,offset in zip(entries,offsets):
        normalized=torch.cat([F.normalize(entry['content'],dim=-1),F.normalize(entry['agent'],dim=-1),
            ((entry['raw_structure']-mean)/std).clamp(-10,10)],-1)
        x.append(normalized);partners.append(entry['paired_partner']+offset);valid.append(entry['paired_valid'])
        for r,(index,mask) in enumerate(entry['adjacency']):adj[r][0].append(index+offset);adj[r][1].append(mask)
    padded=max(lengths);content=torch.zeros(len(ids),padded,128);agent=torch.zeros(len(ids),padded,32);mask=torch.zeros(len(ids),padded,dtype=torch.bool)
    for i,(entry,n) in enumerate(zip(entries,lengths)):
        content[i,:n]=entry['content'];agent[i,:n]=entry['agent'];mask[i,:n]=True
    return {'ids':ids,'lengths':torch.tensor(lengths,device=device),
        'x':torch.cat(x).to(device),'adjacency':[(torch.cat(index).to(device),torch.cat(mask).to(device)) for index,mask in adj],
        'task_index':torch.repeat_interleave(torch.arange(len(ids)),torch.tensor(lengths)).to(device),
        'partner':torch.cat(partners).to(device),'paired_valid':torch.cat(valid).to(device),
        'content':content.to(device),'agent':agent.to(device),'mask':mask.to(device)}

def forward(model,arm,batch):
    if arm=='StepFinder':
        logits,temporal=model(batch['content'],batch['agent'],batch['mask'])
        scores=[logits[i,:int(n)] for i,n in enumerate(batch['lengths'])]
        return scores,(logits,temporal)
    flat=model(batch['x'],batch['adjacency'],batch['task_index'],batch['lengths'],batch['partner'],batch['paired_valid'])
    return list(torch.split(flat,batch['lengths'].cpu().tolist())),None

def loss(scores,extra,arm,batch,labels):
    targets=[labels[sid] for sid in batch['ids']]
    if arm=='StepFinder':
        logits,temporal=extra;onehot=torch.zeros_like(logits)
        onehot[torch.arange(len(targets),device=logits.device),torch.tensor(targets,device=logits.device)]=1
        return stepfinder_loss(logits,onehot,batch['mask'],temporal,lambda_temporal=.9)
    return torch.stack([F.cross_entropy(score[None],torch.tensor([target],device=score.device)) for score,target in zip(scores,targets)]).mean()

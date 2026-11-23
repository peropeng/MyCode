"""Own semantic residual multirelation graph ranker, no baseline implementation."""
import torch
from torch import nn
import torch.nn.functional as F

class RelationLayer(nn.Module):
    def __init__(self,hidden,dropout):
        super().__init__()
        self.messages=nn.ModuleList([nn.Linear(2*hidden,hidden) for _ in range(4)])
        self.gates=nn.ModuleList([nn.Linear(2*hidden,1) for _ in range(4)])
        self.relation=nn.Linear(hidden,4)
        self.norm=nn.LayerNorm(hidden)
        self.dropout=nn.Dropout(dropout)
    def forward(self,h,adj):
        # Sparse neighbor lists padded to each relation's maximum degree (<=2).
        messages=[]
        for r in range(4):
            neighbor,valid=adj[r]
            sender=h[neighbor]; receiver=h[:,None,:].expand_as(sender)
            difference=sender-receiver
            value=F.gelu(self.messages[r](torch.cat([sender,difference],-1)))
            gate=torch.sigmoid(self.gates[r](torch.cat([receiver,difference],-1)))
            value=(value*gate*valid[:,:,None]).sum(1)/valid.sum(1).clamp_min(1)[:,None]
            messages.append(value)
        weights=torch.softmax(self.relation(h),-1)
        update=(torch.stack(messages,1)*weights[:,:,None]).sum(1)
        return self.norm(h+self.dropout(update))

class Ranker(nn.Module):
    def __init__(self,variant,hidden=96,dropout=.15):
        super().__init__()
        self.project=nn.Sequential(nn.Linear(183,hidden),nn.GELU(),nn.Dropout(dropout))
        self.layers=nn.ModuleList([RelationLayer(hidden,dropout) for _ in range(2)] if variant=='semantic_graph' else [])
        self.head=nn.Sequential(nn.Linear(4*hidden,hidden),nn.GELU(),nn.Dropout(dropout),nn.Linear(hidden,1))
    def forward(self,x,adj,task_index,lengths):
        initial=self.project(x); h=initial
        for layer in self.layers: h=layer(h,adj)
        # One-hot matrix multiply gives deterministic task sums on CUDA.
        membership=F.one_hot(task_index,num_classes=len(lengths)).to(h.dtype)
        mean=(membership.T@h)/lengths[:,None]
        context=mean[task_index]
        return self.head(torch.cat([h,initial,context,h-context],-1)).squeeze(-1)

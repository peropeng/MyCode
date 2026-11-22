"""Exact original architectures; paper presets with valid canonical153 SF INITIAL states."""
import random
import numpy as np
import torch
from common import *
import context_base as legacy

def seed_all(seed):
 legacy.seed_all(seed)
 # Flush lazy CUDA seed callbacks before any canonical RNG capture/restore.
 if torch.cuda.is_available():torch.cuda.get_rng_state_all()

rng_state=legacy.rng_state
restore_rng=legacy.restore_rng
state_digest=legacy.state_digest
collate=legacy.collate
def backend_policy():
 return {'deterministic_algorithms':torch.are_deterministic_algorithms_enabled(),'cudnn_deterministic':torch.backends.cudnn.deterministic,
  'cudnn_benchmark':torch.backends.cudnn.benchmark,'matmul_allow_tf32':torch.backends.cuda.matmul.allow_tf32,
  'cudnn_allow_tf32':torch.backends.cudnn.allow_tf32,'num_threads':torch.get_num_threads()}

def rng_digest(state):
 return {'python':digest(state['python']),'numpy':digest([state['numpy'][0],state['numpy'][1].tolist(),*state['numpy'][2:]]),
  'torch':state_digest({'torch':state['torch']}),'cuda':state_digest({str(i):v for i,v in enumerate(state['cuda'])})}

def actual_model_configuration(model):
 return {'parameters':sum(p.numel() for p in model.parameters()),'alpha':model.asi.alpha,'beta':model.scoring.beta,'gamma':model.scoring.gamma,'scales':list(model.scoring.scales)}

def require_model_configuration(model,arm):
 expected={k:PROFILES[arm][k] for k in ('parameters','alpha','beta','gamma','scales')}
 actual=actual_model_configuration(model)
 if actual!=expected:raise RuntimeError('Explicit paper preset configuration changed: '+arm)
 return actual

def create(arm):
 if arm not in ARMS:raise ValueError('Frozen158 preset required')
 cfg=PROFILES[arm]
 model=legacy.original.StepFinder(content_dim=128,agent_dim=32,hidden_dim=64,num_heads=2,head_dim=32,dropout=.5,alpha=cfg['alpha'],beta=cfg['beta'],gamma=cfg['gamma'],scales=list(cfg['scales']))
 require_model_configuration(model,arm);return model

def variant_features(arm,data):return data

def forward(model,arm,batch):return legacy.original.forward(model,'StepFinder',batch)

def loss(scores,extra,arm,batch,labels):
 logits,temporal=extra;targets=[labels[sid] for sid in batch['ids']];onehot=torch.zeros_like(logits)
 onehot[torch.arange(len(targets),device=logits.device),torch.tensor(targets,device=logits.device)]=1
 return legacy.original.stepfinder_loss(logits,onehot,batch['mask'],temporal,lambda_temporal=PROFILES[arm]['lambda_temporal'])

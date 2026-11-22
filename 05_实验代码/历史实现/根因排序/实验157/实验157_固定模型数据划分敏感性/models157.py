"""Exact original architectures; canonical153 INITIAL states loaded only by trainer."""
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

def create(arm):
 if arm not in ARMS:raise ValueError('Frozen157 arm required')
 return legacy.create(arm)

def variant_features(arm,data):return data

def forward(model,arm,batch):return legacy.forward(model,arm,batch)
def loss(scores,extra,arm,batch,labels):return legacy.loss(scores,extra,arm,batch,labels)

"""Original AB representation/head; exactly four candidate context readouts."""
import hashlib,math,random,sys,os
os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
import numpy as np
import torch
from torch import nn
import torch.nn.functional as F
from common import E,CONTEXT_ARMS
sys.path.insert(0,str(E/'sources'))
import original_models as original
PERM_SALT='Exp153-value-perm-v1|'

def value_permutation(sample_id,n,device=None):
 if n<1:raise ValueError('Empty trajectory')
 shift=0 if n==1 else 1+int.from_bytes(hashlib.sha256((PERM_SALT+sample_id).encode()).digest(),'big')%(n-1)
 return (torch.arange(n,device=device)+shift)%n

def attention_mask(task_index,adj,mode):
 same=task_index[:,None]==task_index[None,:]
 if mode!='AB_LOCAL':return same
 n=len(task_index);direct=torch.zeros((n,n),device=task_index.device,dtype=torch.bool)
 receiver=torch.arange(n,device=task_index.device)
 for index,valid in adj:
  for col in range(index.shape[1]):
   flags=valid[:,col]>0
   direct[receiver[flags],index[:,col][flags]]=True
 direct=direct&same
 second=(direct.float()@direct.float())>0
 return (torch.eye(n,device=task_index.device,dtype=torch.bool)|direct|second)&same

class ContextRanker(original.Ranker):
 def __init__(self,mode):
  if mode not in CONTEXT_ARMS:raise ValueError('Fixed context arm required')
  super().__init__('AB',hidden=96,dropout=.15);self.mode=mode
  self.Q=nn.Linear(96,96,bias=False);self.K=nn.Linear(96,96,bias=False)
  self.V=nn.Linear(96,96,bias=False);self.O=nn.Linear(96,96,bias=False)
  nn.init.zeros_(self.O.weight)
 def context_readout(self,h,adj,task_index,lengths,sample_ids):
  membership=F.one_hot(task_index,num_classes=len(lengths)).to(h.dtype)
  mean=(membership.T@h)/lengths[:,None];means=mean[task_index]
  q=self.Q(mean)[task_index] if self.mode=='AB_STATIC' else self.Q(h)
  k=self.K(h);v=self.V(h)
  if self.mode=='AB_VALUE_PERM':
   if sample_ids is None or len(sample_ids)!=len(lengths):raise ValueError('Public IDs needed for fixed value permutation')
   permutations=[];offset=0
   for sid,n in zip(sample_ids,lengths.detach().cpu().tolist()):
    permutations.append(value_permutation(sid,int(n),h.device)+offset);offset+=int(n)
   v=v[torch.cat(permutations)]
  allowed=attention_mask(task_index,adj,self.mode)
  weights=torch.softmax(((q@k.T)/math.sqrt(96)).masked_fill(~allowed,-torch.inf),dim=-1)
  z=weights@v
  return means+self.O(z-self.V(means))
 def forward(self,x,adj,task_index,lengths,partner,paired_valid,sample_ids=None):
  x=self.event(x,partner,paired_valid);initial=self.project(x);h=initial
  for layer in self.layers:h=layer(h,adj)
  context=self.context_readout(h,adj,task_index,lengths,sample_ids)
  return self.head(torch.cat([h,initial,context,h-context],-1)).squeeze(-1)

def seed_all(seed):
 random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
 if torch.cuda.is_available():torch.cuda.manual_seed_all(seed)
 torch.backends.cudnn.deterministic=True;torch.backends.cudnn.benchmark=False
 torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
 torch.use_deterministic_algorithms(True);torch.set_num_threads(4)
def rng_state():
 return {'python':random.getstate(),'numpy':np.random.get_state(),'torch':torch.get_rng_state(),'cuda':torch.cuda.get_rng_state_all() if torch.cuda.is_available() else []}
def restore_rng(state):
 random.setstate(state['python']);np.random.set_state(state['numpy']);torch.set_rng_state(state['torch'])
 if torch.cuda.is_available():torch.cuda.set_rng_state_all(state['cuda'])
def state_digest(state):
 h=hashlib.sha256()
 for name,value in sorted(state.items()):
  v=value.detach().cpu().contiguous();h.update(name.encode());h.update(str(v.dtype).encode());h.update(str(list(v.shape)).encode());h.update(v.numpy().tobytes())
 return h.hexdigest()
def create(arm):
 return original.create('StepFinder' if arm=='SF_REF' else 'AB') if arm in ('AB_REF','SF_REF') else ContextRanker(arm)
def create_initialized(arm,seed):
 seed_all(seed)
 if arm=='SF_REF':
  model=create(arm);return model,rng_state(),{'canonical_seed':seed,'state_digest':state_digest(model.state_dict()),'independent_context_seed':None}
 base=create('AB_REF');base_state={k:v.clone() for k,v in base.state_dict().items()};training_rng=rng_state()
 if arm=='AB_REF':return base,training_rng,{'canonical_seed':seed,'state_digest':state_digest(base_state),'independent_context_seed':None}
 seed_all(seed+153000);model=create(arm);state=model.state_dict()
 for k,v in base_state.items():state[k]=v.clone()
 model.load_state_dict(state);restore_rng(training_rng)
 return model,training_rng,{'canonical_seed':seed,'independent_context_seed':seed+153000,'base_state_digest':state_digest(base_state),'state_digest':state_digest(model.state_dict()),'O_zero':True}
collate=original.collate
def forward(model,arm,batch):
 if arm in ('AB_REF','SF_REF'):return original.forward(model,'StepFinder' if arm=='SF_REF' else 'AB',batch)
 flat=model(batch['x'],batch['adjacency'],batch['task_index'],batch['lengths'],batch['partner'],batch['paired_valid'],sample_ids=batch['ids'])
 return list(torch.split(flat,batch['lengths'].detach().cpu().tolist())),None
def loss(scores,extra,arm,batch,labels):return original.loss(scores,extra,'StepFinder' if arm=='SF_REF' else 'AB',batch,labels)
def variant_features(arm,data):return data

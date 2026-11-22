import json,sys,time,subprocess
import runner
from runner import ASSETS,HERE,publish,sha
import torch
sys.path.insert(0,str(ASSETS/'StepFinder'))
from Q3Emb import Qwen3Embedding
from model import StepFinder,compute_loss
start=time.monotonic()
assert sha(ASSETS/'Qwen3-Embedding-0.6B/model.safetensors')=='0437e45c94563b09e13cb7a64478fc406947a93cb34a7e05870fc8dcd48e23fd'
runner.seed_all(20260816)
enc=Qwen3Embedding(str(ASSETS/'Qwen3-Embedding-0.6B'),model_revision=None)
x=enc.encode(['Synthetic agent searches a file.','Synthetic agent runs a test.','Synthetic agent reads a result.'],dim=128).float()
a=enc.encode(['role_0','role_1','role_0'],dim=32).float()
del enc
model=StepFinder().cuda(); mask=torch.ones(1,3,dtype=torch.bool,device='cuda'); y=torch.tensor([[0,1,0]],device='cuda')
score,tl=model(x.unsqueeze(0),a.unsqueeze(0),mask); loss=compute_loss(score,y,mask,tl); loss.backward()
assert torch.isfinite(score).all() and torch.isfinite(loss)
e,records,boundary=runner.data()
fold_checks=[]
for seed in (20260816,20260817,20260818):
    folds=e.E96._fold_groups(sorted({r['task_group'] for r in records}),seed)
    assert len(set(g for f in folds for g in f))==sum(map(len,folds))==716
    fold_checks.append({'seed':seed,'sizes':list(map(len,folds)),'groups_disjoint':True})
report={'torch':torch.__version__,'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(),'capability':list(torch.cuda.get_device_capability()),'synthetic_embedding_shape':list(x.shape),'synthetic_forward_backward_finite':True,'model_weight_sha256':sha(ASSETS/'Qwen3-Embedding-0.6B/model.safetensors'),'peak_gpu_bytes':torch.cuda.max_memory_allocated(),'seconds':time.monotonic()-start,'folds':fold_checks,'development_boundary':boundary,'packages':subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True).splitlines(),'science_results_exposed':False}
publish(HERE/'results/smoke.json',report)
print(json.dumps({k:v for k,v in report.items() if k not in ['packages','development_boundary']}))

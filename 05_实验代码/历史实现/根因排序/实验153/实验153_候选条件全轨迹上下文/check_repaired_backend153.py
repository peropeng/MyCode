"""Artificial CUDA loss/gradient repeatability; zero optimizer updates/real data."""
import torch
from common import *
import context_models as models
import trainer153 as training
def run():
 require_time(new_test=True);details=[];counts={'CUDA_model_forwards':0,'backward_calls':0,'optimizer_updates':0,'real_records':0,'real_Gold':0}
 for arm in ('AB_GLOBAL','SF_REF'):
  row=next(r for r in read(E/'protocol.json')['source_schedule'] if r['arm']==arm and r['seed']==SOURCE_SEEDS[0])
  model,opt=training.initial_model(row,torch.device('cuda'));del opt
  n=4;index=torch.tensor([[1,0],[0,1],[3,2],[2,3]],device='cuda');valid=torch.ones(4,2,device='cuda')
  batch={'ids':['artificial_backend0','artificial_backend1'],'x':torch.randn(n,183,device='cuda'),
   'lengths':torch.tensor([2,2],device='cuda'),'task_index':torch.tensor([0,0,1,1],device='cuda'),
   'adjacency':[(index.clone(),valid.clone()) for _ in range(4)],'partner':index.clone(),'paired_valid':valid.clone(),
   'content':torch.randn(2,2,128,device='cuda'),'agent':torch.randn(2,2,32,device='cuda'),'mask':torch.ones(2,2,dtype=torch.bool,device='cuda')}
  labels={'artificial_backend0':0,'artificial_backend1':1};rng=models.rng_state();outputs=[]
  for repeat in range(2):
   models.restore_rng(rng);model.zero_grad(set_to_none=True);model.train();scores,extra=models.forward(model,arm,batch);counts['CUDA_model_forwards']+=1
   loss=models.loss(scores,extra,arm,batch,labels);loss.backward();counts['backward_calls']+=1
   if not torch.isfinite(loss) or training.backend_policy()!=training.EXPECTED_BACKEND:raise RuntimeError('Repaired backend artificial CUDA failure')
   grads={k:p.grad.detach().cpu().clone() for k,p in model.named_parameters() if p.grad is not None}
   if any(v.dtype!=torch.float32 or not torch.isfinite(v).all() for v in grads.values()):raise RuntimeError('Invalid/artificial gradient dtype')
   outputs.append((torch.cat(scores).detach().cpu(),models.state_digest(grads),float(loss.detach())))
  if not torch.equal(outputs[0][0],outputs[1][0]) or outputs[0][1:]!=outputs[1][1:]:raise RuntimeError('Artificial CUDA score/loss/gradient not exactly repeatable')
  details.append({'arm':arm,'same_frozen_initial_weights':True,'exact_repeatable_scores_loss_and_gradients':True,'float32_gradients':True,'runtime_backend_policy':training.backend_policy()})
  del model;torch.cuda.empty_cache()
 receipt={'at_utc':now(),'status':'PASS_REPAIRED_CUDA_LOSS_AND_GRADIENT_REPEATABILITY','test_cases':2,'details':details,'counters':counts,
  'source_sha256':{str(E/n):sha(E/n) for n in ('trainer153.py','context_models.py','check_repaired_backend153.py')},
  'no_real_data_old_trained_weights_or_evaluation_labels_read':True,'new_encoder_API_download_Gold':0}
 write_new(E/'runtime_CUDA_repair_check.json',receipt);print(canonical(receipt),flush=True)
if __name__=='__main__':run()

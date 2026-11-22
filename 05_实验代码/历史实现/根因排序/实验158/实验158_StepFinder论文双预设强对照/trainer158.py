"""Exact source and nested AF optimizations; held scoring is deferred."""
import argparse,gc,random
from collections import defaultdict
import numpy as np
import torch
from common import *
import models158 as models
from data158 import source_inputs,af_inputs,scaler_for,grouped_loss

def torch_atomic(path,value):
 path=_output_local(path);tmp=path.with_name(path.name+f'.{os.getpid()}.tmp')
 torch.save(value,tmp);os.replace(tmp,path)
def _output_local(path):
 path=Path(path).resolve()
 if not path.is_relative_to(E):raise ValueError('Exp158 torch writes only')
 path.parent.mkdir(parents=True,exist_ok=True);return path
def cpu_state(model):return {k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
def backend_policy():
 return {'deterministic_algorithms':torch.are_deterministic_algorithms_enabled(),'cudnn_deterministic':torch.backends.cudnn.deterministic,
  'cudnn_benchmark':torch.backends.cudnn.benchmark,'matmul_allow_tf32':torch.backends.cuda.matmul.allow_tf32,
  'cudnn_allow_tf32':torch.backends.cudnn.allow_tf32,'num_threads':torch.get_num_threads()}
EXPECTED_BACKEND={'deterministic_algorithms':True,'cudnn_deterministic':True,'cudnn_benchmark':False,'matmul_allow_tf32':False,'cudnn_allow_tf32':False,'num_threads':4}
def folder_for(row):
 return E/'training'/row['suite']/row['arm']/(str(row['seed']) if row['suite']=='source' else f"{row['seed']}_{row['outer']}")
def all_schedule(prepared):return prepared['source_schedule']+[{'suite':'AF',**r} for r in prepared['af_schedule']]
def verify_protocol():
 p=read(E/'protocol.json');check_hashes(p['training_sources']);check_hashes(p['inputs']);check_hashes(p['initializations'])
 return p
@torch.no_grad()
def predict(model,arm,ids,data,scaler,device):
 model.eval();out={}
 for off in range(0,len(ids),16):
  require_time();batch=models.collate(ids[off:off+16],data,scaler,device);scores,_=models.forward(model,arm,batch)
  for sid,score in zip(batch['ids'],scores):
   if not bool(torch.isfinite(score).all()):raise RuntimeError('Nonfinite score')
   logits=score.cpu();order=sorted(range(len(logits)),key=lambda i:(-float(logits[i]),i))
   out[sid]={'scores':logits.tolist(),'probabilities':torch.softmax(logits,0).tolist(),'order':order,'chosen_step':order[0],'valid':True,'native_complete_ranking':True}
 return out
def validation_metric(pred,labels,by,group_equal):
 values=defaultdict(list)
 for sid,v in pred.items():
  rank=v['order'].index(labels[sid])+1;key=by[sid]['task_group'] if group_equal else sid
  values[key].append((float(rank==1),1/rank))
 means=np.array([np.array(v).mean(0) for v in values.values()]).mean(0)
 return {'Top1':float(means[0]),'MRR':float(means[1]),'records':len(pred),'groups':len(values),'group_equal':group_equal}
def initial_model(row,device):
 models.seed_all(row['initialization_seed'])
 if backend_policy()!=EXPECTED_BACKEND:raise RuntimeError('Frozen runtime backend policy not active')
 initial_path=Path(row['initialization_path']);initial_sha=sha(initial_path)
 ck=torch.load(initial_path,map_location='cpu',weights_only=False)
 model=models.create(row['arm']).to(device);model.load_state_dict(ck['state_dict']);actual_config=models.require_model_configuration(model,row['arm']);models.restore_rng(ck['training_rng'])
 expected_rng=models.rng_digest(ck['training_rng'])
 if models.rng_digest(models.rng_state())!=expected_rng or models.state_digest(model.state_dict())!=ck['info']['state_digest']:raise RuntimeError('Actual canonical INITIAL state/training RNG restoration failed')
 binding={'initialization_path':str(initial_path),'initialization_sha256':initial_sha,'initialization_state_digest':ck['info']['state_digest'],'initialization_training_rng_digest':expected_rng,'actual_canonical_training_RNG_restored':True,'trained_parent_weight_loads':0,'invalid_runtime_asset_loads':0}
 opt=torch.optim.AdamW(model.parameters(),lr=PROFILES[row['arm']]['lr'],weight_decay=.00001)
 binding.update(actual_model_configuration=actual_config,actual_preset_configuration=PROFILES[row['arm']],actual_lr=opt.param_groups[0]['lr'],actual_weight_decay=opt.param_groups[0]['weight_decay'],lambda_temporal=PROFILES[row['arm']]['lambda_temporal'])
 return model,opt,binding

def fit(row,stage,fit_ids,val_ids,data,labels,by,device,base_stages,base_updates,fixed_epochs=None):
 folder=folder_for(row);receiptpath=folder/(stage+'.json');protocol_hash=sha(E/'protocol.json')
 if receiptpath.exists():
  rec=read(receiptpath)
  if rec['protocol_sha256']!=protocol_hash or rec['fit_ids_sha256']!=digest(fit_ids) or sha(rec['checkpoint'])!=rec['checkpoint_sha256']:raise RuntimeError('Completed stage binding changed')
  return rec
 require_time(new_long_task=True);data=models.variant_features(row['arm'],data);model,opt,initial_binding=initial_model(row,device);scaler=scaler_for(data,fit_ids)
 resume_path=folder/(stage+'_resume.pt');best=(-1.,-1.);best_epoch=None;stagnant=0;history=[];updates=0;first=1
 if resume_path.exists():
  ck=torch.load(resume_path,map_location='cpu',weights_only=False)
  if ck['protocol_sha256']!=protocol_hash or ck['fit_ids_sha256']!=digest(fit_ids):raise RuntimeError('Resume binding changed')
  model.load_state_dict(ck['state_dict']);opt.load_state_dict(ck['optimizer']);models.restore_rng(ck['rng'])
  best=tuple(ck['best']);best_epoch=ck['best_epoch'];stagnant=ck['stagnant'];history=ck['history'];updates=ck['updates'];first=ck['epoch']+1
 groups=defaultdict(list)
 for sid in fit_ids:groups[by[sid]['task_group']].append(sid)
 started=time.monotonic();checkpoint=folder/(stage+'_selected.pt' if val_ids else stage+'_checkpoint.pt');current_epoch=first-1;partial=0
 try:
  for epoch in range(first,(PROFILES[row['arm']]['max_epochs'] if fixed_epochs is None else fixed_epochs)+1):
   if val_ids and stagnant>=PROFILES[row['arm']]['patience']:break
   require_time();current_epoch=epoch;epstart=time.monotonic();model.train();loss_sum=0.;batches=0;partial=0
   if row['suite']=='source':
    order=list(fit_ids);random.Random(row['initialization_seed']*100+epoch).shuffle(order);batchlists=[order[k:k+16] for k in range(0,len(order),16)]
   else:
    order=sorted(groups);random.Random(row['initialization_seed']*100+epoch).shuffle(order)
    batchlists=[[s for g in order[k:k+16] for s in groups[g]] for k in range(0,len(order),16)]
   status('TRAINING_RUNNING',current_suite=row['suite'],current_arm=row['arm'],current_seed=row['seed'],current_outer=row.get('outer'),current_stage=stage,current_epoch=epoch,
    completed_optimization_stages=base_stages,optimizer_updates=base_updates+updates,completed_final_models=base_stages if row['suite']=='source' else 6+(base_stages-6)//2)
   for batchids in batchlists:
    require_time();batch=models.collate(batchids,data,scaler,device);opt.zero_grad(set_to_none=True)
    if row['suite']=='source':
     scores,extra=models.forward(model,row['arm'],batch);loss=models.loss(scores,extra,row['arm'],batch,labels)
    else:loss=grouped_loss(model,row['arm'],batch,labels,by)
    if not bool(torch.isfinite(loss)):raise RuntimeError('Nonfinite training loss')
    loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step();updates+=1;partial+=1;loss_sum+=float(loss.detach());batches+=1
   event={'epoch':epoch,'updates':batches,'training_loss':loss_sum/batches,'training_seconds':time.monotonic()-epstart}
   if val_ids:
    metric=validation_metric(predict(model,row['arm'],val_ids,data,scaler,device),labels,by,row['suite']=='AF');candidate=(metric['Top1'],metric['MRR']);improved=candidate>best
    if improved:
     best=candidate;best_epoch=epoch;stagnant=0
     torch_atomic(checkpoint,{'state_dict':cpu_state(model),'scaler_mean':scaler[0],'scaler_std':scaler[1],'row':row,'selected_epoch':epoch,'protocol_sha256':protocol_hash})
    else:stagnant+=1
    event.update(validation=metric,improved=improved,stagnant=stagnant)
   else:best_epoch=fixed_epochs
   event['epoch_total_seconds']=time.monotonic()-epstart;history.append(event)
   torch_atomic(resume_path,{'state_dict':cpu_state(model),'optimizer':opt.state_dict(),'rng':models.rng_state(),'best':best,'best_epoch':best_epoch,'stagnant':stagnant,
    'history':history,'epoch':epoch,'updates':updates,'protocol_sha256':protocol_hash,'fit_ids_sha256':digest(fit_ids)})
   partial=0;append(folder/(stage+'_epochs.jsonl'),event)
   if epoch==1 or epoch%10==0:print(canonical({'Exp158':'epoch','suite':row['suite'],'arm':row['arm'],'seed':row['seed'],'outer':row.get('outer'),'stage':stage,'epoch':epoch,'seconds':round(event['epoch_total_seconds'],3)}),flush=True)
  if best_epoch is None:raise RuntimeError('No selected epoch')
  if not val_ids:torch_atomic(checkpoint,{'state_dict':cpu_state(model),'scaler_mean':scaler[0],'scaler_std':scaler[1],'row':row,'selected_epoch':fixed_epochs,'protocol_sha256':protocol_hash})
  rec={'at_utc':now(),'suite':row['suite'],'arm':row['arm'],'seed':row['seed'],'outer':row.get('outer'),'stage':stage,'selected_epoch':best_epoch,'completed_epochs':current_epoch,'updates':updates,
   'history':history,'checkpoint':str(checkpoint),'checkpoint_sha256':sha(checkpoint),'fit_ids_sha256':digest(fit_ids),'validation_ids_sha256':digest(val_ids),
   'scaler_mean_sha256':models.state_digest({'mean':scaler[0],'std':scaler[1]}),'scaler_fit_only':True,'scaler_fit_ids_sha256':digest(fit_ids),**initial_binding,'held_labels_used_for_selection':0,'runtime_backend_policy':backend_policy(),'protocol_sha256':protocol_hash,'elapsed_seconds':time.monotonic()-started,'max_epochs':PROFILES[row['arm']]['max_epochs'],'patience':PROFILES[row['arm']]['patience'],'hit_epoch_cap':current_epoch==PROFILES[row['arm']]['max_epochs'],'last_epoch_validation_improved':history[-1].get('improved'),'selected_epoch_at_cap':best_epoch==PROFILES[row['arm']]['max_epochs']}
  write_new(receiptpath,rec);return rec
 except Exception as exc:
  append(E/'training/errors.jsonl',{'at_utc':now(),'row':row,'stage':stage,'epoch':current_epoch,'updates_in_partial_epoch':partial,'updates_so_far':updates,'error':str(exc),'type':type(exc).__name__})
  status('TRAINING_ERROR',recent_error=str(exc),optimizer_updates=base_updates+updates,current_stage=stage,next='Repair mechanical error and resume exact completed epoch')
  raise
 finally:del model,opt;gc.collect();torch.cuda.empty_cache()

def run():
 require_time(new_long_task=True);p=verify_protocol()
 if not torch.cuda.is_available():raise RuntimeError('Frozen GPU execution requires CUDA')
 lock=E/'training/producer.lock';lock.parent.mkdir(exist_ok=True);fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
 with os.fdopen(fd,'w') as f:json.dump({'pid':os.getpid(),'at_utc':now(),'experiment':'Exp158'},f)
 stages=0;updates=0;finals=[];started=time.monotonic()
 try:
  data,labels,historical_ids,by=source_inputs();device=torch.device('cuda')
  if historical_ids!=p['source_ids']:raise RuntimeError('Original153 source492/122 members required')
  fixture=read(E/'fixtures/preset_test_receipt.json')
  if fixture['status']!='PASS' or fixture['protocol_sha256']!=sha(E/'protocol.json'):raise RuntimeError('Necessary preset/lambda/validation fixture absent or changed')
  for row in p['source_schedule']:
   rec=fit(row,'source_fit',row['fit_ids'],row['validation_ids'],data,labels,by,device,stages,updates);stages+=1;updates+=rec['updates'];finals.append(rec)
   status('TRAINING_RUNNING',completed_optimization_stages=stages,optimizer_updates=updates,final_models=len(finals),elapsed_training_seconds=time.monotonic()-started)
   print(canonical({'Exp158':'source_model_complete','models':len(finals),'stages':stages,'updates':updates,'elapsed_seconds':round(time.monotonic()-started,1)}),flush=True)
  source_seal=E/'training/source_models_sealed.json'
  if source_seal.exists():
   if read(source_seal)['models']!=finals or read(source_seal)['protocol_sha256']!=sha(E/'protocol.json'):raise RuntimeError('Existing source model seal changed')
  else:write_new(source_seal,{'at_utc':now(),'models':finals.copy(),'stages':6,'updates':updates,'protocol_sha256':sha(E/'protocol.json'),'all6_sealed':True})
  del data,labels,by;gc.collect();data,labels,by=af_inputs()
  for r in p['af_schedule']:
   row={'suite':'AF',**r};selection=fit(row,'selection',row['selection_fit_ids'],row['validation_ids'],data,labels,by,device,stages,updates);stages+=1;updates+=selection['updates']
   refit=fit(row,'refit',row['refit_ids'],[],data,labels,by,device,stages,updates,fixed_epochs=selection['selected_epoch']);stages+=1;updates+=refit['updates'];finals.append(refit)
   status('TRAINING_RUNNING',completed_optimization_stages=stages,optimizer_updates=updates,final_models=len(finals),AF_pairs_completed=len(finals)-6,elapsed_training_seconds=time.monotonic()-started)
   print(canonical({'Exp158':'AF_pair_complete','pair':len(finals)-6,'total30':30,'arm':row['arm'],'seed':row['seed'],'outer':row['outer'],'selected_epoch':selection['selected_epoch'],'stages':stages,'updates':updates,'elapsed_seconds':round(time.monotonic()-started,1)}),flush=True)
  if stages!=66 or len(finals)!=36:raise RuntimeError('Incomplete frozen run')
  check_hashes(p['protected_old_files_sha256'])
  write_new(E/'training/AF_models_sealed.json',{'at_utc':now(),'models':finals[6:],'stages':60,'protocol_sha256':sha(E/'protocol.json'),'all30_sealed':True})
  write_new(E/'training/all_models_sealed.json',{'at_utc':now(),'models':finals,'optimization_stages':stages,'optimizer_updates':updates,'final_models':36,'protocol_sha256':sha(E/'protocol.json'),'all_fixed_models_sealed':True,'target_scores_computed':0,'elapsed_seconds':time.monotonic()-started})
  from select158 import freeze_decisions
  freeze_decisions(p,read(E/'training/all_models_sealed.json'))
  status('ALL_MODELS_SEALED',completed_optimization_stages=stages,optimizer_updates=updates,final_models=36,next='predict158.py then evaluate158.py only after both prediction seals')
 finally:lock.unlink()

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('run',));arg=parser.parse_args();run()

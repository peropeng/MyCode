"""Exact source and nested AF optimizations; held scoring is deferred."""
import argparse,gc,random
from collections import defaultdict
import numpy as np
import torch
from common import *
import context_models as models
from data153 import source_inputs,af_inputs,scaler_for,grouped_loss

def torch_atomic(path,value):
 path=_output_local(path);tmp=path.with_name(path.name+f'.{os.getpid()}.tmp')
 torch.save(value,tmp);os.replace(tmp,path)
def _output_local(path):
 path=Path(path).resolve()
 if not path.is_relative_to(E):raise ValueError('Exp153 torch writes only')
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
def freeze():
 require_time(new_long_task=True);prepared=read(E/'prepared_inputs.json')
 for name in ('context_test_receipt.json','data_test_receipt.json'):
  if read(E/'fixtures'/name)['status']!='PASS':raise RuntimeError('Required fixture failed: '+name)
 check_hashes(prepared['protected_old_files_sha256']);initials={};records=[];signatures={};context_signatures={}
 for row in all_schedule(prepared):
  model,rng,info=models.create_initialized(row['arm'],row['initialization_seed'])
  key=(row['suite'],row['initialization_seed']);sig=models.state_digest({k:v for k,v in model.state_dict().items() if k.split('.')[0] not in ('Q','K','V','O')})
  if row['arm']!='SF_REF':
   if key in signatures and signatures[key]!=sig:raise RuntimeError('Canonical base initialization mismatch')
   signatures[key]=sig
  if row['arm'] in CONTEXT_ARMS:
   fullsig=models.state_digest(model.state_dict())
   if key in context_signatures and context_signatures[key]!=fullsig:raise RuntimeError('Full equal-capacity initialization mismatch')
   context_signatures[key]=fullsig
  path=folder_for(row)/'initial.pt'
  if path.exists():raise RuntimeError('Initialization freeze is single-use')
  torch_atomic(path,{'state_dict':cpu_state(model),'training_rng':rng,'info':info,'row':row})
  initials[str(path)]=sha(path);records.append({'suite':row['suite'],'arm':row['arm'],'seed':row['seed'],'outer':row.get('outer'),'path':str(path),'sha256':sha(path),**info});del model
 sources={str(E/n):sha(E/n) for n in ('common.py','context_models.py','data153.py','trainer153.py','predict153.py')}
 sources.update({str(p):sha(p) for p in (E/'sources').glob('*.py')})
 p={**prepared,'at_utc':now(),'schema':'Exp153-fixed-six-arm-source-and-AF-nested/1.0','primary':'AB_GLOBAL','training_sources':sources,
  'initializations':initials,'initialization_records':records,'inputs':{str(E/n):sha(E/n) for n in ('approved_plan.json','prepared_inputs.json','fixtures/context_test_receipt.json','fixtures/data_test_receipt.json')},
  'device':'cuda','dtype':'float32','batch':16,'optimizer':'AdamW','lr':.001,'graph_wd':.0001,'SF_wd':.00001,'clip':1.,
  'source_loss':'Original134 trajectory-mean CE; SF original padded CE+.9 temporal',
  'AF_loss':'Original138 trajectory CE+.9 SF temporal decomposed per record; mean records per complete group then mean groups',
  'model_seal_rule':'All18 source and all90 AF final models sealed before held prediction; both prediction suites sealed before target scoring',
  'deadline':DEADLINE,'expected_optimization_stages':198,'expected_final_models':108,'expected_outputs':69264}
 write_new(E/'protocol.json',p);write_new(E/'initialization_audit.json',{'at_utc':now(),'status':'PASS','records':records,'base_shared_across_graph_arms':True,'training_rng_restored':True,'O_initial_zero':True,'parameters':p['parameters']})
 status('PROTOCOL_AND_INITIALIZATIONS_SEALED',next='trainer153.py run;198 stages/108 final models/0 target scoring')
 print(canonical({'Exp153':'FROZEN','initial_model_files':len(records),'parameters':p['parameters'],'optimization_stages':198}),flush=True)

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
 ck=torch.load(folder_for(row)/'initial.pt',map_location='cpu',weights_only=False)
 model=models.create(row['arm']).to(device);model.load_state_dict(ck['state_dict']);models.restore_rng(ck['training_rng'])
 opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.00001 if row['arm']=='SF_REF' else .0001)
 return model,opt

def fit(row,stage,fit_ids,val_ids,data,labels,by,device,base_stages,base_updates,fixed_epochs=None):
 folder=folder_for(row);receiptpath=folder/(stage+'.json');protocol_hash=sha(E/'protocol.json')
 if receiptpath.exists():
  rec=read(receiptpath)
  if rec['protocol_sha256']!=protocol_hash or rec['fit_ids_sha256']!=digest(fit_ids) or sha(rec['checkpoint'])!=rec['checkpoint_sha256']:raise RuntimeError('Completed stage binding changed')
  return rec
 require_time(new_long_task=True);model,opt=initial_model(row,device);scaler=scaler_for(data,fit_ids)
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
  for epoch in range(first,(40 if fixed_epochs is None else fixed_epochs)+1):
   if val_ids and stagnant>=8:break
   require_time();current_epoch=epoch;epstart=time.monotonic();model.train();loss_sum=0.;batches=0;partial=0
   if row['suite']=='source':
    order=list(fit_ids);random.Random(row['initialization_seed']*100+epoch).shuffle(order);batchlists=[order[k:k+16] for k in range(0,len(order),16)]
   else:
    order=sorted(groups);random.Random(row['initialization_seed']*100+epoch).shuffle(order)
    batchlists=[[s for g in order[k:k+16] for s in groups[g]] for k in range(0,len(order),16)]
   status('TRAINING_RUNNING',current_suite=row['suite'],current_arm=row['arm'],current_seed=row['seed'],current_outer=row.get('outer'),current_stage=stage,current_epoch=epoch,
    completed_optimization_stages=base_stages,optimizer_updates=base_updates+updates,completed_final_models=base_stages if row['suite']=='source' else 18+(base_stages-18)//2)
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
   if epoch==1 or epoch%10==0:print(canonical({'Exp153':'epoch','suite':row['suite'],'arm':row['arm'],'seed':row['seed'],'outer':row.get('outer'),'stage':stage,'epoch':epoch,'seconds':round(event['epoch_total_seconds'],3)}),flush=True)
  if best_epoch is None:raise RuntimeError('No selected epoch')
  if not val_ids:torch_atomic(checkpoint,{'state_dict':cpu_state(model),'scaler_mean':scaler[0],'scaler_std':scaler[1],'row':row,'selected_epoch':fixed_epochs,'protocol_sha256':protocol_hash})
  rec={'at_utc':now(),'suite':row['suite'],'arm':row['arm'],'seed':row['seed'],'outer':row.get('outer'),'stage':stage,'selected_epoch':best_epoch,'completed_epochs':current_epoch,'updates':updates,
   'history':history,'checkpoint':str(checkpoint),'checkpoint_sha256':sha(checkpoint),'fit_ids_sha256':digest(fit_ids),'validation_ids_sha256':digest(val_ids),
   'scaler_mean_sha256':models.state_digest({'mean':scaler[0],'std':scaler[1]}),'scaler_fit_only':True,'held_labels_used_for_selection':0,'runtime_backend_policy':backend_policy(),'protocol_sha256':protocol_hash,'elapsed_seconds':time.monotonic()-started}
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
 with os.fdopen(fd,'w') as f:json.dump({'pid':os.getpid(),'at_utc':now(),'experiment':'Exp153'},f)
 stages=0;updates=0;finals=[];started=time.monotonic()
 try:
  data,labels,ids,by,_=source_inputs();device=torch.device('cuda')
  for row in p['source_schedule']:
   rec=fit(row,'source_fit',ids['train'],ids['validation'],data,labels,by,device,stages,updates);stages+=1;updates+=rec['updates'];finals.append(rec)
   status('TRAINING_RUNNING',completed_optimization_stages=stages,optimizer_updates=updates,final_models=len(finals),elapsed_training_seconds=time.monotonic()-started)
   print(canonical({'Exp153':'source_model_complete','models':len(finals),'stages':stages,'updates':updates,'elapsed_seconds':round(time.monotonic()-started,1)}),flush=True)
  source_seal=E/'training/source_models_sealed.json'
  if source_seal.exists():
   if read(source_seal)['models']!=finals or read(source_seal)['protocol_sha256']!=sha(E/'protocol.json'):raise RuntimeError('Existing source model seal changed')
  else:write_new(source_seal,{'at_utc':now(),'models':finals.copy(),'stages':18,'updates':updates,'protocol_sha256':sha(E/'protocol.json'),'all18_sealed':True})
  del data,labels,by;gc.collect();data,labels,by=af_inputs()
  for r in p['af_schedule']:
   row={'suite':'AF',**r};selection=fit(row,'selection',row['selection_fit_ids'],row['validation_ids'],data,labels,by,device,stages,updates);stages+=1;updates+=selection['updates']
   refit=fit(row,'refit',row['refit_ids'],[],data,labels,by,device,stages,updates,fixed_epochs=selection['selected_epoch']);stages+=1;updates+=refit['updates'];finals.append(refit)
   status('TRAINING_RUNNING',completed_optimization_stages=stages,optimizer_updates=updates,final_models=len(finals),AF_pairs_completed=len(finals)-18,elapsed_training_seconds=time.monotonic()-started)
   print(canonical({'Exp153':'AF_pair_complete','pair':len(finals)-18,'total90':90,'arm':row['arm'],'seed':row['seed'],'outer':row['outer'],'selected_epoch':selection['selected_epoch'],'stages':stages,'updates':updates,'elapsed_seconds':round(time.monotonic()-started,1)}),flush=True)
  if stages!=198 or len(finals)!=108:raise RuntimeError('Incomplete frozen run')
  check_hashes(p['protected_old_files_sha256'])
  write_new(E/'training/AF_models_sealed.json',{'at_utc':now(),'models':finals[18:],'stages':180,'protocol_sha256':sha(E/'protocol.json'),'all90_sealed':True})
  write_new(E/'training/all_models_sealed.json',{'at_utc':now(),'models':finals,'optimization_stages':stages,'optimizer_updates':updates,'final_models':108,'protocol_sha256':sha(E/'protocol.json'),'all_fixed_models_sealed':True,'target_scores_computed':0,'elapsed_seconds':time.monotonic()-started})
  status('ALL_MODELS_SEALED',completed_optimization_stages=stages,optimizer_updates=updates,final_models=108,next='predict153.py then evaluate153.py only after both prediction seals')
 finally:lock.unlink()

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('freeze','run'));arg=parser.parse_args();freeze() if arg.mode=='freeze' else run()

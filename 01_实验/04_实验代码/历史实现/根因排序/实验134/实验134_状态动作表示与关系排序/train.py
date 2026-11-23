"""All five arms, all three fixed seeds, author-train validation-only selection."""
import argparse
from collections import Counter
import gc
import json
import os
os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
import random
import sys
import time
sys.dont_write_bytecode=True
import numpy as np
import torch
from common import *
import models

def torch_atomic(path,value):
    tmp=Path(path).with_name(Path(path).name+f'.{os.getpid()}.tmp');torch.save(value,tmp);os.replace(tmp,path)
def seed_all(seed):
    random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
    if torch.cuda.is_available():torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic=True;torch.backends.cudnn.benchmark=False;torch.use_deterministic_algorithms(True)
def freeze():
    receipt=read(E/'features/train_validation_features.receipt.json')
    feature_path=E/'features/train_validation_features.pt'
    if sha(feature_path)!=receipt['feature_file_sha256']:raise RuntimeError('feature_seal_changed')
    source_names=('common.py','prepare_data.py','prepare_features.py','models.py','train.py','evaluate_development.py','check_engineering.py')
    sources={str(E/name):sha(E/name) for name in source_names}
    sources.update({str(p):sha(p) for p in (E/'sources').glob('*.py')})
    label_receipt=read(E/'data/label_mapping_receipt.json')
    files=[E/'approved_plan.json',E/'data/public_split_manifest.json',E/'data/public_split_seal.json',E/'data/public_records.json',
        E/'data/selected_train_labels.private.json',E/'data/label_mapping_receipt.json',feature_path,E/'features/train_validation_features.receipt.json']
    parameters={arm:sum(p.numel() for p in models.create(arm).parameters()) for arm in ARMS}
    protocol={'at_utc':now(),'schema':'Exp134-local-same-data-factorial-supervision/1.0','arms':list(ARMS),'seeds':list(SEEDS),
        'sources':sources,'input_hashes':{str(p):sha(p) for p in files},'parameters':parameters,
        'normalization':'own content/role L2; structure23 fit only selected train nodes; validation never in scaler; SF exact same cached raw content/role',
        'selection':'validation exact ordinal Top1, MRR tie break, earliest exact tie; all3 seeds retained; ensemble mean per-trajectory softmax',
        'own_loss':'mean per-trajectory cross entropy','SF_loss':'original compute_loss CE+.9 temporal; unchanged architecture source',
        'own_optimizer':{'name':'AdamW','lr':.001,'weight_decay':.0001},
        'SF_optimizer':{'name':'AdamW','lr':.001,'weight_decay':.00001,'defaults_source':sha(E/'sources/stepfinder_original_main.py')},
        'batch_tasks':16,'max_epochs':40,'early_stopping_patience':8,'gradient_clip':1.0,
        'validation_inference_batching':'frozen manifest order in batches16; SF pads each batch to its longest raw trajectory',
        'relations':['temporal','same_role','same_full_shape_signature','same_nonempty_action_shape'],
        'A_event':'two separately learned257→183 projections/gates of linked content128, difference128 and observed flag; unpaired residual exactly zero',
        'N_A_depth':'two hidden96 feedforward residual layers; no graph messages','B_AB_depth':'two owned Exp130 RelationLayer layers',
        'train_labels':label_receipt['valid_labels'],'test_labels_used_for_optimization_or_epoch_choice':0,'paid_API_calls':0}
    write_new(E/'training_protocol.json',protocol)
    status('EXP134_TRAINING_PROTOCOL_FROZEN',parameter_counts=parameters,next_executable_command='train.py run')
    print(canonical({'training_protocol_frozen':True,'parameters':parameters,'arms':list(ARMS),'seeds':list(SEEDS)}),flush=True)

def inputs():
    protocol=read(E/'training_protocol.json')
    for path,digest_ in {**protocol['sources'],**protocol['input_hashes']}.items():
        if sha(path)!=digest_:raise RuntimeError('frozen_training_input_changed:'+path)
    data=torch.load(E/'features/train_validation_features.pt',map_location='cpu',weights_only=False)['records']
    public=read(E/'data/public_records.json')['records'];labelrows=read(E/'data/selected_train_labels.private.json')['labels']
    labels={r['sample_id']:r['target_ordinal'] for r in labelrows};by={r['sample_id']:r for r in public}
    ids={split:[r['sample_id'] for r in public if r['optimization_split']==split and r['sample_id'] in labels] for split in ('train','validation')}
    if set(data)!=set(labels):raise RuntimeError('shared_feature_label_scope_mismatch')
    if set(by[sid]['task_group'] for sid in ids['train'])&set(by[sid]['task_group'] for sid in ids['validation']):raise RuntimeError('group_leakage')
    values=torch.cat([data[sid]['raw_structure'] for sid in ids['train']]);mean=values.mean(0);std=values.std(0,unbiased=False);std=torch.where(std<1e-6,torch.ones_like(std),std)
    return protocol,data,labels,ids,by,(mean,std)

@torch.no_grad()
def predict(model,arm,ids,data,scaler,device):
    model.eval();out={}
    for start in range(0,len(ids),16):
        subset=ids[start:start+16];batch=models.collate(subset,data,scaler,device);scores,_=models.forward(model,arm,batch)
        for sid,score in zip(subset,scores):
            if not bool(torch.isfinite(score).all()):raise RuntimeError('nonfinite_original_step_scores')
            logits=score.cpu();prob=torch.softmax(logits,0).tolist();order=sorted(range(len(prob)),key=lambda i:(-float(logits[i]),i))
            out[sid]={'scores':logits.tolist(),'probabilities':prob,'order':order,'chosen_step':order[0],'valid':True}
    return out

def metrics(predictions,labels,by):
    def subset(ids):
        n=len(ids)
        return {'n':n,'hits':sum(predictions[sid]['chosen_step']==labels[sid] for sid in ids),
            'exact_step_accuracy':sum(predictions[sid]['chosen_step']==labels[sid] for sid in ids)/n if n else None,
            'MRR':sum(1/(predictions[sid]['order'].index(labels[sid])+1) for sid in ids)/n if n else None,
            'Top3':sum(labels[sid] in predictions[sid]['order'][:3] for sid in ids)/n if n else None}
    ids=list(predictions);return {**subset(ids),'domain':{d:subset([sid for sid in ids if by[sid]['domain']==d]) for d in ('coding','math')}}

def rng_state():
    return {'python':random.getstate(),'numpy':np.random.get_state(),'torch':torch.get_rng_state(),
        'cuda':torch.cuda.get_rng_state_all() if torch.cuda.is_available() else []}
def restore_rng(value):
    random.setstate(value['python']);np.random.set_state(value['numpy']);torch.set_rng_state(value['torch'])
    if torch.cuda.is_available():torch.cuda.set_rng_state_all(value['cuda'])

def run():
    protocol,data,labels,ids,by,scaler=inputs();device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    lock=E/'training/producer.lock';fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    with os.fdopen(fd,'w') as f:json.dump({'pid':os.getpid(),'at_utc':now(),'owner_chat_id':OWNER_ID},f)
    completed=[];runstart=time.monotonic();current=None
    try:
        if (E/'training/model_seal.json').exists():raise RuntimeError('all_models_already_frozen_no_retraining')
        for arm in ARMS:
            for seed in SEEDS:
                current=(arm,seed);folder=E/'training'/arm/str(seed);folder.mkdir(parents=True,exist_ok=True)
                if (folder/'complete.json').exists():
                    receipt=read(folder/'complete.json')
                    if receipt['protocol_sha256']!=sha(E/'training_protocol.json') or sha(receipt['checkpoint'])!=receipt['checkpoint_sha256']:raise RuntimeError('completed_checkpoint_changed')
                    completed.append(receipt);continue
                seed_all(seed);model=models.create(arm).to(device)
                weight_decay=.00001 if arm=='StepFinder' else .0001
                optimizer=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=weight_decay)
                best=(-1.,-1.);best_epoch=None;stagnant=0;start_epoch=1;batch_size=16
                if (folder/'last_resume.pt').exists():
                    resume=torch.load(folder/'last_resume.pt',map_location='cpu',weights_only=False)
                    if resume['protocol_sha256']!=sha(E/'training_protocol.json'):raise RuntimeError('resume_protocol_mismatch')
                    model.load_state_dict(resume['state_dict']);optimizer.load_state_dict(resume['optimizer']);restore_rng(resume['rng'])
                    best=tuple(resume['best']);best_epoch=resume['best_epoch'];stagnant=resume['stagnant'];start_epoch=resume['epoch']+1;batch_size=resume['batch_size']
                    append(folder/'engineering_events.jsonl',{'at_utc':now(),'event':'RESUME_FROM_COMPLETED_EPOCH','epoch':resume['epoch']})
                seedstart=time.monotonic();epoch=start_epoch-1
                if stagnant>=8:start_epoch=41
                for epoch in range(start_epoch,41):
                    status('EXP134_LOCAL_TRAINING',current_arm=arm,current_seed=seed,current_epoch=epoch,
                        completed_training_runs=len(completed),total_training_runs=15,current_best_epoch=best_epoch,
                        compute_device=str(device),next_executable_command='train.py run (resumes completed epoch; retains all fixed seeds)')
                    model.train();order=list(ids['train']);random.Random(seed*100+epoch).shuffle(order);total_loss=0.;n_batches=0
                    for start in range(0,len(order),batch_size):
                        batch=models.collate(order[start:start+batch_size],data,scaler,device);optimizer.zero_grad(set_to_none=True)
                        scores,extra=models.forward(model,arm,batch);loss=models.loss(scores,extra,arm,batch,labels)
                        if not bool(torch.isfinite(loss)):raise RuntimeError('nonfinite_training_loss')
                        loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.0);optimizer.step()
                        total_loss+=float(loss.detach());n_batches+=1
                    validation=predict(model,arm,ids['validation'],data,scaler,device);metric=metrics(validation,labels,by)
                    candidate=(metric['exact_step_accuracy'],metric['MRR']);improved=candidate>best
                    if improved:
                        best=candidate;best_epoch=epoch;stagnant=0
                        checkpoint={'state_dict':{k:v.detach().cpu().clone() for k,v in model.state_dict().items()},
                            'scaler_mean':scaler[0],'scaler_std':scaler[1],'arm':arm,'seed':seed,'epoch':epoch,
                            'validation_metrics':metric,'protocol_sha256':sha(E/'training_protocol.json')}
                        path=folder/f'epoch_{epoch:02d}_best.pt'
                        if path.exists():
                            saved=torch.load(path,map_location='cpu',weights_only=False)
                            if saved['epoch']!=epoch or saved['validation_metrics']!=metric or any(not torch.equal(saved['state_dict'][k],v) for k,v in checkpoint['state_dict'].items()):raise RuntimeError('existing_epoch_checkpoint_differs_no_overwrite')
                        else:torch.save(checkpoint,path)
                    else:stagnant+=1
                    resume={'state_dict':model.state_dict(),'optimizer':optimizer.state_dict(),'rng':rng_state(),
                        'epoch':epoch,'best':best,'best_epoch':best_epoch,'stagnant':stagnant,'batch_size':batch_size,
                        'protocol_sha256':sha(E/'training_protocol.json')}
                    torch_atomic(folder/'last_resume.pt',resume)
                    event={'at_utc':now(),'arm':arm,'seed':seed,'epoch':epoch,'train_loss':total_loss/n_batches,
                        'validation':metric,'new_best':improved,'stagnant_epochs':stagnant,'elapsed_seconds':time.monotonic()-seedstart}
                    append(folder/'epochs.jsonl',event)
                    print(canonical({'arm':arm,'seed':seed,'epoch':epoch,'val_hits':metric['hits'],'val_n':metric['n'],
                        'val_MRR':round(metric['MRR'],5),'new_best':improved,'elapsed_seconds':round(event['elapsed_seconds'],1)}),flush=True)
                    if stagnant>=8:break
                if best_epoch is None:raise RuntimeError('no_selected_validation_checkpoint')
                path=folder/f'epoch_{best_epoch:02d}_best.pt';checkpoint=torch.load(path,map_location='cpu',weights_only=False)
                model.load_state_dict(checkpoint['state_dict']);validation=predict(model,arm,ids['validation'],data,scaler,device)
                write_new(folder/'validation_predictions.json',{'predictions':validation,'only_author_train_validation':True})
                receipt={'at_utc':now(),'arm':arm,'seed':seed,'selected_epoch':best_epoch,'checkpoint':str(path),'checkpoint_sha256':sha(path),
                    'validation_metrics':metrics(validation,labels,by),'parameter_count':sum(p.numel() for p in model.parameters()),
                    'protocol_sha256':sha(E/'training_protocol.json'),'completed_epochs':epoch,'elapsed_seconds':time.monotonic()-seedstart,
                    'test_labels_used':0,'paid_API_calls':0,'compute_device':str(device)}
                write_new(folder/'complete.json',receipt);completed.append(receipt);del model,optimizer;gc.collect();torch.cuda.empty_cache()
        write_new(E/'training/model_seal.json',{'at_utc':now(),'models':completed,'protocol_sha256':sha(E/'training_protocol.json'),
            'all15_fixed_runs_frozen':True,'all3_seeds_retained':True,'test_labels_used_for_selection':0,'paid_API_calls':0,'elapsed_seconds':time.monotonic()-runstart})
        ensemble={};validation_table={}
        for arm in ARMS:
            predictions=[read(E/'training'/arm/str(seed)/'validation_predictions.json')['predictions'] for seed in SEEDS]
            out={}
            for sid in ids['validation']:
                probabilities=np.mean([p[sid]['probabilities'] for p in predictions],axis=0).tolist()
                ranking=sorted(range(len(probabilities)),key=lambda i:(-probabilities[i],i))
                out[sid]={'probabilities':probabilities,'order':ranking,'chosen_step':ranking[0],'valid':True}
            ensemble[arm]=out;validation_table[arm]={'ensemble':metrics(out,labels,by),
                'seeds':{str(r['seed']):r['validation_metrics'] for r in completed if r['arm']==arm}}
        write_new(E/'training/validation_ensemble_predictions.json',{'predictions':ensemble,'all3_fixed_seeds_mean_softmax':True})
        write_new(E/'training/validation_comparison.json',{'at_utc':now(),'scope':'group-disjoint author-train validation; epoch selection data, not fresh confirmation',
            'table':validation_table,'parameter_counts':protocol['parameters'],'test_label_accesses':0,'model_seal_sha256':sha(E/'training/model_seal.json')})
        status('EXP134_ALL_MODELS_FROZEN',completed_training_runs=15,total_training_runs=15,current_arm=None,current_seed=None,current_epoch=None,
            total_training_elapsed_seconds=time.monotonic()-runstart,next_executable_command='evaluate_development.py run (sealed exposed32 only)')
        print(canonical({'all15_models_frozen':True,'ensemble_validation_hits':{a:v['ensemble']['hits'] for a,v in validation_table.items()}}),flush=True)
    except Exception as exc:
        append(E/'training/execution_errors.jsonl',{'at_utc':now(),'current_arm_seed':current,'error':str(exc),'type':type(exc).__name__})
        status('EXP134_TRAINING_ENGINEERING_ERROR',recent_error=str(exc),next_executable_command='repair engineering error then train.py run; no test-based selection')
        raise
    finally:lock.unlink()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('freeze','run'));args=parser.parse_args()
    freeze() if args.mode=='freeze' else run()

"""Same-data StepFinder adaptation; frozen historical comparator, strict group holdout."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, random, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
ASSETS=ROOT/'third_party'
os.environ.setdefault('HF_HOME',str(ASSETS/'hf_cache'))
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG',':4096:8')
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def publish(p,obj):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    temp=p.with_suffix(p.suffix+'.tmp')
    with temp.open('w',encoding='utf-8') as f: json.dump(obj,f,ensure_ascii=False,indent=2)
    if p.exists(): raise FileExistsError(p)
    os.rename(temp,p)
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(spec); sys.modules[name]=m; spec.loader.exec_module(m); return m
def data():
    e=module('e112_exp124',ROOT/'实验/实验112_RQ1时序交互依赖完整排序/runner.py')
    source=ROOT/'实验/实验33_旧版场景F责任主体/real_feasibility_group6'
    records,boundary,_=e._load_train_data(str(source),str(ASSETS/'AFTraj'))
    return e,records,boundary
def text_of(turn):
    return json.dumps({k:str(turn.get(k) or '') for k in ('content','action','thought') if turn.get(k)},ensure_ascii=False,sort_keys=True)
def prepare():
    import torch,numpy as np
    torch.set_num_threads(4)
    from bindings import freeze_or_verify
    bound=freeze_or_verify()
    sys.path.insert(0,str(ASSETS/'StepFinder'))
    from Q3Emb import Qwen3Embedding
    e,records,boundary=data()
    model=Qwen3Embedding(str(ASSETS/'Qwen3-Embedding-0.6B'),model_revision=None)
    cache=ASSETS/'embeddings'; cache.mkdir(exist_ok=True)
    started=time.monotonic(); count=0
    # Only development records are ever passed to the encoder.
    roles={}
    for i,r in enumerate(records):
        path=cache/f'{i:04d}.npz'
        if path.exists():
            assert str(np.load(path)['binding_sha'])==bound['embedding_binding_sha256']
            continue
        cs=[]; rs=[]
        for t in r['turns']:
            role=t['role']
            if role not in roles: roles[role]=model.encode(role,dim=32).float().cpu().numpy()[0]
            rs.append(roles[role])
        sentences=[text_of(t) for t in r['turns']]
        for off in range(0,len(sentences),8):
            cs.extend(model.encode(sentences[off:off+8],dim=128).float().cpu().numpy())
        tmp=path.with_suffix('.tmp.npz'); np.savez(tmp,content=np.array(cs),agent=np.array(rs),input_sha=hashlib.sha256(json.dumps(r['turns'],sort_keys=True).encode()).hexdigest(),binding_sha=bound['embedding_binding_sha256']); os.rename(tmp,path)
        count+=1
        if count%25==0: print(json.dumps({'stage':'embedding','complete':i+1,'total':len(records),'seconds':time.monotonic()-started}),flush=True)
    publish(HERE/'results/embedding_audit.json',{'records':len(records),'steps':sum(len(r['turns']) for r in records),'boundary':boundary,'peak_gpu_bytes':torch.cuda.max_memory_allocated(),'seconds':time.monotonic()-started,'model':'Qwen/Qwen3-Embedding-0.6B','revision':'97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3'})
def seed_all(seed):
    import numpy as np,torch
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic=True; torch.backends.cudnn.benchmark=False
    torch.use_deterministic_algorithms(True)
def batches(indices,features,records,shuffle=False):
    import torch
    ids=list(indices)
    if shuffle: random.shuffle(ids)
    for off in range(0,len(ids),16):
        ii=ids[off:off+16]; n=max(2,max(len(records[i]['turns']) for i in ii))
        c=torch.zeros(len(ii),n,128); a=torch.zeros(len(ii),n,32); mask=torch.zeros(len(ii),n,dtype=torch.bool); y=torch.zeros(len(ii),n)
        for j,i in enumerate(ii):
            l=len(records[i]['turns']); c[j,:l]=features[i][0]; a[j,:l]=features[i][1]; mask[j,:l]=True; y[j,int(records[i]['mistake_step'])]=1
        yield ii,c.cuda(),a.cuda(),mask.cuda(),y.cuda()
def ranks(model,indices,features,records):
    import torch
    model.eval(); out={}
    with torch.no_grad():
        for ii,c,a,m,y in batches(indices,features,records):
            logits,_=model(c,a,m)
            for j,i in enumerate(ii):
                scores=logits[j,:len(records[i]['turns'])].cpu().tolist()
                order=sorted(range(len(scores)),key=lambda k:(-scores[k],k))
                out[i]={'rank':order.index(int(records[i]['mistake_step']))+1,'order':order,'scores':scores}
    return out
def group_score(pred,records,kind='rr'):
    import numpy as np
    groups={}
    for i,p in pred.items():
        r=p['rank']; val=1/r if kind=='rr' else float(r<=int(kind))
        groups.setdefault(records[int(i)]['task_group'],[]).append(val)
    return {g:float(np.mean(v)) for g,v in groups.items()}
def train(indices,val,features,records,seed,epochs=None):
    import torch,numpy as np
    from model import StepFinder,compute_loss
    seed_all(seed); m=StepFinder().cuda(); opt=torch.optim.AdamW(m.parameters(),lr=.001,weight_decay=1e-5)
    best=-1.; best_epoch=1; stagnant=0; history=[]
    for epoch in range(1,(epochs or 50)+1):
        m.train(); losses=[]
        for ii,c,a,mask,y in batches(indices,features,records,True):
            opt.zero_grad(); logits,tl=m(c,a,mask); loss=compute_loss(logits,y,mask,tl,lambda_temporal=.9); loss.backward(); torch.nn.utils.clip_grad_norm_(m.parameters(),1.); opt.step(); losses.append(loss.item())
        row={'epoch':epoch,'loss':float(np.mean(losses))}
        if val:
            score=float(np.mean(list(group_score(ranks(m,val,features,records),records,'1').values())))
            row['validation_task_top1']=score
            if score>best: best=score; best_epoch=epoch; stagnant=0
            else: stagnant+=1
        history.append(row)
        if val and stagnant>=10: break
    return m,best_epoch,history
def run():
    import torch,numpy as np,subprocess
    from bindings import freeze_or_verify,historical_folds
    bound=freeze_or_verify()
    sys.path.insert(0,str(ASSETS/'StepFinder')); torch.set_num_threads(4)
    e,records,boundary=data(); features=[]
    for i,r in enumerate(records):
        z=np.load(ASSETS/'embeddings'/f'{i:04d}.npz'); assert str(z['input_sha'])==hashlib.sha256(json.dumps(r['turns'],sort_keys=True).encode()).hexdigest()
        assert str(z['binding_sha'])==bound['embedding_binding_sha256']
        features.append((torch.from_numpy(z['content']),torch.from_numpy(z['agent'])))
    groups=sorted({r['task_group'] for r in records})
    for seed in (20260816,20260817,20260818):
        folds=e.E96._fold_groups(groups,seed)
        assert folds==historical_folds(records,seed)
        for outer in range(5):
            path=HERE/'results/folds'/f'{seed}_{outer}.json'
            if path.exists():
                existing=load(path)
                assert existing['protocol_sha256']==bound['protocol_sha256'] and existing['runner_sha256']==bound['runner_sha256']
                assert existing['held_groups']==sorted(folds[outer])
                continue
            started=time.monotonic(); held=set(folds[outer]); vi=next(i for i in range(5) if i!=outer); vg=set(folds[vi])
            tr=[i for i,r in enumerate(records) if r['task_group'] not in held|vg]; va=[i for i,r in enumerate(records) if r['task_group'] in vg]; te=[i for i,r in enumerate(records) if r['task_group'] in held]; full=sorted(tr+va)
            assert not set(tr)&set(va) and not set(full)&set(te)
            model,epoch,selection=train(tr,va,features,records,seed+outer*100)
            del model; torch.cuda.empty_cache()
            model,_,fit=train(full,[],features,records,seed+outer*100,epoch)
            cp=ASSETS/'checkpoints'/f'{seed}_{outer}.pt'; cp.parent.mkdir(exist_ok=True)
            if cp.exists(): raise FileExistsError('Unfinished fold has persisted checkpoint; inspect before resume: '+str(cp))
            temp=cp.with_suffix('.tmp'); torch.save(model.state_dict(),temp); os.rename(temp,cp)
            frozen={'seed':seed,'outer':outer,'fit_groups':sorted(set(groups)-held),'held_groups':sorted(held),'validation_groups':sorted(vg),'selected_epoch':epoch,'selection':selection,'fit':fit,'protocol_sha256':sha(HERE/'protocol.json'),'runner_sha256':sha(__file__),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'checkpoint_path':str(cp.relative_to(ROOT)),'checkpoint_sha256':sha(cp),'historical_fold_reconstructed_exact':True,'preclaim_binding_sha256':sha(HERE/'results/preclaim_binding.json')}
            freeze_path=HERE/'results/freezes'/f'{seed}_{outer}.json'
            if not freeze_path.exists(): publish(freeze_path,frozen)
            prediction=ranks(model,te,features,records)
            publish(path,dict(frozen,predictions=prediction,seconds=time.monotonic()-started,peak_gpu_bytes=torch.cuda.max_memory_allocated()))
            print(json.dumps({'stage':'fold_complete','seed':seed,'outer':outer,'held':len(te),'seconds':time.monotonic()-started}),flush=True)
            del model; torch.cuda.empty_cache()
    aggregate(records,boundary)
def aggregate(records,boundary):
    import numpy as np
    from bindings import freeze_or_verify,historical_folds
    bound=freeze_or_verify(); final_checks={'source_binding':True,'fold_keysets':True,'checkpoints':True,'full_coverage':True,'no_confirmation_scoring':not boundary['confirmation_used_for_scoring']}
    oldpath=ROOT/'实验/实验112C_RQ1时序依赖排序纠正式复跑/results/formal_corrected_nested_oof_results.json'
    old=load(oldpath); seeds=[]; pooled={}; details=[]
    for baseline in old['results_by_seed']:
        seed=baseline['seed']; pred={}
        for fold in range(5):
            f=load(HERE/'results/folds'/f'{seed}_{fold}.json'); assert not set(pred)&set(f['predictions'])
            held=set(historical_folds(records,seed)[fold]); assert set(f['held_groups'])==held
            assert set(f['predictions'])=={str(i) for i,r in enumerate(records) if r['task_group'] in held}
            assert not set(f['fit_groups'])&held and not set(f['validation_groups'])&held
            assert sha(ROOT/f['checkpoint_path'])==f['checkpoint_sha256']
            assert f['protocol_sha256']==bound['protocol_sha256'] and f['runner_sha256']==bound['runner_sha256']
            pred.update(f['predictions'])
        assert len(pred)==731
        assert set(baseline['group_mrr']['A_plus_B'])=={r['task_group'] for r in records}
        vals={c:baseline['group_mrr'][c] for c in ['A_plus_B','pairwise_B','local','recency']}
        vals['StepFinder']=group_score(pred,records)
        # Recompute historical group metrics from raw ranks to prove record order matches.
        for c in ['A_plus_B','pairwise_B','local','recency']:
            check=group_score({i:{'rank':v} for i,v in enumerate(baseline['raw_ranks'][c])},records)
            assert all(abs(check[g]-vals[c][g])<1e-12 for g in check)
        seeds.append({'seed':seed,'task_mrr':{c:float(np.mean(list(v.values()))) for c,v in vals.items()},'stepfinder_r1':float(np.mean(list(group_score(pred,records,'1').values()))),'stepfinder_r3':float(np.mean(list(group_score(pred,records,'3').values()))),'stepfinder_mrr_at3':float(np.mean(list(group_score({i:{'rank':p['rank'] if p['rank']<=3 else float('inf')} for i,p in pred.items()},records).values())))})
        details.append({'seed':seed,'group_mrr':vals})
        for c,v in vals.items():
            pooled.setdefault(c,[]).append(v)
    means={c:{g:float(np.mean([v[g] for v in seq])) for g in seq[0]} for c,seq in pooled.items()}
    comparator=max(['StepFinder','pairwise_B','local','recency'],key=lambda c:np.mean(list(means[c].values())))
    rng=np.random.default_rng(20260922); comparisons={}
    for c in ['StepFinder','pairwise_B','local','recency']:
        gs=sorted(means[c]); delta=np.array([means['A_plus_B'][g]-means[c][g] for g in gs]); samples=delta[rng.integers(0,len(gs),(5000,len(gs)))].mean(1); base=float(np.mean(list(means[c].values())))
        comparisons[c]={'absolute_delta':float(delta.mean()),'relative_gain':float(delta.mean()/base) if base else None,'ci95':np.quantile(samples,[.025,.975]).tolist(),'all_seed_positive':all(s['task_mrr']['A_plus_B']>s['task_mrr'][c] for s in seeds),'better':int((delta>1e-12).sum()),'worse':int((delta< -1e-12).sum()),'tie':int((abs(delta)<=1e-12).sum())}
    cc=comparisons[comparator]; go=all(final_checks.values()) and cc['relative_gain'] is not None and cc['relative_gain']>=.10 and cc['ci95'][0]>0 and cc['all_seed_positive']
    publish(HERE/'results/final_audit.json',{'checks':final_checks,'all_pass':all(final_checks.values()),'historical_fold_provenance':'independent reconstruction from immutable E96 split source, fixed data hashes and seeds; prior aggregate did not store explicit outer group lists','protocol_sha256':bound['protocol_sha256'],'runner_sha256':bound['runner_sha256'],'logical_outer_predictions':2193,'folds':15})
    publish(HERE/'results/panel_a.json',{'decision':'INTERNAL_GO' if go else 'STRONG_BASELINE_GAIN_NOT_ESTABLISHED','scope':'historically used internal development set only','n_records':731,'n_groups':716,'historical_sha256':sha(oldpath),'boundary':boundary,'seeds':seeds,'task_mrr_seed_mean':{c:float(np.mean(list(v.values()))) for c,v in means.items()},'strongest_baseline':comparator,'comparisons':comparisons,'group_details':details,'coverage':1.0,'api_calls':0,'cost':0})
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('mode',choices=['prepare','run']); args=p.parse_args()
    (prepare if args.mode=='prepare' else run)()

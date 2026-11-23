"""Independent prediction audit and durable checkpoint/embedding archives, no fitting."""
import hashlib,json,zipfile
from runner import HERE,ROOT,ASSETS,load,publish,sha,data
e,records,boundary=data()
historical=load(ROOT/'实验/实验112C_RQ1时序依赖排序纠正式复跑/results/formal_corrected_nested_oof_results.json')
for seed_output in historical['results_by_seed']:
    for condition in ['A_plus_B','pairwise_B','local','recency']:
        assert len(seed_output['raw_scores'][condition])==731
        assert all(len(scores)==len(records[i]['turns']) for i,scores in enumerate(seed_output['raw_scores'][condition]))
checks=[]; files=[]
for seed in (20260816,20260817,20260818):
    covered=set()
    for outer in range(5):
        fp=HERE/'results/folds'/f'{seed}_{outer}.json'; f=load(fp)
        cp=ROOT/f['checkpoint_path']; assert sha(cp)==f['checkpoint_sha256']
        freeze=load(HERE/'results/freezes'/f'{seed}_{outer}.json')
        assert freeze['checkpoint_sha256']==f['checkpoint_sha256']
        assert set(f['fit_groups']).isdisjoint(f['held_groups'])
        for index,p in f['predictions'].items():
            i=int(index); r=records[i]; n=len(r['turns']); assert i not in covered; covered.add(i)
            assert sorted(p['order'])==list(range(n)) and len(p['scores'])==n
            assert p['order']==sorted(range(n),key=lambda j:(-p['scores'][j],j))
            assert p['rank']==p['order'].index(r['mistake_step'])+1
            assert r['task_group'] in f['held_groups']
        files.append(cp)
        checks.append({'seed':seed,'outer':outer,'checkpoint_sha256':sha(cp),'predictions':len(f['predictions']),'order_scores_gold_evaluator_consistent':True,'state_persisted_before_held':freeze=={k:v for k,v in f.items() if k not in ['predictions','seconds','peak_gpu_bytes']}})
    assert covered==set(range(731))
archives=[]
for name,paths in [('checkpoints',files),('embeddings',sorted((ASSETS/'embeddings').glob('*.npz')))]:
    p=HERE/'results'/f'{name}.zip'
    with zipfile.ZipFile(p,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        members=[]
        for f in paths:
            member=f'{name}/{f.name}'; z.write(f,member); members.append({'path':member,'sha256':sha(f),'bytes':f.stat().st_size})
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        assert all(hashlib.sha256(z.read(m['path'])).hexdigest()==m['sha256'] for m in members)
    archives.append({'path':str(p.relative_to(HERE)),'sha256':sha(p),'bytes':p.stat().st_size,'members':members})
assert len(files)==15 and len(archives[1]['members'])==731
publish(HERE/'results/independent_result_audit.json',{'all_pass':all(x['state_persisted_before_held'] for x in checks),'checks':checks,'candidate_coverage':1.0,'historical_candidates_per_record_same':True,'records_per_seed':731,'groups_per_seed':716,'steps_per_seed':sum(len(r['turns']) for r in records),'no_extra_fit':True,'confirmation_scored':False})
publish(HERE/'results/artifact_manifest.json',{'archives':archives,'public_model_weights_committed':False,'retained_asset_root':str(ASSETS),'runtime_python':str(ROOT/'.venv/Scripts/python.exe'),'original_physical_assets_retained':True})
print(json.dumps({'archives':[{'path':x['path'],'bytes':x['bytes'],'sha256':x['sha256']} for x in archives],'all_prediction_checks':True}))

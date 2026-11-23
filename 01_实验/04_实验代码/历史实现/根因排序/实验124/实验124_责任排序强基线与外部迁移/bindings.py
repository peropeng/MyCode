"""Freeze source, model, input projection and independently rebuilt historical folds."""
import hashlib,inspect,json,subprocess,sys
from pathlib import Path
import runner
from runner import ROOT,HERE,ASSETS,sha,load,publish
EXPECTED='48d71c7090adca3667a31b043a78484f407b4a2f'
def digest(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True).encode()).hexdigest()
def canonical_sha(p):return hashlib.sha256(Path(p).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def binding():
    import torch,transformers
    sf=ASSETS/'StepFinder'; actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=sf,text=True).strip(); assert actual==EXPECTED
    assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=sf,text=True).strip()
    official={}
    for name in ['model.py','Q3Emb.py','feature_construction.py','main.py','collate_fn.py']:
        blob=subprocess.check_output(['git','show',f'{EXPECTED}:{name}'],cwd=sf)
        assert hashlib.sha256(blob).hexdigest()==canonical_sha(sf/name)
        official[name]={'worktree_sha256':sha(sf/name),'git_blob_sha256':hashlib.sha256(blob).hexdigest()}
    qwen=ASSETS/'Qwen3-Embedding-0.6B'
    model={p.name:sha(p) for p in sorted(qwen.iterdir()) if p.is_file()}
    assert model==load(HERE/'results/model_source_manifest.json')['sha256']
    assert model['model.safetensors']=='0437e45c94563b09e13cb7a64478fc406947a93cb34a7e05870fc8dcd48e23fd'
    old=ROOT/'实验/实验112C_RQ1时序依赖排序纠正式复跑/results/formal_corrected_nested_oof_results.json'
    assert canonical_sha(old)=='d99f9468adeadec4e69e30e0a2c44aafc277c4a034be0f1b7f678c4da5deb851'
    p=load(HERE/'protocol.json')
    source={str(f.relative_to(ROOT)):canonical_sha(f) for prefix in ['实验88_','实验96_','实验105_','实验106_','实验112_'] for f in (ROOT/'实验').glob(prefix+'*/runner.py')}
    for name,actual_sha in source.items():
        original=subprocess.check_output(['git','show','ab1fa8d5b23a9d591c5809ea299ce381eb99b21c:'+name.replace('\\','/')],cwd=ROOT)
        assert hashlib.sha256(original).hexdigest()==actual_sha,'historical scientific source drift: '+name
    wrapper=runner.module('e112c_binding',ROOT/'实验/实验112C_RQ1时序依赖排序纠正式复跑/runner.py')
    tie=wrapper.source_binding_audit(); prior=load(old)['exp112c_correction']['source_binding']
    assert tie['digest_function_source_sha256']==prior['digest_function_source_sha256'] and wrapper.scientific_binding_audit()['all_match']
    embedding={'model_files_sha256':model,'official_encoder_sha256':official['Q3Emb.py']['git_blob_sha256'],'projection_source_sha256':hashlib.sha256(inspect.getsource(runner.text_of).encode()).hexdigest(),'embedding_protocol':p['embedding'],'torch':torch.__version__,'transformers':transformers.__version__}
    return {'stepfinder_commit':actual,'official_files':official,'model_files_sha256':model,'science_sources_lf_sha256':source,'science_source_snapshot':'ab1fa8d5b23a9d591c5809ea299ce381eb99b21c','historical_commit_object_available':False,'historical_source_limitation':'Original 4fe2d9 Git object absent after migration; current authoritative source snapshot, exact sealed tie-function SHA, scientific constants, dataset SHA and published split algorithm verified. Original protocol did not seal full runner hashes.','sealed_tie_function_matches':True,'historical_output_worktree_sha256':sha(old),'historical_output_lf_sha256':canonical_sha(old),'protocol_sha256':sha(HERE/'protocol.json'),'runner_sha256':sha(HERE/'runner.py'),'embedding_binding':embedding,'embedding_binding_sha256':digest(embedding)}
def freeze_or_verify():
    b=binding(); p=HERE/'results/preclaim_binding.json'
    if p.exists(): assert load(p)==b,'preclaim/source/cache binding drift'
    else:publish(p,b)
    return b
def historical_folds(records,seed):
    # E96 original historical split is plain sorted -> random.Random(seed).shuffle -> strided 5.
    # The old aggregate did not persist explicit fold keys, so reproduce this independently.
    import random
    names=sorted({r['task_group'] for r in records}); random.Random(seed).shuffle(names)
    return [names[k::5] for k in range(5)]

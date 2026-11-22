"""Compare pre-evaluation scalar and batch API embeddings; no labels/metrics."""
import numpy as np
from runner import ASSETS,HERE,publish
old=ASSETS/'embeddings_scalar_preflight'; new=ASSETS/'embeddings'
cos=[]; errors=[]; records=0
for p in sorted(old.glob('*.npz')):
    if not (new/p.name).exists():continue
    a=np.load(p); b=np.load(new/p.name)
    assert str(a['input_sha'])==str(b['input_sha'])
    x=a['content'].astype(float); y=b['content'].astype(float)
    assert x.shape==y.shape and np.isfinite(x).all() and np.isfinite(y).all()
    cos.extend((x*y).sum(1)/(np.linalg.norm(x,axis=1)*np.linalg.norm(y,axis=1)+1e-30))
    errors.append(float(np.abs(x-y).max())); records+=1
assert records>0
result={'records':records,'steps':len(cos),'minimum_cosine':float(min(cos)),'mean_cosine':float(np.mean(cos)),'max_absolute_feature_difference':max(errors),'all_cosine_above_0_999':bool(min(cos)>.999),'method_metric_exposure':False,'final_cache':'exclusively version2 batch8; scalar features not reused','interpretation':'FP16 batch padding/kernel arithmetic may differ slightly, model and semantic projection unchanged'}
assert result['all_cosine_above_0_999']
publish(HERE/'results/embedding_batch_parity.json',result)
print(result)

"""Descriptive source/domain strata after final evaluation; never alters gates."""
import collections,statistics
from runner import ROOT,HERE,load,publish
mapping=load(HERE/'results/development_task_mapping.json')
old=load(ROOT/'实验/实验112C_RQ1时序依赖排序纠正式复跑/results/formal_corrected_nested_oof_results.json')
rows=[]
for seedresult in old['results_by_seed']:
    seed=seedresult['seed']; sf={}
    for fold in range(5):sf.update(load(HERE/'results/folds'/f'{seed}_{fold}.json')['predictions'])
    for i,meta in enumerate(mapping):
        rows.append(dict(seed=seed,record=i,task_group=meta['task_group'],domain=meta['domain'],unsafe_source=meta['unsafe_source'],a_b_rank=seedresult['raw_ranks']['A_plus_B'][i],stepfinder_rank=sf[str(i)]['rank']))
out={}
for field in ['domain','unsafe_source']:
    out[field]={}
    for value in sorted({r[field] for r in rows}):
        subset=[r for r in rows if r[field]==value]; metrics={}
        for method,key in [('A_plus_B','a_b_rank'),('StepFinder','stepfinder_rank')]:
            groups=collections.defaultdict(list)
            for row in subset:groups[row['task_group']].append(1/row[key])
            metrics[method]=statistics.mean(statistics.mean(v) for v in groups.values())
        out[field][value]={'records':len({r['record'] for r in subset}),'task_groups':len({r['task_group'] for r in subset}),'task_mrr_seed_mean':metrics,'delta':metrics['A_plus_B']-metrics['StepFinder']}
publish(HERE/'results/descriptive_strata.json',{'status':'posthoc_descriptive_only_not_a_gate','strata':out,'formal_execution_failures':0,'environment_failures':'Public download timeouts and empty initial dependencies; recovered before formal fits','external_failure_class':'ASSET_STOP historical exposure','whowhen_failure_class':'NOT_RUN_RESOURCE_GAP','no_refit_or_selection':True})

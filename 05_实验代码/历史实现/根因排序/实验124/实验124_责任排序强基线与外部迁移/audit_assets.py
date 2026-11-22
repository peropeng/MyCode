"""Read-only asset/history gate; never score historical confirmation."""
import hashlib,json,os,subprocess
from pathlib import Path
from runner import HERE,ROOT,ASSETS,load,sha,publish,data
def main():
    manifest=load(ROOT/'实验/实验58_AFTraj外测资产恢复_Gate0/results/asset_manifest.json')
    checks=[]
    for f in manifest['dataset']['files']:
        p=ASSETS/'AFTraj'/f['path']; actual=sha(p)
        checks.append({'path':str(p.relative_to(ROOT)),'sha256':actual,'expected':f['sha256'],'match':actual==f['sha256'],'bytes':p.stat().st_size})
    assert all(c['match'] for c in checks)
    sf=ASSETS/'StepFinder'; commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=sf,text=True).strip()
    assert commit=='48d71c7090adca3667a31b043a78484f407b4a2f'
    history=ROOT/'实验/实验84_TraceElephant选择门_零样本步骤外测'
    h=load(history/'results/exp84_result.json'); ledger=load(history/'source_manifest.json'); protocol=load(history/'protocol.json')
    members=sorted({r['purpose'].split('/',1)[1].split(':')[0] for r in ledger['download_records'] if r['purpose'].startswith('metadata/')})
    runs=sorted({p.split('/')[-2] for p in members})
    assert len(runs)==219
    rows=load(history/'results/row_predictions.json'); assert len(rows)==217
    dev=protocol['source']['adapter_development_run']['run_id']; assert dev not in runs
    external={'decision':'ASSET_STOP','reason':'All 220 released runs have historical adapter/development/evaluation exposure before this freeze. A new model on the same dataset is not unseen external confirmation.','revision':protocol['source']['traceelephant_hf_revision'],'prior_evaluated_runs':217,'prior_evaluated_task_groups':172,'prior_label_unparseable_runs':2,'prior_adapter_run':dev,'prior_fetched_runs':219,'total_historical_exposure_runs':220,'unseen_eligible_runs':0,'unseen_eligible_task_groups':0,'new_model_evaluations':0,'history_files':{str(p.relative_to(ROOT)):sha(p) for p in [history/'results/exp84_result.json',history/'results/row_predictions.json',history/'source_manifest.json',history/'protocol.json']},'historical_runs':runs+[dev],'label_mapping':'Existing Exp84 verified strictly increasing unique original step_id and exact Gold map for 217 rows. Exp124 multi-gold rule is frozen in protocol, but no eligible unseen run remains to evaluate.','cross_dataset_overlap':'Not required to establish zero eligibility: whole dataset removed by prior-use gate. No claim that cross-dataset questions are disjoint.','license':'Dataset card/repository historical audit CC BY 4.0; no data redistributed.'}
    if (HERE/'results/external_gate.json').exists():
        assert load(HERE/'results/external_gate.json')==external
    else: publish(HERE/'results/external_gate.json',external)
    e,records,boundary=data()
    # Keep raw task text out of method; exported only for overlap audit.
    source=ROOT/'实验/实验33_旧版场景F责任主体/real_feasibility_group6'
    io,_=e.E88.load_bound_source(str(source)); raw,test_ids,overlap=io.load_aftraj(str(ASSETS/'AFTraj'))
    groups={r['task_group'] for r in records}
    mapping=[{'task_group':r['task_group'],'conv_id':r['conv_id'],'task':r['task'],'unsafe_source':r['unsafe_source'],'domain':r['domain']} for r in raw if r['task_group'] in groups and r['conv_id'] not in test_ids]
    assert len(mapping)==731
    publish(HERE/'results/development_task_mapping.json',mapping)
    gate={'decision':'PANEL_A_ASSETS_READY_PANEL_B_ASSET_STOP','data_files':checks,'development_boundary':boundary,'stepfinder_commit':commit,'stepfinder_files':{n:sha(sf/n) for n in ['model.py','Q3Emb.py','feature_construction.py','main.py','requirements.txt']},'historical_comparator_sha256':sha(ROOT/'实验/实验112C_RQ1时序依赖排序纠正式复跑/results/formal_corrected_nested_oof_results.json'),'environment':{'python':os.sys.version,'nvidia_smi':subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,driver_version','--format=csv,noheader'],text=True).strip()},'api_calls':0,'new_paid_resources':0,'confirmation_scored':False}
    publish(HERE/'results/asset_gate.json',gate)
    print(json.dumps({'data_hashes_match':True,'development_records':len(records),'external_unseen_eligible':0}))
if __name__=='__main__':main()

"""Frozen15 local predictions on fresh PUBLIC inputs; never loads test labels."""
import sys
from pathlib import Path
T=Path(__file__).resolve().parent;E=T.parent
sys.path.insert(0,str(E));sys.dont_write_bytecode=True
import numpy as np
import torch
import train,models,prepare_features
from shared import *

def main():
    p=verify();records=read(T/'fresh_public_records.json')['records'];by={r['sample_id']:r for r in records};ids=[r['sample_id'] for r in records]
    if (T/'local_predictions.json').exists():raise RuntimeError('fresh_local_predictions_already_sealed_no_regeneration')
    path=E/'features/fresh_confirmation_features.pt'
    if not path.exists():prepare_features.build(records,'fresh_confirmation_features.pt')
    receipt=read(path.with_suffix('.receipt.json'))
    if sha(path)!=receipt['feature_file_sha256']:raise RuntimeError('fresh_feature_seal_changed')
    features=torch.load(path,map_location='cpu',weights_only=False)['records'];modelseal=read(E/'training/model_seal.json')
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu');out={sid:{} for sid in ids}
    for arm in ARMS:
        seeds=[]
        for seed in SEEDS:
            r=next(r for r in modelseal['models'] if r['arm']==arm and r['seed']==seed)
            checkpoint=torch.load(r['checkpoint'],map_location='cpu',weights_only=False)
            scaler=(checkpoint['scaler_mean'],checkpoint['scaler_std'])
            model=models.create(arm).to(device);model.load_state_dict(checkpoint['state_dict'])
            predictions=train.predict(model,arm,ids,features,scaler,device);seeds.append(predictions)
            for sid,prediction in predictions.items():out[sid][arm+'/seed_'+str(seed)]={**prediction,'predicted_role':by[sid]['turns'][prediction['chosen_step']]['role'],
                'native_complete_ranking':True,'role_output_origin':'derived_from_chosen_public_step','checkpoint_sha256':r['checkpoint_sha256']}
            del model;torch.cuda.empty_cache()
        for sid in ids:
            probabilities=np.mean([r[sid]['probabilities'] for r in seeds],axis=0).tolist()
            ranking=sorted(range(len(probabilities)),key=lambda i:(-probabilities[i],i))
            out[sid][arm]={'valid':True,'chosen_step':ranking[0],'predicted_role':by[sid]['turns'][ranking[0]]['role'],
                'order':ranking,'probabilities':probabilities,'native_complete_ranking':True,'role_output_origin':'derived_from_chosen_public_step',
                'ensemble_seeds':list(SEEDS),'ensemble_rule':'unweighted mean of all3 softmaxes'}
    for sid in ids:out[sid].update(qualified_priors(by[sid]))
    write(T/'local_predictions.json',{'at_utc':now(),'predictions':out,'protocol_sha256':sha(T/'protocol.json'),'fresh_Gold_accesses':0})
    write(T/'local_prediction_seal.json',{'at_utc':now(),'predictions_sha256':sha(T/'local_predictions.json'),
        'protocol_sha256':sha(T/'protocol.json'),'public_scope_sha256':sha(T/'public_scope_seal.json'),'local_model_conditions':20,'fresh_Gold_accesses':0})
    CORE.status('EXP134_CONFIRMATION_LOCAL_OUTPUTS_SEALED',fresh_confirmation={'completed_tasks':0,'total_tasks':len(ids),'local_complete_tasks':len(ids),'unexposed_test_label_accesses':0},
        paid_API_calls=0,next_executable_command='confirmation/run_paid.py')
    print(canonical({'fresh_local_tasks_sealed':len(ids),'fixed_model_runs':15,'paid_API_calls':0,'fresh_Gold_accesses':0}),flush=True)

if __name__=='__main__':main()

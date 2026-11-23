"""Preset choice consumes only sealed inner-validation stage histories."""
from common import *

def choose_preset(metrics):
 if set(metrics)!=set(ARMS):raise ValueError('Exactly two paper presets required')
 for arm,v in metrics.items():
  if not all(type(v[k]) in (int,float) and 0<=v[k]<=1 for k in ('Top1','MRR')):raise ValueError('Inner validation metrics required')
 return max(ARMS,key=lambda a:(metrics[a]['Top1'],metrics[a]['MRR'],-ARMS.index(a)))

def selected_validation(rec):
 rows=[r for r in rec['history'] if r['epoch']==rec['selected_epoch']]
 if len(rows)!=1 or 'validation' not in rows[0]:raise RuntimeError('Best checkpoint inner-validation history required')
 return rows[0]['validation']

def freeze_decisions(p,model_seal):
 path=E/'validation_selection_decisions.json';sealpath=E/'validation_selection_sealed.json'
 if path.exists() or sealpath.exists():
  if not path.exists() or not sealpath.exists():raise RuntimeError('Incomplete single-use validation selection seal')
  seal=read(sealpath)
  if seal['decisions_sha256']!=sha(path) or seal['protocol_sha256']!=sha(E/'protocol.json') or seal['model_seal_sha256']!=sha(E/'training/all_models_sealed.json'):raise RuntimeError('Existing preset decisions changed')
  return read(path)
 fitted={(r['suite'],r['arm'],r['seed'],r.get('outer')):r for r in model_seal['models']}
 decisions=[]
 for suite,seeds,outers in (('source',SOURCE_SEEDS,(None,)),('AF',AF_SEEDS,tuple(range(5)))):
  for seed in seeds:
   for outer in outers:
    metrics={};options={}
    for arm in ARMS:
     folder=E/'training'/suite/arm/(str(seed) if suite=='source' else f'{seed}_{outer}')
     stagepath=folder/('source_fit.json' if suite=='source' else 'selection.json');rec=read(stagepath)
     metric=selected_validation(rec);final=fitted[suite,arm,seed,outer]
     metrics[arm]={'Top1':metric['Top1'],'MRR':metric['MRR']}
     options[arm]={'validation_metric':metric,'selected_epoch':rec['selected_epoch'],'validation_stage_path':str(stagepath),
      'validation_stage_sha256':sha(stagepath),'validation_ids_sha256':rec['validation_ids_sha256'],
      'final_checkpoint':final['checkpoint'],'final_checkpoint_sha256':final['checkpoint_sha256'],'preset_configuration':PROFILES[arm],
      'native_prediction_sources':{c:str(prediction_path(c,arm,seed)) for c in COHORTS} if suite=='source' else {'AF':str(fold_prediction_path(arm,seed,outer))}}
    if options[ARMS[0]]['validation_ids_sha256']!=options[ARMS[1]]['validation_ids_sha256']:raise RuntimeError('Matched identical validation IDs required')
    winner=choose_preset(metrics)
    decisions.append({'suite':suite,'seed':seed,'outer':outer,'chosen_preset':winner,'complete_metric_tie':metrics[ARMS[0]]==metrics[ARMS[1]],
     'rule':'Inner-validation Top1 then MRR, complete tie ALG','target_or_held_outcomes_consumed':0,'options':options})
 if len(decisions)!=18:raise RuntimeError('Exactly3source+15AF validation decisions required')
 value={'at_utc':now(),'experiment':'Exp158','status':'FROZEN','name':SELECTED,'decisions':decisions,'decision_count':18,
  'source_decisions':3,'AF_decisions':15,'protocol_sha256':sha(E/'protocol.json'),'model_seal_sha256':sha(E/'training/all_models_sealed.json'),
  'target_scores_or_target_labels_consumed':0,'held_correctness_never_used_for_preset_choice':True,'no_new_optimization_or_neural_forward':True}
 write_new(path,value)
 write_new(sealpath,{'at_utc':now(),'experiment':'Exp158','status':'PASS','decisions_sha256':sha(path),'protocol_sha256':value['protocol_sha256'],
  'model_seal_sha256':value['model_seal_sha256'],'all18_validation_only_choices_sealed':True,'target_labels_joined':0,
  'selection_code_sha256':sha(E/'select158.py')})
 return value

if __name__=='__main__':
 p=read(E/'protocol.json');m=read(E/'training/all_models_sealed.json')
 if not m['all_fixed_models_sealed'] or m['optimization_stages']!=66 or m['final_models']!=36:raise RuntimeError('Complete158 model seal required')
 freeze_decisions(p,m)

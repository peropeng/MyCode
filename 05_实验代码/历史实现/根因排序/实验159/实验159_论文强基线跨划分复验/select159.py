"""Nine validation-only preset choices, sealed before any target scoring."""
from common import *
def choose_preset(metrics):
 if set(metrics)!=set(ARMS):raise ValueError('Exactly two frozen presets required')
 for metric in metrics.values():
  if not all(type(metric[k]) in (int,float) and 0<=metric[k]<=1 for k in ('Top1','MRR')):raise ValueError('Valid inner metrics required')
 return max(ARMS,key=lambda a:(metrics[a]['Top1'],metrics[a]['MRR'],-ARMS.index(a)))
def selected_validation(rec):
 rows=[r for r in rec['history'] if r['epoch']==rec['selected_epoch']]
 if len(rows)!=1 or 'validation' not in rows[0]:raise RuntimeError('Exact selected validation metric required')
 return rows[0]['validation']
def freeze_decisions(p,model_seal):
 path=E/'validation_selection_decisions.json';sealpath=E/'validation_selection_sealed.json'
 if path.exists() or sealpath.exists():
  if not path.exists() or not sealpath.exists() or read(sealpath)['decisions_sha256']!=sha(path):raise RuntimeError('Incomplete or changed existing choices')
  return read(path)
 if (model_seal['optimization_stages'],model_seal['final_models'])!=(18,18):raise RuntimeError('Complete18 models required')
 fitted={(r['replication_block'],r['arm'],r['seed']):r for r in model_seal['models']};decisions=[]
 for block in BLOCKS:
  for seed in SOURCE_SEEDS:
   metrics={};options={}
   for arm in ARMS:
    stagepath=E/'training/source'/block/arm/str(seed)/'source_fit.json';rec=read(stagepath);metric=selected_validation(rec);final=fitted[block,arm,seed]
    metrics[arm]={k:metric[k] for k in ('Top1','MRR')}
    options[arm]={'validation_metric':metric,'selected_epoch':rec['selected_epoch'],'validation_stage_path':str(stagepath),'validation_stage_sha256':sha(stagepath),'validation_ids_sha256':rec['validation_ids_sha256'],'final_checkpoint':final['checkpoint'],'final_checkpoint_sha256':final['checkpoint_sha256'],'preset_configuration':PROFILES[arm],'native_prediction_sources':{c:str(prediction_path(c,arm,block,seed)) for c in COHORTS}}
   if options[ARMS[0]]['validation_ids_sha256']!=options[ARMS[1]]['validation_ids_sha256']:raise RuntimeError('Matched validation members required')
   decisions.append({'suite':'source','replication_block':block,'seed':seed,'outer':None,'chosen_preset':choose_preset(metrics),'complete_metric_tie':metrics[ARMS[0]]==metrics[ARMS[1]],'rule':'innerTop1→MRR; complete tie ALG','target_or_held_outcomes_consumed':0,'options':options})
 value={'at_utc':now(),'experiment':'Exp159','status':'FROZEN','name':SELECTED,'decisions':decisions,'decision_count':9,'source_decisions':9,'AF_decisions':0,'protocol_sha256':sha(E/'protocol.json'),'model_seal_sha256':sha(E/'training/all_models_sealed.json'),'target_scores_or_target_labels_consumed':0,'held_correctness_never_used_for_preset_choice':True,'no_new_optimization_or_neural_forward':True}
 write_new(path,value);write_new(sealpath,{'at_utc':now(),'status':'PASS','decisions_sha256':sha(path),'protocol_sha256':value['protocol_sha256'],'model_seal_sha256':value['model_seal_sha256'],'all9_validation_only_choices_sealed':True,'target_labels_joined':0,'selection_code_sha256':sha(E/'select159.py')})
 return value

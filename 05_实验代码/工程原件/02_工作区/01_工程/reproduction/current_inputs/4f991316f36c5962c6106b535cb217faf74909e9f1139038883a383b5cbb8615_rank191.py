"""G153 unchanged functions and weights; genuine public-only new3 inference."""
from common191 import *
import gc
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1';os.environ['HF_DATASETS_OFFLINE']='1'
os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
C={'tokenizer_loads':0,'tokenizer_prechecks':0,'encoder_loads':0,'encoder_forward_batches':0,'ranker_loads':0,'ranker_forward_batches':0,'ranker_task_outputs':0,'training':0,'new_weights':0,'historical_generation':0,'native':0,'paid':0}
def record():save(E/'neural_actual_counters191.json',{'at_utc':now(),**C})
def main():
 require();import torch,numpy as np
 torch.set_num_threads(3)
 prep=module('original_rank191',E/'ranking_prepare178.py');prep.E=E
 refs=read(E/'frozen15_bindings.json')['tasks'];samples={s['sample_id']:s for s in lines(E/'data/public_inputs.jsonl')}
 records=prep.model_records();assert digest(records)==read(E/'model_bindings191.json')['digest']
 from transformers import AutoTokenizer
 bound=read(ROOT/'工作区/0922-exp124-ranking-baselines/实验/实验124_责任排序强基线与外部迁移/results/preclaim_binding.json')
 for p,h in bound['model_files_sha256'].items():assert sha(prep.QROOT/p)==h
 tokenizer=AutoTokenizer.from_pretrained(str(prep.QROOT),revision=prep.REVISION,trust_remote_code=True,padding_side='left',local_files_only=True);C['tokenizer_loads']+=1;record()
 rows=[];allowed=[]
 for r in refs[12:]:
  tid=r['task_id'];texts=prep.texts_of(samples[tid]['turns']);tokens=[]
  for text in texts:require();tokens.append(len(tokenizer(text,add_special_tokens=True,truncation=False)['input_ids']));C['tokenizer_prechecks']+=1
  bad=[i for i,n in enumerate(tokens) if n>8192]
  row={'task_id':tid,'tokens_per_complete_original_step':tokens,'truncation':False,'max_length':8192,'texts_sha256':hashlib.sha256(json.dumps(texts,ensure_ascii=False).encode()).hexdigest(),'status':'UNKNOWN_WHOLE_PUBLIC_STEP_OVER8192' if bad else 'FIT_PASS','over_cap_steps':bad}
  rows.append(row)
  if not bad:allowed.append(r)
  save(E/'features/tokenizer_whole_step_gate191.json',{'at_utc':now(),'rows':rows,'actual_tokenizer_prechecks':C['tokenizer_prechecks'],'precheck_before_all_encoder_forwards':True});record();print(canonical(row),flush=True)
 data={};encoder=None;roles={};content_cache={};feature_rows=[]
 if allowed:
  require();q3=module('unchanged_qwen191',prep.Q3);assert q3.DEFAULT_MODEL_REVISION==prep.REVISION
  encoder=q3.Qwen3Embedding(str(prep.QROOT),use_cuda=torch.cuda.is_available(),max_length=8192);C['encoder_loads']+=1;record()
  helper=module('unchanged_structure191',prep.STRUCTURE);events=module('unchanged_events191',prep.EVENTS)
  save(E/'features/encoder_identity191.json',{'revision':prep.REVISION,'file_SHAs':bound['model_files_sha256'],'device':str(encoder.model.device),'dtype':str(next(encoder.model.parameters()).dtype),'source':str(prep.Q3),'source_sha256':sha(prep.Q3),'max_length':8192,'separate_precheck_no_text_truncation':True})
  for r in allowed:
   tid=r['task_id'];turns=samples[tid]['turns'];texts=prep.texts_of(turns);content=[];agent=[];before=C['encoder_forward_batches']
   for text,t in zip(texts,turns):
    require();role=t['role'];key=hashlib.sha256(text.encode()).hexdigest()
    if role not in roles:
     roles[role]=encoder.encode([role],dim=32).float().cpu().numpy()[0];C['encoder_forward_batches']+=1;record()
    if key not in content_cache:
     content_cache[key]=encoder.encode([text],dim=128).float().cpu().numpy()[0];C['encoder_forward_batches']+=1;record()
    content.append(content_cache[key]);agent.append(roles[role])
   content=np.asarray(content,dtype=np.float32);agent=np.asarray(agent,dtype=np.float32)
   assert np.isfinite(content).all() and np.isfinite(agent).all()
   data[tid],links=prep.feature_geometry(samples[tid],content,agent,helper,events,torch,np)
   feature_rows.append({'task_id':tid,'new_encoder_batches':C['encoder_forward_batches']-before,'input_turns_sha256':r['input_turns_sha256'],'source':'ORIGINAL_QWEN_CONTENT128_ROLE32_RAW_FLOAT32','observed_state_action_links':links})
   print(canonical({'task':tid,'phase':'NEW_PUBLIC_FEATURES_READY','encoder_forward_batches':C['encoder_forward_batches']}),flush=True)
  del encoder;gc.collect();torch.cuda.empty_cache()
 (E/'features').mkdir(exist_ok=True);torch.save({'records':data,'no_labels_or_private_results':True},E/'features/features191.pt')
 save(E/'features/feature_receipt191.json',{'rows':feature_rows,'feature_sha256':sha(E/'features/features191.pt'),'actual_counts':C})
 predictions=read(E/'cached12_predictions191.json');ids=sorted(data);outputs=[]
 if ids:
  models=prep.models_scoped();models.seed_all(0);seedouts=[]
  def ensemble(group):return {sid:prep.pack(np.mean([v[sid]['probabilities'] for v in group],axis=0,dtype=np.float64).tolist()) for sid in ids}
  for seed in prep.SEEDS:
   folds=[]
   for outer in range(5):
    require();r=next(r for r in records if (r['seed'],r['outer'])==(seed,outer));assert sha(r['checkpoint'])==r['checkpoint_sha256']
    ck=torch.load(r['checkpoint'],map_location='cpu',weights_only=False);model=models.create('AB_GLOBAL').cpu();model.load_state_dict(ck['state_dict'],strict=True);model.eval();C['ranker_loads']+=1;record()
    with torch.no_grad():
     batch=models.collate(ids,data,(ck['scaler_mean'],ck['scaler_std']),torch.device('cpu'));scores,_=models.forward(model,'AB_GLOBAL',batch);C['ranker_forward_batches']+=1;C['ranker_task_outputs']+=len(ids);record()
     out={sid:prep.pack(torch.softmax(score.cpu(),0).tolist()) for sid,score in zip(batch['ids'],scores)}
    p=E/'ranking/AB_GLOBAL'/f'{seed}_{outer}.json';save(p,{'predictions':out,'checkpoint_sha256':r['checkpoint_sha256'],'same_original_unchanged_algorithm':True});outputs.append({'path':str(p),'sha256':sha(p)});folds.append(out)
    del ck,model,batch,scores;gc.collect()
   seedouts.append(ensemble(folds))
  predictions.update(ensemble(seedouts))
 merged=E/'ranking/AB_GLOBAL/ensemble.json';save(merged,{'predictions':predictions,'15_original_models':True,'unknown_new_tasks':[x['task_id'] for x in rows if x['status']!='FIT_PASS']})
 plans={}
 for r in refs:
  tid=r['task_id']
  if tid not in predictions:continue
  pred=predictions[tid];p=E/'ranking/plans'/tid/'OURS_G153_VBR.json';save(p,{'task_id':tid,'method':'OURS_G153_VBR','complete_original_ordinal_order':pred['order'],'probabilities':pred['probabilities'],'chosen_step':pred['chosen_step'],'input_turns_sha256':r['input_turns_sha256'],'mapping_digest':digest(r['mapping']),'checkpoint_manifest_digest':digest(records),'checkpoint_bindings':records,'source':{'path':str(merged),'sha256':sha(merged),'all15_models_averaged':True},'new_forward':tid in ids,'old12_verified_cache':tid not in ids})
  plans[tid]={'path':str(p),'sha256':sha(p)}
 record();save(E/'ranking/ranking_qualification191.json',{'at_utc':now(),'status':'PASS_ALL15' if len(plans)==15 else 'PARTIAL_UNKNOWN','plans':plans,'unknown_tasks':[r['task_id'] for r in refs if r['task_id'] not in plans],'tokenizer_gate':rows,'counts':C,'ranker_outputs':outputs,'checkpoint_manifest_digest':digest(records),'source':str(prep.M153/'context_models.py'),'source_sha256':sha(prep.M153/'context_models.py'),'new_embedding_forward':C['encoder_forward_batches'],'new_ranker_forward':C['ranker_forward_batches'],'new_training':0,'new_Gold':0})
 print(canonical({'phase':'RANKING_FINISHED','plans':len(plans),'counts':C}),flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:record();save(E/'rank_error191.json',{'at_utc':now(),'type':type(e).__name__,'error':str(e),'counts':C,'no_fallback_order':True});raise

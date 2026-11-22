"""Actual new8 features/ranks from unchanged G153 functions and15 fixed models."""
from common166 import *
import gc
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1';os.environ['HF_DATASETS_OFFLINE']='1';os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
COUNTS={'tokenizer_loads':0,'tokenizer_whole_step_checks':0,'encoder_loads':0,'encoder_forward_batches':0,'encoder_unique_texts':0,'ranker_loads':0,'ranker_forward_batches':0,'ranker_task_outputs':0,'training':0,'new_weights':0,'paid_API':0,'native':0,'new_Gold':0}
P191=ROOT/'工作区/1008-exp191-public-rank-output-interface/实验/实验191_十五题公开排序与约束输出接口资格'
def record(phase,**extra):save(E/'ranking/new8_execution224.json',{'at_utc':now(),'phase':phase,'pid':os.getpid(),'counts':COUNTS,**extra})
def main():
 begin=time.monotonic();import torch,numpy as np
 torch.set_num_threads(3)
 prep=module('exp224_original_feature_and_G',P191/'ranking_prepare178.py');prep.E=E
 refs=read(E/'data/selected_task_bindings.json')['tasks'];samples={s['sample_id']:s for s in lines(E/'data/public_inputs.jsonl')}
 missing=[r for r in refs if not r.get('G_frozen_plan')];assert len(missing)==8
 records=prep.model_records();assert len(records)==15 and all(r['arm']=='AB_GLOBAL' and r['suite']=='AF' for r in records)
 identity={str(P191/'ranking_prepare178.py'):sha(P191/'ranking_prepare178.py'),str(prep.M153/'context_models.py'):sha(prep.M153/'context_models.py'),str(prep.STRUCTURE):sha(prep.STRUCTURE),str(prep.EVENTS):sha(prep.EVENTS),str(prep.Q3):sha(prep.Q3)}
 for r in records:assert sha(r['checkpoint'])==r['checkpoint_sha256'];identity[r['checkpoint']]=r['checkpoint_sha256']
 input_seals={str(E/'data/selected_task_bindings.json'):sha(E/'data/selected_task_bindings.json'),str(E/'data/public_inputs.jsonl'):sha(E/'data/public_inputs.jsonl')}
 save(E/'ranking/new8_model_input_seal224.json',{'at_utc':now(),'sources':identity,'inputs':input_seals,'models':records,'model_identity_digest':digest(records),'no_new_training_or_labels':True,'before_any_tokenizer_or_encoder_forward':True})
 from transformers import AutoTokenizer
 bound=read(ROOT/'工作区/0922-exp124-ranking-baselines/实验/实验124_责任排序强基线与外部迁移/results/preclaim_binding.json')
 for p,h in bound['model_files_sha256'].items():assert sha(prep.QROOT/p)==h
 tokenizer=AutoTokenizer.from_pretrained(str(prep.QROOT),revision=prep.REVISION,trust_remote_code=True,padding_side='left',local_files_only=True);COUNTS['tokenizer_loads']+=1
 gate=[];allowed=[]
 for r in missing:
  texts=prep.texts_of(samples[r['task_id']]['turns']);tokens=[]
  for text in texts:tokens.append(len(tokenizer(text,add_special_tokens=True,truncation=False)['input_ids']));COUNTS['tokenizer_whole_step_checks']+=1
  bad=[i for i,n in enumerate(tokens) if n>8192];gate.append({'task_id':r['task_id'],'all_original_step_tokens':tokens,'over8192_steps':bad,'no_text_clipping':True,'status':'WHOLE_STEP_CONTEXT_UNKNOWN' if bad else 'FIT'})
  if not bad:allowed.append(r)
  save(E/'features/whole_step_preflight224.json',{'rows':gate,'counts':COUNTS});record('WHOLE_STEP_TOKENIZER',task_id=r['task_id'])
 del tokenizer;gc.collect();data={};roles={};cache={};feature_rows=[]
 if allowed:
  q3=module('exp224_original_qwen',prep.Q3);assert q3.DEFAULT_MODEL_REVISION==prep.REVISION
  encoder=q3.Qwen3Embedding(str(prep.QROOT),use_cuda=torch.cuda.is_available(),max_length=8192);COUNTS['encoder_loads']+=1
  helper=module('exp224_original_structure',prep.STRUCTURE);events=module('exp224_original_state_action',prep.EVENTS)
  save(E/'features/encoder_identity224.json',{'revision':prep.REVISION,'model_files':bound['model_files_sha256'],'source':str(prep.Q3),'source_sha256':sha(prep.Q3),'device':str(encoder.model.device),'dtype':str(next(encoder.model.parameters()).dtype),'dimensions_content_role':[128,32],'max_length':8192,'whole_step_tokenizer_precheck_before_forward':True})
  for r in allowed:
   tid=r['task_id'];turns=samples[tid]['turns'];texts=prep.texts_of(turns);content=[];agent=[];start=COUNTS['encoder_forward_batches']
   assert hashlib.sha256(json.dumps(turns,sort_keys=True).encode()).hexdigest()==r['input_turns_sha256']
   for text,t in zip(texts,turns):
    role=t['role'];key=hashlib.sha256(text.encode()).hexdigest()
    if role not in roles:roles[role]=encoder.encode([role],dim=32).float().cpu().numpy()[0];COUNTS['encoder_forward_batches']+=1;COUNTS['encoder_unique_texts']+=1
    if key not in cache:cache[key]=encoder.encode([text],dim=128).float().cpu().numpy()[0];COUNTS['encoder_forward_batches']+=1;COUNTS['encoder_unique_texts']+=1
    content.append(cache[key]);agent.append(roles[role]);record('ACTUAL_NEW_RAW_ENCODER',task_id=tid)
   content=np.asarray(content,dtype=np.float32);agent=np.asarray(agent,dtype=np.float32);assert np.isfinite(content).all() and np.isfinite(agent).all()
   data[tid],links=prep.feature_geometry(samples[tid],content,agent,helper,events,torch,np)
   feature_rows.append({'task_id':tid,'input_turns_sha256':r['input_turns_sha256'],'actual_new_encoder_batches':COUNTS['encoder_forward_batches']-start,'observed_state_action_links':links,'old_exact_feature_cache_claimed':False})
  del encoder;gc.collect();torch.cuda.empty_cache()
 (E/'features').mkdir(exist_ok=True);torch.save({'records':data,'no_labels_or_private_results':True},E/'features/new8_features224.pt');save(E/'features/new8_feature_receipt224.json',{'rows':feature_rows,'features_sha256':sha(E/'features/new8_features224.pt'),'counts':COUNTS})
 ids=sorted(data);models=prep.models_scoped();models.seed_all(0);seedouts=[]
 for seed in prep.SEEDS:
  folds=[]
  for outer in range(5):
   r=next(r for r in records if (r['seed'],r['outer'])==(seed,outer));ck=torch.load(r['checkpoint'],map_location='cpu',weights_only=False);model=models.create('AB_GLOBAL').cpu();model.load_state_dict(ck['state_dict'],strict=True);model.eval();COUNTS['ranker_loads']+=1
   with torch.no_grad():
    batch=models.collate(ids,data,(ck['scaler_mean'],ck['scaler_std']),torch.device('cpu'));scores,_=models.forward(model,'AB_GLOBAL',batch);COUNTS['ranker_forward_batches']+=1;COUNTS['ranker_task_outputs']+=len(ids)
    out={sid:prep.pack(torch.softmax(score.cpu(),0).tolist()) for sid,score in zip(batch['ids'],scores)}
   save(E/'ranking/AB_GLOBAL'/f'{seed}_{outer}.json',{'predictions':out,'checkpoint_sha256':r['checkpoint_sha256'],'unchanged_original_G153':True});folds.append(out);record('ACTUAL_G153_FIXED_RANKER',seed=seed,outer=outer)
   del ck,model,batch,scores;gc.collect()
  seedouts.append({sid:prep.pack(np.mean([o[sid]['probabilities'] for o in folds],axis=0,dtype=np.float64).tolist()) for sid in ids})
 predictions={sid:prep.pack(np.mean([o[sid]['probabilities'] for o in seedouts],axis=0,dtype=np.float64).tolist()) for sid in ids};save(E/'ranking/AB_GLOBAL/new8_ensemble.json',{'predictions':predictions,'all15_original_models':True})
 plans={r['task_id']:{'path':r['G_frozen_plan'],'sha256':sha(r['G_frozen_plan']),'existing_exact':True} for r in refs if r.get('G_frozen_plan')}
 for r in missing:
  tid=r['task_id']
  if tid not in predictions:continue
  pred=predictions[tid];path=E/'ranking/plans'/tid/'OURS_G153_VBR.json'
  save(path,{'task_id':tid,'method':'OURS_G153_VBR','complete_original_ordinal_order':pred['order'],'probabilities':pred['probabilities'],'chosen_step':pred['chosen_step'],'input_turns_sha256':r['input_turns_sha256'],'mapping_digest':digest(r['mapping']),'checkpoint_manifest_digest':digest(records),'checkpoint_bindings':records,'source':{'path':str(E/'ranking/AB_GLOBAL/new8_ensemble.json'),'sha256':sha(E/'ranking/AB_GLOBAL/new8_ensemble.json'),'all15_models_averaged':True},'new_actual_encoder_and_ranker':True,'new_training_Gold_API_native':0})
  plans[tid]={'path':str(path),'sha256':sha(path),'existing_exact':False}
 for p,h in {**identity,**input_seals}.items():assert sha(p)==h,'NEURAL_INPUT_SOURCE_DRIFT'
 save(E/'ranking/plan_registry224.json',{'at_utc':now(),'plans':plans,'plans_count':len(plans),'unavailable':[r['task_id'] for r in refs if r['task_id'] not in plans],'counts':COUNTS,'elapsed_seconds':time.monotonic()-begin,'new_training_Gold_API_native':0,'models_input_seal_sha256':sha(E/'ranking/new8_model_input_seal224.json')})
 record('G15323_FINISHED',plans_count=len(plans),elapsed_seconds=time.monotonic()-begin);print(canonical({'G153_plans':len(plans),'counts':COUNTS,'seconds':time.monotonic()-begin}),flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:record('ERROR',type=type(e).__name__,error=str(e));raise

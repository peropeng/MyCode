"""Fresh exact raw embeddings and frozen AF ensembles; old exact inputs alone reuse."""
import os,gc
os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
from common166 import *
import numpy as np
import torch

def run():
 start=time.monotonic();refs=read(E/'data/selected_task_bindings.json')['tasks'];samples={s['sample_id']:s for s in lines(E/'data/public_inputs.jsonl')};ids=sorted(samples)
 data={};receipt=[];encoder=None;batches=0;texts_count=0;roles={};cache={}
 helper=module('exp166_original_structure',ROOT/'实验/实验112_RQ1时序交互依赖完整排序/runner.py')
 events=module('exp166_original_state_action',ROOT/'工作区/1006-exp133-state-action/实验/实验133_状态动作选择性核验/method.py')
 qwenroot=ROOT/'工作区/0922-exp124-ranking-baselines/third_party/Qwen3-Embedding-0.6B'
 q3=module('exp166_original_qwen',ROOT/'工作区/0922-exp124-ranking-baselines/third_party/StepFinder/Q3Emb.py')
 
 for ref in refs:
  sid=ref['task_id'];sample=samples[sid];turns=sample['turns'];n=len(turns);tsha=hashlib.sha256(json.dumps(turns,sort_keys=True).encode()).hexdigest();assert tsha==ref['input_turns_sha256']
  if encoder is None:
   torch.set_num_threads(4);encoder=q3.Qwen3Embedding(str(qwenroot),use_cuda=True,max_length=8192)
   modelbound=read(ROOT/'工作区/0922-exp124-ranking-baselines/实验/实验124_责任排序强基线与外部迁移/results/preclaim_binding.json')
   for f,h in modelbound['model_files_sha256'].items():assert sha(qwenroot/f)==h
   save(E/'features/encoder_identity.json',{'revision':q3.DEFAULT_MODEL_REVISION,'files':modelbound['model_files_sha256'],'max_length':8192,'batch_size':1,'device':'cuda','same_original_raw_encoder':True})
  content=[];agent=[];rawtokens=[];samplebatch=0
  texts=[json.dumps({k:str(t.get(k) or '') for k in ('content','action','thought') if t.get(k)},ensure_ascii=False,sort_keys=True) for t in turns]
  for t,text in zip(turns,texts):
   role=t['role'];rawtokens.append(len(encoder.tokenizer(text,add_special_tokens=True)['input_ids']))
   if role not in roles:roles[role]=encoder.encode(role,dim=32).float().cpu().numpy()[0];batches+=1;texts_count+=1
   agent.append(roles[role])
   key=hashlib.sha256(text.encode()).hexdigest()
   if key not in cache:
    cache[key]=encoder.encode([text],dim=128).float().cpu().numpy()[0];batches+=1;texts_count+=1;samplebatch+=1
   content.append(cache[key]);status('FRESH_ENCODER_RUNNING',current_task=sid,new_encoder_batches=batches,new_encoder_texts=texts_count)
  content=np.asarray(content,dtype=np.float32);agent=np.asarray(agent,dtype=np.float32)
  structure=np.asarray([helper._h0_vector({'turns':turns},i) for i in range(n)],dtype=np.float32);neighbors=helper._build_adjacency({'turns':turns});adjacency=[]
  for rel in ('temporal','same_role','same_full_shape_signature','same_nonempty_action_shape'):
   ix=np.zeros((n,2),dtype=np.int64);mask=np.zeros((n,2),dtype=np.float32)
   for i,ns in enumerate(neighbors[rel]):assert len(ns)<=2;ix[i,:len(ns)]=ns;mask[i,:len(ns)]=1
   adjacency.append((torch.from_numpy(ix),torch.from_numpy(mask)))
  coordinates=[{'original_step_id':t['source_message_index'],'source_channel_role':'assistant'} for t in turns]
  packet=events.representation({'turns':turns,'task':sample['task'],'coordinate_map':coordinates});partner=torch.zeros(n,2,dtype=torch.long);valid=torch.zeros(n,2)
  for p in packet['observed_state_action_links']:
   s,a=p['decision_state'],p['ensuing_action'];partner[s,0]=a;valid[s,0]=1;partner[a,1]=s;valid[a,1]=1
  data[sid]={'content':torch.from_numpy(content),'agent':torch.from_numpy(agent),'raw_structure':torch.from_numpy(structure),'adjacency':adjacency,'paired_partner':partner,'paired_valid':valid}
  receipt.append({'sample_id':sid,'steps':n,'exact_old_full_input':False,'input_turns_sha256':tsha,'texts_sha256':digest(texts),'input_tokens_before_truncation':rawtokens,'truncated_steps':[i for i,x in enumerate(rawtokens) if x>8192],'new_unique_content_batches':samplebatch,'observed_state_action_links':packet['observed_state_action_links']})
 if encoder is not None:del encoder;gc.collect();torch.cuda.empty_cache()
 (E/'features').mkdir(exist_ok=True);torch.save({'records':data,'no_labels_or_outcomes':True},E/'features/features.pt')
 save(E/'features/receipt.json',{'at_utc':now(),'status':'PASS','new_encoder_forward_batches':batches,'new_encoder_unique_texts':texts_count,'rows':receipt,'new_task_content_total_texts':sum(len(samples[r['task_id']]['turns']) for r in refs if r.get('binding_kind')=='Exp166_new_RAW_state'),'within_experiment_exact_text_cache':True,'old_task_full_input_cache_only_if_exact':False,'all_new_RAW_inputs_fresh':True,'seconds':time.monotonic()-start})
 cm=module('exp166_immutable153_common',E153/'common.py');sys.modules['common']=cm;sys.path.insert(0,str(E153));models=module('exp166_immutable153_models',E153/'context_models.py');models.seed_all(0)
 records=[r for r in read(E153/'training/all_models_sealed.json')['models'] if r['suite']=='AF' and r['arm'] in ('AB_GLOBAL','SF_REF')];assert len(records)==30
 inputs={str(p):sha(p) for p in (E/'data/public_inputs.jsonl',E/'data/selected_task_bindings.json',E/'features/features.pt',E/'features/receipt.json',E153/'training/all_models_sealed.json',E153/'context_models.py',E153/'common.py')}
 save(E/'ranking_input_seal.json',{'at_utc':now(),'inputs':inputs,'models':records,'same_frozen_models_no_training':True,'model_outputs_before_recovery':True})
 files={};outputs=0;forwards=0
 def pack(prob):
  order=sorted(range(len(prob)),key=lambda i:(-prob[i],i));return {'probabilities':prob,'order':order,'chosen_step':order[0],'valid':True,'native_complete_ranking':True}
 def ensemble(v):return {sid:pack(np.mean([x[sid]['probabilities'] for x in v],axis=0,dtype=np.float64).tolist()) for sid in ids}
 for arm in ('AB_GLOBAL','SF_REF'):
  seeds=[]
  for seed in (20260816,20260817,20260818):
   folds=[]
   for outer in range(5):
    r=next(r for r in records if (r['arm'],r['seed'],r['outer'])==(arm,seed,outer));assert sha(r['checkpoint'])==r['checkpoint_sha256'];ck=torch.load(r['checkpoint'],map_location='cpu',weights_only=False);model=models.create(arm).cuda();model.load_state_dict(ck['state_dict']);model.eval()
    with torch.no_grad():
     batch=models.collate(ids,data,(ck['scaler_mean'],ck['scaler_std']),torch.device('cuda'));scores,_=models.forward(model,arm,batch);forwards+=1;out={sid:pack(torch.softmax(score.cpu(),0).tolist()) for sid,score in zip(batch['ids'],scores)}
    path=E/'ranking'/arm/f'{seed}_{outer}.json';save(path,{'predictions':out,'checkpoint_sha256':r['checkpoint_sha256'],'same_selected_sorted_task_batch':ids});files[str(path)]=sha(path);outputs+=len(ids);folds.append(out)
    del model,batch,scores;gc.collect();torch.cuda.empty_cache()
   out=ensemble(folds);path=E/'ranking'/arm/f'{seed}.json';save(path,{'predictions':out,'all5_folds':True});files[str(path)]=sha(path);outputs+=len(ids);seeds.append(out)
  out=ensemble(seeds);path=E/'ranking'/arm/'ensemble.json';save(path,{'predictions':out,'all3_seeds':True});files[str(path)]=sha(path);outputs+=len(ids)
 for p,h in inputs.items():assert sha(p)==h
 save(E/'ranking/all_predictions_sealed.json',{'at_utc':now(),'outputs':outputs,'forward_batches':forwards,'models':30,'files':files,'elapsed_seconds':time.monotonic()-start,'new_encoder_batches':batches,'new_unique_encoder_texts':texts_count,'new_training_Gold_paid_API':0});status('RANKING_SEALED',new_ranker_forward_batches=forwards,new_ranking_outputs=outputs)
 print(canonical({'Exp166':'RANKING_SEALED','status':'RANKING_SEALED','tasks':len(ids),'outputs':outputs,'forwards':forwards,'encoder_batches':batches,'seconds':time.monotonic()-start}),flush=True)
if __name__=='__main__':run()

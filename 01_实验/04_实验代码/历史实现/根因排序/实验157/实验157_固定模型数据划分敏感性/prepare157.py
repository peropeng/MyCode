"""Freeze all hash-defined memberships and valid canonical153 INITIAL references."""
from collections import Counter,defaultdict
import torch
from common import *
import models157 as models

SOURCE_SALT='Exp157-source-v1|'
AF_SALT='Exp157-AF-v1|'

def sorted_hash(groups,prefix):
 return sorted(groups,key=lambda g:(hashlib.sha256((prefix+g).encode('utf-8')).hexdigest(),g))

def source_splits(public,old_ids):
 by={r['sample_id']:r for r in public}
 if len(public)!=614 or len(by)!=614 or len({r['task_group'] for r in public})!=614:raise RuntimeError('Source614 unique taskgroups required')
 if Counter(r['domain'] for r in public)!=Counter(coding=320,math=294):raise RuntimeError('Source original domain counts changed')
 result={}
 for block in BLOCKS:
  domain_order={d:sorted_hash([r['task_group'] for r in public if r['domain']==d],SOURCE_SALT+block+'|'+d+'|') for d in ('coding','math')}
  val_groups=set(domain_order['coding'][:64]+domain_order['math'][:58])
  ids={'train':[r['sample_id'] for r in public if r['task_group'] not in val_groups],
       'validation':[r['sample_id'] for r in public if r['task_group'] in val_groups]}
  if tuple(map(len,ids.values()))!=(492,122) or set(ids['train'])&set(ids['validation']):raise RuntimeError('Source492/122 split required')
  counts={part:dict(Counter(by[s]['domain'] for s in values)) for part,values in ids.items()}
  if counts!={'train':{'coding':256,'math':236},'validation':{'coding':64,'math':58}}:raise RuntimeError('Source fixed domain proportions required')
  result[block]={'block':block,'domain_hash_order':domain_order,'ids':ids,'domain_counts':counts,
   'fit_ids_sha256':digest(ids['train']),'validation_ids_sha256':digest(ids['validation']),
   'overlap_with_old_ids':{new+'_'+old:len(set(v)&set(old_ids[old])) for new,v in ids.items() for old in ('train','validation')}}
 return result

def af_partitions(public):
 groups=sorted({r['task_group'] for r in public});result={}
 if len(public)!=731 or len(groups)!=716:raise RuntimeError('AF original731/716 required')
 for block in BLOCKS:
  result[block]={}
  for seed in AF_SEEDS:
   order=sorted_hash(groups,AF_SALT+block+'|'+str(seed)+'|')
   folds={str(o):[g for j,g in enumerate(order) if j%5==o] for o in range(5)}
   if [len(folds[str(o)]) for o in range(5)]!=[144,143,143,143,143]:raise RuntimeError('Original AF716 hashfold counts required')
   result[block][str(seed)]={'block':block,'seed':seed,'hash_group_order':order,'fold_groups':folds,
                            'group_fold_assignment':{g:j%5 for j,g in enumerate(order)},'group_fold_assignment_sha256':digest({g:j%5 for j,g in enumerate(order)})}
 return result

def prepare():
 require_time(new_long_task=True)
 if sha(E/'approved_plan.json')!=PLAN_SHA:raise RuntimeError('Approved157 plan changed')
 plan=read(E/'approved_plan.json');old=read(E153/'protocol.json');parents=plan['parents']
 for root,key in ((E153,'packet153_sha256'),(E155,'packet155_sha256'),(E156,'packet156_sha256')):
  if sha(root/'main_decision_packet.json')!=parents[key] or read(root/'final_execution_audit.json')['status']!='PASS':raise RuntimeError('Complete valid immutable parents required')
 guarded={}
 for root in (E153,E155,E156):
  previous=read(root/'protocol.json');guarded.update(previous['protected_old_files_sha256'])
  for field in ('training_sources','rule_sources_sha256','inputs','initializations'):
   guarded.update(previous.get(field,{}))
  for name in ('protocol.json','main_decision_packet.json','comparison.json','compact_summary.json','final_execution_audit.json','resource_audit.json','initialization_audit.json','training/all_models_sealed.json','results/all_predictions_sealed.json'):
   path=root/name
   if path.is_file():guarded[str(path)]=sha(path)
  model_seal=root/'training/all_models_sealed.json'
  if model_seal.exists():
   for rec in read(model_seal)['models']:guarded[rec['checkpoint']]=rec['checkpoint_sha256']
  guarded.update(read(root/'results/all_predictions_sealed.json')['files'])
 for key in ('root_interpretation','inherited155_design'):guarded[parents[key]]=sha(parents[key])
 check_hashes(guarded)
 source_public_path=E134/'data/public_records.json';af_public_path=E138/'data/public_records.json'
 source_public=read(source_public_path)['records'];af_public=read(af_public_path)['records']
 splits=source_splits(source_public,old['source_ids']);partitions=af_partitions(af_public)
 originals=read(E153/'initialization_audit.json')['records'];canonical_initials={(r['suite'],r['arm'],r['seed'],r['outer']):r for r in originals}
 source=[];AF=[];scaler_specs=[]
 for arm in ARMS:
  for block in BLOCKS:
   for seed in SOURCE_SEEDS:
    canonical_row=next(r for r in old['source_schedule'] if r['arm']==arm and r['seed']==seed)
    ids=splits[block]['ids'];initial=canonical_initials['source',arm,seed,None]
    row={**canonical_row,'replication_block':block,'fit_ids':ids['train'],'validation_ids':ids['validation'],'initialization_path':initial['path']}
    source.append(row);scaler_specs.append({'suite':'source','arm':arm,'replication_block':block,'seed':seed,'outer':None,'stage':'source_fit','scaler_fit_ids_sha256':digest(ids['train'])})
   for seed in AF_SEEDS:
    assignment=partitions[block][str(seed)]['group_fold_assignment']
    for outer in range(5):
     template=next(r for r in old['af_schedule'] if r['arm']==arm and r['seed']==seed and r['outer']==outer)
     val=min(o for o in range(5) if o!=outer)
     held=[r['sample_id'] for r in af_public if assignment[r['task_group']]==outer]
     validation=[r['sample_id'] for r in af_public if assignment[r['task_group']]==val]
     fit=[r['sample_id'] for r in af_public if assignment[r['task_group']] not in (outer,val)]
     refit=[r['sample_id'] for r in af_public if assignment[r['task_group']]!=outer]
     initial=canonical_initials['AF',arm,seed,outer]
     row={'arm':arm,'seed':seed,'outer':outer,'validation_fold':val,'replication_block':block,
      'held_groups':[g for g in sorted(assignment) if assignment[g]==outer],
      'validation_groups':[g for g in sorted(assignment) if assignment[g]==val],
      'inner_fit_groups':[g for g in sorted(assignment) if assignment[g] not in (outer,val)],
      'refit_groups':[g for g in sorted(assignment) if assignment[g]!=outer],
      'partition_sha256':partitions[block][str(seed)]['group_fold_assignment_sha256'],
      'initialization_seed':template['initialization_seed'],'initialization_path':initial['path'],
      'selection_fit_ids':fit,'validation_ids':validation,'refit_ids':refit,'held_ids':held,
      'inference_batches_sha256':digest([held[k:k+16] for k in range(0,len(held),16)])}
     AF.append(row)
     for stage,ids in (('selection',fit),('refit',refit)):
      scaler_specs.append({'suite':'AF','arm':arm,'replication_block':block,'seed':seed,'outer':outer,'stage':stage,'scaler_fit_ids_sha256':digest(ids)})
 if (len(source),len(AF),len(scaler_specs))!=(27,135,297):raise RuntimeError('Exact source27/AF135/stage297 schedule required')
 split_file=E/'splits.json';write_new(split_file,{'at_utc':now(),'experiment':'Exp157','status':'FROZEN','source_salt':SOURCE_SALT,'AF_salt':AF_SALT,
  'source_splits':splits,'AF_partitions':partitions,'target_label_length_or_outcomes_used_for_assignment':0,'source_public_records':str(source_public_path),'AF_public_records':str(af_public_path)})
 split_seal={'at_utc':now(),'experiment':'Exp157','status':'PASS','approved_plan_sha256':PLAN_SHA,'splits_sha256':sha(split_file),
  'source_blocks':3,'AF_partitions':9,'all_source614_and_AF716_memberships_frozen_before_any_training':True,
  'source_public_records_sha256':sha(source_public_path),'AF_public_records_sha256':sha(af_public_path)}
 write_new(E/'split_seal.json',split_seal)
 parameters={a:old['parameters'][a] for a in ARMS};initials={};actual_initials={};records=[]
 for row in source+[{'suite':'AF',**r} for r in AF]:
  path=Path(row['initialization_path']);h=old['initializations'][str(path)]
  if sha(path)!=h or 'invalid' in str(path).casefold():raise RuntimeError('Canonical valid initial binding required')
  if str(path) not in actual_initials:
   ck=torch.load(path,map_location='cpu',weights_only=False);info=ck['info'];state=ck['state_dict']
   state_hash=models.state_digest(state);rng_hash=models.rng_digest(ck['training_rng'])
   if state_hash!=info['state_digest'] or info['canonical_seed']!=row['initialization_seed'] or sum(v.numel() for v in state.values())!=parameters[row['arm']]:raise RuntimeError('Original INITIAL state/RNG/parameter binding required')
   if row['arm']=='AB_GLOBAL' and bool(torch.count_nonzero(state['O.weight'])):raise RuntimeError('Original GLOBAL INITIAL O zero required')
   actual_initials[str(path)]={'state_digest':state_hash,'training_rng_digest':rng_hash,'parameter_count':parameters[row['arm']],
     'canonical_seed':info['canonical_seed'],'independent_context_seed':info.get('independent_context_seed'),'base_state_digest':info.get('base_state_digest'),'O_zero':row['arm']=='AB_GLOBAL'}
   del ck,state
  initials[str(path)]=h
  records.append({'suite':row['suite'],'arm':row['arm'],'seed':row['seed'],'outer':row.get('outer'),'replication_block':row['replication_block'],
   'initialization_seed':row['initialization_seed'],'path':str(path),'sha256':h,**actual_initials[str(path)],'valid_153_INITIAL_only':True,'trained_parent_weight_loads':0,'invalid_runtime_asset_loads':0})
 if (len(initials),len(records))!=(54,162):raise RuntimeError('54 canonical initial files/162 training references required')
 write_new(E/'initialization_audit.json',{'at_utc':now(),'status':'PASS','records':records,'unique_canonical153_INITIAL_files':54,
  'final_training_references':162,'canonical_INITIAL_state_and_RNG_digests_verified':True,'new_initializations_created':0,
  'new_model_constructors_or_forwards_for_preparation':0,'trained_parent_weight_loads':0,'invalid_runtime_asset_loads':0,'parameters':parameters,'runtime_backend_policy':EXPECTED_BACKEND})
 prepared={'at_utc':now(),'status':'READY','experiment':'Exp157','approved_plan_sha256':PLAN_SHA,'primary':PRIMARY,'arms':list(ARMS),'blocks':list(BLOCKS),
  'source_ids':{b:splits[b]['ids'] for b in BLOCKS},'historical_source_ids':old['source_ids'],'source_splits':splits,'AF_partitions':partitions,
  'source_schedule':source,'af_schedule':AF,'scaler_fit_specs':scaler_specs,'target_cohorts':old['target_cohorts'],
  'source_seeds':list(SOURCE_SEEDS),'AF_seeds':list(AF_SEEDS),'source_blocks':SOURCE_BLOCKS,'AF_blocks':AF_BLOCKS,'parameters':parameters,
  'source_public_records':str(source_public_path),'AF_public_records':str(af_public_path),
  'source_training_features':old['source_training_features'],'AF_training_features':old['AF_training_features'],
  'source_training_labels':str(E134/'data/selected_train_labels.private.json'),'AF_training_labels':str(E138/'data/development_labels.private.json'),
  'protected_old_files_sha256':guarded,'max_epochs':40,'patience':8,'batch_tasks_or_complete_groups':16,'expected_optimization_stages':297,'expected_final_models':162,
  'source_target_outputs':77580,'AF_target_outputs':26316,'expected_outputs':103896,'expected_prediction_files':315,'runtime_backend_policy':EXPECTED_BACKEND,
  'aggregation':'Each split independently original3seed softmaxmean; no9-model pooling/no bestsplit selection',
  'new_encoder_API_download_Gold_independent_tasks':0,'fee_CNY':'0','no_target_evaluation_label_joins_before_all_new_predictions_sealed':True}
 write_new(E/'prepared_inputs.json',prepared)
 names=['common.py','context_base.py','models157.py','data157.py','prepare157.py','trainer157.py','predict157.py']
 training_sources={str(E/name):sha(E/name) for name in names};training_sources.update({str(q):sha(q) for q in (E/'sources').glob('*.py')})
 inputs={str(E/n):sha(E/n) for n in ('approved_plan.json','prepared_inputs.json','splits.json','split_seal.json','initialization_audit.json')}
 for path in (source_public_path,af_public_path,Path(prepared['source_training_features']),Path(prepared['AF_training_features']),Path(prepared['source_training_labels']),Path(prepared['AF_training_labels'])):inputs[str(path)]=sha(path)
 protocol={**prepared,'schema':'Exp157-fixed-initial-model-data-split-stability/1.0','training_sources':training_sources,'inputs':inputs,
  'initializations':initials,'initialization_records':records,'split_seal_sha256':sha(E/'split_seal.json'),'unique_canonical_initial_files':54,
  'device':'cuda','dtype':'float32','batch':16,'optimizer':'AdamW','lr':.001,'graph_wd':.0001,'SF_wd':.00001,'clip':1.,
  'source_loss':'Original graph CE; SF original CE+.9temporal','AF_loss':'Record CE/SF temporal first averaged within taskgroup then groupmean',
  'selection':'Validation Top1 then MRR then earliest epoch; max40/patience8','model_seal_rule':'all162 models and103896 outputs sealed before target evaluation join','deadline':DEADLINE}
 write_new(E/'protocol.json',protocol)
 checkpoint={'at_utc':now(),'experiment':'Exp157','phase':'PROTOCOL_AND_SPLITS_AND_INITIAL_REFERENCES_SEALED','owner_chat_id':'01a10cf5-0721-7002-83b8-766a60389490',
  'source_chat_id':'01a0b043-b3d8-77f0-be9d-5eee0fed25b0','context_window_id':'01a11331-eb00-78f1-afb1-95fa109cf366','worktree':str(W),'branch':'exp/1007-exp157-split-stability',
  'approved_plan_sha256':PLAN_SHA,'plan_fully_read':True,'deadline_beijing':'2026-10-07T10:00:00+08:00','ETA_initial_total_minutes':[80,110],
  'expected_optimization_stages':297,'expected_final_models':162,'expected_outputs':103896,'current_pid':None,
  'counters':{'completed_optimization_stages':0,'optimizer_updates':0,'final_models':0,'new_ranker_outputs':0,'new_encoder':0,'new_API':0,'new_downloads':0,'new_Gold':0,'new_independent_tasks':0,'fee_CNY':'0'},
  'science_owner':'root','next':'Necessary puremetadata split fixture once; then train297stage→162models→103896outputs seals→two separateHolm6→finalaudit'}
 write_new(E/'checkpoint.json',checkpoint);write_new(E/'execution_state.json',checkpoint)
 print(canonical({'Exp157':'protocol_prepared','source_fits':27,'AF_pairs':135,'optimization_stages':297,'canonical_initials':54,'initial_references':162,'protected_old_files':len(guarded)}),flush=True)

if __name__=='__main__':prepare()

"""Plan one admitted case only; never write to main, launch native or model."""
import argparse,datetime,os
from contracts241 import *
E=HERE.parent/'实验241_Agentless新确认集21_生成测试ScopeV2'

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--task',required=True);args=parser.parse_args();task=args.task
 base=E/'candidate'/task;flow=E/'runs'/task/METHOD;sup=E/'supervision'/task;destination=ROOT/'实验'/E.name
 terminal=read(base/'TERMINAL_PACKET241.json');selection=read(flow/'immutable_selection.json')
 root_receipt=ROOT/'工作区/1009-research-resume'/('ROOT_ACCEPTANCE241_SCOPEV2_'+task.rsplit('-',1)[-1]+'.json')
 root_accept=read(root_receipt)
 if not terminal['all_owned_jobs_STOP'] or not root_accept['strict_ScopeV2_admitted']:raise EngineeringUnknown('ONLY_ROOT_ADMITTED_CLOSED_PLAN')
 if inventory(selection['selection_root'])!=selection['business_paths_sha256']:raise EngineeringUnknown('PLANNED_IMMUTABLE_SELECTION_DRIFT')
 skipped={f'runs/{task}/{METHOD}/'+s for s in ('actor/repo','runtime/tree/repo','external_once_private/runtime/repo')}
 rows=[];identical=[];collisions=[];seen=set()
 def add(source,relative,category):
  source=Path(source);relative=Path(relative);h=sha(source);target=destination/relative
  if not inside(target,destination):raise EngineeringUnknown('PLANNED_MAIN_SCOPE')
  if target.is_file():
   old=sha(target)
   if old==h:identical.append({'source':str(source),'existing_target':str(target),'sha256':h});return
   original=target;target=destination/'admitted_closed_snapshots'/task/relative
   collisions.append({'preserved_existing_target':str(original),'existing_sha256':old,'append_only_target':str(target),'source_sha256':h})
  if target.is_file():
   if sha(target)!=h:raise EngineeringUnknown('APPEND_ONLY_TARGET_CONFLICT '+str(target))
   identical.append({'source':str(source),'existing_target':str(target),'sha256':h});return
  if str(target) in seen:raise EngineeringUnknown('DUPLICATE_PLAN_TARGET')
  seen.add(str(target));rows.append({'source':str(source),'target':str(target),'relative_to_main':target.relative_to(destination).as_posix(),
   'sha256':h,'bytes':source.stat().st_size,'category':category,'overwrite_existing':False})
 for namespace,own_root in [('candidate',base),('raw_result_state_native_readlogs',flow),('supervision_STOP',sup)]:
  for folder,dirs,files in os.walk(own_root):
   folder=Path(folder);relative=folder.relative_to(E)
   dirs[:]=[name for name in dirs if name not in ('.git','__pycache__','.pytest_cache') and (relative/name).as_posix() not in skipped]
   for name in files:add(folder/name,relative/name,namespace)
 add(root_receipt,root_receipt.name,'Root_original_acceptance_receipt')
 stages=[json.loads(line) for line in (flow/'stage_ledger.jsonl').read_text('utf-8').splitlines() if line.strip()]
 cache_paths=set()
 def refs(v):
  if isinstance(v,dict):
   for k,x in v.items():
    if k=='cache_seal' and isinstance(x,str):cache_paths.add(x)
    else:refs(x)
  elif isinstance(v,list):
   for x in v:refs(x)
 for r in stages:
  if r['stage']=='dense_retrieval':refs(r['evidence'])
 shared_vectors={}
 for p in sorted(cache_paths):
  p=Path(p)
  if not inside(p,E/'retrieval/cases_v2'):raise EngineeringUnknown('DENSE_CACHE_PLAN_SCOPE')
  add(p,p.relative_to(E),'this_case_dense_cache_metadata_only')
  for key,h in read(p)['vector_sha256'].items():shared_vectors[str(E/'retrieval/vectors'/(key+'.npy'))]=h
 seal=read(base/'source_seal.json');critical={p:h for p,h in seal['sources'].items() if p.endswith('.py') and inside(p,ROOT) and not any(t in p for t in ('site-packages','dependencies','deps','native_envs','.venv'))}
 critical.update(read(E/'AUTHOR_SOURCE_MANIFEST241.json')['sources'])
 reused_sources=[];existing_snapshot_manifest=destination/'candidate/getmoto__moto-6352/SOURCE_SNAPSHOTS_INCREMENTAL241.json'
 existing=read(existing_snapshot_manifest)['source_snapshots'] if existing_snapshot_manifest.is_file() else {}
 for original,h in critical.items():
  if sha(original)!=h:raise EngineeringUnknown('CRITICAL_PLAN_SOURCE_DRIFT '+original)
  ref=existing.get(original)
  if ref and ref['sha256']==h and (destination/ref['snapshot']).is_file() and sha(destination/ref['snapshot'])==h:
   reused_sources.append({'source':original,'existing_snapshot':str(destination/ref['snapshot']),'sha256':h});continue
  add(original,Path('admitted_source_snapshots')/task/Path(original).resolve().relative_to(ROOT),'new_case_critical_source_snapshot')
 categories={}
 for r in rows:
  group=categories.setdefault(r['category'],{'files':0,'bytes':0});group['files']+=1;group['bytes']+=r['bytes']
 value={'schema':'Agentless241-append-only-admitted-case-copy-plan/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'task':task,'main_destination':str(destination),'copy_rows':rows,'files_to_copy':len(rows),'bytes_to_copy':sum(r['bytes'] for r in rows),
  'categories':categories,'existing_identical_files_not_copied':identical,'existing_main_files_preserved_at_original_paths':collisions,
  'already_archived_critical_sources_reused':reused_sources,'referenced_vectors_readonly':shared_vectors,'vector_copy_files':0,
  'reconstructible_repo_clone_paths_excluded':sorted(skipped),'all_raw_model_responses_scripts_selected_snapshots_fee_readlogs_STOP_in_plan':True,
  'root_receipt_sha256':sha(root_receipt),'root_admitted':True,'main_writes':0,'git_stage_commit_operations':0,
  'native_model_private_executions':0,'only_administrative_plan_file_written':True,
  'commit_scope':[str(destination)],'future_copy_must_recheck_source_and_target_SHA_and_refuse_any_existing_target_with_different_bytes':True,
  'future_commit_only_owned_new_paths_after_Root_authorizes_apply':True}
 name='COPY_PLAN_ONLY241_'+task+'.json';save(HERE/name,value)
 print(canonical({'plan':str(HERE/name),'task':task,'files':len(rows),'bytes':value['bytes_to_copy'],
  'existing_main_files_preserved':len(collisions),'identical_not_copied':len(identical),'source_snapshots_reused':len(reused_sources),
  'vectors_to_copy':0,'main_writes':0,'stage_commit':0}))
if __name__=='__main__':main()

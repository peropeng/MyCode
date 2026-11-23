"""Copy only one Root-admitted closed ScopeV2 case and its exact recovery data."""
import argparse,datetime,os,shutil
from contracts241 import *
E=HERE.parent/'实验241_Agentless新确认集21_生成测试ScopeV2'

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--task',required=True);args=parser.parse_args();task=args.task
 base=E/'candidate'/task;flow=E/'runs'/task/METHOD;supervision=E/'supervision'/task
 packet=read(base/'TERMINAL_PACKET241.json');admission=read(base/'INFORMATION_ADMISSION_SCOPE_V2_241.json')
 root_receipt=ROOT/'工作区/1009-research-resume'/('ROOT_ACCEPTANCE241_SCOPEV2_'+task.rsplit('-',1)[-1]+'.json')
 accepted=read(root_receipt)
 if not packet['all_owned_jobs_STOP'] or admission['status']!='PASS_OBSERVED_PYTHON_SCOPE_EVENTS' or not accepted['strict_ScopeV2_admitted']:
  raise EngineeringUnknown('INCREMENTAL_ONLY_ROOT_ADMITTED_CLOSED_CASE')
 selection=read(flow/'immutable_selection.json');contract=read(base/'public_contract.json');seal=read(base/'source_seal.json')
 for p,h in {**seal['sources'],**seal['inputs']}.items():
  if sha(p)!=h:raise EngineeringUnknown('CLOSED_INCREMENTAL_SEAL_DRIFT '+p)
 clone_rows=[];business=selection['business_paths_sha256'];full=dict(contract['template_inventory']);full.update(business)
 for suffix,expected in [('actor/repo',business),('runtime/tree/repo',full),('external_once_private/runtime/repo',full)]:
  p=flow/suffix
  if p.is_dir():
   if inventory(p)!=expected:raise EngineeringUnknown('INCREMENTAL_RECONSTRUCTIBLE_CLONE_DRIFT '+suffix)
   clone_rows.append({'path':str(p),'relative':p.relative_to(E).as_posix(),'inventory_sha256':digest(expected),
    'template':contract['template'] if suffix!='actor/repo' else None,'selected_overlay':selection['selection_root'],
    'inventory':expected,'deleted':False,'unique_selected_source_retained':True})
 source_snapshots={};author=read(E/'AUTHOR_SOURCE_MANIFEST241.json')['sources']
 critical={p:h for p,h in seal['sources'].items() if p.endswith('.py') and inside(p,ROOT) and not any(part in p for part in ('site-packages','dependencies','deps','native_envs','.venv'))}
 critical.update(author)
 for original,h in critical.items():
  p=Path(original)
  if sha(p)!=h:raise EngineeringUnknown('SOURCE_SNAPSHOT_DRIFT '+original)
  relative=p.resolve().relative_to(ROOT).as_posix();target=base/'source_snapshots'/relative
  target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
  source_snapshots[original]={'snapshot':target.relative_to(E).as_posix(),'sha256':h}
 save(base/'SOURCE_SNAPSHOTS_INCREMENTAL241.json',{'source_snapshots':source_snapshots,'all_critical_snapshot_bytes_verified':True},scope=E)
 save(base/'RECOVERY_INCREMENTAL241.json',{'task':task,'reconstructible_clones':clone_rows,
  'all_unique_raw_selected_snapshots_scripts_scope_and_native_outputs_retained':True,
  'restore':'Overlay these archived case files into original execution_root. Rebuild omitted selected clones from exact pinned public template plus immutable selected business. Shared dependencies/data remain readonly references. Never replay paid POSTs or reopen closed clocks.'},scope=E)
 destination=ROOT/'实验'/E.name;destination.mkdir(parents=True,exist_ok=True)
 skip={r['relative'] for r in clone_rows};hashes={};prior={};total=0;copied=0;unchanged=0
 def copy_one(source,rel):
  nonlocal total,copied,unchanged
  source=Path(source);rel=Path(rel);target=destination/rel
  if not inside(target,destination):raise EngineeringUnknown('INCREMENTAL_MAIN_WRITE_SCOPE')
  h=sha(source);target.parent.mkdir(parents=True,exist_ok=True)
  if target.is_file() and sha(target)==h:unchanged+=1
  else:
   if target.is_file():
    backup=destination/'evidence_history/main_prior_incremental'/task/rel;backup.parent.mkdir(parents=True,exist_ok=True)
    old=sha(target)
    if backup.is_file() and sha(backup)!=old:raise EngineeringUnknown('PRIOR_VERSION_ALREADY_PRESERVED_DIFFERENT')
    shutil.copyfile(target,backup);prior[rel.as_posix()]={'backup':backup.relative_to(destination).as_posix(),'sha256':old}
   shutil.copyfile(source,target);copied+=1
  if sha(target)!=h:raise EngineeringUnknown('INCREMENTAL_MAIN_COPY_SHA '+str(rel))
  hashes[rel.as_posix()]=h;total+=source.stat().st_size
 for own_root in (base,flow,supervision):
  for directory,dirs,files in os.walk(own_root):
   folder=Path(directory);relative=folder.relative_to(E)
   dirs[:]=[name for name in dirs if name not in ('.git','__pycache__','.pytest_cache') and (relative/name).as_posix() not in skip]
   for name in files:copy_one(folder/name,(relative/name).as_posix())
 stages=[json.loads(line) for line in (flow/'stage_ledger.jsonl').read_text('utf-8').splitlines() if line.strip()]
 cache_paths=set()
 def cache_refs(value):
  if isinstance(value,dict):
   for key,v in value.items():
    if key=='cache_seal' and isinstance(v,str):cache_paths.add(v)
    else:cache_refs(v)
  elif isinstance(value,list):
   for v in value:cache_refs(v)
 for r in stages:
  if r['stage']=='dense_retrieval':cache_refs(r['evidence'])
 vector_refs={};new_vector_copies=0
 for cache_path in sorted(cache_paths):
  cache=Path(cache_path)
  if not inside(cache,E/'retrieval/cases_v2'):raise EngineeringUnknown('TASK_DENSE_CACHE_SCOPE')
  copy_one(cache,cache.relative_to(E));value=read(cache)
  for key,h in value['vector_sha256'].items():
   source=E/'retrieval/vectors'/(key+'.npy');target=destination/'retrieval/vectors'/(key+'.npy')
   if sha(source)!=h:raise EngineeringUnknown('TASK_DENSE_VECTOR_SHA')
   if not target.is_file() or sha(target)!=h:copy_one(source,source.relative_to(E));new_vector_copies+=1
   vector_refs[key]=h
 copy_one(root_receipt,root_receipt.name)
 receipt={'schema':'Agentless241-case-incremental-main-integration/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'task':task,'execution_root':str(E),'main_archive':str(destination),'files_verified':len(hashes),'bytes_verified':total,
  'copied_new_or_changed_files':copied,'already_identical_files_not_recopied':unchanged,'file_sha256':hashes,
  'prior_main_versions_preserved':prior,'only_this_case_candidate_runs_supervision_and_referenced_dense_cache':True,
  'referenced_vector_sha256':vector_refs,'new_or_changed_vector_copies_only':new_vector_copies,
  'no_whole_experiment_or_all_vectors_copy':True,'all_owned_jobs_STOP':True,'root_acceptance_original_bytes':True,
  'root_acceptance_sha256':sha(root_receipt),'old_other_closed_case_sources_seals_runtime_not_modified':True,
  'no_ledger_or_other_experiment_writes':True,'no_science_or_mechanical_reruns':True,
  'incremental_overlay_supersedes_only_listed_base_archive_paths':True,'self_hash_excluded':['INCREMENTAL_MAIN_INTEGRATION241_'+task+'.json']}
 receipt_name='INCREMENTAL_MAIN_INTEGRATION241_'+task+'.json';save(base/receipt_name,receipt,scope=E)
 shutil.copyfile(base/receipt_name,destination/receipt_name)
 print(canonical({'task':task,'files':len(hashes),'bytes':total,'copied':copied,'already_identical':unchanged,
  'new_vector_copies':new_vector_copies,'source_snapshots':len(source_snapshots),'closed_only':True}))
if __name__=='__main__':main()

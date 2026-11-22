"""Archive only this owned 241 cohort, retaining raw evidence and exact hashes."""
import datetime,shutil,os
from contracts241 import *
SCOPES=[HERE,HERE.parent/'实验241_Agentless新确认集21_生成测试ScopeV2']

def clone_records(e):
 records=[]
 for task in read(e/'PREPARED241.json')['tasks']:
  cpath=e/'candidate'/task/'public_contract.json';c=read(cpath)
  flow=e/'runs'/task/METHOD;selected_path=flow/'immutable_selection.json'
  if selected_path.is_file():
   selected=read(selected_path);business=selected['business_paths_sha256'];expected=dict(c['template_inventory']);expected.update(business)
   for suffix,inv in [('actor/repo',business),('runtime/tree/repo',expected),('external_once_private/runtime/repo',expected)]:
    p=flow/suffix
    if not p.is_dir():continue
    if inventory(p)!=inv:raise EngineeringUnknown('CLOSED_CLONE_NOT_SELECTED_OR_TEMPLATE '+str(p))
    records.append({'path':str(p),'relative':p.relative_to(e).as_posix(),'inventory_sha256':digest(inv),
     'rebuild_template':c['template'] if suffix!='actor/repo' else None,'public_contract':str(cpath),
     'selected_overlay':selected['selection_root'],'actor_only':suffix=='actor/repo','excluded_from_archive_reconstructible':True,
     'raw_and_immutable_selected_source_retained':True,'deleted':False})
  for namespace in ('mechanical_native','mechanical_single_fix'):
   root=e/namespace/task/'owned_flow'
   for suffix,inv in [('actor/repo',c['c0_business_paths_sha256']),('runtime/tree/repo',c['template_inventory'])]:
    p=root/suffix
    if p.is_dir():
     if inventory(p)!=inv:raise EngineeringUnknown('MECHANICAL_C0_CLONE_DRIFT '+str(p))
     records.append({'path':str(p),'relative':p.relative_to(e).as_posix(),'inventory_sha256':digest(inv),
      'rebuild_template':c['template'],'public_contract':str(cpath),'actor_only':suffix=='actor/repo',
      'excluded_from_archive_reconstructible':True,'deleted':False})
 return records

def integrate(e):
 destination=(ROOT/'实验'/e.name).resolve()
 if not inside(destination,ROOT/'实验'):raise EngineeringUnknown('MAIN_ARCHIVE_SCOPE')
 destination.mkdir(parents=True,exist_ok=True)
 clones=clone_records(e);skip_relative={r['relative'] for r in clones}
 used={}
 for p in (e/'retrieval/cases_v2').glob('*.json'):
  cache=read(p)
  for key,h in cache['vector_sha256'].items():
   if key in used and used[key]!=h:raise EngineeringUnknown('DENSE_VECTOR_BINDING_CONFLICT')
   used[key]=h
 for key,h in used.items():
  if sha(e/'retrieval/vectors'/(key+'.npy'))!=h:raise EngineeringUnknown('USED_DENSE_VECTOR_DRIFT')
 save(e/'MAIN_RECOVERY_CONFIRM241.json',{'schema':'Agentless241-confirmation-main-recovery/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'execution_root':str(e),'main_archive':str(destination),'reconstructible_clones_not_archived':clones,
  'used_dense_vectors':len(used),'used_dense_vector_sha256':used,'all_raw_responses_scripts_tests_scope_events_and_selected_source_retained':True,
  'restore':'Copy archive back to original execution root; restore omitted clones from exact public contract template inventory and immutable selected business. Never reopen closed clocks or replay paid POSTs. Shared original libraries/data/author/finance referenced by seals remain readonly.',
  'scope1_old2_functional_pass_but_information_hold':e==HERE,'old_scope1_information_unknown_not_backfilled':True},scope=e)
 hashes={};size=0;skipped=0;prior={}
 for directory,dirs,files in os.walk(e):
  folder=Path(directory);base=folder.relative_to(e)
  keep=[]
  for name in dirs:
   child=(base/name).as_posix()
   if name in ('.git','__pycache__','.pytest_cache') or child in skip_relative:skipped+=1
   else:keep.append(name)
  dirs[:]=keep
  for name in files:
   source=folder/name;rel=source.relative_to(e)
   if rel.parent.as_posix()=='retrieval/vectors' and source.stem not in used:skipped+=1;continue
   if name=='MAIN_INTEGRATION_CONFIRM241.json':continue
   target=destination/rel;target.parent.mkdir(parents=True,exist_ok=True);h=sha(source)
   if target.is_file() and sha(target)!=h:
    backup=destination/'evidence_history/main_prior_at_integration'/rel;backup.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(target,backup);prior[rel.as_posix()]=sha(backup)
   shutil.copyfile(source,target)
   if sha(target)!=h:raise EngineeringUnknown('MAIN_ARCHIVE_COPY_SHA '+str(rel))
   hashes[rel.as_posix()]=h;size+=source.stat().st_size
 receipt={'schema':'Agentless241-confirmation-main-integration/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'execution_root':str(e),'main_archive':str(destination),'files_verified':len(hashes),'bytes':size,'file_sha256':hashes,
  'skipped_only_reconstructible_clones_caches_or_unused_vectors':skipped,'used_dense_vector_count':len(used),
  'prior_main_unique_bytes_retained':prior,'all_closed_science_jobs_STOP':True,'old_scope1_information_hold_preserved':True,
  'no_ledger_or_other_experiment_writes':True,'no_science_reruns':True,'self_hash_excluded':['MAIN_INTEGRATION_CONFIRM241.json']}
 save(e/'MAIN_INTEGRATION_CONFIRM241.json',receipt,scope=e)
 shutil.copyfile(e/'MAIN_INTEGRATION_CONFIRM241.json',destination/'MAIN_INTEGRATION_CONFIRM241.json')
 print(canonical({'archive':str(destination),'files':len(hashes),'bytes':size,'used_vectors':len(used),'closed_only':True}))

def main():
 for e in SCOPES:integrate(e)
if __name__=='__main__':main()

"""Pure owner/root binding repair before release; keep old sealed source intact."""
import copy, datetime, hashlib, json, shutil
from pathlib import Path
from prepare250_SOURCE import HERE,read,sha,canonical,save

def main():
 dep=HERE/'deployments/getmoto__moto-5072/trial1';grant=read(dep/'root_grant239.json')
 if any(grant[k] is not False for k in grant if k.endswith('_authorized') or k.endswith('_admitted')):raise RuntimeError('EXP250_DO_NOT_REWRITE_GRANTED_DEPLOYMENT')
 if (dep/'leases').exists() or (dep/'checkpoints').exists():raise RuntimeError('EXP250_NO_ACTUAL_STATE_MAY_BE_RESEALED')
 history=HERE/'source_history/5072_trial1_before_native_owner_fix'
 if history.exists():raise RuntimeError('EXP250_OLD_SEAL_HISTORY_ALREADY_EXISTS')
 history.mkdir(parents=True)
 for path in dep.iterdir():
  if path.is_file():shutil.copyfile(path,history/path.name)
  elif path.name=='repro_guard225':shutil.copytree(path,history/path.name)
 old=read(dep/'protocol225.json');p=copy.deepcopy(old)
 p.update(masked_native_owner_root=str(dep),flat_owner=str(dep),
  selected_task_bindings_path=str(dep/'selected_task_bindings240.json'),
  selected_task_bindings_sha256=sha(dep/'selected_task_bindings240.json'),
  common_current_C0_injection_owner='EnAgent wire250 calls exact shared_input249.inject; unchanged continuous finance v3')
 historical={}
 for name in ('EA19_generated_scope_equivalence_SOURCE','independent_final_original_guard_contract_SOURCE','fresh_Root_public_evaluation_gate'):
  if name in p:historical[name]=p.pop(name)
 save(dep/'HISTORICAL_UNUSED_OLD_OWNER_SOURCE250.json',{'historical_only_not_current_runtime_admission':True,'fields':historical})
 save(dep/'protocol225.json',p)
 owner=Path(p['masked_native_owner_root']).resolve();flat=Path(p['flat_owner']).resolve()
 if owner!=dep.resolve() or flat!=dep.resolve():raise RuntimeError('EXP250_ACTUAL_NATIVE_OWNER_NOT_CURRENT_DEPLOYMENT')
 planned_actor=dep/'r/01/w/coder_0';planned_native=dep/'leases/lease_001/n/getmoto__moto-5072/ENAGENT_ICSE2026_FULL_N3_C200_S30_CONFIRMATION/tree/repo'
 if not planned_actor.resolve().is_relative_to(owner) or not planned_native.resolve().is_relative_to(owner):raise RuntimeError('EXP250_NEW_ACTOR_NATIVE_OUTSIDE_OWNER')
 if planned_native.resolve().is_relative_to(Path(old['masked_native_owner_root']).resolve()):raise RuntimeError('EXP250_OLD_OWNER_FALSE_POSITIVE')
 scopepath=Path(p['public_test_scope_contract']['path']);scope=read(scopepath)
 if sha(scopepath)!=p['public_test_scope_contract']['sha256'] or scope['task_order']!=p['task_order']:raise RuntimeError('EXP250_NEW_SCOPE_BINDING_DRIFT')
 if Path(p['finance_template']).resolve().name!='CONFIRMATION_ACCEPTED_C0_V1_FINANCE_CONFIG.json':raise RuntimeError('EXP250_FINANCE_DESCRIPTION_DRIFT')
 guard=Path(p['masked_native_guard_directory']).resolve()
 for name,h in p['masked_native_guard_source_SHA256'].items():
  if sha(guard/name)!=h:raise RuntimeError('EXP250_TRUSTED_SHARED_GUARD_DRIFT')
 for name in ('root_protocol','parent_source_seal','shared_public249','shared_input249','public_source_bindings249'):
  value=str(p[name]).replace('\\','/')
  if '/1012-exp249-prospective-confirmation/' not in value:raise RuntimeError('EXP250_NEW_COMMON_BINDING_NOT249 '+name)
 body=read(dep/'FIRST_FULL_BODY_SOURCE_NOT_POSTED.json')
 bodySHA=hashlib.sha256(canonical(body).encode()).hexdigest()
 if bodySHA!='1eacfdff0fbc258998a63ac1a5e4167bcd8fbf7290e9e39a8e415d9948922296':raise RuntimeError('EXP250_OWNER_REPAIR_MUST_NOT_CHANGE_FIRST_BODY')
 seal=read(dep/'source_seal239.json')
 for path in list(seal['sources']):seal['sources'][path]=sha(path)
 seal['sources'][str(dep/'HISTORICAL_UNUSED_OLD_OWNER_SOURCE250.json')]=sha(dep/'HISTORICAL_UNUSED_OLD_OWNER_SOURCE250.json')
 save(dep/'source_seal239.json',seal)
 grant.update(protocol_sha256=sha(dep/'protocol225.json'),source_seal_sha256=sha(dep/'source_seal239.json'))
 save(dep/'root_grant239.json',grant)
 commands=read(dep/'FIRST_PILOT_SOURCE_COMMANDS.json');commands.update(protocol_SHA256=sha(dep/'protocol225.json'),source_seal_SHA256=sha(dep/'source_seal239.json'))
 save(dep/'FIRST_PILOT_SOURCE_COMMANDS.json',commands)
 report={'SOURCE_ONLY':True,'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model_POST':0,'native':0,'private':0,'ledger':0,
  'old_source_history':str(history),'old_protocol_SHA256':sha(history/'protocol225.json'),'old_seal_SHA256':sha(history/'source_seal239.json'),
  'current_native_owner':str(owner),'current_flat_owner':str(flat),'planned_actual_actor_root_under_owner':True,'planned_actual_native_root_under_owner':True,
  'old_owner_would_refuse_new_native':True,'current_scope_249_V2_SHA256':sha(scopepath),'actual_shared_guard_SHA_verified':True,
  'actual_root_parent_shared_reader_and_finance_bindings_new':True,'first_body_SHA256_unchanged':bodySHA,
  'new_protocol_SHA256':sha(dep/'protocol225.json'),'new_seal_SHA256':sha(dep/'source_seal239.json'),'false_grant_SHA256':sha(dep/'root_grant239.json')}
 save(HERE/'OWNER_BINDING_PURE_CONTROL250.json',report);print(canonical(report))

if __name__=='__main__':main()

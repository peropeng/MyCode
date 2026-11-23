"""Explicit source derivative only; no method or native invocation."""
from runtime251 import *

source=SHARED/'dispatch_one249.py'
text=source.read_text('utf-8-sig').replace('from trial_runtime249 import *','from runtime251 import *').replace('EXP249','EXP251').replace('Exp249/','Exp251/')
text=text.replace("    config_ref = ready['finance_configuration']", "    if ready.get('source_preview_only') is not False: raise RuntimeError('EXP251_SOURCE_PREVIEW_NEVER_POSTED')\n    config_ref = ready['finance_configuration']")
(HERE/'dispatch_once251_ROOT_ONLY.py').write_text(text,'utf-8')
source_native=SHARED/'ours_candidate_native249.py'
text=source_native.read_text('utf-8-sig').replace('from trial_runtime249 import *','from runtime251 import *').replace('EXP249','EXP251').replace('RootExp249_Candidate_','RootExp251_Candidate_').replace('runs/OURS248_FULL','runs/AGENTLESS_FULL')
text=text.replace("        self.check(full=True)","        self.check(full=True)")
text=text.replace("g.get('maximum_new_original_G_O_native') != 1", "g.get('maximum_new_product_native') != 1")
text=text.replace("    result.update(parent_supervision_path", "    result.update(native_kind=ready['native_kind'], parent_supervision_path")
text=text.replace("    nodes = list(dict.fromkeys(ready['goal_nodes'] + ready['ordinary_nodes']))", "    if ready['native_kind'] == 'generated':\n        return generated_worker(grant, h, jobs, run, active, repo, python, c, expected, hashes, supports, events, masked)\n    if ready['native_kind'] != 'G_O': raise RuntimeError('EXP251_UNDECLARED_NATIVE_KIND')\n    nodes = list(dict.fromkeys(ready['goal_nodes'] + ready['ordinary_nodes']))")
text=text.replace("    return module('_exp249_actual_Root_native_boundary', ROOT_NATIVE)", "    h = module('_exp251_actual_Root_native_boundary', ROOT_NATIVE)\n    h.save = save\n    h.owned = lambda p: Path(p).resolve() if Path(p).resolve().is_relative_to(HERE) else (_ for _ in ()).throw(RuntimeError('EXP251_NATIVE_HELPER_SCOPE'))\n    return h")
# Original identity source stays in E249; only output ownership changes.
text=text.replace("    if args.worker: worker(grant, h, jobs)", "    if args.worker: worker(grant, h, jobs)")
insertion="""
def generated_worker(grant, h, jobs, run, active, repo, python, c, expected, hashes, supports, events, masked):
    ready=grant.ready;out=Path(ready['native_output']);actual_out=out/'actual_generated';actual_out.mkdir(parents=True)
    frozen=Path(c['frozen_public_test_root'])
    def frozen_inventory():
        return {p.relative_to(frozen).as_posix():sha(p) for p in frozen.rglob('*') if p.is_file() and not set(p.relative_to(frozen).parts)&{'.git','__pycache__','.pytest_cache'}}
    before_frozen=frozen_inventory()
    if before_frozen!=c['frozen_inventory']:raise RuntimeError('EXP251_GENERATED_FROZEN_INITIAL_DRIFT')
    code=ready['generated_code']
    if hashlib.sha256(code.encode()).hexdigest()!=ready['generated_code_SHA256'] or grant.value.get('generated_code_SHA256')!=ready['generated_code_SHA256']:
        raise RuntimeError('EXP251_GENERATED_EXACT_CODE_BINDING')
    ast.parse(code)
    script=actual_out/'generated_test.py';script.write_bytes(code.encode())
    envelope=actual_out/'entry_envelope.json';identity=actual_out/'actual_python_identity.json'
    dependencies=grant.value.get('product_dependency_paths',[])
    save(envelope,{'mode':'generated','argv_tail':[str(script)],'expected_physical_python':expected['actual_OS_image'],
        'identity_path':str(identity),'harness_guard':str(Path(c['harness'])/'sitecustomize.py'),'harness':c['harness'],
        'source_root':str(repo),'frozen_root':c['frozen_public_test_root'],'output':str(actual_out),'package':c['package'],
        'dependency_paths':dependencies,'dependency_files_sha256':grant.value.get('dependency_files_sha256',{})})
    environment=run.qualify.isolated_env(active,repo,Path(c['frozen_public_test_root']),actual_out,python,c['package'])
    environment['PYTHONPATH']='';environment['PYTHONNOUSERSITE']='1';environment['PYTHONDONTWRITEBYTECODE']='1'
    entry=HERE/'native_core/product_entry241.py'
    payload=("import os,sys,site,runpy;sys.path.extend(site.getsitepackages());sys.path.insert(0,"+repr(str(python.parent.parent/'Lib/site-packages'))+");sys.path.insert(0,"+repr(str(entry.parent))+ ");"
        "os.environ['PATCHPILOT_JOB']=os.environ['COMMON_NATIVE_OWNED_JOB'];sys.argv="+repr([str(entry),str(envelope)])+
        ";runpy.run_path("+repr(str(entry))+",run_name='__main__')")
    argv=[str(python),'-S','-B','-c',payload]
    scheduler=module('_exp251_generated_four_slots',ROOT/'工作区/1010-unified-six/native_four_slots_v5_SOURCE.py')
    scheduling=read(ROOT/'工作区/1010-unified-six/ROOT_COMMON_NATIVE_SCHEDULING_V5_FOUR_SOURCE.json')
    with scheduler.native_lane(scheduling['lock_path'],c['package'],grant.check,lambda v:events.append({'stage':'V5_four_slots','value':v})):
        grant.check(full=True);value=run.qualify.execute(argv,actual_out,actual_out/'execution.log',300,environment)
    masked.verify_actor(repo,hashes,supports)
    if {p:sha(repo/p) for p in hashes}!=hashes:raise RuntimeError('EXP251_GENERATED_BUSINESS_DRIFT')
    if not identity.is_file():raise RuntimeError('EXP251_GENERATED_LEGACY_IDENTITY_MISSING')
    value['actual_product_python_identity']=read(identity);value['Job']=value['stop_receipt']['specific_job_name'];value['executed']=True
    # Compatibility names are derived solely from the original executor's actual
    # held-birth, membership and final zero-active Job accounting observations.
    stop=value['stop_receipt'];stop.update(root_stopped=stop.get('root_process_stopped'),own_Job_empty_before_close=stop.get('job_active_processes_after_termination')==0,
        descendants_stopped=stop.get('all_owned_descendants_terminated'),assigned_root_verified_member=value.get('root_PID_birth_verified') is True and value.get('specific_Job_membership_observed') is True)
    guard=(actual_out/'guard_ready.json').is_file();scope_path=actual_out/'generated_scope_events.jsonl'
    if not scope_path.is_file():raise RuntimeError('EXP251_GENERATED_SCOPE_AUDIT_MISSING')
    rows=[json.loads(s) for s in scope_path.read_text('utf-8-sig').splitlines() if s.strip()]
    classify=module('_exp251_generated_classifier',HERE/'native_core/guarded_reproduction_invalid_SOURCE.py')
    stable=frozen_inventory()==before_frozen
    if not stable:raise RuntimeError('EXP251_GENERATED_FROZEN_FINAL_DRIFT')
    evidence=classify.classify(value,rows,guard,True,stable,expected['actual_OS_image'],str(actual_out))
    imports=read(actual_out/'actual_product_imports.json') if (actual_out/'actual_product_imports.json').is_file() else []
    markers=[s.strip() for s in value['stdout'].splitlines() if s.strip() in ('Issue reproduced','Issue resolved','Other issues')]
    marker=markers[0] if len(markers)==1 and value['exit_code']==0 and imports and not evidence['known_guard_refusal_invalid'] else None
    value.update(**evidence,guard_loaded=guard,business_state_unchanged=True,frozen_tests_unchanged=True,actual_product_imports=imports,
        generated_script_sha256=sha(script),snapshot_sha256=ready['candidate_snapshot']['inventory_sha256'],semantic_marker=marker,scope_event_log_sha256=sha(scope_path))
    result={'status':marker or 'MODEL_REPRODUCTION_INVALID','reproduced':marker=='Issue reproduced','resolved':marker=='Issue resolved',
        'not_reproduced':marker=='Other issues','stdout':value['stdout'],'stderr':value.get('stderr',''),'exit_code':value['exit_code'],'native_record':value}
    save(actual_out/'run.json',result);save(out/'NATIVE_TRANSPORT_EVIDENCE.json',events)
    save(out/'WORKER_COMPLETED_PUBLIC.json',{'task_id':ready['task_id'],'trial_id':ready['trial_id'],'attempt':ready['attempt'],
        'candidate_snapshot':ready['candidate_snapshot'],'candidate_source_sha256':hashes,'generated_code_SHA256':ready['generated_code_SHA256'],
        'public_native_path':str(actual_out/'run.json'),'public_native_SHA256':sha(actual_out/'run.json'),'one_actual_generated_native':True,
        'Root_grant_SHA256':grant.sha256,'model_private_finance':0})

"""
text=text.replace('import argparse\n','import argparse\nimport ast\n')
text=text.replace('\ndef main():', '\n'+insertion+'\ndef main():')
(HERE/'native_once251_ROOT_ONLY.py').write_text(text,'utf-8')
source_final=SHARED/'final249_ROOT_ONLY.py'
final=source_final.read_text('utf-8-sig').replace('from trial_runtime249 import *','from runtime251 import *').replace('from ours_candidate_native249 import helper','from native_once251_ROOT_ONLY import helper').replace('runs/OURS248_FULL','runs/AGENTLESS_FULL').replace('RootExp249_Final_','RootExp251_Final_').replace('EXP249','EXP251')
(HERE/'final_once251_ROOT_ONLY.py').write_text(final,'utf-8')
save(HERE/'BOUNDARY_SOURCE_DERIVATIVE251.json',{'dispatch_original':ref(source),'dispatch_new':ref(HERE/'dispatch_once251_ROOT_ONLY.py'),
 'native_original':ref(source_native),'native_new':ref(HERE/'native_once251_ROOT_ONLY.py'),'original_G_O_and_held_Job_core_retained':True,
 'final_original':ref(source_final),'final_new':ref(HERE/'final_once251_ROOT_ONLY.py'),
 'generated_entry_scope_classifier_exact_byte_copy':True,'method_generation_or_native_during_derivation':0})
print(canonical({'status':'BOUNDARY_SOURCE_READY_ONLY','dispatch':sha(HERE/'dispatch_once251_ROOT_ONLY.py'),'native':sha(HERE/'native_once251_ROOT_ONLY.py')}))

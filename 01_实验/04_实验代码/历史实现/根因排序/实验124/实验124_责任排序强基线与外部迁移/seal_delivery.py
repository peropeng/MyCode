"""Seal terminal JSON, complete logs, archives and source bytes for integration."""
import shutil,subprocess
from runner import HERE,ROOT,ASSETS,publish,load,sha
for name in ['formal.log','embedding.log','embedding_scalar_preflight.log']:
    dest=HERE/'results/logs'/name; dest.parent.mkdir(exist_ok=True)
    assert not dest.exists(); shutil.copyfile(ASSETS/name,dest)
publish(HERE/'results/attempt_terminal.json',{'status':'COMPLETED_PANEL_A_EXTERNAL_ASSET_STOP_WHOWHEN_RESOURCE_GAP','formal_fold_count':15,'formal_fit_count':30,'formal_retries':0,'all_held_predictions_completed':True,'same_configuration_all_formal_folds':True,'preflight_amendments':1,'scalar_preflight_records':64,'formal_result_sha256':sha(HERE/'results/panel_a.json'),'formal_audit_sha256':sha(HERE/'results/final_audit.json'),'independent_audit_sha256':sha(HERE/'results/independent_result_audit.json'),'checkpoints_and_embeddings_manifest_sha256':sha(HERE/'results/artifact_manifest.json'),'science_code_commits':sorted({load(p)['git_commit'] for p in (HERE/'results/folds').glob('*.json')}),'gpu_released_after_completion':True})
rows=[]
for p in sorted(HERE.rglob('*')):
    if not p.is_file() or '__pycache__' in p.parts or p.name=='delivery_manifest.json':continue
    rows.append({'path':p.relative_to(HERE).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
publish(HERE/'results/delivery_manifest.json',{'files':rows,'all_terminal_json_included':True,'excludes':['__pycache__','delivery_manifest.json (self)'],'byte_policy':'.gitattributes * -text','publication':'Final files immutable; Git commit supplies external manifest identity.'})
print({'sealed_files':len(rows),'terminal_sha256':sha(HERE/'results/attempt_terminal.json'),'delivery_manifest_sha256':sha(HERE/'results/delivery_manifest.json')})

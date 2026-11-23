"""Freeze a terminal public-only choice for a separate Root final evaluator.

This program has no transport/native entry point and never reads private
selectors or private results. It accepts only existing public witnesses.
"""
import argparse, copy, hashlib, importlib.util, json, os, sys
from pathlib import Path

E=Path(__file__).resolve().parent
R=Path('D:/Code/毕设/graduate-thesis-experiments')
OLD=R/'工作区/1011-our19'
sys.dont_write_bytecode=True
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')

def read(path):return json.loads(Path(path).read_text('utf-8-sig'))
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(value):return hashlib.sha256(canonical(value).encode()).hexdigest()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):
    path=Path(path).resolve()
    if not path.is_relative_to(E):raise RuntimeError('EXP248_FINAL_PREPARE_WRITE_OUTSIDE_SCOPE')
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.'+str(os.getpid())+'.tmp')
    with tmp.open('w',encoding='utf-8') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    os.replace(tmp,path)

def select_public_witness(index,terminal,source_sha):
    matches=[candidate for candidate in terminal.get('candidates',[]) if candidate.get('business_source_sha256')==source_sha]
    if matches:
        candidate=min(matches,key=lambda row:row['attempt'])
        native=copy.deepcopy(candidate['public_validation']['native_record']);path=Path(native['path']).resolve()
        directory=path.parent.parent;completed_path=directory/'COMPLETED_PUBLIC.json';supervision_path=directory/'SUPERVISION.json'
        if not path.is_relative_to(E/'forward'/str(index)) or not completed_path.exists() or not supervision_path.exists():
            raise RuntimeError('EXP248_SELECTED_PUBLIC_NATIVE_NOT_OWN_COMPLETED_BOUNDARY')
        completed=read(completed_path);supervision=read(supervision_path)
        if completed['candidate_source_sha256']!=source_sha or completed['public_native_SHA256']!=sha(path):
            raise RuntimeError('EXP248_SELECTED_PUBLIC_CANDIDATE_SOURCE_OR_WITNESS_DRIFT')
        if (supervision['exit_code']!=0 or supervision['error'] is not None
            or supervision['stop_receipt']['all_owned_descendants_terminated'] is not True):
            raise RuntimeError('EXP248_SELECTED_PUBLIC_PARENT_STOP_NOT_COMPLETE')
        return read(path),path,{'origin':'This version selected candidate complete public native',
            'candidate_observation_attempt':candidate['attempt'],'public_completed_path':str(completed_path),
            'public_completed_SHA256':sha(completed_path),'public_supervision_path':str(supervision_path),
            'public_supervision_SHA256':sha(supervision_path),'public_parent_STOP_known':True}
    # A normal terminal can legitimately choose C0 over equally failing larger
    # edits. Its unchanged public observation is reused, never read from private.
    rows=[json.loads(line) for line in (OLD/'r'/str(index)/'f/stage_ledger.jsonl').read_text('utf-8-sig').splitlines() if line.strip()]
    witness=next(row['evidence'] for row in rows if row['stage']=='progress_initial_actual_public_observation_reused')
    initial_input=read(OLD/'r'/str(index)/'f/input.json')
    initial_source=initial_input.get('C0_business_sha256')
    # The input schema can carry this identity in a different public binding;
    # use the existing common C0 supplement for the exact source inventory.
    finance=read(R/'工作区/1011-unbudgeted-common/FINANCE_CONFIG_CONTINUE.json')
    registry=read(finance['common_C0_supplement_registry']);task=terminal['task_id'] if 'task_id' in terminal else registry['task_order'][index]
    entry=registry['tasks'][task]
    if sha(entry['path'])!=entry['sha256']:raise RuntimeError('EXP248_ORIGINAL_PUBLIC_C0_SUPPLEMENT_DRIFT')
    supplement=read(entry['path'])
    if supplement['actual_C0_source_SHA256']!=source_sha or supplement['current_C0_native_record_SHA256']!=witness['sha256']:
        raise RuntimeError('EXP248_TERMINAL_SOURCE_HAS_NO_MATCHING_PUBLIC_OBSERVATION')
    path=Path(witness['path']).resolve()
    if sha(path)!=witness['sha256']:raise RuntimeError('EXP248_ORIGINAL_PUBLIC_C0_NATIVE_DRIFT')
    return read(path),path,{'origin':'Exact unchanged initial public C0 observation reused',
        'candidate_observation_attempt':0,'public_parent_STOP_known_from_original_complete_C0_certificate':True,
        'new_model_or_native_to_reconstruct_public_witness':0}

def prepare(index):
    tasks=read(R/'工作区/1011-unbudgeted-common/COMMON_CONTRACT_SOURCE.json')['task_order'];task=tasks[index]
    forward=E/'forward'/str(index);terminal_path=forward/'PUBLIC_ONLY_NATURAL_TERMINAL.json';source_path=forward/'SELECTED_BUSINESS_SOURCE.json'
    if not terminal_path.exists() or not source_path.exists():
        return {'status':'WAITING_FOR_PUBLIC_NATURAL_TERMINAL','task_id':task,'private_read_or_native':0}
    terminal=read(terminal_path)
    if terminal.get('error') is not None or terminal.get('status')!='COMPLETED':
        raise RuntimeError('EXP248_FINAL_SELECTION_ENGINEERING_UNKNOWN_NOT_FROZEN')
    source=read(source_path);source_sha={rel:hashlib.sha256(text.encode()).hexdigest() for rel,text in sorted(source.items())}
    protocol=read(OLD/'protocol240.json');oracle_ref=protocol['public_goal_ordinary_oracle_contract'];mask_ref=protocol['public_test_scope_contract']
    for ref in (oracle_ref,mask_ref):
        if sha(ref['path'])!=ref['sha256']:raise RuntimeError('EXP248_ORIGINAL_PUBLIC_CONTRACT_DRIFT')
    oracle=next(row for row in read(oracle_ref['path'])['tasks'] if row['task_id']==task)
    native,path,provenance=select_public_witness(index,terminal,source_sha)
    if set(native['requested_nodes'])!=set(oracle['target_nodes']+oracle['ordinary_nodes']):
        raise RuntimeError('EXP248_SELECTED_PUBLIC_G_O_SCOPE_NOT_EXACT_ORIGINAL')
    spec=importlib.util.spec_from_file_location('_final248_public_progress_guard',OLD/'progress_guard240.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    observed=guard.observe({'native_record':native,'outcomes':{node:native['pytest']['outcomes'][node] for node in oracle['ordinary_nodes']}},oracle['target_nodes'],oracle['ordinary_nodes'])
    if not observed['ordinary_pass']:raise RuntimeError('EXP248_FINAL_SELECTED_STATE_LOST_ORDINARY_PASS')
    refs=read(OLD/'selected_task_bindings240.json')['tasks'];ref=next(row for row in refs if row['task_id']==task)
    scope=next(row for row in read(mask_ref['path'])['tasks'] if row['task_id']==task)
    supports={**scope['business_and_support_files_in_view'],**scope['public_test_py_files_SHA256']}
    supports={rel:h for rel,h in supports.items() if rel not in source_sha}
    snapshot=terminal['final_snapshot']
    if digest({**source_sha,**supports})!=snapshot['inventory_sha256']:
        raise RuntimeError('EXP248_SELECTED_SNAPSHOT_FULL_INVENTORY_DRIFT')
    destination=E/'final_ready'/str(index);certificate_path=destination/'FROZEN_PUBLIC_SELECTION_CERTIFICATE.json';frozen_source=destination/'FROZEN_BUSINESS_SOURCE.json';ready_path=destination/'READY.json'
    if ready_path.exists():
        ready=read(ready_path)
        if ready['public_terminal_SHA256']!=sha(terminal_path) or ready['candidate_source_sha256']!=source_sha:
            raise RuntimeError('EXP248_ALREADY_FROZEN_SELECTION_CANNOT_CHANGE')
        return {'status':'ALREADY_FROZEN_NO_PRIVATE_READ','task_id':task,'ready_path':str(ready_path),'ready_SHA256':sha(ready_path)}
    certificate={'schema':'frozen-selected-source-public-certificate/1','task_id':task,
        'candidate_source_sha256':source_sha,'candidate_source_inventory_SHA256':digest(source_sha),
        'candidate_snapshot':snapshot,'public_native_record_path':str(path),'public_native_record_SHA256':sha(path),
        'ordinary_all_PASS':observed['ordinary_pass'],'Goal_actual_PASS':sorted(observed['goal_pass']),
        'failed_Goals':observed['failed_goals'],'public_G_O_actual_all_PASS':observed['ordinary_pass'] and observed['failed_goals']==0,
        'public_complete_known_guarded_and_product_STOP':True,'public_observation_provenance':provenance,
        'source_selected_before_private':True,'private_reads':0,'model_or_native':0}
    save(frozen_source,source);save(certificate_path,certificate)
    ready={'schema':'exp248-frozen-public-choice-Root-only-once-final/1','task_id':task,'index':index,
        'attempt':terminal.get('first_public_pass_attempt') or provenance['candidate_observation_attempt'],
        'candidate_snapshot':snapshot,'candidate_source_sha256':source_sha,
        'business_source_file':str(frozen_source),'business_source_file_SHA256':sha(frozen_source),
        'goal_nodes':oracle['target_nodes'],'ordinary_nodes':oracle['ordinary_nodes'],'ref':ref,
        'original_masked_scope':mask_ref,'original_oracle_contract':oracle_ref,'original_runtime_contract':protocol,
        'native_output':str(E/'final_private_ROOT'/str(index)),
        'public_terminal_path':str(terminal_path),'public_terminal_SHA256':sha(terminal_path),
        'public_certificate_path':str(certificate_path),'public_certificate_SHA256':sha(certificate_path),
        'original_private_reference_path':str(OLD/'r'/str(index)/'f/final_preservation/run.json'),
        'original_private_reference_not_read_by_preparing_actor':True,
        'model_authorized':False,'native_authorized':False,'private_authorized':False,
        'Root_exact_actual_grant_required':True,'private_details_must_not_return_to_any_model_or_repair_actor':True,
        'no_further_generation_after_this_public_natural_terminal':True,'new_native':0,'private':0,'model':0}
    save(ready_path,ready)
    return {'status':'FINAL_SELECTED_SOURCE_FROZEN_ROOT_ONLY_READY','task_id':task,'ready_path':str(ready_path),
        'ready_SHA256':sha(ready_path),'public_G_O_actual_all_PASS':certificate['public_G_O_actual_all_PASS'],
        'private_read_or_native':0}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--index',required=True,type=int);args=parser.parse_args()
    print(canonical(prepare(args.index)),flush=True)
if __name__=='__main__':main()

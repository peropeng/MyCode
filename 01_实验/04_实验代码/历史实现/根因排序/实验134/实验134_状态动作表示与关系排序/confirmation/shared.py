"""Confirmation utilities; deliberately independent of API runtime common.py."""
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

T=Path(__file__).resolve().parent;E=T.parent;W=E.parents[1]
ROOT=Path('D:/Code/毕设/graduate-thesis-experiments')
API=ROOT/'工作区/1005-exp132-paper-three/实验/实验132_论文驱动三案归因对比/engineering_v2/api'
RES=T/'api_runtime';PAID=('AA','Binary','SDBL','AA_STRUCTURED')
ARMS=('N','A','B','AB','StepFinder');SEEDS=(20261006,20261007,20261008)
PRIORS=('PRI_FIRST_ENGINEER','PRI_FIRST_ENGINEER_STATE','PRI_CONSTANT3','PRI_CONSTANT4')
PROJECTED={name+'_OBSERVED_EVENT_STATE_PROJECTION':name for name in ('AA','Binary','SDBL','StepFinder')}
LOCAL=ARMS+tuple(arm+'/seed_'+str(seed) for arm in ARMS for seed in SEEDS)
CONDITIONS=LOCAL+PAID+PRIORS+tuple(PROJECTED)
PRIMARY_COMPARATORS=('AA','Binary','SDBL','StepFinder','AA_STRUCTURED')+tuple(PROJECTED)+PRIORS
SECONDARY_PAIRS=(('N','A'),('N','B'),('N','AB'),('A','B'),('A','AB'),('B','AB'),
                 ('StepFinder','N'),('StepFinder','A'),('StepFinder','AB'))
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode('utf-8')).hexdigest()
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def lines(p):return [json.loads(s) for s in Path(p).read_text('utf-8-sig').splitlines() if s] if Path(p).exists() else []
def write(p,v):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def atomic(p,v):
    p=Path(p);tmp=p.with_name(p.name+f'.{os.getpid()}.tmp')
    with tmp.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,p)
def append(p,v):
    with Path(p).open('a',encoding='utf-8') as f:f.write(canonical(v)+'\n');f.flush();os.fsync(f.fileno())
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec)
    sys.modules[name]=result;exec(compile(Path(path).read_text('utf-8-sig'),str(path),'exec'),result.__dict__);return result
CORE=module(E/'common.py','exp134_confirmation_status_core')
EVENTS=module(ROOT/'工作区/1006-exp133-state-action/实验/实验133_状态动作选择性核验/method.py','exp134_confirmation_public_events')
AA_PARSER=module(ROOT/'工作区/1006-exp133-state-action/实验/实验133_状态动作选择性核验/development_v2/method.py','exp134_confirmation_aa_display_parser')
def verify():
    p=read(T/'protocol.json')
    for path,h in p['frozen_files'].items():
        if sha(path)!=h:raise RuntimeError('frozen_confirmation_input_changed:'+path)
    seal=read(E/'training/model_seal.json')
    if sha(E/'training/model_seal.json')!=read(T/'approved_decision.json')['model_seal_sha256']:raise RuntimeError('primary_model_seal_changed')
    for r in seal['models']:
        if sha(r['checkpoint'])!=r['checkpoint_sha256']:raise RuntimeError('frozen_model_changed')
    return p
def native_choice(step,record,**extra):
    valid=type(step) is int and 0<=step<len(record['turns'])
    return {'valid':valid,'chosen_step':step if valid else None,'predicted_role':record['turns'][step]['role'] if valid else None,
            'order':None,'native_complete_ranking':False,**extra}
def event_projection(original,record,condition,source_condition):
    mapping={pair['ensuing_action']:pair['decision_state'] for pair in EVENTS.representation(record)['observed_state_action_links']}
    old=original.get('chosen_step') if original.get('valid') else None;choice=mapping.get(old,old)
    return native_choice(choice,record,zero_API=True,derived_control=True,source_condition=source_condition,
        original_chosen_step=old,observed_event_projection_applied=old is not None and choice!=old,
        predicted_role=original.get('predicted_role'),role_output_origin='preserved_original_method_role',
        projection_never_changes_original_prediction=True)
def qualified_priors(record):
    packet=EVENTS.representation(record);values=EVENTS.controls(record,packet,0,None)
    return {name:native_choice(values[name],record,zero_API=True,position_control=True) for name in PRIORS}

import datetime
import hashlib
import json
import os
from pathlib import Path
import time

E=Path(__file__).resolve().parent
W=E.parents[1]
ROOT=Path('D:/Code/毕设/graduate-thesis-experiments')
PYTHON=ROOT/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'
SOURCE_ZIP=ROOT/'工作区/1005-exp132-paper-three/scratch/exp132/agentracer-data-v1.0.0.zip'
OWNER_ID='01a10cf5-0724-7a31-b0ac-feee7bf77684'
SEEDS=(20261006,20261007,20261008)
ARMS=('N','A','B','AB','StepFinder')
STARTED=time.monotonic()

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(value):return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def read(path):return json.loads(Path(path).read_text('utf-8-sig'))
def write_new(path,value):
    with Path(path).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def atomic(path,value):
    p=Path(path);tmp=p.with_name(p.name+f'.{os.getpid()}.tmp')
    with tmp.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,p)
def append(path,value):
    with Path(path).open('a',encoding='utf-8') as f:f.write(canonical(value)+'\n');f.flush();os.fsync(f.fileno())
def status(phase,**values):
    owner=read(W/'execution_owner.json')
    if owner['owner_chat_id']!=OWNER_ID or owner['owner_released']:raise RuntimeError('exclusive_Exp134_owner_required')
    state=read(E/'execution_state.json') if (E/'execution_state.json').exists() else {}
    active=phase in ('EXP134_PUBLIC_SPLIT_FREEZE','EXP134_LOCAL_EMBEDDING_CACHE','EXP134_LOCAL_TRAINING','EXP134_EXPOSED32_LABEL_FREE_INFERENCE')
    state.update(schema='Exp134-local-execution-state/1.0',at_utc=now(),experiment='Exp134',owner_chat_id=OWNER_ID,
        phase=phase,current_pid=os.getpid() if active else None,current_command=' '.join(__import__('sys').argv) if active else None,
        phase_elapsed_seconds=time.monotonic()-STARTED,paid_API_calls=0,unsettled_requests=0,
        balance_CNY='4.55',protected_confirmation_CNY='2.25',account_floor_CNY='1.02',
        fresh_confirmation={'completed_tasks':0,'unexposed_test_label_accesses':0})
    state.update(values)
    atomic(E/'execution_state.json',state);atomic(W/'execution_state.json',state)
    atomic(W/'execution_checkpoint.json',{'at_utc':now(),'experiment':'Exp134','phase':phase,'owner_chat_id':OWNER_ID,
        'state':str(E/'execution_state.json'),'plan':str(E/'approved_plan.json'),'paid_API_calls':0,
        'unexposed_test_label_accesses':0,'next_executable_command':state.get('next_executable_command'),
        'data_manifest':str(E/'data/public_split_manifest.json'),'model_protocol':str(E/'training_protocol.json')})
    owner.update(at_utc=state['at_utc'],phase=phase,current_runner_pid=state['current_pid'],current_command=state['current_command'])
    atomic(W/'execution_owner.json',owner)

def public_object(raw,allowed):
    """Decode only whitelisted top-level values; skip all other JSON values.

    Private labels/answers/reasons are never deserialized by the public path.
    """
    if isinstance(raw,bytes):raw=raw.decode('utf-8-sig')
    decoder=json.JSONDecoder();i=0;n=len(raw);out={};seen=set()
    def space(index):
        while index<n and raw[index].isspace():index+=1
        return index
    i=space(i)
    if i>=n or raw[i]!='{':raise ValueError('top_level_object_required')
    i+=1
    while True:
        i=space(i)
        if raw[i]=='}':break
        key,end=decoder.raw_decode(raw,i)
        if not isinstance(key,str) or key in seen:raise ValueError('invalid_or_duplicate_top_level_key')
        seen.add(key);i=space(end)
        if raw[i]!=':':raise ValueError('missing_colon')
        i=space(i+1)
        if key in allowed:
            value,i=decoder.raw_decode(raw,i);out[key]=value
        else:
            depth=0;quoted=False;escaped=False
            while i<n:
                c=raw[i]
                if quoted:
                    if escaped:escaped=False
                    elif c=='\\':escaped=True
                    elif c=='"':quoted=False
                elif c=='"':quoted=True
                elif c in '[{':depth+=1
                elif c in ']}':
                    if depth==0:break
                    depth-=1
                elif c==',' and depth==0:break
                i+=1
            if quoted or depth:raise ValueError('unclosed_skipped_JSON_value')
        i=space(i)
        if raw[i]==',':i+=1;continue
        if raw[i]=='}':break
        raise ValueError('invalid_object_separator')
    if raw[space(i+1):].strip():raise ValueError('trailing_JSON_data')
    return out

"""EXP249 source-only common definitions; no execution or remote clients on import."""
import datetime
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
R = Path('D:/Code/毕设/graduate-thesis-experiments')
COMMON = R / '工作区/1010-unified-six'
OLD = R / '工作区/1011-our19'
PUBLIC_CONTRACTS = R / '实验/实验241_Agentless新确认集21_生成测试ScopeV2/candidate'
METHODS = ['OURS_CURRENT_FAILURE_BOUND_248', 'AGENTLESS_FSE2025', 'ENAGENT_ICSE2026']
TASKS = ['dask__dask-9378', 'getmoto__moto-5072', 'getmoto__moto-5134',
         'getmoto__moto-5286', 'getmoto__moto-6352', 'pydantic__pydantic-8567']
FIRST_TWO = TASKS[2:4]
CONTROLLER = R / '工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'
V14 = COMMON / 'shared_native_v14_certificate_complete'


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            value.update(block)
    return value.hexdigest()


def owned(path):
    path = Path(path).resolve()
    if not path.is_relative_to(E.resolve()) or path == E.resolve():
        raise RuntimeError('EXP249_OUTPUT_OUTSIDE_OWN_SCOPE')
    return path


def save(path, value):
    path = owned(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.' + str(os.getpid()) + '.tmp')
    with temp.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def intent(path, value):
    path = owned(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        stream.write(canonical(value) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def safe_rel(text):
    p = Path(text)
    if not isinstance(text, str) or p.is_absolute() or '..' in p.parts or '.git' in p.parts or ':' in text or '\\' in text:
        raise RuntimeError('EXP249_RELATIVE_PATH_REQUIRED')
    return p.as_posix()


class Grant:
    """A separate exact Root release is needed for each real action."""
    def __init__(self, path, action, tasks):
        self.path = Path(path).resolve()
        self.sha256 = sha(self.path)
        self.value = read(self.path)
        self.action = action
        self.tasks = list(tasks)
        self.check(full=True)

    def check(self, full=False):
        g = self.value
        if sha(self.path) != self.sha256:
            raise RuntimeError('EXP249_ROOT_GRANT_CHANGED')
        if g.get('root_authorized') is not True or g.get('action') != self.action or g.get('task_ids') != self.tasks:
            raise RuntimeError('EXP249_ROOT_EXACT_ACTION_NOT_GRANTED')
        if not self.tasks or any(t not in FIRST_TWO for t in self.tasks):
            raise RuntimeError('EXP249_FIRST_TWO_ONLY_AT_THIS_GATE')
        for name in ('model_authorized', 'private_execution_authorized', 'finance_authorized'):
            if g.get(name) is not False:
                raise RuntimeError('EXP249_MODEL_PRIVATE_FINANCE_MUST_BE_FALSE')
        native = self.action in ('identity', 'current_C0')
        if g.get('native_authorized') is not native:
            raise RuntimeError('EXP249_NATIVE_ACTION_PERMISSION_MISMATCH')
        if g.get('trusted_original_test_source_read_authorized') is not (self.action == 'materialize'):
            raise RuntimeError('EXP249_TRUSTED_MASKING_READ_NOT_GRANTED')
        end = g.get('lease_end_UTC')
        if not isinstance(end, str) or time.time() >= datetime.datetime.fromisoformat(end).timestamp():
            raise RuntimeError('EXP249_ROOT_LEASE_CLOSED')
        if (E / 'STOP_REQUESTED.json').exists() or any(Path(p).exists() for p in g.get('root_stop_paths', [])):
            raise RuntimeError('EXP249_ROOT_OR_LOCAL_STOP')
        if g.get('protocol_SHA256') != sha(E / 'protocol249_SOURCE.json') or g.get('source_seal_SHA256') != sha(E / 'SOURCE_SEAL249.json'):
            raise RuntimeError('EXP249_SOURCE_RELEASE_BINDING_MISMATCH')
        if full:
            seal = read(E / 'SOURCE_SEAL249.json')
            for path, expected in {**seal['sources_SHA256'], **seal['public_inputs_SHA256']}.items():
                if sha(path) != expected:
                    raise RuntimeError('EXP249_SOURCE_INPUT_DRIFT ' + path)
        return True


def binding(task):
    value = read(E / 'TASK_BINDINGS249_SOURCE.json')
    row = next(v for v in value['tasks'] if v['task_id'] == task)
    contract_path = Path(row['public_contract'])
    if sha(contract_path) != row['public_contract_SHA256']:
        raise RuntimeError('EXP249_PUBLIC_CONTRACT_DRIFT')
    return row, read(contract_path)

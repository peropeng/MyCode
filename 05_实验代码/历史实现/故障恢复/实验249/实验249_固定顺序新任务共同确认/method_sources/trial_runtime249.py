"""Durable trial namespace and pure public binding checks; no execution clients."""
import copy
import datetime
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
E249 = HERE.parent
ROOT = Path('D:/Code/毕设/graduate-thesis-experiments')
OLD = ROOT / '工作区/1011-our19'
FIN = ROOT / '工作区/1010-unified-six/finance_queue_remaining_SOURCE'
SOURCE248 = ROOT / '工作区/1012-exp248-current-feedback-repair/实验/实验248_当前失败反馈绑定与修复闭包'


def read(path): return json.loads(Path(path).read_text('utf-8-sig'))
def canonical(value): return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
def digest(value): return hashlib.sha256(canonical(value).encode()).hexdigest()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def clean(value):
    if isinstance(value, dict): return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (set, tuple)): return [clean(v) for v in sorted(value)]
    if isinstance(value, list): return [clean(v) for v in value]
    if isinstance(value, Path): return str(value)
    return value


def save(path, value):
    path = Path(path).resolve()
    if not path.is_relative_to(HERE.resolve()): raise RuntimeError('EXP249_METHOD_WRITE_OUTSIDE_OWN_SCOPE')
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.' + str(os.getpid()) + '.tmp')
    with temp.open('x', encoding='utf-8') as stream:
        json.dump(clean(value), stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    os.replace(temp, path)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec); sys.modules[name] = value; spec.loader.exec_module(value)
    return value


def checked_contract(path, method):
    c = read(path)
    protocol = read(E249 / 'protocol249_SOURCE.json')
    if c.get('method') != method or c.get('task_id') not in protocol['task_order'] or c.get('trial_id') not in protocol['trial_ids']:
        raise RuntimeError('EXP249_METHOD_TASK_TRIAL_SCOPE')
    trial = protocol['trial_ids'].index(c['trial_id'])
    if c.get('trial_master_seed') != protocol['trial_master_seeds'][trial]:
        raise RuntimeError('EXP249_PREDECLARED_REPEAT_SEED_DRIFT')
    out = Path(c['output_root']).resolve()
    expected = (HERE / 'runs' / method / c['task_id'] / c['trial_id']).resolve()
    if out != expected: raise RuntimeError('EXP249_UNIQUE_METHOD_TASK_TRIAL_NAMESPACE_REQUIRED')
    for label in ('public_contract', 'public_test_scope_contract', 'current_C0_observation', 'current_C0_parent_terminal', 'finance_configuration'):
        ref = c.get(label, {})
        if not isinstance(ref.get('path'), str) or not isinstance(ref.get('sha256'), str):
            raise RuntimeError('EXP249_DEPENDENCY_NOT_BOUND_' + label)
        if sha(ref['path']) != ref['sha256']: raise RuntimeError('EXP249_BOUND_INPUT_DRIFT_' + label)
    parent = read(c['current_C0_parent_terminal']['path'])
    if parent.get('task_id') != c['task_id'] or parent.get('exit_code') != 0 or parent.get('error') is not None or parent.get('stop_receipt', {}).get('all_owned_descendants_terminated') is not True:
        raise RuntimeError('EXP249_FRESH_C0_PARENT_STOP_REQUIRED')
    scope = read(c['public_test_scope_contract']['path'])
    row = next(v for v in scope['tasks'] if v['task_id'] == c['task_id'])
    if row.get('materialization_qualified') is not True: raise RuntimeError('EXP249_CURRENT_MASKED_VIEW_UNAVAILABLE')
    config = read(c['finance_configuration']['path'])
    if c.get('finance_phase') not in config.get('phases', {}): raise RuntimeError('EXP249_NEW_PHASE_NOT_REGISTERED')
    import shared_input249
    supplement, decoded = shared_input249.supplement(config, c['task_id'])
    if supplement.get('current_masked_scope_SHA256') != c['public_test_scope_contract']['sha256']:
        raise RuntimeError('EXP249_C0_AND_CURRENT_MASKED_VIEW_MISMATCH')
    if supplement.get('fresh_C0_observation_SHA256') != c['current_C0_observation']['sha256'] or supplement.get('fresh_C0_parent_terminal_SHA256') != c['current_C0_parent_terminal']['sha256']:
        raise RuntimeError('EXP249_CURRENT_C0_COMMON_SUPPLEMENT_WITNESS_DRIFT')
    return c, out, config, supplement, decoded


def trial_seed(contract, role, original_seed, reader_index=0):
    return int(hashlib.sha256(canonical({'master': contract['trial_master_seed'], 'task': contract['task_id'],
        'stage': role, 'original_fixed_stage_seed': int(original_seed), 'reader_index': reader_index}).encode()).hexdigest()[:8], 16) % 2147483647


def verify_source_seal(path):
    value = read(path)
    for source, expected in value['sources_SHA256'].items():
        if sha(source) != expected: raise RuntimeError('EXP249_METHOD_SOURCE_DRIFT ' + source)
    for source, expected in value.get('public_inputs_SHA256', {}).items():
        if sha(source) != expected: raise RuntimeError('EXP249_METHOD_PUBLIC_INPUT_DRIFT ' + source)
    return value

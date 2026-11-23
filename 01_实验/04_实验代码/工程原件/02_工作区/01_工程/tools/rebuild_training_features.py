"""Rebuild the lost label-free training cache from verified original inputs.

This only runs the frozen encoder. It neither trains a ranker nor reads test
labels. Historical source files remain byte-for-byte unchanged. The resulting
cache has a new receipt and is never presented as the deleted original bytes.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import gc
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import sys
import time
from datetime import datetime, timezone

ENGINE = Path(__file__).resolve().parents[1]
ROOT = ENGINE.parents[1]
HISTORY = ROOT / '01_实验/历史结论与经验/实验'
ORIGINAL = HISTORY / '实验134_状态动作表示与关系排序'
HELPERS = ENGINE / 'src/thesis_recovery/frozen/training_public_helpers'
E = ENGINE / '.rebuild/paper-inputs/rq1-source'
sys.dont_write_bytecode = True
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
GPU_TORCH = ENGINE / '.external/torch-cuda'
if GPU_TORCH.is_dir():
    sys.path.insert(0, str(GPU_TORCH))


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(2**20), b''):
            digest.update(block)
    return digest.hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def write_new(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def append(path, value):
    with Path(path).open('a', encoding='utf-8', newline='\n') as stream:
        stream.write(canonical(value) + '\n')


def status(phase, **fields):
    append(E / 'features/rebuild_progress.jsonl', {'at_utc': now(), 'phase': phase, **fields})


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_text(encoding='utf-8-sig'), str(path), 'exec'), module.__dict__)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight', action='store_true')
    args = parser.parse_args()
    expected_inputs = {
        'public_records.json': '9b792f522651027ccafd76af43c88da7fc6a1b5e579ba848cfc9fe39028c4885',
        'selected_train_labels.private.json': 'a5f50889aefc6b66cd4b0a5077e137682569d5e24ae8802c26f4203eb59477f1',
    }
    # Verify label-file bytes without parsing any label values.
    for name, expected in expected_inputs.items():
        if sha(E / 'data' / name) != expected:
            raise RuntimeError('original_selected_input_changed:' + name)
    helper_hashes = {
        'runner88.py': 'e6cc523e9d1da8328face122b216492d130ab51eb2afe7b099d87dee9798ed54',
        'runner112.py': 'ab02c95823bdd6baaa5d3cf7c7d467fbcfaa8743788a91820b4de55be87dc9df',
        'method133.py': '523d73d589fef9d3f3f180d86c3f961bfaf6abf0d5bb422ecbb48c08a99802f1',
    }
    for name, expected in helper_hashes.items():
        if sha(HELPERS / name) != expected:
            raise RuntimeError('original_public_helper_changed:' + name)
    import numpy as np
    import torch
    adapters = load_module(ORIGINAL / 'sources/model_adapters.py', 'restored_original_training_adapters')
    assets = {
        'encoder_directory': ENGINE / '.external/Qwen3-Embedding-0.6B',
        'structure88_source': HELPERS / 'runner88.py',
        'structure112_source': HELPERS / 'runner112.py',
    }
    binding = {'encoder_files': {}, 'binding_scope': 'cache_rebuild_encoder_and_public_helpers_only'}
    for name, expected in adapters.ENCODER_FILE_HASHES.items():
        if sha(assets['encoder_directory'] / name) != expected:
            raise RuntimeError('original_encoder_changed:' + name)
        binding['encoder_files'][name] = expected
    binding['public_helpers'] = helper_hashes
    adapters.default_assets = lambda: assets
    adapters.verify_asset_binding = lambda selected: binding
    events = adapters._pure_old_helpers(
        HELPERS / 'method133.py', {'is_state', 'representation'}, set(), {'json': json})
    source = ORIGINAL / 'prepare_features.py'
    source_hash = sha(source)
    namespace = {
        'adapters': adapters, 'np': np, 'torch': torch, 'Counter': Counter,
        'gc': gc, 'hashlib': hashlib, 'sqlite3': sqlite3, 'time': time,
        'E': E, 'ROOT': ROOT, 'canonical': canonical, 'digest': digest,
        'now': now, 'sha': sha, 'write_new': write_new, 'append': append, 'status': status,
        'load_original_events': lambda: (events, HELPERS / 'method133.py'),
    }
    tree = ast.parse(source.read_text(encoding='utf-8-sig'))
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in {'feature_input', 'build'}]
    if {node.name for node in nodes} != {'feature_input', 'build'}:
        raise RuntimeError('original_feature_builder_definitions_missing')
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), str(source), 'exec'), namespace)
    records = json.loads((E / 'data/public_records.json').read_text(encoding='utf-8'))['records']
    if len(records) != 614 or len({r['sample_id'] for r in records}) != 614:
        raise RuntimeError('selected_training_record_count_changed')
    structure = adapters.load_public_structure_helpers(assets)
    steps = 0
    for record in records:
        item = namespace['feature_input'](record, structure, events)
        n = len(record['turns']); steps += n
        if item['raw_structure'].shape != (n, 23) or not torch.isfinite(item['raw_structure']).all():
            raise RuntimeError('invalid_original_structure_features')
        if len(item['adjacency']) != 4:
            raise RuntimeError('missing_relation_channel')
    preflight = {'records': len(records), 'steps': steps, 'original_source_sha256': source_hash,
                 'encoder_revision': adapters.ENCODER_REVISION, 'encoder_files': binding['encoder_files'],
                 'helper_sha256': helper_hashes, 'torch_version': torch.__version__,
                 'cuda_available': torch.cuda.is_available(), 'new_training_steps': 0,
                 'test_label_values_parsed': 0, 'paid_api_calls': 0}
    print(canonical({'feature_rebuild_preflight': preflight}), flush=True)
    if args.preflight:
        return
    if not torch.cuda.is_available():
        raise RuntimeError('GPU_runtime_required_for_bounded_cache_rebuild')
    (E / 'features').mkdir(exist_ok=True)
    # The original builder records this local source binding after saving.
    # Preserve the original bytes at its expected relative receipt location.
    source_copy = E / 'sources/model_adapters.py'
    original_adapter = ORIGINAL / 'sources/model_adapters.py'
    source_copy.parent.mkdir(exist_ok=True)
    if source_copy.exists():
        if sha(source_copy) != sha(original_adapter):
            raise RuntimeError('restored_adapter_source_differs_no_overwrite')
    else:
        with source_copy.open('xb') as stream:
            stream.write(original_adapter.read_bytes())
    receipt = namespace['build'](records, 'train_validation_features.pt')
    receipt.update({'restoration_status': 'rebuilt_from_byte_identical_public_inputs_with_original_frozen_encoder',
                    'original_cache_bytes_restored': False,
                    'deleted_original_feature_sha256': '9e07a4398899f4698e321a2173d71f96c9643be0409685a2bd8395c04c8699f1',
                    'historical_cache_sha256_match': receipt['feature_file_sha256'] == '9e07a4398899f4698e321a2173d71f96c9643be0409685a2bd8395c04c8699f1',
                    'original_feature_builder_sha256': source_hash,
                    'new_training_steps': 0, 'test_label_values_parsed': 0, 'paid_api_calls': 0,
                    'output': (E / 'features/train_validation_features.pt').relative_to(ENGINE).as_posix(),
                    'sqlite_sha256': sha(E / 'features/embedding_cache.sqlite3')})
    # The original receipt stays untouched; this separate receipt describes restoration.
    write_new(ENGINE / 'verification/rq1_training_feature_rebuild.json', receipt)
    print(canonical({'cache_rebuild_complete': True, 'receipt': 'verification/rq1_training_feature_rebuild.json'}), flush=True)


if __name__ == '__main__':
    main()

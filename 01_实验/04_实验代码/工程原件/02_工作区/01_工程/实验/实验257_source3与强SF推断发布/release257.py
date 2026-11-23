"""Prospective public-only Exp257 inference; no trainer, task runner or labels.

The immutable model sources are byte copies. Public helper functions alone are
AST-extracted. All writes remain in this experiment; assets are read in place.
"""
import ast
import collections
import csv
import datetime
import gc
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import random
import sys
import time
import types

os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_DATASETS_OFFLINE'] = '1'
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8')
E = Path(__file__).resolve().parent
ROOT = Path('D:/Code/毕设/graduate-thesis-experiments')
P249 = ROOT / '工作区/1012-exp249-prospective-confirmation/实验/实验249_固定顺序新任务共同确认'
P224 = ROOT / '工作区/1008-2320-exp224-flash-common/实验/实验224_二十三题Flash完整共同恢复比较'
P191 = ROOT / '工作区/1008-exp191-public-rank-output-interface/实验/实验191_十五题公开排序与约束输出接口资格'
P166 = ROOT / '工作区/1007-exp166-four-paper-baselines/实验/实验166_四项正式论文基线快速整体验证'
P153 = ROOT / '工作区/1007-exp153-global-context/实验/实验153_候选条件全轨迹上下文'
P158 = ROOT / '工作区/1007-exp158-author-preset-baseline/实验/实验158_StepFinder论文双预设强对照'
QROOT = ROOT / '工作区/0922-exp124-ranking-baselines/third_party/Qwen3-Embedding-0.6B'
REVISION = '97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3'
SOURCE_SEEDS = [20261006, 20261007, 20261008]
RELATIONS = ['temporal', 'same_role', 'same_full_shape_signature', 'same_nonempty_action_shape']
IDENTITIES = {}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def bind(path, expected=None):
    path = Path(path).resolve()
    actual = sha(path)
    if expected is not None:
        assert actual == expected, ('ASSET_SHA_DRIFT', str(path), actual, expected)
    IDENTITIES[str(path)] = actual
    return actual


def read(path, expected=None):
    bind(path, expected)
    return json.loads(Path(path).read_text('utf-8-sig'))


def save(relative, value):
    path = (E / relative).resolve()
    assert path.is_relative_to(E), 'EXP257_WRITE_SCOPE'
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', 'utf-8')
    os.replace(tmp, path)


def event(phase, **extra):
    value = {'at_utc': now(), 'phase': phase, 'pid': os.getpid(), **extra}
    save('EXECUTION_STATUS257.json', value)
    print(canonical(value), flush=True)


def module(name, path):
    bind(path)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def pure(path, functions, constants, namespace):
    bind(path)
    nodes = []
    found = set()
    for node in ast.parse(Path(path).read_text('utf-8-sig')).body:
        if isinstance(node, ast.FunctionDef) and node.name in functions:
            nodes.append(node)
            found.add(node.name)
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in constants:
            ast.literal_eval(node.value)
            nodes.append(node)
            found.add(node.targets[0].id)
    assert found == functions | constants, (path, found)
    future = ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0)
    packet = ast.fix_missing_locations(ast.Module(body=[future, *nodes], type_ignores=[]))
    exec(compile(packet, str(path) + ':pure-public-only', 'exec'), namespace)
    return types.SimpleNamespace(**{name: namespace[name] for name in found})


def public_helpers():
    base = {'json': json, 'hashlib': hashlib, 'Counter': collections.Counter, 'defaultdict': collections.defaultdict}
    old88 = pure(ROOT / '实验/实验88_责任桥_去错误词与长度资格/runner.py',
                 {'_arity_bucket', '_shape', '_shape_depth', '_parse_shape', '_parsed_value', '_field_descriptor', 'turn_structure', '_step_stats', '_local_score', '_tie_digest'},
                 {'MAX_SHAPE_DEPTH', 'MAX_SHAPE_CHILDREN', 'E2_LOCAL_WEIGHTS'}, dict(base))
    return pure(ROOT / '实验/实验112_RQ1时序交互依赖完整排序/runner.py',
                {'phase_for_step', '_anonymous_digest', '_h0_vector', '_shape_labels', '_empty_neighbors', '_build_adjacency'},
                {'H0_DESCRIPTOR_NAMES', 'CHANNELS'}, {**base, 'E88': old88})


def models_scoped():
    names = ('common', 'original_models', 'owned_exp130_model', 'stepfinder_model')
    previous = {name: sys.modules.get(name) for name in names}
    previous_path = sys.path.copy()
    try:
        shim = types.ModuleType('exp257_minimal_common')
        shim.E = E
        shim.CONTEXT_ARMS = ('AB_GLOBAL', 'AB_LOCAL', 'AB_STATIC', 'AB_VALUE_PERM')
        sys.modules['common'] = shim
        sys.path.insert(0, str(E / 'sources'))
        for name in names[2:]:
            sys.modules[name] = module('exp257_' + name, E / 'sources' / (name + '.py'))
        sys.modules['original_models'] = module('exp257_original_models', E / 'sources/original_models.py')
        result = module('exp257_context_models', E / 'sources/context_models.py')
    finally:
        sys.path[:] = previous_path
        for name, old in previous.items():
            if old is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old
    return result


def tasks_and_contracts():
    a = read(ROOT / '工作区/1012-until0900-common/confirmation_common_C0_v4/COMMON_C0_SUPPLEMENT_REGISTRY.json')
    b = read(ROOT / '工作区/1012-until0900-common/confirmation_common_C0_next6_prospective_v1/COMMON_QUALIFIED_C0_REGISTRY.json')
    c = read(P249 / 'last_nine_qualification_SOURCE/ROOT_QUALIFIED_C0_LAST9_REGISTRY_CLOSED.json')
    original = a['task_order'] + b['fixed_six_task_order'] + [r['task_id'] for r in c['all_planned_rows']]
    ids = a['qualified_tasks_only'] + b['qualified_common_task_order'] + c['qualified_task_order']
    assert len(original) == len(set(original)) == 21
    assert len(ids) == len(set(ids)) == 18
    assert ids == [tid for tid in original if tid in set(ids)]
    contracts, qualification = {}, {}
    for tid in ids:
        if tid in a['tasks']:
            row = a['tasks'][tid]
            assert row['Root_actual_C0_accepted'] is True
            bind(row['path'], row['sha256'])
            bind(row['current_parent_path'], row['current_parent_STOP_SHA256'])
            path = P249 / 'contracts' / tid / 'public_contract.json'
        elif tid in b['tasks']:
            row = b['tasks'][tid]
            assert row['Root_actual_C0_accepted'] is True and row['qualification_status'] == 'QUALIFIED'
            bind(row['path'], row['sha256'])
            bind(row['current_parent_path'], row['current_parent_STOP_SHA256'])
            path = Path(row['public_contract']['path'])
            bind(path, row['public_contract']['sha256'])
        else:
            row = next(r for r in c['all_planned_rows'] if r['task_id'] == tid)
            assert row['qualification_status'] == 'QUALIFIED_CURRENT_C0'
            bind(row['parent_STOP']['path'], row['parent_STOP']['sha256'])
            path = Path(row['public_contract']['path'])
            bind(path, row['public_contract']['sha256'])
        contract = read(path)
        assert contract['task_id'] == tid and contract['actor_private_nodes_fields_or_callback'] is False
        contracts[tid] = contract
        qualification[tid] = {'original_plan_slot': original.index(tid) + 1, 'contract_path': str(path), 'contract_sha256': sha(path), 'current_C0_qualified': True,
                              'legal_business_paths_sha256': digest(sorted(contract['c0_business_paths_sha256'])), 'qualification_record': row}
    return ids, original, contracts, qualification


def pack(prob):
    assert prob and all(__import__('math').isfinite(p) and p >= 0 for p in prob)
    assert abs(sum(prob) - 1) < 1e-5
    order = sorted(range(len(prob)), key=lambda i: (-prob[i], i))
    return {'probabilities': prob, 'order': order, 'chosen_step': order[0], 'valid': True, 'native_complete_ranking': True}


def geometry(sample, raw, helper, events, torch, np):
    turns = sample['turns']
    n = len(turns)
    structure = np.asarray([helper._h0_vector({'turns': turns}, i) for i in range(n)], dtype=np.float32)
    neighbors = helper._build_adjacency({'turns': turns})
    adjacency, edge_sets = [], {}
    for rel in RELATIONS:
        ix = np.zeros((n, 2), dtype=np.int64)
        mask = np.zeros((n, 2), dtype=np.float32)
        edges = set()
        for i, ns in enumerate(neighbors[rel]):
            assert len(ns) <= 2
            ix[i, :len(ns)] = ns
            mask[i, :len(ns)] = 1
            edges.update((i, j) for j in ns)
        edge_sets[rel] = edges
        adjacency.append((torch.from_numpy(ix), torch.from_numpy(mask)))
    coordinates = [{'original_step_id': t['source_message_index'], 'source_channel_role': 'assistant'} for t in turns]
    packet = events.representation({'turns': turns, 'task': sample['task'], 'coordinate_map': coordinates})
    partner = torch.zeros(n, 2, dtype=torch.long)
    valid = torch.zeros(n, 2)
    for link in packet['observed_state_action_links']:
        s, a = link['decision_state'], link['ensuing_action']
        partner[s, 0] = a
        valid[s, 0] = 1
        partner[a, 1] = s
        valid[a, 1] = 1
    record = {'content': raw['content'], 'agent': raw['agent'], 'raw_structure': torch.from_numpy(structure),
              'adjacency': adjacency, 'paired_partner': partner, 'paired_valid': valid}
    pairs = {}
    for x, y in itertools.combinations(RELATIONS, 2):
        union = edge_sets[x] | edge_sets[y]
        pairs[x + '__' + y] = {'intersection_directed_edges': len(edge_sets[x] & edge_sets[y]), 'union_directed_edges': len(union),
                               'jaccard': len(edge_sets[x] & edge_sets[y]) / len(union) if union else None, 'exactly_equal': edge_sets[x] == edge_sets[y]}
    return record, {'edge_convention': 'directed receiver-to-neighbor; each relation <=2 per node', 'relation_directed_edges': {r: len(edge_sets[r]) for r in RELATIONS},
                    'pairwise_overlap': pairs, 'observed_state_action_links': packet['observed_state_action_links'], 'valid_pair_count': len(packet['observed_state_action_links']),
                    'effective_partner_direction_entries': int(valid.sum().item()), 'unique_roles': sorted(set(t['role'] for t in turns))}


def legal_evidence(ref, contract):
    path = Path(ref['task_path']) / 'visible/edits.json'
    edits = read(path)
    by_id = {e['call_id']: e for e in edits}
    assert len(by_id) == len(edits)
    legal_paths = set(contract['c0_business_paths_sha256'])
    assets = Path(ref['asset_root'])
    blob_cache = {}
    def blob(binding):
        if binding is None:
            return b''
        key = (binding['blob'], binding['sha256'])
        if key not in blob_cache:
            p = assets / binding['blob']
            bind(p, binding['sha256'])
            blob_cache[key] = p.read_bytes()
        return blob_cache[key]
    candidates, skipped = {}, []
    for row in ref['mapping']:
        step = row['step']
        for call_id in row['successful_edit_ids']:
            edit = by_id[call_id]
            business_path = edit['state_path'].removeprefix('repo/')
            if business_path not in legal_paths:
                skipped.append({'step': step, 'call_id': call_id, 'reason': 'OUTSIDE_CURRENT_LEGAL_BUSINESS_PATHS'})
                continue
            before, after = blob(edit.get('before')), blob(edit.get('after'))
            if before == after:
                skipped.append({'step': step, 'call_id': call_id, 'reason': 'NO_ACTUAL_BEFORE_AFTER_CHANGE'})
                continue
            assert before.decode('utf-8') != after.decode('utf-8')
            candidates[call_id] = {'step': step, 'call_id': call_id, 'path': business_path, 'before_sha256': hashlib.sha256(before).hexdigest(), 'after_sha256': hashlib.sha256(after).hexdigest()}
    return candidates, skipped, {'path': str(path), 'sha256': sha(path)}


def ordered_legal(order, mapping, candidates):
    by_step = {r['step']: r for r in mapping}
    seen, result = set(), []
    for step in order:
        for call_id in by_step[step]['successful_edit_ids']:
            if call_id in seen:
                continue
            seen.add(call_id)
            if call_id in candidates:
                result.append(candidates[call_id])
    return result


def first_divergence(a, b):
    for i, (x, y) in enumerate(itertools.zip_longest(a, b)):
        if x != y:
            return i + 1
    return None


def main():
    start = time.monotonic()
    bind(__file__)
    plan = ROOT / '开题/20261012_Astra两小时独立审阅/03_后续四小时实验执行计划.md'
    bind(plan, '57843b350ebf8f1950ab4e88aea06d3fd7e5d797108792705a7eca61ec7341aa')
    assets = read(ROOT / '工作区/1012-astra-review-2h/middle/模型参数与最小推断资产引用.json', '3e30db83b717952bc9c589cb0e9e6ab1b496d17d8647d3d3bdc8af98edfaada5')
    ids, original, contracts, qualification = tasks_and_contracts()
    refs = {r['task_id']: r for r in read(P224 / 'data/selected_task_bindings.json')['tasks']}
    bind(P224 / 'data/public_inputs.jsonl')
    samples = {r['sample_id']: r for r in [json.loads(line) for line in (P224 / 'data/public_inputs.jsonl').read_text('utf-8-sig').splitlines() if line.strip()]}
    batches = [ids[:16], ids[16:]]
    protocol = {'schema': 'EXP257-public-source3-strongSF-prospective-inference/1', 'frozen_at_utc': now(), 'window_start_beijing': '2026-10-12T19:29:36+08:00',
                'window_deadline_beijing': '2026-10-12T23:29:36+08:00', 'original_plan21_order': original, 'qualified18_order': ids, 'excluded_unqualified': [tid for tid in original if tid not in ids],
                'qualification': qualification, 'batches': [{'ids': batch, 'padded_T': max(len(samples[tid]['turns']) for tid in batch)} for batch in batches],
                'batch_policy': 'Original qualified plan order, 16+2; same fixed batch for all models and seeds. Preserve SF padded-T bias unchanged.',
                'source3_seeds': SOURCE_SEEDS, 'source3_selected_epochs': [6, 6, 3], 'SF_ALG50_selected_epochs': [23, 14, 20],
                'SF_explicit_config': {'content_dim': 128, 'agent_dim': 32, 'hidden_dim': 64, 'num_heads': 2, 'head_dim': 32, 'dropout': .5, 'alpha': .1, 'beta': .9, 'gamma': .4, 'scales': [1, 2]},
                'feature_policy': 'Reuse only exact public turn/role/text bound raw content128+actor32 float32; reconstruct structure23, adjacency, event geometry from AST-extracted pure functions and verify against cached geometry.',
                'OURS_semantic_normalization': 'original collate separate L2 for content and actor', 'SF_semantic_input': 'original raw float32; no L2 adaptation',
                'scalers': 'Every checkpoint own scaler_mean and scaler_std; no fitting', 'ensemble': 'softmax float32 per trajectory then equal mean float64; source3/SF 3 seeds; AF 5 folds then 3 seeds',
                'tie_break': 'original ordinal ascending', 'recovery_deployment': 'Exp249 MAX3 progressive first 1/2/3 legal edit evidence',
                'selection_rule': 'First two in original plan order with >=2 legal changed business edits and different source3-vs-ALG50 first3 call-ID prefix, without outcomes or Gold.',
                'generation_native_training_newGold_downloads': 0, 'execution_device': 'CPU float32, deterministic, threads=4; GPU peak=0', 'source_SHA256_before_forward': dict(IDENTITIES)}
    save('PROTOCOL257.json', protocol)
    protocol_sha = sha(E / 'PROTOCOL257.json')
    event('PROTOCOL_FROZEN_BEFORE_FORWARD', tasks=len(ids), batches=protocol['batches'], protocol_sha256=protocol_sha)
    import numpy as np
    import torch
    torch.set_num_threads(4)
    try:
        import psutil
        process = psutil.Process()
    except ImportError:
        process = None
    runtime = {'python': sys.executable, 'python_version': sys.version, 'torch': torch.__version__, 'numpy': np.__version__, 'cuda_available': torch.cuda.is_available(), 'device': 'cpu',
               'threads': torch.get_num_threads(), 'GPU_allocated_for_exp257_bytes': 0}
    feature_begin = time.monotonic()
    helper = public_helpers()
    events = pure(ROOT / '工作区/1006-exp133-state-action/实验/实验133_状态动作选择性核验/method.py', {'is_state', 'representation'}, set(), {'json': json})
    geometry_fn = geometry
    producer_sets = [(P166, 'features/features.pt', 'features/receipt.json', 'features/encoder_identity.json', 'data/public_inputs.jsonl', 'rank166.py'),
                     (P191, 'features/features191.pt', 'features/feature_receipt191.json', 'features/encoder_identity191.json', 'data/public_inputs.jsonl', 'rank191.py'),
                     (P224, 'features/new8_features224.pt', 'features/new8_feature_receipt224.json', 'features/encoder_identity224.json', 'data/public_inputs.jsonl', 'rank8_224.py')]
    bound = read(ROOT / '工作区/0922-exp124-ranking-baselines/实验/实验124_责任排序强基线与外部迁移/results/preclaim_binding.json')
    # Actual existing encoder bytes and source identity verified; tokenizer is local-only.
    for name, expected in bound['model_files_sha256'].items():
        bind(QROOT / name, expected)
    encoder_source = ROOT / '工作区/0922-exp124-ranking-baselines/third_party/StepFinder/Q3Emb.py'
    bind(encoder_source, '6a6fa26c53d8b47d7bd851e0971960b540b59ea79ddc7300961872b3cd7d3189')
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(str(QROOT), revision=REVISION, padding_side='left', local_files_only=True, trust_remote_code=True)
    data, feature_rows, geo_rows, provider = {}, [], {}, {}
    for directory, tensor_name, receipt_name, encoder_name, public_name, producer_name in producer_sets:
        receipt = read(directory / receipt_name)
        encoder = read(directory / encoder_name)
        assert encoder['revision'] == REVISION and encoder['max_length'] == 8192
        hashes = encoder.get('files', encoder.get('file_SHAs', encoder.get('model_files')))
        assert hashes == bound['model_files_sha256']
        bind(directory / producer_name)
        bind(P191 / 'ranking_prepare178.py')
        producer_public = directory / public_name
        bind(producer_public)
        producer_samples = {r['sample_id']: r for r in [json.loads(line) for line in producer_public.read_text('utf-8-sig').splitlines() if line.strip()]}
        expected = receipt.get('feature_file_sha256', receipt.get('feature_sha256', receipt.get('features_sha256')))
        tensor_sha = bind(directory / tensor_name, expected)
        if directory == P166:
            tensor_sha = bind(directory / tensor_name, 'c9c70d59e1c0ada826fcb21d38b0f325c5227dc8f5b98c1dcd309213e75f6a2d6') if False else tensor_sha
        records = torch.load(directory / tensor_name, map_location='cpu', weights_only=False)['records']
        for row in receipt['rows']:
            tid = row.get('task_id', row.get('sample_id'))
            if tid not in ids or tid in data:
                continue
            sample = samples[tid]
            ref = refs[tid]
            assert sample['turns'] == producer_samples[tid]['turns'], ('CACHE_PUBLIC_TURNS_DRIFT', tid)
            turns_sha = hashlib.sha256(json.dumps(sample['turns'], sort_keys=True).encode()).hexdigest()
            assert turns_sha == ref['input_turns_sha256'] == row['input_turns_sha256']
            turns = sample['turns']
            assert sorted(set(t['role'] for t in turns)) == ['role_0'], ('ANONYMOUS_ROLE_PROTOCOL', tid)
            assert [t['source_message_index'] for t in turns] == [r['message_index'] for r in ref['mapping']]
            assert [r['step'] for r in ref['mapping']] == list(range(len(turns)))
            texts = [json.dumps({k: str(t.get(k) or '') for k in ('content', 'action', 'thought') if t.get(k)}, ensure_ascii=False, sort_keys=True) for t in turns]
            tokens = [len(tokenizer(text, add_special_tokens=True, truncation=False)['input_ids']) for text in texts]
            raw = records[tid]
            assert raw['content'].dtype == raw['agent'].dtype == torch.float32
            assert tuple(raw['content'].shape) == (len(turns), 128) and tuple(raw['agent'].shape) == (len(turns), 32)
            assert torch.isfinite(raw['content']).all() and torch.isfinite(raw['agent']).all()
            record, geo = geometry_fn(sample, raw, helper, events, torch, np)
            for name in ('raw_structure', 'paired_partner', 'paired_valid'):
                assert torch.equal(record[name], raw[name]), ('CACHED_GEOMETRY_DRIFT', tid, name)
            for got, old in zip(record['adjacency'], raw['adjacency']):
                assert all(torch.equal(a, b) for a, b in zip(got, old)), ('CACHED_ADJACENCY_DRIFT', tid)
            if 'texts_sha256' in row:
                assert digest(texts) == row['texts_sha256'] or hashlib.sha256(json.dumps(texts, ensure_ascii=False).encode()).hexdigest() == row['texts_sha256']
            data[tid] = record
            geo_rows[tid] = geo
            provider[tid] = {'tensor': str(directory / tensor_name), 'tensor_sha256': tensor_sha, 'producer': str(directory / producer_name), 'receipt': str(directory / receipt_name), 'encoder_identity': str(directory / encoder_name)}
            feature_rows.append({'task_id': tid, 'input_turns_sha256': turns_sha, 'public_sample_sha256': digest(sample), 'texts_sha256': digest(texts), 'anonymous_actor_mapping': {'unique_roles': ['role_0'], 'first_seen_role_order': ['role_0']},
                                 'original_ordinal_mapping': ref['mapping'], 'mapping_digest': digest(ref['mapping']), 'provider': provider[tid], 'exact_public_turns_match': True, 'cached_geometry_equals_rebuilt_pure_geometry': True,
                                 'input_tokens_before_truncation': tokens, 'truncated_steps': [i for i, t in enumerate(tokens) if t > 8192], 'max_length': 8192, 'new_encoder_forward_batches': 0})
    assert set(data) == set(ids), ('MISSING_EXACT_RAW_FEATURES', sorted(set(ids) - set(data)))
    feature_path = E / 'features/features257.pt'
    feature_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({'records': data, 'no_labels_or_outcomes': True, 'public_input_SHA256': sha(P224 / 'data/public_inputs.jsonl')}, feature_path)
    feature_sha = bind(feature_path)
    save('FEATURE_RECEIPT257.json', {'at_utc': now(), 'rows': sorted(feature_rows, key=lambda r: ids.index(r['task_id'])), 'feature_sha256': feature_sha,
                                   'new_encoder_forward_batches': 0, 'new_local_tokenizer_text_checks': sum(len(samples[t]['turns']) for t in ids), 'feature_prepare_seconds': time.monotonic() - feature_begin,
                                   'encoder_revision': REVISION, 'encoder_files': bound['model_files_sha256'], 'raw_tensor_new_model_loading_permitted': True})
    save('MECHANISM_GEOMETRY257.json', {'at_utc': now(), 'task_order': ids, 'rows': geo_rows, 'total_valid_pairs': sum(r['valid_pair_count'] for r in geo_rows.values()),
                                      'time_role_equal_task_count': sum(r['pairwise_overlap']['temporal__same_role']['exactly_equal'] for r in geo_rows.values())})
    event('EXACT_FEATURES_READY', tasks=len(data), new_encoder_forwards=0, new_tokenizer_checks=sum(len(samples[t]['turns']) for t in ids))
    for name in ('context_models', 'original_models', 'owned_exp130_model', 'stepfinder_model'):
        origin = P153 / ('context_models.py' if name == 'context_models' else 'sources/' + name + '.py')
        assert bind(E / 'sources' / (name + '.py')) == bind(origin)
    model_records = []
    for r in assets['source3_checkpoints']:
        bind(r['record_path'], r['record_sha256'])
        bind(r['checkpoint'], r['checkpoint_sha256'])
        model_records.append({'method': 'SOURCE3', 'seed': r['seed'], 'outer': None, 'selected_epoch': r['selected_epoch'], 'path': r['checkpoint'], 'sha256': r['checkpoint_sha256'], 'training_identity': r})
    for r in assets['SF_source_inner_validation_selected_checkpoints']:
        assert r['chosen_preset'] == 'SF_ALG_PAPER50'
        bind(r['checkpoint']['path'], r['checkpoint']['sha256'])
        model_records.append({'method': 'SF_ALG50', 'seed': r['seed'], 'outer': None, 'selected_epoch': r['epoch'], 'path': r['checkpoint']['path'], 'sha256': r['checkpoint']['sha256'], 'training_identity': r})
    for r in assets['AF15_model_refs']:
        bind(r['checkpoint']['path'], r['checkpoint']['SHA256'])
        model_records.append({'method': 'AF15', 'seed': r['seed'], 'outer': r['outer'], 'selected_epoch': r['epoch'], 'path': r['checkpoint']['path'], 'sha256': r['checkpoint']['SHA256'], 'training_identity': r})
    assert len(model_records) == 21
    bind(P158 / 'validation_selection_decisions.json', 'eadd99ba97cff937c7e13cc5540ec4650e7d0a1f4b5a03bd734cf91b86105816')
    save('PRE_FORWARD_SOURCE_INPUT_SEAL257.json', {'at_utc': now(), 'protocol_sha256': protocol_sha, 'feature_sha256': feature_sha, 'models': model_records, 'files': dict(IDENTITIES), 'before_any_ranker_forward': True})
    models = models_scoped()
    models.seed_all(0)
    model_outputs, model_metrics = {}, []
    forward_count = 0
    for r in model_records:
        began = time.monotonic()
        ck = torch.load(r['path'], map_location='cpu', weights_only=False)
        scaler = ck['scaler_mean'], ck['scaler_std']
        assert tuple(scaler[0].shape) == tuple(scaler[1].shape) == (23,)
        if r['method'] == 'SF_ALG50':
            model = models.original.StepFinder(**protocol['SF_explicit_config'])
            assert (model.asi.alpha, model.scoring.beta, model.scoring.gamma, list(model.scoring.scales)) == (.1, .9, .4, [1, 2])
            arm = 'SF_REF'
        else:
            model = models.create('AB_GLOBAL')
            arm = 'AB_GLOBAL'
        model.load_state_dict(ck['state_dict'], strict=True)
        model.eval()
        assert sum(p.numel() for p in model.parameters()) == (277633 if r['method'] == 'SF_ALG50' else 337457)
        out = {}
        with torch.inference_mode():
            for members in batches:
                batch = models.collate(members, data, scaler, torch.device('cpu'))
                scores, _ = models.forward(model, arm, batch)
                forward_count += 1
                for tid, score in zip(members, scores):
                    out[tid] = {**pack(torch.softmax(score.cpu(), 0).tolist()), 'logits': score.cpu().tolist()}
        key = r['method'] + '/' + str(r['seed']) + ('' if r['outer'] is None else '_' + str(r['outer']))
        model_outputs[key] = out
        tensor_hash = lambda t: hashlib.sha256(t.detach().cpu().contiguous().numpy().tobytes()).hexdigest()
        info = {**r, 'key': key, 'scaler_mean_bytes_sha256': tensor_hash(scaler[0]), 'scaler_std_bytes_sha256': tensor_hash(scaler[1]),
                'parameter_count': sum(p.numel() for p in model.parameters()), 'elapsed_seconds': time.monotonic() - began, 'forward_batches': 2, 'task_outputs': 18,
                'process_RSS_bytes': process.memory_info().rss if process else None}
        model_metrics.append(info)
        save('ranking/' + key + '.json', {'model': info, 'batches': protocol['batches'], 'predictions': out})
        event('REAL_MODEL_FORWARD_COMPLETE', method=r['method'], seed=r['seed'], outer=r['outer'], batches=forward_count, outputs=forward_count * 9, seconds=info['elapsed_seconds'])
        del ck, model, batch, scores
        gc.collect()
    def average(group):
        return {tid: pack(np.mean([o[tid]['probabilities'] for o in group], axis=0, dtype=np.float64).tolist()) for tid in ids}
    ensembles, seed_ensembles = {}, {}
    for method in ('SOURCE3', 'SF_ALG50', 'AF15'):
        records = [r for r in model_records if r['method'] == method]
        seed_ensembles[method] = {}
        for seed in sorted(set(r['seed'] for r in records)):
            group = [model_outputs[method + '/' + str(seed) + ('' if r['outer'] is None else '_' + str(r['outer']))] for r in records if r['seed'] == seed]
            seed_ensembles[method][str(seed)] = average(group)
        ensembles[method] = average(list(seed_ensembles[method].values()))
        save('ranking/' + method + '/ensemble.json', {'predictions': ensembles[method], 'seed_ensembles': seed_ensembles[method], 'same_fixed_batches': protocol['batches'], 'new_inference': True})
    for tid in ids:
        for method in ensembles:
            pred = ensembles[method][tid]
            save('ranking/plans/' + tid + '/' + method + '.json', {'task_id': tid, 'method': method, 'complete_original_ordinal_order': pred['order'], 'probabilities': pred['probabilities'],
                 'input_turns_sha256': refs[tid]['input_turns_sha256'], 'mapping_digest': digest(refs[tid]['mapping']), 'protocol_sha256': protocol_sha, 'feature_sha256': feature_sha,
                 'new_real_inference': True, 'source': {'path': str(E / 'ranking' / method / 'ensemble.json'), 'sha256': sha(E / 'ranking' / method / 'ensemble.json')}})
    evidence, opportunity_rows, eligible = {}, [], []
    comparisons = [('SOURCE3', m) for m in ('SF_ALG50', 'AF15', 'REVERSE', 'RANDOM')]
    for tid in ids:
        ref = refs[tid]
        candidates, skipped, edit_binding = legal_evidence(ref, contracts[tid])
        orders = {m: ensembles[m][tid]['order'] for m in ensembles}
        orders['REVERSE'] = list(reversed(range(len(ref['mapping']))))
        seed_text = 'Exp178|randomorder|' + tid
        seed_hex = hashlib.sha256(seed_text.encode()).hexdigest()
        orders['RANDOM'] = list(range(len(ref['mapping'])))
        random.Random(int(seed_hex, 16)).shuffle(orders['RANDOM'])
        legal = {m: ordered_legal(order, ref['mapping'], candidates) for m, order in orders.items()}
        prefixes = {m: [r['call_id'] for r in rows[:3]] for m, rows in legal.items()}
        pair_stats = {}
        for left, right in comparisons:
            left_ids, right_ids = [e['call_id'] for e in legal[left]], [e['call_id'] for e in legal[right]]
            pair_stats[right] = {'full_order_equal': orders[left] == orders[right], 'legal_call_order_equal': left_ids == right_ids,
                                'prefix3_equal': prefixes[left] == prefixes[right], 'full_first_divergence_one_based': first_divergence(orders[left], orders[right]),
                                'legal_first_divergence_one_based': first_divergence(left_ids, right_ids), 'prefix3_first_divergence_one_based': first_divergence(prefixes[left], prefixes[right]),
                                'prefix1_equal': prefixes[left][:1] == prefixes[right][:1], 'prefix2_equal': prefixes[left][:2] == prefixes[right][:2]}
        relevant = len(candidates) >= 2 and prefixes['SOURCE3'] != prefixes['SF_ALG50']
        if relevant:
            eligible.append(tid)
        evidence[tid] = {'original_plan_slot': qualification[tid]['original_plan_slot'], 'candidate_count': len(candidates), 'legal_business_path_count': len(contracts[tid]['c0_business_paths_sha256']),
                         'legal_changed_edit_bindings': list(candidates.values()), 'skipped': skipped, 'visible_edits': edit_binding, 'complete_original_ordinal_orders': orders,
                         'all_legal_edit_orders': legal, 'progressive_prefix_call_ids': {m: [p[:i] for i in (1, 2, 3)] for m, p in prefixes.items()}, 'comparison_vs_source3': pair_stats,
                         'SF_intervention_eligible': relevant, 'random_seed_text': seed_text, 'random_seed_sha256': seed_hex}
        opportunity_rows.append({'task_id': tid, 'original_plan_slot': qualification[tid]['original_plan_slot'], 'steps': len(ref['mapping']), 'legal_candidate_count': len(candidates),
                                 'source3_sf_prefix3_different': relevant, **{m.lower() + '_full_order': canonical(orders[m]) for m in orders},
                                 **{m.lower() + '_legal_call_order': canonical([e['call_id'] for e in legal[m]]) for m in orders},
                                 **{m.lower() + '_prefix3_call_ids': canonical(prefixes[m]) for m in orders},
                                 **{m.lower() + '_full_order_equal_source3': pair_stats[m]['full_order_equal'] for m in pair_stats},
                                 **{m.lower() + '_legal_order_equal_source3': pair_stats[m]['legal_call_order_equal'] for m in pair_stats},
                                 **{m.lower() + '_prefix3_equal_source3': pair_stats[m]['prefix3_equal'] for m in pair_stats},
                                 **{m.lower() + '_legal_first_divergence_one_based': pair_stats[m]['legal_first_divergence_one_based'] for m in pair_stats},
                                 **{m.lower() + '_prefix3_first_divergence_one_based': pair_stats[m]['prefix3_first_divergence_one_based'] for m in pair_stats}})
    audit = {'schema': 'EXP257-ranking-legal-intervention-opportunities/1', 'at_utc': now(), 'task_order': ids, 'rows': evidence,
             'all18_real_source3_SF_AF15_outputs': True, 'eligible_in_original_order': eligible, 'selected_first_two': eligible[:2], 'selection_only_public_order_and_legality': True,
             'source3_sf_full_order_different_tasks': sum(not r['comparison_vs_source3']['SF_ALG50']['full_order_equal'] for r in evidence.values()),
             'source3_sf_legal_order_different_tasks': sum(not r['comparison_vs_source3']['SF_ALG50']['legal_call_order_equal'] for r in evidence.values()),
             'source3_sf_prefix3_different_tasks': sum(not r['comparison_vs_source3']['SF_ALG50']['prefix3_equal'] for r in evidence.values()),
             'source3_sf_eligible_tasks': len(eligible), 'noncausal_development_audit': True, 'no_accuracy_without_gold': True}
    save('RANKING_INTERVENTION_OPPORTUNITIES.json', audit)
    with (E / 'RANKING_INTERVENTION_OPPORTUNITIES.tsv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(opportunity_rows[0]), delimiter='\t')
        writer.writeheader()
        writer.writerows(opportunity_rows)
    for path, expected in IDENTITIES.items():
        assert sha(path) == expected, ('END_SOURCE_DRIFT', path)
    assert sha(E / 'PROTOCOL257.json') == protocol_sha
    release = {'schema': 'EXP257-real-source3-strongSF-AF15-release/1', 'status': 'COMPLETE_REAL_INFERENCE_RELEASE', 'at_utc': now(), 'pid': os.getpid(),
               'task_order': ids, 'original_plan21_order': original, 'task_count': 18, 'protocol_path': str(E / 'PROTOCOL257.json'), 'protocol_sha256': protocol_sha,
               'feature_sha256': feature_sha, 'feature_receipt_sha256': sha(E / 'FEATURE_RECEIPT257.json'), 'models': model_metrics, 'batches': protocol['batches'], 'runtime': runtime,
               'model_outputs': model_outputs, 'seed_ensembles': seed_ensembles, 'ensembles': ensembles, 'geometry_sha256': sha(E / 'MECHANISM_GEOMETRY257.json'),
               'intervention_audit_path': str(E / 'RANKING_INTERVENTION_OPPORTUNITIES.json'), 'intervention_audit_sha256': sha(E / 'RANKING_INTERVENTION_OPPORTUNITIES.json'),
               'selected_first_two': eligible[:2], 'real_ranker_loads': 21, 'real_forward_batches': forward_count, 'real_per_model_task_outputs': 378,
               'new_encoder_forwards': 0, 'elapsed_seconds': time.monotonic() - start, 'source_SHA256': dict(IDENTITIES), 'new_model_POST_native_training_Gold_downloads': 0,
               'scientific_scope': 'public ranking deployment and legal edit opportunity audit on exposed development tasks; no RQ1 accuracy or recovery performance claim'}
    save('RQ1_SOURCE3_RELEASE.json', release)
    event('REAL_RELEASE_COMPLETE', forwards=forward_count, tasks=18, eligible=eligible, selected=eligible[:2], elapsed_seconds=release['elapsed_seconds'], release_sha256=sha(E / 'RQ1_SOURCE3_RELEASE.json'))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        event('ERROR', type=type(exc).__name__, error=str(exc))
        raise

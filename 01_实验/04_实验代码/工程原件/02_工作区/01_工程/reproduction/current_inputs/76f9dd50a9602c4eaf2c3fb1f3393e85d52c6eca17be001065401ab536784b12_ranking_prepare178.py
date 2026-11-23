"""Prepare complete original-ordinal G153 AF AB_GLOBAL plans before recovery.

Old exact Exp166 plans are reused only after public input and model identity
checks. Other qualified inputs use the same15 frozen checkpoints. No labels,
training, paid generation, native tests, or recovery outcomes are accessed.
"""
import datetime
import gc
import hashlib
import importlib.util
import json
import os
import sys
import time
import types
from pathlib import Path

os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_DATASETS_OFFLINE'] = '1'
sys.dont_write_bytecode = True
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

E = Path(__file__).resolve().parent
ROOT = E.parents[3]
OLD = ROOT / '工作区/1007-exp166-four-paper-baselines/实验/实验166_四项正式论文基线快速整体验证'
M153 = ROOT / '工作区/1007-exp153-global-context/实验/实验153_候选条件全轨迹上下文'
QROOT = ROOT / '工作区/0922-exp124-ranking-baselines/third_party/Qwen3-Embedding-0.6B'
Q3 = ROOT / '工作区/0922-exp124-ranking-baselines/third_party/StepFinder/Q3Emb.py'
STRUCTURE = ROOT / '实验/实验112_RQ1时序交互依赖完整排序/runner.py'
EVENTS = ROOT / '工作区/1006-exp133-state-action/实验/实验133_状态动作选择性核验/method.py'
SEEDS = (20260816, 20260817, 20260818)
REVISION = '97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3'


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def lines(path):
    return [json.loads(line) for line in Path(path).read_text('utf-8-sig').splitlines() if line.strip()]


def save(path, value):
    path = Path(path).resolve()
    if not any(path.is_relative_to((E / branch).resolve()) for branch in ('ranking', 'features')):
        raise ValueError('EXP178_RANKPREP_WRITE_SCOPE')
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.' + str(os.getpid()) + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', 'utf-8')
    os.replace(tmp, path)


def event(phase, **extra):
    value = {'at_utc': now(), 'phase': phase, 'pid': os.getpid(), **extra}
    save(E / 'ranking/preparation_checkpoint.json', value)
    print(canonical(value), flush=True)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def turns_sha(turns):
    # Byte-identical legacy input identity; separate from canonical mapping digest.
    return hashlib.sha256(json.dumps(turns, sort_keys=True).encode('utf-8')).hexdigest()


def texts_of(turns):
    return [json.dumps({k: str(t.get(k) or '') for k in ('content', 'action', 'thought') if t.get(k)},
                       ensure_ascii=False, sort_keys=True) for t in turns]


def model_records():
    # Read manifest identity fields only; no history, metrics or evaluation labels.
    manifest = read(M153 / 'training/all_models_sealed.json')
    records = [{k: row[k] for k in ('suite', 'arm', 'seed', 'outer', 'checkpoint', 'checkpoint_sha256')}
               for row in manifest['models'] if row['suite'] == 'AF' and row['arm'] == 'AB_GLOBAL']
    assert len(records) == 15
    assert {(r['seed'], r['outer']) for r in records} == {(s, o) for s in SEEDS for o in range(5)}
    records.sort(key=lambda r: (r['seed'], r['outer']))
    old_seal = read(OLD / 'ranking_input_seal.json')
    old_records = [{k: row[k] for k in records[0]} for row in old_seal['models']
                   if row['suite'] == 'AF' and row['arm'] == 'AB_GLOBAL']
    assert sorted(old_records, key=lambda r: (r['seed'], r['outer'])) == records
    for path in (M153 / 'context_models.py', M153 / 'common.py'):
        assert old_seal['inputs'][str(path)] == sha(path), 'G153_SOURCE_DRIFT'
    for record in records:
        assert sha(record['checkpoint']) == record['checkpoint_sha256'], 'G153_CHECKPOINT_DRIFT'
    return records


def models_scoped():
    # Scoped aliases are restored in this standalone process, never touch a
    # runner's Env/common module or write any imported legacy output directory.
    names = ('common', 'original_models', 'owned_exp130_model', 'stepfinder_model')
    previous = {name: sys.modules.get(name) for name in names}
    previous_path = sys.path.copy()
    try:
        shim = types.ModuleType('exp178_rankprep_common_scope')
        shim.E = M153
        shim.CONTEXT_ARMS = ('AB_GLOBAL', 'AB_LOCAL', 'AB_STATIC', 'AB_VALUE_PERM')
        sys.modules['common'] = shim
        sys.path.insert(0, str(M153 / 'sources'))
        for name in names[2:]:
            sys.modules[name] = module('exp178_rankprep_' + name, M153 / 'sources' / (name + '.py'))
        sys.modules['original_models'] = module('exp178_rankprep_original_models', M153 / 'sources/original_models.py')
        result = module('exp178_rankprep_context_models', M153 / 'context_models.py')
    finally:
        sys.path[:] = previous_path
        for name, old in previous.items():
            if old is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old
    return result


def feature_geometry(sample, content, agent, helper, events, torch, np):
    turns = sample['turns']
    n = len(turns)
    structure = np.asarray([helper._h0_vector({'turns': turns}, i) for i in range(n)], dtype=np.float32)
    neighbors = helper._build_adjacency({'turns': turns})
    adjacency = []
    for rel in ('temporal', 'same_role', 'same_full_shape_signature', 'same_nonempty_action_shape'):
        ix = np.zeros((n, 2), dtype=np.int64)
        mask = np.zeros((n, 2), dtype=np.float32)
        for i, ns in enumerate(neighbors[rel]):
            assert len(ns) <= 2
            ix[i, :len(ns)] = ns
            mask[i, :len(ns)] = 1
        adjacency.append((torch.from_numpy(ix), torch.from_numpy(mask)))
    coordinates = [{'original_step_id': t['source_message_index'], 'source_channel_role': 'assistant'}
                   for t in turns]
    packet = events.representation({'turns': turns, 'task': sample['task'], 'coordinate_map': coordinates})
    partner = torch.zeros(n, 2, dtype=torch.long)
    valid = torch.zeros(n, 2)
    for link in packet['observed_state_action_links']:
        state, action = link['decision_state'], link['ensuing_action']
        partner[state, 0] = action
        valid[state, 0] = 1
        partner[action, 1] = state
        valid[action, 1] = 1
    data = {'content': torch.from_numpy(content), 'agent': torch.from_numpy(agent),
            'raw_structure': torch.from_numpy(structure), 'adjacency': adjacency,
            'paired_partner': partner, 'paired_valid': valid}
    return data, packet['observed_state_action_links']


def pack(probabilities):
    assert probabilities and all(isinstance(v, (int, float)) for v in probabilities)
    assert all(__import__('math').isfinite(v) and v >= 0 for v in probabilities)
    assert abs(sum(probabilities) - 1) < 1e-5
    order = sorted(range(len(probabilities)), key=lambda i: (-probabilities[i], i))
    return {'probabilities': probabilities, 'order': order, 'chosen_step': order[0],
            'valid': True, 'native_complete_ranking': True}


def main():
    start = time.monotonic()
    import numpy as np
    import torch
    torch.set_num_threads(4)
    bindings_path = E / 'data/selected_task_bindings.json'
    public_path = E / 'data/public_inputs.jsonl'
    bindings = read(bindings_path)
    refs = bindings['tasks']
    samples = {row['sample_id']: row for row in lines(public_path)}
    assert len(refs) == len(samples) and {r['task_id'] for r in refs} == set(samples)
    assert 1 <= len(refs) <= 14
    binding_inputs = {str(bindings_path): sha(bindings_path), str(public_path): sha(public_path)}
    if (E / 'data/candidate_binding_registry.json').exists():
        binding_inputs[str(E / 'data/candidate_binding_registry.json')] = sha(E / 'data/candidate_binding_registry.json')
        assert bindings.get('candidate_registry_sha256') == binding_inputs[str(E / 'data/candidate_binding_registry.json')]
    records = model_records()
    sources = {str(path): sha(path) for path in (
        Path(__file__), OLD / 'rank166.py', OLD / 'ranking_input_seal.json',
        OLD / 'ranking/AB_GLOBAL/ensemble.json', OLD / 'ranking/all_predictions_sealed.json',
        M153 / 'training/all_models_sealed.json', M153 / 'context_models.py', M153 / 'common.py',
        M153 / 'sources/original_models.py', M153 / 'sources/owned_exp130_model.py',
        M153 / 'sources/stepfinder_model.py', STRUCTURE, EVENTS, Q3)}
    model_identity = digest(records)
    old_refs = {r['task_id']: r for r in read(OLD / 'data/selected_task_bindings.json')['tasks']}
    old_samples = {r['sample_id']: r for r in lines(OLD / 'data/public_inputs.jsonl')}
    old_ensemble_path = OLD / 'ranking/AB_GLOBAL/ensemble.json'
    old_ensemble = read(old_ensemble_path)['predictions']
    old_predictions_seal = read(OLD / 'ranking/all_predictions_sealed.json')
    assert old_predictions_seal['files'][str(old_ensemble_path)] == sha(old_ensemble_path)
    rows, predictions, new_refs = [], {}, []
    old_read_start = time.monotonic()
    for ref in sorted(refs, key=lambda r: r['task_id']):
        tid = ref['task_id']
        sample = samples[tid]
        assert not any(k in sample for k in ('gold', 'mistake_step', 'mistake_agent', 'answer', 'ground_truth'))
        assert turns_sha(sample['turns']) == ref['input_turns_sha256']
        assert len(sample['turns']) == len(ref['mapping']) and sorted(r['step'] for r in ref['mapping']) == list(range(len(sample['turns'])))
        assert [t['source_message_index'] for t in sample['turns']] == [r['message_index'] for r in ref['mapping']]
        row = {'task_id': tid, 'steps': len(sample['turns']), 'input_turns_sha256': ref['input_turns_sha256'],
               'mapping_digest': digest(ref['mapping']), 'checkpoint_manifest_digest': model_identity}
        plan_path = OLD / 'frozen_plans' / tid / 'OURS_G153_VBR.json'
        if plan_path.exists() and tid in old_refs and tid in old_ensemble:
            old_ref = old_refs[tid]
            assert sample['turns'] == old_samples[tid]['turns'], 'OLD_G153_INPUT_TURNS_CHANGED'
            assert ref['input_turns_sha256'] == old_ref['input_turns_sha256']
            assert ref['mapping'] == old_ref['mapping'], 'OLD_G153_ORDINAL_MAPPING_CHANGED'
            prefix = Path(ref['task_path']) / 'visible/source_prefix.json'
            old_prefix = Path(old_ref['task_path']) / 'visible/source_prefix.json'
            assert sha(prefix) == sha(old_prefix), 'OLD_G153_SOURCE_PREFIX_CHANGED'
            plan = read(plan_path)
            assert plan['method'] == 'OURS_G153_VBR' and plan['source']['all15_models_averaged'] is True
            assert plan['source']['sha256'] == sha(old_ensemble_path)
            pred = pack(old_ensemble[tid]['probabilities'])
            assert pred['order'] == old_ensemble[tid]['order'] == plan['complete_original_ordinal_order']
            assert sorted(pred['order']) == list(range(len(sample['turns'])))
            predictions[tid] = pred
            row.update(provenance='EXACT_EXP166_G153_AF_AB_GLOBAL_CACHED_PLAN',
                       cached_plan_path=str(plan_path), cached_plan_sha256=sha(plan_path),
                       cached_ensemble_path=str(old_ensemble_path), cached_ensemble_sha256=sha(old_ensemble_path),
                       source_prefix_sha256=sha(prefix), new_ranker_forwards=0, new_encoder_forwards=0)
        else:
            new_refs.append(ref)
            row.update(provenance='NEW_SAME_G153_AF_AB_GLOBAL15_CHECKPOINT_FORWARD',
                       new_ranker_forwards=15, new_encoder_forwards=None)
        rows.append(row)
    old_read_seconds = time.monotonic() - old_read_start
    event('INPUT_AND_G153_IDENTITIES_PASS', total_tasks=len(refs), cached_tasks=len(refs)-len(new_refs),
          new_forward_tasks=[r['task_id'] for r in new_refs], cached_read_seconds=old_read_seconds)
    helper = module('exp178_rankprep_original_structure', STRUCTURE) if new_refs else None
    events = module('exp178_rankprep_original_state_action', EVENTS) if new_refs else None
    data, feature_rows, encoder, role_cache, content_cache = {}, [], None, {}, {}
    encoder_batches = encoder_texts = 0
    encoder_identity = None
    cpu_fallback_used = False

    def encode_fresh(texts, roles):
        nonlocal encoder, encoder_batches, encoder_texts, encoder_identity, cpu_fallback_used
        if encoder is None:
            q3 = module('exp178_rankprep_original_qwen', Q3)
            bound = read(ROOT / '工作区/0922-exp124-ranking-baselines/实验/实验124_责任排序强基线与外部迁移/results/preclaim_binding.json')
            for f, h in bound['model_files_sha256'].items():
                assert sha(QROOT / f) == h
            use_cuda = torch.cuda.is_available()
            try:
                encoder = q3.Qwen3Embedding(str(QROOT), use_cuda=use_cuda, max_length=8192)
            except torch.cuda.OutOfMemoryError:
                cpu_fallback_used = True
                gc.collect()
                torch.cuda.empty_cache()
                use_cuda = False
                encoder = q3.Qwen3Embedding(str(QROOT), use_cuda=False, max_length=8192)
            encoder_identity = {'revision': q3.DEFAULT_MODEL_REVISION, 'files': bound['model_files_sha256'],
                                'max_length': 8192, 'batch_size': 1, 'output_dtype': 'float32',
                                'model_dtype': str(next(encoder.model.parameters()).dtype),
                                'device': str(encoder.model.device), 'cpu_fallback_used': cpu_fallback_used}
            save(E / 'features/encoder_identity.json', encoder_identity)
        result_content, result_agent, tokens = [], [], []

        def actual_encode(text, dim):
            nonlocal encoder, cpu_fallback_used, encoder_batches, encoder_texts
            try:
                value = encoder.encode([text], dim=dim).float().cpu().numpy()[0]
            except torch.cuda.OutOfMemoryError:
                if cpu_fallback_used:
                    raise
                cpu_fallback_used = True
                encoder.model = encoder.model.cpu()
                gc.collect()
                torch.cuda.empty_cache()
                value = encoder.encode([text], dim=dim).float().cpu().numpy()[0]
                encoder_identity.update(device='cpu', cpu_fallback_used=True)
                save(E / 'features/encoder_identity.json', encoder_identity)
            encoder_batches += 1
            encoder_texts += 1
            return value

        for text, role in zip(texts, roles):
            tokens.append(len(encoder.tokenizer(text, add_special_tokens=True)['input_ids']))
            if role not in role_cache:
                role_cache[role] = actual_encode(role, 32)
            key = hashlib.sha256(text.encode('utf-8')).hexdigest()
            if key not in content_cache:
                content_cache[key] = actual_encode(text, 128)
            result_content.append(content_cache[key])
            result_agent.append(role_cache[role])
        return np.asarray(result_content, dtype=np.float32), np.asarray(result_agent, dtype=np.float32), tokens

    for ref in new_refs:
        began = time.monotonic()
        tid = ref['task_id']
        sample = samples[tid]
        turns = sample['turns']
        texts = texts_of(turns)
        text_sha = hashlib.sha256(json.dumps(texts, ensure_ascii=False).encode('utf-8')).hexdigest()
        cache_ref = ref.get('raw_encoding_cache')
        fresh_before = encoder_batches
        historic = {}
        if cache_ref and Path(cache_ref['path']).exists():
            assert sha(cache_ref['path']) == cache_ref['sha256'], 'RAW_ENCODING_CACHE_SHA_DRIFT'
            producer = cache_ref['producer_encoding']
            assert producer['saved_feature_sha256'] == cache_ref['sha256']
            assert producer['content_texts_sha256'] == text_sha, 'RAW_ENCODING_TEXT_REPRESENTATION_DRIFT'
            assert producer['max_length'] == 8192 and cache_ref['qwen_revision'] == REVISION
            with np.load(cache_ref['path'], allow_pickle=False) as cached:
                assert str(cached['input_sha']) == ref['input_turns_sha256']
                content, agent = cached['content'].copy(), cached['agent'].copy()
            assert content.dtype == agent.dtype == np.dtype('float32')
            rawtokens = producer['input_tokens_per_step_before_truncation']
            historic = {'cache_path': cache_ref['path'], 'cache_sha256': cache_ref['sha256'],
                        'encoder_revision': cache_ref['qwen_revision'], 'actual_historic_encoder': producer,
                        'new_encoder_forwards': 0, 'representation': 'Original raw content128/role32 float32 before AB L2'}
            feature_source = 'SHA_AND_EXACT_TEXT_BOUND_RAW_ENCODING_CACHE'
        else:
            content, agent, rawtokens = encode_fresh(texts, [t['role'] for t in turns])
            feature_source = 'NEW_ORIGINAL_RAW_ENCODER_FORWARD'
        assert content.shape == (len(turns), 128) and agent.shape == (len(turns), 32)
        assert np.isfinite(content).all() and np.isfinite(agent).all()
        data[tid], links = feature_geometry(sample, content, agent, helper, events, torch, np)
        feature_rows.append({'task_id': tid, 'steps': len(turns), 'input_turns_sha256': ref['input_turns_sha256'],
                             'texts_sha256': text_sha, 'source': feature_source, **historic,
                             'input_tokens_before_truncation': rawtokens,
                             'truncated_steps': [i for i, n in enumerate(rawtokens) if n > 8192],
                             'new_encoder_forwards': encoder_batches - fresh_before,
                             'observed_state_action_links': links,
                             'feature_seconds': time.monotonic() - began})
        next(r for r in rows if r['task_id'] == tid)['new_encoder_forwards'] = encoder_batches - fresh_before
        event('FEATURE_TASK_READY', task_id=tid, source=feature_source, new_encoder_batches=encoder_batches)
    if encoder is not None:
        del encoder
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    feature_path = E / 'features/new_G153_exact_inputs.pt'
    feature_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({'records': data, 'no_labels_or_outcomes': True}, feature_path)
    save(E / 'features/preparation_receipt.json', {'at_utc': now(), 'status': 'PASS', 'rows': feature_rows,
                                                 'feature_file_sha256': sha(feature_path),
                                                 'new_encoder_forward_batches': encoder_batches,
                                                 'new_encoder_unique_texts': encoder_texts,
                                                 'encoder_identity': encoder_identity, 'paid_API_CNY': '0'})
    forward_files, forward_records = {}, []
    if new_refs:
        models = models_scoped()
        models.seed_all(0)
        new_ids = sorted(data)
        seed_outputs = []

        def ensemble(group):
            return {sid: pack(np.mean([v[sid]['probabilities'] for v in group], axis=0, dtype=np.float64).tolist())
                    for sid in new_ids}

        for seed in SEEDS:
            folds = []
            for outer in range(5):
                began = time.monotonic()
                record = next(r for r in records if (r['seed'], r['outer']) == (seed, outer))
                ck = torch.load(record['checkpoint'], map_location='cpu', weights_only=False)
                checkpoint_row = ck.get('row', {})
                assert all(checkpoint_row.get(k) == record[k] for k in ('suite', 'arm', 'seed', 'outer'))
                assert ck['scaler_mean'].shape == ck['scaler_std'].shape == (23,)
                assert bool(torch.isfinite(ck['scaler_mean']).all() and torch.isfinite(ck['scaler_std']).all())
                assert bool((ck['scaler_std'] > 0).all())
                model = models.create('AB_GLOBAL').cpu()
                model.load_state_dict(ck['state_dict'], strict=True)
                model.eval()
                with torch.no_grad():
                    batch = models.collate(new_ids, data, (ck['scaler_mean'], ck['scaler_std']), torch.device('cpu'))
                    scores, _ = models.forward(model, 'AB_GLOBAL', batch)
                    out = {sid: pack(torch.softmax(score.cpu(), 0).tolist()) for sid, score in zip(batch['ids'], scores)}
                path = E / 'ranking/AB_GLOBAL' / (str(seed) + '_' + str(outer) + '.json')
                row = {'seed': seed, 'outer': outer, 'checkpoint': record['checkpoint'],
                       'checkpoint_sha256': record['checkpoint_sha256'], 'device': 'cpu',
                       'same_selected_sorted_task_batch': new_ids, 'forward_seconds': time.monotonic() - began}
                save(path, {'predictions': out, **row})
                forward_files[str(path)] = sha(path)
                forward_records.append(row)
                folds.append(out)
                event('FROZEN_G153_FORWARD', seed=seed, outer=outer, completed_forward_batches=len(forward_records))
                del model, batch, scores, ck
                gc.collect()
            out = ensemble(folds)
            path = E / 'ranking/AB_GLOBAL' / (str(seed) + '.json')
            save(path, {'predictions': out, 'all5_folds': True})
            forward_files[str(path)] = sha(path)
            seed_outputs.append(out)
        predictions.update(ensemble(seed_outputs))
    merged_path = E / 'ranking/AB_GLOBAL/ensemble.json'
    save(merged_path, {'predictions': predictions, 'all3_seeds': True,
                       'same_G153_AF_AB_GLOBAL15_models': True, 'checkpoint_manifest_digest': model_identity})
    plans = {}
    for row in rows:
        tid = row['task_id']
        pred = predictions[tid]
        assert sorted(pred['order']) == list(range(row['steps']))
        path = E / 'ranking/plans' / tid / 'OURS_G153_VBR.json'
        save(path, {'task_id': tid, 'method': 'OURS_G153_VBR', 'diagnostic_pending': False,
                    'complete_original_ordinal_order': pred['order'], 'probabilities': pred['probabilities'],
                    'chosen_step': pred['chosen_step'], 'native_complete_ranking': True,
                    'source': {'path': str(merged_path), 'sha256': sha(merged_path), 'all15_models_averaged': True},
                    'input_turns_sha256': row['input_turns_sha256'], 'mapping_digest': row['mapping_digest'],
                    'checkpoint_manifest_digest': model_identity, 'checkpoint_bindings': records,
                    'provenance': row})
        plans[tid] = {'path': str(path), 'sha256': sha(path), 'steps': row['steps'],
                      'input_turns_sha256': row['input_turns_sha256'], 'mapping_digest': row['mapping_digest']}
    for path, expected in {**binding_inputs, **sources}.items():
        assert sha(path) == expected, 'PREPARATION_SOURCE_OR_DATA_DRIFT:' + path
    for record in records:
        assert sha(record['checkpoint']) == record['checkpoint_sha256']
    save(E / 'ranking/all_G153_plans_sealed.json', {
        'at_utc': now(), 'status': 'READY', 'tasks': len(rows), 'plans': plans,
        'rows': rows, 'inputs': binding_inputs, 'sources': sources,
        'checkpoint_bindings': records, 'checkpoint_manifest_digest': model_identity,
        'new_ranker_forward_batches': len(forward_records),
        'new_ranker_task_outputs': len(forward_records) * len(new_refs),
        'forward_records': forward_records, 'forward_files': forward_files,
        'cached_G153_tasks': len(refs) - len(new_refs), 'cached_read_seconds': old_read_seconds,
        'new_encoder_forward_batches': encoder_batches, 'new_encoder_unique_texts': encoder_texts,
        'features_file': str(feature_path), 'features_sha256': sha(feature_path),
        'ensemble_file': str(merged_path), 'ensemble_sha256': sha(merged_path),
        'ranker_device': 'cpu', 'ranker_dtype': 'float32',
        'same_algorithm_source_and_checkpoints_as_cached166': True,
        'bitwise_CPU_CUDA_probability_equivalence_claimed': False,
        'new_training': 0, 'new_Gold_or_private_reads': 0, 'new_target_native': 0,
        'paid_API': 0, 'fees_CNY': '0', 'elapsed_seconds': time.monotonic() - start})
    event('ALL_G153_PLANS_READY', tasks=len(rows), new_ranker_forward_batches=len(forward_records),
          new_encoder_batches=encoder_batches, seconds=time.monotonic() - start)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        event('PREPARATION_UNKNOWN', error_type=type(exc).__name__, error=str(exc))
        raise

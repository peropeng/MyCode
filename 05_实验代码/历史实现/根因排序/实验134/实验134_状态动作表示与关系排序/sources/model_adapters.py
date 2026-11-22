"""Label-free Exp132 adapters for the two independent frozen semantic models.

No model, asset, dataset, or encoder is loaded on import. The producer invokes
these definitions only after the common protocol/source freeze. Old training
entry points and feature_construction.process_log are never imported or called.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import types

import numpy as np
import torch


DEFAULT_REPOSITORY_ROOT = 'D:/Code/毕设/graduate-thesis-experiments'
ENCODER_REVISION = '97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3'
MODEL_HASHES = {
    'ours_source': '81dbfa7503b61659d0faf12be132b00eddb770b23bfb4e77ccfcdc96e2118a44',
    'ours_checkpoint': '3b5ed6844bc502d4143700f9eb1ea7a0dba3d6b4fa00c41194b69aff41e94e58',
    'sf_source': '96ea4dce3a76a9a730d59c7aac1954c6d5f9f2d449c55c5e3b6d9092c00c0c5a',
    'sf_checkpoint': 'ac12e8905eb0337e082da8b4054ebb38a11b092f620f4f3e8353a5b57194aa08',
    'encoder_source': '6a6fa26c53d8b47d7bd851e0971960b540b59ea79ddc7300961872b3cd7d3189',
    'structure88_source': 'e6cc523e9d1da8328face122b216492d130ab51eb2afe7b099d87dee9798ed54',
    'structure112_source': 'ab02c95823bdd6baaa5d3cf7c7d467fbcfaa8743788a91820b4de55be87dc9df',
}
ENCODER_FILE_HASHES = {
    'model.safetensors': '0437e45c94563b09e13cb7a64478fc406947a93cb34a7e05870fc8dcd48e23fd',
    'config.json': 'b5bf1f51fc45be473a54718cef92448d90a1be001bf9b9a44b8c7f10a19feaa9',
    'tokenizer.json': 'def76fb086971c7867b829c23a26261e38d9d74e02139253b38aeb9df8b4b50a',
    'tokenizer_config.json': '253153d0738ceb4c668d2eff957714dd2bea0b56de772a9fdccd96cbf517e6a0',
    'merges.txt': '8831e4f1a044471340f7c0a83d7bd71306a5b867e95fd870f74d0c5308a904d5',
    'vocab.json': 'ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910',
}
RELATIONS = ('temporal', 'same_role', 'same_full_shape_signature', 'same_nonempty_action_shape')
TURN_FIELDS = ('role', 'content', 'action', 'thought')


class AssetBindingError(RuntimeError):
    pass


def public_record(record):
    """Copy only the common public contract; mapping never enters neural input."""
    if not isinstance(record, dict) or type(record.get('sample_id')) not in (str, int):
        raise ValueError('public_record_requires_original_sample_id')
    if not isinstance(record.get('task'), str):
        raise ValueError('public_task_must_be_a_string')
    turns = record.get('turns')
    if not isinstance(turns, list) or not turns:
        raise ValueError('public_turns_must_be_a_nonempty_list')
    selected = []
    for turn in turns:
        if not isinstance(turn, dict):
            raise ValueError('each_public_turn_must_be_a_dictionary')
        fields = {key: turn.get(key, '') for key in TURN_FIELDS}
        if not all(isinstance(value, str) for value in fields.values()):
            raise ValueError('common_public_turn_fields_must_be_strings')
        selected.append(fields)
    step_map = record.get('original_step_map', record.get('coordinate_map'))
    if not isinstance(step_map, (list, dict)) or len(step_map) != len(selected):
        raise ValueError('original_step_map_must_align_with_all_public_turns')
    # Ensure a serializable opaque coordinate map, without copying any other fields.
    step_map = json.loads(json.dumps(step_map, ensure_ascii=False, allow_nan=False))
    return {'sample_id': record['sample_id'], 'task': record['task'],
            'turns': selected, 'original_step_map': step_map}


def public_hash(record):
    selected = public_record(record)
    payload = {'sample_id': selected['sample_id'], 'task': selected['task'], 'turns': selected['turns'],
               'original_step_map': selected['original_step_map']}
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()


def anonymous_public_turns(record):
    selected = public_record(record)
    role_map = {}
    turns = []
    for turn in selected['turns']:
        role = turn['role']
        if role not in role_map:
            role_map[role] = 'role_' + str(len(role_map))
        turns.append({**turn, 'role': role_map[role]})
    return turns


def embedding_text(turn):
    """Exact old Exp124 text_of projection; task and metadata are absent."""
    return json.dumps({key: str(turn.get(key) or '') for key in ('content', 'action', 'thought')
                       if turn.get(key)}, ensure_ascii=False, sort_keys=True)


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def default_assets(repository_root=DEFAULT_REPOSITORY_ROOT):
    root = Path(repository_root)
    old124 = root / '工作区/0922-exp124-ranking-baselines'
    old130 = root / '实验/实验130_语义多关系诊断改进'
    return {
        'ours_source': old130 / 'model.py',
        'ours_checkpoint': old130 / 'results/v2/checkpoints/semantic_graph/20260816_0.pt',
        'sf_source': old124 / 'third_party/StepFinder/model.py',
        'sf_checkpoint': old124 / 'third_party/checkpoints/20260816_0.pt',
        'encoder_source': old124 / 'third_party/StepFinder/Q3Emb.py',
        'structure88_source': root / '实验/实验88_责任桥_去错误词与长度资格/runner.py',
        'structure112_source': root / '实验/实验112_RQ1时序交互依赖完整排序/runner.py',
        'encoder_directory': old124 / 'third_party/Qwen3-Embedding-0.6B',
    }


def verify_asset_binding(assets):
    binding = {}
    for name, expected in MODEL_HASHES.items():
        path = Path(assets[name])
        if not path.is_file():
            raise AssetBindingError('missing_frozen_asset:' + name)
        actual = sha256_file(path)
        if actual != expected:
            raise AssetBindingError('frozen_asset_hash_mismatch:' + name)
        binding[name] = {'path': str(path), 'sha256': actual}
    directory = Path(assets['encoder_directory'])
    binding['encoder_files'] = {}
    for name, expected in ENCODER_FILE_HASHES.items():
        path = directory / name
        if not path.is_file() or sha256_file(path) != expected:
            raise AssetBindingError('frozen_encoder_hash_mismatch:' + name)
        binding['encoder_files'][name] = expected
    return binding


def _pure_old_helpers(path, function_names, constant_names, namespace):
    """Compile ONLY named public pure functions/constants, never old module imports."""
    tree = ast.parse(Path(path).read_text(encoding='utf-8-sig'))
    nodes = []
    found_functions, found_constants = set(), set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in function_names:
            nodes.append(node)
            found_functions.add(node.name)
        elif isinstance(node, ast.Assign):
            names = [target.id for target in node.targets if isinstance(target, ast.Name)]
            if len(names) == 1 and names[0] in constant_names:
                ast.literal_eval(node.value)  # Constants must be literal, without hidden calls.
                nodes.append(node)
                found_constants.add(names[0])
    if found_functions != set(function_names) or found_constants != set(constant_names):
        raise AssetBindingError('missing_frozen_public_helper_definition')
    future = ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0)
    module = ast.fix_missing_locations(ast.Module(body=[future, *nodes], type_ignores=[]))
    exec(compile(module, str(path) + ':public_helpers_only', 'exec'), namespace)
    return types.SimpleNamespace(**{name: namespace[name] for name in function_names | constant_names})


def load_public_structure_helpers(assets):
    base = {'json': json, 'hashlib': hashlib, 'Counter': Counter, 'defaultdict': defaultdict}
    old88 = _pure_old_helpers(
        assets['structure88_source'],
        {'_arity_bucket', '_shape', '_shape_depth', '_parse_shape', '_parsed_value', '_field_descriptor',
         'turn_structure', '_step_stats', '_local_score', '_tie_digest'},
        {'MAX_SHAPE_DEPTH', 'MAX_SHAPE_CHILDREN', 'E2_LOCAL_WEIGHTS'}, dict(base),
    )
    return _pure_old_helpers(
        assets['structure112_source'],
        {'phase_for_step', '_anonymous_digest', '_h0_vector', '_shape_labels', '_empty_neighbors', '_build_adjacency'},
        {'H0_DESCRIPTOR_NAMES', 'CHANNELS'}, {**base, 'E88': old88},
    )


def _load_architecture(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssetBindingError('cannot_load_frozen_architecture_source')
    module = importlib.util.module_from_spec(spec)
    # Execute the verified source without SourceFileLoader's implicit pyc write
    # in an old experiment/asset directory. No old entrypoint is called.
    source = Path(path).read_text(encoding='utf-8-sig')
    exec(compile(source, str(path), 'exec'), module.__dict__)
    return module


class FrozenQwenEncoder:
    """Original real pooling/projection, with local-files-only asset loading."""
    def __init__(self, directory, device='cuda'):
        from transformers import AutoModel, AutoTokenizer
        from transformers.utils import is_flash_attn_2_available
        self.device = torch.device(device)
        if self.device.type == 'cuda' and not torch.cuda.is_available():
            raise AssetBindingError('declared_CUDA_encoder_device_unavailable')
        kwargs = {'local_files_only': True, 'trust_remote_code': True, 'torch_dtype': torch.float16}
        if self.device.type == 'cuda' and is_flash_attn_2_available():
            kwargs['attn_implementation'] = 'flash_attention_2'
        self.model = AutoModel.from_pretrained(str(directory), **kwargs).to(self.device).eval()
        self.model.requires_grad_(False)
        self.tokenizer = AutoTokenizer.from_pretrained(str(directory), local_files_only=True,
            trust_remote_code=True, padding_side='left')
        self.max_length = 8192
        self.batch_calls = 0
        self.texts_encoded = 0
        self.truncated_texts = 0

    def encode(self, texts, dimension):
        if not isinstance(texts, list) or not texts or len(texts) > 8 or not all(isinstance(t, str) for t in texts):
            raise ValueError('encoder_batches_require_one_to_eight_public_text_strings')
        if dimension not in (128, 32):
            raise ValueError('only_original_frozen_embedding_dimensions_are_allowed')
        lengths = [len(row) for row in self.tokenizer(texts, padding=False, truncation=False)['input_ids']]
        inputs = self.tokenizer(texts, padding=True, truncation=True, max_length=8192, return_tensors='pt').to(self.device)
        self.batch_calls += 1
        self.texts_encoded += len(texts)
        self.truncated_texts += sum(length > self.max_length for length in lengths)
        with torch.no_grad():
            hidden = self.model(**inputs).last_hidden_state
            mask = inputs['attention_mask']
            if bool((mask[:, -1].sum() == mask.shape[0]).item()):
                pooled = hidden[:, -1]
            else:
                pooled = hidden[torch.arange(len(texts), device=hidden.device), mask.sum(1) - 1]
            output = pooled[:, :dimension].float().cpu().clone()
        if output.shape != (len(texts), dimension) or not bool(torch.isfinite(output).all().item()):
            raise AssetBindingError('real_encoder_output_invalid')
        return output, lengths


class FrozenModelAdapters:
    """Lazy explicit loading; all real operations are producer-owned after freeze."""
    def __init__(self, repository_root=DEFAULT_REPOSITORY_ROOT, encoder_device='cuda', ranker_device='cpu'):
        self.assets = default_assets(repository_root)
        self.encoder_device = encoder_device
        self.ranker_device = torch.device(ranker_device)
        self.binding = None
        self.encoder = self.ours = self.stepfinder = self.structure = None
        self.mean = self.std = None
        self.role_embeddings = {}
        self.encoded = {}
        self.record_hashes = {}
        self.forward_counts = {'ours': 0, 'stepfinder': 0}

    def load_rankers(self):
        if self.ours is not None:
            return self.binding
        self.binding = verify_asset_binding(self.assets)
        ours_module = _load_architecture(self.assets['ours_source'], 'exp132_frozen_ours_v2')
        sf_module = _load_architecture(self.assets['sf_source'], 'exp132_frozen_stepfinder')
        with torch.random.fork_rng(devices=[]):
            ours = ours_module.Ranker('semantic_graph', hidden=96, dropout=0.15)
            stepfinder = sf_module.StepFinder()
        # Trusted old frozen checkpoint includes numpy scaler arrays; exact hash precedes loading.
        checkpoint = torch.load(self.assets['ours_checkpoint'], map_location='cpu', weights_only=False)
        if not isinstance(checkpoint, dict) or set(checkpoint) != {'state_dict', 'mean', 'std'}:
            raise AssetBindingError('frozen_ours_checkpoint_schema_changed')
        ours.load_state_dict(checkpoint['state_dict'], strict=True)
        stepfinder.load_state_dict(torch.load(self.assets['sf_checkpoint'], map_location='cpu', weights_only=True), strict=True)
        self.mean = np.asarray(checkpoint['mean'], dtype=np.float32)
        self.std = np.asarray(checkpoint['std'], dtype=np.float32)
        if self.mean.shape != (23,) or self.std.shape != (23,) or not np.isfinite(self.mean).all() or not np.isfinite(self.std).all() or not (self.std > 0).all():
            raise AssetBindingError('old_training_structure_scaler_invalid')
        if sum(p.numel() for p in ours.parameters()) != 205649:
            raise AssetBindingError('ours_frozen_architecture_parameter_count_changed')
        self.structure = load_public_structure_helpers(self.assets)
        self.ours = ours.to(self.ranker_device).eval().requires_grad_(False)
        self.stepfinder = stepfinder.to(self.ranker_device).eval().requires_grad_(False)
        return self.binding

    def _load_encoder(self):
        if self.encoder is None:
            if self.binding is None:
                self.binding = verify_asset_binding(self.assets)
            self.encoder = FrozenQwenEncoder(self.assets['encoder_directory'], self.encoder_device)

    def encode_public_records(self, records):
        selected_records = [public_record(record) for record in records]
        ids = [record['sample_id'] for record in selected_records]
        if len(set(ids)) != len(ids):
            raise ValueError('duplicate_public_sample_IDs')
        self._load_encoder()
        for record in selected_records:
            sid = record['sample_id']
            digest = public_hash(record)
            if sid in self.encoded:
                if self.record_hashes[sid] != digest:
                    raise ValueError('same_sample_ID_with_changed_public_input')
                continue
            turns = anonymous_public_turns(record)
            for turn in turns:
                role = turn['role']
                if role not in self.role_embeddings:
                    encoded_role, _ = self.encoder.encode([role], 32)
                    self.role_embeddings[role] = encoded_role[0]
            texts = [embedding_text(turn) for turn in turns]
            content_parts, token_lengths = [], []
            for offset in range(0, len(texts), 8):
                vectors, lengths = self.encoder.encode(texts[offset:offset + 8], 128)
                content_parts.append(vectors)
                token_lengths.extend(lengths)
            self.encoded[sid] = {
                'content': torch.cat(content_parts),
                'agent': torch.stack([self.role_embeddings[turn['role']] for turn in turns]),
                'public_sha256': digest, 'content_token_lengths': token_lengths,
                'truncated_step_indices': [i for i, length in enumerate(token_lengths) if length > 8192],
            }
            self.record_hashes[sid] = digest
        return {sid: self.encoded[sid] for sid in ids}

    def _validate_embeddings(self, record, embeddings):
        n = len(record['turns'])
        if embeddings.get('public_sha256') != public_hash(record):
            raise AssetBindingError('embedding_public_input_binding_mismatch')
        for name, dimension in (('content', 128), ('agent', 32)):
            tensor = embeddings[name]
            if not isinstance(tensor, torch.Tensor) or tensor.shape != (n, dimension) or tensor.dtype != torch.float32 or tensor.device.type != 'cpu' or tensor.requires_grad or not bool(torch.isfinite(tensor).all().item()):
                raise AssetBindingError('invalid_frozen_public_embedding:' + name)

    def score_record(self, record, embeddings, model='ours'):
        if model not in ('ours', 'stepfinder'):
            raise ValueError('only_two_independent_frozen_model_names_are_allowed')
        record = public_record(record)
        self._validate_embeddings(record, embeddings)
        self.load_rankers()
        n = len(record['turns'])
        with torch.no_grad():
            if model == 'ours':
                c = embeddings['content'].numpy().astype(np.float32)
                a = embeddings['agent'].numpy().astype(np.float32)
                c = c / np.maximum(np.linalg.norm(c, axis=1, keepdims=True), 1e-8)
                a = a / np.maximum(np.linalg.norm(a, axis=1, keepdims=True), 1e-8)
                visible = {'turns': anonymous_public_turns(record)}
                structure = np.array([self.structure._h0_vector(visible, i) for i in range(n)], dtype=np.float32)
                x = np.concatenate([c, a, np.clip((structure - self.mean) / self.std, -10, 10)], axis=1)
                neighbors = self.structure._build_adjacency(visible)
                adjacency = []
                for relation in RELATIONS:
                    indices = np.zeros((n, 2), dtype=np.int64)
                    valid = np.zeros((n, 2), dtype=np.float32)
                    for receiver, senders in enumerate(neighbors[relation]):
                        if len(senders) > 2:
                            raise AssetBindingError('original_relation_degree_exceeded')
                        indices[receiver, :len(senders)] = senders
                        valid[receiver, :len(senders)] = 1.0
                    adjacency.append((torch.as_tensor(indices, device=self.ranker_device),
                                      torch.as_tensor(valid, device=self.ranker_device)))
                self.forward_counts[model] += 1
                scores = self.ours(torch.as_tensor(x, device=self.ranker_device), adjacency,
                    torch.zeros(n, dtype=torch.long, device=self.ranker_device),
                    torch.tensor([n], device=self.ranker_device)).cpu().tolist()
                digests = [self.structure._anonymous_digest(visible, i) for i in range(n)]
                order = sorted(range(n), key=lambda i: (-scores[i], digests[i], i))
            else:
                padded = max(2, n)
                content = torch.zeros(1, padded, 128, device=self.ranker_device)
                agent = torch.zeros(1, padded, 32, device=self.ranker_device)
                mask = torch.zeros(1, padded, dtype=torch.bool, device=self.ranker_device)
                content[0, :n] = embeddings['content'].to(self.ranker_device)
                agent[0, :n] = embeddings['agent'].to(self.ranker_device)
                mask[0, :n] = True
                self.forward_counts[model] += 1
                logits, _ = self.stepfinder(content, agent, mask)
                scores = logits[0, :n].cpu().tolist()
                order = sorted(range(n), key=lambda i: (-scores[i], i))
        if not all(np.isfinite(float(score)) for score in scores):
            raise AssetBindingError('frozen_model_produced_nonfinite_scores')
        return {'sample_id': record['sample_id'], 'model': 'OURS_EXP130_V2' if model == 'ours' else 'STEPFINDER',
                'scores': scores, 'order': order, 'chosen_step': order[0],
                'public_sha256': embeddings['public_sha256'], 'steps': n,
                'checkpoint_sha256': MODEL_HASHES['ours_checkpoint' if model == 'ours' else 'sf_checkpoint']}

    def predict_public_records(self, records):
        records = [public_record(record) for record in records]
        embeddings = self.encode_public_records(records)
        return {record['sample_id']: {
                    'A_FROZEN': self.score_record(record, embeddings[record['sample_id']], 'ours'),
                    'StepFinder': self.score_record(record, embeddings[record['sample_id']], 'stepfinder')}
                for record in records}

    def receipt(self):
        return {'asset_binding': copy.deepcopy(self.binding), 'seed': 20260816, 'outer_fold': 0,
                'checkpoint_choice': 'canonical_first_frozen_checkpoint_no_performance_selection',
                'encoder_revision': ENCODER_REVISION, 'encoder_device': str(self.encoder_device),
                'ranker_device': str(self.ranker_device), 'new_training_steps': 0,
                'new_inference_label_accesses': 0, 'downloads': 0,
                'historical_supervision': 'frozen_AF_Traj_572_outer_train_groups_no_new_target_training',
                'stepfinder_padding': 'per_record_max_2_n',
                'encoder_batch_calls': 0 if self.encoder is None else self.encoder.batch_calls,
                'encoder_texts': 0 if self.encoder is None else self.encoder.texts_encoded,
                'encoder_truncated_texts': 0 if self.encoder is None else self.encoder.truncated_texts,
                'ranker_record_forwards': dict(self.forward_counts), 'records_encoded': len(self.encoded)}

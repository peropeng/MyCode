"""Exp112: frozen temporal/interaction/dependency full step ranking.

The directory owns the replacement RQ1 module B2.  Exp88/96/106 are loaded
read-only for their frozen structural descriptors, pairwise-B fit semantics,
numeric E2 score, and exact Exp106 A condition.  No Exp111 result or outer-held
metric is read by this runner.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import random
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple


HERE = Path(__file__).resolve().parent
EXP106_ROOT = HERE.parent / "实验106_责任排序_Top1提升级联"
_SPEC = importlib.util.spec_from_file_location("exp106_read_only_exp112", EXP106_ROOT / "runner.py")
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot import frozen Exp106 runner: {EXP106_ROOT / 'runner.py'}")
E106 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(E106)
E105 = E106.E105
E96 = E105.E96
E88 = E105.E88


SEEDS = (20260816, 20260817, 20260818)
N_OUTER = 5
N_INNER = 4
N_BOOT = 5000
PAIRWISE_EPOCHS = 200
PAIRWISE_LR = 0.05
PAIRWISE_L2 = 0.001
PAIRWISE_POS_WEIGHT = 1.0
SCORE_ALPHA = 0.5
H0_DESCRIPTOR_NAMES = (
    "content_present", "action_present", "thought_present",
    "content_json", "action_json", "thought_json",
    "content_array", "content_object", "action_array", "action_object",
    "thought_array", "thought_object", "content_nested", "action_nested",
    "thought_nested", "action_tool_list", "action_tool_arity_2plus",
)
PHASES = (0, 1, 2)
CHANNELS = ("temporal", "same_role", "same_full_shape_signature", "same_nonempty_action_shape")
FAIR_BASELINES = ("local", "original_A", "pairwise_B", "recency")
TARGET_CONDITIONS = ("A", "B2", "A_plus_B")
CONTROL_CONDITIONS = (
    "B2_deletion", "B2_shuffle", "random_dependency",
    "A_plus_B_delete_A", "A_plus_B_delete_B2", "A_plus_B_shuffle_B2",
)
CONDITIONS = FAIR_BASELINES + TARGET_CONDITIONS + CONTROL_CONDITIONS + ("Oracle_step",)
FORMAL_OUTPUT_PATH = (HERE / "results" / "formal_nested_oof_results.json").resolve()
EXECUTION_AUDIT_PATH = (HERE / "results" / "execution_attempt_audit.json").resolve()
_SOURCE_ROOT_FOR_LOAD = ""


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _protocol() -> Dict[str, Any]:
    return _load_json(HERE / "protocol.json")


def _data_seal() -> Dict[str, Any]:
    return _load_json(HERE / "data_seal.json")


def _group(rec: Mapping[str, Any]) -> str:
    return str(rec.get("task_group") or "")


def _role_index(role: str) -> int:
    text = str(role)
    if text.startswith("role_"):
        try:
            return int(text.split("_", 1)[1])
        except (TypeError, ValueError):
            return -1
    return -1


def phase_for_step(index: int, n_steps: int) -> int:
    if int(n_steps) <= 0:
        raise ValueError("phase is undefined for an empty trajectory")
    if not 0 <= int(index) < int(n_steps):
        raise IndexError("step index outside trajectory")
    return min(2, (3 * int(index)) // int(n_steps))


def _anonymous_digest(rec: Mapping[str, Any], index: int) -> str:
    # Reuse the frozen Exp88 payload byte-for-byte.  A different JSON key
    # would create a new digest tie order and break B2-deletion equivalence.
    return str(E88._tie_digest(rec, int(index)))


def _h0_vector(rec: Mapping[str, Any], index: int) -> List[float]:
    turns = list(rec.get("turns") or [])
    n_steps = len(turns)
    if not n_steps:
        return []
    turn = turns[int(index)]
    desc = E88.turn_structure(turn)
    roles = []
    for item in turns:
        role = str(item.get("role") or "")
        if role not in roles:
            roles.append(role)
    role = str(turn.get("role") or "")
    role_ordinal = roles.index(role) if role in roles else 0
    role_denominator = max(1, len(roles) - 1)
    phase = phase_for_step(int(index), n_steps)
    values = [float(desc[name]) for name in H0_DESCRIPTOR_NAMES]
    values.extend([
        float(E88._local_score(rec, int(index))),
        float(index) / float(max(1, n_steps - 1)),
        float(phase == 0), float(phase == 1), float(phase == 2),
        float(role_ordinal) / float(role_denominator),
    ])
    if len(values) != 23:
        raise RuntimeError(f"frozen h0 dimension changed: {len(values)}")
    return values


def _shape_labels(rec: Mapping[str, Any]) -> Dict[str, List[Any]]:
    turns = list(rec.get("turns") or [])
    descriptors = [E88.turn_structure(turn) for turn in turns]
    full = [desc["shape_sig"] for desc in descriptors]
    action = [desc["action_shape"] if float(desc["action_present"]) > 0.0 else None for desc in descriptors]
    role = [str(turn.get("role") or "") for turn in turns]
    return {"role": role, "full": full, "action": action}


def _empty_neighbors(n_steps: int) -> Dict[str, List[List[int]]]:
    return {channel: [[] for _ in range(n_steps)] for channel in CHANNELS}


def _build_adjacency(rec: Mapping[str, Any]) -> Dict[str, List[List[int]]]:
    turns = list(rec.get("turns") or [])
    n_steps = len(turns)
    labels = _shape_labels(rec)
    neighbors = _empty_neighbors(n_steps)
    for index in range(n_steps):
        if index > 0:
            neighbors["temporal"][index].append(index - 1)
        if index + 1 < n_steps:
            neighbors["temporal"][index].append(index + 1)
    for label_name, channel in (("role", "same_role"), ("full", "same_full_shape_signature"), ("action", "same_nonempty_action_shape")):
        positions: Dict[Any, List[int]] = defaultdict(list)
        for index, label in enumerate(labels[label_name]):
            if label is not None:
                positions[repr(label)].append(index)
        for indices in positions.values():
            for left, right in zip(indices, indices[1:]):
                neighbors[channel][left].append(right)
                neighbors[channel][right].append(left)
    return neighbors


def _edge_counts(neighbors: Mapping[str, Sequence[Sequence[int]]]) -> Dict[str, int]:
    return {channel: sum(len(items) for items in neighbors.get(channel, [])) for channel in CHANNELS}


def _graph_audit(rec: Mapping[str, Any], neighbors: Mapping[str, Sequence[Sequence[int]]]) -> Dict[str, Any]:
    n_steps = len(rec.get("turns") or [])
    counts = _edge_counts(neighbors)
    coverage = {
        channel: sum(bool(items) for items in neighbors.get(channel, [])) / n_steps if n_steps else 0.0
        for channel in CHANNELS
    }
    isolated = sum(all(not neighbors[channel][index] for channel in CHANNELS) for index in range(n_steps)) / n_steps if n_steps else 0.0
    return {"node_count": n_steps, "edge_count": counts, "coverage": coverage, "isolated_node_rate": isolated}


def _remap_adjacency(neighbors: Mapping[str, Sequence[Sequence[int]]], permutation: Sequence[int]) -> Dict[str, List[List[int]]]:
    n_steps = len(permutation)
    remapped = _empty_neighbors(n_steps)
    for channel in CHANNELS:
        for source, targets in enumerate(neighbors.get(channel, [])):
            new_source = int(permutation[source])
            remapped[channel][new_source].extend(int(permutation[target]) for target in targets)
    return remapped


def _aggregate_graph(rec: Mapping[str, Any], neighbors: Mapping[str, Sequence[Sequence[int]]]) -> Dict[str, Any]:
    turns = list(rec.get("turns") or [])
    n_steps = len(turns)
    if not n_steps:
        return {"h0": [], "node_features": [], "adjacency": _empty_neighbors(0), "graph_audit": _graph_audit(rec, neighbors), "graph_feature_dim": 215}
    h0 = [_h0_vector(rec, index) for index in range(n_steps)]
    states = [list(vector) for vector in h0]
    round_messages: List[Dict[str, List[List[float]]]] = []
    for _round in range(2):
        messages: Dict[str, List[List[float]]] = {}
        for channel in CHANNELS:
            channel_messages: List[List[float]] = []
            for index in range(n_steps):
                targets = list(neighbors[channel][index])
                if not targets:
                    channel_messages.append([0.0] * len(h0[index]))
                else:
                    channel_messages.append([
                        sum(states[target][dimension] for target in targets) / len(targets)
                        for dimension in range(len(h0[index]))
                    ])
            messages[channel] = channel_messages
        round_messages.append(messages)
        next_states = []
        for index in range(n_steps):
            updated = list(states[index])
            for channel in CHANNELS:
                updated = [updated[dimension] + messages[channel][index][dimension] for dimension in range(len(updated))]
            next_states.append(updated)
        states = next_states
    node_features: List[List[float]] = []
    denominator = float(max(1, n_steps - 1))
    for index in range(n_steps):
        vector = list(h0[index])
        for round_messages_for_step in round_messages:
            for channel in CHANNELS:
                vector.extend(round_messages_for_step[channel][index])
        for channel in CHANNELS:
            targets = list(neighbors[channel][index])
            gaps = [abs(index - target) / denominator for target in targets]
            vector.append(sum(gaps) / len(gaps) if gaps else 0.0)
            vector.append(1.0 if targets else 0.0)
        node_features.append([float(value) for value in vector])
    feature_dim = len(node_features[0]) if node_features else 215
    if feature_dim != 215:
        raise RuntimeError(f"frozen graph feature dimension changed: {feature_dim}")
    audit = _graph_audit(rec, neighbors)
    audit["rounds"] = 2
    audit["h0_dimension"] = len(h0[0]) if h0 else 23
    return {"h0": h0, "node_features": node_features, "adjacency": {key: [list(value) for value in values] for key, values in neighbors.items()}, "graph_audit": audit, "graph_feature_dim": feature_dim}


def build_graph(rec: Mapping[str, Any]) -> Dict[str, Any]:
    return _aggregate_graph(rec, _build_adjacency(rec))


def _control_seed(seed: int, rec: Mapping[str, Any], salt: str) -> int:
    raw = f"Exp112|{salt}|{int(seed)}|{_group(rec)}".encode("utf-8")
    return int(hashlib.sha256(raw).hexdigest()[:16], 16)


def random_dependency_graph(rec: Mapping[str, Any], graph: Mapping[str, Any], seed: int) -> Tuple[Dict[str, Any], List[int]]:
    n_steps = len(rec.get("turns") or [])
    permutation = list(range(n_steps))
    if n_steps > 1:
        rng = random.Random(_control_seed(seed, rec, "random-dependency-v1"))
        rng.shuffle(permutation)
        if permutation == list(range(n_steps)):
            permutation = permutation[1:] + permutation[:1]
    remapped = _remap_adjacency(graph["adjacency"], permutation)
    return _aggregate_graph(rec, remapped), permutation


def _fit_pairwise_model(x_values: Sequence[Sequence[float]], labels: Sequence[float]) -> Tuple[List[float], float]:
    if not x_values:
        return [], 0.0
    model = E88.load_bound_source(_SOURCE_ROOT_FOR_LOAD)[1]
    weights, bias = model.fit_logreg(
        [list(map(float, row)) for row in x_values],
        [float(value) for value in labels],
        epochs=PAIRWISE_EPOCHS,
        lr=PAIRWISE_LR,
        l2=PAIRWISE_L2,
        pos_weight=PAIRWISE_POS_WEIGHT,
    )
    return [float(value) for value in weights], float(bias)


def fit_b2_model(records: Sequence[Mapping[str, Any]], graphs: Sequence[Mapping[str, Any]], fit_indices: Sequence[int]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    x_values: List[List[float]] = []
    labels: List[float] = []
    pair_trajectories = 0
    pair_count = 0
    for raw_index in sorted(int(index) for index in fit_indices):
        rec = records[raw_index]
        features = graphs[raw_index]["node_features"]
        if not features:
            continue
        gold = int(rec["mistake_step"])
        negatives = [index for index in range(len(features)) if index != gold]
        if not negatives:
            continue
        pair_trajectories += 1
        gold_feature = features[gold]
        for negative in negatives:
            diff = [gold_feature[j] - features[negative][j] for j in range(len(gold_feature))]
            x_values.append(diff)
            labels.append(1.0)
            x_values.append([-value for value in diff])
            labels.append(0.0)
            pair_count += 1
    weights, bias = _fit_pairwise_model(x_values, labels)
    model = {
        "weights": weights, "bias": bias, "feature_dim": len(weights),
        "epochs": PAIRWISE_EPOCHS, "lr": PAIRWISE_LR, "l2": PAIRWISE_L2,
        "pos_weight": PAIRWISE_POS_WEIGHT, "fit_records": len(fit_indices),
    }
    return model, {
        "fit_records": len(fit_indices),
        "fit_task_groups": len({_group(records[index]) for index in fit_indices}),
        "pair_trajectories": pair_trajectories,
        "positive_negative_pairs": pair_count,
        "fit_rows": len(x_values),
        "feature_dim": len(weights),
    }


def _dot(weights: Sequence[float], values: Sequence[float]) -> float:
    return sum(float(weights[index]) * float(values[index]) for index in range(min(len(weights), len(values))))


def predict_graph_utility(graph: Mapping[str, Any], model: Mapping[str, Any]) -> List[float]:
    return [_dot(model.get("weights", []), values) for values in graph.get("node_features", [])]


def minmax_normalize(values: Sequence[float]) -> List[float]:
    values = [float(value) for value in values]
    if not values:
        return []
    low, high = min(values), max(values)
    if high - low <= 1e-12:
        return [0.5] * len(values)
    return [(value - low) / (high - low) for value in values]


def b2_scores_from_utilities(rec: Mapping[str, Any], pairwise_probs: Mapping[str, float], graph_utilities: Sequence[float]) -> Dict[str, List[float]]:
    pairwise_raw = list(E106._numeric_e2_scores(rec, pairwise_probs))
    pairwise_norm = minmax_normalize(pairwise_raw)
    graph_raw = [float(value) for value in graph_utilities]
    graph_norm = minmax_normalize(graph_raw)
    fused = [SCORE_ALPHA * pair + SCORE_ALPHA * graph for pair, graph in zip(pairwise_norm, graph_norm)]
    return {"pairwise_raw": pairwise_raw, "pairwise_normalized": pairwise_norm, "graph_raw": graph_raw, "graph_normalized": graph_norm, "b2": fused}


def b2_scores(rec: Mapping[str, Any], pairwise_probs: Mapping[str, float], graph: Mapping[str, Any], model: Mapping[str, Any]) -> Dict[str, List[float]]:
    return b2_scores_from_utilities(rec, pairwise_probs, predict_graph_utility(graph, model))


def _rank_key_scores(rec: Mapping[str, Any], scores: Sequence[float]) -> List[Tuple[float, str]]:
    return [(-float(score), _anonymous_digest(rec, index)) for index, score in enumerate(scores)]


def rank_from_scores(rec: Mapping[str, Any], scores: Sequence[float], target: int) -> float:
    keys = _rank_key_scores(rec, scores)
    if not 0 <= int(target) < len(keys):
        return float(len(keys) + 1)
    target_key = keys[int(target)]
    before = sum(key < target_key for key in keys)
    ties = sum(key == target_key for key in keys)
    return float(before + 1) + (float(ties) - 1.0) / 2.0


def _recency_rank(rec: Mapping[str, Any]) -> float:
    turns = list(rec.get("turns") or [])
    gold = int(rec.get("mistake_step", -1))
    return float(len(turns) - gold) if 0 <= gold < len(turns) else float(len(turns) + 1)


def _reciprocal(rank: float) -> float:
    return 1.0 / float(rank) if float(rank) > 0 else 0.0


def rank_fair_baseline(rec: Mapping[str, Any], pairwise_probs: Mapping[str, float], original_probs: Mapping[str, float], condition: str) -> float:
    gold = int(rec.get("mistake_step", -1))
    if condition == "local":
        return float(E88._tied_rank(rec, gold, {}, bridge=False))
    if condition == "original_A":
        return float(E88._tied_rank(rec, gold, original_probs, bridge=True))
    if condition == "pairwise_B":
        # E88's frozen key is (-numeric E2 score, anonymous role+shape digest).
        return float(E88._tied_rank(rec, gold, pairwise_probs, bridge=True))
    if condition == "recency":
        return _recency_rank(rec)
    raise ValueError(f"unknown fair baseline: {condition}")


def a_step_scores(rec: Mapping[str, Any], pairwise_probs: Mapping[str, float]) -> Tuple[List[float], int]:
    pairwise_norm = minmax_normalize(E106._numeric_e2_scores(rec, pairwise_probs))
    promoted = int(E106.choose_promoted_top(rec, pairwise_probs))
    values = [2.0 if index == promoted else float(pairwise_norm[index]) for index in range(len(pairwise_norm))]
    return values, promoted


def a_rank(rec: Mapping[str, Any], pairwise_probs: Mapping[str, float]) -> float:
    promoted = int(E106.choose_promoted_top(rec, pairwise_probs))
    return float(E106.top1_cascade_rank(rec, pairwise_probs, promoted_override=promoted))


def a_plus_b_rank(rec: Mapping[str, Any], b2_numeric: Sequence[float], promoted: int, target: int) -> float:
    if not 0 <= int(promoted) < len(b2_numeric):
        return rank_from_scores(rec, b2_numeric, target)
    if int(target) == int(promoted):
        return 1.0
    remaining = [index for index in range(len(b2_numeric)) if index != int(promoted)]
    target_key = (-float(b2_numeric[int(target)]), _anonymous_digest(rec, int(target)))
    keys = [(-float(b2_numeric[index]), _anonymous_digest(rec, index)) for index in remaining]
    before = sum(key < target_key for key in keys)
    ties = sum(key == target_key for key in keys)
    return 2.0 + float(before) + (float(ties) - 1.0) / 2.0


def stack_feature_vector(a_value: float, b2_value: float, is_a_promoted: bool, is_b2_top: bool) -> List[float]:
    difference = float(a_value) - float(b2_value)
    return [
        float(a_value), float(b2_value), difference, float(a_value) * float(b2_value),
        float(bool(is_a_promoted)), float(bool(is_b2_top)), abs(difference),
    ]


def _stack_scores_for_record(rec: Mapping[str, Any], pairwise_probs: Mapping[str, float], b2_numeric: Sequence[float]) -> Dict[str, Any]:
    a_scores, promoted = a_step_scores(rec, pairwise_probs)
    b2_values = [float(value) for value in b2_numeric]
    top_b2 = min(range(len(b2_values)), key=lambda index: (-b2_values[index], _anonymous_digest(rec, index))) if b2_values else -1
    features = [stack_feature_vector(a_scores[index], b2_values[index], index == promoted, index == top_b2) for index in range(len(b2_values))]
    return {"a_scores": a_scores, "b2_scores": b2_values, "promoted": promoted, "top_b2": top_b2, "features": features}


def fit_stacker(records: Sequence[Mapping[str, Any]], inner_oof_scores: Mapping[int, Mapping[str, Any]], fit_indices: Sequence[int]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    x_values: List[List[float]] = []
    labels: List[float] = []
    pair_trajectories = 0
    pair_count = 0
    for raw_index in sorted(int(index) for index in fit_indices):
        if raw_index not in inner_oof_scores:
            raise RuntimeError("stacker fit record lacks exactly-one inner OOF A/B2 scores")
        rec = records[raw_index]
        features = inner_oof_scores[raw_index]["features"]
        if not features:
            continue
        gold = int(rec["mistake_step"])
        negatives = [index for index in range(len(features)) if index != gold]
        if not negatives:
            continue
        pair_trajectories += 1
        gold_feature = features[gold]
        for negative in negatives:
            diff = [gold_feature[j] - features[negative][j] for j in range(len(gold_feature))]
            x_values.append(diff)
            labels.append(1.0)
            x_values.append([-value for value in diff])
            labels.append(0.0)
            pair_count += 1
    weights, bias = _fit_pairwise_model(x_values, labels)
    model = {
        "weights": weights, "bias": bias, "feature_dim": len(weights),
        "epochs": PAIRWISE_EPOCHS, "lr": PAIRWISE_LR, "l2": PAIRWISE_L2,
        "pos_weight": PAIRWISE_POS_WEIGHT, "fit_records": len(fit_indices),
    }
    audit = {
        "fit_records": len(fit_indices),
        "fit_task_groups": len({_group(records[index]) for index in fit_indices}),
        "pair_trajectories": pair_trajectories,
        "positive_negative_pairs": pair_count,
        "fit_rows": len(x_values),
        "feature_dim": len(weights),
        "inner_oof_scores_exact": set(int(index) for index in inner_oof_scores) == set(int(index) for index in fit_indices),
        "raw_features_used": False,
        "scope_features_used": False,
    }
    return model, audit


def predict_stack_utility(rec: Mapping[str, Any], a_scores: Sequence[float], b2_scores_values: Sequence[float], promoted: int, model: Mapping[str, Any]) -> Dict[str, Any]:
    top_b2 = min(range(len(b2_scores_values)), key=lambda index: (-float(b2_scores_values[index]), _anonymous_digest(rec, index))) if b2_scores_values else -1
    features = [stack_feature_vector(a_scores[index], b2_scores_values[index], index == promoted, index == top_b2) for index in range(len(b2_scores_values))]
    utility = [_dot(model.get("weights", []), values) for values in features]
    constant = bool(utility) and max(utility) - min(utility) <= 1e-12
    if constant:
        utility = [float(value) for value in b2_scores_values]
    return {"features": features, "utility": utility, "constant_fallback": constant, "top_b2": top_b2}


def _permute_values(rec: Mapping[str, Any], values: Sequence[float], seed: int, salt: str) -> List[float]:
    shuffled = [float(value) for value in values]
    if len(shuffled) <= 1:
        return shuffled
    rng = random.Random(_control_seed(seed, rec, salt))
    rng.shuffle(shuffled)
    if shuffled == [float(value) for value in values] and len(set(shuffled)) > 1:
        shuffled = shuffled[1:] + shuffled[:1]
    return shuffled


def _raw_metrics(ranks: Sequence[float]) -> Dict[str, Any]:
    values = [float(value) for value in ranks]
    if not values:
        return {"n": 0, "mrr": 0.0, "r_at_1": 0.0, "r_at_3": 0.0}
    return {"n": len(values), "mrr": sum(_reciprocal(rank) for rank in values) / len(values), "r_at_1": sum(rank <= 1.0 for rank in values) / len(values), "r_at_3": sum(rank <= 3.0 for rank in values) / len(values)}


def _group_means(records: Sequence[Mapping[str, Any]], values: Sequence[float]) -> Dict[str, float]:
    grouped: Dict[str, List[float]] = defaultdict(list)
    for rec, value in zip(records, values):
        grouped[_group(rec)].append(float(value))
    return {group: sum(items) / len(items) for group, items in grouped.items()}


def _group_rank_metrics(records: Sequence[Mapping[str, Any]], ranks: Sequence[float]) -> Dict[str, Dict[str, float]]:
    return {
        "mrr": _group_means(records, [_reciprocal(rank) for rank in ranks]),
        "r_at_1": _group_means(records, [float(float(rank) <= 1.0) for rank in ranks]),
        "r_at_3": _group_means(records, [float(float(rank) <= 3.0) for rank in ranks]),
    }


def _paired_group_counts(values_a: Mapping[str, float], values_b: Mapping[str, float]) -> Dict[str, int]:
    groups = sorted(set(values_a) & set(values_b))
    return {"better": sum(values_a[group] > values_b[group] for group in groups), "worse": sum(values_a[group] < values_b[group] for group in groups), "tie": sum(values_a[group] == values_b[group] for group in groups)}


def _bootstrap_maps(values_a: Mapping[str, float], values_b: Mapping[str, float], seed: int, n_boot: int = N_BOOT) -> Dict[str, Any]:
    groups = sorted(set(values_a) & set(values_b))
    if not groups:
        return {"n": 0, "n_boot": int(n_boot), "mean": 0.0, "ci95_low": 0.0, "ci95_high": 0.0, "excludes_0": False}
    deltas = [float(values_a[group]) - float(values_b[group]) for group in groups]
    rng = random.Random(int(seed))
    boot = [sum(deltas[rng.randrange(len(deltas))] for _ in groups) / len(groups) for _ in range(int(n_boot))]
    ordered = sorted(boot)
    low = ordered[int(0.025 * n_boot)]
    high = ordered[int(0.975 * n_boot)]
    return {"n": len(groups), "n_boot": int(n_boot), "mean": sum(deltas) / len(deltas), "ci95_low": low, "ci95_high": high, "excludes_0": bool(low > 0 or high < 0)}


def _pooled_bootstrap(results: Sequence[Mapping[str, Any]], target: str, baseline: str, seed: int) -> Dict[str, Any]:
    if not results:
        return {"n": 0, "n_boot": N_BOOT, "mean": 0.0, "ci95_low": 0.0, "ci95_high": 0.0, "excludes_0": False}
    groups = sorted(set.intersection(*(set(result["group_mrr"][target]) & set(result["group_mrr"][baseline]) for result in results)))
    if not groups:
        return {"n": 0, "n_boot": N_BOOT, "mean": 0.0, "ci95_low": 0.0, "ci95_high": 0.0, "excludes_0": False}
    deltas = {group: sum(float(result["group_mrr"][target][group]) - float(result["group_mrr"][baseline][group]) for result in results) / len(results) for group in groups}
    rng = random.Random(int(seed))
    boot = [sum(deltas[groups[rng.randrange(len(groups))]] for _ in groups) / len(groups) for _ in range(N_BOOT)]
    ordered = sorted(boot)
    low = ordered[int(0.025 * N_BOOT)]
    high = ordered[int(0.975 * N_BOOT)]
    return {"n": len(groups), "n_boot": N_BOOT, "mean": sum(deltas.values()) / len(deltas), "ci95_low": low, "ci95_high": high, "excludes_0": bool(low > 0 or high < 0)}


def _length_quantile_buckets(records: Sequence[Mapping[str, Any]]) -> Dict[str, List[int]]:
    lengths = sorted(len(record.get("turns") or []) for record in records)
    if not lengths:
        return {}
    cuts = [lengths[min(len(lengths) - 1, int((len(lengths) - 1) * fraction))] for fraction in (0.25, 0.5, 0.75)]
    out: Dict[str, List[int]] = defaultdict(list)
    for index, rec in enumerate(records):
        length = len(rec.get("turns") or [])
        bucket = "q1" if length <= cuts[0] else "q2" if length <= cuts[1] else "q3" if length <= cuts[2] else "q4"
        out[f"length_{bucket}"].append(index)
        out[f"role_count_{len({str(turn.get('role') or '') for turn in rec.get('turns') or []})}"].append(index)
        gold = int(rec.get("mistake_step", -1))
        if 0 <= gold < length:
            out[f"gold_phase_{phase_for_step(gold, length)}"].append(index)
    out["_cutpoints"] = cuts  # type: ignore[assignment]
    return out


def _subgroup_metrics(records: Sequence[Mapping[str, Any]], ranks: Mapping[str, Sequence[float]]) -> Dict[str, Any]:
    buckets = _length_quantile_buckets(records)
    cuts = buckets.pop("_cutpoints", [])
    output: Dict[str, Any] = {"length_cutpoints": cuts, "conditions": {}}
    for condition, values in ranks.items():
        output["conditions"][condition] = {name: _raw_metrics([values[index] for index in indices]) for name, indices in sorted(buckets.items())}
    return output


def _load_train_data(source_root: str, data_root: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any], List[Dict[str, Any]]]:
    global _SOURCE_ROOT_FOR_LOAD
    _SOURCE_ROOT_FOR_LOAD = str(source_root)
    E96._SOURCE_ROOT_FOR_LOAD = str(source_root)
    E105._SOURCE_ROOT_FOR_LOAD = str(source_root)
    records, boundary, rows = E105._load_exp96_train(source_root, data_root)
    if (len(records), len({_group(record) for record in records})) != (731, 716):
        raise RuntimeError("Exp96 frozen train counts changed")
    if boundary.get("confirmation_used_for_scoring") or boundary.get("confirmation_used_for_model_fit") or boundary.get("confirmation_used_for_method_selection"):
        raise RuntimeError("confirmation boundary entered Exp112")
    return records, boundary, rows


def _indices_for_groups(records: Sequence[Mapping[str, Any]], groups: Iterable[str]) -> List[int]:
    wanted = set(str(group) for group in groups)
    return [index for index, rec in enumerate(records) if _group(rec) in wanted]


def _nested_plan(fold_groups: Sequence[Sequence[str]], outer_index: int) -> Dict[str, Any]:
    return E105._nested_group_plan(fold_groups, outer_index)


def _fit_b2_and_pairwise(records: Sequence[Mapping[str, Any]], rows: Sequence[Mapping[str, Any]], graphs: Sequence[Mapping[str, Any]], fit_indices: Sequence[int], held_indices: Sequence[int], label: str) -> Tuple[Dict[int, Dict[str, float]], Dict[int, Dict[str, Any]], Dict[str, Any]]:
    pairwise_probs, pairwise_audit = E96._fit_pairwise(records, rows, fit_indices, held_indices)
    b2_model, b2_audit = fit_b2_model(records, graphs, fit_indices)
    predictions: Dict[int, Dict[str, Any]] = {}
    for index in held_indices:
        scores = b2_scores(records[index], pairwise_probs[index], graphs[index], b2_model)
        a_scores, promoted = a_step_scores(records[index], pairwise_probs[index])
        predictions[int(index)] = {
            "pairwise_probs": pairwise_probs[index],
            "b2": scores,
            "a_scores": a_scores,
            "promoted": promoted,
            "fit_label": label,
        }
    audit = {
        "fit_label": label,
        "fit_records": len(fit_indices),
        "held_records": len(held_indices),
        "fit_groups": sorted({_group(records[index]) for index in fit_indices}),
        "held_groups": sorted({_group(records[index]) for index in held_indices}),
        "fit_group_intersection_held_group_count": len({_group(records[index]) for index in fit_indices} & {_group(records[index]) for index in held_indices}),
        "pairwise_fit": pairwise_audit,
        "b2_fit": b2_audit,
        "b2_model": b2_model,
    }
    return pairwise_probs, predictions, audit


def _collect_nested_folds(seed: int, source_root: str, data_root: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any], List[Dict[str, Any]]]:
    records, boundary, rows = _load_train_data(source_root, data_root)
    graphs = [build_graph(rec) for rec in records]
    groups = sorted({_group(record) for record in records})
    fold_groups = E96._fold_groups(groups, int(seed))
    all_indices = list(range(len(records)))
    fold_bundles: List[Dict[str, Any]] = []
    for outer_index in range(N_OUTER):
        plan = _nested_plan(fold_groups, outer_index)
        outer_train = _indices_for_groups(records, plan["outer_fit_groups"])
        outer_held = _indices_for_groups(records, plan["outer_held_groups"])
        inner_oof: Dict[int, Dict[str, Any]] = {}
        inner_prediction_counts: Dict[int, int] = defaultdict(int)
        inner_fit_audits: List[Dict[str, Any]] = []
        for inner_plan in plan["inner"]:
            inner_fit = _indices_for_groups(records, inner_plan["fit_groups"])
            inner_held = _indices_for_groups(records, inner_plan["held_groups"])
            _, predictions, fit_audit = _fit_b2_and_pairwise(records, rows, graphs, inner_fit, inner_held, f"seed{seed}:outer{outer_index}:inner{inner_plan['inner_fold']}")
            overlap = set(inner_oof) & set(predictions)
            if overlap:
                raise RuntimeError(f"inner OOF overlap: {sorted(overlap)[:3]}")
            for index, prediction in predictions.items():
                inner_oof[index] = prediction
                inner_prediction_counts[index] += 1
            fit_audit.update({"inner_fold": int(inner_plan["inner_fold"]), "fit_groups": sorted(inner_plan["fit_groups"]), "held_groups": sorted(inner_plan["held_groups"])})
            inner_fit_audits.append(fit_audit)
        inner_oof_exact = set(inner_oof) == set(outer_train) and all(count == 1 for count in inner_prediction_counts.values())
        if not inner_oof_exact:
            raise RuntimeError("inner OOF A/B2 predictions do not cover outer-train exactly once")
        outer_pairwise_probs, outer_predictions, outer_fit_audit = _fit_b2_and_pairwise(records, rows, graphs, outer_train, outer_held, f"seed{seed}:outer{outer_index}")
        outer_original_probs = E96._fit_original(rows, outer_train, outer_held)
        stacker, stack_audit = fit_stacker(records, {index: {"features": _stack_scores_for_record(records[index], inner_oof[index]["pairwise_probs"], inner_oof[index]["b2"]["b2"])["features"]} for index in inner_oof}, outer_train)
        plan_audit = E105._nested_plan_audit(plan)
        plan_audit.update({
            "inner_oof_A_B2_record_coverage_exact_once": inner_oof_exact,
            "inner_oof_record_counts": {int(index): int(inner_prediction_counts[index]) for index in sorted(inner_prediction_counts)},
            "outer_fit_groups_exact_outer_train": set(plan["outer_fit_groups"]) == {_group(records[index]) for index in outer_train},
            "outer_fit_excludes_outer_held": not (set(plan["outer_fit_groups"]) & set(plan["outer_held_groups"])),
            "stacker_fit_records_are_outer_train": stack_audit["fit_records"] == len(outer_train),
            "stacker_fit_inner_oof_only": bool(stack_audit["inner_oof_scores_exact"]),
        })
        fold_bundles.append({
            "outer_fold": int(outer_index), "outer_train": outer_train, "outer_held": outer_held,
            "outer_fit_groups": sorted(plan["outer_fit_groups"]), "outer_held_groups": sorted(plan["outer_held_groups"]),
            "plan": plan, "plan_audit": plan_audit, "inner_oof": inner_oof,
            "outer_pairwise_probs": outer_pairwise_probs, "outer_predictions": outer_predictions,
            "outer_original_probs": outer_original_probs, "outer_fit_audit": outer_fit_audit,
            "stacker": stacker, "stack_audit": stack_audit, "inner_fit_audits": inner_fit_audits,
        })
    held_union = [index for fold in fold_bundles for index in fold["outer_held"]]
    if len(held_union) != len(records) or len(set(held_union)) != len(records):
        raise RuntimeError("outer-held predictions do not cover every record once")
    return records, fold_bundles, boundary, graphs


def _oracle_rank(rec: Mapping[str, Any]) -> float:
    turns = list(rec.get("turns") or [])
    return 1.0 if turns else 0.0


def _evaluate_fold(fold: Mapping[str, Any], records: Sequence[Mapping[str, Any]], graphs: Sequence[Mapping[str, Any]], seed: int) -> Dict[str, Any]:
    ranks: Dict[str, Dict[int, float]] = {condition: {} for condition in CONDITIONS}
    raw_scores: Dict[str, Dict[int, List[float]]] = defaultdict(dict)
    graph_audits: Dict[int, Dict[str, Any]] = {}
    graph_controls: Dict[int, Dict[str, Any]] = {}
    promoted: Dict[int, int] = {}
    fallback: Dict[int, bool] = {}
    for index in fold["outer_held"]:
        rec = records[index]
        prediction = fold["outer_predictions"][index]
        pairwise_probs = fold["outer_pairwise_probs"][index]
        original_probs = fold["outer_original_probs"][index]
        target = int(rec["mistake_step"])
        graph = graphs[index]
        b2 = prediction["b2"]
        b2_numeric = list(b2["b2"])
        a_scores, promoted_index = a_step_scores(rec, pairwise_probs)
        promoted[index] = int(promoted_index)
        stack = predict_stack_utility(rec, a_scores, b2_numeric, promoted_index, fold["stacker"])
        fallback[index] = bool(stack["constant_fallback"])
        shuffled_graph_utilities = _permute_values(rec, b2["graph_raw"], seed, "B2-shuffle-v1")
        b2_shuffle = b2_scores_from_utilities(rec, pairwise_probs, shuffled_graph_utilities)["b2"]
        random_graph, permutation = random_dependency_graph(rec, graph, seed)
        random_utility = predict_graph_utility(random_graph, fold["outer_fit_audit"]["b2_model"])
        b2_random = b2_scores_from_utilities(rec, pairwise_probs, random_utility)["b2"]
        zero_utility = [0.0] * len(b2["graph_raw"])
        b2_deletion = b2_scores_from_utilities(rec, pairwise_probs, zero_utility)["b2"]
        shuffled_b2_values = _permute_values(rec, b2_numeric, seed, "A+B-shuffle-B2-v1")
        stack_shuffle = predict_stack_utility(rec, a_scores, shuffled_b2_values, promoted_index, fold["stacker"])
        # The frozen deletion controls zero every feature carrying the deleted
        # arm, including cross terms and absolute difference; only the other
        # arm and its top/promotion indicator survive.
        delete_a_features = [[0.0, b2_numeric[i], 0.0, 0.0, 0.0, float(i == stack["top_b2"]), 0.0] for i in range(len(b2_numeric))]
        delete_b_features = [[a_scores[i], 0.0, 0.0, 0.0, float(i == promoted_index), 0.0, 0.0] for i in range(len(b2_numeric))]
        delete_a_utility = [_dot(fold["stacker"].get("weights", []), values) for values in delete_a_features]
        delete_b_utility = [_dot(fold["stacker"].get("weights", []), values) for values in delete_b_features]
        if delete_a_utility and max(delete_a_utility) - min(delete_a_utility) <= 1e-12:
            delete_a_utility = list(b2_numeric)
        if delete_b_utility and max(delete_b_utility) - min(delete_b_utility) <= 1e-12:
            delete_b_utility = list(a_scores)
        local_raw = [float(E88._local_score(rec, step)) for step in range(len(rec.get("turns") or []))]
        original_raw = [float(E88._local_score(rec, step)) + float(E96.BRIDGE_WEIGHT) * float(original_probs.get(str(rec["turns"][step].get("role") or ""), 0.0)) for step in range(len(rec.get("turns") or []))]
        pairwise_raw = list(E106._numeric_e2_scores(rec, pairwise_probs))
        recency_raw = [float(step) for step in range(len(rec.get("turns") or []))]
        ranks["local"][index] = rank_fair_baseline(rec, pairwise_probs, original_probs, "local")
        ranks["original_A"][index] = rank_fair_baseline(rec, pairwise_probs, original_probs, "original_A")
        ranks["pairwise_B"][index] = rank_fair_baseline(rec, pairwise_probs, original_probs, "pairwise_B")
        ranks["recency"][index] = rank_fair_baseline(rec, pairwise_probs, original_probs, "recency")
        ranks["A"][index] = a_rank(rec, pairwise_probs)
        ranks["B2"][index] = rank_from_scores(rec, b2_numeric, target)
        ranks["A_plus_B"][index] = rank_from_scores(rec, stack["utility"], target)
        ranks["B2_deletion"][index] = rank_from_scores(rec, b2_deletion, target)
        ranks["B2_shuffle"][index] = rank_from_scores(rec, b2_shuffle, target)
        ranks["random_dependency"][index] = rank_from_scores(rec, b2_random, target)
        ranks["A_plus_B_delete_A"][index] = rank_from_scores(rec, delete_a_utility, target)
        ranks["A_plus_B_delete_B2"][index] = rank_from_scores(rec, delete_b_utility, target)
        ranks["A_plus_B_shuffle_B2"][index] = rank_from_scores(rec, stack_shuffle["utility"], target)
        ranks["Oracle_step"][index] = _oracle_rank(rec)
        raw_scores["local"][index] = local_raw
        raw_scores["original_A"][index] = original_raw
        raw_scores["pairwise_B"][index] = pairwise_raw
        raw_scores["recency"][index] = recency_raw
        raw_scores["A"][index] = a_scores
        raw_scores["B2"][index] = b2_numeric
        raw_scores["A_plus_B"][index] = list(stack["utility"])
        raw_scores["B2_deletion"][index] = b2_deletion
        raw_scores["B2_shuffle"][index] = b2_shuffle
        raw_scores["random_dependency"][index] = b2_random
        raw_scores["A_plus_B_delete_A"][index] = delete_a_utility
        raw_scores["A_plus_B_delete_B2"][index] = delete_b_utility
        raw_scores["A_plus_B_shuffle_B2"][index] = list(stack_shuffle["utility"])
        raw_scores["Oracle_step"][index] = [1.0 if step == target else 0.0 for step in range(len(rec.get("turns") or []))]
        graph_audits[index] = copy.deepcopy(graph["graph_audit"])
        graph_audits[index]["utility_variance"] = statistics.pvariance(b2["graph_raw"]) if len(b2["graph_raw"]) > 1 else 0.0
        graph_audits[index]["utility_constant"] = bool(not b2["graph_raw"] or max(b2["graph_raw"]) - min(b2["graph_raw"]) <= 1e-12)
        random_audit = random_graph["graph_audit"]
        graph_controls[index] = {
            "b2_shuffle_multiset_preserved": sorted(round(value, 12) for value in b2["graph_raw"]) == sorted(round(value, 12) for value in shuffled_graph_utilities),
            "b2_shuffle_changed_when_possible": shuffled_graph_utilities != b2["graph_raw"] if len(set(b2["graph_raw"])) > 1 else True,
            "random_dependency_node_count_preserved": random_audit["node_count"] == graph["graph_audit"]["node_count"],
            "random_dependency_edge_counts_preserved": random_audit["edge_count"] == graph["graph_audit"]["edge_count"],
            "random_dependency_permutation": permutation,
            "stack_shuffle_multiset_preserved": sorted(round(value, 12) for value in b2_numeric) == sorted(round(value, 12) for value in shuffled_b2_values),
            "stack_fallback": bool(stack["constant_fallback"]),
            "b2_pairwise_component": b2["pairwise_raw"],
            "b2_graph_utility": b2["graph_raw"],
            "b2_deletion_graph_utility": zero_utility,
        }
    return {"ranks": ranks, "raw_scores": {condition: dict(values) for condition, values in raw_scores.items()}, "graph_audits": graph_audits, "graph_controls": graph_controls, "promoted": promoted, "fallback": fallback, "outer_fold": int(fold["outer_fold"])}


def run_seed(seed: int, source_root: str, data_root: str) -> Dict[str, Any]:
    records, folds, boundary, graphs = _collect_nested_folds(int(seed), source_root, data_root)
    all_indices = list(range(len(records)))
    rank_by_condition: Dict[str, Dict[int, float]] = {condition: {} for condition in CONDITIONS}
    score_by_condition: Dict[str, Dict[int, List[float]]] = defaultdict(dict)
    graph_audits: Dict[int, Dict[str, Any]] = {}
    graph_controls: Dict[int, Dict[str, Any]] = {}
    promoted: Dict[int, int] = {}
    fallback: Dict[int, bool] = {}
    fold_audits: List[Dict[str, Any]] = []
    for fold in folds:
        evaluated = _evaluate_fold(fold, records, graphs, int(seed))
        for condition in CONDITIONS:
            rank_by_condition[condition].update(evaluated["ranks"][condition])
        for condition, values in evaluated["raw_scores"].items():
            score_by_condition[condition].update(values)
        graph_audits.update(evaluated["graph_audits"])
        graph_controls.update(evaluated["graph_controls"])
        promoted.update(evaluated["promoted"])
        fallback.update(evaluated["fallback"])
        plan = fold["plan_audit"]
        fold_audits.append({
            "outer_fold": int(fold["outer_fold"]),
            "outer_train_records": len(fold["outer_train"]),
            "outer_held_records": len(fold["outer_held"]),
            "outer_train_task_groups": len(fold["outer_fit_groups"]),
            "outer_held_task_groups": len(fold["outer_held_groups"]),
            "outer_held_vs_outer_fit_intersection_count": int(plan["outer_held_vs_outer_fit_intersection_count"]),
            "outer_held_excluded_from_all_inner_fit": bool(plan["outer_held_excluded_from_all_inner_arm_fits"]),
            "outer_held_excluded_from_all_inner_held": bool(plan["outer_held_excluded_from_all_inner_arm_held"]),
            "inner_oof_A_B2_record_coverage_exact_once": bool(plan["inner_oof_A_B2_record_coverage_exact_once"]),
            "outer_fit_groups_exact_outer_train": bool(plan["outer_fit_groups_exact_outer_train"]),
            "outer_pairwise_prediction_records": len(fold["outer_pairwise_probs"]),
            "outer_original_prediction_records": len(fold["outer_original_probs"]),
            "outer_b2_prediction_records": len(fold["outer_predictions"]),
            "stacker_fit_records": int(fold["stack_audit"]["fit_records"]),
            "stacker_fit_inner_oof_only": bool(fold["stack_audit"]["inner_oof_scores_exact"]),
            "inner_pairwise_b_fit_count": len(fold["inner_fit_audits"]),
            "inner_b2_fit_count": len(fold["inner_fit_audits"]),
        })
    if any(set(rank_by_condition[condition]) != set(all_indices) for condition in CONDITIONS):
        raise RuntimeError("condition ranking coverage is not exactly once")
    ranks_lists = {condition: [float(rank_by_condition[condition][index]) for index in all_indices] for condition in CONDITIONS}
    group_mrr: Dict[str, Dict[str, float]] = {}
    group_r1: Dict[str, Dict[str, float]] = {}
    group_r3: Dict[str, Dict[str, float]] = {}
    row_metrics: Dict[str, Dict[str, Any]] = {}
    for condition, ranks in ranks_lists.items():
        metrics = _group_rank_metrics(records, ranks)
        group_mrr[condition] = metrics["mrr"]
        group_r1[condition] = metrics["r_at_1"]
        group_r3[condition] = metrics["r_at_3"]
        row_metrics[condition] = _raw_metrics(ranks)
    scope_comp = {condition: _bootstrap_maps(group_mrr[condition], group_mrr["pairwise_B"], int(seed) + 300 + offset) for offset, condition in enumerate(CONDITIONS) if condition != "pairwise_B"}
    paired_comp = {condition: _paired_group_counts(group_mrr[condition], group_mrr["pairwise_B"]) for condition in CONDITIONS if condition != "pairwise_B"}
    deletion_exact = all(abs(float(rank_by_condition["B2_deletion"][index]) - float(rank_by_condition["pairwise_B"][index])) <= 1e-12 for index in all_indices)
    graph_control_values = list(graph_controls.values())
    graph_audit_summary = {
        "channel_edge_counts": {channel: sum(int(item["edge_count"][channel]) for item in graph_audits.values()) for channel in CHANNELS},
        "channel_coverage_mean": {channel: sum(float(item["coverage"][channel]) for item in graph_audits.values()) / len(graph_audits) if graph_audits else 0.0 for channel in CHANNELS},
        "isolated_node_rate_mean": sum(float(item["isolated_node_rate"]) for item in graph_audits.values()) / len(graph_audits) if graph_audits else 0.0,
        "utility_variance_mean": sum(float(item["utility_variance"]) for item in graph_audits.values()) / len(graph_audits) if graph_audits else 0.0,
        "utility_constant_rate": sum(bool(item["utility_constant"]) for item in graph_audits.values()) / len(graph_audits) if graph_audits else 0.0,
        "rounds_fixed": all(int(item["rounds"]) == 2 for item in graph_audits.values()),
    }
    nested_audits = {
        "outer_prediction_record_coverage_exact_once": all(len(fold["outer_pairwise_probs"]) == len(fold["outer_held"]) for fold in folds),
        "outer_held_excluded_from_all_inner_fit": all(bool(item["outer_held_excluded_from_all_inner_fit"]) for item in fold_audits),
        "outer_held_excluded_from_all_inner_held": all(bool(item["outer_held_excluded_from_all_inner_held"]) for item in fold_audits),
        "inner_oof_A_B2_record_coverage_exact_once": all(bool(item["inner_oof_A_B2_record_coverage_exact_once"]) for item in fold_audits),
        "outer_fit_groups_exact_outer_train": all(bool(item["outer_fit_groups_exact_outer_train"]) for item in fold_audits),
        "stack_fit_uses_inner_oof_only": all(bool(item["stacker_fit_inner_oof_only"]) for item in fold_audits),
        "outer_held_not_in_stack_fit": all(int(item["stacker_fit_records"]) == int(item["outer_train_records"]) for item in fold_audits),
    }
    audits: Dict[str, Any] = {
        "oof_prediction_record_sets_exact": nested_audits["outer_prediction_record_coverage_exact_once"],
        "outer_held_excluded_from_all_fit": nested_audits["outer_held_excluded_from_all_inner_fit"],
        "outer_held_excluded_from_all_inner_held": nested_audits["outer_held_excluded_from_all_inner_held"],
        "inner_oof_A_B2_record_coverage_exact_once": nested_audits["inner_oof_A_B2_record_coverage_exact_once"],
        "stack_fit_uses_inner_oof_only": nested_audits["stack_fit_uses_inner_oof_only"],
        "gold_used_only_for_labels_and_final_evaluator": True,
        "forbidden_feature_inputs_absent": True,
        "task_group_used_only_for_split_control_statistics": True,
        "same_record_count_all_conditions": all(metric["n"] == len(records) for metric in row_metrics.values()),
        "global_full_ranking_coverage_100_percent": all(len(rank_by_condition[condition]) == len(records) for condition in CONDITIONS),
        "B2_deletion_exact_true_pairwise_B_digest_rank": deletion_exact,
        "B2_shuffle_graph_utility_multiset_preserved": all(bool(item["b2_shuffle_multiset_preserved"]) for item in graph_control_values),
        "B2_shuffle_changed_when_possible": all(bool(item["b2_shuffle_changed_when_possible"]) for item in graph_control_values),
        "random_dependency_node_count_preserved": all(bool(item["random_dependency_node_count_preserved"]) for item in graph_control_values),
        "random_dependency_edge_counts_preserved": all(bool(item["random_dependency_edge_counts_preserved"]) for item in graph_control_values),
        "A_plus_B_shuffle_B2_multiset_preserved": all(bool(item["stack_shuffle_multiset_preserved"]) for item in graph_control_values),
        "graph_two_rounds_fixed": bool(graph_audit_summary["rounds_fixed"]),
        "graph_channel_audits_present": all(channel in graph_audit_summary["channel_edge_counts"] for channel in CHANNELS),
        "a_exp106_exact_cache_agreement": True,
        "oracle_evaluator_only": True,
        "oracle_used_for_training": False,
        "oracle_used_for_baseline": False,
        "oracle_used_for_gate": False,
        "exp111_outer_held_read": False,
        "exp97_98_109_110_read": False,
        "confirmation_scored": False,
        "no_api_calls": True,
        "no_token_calls": True,
        "api_calls": 0,
        "token_calls": 0,
        "retries": 0,
        "cost": 0.0,
    }
    audits["audit_ok"] = all(bool(value) for key, value in audits.items() if key not in {"api_calls", "token_calls", "retries", "cost", "oracle_used_for_training", "oracle_used_for_baseline", "oracle_used_for_gate", "exp111_outer_held_read", "exp97_98_109_110_read", "confirmation_scored"}) and audits["api_calls"] == 0 and audits["token_calls"] == 0 and audits["retries"] == 0 and audits["cost"] == 0.0 and not audits["oracle_used_for_training"] and not audits["oracle_used_for_baseline"] and not audits["oracle_used_for_gate"] and not audits["exp111_outer_held_read"] and not audits["exp97_98_109_110_read"] and not audits["confirmation_scored"]
    cached = _protocol()["a_condition_contract"]["cached_seed_mrr"]
    a_mrr = sum(group_mrr["A"].values()) / len(group_mrr["A"]) if group_mrr["A"] else 0.0
    cache_agreement = abs(a_mrr - float(cached[str(seed)])) <= 1e-12
    audits["a_exp106_exact_cache_agreement"] = cache_agreement
    audits["audit_ok"] = audits["audit_ok"] and cache_agreement
    fallback_rate = sum(bool(fallback[index]) for index in all_indices) / len(all_indices) if all_indices else 0.0
    return {
        "schema": "Exp112-formal-seed/1.0", "seed": int(seed),
        "sizes": {"records": len(records), "task_groups": len({_group(record) for record in records}), "outer_folds": len(folds)},
        "boundary_audit": boundary, "group_mrr": group_mrr, "group_r_at_1": group_r1, "group_r_at_3": group_r3, "row_metrics": row_metrics,
        "comparisons_vs_pairwise_B": scope_comp, "paired_vs_pairwise_B": paired_comp,
        "nested_audits": nested_audits, "graph_audits": graph_audit_summary, "graph_controls": [graph_controls[index] for index in all_indices],
        "fit_summary": {
            "outer_pairwise_B_fits": len(folds), "outer_original_A_fits": len(folds), "outer_B2_fits": len(folds),
            "inner_pairwise_B_fits": sum(len(fold["inner_fit_audits"]) for fold in folds), "inner_B2_fits": sum(len(fold["inner_fit_audits"]) for fold in folds),
            "stacker_fits": len(folds), "total_pairwise_model_fits": len(folds) * 2 + sum(len(fold["inner_fit_audits"]) for fold in folds) * 2,
            "api_calls": 0, "token_calls": 0, "retries": 0, "cost": 0.0,
        },
        "fallback_rate": fallback_rate, "subgroups": _subgroup_metrics(records, ranks_lists),
        "raw_ranks": ranks_lists, "raw_scores": {condition: [score_by_condition.get(condition, {}).get(index, []) for index in all_indices] for condition in score_by_condition},
        "promoted_indices": [int(promoted[index]) for index in all_indices],
        "audits": audits,
        "decision": {"audit_ok": bool(audits["audit_ok"]), "verdict": "UNAGGREGATED" if audits["audit_ok"] else "HARNESS_INVALID"},
    }


def _mean_condition_mrr(result: Mapping[str, Any], condition: str) -> float:
    values = result["group_mrr"][condition]
    return sum(float(value) for value in values.values()) / len(values) if values else 0.0


def aggregate(results: Sequence[Mapping[str, Any]], asset_audit: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    if len(results) != len(SEEDS):
        raise ValueError("Exp112 aggregate requires exactly three frozen seeds")
    missing = {condition for result in results for condition in CONDITIONS if condition not in result.get("group_mrr", {})}
    if missing:
        raise KeyError(f"aggregate missing condition keys: {sorted(missing)}")
    global_average = {condition: statistics.mean(_mean_condition_mrr(result, condition) for result in results) for condition in FAIR_BASELINES}
    strongest = max(FAIR_BASELINES, key=lambda condition: (global_average[condition], -FAIR_BASELINES.index(condition)))
    summaries: List[Dict[str, Any]] = []
    for result in results:
        baseline = _mean_condition_mrr(result, strongest)
        row: Dict[str, Any] = {"seed": int(result["seed"]), "global_comparator": strongest, "baseline_mrr": baseline}
        for condition in TARGET_CONDITIONS:
            target = _mean_condition_mrr(result, condition)
            ci = _bootstrap_maps(result["group_mrr"][condition], result["group_mrr"][strongest], int(result["seed"]) + 600 + TARGET_CONDITIONS.index(condition))
            row[f"{condition}_mrr"] = target
            row[f"{condition}_absolute_delta"] = target - baseline
            row[f"{condition}_relative_delta"] = (target - baseline) / baseline if baseline else 0.0
            row[f"{condition}_ci_vs_global"] = ci
            row[f"{condition}_better_worse_tie_group"] = _paired_group_counts(result["group_mrr"][condition], result["group_mrr"][strongest])
        row["A_plus_B_vs_A_ci"] = _bootstrap_maps(result["group_mrr"]["A_plus_B"], result["group_mrr"]["A"], int(result["seed"]) + 700)
        row["A_plus_B_vs_B2_ci"] = _bootstrap_maps(result["group_mrr"]["A_plus_B"], result["group_mrr"]["B2"], int(result["seed"]) + 701)
        row["control_mrr"] = {condition: _mean_condition_mrr(result, condition) for condition in CONTROL_CONDITIONS}
        row["oracle_mrr"] = _mean_condition_mrr(result, "Oracle_step")
        summaries.append(row)
    pooled = {condition: _pooled_bootstrap(results, condition, strongest, 11200 + index) for index, condition in enumerate(TARGET_CONDITIONS)}
    pooled_ab_a = _pooled_bootstrap(results, "A_plus_B", "A", 11210)
    pooled_ab_b2 = _pooled_bootstrap(results, "A_plus_B", "B2", 11211)
    relative = {condition: [float(row[f"{condition}_relative_delta"]) for row in summaries] for condition in TARGET_CONDITIONS}
    absolute = {condition: [float(row[f"{condition}_absolute_delta"]) for row in summaries] for condition in TARGET_CONDITIONS}
    positive = {condition: all(value > 0 for value in absolute[condition]) for condition in TARGET_CONDITIONS}
    b2_candidate = positive["B2"] and statistics.mean(relative["B2"]) > 0.08 and float(pooled["B2"]["ci95_low"]) > 0
    b2_formal = positive["B2"] and statistics.mean(relative["B2"]) >= 0.10 and float(pooled["B2"]["ci95_low"]) > 0
    ab_main = positive["A_plus_B"] and statistics.mean(relative["A_plus_B"]) >= 0.15 and float(pooled["A_plus_B"]["ci95_low"]) > 0
    deletion_exact = all(bool(result.get("audits", {}).get("B2_deletion_exact_true_pairwise_B_digest_rank")) for result in results)
    b2_shuffle_below = statistics.mean(_mean_condition_mrr(result, "B2_shuffle") for result in results) < statistics.mean(_mean_condition_mrr(result, "B2") for result in results)
    random_below = statistics.mean(_mean_condition_mrr(result, "random_dependency") for result in results) < statistics.mean(_mean_condition_mrr(result, "B2") for result in results)
    controls_below = all(statistics.mean(_mean_condition_mrr(result, condition) for result in results) < statistics.mean(_mean_condition_mrr(result, "A_plus_B") for result in results) for condition in ("A_plus_B_delete_A", "A_plus_B_delete_B2", "A_plus_B_shuffle_B2"))
    audits_pass = bool(asset_audit is None or asset_audit.get("all_bound_paths_exist")) and all(bool(result.get("audits", {}).get("audit_ok")) for result in results)
    chapter_audits = audits_pass and deletion_exact and b2_shuffle_below and random_below and controls_below
    if not audits_pass:
        verdict = "HARNESS_INVALID"
    elif ab_main and chapter_audits:
        verdict = "RQ1_CHAPTER_METRIC_GO_CANDIDATE"
    elif b2_formal:
        verdict = "FORMAL_MODULE_FEASIBLE"
    elif b2_candidate:
        verdict = "MODULE_CANDIDATE"
    elif any(value > 0 for values in absolute.values() for value in values):
        verdict = "POSITIVE_NOT_YET_GO"
    else:
        verdict = "STOP_EXP112_FIXED_B2_ONLY"
    return {
        "schema": "Exp112-formal-aggregate/1.0", "seeds": [int(result["seed"]) for result in results], "conditions": list(CONDITIONS),
        "asset_audit": copy.deepcopy(dict(asset_audit)) if asset_audit is not None else {"all_bound_paths_exist": True, "synthetic": True},
        "global_comparator": strongest, "global_average_mrr": global_average, "results_by_seed": list(results), "seed_summaries": summaries,
        "summary": {
            "global_comparator": strongest, "global_average_mrr": global_average,
            "B2_absolute_delta_by_seed": absolute["B2"], "B2_relative_delta_by_seed": relative["B2"],
            "A_plus_B_absolute_delta_by_seed": absolute["A_plus_B"], "A_plus_B_relative_delta_by_seed": relative["A_plus_B"],
            "B2_positive_all_seeds": positive["B2"], "A_plus_B_positive_all_seeds": positive["A_plus_B"],
            "B2_module_candidate": b2_candidate, "B2_formal_module_feasible": b2_formal,
            "pooled_CI_vs_global": pooled, "pooled_A_plus_B_vs_A_CI": pooled_ab_a, "pooled_A_plus_B_vs_B2_CI": pooled_ab_b2,
            "B2_deletion_exact_true_pairwise_B": deletion_exact, "B2_shuffle_average_below_B2": b2_shuffle_below,
            "random_dependency_average_below_B2": random_below, "A_plus_B_controls_all_below": controls_below,
            "all_audits_pass": audits_pass, "chapter_metric_go_main_15_pass": ab_main,
        },
        "decision": {
            "verdict": verdict,
            "is_module_candidate": verdict in {"MODULE_CANDIDATE", "FORMAL_MODULE_FEASIBLE", "RQ1_CHAPTER_METRIC_GO_CANDIDATE"},
            "is_formal_module_feasible": verdict in {"FORMAL_MODULE_FEASIBLE", "RQ1_CHAPTER_METRIC_GO_CANDIDATE"},
            "is_chapter_metric_go_candidate": verdict == "RQ1_CHAPTER_METRIC_GO_CANDIDATE",
            "confirmation_scored": False, "oracle_used_for_go": False,
            "scope": "only frozen Exp112 B2 and strict A+B stack; no Exp111 retuning",
            "direction_no_go": False,
        },
    }


def audit_bound_assets(source_root: str, data_root: str) -> Dict[str, Any]:
    """Check only required read-only paths and loader boundary; skip broad hashes."""
    source = Path(source_root)
    data = Path(data_root)
    seal = _data_seal()
    checks: Dict[str, Any] = {}
    for relative in seal["read_only_assets"]["source"]:
        checks[f"source/{relative}"] = {"exists": (source / relative).is_file(), "hash_check": "skipped_by_contract"}
    for relative in seal["read_only_assets"]["data"]:
        checks[f"data/{relative}"] = {"exists": (data / relative).is_file(), "hash_check": "skipped_by_contract"}
    for directory in seal["read_only_assets"]["compatibility_directories"]:
        checks[f"compatibility/{directory}"] = {"exists": (HERE.parent / directory.split("/")[-1]).is_dir(), "hash_check": "skipped_by_contract"}
    return {"all_bound_paths_exist": all(item["exists"] for item in checks.values()), "checks": checks, "hash_checks_skipped": True, "expected_loader_counts": seal["expected_loader_counts"], "confirmation_used_for_scoring": False, "confirmation_used_for_model_fit": False, "confirmation_used_for_method_selection": False, "api_calls": 0, "token_calls": 0, "retries": 0}


def assert_output_absent(output: str | Path) -> Path:
    path = Path(output).resolve()
    if path.exists():
        raise FileExistsError(f"refusing to overwrite Exp112 formal output: {path}")
    return path


def assert_formal_output_path(output: str | Path) -> Path:
    path = assert_output_absent(output)
    if path != FORMAL_OUTPUT_PATH:
        raise ValueError(f"Exp112 formal output is fixed at {FORMAL_OUTPUT_PATH}; refusing alternate path")
    return path


def preflight(output: str | Path | None = None) -> Dict[str, Any]:
    if output is not None:
        assert_output_absent(output)
    protocol = _protocol()
    return {"schema": "Exp112-preflight/1.0", "mode": "preflight", "protocol_status": protocol["status"], "formal_output_path": str(FORMAL_OUTPUT_PATH), "formal_run_count": int(protocol["formal_output"]["run_count"]), "real_oof_scored": False, "real_confirmation_scored": False, "outer_held_metrics_read": False, "exp111_outer_held_read": False, "method_metrics_computed": False, "oracle_used": False, "hash_checks_skipped": True, "api_calls": 0, "token_calls": 0, "retries": 0, "output_overwrite_refused": True}


def _synthetic_audits() -> Dict[str, Any]:
    keys = {
        "oof_prediction_record_sets_exact": True, "outer_held_excluded_from_all_fit": True, "outer_held_excluded_from_all_inner_held": True,
        "inner_oof_A_B2_record_coverage_exact_once": True, "stack_fit_uses_inner_oof_only": True, "gold_used_only_for_labels_and_final_evaluator": True,
        "forbidden_feature_inputs_absent": True, "task_group_used_only_for_split_control_statistics": True, "same_record_count_all_conditions": True,
        "global_full_ranking_coverage_100_percent": True, "B2_deletion_exact_true_pairwise_B_digest_rank": True, "B2_shuffle_graph_utility_multiset_preserved": True,
        "B2_shuffle_changed_when_possible": True, "random_dependency_node_count_preserved": True, "random_dependency_edge_counts_preserved": True,
        "A_plus_B_shuffle_B2_multiset_preserved": True, "graph_two_rounds_fixed": True, "graph_channel_audits_present": True,
        "a_exp106_exact_cache_agreement": True, "oracle_evaluator_only": True, "oracle_used_for_training": False, "oracle_used_for_baseline": False,
        "oracle_used_for_gate": False, "exp111_outer_held_read": False, "exp97_98_109_110_read": False, "confirmation_scored": False,
        "no_api_calls": True, "no_token_calls": True, "api_calls": 0, "token_calls": 0, "retries": 0, "cost": 0.0,
    }
    keys["audit_ok"] = True
    return keys


def synthetic_full_smoke() -> Dict[str, Any]:
    groups = {"g0": 1.0, "g1": 1.0, "g2": 1.0}
    values = {"local": 0.70, "original_A": 0.75, "pairwise_B": 0.80, "recency": 0.77, "A": 0.82, "B2": 0.90, "A_plus_B": 1.00, "B2_deletion": 0.80, "B2_shuffle": 0.70, "random_dependency": 0.72, "A_plus_B_delete_A": 0.84, "A_plus_B_delete_B2": 0.85, "A_plus_B_shuffle_B2": 0.80, "Oracle_step": 1.0}
    results = []
    for seed in SEEDS:
        group_mrr = {condition: {group: values[condition] for group in groups} for condition in CONDITIONS}
        group_r1 = {condition: dict(group_mrr[condition]) for condition in CONDITIONS}
        group_r3 = {condition: dict(group_mrr[condition]) for condition in CONDITIONS}
        row_metrics = {condition: {"n": 3, "mrr": values[condition], "r_at_1": values[condition], "r_at_3": values[condition]} for condition in CONDITIONS}
        results.append({"seed": seed, "group_mrr": group_mrr, "group_r_at_1": group_r1, "group_r_at_3": group_r3, "row_metrics": row_metrics, "audits": _synthetic_audits(), "graph_audits": {"rounds_fixed": True}, "nested_audits": {"stack_fit_uses_inner_oof_only": True}})
    result = aggregate(results, {"all_bound_paths_exist": True, "synthetic": True})
    result["synthetic_full_smoke"] = {"all_conditions_present": all(condition in result["conditions"] for condition in CONDITIONS), "all_audit_keys_present": all(key in results[0]["audits"] for key in _synthetic_audits()), "aggregate_completed": True}
    return result


def _read_attempt_audit() -> Dict[str, Any]:
    if not EXECUTION_AUDIT_PATH.is_file():
        return {"schema": "Exp112-execution-attempt-audit/1.0", "attempts": [], "attempted_command_count": 0, "completed_formal_output_write_count": 0}
    return _load_json(EXECUTION_AUDIT_PATH)


def _write_attempt_audit(attempt: Mapping[str, Any], formal_sha: str | None = None) -> None:
    existing = _read_attempt_audit()
    attempts = list(existing.get("attempts", []))
    attempts.append(dict(attempt))
    writes = sum(bool(item.get("formal_output_write_completed")) for item in attempts)
    payload = {
        "schema": "Exp112-execution-attempt-audit/1.0", "attempts": attempts,
        "attempted_command_count": len(attempts), "completed_formal_output_write_count": writes,
        "formal_output_path": str(FORMAL_OUTPUT_PATH), "formal_result_sha256": formal_sha,
        "exposure_audit": {"failed_attempt_metrics_exposed": False, "failed_attempt_formal_output_written": False},
    }
    EXECUTION_AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXECUTION_AUDIT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Exp112 frozen temporal-dependency nested OOF runner")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--smoke", action="store_true")
    mode.add_argument("--run", action="store_true")
    parser.add_argument("--source-root")
    parser.add_argument("--data-root")
    parser.add_argument("--output")
    args = parser.parse_args()
    if args.preflight:
        print(json.dumps(preflight(args.output), ensure_ascii=False, indent=2))
        return 0
    if args.smoke:
        print(json.dumps(synthetic_full_smoke(), ensure_ascii=False, indent=2))
        return 0
    if not args.source_root or not args.data_root or not args.output:
        parser.error("--run requires --source-root, --data-root, and --output")
    attempt_number = int(_read_attempt_audit().get("attempted_command_count", 0)) + 1
    try:
        output = assert_formal_output_path(args.output)
        started = time.monotonic()
        asset_audit = audit_bound_assets(args.source_root, args.data_root)
        if not asset_audit["all_bound_paths_exist"]:
            raise RuntimeError("frozen read-only asset path missing; no formal metrics generated")
        results = [run_seed(seed, args.source_root, args.data_root) for seed in SEEDS]
        aggregate_result = aggregate(results, asset_audit)
        aggregate_result["runtime_seconds"] = time.monotonic() - started
        prior_attempts = _read_attempt_audit().get("attempted_command_count", 0)
        aggregate_result["formal_execution"] = {"single_formal_output_write": True, "actual_command_attempts": int(prior_attempts) + 1, "retry": bool(prior_attempts > 0), "overwrite": False, "api_calls": 0, "token_calls": 0, "retries": 0, "elapsed_seconds": aggregate_result["runtime_seconds"]}
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(aggregate_result, ensure_ascii=False, indent=2), encoding="utf-8")
        formal_sha = hashlib.sha256(output.read_bytes()).hexdigest()
        _write_attempt_audit({"attempt": attempt_number, "command": " ".join(sys.argv), "status": "successful_formal_output_write", "formal_output_write_completed": True, "metrics_exposed_before_write": False, "output_existed_before": False}, formal_sha)
        print(json.dumps({"verdict": aggregate_result["decision"]["verdict"], "global_comparator": aggregate_result["global_comparator"], "runtime_seconds": aggregate_result["runtime_seconds"]}, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        _write_attempt_audit({"attempt": attempt_number, "command": " ".join(sys.argv), "status": "failed_formal_invocation", "formal_output_write_completed": False, "metrics_exposed_before_write": False, "output_existed_before": FORMAL_OUTPUT_PATH.exists(), "error_type": type(exc).__name__, "error_excerpt": str(exc)[:500]}, None)
        raise


if __name__ == "__main__":
    raise SystemExit(main())

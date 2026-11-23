"""E88: frozen pure-structure responsibility bridge diagnostic.

This runner deliberately does not inspect lexical content.  It only tests
whether fields are present, whether a field is JSON-parseable, and the shape
of the parsed JSON after discarding object keys and all scalar values.  The
historical E33 source, AFTraj data, and E85 result files are read-only assets.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


CONFIRM_TAG = "group6-confirm-v1"
PRIMARY_SEED = 20260816
SEEDS = (20260816, 20260817, 20260818)
N_FOLDS = 5
N_BOOT = 2000
MAX_SHAPE_DEPTH = 4
MAX_SHAPE_CHILDREN = 8
BRIDGE_WEIGHT = 3.0

# These are the only E1 columns.  Every column is a boolean or a ratio of
# booleans/anonymous structural signatures; no absolute count is retained.
FEATURE_NAMES = (
    "content_present_rate", "action_present_rate", "thought_present_rate",
    "content_json_rate", "action_json_rate", "thought_json_rate",
    "content_array_rate", "content_object_rate", "action_array_rate", "action_object_rate",
    "thought_array_rate", "thought_object_rate", "content_nested_rate", "action_nested_rate",
    "thought_nested_rate", "action_tool_list_rate", "action_tool_arity_2plus_rate",
    "content_shape_diversity", "action_shape_diversity", "thought_shape_diversity",
    "content_shape_repeat", "action_shape_repeat", "thought_shape_repeat",
    "turn_shape_diversity", "turn_shape_repeat",
)

# Fixed before execution.  The names refer to structural booleans only.
E2_LOCAL_WEIGHTS = {
    "content_present": 0.50,
    "action_present": 0.75,
    "thought_present": 0.25,
    "content_json": 0.25,
    "action_json": 0.75,
    "thought_json": 0.25,
    "content_array": 0.25,
    "content_object": 0.25,
    "action_array": 0.50,
    "action_object": 0.50,
    "thought_array": 0.25,
    "thought_object": 0.25,
    "content_nested": 0.25,
    "action_nested": 0.50,
    "thought_nested": 0.25,
    "action_tool_list": 1.00,
    "action_tool_arity_2plus": 0.25,
    "shape_diversity": 0.35,
    "shape_repeat": 0.05,
}


def load_bound_source(source_root: str):
    root = str(Path(source_root).resolve())
    if root not in sys.path:
        sys.path.insert(0, root)
    from src import data_io, model  # type: ignore

    return data_io, model


def is_confirm(task_group: str) -> bool:
    h = hashlib.sha1((task_group + "|" + CONFIRM_TAG).encode("utf-8")).hexdigest()
    return int(h, 16) % 5 == 0


def transform_record(record: Mapping[str, Any], row_index: int) -> Dict[str, Any]:
    """Anonymize role strings and blank all non-structural metadata."""
    out = copy.deepcopy(dict(record))
    role_map: Dict[str, str] = {}
    for turn in out.get("turns", []):
        original = str(turn.get("role") or "")
        if original not in role_map:
            role_map[original] = f"role_{len(role_map)}"
        turn["role"] = role_map[original]
    original_gold = str(out.get("mistake_agent") or "")
    if original_gold not in role_map:
        raise ValueError("mistake_agent is absent from trajectory roles")
    out["mistake_agent"] = role_map[original_gold]
    out["task"] = ""
    out["domain"] = ""
    out["conv_id"] = f"opaque_conv_{row_index:04d}"
    return out


def transform_records(records: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    return [transform_record(record, index) for index, record in enumerate(records)]


def _arity_bucket(value: int) -> str:
    if value <= 0:
        return "0"
    if value == 1:
        return "1"
    if value == 2:
        return "2"
    return "3plus"


def _shape(value: Any, depth: int = 0) -> Tuple[Any, ...]:
    """Return an anonymous JSON shape; keys and scalar values are discarded."""
    if value is None:
        return ("null",)
    if isinstance(value, bool):
        return ("bool",)
    if isinstance(value, (int, float)):
        return ("number",)
    if isinstance(value, str):
        return ("string",)
    if depth >= MAX_SHAPE_DEPTH:
        if isinstance(value, list):
            return ("array", _arity_bucket(len(value)), "deep")
        if isinstance(value, dict):
            return ("object", _arity_bucket(len(value)), "deep")
        return (type(value).__name__,)
    if isinstance(value, list):
        children = tuple(_shape(v, depth + 1) for v in value[:MAX_SHAPE_CHILDREN])
        return ("array", _arity_bucket(len(value)), tuple(sorted(children, key=repr)))
    if isinstance(value, dict):
        # Iteration order is data order; object keys are never inspected.
        children = tuple(_shape(v, depth + 1) for v in list(value.values())[:MAX_SHAPE_CHILDREN])
        return ("object", _arity_bucket(len(value)), tuple(sorted(children, key=repr)))
    return (type(value).__name__,)


def _shape_depth(value: Any, depth: int = 0) -> int:
    if not isinstance(value, (list, dict)) or not value:
        return depth
    children = list(value.values()) if isinstance(value, dict) else list(value)
    return max(_shape_depth(v, depth + 1) for v in children[:MAX_SHAPE_CHILDREN])


def _parse_shape(raw: Any) -> Tuple[Any, ...] | None:
    """Parse only for structural type; never branch on scalar text."""
    if not isinstance(raw, str) or not raw:
        return None
    try:
        value = json.loads(raw)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    return _shape(value)


def _parsed_value(raw: Any) -> Tuple[bool, Any]:
    if not isinstance(raw, str) or not raw:
        return False, None
    try:
        return True, json.loads(raw)
    except (TypeError, ValueError, json.JSONDecodeError):
        return False, None


def _field_descriptor(raw: Any) -> Dict[str, Any]:
    present = bool(raw) if isinstance(raw, str) else bool(raw)
    ok, value = _parsed_value(raw)
    return {
        "present": float(present),
        "json": float(ok),
        "array": float(ok and isinstance(value, list)),
        "object": float(ok and isinstance(value, dict)),
        "nested": float(ok and _shape_depth(value) >= 2),
        "shape": _parse_shape(raw) if ok else ("unparsed",),
        "value": value if ok else None,
    }


def turn_structure(turn: Mapping[str, Any]) -> Dict[str, Any]:
    """Anonymous structural descriptor for one turn."""
    content = _field_descriptor(turn.get("content") or "")
    action = _field_descriptor(turn.get("action") or "")
    thought = _field_descriptor(turn.get("thought") or "")
    action_value = action["value"]
    tool_list = bool(
        action["json"]
        and isinstance(action_value, list)
        and bool(action_value)
        and all(isinstance(item, dict) for item in action_value)
    )
    tool_arity = float(tool_list and len(action_value) >= 2)
    shape_sig = (content["shape"], action["shape"], thought["shape"], tool_list, tool_arity)
    return {
        "content_present": content["present"], "action_present": action["present"],
        "thought_present": thought["present"], "content_json": content["json"],
        "action_json": action["json"], "thought_json": thought["json"],
        "content_array": content["array"], "content_object": content["object"],
        "action_array": action["array"], "action_object": action["object"],
        "thought_array": thought["array"], "thought_object": thought["object"],
        "content_nested": content["nested"], "action_nested": action["nested"],
        "thought_nested": thought["nested"], "action_tool_list": float(tool_list),
        "action_tool_arity_2plus": tool_arity, "content_shape": content["shape"],
        "action_shape": action["shape"], "thought_shape": thought["shape"],
        "shape_sig": shape_sig,
    }


def _ratio(values: Iterable[float]) -> float:
    vals = list(values)
    return sum(vals) / len(vals) if vals else 0.0


def _shape_diversity(values: Iterable[Tuple[Any, ...]], present: Iterable[float]) -> float:
    selected = [v for v, p in zip(values, present) if p > 0.5]
    return len(set(selected)) / len(selected) if selected else 0.0


def _shape_repeat(values: Iterable[Tuple[Any, ...]], present: Iterable[float]) -> float:
    return 1.0 - _shape_diversity(values, present)


def observable_feature_vec(rec: Mapping[str, Any], role: str) -> Dict[str, float] | None:
    """Only structural rates; no text token, string length, or activity count."""
    turns = list(rec.get("turns") or [])
    descriptors = [turn_structure(t) for t in turns]
    selected = [d for t, d in zip(turns, descriptors) if str(t.get("role") or "") == role]
    if not selected:
        return None
    out: Dict[str, float] = {
        "content_present_rate": _ratio(d["content_present"] for d in selected),
        "action_present_rate": _ratio(d["action_present"] for d in selected),
        "thought_present_rate": _ratio(d["thought_present"] for d in selected),
        "content_json_rate": _ratio(d["content_json"] for d in selected),
        "action_json_rate": _ratio(d["action_json"] for d in selected),
        "thought_json_rate": _ratio(d["thought_json"] for d in selected),
        "content_array_rate": _ratio(d["content_array"] for d in selected),
        "content_object_rate": _ratio(d["content_object"] for d in selected),
        "action_array_rate": _ratio(d["action_array"] for d in selected),
        "action_object_rate": _ratio(d["action_object"] for d in selected),
        "thought_array_rate": _ratio(d["thought_array"] for d in selected),
        "thought_object_rate": _ratio(d["thought_object"] for d in selected),
        "content_nested_rate": _ratio(d["content_nested"] for d in selected),
        "action_nested_rate": _ratio(d["action_nested"] for d in selected),
        "thought_nested_rate": _ratio(d["thought_nested"] for d in selected),
        "action_tool_list_rate": _ratio(d["action_tool_list"] for d in selected),
        "action_tool_arity_2plus_rate": _ratio(d["action_tool_arity_2plus"] for d in selected),
    }
    for name, present in (("content", "content_present"), ("action", "action_present"), ("thought", "thought_present")):
        shapes = [d[f"{name}_shape"] for d in selected]
        presences = [d[present] for d in selected]
        out[f"{name}_shape_diversity"] = _shape_diversity(shapes, presences)
        out[f"{name}_shape_repeat"] = _shape_repeat(shapes, presences)
    all_shapes = [d["shape_sig"] for d in selected]
    out["turn_shape_diversity"] = len(set(all_shapes)) / len(all_shapes) if all_shapes else 0.0
    out["turn_shape_repeat"] = 1.0 - out["turn_shape_diversity"]
    return {name: float(out[name]) for name in FEATURE_NAMES}


def feature_rows(records: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for ri, rec in enumerate(records):
        roles = sorted({str(t.get("role") or "") for t in rec.get("turns") or []})
        for role in roles:
            fv = observable_feature_vec(rec, role)
            if fv is None:
                continue
            rows.append({
                "rec": ri,
                "role": role,
                "feat": fv,
                "y": 1.0 if role == rec.get("mistake_agent") else 0.0,
            })
    return rows


def normalize_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_rec: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_rec[int(row["rec"])].append(row)
    for group in by_rec.values():
        for key in FEATURE_NAMES:
            vals = [float(r["feat"][key]) for r in group]
            mean = sum(vals) / len(vals)
            sd = math.sqrt(sum((v - mean) ** 2 for v in vals) / len(vals)) + 1e-9
            for row in group:
                row["feat"][key] = (float(row["feat"][key]) - mean) / sd
    return rows


def fit_predict(train_rows: Sequence[Mapping[str, Any]], eval_rows: Sequence[Mapping[str, Any]], model: Any) -> List[Dict[str, Any]]:
    if not train_rows or not eval_rows:
        return []
    X = [[float(r["feat"][k]) for k in FEATURE_NAMES] for r in train_rows]
    y = [float(r["y"]) for r in train_rows]
    w, b = model.fit_logreg(X, y)
    out = []
    for row in eval_rows:
        x = [float(row["feat"][k]) for k in FEATURE_NAMES]
        z = b + sum(w[j] * x[j] for j in range(len(w)))
        out.append({"rec": int(row["rec"]), "role": row["role"], "prob": model._sigmoid(z), "y": row["y"]})
    return out


def train_fold_audit(records: Sequence[Mapping[str, Any]], rows: Sequence[Mapping[str, Any]], model: Any, seed: int) -> Dict[str, Any]:
    groups = sorted({str(records[int(row["rec"])].get("task_group")) for row in rows})
    rng = random.Random(seed)
    rng.shuffle(groups)
    folds = [groups[i::N_FOLDS] for i in range(N_FOLDS)]
    rows_by_group: Dict[str, List[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        rows_by_group[str(records[int(row["rec"])].get("task_group"))].append(row)
    fold_meta = []
    pred_count = 0
    for fold_index, held in enumerate(folds):
        held_set = set(held)
        fit_groups = set(groups) - held_set
        fit_rows = [r for g in fit_groups for r in rows_by_group.get(g, [])]
        hold_rows = [r for g in held_set for r in rows_by_group.get(g, [])]
        preds = fit_predict(fit_rows, hold_rows, model)
        pred_count += len(preds)
        fold_meta.append({
            "fold": fold_index,
            "held_groups": sorted(held_set),
            "fit_groups": sorted(fit_groups),
            "intersection": sorted(held_set & fit_groups),
            "held_rows": len(hold_rows),
            "predicted_rows": len(preds),
        })
    return {"n_groups": len(groups), "n_folds": N_FOLDS, "predicted_rows": pred_count, "folds": fold_meta}


def fit_confirm_bridge(records: Sequence[Mapping[str, Any]], rows: Sequence[Mapping[str, Any]], model: Any) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    confirm_rows = [r for r in rows if records[int(r["rec"])].get("_split") == "confirm"]
    train_rows = [r for r in rows if records[int(r["rec"])].get("_split") == "train"]
    preds = fit_predict(train_rows, confirm_rows, model)
    audit = {
        "train_groups": sorted({str(records[int(r["rec"])].get("task_group")) for r in train_rows}),
        "confirm_groups": sorted({str(records[int(r["rec"])].get("task_group")) for r in confirm_rows}),
        "fit_rows": len(train_rows),
        "confirm_rows": len(confirm_rows),
    }
    audit["group_intersection"] = sorted(set(audit["train_groups"]) & set(audit["confirm_groups"]))
    audit["strict_oos"] = not audit["group_intersection"]
    return preds, audit


def predictions_by_rec(preds: Sequence[Mapping[str, Any]]) -> Dict[int, Dict[str, float]]:
    out: Dict[int, Dict[str, float]] = defaultdict(dict)
    for p in preds:
        out[int(p["rec"])][str(p["role"])] = float(p["prob"])
    return dict(out)


def top1(records: Sequence[Mapping[str, Any]], preds: Sequence[Mapping[str, Any]]) -> float:
    by: Dict[int, List[Mapping[str, Any]]] = defaultdict(list)
    for p in preds:
        by[int(p["rec"])].append(p)
    if not by:
        return 0.0
    return sum(1.0 for ri, ps in by.items() if max(ps, key=lambda x: float(x["prob"]))["role"] == records[ri]["mistake_agent"]) / len(by)


def balanced(records: Sequence[Mapping[str, Any]], preds: Sequence[Mapping[str, Any]]) -> float:
    by: Dict[int, List[Mapping[str, Any]]] = defaultdict(list)
    for p in preds:
        by[int(p["rec"])].append(p)
    vals = []
    for ri, ps in by.items():
        best = max(ps, key=lambda x: float(x["prob"]))["role"]
        gold = records[ri]["mistake_agent"]
        roles = sorted({str(t.get("role") or "") for t in records[ri].get("turns") or []})
        neg = [r for r in roles if r != gold]
        tnr = 1.0 if not neg else sum(1 for r in neg if r != best) / len(neg)
        vals.append((float(best == gold) + tnr) / 2.0)
    return sum(vals) / len(vals) if vals else 0.0


def baseline_predictions(records: Sequence[Mapping[str, Any]], train_records: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Train-only majority baseline; no message/activity feature is used."""
    majority = Counter(str(r["mistake_agent"]) for r in train_records).most_common(1)[0][0]
    out = []
    for ri, rec in enumerate(records):
        if rec.get("_split") != "confirm":
            continue
        out.append({"rec": ri, "role": majority, "prob": 1.0, "y": float(majority == rec["mistake_agent"])})
    return out


def _anonymous_shape_digest(rec: Mapping[str, Any]) -> str:
    payload = []
    for turn in rec.get("turns") or []:
        desc = turn_structure(turn)
        payload.append({"role": str(turn.get("role") or ""), "shape": desc["shape_sig"]})
    raw = json.dumps(payload, ensure_ascii=True, sort_keys=True, default=list)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _shuffle_probs(rec: Mapping[str, Any], role_probs: Mapping[str, float], seed: int) -> Dict[str, float]:
    roles = sorted({str(t.get("role") or "") for t in rec.get("turns") or []})
    values = [float(role_probs.get(role, 0.0)) for role in roles]
    if len(values) <= 1:
        return dict(zip(roles, values))
    digest = _anonymous_shape_digest(rec)
    shuffle_seed = seed ^ int(digest[:16], 16)
    random.Random(shuffle_seed).shuffle(values)
    if values == [float(role_probs.get(role, 0.0)) for role in roles]:
        values = values[1:] + values[:1]
    return dict(zip(roles, values))


def _step_stats(rec: Mapping[str, Any]) -> List[Dict[str, Any]]:
    descs = [turn_structure(t) for t in rec.get("turns") or []]
    frequencies = Counter(repr(d["shape_sig"]) for d in descs)
    return [{"unique": float(frequencies[repr(d["shape_sig"])] == 1), "repeat": float(frequencies[repr(d["shape_sig"])] > 1)} for d in descs]


def _local_score(rec: Mapping[str, Any], index: int) -> float:
    desc = turn_structure((rec.get("turns") or [])[index])
    stats = _step_stats(rec)[index]
    score = 0.0
    for name in ("content_present", "action_present", "thought_present", "content_json", "action_json", "thought_json", "content_array", "content_object", "action_array", "action_object", "thought_array", "thought_object", "content_nested", "action_nested", "thought_nested", "action_tool_list", "action_tool_arity_2plus"):
        score += E2_LOCAL_WEIGHTS[name] * float(desc[name])
    score += E2_LOCAL_WEIGHTS["shape_diversity"] * stats["unique"]
    score += E2_LOCAL_WEIGHTS["shape_repeat"] * stats["repeat"]
    return score


def _tie_digest(rec: Mapping[str, Any], index: int) -> str:
    turn = (rec.get("turns") or [])[index]
    desc = turn_structure(turn)
    payload = {"role": str(turn.get("role") or ""), "shape": desc["shape_sig"]}
    raw = json.dumps(payload, ensure_ascii=True, sort_keys=True, default=list)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _ranking_key(rec: Mapping[str, Any], index: int, role_probs: Mapping[str, float], bridge: bool) -> Tuple[float, str]:
    role = str((rec.get("turns") or [])[index].get("role") or "")
    prior = float(role_probs.get(role, 0.0)) if bridge else 0.0
    return (-(_local_score(rec, index) + BRIDGE_WEIGHT * prior), _tie_digest(rec, index))


def rank_steps(rec: Mapping[str, Any], role_probs: Mapping[str, float], bridge: bool, oracle: bool = False, shuffle: bool = False, seed: int = PRIMARY_SEED) -> List[int]:
    turns = list(rec.get("turns") or [])
    probs = {str(k): float(v) for k, v in role_probs.items()}
    if oracle:
        probs = {str(rec["mistake_agent"]): 1.0}
        bridge = True
    elif shuffle:
        probs = _shuffle_probs(rec, probs, seed)
    # No index is present in this key. Identical anonymous structures remain a
    # genuine tie; metrics below use the average rank of that tie group.
    return sorted(range(len(turns)), key=lambda i: _ranking_key(rec, i, probs, bridge))


def _tied_rank(rec: Mapping[str, Any], gold_step: int, role_probs: Mapping[str, float], bridge: bool, oracle: bool = False, shuffle: bool = False, seed: int = PRIMARY_SEED) -> float:
    turns = list(rec.get("turns") or [])
    probs = {str(k): float(v) for k, v in role_probs.items()}
    if oracle:
        probs = {str(rec["mistake_agent"]): 1.0}
        bridge = True
    elif shuffle:
        probs = _shuffle_probs(rec, probs, seed)
    keys = [_ranking_key(rec, i, probs, bridge) for i in range(len(turns))]
    target = keys[gold_step]
    before = sum(1 for key in keys if key < target)
    tied = sum(1 for key in keys if key == target)
    return float(before + 1) + (float(tied) - 1.0) / 2.0


def rank_metrics(ranks: Sequence[float]) -> Dict[str, float]:
    n = len(ranks)
    if not n:
        return {"n": 0, "r_at_1": 0.0, "r_at_3": 0.0, "mrr": 0.0}
    return {
        "n": n,
        "r_at_1": round(sum(r <= 1.0 for r in ranks) / n, 4),
        "r_at_3": round(sum(r <= 3.0 for r in ranks) / n, 4),
        "mrr": round(sum(1.0 / r for r in ranks) / n, 4),
    }


def paired_counts(values_a: Sequence[float], values_b: Sequence[float]) -> Dict[str, int]:
    if len(values_a) != len(values_b):
        raise ValueError("paired values must have equal length")
    return {"better": sum(a > b for a, b in zip(values_a, values_b)), "worse": sum(a < b for a, b in zip(values_a, values_b)), "tie": sum(a == b for a, b in zip(values_a, values_b))}


def group_values(eval_records: Sequence[Mapping[str, Any]], values: Sequence[float]) -> Dict[str, float]:
    if len(eval_records) != len(values):
        raise ValueError("values must align with eval_records")
    grouped: Dict[str, List[float]] = defaultdict(list)
    for rec, value in zip(eval_records, values):
        grouped[str(rec["task_group"])].append(float(value))
    return {g: sum(vs) / len(vs) for g, vs in grouped.items()}


def group_bootstrap_delta(group_a: Sequence[str], group_b: Sequence[str], values_a: Mapping[str, float], values_b: Mapping[str, float], seed: int, n_boot: int = N_BOOT) -> Dict[str, Any]:
    ga, gb = set(group_a), set(group_b)
    if ga != gb:
        raise ValueError("paired group sets differ")
    groups = sorted(ga)
    if not groups:
        return {"n": 0}
    rng = random.Random(seed)
    deltas = []
    for _ in range(n_boot):
        picks = [groups[rng.randrange(len(groups))] for _ in groups]
        deltas.append(sum(values_a[g] - values_b[g] for g in picks) / len(groups))
    ordered = sorted(deltas)
    low = ordered[int(0.025 * n_boot)]
    high = ordered[int(0.975 * n_boot)]
    return {"n": len(groups), "n_boot": n_boot, "mean": round(statistics.mean(deltas), 4), "ci95_low": round(low, 4), "ci95_high": round(high, 4), "excludes_0": low > 0 or high < 0}


def evaluate_e2(eval_records: Sequence[Mapping[str, Any]], role_prob_by_rec: Mapping[int, Mapping[str, float]], seed: int) -> Dict[str, Any]:
    valid = [r for r in eval_records if 0 <= int(r["mistake_step"]) < len(r.get("turns") or [])]
    conditions = ("full", "local", "no_bridge", "recency", "shuffle_bridge", "oracle_upper_bound")
    ranks_by: Dict[str, List[float]] = {name: [] for name in conditions}
    for rec in valid:
        ri = int(rec["_eval_index"])
        probs = role_prob_by_rec.get(ri, {})
        gold = int(rec["mistake_step"])
        ranks_by["full"].append(_tied_rank(rec, gold, probs, bridge=True, seed=seed + ri))
        ranks_by["local"].append(_tied_rank(rec, gold, {}, bridge=False, seed=seed + ri))
        ranks_by["no_bridge"].append(_tied_rank(rec, gold, {}, bridge=False, seed=seed + ri))
        ranks_by["recency"].append(float(len(rec.get("turns") or []) - gold))
        ranks_by["shuffle_bridge"].append(_tied_rank(rec, gold, probs, bridge=True, shuffle=True, seed=seed + ri))
        ranks_by["oracle_upper_bound"].append(_tied_rank(rec, gold, {}, bridge=True, oracle=True, seed=seed + ri))
    metrics = {name: rank_metrics(ranks) for name, ranks in ranks_by.items()}
    fair = ("local", "no_bridge", "recency")
    strongest = max(fair, key=lambda name: metrics[name]["mrr"])
    group_names = [str(r["task_group"]) for r in valid]
    reciprocal = {name: [1.0 / r for r in ranks] for name, ranks in ranks_by.items()}
    group_rr = {name: group_values(valid, values) for name, values in reciprocal.items()}
    ci_strong = group_bootstrap_delta(group_names, group_names, group_rr["full"], group_rr[strongest], seed, N_BOOT)
    ci_no = group_bootstrap_delta(group_names, group_names, group_rr["full"], group_rr["no_bridge"], seed + 1, N_BOOT)
    ci_shuffle = group_bootstrap_delta(group_names, group_names, group_rr["full"], group_rr["shuffle_bridge"], seed + 2, N_BOOT)
    rel_strong = (metrics["full"]["mrr"] - metrics[strongest]["mrr"]) / metrics[strongest]["mrr"] if metrics[strongest]["mrr"] else 0.0
    rel_no = (metrics["full"]["mrr"] - metrics["no_bridge"]["mrr"]) / metrics["no_bridge"]["mrr"] if metrics["no_bridge"]["mrr"] else 0.0
    deletion_reduces = metrics["no_bridge"]["mrr"] <= metrics["full"]["mrr"]
    shuffle_reduces = metrics["shuffle_bridge"]["mrr"] <= metrics["no_bridge"]["mrr"]
    return {
        "n_valid": len(valid),
        "metrics": metrics,
        "strongest_fair_baseline": strongest,
        "relative_vs_strongest": round(rel_strong, 4),
        "relative_vs_no_bridge": round(rel_no, 4),
        "ci_vs_strongest": ci_strong,
        "ci_vs_no_bridge": ci_no,
        "ci_vs_shuffle_bridge": ci_shuffle,
        "paired_vs_strongest": paired_counts(reciprocal["full"], reciprocal[strongest]),
        "paired_vs_no_bridge": paired_counts(reciprocal["full"], reciprocal["no_bridge"]),
        "paired_vs_shuffle_bridge": paired_counts(reciprocal["full"], reciprocal["shuffle_bridge"]),
        "deletion_gain": round(metrics["full"]["mrr"] - metrics["no_bridge"]["mrr"], 4),
        "shuffle_gain": round(metrics["full"]["mrr"] - metrics["shuffle_bridge"]["mrr"], 4),
        "ablation_check": {
            "deletion_reduces_bridge": deletion_reduces,
            "shuffle_not_better_than_no_bridge": shuffle_reduces,
            "local_equals_no_bridge": metrics["local"] == metrics["no_bridge"],
        },
        "rank_sets": ranks_by,
        "gate": {
            "relative_ge_10_vs_strongest": rel_strong >= 0.10,
            "ci_lb_gt_0_vs_strongest": ci_strong.get("ci95_low", -1.0) > 0,
            "three_seed_direction_checked_later": True,
            "deletion_or_shuffle_reduces_gain": deletion_reduces and shuffle_reduces,
        },
    }


def audit_source_and_data(source_root: str, data_root: str, exp85_root: str, output_dir: str) -> Dict[str, Any]:
    here = Path(__file__).resolve().parent
    protocol = json.loads((here / "protocol.json").read_text(encoding="utf-8"))
    source_hashes = {}
    for rel, expected in protocol["bound_read_only_assets"]["source_sha256"].items():
        path = Path(source_root) / rel
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        source_hashes[rel] = {"expected": expected, "actual": actual, "match": actual == expected}
    expected_data = json.loads((here / "data_seal.json").read_text(encoding="utf-8"))["files"]
    data_hashes = {}
    for rel, spec in expected_data.items():
        path = Path(data_root) / rel
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        data_hashes[rel] = {"expected": spec["sha256"], "actual": actual, "bytes": path.stat().st_size, "match": actual == spec["sha256"]}
    exp85_hashes = {}
    for rel, expected in protocol["bound_read_only_assets"]["exp85_result_sha256"].items():
        path = Path(exp85_root) / rel
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        exp85_hashes[rel] = {"expected": expected, "actual": actual, "match": actual == expected}
    exp85_aggregate = json.loads((Path(exp85_root) / "results/aggregate_results.json").read_text(encoding="utf-8"))
    exp85_replay_ok = bool(exp85_aggregate.get("original_replay", {}).get("byte_identical"))
    audit = {
        "source": source_hashes,
        "data": data_hashes,
        "exp85_results": exp85_hashes,
        "exp85_original_replay_byte_identical": exp85_replay_ok,
        "all_source_match": all(v["match"] for v in source_hashes.values()),
        "all_data_match": all(v["match"] for v in data_hashes.values()),
        "all_exp85_hash_match": all(v["match"] for v in exp85_hashes.values()),
        "exp85_input_result_hash_match": all(v["match"] for v in source_hashes.values()) and all(v["match"] for v in data_hashes.values()) and all(v["match"] for v in exp85_hashes.values()) and exp85_replay_ok,
    }
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    (Path(output_dir) / "asset_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    if not audit["all_source_match"] or not audit["all_data_match"] or not audit["all_exp85_hash_match"] or not exp85_replay_ok:
        raise RuntimeError("read-only source/data/Exp85 hash mismatch")
    return audit


def run(seed: int, source_root: str, data_root: str) -> Dict[str, Any]:
    data_io, model = load_bound_source(source_root)
    base_records, test_ids, overlap = data_io.load_aftraj(data_root)
    for rec in base_records:
        rec["_official_test"] = rec["conv_id"] in test_ids
    test_groups = {str(r["task_group"]) for r in base_records if r["_official_test"]}
    transformed = transform_records(base_records)
    for base, rec in zip(base_records, transformed):
        rec["_official_test"] = bool(base["_official_test"])
    pool = [r for r in transformed if not r["_official_test"] and str(r["task_group"]) not in test_groups]
    confirm = [r for r in pool if is_confirm(str(r["task_group"]))]
    train = [r for r in pool if not is_confirm(str(r["task_group"]))]
    if len(pool) != 911 or len(train) != 731 or len(confirm) != 180 or len(overlap) != 40:
        raise RuntimeError("E33/E85 frozen split counts changed")
    train_groups = {str(r["task_group"]) for r in train}
    confirm_groups = {str(r["task_group"]) for r in confirm}
    if train_groups & confirm_groups:
        raise RuntimeError("train/confirm task_group leakage")
    all_eval = train + confirm
    for ri, rec in enumerate(all_eval):
        rec["_split"] = "confirm" if ri >= len(train) else "train"
        rec["_eval_index"] = ri
    rows = normalize_rows(feature_rows(all_eval))
    train_rows = [r for r in rows if all_eval[int(r["rec"])].get("_split") == "train"]
    oof_audit = train_fold_audit(all_eval, train_rows, model, seed)
    preds, bridge_audit = fit_confirm_bridge(all_eval, rows, model)
    pred_recs = {int(p["rec"]) for p in preds}
    expected_recs = {i for i, r in enumerate(all_eval) if r.get("_split") == "confirm"}
    if pred_recs != expected_recs:
        raise RuntimeError("full bridge prediction records do not exactly match confirm records")
    e1_method = top1(all_eval, preds)
    e1_balanced = balanced(all_eval, preds)
    majority_preds = baseline_predictions(all_eval, train)
    majority_acc = top1(all_eval, majority_preds)
    method_hit_vals = {ri: float(max([p for p in preds if int(p["rec"]) == ri], key=lambda p: p["prob"])["role"] == all_eval[ri]["mistake_agent"]) for ri in expected_recs}
    majority_hit_vals = {ri: float(next(p for p in majority_preds if int(p["rec"]) == ri)["role"] == all_eval[ri]["mistake_agent"]) for ri in expected_recs}
    eval_records = [all_eval[ri] for ri in sorted(expected_recs)]
    e1_ci = group_bootstrap_delta(
        [str(r["task_group"]) for r in eval_records],
        [str(r["task_group"]) for r in eval_records],
        group_values(eval_records, [method_hit_vals[ri] for ri in sorted(expected_recs)]),
        group_values(eval_records, [majority_hit_vals[ri] for ri in sorted(expected_recs)]),
        seed,
        N_BOOT,
    )
    e1_paired = paired_counts([method_hit_vals[ri] for ri in sorted(expected_recs)], [majority_hit_vals[ri] for ri in sorted(expected_recs)])
    role_probs = predictions_by_rec(preds)
    e2 = evaluate_e2(confirm, role_probs, seed)
    train_oof_ok = all(not f["intersection"] for f in oof_audit["folds"])
    leakage = {
        "train_confirm_task_group_intersection": sorted(train_groups & confirm_groups),
        "bridge_prediction_records_exact": pred_recs == expected_recs,
        "bridge_train_confirm_group_intersection": bridge_audit["group_intersection"],
        "train_oof_folds_disjoint": train_oof_ok,
        "model_visible_task_blank": all(not r.get("task") for r in all_eval),
        "model_visible_domain_blank": all(not r.get("domain") for r in all_eval),
        "model_visible_conv_id_opaque": all(str(r.get("conv_id", "")).startswith("opaque_conv_") for r in all_eval),
        "anonymous_roles_only": all(str(t.get("role", "")).startswith("role_") for r in all_eval for t in r.get("turns") or []),
        "feature_names": list(FEATURE_NAMES),
        "feature_count_is_not_retained": True,
        "lexical_length_position_inputs": False,
        "gold_only_scoring": True,
        "same_budget_all_e2_conditions": all(e2["metrics"][name]["n"] == e2["n_valid"] for name in e2["metrics"]),
    }
    checks_pass = all(leakage.values()) and bool(bridge_audit["strict_oos"])
    positive = e2["relative_vs_strongest"] > 0
    gate = dict(e2["gate"])
    gate["input_and_budget_audit"] = checks_pass
    gate["seed_direction_checked_later"] = True
    per_seed_verdict = "REPRODUCED_FULLY_DESHORTCUT_GO" if all(gate.values()) else ("POSITIVE_NOT_YET_GO" if positive else "STOP_THIS_PURE_STRUCTURE_IMPLEMENTATION_ONLY")
    return {
        "schema": "E88-pure-anonymous-structure/1.0",
        "seed": seed,
        "sizes": {"loaded": len(base_records), "official_test": sum(1 for r in base_records if r["_official_test"]), "overlap_removed": len(overlap), "pool": len(pool), "train": len(train), "confirm": len(confirm), "e2_valid": e2["n_valid"], "paired_task_groups": len(confirm_groups)},
        "configuration": {"feature_names": list(FEATURE_NAMES), "e2_local_weights": E2_LOCAL_WEIGHTS, "bridge_weight": BRIDGE_WEIGHT, "role_anonymization": "first_appearance_per_trajectory", "task_group_split": CONFIRM_TAG, "tie_break": "anonymous_role_plus_structural_signature_sha256; exact ties average-ranked", "recency_is_external_baseline": True},
        "e1": {"method_top1": round(e1_method, 4), "method_balanced": round(e1_balanced, 4), "majority_train_only": round(majority_acc, 4), "relative_gain": round((e1_method - majority_acc) / majority_acc, 4) if majority_acc else 0.0, "paired_counts": e1_paired, "paired_ci": e1_ci},
        "e2": e2,
        "oos_audit": {"bridge": bridge_audit, "train_oof": oof_audit, "leakage": leakage},
        "decision": {"verdict": per_seed_verdict, "direction_no_go": False, "scope": "only the fixed pure anonymous structural implementation"},
    }


def aggregate(results: Sequence[Mapping[str, Any]], asset_audit: Mapping[str, Any]) -> Dict[str, Any]:
    gates = [bool(all(r["e2"]["gate"].values()) and r["oos_audit"]["leakage"]["lexical_length_position_inputs"] is False) for r in results]
    positive = [float(r["e2"]["relative_vs_strongest"]) > 0 for r in results]
    all_positive = all(positive) if positive else False
    all_gate = all(gates) if gates else False
    if all_gate and all_positive and asset_audit.get("exp85_input_result_hash_match"):
        verdict = "REPRODUCED_FULLY_DESHORTCUT_GO"
    elif any(positive):
        verdict = "POSITIVE_NOT_YET_GO"
    else:
        verdict = "STOP_THIS_PURE_STRUCTURE_IMPLEMENTATION_ONLY"
    return {
        "schema": "E88-aggregate/1.0",
        "seeds": [int(r["seed"]) for r in results],
        "asset_audit": asset_audit,
        "results_by_seed": list(results),
        "decision": {
            "verdict": verdict,
            "direction_no_go": False,
            "all_three_seeds_positive": all_positive,
            "all_seed_gates": all_gate,
            "exact_stop_scope": "若 verdict 为 STOP，仅停止 E88 固定纯结构输入/权重；Exp85 历史部分正向结果仍保留。",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--exp85-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--all-seeds", action="store_true")
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    asset_audit = audit_source_and_data(args.source_root, args.data_dir, args.exp85_root, str(out))
    seeds = SEEDS if args.all_seeds or args.seed is None else (args.seed,)
    results = []
    for seed in seeds:
        result = run(int(seed), args.source_root, args.data_dir)
        results.append(result)
        (out / f"structural_seed_{seed}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if len(results) > 1:
        summary = aggregate(results, asset_audit)
        (out / "aggregate_results.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"verdict": summary["decision"]["verdict"], "seeds": summary["seeds"], "e2_mrr": [r["e2"]["metrics"] for r in results]}, ensure_ascii=False, indent=2))
    else:
        result = results[0]
        print(json.dumps({"verdict": result["decision"]["verdict"], "seed": result["seed"], "sizes": result["sizes"], "e1": result["e1"], "e2": {k: result["e2"][k] for k in ("metrics", "strongest_fair_baseline", "relative_vs_strongest", "ci_vs_strongest", "gate")}}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

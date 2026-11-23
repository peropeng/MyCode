"""Current RQ1 protocol and opt-in training, separate from the frozen archive.

Preparing a protocol reads public records and hashes assets, without parsing
label values. Training is a separate explicit command; no held evaluation or
network client is included here.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import random
import socket
import time

from .ranking import file_sha, load_models, project_root

CONDITIONS = ("complete", "without_multirelation", "without_candidate_attention", "coding_only", "StepFinder")
SEEDS = (20261006, 20261007, 20261008)
SOURCE = ".rebuild/paper-inputs/rq1-source"


def digest(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def partition(records, condition):
    if condition not in CONDITIONS:
        raise ValueError("Unknown condition")
    selected = [r for r in records if condition != "coding_only" or r["domain"] == "coding"]
    if len({r["sample_id"] for r in selected}) != len(selected):
        raise ValueError("Duplicate sample IDs")
    splits = {name: [r["sample_id"] for r in selected if r["optimization_split"] == name]
              for name in ("train", "validation")}
    if sum(map(len, splits.values())) != len(selected):
        raise ValueError("Unexpected optimization split")
    groups = {name: {r["task_group"] for r in selected if r["optimization_split"] == name}
              for name in splits}
    if groups["train"] & groups["validation"]:
        raise ValueError("Original task crosses train/validation")
    if not all(splits.values()):
        raise ValueError("Empty train/validation split")
    return splits


def settings(condition):
    return {"batch_size": 16, "learning_rate": .001,
            "weight_decay": .00001 if condition == "StepFinder" else .0001,
            "max_epochs": 50 if condition == "StepFinder" else 40,
            "patience": 10 if condition == "StepFinder" else 8,
            "gradient_clip": 1., "selection": "validation Top1, then MRR, then earliest",
            "loss": "author CE + 0.9 temporal" if condition == "StepFinder" else "trajectory mean CE",
            "scaler": "training nodes only", "held_evaluation": False}


def prepare(root=None):
    root = Path(root or project_root())
    public = root / SOURCE / "data/public_records.json"
    records = json.loads(public.read_text(encoding="utf-8"))["records"]
    counts = Counter((r["domain"], r["optimization_split"]) for r in records)
    if counts != {("coding", "train"): 256, ("coding", "validation"): 64,
                  ("math", "train"): 236, ("math", "validation"): 58}:
        raise ValueError("Selected 614-record scope changed")
    files = [public, root / SOURCE / "data/selected_train_labels.private.json",
             root / SOURCE / "features/train_validation_features.pt",
             root / "src/thesis_recovery/rq1_study.py", root / "src/thesis_recovery/ranking.py",
             root / "src/thesis_recovery/__main__.py", root / ".external/StepFinder/model.py"]
    files += list((root / "src/thesis_recovery/frozen/ranking").rglob("*.py"))
    binding = {p.relative_to(root).as_posix(): file_sha(p) for p in files}
    protocol = {"schema": 1, "scope": "RQ1 development protocol; no independent evaluation executed",
                "conditions": {c: {"members": partition(records, c), "settings": settings(c)} for c in CONDITIONS},
                "seeds": list(SEEDS), "bindings": binding,
                "modules": {"complete": "frozen AB_GLOBAL including event pairing",
                            "without_multirelation": "replace 2 RelationLayers by 2 node-only residual layers; retain pairing and candidate attention",
                            "without_candidate_attention": "frozen AB_REF mean background; retain graph and event pairing",
                            "coding_only": "complete architecture, coding train256/validation64; refit scaler",
                            "StepFinder": "author model, explicit ALG_PAPER50 preset"},
                "new_training_steps": 0, "api_requests": 0, "held_label_reads": 0,
                "reuse": "Existing six models remain candidates; new launcher is not bitwise historical retraining.",
                "evaluation_status": "AFTraj163/coding127 membership and development exposure still require audit"}
    return protocol


def verify_bindings(protocol, root):
    for name, expected in protocol["bindings"].items():
        if file_sha(Path(root) / name) != expected:
            raise ValueError("Protocol input/code changed: " + name)


def create_model(condition, seed, models=None):
    """Preserve common initial tensors; no tuning of the complete model."""
    if condition not in CONDITIONS:
        raise ValueError("Unknown condition")
    import torch
    models = models or load_models()
    models.seed_all(seed)
    if condition == "StepFinder":
        model = models.original.StepFinder(content_dim=128, agent_dim=32, hidden_dim=64,
                                           num_heads=2, head_dim=32, dropout=.5,
                                           alpha=.1, beta=.9, gamma=.4, scales=[1, 2])
        return model
    canonical = models.create("AB_GLOBAL")
    canonical_state = dict(canonical.state_dict())
    rng = models.rng_state()
    if condition in ("complete", "coding_only"):
        return canonical
    if condition == "without_candidate_attention":
        model = models.create("AB_REF")
    else:
        model = canonical
        model.layers = torch.nn.ModuleList([models.original.NodeLayer(96, .15) for _ in range(2)])
    shared = {k: v for k, v in canonical_state.items() if k in model.state_dict()
              and not (condition == "without_multirelation" and k.startswith("layers."))}
    # New node-only layers intentionally use fresh parameters.
    model.load_state_dict(shared, strict=False)
    models.restore_rng(rng)
    return model


def score_batch(model, condition, batch, models):
    arm = "SF_REF" if condition == "StepFinder" else "AB_REF" if condition == "without_candidate_attention" else "AB_GLOBAL"
    return models.forward(model, arm, batch)


def fit_scaler(data, ids):
    import torch
    values = torch.cat([data[s]["raw_structure"] for s in ids])
    std = values.std(0, unbiased=False)
    return values.mean(0), torch.where(std < 1e-6, torch.ones_like(std), std)


def ranking_metrics(orders, labels):
    if not orders:
        raise ValueError("Empty evaluation")
    ranks = []
    for sid, order in orders.items():
        if sorted(order) != list(range(len(order))):
            raise ValueError("A complete native ranking is required")
        ranks.append(order.index(labels[sid]) + 1)
    return {"correct": sum(r == 1 for r in ranks), "total": len(ranks),
            "Top1": sum(r == 1 for r in ranks) / len(ranks),
            "MRR": sum(1 / r for r in ranks) / len(ranks),
            "Hit@3_correct": sum(r <= 3 for r in ranks), "Hit@5_correct": sum(r <= 5 for r in ranks)}


def train(protocol_path, condition, seed, device="cpu", root=None):
    """Train one explicitly requested condition, resumable at committed epochs.

    Partial epochs are discarded on restart. This is a new run, never appended
    to archived training or counted as a completed formal experiment here.
    """
    import torch
    root = Path(root or project_root())
    protocol_path = Path(protocol_path).resolve()
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    verify_bindings(protocol, root)
    if seed not in protocol["seeds"] or condition not in protocol["conditions"]:
        raise ValueError("Condition/seed outside frozen protocol")
    if device != "cpu" and not torch.cuda.is_available():
        raise ValueError("Requested CUDA is unavailable")
    model_api = load_models(root)
    model = create_model(condition, seed, model_api).to(device)
    data = torch.load(root / SOURCE / "features/train_validation_features.pt", map_location="cpu", weights_only=False)["records"]
    raw_labels = json.loads((root / SOURCE / "data/selected_train_labels.private.json").read_text(encoding="utf-8"))["labels"]
    labels = {r["sample_id"]: r["target_ordinal"] for r in raw_labels}
    cfg = protocol["conditions"][condition]
    members, config = cfg["members"], cfg["settings"]
    for sid in members["train"] + members["validation"]:
        if sid not in data or not 0 <= labels[sid] < len(data[sid]["content"]):
            raise ValueError("Missing feature/invalid selected label: " + sid)
    scaler = fit_scaler(data, members["train"])
    optimizer = torch.optim.AdamW(model.parameters(), lr=config["learning_rate"], weight_decay=config["weight_decay"])
    binding = {"protocol": file_sha(protocol_path), "condition": condition, "seed": seed,
               "device": device, "torch": torch.__version__, "numpy": __import__("numpy").__version__}
    folder = root / ".rebuild/rq1-study" / binding["protocol"] / condition / str(seed)
    folder.mkdir(parents=True, exist_ok=True)
    lock = folder / "producer.lock"
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise RuntimeError("Producer lock exists: " + str(lock) +
                           "; verify recorded host/PID has stopped before removing this lock and resuming") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        json.dump({"pid": os.getpid(), "host": socket.gethostname(), "binding": binding}, stream)
    try:
        resume = folder / "resume.pt"
        state = {"binding": binding, "epoch": 0, "best": (-1., -1.), "stagnant": 0, "history": [], "selected": None}
        if resume.exists():
            state = torch.load(resume, map_location=device, weights_only=False)
            if state["binding"] != binding:
                raise ValueError("Resume configuration/runtime changed")
            model.load_state_dict(state["model"])
            optimizer.load_state_dict(state["optimizer"])
            # RNG byte tensors must remain on CPU even for CUDA optimizer loads.
            rng = state["rng"]
            rng["torch"] = rng["torch"].cpu()
            rng["cuda"] = [v.cpu() for v in rng["cuda"]]
            model_api.restore_rng(rng)
        if (folder / "complete.json").exists():
            result = json.loads((folder / "complete.json").read_text(encoding="utf-8"))
            if result["binding"] != binding:
                raise ValueError("Completed output binding changed")
            if (folder / "selected.pt").exists() and file_sha(folder / "selected.pt") == result.get("selected_sha256"):
                return result
            # Recover publication from the committed state without retraining.
            if state["selected"] is None:
                raise ValueError("Selected output is damaged and no committed state is available")
        for epoch in range(state["epoch"] + 1, config["max_epochs"] + 1):
            if state["stagnant"] >= config["patience"]:
                break
            started = time.monotonic()
            order = list(members["train"])
            random.Random(seed * 100 + epoch).shuffle(order)
            model.train()
            total_loss = 0.
            for offset in range(0, len(order), config["batch_size"]):
                ids = order[offset:offset + config["batch_size"]]
                batch = model_api.collate(ids, data, scaler, torch.device(device))
                optimizer.zero_grad(set_to_none=True)
                scores, extra = score_batch(model, condition, batch, model_api)
                arm = "SF_REF" if condition == "StepFinder" else "AB_GLOBAL"
                loss = model_api.loss(scores, extra, arm, batch, labels)
                if not torch.isfinite(loss):
                    raise RuntimeError("Nonfinite training loss")
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), config["gradient_clip"])
                optimizer.step()
                total_loss += float(loss.detach()) * len(ids)
            model.eval()
            orders = {}
            with torch.inference_mode():
                for offset in range(0, len(members["validation"]), config["batch_size"]):
                    ids = members["validation"][offset:offset + config["batch_size"]]
                    batch = model_api.collate(ids, data, scaler, torch.device(device))
                    scores, _ = score_batch(model, condition, batch, model_api)
                    for sid, score in zip(ids, scores):
                        if not bool(torch.isfinite(score).all()):
                            raise RuntimeError("Nonfinite validation scores: " + sid)
                        values = score.cpu().tolist()
                        orders[sid] = sorted(range(len(values)), key=lambda i: (-values[i], i))
            metrics = ranking_metrics(orders, labels)
            key = (metrics["Top1"], metrics["MRR"])
            if key > tuple(state["best"]):
                state["best"], state["stagnant"] = key, 0
                state["selected"] = {"state_dict": {k: v.detach().cpu().clone() for k, v in model.state_dict().items()},
                                     "scaler_mean": scaler[0], "scaler_std": scaler[1], "epoch": epoch,
                                     "binding": binding, "metrics": metrics, "members": members}
            else:
                state["stagnant"] += 1
            state["epoch"] = epoch
            state["history"].append({"epoch": epoch, "training_loss": total_loss / len(order),
                                      "validation": metrics, "seconds": time.monotonic() - started})
            state.update(model=model.state_dict(), optimizer=optimizer.state_dict(), rng=model_api.rng_state())
            tmp = resume.with_suffix(".tmp")
            torch.save(state, tmp)
            os.replace(tmp, resume)
        # Publish selected model only from an atomically committed epoch state.
        tmp = folder / "selected.tmp"
        torch.save(state["selected"], tmp)
        os.replace(tmp, folder / "selected.pt")
        result = {"binding": binding, "completed_epochs": state["epoch"],
                  "selected_epoch": state["selected"]["epoch"], "history": state["history"],
                  "selected_sha256": file_sha(folder / "selected.pt"),
                  "status": "DEVELOPMENT_TRAINING_COMPLETE", "held_evaluation": "NOT_RUN"}
        write_json(folder / "complete.json", result)
        return result
    finally:
        lock.unlink()

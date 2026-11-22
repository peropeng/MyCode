"""Tiny artificial tensors for frozen Exp153 behavior checks; no datasets."""
from __future__ import annotations

import copy
import hashlib
import math
import torch

COUNTERS = {"initialized_models": 0, "model_clones": 0, "collate_calls": 0,
            "attention_mask_calls": 0, "permutation_calls": 0,
            "context_readout_calls": 0, "CPU_model_forward_calls": 0,
            "original_reference_forward_calls": 0, "loss_forward_calls": 0,
            "CUDA_model_forward_calls": 0, "optimizer_steps": 0, "backward_calls": 0,
            "scaler_calls": 0, "grouped_loss_calls": 0, "AF_schedule_calls": 0}
NUMERIC_DETAILS = []


def initialized(cm, arm, seed):
    COUNTERS["initialized_models"] += 1
    return cm.create_initialized(arm, seed)


def clone(model):
    COUNTERS["model_clones"] += 1
    return copy.deepcopy(model)


def mask(cm, task_index, adjacency, arm):
    COUNTERS["attention_mask_calls"] += 1
    return cm.attention_mask(task_index, adjacency, arm)


def permutation(cm, sid, n):
    COUNTERS["permutation_calls"] += 1
    return cm.value_permutation(sid, n, device="cpu")


def forward(cm, model, arm, batch, original=False):
    COUNTERS["CPU_model_forward_calls"] += 1
    if original:
        COUNTERS["original_reference_forward_calls"] += 1
    with torch.no_grad():
        return cm.original.forward(model, "StepFinder" if arm == "SF_REF" else "AB", batch) if original else cm.forward(model, arm, batch)


def loss(cm, scores, extra, arm, batch, labels, original=False):
    COUNTERS["loss_forward_calls"] += 1
    with torch.no_grad():
        return cm.original.loss(scores, extra, "StepFinder" if arm == "SF_REF" else "AB", batch, labels) if original else cm.loss(scores, extra, arm, batch, labels)


def fixture_adjacency(n, chain=True):
    adjacency = []
    for relation in range(4):
        indices = torch.arange(n).long()[:, None].repeat(1, 2)
        flags = torch.zeros(n, 2)
        if chain and relation + 1 < n:
            indices[relation + 1, 0] = relation
            flags[relation + 1, 0] = 1
        adjacency.append((indices, flags))
    return adjacency


def artificial_entries():
    entries = {}
    for sid, n, offset in [("artificial.alpha", 5, 1), ("artificial.beta", 3, 17)]:
        content = (torch.arange(n * 128, dtype=torch.float32).reshape(n, 128) + offset) / 19
        agent = (torch.arange(n * 32, dtype=torch.float32).reshape(n, 32) + 2 * offset) / 13
        structure = (torch.arange(n * 23, dtype=torch.float32).reshape(n, 23) % 7 - 3) / 5
        entries[sid] = {"content": content, "agent": agent, "raw_structure": structure,
                        "paired_partner": torch.stack([torch.arange(n), (torch.arange(n) + 1) % n], dim=1),
                        "paired_valid": torch.tensor([[0., 1.]]).repeat(n, 1),
                        "adjacency": fixture_adjacency(n)}
    scaler = (torch.linspace(-.2, .2, 23), torch.linspace(.5, 1.5, 23))
    labels = {"artificial.alpha": 2, "artificial.beta": 1}
    return entries, scaler, labels


def collate(cm):
    entries, scaler, labels = artificial_entries()
    COUNTERS["collate_calls"] += 1
    batch = cm.collate(list(entries), entries, scaler, "cpu")
    return batch, entries, scaler, labels


def directed_mask_fixture():
    task_index = torch.tensor([0, 0, 0, 0, 0, 1, 1, 1])
    adjacency = []
    for relation in range(4):
        index = torch.full((8, 2), 999, dtype=torch.long)
        valid = torch.zeros(8, 2)
        receiver, sender = relation + 1, relation
        index[receiver, 0] = sender
        valid[receiver, 0] = 1
        adjacency.append((index, valid))
    adjacency[0][0][6, 0] = 5
    adjacency[0][1][6, 0] = 1
    adjacency[3][0][7, 0] = 6
    adjacency[3][1][7, 0] = 1
    # Deliberately visible cross-task edges must not introduce within-task paths.
    adjacency[2][0][0, 0] = 5
    adjacency[2][1][0, 0] = 1
    adjacency[0][0][7, 1] = 4
    adjacency[0][1][7, 1] = 1
    expected_rows = [{0}, {0, 1}, {0, 1, 2}, {1, 2, 3}, {2, 3, 4}, {5}, {5, 6}, {5, 6, 7}]
    expected = torch.tensor([[j in row for j in range(8)] for row in expected_rows])
    return task_index, adjacency, expected


def representation():
    h = torch.zeros(8, 96)
    h[:, 0] = torch.tensor([3., -1., 2., 0., 1., 8., -3., 4.])
    for i in range(8):
        h[i, 1 + i] = 2 + i % 3
    return h


def identity_readout(model, o_scale=1):
    with torch.no_grad():
        for name in ["Q", "K", "V"]:
            getattr(model, name).weight.copy_(torch.eye(96))
        model.O.weight.copy_(o_scale * torch.eye(96))
    return model.eval()


def independent_expected_context(h, lengths, static=False, permuted=False, sample_ids=None, o_scale=1):
    """Direct specification on each task; never imports the implementation mask."""
    chunks = torch.split(h, [int(n) for n in lengths])
    out = []
    for task, block in enumerate(chunks):
        mean = block.mean(dim=0)
        query = mean[None].expand_as(block) if static else block
        values = block
        if permuted:
            n = len(block)
            digest = hashlib.sha256(("Exp153-value-perm-v1|" + sample_ids[task]).encode()).digest()
            shift = 0 if n == 1 else 1 + int.from_bytes(digest, "big") % (n - 1)
            values = block[(torch.arange(n) + shift) % n]
        attention = torch.softmax(query @ block.T / math.sqrt(96), dim=1)
        out.append(mean[None] + o_scale * (attention @ values - mean[None]))
    return torch.cat(out)


def artificial_af_metadata(seeds):
    """731 invented record IDs / 716 invented groups; no tensors or labels."""
    groups = [f"artificial.group.{i}" for i in range(716)]
    public = [{"sample_id": f"artificial.record.{i}", "task_group": groups[i]} for i in range(716)]
    public += [{"sample_id": f"artificial.extra.{i}", "task_group": groups[i]} for i in range(15)]
    partitions = {outer: [g for i, g in enumerate(groups) if i % 5 == outer] for outer in range(5)}
    folds = {}
    for seed in seeds:
        rows = []
        for outer in range(5):
            validation_fold = next(i for i in range(5) if i != outer)
            rows.append({"outer": outer, "initialization_seed": seed + outer,
                         "inner_fit_groups": [g for i in range(5) if i not in (outer, validation_fold) for g in partitions[i]],
                         "validation_groups": list(partitions[validation_fold]),
                         "refit_groups": [g for i in range(5) if i != outer for g in partitions[i]],
                         "held_groups": list(partitions[outer])})
        folds[str(seed)] = rows
    return public, folds


def artificial_group_loss():
    from types import SimpleNamespace
    ids = ["artificial.group0.a", "artificial.group0.b", "artificial.group1.a"]
    labels = {ids[0]: 0, ids[1]: 1, ids[2]: 0}
    by = {ids[0]: {"task_group": "group0"}, ids[1]: {"task_group": "group0"}, ids[2]: {"task_group": "group1"}}
    lengths = [4, 3, 2]
    logits = torch.tensor([[3., 0., -1., -2.], [0., 4., 1., 999.], [-2., 0., 999., 999.]])
    mask = torch.tensor([[True] * 4, [True, True, True, False], [True, True, False, False]])
    h = torch.tensor([1., 2., 3.])[:, None, None].expand(3, 4, 2).clone()
    batch = {"ids": ids, "mask": mask, "content": torch.zeros(3, 4, 128), "agent": torch.zeros(3, 4, 32)}
    class Scoring:
        def __call__(self, values, current_mask):
            return logits, torch.tensor(0.)
        def temporal_head(self, values):
            return torch.zeros_like(values)
    model = SimpleNamespace(tfe=lambda *args: h, asi=lambda values, *args: values, scoring=Scoring())
    scores = [logits[i, :n] for i, n in enumerate(lengths)]
    return batch, model, logits, h, scores, labels, by

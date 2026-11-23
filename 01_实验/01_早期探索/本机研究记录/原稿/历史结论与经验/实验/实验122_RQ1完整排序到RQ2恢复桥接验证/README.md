# Exp122 — RQ1 complete-ranking → RQ2 recovery bridge

Exp122 is the prospective joint experiment that tests the scientific bridge between RQ1 diagnosis and RQ2 recovery. It does not reinterpret an old ablation as that bridge. The formal design freezes one outer-fold decision, unseals held fields once, constructs one `original`/`extent`/`dependency` cache per task, and evaluates every registered order against those same caches with budget 2.

## Registered contrasts

- `rq1_full_rank_dependency_slice`: the untouched complete Exp113J/RQ1 ranking on dependency slices.
- `rq1_top1_rq2_posterior_dependency_slice`: Exp121's native order, which preserves RQ1 Top-1 and uses the outer-train-only RQ2 candidate posterior for the tail.
- `rq1_top1_canonical_tail_dependency_slice`: the same RQ1 Top-1 followed by canonical position order.
- `rq1_full_rank_shuffle_dependency_slice`: a deterministic non-identity rotation of the raw RQ1 complete ranking. It preserves the complete candidate multiset but deliberately does **not** protect Top-1: a nonzero rotation moves the original RQ1 Top-1. This is the full-ranking identity/order null, not a protected-Top-1 tail comparator.
- `no_rq1_fixed_dependency_slice` and `no_rq1_uniform_dependency_slice`: same-pool, same-budget no-RQ1 controls.
- The native posterior order is also applied to singleton, extent-matched, and dependency pools, separating scope size from same-target dependency identity.
- `no_recovery`, singleton Oracle, and dependency-slice Oracle remain registered bounds.

Every non-Oracle recovery condition has budget 2. The formal population is frozen at 34 tasks, 8 repositories, and seeds `20260816..20260818`. Before the decision digest is frozen, the runner may read visible inputs and outer-train fields only; held outcome, Gold, responsible position, and fault call remain sealed.

The formal report requires exactly 102 unique task×seed rows for every condition and a common key set. It pre-registers five paired task-group bootstrap contrasts: posterior vs raw dependency order; raw vs canonical tail (RQ1-tail value); posterior vs canonical tail (RQ2-tail value); posterior dependency vs extent (dependency identity); and posterior extent vs singleton (scope size).

## Execution state

After the portable assets reached READY and the full nonformal test suite passed, the user explicitly authorized one formal invocation. `results/exp122_formal_authorization.json` therefore contains `authorized=true` with invocation count zero before execution. Formal publication is no-overwrite and batch atomic after an immutable attempt claim. The formal entry point performs protocol, frozen-source, ranking, and external-asset readiness checks read-only before writing that claim; a non-ready host cannot consume the one-shot namespace.

Before migrated assets are restored, the local nonformal preflight reports `BLOCKED_MISSING_EXTERNAL_ASSETS`. Synthetic closure/order checks, source/protocol checks, and the historical evidence audit remain runnable. A readiness failure is an environment state, not a failed experiment.

On a migrated host, `results/exp122_asset_binding.json` provides the Exp122-only portable path overlay. It binds the SFT to the frozen Hugging Face revision, byte size, and SHA-256, and maps the 34 task commits to eight explicitly named official Git remotes. The overlay changes paths only: it does not rewrite any frozen parent artifact or change a registered condition, feature, budget, ranking, held field, or metric.

## Historical evidence audit

`python runner.py --historical-evidence-audit` reads the already frozen Exp120/121 formal outputs only in a separate posthoc path. It verifies every stable scientific record field for their genuinely shared conditions (excluding label and wall-clock; full order is compared only at the executed budget-2 prefix), and directly pairs Exp120 `a_plus_b_prime` with Exp121 `native_ranked_dependency_slice`. The direct audit reports Top-1 equality, paired task-group bootstrap CI, harm, attempts, cost, and probe totals. This evidence is cross-run and cannot replace Exp122's prospective joint formal run.

The audit also records the Exp120 confound: `a_deletion` and `a_shuffle` were evaluated on the original singleton pool, while `a_plus_b_prime` used the dependency pool. Therefore those two Exp120 labels cannot isolate ranking on an identical dependency cache.

## Commands

```bash
python -m unittest discover -s "实验/实验122_RQ1完整排序到RQ2恢复桥接验证" -p "test_*.py" -v
python -m py_compile "实验/实验122_RQ1完整排序到RQ2恢复桥接验证/runner.py"
python "实验/实验122_RQ1完整排序到RQ2恢复桥接验证/runner.py" --preflight
python "实验/实验122_RQ1完整排序到RQ2恢复桥接验证/runner.py" --asset-ready-preflight
python "实验/实验122_RQ1完整排序到RQ2恢复桥接验证/runner.py" --historical-evidence-audit
```

Run `--run` exactly once after the committed authorization receipt; no retry or overwrite is allowed.

# Exp121 — RQ2 native-ranked dependency-slice recovery

Exp121 is one bounded design validation for the already frozen RQ2 story:
RQ1 localizes responsibility, and RQ2 uses that diagnosis to choose a safe
transactional recovery plan.  The method is not a third module.  It applies
the existing outer-train-only `fit_native_orders` selector (protected RQ1
top-1 plus the frozen parent candidate posterior, with unchanged parameters)
to Exp120's visible same-target forward dependency-closed multi-granularity
slice pool.

In plain terms, RQ1 answers “which action is most responsible?”, while this
experiment asks “after that diagnosis, which rollback/replay plan safely
recovers the task when tool calls have persistent state effects?”  A is the
diagnosis-guided recovery candidate ranking; B′ is the dependency-closed
rollback/replay plan.  `native_ranked_dependency_slice` is A+B′, not a new
module and not a scope/capacity/CRC/DP/risk variant.

## Frozen design

All conditions use 34 tasks, 8 repositories, 8 visible anchors, two attempts,
three frozen seeds, the same final-checkpoint fault/reference/probe contract,
and 5,000 task-group paired-bootstrap replicates.  The dependency pool is
the Exp120 visible same-target, strictly-forward state-delta suffix.  The
extent control preserves each dependency plan's omission-count multiset and
forward chronology but removes target identity.  No held outcome, Gold,
responsible position, candidate identity, old formal metric, or Exp120 formal
record is used to construct a pool or order.

The read-only source provenance is frozen and checked by actual bytes plus
the base-commit blobs: Exp120 `runner.py` SHA-256 is
`b07440ee10b05271249fdb92cc619be9c86b219c61691033f026306445d23fce`, Exp120
`protocol.json` SHA-256 is
`221b6a37e4f6192dc09c3a7435f95359a262c3aaaf1cad5edbf46fb589338ff8`, and the
Exp113J visible ranking source SHA-256 is
`996b5685a72b19c22a617b762c028bb95e12b7e86989075e17c8dd70afe57494`.
The imported module's resolved `__file__` and import-spec origin must both
match the frozen Exp120 runner path; this path-identity check and all three
source/base-commit SHA checks are conjunctive execution gates.

The one registered method and its controls are:

* no recovery; fair singleton `native_prefix2`, `fixed_last_prefix2`, and
  `uniform_equal_comparable_budget` baselines;
* `native_ranked_dependency_slice`: the outer-train-only native order applied
  to dependency slices;
* B attribution: the same native order on original singleton deletion and on
  the extent-matched nondependency control;
* A attribution: fixed anonymous order on dependency slices and a
  deterministic, outcome-free, nonidentity rotation of the frozen native
  order on the same dependency pool;
* original singleton Oracle and dependency-slice Oracle.

There are no additional model, threshold, closure, capacity, risk, or random
scope variants.  The native order is fit once per seed/outer fold before held
unseal and then reused unchanged for original, dependency, and extent pools.

## Prospective gate

The method must be at least 10% above the strongest fair singleton baseline,
positive on all three seeds, and have a strictly positive 5,000-replicate
task-group paired-bootstrap lower bound.  It must also be strictly above the
same-native singleton deletion, same-native extent control, fixed dependency
slice, and shuffled-native dependency slice.  Harm count and rate may not
exceed the strongest fair baseline, and the dependency-slice Oracle must be
at least the method.  Fresh clone/cleanup, identical fault/reference/probe,
freeze-before-unseal, real Exp116E TNR provenance, 8/8 shape, and nonidentity
extent support are conjunctive execution gates.  A result can report a
positive signal without satisfying the chapter gate; missing any gate means
RQ2 is not GO from this experiment.

The 15% figure is reported only as an aspirational Oracle reachability/count
explanation.  It does not replace the prospective 10% method gate or alter
earlier frozen experiments.

## Formal outcome

The single authorized formal invocation completed and returned
`RQ2_CHAPTER_GO_NATIVE_DEPENDENCY_SLICE`.  The strongest fair singleton
baseline recovered `7/34` tasks (`RSR=0.205882`), while
`native_ranked_dependency_slice` recovered `14/34` (`RSR=0.411765`): absolute
`+0.205882`, relative `+100%`, with three-seed relative gains all positive and
a 5,000-replicate task-group paired-bootstrap 95% CI of
`[0.088235, 0.352941]` (`7/0/27` wins/losses/ties).  Harm decreased from
`75/102` to `63/102` executions.

The registered method strictly exceeded every attribution control:
same-native singleton deletion `7/34`, same-native extent-matched nondependency
control `12/34`, fixed dependency slice `6/34`, and shuffled-native dependency
slice `1/34`.  The dependency-slice Oracle recovered `16/34`.  Every registered
execution, source-provenance, freeze-before-unseal, held-access, fresh-clone,
cleanup, and no-old-metric gate passed.

The causal wording is deliberately limited.  The full A+B′ recovery plan is
credible, but most of its gain can also be obtained by a larger forward
omission extent: dependency identity adds only two recoveries over the
extent-matched control (`14/34` versus `12/34`).  This experiment therefore
supports diagnosis-guided, dependency-aware transactional recovery as a
combined method; it does not establish that dependency semantics alone caused
the full `+100%` gain, nor does it establish natural-failure self-healing.

Formal artifacts:

* `results/exp121_formal_report.json`, SHA-256
  `507ddb820c6229756a82fa2653d5c7a7c92ee471449a16cf794227f3ce71b5d5`;
* `results/exp121_formal_audit.json`, SHA-256
  `d41f81ae4bb4e511e7ccc5fd78316902b7350c9c7443c3830510891679274652`;
* formal output SHA-256
  `4c3652c86669a04bfa8a9203ca1f90125fb198eeacda366e715191cad82f8f7e`.

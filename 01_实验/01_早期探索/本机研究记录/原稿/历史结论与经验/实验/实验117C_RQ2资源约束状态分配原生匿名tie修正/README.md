# Exp117C：native anonymous-tie harness correction

Exp117C is an independent namespace correcting the Exp117 harness before any
metric is produced. It is not a second scientific candidate, not a second
trial, and not GO evidence. The superseded Exp117 `HARNESS_INVALID` audit,
claim, and terminal SHA values are recorded only as historical harness
evidence.

The protocol keeps the widest scientifically viable frozen envelope needed to
avoid premature narrowing, while executing only the required 15-condition
fairness/attribution package. It is not an exhaustive configuration sweep.
Once RQ2 B and A+B both satisfy the strict chapter GO gates, the RQ2 line
stops.

## Frozen surface

- 34 tasks, 8 repositories, 8 candidates per task, 3 seeds, and 24 outer folds.
- B: native candidate posterior/full ranking → outer-train marginal-value
  prediction → fold capacity-constrained Active/Standby allocation → the same
  checkpoint transaction/TNR.
- A+B reuses the exact B state map; it does not fit a second B.
- Fixed ExtraTrees parameters, fixed capacity quotas, candidate/state/route
  deletion and shuffle controls, protected random equal-budget control, and
  Oracle upper bound are all retained.
- B's strict attribution controls are candidate-posterior deletion/shuffle and
  state deletion/shuffle, in addition to the parent final-checkpoint,
  capacity, and TNR core audits. The A-only route audit is not required to
  establish B and cannot block B.
- A+B additionally requires no-recovery, protected-random equal-budget,
  candidate/state deletion and shuffle, A-route shuffle, Oracle at least A+B,
  and harmful-not-worse controls. The formal GO gate is conjunctive: B formal
  module plus A+B candidate, positive task-group paired bootstrap lower bounds,
  and the controls assigned to each module.

The only schema correction is the anonymous tie helper: each candidate
contributes only `position` plus the parent canonical eight-dimensional
`native_feature_vector`. Missing, non-eight-dimensional, nonnumeric, NaN, or
Inf vectors fail closed. Production/outer-train posterior ranking continues
to call the exact parent `protected_native_order`; the C native-vector digest
is restricted to the original anonymous allocation/tie helper call sites.

## Formal archive state

The one authorized formal invocation is archived byte-for-byte in the four
independent C paths. Its command exited `2` only because `run_formal()` had
completed and the CLI then fell through to `argparse`'s no-selection
`parser.error`; there was no retry or overwrite. The terminal is
`COMPLETED` with commit marker `COMMITTED`; the claim remains the raw
executor receipt with status `RUNNING`.

| artifact | SHA-256 |
| --- | --- |
| `results/asset_alignment_gate_exp117c.json` | `a4bdd6e0df917b95e8f63a23d8b2f5b5a69a2045bc4aef92c87de8bbbec2315b` |
| `results/execution_attempt_audit_exp117c.json` | `5bb620bdcea2f4cd55a07bcf6eab8431b3a5f61814ca175939f438b04280a218` |
| `results/exp117c_attempt_claim.json` | `eab0006537588f6ff056378af82a412481b6f79fd966bbc60575a250f840c091` |
| `results/exp117c_attempt_terminal.json` | `d0b1b0d534e701e97f0c3a79d356b7bcc4e56fc0ef34fcdf323385eda69d5c3f` |

The archived conclusion is
`EXP117C_RQ2_STOP_CAPACITY_STATE_ALLOCATION`: B relative improvement is
`21.0526%`, but its task-group bootstrap lower bound is `-0.0784314`; A+B is
`-15.7895%` with lower bound `-0.1568627`. State deletion does not lower B.
The formal audit's `capacity_core_required=false` is recorded as a checks
aggregation omission of native-tie/payload fields. Runner semantics and the
STOP judgment were not changed or rerun because these independent negative
GO gates already determine the conclusion.

See [protocol.json](protocol.json) for the complete freeze and
[data_seal.json](data_seal.json) for dynamic SHA verification of the runner,
protocol, authorization receipt, tests, README, and all preflight artifacts.

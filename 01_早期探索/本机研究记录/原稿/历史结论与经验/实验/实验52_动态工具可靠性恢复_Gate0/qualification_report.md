# 动态工具可靠性恢复 Gate0 资格报告

## Decision

`CONDITIONAL_ASSET_BLOCKED`。这不是章节 GO，也不计入“同一个冻结目标的三次方法失败”。Gate0 只审计资产、Gold、外测和重叠，不测科学效果。

## Evidence summary

| Gate | Frozen requirement | Observed | Result |
|---|---|---:|---|
| Formal literature | 3–5 formal core papers | 5 | pass |
| Public runnable assets | at least 2 | 4 candidates, 0 verified end-to-end | blocked |
| Natural/real Agent external | at least 1 | WMA/WebArena candidate only | blocked |
| Independent tasks / held-out | 50 / 20 | 0 eligible | blocked |
| Executor-derived next-call failure Gold | 30 | 0 audited | blocked |
| Executable recovery Gold | 30 | 0 audited | blocked |
| No-model offline first baseline | 1 | 0 qualified | blocked |
| Tools/failure families | at least 2 | 7 candidate, 0 qualified | blocked |
| Exact overlap | same input + output + intervention | not confirmed, risk HIGH | conditional |

## Asset-specific conclusions

- ResiliBench is the strongest synthetic candidate: the official paper reports 5,040 tasks, 30 APIs and five error types, but the shallow clone contains only Git-LFS pointers. Its parameterized failure model and known-statistics MDP workflow cannot be the only external evidence.
- ToolEVO is a useful API-variation candidate, but the official README requires external ToolQA corpus, an API server and Llama3/Qwen weights. Its explicit invocation/deprecation errors and synthetic API changes do not automatically become natural stochastic failure labels.
- WMA has real web-environment semantics, transition/action samples and official evaluators, but the repository’s sample files are only 10 rows each and do not include stable executor failure-type labels. Full WebArena setup is Docker-heavy and trajectory generation imports OpenAI.
- OpenApps is the cleanest no-model environment candidate: the official repository exposes transparent Python state/reward logic and advertises single-CPU execution. Static config inspection found 28 base tasks, 243 goal variations and 100 longer-horizon records. These are GUI environment variations, not tool-failure trajectories; it can only support a control or state/reward smoke unless a separate failure injector is preregistered.

## Overlap kill test

The closest pressure is ICLR 2026 *Do Large Language Models Know What They Are Capable Of?*: it predicts task success probability before and during multi-step execution and uses confidence for costly continue decisions. ResiliBench already evaluates workflows under probabilistic tool failures using known reliability statistics. ToolEVO already adapts tool usage from environment errors. ReIn and BacktrackAgent already provide test-time recovery/backtracking. The candidate survives Gate0 only as a conditional question: can executor-derived, pre-call, dependency-conditioned failure risk provide information not present in those works and improve recovery on a natural external asset? A classifier/calibrator or cost-weight-only change fails the overlap gate.

## Permitted next step

One bounded Gate1 asset experiment may inspect the minimum LFS schemas/official evaluator or a second natural executable asset. It must not download weights, call models/APIs, run full Docker, or alter the locked Brier/recovery protocol. If the Gold/replay chain remains absent, stop the candidate as `STOP_ASSET`; if the overlap kill test fails, stop as `REJECTED_OVERLAP`.

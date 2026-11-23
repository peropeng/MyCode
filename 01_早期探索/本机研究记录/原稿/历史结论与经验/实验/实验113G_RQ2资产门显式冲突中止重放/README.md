# Exp113G：RQ2 资产门显式冲突中止重放

Exp113G 当前状态为 `HARNESS_INVALID`：唯一一次正式资产资格门 invocation
已完成但在 inherited selection 阶段失败，未生成 formal output。它完整继承 Exp113F 的
response-conditioned transaction semantics，并把反事实 omission 造成的
后续成功 editor precondition divergence 显式记录为 conflict-abort。它不
是 Exp114 module B，不产生 recovery success，也不作 method/chapter GO。

## Frozen transaction contract

窗口 272 calls 固定为：

```text
104  success_state_delta
 18  failed_transaction_noop
150  stateless_noop
```

相邻 response success 的 editor call 才提交 exact state delta；明确 failure
的 editor call 不改文件、不 push/pop undo history；missing/unclassified
response fail closed；non-editor/view 为 stateless no-op。

候选 omission 固定为：

```text
success editor  -> state_delta_omission, state_changing=true,  omit_call_delta=true
failed editor   -> failed_transaction_noop_omission, state_changing=false, omit_call_delta=false
other/view      -> stateless_noop_omission, state_changing=false, omit_call_delta=false
```

全部 34 × 8 = 272 candidates 保持 `intervention_executable=true`。

## Explicit conflict-abort

反事实分支省略 candidate 后，后续 response-success editor transaction 仍尝试
严格 exact apply。若 target、old text、insert line、create/delete 或 undo
history precondition 失效：

- 记录 `counterfactual_transaction_conflict`、task/branch/call/command/path
  hash、precondition failure；
- 记录 state/history before/after hash，二者必须相同；
- 原子 `abort_noop`，不写文件、不 push/pop history；
- 继续后续 call，冲突不计为 recovery success。

response-failure undo 仍是 failed-transaction no-op；response-success undo
没有 committed history 时记录 conflict-abort。

## Non-formal exhaustive preflight

唯一 CLI 入口：

```text
python3 实验/实验113G_RQ2资产门显式冲突中止重放/scripts/run_conflict_abort_replay_preflight.py --preflight
```

该入口执行 34 个 selected local source clone/checkout、272 个 response
classification audit 和 272 个完整 prefix/window omission branches。每个
branch 必须走到 window 末尾；conflict 可以大于零，但未捕获 editor exception
必须为 0，临时目录必须清理。

使用 `git clone --no-checkout --no-hardlinks`、精确 detached base、
`git cat-file -e <base_commit>^{commit}`、`rev-parse HEAD`，并设置
`GIT_TERMINAL_PROMPT=0`、`GIT_OPTIONAL_LOCKS=0`、`GIT_NO_LAZY_FETCH=1`。
代码禁止 fetch/pull/remote/submodule/network fallback。

独立结果（exclusive/no-overwrite）：

```text
results/conflict_abort_replay_preflight.json
results/conflict_abort_replay_preflight_attempt_audit.json
```

formal output/audit 独立；invocation 前两者均不存在：

```text
results/asset_alignment_gate_conflict_abort.json
results/execution_attempt_audit_conflict_abort.json
```

## Formal integration surface and final attempt

`ConflictAbortExecutor.execute_task()` 已接入继承的 C/D/original
qualification 路径：在 evaluator latch 解封后，为每个 arm/baseline/Oracle
从 exact-base local clone 独立 reset，执行 response-conditioned
prefix/window，按继承 fault timing 注入 syntax fault，并运行 target compile
probe。成功 editor transaction 才提交 state delta；counterfactual
precondition 失效时记录 `counterfactual_transaction_conflict`，原子
`abort_noop`，不计 recovery success，随后调用继续。

`build_corrected_tasks()` 冻结 34 tasks、8 candidates、104/18/150 response
分类，并在 Gold latch 前保持 anonymous feature record。`run_qualification()`
通过独立 G output/audit、single-invocation/no-retry/no-overwrite guard、stage-aware
failure audit 和 hook restoration 复用原始 fit/ranking/aggregate/Gate；decorate
明确 `inherited_asset_metrics_present=true`、
`new_metrics_generated_by_correction_layer=false`、method/chapter false。

G 专属 verdict 固定为：

```text
GO:   EXP113G_ASSET_ALIGNMENT_GO_CONTROLLED_ONLY_RESPONSE_CONDITIONED_CONFLICT_ABORT_REPLAY
STOP: EXP113G_ASSET_ALIGNMENT_STOP_RESPONSE_CONDITIONED_CONFLICT_ABORT_REPLAY
```

decorate 将 inherited D/C GO 或 original STOP 映射到上述 G namespace，并在
`gate.source_verdict` 保留映射前 verdict。

本轮按授权 exact command 执行一次：

```text
python3 实验/实验113G_RQ2资产门显式冲突中止重放/scripts/run_conflict_abort_replay_preflight.py --run
```

进程 exit `1`，elapsed 约 `250.6s`，没有重试或代码修复。最终 failure audit
记录：

```text
status=HARNESS_INVALID
failure_stage=corrected_task_builder
error_type=ContractError
error_excerpt=fixed-rollback has no executable candidate
actual_command_attempts=1, retry=false, overwrite=false
```

G formal output 不存在；独立 audit 已封存，SHA256 为
`30cd9d89f917b8a6a29ad1a2be05d1121ab05016d361da2aba3d1941e5bf4ef7`。
该失败不产生资产门 GO，也不构成 method/chapter GO；未读取或汇报中间
ranking/metric，既有 non-formal preflight JSON 未重写。

## Verification

```text
python3 -m unittest discover -s 实验/实验113G_RQ2资产门显式冲突中止重放/tests -p 'test_*.py'
python3 -m py_compile 实验/实验113G_RQ2资产门显式冲突中止重放/scripts/run_conflict_abort_replay_preflight.py 实验/实验113G_RQ2资产门显式冲突中止重放/tests/test_conflict_abort_replay_preflight.py
git diff --check
```

## Completed non-formal preflight

本轮已完成：source clone `34/34`、window response audit `272/272`、完整
omission branches `272/272`，未捕获 editor exception 为 `0`，临时目录全部
清理。共有 45 branches 发生 conflict，共 52 次 transaction conflict，
branch-level conflict rate 为 `45/272`，call-level conflict total / branch
count 为 `52/272`。主要 precondition 分类为：

```text
str_replace_old_text_count_not_one       48
undo_without_committed_history            2
str_replace_target_missing_or_not_file    2
```

每条 conflict 都记录 path hash、precondition failure、state/history
before/after hash；本次所有 hash 相等、history unchanged，effect 均为
`abort_noop`，且后续调用继续执行。conflict 不被计为 recovery success。

独立结果 SHA256：

```text
preflight output: c98b575813fde0a763edfdd7dc95d64954cf3673520995eb54834f02c62972c3
attempt audit:    f9e26412de4ee801d0364bacf78b2c61e5d095d4a8e5cba9ece031f9df2b51d6
```

正式尝试后：`formal_attempts=1`；G formal output 不存在，G failure audit
已写入；D/F audit/output、旧实验 targeted SHA/absence contract 均未覆盖。

集成测试还覆盖真实最小 local repository clone：`No` 分支在省略前置
state delta 后产生 conflict-abort 且 probe 通过，另一 branch 在 fault 后
无 conflict 但 probe 失败；所有 8 个冻结 label 均使用相同 executor、独立
reset 和透明 conflict 字段。冻结前标准库测试为 `15/15`；正式 command
只执行一次且失败后未重跑。

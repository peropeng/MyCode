# Exp113F：RQ2 资产门响应条件事务重放纠正

Exp113F 是独立的、非正式 harness semantic correction。它只修正
Exp113E02 可见轨迹中的 editor transaction commit 语义，不运行正式 ranking、
metric、qualification 或章节判断。

## 冻结边界

- 继承 Exp113D 的 34 条 selected local sources、base commit、三固定根和
  local clone contract；不修改 D inventory、audit 或 output。
- 只读取 E02 allowlisted identity/window geometry 与 raw SFT `messages` 列。
  相邻 response signal 复用 Exp113E 的 `_response_signal` 和
  `iter_raw_calls`；不读取 `responsible_position`、fault、Gold/evaluator、
  ranking/model 或 metric 字段。
- Exp113C/D 的 helper tuple correction、匿名 adapter、Exp112 deployment、
  seeds/folds/models、arms/baselines/budgets 和 Gate 六条件均为 inherited
  contract；本目录不是 method/chapter GO。

## Response-conditioned transaction semantics

相邻 tool response 为 success 时，editor call 才提交精确 state delta 并
push undo snapshot。明确 failure 是失败事务 no-op：不改文件、不 push/pop
undo history。missing/unclassified response fail closed，同样不默认成功。
非 editor 与 `view` 保持 stateless no-op。

272 个 frozen window calls 的分类为：

```text
104  success_state_delta
 18  failed_transaction_noop
150  stateless_noop
```

18 个失败 editor candidate 在 `candidate_map` 中固定为：

```text
intervention_kind=failed_transaction_noop_omission
state_changing=false
omit_call_delta=false
intervention_executable=true
```

## Exhaustive non-formal preflight

唯一可执行入口是：

```text
python3 实验/实验113F_RQ2资产门响应条件事务重放纠正/scripts/run_response_conditioned_replay_preflight.py --preflight
```

它执行：

- 34 个 selected source 的真实 local clone/精确 base checkout audit；
- 272 个 window response classification audit；
- 每个 task × 8 candidate 的独立临时 clone，在 prefix/window 上按
  response-conditioned 语义完成 omission replay；
- `git clone --no-checkout --no-hardlinks`、detached frozen base、
  `rev-parse HEAD` 与 `git cat-file -e <base_commit>^{commit}` 校验；
- `GIT_TERMINAL_PROMPT=0`、`GIT_OPTIONAL_LOCKS=0`、`GIT_NO_LAZY_FETCH=1`，
  禁止 fetch/pull/remote/submodule/network fallback；
- 临时目录清理、failed editor 无 mutation/no history 和成功 editor 严格
  precondition。

输出独立且 exclusive/no-overwrite：

```text
results/response_conditioned_replay_preflight.json
results/response_conditioned_replay_preflight_attempt_audit.json
```

F formal output/audit 仍必须不存在：

```text
results/asset_alignment_gate_response_conditioned.json
results/execution_attempt_audit_response_conditioned.json
```

`formal_attempts=0` 永远成立；本目录没有 formal `--run` 入口。

## Verification

```text
python3 -m unittest discover -s 实验/实验113F_RQ2资产门响应条件事务重放纠正/tests -p 'test_*.py'
python3 -m py_compile 实验/实验113F_RQ2资产门响应条件事务重放纠正/scripts/run_response_conditioned_replay_preflight.py 实验/实验113F_RQ2资产门响应条件事务重放纠正/tests/test_response_conditioned_replay_preflight.py
git diff --check
```

诊断结果不等于资产资格门 GO、method GO 或 chapter GO；主线程必须另行审查
协议与 preflight 结果后，才可决定后续动作。

## Current preflight evidence

本轮唯一一次 exhaustive invocation 已完成 source clone `34/34` 与 response
classification `272/272`，但严格 response-conditioned omission replay 为
`229/272`，因此独立结果状态为 `INCOMPLETE`，没有伪造完整 coverage，也没有
formal attempt。失败均为后续 success editor call 的真实 precondition
contradiction：省略前一成功 state delta，或跳过前一明确失败事务后，后续
success `str_replace` 的 `old_str` 不再存在/唯一。将这些 success call 静默
当作 no-op 会违反本协议的 exact-commit 语义；因此该结果不能宣称 272/272
通过，需主线程决定是否接受该 contradiction 作为诊断边界。

失败输出和 attempt audit 保留在上述独立 F namespace，`formal_attempts=0`，
F formal output/audit 与 D audit/output 均未写入。

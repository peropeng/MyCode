# Exp113D：RQ2 资产门本地对象源纠正式复跑

Exp113D 是 Exp113C 的 correction-only 复跑协议。它继承 Exp113C 的真实
helper tuple correction、E02 的 34 条任务与 8 个候选、匿名 adapter、Exp112
deployment、seed/fold/model/arm/baseline/budget、272 个候选调用和 omission
语义。唯一运行时变化是 repository object source binding：每条 E02 task 从
已提交的 `results/local_object_source_inventory.json` 读取一个 deterministic
selected source。

source 选择固定为
`checkpoint_gate_runtime > p1_multifault > same_checkpoint_repositories`，
同根按字典序第一。每条 source 必须是三个硬编码根之一的绝对、非 symlink
候选目录，候选名必须匹配 task 的 instance/repository key，并在运行前用
`git cat-file -e <base_commit>^{commit}` 重新确认精确 frozen object。任何
缺失、错误根、symlink、重复 candidate check 或 commit 不可达都报告
`ASSET_SOURCE_INCOMPLETE`，不启动 ranking 或 formal replay。

formal replay 的临时仓库只允许通过本地 source 执行：

```text
git clone --no-checkout --no-hardlinks <selected-local-source> <temporary-directory>
git checkout --detach <base_commit>
```

每个 arm/baseline 仍由继承的 Exp113 executor reset 到同一个精确
`base_commit`；terminal prompt 被禁用，代码没有远端 URL、fetch、pull、
submodule 或 network fallback。

输出命名空间独立于 Exp113/Exp113C：

- `results/asset_alignment_gate_local_object_source_corrected.json`
- `results/execution_attempt_audit_local_object_source_corrected.json`

两者 single-invocation、single-write、no-retry、no-overwrite。冻结阶段
formal output 与 attempt audit 均不存在，`formal_execution_run_count=0`；本
目录只运行 inventory、静态检查和 mock/non-formal probes，不读取正式指标。

提交前的独立 local-object preflight 使用：

```text
python3 correction_runner.py --local-clone-checkout-probe
```

它对 34 个 selected source 逐个真实执行 local clone、detached frozen-base
checkout 和 `rev-parse HEAD`，把结果 exclusive 写入
`results/local_clone_checkout_preflight.json`；临时 clone 自动清理。该文件
明确记录 `coverage=34/34`、`formal_attempts=0`、
`formal_metrics_generated=false`，且不是 formal output/audit。任何一个 clone
或 object 校验失败都会写 `source_status=incomplete` / `ASSET_SOURCE_INCOMPLETE`
并保持 formal attempts 为 0。

结果语义上，source-binding audit 自身标记 `contains_metrics=false`；正式
aggregate 只继承 Exp113C 的资产指标，新增 correction 层指标始终为
`new_metrics_generated_by_correction_layer=false`，并显式记录
`inherited_asset_metrics_present=true`。

## Verification boundary

标准库测试覆盖 inventory 选择优先级、34/34 coverage、精确 object、伪造
missing/wrong-root/symlink/duplicate/commit-missing source、无网络 clone
命令、frozen checkout、Exp113C helper tuple/omission/arms/budgets/digest
继承，以及独立输出 guard。正式 `--run` 必须由主线程审查后单独授权。

## Formal invocation status

主线程授权的唯一正式命令已执行一次：

```text
python3 实验/实验113D_RQ2资产门本地对象源纠正式复跑/correction_runner.py --run
```

本次执行以 `HARNESS_INVALID` 结束（`QualificationError: str_replace old
text count is not exactly one`），`actual_command_attempts=1`、`retry=false`、
`overwrite=false`。失败发生在正式结果写入前；
`results/asset_alignment_gate_local_object_source_corrected.json` 不存在，
独立审计 `results/execution_attempt_audit_local_object_source_corrected.json`
已保留，且记录 `formal_output_written=false`、`formal_metrics_generated=false`。
该结果不构成资产门通过，也不构成 method/chapter GO；不得据此重跑或解读正式
指标。34/34 local-object preflight 仍为此前冻结的非正式证据。

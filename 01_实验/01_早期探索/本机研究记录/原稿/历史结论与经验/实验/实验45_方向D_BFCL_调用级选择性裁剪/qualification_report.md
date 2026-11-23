# 方向 D 调用级选择性裁剪 Gate 报告

## 0. 旧版结果作废与隔离修正版

旧版按 `(task_hash, full_output_digest)` 复用官方 checker 结果；官方 `multi_turn_utils` 会按 model/test/class namespace 复用 stateful instance，导致相同 output 的不同 candidate 跨 candidate 污染。旧版分数和 unique-output reuse 口径均为 **INVALID**，不得作为本设计证据。修正版不改候选池、Gold 边界或门槛；每个 candidate/replay 使用含 experiment、task hash、candidate hash、完整输出 digest、replay index 的独立 namespace，并在 `finally` 清理 model、ground_truth 和 involved class instance。

本报告只记录元数据、哈希和聚合数字；不包含 raw response、Gold、call value 或 schema 原文。

- 固定样本：120 条（四家族各 30 条）；No=75/120。
- ExactDedupRule=74/120；全局最强 baseline=No（75/120）。
- Oracle=77/120；相对最强 baseline=0.0267；净救回=2。
- Bootstrap：point=0.0167，95% CI=[0.0000, 0.0417]。
- 双 replay：120/120 task 全候选一致；harness error task=0。
- Public support：98 条含 multi-call，120 条含 multi-item，within-item duplicate=0，within-turn duplicate=33，history duplicate=8。

## 隔离、顺序与 fresh-process 审计

- evaluator isolation audit：18836 scoring calls；checker invocation=7680；created=removed=24584；preexisting=0；missing=0；732 个 expected key 因 checker 早退未创建；`harness_invalid=false`；final prefix leak=0。
- 正式 replay1 按 candidate 升序、replay2 按逆序；固定 seed `20260821` shuffle 全量 9418/9418 candidate outcome fingerprints 一致，且 shuffle 改变了两条 replay 的执行顺序。
- 独立 fresh subprocess 复核全部 120 个 No 与每个 family×operator 非 No 候选至少 5%，共 601/601 fingerprints 一致；checker exception=0；created=removed=1580；preexisting=0；final leak=0；`harness_invalid=false`。

## 决策：STOP

失败原因：

- ORACLE_RELATIVE_GAIN_BELOW_10_PERCENT
- RESCUED_TASKS_BELOW_8:2
- PAIRED_CLUSTER_BOOTSTRAP_CI_LOWER_NOT_POSITIVE

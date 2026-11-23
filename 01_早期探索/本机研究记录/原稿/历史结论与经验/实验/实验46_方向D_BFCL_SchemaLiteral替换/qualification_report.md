# 方向 D 设计 3/3：Schema/可见字面量局部替换 Gate 报告

本报告只记录哈希、索引、布尔结果和聚合计数，不包含 raw response、Gold、schema 原文或用户 literal。

## 0. 旧版结果作废与隔离修正版

旧版按 `(task_hash, full_output_digest)` 复用官方 checker 结果；官方 stateful evaluator namespace 跨 candidate 复用，故旧版分数和 unique-output reuse 口径均为 **INVALID**，不得作为本设计证据。修正版不改候选池、Gold 边界或门槛；每个 candidate/replay 使用含 experiment、task hash、candidate hash、完整输出 digest、replay index 的独立 namespace，并在 `finally` 清理 model、ground_truth 和 involved class instance。

- 固定样本：120 条（四家族各 30 条）；No=75/120。
- LexicalSchemaRule=6/120；全局最强 baseline=No（75/120）。
- Oracle（仅六类局部替换，不含 baseline）：76/120；相对最强 baseline=0.0133；净救回=1；受损=0。
- Bootstrap：point=0.0083，95% CI=[0.0000, 0.0250]。
- 双 replay：120/120 task 全候选一致；harness error task=0。
- Support：候选总数=26503；全量输出 digest=25839；语义 no-op 未计 support。

## 隔离、顺序与 fresh-process 审计

- evaluator isolation audit：53006 scoring calls；checker invocation=16588；created=removed=55708；preexisting=0；missing=0；uncreated expected=0；`harness_invalid=false`；final prefix leak=0。
- 正式 replay1 按 candidate 升序、replay2 按逆序；固定 seed `20260821` shuffle 全量 26503/26503 candidate outcome fingerprints 一致，且 shuffle 改变了两条 replay 的执行顺序。
- 独立 fresh subprocess 复核全部 120 个 No 与每个 family×operator 非 No 候选至少 5%，共 1449/1449 fingerprints 一致；checker exception=0；created=removed=2504；preexisting=0；final leak=0；`harness_invalid=false`。

## 决策：STOP

失败原因：

- ORACLE_RELATIVE_GAIN_BELOW_10_PERCENT
- RESCUED_TASKS_BELOW_8:1
- PAIRED_CLUSTER_BOOTSTRAP_CI_LOWER_NOT_POSITIVE

# Exp106 责任排序：Top-1 提升级联

本目录冻结一次可证伪的秩深度模块替换。Exp105 固定连续软融合显示 R@1 大幅提高、R@3 下降，但 MRR 只有三 seed 同向小正。Exp106 不调 alpha，而是将软融合降级为只选一个顶部候选：

1. 复用 Exp105 的固定 `alpha=0.5` 软分数，只提升其 Top-1 步骤；
2. 提升项固定为第 1 名；
3. 其余步骤不再混合 recency，完全按 `pairwise_B` 数值步骤分数降序，精确数值并列用平均秩。

提升不读 Gold。软分数并列时，先用 Exp88 的匿名角色+结构 digest 排序；若仍是结构同质候选，用固定 salt 与整条匿名位置轨迹的 SHA-256 选择唯一 offset。该规则不读 `mistake_agent/mistake_step/task/domain/conv_id/task_group`，不固定偏爱最早或最近步骤；位置本身是允许的匿名结构。

## 冻结合同

- 数据：Exp96 的 731 条 train、716 个 task groups。3 seeds × 5 outer folds。
- 拟合：`original_A/pairwise_B` 严格 outer-train 拟合并预测 outer-held；保留 Exp101 硬门需要的四个 inner-held OOF。
- 条件：`local/original_A/pairwise_B/recency/exp101_hard_gate/exp105_soft_fusion/top1_cascade/deletion_global_arm/shuffled_promoted_top`。
- 公平 baseline 只能在 `local/original_A/pairwise_B/recency` 中三 seed 汇总后全局选一次。
- `shuffled_promoted_top` 在每条非单步记录内将一个提升 one-hot 改到另一个位置，其余仍用同一 pairwise_B 尾部。
- 禁止 Gold 促销、alpha/阈值调参、confirmation 评分、API/token/retry。
- 正式输出只能写 `results/formal_nested_oof_results.json`，最多一次，禁止覆盖或重试。

## 专用判定

只有资产 hash、nested split、Gold 隔离、删除和 shuffle 审计全部通过，且三 seed 相对同一全局最强公平 baseline 的 delta 均为正、每个 5000 次 task-group paired bootstrap CI 下界均大于 0，才判 `TOP1_CASCADE_FEASIBILITY_GO`。

只要审计干净且任一 seed 有正 delta，但未通过所有 GO 门，必须保留为 `TOP1_CASCADE_POSITIVE_NOT_YET_GO`。只有三 seed 稳定全非正才能判 `STOP_EXP106_FIXED_TOP1_CASCADE_ONLY`，只淘汰这一个候选提升+原始 pairwise_B 尾部实现，`direction_no_go=false`，不得扩大为责任排序、Exp101、Exp105 或 pairwise_B 的 NO-GO。

当前状态：协议、seal、runner 与测试已冻结；唯一正式 OOF 已执行。

## 唯一正式 nested OOF 结果

冻结实现 commit 为 `f8f7bb2`。唯一正式命令在约 192 秒内完成，生成 `results/formal_nested_oof_results.json`（SHA-256 `5fa98f6d53b061eecf0e4d0e4120ae7f58418230ff516651fe0bcd6bd2de55f9`）；API/token/retry 均为 0，未评分 confirmation，未读取 Exp97/98 Gold。

一次性全局公平 baseline 为 `pairwise_B`（三 seed task-group MRR 均值 0.343700）。目标 `top1_cascade` 的逐 seed 结果如下：

| seed | Top-1 cascade MRR | pairwise_B MRR | 绝对差 | 相对差 | paired bootstrap 95% CI | group better/worse/tie | shuffle MRR |
|---|---:|---:|---:|---:|---|---:|---:|
| 20260816 | 0.377519 | 0.344260 | +0.033259 | +9.6612% | [0.020390, 0.046766] | 70 / 88 / 558 | 0.343680 |
| 20260817 | 0.377253 | 0.344457 | +0.032796 | +9.5211% | [0.019788, 0.046795] | 69 / 91 / 556 | 0.349911 |
| 20260818 | 0.377398 | 0.342382 | +0.035016 | +10.2271% | [0.021413, 0.049333] | 71 / 89 / 556 | 0.330750 |

三 seed 点估计全正，平均绝对差 +0.033691；pooled 95% CI 为 [0.020358, 0.047149]。三个逐 seed CI 下界均大于 0，且每个 seed 的 `shuffled_promoted_top` 均低于目标。

秩深度证据与设计目标一致：Top-1 cascade 保留了 Exp105 的 task-group R@1（0.158170/0.157821/0.157821，对 pairwise_B 为 0.069832/0.069832/0.067039），同时将 R@3 修复到 0.464735/0.464735/0.464735，高于 pairwise_B 的 0.456913/0.458310/0.454120，也明显高于 Exp105 soft 的 0.420042/0.422137/0.422137。这表明正信号来自“只提升一个软顶部，保留 pairwise_B 尾部”的模块替换，而不是继续调 alpha。

15 个 outer fold 的 outer-held/inner-OOF 隔离、每条记录覆盖一次、单一提升、匿名确定并列、pairwise_B 尾部平均并列秩、shuffle one-hot、资产 hash、Gold 隔离和预算审计全部通过。删除条件严格等于全局 `pairwise_B`。

顶层判定为 `TOP1_CASCADE_FEASIBILITY_GO`，这是 Exp106 自身的 RQ 可行性 GO；`direction_no_go=false`。`is_final_paper_go=false`，不单独声称 final-paper 或两章 GO，需由主线与 Exp101 的既有 GO 完成 RQ 独立性与两章故事验收。

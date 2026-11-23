# Exp105 责任排序：固定连续软融合

本目录冻结一次可证伪的模块替换实验：将 Exp104 失败的离散稳健门替换为无阈值连续融合。目标方法对每条 outer-held 记录分别计算：

1. `pairwise_B` 数值步骤分数（E88 local + 3 × outer-OOF pairwise role probability），在该记录内 min-max 到 `[0,1]`；
2. 完全不读 Gold 的 recency ramp（第 `i` 步为 `i/(n-1)`），同样在该记录内 min-max；
3. 用冻结的 `SOFT_ALPHA=0.5` 做凸组合，高分优先；数值精确并列用平均秩。

常量向量归一为中性 `0.5`。不搜索 alpha、阈值或任何超参数。Gold 只为保留的 Exp101 硬门 comparator 提供 inner-OOF 标签，并在最终 evaluator 读取错误步骤；soft score 本身不读取 `mistake_agent` 或 `mistake_step`。

## 冻结执行合同

数据仍是 Exp96 的 731 条训练记录、716 个 task groups、3 seeds × 5 outer folds。每个 outer fold 的 `original_A` 和 `pairwise_B` 只在 outer-train 拟合并预测 outer-held。为保持与 Exp101 硬门可比，outer-train 仍做四个 inner-held OOF；soft fusion 没有拟合参数。

公平 baseline 固定集合为 `local/original_A/pairwise_B/recency`，只在三 seed 汇总后一次性选全局最强者。条件完整保留：

- 四个公平 baseline；
- `exp101_hard_gate` 兼容 comparator；
- 目标 `soft_fusion`；
- 删除实验 `deletion_global_arm`；
- 在每条记录内打乱 pairwise 连续步骤权重、保持精确多重集的 `shuffled_soft_weights`。

正式输出只能写 `results/formal_nested_oof_results.json`，最多一次，禁止覆盖、重试和调参。Exp97/98 Gold 与 confirmation 均禁止读取或评分。

## 判定

只有三个 seed 相对同一个全局最强公平 baseline 都为正、每个 5000 次 task-group paired bootstrap CI 下界都大于 0，并且删除、shuffle、hash、split 和 Gold 泄漏审计全部通过，才判 `SOFT_FUSION_FEASIBILITY_GO`。

任一审计干净的非误差正信号但未通过全部门槛，必须保留为 `SOFT_FUSION_POSITIVE_NOT_YET_GO`。只有稳定全非正才可写 `STOP_EXP105_FIXED_SOFT_FUSION_ONLY`，且只淘汰这个固定 alpha=0.5 归一化融合，不得扩大成责任排序、pairwise_B、recency 或 Exp101 的 NO-GO。

当前状态：协议、seal、runner 与测试已冻结；唯一正式 OOF 已执行。

## 唯一正式 nested OOF 结果

冻结实现 commit 为 `9a67462076646dcfdb1b4bdb29e30b53fc4ff384`。唯一正式命令在约 202 秒内完成，生成 `results/formal_nested_oof_results.json`（SHA-256 `ebf2414f563c42fb6f2a723a4ddd428b675e000a4f1c36f1ecd65ae4efb29779`）；API/token/retry 均为 0，未评分 confirmation，未读取 Exp97/98 Gold。

正式运行后的复核发现，冻结提交前清理 `protocol.json` 末尾空行后，`data_seal.protocol_sha256` 仍是清理前字节的 hash。方法字段、协议语义、runner 和正式运行输入均未改变；结果提交只把 seal 中这一项更正为正式运行实际读取文件的 SHA-256 `517c1651c1be067b17fae78b75a64203582a13f96e2dcfa7e218a37f03e8f4fc`，没有重跑或重评分。

一次性全局公平 baseline 是 `pairwise_B`（三 seed task-group MRR 均值 0.343700）。目标 `soft_fusion` 的逐 seed 结果如下：

| seed | soft fusion MRR | pairwise_B MRR | 绝对差 | 相对差 | paired bootstrap 95% CI | group better/worse/tie | shuffle MRR |
|---|---:|---:|---:|---:|---|---:|---:|
| 20260816 | 0.344352 | 0.344260 | +0.000093 | +0.0269% | [-0.015864, 0.016211] | 209 / 345 / 162 | 0.351018 |
| 20260817 | 0.344479 | 0.344457 | +0.000022 | +0.0065% | [-0.015984, 0.016812] | 210 / 345 / 161 | 0.333973 |
| 20260818 | 0.344295 | 0.342382 | +0.001913 | +0.5588% | [-0.013720, 0.018787] | 215 / 342 / 159 | 0.346878 |

三 seed 点估计全正，平均绝对差为 +0.000676；pooled 95% CI 为 [-0.015489, 0.016591]。这是审计干净但很小、尚不能排除误差的正信号，不能写成固定融合失败。另一方面，三个逐 seed CI 均跨 0，shuffle 只在 seed 20260817 低于目标，未通过预注册 GO 门。

深度指标揭示了可继续利用的结构信号：soft fusion 的 task-group R@1 为 0.158170/0.157821/0.157821，明显高于 pairwise_B 的 0.069832/0.069832/0.067039；但 R@3 降为 0.420042/0.422137/0.422137，而 pairwise_B 为 0.456913/0.458310/0.454120。固定等权融合把更多正确步骤推到第一名，同时过度扰动前三名稳定性。行等权 MRR 为 0.340871/0.340313/0.340166，对 pairwise_B 为 0.341616/0.341809/0.339774，同样呈混合异质性。

保留的 `exp101_hard_gate` comparator 完整复现其强信号，task-group MRR 为 0.373694/0.379612/0.378026；它不是本实验的新 GO，也不参与公平 baseline 选择，但证明 Exp105 的运行框架没有把 Exp101 的既有 GO 信号抹掉。

资产 hash、15 个 outer-fold/inner-OOF 隔离、outer-held 覆盖一次、Gold 隔离、逐记录归一化、固定 alpha、shuffle 多重集、同记录数和预算审计全部通过。删除条件严格等于全局 `pairwise_B`。

顶层判定为 `SOFT_FUSION_POSITIVE_NOT_YET_GO`：`direction_no_go=false`。本结论只说明固定 alpha=0.5、逐记录 min-max 的线性等权融合尚未成为第二个 RQ GO；不得写成连续融合家族、责任排序方向、Exp101、pairwise_B 或 recency 的 NO-GO。下一次模块替换应直接针对“R@1 大幅提高、R@3 下降”的秩深度错配，而不是调本实验 alpha 或重跑。

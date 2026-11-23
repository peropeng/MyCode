# Exp96：责任主体组内 Pairwise 候选排序

本实验只做阶段 1 的严格 `task_group` OOF 可行性验证。固定数据边界为 AFTraj 去官方 test/task overlap 后的 731 条 train 记录（716 个 task group）；180 条 confirmation 只记录数量、组隔离和不透明边界摘要，未进入特征、拟合、评分或方法选择。

## 机制与比较

- `local`：E88 固定纯匿名结构局部步评分。
- `original_A`：E88 逐角色独立 logistic responsibility bridge。
- `pairwise_B`：每条 train 轨迹构造 Gold 与每个非 Gold 角色的双向差分，使用固定 `epochs=200, lr=0.05, l2=0.001, pos_weight=1.0` 学习组内 utility；推断时在轨迹内 softmax，并以固定 bridge weight 3.0 注入 E2。
- `deletion`：删除 B 的责任桥，必须与 `local` 完全相同。
- `recency`：预注册公平外部基线。
- `shuffled_B`：保持 B 的概率多重集和预算，只在匿名角色内确定性置换，作为负对照。

每个 seed 使用相同的 5 个 task-group 外层折；每个 outer-held 只由 outer-train 拟合 A/B。没有 API、token 或阈值搜索。

## 阶段 1 实际结果

固定的全局最强公平基线是 `original_A`（三 seed 平均 MRR 0.333533，高于 local 0.3123 和 recency 0.3256）。`pairwise_B` 的 E2 MRR 为：

| seed | original A MRR | pairwise B MRR | 相对提升 | task-group paired CI 下界 |
|---|---:|---:|---:|---:|
| 20260816 | 0.3340 | 0.3416 | +2.275% | +0.0012 |
| 20260817 | 0.3348 | 0.3418 | +2.091% | +0.0017 |
| 20260818 | 0.3318 | 0.3398 | +2.411% | +0.0017 |

三 seed 都是正向；审计、折间隔离、预测记录覆盖、删除等价和 shuffled 概率多重集检查全部通过。`pairwise_B` 相对 `shuffled_B` 的平均 MRR 差为 +0.051667。

E1 top-1 不是同步提升：

| seed | original A top-1 | pairwise B top-1 | B-A |
|---|---:|---:|---:|
| 20260816 | 64.98% | 63.47% | -1.51pp |
| 20260817 | 65.12% | 63.47% | -1.65pp |
| 20260818 | 64.30% | 63.34% | -0.96pp |

因此阶段结论是 `POSITIVE_NOT_YET_GO_STAGE1`：保留“组内 pairwise 能改善下游步排序”的真实正信号，但不把它写成 GO，也不自动评分历史 confirmation。下一步若继续，应先由主线程决定是否把 E1 top-1 不升但 E2 MRR 稳定提升作为新的冻结确认假设；不得事后修改本实验门槛。

正式结果见 `results/aggregate_results.json` 及三个 seed 文件。

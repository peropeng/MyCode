# Exp99：责任信号与强 Recency 底座的无参数秩融合

## 正式运行记录

- 冻结 runner：`5d9106a89dc8486b5be97c48f066fecc5da3e1e9`。
- 第 1 次正式尝试：`389cf6a5a59d85b00b3059797fc7ff4e9fdcadc2`，在边界审计阶段因 `boundary["pool"]` 同时被用作列表和整数计数而触发 `HARNESS_INVALID`；没有生成结果 JSON，不计方法失败。
- 第 2 次正式尝试：在修复后的 `5d9106a89dc8486b5be97c48f066fecc5da3e1e9` 上，以 3 个 seed 一次性完成，生成本目录 `results/` 下的唯一正式结果。
- 第 2 次生成的旧聚合错误地用行等权 MRR 做 verdict，与冻结的任务组等权主指标不一致；旧 `STOP_EXP99_FIXED_RRF_ONLY` 因此作废并记为 Harness 无效。
- 达到三次受限执行问题后，Sol 仅使用已缓存的 `group_mrr` 做一次聚合修复；没有重跑模型、折或数据。修复代码为 `8138ebf`，结果格式升级为 `Exp99-stage1-aggregate/1.1`。
- API/token/retry：`0/0/0`。

## 数据与审计边界

阶段 1 使用 731 条 train 记录、716 个 task group，3 seeds × 5 个 task-group OOF fold。AFTraj unsafe parquet 原始 1114 行先只投影 `conv_id/task` 构造 opaque 边界；随后只对 731 个 train `conv_id` 投影训练列。180 条 confirmation 与 163 条 official 只保留 `conv_id/task_group` 边界，没有读取 turns 或 Gold/error 字段。

三次 seed 的边界均为：loaded 1074、official 163（161 groups）、overlap 40、pool 911（884 groups）、train 731（716 groups）、confirmation 180（168 groups）。资产审计 32/32 通过，所有泄漏、预算、折隔离、匿名输入、删除等价、置乱多重集和并列秩审计通过。

## 阶段 1 结果

按冻结的任务组等权主指标，全局最强公平基线仍是 `pairwise_local_bridge`，三 seed 平均 MRR 为 `0.343700`。目标方法 `recency_rrf_pairwise_B` 平均 MRR 为 `0.345163`，绝对高 `0.001463`、相对高 `0.426%`。

| seed | Pairwise 任务组 MRR | RRF(B) 任务组 MRR | 绝对差 | 相对差 | 95% CI | 任务组 better / worse / tie |
|---|---:|---:|---:|---:|---|---:|
| 20260816 | 0.344260 | 0.345957 | +0.001697 | +0.493% | [-0.019820, 0.023588] | 268 / 333 / 115 |
| 20260817 | 0.344457 | 0.345015 | +0.000558 | +0.162% | [-0.020164, 0.022300] | 270 / 332 / 114 |
| 20260818 | 0.342382 | 0.344517 | +0.002135 | +0.624% | [-0.018458, 0.023145] | 267 / 331 / 118 |

其他公平基线的任务组等权三 seed平均 MRR：`recency=0.330520`、`local_structural=0.314238`、`recency_rrf_original_A=0.342698`。RRF(B) 相对这些基线和最强 Pairwise bridge 都为正，但三个 CI 均跨 0。

行等权诊断必须同时保留：RRF(B) 的行 MRR 三 seed 分别比 Pairwise bridge 低 `0.186% / 0.563% / 0.113%`。这说明增益依赖“每个任务等权”，而在记录较多的任务组上并不占优，是需要外部确认的数据异质性风险。

RRF(B) 的 R@1/R@3 分别为：

- 20260816：12.038% / 42.134%；
- 20260817：11.765% / 41.997%；
- 20260818：11.765% / 41.860%。

删除责任路由后三个 seed 均严格等于 recency。置乱责任概率多重集后，MRR 为 `0.308427/0.306214/0.303706`，均低于 RRF(B)，说明责任角色对应关系仍含有真实信号；但该信号没有在 recency 底座上超过 pairwise bridge。

## 预注册判定

结果 JSON 的 verdict 为：

`RRF_POSITIVE_NOT_YET_GO`

这是审计干净的探索性正结果：任务组等权主指标三 seed 都高于全局最强基线，但 CI 均跨 0，因此不能叫 GO，也不能进入论文结论。`direction_no_go=false`、`is_experiment_go=false`、`is_final_go=false`；没有使用 confirmation 或 official 做本实验确认。

触发依据是：任务组等权绝对差为 `+0.001697 / +0.000558 / +0.002135`，三 seed 同向；删除责任路由严格退回 Recency，置乱责任对应关系后均明显变差，且所有资产、泄漏和预算审计通过。

## 必须保留的统计风险

结果显示明确的加权异质性：三个 seed 的行级点差均为负，但冻结的任务组等权点差均为正；716 个 group 的 pooled 差为 `+0.001360`，95% CI `[-0.020195, 0.023100]`。

因此 Exp99 只能作为“很小、方向一致、尚不稳定”的条件性正信号。它没有达到 `CONTINUE_RRF_TO_NEW_EXTERNAL_CONFIRMATION` 的 CI 门槛，更不能作为第二个 GO；但也不存在停止该方向的绝对证据。下一步若继续，必须使用新的独立任务确认任务组等权提升，并同时报告行等权敏感性。

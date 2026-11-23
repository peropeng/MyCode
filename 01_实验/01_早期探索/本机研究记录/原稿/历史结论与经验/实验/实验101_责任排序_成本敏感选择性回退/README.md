# Exp101 责任排序：成本敏感选择性回退

本目录冻结一个可被否定的单一机制：门控器逐条在 `recency` 与已经验证的 `pairwise_B` 两个 arm 之间选择。门控器不新增候选、不增加 API/token 调用，也不引入第三个排序模块。

## Stage B OOF 授权边界

协议、数据 seal、runner 和合成测试已经冻结；Stage B 仅授权一次真实 Exp96 OOF 评分，当前仍未运行任何真实 OOF 或 Gold。开发对象固定为 Exp96 的 731 条训练记录、716 个 task groups、3 seeds × 5 个 task-group outer folds。每个 outer fold 的 gate 训练再做严格 4-way inner OOF：每个 inner arm 只用其余 3 个 outer-train folds 拟合，合并的 inner-held 预测训练 gate，最后只把 gate 应用于 outer-held 的干净 arm 预测。Exp97/98 的历史结果只用于缓存的 Oracle 上界审计，不能作为新的确认集。

`original_A` 和 `pairwise_B` 各为 3 seeds × 5 outer × (1 outer fit + 4 inner fits) = 75 次模型 fit；本次授权冻结尚未执行这些 fit。

门控输入只有预测时可见的 9 个字段：轨迹长度 `log1p`、角色数、pairwise 角色最大概率、top1-top2 margin、归一化熵、最后角色概率是否等于最大角色概率、最后一步 E2 数值分数是否等于全局最大值（并列也算）、E2 前两名数值分数差、E2 top 与 recency step 的数值分数差。Gold 只用于 inner OOF 训练组的优势标签和最终评价，不能进入特征或模型输入。

标签为 `RR(pairwise_B) > RR(recency)`，反向为 0，精确 ties 排除；样本权重为绝对优势并在训练组归一到均值 1。标准化仅 fit outer-train，logistic 参数固定为 L2=1.0、lr=0.05、200 epochs、threshold=0.5，不搜索阈值。

## 缓存 Oracle 上界（不是方法结果）

只从既有 `aggregate_results.json` 的 `e2.group_mrr` 计算 `max(recency,pairwise_B)`，不读取 Gold，也不进入 gate 或 GO：

| 数据 | task groups | Oracle 相对 recency |
|---|---:|---:|
| Exp96 OOF | 716 | +37.466%（三个 seed 均值；逐 seed 约 +37.1%～+37.7%） |
| Exp97 历史确认 | 168 | +44.395% |
| Exp98 历史官方测试 | 161 | +32.594% |

这是“如果逐条知道哪一个 arm 更好”的不可实现上界，用来说明选择空间，不是 Exp101 的提升、GO 或 Oracle 方法。

## 判定范围

三 seed 相对一次性选出的最强公平基线均为正、每个 paired bootstrap 95% CI 下界大于 0、删除全局 arm、shuffle 保持选择率且低于 gate、所有审计通过，才是 `SELECTIVE_GATE_FEASIBILITY_GO`。任何干净正信号但未过全部门槛都保留为 `SELECTIVE_GATE_POSITIVE_NOT_YET_GO`；稳定全不正时只写 `STOP_EXP101_FIXED_SELECTIVE_GATE_ONLY`，不扩大为 pairwise、recency 或责任排序方向 NO-GO。10% final-paper 门另行保留。

正式运行合同固定为一次 `runner.py --run`，输出必须是 `results/formal_nested_oof_results.json`；已有文件拒绝覆盖，禁止重试和调参。confirmation 评分仍被禁止。`runner.py --preflight`/`--dry-run` 只读协议并明确报告未评分；本次唯一 OOF 结果已写入固定路径。

## 正式 nested OOF 结果（唯一一次运行）

正式运行使用冻结 commit `a185bf459a5398a0ae8fef193ad13c8b29dc66a7`、Exp96 的 731 条记录/716 个 task groups、3 个 seed 和 5 个 outer folds。唯一运行耗时 225.61 秒，输出为 `results/formal_nested_oof_results.json`；没有 API/token 调用、重试或候选预算变化。全局最强公平基线一次性选为 `pairwise_B`，因为 task-group 平均 MRR 为 0.343700，高于 `recency` 0.330520、`original_A` 0.336003 和 `local` 0.314238。

主指标是 task-group 等权 MRR；CI 为 716 个 task groups 上的 5000 次 paired bootstrap。每行的 `CI95` 使用顶层最终判定采用的 `seed_summaries[*].ci_vs_global` 选择门相对全局 `pairwise_B` 差值区间，`better/worse/tie` 也是 task-group 配对计数。结果中的 `results_by_seed[*].ci_vs_fair[pairwise_B]` 仅作辅助敏感性分析，不用于顶层 verdict，避免两套口径混淆。

| seed | 选择门 MRR | pairwise_B MRR | 绝对提升 | 相对提升 | CI95 | better/worse/tie | 选择 pairwise / 回退 recency | shuffle 选择率 |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| 20260816 | 0.373694 | 0.344260 | +0.029434 | +8.55% | [0.019035, 0.039818] | 106 / 22 / 588 | 81.40% / 18.60% | 81.40% |
| 20260817 | 0.379612 | 0.344457 | +0.035155 | +10.21% | [0.026173, 0.044644] | 105 / 15 / 596 | 83.58% / 16.42% | 83.58% |
| 20260818 | 0.378026 | 0.342382 | +0.035644 | +10.41% | [0.026872, 0.045025] | 105 / 13 / 598 | 83.86% / 16.14% | 83.86% |

行等权敏感性结果同方向：

| seed | 选择门 / pairwise_B 行 MRR | 绝对提升 | 相对提升 | row better/worse/tie |
|---|---:|---:|---:|---:|
| 20260816 | 0.368632 / 0.341616 | +0.027016 | +7.91% | 107 / 28 / 596 |
| 20260817 | 0.376243 / 0.341809 | +0.034434 | +10.07% | 105 / 15 / 611 |
| 20260818 | 0.374687 / 0.339774 | +0.034912 | +10.28% | 105 / 13 / 613 |

选择门与 `pairwise_B` 的 group R@1/R@3 分别为：20260816 为 0.108939/0.456704 对 0.069832/0.456913，20260817 为 0.114525/0.466690 对 0.069832/0.458310，20260818 为 0.111732/0.461103 对 0.067039/0.454120。行等权 R@1/R@3 分别为：20260816 为 0.106703/0.447332 对 0.068399/0.452804，20260817 为 0.112175/0.462380 对 0.068399/0.454172，20260818 为 0.109439/0.456908 对 0.065663/0.450068。

汇总提升为 +0.033411 MRR，pooled 95% CI 为 [0.023990, 0.043117]，不跨 0；相对全局 `pairwise_B` 为 +9.72%。删除实验在三个 seed 均严格退回 `pairwise_B`（删除门控后等于全局基线）；shuffle 保持完全相同的选择率，但 MRR 降为 0.340966、0.336063、0.338453，均低于真实选择门的 0.373694、0.379612、0.378026。

审计结果全部通过：15 个 outer folds 中每个 outer-held 与 inner fit/held 的交集均为 0；inner OOF 对 outer-train 的记录和 task groups 恰好覆盖一次；outer arm 只在 outer-train 拟合；gate 训练记录只来自 inner OOF。Gold 没有进入特征或模型输入，Oracle 没有进入 gate、基线或 GO 判定；21 项冻结资产 hash 全匹配。

顶层精确判定为 `SELECTIVE_GATE_FEASIBILITY_GO`。三个 seed 都为正、每个 CI 下界都大于 0、删除与 shuffle 门通过、审计通过，因此这是 Exp101 的可行性 GO；不是 final paper GO。首个 seed 的相对提升为 8.55%，汇总相对提升为 9.72%，未满足最终论文的 10% 门；confirmation 仍未运行。结果 JSON 中每个 seed 的内部 `decision` 字段保留实现层的 `UNAGGREGATED_STAGE_A_RESULT` 标记，最终判定以顶层 `decision` 为准。

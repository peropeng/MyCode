# Exp107：Top-1 级联的效用加权选择性路由/回退

本实验只回答一个集成问题：第一章的冻结 `Exp106 Top-1 cascade` 能否作为结构化 arm，被第二章一个严格 OOF、Gold-free 的效用路由器选择，并稳定优于结构 arm、回退 arm 与既有 `Exp101` 硬门。

路由器复用 Exp101 固定的 9 个匿名结构特征及固定加权 logistic：L2=1、学习率 0.05、200 epochs、阈值 0.5。唯一变化是每个 outer fold 内，使用 4-way inner OOF 预测重新形成标签：`RR(exp106_top1_cascade) > RR(recency)`；完全并列样本排除，样本权重为绝对 RR 优势并归一到均值 1。outer-held 的路由特征、概率和决定均不读取 Gold。

这不是计算成本实验。`recency` 只是固定回退 arm；章节叙事使用“效用加权选择性路由/回退”，不声称真实延迟、token 或费用节省。

## 冻结合同

- 数据与切分：731 records / 716 task groups；3 seeds × 5 outer × 4 inner，task-group 隔离。
- 条件：`local/original_A/pairwise_B/recency/exp101_hard_gate/exp106_top1_cascade/selective_top1_cascade/deletion_router/deletion_top1/shuffle_router`。
- `deletion_router` 必须逐项等于 `exp106_top1_cascade`；`deletion_top1` 必须逐项等于 `exp101_hard_gate`。
- `shuffle_router` 在每个 outer-held fold 保持结构 arm 选择数，打乱路由决定；只要存在两类决定，就必须实际改变至少一项。
- 统计主指标为 task-group equal MRR；同时报告 row-equal MRR、R@1、R@3、5000 次 paired bootstrap、better/worse/tie 与选择率。
- outer-held Gold 只在路由决定完成后用于最终指标和诊断：非并列决策准确率、效用加权准确率、per-record oracle regret、相对 recency 捕获的 oracle gain。它们不进入训练特征，也不进入 GO 判定。
- 用户已确认 sealed asset hashes 全部匹配；正式命令不再重复额外资产安全预检。split、OOF 与 Gold 隔离仍按协议审计。
- 禁止阈值/超参搜索、confirmation 评分、API/token、覆盖与重试。正式输出固定为 `results/formal_nested_oof_results.json`，只运行一次。

## 双层判定

`A_PLUS_B_INTEGRATION_GO`：一次性从 `exp101_hard_gate`、`exp106_top1_cascade` 与常规公平 baselines 中按三 seed 平均 MRR 选出全局最强组件比较器；目标相对它三 seed delta 全正、逐 seed CI 下界均 >0，且 deletion/shuffle/隔离审计全部通过。

`TWO_CHAPTER_METRIC_GO`：在前一层通过的基础上，目标相对一次性最强常规公平 baseline 的三 seed 平均相对增益 >=10%，且三 seed 逐 seed CI 下界均 >0。10% 只约束三 seed 平均；逐 seed增益照实报告。

审计干净且存在非误差正增益但未过门，判 `POSITIVE_NOT_YET_GO`。只有三 seed 相对最强组件全部非正，才停止这一固定路由方案，`direction_no_go=false`。Harness 失败不算方法失败。

## 唯一正式 nested OOF 结果

冻结实现 commit 为 `7acb664`。唯一正式进程约 249 秒完成，结果文件 SHA-256 为 `94c3051d141af2d03d238a64ca32fb34679da19f35516f14b3ebb60240246e9d`。用户已确认 sealed hashes 匹配，命令未重复资产安全预检；协议内 15 个 outer fold 的 split、inner OOF、Gold 隔离、权重、删除和预算审计全部通过，API/token/retry 为 0，未评分 confirmation。

一次性全局最强组件比较器为 `exp106_top1_cascade`，最强常规公平 baseline 为 `pairwise_B`：

| seed | target MRR | Exp106 MRR | delta / CI | vs pairwise_B | 选择率 | weighted accuracy | oracle regret |
|---|---:|---:|---:|---:|---:|---:|---:|
| 20260816 | 0.377519 | 0.377519 | 0 / [0, 0] | +9.6612%, CI [0.020203, 0.047184] | 100% | 61.0600% | 0.087435 |
| 20260817 | 0.377253 | 0.377253 | 0 / [0, 0] | +9.5211%, CI [0.019464, 0.046792] | 100% | 60.8881% | 0.087472 |
| 20260818 | 0.377398 | 0.377398 | 0 / [0, 0] | +10.2271%, CI [0.021295, 0.049117] | 100% | 60.9229% | 0.087368 |

固定阈值在 15/15 outer folds 都选择 Exp106，目标因而逐记录退化为 Exp106：相对最强组件的 better/worse/tie 都是 `0/0/716`，shuffle 也无法在保持 100% 选择率时改变决定。相对 pairwise_B 的三 seed 平均相对增益为 **9.8031%**，pooled CI `[0.020847, 0.046971]`；这是 Exp106 已有正信号的完整保留，不是 Exp107 路由带来的新增提高，也未达到预冻结的平均 10% 两章门槛。

outer-held 诊断显示仍存在未捕获的 arm 互补空间：非并列 679–680 条，普通决策准确率 56.55%–56.70%，效用加权准确率 60.89%–61.06%，只捕获相对 recency 的 oracle gain 约 34.82%–34.96%。这些 Gold 后验诊断不进入 GO，但定位了失败机制为“固定加权 logistic + 0.5 阈值全选结构 arm”，而非证明两 arm 不可路由。

顶层判定为 `STOP_EXP107_FIXED_ROUTING_ONLY`：`A_PLUS_B_INTEGRATION_GO=false`，`TWO_CHAPTER_METRIC_GO=false`，`direction_no_go=false`。该结论只淘汰这一固定路由实现，不否定 Exp106 的 RQ GO、Exp101 的既有 GO或效用加权选择性路由方向。

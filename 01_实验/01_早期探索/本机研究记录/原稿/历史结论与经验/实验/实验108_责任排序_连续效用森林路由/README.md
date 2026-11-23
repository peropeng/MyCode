# Exp108：连续效用森林路由

本实验升级 Exp107 的二值线性路由器：在每个 outer fold 内，用 4-way inner OOF 预测构造连续效用
`u = RR(exp106_top1_cascade) - RR(recency)`，再以冻结的 9 个 Gold-free 结构特征训练固定
`ExtraTreesRegressor`。outer-held 仅当 `u_hat > 0` 时选择 Exp106，否则回退 recency。

Gold 只用于 inner-OOF 连续目标和最终评价；outer-held 的特征、预测与路由决定不读取 Gold。所有超参和
零阈值均在正式运行前冻结，不搜索阈值、不调参、不评分 confirmation。

## 冻结合同

- 数据：731 records / 716 task groups；3 seeds × 5 outer × 4 inner，task-group 严格隔离。
- 模型：`ExtraTreesRegressor(n_estimators=256, max_depth=4, min_samples_leaf=20, max_features=1.0, bootstrap=False, n_jobs=1)`；`random_state = seed + 1009 * outer_fold + 108`。
- 条件：4 个常规 baseline、Exp101、Exp106、Exp107、`utility_forest_router`、`deletion_router`、`shuffle_router`。
- `deletion_router` 逐项等于 Exp106；shuffle 在每个 outer-held fold 保持结构 arm 选择数。
- 主指标：task-group equal MRR；辅助报告 row MRR、R@1、R@3、选择率、回归 MAE、符号准确率、效用加权准确率、oracle regret 与 captured gain。
- paired bootstrap 5000 次。全局组件比较器按三 seed 平均 MRR 一次性从公平 baselines、Exp101、Exp106、Exp107 中选出。
- 用户已确认 sealed assets 全部匹配；不重复资产哈希安全预检。协议内 split、OOF、Gold 隔离与控制条件审计保留。
- 正式输出固定为 `results/formal_nested_oof_results.json`，不可覆盖、不可重试，只运行一次。

## 判定

`UTILITY_FOREST_INTEGRATION_GO`：协议审计、deletion 与 shuffle 均通过；相对一次性全局最强组件的三 seed delta 全正，且 pooled task-group CI 下界 > 0。逐 seed CI 只报告，不进入这一层门槛。

`TWO_CHAPTER_METRIC_GO`：前一层通过；相对一次性最强常规公平 baseline 的三 seed 平均相对增益 >=10%；三 seed delta 全正且每 seed CI 下界 >0。

审计干净且存在非误差正增益但未过全部门槛，判 `POSITIVE_NOT_YET_GO`。只有相对最强组件三 seed 全非正才判 `STOP_EXP108_FIXED_FOREST_ONLY`，且 `direction_no_go=false`。Harness 无效不算方法失败。

## 唯一正式 nested-OOF 结果

冻结实现 commit 为 `1db51a9b3791681d99633396a1866ffd62968b15`。唯一正式进程约 292 秒完成，结果 SHA-256 为 `72d67e362f96e77939e1db0f29b9ee318d6757fd2d4f613dbf177aacc832f422`；未重复资产哈希预检、未重试、未评分 confirmation。

一次性全局最强组件为 `exp106_top1_cascade`（与退化为 Exp106 的 Exp107 同分，按冻结顺序取 Exp106），最强常规公平 baseline 为 `pairwise_B`：

| seed | target MRR | Exp106 MRR | delta / 95% CI | vs pairwise_B | 选择 Exp106 | weighted accuracy |
|---|---:|---:|---:|---:|---:|---:|
| 20260816 | 0.412092 | 0.377519 | +0.034573 / [0.020334, 0.049486] | +19.7038% | 64.43% | 76.43% |
| 20260817 | 0.406812 | 0.377253 | +0.029559 / [0.016984, 0.042808] | +18.1024% | 70.86% | 74.09% |
| 20260818 | 0.413805 | 0.377398 | +0.036408 / [0.021906, 0.051450] | +20.8608% | 62.93% | 77.18% |

相对 Exp106 的 pooled delta 为 **+0.033513**，95% CI **[0.020493, 0.047276]**；相对 pairwise_B 的三 seed 平均相对增益为 **+19.5557%**，三 seed CI 下界均大于 0。deletion 逐项等于 Exp106 且三 seed 都低于 target；保持每 fold 选择数的 shuffle 也三 seed都低于 target。所有 split、inner-OOF、Gold 隔离、特征、森林超参、记录数与预算审计通过。

顶层判定为 `TWO_CHAPTER_METRIC_GO`：`UTILITY_FOREST_INTEGRATION_GO=true`，`TWO_CHAPTER_METRIC_GO=true`。这是严格 nested-OOF 的两章指标门通过；结果仍明确标记 `is_final_paper_go=false`，未把未见外部确认或最终论文验收混入本实验结论。

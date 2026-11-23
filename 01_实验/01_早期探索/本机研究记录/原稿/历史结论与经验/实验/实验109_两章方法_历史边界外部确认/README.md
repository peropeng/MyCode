# Exp109：两章方法的历史边界外部确认

本实验将 Exp108 冻结的连续效用 ExtraTrees 路由器零调参迁移到 Exp97 confirmation
和 Exp98 official-test 两个历史边界。它们已被早期实验使用，所以结论只是
**frozen historical-boundary external stress**，不冒充 pristine unseen confirmation。

## 冻结方法

- 每个 seed 仅用 Exp96 train 的 5-fold task-group 严格 OOF 预测构造 731 个连续效用目标和 9 个 Gold-free 特征。
- 以 Exp108 同参数 ExtraTrees 拟合全训练路由器；外部 arm 按 Exp97/98 冻结合同只在 Exp96 train 拟合。
- 先完成外部 arm 预测、Exp101/Exp108 决策和保持选择数的 shuffle，再由冻结 loader 挂接边界 Gold 最终评价。
- 条件包含 4 常规 baseline、Exp101、Exp106、Exp108 target、deletion=Exp106 和 shuffle；oracle 只作诊断。
- 用户已确认资产哈希全部匹配，不重复安全哈希预检。

## 决策

每个边界的最强公平 baseline 与最强组件比较器分别按三 seed 平均 MRR 一次性选定。
边界 GO 需相对最强公平 baseline 三 seed 平均相对增益至少 10%、每 seed delta
为正且 CI 下界大于 0；同时相对最强组件三 seed delta 全正、pooled CI 下界大于 0，
且 deletion/shuffle/隔离/预算全过。

总体 `TWO_CHAPTER_OPENING_EXTERNAL_GO` 要求至少一个边界 GO，另一边界相对自身最强公平 baseline
的三 seed 平均绝对 delta 不为负。有清洁正信号但未全过时保留为 `POSITIVE_NOT_YET_GO`；
只有两边界对公平 baseline 都稳定全非正才停此固定外推，`direction_no_go=false`。

## 执行

```bash
python runner.py --preflight
python runner.py --run \
  --source-root /Users/peroyang/My/MyWork/worktrees/0823-exp92-group-conformal/实验/实验33_旧版场景F责任主体/real_feasibility_group6 \
  --data-root /Users/peroyang/My/MyWork/worktrees/0822-aftraj-asset/third_party/data/AFTraj \
  --output "$PWD/results/formal_external_confirmation_results.json"
```

正式运行只允许一次，输出不可覆盖、不可重试、不可调参。

## 唯一正式结果

冻结实现 commit 为 `c1981f9`。唯一正式进程约 100 秒完成，结果 SHA-256 为
`02c172b668b780fba1bf8471f454a3c7f6b5a3352fd46c2b80c5235400e4ace8`。没有重试、调参、读取历史聚合指标或重复资产哈希安全预检。

| 边界 | target MRR | 最强公平 baseline | 相对增益 / pooled CI | 最强组件 | 组件 delta / pooled CI | 选择 Exp106 |
|---|---:|---:|---:|---:|---:|---:|
| Exp97 confirmation | 0.429745 | pairwise_B 0.363027 | +18.3781% / [0.022889, 0.110629] | Exp106 0.400539 | +0.029206 / [-0.005758, 0.064602] | 65.56% |
| Exp98 official test | 0.384720–0.386583 | recency 0.328717 | +17.4145% / [0.024963, 0.091046] | Exp101 0.361692 | +0.023028–0.024891 / [-0.007008, 0.058441] | 67.48%–68.10% |

两个边界相对各自最强公平 baseline 都超过 10%，每 seed delta 全正且每 seed CI 下界大于 0；
相对最强组件的每 seed delta 也全正。但两个边界的组件 pooled CI 下界分别为
`-0.005758` 和 `-0.007008`，未过冻结的组件独立性门。deletion 逐项等于 Exp106，shuffle 三 seed
都低于 target；30 次 Exp96 OOF arm fit、12 次外部 arm fit、6 次 router fit 与所有 Gold 隔离/预算审计全部通过。

因此顶层判定为 `POSITIVE_NOT_YET_GO`，`direction_no_go=false`。这是两个外部历史边界上都可复现的大幅正增益，
只因相对强组件的 pooled CI 尚跨 0 而不升格为 `TWO_CHAPTER_OPENING_EXTERNAL_GO`；不将它解读为方向 no-go。

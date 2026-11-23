# Exp104 责任排序：稳健不确定性门控升级

Exp104 是 Exp101 固定 selective gate 的一次预注册模块升级。数据、Gold、Exp96 的 `pairwise_B` / `recency` arms 和原 9 个 gate 特征全部保持不变；新增的后置护栏只有两个固定条件：旧 gate 已选择 `pairwise_B`，且 pairwise 概率至少 `0.65`、top1-top2 margin 至少 `0.15`。任一条件不满足都回退到 recency。阈值在正式运行前冻结，不搜索、不调参、不增加 API/token/候选预算。

所有拟合均为 Exp96 的 731 条记录、716 个 task groups、3 seeds × 5 outer folds 的严格 nested OOF。Gold 只用于 inner OOF 标签和最终评估；确认集与 Exp97/98 Gold 不读取。对照包含 `local`、`original_A`、`pairwise_B`、`recency`、Exp101 `selective_gate`、Exp104 `robust_selective_gate`、删除全局 arm 和保持选择率的 shuffle。

## 正式结果

唯一正式命令：

```bash
python3 runner.py --run \
  --source-root /Users/peroyang/My/MyWork/worktrees/0823-exp92-group-conformal/实验/实验33_旧版场景F责任主体/real_feasibility_group6 \
  --data-root /Users/peroyang/My/MyWork/worktrees/0822-aftraj-asset/third_party/data/AFTraj \
  --output results/formal_nested_oof_results.json
```

`results/formal_nested_oof_results.json` 是唯一一次运行产物（hash `64c7aed9334bd88341b05a5d5d09693fb41e4b390ddb27a39fd4be66481382d2`）。21 项资产/泄漏/预算审计全部通过，API/token 均为 0，确认评分为 false。

| seed | robust MRR | pairwise_B MRR | delta | 95% CI | robust pairwise 选择率 |
|---|---:|---:|---:|---|---:|
| 20260816 | 0.330520 | 0.344260 | -0.013740 | [-0.037424, 0.010005] | 0.00% |
| 20260817 | 0.330520 | 0.344457 | -0.013937 | [-0.036982, 0.010006] | 0.00% |
| 20260818 | 0.330520 | 0.342382 | -0.011861 | [-0.035180, 0.012223] | 0.00% |

护栏没有在任何 outer-held 记录上放行 pairwise，因而退化为 recency；shuffle 与真实护栏相同，删除检查通过，但 shuffle 没有低于真实护栏。顶层判定为 `STOP_EXP104_ROBUST_GUARD_ONLY`。这是对本次固定阈值护栏“过度保守、未触发”的结论，不是对 Exp101 的正向结果、pairwise_B、recency 或责任排序方向的 NO-GO；CI 跨 0 也不提供正向证据。下一次升级应优先改为可校准的分层/软护栏并重新预注册，而不是重写本次结果。

`python3 -m unittest discover -s tests -p 'test_*.py'`：21/21 通过。

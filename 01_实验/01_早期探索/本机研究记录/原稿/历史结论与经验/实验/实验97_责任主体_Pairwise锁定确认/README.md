# Exp97：责任主体 Pairwise 未见确认集锁定复跑

## 结论

本实验严格按冻结协议只进行了一次正式运行，使用 3 个预注册 seed。结论为：

`CONFIRMED_POSITIVE_NOT_YET_GO`

这不是方法 NO-GO，也不是第二个实验级 GO。可直白地理解为：在 180 条从未参与 Exp96 拟合、选择或调参的 confirmation 数据上，pairwise_B 的下游排序平均确实更好；但是样本量下的 95% task-group 配对置信区间仍略微跨过 0，因此证据还不够稳，不能称为 GO。

## 冻结与运行审计

- 冻结 runner commit：`836be7639d430f8a6df2b24f5fd648f88de6fe4d`。
- 数据：731 条 train、716 个 train task groups；180 条 confirmation、168 个 confirmation task groups。
- confirmation Gold 只在 731 条 train 完成拟合后用于最终评分；没有用于模型拟合、方法选择或阈值选择。
- 资产 hash、分组隔离、匿名结构输入、预测记录覆盖、删除等价和 shuffled 负对照均通过。
- API/token/retry：0/0/0。
- 正式评分次数：1；没有第二次运行。

正式命令为：

```text
python3 实验/实验97_责任主体_Pairwise锁定确认/runner.py \
  --source-root /Users/peroyang/My/MyWork/worktrees/0823-exp92-group-conformal/实验/实验33_旧版场景F责任主体/real_feasibility_group6 \
  --data-root /Users/peroyang/My/MyWork/worktrees/0822-aftraj-asset/third_party/data/AFTraj \
  --output 实验/实验97_责任主体_Pairwise锁定确认/results \
  --formal-confirmation --all-seeds
```

## 主要数据（pairwise_B 对冻结 strongest comparator original_A）

三次 seed 的方法输出相同，因为拟合过程确定性；seed 主要影响 bootstrap 和 shuffled negative control。

| seed | original_A E2 MRR | pairwise_B E2 MRR | 绝对提升 | 相对提升 | 95% CI（MRR 差） |
|---|---:|---:|---:|---:|---:|
| 20260816 | 0.343020 | 0.353452 | +0.010432（+1.0432pp） | +3.0412% | [-0.000250, +0.029335] |
| 20260817 | 0.343020 | 0.353452 | +0.010432（+1.0432pp） | +3.0412% | [-0.000266, +0.030382] |
| 20260818 | 0.343020 | 0.353452 | +0.010432（+1.0432pp） | +3.0412% | [-0.000335, +0.030614] |

这里的 CI 单位是 MRR 差，不是相对百分比。三个下界分别约为 -0.025pp、-0.0266pp、-0.0335pp，均没有严格大于 0。合并 168 个 task groups 的 pooled CI 为 `[-0.000116, +0.029731]`，同样跨 0。

## 其他指标

| 条件 | E2 MRR | R@1 | R@3 |
|---|---:|---:|---:|
| local | 0.334939 | 12.7778% | 38.8889% |
| original_A | 0.343020 | 8.3333% | 38.8889% |
| pairwise_B | 0.353452 | 10.0000% | 40.5556% |
| deletion（应等于 local） | 0.334939 | 12.7778% | 38.8889% |
| recency | 0.323388 | 8.8889% | 41.1111% |

shuffled_B 的 MRR 分别为 `0.330262 / 0.306741 / 0.310588`，都低于 pairwise_B；概率值的 multiset 在打乱前后保持不变。因此正向信号不是单纯来自“存在一组概率”或额外预算。删除责任桥后与 local 完全相同。

E1 role top-1 诊断中，pairwise_B 为 `60.5556%`，original_A 为 `59.4444%`，提高 `+1.1112pp`；但 168 个 task-group bootstrap CI 为 `[-2.381pp, +4.762pp]`，所以 E1 也不能单独作为稳健 GO 证据。pairwise_B 相对 original_A 的逐条 top-1 配对为：6 条更好、4 条更差、170 条相同。

## 本次结论的边界

本实验证明了一个有希望但尚未达到确认门槛的事实：pairwise responsibility 的 soft distribution 在未见 confirmation 上把 E2 MRR 从 `0.343020` 提高到 `0.353452`，三 seed 方向一致，且 shuffled/deletion 对照符合预期。

它没有证明最终论文级 GO，也没有满足“每个 seed CI 下界大于 0”的稳定性要求。因为 pooled CI 仍跨 0，本次不写 STOP：停止会错误地把“正向但样本不够稳”当成真实失败。下一步必须由主线程重新冻结一个独立确认/扩大任务边界或其他最小验证方案，不能修改本次结果或事后改写门槛。

结果文件：

- `results/aggregate_results.json`
- `results/exp97_seed_20260816.json`
- `results/exp97_seed_20260817.json`
- `results/exp97_seed_20260818.json`
- `results/asset_audit.json`

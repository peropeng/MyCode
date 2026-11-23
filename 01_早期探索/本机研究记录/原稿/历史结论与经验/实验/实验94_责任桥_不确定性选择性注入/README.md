# Exp94：责任桥不确定性选择性注入（阶段 1，731 条 train）

## 先说结论

本阶段没有证明“选择性注入”比全量责任桥更好，因此不能进入 180 条 confirmation，也不能记为第二个 GO。

准确结论是：`COMBINATION_NO_GAIN_PRESERVE_BRIDGE_SIGNAL`。

- 被检验的目标机制是：责任概率置信度低时回退到 local，只在 `ranking_change=true` 且 margin 达到阈值时使用责任桥。
- 这个门在 3 个 seed 的 15 个 outer fold 中都选择了 `no-margin`，所以实际等价于“凡是责任桥会改变排序就使用责任桥”。
- 因而 selective 与 `always_bridge` 的 MRR 在三个 seed 中完全相同：选择性门没有带来新增提升。
- 但责任桥本身相对 local 的正向信号保留：3 个 seed 的相对提升约为 **6.24%—7.20%**，task-group paired bootstrap 的 MRR 差值 95% CI 下界均大于 0。
- 这只排除当前“margin 阈值选择性门”这一组合机制，不否定 E85/E88 的责任桥方向，也不构成 `TRUE_METHOD_NO_GO`。

## 阶段边界

本轮严格只用 E33/E88 冻结池中的 **731 条 train 记录**，按 `task_group` 做 5-fold outer OOF；每个 outer-train 内再做 5-fold inner OOF 选择阈值。180 条 confirmation 只用于冻结边界的计数、分组不交集和 opaque identifier digest，未进入特征、模型拟合、阈值选择、排序或统计。

输入沿用 E88 的纯匿名结构特征和固定步骤权重；没有网络、LLM、API、token 或第三模块。候选阈值只有 `no-margin`、`q0.50`、`q0.65`、`q0.80`。阈值选择只看 inner OOF 的 task-group macro MRR，并相对于 `max(local, always_bridge, recency)` 计算 utility。

## 结果（中文解释）

| seed | local MRR | always bridge MRR | selective MRR | selective 相对最强公平基线 | bridge 相对 local | bridge-vs-local 95% CI（绝对 MRR） |
|---|---:|---:|---:|---:|---:|---:|
| 20260816 | 0.3123 | 0.3340 | 0.3340 | 0.00% | +6.95% | [0.0093, 0.0342] |
| 20260817 | 0.3123 | 0.3348 | 0.3348 | 0.00% | +7.20% | [0.0102, 0.0351] |
| 20260818 | 0.3123 | 0.3318 | 0.3318 | 0.00% | +6.24% | [0.0067, 0.0326] |

这里的“selective 相对最强公平基线为 0”不是没有提升，而是因为每个 seed 的最强公平基线正好是 `always_bridge`，而 selective 与它逐条排序相同。真正保留下来的提升是 **always bridge 相对 local**，不是 margin 门新增的提升。

门并未退化成全接收或全拒绝：outer-held 路由覆盖率约 **66.67%—80.14%**，且各 fold 都发生过排序改变；但 inner OOF 中所有 fold 都认为 `no-margin` 的 utility 最好，三个分位数门均更差。外层的 local-on-routed 约为 **69.7%—70.1%**，说明被路由的样本中全量桥仍常常有帮助，但门没有识别出应回退的伤害样本。

匹配覆盖随机门和 shuffled responsibility 均不是新的正向证据：它们的 MRR 低于全量 bridge，但这只能说明责任桥信号不等于随机置换，不能把它包装成 selective 门的增益。

## 硬审计

- train task-group 与 confirmation task-group 交集为 0；outer/inner group fold 均不交叠。
- 731 条 train 记录被 outer folds 恰好覆盖一次。
- 删除门的排序逐条等于 Base local。
- 结构输入不含错误词、长度、位置、task、domain、role name、task ID 或 Gold。
- confirmation 未评分、未用于阈值选择、未用于模型拟合。
- API/token 调用均为 0。
- 数据与源代码 SHA-256 与冻结 `data_seal.json` 一致。

## 正式执行审计

正式 runner 共尝试 3 次，没有第 4 次：

1. 第 1 次在正式评分前被错误的 official-test 计数断言拦截：`len(test_ids)=332` 被误当成 official-test 记录数，实际记录数为 163；这是 HARNESS_INVALID，未产生方法结果。
2. 修复计数后第 2 次完整跑完 3 个 seed。方法指标和嵌套 OOF 证据有效，但发现 aggregate 审计把“confirmation_used_for_scoring=false”和“api_calls=0/token_calls=0”当成失败；这是审计极性错误，不能把它写成方法失败。
3. 修复审计极性后第 3 次启动；在 20260816 输出生成后，按执行边界停止，不再进行第 4 次重跑。主线随后只用现有三个 seed JSON 做 Sol-only 离线聚合复核；确认预测、排名、MRR、CI 和 asset payload 完全不变，仅将审计通过位修正为 `true`，并将裁决修正为 `COMBINATION_NO_GAIN_PRESERVE_BRIDGE_SIGNAL`。这不是新的方法运行或确认实验。

上述都是执行/Harness 问题，不计入同一冻结目标的实质方法失败次数。当前冻结目标的实质结论只有：**margin 选择性门没有新增增益；全量责任桥的正向信号保留**。

## 后续边界

本实验到此停止继续扩展。不得读取 180 条 confirmation 来为该门补故事，也不得因为该组合无增益而停止责任桥方向。若要继续，必须由主线程重新冻结一个理论上不同的机制，并明确新的确认资格；本目录本阶段不声称 GO。

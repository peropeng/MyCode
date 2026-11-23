# Exp95：责任桥局部证据兼容性风险门（阶段 1）

## 结论

本实验阶段 1 的固定结论是：`COMBINATION_NO_GAIN_PRESERVE_BRIDGE_SIGNAL`。

这句话的含义是：

- **兼容性风险门没有带来新的提升**。它相对每个 seed 的最强公平基线（local、always bridge、recency 三者取强）没有正增益；seed 20260817 还下降 **0.3584%**，另外两个 seed 与 always bridge 完全相同。
- **不能据此否定责任桥本身**。固定 `always_bridge` 相对 `local` 在三个 seed 都保持正向，MRR 相对提升约 **6.24%—7.20%**，其 task-group paired bootstrap 绝对 MRR CI 下界分别为 **0.0093、0.0093、0.0067**，均大于 0。
- 这不是 `TRUE_METHOD_NO_GO`，也不是 confirmation GO。它只排除“用 local 最佳分数差作为 override-cost、以 compatibility threshold 选择性注入”的新增机制。

## 固定边界与机制

本阶段只评分 **731 条 train 记录、716 个 task_group**，按 task_group 做 3 seeds × 5 outer folds；每个 outer-train 内再做 5-fold strict OOF 选择阈值。180 条 confirmation 只用于边界计数、分组不交集、opaque identifier digest 和文件 hash，**没有进入模型拟合、阈值选择、排序或统计**。

方法矩阵为：

- `local`：E88 纯匿名结构 local score；
- `always_bridge`：local score + 固定 `3.0 ×` strict OOS 匿名责任概率；
- `selective`：只有 full 与 local 会改变排序，且 top responsibility role 的 local `override_cost` 不超过 inner OOF 选择的阈值时，才使用 bridge，否则回退 local；
- 阈值候选严格为 `zero`、`q0.25`、`q0.50`、`q0.75`、`no-gate`；没有使用 responsibility margin；
- `matched_random` 与 `shuffled_responsibility` 是保持路由覆盖率/概率多重集的负对照；`deletion` 必须逐条等于 local。

## 三个 seed 的结果

| seed | local MRR | always bridge MRR | selective MRR | selective 相对最强公平基线 | always bridge 相对 local | bridge-vs-local 绝对 MRR CI |
|---|---:|---:|---:|---:|---:|---:|
| 20260816 | 0.3123 | 0.3340 | 0.3340 | 0.0000% | +6.9484% | [0.0093, 0.0342] |
| 20260817 | 0.3123 | 0.3348 | 0.3336 | -0.3584% | +7.2046% | [0.0093, 0.0335] |
| 20260818 | 0.3123 | 0.3318 | 0.3318 | 0.0000% | +6.2440% | [0.0067, 0.0326] |

补充：selective 的 outer-held 路由覆盖率为 **73.3242%—74.5554%**，不是全接收或全拒绝；15 个 outer fold 均发生过排序改变。三 seed 相对最强公平基线的平均相对差为 **-0.1195%**，相对 matched-random 和 shuffled controls 的平均差分别为 **-1.6671%** 和 **-12.5381%**。

## 审计

- 731 条记录被 outer folds 恰好覆盖一次；outer/inner task_group 均无交集。
- `override_cost` 只由匿名结构 local score 计算；top role 概率同分使用匿名稳定 hash；Gold 不参与路由。
- `deletion == local` 逐条成立；结构输入未读取错误词、长度、位置、task、domain、role name、ID 或 Gold。
- 三个 seed 的 5000 次 task-group paired bootstrap、固定候选集、confirmation 未评分、零 API/token 预算审计均通过。
- 正式执行共 2 次：第 1 次在评分前发现 data seal 中人工录入的源 hash typo，属于 HARNESS_INVALID；第 2 次完整完成三 seed。随后只修正“expected false 的 confirmation-used 审计极性”并对既有 seed JSON 离线重聚合，没有重算 OOF、没有修改任何分数。

## 绝对停止范围

到此停止 Exp95 本目录的继续扩展，不读取 180 条 confirmation 做补故事，也不追加第三模块或调整阈值。停止对象仅为：**当前 override-cost compatibility gate 作为责任桥的新增组合机制没有可证明增益**。保留 E85/E88 与本实验中 `always_bridge` 相对 local 的正向责任桥信号；若继续，必须重新冻结理论上不同的机制和独立资格边界。

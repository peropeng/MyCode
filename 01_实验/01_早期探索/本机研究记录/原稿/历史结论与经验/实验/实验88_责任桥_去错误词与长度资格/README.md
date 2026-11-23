# Exp88：责任桥纯结构输入的去错误词与长度资格审计

## 目的和边界

Exp85 在去除 role/task/domain/position 后仍有正向结果，但输入还保留错误、验证、重试词和长度/活动量特征。本实验只做一个预冻结诊断：把这些词面、字符串长度、绝对消息/动作数量和位置全部排除，仅保留匿名结构布尔量和比例，例如字段是否存在、JSON 是否可解析、匿名 JSON 类型/有限 arity/嵌套形状、结构重复率和多样性率。

原始 role 只用于每条轨迹建立 `role_0`、`role_1` 等匿名映射；原始 role/tool 名、task、domain、conv_id、task_group、`mistake_agent` 和 `mistake_step` 不进入模型输入。`task_group` 只用于 E33 冻结切分和配对统计。E2 的 `full` 只在纯结构局部分数上增加严格 OOS 的匿名责任概率；`no_bridge` 将 prior 固定为 0；shuffle 在每条 confirmation 轨迹内置换匿名 role 概率。recency 只作为外部强基线，不是方法输入。

## 冻结资产和执行

- E33/E85 冻结数据：731 train、180 confirmation、168 个 task groups；官方 test 与重叠任务按原协议排除。
- 3 个预注册 seed：20260816、20260817、20260818。
- 每个条件都是同一 180 条有效 confirmation、同一结构输入和同一调用预算。
- E33 源文件、AFTraj 数据和 Exp85 original replay/aggregate 的 SHA-256 全部匹配；train/confirm、5-fold OOF 和模型输入审计通过。

运行器和协议在执行前提交于 `9710406` 的父提交 `1419b88` 之后；结果文件见 `results/`。

## 结果（中文解释）

三个 seed 的 `full`、`local` 和 `no_bridge` 点估计完全相同：

| 条件 | MRR | R@1 | R@3 |
|---|---:|---:|---:|
| full 纯结构 + OOS 责任桥 | 0.3430 | 8.33% | 38.89% |
| local 纯结构局部证据 | 0.3349 | 12.78% | 38.89% |
| no_bridge 删除责任桥 | 0.3349 | 12.78% | 38.89% |
| recency 外部强基线 | 0.3234 | 8.89% | 41.11% |
| oracle 上界 | 0.5233 | 22.78% | 71.67% |

因此，`full` 相对最强公平基线（local/no_bridge，MRR=0.3349）只提高 0.0081，即约 **2.42%**。三个 seed 的逐组 paired 结果都是 88 组更好、13 组更差、79 组相同；但 task-group paired bootstrap 95% CI 下界分别为 -0.0206、-0.0211、-0.0219，均跨过 0，因此不能称为稳定统计 GO。E1 责任主体 Top-1 为 59.44%，与 train-only majority 59.44% 完全相同，没有 E1 提升。

桥破坏性对照也没有完全通过：shuffle bridge 的 MRR 分别为 0.3266、0.3371、0.3101；第二个 seed 的 0.3371 反而高于 no_bridge 的 0.3349，说明“置乱后必然消除桥增益”并非三个 seed 一致成立。

## 结论

最终判定为 `POSITIVE_NOT_YET_GO`，不是 `GO`，也不是方向 `NO-GO`。可复现的事实是：在完全去掉错误词、长度/活动量和位置后，纯结构 bridge 在 3 个 seed 都比 local 高约 2.42%，但幅度很小、CI 跨 0，且 shuffle 审计有一个 seed 不通过。

若将来停止，绝对停止对象只能是“本次固定纯结构输入 + 固定权重 + 当前 E33 confirmation”的实现；原因是它没有达到预注册的 10% 相对提升、CI 下界大于 0 和一致破坏性对照门槛。该结论不否定 Exp85 的历史部分正向结果，也不构成责任桥方向的 `TRUE_METHOD_NO_GO`。

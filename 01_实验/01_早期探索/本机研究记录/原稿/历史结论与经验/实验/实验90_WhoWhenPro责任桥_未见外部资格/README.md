# Exp90：Who&When Pro 匿名责任桥未见外部资格探针

## 当前边界

本实验只回答一个窄问题：在尚未参与 adapter 设计的新 Who&When Pro 页面中，是否有足够多的多角色轨迹，且 Gold 的责任主体和步骤能从释放的 `agent/agent_id + round + position` 精确映射到一个事件。通过资格门后，才在这些行上运行 AFTraj 训练的匿名结构责任桥。

这不是 Exp80 safe/unsafe Exact-F1 配对确认，也不是把 failure-only 外测直接写成论文 GO。旧 Exp81 样本和已打开的 Exp83 六页只用于 schema/Gold 映射审计与 ID 排除，禁止进入本实验的方法指标。

## 第一次下载：采样设计无效（不计方法失败）

首次预注册的连续早期 offset `[100,200,300,400,500,600]` 共返回 600 行；去除 9 个与旧缓存重叠的 ID 后剩 591 行，但 `eligible=0、task_groups=0`。其中 170 行是只有 `agents+round` 的 round-only，396 行是单 agent flat action，25 行虽有 Gold agent 但只有 `stage`、没有可审计的 event-level step/round.position。这个结果证明的是“连续早期 offset 没覆盖目标 schema”，不是“Who&When Pro 没有评价对象”：预下载 887 行已经有 312 条/235 groups 的精确映射。

因此第一次结果保存为 `results/initial_sampling_invalid.json`，不计方法失败、不触发资产全局 STOP，也不运行方法指标。第二次只修正采样层，不改变 adapter、模型、指标或阈值。

第二次首个修正页确实返回了 100 条 eligible，但只有 72 个 task groups；runner 当时错误地只检查行数并提前停止。这一结果保存为 `results/second_sampling_harness_invalid.json`，属于 Harness 无效，不计方法失败。第三次会沿用同一分层、只修复联合停止条件 `rows>=100 AND groups>=100`。

## 第三次结果的离线审计与 Sol 限定重放

第三次固定页只下载了 `3613` 和 `3813` 两页（200 行、去重后 196 条 eligible、104 个 task groups、1,453,621 bytes），因此资格门本身通过。Gold agent 与事件坐标的精确匹配为 `196/196`，Gold role 映射也为 `196/196`；不是 adapter 把责任方向映反。

但第三次原始运行的 `leakage_and_budget` 门把 `api_calls=0`、`token_calls=0` 当成布尔 False 参与 `all()`，把“零调用”错误判成失败。这是 Harness 审计错误，不是泄漏，也使第三次不能作为干净的方法结论。原始结果保存在 `results/third_result_pre_audit_fix.json`，修正后的门和所有离线证据保存在 `results/third_offline_audit.json`；修正没有下载新页，也没有进行第四次方法运行。

离线逐行检查还解释了为何四个条件的分数完全相同：196 条样本只有 8 种轨迹长度模板，所有 output/tool/phase/input 的匿名结构都是 `string`，1004 个相邻事件的 `state_transition` 全为 0。每行两个匿名角色的结构统计完全相同，所以 AFTraj bridge 对每个角色都给出同一个概率 `0.4017383934`。full 相对 deletion 的 raw score 确实每个事件增加 `+1.2052151803`，但这是同一行所有 step 的同一个常数，故 196/196 行排序不变。

当前数据上的 E1 `argmax` 方向也没有写反：它确实选最高概率角色；只是 196 行全为并列，稳定插入顺序选择 `generic_role_0`，而 Gold 全为 `generic_role_1`，所以命中 `0/196` 不能当作责任桥反向证据。tie key 没有使用坐标、索引、原文或 raw identity，但在完全结构并列时匿名 role token 会决定固定次序；这只影响并列时的绝对排名，不改变 full/deletion 的零差异。

第三次 Luna 原始运行因裁决门布尔实现错误先保留为 `HARNESS_INVALID_THIRD_RUN`，不计方法失败。按“三次执行不行后仅由 Sol 处理不能执行项”的规则，主线 Sol 随后仅使用已冻结的两个本地页面重放同一 runner：没有新下载、没有换数据、没有改模型/特征/权重/指标。修正后所有方法分数和 CI 与原始运行逐项相同，只有两个裁决布尔值被正确重算。验证记录见 `results/sol_replay_verification.json`。

因此当前有效结论是 `STOP_FIXED_EXTERNAL_BRIDGE_IMPLEMENTATION_ONLY`，绝对停止对象仅为“当前 Who&When adapter + 纯匿名结构 state-transition + 固定 AFTraj 责任桥权重”。硬证据是：196/196 行的 full、deletion 和 shuffle 排序完全相同，MRR 均为 `0.5586`；相对最强 fixed-last baseline `0.8689` 低 `0.3103`，任务组 CI 为 `[-0.388362,-0.211806]`；1004 个事件的 state-transition 全为 0，角色概率全部同为 `0.4017383934`。这是该固定实现的一次实质方法失败，不是责任桥方向 NO-GO，也不停止 Who&When Pro 资产用于其他可观测机制。

## 预下载资格审计

| 来源 | 总行数 | 精确多角色 Gold agent+step | 排除的主要行 |
|---|---:|---:|---|
| Exp81 缓存 | 287 | 86 | 154 单 agent flat action；47 round/debate 只有 agents+round |
| Exp83 已打开页面 | 600 | 226 | 374 单 agent flat action；其余无可用单事件 Gold 映射 |
| 合计去重 | 887 | **312（235 个 task groups）** | 达到预注册 100 行/100 group 门槛 |

允许的两种轨迹 schema 是：带 `kind=agent` 的事件，或虽无 `kind` 但显式含 `agent_id/role/round/position/output` 的事件。Gold 必须含单一 `agent`，并通过 `step="round.position"` 或整数 `round+position` 精确匹配；嵌套 round 不猜测性压平，单 agent flat action 不补造 agent。

## 冻结后的新页

固定 revision 为 `0bd196c8a040841c4ae167ab33cc8151de246f1f`。第二次分层 offset 冻结为 `[3613,3813,4613,4813,5613,5813]`：分别围绕已打开且确认有合法多角色 schema 的 `math/mathchat`、`scibench/mathchat`、`tablebench` 区段取相邻不重叠页；它们与 Exp81/Exp83 及第一次 `[100..600]` 区间均不重叠。每页 100 行，累计原始响应不超过 20 MiB；发现去除 Exp81/83 已用 ID 后有 100 条 eligible 且有 100 个 task groups 即停止，不全量下载。新页的原始响应只写入被忽略的 `runtime/`。

## 方法

责任桥模型只在 AFTraj 冻结的 731 条 train 轨迹上拟合，Who&When Pro 不参与调参。每条外部轨迹先把 agent 身份匿名化为按首次出现顺序的 generic role；方法只使用输出/工具调用/phase/input 的存在性和匿名 JSON 结构。唯一新增机制是一个 `state_transition`：相邻事件的匿名结构状态是否变化。禁止词法、错误词、字符串长度、任务、角色名、工具名、ID、Gold、注入字段和绝对位置。

比较 `full_bridge`、`local`、`no_bridge_deletion`、role-probability shuffle，以及 fixed step 1/midpoint/last event 强基线。主指标是 E2 step MRR，另报 R@1、R@3 和 Gold agent 可用时的 E1 top-1。置信区间按 task group paired bootstrap。

## 裁决

- `EXTERNAL_BRIDGE_GO`：至少 100 eligible 行和 100 groups，full 相对最强公平基线绝对提高且相对至少 10%，bootstrap CI 下界大于 0，better>worse，删除/置乱责任桥后增益消失或明显减弱，且审计通过。
- `POSITIVE_NOT_YET_GO`：任何真实同预算正增益但尚未通过全部门槛；保留正向信号，不能写 STOP。
- `ASSET_STOP`：六页后仍不足 100 行或 100 groups。绝对停止对象是“本次外部评价对象资格”，理由是没有足够的可审计 Gold agent+step 行；这不是算法 NO-GO，AFTraj 历史 bridge 正向不受影响。
- 方法停止（若发生）只针对“固定 adapter + 纯结构 state-transition + 固定 AFTraj 权重”，不触发方向 NO-GO。

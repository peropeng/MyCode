# 结论36：方向B分层记忆管理与可靠利用——实时 Gate 记录

> 状态：备选方向资格实验进行中  
> 建立时间：2026-08-21  
> 证据原则：方向 B 与方向 A 独立裁决；论文数量、仓库 star、被动问答检索命中均不能替代 Agent 工具任务中的可靠记忆利用。

## 0. 当前裁决

| 项目 | 状态 | 说明 |
|---|---|---|
| Gate 0：论文/代码/benchmark 可复现 | **CONDITIONAL** | 多个资产可下载并通过最低 smoke，但许可证不完整、G-Memory pinned commit 有语法错误、无完整端到端复现 |
| Gate 1：真实 memory-dependent 任务 | **STOP** | 四个官方资产的自然合格案例为 0；缺少完整 memory→retrieve/use→tool/result→独立错误标签链 |
| RQ1：分层记忆构建与效用估计 | 未开始 | 固定 Token 预算下必须改善未见工具任务成功率 |
| RQ2：记忆更新、冲突与可靠利用 | 未开始 | Oracle utility 无增益则两章桥接 NO-GO |
| 两章总体 | **STOP** | Gate1 自然数据门未过；除非作者提供许可清楚的完整自然轨迹，否则不进入 Gate2/3 |

## 1. Gate 0 冻结判据

- 核验 AWM、HiAgent、G-Memory、AgeMem、How Memory Management Impacts LLM Agents、Mem2ActBench 等正式论文与资源身份；
- 至少 3 个可运行开源实现是文档建议门，少于 2 个可执行环境则 STOP；
- 代码、数据、模型和许可证分别记录；
- 仓库 README 中有命令不等于 smoke 已通过；
- 完整 RL 训练不是首轮 Gate 要求。

## 2. Gate 1 冻结判据

- 至少 100 个独立任务；
- 至少 30 个 stale/conflict/error-memory 案例；
- 代表样本中至少 80% 确实需要跨会话/跨 episode 记忆；
- 必须包含 Agent 决策或工具行为，不以普通问答和静态检索替代；
- 同一 episode 的派生项同组，不能作为独立任务夸大样本量；
- Gold 不得被提示模板、ID 或未来结果直接暴露。

## 3. 两章桥接预注册

固定记忆控制器，只替换效用信息：

1. No Utility；
2. Random Utility；
3. Shuffled Predicted Utility；
4. Predicted RQ1 Utility；
5. Oracle Future Utility。

只有 `Oracle > 最强 recency/vector baseline` 至少 10% 且任务级 CI 下界大于 0，才证明“效用信息有管理价值”；之后 Predicted 必须胜 Shuffled。Oracle 无效时停止该两章结构，不能靠增加上下文长度补救。

## 4. 执行隔离

- 基础分支：`main`
- 基础提交：`4cb7d20ada545f47f20374103bc41e05e084aaa0`
- 执行分支：`exp/0821-direction-b-gate01`
- worktree：`/Users/peroyang/My/MyWork/worktrees/0821-direction-b-gate01`
- 执行线程只拥有：`实验/实验36_方向B分层记忆Gate0Gate1/`
- Docker/Colima 已由主线程验证可用，但容器可用只算环境资格。

## 5. 实验轮次

| 轮次 | 目标 | 当前结果 | 科研进展 | 下一步 |
|---:|---|---|---|---|
| B1 | Gate 0/1 公开资产与任务资格 | Gate0 CONDITIONAL；Gate1 CONDITIONAL | 有科研正信号：任务规模、工具行为和冲突候选足够进入最小 Harness 重组 | 从 discarded lineage 构建 30-task 可重放主动记忆合同 |
| B2 | 30-task 主动记忆合同 | 构造合同子门 GO；方向 Gate1 仍 CONDITIONAL | 有工程与合同进展；无自然标签或方法效果进展 | 寻找完整 session 的自然 stale/conflict/error 轨迹，或转 Gate2 最小真实工具基线 |
| B3 | 四个官方自然错误记忆资产审计 | **Gate1 STOP**；自然合格 0 | 取得决定性负证据：当前公开资产不支持两章所需自然因果链 | 停止 B 的两章投入；仅在作者补齐完整轨迹时重开 |

## 6. 轮次 B1 验收证据

- 执行提交：`01599868092a84a3efc99f4c76674dcb22bc0b7f`，已由主线程审查并 cherry-pick 为 `5624c47`；
- Mem2ActBench：400 QA、2,029 session，按 source episode 去重后 384 组；
- 严格 memory-dependent 候选：373/384；确定性抽样与冲突加采样的 40/40 代表项具有历史依赖和目标工具合同；
- 364/384 episode 所在 session 有 assistant tool call + tool result；但只有 310/384 能从一个 shipped session 完整覆盖全部 source，74/384 不完整；
- 专用 `has_temporal_conflict=true` 为 25 组，discarded lineage 为 30 组，union 为 53；显式 stale label=0，显式 error-memory label=0；
- shipped schema 没有可验证的 `memory_write/retrieve/update/delete`、过时状态或错误记忆后果字段；因此只能支持“历史信息→工具参数”资格，尚不能支持完整记忆治理章节；
- AWM、HiAgent、AgeMem 最低 smoke 通过；G-Memory pinned commit 有 3 个 SyntaxError；只有 AWM 根许可证明确 Apache-2.0，其余多项仍 UNKNOWN 或 README 声称；
- 主线程复验：`python3 tests/test_analyze_mem2actbench.py` 为 3/3 通过，`py_compile` 与 diff check 通过。

当前科研裁决：**方向 B 是三组中当前最值得继续的资产线之一，但仍不是两章 GO。** 下一轮先补最小可执行合同：从 30 个 discarded lineage 重组单一可重放 episode，引入确定性 memory store stub 和 add/retrieve/update/delete trace，冻结至少 10 stale、10 conflict、10 error-memory 任务。该结果只能验证构造合同；只有自然标签、完整 trace 与真实工具结果也成立，才能重判方向 Gate1 GO。

## 7. 轮次 B2 验收证据

- 执行提交：`084bc7b4164814558da93f7511a217abb6f33b5b`；主线程因“真实依赖”口径夸大退回，修正提交为 `7e3c2f2f5979453db1d1a3f9dc22fd0e2ebe9afb`；主线 cherry-pick 为 `f752a19`、`49bd628`。
- 30 个任务均可追溯到 Mem2ActBench pinned commit 的 `conflict_evolutions.csv` 与 `original_records_with_facts.csv` 行；事实文本来自源数据，未另编领域故事。
- 三类 intervention 各 10 项；确定性 store 显式记录 add/retrieve/update/delete；无记忆、correct memory、harmful memory 三条件均执行两次。
- 构造干预依赖为 30/30，clean replay 为 30/30，memory remove/tamper 改变工具调用与结果为 30/30；因此 **constructed/recomposed contract subgate=GO**。
- 该 30/30 由固定策略读取 fact text 后计算指纹、evaluator 比较同源指纹构成，证明的是合同和干预链可工作，不是真实 Agent 学会记忆管理，也不是方法相对基线的增益。
- source trace 有文档化记录 30/30，但 selected retained/discarded source 的完整 shipped session trace 为 **0/30**；缺失被显式记录，不能把“缺口写清楚”称为“自然 trace 完整”。
- stale/conflict/error-memory 只是三种人工 intervention 标签，三类使用同一个 store、policy 和 evaluator；不能分别报告为三类算法效果。
- Gold-only 反事实测试确认：只改 evaluator Gold、保持 online memory/input 不变时 agent policy 输出不变。主线程复跑 4/4 单测、clean result rebuild、`py_compile`、`bash -n` 和 diff check 均通过。

当前科研裁决：**B2 消除了主动 memory lifecycle 和可重放合同的工程疑问，但没有消除自然数据疑问。Gate1 保持 CONDITIONAL，RQ1/RQ2 仍均未开始。**

## 8. 轮次 B3 验收证据

- 执行提交：`e6ac332920e967659f17a194a96111ded6611f15`；主线程因宿主机直接反序列化互联网 pickle 拒绝验收，安全修正提交实际为 `ccc680e0b53bdeaef9413afba77476e38f397335`；主线 cherry-pick 为 `3c77765`、`f99c7df`。
- ACL 2026 *How Memory Management Impacts LLM Agents*：作者 memory database 23,388 条，字段仅为场景、历史/未来轨迹、目标和 objects；无 retrieve/use、目标工具调用、任务结果或 error Gold。`gt_traj.pkl` 6,019 条，与 memory token 交集为 0。
- Fine-Mem：官方仓库只有 README 与 Apache-2.0 LICENSE，没有论文描述的 operation/credit 数据与自然轨迹。
- AgeMem：代码有主动记忆工具，但没有自然 stale/conflict/error 运行轨迹，根许可证仍 UNKNOWN。
- Mem2ActBench：400 QA、2,029 session、384 去重 episode；有 307 组历史 assistant tool call + tool result，但这是 source history，不是 memory manager retrieve/use；目标 task 的实际 tool/result 为 0，显式 memory trace 为 0，显式 stale/error Gold 为 0。
- 四项合计自然合格案例 **0**，未达到至少 30 案例门；不能计算“代表审计至少 80% 真依赖记忆且有工具行为”。
- 安全修正后，不受信任 pickle 只在 Docker `--network none --read-only --cap-drop ALL --security-opt no-new-privileges`、非 root、输入只读的沙箱中反序列化；summary 保存输入 SHA256/大小、image ID 与命令。宿主审计脚本不再 import/call pickle。
- 主线程复验：8/8 单测、`py_compile`、shell syntax、diff check 通过；Docker 沙箱实跑状态 `SANDBOXED_OK`。

当前科研裁决：**方向 B 的公开自然数据 Gate1 STOP。** B1 的历史依赖规模和 B2 的构造生命周期合同均不能补齐自然错误记忆后果。若没有作者提供的、许可明确且含完整运行链与独立标签的轨迹，不再执行 Gate2、Gate3 或付费 API。

## 9. 禁止表述

- 不能把向量检索、摘要或长期对话直接称为 Agent 记忆创新；
- 不能只报告 Token 降低而没有工具任务成功、错误记忆影响或冲突治理；
- 不能用测试任务结果回写同一测试任务的记忆效用；
- 不能把被动问答样本计为 memory-dependent Agent 工具任务；
- 不能把 README 可见、依赖可安装或一次 smoke 成功写成两章 GO。

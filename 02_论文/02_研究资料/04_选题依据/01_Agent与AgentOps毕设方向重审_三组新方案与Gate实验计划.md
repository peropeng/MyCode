# Agent 与 AgentOps 研究生毕设方向重审

## 三组新方案与 Gate 0—5 可行性实验计划

**版本日期：2026-08-21**  
**文档性质：方向重审与开题前可行性计划，不是已取得的论文结果**  
**适用范围：Agent 自身机制、Agent Harness、上下文与记忆、过程验证、AgentOps 与可靠执行**

---

# 1. 审查结论摘要

当前不应继续把“在线故障检测 → 责任动作定位”当作默认主线。既有材料已经说明：过程时点 Gold 难定义、普通在线风险模型未胜公平强基线、风险分数没有稳定改善责任动作定位；目前唯一可靠的方法级正结果，是在 **34 个任务、8 个仓库、受控单调语法故障**上完成同状态二元重放和撤销闭环。它证明了一个窄机制，但不能外推到自然 Agent 故障，也不足以形成两章。

重新检索后，最推荐的新方向是：

> **《面向工具增强智能体的动作效果验证与故障恢复方法研究》**

该方向以“动作执行后是否达到预期效果”为第一章，以“发现效果不一致后如何选择性恢复”为第二章。它有 ACL 2026 Long 的 VeriGUI、ACL 2026 Long 的 Fission-GRPO、ICML 2025 的 SyncMind、ICML 2025 的 GuardAgent 和 OOPSLA 2026 的 Process-Centric Analysis 直接站台；同时能复用现有 checkpoint、重放、动作撤销、状态哈希和 API 结构化输出资产。最低成本的先证伪实验不是再训练模型，而是先审计 30 个独立任务是否拥有稳定的“动作前状态—动作—动作后状态—预期效果”合同，并验证理想效果证据是否真的改善恢复成功率。

备选方向是“长程 Agent 的分层记忆管理与可靠利用”；第三方向是“过程评价与选择性反馈优化”。二者文献基础充足，但前者需要新建记忆实验 Harness，后者与已有 verifier 工作重叠更密集。原“故障传播”“责任主体预测”“普通在线失败预测”不再推荐为主线。

## 1.1 本地 Gate 执行后的最新状态（2026-08-21）

> 本节是文档初稿形成后实际执行的更新。外部 GPT 看不到本地文件时，应以本节和第 2 节的历史证据为当前事实，不要把第 5—11 节的方案描述误当成已取得结果。

| 方向 | 已执行实验 | 当前严格裁决 | 已证明 | 尚未证明/硬缺口 |
|---|---|---|---|---|
| A：动作效果验证→恢复 | 实验35 Gate0/1；实验38 SyncBench bounded replay；实验42 AppWorld 最终资格门 | Gate0 `STOP`；Gate1 `STOP`；RQ1/RQ2 与两章均 `STOP` | 30 个构造 task、3 个本地环境抽象、13 类效果的合同可执行；AppWorld 引擎、147 个 train/dev task、checkpoint 与 evaluator 入口可运行 | 冻结的公开 train/dev GPT-4o 动作轨迹目录不存在；替代 test 输出无 `environment_io.md`；不能从 Gold/validation solution 逆造动作，因此未进入自然 30-task Gate1 |
| B：分层记忆→可靠治理 | 实验36 Gate0/1；实验39 30-task 主动记忆合同；实验40 四项官方自然资产审计 | Gate0 `CONDITIONAL`；Gate1 `STOP`；两章 `STOP` | Mem2ActBench 有 384 个去重 episode、373 个历史依赖候选；30 个重组任务的 add/retrieve/update/delete 合同可执行 | 四项官方资产的自然合格案例为 0；没有完整 memory→retrieve/use→tool/result→独立错误标签链，停止 Gate2/3 |
| C：过程评价→反馈优化 | 实验37 Gate0/1 | Gate0 `CONDITIONAL`；Gate1 `STOP` | DevAI/Plan-RewardBench 等资产 schema 与规模已核验 | DevAI requirement→evidence 映射为 0/365；标签/证据不能独立重建，同 Judge 风险未消除；不应继续 Gate2/3 |
| D：BFCL 接口契约鲁棒性→失败修复 | 实验43 Gate0/1；实验44 契约 patch；实验45 调用级裁剪；实验46 schema/literal 替换 | Gate0 `GO`；Gate1 `GO`；实验44‑46科学分数降级为 `INVALID_HARNESS_STATE_LEAK`；两章未 `GO` | 四家族各 30，全局 120 个任务与 120 个结构签名唯一；三设计分别冻结3264/9418/26503个 Gold-blind 候选，冻结/support 证据仍有效 | 三个 runner 对同task的所有candidate复用 evaluator namespace，使有状态实例跨候选串扰；旧75/120、0救回、CI[0,0]与120/120一致均不能支持STOP，正在隔离重评 |

当前没有任何一组达到“两章 GO”。A、B、C 均已在冻结的数据资格门停止；D 的数据与 evaluator 资格门已 GO，但修复信息价值尚未成立。此前的 Sol Max 复审是一次历史方向处置，不得解读为“累计任意三次失败就切 Sol”。今后的唯一计数规则是：针对**同一个明确目标预期**，必须先由执行线程换三种实质不同的模块/设计且全部无进展，才可委派 Sol Max 独立调研。安装、下载、修 bug、重跑、小幅调参和不同方向各失败一次，都不计入这三次。

首轮本地代码审查还暴露了两类必须保留的可信性问题：

1. 实验35初版 filesystem probe 读取 `expected_effect` 来选择观察路径，属于 Oracle 定向观察。修正后 filesystem 统一采集完整临时目录，JSON/CLI 只使用 public action；Gold 只在 observation 冻结后进入 evaluator。
2. 实验39初版把固定“读取 fact text→计算同源指纹”的 30/30 称为真实 memory dependency。主线程退回并改为“构造干预依赖”；它只证明合同和生命周期可执行，不证明真实 Agent 会管理记忆。
3. 实验38初版把 pytest 输出中的 0.15s/0.14s wall-clock 差异误判为 replay mismatch，并把 fixture setup error 写成目标测试失败。修正后 clean replay 为 2/2，但稳定效果 Oracle 仍为 0/2。
4. 实验40初版在宿主机直接反序列化互联网 pickle。修正后只在无网络、只读、降权、非 root Docker 沙箱中执行，并记录文件 SHA256、镜像 ID 与命令；安全修正不改变自然合格案例 0 的科研 STOP。

截至本次更新，Docker/Colima 已自行安装并验证：Docker client 29.7.2、server 29.5.2、arm64，`hello-world` 返回 0。Docker 可用只算基础设施资格，不算方向或章节 GO。

---

# 2. 对现有实验的独立复核

## 2.1 同意保留的证据

| 现有证据 | 当前可支持的结论 | 在新方向中的位置 |
|---|---|---|
| 10 个任务、20 个编辑动作的检查点恢复与精确重放 | Agent 动作状态可以在受控软件环境中保存、恢复和复现 | Harness 基础设施与 Gate 1 数据合同 |
| 34 个任务、8 个仓库的同检查点二元重放 | 在已知 8 动作区间和单调语法 Oracle 下，二分重放能以 3 次检查定位首个状态转坏动作 | 候选方向 A 的受控基线、回归测试和机制种子 |
| 目标动作撤销 34/34 恢复，后续同文件动作撤销 0/34 | 在这批受控样本上，已定位动作具有比文件相关性更强的干预证据 | 恢复验收协议和阴性对照 |
| trace 解析、任务级切分、OOF、bootstrap、API 预算记录 | 可以降低新实验实现与可信性成本 | 实验协议，不是创新 |

## 2.2 必须降级或保留为负结果的内容

1. **普通在线故障检测不成立。**无成功参照的动作状态在线检测未胜 Fail-Fast 风格基线，且终局成败无法给出“故障在第几步形成”的可靠 Gold。
2. **风险分数到责任动作的桥接不成立。**风险峰值、传播分数和错误生命周期权重多次未稳定改善责任动作排序。
3. **受控语法故障不能外推到自然失败。**当前二分定位依赖单调的“可编译 → 不可编译”状态；自然轨迹可能自我恢复、出现多故障、延迟后果或非单调测试变化。
4. **checkpoint 是资产，不是一章。**保存 JSON、状态哈希、重放脚本和 Docker 环境不能单独构成研究贡献。
5. **责任主体与传播主线不再复活。**旧数字来自特定构造标签和同源数据，且传播增量已在公平 Gate 下 NO-GO。

## 2.3 当前最稀缺的研究资产

当前最稀缺的并不是更强模型，而是：

> **可在同一执行状态下复现、具有明确预期效果、能以工具返回或环境状态自动判定的 Agent 动作样本。**

它决定了能否区分：

- 动作调用成功但语义效果错误；
- 日志看起来异常但实际状态正确；
- 瞬时失败但后续已恢复；
- 真正需要恢复的持续效果不一致；
- 恢复动作是否改善最终任务，而不是只改变一段文字解释。

---

# 3. 当前方向的处置

## 3.1 原主线

> 在线故障检测 → 责任动作定位

**处置：放弃作为默认开题题目。**

原因不是“在线检测没有研究价值”，而是当前本地资产无法稳定定义过程 Gold，且既有方法与桥接均未通过冻结比较。它可以作为候选方向 A 中的一个辅助指标，例如“动作效果不一致被发现的延迟”，但不再单独承担一章。

## 3.2 实验 02 的受控责任动作定位

**处置：降为候选方向 A 的方法模块、强基线和评测协议。**

它尚不足以单独承担一章，因为：

- 故障类型单一；
- 区间由构造过程给定；
- Oracle 单调；
- 二分搜索的准确性在这种设定下接近算法性质；
- 没有面对自然工具错误、延迟效果、错误参数、状态冲突和自我恢复。

它的价值在于已经证明“同状态重放 + 目标撤销 + 阴性动作对照”的执行链可运行。

---

# 4. 三组候选方向总览与排序

| 排名 | 候选方向 | 推荐题目 | 两章关系 | 当前资产复用 | 最大风险 | 当前判定 |
|---:|---|---|---|---|---|---|
| 1 | 动作效果验证与选择性恢复 | **面向工具增强智能体的动作效果验证与故障恢复方法研究** | RQ1 的效果判定、证据和不确定性直接进入 RQ2 恢复决策 | checkpoint、重放、撤销、状态哈希、API schema 高度复用 | 语义和延迟效果 Gold 是否可稳定构造 | **首选，Conditional-Go** |
| 2 | 分层记忆管理与可靠利用 | **面向长程智能体的分层记忆管理与可靠利用方法研究** | RQ1 产生带来源和效用的记忆；RQ2 用真实预测决定检索、更新和删除 | trace、任务级切分、OOF、API 框架可复用 | 领域拥挤、在线运行成本高、需新建 memory harness | **备选，Conditional-Go** |
| 3 | 过程评价与选择性反馈优化 | **面向软件工程智能体的过程评价与反馈优化方法研究** | RQ1 输出要求级评价和证据；RQ2 用样本外反馈选择或修正轨迹 | SWE-Gym、测试环境、API 调用记录较易复用 | 与 Agent-as-a-Judge、SWE-Gym verifier、Agentic Rubrics 重叠强 | **可研究，但不建议当前主选** |

明确排除为主线：

- 普通前缀成败预测；
- 责任 Agent → 责任步骤；
- 故障传播链必须改善定位；
- 把 checkpoint、二分和编译检查包装成独立理论；
- 继续调旧 Flash 提示词、阈值或错误词特征。

---

# 5. 候选方向 A：动作效果验证与故障恢复

## 5.1 建议题目

> **《面向工具增强智能体的动作效果验证与故障恢复方法研究》**

题目处于稳妥层级：

- 对象是工具增强智能体；
- 第一项问题是动作效果验证；
- 第二项问题是故障恢复；
- 不写具体模型、数据集、二分、检查点、阈值或“自愈”等过强词。

“动作效果验证”有正式论文直接使用的 Action-Effect Verification 概念，不是本课题自造术语。

## 5.2 一句白话问题

> Agent 调完工具以后，不能只相信“调用成功”；先检查想要的变化是否真的发生，发现不一致后，再选择最合适的重试、替代、回滚或重规划方式。

## 5.3 统一学术主线

```text
Agent 形成当前子目标
        ↓
产生工具调用或状态修改动作
        ↓
动作带有可描述的预期效果
        ↓
观察工具返回、环境状态差异和可执行检查
        ↓
RQ1：判断效果已实现 / 效果不一致 / 证据不足
        ↓
RQ2：依据不一致类型和证据选择恢复策略
        ↓
在同一检查点验证恢复是否真正改善任务且不引入回归
```

该主线避免了旧方向的核心问题：不再用终局失败反推中间故障时点，而是直接评价动作声明与可观察后果之间的关系。

---

## 5.4 RQ1：动作效果验证

### 白话定义

> Agent 做完一步后，预期的文件、页面、数据库或工具状态到底有没有发生；证据不够时能不能明确说“不确定”，而不是强行判断成功或失败？

### 学术定义

> 给定工具增强智能体在时刻 \(t\) 的子目标、动作调用、动作前状态和动作后可观察反馈，研究如何形成动作预期效果表示，融合工具返回、状态差异和可执行探针，输出“效果已实现、效果不一致、证据不足”的判定、效果类型及支持证据。

### 输入

- 当前任务与子目标；
- 工具名、参数和动作声明；
- 动作前可观察状态；
- 工具返回、动作后状态和可执行检查结果；
- 不读取未来轨迹和最终任务标签。

### 输出

- 三值效果判定；
- 不一致类型；
- 证据对象与证据位置；
- 置信度或拒识结果；
- 可交给 RQ2 的候选恢复上下文。

### 方法模块

#### M1：动作预期效果表示

**来源：**

- VeriGUI 的 Thinking–Verification–Action–Expectation；
- GuardAgent / ShieldAgent 的可执行规则与动作约束；
- 工具 schema、任务子目标和显式操作语义。

**Agent 特有瓶颈：**  
工具返回 0、HTTP 200 或函数调用成功，只说明调用协议完成，不说明 Agent 想要的语义目标已实现。

**实现边界：**

- 从工具 schema、动作参数和当前子目标中抽取“预期改变什么”；
- 对可程序化动作优先生成路径、字段、实体、页面元素或测试条件；
- LLM 只能补充难以结构化的语义预期，不得单独产生 Gold。

#### M2：多源效果证据验证

**来源：**

- 软件测试、状态差异、不变量检查；
- Agentic Rubrics 的上下文取证；
- Process-Centric Analysis 的动作—阶段—验证过程表示。

**Agent 特有瓶颈：**  
一个动作可能在多个通道留下证据；只看工具文本容易误判异步完成、缓存状态或间接副作用。

**证据优先级：**

1. 可执行测试或确定性状态差异；
2. 工具返回与环境查询；
3. 后续独立观察；
4. LLM 语义判断。

#### M3：证据不足时的选择性判定

**来源：**选择性预测和 VeriGUI 对失败识别的处理。

**作用：**  
延迟效果、不可观测状态和多步事务中，错误的强制失败判断会引发不必要恢复。模型允许输出“证据不足”，将该类样本交给低频复查，而不是立即中断。

### RQ1 核心贡献的合格表述

不能写：

> 提出检查点、状态 diff 和 LLM 判断三个模块。

可以写：

> 研究工具增强智能体中“协议成功不等于目标效果实现”的动作级验证问题，并构造一条由预期效果、可观察状态证据和拒识条件组成的可审计判定机制，系统分析不同效果类型、延迟和可观测性对验证可靠性的影响。

### RQ1 强基线

1. **Return-Code / Tool-Status**：只依据工具退出码或返回状态；
2. **Periodic / Every-Step Probe**：固定周期或每步运行通用检查；
3. **GuardAgent-style Executable Checker**：把动作约束转成代码检查；
4. **Direct LLM Verifier**：同预算 API 直接读动作和返回作判断；
5. **Oracle State Checker**：人工正确效果字段或全量执行测试，仅作上界。

### RQ1 主指标

**三类效果判定 macro-F1**：`achieved / mismatch / insufficient`。

必要辅助指标：

- 判定与证据联合正确率；
- clean false alarm；
- mismatch Recall；
- 首次可判定延迟；
- 每个动作平均探针/API/Token 成本；
- 分工具类型、效果类型、延迟和自然/构造错误结果。

### 什么结果会否定 RQ1

- Return-Code 或固定探针已达到近乎饱和，方法增益不足 10%；
- 预期效果只能靠人工逐条写，无法规模化；
- 语义效果的标注一致性长期低于 0.60；
- 模型主要读取显式错误词、注入字段或工具异常码；
- 跨任务或跨工具后性能接近随机。

---

## 5.5 RQ2：检测证据驱动的选择性恢复

### 白话定义

> 发现动作没有达到预期以后，不是统一“再试一次”，而是根据失败类型决定重试、换工具、修正参数、回滚还是重新规划，并验证恢复是否真的有效。

### 学术定义

> 将 RQ1 对未见任务产生的效果判定、不一致类型、证据与不确定性作为恢复上下文，在固定工具/API/探针预算下，对重试、参数修正、替代工具、状态回滚和重规划候选进行选择，并以任务结果恢复和非回归检查评价恢复有效性。

### 输入

- RQ1 的任务级样本外效果判定；
- 当前检查点和动作前后状态；
- 候选恢复操作；
- 剩余交互、Token 或时间预算。

### 输出

- 是否值得恢复；
- 恢复类型与具体动作；
- 恢复后验收证据；
- 继续、回退或交给人工的决策。

### 方法模块

#### M1：不一致类型条件化的恢复候选

**来源：**

- Fission-GRPO 的执行错误诊断与恢复训练；
- SyncMind 的 out-of-sync recovery；
- VeriGUI 的失败识别与纠正。

**候选示例：**

- 参数格式错误 → 修正参数后重试；
- 环境状态已变化 → 重新读取状态并重规划；
- 工具暂时不可用 → 替代工具或延迟重试；
- 文件状态被破坏 → 回滚到动作前检查点；
- 效果证据不足 → 只追加确认探针，不立即修改状态。

#### M2：选择性恢复决策

**研究问题：**  
何时恢复、采取何种恢复，才能提高任务成功率而不干扰本来正常的执行？

**机制：**

- 根据 RQ1 置信度、不一致类型和恢复成本排序；
- 低置信时继续观察或请求人工；
- 高置信且可回滚时执行最小恢复；
- 固定总预算，防止“多调用自然更强”。

#### M3：同状态恢复与非回归验收

**来源：**

- 现有 checkpoint / replay / 撤销资产；
- SyncBench 与 SWE-Gym 的可执行测试；
- 软件回归测试和事务恢复思想。

**验收：**

- 目标效果恢复；
- 非目标状态未回退；
- 从相同起点对比恢复策略；
- 失败环境、无法重放和不确定样本单独报告。

### RQ2 核心贡献的合格表述

> 分析不同动作效果不一致对恢复策略选择的影响，研究样本外效果证据是否能在同等预算下改善恢复成功率，并以同状态重放和非回归检查区分“语言上看似合理的建议”与实际恢复。

### RQ2 强基线

1. **Retry Same Action**：原动作直接重试；
2. **Reflection + Retry**：让模型反思后再次调用；
3. **Rollback Last Action**：统一撤销最近动作；
4. **Fixed Recovery Policy**：按工具错误码使用固定映射；
5. **Fission-GRPO / SyncMind Protocol**：能运行时采用论文协议；代码未开放时做受控协议复现并注明。

### RQ2 主指标

**Recovery Success Rate**：检测到不一致后，在固定预算内恢复目标效果或最终任务成功的任务比例。

辅助指标：

- 最终任务成功率；
- harmful recovery rate；
- 平均恢复调用数、Token、时间和测试次数；
- 恢复后非目标测试回退率；
- 不同故障类型的恢复率；
- abstention 后人工/追加验证覆盖率。

### 两章关系专门证伪实验

保持恢复候选、模型、调用次数和预算完全相同，只替换 RQ1 信息：

1. No Evidence；
2. Random Evidence；
3. Shuffled Predicted Evidence；
4. Predicted RQ1 Evidence；
5. Oracle Effect Evidence。

完整论文只有在：

```text
Predicted > No / Random / Shuffled
Oracle > Predicted
```

且 Predicted 相对最强公平对照主指标提升至少 10%、任务级配对 bootstrap 的 95% CI 下界大于 0 时，才能主张 RQ1 对 RQ2 有真实价值。

---

## 5.6 核心论文组 A

| 论文 | 正式身份 | CCF | 全文主要任务 | 代码、数据与风险 |
|---|---|---|---|---|
| [Don’t Act Blindly: Robust GUI Automation via Action-Effect Verification and Self-Correction](https://aclanthology.org/2026.acl-long.1335/) | ACL 2026 Volume 1 Long | A | 动作效果验证与自我纠正 | 正式页已核；本轮未找到公开代码，Gate 0 需继续核验 |
| [SyncMind: Measuring Agent Out-of-Sync Recovery in Collaborative Software Engineering](https://proceedings.mlr.press/v267/guo25l.html) | ICML 2025 | A | 软件 Agent 状态不同步与恢复 | [代码](https://github.com/xhguo7/SyncMind)和 SyncBench 公开；根仓库未声明许可证，需确认再发布派生物 |
| [Robust Tool Use via Fission-GRPO: Learning to Recover from Execution Errors](https://aclanthology.org/2026.acl-long.1880/) | ACL 2026 Volume 1 Long | A | 多轮工具执行错误恢复 | [仓库](https://github.com/zxzadm/Fission-GRPO)目前仅占位，训练代码和数据尚未发布 |
| [GuardAgent: Safeguard LLM Agents via Knowledge-Enabled Reasoning](https://proceedings.mlr.press/v267/xiang25a.html) | ICML 2025 | A | 对目标 Agent 动作执行可验证约束检查 | [代码](https://github.com/guardagent/code)和数据入口公开；根许可证需 Gate 0 核验 |
| [Process-Centric Analysis of Agentic Software Systems](https://doi.org/10.1145/3798271) | OOPSLA 2026 正式论文 | A | 软件 Agent 执行过程表示、问题模式与运行干预 | [Graphectory](https://github.com/Intelligent-CAT-Lab/Graphectory)公开，仓库 NCSA；论文页面为 CC BY 4.0 |

前沿或补充压力：

- ShieldAgent，ICML 2025：可验证安全规则，不作为效果验证同义替代；
- Agentic Rubrics，ACL 2026 Long：上下文取证与可扩展 verifier；
- BFCL v4、TAU-Bench、TAU2-Bench：工具调用和恢复外测；
- 当前 34 个受控语法故障：仅作 Gate 1/2 smoke test。

---

## 5.7 数据与环境方案

### 主实验候选

1. **SyncBench**：优先审计 300 条官方评测子集，再决定是否使用 24,332 条全量实例；
2. **BFCL v4 Multi-Turn**：用于工具执行错误与恢复；
3. **TAU-Bench / TAU2-Bench**：跨工具交互外测；
4. **SWE-Gym / OpenHands**：软件仓库状态、测试与 checkpoint；
5. **当前 34 个受控案例**：检查重放、撤销和阴性对照是否回归。

### 最小统计单位

- 独立 task / instance；
- 同一任务的不同错误、重复 rollout 和恢复尝试必须同组；
- 不以动作行数或单次 API 调用作为独立样本。

### 自然与构造比例

- Gate 1 可先使用构造效果不一致验证接口；
- Gate 4 主结果至少一半来自 benchmark 原生错误、状态漂移或真实工具失败；
- 构造故障必须分类型，并在自然失败上单独外测。

### 计算资源

- Gate 0—2：CPU / Mac + API 即可；
- SyncBench、SWE-Gym 正式重放：Linux + Docker；
- 训练小型分类器或冻结 embedding：12GB GPU 足够，非必需；
- 不建议开题前复现 Fission-GRPO 的完整 8B RL 训练。

---

# 6. 候选方向 B：分层记忆管理与可靠利用

## 6.1 建议题目

> **《面向长程智能体的分层记忆管理与可靠利用方法研究》**

## 6.2 一句白话问题

> Agent 不应把所有历史都塞回上下文；它需要知道什么值得记、如何压缩，以及什么时候一条旧经验已经过时、冲突或会误导当前任务。

## 6.3 统一学术主线

```text
长期交互和多次任务产生大量轨迹
        ↓
RQ1：按子目标/工作流组织经验，保留来源并估计未来效用
        ↓
形成受预算约束的结构化记忆
        ↓
RQ2：根据任务、冲突、时效和效用决定检索、更新或删除
        ↓
评价记忆是否真正帮助工具选择、参数落地和任务成功
```

---

## 6.4 RQ1：分层记忆构建与效用估计

### 白话定义

> 一条很长的轨迹里，哪些是以后还能复用的步骤、规则和坑点，应该以什么粒度存下来？

### 学术定义

> 给定长程 Agent 的历史动作—观察轨迹和任务结果，研究如何按子目标与工作流进行分层切分，保留记忆来源和证据，并估计各记忆单元对未来未见任务的效用，在固定记忆与上下文预算下构建可复用记忆库。

### 方法模块

1. **子目标/工作流分层切分**  
   来源：HiAgent、Agent Workflow Memory。
2. **带来源的记忆压缩与合并**  
   来源：G-Memory、GAM 等分层图记忆；每条摘要可追溯到原始事件。
3. **未来任务效用估计**  
   来源：How Memory Management Impacts LLM Agents、Fine-Mem；用后续任务评价产生效用标签，而不是 LLM 自评。

### 输入/输出

- 输入：历史轨迹、任务、结果、工具与状态；
- 输出：分层记忆单元、来源事件、适用条件、效用分数和冲突标记。

### RQ1 独立价值与主指标

RQ1 不是为 RQ2 做数据清洗，而是单独回答“怎样构造在固定预算下更有用的 Agent 记忆”。

**主指标：固定记忆 Token 预算下的未见任务成功率。**

辅助指标：

- 相关证据召回；
- 记忆压缩率；
- 来源可追溯率；
- 有害记忆率；
- 工具与参数 grounding 正确率。

### 强基线

1. Full History；
2. Recency / Running Summary；
3. Vector Retrieval；
4. HiAgent；
5. Agent Workflow Memory。

---

## 6.5 RQ2：记忆更新、冲突与可靠利用

### 白话定义

> Agent 面对新任务时，应该用哪条记忆；发现记忆冲突、过时或曾导致失败时，能不能更新、降权或删除？

### 学术定义

> 将 RQ1 对未见任务生成的记忆效用、来源和适用条件作为样本外证据，研究 Agent 对记忆进行检索、应用、更新、合并、降权或删除的策略，并在分布变化和错误经验条件下评价长期任务性能与有害经验传播。

### 方法模块

1. **效用感知检索与应用**；
2. **冲突、时效和错误经验治理**；
3. **工具调用中的证据化参数落地**。

### 主指标

**长期任务成功率或平均累计成功率。**

辅助指标：

- harmful-memory induced failure rate；
- 冲突解析准确率；
- memory operation precision；
- Token / 延迟 / 存储成本；
- 新旧任务与跨域表现。

### 两章关系证伪

固定 RQ2 控制器，仅替换记忆质量信号：

- No Utility；
- Random Utility；
- Shuffled Predicted Utility；
- Predicted RQ1 Utility；
- Oracle Future Utility。

Predicted 必须相对最强公平基线提升至少 10%，且任务级 CI 下界大于 0；若 Oracle 效用都不能改善长期表现，则“先预测记忆效用再治理”没有必要。

---

## 6.6 核心论文组 B

| 论文 | 正式身份 | CCF | 全文主要任务 | 代码、数据与风险 |
|---|---|---|---|---|
| [Agent Workflow Memory](https://proceedings.mlr.press/v267/wang25bx.html) | ICML 2025 | A | 从经验归纳可复用工作流并选择性提供 | [代码](https://github.com/zorazrw/agent-workflow-memory)，Apache-2.0 |
| [HiAgent: Hierarchical Working Memory Management](https://aclanthology.org/2025.acl-long.1575/) | ACL 2025 Long | A | 基于子目标的分层工作记忆 | [代码](https://github.com/HiAgent2024/HiAgent)公开；许可证需 Gate 0 锁定 |
| [G-Memory: Tracing Hierarchical Memory for Multi-Agent Systems](https://proceedings.neurips.cc/paper_files/paper/2025/hash/136a45cd9b841bf785625709a19c6508-Abstract-Conference.html) | NeurIPS 2025 Main | A | 多智能体跨试次分层记忆 | [代码](https://github.com/bingreeky/GMemory)公开；许可证需核验 |
| [Agentic Memory: Learning Unified Long-Term and Short-Term Memory Management](https://aclanthology.org/2026.acl-long.981/) | ACL 2026 Long | A | 把存、取、更新、摘要、丢弃建成 Agent 动作 | [代码](https://github.com/y1y5/AgeMem)公开；完整 RL 训练资源较高 |
| [How Memory Management Impacts LLM Agents](https://aclanthology.org/2026.acl-long.27/) | ACL 2026 Long | A | 研究记忆增加/删除、错误传播和错误经验回放 | 论文正式；代码与数据入口需 Gate 0 继续核验 |

直接 benchmark：

- [Mem2ActBench](https://aclanthology.org/2026.acl-long.370/)：400 个工具任务、2,029 个持久会话，代码数据公开；
- [Fine-Mem](https://aclanthology.org/2026.acl-long.900/)：记忆操作的细粒度信用分配；
- [GAM](https://aclanthology.org/2026.acl-long.1600/)：编码与巩固分离；
- [Controllable Memory Usage](https://aclanthology.org/2026.acl-long.670/)：可控记忆依赖。

---

## 6.7 主要风险

1. **领域拥挤。**若只做“分层 + 向量检索 + 摘要”，会被判为拼装。
2. **数据和运行成本。**WebArena 等长程任务 API 成本明显高于离线轨迹分类。
3. **效用标签泄漏。**不能用测试任务结果回写同一测试任务的记忆分数。
4. **实验结论容易依赖模型。**必须至少跨两个 backbone 或报告模型依赖。
5. **当前资产复用较少。**现有 checkpoint 可用于软件记忆外测，但主 Harness 需要新建。

---

# 7. 候选方向 C：过程评价与选择性反馈优化

## 7.1 建议题目

> **《面向软件工程智能体的过程评价与反馈优化方法研究》**

## 7.2 一句白话问题

> 最终测试只告诉我们“做成没有”；过程评价要指出哪项要求还没满足、证据是什么，再检验这条反馈是否真能让 Agent 改好，而不是把正确运行带坏。

## 7.3 统一学术主线

```text
任务要求与 Agent 执行轨迹
        ↓
RQ1：要求级过程评价、主动取证与证据充分度
        ↓
产生样本外评价和可操作反馈
        ↓
RQ2：选择最值得使用的反馈进行候选选择或一次修正
        ↓
以程序测试和任务结果评价净收益与有害反馈
```

---

## 7.4 RQ1：证据约束的过程评价

### 白话定义

> 评价器能不能指出“具体哪条要求没做到”，并拿出仓库、工具、测试或轨迹证据，而不是只给一个总分和一段理由？

### 学术定义

> 给定软件工程任务的层级要求、Agent 轨迹及其产物，研究如何进行要求级分解、主动获取上下文证据，并输出要求判定、证据和置信度，在不读取隐藏测试结论的条件下提高过程评价可靠性。

### 方法模块

1. **任务特定要求或 rubric 构建**；
2. **主动证据获取与要求—证据对齐**；
3. **证据不足时拒识和可靠性估计**。

### 主指标

**要求判定与证据联合正确率。**

辅助指标：

- pairwise trajectory preference accuracy；
- requirement macro-F1；
- evidence precision/recall；
- ECE / risk–coverage；
- API/工具调用成本；
- 长轨迹退化。

### 强基线

1. outcome-only / test-only；
2. direct LLM-as-a-Judge；
3. Agent-as-a-Judge；
4. Agentic Rubrics；
5. Plan-RewardBench 中的代表 reward model。

---

## 7.5 RQ2：选择性反馈驱动的测试时优化

### 白话定义

> 评价器提出问题以后，哪些反馈值得交给 Agent；它能不能提高最终成功率，同时避免对本来正确的方案乱改？

### 学术定义

> 将 RQ1 对未见任务产生的要求级判定、证据和置信度作为反馈，在固定测试时预算下进行候选选择、局部修正或一次迭代优化，并用可执行测试评价任务成功增益、有害反馈率和成本。

### 方法模块

1. **反馈优先级与压缩**；
2. **选择性修正或 best-of-N 选择**；
3. **非退化验收与回退**。

### 主指标

**最终 resolve / task success rate。**

辅助指标：

- harmful feedback rate；
- 反馈接受后测试改善；
- 调用次数、Token、时间；
- 无反馈、随机反馈和完整反馈的差异；
- 证据正确但修正无效的比例。

### 两章关系证伪

在相同 Agent、候选数和总调用预算下比较：

- No Feedback；
- Random Feedback；
- Shuffled Predicted Feedback；
- Predicted RQ1 Feedback；
- Oracle Requirement Feedback。

若 Predicted 不优于 No / Random / Shuffled，说明评价正确性没有转化为 Agent 改进，整套“两章递进”不成立。

---

## 7.6 核心论文组 C

| 论文 | 正式身份 | CCF | 全文主要任务 | 代码、数据与风险 |
|---|---|---|---|---|
| [Agent-as-a-Judge: Evaluate Agents with Agents](https://proceedings.mlr.press/v267/zhuge25a.html) | ICML 2025 | A | 对完整 Agent 过程进行中间反馈和要求级评价 | [代码](https://github.com/metauto-ai/agent-as-a-judge)与 DevAI 公开 |
| [Training Software Engineering Agents and Verifiers with SWE-Gym](https://proceedings.mlr.press/v267/pan25g.html) | ICML 2025 | A | 训练 SWE Agent 和 verifier，并做推理时扩展 | [代码](https://github.com/SWE-Gym/SWE-Gym)、任务和轨迹公开 |
| [Aligning Agents via Planning: Plan-RewardBench](https://aclanthology.org/2026.acl-long.1062/) | ACL 2026 Long | A | 轨迹级 reward model 与困难恢复负例 | 1,171 对数据与评价代码公开；许可证需再次按仓库和数据卡分别锁定 |
| [Agentic Rubrics as Contextual Verifiers for SWE Agents](https://aclanthology.org/2026.acl-long.697/) | ACL 2026 Long | A | 通过仓库交互生成上下文相关 rubric 并评价 patch | 正式论文已核；代码状态需 Gate 0 核验 |
| [Proposer-Agent-Evaluator: Autonomous Skill Discovery](https://proceedings.mlr.press/v267/zhou25ah.html) | ICML 2025 | A | evaluator 作为奖励信号驱动 Agent 改进 | PMLR 提供 Software 入口；运行 WebArena 成本较高 |

补充：

- Self-Challenging Language Model Agents，NeurIPS 2025 Main；
- DeepVerifier 为 ACL 2026 Findings，只作前沿补充，不计 CCF A 正式核心；
- PaperBench，ICML 2025，可提供分层 rubric 与 judge 检验思路。

---

## 7.7 为什么不作为首选

1. Agent-as-a-Judge、SWE-Gym verifier 和 Agentic Rubrics 已直接覆盖大量方法空间；
2. 若只增加“要求分解 + 证据检索 + 反馈”，容易被认定为复现与组合；
3. RQ1 评价器与 RQ2 修正器可能共享同一个 LLM，产生循环偏差；
4. 闭源 API 成本较高；
5. 只有“证据正确性能预测修正效用、选择性反馈降低有害修改”这一更进一步结论有较强辩护力，必须尽早通过 Gate 3。

---

# 8. 文献身份与 CCF 核验规则

第七版 CCF 目录于 2026 年 3 月正式发布。开题材料应按以下口径：

1. 只有 Full / Regular / 正式 Long Paper 按会议等级计入；
2. Findings、Short、Demo、Workshop、Datasets & Benchmarks 特殊 Track 不自动计入；
3. ICML、ACL、NeurIPS 按人工智能类 A 处理；
4. OOPSLA 按软件工程/系统软件/程序设计语言类 A 处理；
5. CCF 等级属于 venue，不代表单篇论文天然高质量；
6. 代码、数据、模型和环境许可证必须分开核验。

CCF 官方入口：

- https://www.ccf.org.cn/Academic_Evaluation/By_category/2026-03-31/870181.shtml

每篇核心论文在 Gate 0 建立如下 manifest：

```text
paper_title
authors
year
venue
paper_type
ccf_category
official_paper_url
official_code_url
code_commit
code_license
dataset_url
dataset_version
dataset_license
model_or_image
minimum_hardware
smoke_test_command
reproduction_status
```

---

# 9. 三组方向的 Gate 0—5 计划

## 9.1 方向 A Gate 表

| Gate | 唯一问题 | 最小数据/环境 | 方法与基线 | 主指标和门槛 | 资源/时间 | GO / STOP |
|---|---|---|---|---|---|---|
| Gate 0 | 是否有正式方向站台和可运行资产？ | 5 篇论文身份；SyncMind、GuardAgent、Graphectory、SWE-Gym/BFCL 入口 | 零代码文献/仓库审计 | 至少 3 篇正式 CCF A 直接覆盖验证或恢复；至少 1 个可执行 benchmark | 0 GPU，0 API，1 天 | 资产可下载、许可可用于研究、至少一条 smoke command 存在则 GO；否则 STOP |
| Gate 1 | 动作效果能否被稳定定义和自动判定？ | 30 独立任务，≥3 仓库/环境，≥3 效果类型，每类约 10 | return code、状态 diff、确定性 probe；人工只做审计 | ≥70% 样本拥有稳定 pre/action/post/effect Oracle；clean 重放一致率 ≥90% | CPU/Docker，1—2 天 | 不足 30 个独立合格任务或 Oracle 主要靠 LLM 自评则 STOP |
| Gate 2 | 问题是否过于简单或存在捷径？ | Gate 1 样本，另留 10 任务确认 | Return-Code、Periodic、Every-Step、Direct LLM、Oracle | macro-F1；若最强简单基线已 >95% 且无困难子集，方向过小 | 300—800 API 调用，2—3 天 | 存在语义/延迟/状态冲突困难子集且模板审计通过则 GO |
| Gate 3 | RQ1 信息是否真的改善恢复？ | 30—50 个可恢复 episode | No/Random/Shuffled/Predicted/Oracle Evidence；retry/rollback/reflection | Oracle 相对 No ≥10% 且 CI>0；Predicted 至少正向趋势且胜 Random/Shuffled | 4 条件重放，2—4 天 | Oracle 无增益直接 NO-GO；Predicted≈Shuffled 则暂缓方法 |
| Gate 4 | 2—3 个模块能否胜强公平基线？ | 100—200 独立任务，≥3 错误类型，任务级切分 | 完整 M1—M3，对 GuardAgent/VeriGUI 协议/SyncMind/Fission 近似基线 | RQ1 macro-F1、RQ2 recovery success；相对最强基线 ≥10%，paired CI 下界>0 | 1—2 周，约 \$100—300 API | 任一主章不过门则不能以双章主线开题 |
| Gate 5 | 是否具有自然与外部效度？ | 第二 benchmark/框架；≥50 自然故障任务 | 跨模型、跨工具、延迟和非单调恢复 | 方向一致；harmful recovery 不恶化；至少一个外部域 CI 不全面为负 | 1—2 周 | 只能受控语法成立则论文降为窄 Harness 研究，不使用广义标题 |

### 方向 A 允许转向

- Gate 1 缺语义 Oracle：转向方向 C 的过程 evaluator；
- Oracle 恢复有效但 Predicted 无效：保留问题，改进 RQ1，不用 Oracle 充当方法；
- 单调二分只在语法故障有效：改用分段候选检查或直接枚举高置信动作，不强行保留二分。

### 方向 A 禁止补救

- 扩大 API 次数但不固定预算；
- 把注入字段、异常码或最终测试直接输入 verifier；
- 将现有 34 个构造样本拆成多个“独立正实验”；
- Predicted 失败后把 Oracle 写成主结果。

---

## 9.2 方向 B Gate 表

| Gate | 唯一问题 | 最小数据/环境 | 方法与基线 | 主指标和门槛 | 资源/时间 | GO / STOP |
|---|---|---|---|---|---|---|
| Gate 0 | 论文、代码和 benchmark 是否可复现？ | AWM、HiAgent、G-Memory、AgeMem、Mem2ActBench | 仓库、许可证、入口审计 | 至少 3 个可运行开源实现；至少 1 个主动记忆利用 benchmark | 1 天 | 只有论文无可跑资产则 CONDITIONAL；不足 2 个环境则 STOP |
| Gate 1 | 是否有真实 memory-dependent 任务和冲突案例？ | ≥100 独立任务；≥30 stale/conflict/error-memory cases | 任务与记忆字段审计 | human/sample audit 中 ≥80% 确实依赖记忆；Gold 不由提示模板直接暴露 | 1—2 天 | 只能做被动问答、没有工具行为或冲突时 STOP |
| Gate 2 | 简单 RAG 是否已足够？ | 100 任务任务级划分 | Full context、recency、vector retrieval、AWM、HiAgent | 固定 Token 预算下任务成功率 | 2—4 天，API \$30—100 | 复杂结构不胜 vector/summary，且错误记忆影响很低，则 NO-GO |
| Gate 3 | 预测效用是否能帮助记忆治理？ | ≥80 任务，多轮或跨 episode | No/Random/Shuffled/Predicted/Oracle utility | Oracle 相对 recency/vector ≥10% 且 CI>0；Predicted 胜 Shuffled | 2—4 天 | Oracle 都无效则停止“效用预测→管理”桥梁 |
| Gate 4 | 分层构建与治理是否分别成立？ | 200—400 任务，2 个 benchmark | M1—M3；AgeMem/Memory-R1 协议；错误记忆控制 | RQ1/RQ2 主指标均 ≥10% + CI | 1—2 周，API \$150—500 | 只节省 Token 不提升成功率则标题降级为效率研究 |
| Gate 5 | 跨模型与分布变化是否可靠？ | 第二 backbone、跨网站/任务域、memory noise | 模型/域/长度分层 | harmful-memory rate 显著降低；至少一个外部 benchmark 正向 | 1—2 周 | 只在单一模型/同题复用成立则不能声称一般长期记忆 |

---

## 9.3 方向 C Gate 表

| Gate | 唯一问题 | 最小数据/环境 | 方法与基线 | 主指标和门槛 | 资源/时间 | GO / STOP |
|---|---|---|---|---|---|---|
| Gate 0 | 是否存在公开、可执行的 process evaluation 资产？ | DevAI、Plan-RewardBench、SWE-Gym、Agentic Rubrics | 论文/代码/许可核验 | 至少 3 篇正式 CCF A；至少 2 个可运行 benchmark | 1 天 | 只剩闭源 judge 和无 Gold 评价时 STOP |
| Gate 1 | requirement/evidence Gold 是否可信？ | ≥100 独立 task/trajectory；至少 300 requirement items | 人工/测试/rubric 对齐审计 | ≥80% requirement 可映射到证据；不读取隐藏测试结论 | 1—3 天 | 主要标签来自同一个 Judge 自评则 STOP |
| Gate 2 | 强 judge 是否已覆盖方法空间？ | 100 任务 | test-only、LLM-Judge、Agent-as-a-Judge、Agentic Rubrics、RM | joint verdict+evidence accuracy | API \$50—150，3—5 天 | 新方法不胜强 judge 或只多调用工具则 NO-GO |
| Gate 3 | 正确反馈是否真的改善 Agent？ | 50—100 任务，1 次修正或固定 best-of-N | No/Random/Shuffled/Predicted/Oracle feedback | Oracle 改善 final success ≥10%；Predicted 胜 No/Shuffled 且 harmful feedback 可控 | API \$100—300，3—5 天 | verifier 准但反馈无效，则不能形成双章 |
| Gate 4 | 评价与选择性反馈模块能否双过门？ | 200+ 任务，任务级外测 | M1—M3 与强基线 | 两章各 ≥10% + paired CI | 1—2 周 | 只提高评价分，不提高可执行任务结果则降为单章方向 |
| Gate 5 | 长轨迹和跨 Agent 是否泛化？ | 第二框架/模型；长轨迹与失败恢复分层 | 跨模型、证据缺失、预算分析 | 外部方向一致；risk–coverage 可用 | 1—2 周 | 只适用于单一 judge/backend 时不作为首选毕设 |

---

# 10. 首选方向 A：第一周执行清单

## 第 1 天：论文与仓库锁定

**工作：**

1. 保存 CCF 第七版目录页面/PDF；
2. 核验 VeriGUI、SyncMind、Fission-GRPO、GuardAgent、Process-Centric Analysis 的正式页；
3. clone 或固定 SyncMind、GuardAgent、Graphectory、SWE-Gym；
4. 记录 commit、license、数据链接、smoke command 和硬件条件。

**产物：**

- `paper_manifest.csv`
- `repo_manifest.csv`
- `license_risk.md`

**当天停止条件：**

- 找不到至少 3 篇正式 CCF A 对验证/恢复直接站台；
- 没有一个可执行、可下载的主 benchmark；
- 数据或许可证明确禁止研究使用。

**不做：**训练模型、调用大规模 API、写完整 Harness。

---

## 第 2 天：动作效果数据资格审计

**工作：**

1. 从 SyncBench 评测子集抽 15 条；
2. 从当前受控软件案例抽 10 条；
3. 从 BFCL/TAU 或其他工具错误数据抽 5—10 条；
4. 对每条填：

```text
task_id
environment
pre_state
action
expected_effect
post_observation
post_state
effect_oracle
oracle_source
delay
replayable
natural_or_constructed
```

**产物：**

- `effect_contract_sample.jsonl`
- `qualification_report.md`

**当天停止条件：**

- 合格样本不足 30；
- 大多数只有最终成败，没有动作效果；
- pre/post 状态不能配对；
- Oracle 只能依靠 LLM 解释。

---

## 第 3 天：最强简单基线

**工作：**

- Return-Code；
- Last Observation Keyword；
- Fixed Periodic Probe；
- Every-Step Probe；
- Direct LLM Verifier（小预算）。

**产物：**

- `baseline_results.json`
- `shortcut_audit.md`

**审计：**

- 屏蔽显式 error/failed；
- 打乱工具名；
- 同任务不跨划分；
- 检查注入字段不进特征。

**当天停止条件：**

- 简单 return code 在所有有效类型上接近满分；
- 模板/错误词屏蔽后任务无法定义；
- 所谓语义效果实际都是工具协议错误。

---

## 第 4 天：恢复 Oracle Bridge

**工作：**

对 20—30 个可恢复任务比较：

- No Evidence；
- Random Effect Type；
- Oracle Effect Type + Evidence。

恢复策略固定为：

- retry；
- 参数修正；
- rollback；
- re-observe and replan。

**产物：**

- `oracle_bridge_results.json`
- `paired_effect_table.csv`

**当天停止条件：**

- Oracle 不比 No/Random 提高 10%；
- 恢复结果主要由给定注入步骤直接保证；
- 不能从同一检查点复现。

---

## 第 5 天：最小预测 verifier

**工作：**

- M1 使用规则/工具 schema 生成预期效果；
- M2 使用状态 diff + probe；
- M3 仅做 confidence/unknown；
- 不训练大模型。

**产物：**

- `minimal_verifier.py`
- `predicted_effects.jsonl`
- `verifier_pilot.md`

**当天停止条件：**

- Predicted 与 Shuffled 相同；
- 预测几乎完全复制错误码；
- clean false alarm 不可接受。

---

## 第 6 天：Predicted Bridge 与成本对齐

**工作：**

比较 No / Random / Shuffled / Predicted / Oracle，确保：

- 相同候选恢复动作；
- 相同 API 调用上限；
- 相同 probe 次数；
- 相同任务和随机种子。

**产物：**

- `bridge_matrix.csv`
- `cost_manifest.json`
- `decision_draft.md`

---

## 第 7 天：方向裁决

第一周结束只有满足以下条件才进入方法实现：

1. 30 个以上独立合格任务；
2. 至少 3 类效果不一致；
3. Oracle Bridge 过 10% + CI 门，或小样本 CI 尚宽但所有任务级方向一致；
4. Predicted 明显优于 Random/Shuffled；
5. clean false alarm 可控；
6. 主数据、代码和许可证可继续使用。

否则：

- 数据 Gold 不行 → 停 A，转 C；
- Oracle 无增益 → 停 A；
- Predicted 不行但 Oracle 行 → 允许进入两周改进，不允许用 Oracle 开题；
- 只有受控语法行 → A 降为 Harness 小方向，不使用宽标题。

### 第一周明确不做

- 不训练 7B/8B RL 模型；
- 不全量跑 SyncBench 24k；
- 不大规模调 Prompt；
- 不为漂亮数字更改主指标；
- 不写复杂 Web UI；
- 不把现有 34 任务当自然外测；
- 不提前制作“已 GO”的开题 PPT。

---

# 11. 首选方向 A：八周里程碑

| 周 | 阶段 | 硬产出 | 进入下一周条件 |
|---:|---|---|---|
| 1 | Gate 0—3 | 文献/许可 manifest、30-task effect contract、基线、Oracle/Predicted Bridge | Oracle 有价值且 Predicted 胜随机 |
| 2 | 数据合同扩大 | 60—100 任务、三类效果、clean controls、任务级 split | ≥70% 可稳定判定和重放 |
| 3 | RQ1 最小方法 | M1—M3、5 个基线、任务级测试、快捷方式审计 | macro-F1 相对最强公平基线有 ≥10% 趋势 |
| 4 | RQ1 冻结确认 | 全新任务确认、paired bootstrap、成本/延迟 | CI 下界 >0，clean FPR 可控 |
| 5 | RQ2 恢复策略 | retry/reflect/rollback/fixed/proposed；同预算条件 | Predicted evidence 胜 No/Random/Shuffled |
| 6 | 多类型与非单调故障 | 参数、状态漂移、局部测试回归；分段搜索 | 不只语法故障成立 |
| 7 | 外测 | 第二 benchmark 或 Agent 框架；至少 50 任务 | 至少一个外部域正向且无严重负迁移 |
| 8 | 冻结开题 | 技术图、结果表、风险、协议、复现脚本、开题稿 | 两章均有独立主结果或明确 Conditional-Go 证据 |

---

# 12. 最终推荐

## 12.1 首选

> **动作效果验证与选择性恢复**

### 为什么排第一

1. 有正式 CCF A 论文对整篇方向直接站台，而不是只给小模块引用；
2. 研究对象比“最终失败预测”更可操作，Gold 可来自工具结果、状态 diff 和测试；
3. 两章关系自然：验证证据直接决定恢复，而不是强行用风险分数解释根因；
4. 能最大化复用 checkpoint、同状态 replay、撤销和阴性对照资产；
5. 最便宜的 Gate 可以在一周内完成；
6. 即使最终方法不胜，仍可得到动作效果可观测性、延迟、恢复适用边界等清楚结论。

### 当前判定

**Conditional-Go。**

在完成 Gate 1 的效果合同和 Gate 3 的 Oracle/Predicted Bridge 前，不能直接写成“已可开题”。

---

## 12.2 备选

> **分层记忆管理与可靠利用**

### 为什么作为备选

- 2025—2026 正式高水平论文非常充足；
- 有主动记忆利用、错误经验传播和新增/删除等完整问题；
- 与用户已有 BranchMind、上下文与记忆兴趣一致；
- 不依赖难定义的故障时点 Gold。

但它需要新 Harness，复现范围大，且容易与现有 memory framework 重叠。只有 Gate 1 能形成真实 memory-dependent 工具任务、Gate 3 证明效用预测有管理增量时才适合作为主线。

---

## 12.3 第三方向

> **过程评价与选择性反馈优化**

它有充足正式论文和数据，但重叠压力最大。若 Agent-as-a-Judge、Agentic Rubrics 或 SWE-Gym verifier 已在同预算下覆盖完整方法，新增工作很容易退化为 Prompt/系统拼装。除非 Gate 3 证明“证据正确性 + 选择性反馈”显著降低有害修正，否则不建议优先投入。

---

## 12.4 明确不再建议

1. 普通在线失败预测；
2. 责任 Agent → 责任动作；
3. 故障传播链必须改善定位；
4. 只做受控语法二分定位；
5. 仅换模型、embedding 或 Prompt；
6. 仅做 Agent trace 可视化；
7. 把历史成功轨迹当 Gold；
8. 让 LLM Judge 自己提供标签、证据和最终裁判。

---

# 13. 仍会改变决策的本地信息

只需要补充以下信息；其余不应阻止先做 Gate 0/1：

1. **当前是否有可用 Linux + Docker 环境**，以及单任务容器运行的平均时间；
2. **可使用的 API 模型、每分钟限制和可接受总预算**，不提供密钥；
3. **是否接受主域从软件 Agent 扩展到工具/GUI Agent**。若只接受软件 Agent，方向 A 主数据优先 SyncBench + SWE-Gym；
4. **当前磁盘空间与 GPU 是否仍约为 12GB 显存级别**；
5. **能否保存新采样 Agent 的每步 checkpoint 或 git commit**。这一项直接决定自然恢复实验上限。

---

# 14. 最终一句话

> 不再围绕“怎样从终局失败猜中间故障”继续堆检测器，而把研究对象前移到工具动作的预期效果与真实后果，先验证动作是否真正生效，再研究证据驱动的选择性恢复；这是当前文献站台、可执行 Gold、既有资产复用和两章递进关系最均衡的新方案。

---

# 15. 此前一次 Sol Max 独立复审（历史记录）

> 复审时间：2026-08-21。复审者只读检查要求、结论00/35/36/37及实验35/38/39/40，并重新核验官方论文与资产。本节覆盖第12节的初稿推荐口径。这是历史记录，不作为今后“三种设计”的计数先例；新计数只能针对同一明确目标。

## 15.1 独立总裁决

- A 只保留最后一次 **AppWorld 资格—Oracle桥** 实验；不继续 SyncBench，也不选 τ-bench 做本次最低成本入口。任一冻结门失败，A 永久 STOP。
- B 维持 Gate1 STOP：当前公开资产中，完整 `memory→retrieve/use→tool/result→独立 stale/error/conflict Gold` 自然案例为 0。
- C 维持 Gate1 STOP：requirement→evidence/source/location 独立映射为 0/365。
- 复审当时的顶层事实为：**A CONDITIONAL，B STOP，C STOP，0/3 方向两章 GO。** 实验42执行后，更新为 **A STOP，B STOP，C STOP，0/3 方向两章 GO。**

### 15.1.1 AppWorld 实际执行结果（实验42）

以下是计划形成后的本地实测，不是资源页推测：

- 官方仓库 tag/commit 与 `appworld==0.1.3.post1` 一致；install、data 下载、experiment-output 下载均成功，无付费 API。
- `appworld verify tasks` 对 train+dev 147/147 通过；固定 train 5 + dev 5 的入口 smoke 均可构造环境、保存/恢复 checkpoint，并调用中间态 evaluator。
- 预注册的 `simplified_react_code_agent_gpt-4o-2024-05-13_train` 和 `..._dev` 目录在官方 output bundle 中均不存在。
- 可见的 `react_gpt4o_test_normal`（168 task）和 `react_gpt4o_test_challenge`（417 task）均没有 `environment_io.md`；它们属于 test split，不能替代 train/dev 动作级自然轨迹。
- scenario ID 未在可公开提交的 schema 中序列化，不能读取受保护 generator 源码反推独立性。

因此实验42严格裁决 `Gate0=STOP`、`Gate1 ready=STOP`，没有执行下述 30-task Gate1。方向 A 按独立复审的冻结规则永久 STOP。

## 15.2 为什么最后选择 AppWorld

正式论文：[AppWorld，ACL 2024 Long，Best Resource Paper](https://aclanthology.org/2024.acl-long.850/)；官方代码：[StonyBrookNLP/appworld](https://github.com/StonyBrookNLP/appworld)。冻结 `appworld==0.1.3.post1`，对应 tag commit `66ad8099e12188ece0d3fe45e661dbc01880813b`。

官方入口：

```bash
pip install appworld==0.1.3.post1
appworld install
appworld download data
appworld download experiment-outputs
appworld verify tasks
```

只使用官方公开的 train/dev GPT-4o 轨迹：

- `simplified_react_code_agent_gpt-4o-2024-05-13_train`；
- `simplified_react_code_agent_gpt-4o-2024-05-13_dev`。

这些输出预期包含 `environment_io.md`、`api_calls.jsonl`、数据库变化与版本信息；train/dev 公开 ground truth、evaluation code、API calls 和 validation solution，环境提供 `world.save_state()` / `world.load_state()`。AppWorld 用数据库状态单测评价任务与 collateral damage，允许替代完成路径，比把 canonical action sequence 当唯一 Gold 更适合动作效果与恢复。

“自然”在本文只表示：**非本项目构造、由公开真实 Agent 运行得到、运行于模拟可执行 benchmark 的轨迹**；不得写成生产环境自然日志。许可证为 Apache-2.0 加保护内容再分发限制；可本地研究，但不得提交或公开解密后的原始 task/evaluator/trajectory 派生包。

不选 τ-bench 的原因：原始 [τ-bench 是 ICLR 2025 正式论文](https://openreview.net/pdf?id=roNSXZpUDN)，但 canonical ground-truth action sequence 对合法替代路径可能有偏差；原版、τ² 和 leaderboard trajectory 的版本边界还需额外冻结，新 rollout 通常依赖 user/agent LLM。当前 [τ² 代码](https://github.com/sierra-research/tau2-bench) 不能冒充原始 ICLR 2025 正式论文。

## 15.3 AppWorld 最后一次 Gate1

> **执行状态：未进入。** 本节保留的是预注册协议；实验42已在资产 Gate0 因动作级 train/dev 轨迹缺失而 STOP，不得把 10-task 引擎 smoke 或 test split 数据写成下述 Gate1 已完成。

固定样本：

1. 按 `SHA256("20260821"|task_id)` 排序；
2. 固定 30 个不同 task generator/scenario，每个 generator 至多一个 variant；
3. 至少覆盖 3 个 primary app；
4. 不按最终成功、Gold 或“看起来可跑”过滤；
5. generator/scenario 独立性无法确认时，直接 STOP。

每个任务从同一初态重放两次；每个 state-changing block 保存：

```text
pre checkpoint → natural action block → post checkpoint
              → API/output → DB delta
```

动作效果 Gold 只能在冻结 observation 后由官方 requirement/collateral evaluator 向量计算：

\[
effect(a_t)=E(s_{t+1})-E(s_t)
\]

类别冻结为：

1. `progress`：至少一项 fail→pass，且无 pass→fail/collateral；
2. `regression_or_collateral`：任一 pass→fail 或意外状态改变；
3. `no_verified_progress_or_error`：向量不变、执行错误或无可验证效果。

若 evaluator 不能在中间 checkpoint 稳定运行，或只对最终完成态有意义，不得自行补动作标签，直接 STOP。

Gate1 所有门必须同时满足：

- clean replay ≥27/30；
- 稳定动作效果 Oracle ≥21/30；
- 3 类效果均出现，且每类来自至少 5 个不同 task；
- ≥3 primary app；
- 30 个独立 task 均有 state-changing action；
- task、原始输出、代码和数据版本/SHA 全部落盘。

任一不达即 A Gate1 STOP；不得换 seed、降门、补构造 action 或用 validation solution 生成动作。

在线 verifier 只允许 task instruction、当前/历史自然 action、API 返回/异常、stdout/stderr、schema-level state-delta 摘要。禁止读取 `.ground_truth`、evaluation code、requirement vector、validation solution、ground-truth API calls、未来动作和最终结果。Predicted 先冻结，之后才能打开 evaluator；切分按 generator/scenario，统计单位始终是 task。

## 15.4 RQ1 Gate2 与恢复 Gate3

RQ1 使用 task-grouped 5-fold OOF，基线冻结为：majority effect、API status/exception rule、state-delta magnitude rule、instruction–action lexical/embedding baseline。可用本地线性/树模型，不调用付费 API。主指标为 task 聚合 macro-F1；Predicted 相对最强冻结基线必须 ≥10% relative，且 task paired-bootstrap 95% CI 下界 >0，否则 RQ1 不 GO。

恢复动作冻结为：从 action 前 checkpoint 恢复、跳过该 block，再重放原公开 suffix。所有条件拥有相同 checkpoint 权限：

- No：不恢复；
- Random：以 Oracle 相同干预率随机 rollback；
- Shuffled：在同 fold/app 内置换 Predicted 分数；
- Predicted：仅用 OOF effect score；
- Oracle：只用官方动作效果 Gold，作为信息上界；
- API-error-only rollback：公平强简单对照。

主指标为最终官方 requirement pass fraction / SGC；TGC、collateral rate 和额外执行成本为辅助指标。每个 task 只贡献一个最终分数。

严格裁决：

1. Oracle 相对 `No/Random/API-error-only` 最强者 ≥10% relative，且 task paired-bootstrap CI 下界 >0，桥接才有信息价值；否则 A 永久 STOP。
2. Oracle 通过后，Predicted 相对 `No/Random/Shuffled/API-error-only` 最强者也必须 ≥10% relative + CI 下界 >0；否则两章结构 STOP。
3. 30-task 只算开题前 Gate，不足以直接声称完整章节或论文 GO；仍需更大自然任务与跨轨迹/模型外测。

## 15.5 AppWorld 失败后的新方向排序

### 首选：状态化工具 Agent 的接口契约鲁棒性与失败修复

- 第一章：跨 schema/format/state 变化的工具调用失效检测与诊断；
- 第二章：消费第一章 OOF 诊断的 abstain、clarify、canonicalize、retry 修复；
- 正式锚点：[BFCL，ICML 2025](https://proceedings.mlr.press/v267/patil25a.html)；
- 官方资产：[Berkeley Function Calling Leaderboard](https://github.com/ShishirPatil/gorilla/tree/main/berkeley-function-call-leaderboard)，可离线使用公开 model response/evaluator；
- 外测：[Apple ToolSandbox](https://github.com/apple/ToolSandbox)，但其论文是 NAACL 2025 Findings，不能冒充 CCF A 主会。

最低 Gate：固定 120 个独立 BFCL task，四个 multi-turn 族 `base/miss_func/miss_param/long_context` 各30；evaluator 两次一致 ≥114/120，每族去重后 ≥25。Gate3 比较 No/Random/Shuffled/Predicted/Oracle，Oracle 与 Predicted 均须相对最强公平基线 ≥10% relative 且 task paired-bootstrap CI 下界 >0。

### 次选：Agent 安全策略执行与动态最小权限工具编排

- 第一章：把安全/访问控制策略编译为可执行 action authorization；
- 第二章：基于预测风险动态暴露、撤销或隔离工具能力；
- 正式资产：[ASB，ICLR 2025](https://openreview.net/forum?id=V4y0CpX4hK)及[官方代码](https://github.com/agiresearch/ASB)；
- 补充资产：[AgentDojo，NeurIPS 2024 Datasets & Benchmarks Track](https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html)及[官方代码](https://github.com/ethz-spylab/agentdojo)。

Gate0 必须先证明无需付费 API、8GB 本机能重放公开 response 与 programmatic utility/security checks；否则 STOP。

### 第三：状态化 user–agent 协同的失同步检测与澄清恢复

- 第一章：检测 Agent belief、用户约束和数据库状态失同步；
- 第二章：由 OOF 失同步类型选择 clarify/replan/rollback；
- 正式锚点为原始 τ-bench ICLR 2025，ToolSandbox milestone DAG 作为第二环境；
- 若拿不到可离线重放的公开 trajectory，或必须付费生成 user/agent rollout，Gate0 即 STOP。

## 15.6 对全部实验的最终阅读方式

- 实验01、28：数据/历史资格 GO，不是方法 GO；
- 实验02：窄范围受控责任动作机制 GO，不代表自然因果；
- 实验04、09、10、11、12、14、31、34：研究假设 NO-GO；
- 实验06、07、08、15、16、18、26、29、30：开发/历史正信号；
- 实验03、05、13、17、19—25、27：资产、基础设施或 Stage0 STOP；
- 实验32、33：历史混合/降级证据；
- 实验35：constructed contract GO，方向 A Gate1 CONDITIONAL；
- 实验36、39：B 的规模与构造生命周期信号，不能覆盖自然数据；
- 实验37：C Gate1 STOP；
- 实验38：clean replay 2/2、stable Oracle 0/2，方向 A 仍 CONDITIONAL；
- 实验40：B 自然合格案例 0，Gate1 STOP。
- 实验42：AppWorld 引擎与 147 个 train/dev task 可运行，但冻结的公开动作级 train/dev 轨迹不存在，Gate0 STOP；方向 A 永久 STOP。

最容易误读的三个数字是：实验35的30/30只证明接口；实验39的30/30是同源指纹合同敏感性；实验38的2/2只证明失败环境能一致复现。它们均不是章节研究 GO。

---

# 16. BFCL 方向 D 的实测状态与后续复审任务

> 本节是给无法读取本地文件的外部 GPT 的完整现状摘要。不得仅凭第15节的事前计划做判断。

## 16.1 研究目标与两章最低合同

方向 D 的候选题目是《面向状态化工具智能体的接口契约鲁棒性诊断与失败修复方法研究》。

- 第一章目标：只用在线可见的 user/response 前缀与公开 tool schema，对调用失败做 grouped OOF 检测/诊断，显著胜过强规则基线。
- 第二章目标：消费第一章的 OOF 诊断，选择性执行真实改变 response 的修复，并在官方 evaluator 下取得显著收益。
- 两章不能只靠共用一个数据集连接。修复 Oracle 先要证明失败 response 中仍有可用信息；Oracle 无信息价值时，不应先训练诊断器。

## 16.2 锁定资产与 Gate0/1 实测

- 官方代码：`ShishirPatil/gorilla` commit `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`。
- 官方包：`bfcl-eval==2026.3.23`。
- 公开结果索引：`HuanzhiMao/BFCL-Result` commit `6830ed13035c0cfee9aa7a9a0ffed70f10b3dd50`，锁定 `2025-12-16/result/BitAgent_BitAgent-Bounty-8B/multi_turn`。
- 四个家族：`multi_turn_base`、`multi_turn_miss_func`、`multi_turn_miss_param`、`multi_turn_long_context`。源端每家族 200 task/200 public response，均严格 200/200 join。
- Gate1 使用四家族各 30 的固定 manifest；全局 120 个 task hash 唯一，120 个结构签名唯一。初版曾只有 95 个跨家族独立结构，已被主线程拒绝并改为全局去重重抽，不保留虚高的 120 口径。
- 官方 evaluator 双 replay 120/120 一致，0 harness error。原始 `No` clean VALID 为 75/120：base 22/30、miss_func 14/30、miss_param 22/30、long_context 17/30。

因此 Gate0 和 Gate1 是 GO，但这只证明数据、join、独立性和 evaluator 稳定；75/120 是公开模型的原始成绩，120/120 是 replay 一致率，两者都不是本项目的章节 GO。

## 16.3 必须遵守的 Gold/未来信息边界

在线 policy 只能看当前及历史公开 user/response 前缀和当轮可见 schema。以下字段一律禁止：`possible_answer/ground_truth`、官方 evaluator 产生的 error class、future user/assistant/tool turn、完整 question 长度、`initial_config`、`missed_function`、path/family、hidden state、`inference_log`、最终 score。Gold 只能在全体候选输出、operator 与完整输出 digest 已冻结之后，由隔离的离线评分阶段读取。

特别注意：公开 BitAgent `result` 允许评估“执行前 response patch”，但不包含可合法使用的真实 tool output/state/handler step。所以它目前不支持冒充成“观察执行后反馈再 retry”的交互式恢复。

## 16.4 同一修复目标的三设计升级规则

明确目标是：**BFCL 公开 response 与可见 schema/user 前缀是否保留足以实现执行前修复的信息**。

针对这一目标，预注册三种实质不同的模块：

1. 契约字段 patch：函数/参数规范化、类型安全转换、当前字面量填充、invalid call 删除、abstain。
2. 调用级选择性裁剪：leave-one/keep-one call、item 裁剪、严格重复调用删除。
3. schema/可见字面量局部替换：对已有 call 做单参数替换或填充、类型兼容函数替换、最多一次“函数替换+一个缺失参数填充”；不删 call、不新增 call、不读未来轮。

三者共用门槛：全局最强真实 baseline 预先冻结，Oracle 相对它至少 10% relative，净救回至少 8/120，task-paired bootstrap 95% CI 下界大于0，全候选双 replay 120/120，harness error=0。只有全部同时满足才 GO。

“三次”不是命令执行次数，也不是三个方向各失败一次。下载/安装、修复 bug、重跑、调阈值、改 seed 和同模块的小变体均不计数。第三种模块也严格 STOP 后，才可委派 Sol Max 对这一目标做新的独立调研。

## 16.5 修复设计 1/3：契约 patch 实测

冻结 3264 个候选。真实 support 审计显示：Name/Type/Fill 语义改变均为0；DropInvalid 有 354 个候选/102 task；Abstain 覆盖120 task。初版曾把 JSON 空格重序列化当成参数变化，已被主线程拒绝并改为“语义不变则保留原文”。

| 指标 | 结果 |
|---|---:|
| No | 75/120 |
| SchemaRuleRepair | 70/120 |
| Oracle | 75/120 |
| 净救回 | 0 |
| bootstrap 95% CI | [0,0] |
| 双 replay / harness error | 120/120 / 0 |

裁决：设计 1/3 `STOP`。

## 16.6 修复设计 2/3：调用级裁剪实测

冻结 9418 个候选。support 并非为空：98/120 含 multi-call，120/120 含 multi-response-item，turn 内重复任务33条，历史重复8条，共解码2433个 call。

| 指标 | 结果 |
|---|---:|
| No | 75/120 |
| ExactDedupRule | 74/120 |
| Oracle | 75/120 |
| 净救回 | 0 |
| bootstrap 95% CI | [0,0] |
| 双 replay / harness error | 120/120 / 0 |

裁决：设计 2/3 `STOP`。它的失败不是“没有多调用可剪”，而是这些裁剪候选无法救回任何 No 失败任务。

## 16.7 修复设计 3/3 与外部 GPT 待做决策

设计3已完成，它只改已有 call，不增删/不重排 call；同一候选最多改一个已有 call，只有“函数替换+填一参数”可包含两个原子字段编辑。所有26503个候选与25839个完整输出 digest 均在 Gold 前冻结；主线程独立复跑 support-only 和全量 evaluator，结果与提交一致。

support 并非为空：已有参数替换 5874 个/101 task，swap 2083/92，兼容函数替换 8774/107，函数替换+单 literal 9532/87；缺失 required+可见 literal 和 enum 明示对齐均为0。

| 指标 | 结果 |
|---|---:|
| No | 75/120 |
| LexicalSchemaRule | 5/120 |
| 全局最强 baseline | No（75/120） |
| Oracle（不含 baseline） | 75/120 |
| 净救回 / 受损 / 不变 | 0 / 0 / 120 |
| bootstrap 95% CI | [0,0] |
| 双 replay / harness error | 120/120 / 0 |

裁决：设计 3/3 `STOP`。这不是 support 为空或 evaluator 不稳定，而是大量实际局部替换仍无法救回任何 No 失败任务。

因此同一修复目标已满足三种实质不同模块全部无进展的条件，Sol Max 独立复审现已启动。复审必须回答：

1. 这是 BFCL 当前公开 response 的可观测性上限，还是三种候选空间均避开了真正错误机制？
2. 在不读 Gold/未来轮/hidden state、不调用新模型的前提下，是否还存在一个**机理上不同**、可被官方 evaluator 重评的修复桥？若有，需明确输入、干预、强基线、泄漏防线与一轮停止门。
3. 若无，方向 D 是否应在第二章桥接上 STOP，并转向第15.5节的 ASB/AgentDojo 安全策略与动态最小权限方向？
4. 新方向必须先证明两章各自有至少一个可执行 Gold、一个非循环的信息桥和一个不依赖付费 API 的最小自然样本 Gate；不得只换题目名称。

在 Sol 报告返回前，当前严格事实仍是：A/B/C STOP，D Gate0/1 GO 但第二章修复桥 3/3 STOP，**没有任一方向达到两章 GO**。

## 16.8 Sol Max 复审后的关键更正：三组旧分数 INVALID

> 本节是最新且最高优先级口径，覆盖第16.5—16.7节对三组 `STOP` 的解读。候选规则、Gold前冻结和support统计仍可保留；所有旧Oracle/救回/bootstrap/双replay科学结论必须废弃并重评。

官方 BFCL `execute_multi_turn_func_call` 将有状态class instance以 `model_name + test_entry_id + class_name` 为键存入模块 `globals()`；同名时明确复用为 subsequent turns，且checker不自动cleanup。实验44/45/46的runner对同一task的所有candidate只用 `replay_index + task_hash`生成`model_name`，没有candidate digest。所以No之后的candidate会从前一candidate的模拟状态继续；ground-truth namespace也同样积累。两条replay流按同一candidate顺序污染，因而可以“120/120一致地错”。

正确重评合同：

1. 保留同一120 task、候选生成器、candidate/output digest与全部原门槛，不在看到Gold后改候选。
2. namespace必须包含 `(task_hash, candidate_output_digest, replay_id)`；评分前断言实例键不存在，每个candidate后在`finally`删除model与ground-truth的所有involved-class instance。
3. replay-1按candidate升序、replay-2按逆序，且再做固定seed shuffle；每个 `(task,candidate)` outcome指纹必须完全相同。
4. fresh subprocess复核全120个No，并对非No按operator×family固定分层抽至少5%；任一顺序/进程不一致、残留global key或No不能复现75/120，都只能判`HARNESS_INVALID`。
5. 隔离后再重算三组全局强基线、Oracle、净救回与10000次结构簇paired bootstrap；旧的“3/3 STOP”计数撤回，无效实验不算三次无进展。

Sol还找到前三种模块确实未覆盖的唯一机理：**同一已有response item内的call执行顺序**。官方executor按call list顺序逐个执行并改变状态，只有execution-response的后续比较是unordered；而实验44‑46均明确`call_reorder=false`。公开support为98/120 task含multi-call item，共668个multi-call items；旧的17个evaluator-invalid中16个含multi-call。

若三组隔离重评仍全部严格STOP，只允许一个新桥 `WithinItemCallOrdering`：一次只重排一个已有item内的calls，保留call multiset/函数/参数/值/数量，不跨item/turn，不读Gold、future、tool output或state。预计有119960个changed permutations。以No与一个全局`SchemaDependencyOrder`为强基线，门槛仍为relative gain≥10%、net rescue≥8、CI lower>0、No=75/120、正/逆序全候选一致、0 harness error与fresh-process一致。任一科学门失败，D第二章永久STOP，不再加第五种局部算子；任一harness门失败只判INVALID。

如果D最终失败，下一条件候选改为**AgentDojo动作级策略授权与风险自适应能力防火墙**，不以ASB为主资产。AgentDojo必须先解决两个Gate0陷阱：旧`runs/`不总是显式记录benchmark/package version，不能默认join到v1.2.2；字段`security=True`在有injection时实际表示attack success（坏），必须重命名为`attack_success`并以`safe = not attack_success`评价。

当前最新严格事实：A/B/C STOP；D Gate0/1 GO，实验44‑46分数INVALID待隔离重评；AgentDojo尚未Gate0。**仍无任一方向达到两章GO。**

# 17. 核心论文局限的二次交叉复核：为什么下一方向是“动态授权”

> 本节为了供不能读取本地文件的外部 GPT 独立复审而写。它不把文献推理写成实验成功；当前严格状态仍是 **0 个方向两章 GO**。

## 17.1 不再按“想一个新模块”选题

二次复核不再从现有代码或某个数据集的字段反推论文，而是只保留同时满足以下条件的问题：

1. 问题是多篇近年 Agent 论文作者在 Limitation/Future Work 中自己暴露的交集；
2. 至少有一组 ICML/NeurIPS 正式主会论文能分别站台两个研究问题；
3. 可用真实模型在可执行 Agent benchmark 中产生的官方轨迹，而不是小型合成文本；
4. 标签有机会由程序化环境 evaluator 或反事实状态差分产生，不依赖 LLM judge 解释；
5. 第一章能独立评价，第二章只消费第一章 OOF 预测，关系可用 No/Random/Shuffled/Predicted/Oracle 证伪。

## 17.2 多篇论文自述不足的交叉

| 论文 | 正式身份 | 作者自述或实证的边界 | 对新方向的约束 |
|---|---|---|---|
| [AgentDojo](https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html) | NeurIPS 2024 Datasets & Benchmarks Track，只作环境/数据资产 | 静态 tool filtering 在下一步工具取决于前序返回时无法预规划；当合法任务和攻击共用工具时也失效，论文报告后者约占17%；尚未覆盖不重置上下文的多任务时序 | 不能再做静态黑白名单；要研究按当前状态和依赖逐步暴露/撤销能力 |
| [GuardAgent](https://proceedings.mlr.press/v267/xiang25a.html) | ICML 2025 正式主会 | LLM 先生成 plan 再生成 guardrail code，工具箱与记忆决定代码可执行性；作者将自动 toolbox 设计、更强 planning 推理、多 Agent 守卫列为后续 | 不做另一个守卫代码生成器；要研究当前动作所需的最小、短期、可撤销权限 |
| [ShieldAgent](https://proceedings.mlr.press/v267/chen25ae.html) | ICML 2025 正式主会 | 将政策抽取为 action-based probabilistic rule circuits，对轨迹生成验证计划；对需要策略外部知识的 hallucination risk 略弱 | 不能只换策略表示或验证 prompt；必须加入执行时状态、工具返回依赖和授权时效 |
| [AI Agents Need Authenticated Delegation](https://proceedings.mlr.press/v267/south25a.html) | ICML 2025 Position，只作问题与理论支撑 | 自然语言 scope 翻译面临正确性、LLM攻击面、上下文漂移、第三方执行可靠性问题 | 不做 OAuth/OIDC 工程 Demo；要实证自然语言委托到动作级授权的正确性与上下文更新 |
| [AgentAuditor](https://proceedings.neurips.cc/paper_files/paper/2025/hash/3dc85735f6e2fcf093e67b134fa00d21-Abstract-Conference.html) | NeurIPS 2025 Main Conference | 记忆增强 LLM evaluator 依赖 shot 标签质量，继承 CoT 资源/推理限制，只实证 binary safe/unsafe | 不做另一个 LLM judge；动作 Gold 必须来自程序化环境反事实，且必须改善执行结果 |
| [SafeArena](https://proceedings.mlr.press/v267/tur25a.html) | ICML 2025 正式主会 | 恶意意图是显式的，可被外部分类器直接发现；自动 evaluator 可能漏掉其他有害行为 | 不做 user-prompt 恶意分类；必须基于轨迹前缀、当前动作和状态后果 |
| [BFCL](https://proceedings.mlr.press/v267/patil25a.html) / [tau-bench](https://proceedings.iclr.cc/paper_files/paper/2025/hash/1b126cc38b8638e07bef37e7b2bb72bf-Abstract-Conference.html) / [AppWorld](https://aclanthology.org/2024.acl-long.850/) | 工具使用和长程可靠性补充 | 多轮、复合请求、规则遵循、状态/长程记忆和前序输出依赖均仍困难 | 授权不能只看单个 call 文本，需显式表示当前状态和 action-data dependency |

## 17.3 可辩护的统一问题

> **当合法任务与攻击共用工具、下一步所需能力取决于前序执行结果时，如何将用户委托、显式策略和当前环境证据转换为动作级、有时限、可撤销的最小权限，并在不显著伤害任务效用的前提下阻断越权执行？**

暂定题目：

> **《面向工具智能体的动作级策略授权与动态最小权限控制方法研究》**

它不是普通内容安全分类，研究对象是 Agent 的工具动作、状态化执行、能力暴露与撤销，属于 Agent Harness / AgentOps 运行风险控制。

## 17.4 两章的详细合同

### 第一章：可执行证据约束的动作级策略授权

- 输入：用户委托、显式策略、公开 function schema、当前轨迹前缀、proposed call。
- 输出：`allow / deny / abstain` 和可审计的 policy-resource-dependency evidence。
- 三个模块：
  1. 策略-资源绑定；
  2. 可见前缀的工具依赖接地；
  3. 证据不足时的选择性 abstention。
- 程序化 Gold：对已执行 call 进行 allow/block 反事实；用 user utility 和 injection attack-goal evaluator 的 before/after 差分定义 `utility-essential / attack-enabling / neutral`。
- 主指标：按 base task 分组的 OOF macro-F1；辅指标为 attack-enabling recall、utility-essential precision、coverage-risk。

### 第二章：依赖感知的动态最小权限能力防火墙

- 输入：仅使用第一章任务级 OOF 授权/风险分数、当前依赖状态与公开 schema。
- 输出：工具/参数/资源级短期 capability lease，以及 expose/restrict/isolate/revoke/block 决策。
- 三个模块：
  1. 当前步最小能力租约；
  2. 工具返回后按依赖续期或撤销；
  3. deny/abstain 的选择性强制与安全终止。
- 主指标：任务级 `J = utility_success AND NOT attack_success`；分开报告 utility、attack success、能力暴露面积、撤销延迟与成本。

两章专门证伪：`No/AllowAll / Random / Shuffled chapter-1 scores / OOF Predicted / Oracle`。Oracle 只证明信息上界；Predicted 不优于全局最强公平基线，则两章关系 STOP。

## 17.5 与已有方法的差异必须按这个口径写

- 相对 GuardAgent：不是生成另一份 guardrail code，而是对当前 proposed action 绑定最小、短期权限。
- 相对 ShieldAgent：不是只判断轨迹是否违反显式政策，而是把工具数据依赖和权限时效加入执行前强制。
- 相对 AgentDojo ToolFilter：不是事先一次性选工具集，而是每个状态步生成、续期和撤销 lease。
- 相对 AgentAuditor：不是轨迹文本 safe/unsafe judge，而是程序化反事实动作 Gold，并必须改善 task-level executable outcome。
- 相对 Authenticated Delegation：不是 OAuth/OIDC 凭证 Demo，而是在可执行 Agent benchmark 上实证委托 scope 的动作绑定、漂移和动态撤销。

## 17.6 为什么首个数据 Gate 选 AgentDojo，不选 ASB/SafeArena

- AgentDojo 是 stateful executable tool-agent environment，官方 repo 有实际模型轨迹、tool calls/tool outputs、utility/security evaluator。
- ASB 官方实现的主成功判定包含 substring 检查、GPT-4o-mini refusal judge 和 OpenAI embeddings，无法在不调付费 API 的情况下给出程序化 utility/security Gold。
- SafeArena 重度依赖易碎自动指标/轨迹评判，而且恶意意图显式，更适合作外部效度或困难样本来源，不适合第一轮严格 Gold Gate。

## 17.7 AgentDojo Gate0：版本与官方自然轨迹资格

1. 锁定官方 repo commit 和稳定 package version，对 `runs/` 做 metadata census。
2. 每个 run 记录 blob SHA、引入/最后修改 commit、suite/package/benchmark version；无法唯一绑定版本则剔除。
3. 严格 join key：`repo_commit + package_version + benchmark_version + suite + user_task_id + injection_task_id + attack_type + pipeline_name + run_blob_sha`。
4. 基础独立单位是 `(suite, canonical user_task)`；attack/defense/model/rollout 只是关联 episode，不重复算独立样本。
5. 最低门：至少 80 个唯一 base-task structures，覆盖 4 suites；每个 base task 有同 pipeline/model 的 clean 和 attacked episode；总计至少 160 episodes。
6. 数量不足即 STOP；不许用改写 prompt、合成轨迹或跨版本模糊 join 补数。

## 17.8 AgentDojo Gate1：精确 replay 与动作反事实 support

### 原样 replay 硬门

- 从精确版本重建 initial environment 和 injections，只执行确实进入 runtime 的 calls；blocked-but-attempted 不可假装执行。
- 保留 original final assistant text，因为 utility evaluator 可能依赖文本。
- fresh environment 双 replay，重新计算 user utility 与 injection `attack_success`。
- 注意：AgentDojo 的 `security=True` 在有 injection 时表示攻击成功，是坏标签；必须重命名为 `attack_success`，不能解释为 safe。
- 门槛：160/160 join 完整，stored labels 100% 复现，双 replay 100% 一致，0 harness error，每 suite 均非空，clean/attack pair 完整。不接受 90% 近似标签。

### action counterfactual support 硬门

- 对每个已执行 call 构造 allow/block；只有后续 call 参数与控制流不依赖被阻断 tool output 时，才允许固定 suffix replay。
- 依赖断裂标为 `OFF_POLICY_SUFFIX`，不作负例，不得假装 Agent 会按原路径继续。
- 最低 support：120 个稳定 counterfactual calls，来自至少 60 base tasks 和 3 suites；`utility-essential / attack-enabling / neutral` 各至少 20；全部标签由程序化 before/after evaluator 差分产生。
- 任一 support 门不足即 STOP，不生成 synthetic 30/30 补数。

## 17.9 Oracle bridge 与完整停止门

- 公平基线：`AllowAll`、`DenyAllMutating`、`StaticSchemaRisk`；全局只选一个 strongest arm，禁止逐 task union。
- 桥接臂：`No/AllowAll`、`Random`、`Shuffled`、`OOF Predicted`、`Oracle`。
- Oracle 和最终 Predicted 对全局 strongest baseline 都必须满足：
  1. `J = utility AND safe` 相对提升至少 10%；
  2. 净 rescue 至少 8 个 base tasks；
  3. 按 base task cluster 的 paired bootstrap 95% CI lower > 0；
  4. utility 绝对下降不超过 5 个百分点；
  5. replay/harness 门全部通过。
- Oracle 不过：整个两章桥 STOP，不训预测器。
- Oracle 过、Predicted 不过：只能证明信息上界存在，不能宣称两章 GO。
- 如果不重跑模型、只在已有 proposed-action stream 上做干预，论文必须准确称为 `execution-time capability firewall`，不宣称验证了 prompt-time tool orchestration 或 Agent 重规划。

## 17.10 当前决策顺序

1. 先完成 BFCL 实验44--46隔离重评；旧分数不算三次有效失败。
2. 如果三个实质不同的同目标设计在正确 harness 下均 STOP，只执行 Sol 独立审阅找到的 `Within-Item Call Ordering` 桥。
3. call-order 也 STOP，则 D 第二章永久 STOP，不再叠第五个局部 operator。
4. 然后执行 AgentDojo Gate0/1；这是由多篇论文限制导出的新目标，不是 BFCL 同目标的第四次换模块。
5. AgentDojo 版本 join、精确 replay、counterfactual support 或 Oracle bridge 任一不过即 STOP；先不训模型、不调付费 API、不合成轨迹补数。

## 17.11 请外部 GPT 重点独立反驳的问题

1. 以上缺口是否已被 GuardAgent/ShieldAgent 的 online guardrail 实质覆盖？请按输入、权限对象、时效、依赖更新和执行干预逐项比较，不要只比较名词。
2. 动作级 counterfactual label 在 AgentDojo 中是否真能严格定义？特别检查 off-policy suffix、attempted-vs-executed call、final assistant text 对 utility evaluator 的影响。
3. 第一章 `allow/deny/abstain` 是否有独立小论文价值，还是只是第二章的一个分数器？
4. 不调用新 Agent 模型时，execution-time firewall 的主张边界应如何写，才不会把固定轨迹干预误写成完整的动态 tool orchestration？
5. 除 AgentDojo 外，是否存在另一个具有官方自然模型轨迹、stateful executable environment、程序化 utility 和 security Gold，并且版本可严格 join 的公开资产？

当前文献裁决：**这是一个可以进入数据 Gate 的 `CONDITIONAL` 方向，不是已经可开题的 GO 方向。** 它相对此前设想的改善是：问题来自多篇论文局限的交集，两章有非循环输出桥，且第一步先验证数据/Gold/反事实是否真存在。

## 17.12 重要覆盖更正：第17.3--17.9节的 V1 方向与 Task Shield / IPIGuard 高度重叠

> 本节覆盖第17.3--17.9节“可直接进入 AgentDojo 数据 Gate”的中间判断。在按《研究生毕设选题实验可行性探索要求》继续扩大直接重叠检索后，V1 已不再符合“与最新论文的可辩护增量”硬要求。

两篇漏掉的直接重叠工作：

1. [The Task Shield: Enforcing Task Alignment to Defend Against Indirect Prompt Injection in LLM Agents](https://aclanthology.org/2025.acl-long.1435/)，ACL 2025 Volume 1 Long Paper。它已经将“每个 instruction 和 tool call 是否贡献于 user-specified goal”定义为 test-time task alignment，并在 AgentDojo 上同时评估 attack success 和 task utility。这与 V1 第一章的主任务不是相邻，而是近乎直接重合。
2. [IPIGuard: A Novel Tool Dependency Graph-Based Defense Against Indirect Prompt Injection in LLM Agents](https://aclanthology.org/2025.emnlp-main.53/)，EMNLP 2025 Main（Oral）。它已经通过 Tool Dependency Graph 将 action planning 与 external data interaction 解耦，并使用 pending node、argument estimation、node expansion 处理“后续工具/参数必须由前序 tool response 决定”的 dynamic planning task。这与 V1 第二章的依赖感知动态控制高度重合。

所以 V1 题目《面向工具智能体的动作级策略授权与动态最小权限控制方法研究》当前正式降级为：

> **`V1 REJECTED_OVERLAP`：不进入原计划 AgentDojo Gate0/1，只保留为待重定义的问题簇。**

两篇核心论文自己的限制为：

- Task Shield 依赖 powerful defender LLM；弱模型或对抗探测可使指令抽取/贡献打分失败，导致 false positive/negative；每个 assistant response 和 tool output 要额外 LLM call；主实验只覆盖 GPT 家族和 AgentDojo，未测开源 backbones。
- IPIGuard 只覆盖干预 tool usage 的 IPI，不覆盖只篡改 textual output 的攻击；由于 LLM 调用成本，实验规模受限；它依赖具有较强 planning capability 的模型。
- [USENIX Security 2026 SoK: Attack and Defense Landscape of Agentic AI Systems](https://www.usenix.org/system/files/conference/usenixsecurity26/sec26_prepub_kim-juhee-agentic.pdf) 明确说明，当前 Agent access-control 方法主要面向 RAG/vector database，对多工具、多数据源、多 Agent 和 evolving task/trust context 仍缺少 adaptive policy framework。但这只是问题簇站台，不能替代两章任务、方法和数据 Gate。

目前不立即把剩余限制包装成新题目，因为：

1. 只做“轻量化/少调 LLM/换开源模型”主要是成本或模型替换，不满足两章独立研究价值。
2. “短期 capability lease、动态撤销、多任务 context drift”尚未找到同时满足正式 CCF A 方法站台、公开可执行环境、官方自然轨迹、程序化 Gold 的资产。
3. 只在已有 AgentDojo response 上 block call 会导致 off-policy suffix，无法充分验证 IPIGuard 已经覆盖的 replanning/dynamic traversal。
4. Task Shield 未找到可确认的作者官方代码；IPIGuard 虽有 [官方 Apache-2.0 代码](https://github.com/Greysahy/ipiguard)，但官方运行合同需 OpenAI-compatible API。当前无法保证同预算、同模型的强基线复现。

更正后的顺序是：

1. 先完成 BFCL 唯一 call-order 桥。
2. 若 D 最终 STOP，不直接执行第17.7--17.9节的 AgentDojo 旧计划；先做新方向 Gate0 重定义。
3. 新 RQ 必须与 Task Shield/IPIGuard 逐项比较任务、online input、机制、Gold、干预对象和外测，至少在一项上形成实质新问题，不能只改名。
4. 无法找到 3--5 篇合格核心论文、每章至少一篇直接 CCF A Full/Regular 站台、两个独立可执行 Gold 和非循环桥，则整个安全/授权问题簇 STOP，重新选题。

# 18. 按2026正式论文再次改向：三组候选与新的首选数据 Gate

> 本节覆盖此前“D 失败后优先 AgentDojo 动态授权”的顺序。GPT 提出的方向可随时删除；唯一最高约束是《研究生毕设选题、调研与实验统一要求》。当前仍是 **0 个方向两章 GO**。

## 18.1 三组候选的新排序

| 排名 | 候选组 | 两章关系 | 关键正式论文 | 当前阻塞 |
|---:|---|---|---|---|
| 1 | Agent 系统真实 issue 定位与可执行修复 | Agent 架构证据的 OOF file/function 定位 -> 定位约束下的 patch 生成与无回归验证 | NeurIPS 2025 Main `Can Agent Fix Agent Issues?`；ICLR 2026 `Improving Code Localization with Repository Memory`；NeurIPS 2025 Main `Self-Challenging Language Model Agents`、`STRATUS` | 必须先证明50个任务有严格 issue/buggy/patch/location/test/image join、足够独立样本和可复现 Docker Gold；修复阶段还缺同模型公平执行条件 |
| 2 | 长程 Agent 证据保真上下文与风险触发恢复 | 可执行约束/证据保真的 context state -> OOF 丢证据风险触发 restore/replay/replan | ICLR 2026 Sculptor、MEM1；ACL 2026 Long COMPASS、FS-Researcher、GTA | 已有工作已覆盖 summary/fold/restore/context manager；若不能增加程序化 process fidelity Gold，就只是重复/摘要优化 |
| 3 | 动态工具可靠性估计与自适应恢复 | OOF tool transition/failure risk -> retry/alternative/dependency repair/backtrack/safe stop | ICLR 2025 ToolEVO、WMA；ICLR 2026 ReIn、ResiliBench；EMNLP 2025 Main BacktrackAgent | ToolEVO需A100；多方法依赖API；ResiliBench为构造环境，不能作唯一证据；2026直接重叠尚需继续检索 |

旧记忆方向不因出现新论文自动复活。ACL 2026 `How Memory Management Impacts LLM Agents` 已直接覆盖 memory addition/deletion、future-evaluation quality、error propagation、misaligned replay 和 distribution shift；ICLR 2026 AMemGym 已覆盖 on-policy Write/Read/Utilization 诊断。若新设想仍只是 entry 质量打分或增删策略，就与新论文重叠并保持 STOP。

## 18.2 为什么首选改为 AgentIssue-Bench

[Can Agent Fix Agent Issues?](https://proceedings.neurips.cc/paper_files/paper/2025/hash/45f0ab2d264a057113492b35c5ef47f2-Abstract-Conference.html) 是 NeurIPS 2025 Main Conference 正式论文。它分析201个真实 Agent 系统 issue，并发布50个可复现 issue-resolution tasks。每个任务带真实 issue、buggy/fixed repository state、developer patch、failure-triggering tests 和 Docker 环境；[官方仓库](https://github.com/alfin06/AgentIssue-Bench) 为 MIT 许可证，还保存 Agentless、AutoCodeRover、SWE-agent 在 GPT-4o/Claude-3.5 上的生成 patch。

这与旧 DevAI 的关键区别不是“数据集更新”，而是 Gold 形态改变：旧路线365条 requirement 中独立 requirement-to-evidence mapping 为0；新资产理论上可以由 developer patch 与失败触发测试建立 `issue -> failed behavior -> changed location -> executable fix`。但“理论上可以”不等于已经通过，本地必须先做严格 join 和 Gold census。

## 18.3 候选题目和两章

暂定题目：

> **《面向智能体系统的软件问题定位与可执行修复方法研究》**

第一章：**Agent 架构证据约束的问题定位**。

- 输入：issue、buggy repo、失败测试输出、静态依赖和 Agent component roles。
- 输出：file/function Top-K、责任组件类别、test-to-location evidence chain。
- 三模块：Agent 组件语义映射；repository evolution memory；失败测试证据接地。
- 独立主指标：task-level function/file MRR（优先 function MRR）；辅助 Top-K、developer-patch coverage、evidence coverage。
- 主要 baseline：BM25/stack trace；同信息 Agentless localization；ICLR 2026 Repository Memory；另一个近年直接 localization baseline，总数不超过5。

第二章：**OOF 定位引导的测试约束修复与 Transactional No-Regression**。

- 输入只允许第一章 task-level OOF Top-K/evidence；禁止 developer-location Gold。
- 输出可应用 patch 与验证证据。
- 三模块：证据约束 patch context；verification-function 候选修复；failure flip + pass-to-pass 的 transactional sandbox。
- 独立主指标：task resolution rate；辅助 fail-to-pass、pass-to-pass、patch scope、执行次数和成本。
- 桥接：`No localization / Random / Shuffled OOF / OOF Predicted / Oracle developer locations`。Oracle仅信息上界；Predicted不过则两章关系 STOP。

创新不能写成“把 Repository Memory 搬到新 benchmark”。必须证明 Agent-specific component semantics 或 test dependency evidence 在真实 Agent issue 上提供独立增量，并报告在哪些 prompt/config/model adapter/tool schema/orchestration issue 类别有效或失败。

## 18.4 AgentIssue Gate0/1 预注册

Gate0（不先运行代码模型）：

1. 锁官方 repo commit、50个 Docker tags、issue/buggy/fixed/test/patch SHA 与许可证。
2. 建立严格 join：`issue -> buggy commit -> developer patch -> changed file/function -> failure-triggering test -> image tag`。
3. 至少40/50有稳定 file-set Gold，至少30/50有 function/等价语义单元 Gold；不足则第一章 STOP。
4. 按 repository + issue family + patch structure 分组；同repo和相似patch模板不得跨train/test。
5. 201 issue 只能作训练/分析补充；没有 executable test 的条目不能混入第二章主表。
6. 统计独立任务功效；若结构去重后的测试任务少于20，或10%预注册门在50任务上明显不可检验，则整方向 STOP。

只读 registry 预检已得到：官方 repo HEAD 为 `1d498dec35e347c4e7b9e1c318ef28fc5fa97318`；论文主集由 `pull_images.py` 冻结为50个 tag，Docker Hub 现有85个 tag，后续扩展不能混入论文主表。50个主 tag 全部存在，压缩层合计约28.58 GiB；14个仅 `linux/arm64`，36个仅 `linux/amd64`。官方 `test_agentissue_bench.py` 会先强制删除本机全部 Docker images，并交互收集 OpenAI/Google/search keys，因此禁止直接运行；必须自建单-tag、非破坏、无上传 wrapper。

Gate1（环境与 Gold 复现，不生成新 patch）：

1. SHA-256冻结5个跨仓库、跨架构试点，逐个拉取单一 image；先用arm64原生样本，再单独验证amd64模拟执行；禁止官方 all-tag 下载/删除脚本。
2. buggy failure test 必须5/5复现；developer patch 后必须5/5 fail-to-pass，且已有 pass tests 不回归。
3. 任一 issue/image/repo/patch 版本错配判 `INVALID_ASSET_JOIN`，只修资产链，不计“实验失败次数”。
4. 试点通过后扩到全部合格任务，fresh container 双运行一致，0 harness error。
5. Gate1 GO 只表示数据可用；之后第一章和第二章仍分别要相对冻结最强公平 baseline 提升至少10%，task-level paired bootstrap 95% CI lower >0。

## 18.5 成本与强 baseline 限制

当前机器是16GB Apple Silicon，Docker已经可用，磁盘余量可支撑先做单 tag probe；可执行静态分析、镜像 replay 和小模型探针，但不能假定能等价复现 A100 训练或 GPT-4o/Claude。当前环境未发现现成模型 API key。

因此第一轮只做不用新模型的资产/Gold Gate。官方 Agentless/AutoCodeRover/SWE-agent patch 可用于外部基线审计；若无法以同模型、同预算重跑，它们不能与本方法组成严格配对主表。进入正式修复 Gate 前，外部 GPT 必须判断以下任一方案是否公平：

1. 用户提供冻结 API/model budget，所有 arm 同模型同调用预算；
2. 本地可运行同一开源代码模型，所有 arm 共享权重、上下文和执行预算；
3. 只研究定位章节，并另找不需新生成的第二个独立任务。若第三种导致两章失去真实关系，则方向 STOP。

## 18.6 给外部 GPT 的独立审阅问题

1. AgentIssue-Bench 的50任务能否支撑 function/file localization 的独立章节，还是多文件 patch 与小样本使 Gold/统计功效不足？
2. `Agent component semantics + repository memory + failing-test grounding` 是否有实质机制增量，还是普通 SWE localization 的组合包装？
3. 第二章如何在不泄漏 developer patch/location 的前提下，用第一章 OOF 定位公平改善修复？
4. 50任务上10%相对增益与 paired bootstrap CI lower>0 的最小可检测效应如何；是否必须增加同定义的真实 Agent issue 外测？
5. 官方生成 patches 能否用于冻结 baseline，而不与新模型 arm产生模型/预算不公平？若不能，最低成本的同模型重跑合同是什么？

当前最新执行顺序：BFCL 唯一 call-order 桥已经完成并严格 STOP。119,960个非原顺序排列在Gold前冻结，No=75/120、SchemaDependencyOrder=73/120、Oracle=75/120、净救回0、相对提升0、paired bootstrap 95% CI=[0,0]；全候选正逆/固定shuffle一致，fresh subprocess 6129/6129一致，0 harness error。故D第二章永久STOP，不再增加第五个局部operator。

AgentIssue资产/Gold Gate0已经完成。50个主tag全部存在，表格与tag/reference为50/50；但官方checkout只有44/50能唯一连接patch/test记录。patch-only file Gold为43/50、code-hunk/line-range region Gold为32/50，strict named-function Gold仅26/50。44个匹配记录的instance/repo/base/setup一致，但test_patch仅43/44非空，FAIL_TO_PASS列表0/44非空；镜像可能用自带`test_buggy/test_fixed`脚本补足执行证据，但这尚未实测。按同repo和当前粗结构连通分组后，file候选只能形成42 test/1 train，region候选31 test/1 train，无法满足双方至少20条。因此原“function localization”版本严格STOP；只有把第一章改为file+code-region时保留`CONDITIONAL_ASSET_BLOCKED`，不能把32条region冒充function Gold。

AgentIssue最小Docker Gate1已经完成。冻结索引29、15、19、48、28的5个镜像均可pull/inspect，OS/architecture/digest匹配5/5，buggy与fixed均完成双重放；但预注册统一标准标记的fail-to-pass合格数为0/5，arm64对照index48没有唯一commit pair且diff仅header，部分镜像还因断网依赖安装使fixed退出码不能统一解释。Phase A严格合格0/5，因此未执行Phase B。逐镜像新增regex、联网或重定义成功条件属于后验Harness适配，禁止。

结合Gate0的function Gold 26/50、file/region无泄漏split仅42/1与31/1，候选组一正式裁决`STOP_ASSET_AND_POWER`，不进入模型、定位或修复实验。它是资产/任务资格失败，不计入“同一冻结目标三次实质方法设计失败”，也不触发Sol方法复审。当前转候选组二“长程Agent证据保真上下文与风险触发恢复”Gate0。

## 18.7 候选2/3 Gate0实测后的再裁决

候选2已经完成实验51只读Gate0并裁决`REJECTED_OVERLAP`。OCR-Memory（ACL 2026 Long）已做visual anchor、外部日志逐字确定性恢复和active recall；CoMem（ICML 2026）已用action-consistency优化压缩后的functional equivalence；SUPO（ACL 2026 Long）已端到端联合优化tool-use summary与Agent policy；Sculptor已有可逆fragment/fold/summary/hide/restore/search。原设想若再加provenance verifier或risk trigger，仍只是现有机制的编排包装。

资产层同样未过：MEM1 demo 1000行与CoMem BrowseComp 128行均不含完整`constraint -> tool/source anchor -> transform -> executable outcome`链。严格合格独立任务、held-out、process-fidelity Gold、冻结无模型replay链和自然外测均为0。因此候选2不进入模型/API Gate1，且本次资格失败不计方法设计失败次数。

候选3完成实验52只读Gate0，暂为`CONDITIONAL_ASSET_BLOCKED`而非GO。ResiliBench、ToolEVO、WMA、OpenApps提供四类候选资产，但当前next-call failure Gold 0/30、recovery Gold 0/30、held-out 0/20、离线replay 0/1、自然外测0/1。OpenApps虽然可单CPU且state/reward透明，但UI variation不是随机tool failure；ResiliBench虽有5040任务/30 API/五类参数化错误，核心文件目前为Git-LFS pointer且构造数据不能作唯一证据。

同时，ICLR 2026 `Do Large Language Models Know What They Are Capable Of?`已覆盖多步Agent执行中在线成功概率更新与有失败成本的continue决策。候选3只有在“executor-derived、失败前、dependency-conditioned的next-call风险”能提供该工作没有的信息，并在自然Agent资产上改善恢复时才有增量；换分类器、校准器或成本权重直接`REJECTED_OVERLAP`。

实验53已完成这一次无模型/无API的有界资产Gate1。ResiliBench的11个LFS pointer合计483,073,122 B，超冻结250 MiB上限，故payload未下载；WMA 80行样例与ToolEVO数据都没有executor failure/recovery Gold；OpenApps state/reward无模型双运行通过，但没有自然tool-failure trajectory。六项硬门最终均为0，Phase B未运行，候选3正式`STOP_ASSET`。这是资产失败，不计方法失败。

## 18.8 已完成的新资产 Gate：EXP-Bench 与 Gaia2

> **收尾状态（2026-08-21）**：以下资产/重叠审计已完成，两者均`STOP_ASSET`，不是方法实验失败，更不是两章GO。

### 候选4：EXP-Bench科研Agent实验过程验证与执行恢复

- 核心资产：[EXP-Bench，ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/c411f5b2d9c55f1685e72db224ad8b0e-Abstract-Conference.html)，论文报告461个科研实验任务、51篇顶级论文，完整可执行实验成功率仅0.5%。
- 第一章候选：将研究问题、starter code、公开trace、过程规范与产物映射为可验证milestone/evidence状态。
- 第二章候选：只消费第一章任务级OOF证据，选择最小修复、依赖重跑或安全停止，以真实执行成功与无回归为结果。
- 必杀门：至少100个非LLM judge的程序化过程Gold、50个可执行失败—修复结果、40 held-out/至少10篇论文分组切分、无模型CPU重放和两类论文/任务family。任一不成立即`STOP_ASSET`。
- 实测裁决：官方规模声称461 tasks、51 papers、12,737 subtasks，但本地starter repo、trace-like文件、程序化milestone/evidence Gold、failure→repair/rerun Gold、冻结trace→artifact→test→outcome链和CPU无API smoke均为0。文本design/expected_outcome与LLM judge不计Gold。实验54裁决`STOP_ASSET`。

### 候选5：Gaia2等价过程验证与依赖感知局部恢复

- 核心资产：[Gaia2，ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/file/c26a67e0470774df98c12480ec5d2d7b-Paper-Conference.pdf)与官方 [ARE](https://github.com/facebookresearch/meta-agents-research-environments)。官方文档报告800个场景、10个universe、11个应用，包含动态事件、write-action DAG、parent/timing约束和程序化验证。数量仍须以实际数据文件核对。
- 明确研究缺口：论文的ARE verifier显式假设没有等价write action，合法替代应用/动作可能被错判。
- 第一章候选：依赖偏序、状态效果等价和时序一致性联合的过程验证；必须有独立Gold评价，不能用官方verifier自证。
- 第二章候选：用第一章任务级OOF输出计算失效依赖闭包、选择checkpoint与最小重放/替代/安全停止。
- 必杀门：至少100个可解析外部场景，60条独立等价/非等价过程Gold（至少20条公开自然Agent轨迹），40个可执行失败—恢复结果，按universe/scenario/template分组的held-out，一个无模型双重放和一个非Oracle变体自然外测。
- 实测裁决：160/160 mini场景和action DAG可解析，含1,042 OracleEvent和179环境事件；结构parser无模型双digest一致。但独立等价Gold 0/60、公开真实Agent轨迹0/20、failure→repair 0/40、held-out 0/20、自然外测0/1。Oracle/verifier不能自证，实验55裁决`STOP_ASSET`。

### 下一候选队列（未运行，非结论）

[ImpossibleBench，ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/ca688eb14e29701a11bdba6633186328-Abstract-Conference.html)公开了可执行的“测试通过但违反规格”Agent行为，可能支撑“规格—测试冲突的过程识别→评测Harness强化”。但论文自身已覆盖作弊率、行为分析、context engineering和monitoring testbed，目前只作排队候选，不自动启动。新对话应将它与其他论文配对一起独立排名，不得因为已写入本文就默认它是下一方向。

## 18.9 用户新决策：两论文复现优先的1+1路线

下一轮不直接从庞大两章合同开始，也不将完整外测、大样本Gold和两章关系全部当作第一次pilot入口。新顺序是：

1. 先从2025--2026 CCF A正式Agent论文的limitations、failure analysis和future work中选3--5组两论文配对，不被GPT旧方向绑定。
2. 优先代码、数据、许可完整，且能在16GB Apple Silicon + Docker或小额可控API上复现的一组。
3. 先分别复现论文P和Q的一个官方主结果，不加自研模块。
4. 两篇均复现成功后，从P取模块A、从Q取模块B，做仅含两个核心模块的`Base / A / B / A+B`小实验。
5. 先证明一个模块有稳定正增量，再证明第二模块有额外价值。若无效，替换论文模块，不堆第三个模块。
6. 两模块pilot有效后，再进入正式两章设计、强baseline、分组OOF、10%增益、95% CI下界>0和真实外测。

这是对实验进入顺序的放松，不是对最终毕设科研标准的放松。每章两个核心模块已经足够；复现本身不算创新贡献，但它是后续组合设计的必要可行性基础。

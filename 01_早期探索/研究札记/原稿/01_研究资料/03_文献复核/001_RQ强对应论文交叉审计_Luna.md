# 两个核心 RQ 的近三年 CCF B+ 强对应论文交叉审计

> 执行线程：Luna/max
>
> 审计日期：2026-08-23
>
> 基础提交：`main @ 06bca58e3602f599a280ed8e3772993072fad6c6`
>
> 口径：正式论文、2024—2026、CCF 第七版（2026-03-31 发布）B 及以上；会议论文只把 Full / Regular / Long 作为核心计数。Findings、Workshop、Demo、Short、Datasets & Benchmarks Track、预印本不冒充核心论文。

## 1. 先给结论

当前两个 RQ 的文献证据强度不对称：

| RQ | 严格问题定义 | 近三年 CCF B+、正式论文的强对应数量 | 结论 |
|---|---|---:|---|
| RQ1 | 已失败的 Agent/MAS 轨迹中定位责任 Agent、决定性步骤或根因步骤 | **6** | 文献站台充分，可以证明该问题已被主流 Agent 研究作为完整任务提出；其中至少 5 篇是 CCF A 正式论文 |
| RQ2（当前原文） | 面对不同失败样本，自适应选择诊断/归因/回退策略，以提高失败归因可靠性 | **0 篇“全文完全同题”**；有 6 篇“自适应失败处理/可靠性”结构同题 | 不能把当前 RQ2 直接写成已有成熟“选择性归因路由”问题；但做一次最小问题重述后，已有足够的 Agent 可靠性/失败处理文献支持 |

这里的“0”不是说 RQ2 没有价值，而是严格遵守“整篇论文的核心问题、任务和结论必须同类”后的结果：我没有发现一篇近三年 CCF B+ 正式论文把“对每个失败样本选择哪一种归因器/回退归因器，并以归因质量为目标”作为全文主问题。现有论文主要研究的是风险感知的 Agent 状态选择、故障检测—诊断—缓解闭环、错误检测后的回退或恢复，而不是“归因器之间的样本级选择”。

因此，建议主线程在开题报告中把两种证据分开写：

1. **RQ1 可直接按当前标题开题。** `Who&When`、`StepFinder`、`Scope Delineation`、`FLKR`、`TraceElephant`、`AgenTracer` 已经分别从问题定义、步骤定位、长轨迹/全观测、代码生成 MAS 和自动化标注/反馈等角度直接证明该问题通用且必要。
2. **RQ2 若保留现有 Exp108，需要最小重述为“样本异质性下的自适应失败诊断与处置/回退策略选择”。** 现有 Exp108 的 OOF utility forest 可以作为这个更大问题的一种实现；但不能声称已有文献已经直接证明“归因器路由”本身。
3. **若导师坚持 RQ2 必须是“失败归因可靠性选择”原句，当前文献不能给出 5 篇强对应论文。** 最小诚实结论应是 RQ2 文献 Gate 未过，不能用 BEST-Route 等纯 LLM 路由论文凑数。

## 2. 审计与 CCF 核验口径

### 2.1 要求文件中的硬约束

已完整重读 `/Users/peroyang/My/MyWork/研究生毕设选题实验可行性探索要求.md`（584 行）以及当前报告 `开题/当前主线/开题设想03_责任步骤级联定位与效用感知选择性归因_两章开题GO.md`（307 行）。本次审计特别遵循以下条款：

- 每个核心研究问题必须有至少一篇论文，其全文主要研究方向、任务和结论与该问题一致；
- 核心论文优先为 2025—2026 CCF A 正式 Full / Regular / Long，主要 baseline 至少 CCF B；
- Findings、Workshop、Demo、Short、Datasets & Benchmarks Track 可作补充，不得冒充核心；
- 第一章和第二章必须分别独立成立，不能只把一个任务拆成两张表；
- “只做成本、Token 或路由优化且缺乏更大的 Agent 研究目的”不接受；
- 第二章若使用第一章输出，必须使用严格 OOF / 样本外输出，不能使用 Gold 或 Oracle 代替预测产出。

用户新增澄清是：研究现状论文的方法可以与本项目完全不同，核心是证明“这种研究问题”已被主流研究认可。因此本审计不要求论文复现秩深度级联、ExtraTrees 或 OOF forest；只要求论文的研究对象、输入输出和主要结论与 RQ 的问题层级同类。

### 2.2 CCF 版本与正式论文类型

使用的 CCF 依据为：[CCF 第七版目录正式发布公告](https://www.ccf.org.cn/Academic_Evaluation/By_category/)（2026-03-31）及其分领域目录：[人工智能目录](https://www.ccf.org.cn/Academic_Evaluation/AI/)、[数据库/数据挖掘/内容检索目录](https://www.ccf.org.cn/Academic_Evaluation/DM_CS/)。CCF 公告明确说明：会议论文只把 Full paper 或 Regular paper 纳入目录，Short、Demo、Technical Brief、Summary、Findings 和 Workshop 不计入目录。

本报告使用的 venue 级别如下：

- CCF A：AAAI、NeurIPS、ACL、ICML、ICLR、SIGKDD；
- CCF B：EMNLP、AAMAS、UAI 等；
- EACL 不在本版 CCF B+ 目录中，EACL 论文只能列为补充，不能计入严格数量；
- 论文级别不由 venue 自动保证，仍需核对正式 track 和 paper type。2026 年的 ACL Long、AAAI Technical Track、ICLR Main、KDD Proceedings 研究论文按正式长文处理；Findings / D&B 单列。

### 2.3 四级对应标签

- **强**：论文全文把同一个 Agent 问题当作主任务，且主要实验结论直接证明该问题存在、困难或需要解决。
- **中**：研究对象和可靠性问题相同或高度相邻，但输出任务不同，或没有样本级策略选择；可支撑“方向/问题家族存在”，不能直接支撑当前公式化 RQ。
- **弱**：只提供一个模块、基准、观察或通用方法；不能作为该 RQ 的方向站台。
- **不计入**：预印本、Findings、Workshop、D&B、Demo、非正式页面，或全文研究目的明显不是该 Agent 问题。

## 3. RQ1：Agent/MAS 失败责任主体或关键步骤定位

### 3.1 当前 RQ1 的问题边界

当前 RQ1 是：

> 给定已经失败的 Agent/MAS 执行轨迹，在不读取 Gold 责任标签的条件下，定位负责失败的 Agent、决定性步骤、根因步骤或最早不可恢复步骤，并可输出步骤级排序。

该表述不限定是监督分类、LLM 推理、图分析、反事实重放还是时序模型；`责任 Agent/关键步骤定位` 是问题核心。按此标准，近三年已有至少 6 篇 CCF A 正式论文直接研究该问题。

### 3.2 强对应核心论文（严格计数 6）

| 论文（年份） | 正式 venue / track | CCF | 全文主要任务与结论 | 与当前 RQ1 的强对应理由 | 计数 |
|---|---|---|---|---|---|
| [Which Agent Causes Task Failures and When? On Automated Failure Attribution of LLM Multi-Agent Systems](https://proceedings.mlr.press/v267/zhang25cq.html)（Zhang et al., 2025） | ICML 2025 Main，PMLR 267:76583–76599 | A | 正式提出并定义 automated failure attribution；构建包含 127 个 MAS 的 Who&When，标注责任 Agent 与 decisive error step；实验显示最佳 Agent-level accuracy 53.5%，Step-level 仅 14.2%，部分方法低于随机，SOTA reasoning model 也不可用。 | 这是与 RQ1 几乎同义的完整问题定义、数据、指标和结论；同时直接证明责任步骤定位不是轻易可由通用 LLM 解决的小模块。 | **强** |
| [StepFinder: A Temporal Semantic Framework for Failure Attribution in Multi-Agent Systems](https://doi.org/10.1145/3770855.3817991)（Zhu et al., 2026） | KDD 2026 Proceedings V.2，研究论文，12 页 | A | 把 MAS failure attribution 作为完整任务，输入失败执行日志，输出 root-cause step；用 temporal semantic sequence、agent-aware interaction 和 step-level error scoring 做步骤定位，在 Who&When 上超过 LLM 和时序基线，并报告显著推理效率优势。 | 全文目标就是失败步骤归因/根因步骤定位；方法虽与本项目不同，但任务、输出和“失败轨迹中找责任步骤”的结论完全同类。 | **强** |
| [Scope Delineation Before Localization: A Two-Stage Framework for Enhancing Failure Attribution in Multi-Agent Systems](https://ojs.aaai.org/index.php/AAAI/article/view/40594)（Sun et al., 2026） | AAAI-26 Technical Track on NLP IV | A | 将 MAS 失败归因分成先识别 failure scope、再 pinpoint failure step 的两阶段任务；在 Who&When 上验证，step-level accuracy 最多提高 24.27%。 | 全文问题不是借用了 scope module，而是直接研究“如何定位 MAS 的责任步骤”；并且结论证明结构化/分阶段定位本身是必要方向。 | **强** |
| [Failure Localization in Multi-Agent Code Generation via Knowledge-Guided and Transferable Reasoning](https://ojs.aaai.org/index.php/AAAI/article/view/36993)（Geng et al., 2026） | AAAI-26 Technical Track on Application Domains I | A | 研究多 Agent 代码生成的 fine-grained failure localization；建立 COFL 专家标注 benchmark，提出 FLKR，报告相对 prompting 方法最多 14 个百分点的 Fault Localization Accuracy 和最多 45 个百分点的 Top-1 accuracy 提升，并在 divergent / real-world / refinement-critical 情形泛化。 | 虽场景限定代码生成，但全文主问题仍是多 Agent 失败定位和责任信号，而不是把定位当作修复系统的小模块；证明 RQ1 在另一类 Agent 任务中同样成立。 | **强** |
| [Seeing the Whole Elephant: A Benchmark for Failure Attribution in LLM-based Multi-Agent Systems](https://aclanthology.org/2026.acl-long.912/)（Chen et al., 2026） | ACL 2026 Volume 1 Long Papers | A | 定义 Agent-level responsible component 与 step-level decisive failure step；发布 TraceElephant 全可观测执行轨迹和可复现环境；报告完整 trace 相对于 output-only trace 可使 step attribution accuracy 提高约 76.5%，并发现 step-level 对缺失上下文更敏感。 | 全文以 failure attribution 作为 benchmark 主问题，且结论直接说明“责任步骤定位需要完整过程证据”，为本项目用 trace 结构做步骤排序提供了问题级依据。 | **强** |
| [AgenTracer: Who Is Inducing Failure in the LLM Agentic Systems?](https://iclr.cc/virtual/2026/poster/10007726)（Zhang et al., 2026） | ICLR 2026 Main / Poster | A | 将 agentic failure attribution 定义为在长轨迹中定位责任 Agent 或步骤；用 counterfactual replay + programmed fault injection 构建 TracerTraj，再训练 AgenTracer-8B；在 Who&When 上超过大型闭源模型，并把归因反馈用于 MetaGPT / MaAS 自我改进。 | 全文研究目标是自动化 Agent failure attribution，既定位 Agent 又定位 decisive step，并以可执行反馈说明归因结果的系统价值；与 RQ1 的问题级对应非常直接。 | **强** |

**RQ1 严格计数：6。** 其中 `Who&When` 是 ICML A 的问题奠基论文，`StepFinder` 是 KDD A 的步骤归因论文，`Scope Delineation` 与 `FLKR` 是 AAAI A 的两种不同场景/方法，`TraceElephant` 是 ACL A 的全观测 benchmark，`AgenTracer` 是 ICLR A 的反事实标注与自动归因。已经远超“至少 5 篇”的要求，且至少一篇（实际上多篇）全文主问题与 RQ1 一致。

### 3.3 RQ1 直接但不进入严格计数的补充论文

| 论文 | 正式身份 | 对 RQ1 的帮助 | 为什么不计入核心 |
|---|---|---|---|
| [RAFFLES: Reasoning-based Attribution of Faults for LLM Systems](https://aclanthology.org/2026.eacl-long.359/) | EACL 2026 Long | 在 Who&When 上做 step-level fault attribution，并在数学推理等任务测试故障诊断，说明问题具有跨任务外延。 | EACL 不在当前 CCF 第七版 B+ 目录中，故不得进入严格 CCF 计数。 |
| [Towards Self-Improving Error Diagnosis in Multi-Agent Systems](https://aclanthology.org/2026.findings-acl.98/) | Findings of ACL 2026 | ErrorProbe 全文研究责任 Agent 与 originating error step，并利用可执行证据更新 episodic memory；问题高度直接。 | Findings 明确不计入 CCF 会议目录，只作前沿补充。 |
| [Who is Introducing the Failure? Automatically Attributing Failures of Multi-Agent Systems via Spectrum Analysis](https://arxiv.org/abs/2509.13782) | arXiv 2025 | FAMAS 用多次轨迹 replay 和 spectrum analysis 估计 Agent action 的责任概率，全文研究失败归因。 | 截至审计日只核验到 arXiv，未核验正式 CCF B+ venue。 |
| [GraphTracer: Graph-Guided Failure Tracing in LLM Agents for Robust Multi-Turn Deep Search](https://arxiv.org/abs/2510.10581) | arXiv 2025 | 用 information dependency graph 区分症状与根因，直接处理多 Agent 错误传播。 | 未核验正式 CCF B+ venue；不可当作核心论文计数。 |

### 3.4 RQ1 的必要性结论

RQ1 的文献不仅说明“有人做过”，而且形成了互相独立的必要性证据：

- `Who&When` 说明通用 reasoning model 的 step-level attribution 仍很低，任务本身困难且需要专门研究；
- `StepFinder`、`Scope Delineation`、`FLKR` 说明时序、scope、知识/行为编码等不同机制都被用来解决同一个完整问题；
- `TraceElephant` 说明可观测输入是否完整会显著改变责任步骤定位，证明 trace 组织不是实现细节；
- `AgenTracer` 说明通过反事实重放产生责任标签并把归因反馈给 Agent，进一步证明该任务对 Agent 调试和改进有实际闭环价值。

因此，RQ1 可以在开题报告第一章“研究现状”中明确写成一个已经被 ICML/KDD/AAAI/ACL/ICLR 多个 CCF A 正式论文共同确认的 AgentOps/Agent reliability 研究问题，而不是把当前实验中的秩深度级联包装成论文界尚不存在的细节。

## 4. RQ2：样本级自适应诊断/归因/回退策略选择

### 4.1 必须先区分两个层次

当前报告里的 RQ2 是：

> 给定 RQ1 的严格 OOF 排序和 Gold-free 轨迹特征，预测本条失败轨迹中 RQ1 相对 recency 的效用，逐样本选择使用 RQ1 或回退 recency，以提高最终责任排序可靠性。

这是一个有清楚实验定义的“选择性归因/路由”问题，但它比一般的 Agent 失败处理问题更窄。文献中可以区分：

1. **全文完全同题**：论文的主要研究问题就是“对不同失败样本选择不同归因器/诊断策略，以提高归因质量”。本次严格检索结果为 0。
2. **问题结构同题**：论文全文研究“根据风险/异常/冲突状态选择或执行不同的 Agent 诊断、隔离、回退、恢复策略，以提高系统可靠性”。这类论文有至少 6 篇 CCF B+ 正式论文。它们可以支持 RQ2 的最小重述，但不能被写成已经直接提出了当前的 OOF utility routing。
3. **只有方法同题**：通用 LLM model routing / cascading 根据质量、置信度或成本选择模型；这类论文只能作为方法来源，不能证明 Agent 失败归因路由这一研究问题。

用户已明确“研究现状论文的方法可以不同”，所以第 2 类可以作为重述后 RQ2 的方向站台；但必须在报告中注明它们支撑的是“自适应失败处理/可靠性策略选择”这一问题家族，而不是当前具体的归因器路由公式。

### 4.2 RQ2 问题结构同题的正式论文（重述后可用）

以下论文全部是 2024—2026 的正式 CCF B+ 主会长文；它们不要求使用本项目方法，但全文主问题都是 Agent 失败时如何检测、选择状态、诊断、阻断、回退或恢复。

| 论文（年份） | 正式 venue / track | CCF | 全文主要任务与主要结论 | 与当前 RQ2 的对应层级 | 计入判断 |
|---|---|---|---|---|---|
| [Taming “Zombie” Agents: A Markov State-Aware Framework for Resilient Multi-Agent Evolution](https://aclanthology.org/2026.acl-long.373/)（Zhang et al., 2026） | ACL 2026 Volume 1 Long Papers | A | 研究多 Agent 协作中的暂时失效/幻觉风险；用 risk estimator 动态把 Agent 置为 Active、Standby 或 Terminated，并按状态选择传播边；结论是软状态转换既保留可恢复 Agent，又降低不可靠节点影响，在多类任务中优于强基线。 | “根据每个样本/Agent 的风险选择继续、观察或隔离策略”与 RQ2 的样本异质性和安全回退结构同题；输出不是责任排序，因此不是当前 RQ2 的全文同题。 | **中（重述后强）** |
| [STRATUS: A Multi-agent System for Autonomous Reliability Engineering of Modern Clouds](https://proceedings.neurips.cc/paper_files/paper/2025/hash/47a6e9e2c3019f13ad94a0f259fe4970-Abstract-Conference.html)（Chen et al., 2025） | NeurIPS 2025 Main Conference | A | 研究云服务中的 Agentic SRE；将 failure detection、diagnosis、mitigation 组织成状态机，提出 Transactional No-Regression 约束，结论是可安全探索并把 AIOpsLab/ITBench 的 failure mitigation 成功率提升至少 1.5 倍。 | 全文目标是根据运行失败状态选择可靠的检测—诊断—缓解流程，证明 Agent 可靠性策略选择是独立问题；但它不比较不同 attribution ranker，也不以 attribution MRR 为目标。 | **中（重述后强）** |
| [On the Resilience of LLM-Based Multi-Agent Collaboration with Faulty Agents](https://proceedings.mlr.press/v267/huang25ay.html)（Huang et al., 2025） | ICML 2025 Main，PMLR 267:26202–26226 | A | 系统研究 faulty/clumsy/malicious agents 对协作结构的影响；比较多种拓扑并发现 hierarchical 结构性能下降最低（5.5%），再用 Challenger 和 Inspector 检查、纠正消息，最多恢复 96.4% 的错误。 | 全文主问题是失败 Agent 下的防御/恢复策略，而非成本路由；说明不同失败结构需要不同的诊断或防御策略。没有显式做按样本选择 attribution method，因此是结构同题。 | **中（重述后强）** |
| [BacktrackAgent: Enhancing GUI Agent with Error Detection and Backtracking Mechanism](https://aclanthology.org/2025.emnlp-main.212/)（Wu et al., 2025） | EMNLP 2025 Main | B | 研究长程 GUI Agent 的错误检测与恢复；以 verifier、judger、reflector 发现错误并触发 backtracking，结论是在 Mobile3M 和 Auto-UI 上提高 task success 与 step accuracy。 | 全文主问题就是 Agent 执行失败后的检测与回退，证明“失败后是否继续、回退还是修正”是完整 Agent 研究问题；但它采用固定机制，不做不同归因器间的选择。 | **中（重述后强）** |
| [ReAgent: Reversible Multi-Agent Reasoning for Knowledge-Enhanced Multi-Hop QA](https://aclanthology.org/2025.emnlp-main.202/)（Zhao et al., 2025） | EMNLP 2025 Main | B | 研究多 Agent/多跳推理中的早期错误传播；当发现冲突时回退到此前有效状态，采用 local/global rollback，三类 QA benchmark 相对 forward-only 约提升 6%。 | 全文主问题是错误发现后的可逆推理和回退策略，说明 recovery/fallback 不是工程附属功能；但其回退协议固定，且目标是 QA 成功率而非失败归因可靠性。 | **中（重述后强）** |
| [SyncMind: Measuring Agent Out-of-Sync Recovery in Collaborative Software Engineering](https://proceedings.mlr.press/v267/guo25l.html)（Guo et al., 2025） | ICML 2025 Main，PMLR 267:20993–21066 | A | 定义协作软件工程中的 out-of-sync failure，构建 24,332 个真实仓库场景和可执行测试，系统测量 Agent 恢复；结论是协作行为与 recovery success 正相关，而现有 Agent 缺乏 resource awareness 和 adaptability。 | 全文把“不同运行状态下如何恢复以及是否具备自适应能力”作为主问题，证明 Agent 失败恢复具有通用研究价值；它是 recovery benchmark，不是 attribution-router 论文。 | **中（重述后中/强）** |
| [Resilience in Ambient Multi-Agent LLMs via Decentralized Bio-Autonomic Control and Immune-Inspired Anomaly Detection](https://ojs.aaai.org/index.php/AAAI/article/view/41065)（Darabi et al., 2026） | AAAI-26 Special Track on AI Alignment | A | 研究多 Agent LLM 的 Monitor–Analyze–Plan–Execute 自主控制环，结合 anomaly detection、trust 和 fault isolation，结论是可以提高 resilience/recovery。 | 全文研究的是异常状态下的监测、隔离和自适应恢复，和广义 RQ2 同题；但架构较宏观，未对失败归因质量或样本级路由作严格实验，建议只作补充结构证据。 | **中/弱** |
| [Can Agent Fix Agent Issues?](https://proceedings.neurips.cc/paper_files/paper/2025/hash/45f0ab2d264a057113492b35c5ef47f2-Abstract-Conference.html)（Rahardja et al., 2025） | NeurIPS 2025 Main Conference | A | 构建 AgentIssue-bench，分析 201 个真实 Agent issue，50 个带失败触发测试的可执行修复任务；现有 SE Agent 解决率仅 0.67%—4.67%，证明 Agent 系统维护/修复明显不同于传统软件。 | 证明故障后的诊断、修复和可执行恢复具有独立 Agent 研究必要性；但它研究 issue resolution，不是轨迹级样本路由，作为广义背景而非当前 RQ2 核心论文。 | **中/弱** |

**重述后的 RQ2 可使用的正式论文数量：至少 5 篇（保守取 AgentRevive、STRATUS、ICML Resilience、BacktrackAgent、ReAgent；加上 SyncMind 可达 6 篇）。** 但是，当前原句“选择归因器并提高归因 MRR”的严格同题数量仍为 0，不能在报告中混写。

### 4.3 RQ2 的通用路由论文：只能算方法支持

以下论文是正式 ICML 2025 Main，且 CCF A；它们可以支持“根据样本特征预测效用、在策略之间进行选择”这一方法结构，但全文目标是 LLM 模型质量/成本路由，不是 Agent 失败诊断或归因可靠性。因此不进入 RQ2 的问题强对应计数：

| 论文 | 全文目标 | 只能怎样引用 |
|---|---|---|
| [BEST-Route: Adaptive LLM Routing with Test-Time Optimal Compute](https://proceedings.mlr.press/v267/ding25d.html) | 按输入难度与效用选择模型/计算预算，提高质量—成本权衡 | 方法论背景：样本级效用预测与选择性计算；不能证明 Agent 失败归因问题存在 |
| [A Unified Approach to Routing and Cascading for LLMs](https://proceedings.mlr.press/v267/dekoninck25a.html) | 统一 model routing/cascading，在质量、成本和级联决策间优化 | 方法模块来源：cascade / fallback；不能代替 AgentOps 可靠性方向论文 |
| [Learning to Route LLMs with Confidence Tokens](https://proceedings.mlr.press/v267/chuang25b.html) | 学习置信 token 进行模型选择和拒答 | 方法模块来源：置信/拒答决策；不是失败轨迹归因 |

特别注意：若开题报告把这三篇写成“RQ2 的强对应论文”，会触碰要求文件中“不接受只做成本、Token 或路由优化且缺乏更大 Agent 目的”的禁区。正确写法是：它们为 Exp108 的效用预测/回退形式提供一般方法依据；AgentRevive、STRATUS、Resilience、BacktrackAgent、ReAgent、SyncMind 才负责证明更大的 Agent 失败处理问题。

### 4.4 RQ2 的严格计数结论

为了避免通过降低标准凑足 5 篇，给出两个分母：

| 计数口径 | 强对应数量 | 能否写进当前开题报告 |
|---|---:|---|
| `RQ2-literal`：每条失败样本选择不同 attribution/ranker/fallback ranker，并以 attribution reliability/MRR 为主要结果 | **0** | 不能声称已有 5 篇直接站台；需重构问题或继续做新实验 |
| `RQ2-broad`：根据运行风险/异常/冲突选择 Agent 的诊断、隔离、回退或恢复策略，以提升 Agent reliability | **至少 5（保守）** | 可以作为最小重述后的第二章方向站台；必须改标题、定义和相关工作措辞 |
| 只引用 generic LLM routing/cascading | 0 | 不能作为 RQ2 方向证明，只能作方法支持 |

## 5. 两个最小重构选项（不在本线程执行实验）

### 选项 A：保留 Exp97/98/108/110，最小重述 RQ2（推荐先走）

将 RQ2 从：

> 基于样本外效用预测的选择性归因与回退

重述为：

> **面向异质失败轨迹的自适应诊断与处置策略选择**：面对不同 Agent 失败样本，如何依据部署时可见的运行证据选择结构化归因、时间近因、回退或其他可靠处置策略，从而降低统一策略在部分失败类型上的失效。

这样处理的理由：

- `Exp108` 的 OOF utility forest 仍可作为“策略选择器”的具体实现；`Exp106` 与 recency 是两个诊断/归因 arms；
- `Exp97/98/110` 的跨边界结果可以保留为自适应策略方向的可行性证据；
- AgentRevive、STRATUS、ICML Resilience、BacktrackAgent、ReAgent、SyncMind 支撑的是“失败状态异质、需要条件化诊断/处置/回退”的大问题；
- 仍必须诚实说明：这些论文并不提出 attribution ranker routing，Exp108 是把“自适应失败处理”具体化到失败归因排序的研究增量。

需要补写到开题报告的限制：

1. 不把“选择 RQ1 还是 recency”写成已有文献已经标准化的任务；
2. 不把 LLM routing 论文当作 Agent failure-attribution 论文；
3. 把 RQ2 的主指标从单一 MRR 扩展为归因可靠性、route regret、risk–coverage 和必要的执行/回退收益；
4. 论文阶段仍需在 pristine unseen benchmark 上验证，证明路由不是对 Exp96/97/98 的后验小型 ensemble trick。

**复用程度：最高。** 现有 Exp97/98/108/110 证据都可以保留，主要变化是问题命名、相关工作分类和实验解释，不需要现在立刻新增实验即可继续开题讨论。

### 选项 B：把 RQ2 改成“失败归因驱动的可执行恢复/干预”（需要新增实验）

将 RQ2 改为：

> **失败归因驱动的选择性恢复**：在 RQ1 给出责任 Agent/步骤候选后，如何选择回退、重放、替换或继续执行，并用任务结果翻转/恢复率验证归因是否具有可执行价值。

这样能与 `STRATUS`、`BacktrackAgent`、`ReAgent`、`SyncMind`、`On the Resilience...` 和 `Can Agent Fix Agent Issues?` 形成更直接的“诊断—处置—结果”文献链，同时比“归因器路由”更容易找到 5 篇整篇问题同类的正式论文。但当前 Exp108 只能成为前置 pilot 或策略选择模块，不能继续作为第二章完整主体；必须新增：

- 对 RQ1 Top-1 / Top-k 候选做同状态 replay、撤销、替换或回退；
- 比较无归因、Oracle 归因、预测归因、错误归因和随机归因；
- 以任务成功恢复率、非目标回归率、执行成本和诊断延迟为主指标；
- 证明责任排序真的能改变系统结果，而不是只提高离线 MRR。

**复用程度：较低。** 可复用 trace 读取、task split、OOF、检查点/重放接口和 RQ1 输出，但 Exp108 的最终 MRR 不能直接代替恢复实验。

## 6. 是否已经足以证明必要性与开题

### RQ1

**足以。** 文献证据已经满足并明显超过 Gate 0：

- 6 篇近三年正式 CCF A 直接论文；
- 至少 1 篇（实际 6 篇）全文主要问题与“责任主体/关键步骤定位”一致；
- 论文覆盖基准、时序模型、scope 分解、知识引导、完整 trace、反事实重放等不同方法，说明问题不是由本项目某个模块反向制造的；
- 多篇论文的困难结论（Who&When 的 step accuracy 很低、TraceElephant 对观测完整性敏感）直接证明必要性。

### RQ2

**当前原句不足以直接宣称“已有 5 篇强对应论文”。** 但“自适应 Agent 失败诊断/处置/回退”这一更大问题已有至少 5 篇正式 CCF B+ 论文，且包含 ACL/NeurIPS/ICML/EMNLP 的主会长文。因而：

- 采用选项 A，RQ2 可以作为**最小重述后的开题 GO 候选**；开题报告需明确“文献支撑的是问题家族，当前 OOF utility routing 是本课题具体化”；
- 不重述、坚持“归因器路由”原句，则文献 Gate 不通过，应按选项 B 继续实验或更换第二章问题；
- 无论采用哪项，不能把 RQ2 现有 Exp108 的正 MRR 结果单独当成“研究问题已被文献证明通用”的替代品。

### 两章整体

当前实验报告中的 RQ1/RQ2 指标证据可以支持“实验可行性”叙述，但文献审计后不能继续无条件保留“两个 RQ 均已有完全同题强论文”的表述。最稳妥的开题判断是：

> **RQ1 文献 GO；RQ2 需采用选项 A 的最小问题重述后才可进入两章开题 GO。若不接受重述，RQ2 文献 Gate 为 NO-GO，不能通过 generic routing 论文凑成 GO。**

## 7. 检索与核验记录

### 7.1 检索范围与来源

- 先阅读本地要求文件和当前主线报告，锁定 RQ1/RQ2 的输入、输出和“全文问题同类”标准；
- 以官方出版页面为主：PMLR（ICML）、AAAI Proceedings、ACL Anthology（ACL/EMNLP）、NeurIPS Proceedings、ACM DOI / KDD proceedings；
- 以 CCF 官方第七版公告及分领域目录核对 venue 级别和正式 paper 类型边界；
- 对每篇候选至少核对标题、年份、正式 venue/track、摘要中任务定义、主要结论和正式 URL；
- 没有进行资产哈希、安全检查、下载完整性检查，也没有执行新实验，符合本任务边界与用户确认。

### 7.2 尚未完全核验的事项

以下项目不影响本审计的方向结论，但进入最终开题参考文献表前必须补齐：

1. `StepFinder` 的 ACM DOI 和 KDD Proceedings V.2 已核到，但 ACM landing page 的公开 metadata 没有明确展示 Full/Regular 标签；应保存 ACM/PDF 的正式 paper-type 证据。
2. `AgenTracer` 已核到 ICLR 2026 官方 poster/OpenReview 和 Main 论文身份；应在最终材料中保留 CCF 第七版中 ICLR A 的目录快照，避免沿用旧版 CCF 页面造成歧义。
3. 每篇论文的代码、数据和许可证没有逐仓库完成审计；当前只记录了官方论文页及其是否明确提供数据/代码的摘要信息。按要求文件，最终实验前还需逐项核验 license 和可复现性。
4. 2026 论文是截至 2026-08-23 的当前正式出版状态；若学校采用旧版 CCF 目录，应在开题报告中注明使用 CCF 第七版并保留版本日期。
5. RQ2 的 5—6 篇“问题结构同题”论文分属云 SRE、GUI Agent、多跳 QA、协作软件工程和 MAS resilience；它们支持的是 Agent reliability / failure handling 的通用性，不等于在当前 MAS attribution 数据上的外部有效性。外部有效性仍需实验验证。

## 8. 给主线程的可直接采用的改写句

### RQ1 研究现状句

> 近三年，ICML、KDD、AAAI、ACL 和 ICLR 的正式论文已将多智能体失败归因明确为一个独立的 Agent 研究任务：给定失败执行轨迹，定位责任 Agent、决定性步骤或根因步骤。Who&When 发现现有通用推理模型在 step-level attribution 上仍然很弱；StepFinder、Scope Delineation、FLKR、TraceElephant 和 AgenTracer 分别从时序语义、范围先验、知识引导、全轨迹观测和反事实重放等角度证明该问题需要专门的过程级方法。因此，本课题研究责任步骤排序具有明确的文献问题基础。

### RQ2 选项 A 研究现状句

> 现有 Agent 可靠性研究进一步表明，失败并非由一种固定机制统一处理：AgentRevive 根据风险在 Active/Standby/Terminated 状态间转换，STRATUS 在检测—诊断—缓解状态机中执行安全处置，ICML Resilience 研究 faulty Agent 下的拓扑与检查机制，BacktrackAgent 和 ReAgent 分别通过错误检测后的 backtracking/rollback 恢复 GUI 与多跳推理任务，SyncMind 则系统测量不同 out-of-sync 状态下的恢复能力。它们共同支持“失败样本具有异质性，Agent 需要条件化选择诊断或回退策略”这一问题家族。本课题进一步把该问题具体化为：利用严格 OOF 的效用预测，在结构化责任排序与时间近因之间进行样本级选择。

### 不应采用的句子

> “BEST-Route、Unified Routing 和 Confidence Tokens 已经证明了 Agent 失败归因路由问题。”

这句话不成立。它们证明的是通用 LLM routing/cascading 的方法可行性，不能替代 Agent failure diagnosis / recovery 的方向站台。


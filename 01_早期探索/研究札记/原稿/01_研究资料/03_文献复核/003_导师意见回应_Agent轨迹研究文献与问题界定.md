# 导师意见回应：Agent 轨迹研究的文献证据与问题界定

核查日期：2026年9月19日。依据：[导师意见.md](D:/Code/毕设/导师意见.md)。

本轮先解决概念、文献相关性和研究范围问题，不确定论文题目，不修改PPT。下文的学术定义均来自原论文；“分析”“建议”和“待验证安排”是据此作出的研究判断，不冒充论文已经给出的定义或结论。已核读的章节、正式发表记录和原文入口列在文末，未以摘要或论文名称代替核心内容阅读。

## 1. 对导师意见的总体判断

**当前最先需要确定的是“要判断什么”，其次才是“用什么表示和算法判断”。** 现有相关论文分别判断失败模式、责任主体与关键步骤、各主体的责任分布，以及执行后的状态能否被撤销。这些任务不能用一个“可靠性”概念覆盖，也不能因为都使用轨迹就视为同一研究方向。具体任务定义见第3节，状态处理的区别见第5节。

当前材料具备继续讨论“Agent执行过程的失败分析与诊断”的文献基础；但现有两个研究内容要形成一条主线，还需要解释：诊断的对象、被恢复的对象、实验中的系统是否相同，以及第二项工作究竟检验诊断效果，还是解决独立的事务恢复问题。这是研究范围问题，换一个题目措辞不能解决。

| 导师关注点 | 本轮处理结论 | 仍需落实的具体条件 |
|---|---|---|
| 属于哪个知识体系、哪个层次 | 先按失败分析与诊断、事务恢复两条文献线区分；Agent是研究对象还是实施工具须逐篇判断 | 选定一个主要对象和任务判据 |
| 什么是失败，处理哪类失败 | 区分服务失效、过程错误、关键失败；不能把终局测试失败当成关键步骤标签 | 明确采用哪篇论文的归因定义及数据标签 |
| 图是什么、如何支持诊断 | 图是证据的表示；构图、推断和结论验证是三个需要分别交代的环节 | 说明节点单位、每种边的来源、诊断算法及对照方法 |
| 数据如何感知和获得 | 任务结果、实际决策输入、动作输出、工具观测和状态变化承担不同证据作用 | 核对公开数据实际包含哪些字段，不能靠输出文本补造缺失输入 |
| 两个内容如何递进 | 诊断与其验证/干预可以共享对象；诊断与事务管理也可能成为两套工作 | 在同一批任务、同一系统和相容判据下检验二者的联系 |
| 用案例讲清楚 | 第7节用真实软件修复案例区分定位、撤销与任务完成 | 案例中的过程诊断部分需另采轨迹，不能把补丁样例当现成归因数据 |
| 文献是否集中、是否达到要求 | 正式论文按CCF目录筛选，经典来源用于定义；原[5]—[12]逐项复核 | 核心文献围绕所选方向集中，邻近机制不再同时承担主线论证 |

## 2. 文献筛选与发表状态核验

### 2.1 筛选口径

本轮围绕四组问题检索原始论文：Agent执行轨迹与过程分析、多Agent失败归因、观测证据与诊断验证、回退与事务恢复；优先核对PMLR、ACL Anthology、AAAI、NeurIPS、ACM及PVLDB正式记录。arXiv用于读取作者全文和补充尚未正式发表的研究，不以投稿模板或审稿页面推定录用。

CCF等级依据2026年3月发布、4月9日勘误的第七版正式目录。官网正文访问存在验证限制，目录条目通过CCF署名的正式版PDF镜像逐项核对；不是采用GitHub作者自定评级。该目录中的TDSC、Artificial Intelligence、ICML、ICLR、NeurIPS、AAAI、ACL、OOPSLA、SIGMOD、TODS列为A，EMNLP为B，ESWC为C。目录等级描述发表载体，不能代替论文相关性和论证质量。[CCF正式发布页](https://www.ccf.org.cn/Academic_Evaluation/By_category/)；[所核对正式版PDF的镜像仓库](https://github.com/LovenSar/CCF_RANK/tree/55ca5eae67c26d518c6a8b71ee5827a053086f20)。

### 2.2 建议保留的核心与补充文献

| 文献 | 核实的发表状态 | 本轮用途 |
|---|---|---|
| ReAct；Reflexion | ICLR 2023；NeurIPS 2023，按本次目录均CCF A | 高引用Agent基础：执行轨迹及基于轨迹的反馈重试 |
| Who&When | ICML 2025，CCF A | 责任Agent与关键步骤的任务定义 |
| MAST | NeurIPS 2025，Datasets and Benchmarks Track，CCF A | 多Agent失败模式分类 |
| SDBL | AAAI 2026，CCF A | 候选范围筛选与最终定位的直接对照 |
| FLKR | AAAI 2026，CCF A | 代码生成中责任分布的另一种任务定义 |
| TraceElephant | ACL 2026长文，CCF A | 决策上下文、职责和局部干预验证 |
| Process-Centric Analysis / Graphectory | PACMPL 10(OOPSLA1)，Article 163，2026；对应OOPSLA，CCF A | 软件Agent轨迹的具体图表示和过程分析 |
| ReAgent | EMNLP 2025主会议，CCF B | 推理状态回退的邻近机制 |
| STRATUS | NeurIPS 2025，CCF A | Agent辅助运维及受约束的状态撤销 |
| SagaLLM | PVLDB 18(12)，2025，experience paper | 多Agent工作流事务方向的近邻；单独注明载体 |
| Avizienis等；Reiter | TDSC 2004；Artificial Intelligence 1987，均CCF A | 失效、可靠性、诊断的经典定义 |
| Sagas；ARIES | SIGMOD 1987；TODS 1992，均CCF A | 语义补偿与日志恢复的经典定义 |
| SWE-bench | ICLR 2024，CCF A | 公开软件修复任务与完成判据 |
| R-GCN | ESWC 2018，CCF C；有arXiv全文 | 高引用的关系图方法基础，不计入B以上主组 |
| AgentDebug；AgentRx | 本轮只核实到arXiv预印本 | 原[6]复核及定义差异补充，不冒充高引用核心 |

上表每篇的正式记录及已读位置见第9节。OOPSLA论文已经有PACMPL正式发表信息；2026年10月会议尚未召开，这两种状态不矛盾。PVLDB论文如用于学校认定，应遵循本校对PVLDB/VLDB的口径；本轮不把目录中的VLDB会议条目直接写成“PVLDB期刊A”。

### 2.3 如何处理“arXiv高引用”

不能把“新”“热门”或“题目相关”写成“高引用”。本轮核对到以下高引用基础工作，均标明计数来源与日期，不混合不同数据库或重复版本：

| 论文 | 2026-09-19查询的引用数 | 精确匹配依据及记录 |
|---|---:|---|
| ReAct | 11,351 | Semantic Scholar，以`arXiv:2210.03629`查询，并核对标题和ICLR记录；[论文记录](https://www.semanticscholar.org/paper/99832586d55f540f603637e458a292406a0ed75d) |
| Reflexion | 5,319 | Semantic Scholar，以`arXiv:2303.11366`及正式DOI查询，返回同一记录；[论文记录](https://www.semanticscholar.org/paper/0671fd553dd670a4e820553a974bc48040ba0819) |
| R-GCN | 5,266 | OpenAlex，精确匹配正式DOI；[论文记录](https://openalex.org/W2604314403) |

ReAct和Reflexion均已正式发表，适合补充Agent轨迹基础，不列作“未发表arXiv”。R-GCN虽发表于CCF C载体，仍可作为高引用的关系图基础补充，但它不研究Agent轨迹。三者的引用量都不能证明失败诊断有效。

AgentDebug、AgentRx在不同索引中的覆盖和计数不足以据此认定为高引用，故仅保留为必要的审计补充。已正式发表且有arXiv版本的工作，按正式版本著录，不重复算作另一篇论文。本次引用数及精确查询标识保存在[核验元数据](005_文献核验元数据.json)。

## 3. 用论文定义回答“失败与诊断究竟是什么”

先交代轨迹的来源。ReAct把语言推理加入Agent的行动过程，使后续决策利用此前动作与环境观察；Reflexion进一步将一次执行轨迹和评价反馈转成经验摘要，供后续尝试使用。前者说明单次执行如何组织，后者说明跨次执行如何利用经验；两者均未给出通用的关键失败步骤真值。[ReAct §2—4](https://arxiv.org/html/2210.03629v3)；[Reflexion §3及Algorithm 1](https://papers.nips.cc/paper_files/paper/2023/file/1b44b878bb782e6954cd888628510e90-Paper-Conference.pdf)。因此，需要把“使用轨迹求解任务”与“以轨迹为证据诊断失败”区分开。

### 3.1 先分开失效事件、错误状态和原因

Avizienis等把**failure**定义为交付服务偏离正确服务的事件；**error**是系统状态中可能导致后续失效的部分；**fault**是错误的已判定或假定原因。可靠性是正确服务的连续性。其图16中，检测识别错误的存在，诊断按位置和类型识别错误原因；恢复将含错误及可能含故障的状态，转为无已检测错误、无可再次激活故障的状态，回滚属于错误处理。“无已检测错误”不能扩大为消除了所有错误。[原文§2.1—2.3、§5.2.1及图16，pp.12—13、25](https://www.landwehr.org/2004-aviz-laprie-randell.pdf)。

**对本研究的分析：**工具调用报错是否构成整体系统的服务失效，取决于系统边界及正确服务判据；后续修复不能消除已发生的失效事件。若采用终局任务成败判据，则另按该任务的评价协议判断。中文“失败”可以沿用Agent论文表达，但每次都应明确指终局结果、过程行为还是诊断目标。

### 3.2 Agent论文并没有统一的“关键错误”定义

| 来源 | 论文实际判断的对象 | 采用时必须保留的区别 |
|---|---|---|
| Who&When | 保留此前轨迹，纠正某Agent某步动作并相应调整后续，可以把失败变为成功的关键错误；多个符合时取最早者 | 形式化干预语义与专家标注是两个层次；不等于每条标签都已实际重跑验证 |
| MAST | 14种失败模式，归入系统设计、Agent间失配、任务验证三类 | 模式分类不提供唯一关键步骤；部分模式也见于成功运行 |
| FLKR | 多Agent代码生成中的归一化责任分布 | 输出主体责任分数，不输出首个关键步骤；不能与步骤定位准确率互换 |
| TraceElephant | 结合职责和可恢复性判断责任组件及关键步骤 | 上游出错后若验证者仍有纠正职责，后者错失恢复机会可能成为归因对象 |
| AgentRx（补充） | 首次未恢复的失败 | 首次错误、约束违反、首次未恢复失败不必发生在同一步 |

定义位置：[Who&When §2](https://arxiv.org/html/2505.00212v1#S2)；[MAST §3及附录A、J.1](https://papers.nips.cc/paper_files/paper/2025/file/b1041e52d3be19f0a9bc491657488e4a-Paper-Datasets_and_Benchmarks_Track.pdf)；[FLKR §Problem Formulation，p.320](https://ojs.aaai.org/index.php/AAAI/article/download/36993/40955)；[TraceElephant §2及附录A.1](https://aclanthology.org/2026.acl-long.912.pdf)；[AgentRx §2.1—2.2](https://arxiv.org/html/2602.02475v1#S2)。

**对范围的建议：**如果继续做步骤级定位，应先选择并保持一个基准的关键步骤定义。不同定义的数据可用于跨基准研究，但不能直接混合训练、统一称为“根因真值”。如果改做失败模式分类或主体责任分配，输入标签、输出对象和评价指标都要随之调整。这里不另造一种折中定义。

### 3.3 责任排序能否称为诊断

Reiter的模型诊断输入包括系统描述`SD`、组件集合和观测`OBS`；诊断是假定其中部分组件异常、其余正常时，仍能与描述和观测保持逻辑一致的极小组件集。极小指集合包含意义，不是数量最少。排序分数本身没有检查这些条件，因此不能据可疑度排名宣称实现了Reiter式诊断。[原文定义2.1、2.3、2.4，pp.59、62—63](https://www.cs.ru.nl/P.Lucas/teaching/KeR/reiter.pdf)。

这不要求所有数据驱动研究都采用逻辑诊断，也不禁止使用“诊断”一词。对当前工作更准确的做法是：以选定Agent论文的失败归因任务为依据，说明排序是候选检查顺序还是最终归因输出，并明确它的正确性由什么标签或实验判断。

## 4. “多关系图”需要回答的四个问题

### 4.1 来自哪一种图，而不是来自哪个宽泛领域

R-GCN论文使用有向、带关系标签的多重图`G=(V,E,R)`，边带关系类型，模型通过按关系参数化的消息传递更新节点表示。图的数据结构和R-GCN的可学习运算应分别说明。具有多种边并不意味着已经实现R-GCN。[原文§2及§2.1式(2)](https://arxiv.org/html/1703.06103v4#S2)。

Graphectory则给出Agent轨迹的具体定义：节点对应不同动作，重复动作可复用节点；时序边记录动作转移，结构边记录目录—文件—代码块等包含式导航关系，允许有环。它不是“一步一个节点、角色边加相似边”的通用定义。[原文§2定义1、§2.1](https://arxiv.org/html/2512.02393v3#S2)。

因此，应分别交代**图类型、节点与边的语义、构图过程、图上的诊断运算**。“基于多关系图建模”只说明过程，尚未回答怎样给出诊断结果。

### 4.2 哪些边能从现有日志直接得到

以下为记录要求的分析，不是新增的图算法定义。

| 拟使用的信息 | 需要的原始证据 | 可支持的含义与待核实事项 |
|---|---|---|
| 执行先后 | 步骤索引、时间或调度记录 | 可表示顺序，不能单独推出因果依赖 |
| 消息传递、实际输入 | 发送者、接收者、消息标识和该步实际输入 | 可说明信息是否送达；仅有全局聊天日志不能保证某Agent实际看到该消息 |
| 角色归属 | 系统配置与职责说明 | 同一角色或同一Agent不是同一概念，也不自动构成错误传播关系 |
| 文件与操作对象 | 路径、工具参数、版本及读写记录 | 路径层次可支撑导航关系；要主张数据依赖还需读写与版本证据 |
| 语义相似 | 内容、编码器、相似度及建边规则 | 属于计算得到的关系，应报告误差；相似不能直接作为致因证据 |

实际决策上下文的重要性来自[TraceElephant §3.2—3.3](https://aclanthology.org/2026.acl-long.912.pdf)，软件对象层次来自[Graphectory定义1](https://arxiv.org/html/2512.02393v3#S2)。表中的适用限制是据证据来源所作的分析，不把这些关系预先称为因果边。

### 4.3 人工智能方法具体用在哪一步

应把流程写成“原始轨迹→信息提取/表示→诊断推断→评价”，并标出哪些环节使用规则、LLM或训练模型。例如，SDBL先生成候选步骤集合，再把候选集合连同完整日志交给LLM定位；它并非只输入截断后的片段。其候选Hit@K与最终Agent/步骤准确率分别评价中间阶段和最终结论。[原文方法及评价，pp.33110—33112](https://ojs.aaai.org/index.php/AAAI/article/view/40594/44555)。

对当前已有方案，若实际采用固定聚合加评分器，应按实现如实写出，不能借R-GCN文献把固定运算称为已训练关系卷积。是否值得使用图，要由相同数据、候选范围和预算下的比较支持，不能从“日志有关系”直接推到“图方法更好”。

### 4.4 需要什么证据才可以说诊断可信

建议分开报告四种结果：与人工标签的一致性、证据记录是否完整可复核、有限干预后的局部变化、重新执行到终局后的任务结果。这是对不同实验对象的区分，并非一套新的可信度指标。

TraceElephant的动态方法最多提出3个候选，改变候选处输入并观察后续3步；作者将其限制为局部责任验证，不能写成完整任务修复。Who&When的专家标签也不能自动升级为干预真值。[TraceElephant附录A.6.3](https://aclanthology.org/2026.acl-long.912.pdf)；[Who&When §3](https://arxiv.org/html/2505.00212v1#S3)。对拟开展的干预实验，还应固定重试预算、记录随机性并设置对照；一次成功续行不能单独证明找到了唯一真实原因。

## 5. 回退、补偿和恢复属于什么层次

| 文献 | 被处理的状态与方法 | 结果不能被扩大为 |
|---|---|---|
| Sagas | 长事务拆为局部事务；对已完成部分执行应用定义的补偿 | 数据逐位回到最初状态，或外部从未观察过中间结果 |
| ARIES | 根据持久更新日志重做、撤销，支持事务原子性与持久性；检查点减少恢复扫描工作 | 任何Agent文本日志都满足WAL，或任务答案正确 |
| ReAgent | 多跳问答的断言、证据和中间推断发生冲突时，局部或全局回退后重新推理 | 文件、订单和外部服务副作用已经撤销 |
| STRATUS | Agent对云故障进行检测、诊断和缓解；事务边界处约束严重度不增加 | 云故障必然被解决，或Agent自身的失败原因被归因 |
| SagaLLM | 保存工作流状态与操作依赖，独立验证、补偿并重新规划 | 任意工具获得严格ACID，或LLM生成的补偿已被形式化证明正确 |

出处：[Sagas §1，pp.249—250](https://sigmodrecord.org/?download_id=11106&smd_process_download=1)；[ARIES §1.1、§5.4](https://www.cs.cmu.edu/~natassa/courses/15-721/papers/p94-mohan.pdf)；[ReAgent §3—4](https://aclanthology.org/2025.emnlp-main.202.pdf)；[STRATUS §3—4](https://proceedings.neurips.cc/paper_files/paper/2025/file/47a6e9e2c3019f13ad94a0f259fe4970-Paper-Conference.pdf)；[SagaLLM §3—6](https://www.vldb.org/pvldb/vol18/p4874-chang.pdf)。

两个条件尤其不能遗漏。STRATUS的TNR依赖写者独占、精确Undo和有界动作序列，而且事务内部状态可暂时恶化；SagaLLM借鉴的补偿则有业务语义，论文也明确放松严格ACID，并将补偿代码的形式验证留作未来工作。二者不能相互替代证明条件。[STRATUS §3及§4.1](https://proceedings.neurips.cc/paper_files/paper/2025/file/47a6e9e2c3019f13ad94a0f259fe4970-Paper-Conference.pdf)；[SagaLLM §3.1、§6](https://www.vldb.org/pvldb/vol18/p4874-chang.pdf)。

**对导师意见的回应：**如果主要研究关键步骤诊断，恢复可以作为诊断的应用或验证，但必须单独评价；如果主要研究事务管理，则应围绕状态、依赖、并发、失败模型、提交与补偿组织问题。不能让“轨迹诊断”承担“事务正确性”的证明，也不能让“回滚成功”承担“归因正确”的证明。

## 6. 现有第5—12篇文献逐项重审

编号对应当前V5修订版，仅用于定位原有条目。

| 原编号 | 真正研究对象；Agent的角色 | 与主问题的关系及处理建议 |
|---|---|---|
| [5] Process-Centric Analysis | 软件Agent的执行过程是研究对象 | 保留为轨迹图与过程分析来源；已有在线监测和干预，不能说其“仅离线分析、不能干预” |
| [6] AgentDebug | 单Agent运行及内部模块错误是对象；诊断器提供反馈 | 降为预印本补充；单Agent的规划/记忆等模块不能直接改称多个Agent |
| [7] ReAgent | 多Agent问答推理与纠错机制；应用目标是问答 | 可保留为推理回退近邻，不能支撑文件或仓库事务恢复 |
| [8] STRATUS | 云系统故障是主要待处理对象；Agent是运维修复手段 | 若走Agent自身失败诊断，应放在应用邻近工作；若讨论受约束执行，保留TNR及假设 |
| [9] SagaLLM | 多Agent规划工作流及状态协调机制 | 事务方向的近邻；不是步骤级失败归因基准，也不是大规模回滚正确性实证 |
| [10] SDBL | 多Agent失败轨迹是对象；LLM执行两阶段归因 | 保留为步骤定位强相关工作与直接比较对象 |
| [11] FLKR | 多Agent代码生成失败是对象 | 保留为责任分配相关工作；明确主体级责任分布与步骤级定位不同 |
| [12] TraceElephant | Agent/组件运行及其可观测上下文是对象；另用诊断Agent作分析工具 | 保留为数据条件和验证的核心来源；不能把局部探测写成终局修复 |

各行的依据见第3—5节及第9节原文。另有三处阅读后必须保留的细节：

- **AgentDebug存在版本内叙述不一致。** §3.2的逐步反事实测试描述，与Algorithm 1的“LLM (no rollout/counterfactuals)”注释不一致。未经实现复核，不宣称其已逐条完成真实反事实验证。[原文§3.2、Algorithm 1](https://arxiv.org/html/2509.25370v1#S3)。
- **SDBL与Who&When样本口径不同。** SDBL表1使用54条人工系统日志、126条自动系统日志；不能误写成54/126个系统，也不能与原基准184条直接混报。[SDBL实验部分](https://ojs.aaai.org/index.php/AAAI/article/view/40594/44555)。
- **已有工作并非没有排序、候选或反馈。** 因此，研究缺口不能写成“现有方法只能定位，本文首次排序并恢复”。需要具体比较输入证据、输出粒度、计算成本、干预条件和评价对象，再判断能否形成新贡献。

## 7. 用同一个软件任务解释研究对象、过程和成果

### 7.1 真实任务：KernelPCA修复

SWE-bench原论文表34给出`scikit-learn/scikit-learn`任务13241，涉及KernelPCA重复降维结果的符号不确定性；展示的SWE-Llama补丁未解决问题并破坏既有行为，参考修复使用`svd_flip`。这是论文中的模型修复失败案例，不是已经完成的多Agent诊断与恢复实验。[SWE-bench表34，pp.51—52](https://arxiv.org/pdf/2310.06770#page=51)；[对应Issue](https://github.com/scikit-learn/scikit-learn/issues/8798)；[对应PR](https://github.com/scikit-learn/scikit-learn/pull/13241)。

任务完成判据采用SWE-bench的测试协议：`FAIL_TO_PASS`与`PASS_TO_PASS`均通过。撤回错误补丁可能消除新增退化，却仍未修好原问题；因此回滚与任务完成必须分开报告。[SWE-bench §2、附录A.4](https://arxiv.org/pdf/2310.06770#page=20)。

### 7.2 从该任务出发，怎样构成可研究的过程

以下是**待采集、待验证的研究安排**，不虚构论文中的步骤编号、Agent角色或实验结果。

1. **固定对象与环境。** 使用该任务的仓库版本、问题说明和测试条件，记录具体Agent系统、模型、工具及运行配置；若研究多Agent，还要选择真实的多Agent系统，不能把单Agent调用工具直接视为多Agent协作。
2. **采集执行证据。** 在运行器中记录每步实际输入、输出、动作及工具观测；涉及文件写入时保存可对应的差分和状态版本。明确哪些字段来自公开轨迹，哪些需自行运行获取。
3. **确认终局并准备标签。** 由评测结果确定这次是否失败；再按选定论文的步骤归因定义标注，分别记录证据与不确定性。测试失败本身不提供唯一关键步骤。
4. **在离线分析程序中处理轨迹。** 比较完整序列、候选筛选及待研究的图表示；输出责任候选、依据和次序。图中关系只采用实际可获得或明确标记为推断的数据。
5. **在隔离副本中检验诊断的用途。** 从候选处修正输入、行动或回退状态，按照预先约定的续行协议执行；分别记录局部变化和终局测试。保存同预算对照，不能把“允许更多重试”当作诊断优势。

这些安排分别借鉴Who&When的归因任务、TraceElephant的观测要求、Graphectory的轨迹表示和SWE-bench的任务协议；它们的组合是否有研究价值仍需实验，不作为已有论文共同提出的方法。

### 7.3 两项成果应该分别展示什么

| 成果展示 | 应展示的可检查内容 | 不能用来替代它的内容 |
|---|---|---|
| 诊断结果案例 | 一条具体失败轨迹，明确标注标准；候选步骤、责任单位、对应输入输出和判定依据；与标签或干预证据的比较 | 只显示“最后测试失败”或一段听起来合理的解释 |
| 诊断应用/恢复结果案例 | 同一任务干预前后的状态与行为；哪些修改被撤销、哪些保留；局部检查、终局测试、成本和失败尝试 | 只显示成功回滚命令，或只显示任务最终通过 |

本轮没有运行该任务，故不提供虚构步骤、排名分数或成功率。如果最后选择纯诊断方向，第二项可展示诊断的验证结果；如果选择事务方向，第二项必须把状态管理本身作为研究对象。

## 8. 在不定题的前提下收敛研究

### 8.1 两条可以继续讨论、但不能含混合并的路线

| 项目 | 以失败诊断为核心 | 以工作流事务恢复为核心 |
|---|---|---|
| 主要对象 | Agent系统的失败执行过程 | 带外部副作用的Agent工作流与状态 |
| 核心文献 | Who&When、MAST、SDBL、TraceElephant；Graphectory作表示参照 | Sagas、ARIES、SagaLLM；STRATUS作条件化安全机制参照 |
| 第一项可讨论内容 | 在明确归因定义下，利用可获得轨迹证据定位关键主体/步骤 | 记录操作、状态、依赖及恢复所需信息 |
| 第二项可讨论内容 | 检验诊断证据及有依据的干预是否有效 | 在明确失败与并发条件下执行撤销/补偿并检查结果 |
| 两项联系 | 相同对象下，从判断到验证与应用 | 相同状态模型下，从记录与决策到恢复执行 |
| 最关键的数据前提 | 定义相容的标签、实际决策输入；干预还需要可运行环境 | 可操作状态、依赖、恢复动作及外部副作用边界 |
| 主要未决问题 | 相对既有定位和动态验证工作的新增贡献是什么 | 当前环境是否真的包含需事务机制解决的独立问题 |

**本轮建议优先论证失败诊断路线，但不据此确定题目或取消另一项工作。** 原因是现有核心材料已经有直接归因定义、公开基准和强相关比较工作；事务路线则还需要更明确的状态与失败模型。此建议是对已有材料的判断，不是论文证明“诊断方向更好”。应先核对离线归因评价所需标签；若第二项采用干预验证，再核对可运行的续行环境。两项的可行性分别判断。

还要处理当前研究对象的不一致：现有材料的RQ1主要面向多Agent失败轨迹，RQ2验证场景主要是单助手软件工具动作流。[当前V5文字记录，第5页](D:/Code/毕设/graduate-thesis-experiments/开题/开题报告PPT/V5_修订版_全文提取_含公式图表与备注.md:132)。两者可以分别研究，但若要声明端到端递进，必须证明诊断单位如何对应真实写入步骤，并在共同场景中验证；不能仅靠只读接口连接就认为研究问题已经统一。

### 8.2 本轮能够交给导师讨论的三行内容

下面保留题目空缺，不给出候选标题。

> **第一行：题目暂不确定；先确认主要研究对象及所采用的失败归因定义。**  
> **第二行：若采用失败诊断路线，关注Agent系统执行失败后，仅有终局结果不足以确定责任主体与关键步骤的问题；利用执行过程证据支持可检查的诊断。**  
> **第三行：两个待论证内容为步骤级失败归因，以及在同一系统和任务中对诊断依据与干预效果的验证。**

第二、三行是用于讨论的方向描述，不是已定研究问题或创新点。下一轮应先核对数据是否支持这两项内容，再决定是否保留图方法、责任排序和恢复机制，以及哪些词值得进入题目。

### 8.3 按开题要素列出当前已知与缺口

| 要素 | 文献已提供的基础 | 还需形成的研究决定或证据 |
|---|---|---|
| 背景、意义 | 终局评价、失败模式分析和过程诊断针对不同信息需求 | 说明目标使用者、具体困难及解决后的可评价价值 |
| 研究对象、范围 | 单Agent、多Agent、功能组件、外部服务已有明确区分 | 选定系统；限定失败类型与不处理的情形 |
| 研究问题 | 模式分类、关键步骤定位、责任分布均有现成定义 | 选择一个主要任务，说明两个内容如何支撑它 |
| 核心技术、方法 | 序列诊断、候选筛选、图表示、学习评分和干预均已有工作 | 解释具体技术解决哪项困难，给出必要基线和消融 |
| 数据来源 | 公开归因数据、软件任务和过程轨迹可以分别获得 | 核对版本、许可、字段、标签相容性及复现条件 |
| 正确性与有效性 | 人工一致性、局部验证、任务测试分别有相应实践 | 选定主要评价对象，区分方法效果与推断强度 |
| 研究贡献 | 本轮排除了若干不准确的“已有研究没有……”表述 | 在固定基准与强对照下证明具体新增能力 |

## 9. 已核读内容与原文索引

以下按阅读用途组织，条目中的节号和页码用于继续精读。页码优先为印刷页码；标注“PDF页”时以文件第一页起计。

### 9.1 概念与图方法基础

1. **Avizienis, Laprie, Randell, Landwehr. Basic Concepts and Taxonomy of Dependable and Secure Computing. TDSC 1(1):11–33, 2004.** 已读§2.1—2.4、§5.2.1并核对图16。用于区分失效、错误、故障、可靠性、诊断和恢复；不提供Agent分类或算法效果。[DOI](https://doi.org/10.1109/TDSC.2004.2)；[全文](https://www.landwehr.org/2004-aviz-laprie-randell.pdf)。
2. **Reiter. A Theory of Diagnosis from First Principles. Artificial Intelligence 32(1):57–95, 1987.** 已读§1—2、§3命题3.1—3.4、§4.1。重点复读定义2.4，理解一致性、极小诊断及新增观测的作用。[DOI](https://doi.org/10.1016/0004-3702(87)90062-2)；[全文](https://www.cs.ru.nl/P.Lucas/teaching/KeR/reiter.pdf)。
3. **Schlichtkrull et al. Modeling Relational Data with Graph Convolutional Networks. ESWC 2018:593–607.** 已读§2—2.1，重点为图表示和关系参数化更新。属于通用关系数据方法；不能替代Agent问题定义。[DOI](https://doi.org/10.1007/978-3-319-93417-4_38)；[全文](https://arxiv.org/html/1703.06103v4)。

### 9.2 失败轨迹分析与归因

4. **Zhang et al. Which Agent Causes Task Failures and When? On Automated Failure Attribution of LLM Multi-Agent Systems. ICML 2025, PMLR 267:76583–76599.** 已读§2、§3—3.3、§4.1、附录B/F。184例来自127种系统配置；输出Agent、步骤和解释，按主体与步骤命中评价。下一步应核对实际采用的数据发布版本及标签字段。[正式记录](https://proceedings.mlr.press/v267/zhang25cq.html)；[全文](https://arxiv.org/html/2505.00212v1)。
5. **Cemri et al. Why Do Multi-Agent LLM Systems Fail? NeurIPS 2025, Datasets and Benchmarks Track.** 已读§3.1—3.4、§4、附录A和J.1。采用正式版的1642条轨迹、7种系统口径，早期版本的150条分析集不能替代完整数据规模。适合先理解具体模式，再决定研究子集。[正式记录](https://papers.nips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html)；[全文](https://papers.nips.cc/paper_files/paper/2025/file/b1041e52d3be19f0a9bc491657488e4a-Paper-Datasets_and_Benchmarks_Track.pdf)。
6. **Sun et al. Scope Delineation Before Localization: A Two-Stage Framework for Enhancing Failure Attribution in Multi-Agent Systems. AAAI 2026.** 已读Problem Definition、方法式(1)、(5)—(8)、评价与表1，pp.33110—33112。适合检查候选覆盖与最终定位之间的联系。[正式记录](https://ojs.aaai.org/index.php/AAAI/article/view/40594)；[全文](https://ojs.aaai.org/index.php/AAAI/article/view/40594/44555)。
7. **Geng et al. Failure Localization in Multi-Agent Code Generation via Knowledge-Guided and Transferable Reasoning. AAAI 40(1):318–326, 2026.** 已读问题定义、方法式(1)—(12)、数据与指标、表2。通过代码/角色表征、知识对齐和相邻角色差异学习评分；COFL含2520条无标签训练失败和142条标注评估案例。FLA衡量责任向量的余弦相似度，不能改称普通准确率。[正式记录](https://ojs.aaai.org/index.php/AAAI/article/view/36993)；[全文](https://ojs.aaai.org/index.php/AAAI/article/download/36993/40955)。
8. **Chen et al. Seeing the Whole Elephant: A Benchmark for Failure Attribution in LLM-based Multi-Agent Systems. ACL 2026:19888–19905.** 已读§2、§3.2—3.3、附录A.1、A.5—A.6，正式PDF核对至A.6.3。220条失败轨迹；含单Agent系统的功能组件归因，不能全称为多独立Agent。重点理解“实际看到什么”如何影响责任判断。[正式记录](https://aclanthology.org/2026.acl-long.912/)；[全文](https://aclanthology.org/2026.acl-long.912.pdf)。
9. **Liu et al. Process-Centric Analysis of Agentic Software Systems. PACMPL 10(OOPSLA1), Article 163, 2026.** 已读§2定义1—2、§2.1—2.4、§3.1和§3.5及图1—2。分析SWE-agent/OpenHands的4000条轨迹；方法包含在线干预。图示django-10973的两条运行均成功，不能拿其中的低效或缺少验证直接当失败样例。[DOI](https://doi.org/10.1145/3798271)；[全文](https://arxiv.org/html/2512.02393v3)；[OOPSLA官方条目](https://2026.splashcon.org/details/oopsla-2026/74/Process-Centric-Analysis-of-Agentic-Software-Systems)。
10. **Zhu et al. Where LLM Agents Fail and How They can Learn From Failures. arXiv:2509.25370, 2025.** 已读§2—4.1、Algorithm 1及附录A.2。AgentErrorBench有200条来自ALFWorld、WebShop、GAIA的失败轨迹，诊断步骤、模块和类别；出版资格及实现冲突按第6节处理。[记录与版本](https://arxiv.org/abs/2509.25370)；[所读全文v1](https://arxiv.org/html/2509.25370v1)。
11. **AgentRx: Diagnosing AI Agent Failures from Execution Trajectories. arXiv:2602.02475, 2026.** 已读§1—4.1、附录B。通过工具模式、政策和轨迹生成可执行约束，形成违规证据再诊断；115条轨迹。用于理解违规证据与关键失败的区别，本轮不作高引用主证据。[记录](https://arxiv.org/abs/2602.02475)；[所读全文v1](https://arxiv.org/html/2602.02475v1)。

### 9.3 回退、事务与软件任务

12. **Garcia-Molina, Salem. Sagas. SIGMOD 1987:249–259.** 已读§1，重点是长事务拆分与补偿语义，取消预订例说明为何不能简单覆盖为旧值。[DOI](https://doi.org/10.1145/38713.38742)；[全文](https://sigmodrecord.org/?download_id=11106&smd_process_download=1)。
13. **Mohan et al. ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging. TODS 17(1):94–162, 1992.** 已读§1.1及§5.4；用于明确日志、重做、撤销与检查点前提。[IBM出版记录](https://research.ibm.com/publications/aries-a-transaction-recovery-method-supporting-fine-granularity-locking-and-partial-rollbacks-using-write-ahead-logging)；[全文](https://www.cs.cmu.edu/~natassa/courses/15-721/papers/p94-mohan.pdf)。
14. **Zhao et al. ReAgent: Reversible Multi-Agent Reasoning for Knowledge-Enhanced Multi-Hop QA. EMNLP 2025:4067–4089.** 已读§3—4、§5.1—5.3。实验为HotpotQA、2WikiMultiHopQA、MuSiQue各1000个验证样本，评价EM/F1和回退消融；不是外部状态恢复评测。[正式记录](https://aclanthology.org/2025.emnlp-main.202/)；[全文](https://aclanthology.org/2025.emnlp-main.202.pdf)。
15. **Chen et al. STRATUS: A Multi-agent System for Autonomous Reliability Engineering of Modern Clouds. NeurIPS 2025.** 已读§2—5，尤其TNR条件、§4.1的Undo限制及§5实验边界。输入云日志、追踪、指标和资源信息，输出缓解操作；在AIOpsLab和ITBench上评价。[正式全文](https://proceedings.neurips.cc/paper_files/paper/2025/file/47a6e9e2c3019f13ad94a0f259fe4970-Paper-Conference.pdf)。
16. **Chang, Geng. SagaLLM: Context Management, Validation, and Transaction Guarantees for Multi-Agent LLM Planning. PVLDB 18(12):4874–4886, 2025.** 已读§3—6。实证选用REALM的P5/P6/P8/P9规划案例；表10为定性比较，不应改写为恢复成功率证据。[DOI](https://doi.org/10.14778/3750601.3750611)；[全文](https://www.vldb.org/pvldb/vol18/p4874-chang.pdf)。
17. **Jimenez et al. SWE-bench: Can Language Models Resolve Real-World GitHub Issues? ICLR 2024.** 已读§2、附录A.4、表34。任务、补丁与测试结果可解释软件修复评价；它不直接提供完整步骤归因标签。[作者发布页](https://www.swebench.com/original.html)；[全文](https://arxiv.org/pdf/2310.06770)；[官方数据集](https://huggingface.co/datasets/princeton-nlp/SWE-bench)。

### 9.4 高引用Agent轨迹基础

18. **Yao et al. ReAct: Synergizing Reasoning and Acting in Language Models. ICLR 2023.** 已读§2—4、附录D/E.1；arXiv v3首页与ICLR官方记录核实发表。实验覆盖HotpotQA、FEVER、ALFWorld、WebShop，按各自答案、分类或任务指标评价。Agent决策机制是研究对象，也作为任务求解手段；推理文本不能直接视为模型内部计算的忠实记录。[正式记录](https://openreview.net/forum?id=WE_vluYUL-X)；[全文](https://arxiv.org/html/2210.03629v3)；[精确引用查询](https://api.semanticscholar.org/graph/v1/paper/arXiv:2210.03629?fields=title,year,venue,citationCount,externalIds,url)。
19. **Shinn et al. Reflexion: Language Agents with Verbal Reinforcement Learning. NeurIPS 2023.** 已读正式PDF§3—4、图2、Algorithm 1。执行器、评价器与反思模块协作，将反馈写入记忆而不更新LLM权重；实验覆盖ALFWorld、HotpotQA和编码任务。反思摘要不是独立标注的根因；多次尝试的累计成功不能与单次执行直接混比，代码`pass@1`也不意味着只调用一次LLM。[正式记录](https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html)；[全文](https://papers.nips.cc/paper_files/paper/2023/file/1b44b878bb782e6954cd888628510e90-Paper-Conference.pdf)；[精确引用查询](https://api.semanticscholar.org/graph/v1/paper/DOI:10.52202/075280-0377?fields=title,year,venue,citationCount,externalIds,url)。

建议后续精读顺序为：经典概念与ReAct/Reflexion→Who&When与MAST→SDBL和TraceElephant→Graphectory，再按选定路线读FLKR或事务恢复文献。每篇需要回答的不是“用了什么关键词”，而是输入是什么、判断什么、如何得到结果、由什么证据验证，以及这些条件能否在拟研究系统中成立。

# 开题PPT V9逐页内容

## 第1页 基于学习排序的智能体失败诊断与执行恢复方法

基于学习排序的智能体
失败诊断与执行恢复方法

开题报告  ·  汇报人：杨亚鹏  ·  2026年10月

Learning to Rank for Agent Failure Diagnosis and Execution Recovery

## 第2页 六章目录

01.
02.
03.
04.
05.
06.

背景与现状
目标与问题
内容与方法
难点与创新
实验与指标
基础与进度

Background and Related Work
Objectives and Problem Definition
Research Content and Methods
Challenges and Contributions
Experiments and Evaluation
Research Basis and Schedule

## 第3页 研究背景与国内外研究现状



## 第4页 1.1 研究背景（1/2）

从模型输出到持续执行

大语言模型的能力由文本理解、指令遵循与多步推理，逐步延伸到需要规划和
执行的复杂任务。智能体连接模型、工具与环境，将自然语言需求转化为连续
行动。[1–3]

在科学实验、网页操作、计算机使用和软件工程中，智能体都需要根据
环境反馈调整后续行动，并在多步交互中保持目标一致。[6–9]

任务质量因而取决于完整执行过程：一次判断或动作会改变后续可见的信息、
代码和环境状态，局部错误可能在较晚的验收阶段才显现。

## 第5页 1.1 研究背景（2/2）

执行可靠性中的连续问题

01

错误传播： 早期观测误读、计划偏差或不当动作可能进入后续步骤使用的
中间状态，使责任发生位置与最终失败症状出现的位置产生时序错位。
[10,11]

02

诊断需求： 任务结果只能说明是否成功。失败诊断还需比较轨迹内各步骤
的责任线索，形成优先检查次序，为系统改进提供依据。[12]

03

恢复需求： 诊断结果需要转化为当前可执行的修正，并通过验证判断任务
是否推进、先前已经通过的行为是否仍然保持。[13–15]

## 第6页 1.2.1 智能体构建与执行可靠性

2023

Yao 等

ReAct交替组织推理、动作与环境观察，使模型能够依据外部反馈调
整后续行动，建立持续执行的基本方式。[3]

2024

Wu / Hong 等

AutoGen、MetaGPT分别通过可编程会话与角色分工组织协作，将
单次生成扩展为多主体的信息交互和结构化执行。[4,5]

2025

Cemri 等

MAST将多智能体失败归纳为系统设计、智能体间失配和任务验证等
类别，揭示了多环节失效，推动研究转向过程分析与系统改进。[10]

## 第7页 1.2.2 失败归因与责任步骤排序（1/2）

责任判断与学习式评分

2025

Zhang 等

Who & When识别责任智能体与决定性错误步骤，比较完整日志一
次判断、二分搜索和逐前缀检查，明确细粒度归因的评价对象。[12]

2026

Sun / Zhu 等

SDBL先约束可疑范围再识别责任位置。StepFinder联合步骤语义、
时序与角色交互学习责任分数，将部分生成式诊断转为专门模型计算。
[16,11]

2026

Rafi / Deng 等

FALAT、DeFA预印本使用依赖信息组织轨迹搜索与归因。引入关系已
有研究基础，仍需检验具体表示和传播方式的有效增量。[17,18]

## 第8页 1.2.2 失败归因与责任步骤排序（2/2）

监督条件与本文切入点

监督来源决定诊断含义。 Aegis、AgenTracer通过错误生成或故障诱发构造归
因数据；TraceElephant强调工具返回、环境信息和系统配置等完整观察对判
断的影响。[19–21]

不同来源采用不同责任定义和信息条件。本文保留来源标注，明确可见字段、
步骤边界及原始索引，先核对兼容性，再开展共同评价。

本课题关注步骤语义、可观察关系与候选相关上下文的联合评分。研究增量需
要在相同输入、监督及训练资源下体现，并进一步考察排序对恢复行动的作用。

## 第9页 1.2.3 反馈纠错与可恢复执行

2023

Madaan / Shinn 
等

Self-Refine、Reflexion分别通过反馈修订和语言反思支持后续尝试，
使纠错能够利用先前生成或执行的经验。[22,23]

2024

Gou / Huang 等

CRITIC使用外部工具检验输出后再修改。自纠错研究表明，缺少有效
外部反馈时，反复修改并不能稳定带来改善。[24,25]

2025–2026

Chang / Zhuang
 / Yu 等

SagaLLM研究上下文、验证与事务补偿。AgentRewind、
Rollback-Induced Reflection预印本进一步处理环境恢复、回退位
置与反思保留，恢复范围由文本扩展到执行状态。[14,15,26]

## 第10页 1.2.4 诊断引导恢复与软件任务求解（1/2）

软件任务的完整求解方法

2025

Xia / Li 等

Agentless通过分层定位、补丁生成与验证选择求解仓库问题。
PatchPilot依据验证反馈继续细化修复，形成可执行的软件任务流程。
[27,28]

2026

Tian / Ruan 等

EnAgent利用候选生成、剪枝与工具辅助选择组织集成推理。
AOrchestra按需创建子智能体，组织任务上下文与工具执行。
[29,30]

比较对象

完整执行流程

这些方法提供固定流程、多轨迹集成与动态任务组织的完整参照。本
文将在共同失败状态、信息与资源条件下比较其恢复表现。

## 第11页 1.2.4 诊断引导恢复与软件任务求解（2/2）

诊断到行动仍需独立验证

状态与认知需要重新对齐。 SyncMind研究认知与实际代码状态失配后的恢复；
DoVer通过实际干预和重新执行检验故障解释。[31,13]

诊断开始直接约束行动。 DARC预印本使用开发阶段的任务族失败分析选择恢
复策略，并在测试前冻结策略。其决策对象与单条轨迹的步骤排序有所区别。
[32]

失败预测与预防研究指出，较高预测能力并不自动形成有效干预，中途纠偏还
可能破坏原本能成功的执行。[33] 因此本文分别评价
诊断质量、实际恢复与作用机制。

## 第12页 1.3 现有问题与研究意义

01

关系与上下文的信息价值： 在相同监督和输入下，检验跨步骤联系与候选
相关聚合能否提高标注责任步骤的排名，并同时衡量额外计算成本。

02

历史诊断与当前动作的对应： 将责任线索映射到当前可检查对象，结合最
新公开反馈生成和验证修正，分析排序何时能够转化为恢复收益。

03

新进展与已有行为的协调： 以稳定行为身份记录已验证进展，比较接纳、
拒绝和回退规则对恢复成功、行为退化及验证代价的影响。

软件任务提供代码状态、工具记录与可执行验收，使上述联系能够被具体观察。[9,34,35]

## 第13页 研究目标与问题定义



## 第14页 2.1 研究目标

责任步骤排序

以失败轨迹为输入，在可变长度步
骤集合中联合使用语义、可观察关
系与候选相关上下文，学习
相对诊断优先级。

观察标注步骤排名、训练变化与端
到端推断开销。

诊断引导执行恢复

以失败形成的当前状态为起点，把
排序转为当前可用证据，结合公开
反馈生成修正，并通过
行为验证与状态接纳继续推进原任
务。

观察恢复、资源和行为退化。

两项目标通过“排序产物—当前证据—生成动作—验证结果”衔接。

## 第15页 2.2 研究问题

RQ1

如何联合步骤语义、可观察关系与候选相关上下文，提高标注责任步骤在
失败轨迹内的排名？

一条轨迹为排序组，步骤为候选，来源标注提供监督。与StepFinder等方法在共
同条件下比较MRR、Top-1、Hit@k及开销。

RQ2

责任排序能否通过有限预算下的证据选择，提高失败执行的恢复效果并控
制已有行为退化？

先映射当前对象，再生成与验证修正。通过完整系统比较衡量效用，通过固定恢
复器中的排序替换与置换识别增量。

## 第16页 2.3 研究对象与基本概念（1/2）

执行轨迹与责任步骤

轨迹记录同一任务的有序文本、动
作、观察和行为来源。责任步骤按
数据来源标注定义，是排序监督目
标。

未标注步骤不等于无责任，标注位
置也不等于经反事实检验确认的唯
一根因。

排序证据与执行状态

步骤排序给出轨迹内的预测检查次
序。恢复证据进一步说明历史对象、
当前内容和公开失败现象。

当前状态已被接纳；候选状态尚待
验证；交付状态按固定公开规则选
定后接受独立验收。

## 第17页 2.3 研究对象与基本概念（2/2）

匿名角色与多智能体的边界

匿名角色是逐轨迹重编号。 Planner、Coder、Reviewer可映射为role_0、
role_1、role_2。同一角色保持相同编号，另一条轨迹的role_0可以对应其他
职责。

匿名化保留行为来源与同角色联系，去除角色名称字段中的职业语义；它不会
删除协作关系，也不能保证轨迹正文中不存在身份线索。

当前恢复实现由单个修复生成器配合工具与验证器运行。 排序模型可分析多角
色轨迹，当前软件恢复输入只有一个匿名执行角色，故本文不将模块分工表述
为多智能体协作创新。

## 第18页 2.4 理论基础与方法依据

•

学习排序 [36]： 轨迹定义候选组，步骤定义排序项，责任标注约束相对优先级。
有限检查与证据预算赋予全步骤次序明确用途。

•

监督与损失边界： 单标注下，轨迹内softmax损失等价于位置分类交叉熵。贡
献拟来自表示、关系和上下文，不把已有损失改名视为创新。

•

多关系表示 [37]： 区分时序、角色和结构等联系，分别聚合邻域信息；关系边
表示可观察关联，其含义不直接等同于因果依赖。

•

反馈与状态管理 [23,24,38]： 结合语言反思、工具反馈与操作记录思想，通过
隔离验证、接纳和行为保护管理恢复，保障范围由实际验证条件限定。

## 第19页 研究内容与技术路线



## 第20页 3.1 总体技术路线与排序任务定义（1/2）

失败轨迹与可见字段
文本、动作、匿名角色

RQ1 轨迹内学习排序
语义、关系与候选上下文

全步骤预测优先次序
标注位置决定定位评价

历史到当前的证据映射
对象对应、去重与证据预算

RQ2 反馈驱动修复
当前代码、公开观察与动作

验证、接纳与交付
身份保护、预算与选择规则

图3-1 基于学习排序的失败诊断与执行恢复技术路线

定位指标评价标注步骤的排名。独立验收评价方法选定的交付状态，验收反馈不进入恢复。

## 第21页 3.1 总体技术路线与排序任务定义（2/2）

轨迹内排序的任务定义

01

排序样本： Dq = (Tq, Yq)：Tq为同一执行的有效步骤，Yq为来源标注的责
任索引。查询组由一次任务执行确定，无需额外假定检索查询。

02

评分与输出： 计算sqi = fθ(Tq, i)，按分数降序输出全部有效步骤的优先次
序。预处理固定步骤边界与原始索引，同分按原索引处理，补齐位置不参
与排序。

03

信息与时间范围： 诊断读取完整的已发生轨迹，包含候选之后已经观察到
的步骤。它属于执行后诊断；恢复生成器另读任务要求、当前代码与公开
反馈。

## 第22页 3.2 语义、多关系与候选上下文联合排序

步骤输入183维
文本128、角色32
公开结构23维

事件关联残差
有配对则双向补充
缺失配对置零

两层多关系传播
邻接、同角色
结构与动作签名

候选步骤相关上下文
每个步骤作为查询
同轨迹注意力聚合

融合评分与轨迹内归一化
s = MLP[h; h⁽⁰⁾; c; h−c]

步骤优先次序
按分数降序 argsort

图3-2 步骤表示、多关系、候选上下文与学习排序

训练提升标注位置的相对排名。单正例损失等价于轨迹内位置交叉熵，未标注步骤之间没
有完整次序监督。

## 第23页 3.2.1 步骤表示与关系传播（1/2）

步骤表示

冻结文本编码处理内容、动作与思
考，匿名角色编码标识行为来源，
公开结构特征描述位置、事件和格
式。

现有起点：128维文本 + 32维角色
 + 23维结构，经训练组统计规范
化后投影到96维隐空间。事件配对
残差在缺失配对时置零。

有类型的可观察关系

连接前后最近的匹配步骤，使用时
序相邻、同匿名角色、完整结构签
名、非空动作结构四类关系，不使
用责任标签构边。

空邻居保留为空；结构相同不代表
语义相同。单角色时同角色边可能
与时序边重合，需要报告重合率。

## 第24页 3.2.1 步骤表示与关系传播（2/2）

门控消息与关系融合

关系消息依据发送节点及其与接收节点的差值形成门控，再在每类关系内求均值。

mᵢᵣ = meanⱼ∈Nᵣ(i) { σ(gᵣ[hᵢ ; hⱼ−hᵢ]) ⊙ φᵣ[hⱼ ; hⱼ−hᵢ] }

βᵢᵣ = softmaxᵣ(Wβhᵢ)

hᵢ⁽ˡ⁺¹⁾ = LN { hᵢ⁽ˡ⁾ + Dropout[ Σᵣ βᵢᵣ⁽ˡ⁾mᵢᵣ⁽ˡ⁾ ] }

节点自信息由残差保留；空邻居产生零消息。当前实现采用两层传播。

关系权重因候选而异：由当前节点表示计算，使不同步骤利用不同关系通道。

## 第25页 3.2.2 候选相关上下文、监督与推断（1/2）

候选相关上下文与融合评分

每个待排序步骤作为查询，在同一轨迹全部有效步骤上聚合上下文，包含自身，不
访问其他轨迹。

αᵢⱼ = softmaxⱼ[(WQhᵢ)ᵀWKhⱼ / √d]，   zᵢ = Σⱼ αᵢⱼ WVhⱼ

cᵢ = h̄ + WO(zᵢ − WVh̄)

sᵢ = MLP[ hᵢ ; hᵢ⁽⁰⁾ ; cᵢ ; hᵢ − cᵢ ]

同一段历史对不同候选具有不同权重，全轨迹均值保留为基准。关系表示、初始表
示与候选上下文共同形成一个分数。

全局注意力具有随步骤数增长的二次计算与存储开销；长轨迹必须报告耗时、峰值
显存和截断比例。

## 第26页 3.2.2 候选相关上下文、监督与推断（2/2）

监督目标、推断与解释边界

当前主实验使用单个标注责任步骤i*，在同一轨迹内归一化并训练。

p(q,i) = exp[s(q,i)] / Σⱼ exp[s(q,j)]

L = − (1/N) Σq log p(q,i*)

πq = argsortᵢ[−s(q,i)]

该目标与轨迹内位置分类交叉熵等价。非标注步骤之间没有完整真实次序监督；多
正例语义需另行定义，主实验不混用。

推断输出全步骤检查次序，便于按证据预算选取前若干项。分数用于轨迹内比较，
不解释为因果责任概率。

## 第27页 3.3 从历史排序到当前恢复证据（1/2）

历史责任位置如何成为当前可用证据

01

保留历史来源： 每条证据保存原始步骤索引、历史动作及对象、关联上下
文和映射状态，使诊断结果能够追溯到原始轨迹。

02

对齐当前对象： 区分对象仍存在、对象已变化和无法可靠对应。对象变化
时重新读取当前内容，旧行号和旧文本不直接成为可应用编辑。

03

组织有限证据： 按排序扫描可映射项，合并相同动作或对象并保留来源；
无法可靠映射的项可作解释线索，不自动触发撤销。

## 第28页 3.3 从历史排序到当前恢复证据（2/2）

条数与token约束下的证据接口

恢复器联合任务要求Q、当前状态Sₜ、公开反馈Fₜ与排序证据Eₜ，提出当前可执行
动作。

Eₜ = Select(Kₜ, Cₑ) { M(x[π(j)], Sₜ, Fₜ) : j = 1,…,m }

aₜ ∼ G(Q, Sₜ, Fₜ, Eₜ)

Kₜ限制证据条数，Cₑ限制证据token。确认前固定扫描、合并、截断及解释性证据
计数规则，记录实际可用条数与token。

基本设置只在初始失败轨迹上排序一次，逐轮更新对象映射与反馈。不同排序若映
射成相同证据，其作用可能被接口吸收，需直接记录。

## 第29页 3.4 公开反馈驱动的迭代执行恢复（1/2）

组织当前证据
责任排序、对象映射
最新公开失败反馈

生成候选动作
基于当前代码
动态提出修复

隔离执行与验证
检查可应用性
观察目标与既有行为

判断接纳并更新状态
通过保护条件则接纳
否则保留此前状态

继续时记录反馈并重新映射
原排序固定
当前状态与反馈更新

完成或资源截止
按公开规则选择交付

独立验收
结果仅用于评价

图3-3 诊断证据、公开反馈与行为保护共同驱动恢复

接纳约束为 B ∪ Hₜ ⊆ Pass(S′)。回退不重置时间和token，独立验收不用于挑选历史候
选。

## 第30页 3.4 公开反馈驱动的迭代执行恢复（2/2）

执行规则与验收隔离

动作生成。 从当前已接纳状态出发，结合尚未满足的要求、优先证据和最新公
开反馈提出候选修正。软件任务主要修改当前代码，仅对具有明确语义的操作
采用受控撤销。

隔离执行与公开验证。 候选在独立副本中应用，统一检查编辑格式、对象及唯
一匹配位置。解析失败、不可应用、执行异常和验证不确定分别记录，并可反
馈给下一轮。

接纳、停止与交付。 满足保护条件才更新状态，否则保留此前状态与拒绝反馈。
达到完成条件、迭代或资源上限时，按固定公开规则选定一个交付状态；独立
验收不返回生成器。

## 第31页 3.5 行为身份保护与候选接纳（1/2）

保护集合的初值、接纳与更新

B为初始已通过的回归行为，G为公开目标集合，Hₜ为已接纳且需保留的目标身份。

H₀ = G ∩ Pass(S₀)

Accept(S′ | Sₜ) = 𝟙[ B ∪ Hₜ ⊆ Pass(S′) ]

Hₜ₊₁ = Hₜ ∪ { G ∩ Pass(S′) }，仅在接纳后更新

拒绝时保持Sₜ和Hₜ。行为身份来自固定验证定义，候选不得编辑测试以改变保护对
象，缺失或不确定结果不算通过。

允许满足保护条件但暂未新增目标的中性候选；完全相同状态去重。公开完成则交
付当前状态，否则按预定规则选择已接纳状态。

## 第32页 3.5 行为身份保护与候选接纳（2/2）

已接纳状态

目标甲、丙通过

目标通过数：2

新候选状态

目标甲、乙通过

目标通过数：2

按数量保护： 目标总数未减少，可以接纳。丙失效被乙新增掩盖。

按身份保护： 原已通过的丙必须保留，因此拒绝该候选。保护可能同时阻止需要暂时
退步的有效路径。

示例仅解释规则。实验需共同报告独立退化、拒绝路径、验证成本和最终恢复效果。

## 第33页 3.6 模块接口与实现范围

•

可替换接口： 排序输出索引、分数与次序；映射输出对象对应、证据与来源；
生成和验证记录动作与资源；状态接口保存接纳原因和交付选择。

•

现有原型： 已有语义关系排序、候选相关上下文、排序接入、反馈修复与状态
记录，为正式比较提供实施基础。

•

拟完善机制： 统一证据token预算、行为身份、重复候选与部署参数，核对排
序模型到实际生成输入的完整对应。

•

后续扩展： 重新诊断、可恢复分支与允许暂时退步的软保护分别作为独立变体。
先完成主要评价，再依据机制事件扩展。

## 第34页 拟解决的关键问题与预期创新



## 第35页 4.1 关系与上下文的有效信息增量

核心问题：多关系与候选上下文是否增加有效信息？ 时序、角色和依赖已用于
归因，仅增加图层或注意力并不能自动证明方法价值。[11,17,18]

拟检验关系传播是否补充跨步骤证据，候选相关聚合是否进一步区分这些证据
对不同位置的作用，从而提高标注步骤排名。

在共同输入与训练划分下，设置去关系、统一全局上下文、逐类关系移除及容
量匹配条件，比较MRR、Top-1与端到端成本。单角色关系重合与长轨迹开销
共同限定适用范围。

## 第36页 4.2 历史诊断结果向当前行动的传递

01

诊断信息是否进入恢复： 历史分数经过对象变化、映射和去重后，可能不
再改变生成输入。保留排序、实际证据和请求，核实信息传递。

02

输入改变是否带来行动差异： 固定生成器、证据预算与验证规则，比较本
文排序、StepFinder排序、时间次序和顺序置换，观察对象与动作变化。

03

行动差异是否形成恢复收益： 考察首次有效进展、预算内恢复率与总资源。
证据变化、动作变化与最终成功分别报告，不从诊断指标直接推定行动收
益。

## 第37页 4.3 进展保持与探索空间的协调

拟获得的收益

记录具体行为身份，减少“总数相
同、行为替换”的接纳损害。

在相同保护范围与验证下，比较数
量规则和身份规则，观察退化、拒
绝与后续修复路径。

需要检验的代价

严格保护可能增加验证成本，或阻
止必须暂时退步的有效路径。

自然任务评价总体恢复，受控场景
解释接纳差异。公开指标按规则恒
零时，仍需独立验收与成本证据。

## 第38页 4.4 预期方法贡献与验证边界

预期贡献一

面向责任步骤排序的语义、多关系
与候选上下文联合评分方法。

贡献由共同监督下的诊断质量和效
率增量支持，分别说明关系冗余与
计算代价。

预期贡献二

由排序证据、当前反馈与行为身份
约束共同支持的执行恢复方法。

建立历史步骤到当前对象、动作与
验证结果的对应，通过完整系统与
机制对照评价效用。

最终创新性与有效性以共同任务上的正式比较为依据，当前原型与开发结果提供继续验证的基础。

## 第39页 数据来源与实验设计



## 第40页 5.1 数据构造与训练、验证和确认划分（1/3）

表5-1 数据来源、规模与当前研究样本

数据来源	原始发布规模	本研究已整理样本	用途
AFTraj	2,276条轨迹：正常
1,162、失败1,114；覆
盖math、coding、
agentic [41]	731条失败轨迹 / 716个
源任务组；其中120条、
120组用于开发	责任步骤排序；任务类
型与轨迹结构分析
AgenTracer
 coding	采用扩展发布版：
coding官方训练1,141
条、测试127条 [42]	614条训练验证池：
coding 320、math 294；
固定coding评价363条	软件相关诊断评价；训
练划分稳健性
SWE-Gym
与
OpenHands
轨迹	SWE-Gym共2,438个
Python软件问题 [35]	23个不同issue的恢复来
源池	恢复开发、纳入资格与
资源校准

## 第41页 5.1 数据构造与训练、验证和确认划分（2/3）

表5-2 训练、验证、开发评价与独立确认设计

数据与阶段	训练与模型选择	评价安排	独立性与规模说明
AFTraj开发	716组五折；外层训练内
再分训练/验证；3次初始
化	外层组外预测，汇总
731条轨迹	内部验证调参；已用于研究选择
的结果属开发评价
AFTraj确认	冻结结构、训练流程与输
入定义	官方测试163条失败轨
迹作为候选	先审查任务重叠与历史曝光；合
格数据实报告
AgenTracer
开发	划分A/B/C；各492训练、
122验证；各3次初始化	共同363条coding评价
集	训练、验证、评价源任务隔离；
评价集已参与开发
AgenTracer
确认	固定开发阶段的训练与选
择规则	官方coding测试127条
作为候选	完成身份与曝光审查后冻结；不
按确认结果重选模型
执行恢复	23个已整理issue用于开发
与预算校准	同来源新增未参与开发
的合格issue	固定任务与初态；实际纳入数为
分母；自然与受控状态分报

## 第42页 5.1 数据构造与训练、验证和确认划分（3/3）

任务分组与数据隔离

同一原始问题的多条轨迹、错误变
体和派生样本放入同组。训练、验
证、评价按源任务身份隔离。

已用于开发的120条AFTraj及363条
AgenTracer评价轨迹，不重新称为
未曝光确认集。

恢复样本与纳入规则

计划新增20个未参与开发的合格
issue，覆盖至少3个仓库。按预定
顺序核验可恢复初态、公开反馈、
独立验收及身份无重叠。

自然失败与受控构造状态分开报告；
不足时列原因，不按方法胜负挑题。

AFTraj开发子集120条：coding 24、math 48、agentic 48；恢复来源池23个issue承担开发与资源校准。

## 第43页 5.2 实验流程与共同运行条件（1/3）

来源、纳入与分组
开发数据与独立确认隔离
按源任务控制重复

固定方法与共同条件
输入、验证、内部参数
预算与预定重复

RQ1 诊断与效率
组内训练、折外预测
MRR、Top-1与总开销

模型到恢复输入核对
训练隔离、排序产物
实际证据与生成请求

RQ2 完整恢复比较
本文、Agentless
EnAgent、AOrchestra

机制与统计解释
排序替换、保护控制
任务级配对与不确定性

图5-1 排序、完整恢复与机制分析的实验流程

计划20个未曝光issue、每题三次重复。完整方法与主要机制确认分别估算资源，各预算
节点使用共同可观测分母。

## 第44页 5.2 实验流程与共同运行条件（2/3）

排序训练与模型选择

冻结编码器，两层关系传播，隐维
96，dropout 0.15。AdamW学习
率由内部验证在10⁻⁴、3×10⁻⁴、
10⁻³中选择，最多80轮，MRR连
续10轮无改善时停止。

相同选择信息与可比训练资源，记
录各次初始化、编码截断及端到端
开销。

恢复部署与输入核对

使用共同deepseek-flash生成后端，
本地诊断模型单列。保留各方法定
位、生成、验证与选择核心，说明
从失败中间状态启动的适配。

核对选定模型与训练清单、排序产
物、恢复器读取、实际生成请求，
确认训练无任务重叠。

以上为拟采用配置。正式确认前冻结模型、预处理、内部参数与资源规则。

## 第45页 5.2 实验流程与共同运行条件（3/3）

表5-3 完整恢复实验的共同条件

条件	统一设置	记录与核对内容
任务起点	同一任务描述、仓库版本与失败状态	初态、原始轨迹与允许访问的公开观察
模型与工具	使用共同生成后端；本地诊断模型另行
记录	生成参数、模型版本、上下文限制及工具权限
验证	同一公开验证许可与最终独立验收标准	每次公开检查、最终交付结果及验收结果
算法部署	保留各方法核心阶段，固定内部参数	候选规模、迭代次数、选择规则及与论文配置
的差异
资源	共同时间与token上限，统一计量边界	所有子智能体、候选生成和验证环节的累计使
用量
重复	每个issue按预先确定的规则运行三条独
立完整轨迹	全部重复的终态、预算内结果、异常和删失原
因

## 第46页 5.3 比较方法与实验分工（1/3）

表5-4 责任排序比较方法及评价范围

方法	原有诊断机制	可直接比较的输出与指标
本文责任排序	步骤语义、多关系交互、候选相关
上下文与列表式训练	完整步骤次序；Top-1、Top-3、Top-5、
MRR及效率
StepFinder	时序语义表示、角色感知交互与步
骤评分	依据原始步骤分数形成次序，采用共同排
序指标及效率口径
All-at-Once	一次阅读完整轨迹，输出责任判断	原生责任位置；Top-1、有效输出率及调
用开销
Binary 
Search	在轨迹区间中递归判断并缩小范围	原生责任位置；Top-1、有效输出率及搜
索开销

## 第47页 5.3 比较方法与实验分工（2/3）

表5-5 完整系统比较与内部控制的分工

实验	方法或条件	回答的问题
完整恢复比较	本文完整方法、Agentless、
EnAgent、AOrchestra	诊断引导恢复与固定流程、多轨迹集成、
动态任务组织的整体差异
诊断模块控制	固定本文恢复器，分别使用本文排
序、StepFinder排序和固定时间次
序；无诊断条件单列	责任排序是否改变证据、动作与恢复结果
反馈与证据控
制	固定生成器、验证与资源，改变反
馈组织、上下文选择及状态映射	诊断信息如何转化为有效恢复行动
状态保护控制	固定候选执行接口，改变行为保护
规则	保护对象与接纳条件对退化、进展及成本
的作用

## 第48页 5.3 比较方法与实验分工（3/3）

诊断比较与完整恢复比较分别设置。 StepFinder、All-at-Once和Binary 
Search提供学习式评分、整体日志阅读与区间搜索参照；Agentless、
EnAgent和AOrchestra提供完整流程参照。[11,12,27,29,30]

完整恢复基线应已正式发表、具有公开核心实现，并适用于共同恢复任务，包
含2026年正式发表的方法。核对论文、作者核心源码与实际部署之间的对应，
明确参数适配。

开发小试核对完整可执行性，确认任务按预定资格纳入。
保留强对手胜出及正常负结果；工程未知和未运行分别报告。固定本文恢复器
的排序替换仅回答模块作用。

## 第49页 5.4 评价指标、资源预算与效率分析（1/4）

表5-6 主要评价指标与统计对象

评价对象	主要指标	统计与解释
步骤级诊断	任务组MRR、Top-1、Hit@3/5、有效输
出率	MRR为排序主指标；单位置方法仅比较Top-1与
有效率
诊断效率	P50/P95耗时、峰值内存、调用/token	含编码、结构与评分；首加载与已加载运行分报
执行恢复	30分钟RSR、其他节点RSR、自然终态成
功率	独立验收当时按公开规则选定的一个交付状态
累计资源	总历时、运行时间、token、调用、验证、
费用	包含失败候选、筛选、选择及全部子智能体
成功成本	完整可观测运行总成本 / 成功次数	计入失败成本；零成功不可估计；删失单列
行为退化	接纳转移、运行级、最终交付退化率	按共同的行为身份评价；空分母不适用
作用机制	证据/动作变化、首次进展、重复及拒绝	检验排序参与决策的过程，以及保护的收益与代价

## 第50页 5.4 评价指标、资源预算与效率分析（2/4）

任务组宏平均与共同可观测分母

诊断先在同一源任务组内平均，再对任务组宏平均。r(q)为最前标注位置的排名，无
效输出取∞。

MRR = (1/G) Σg [(1/|Dg|) Σq∈Dg 1/r(q)]

Hit@k = (1/G) Σg [(1/|Dg|) Σq∈Dg 𝟙[r(q) ≤ min(k,m(q))]]

RSR(B) = (1/J) Σj [(1/R) Σr 𝟙[A(Sⱼᵣ(B)) = 1]]

每个issue预定R = 3次独立完整重复。预算B处评价当时按公开规则选定的一个交付
状态，不取三次最好结果。

缺失时，配对RSR使用各方法均有全部R次可判定结果的共同issue集合J(B)；另报
计划覆盖和缺失原因。

## 第51页 5.4 评价指标、资源预算与效率分析（3/4）

时间与token预算

以30分钟RSR为恢复主指标，同参
数下观察15、60分钟节点。token
拟用20k、40k、80k共同水平，开
发阶段核对完整可实施后冻结。

计时包含编码、排序、映射、生成、
工具、验证与选择。全部子智能体
和失败候选资源均计入。

快照、终态与成本

快照在执行期间保存，运行后才独
立验收，结果不返回生成器。自然
终态单列，续跑保留原累计资源，
不重写原预算成绩。

成功成本 = 完整可观测运行总成本
 / 成功次数，包含失败成本；零成
功不可估计，删失与费用未知单列。

## 第52页 5.4 评价指标、资源预算与效率分析（4/4）

行为退化的评价与解释

共同退化参照。 跨策略评价采用初始回归行为B，以及上一已接纳状态中通过
的公开目标身份；不因某方法实际保护范围较小而缩小评价集合。

接纳转移退化率以具有非空保护集合的已接纳转移为分母，统计其中丢失至少
一项保护身份的转移。同时报告运行级退化与最终交付退化，减少接纳频率不
同带来的误解。

严格身份保护可能在同一确定性公开验证下使退化率按规则为零，因此还需观
察独立验收、拒绝路径、验证成本和恢复效果。被拒绝候选的损害不计为交付
退化。

## 第53页 5.5 消融实验与诊断到行动的机制分析（1/3）

表5-7 责任排序的消融与敏感性实验

控制因素	比较条件	主要观察
多关系交互	完整模型与去除关系传播的语义评分模
型	关系信息对定位、排名及不同轨迹结构的增量
候选相关上下
文	候选相关聚合与统一全局上下文；补充
去除上下文条件	差异化上下文是否提高候选区分能力
关系类型	分别移除时序、同角色、完整结构签名
或非空动作结构关系并重新训练；事件
配对残差另设关闭条件	各关系的贡献、重合及来源依赖
信息与模型规
模	语义、位置和结构特征控制，并保持可
比表示容量	收益是否来自特定信息，而非仅增加容量
结构与角色敏
感性	对固定模型置换关系端点；在首次出现
规范化之后，一致置换匿名编号并重算
角色编码，保持同角色邻接不变	模型是否依赖正确关系对应，及是否受匿名编
号顺序影响

## 第54页 5.5 消融实验与诊断到行动的机制分析（2/3）

表5-8 执行恢复的控制实验

控制因素	比较条件	主要观察
诊断来源与顺
序	本文排序、StepFinder排序、时间
次序；另设无诊断与责任次序置换	选中证据、修改对象、首次有效进展、
RSR及总资源
诊断与反馈协
同	有无诊断 × 有无显式结构化反馈包，
形成四个条件	诊断与最新失败反馈是否具有互补作用
恢复上下文	关系相关上下文与相同输入预算的
时间邻域上下文	跨步骤关联是否比单纯邻近信息更有价值
历史与当前状
态映射	当前状态对齐的证据与仅使用历史
片段的证据	过时信息、不可应用动作和方向偏移情况
行为保护	既有回归行为保护、按目标通过数
量保护、按目标身份集合保护	接纳差异、已接纳状态退化、任务推进及
验证成本

## 第55页 5.5 消融实验与诊断到行动的机制分析（3/3）

排序替换与无诊断

固定生成器、动作接口、验证和总
资源。本文排序、StepFinder排序、
时间次序与置换采用共同证据条数
上限、映射规则和token上限，报
告实际用量。

无诊断移除历史归因证据，保留任
务、当前代码及原生反馈，衡量整
个历史证据接口的增量。

反馈组织与机制记录

有无诊断 × 有无显式结构化反馈包
形成四条件；去除反馈包仍保留工
具原生观察与公开验证，避免关闭
验证器混入比较。

记录责任步骤、证据、动作、反馈、
接纳和交付的对应；受控压力场景
单列，不混入自然任务总体恢复率。

## 第56页 5.6 稳健性、有效性与后续扩展（1/2）

稳健性与结论范围

01

统计单位： 以源任务或issue为单位，保留全部预定重复，采用分组配对
bootstrap和95%置信区间；小样本同时列逐题结果。

02

主要分层： 预设轨迹长度与初始保护行为规模，阈值由开发数据确定。角
色数、关系重合、任务类型和反馈具体程度作描述性分析。

03

有效性控制： 核查源任务隔离、信息许可、基线核心、动作接口、预算边
界和验收隔离。开发、单题与部分配对结果明确证据范围。

## 第57页 5.6 稳健性、有效性与后续扩展（2/2）

主要研究承诺的资源估算

完整方法比较

20个issue × 4方法 × 3重复

240条运行

30分钟节点：最多120串行小时

主要机制确认

20个issue × 2新增条件 × 3重复

另120条运行

30分钟节点：最多60串行小时

复用与扩展规则： 相同配置的本文条件直接复用。15/30/60分钟快照按最大节点计费；
token前缀仅在规划不依赖剩余预算时复用。先核开发费用，再分批推进，扩展后置。

## 第58页 研究基础、进度安排与预期成果



## 第59页 6.1 前期研究基础

责任排序的开发基础

AFTraj固定120任务组：本文Top-1
 86/120，强StepFinder 82/120，
差3.33个百分点。

AgenTracer已有614条训练验证来
源池、363条固定开发评价轨迹和
三个分组划分，可分析训练选择变
化。

执行恢复的实施基础

已实现排序接入、当前代码与反馈
组织、候选生成、公开验证和状态
记录。Agentless、EnAgent有完
整运行基础，AOrchestra完整先导
已通过独立验收。

最新排序替换先导完成5条轨迹，
涉及同一个已曝光issue。

以上是开发与可行性证据。仍需未曝光共同任务上的正式比较，尚不能据此确认排序的独立恢复收益。

## 第60页 6.2 研究进度安排

第1—3周

方案与数据

完善术语、监督和指标，审查任务分组与曝光，形成确认
候选清单并核定资源。

第4—8周

责任步骤排序

完成训练、强对照、主要消融与端到端效率分析，固定模
型和预处理。

第9—13周

完整执行恢复

统一对象映射、证据预算、行为保护与交付选择，开展共
同任务完整比较。

第14—17周

机制与稳健性

补齐排序控制、必要保护实验及分层分析，报告全部重复、
负结果和限制。

第18—20周

论文与答辩

综合方法、数据与实验，完善图表、论证和复查材料，完
成论文与答辩稿。

以开题通过所在周为起点，与学校节点衔接。确认阶段固定配置，方法调整另列变体。

## 第61页 6.3 预期研究成果

形成一种基于轨迹内学习排序的步骤级失败诊断方法，明确语义、可观察关系
与候选上下文对责任步骤排名的作用，并报告质量、训练变化和端到端计算代
价。

形成一种由排序证据、当前反馈与行为身份约束共同支持的执行恢复方法，建
立历史步骤、当前对象、动作与验证结果的对应，通过完整比较和固定恢复器
控制评价效用。

交付学位论文、研究原型、数据分组与评价说明，以及可复查实验记录。分别
说明诊断与恢复的证据范围，软件场景中的结果不直接推广为任意系统的因果
诊断或全面容错能力。

## 第62页 主要参考文献

[1] Long Ouyang, Jeff Wu, Xu Jiang, et al. Training language models to follow instructions with human feedback. Advances in 
Neural Information Processing Systems 35, 2022.

[2] Jason Wei, Xuezhi Wang, Dale Schuurmans, et al. Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. 
Advances in Neural Information Processing Systems 35, 2022.

[3] Shunyu Yao, Jeffrey Zhao, Dian Yu, et al. ReAct: Synergizing Reasoning and Acting in Language Models. International 
Conference on Learning Representations (ICLR), 2023.

[4] Qingyun Wu, Gagan Bansal, Jieyu Zhang, et al. AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent 
Conversations. Conference on Language Modeling (COLM 2024).

[5] Sirui Hong, Mingchen Zhuge, Jonathan Chen, et al. MetaGPT: Meta Programming for A Multi-Agent Collaborative 
Framework. International Conference on Learning Representations (ICLR 2024).

[6] Daniil A. Boiko, Robert MacKnight, Ben Kline, et al. Autonomous chemical research with large language models. Nature 624:
570-578, 2023.

[7] Shuyan Zhou, Frank F. Xu, Hao Zhu, et al. WebArena: A Realistic Web Environment for Building Autonomous Agents. 
International Conference on Learning Representations (ICLR 2024).

## 第63页 主要参考文献

[8] Tianbao Xie, Danyang Zhang, Jixuan Chen, et al. OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real 
Computer Environments. Advances in Neural Information Processing Systems 37, Datasets and Benchmarks Track, 2024.

[9] John Yang, Carlos E. Jimenez, Alexander Wettig, et al. SWE-agent: Agent-Computer Interfaces Enable Automated Software 
Engineering. Advances in Neural Information Processing Systems, 2024.

[10] Mert Cemri, Melissa Z Pan, Shuyi Yang, et al. Why Do Multi-Agent LLM Systems Fail? Advances in Neural Information 
Processing Systems, Datasets and Benchmarks Track, 2025.

[11] Taiyu Zhu, Yifan Wu, Weilin Jin, et al. StepFinder: A Temporal Semantic Framework for Failure Attribution in Multi-Agent 
Systems. Proceedings of the 32nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2: 6946–6957, 2026.

[12] Shaokun Zhang, Ming Yin, Jieyu Zhang, et al. Which Agent Causes Task Failures and When? On Automated Failure 
Attribution of LLM Multi-Agent Systems. Proceedings of the 42nd International Conference on Machine Learning (ICML), 
PMLR 267: 76583–76599, 2025.

[13] Ming Ma, Jue Zhang, Fangkai Yang, et al. DoVer: Intervention-Driven Auto Debugging for LLM Multi-Agent Systems. 
International Conference on Learning Representations (ICLR), 2026.

[14] Edward Y. Chang, Longling Geng. SagaLLM: Context Management, Validation, and Transaction Guarantees for Multi-Agent 
LLM Planning. Proceedings of the VLDB Endowment, 18(12): 4874–4886, 2025.

## 第64页 主要参考文献

[15] Yu Zhuang, Kefei Chen, Yitong Duan, et al. AgentRewind: Recoverable Execution for Long-Horizon LLM Agents. arXiv preprint 
arXiv:2608.14380, 2026.

[16] Kai Sun, Wenqiang Li, Bo Dong, et al. Scope Delineation Before Localization: A Two-Stage Framework for Enhancing Failure 
Attribution in Multi-Agent Systems. Proceedings of the AAAI Conference on Artificial Intelligence, 40(39): 33108–33116, 2026.

[17] Md Nakhla Rafi, Md Ahasanuzzaman, Dong Jae Kim, et al. FALAT: Tracing Failures in LLM Agent Trajectories via 
Dependency-Guided Search. arXiv preprint arXiv:2606.00765, 2026.

[18] Bo Deng, Xinlei Zheng, Yi Wei, et al. DeFA: Dependency-Guided Failure Attribution for LLM Agents. arXiv preprint arXiv:
2610.01256, 2026.

[19] Fanqi Kong, Ruijie Zhang, Huaxiao Yin, et al. Aegis: Automated Error Generation and Attribution for Multi-Agent Systems. 
International Conference on Learning Representations (ICLR), 2026.

[20] Guibin Zhang, Junhao Wang, Junjie Chen, et al. AgenTracer: Who Is Inducing Failure in the LLM Agentic Systems? International 
Conference on Learning Representations (ICLR), 2026.

[21] Mengzhuo Chen, Junjie Wang, Fangwen Mu, et al. Seeing the Whole Elephant: A Benchmark for Failure Attribution in LLM-based 
Multi-Agent Systems. Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers
): 19888–19905, 2026.

## 第65页 主要参考文献

[22] Aman Madaan, Niket Tandon, Prakhar Gupta, et al. Self-Refine: Iterative Refinement with Self-Feedback. Advances in 
Neural Information Processing Systems, 36, 2023.

[23] Noah Shinn, Federico Cassano, Ashwin Gopinath, et al. Reflexion: Language Agents with Verbal Reinforcement Learning. 
Advances in Neural Information Processing Systems, 2023.

[24] Zhibin Gou, Zhihong Shao, Yeyun Gong, et al. CRITIC: Large Language Models Can Self-Correct with Tool-Interactive 
Critiquing. International Conference on Learning Representations (ICLR), 2024.

[25] Jie Huang, Xinyun Chen, Swaroop Mishra, et al. Large Language Models Cannot Self-Correct Reasoning Yet. International 
Conference on Learning Representations (ICLR), 2024.

[26] Yi Yu, Liuyi Yao, Yaliang Li, et al. Rollback the World, Keep the Reflection: Rollback-Induced Reflection for Long-Horizon 
LLM Agents. arXiv preprint arXiv:2609.18304, 2026.

[27] Chunqiu Steven Xia, Yinlin Deng, Soren Dunn, et al. Demystifying LLM-Based Software Engineering Agents. Proceedings 
of the ACM on Software Engineering, 2(FSE): 801–824, 2025.

[28] Hongwei Li, Yuheng Tang, Shiqi Wang, et al. PatchPilot: A Cost-Efficient Software Engineering Agent with Early Attempts 
on Formal Verification. Proceedings of the 42nd International Conference on Machine Learning (ICML), PMLR 267: 35922–
35941, 2025.

## 第66页 主要参考文献

[29] Zhao Tian, Pengfei Gao, Junjie Chen, et al. Agent-Based Ensemble Reasoning for Repository-Level Issue Resolution. 
Proceedings of the IEEE/ACM 48th International Conference on Software Engineering (ICSE): 1406–1418, 2026.

[30] Jianhao Ruan, Zhihao Xu, Yiran Peng, et al. AOrchestra: Automating Sub-Agent Creation for Agentic Orchestration. 
Proceedings of the 43rd International Conference on Machine Learning (ICML), PMLR 306: 106017–106040, 2026.

[31] Xuehang Guo, Xingyao Wang, Yangyi Chen, et al. SyncMind: Measuring Agent Out-of-Sync Recovery in Collaborative 
Software Engineering. Proceedings of the 42nd International Conference on Machine Learning (ICML), PMLR 267: 20993–
21066, 2025.

[32] Pan Wang, Yihao Hu, Hang Wang, et al. Diagnosis Before Recovery: Turning Agent Failures into Selective Self-Correction. 
arXiv preprint arXiv:2608.11772, 2026.

[33] Rakshith Vasudev, Melisa Russak, Dan Bikel, et al. The Intervention Paradox: Accurate Failure Prediction in Agents Does 
Not Imply Effective Failure Prevention. arXiv preprint arXiv:2602.03338, 2026.

[34] Carlos E. Jimenez, John Yang, Alexander Wettig, et al. SWE-bench: Can Language Models Resolve Real-world GitHub 
Issues? International Conference on Learning Representations (ICLR), 2024.

[35] Jiayi Pan, Xingyao Wang, Graham Neubig, et al. Training Software Engineering Agents and Verifiers with SWE-Gym. 
Proceedings of the 42nd International Conference on Machine Learning (ICML), PMLR 267: 47717–47737, 2025.

## 第67页 主要参考文献

[36] Zhe Cao, Tao Qin, Tie-Yan Liu, et al. Learning to Rank: From Pairwise Approach to Listwise Approach. Proceedings of the 
24th International Conference on Machine Learning (ICML): 129–136, 2007.

[37] Michael Schlichtkrull, Thomas N. Kipf, Peter Bloem, et al. Modeling Relational Data with Graph Convolutional Networks. 
The Semantic Web (ESWC), Lecture Notes in Computer Science: 593–607, 2018.

[38] Hector Garcia-Molina, Kenneth Salem. Sagas. Proceedings of the ACM SIGMOD International Conference on Management 
of Data: 249–259, 1987.

[39] Xingzuo Li, Kehai Chen, Yunfei Long, et al. Generator-Assistant Stepwise Rollback Framework for Large Language Model 
Agent. Proceedings of the Conference on Empirical Methods in Natural Language Processing (EMNLP): 17683–17700, 2025.

[40] Zhisong Zhang, Tianqing Fang, Kaixin Ma, et al. WebRollback: Enhancing Web Agents with Explicit Rollback Mechanisms. 
Proceedings of the Conference of the European Chapter of the Association for Computational Linguistics (Volume 2: Short Papers)
: 187–197, 2026.

[41] ZBox008003. AFTraj dataset card. Hugging Face, 数据集说明，2026年10月13日访问.

[42] AgenTracer authors. AgenTracer expanded dataset release, data-v1.0.0. GitHub, 数据发布说明，2026年10月13日访问.

## 第68页 感谢聆听，敬请指正




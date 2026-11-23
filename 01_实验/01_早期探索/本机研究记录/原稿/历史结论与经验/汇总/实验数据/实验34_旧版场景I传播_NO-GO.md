# 实验34数据与审计附件

- 当前严格状态：**NO-GO**
- 原编号：`旧版场景I`
- 机器资产：`实验/实验34_旧版场景I传播/`
- 主结论：`结论/结论34_实验34_旧版场景I传播_NO-GO.md`

本文件保存详细指标、原结果摘录和审阅证据；研究判断以主结论为准。

## 原实验结果与指标

以下内容直接并入原结果/报告；它们保留当时数字和判断，但最终等级以本文件开头的严格状态为准。

### 来源：历史__旧版场景I_故障传播到责任动作定位__real_feasibility_propagation__results__feasibility_report.md

### 故障传播到责任动作定位：真实可行性 Pilot 报告

#### 结论先行

预注册主 Gate 决策：**NO-GO**。该结论只基于 protocol.json 冻结的任务级折外预测、六个条件和 task-cluster paired bootstrap；不是把数据集责任标注包装成因果证明。

公平比较中，Predicted Propagation 相对 Predicted Agent-only 的 MRR 为 -0.0066（相对 -0.89%），CI 为 [-0.012075705800475463, -0.0006207359648416409]。

#### 1. 数据审计与纳入规则

原始文件共 6257 条；纳入六种多智能体框架 2670 条，展开后候选事件 14792 个；原始任务指纹 1069 个，其中有重复 rollout 的任务簇 742 个。映射行数 2670，映射率 100.00%。

MacNet 使用 accepted_predictions 的多金标集合；Magentic-One、MetaGPT、MathChat 使用公开的 Agent+位置字段；Debate/Dylan 只有 round+Agent 集合，因此不能伪装成唯一动作金标。所有 ground_truth 字段仅用于训练标签与评价，未进入特征。

显式错误词命中 3225 次；is_injected/is_replayed 事件文本丢弃 7031 个，但事件本身仍保留为候选。角色名按首次出现顺序匿名化。

#### 2. 研究逻辑

RQ1 的上游信息是：错误引入或继续传播的事件是否能从可观察的全过程证据、时序变化和依赖聚合中产生软概率。RQ2 的桥接问题是：这些传播软概率是否比‘只知道哪个 Agent 可疑’更能找到责任动作。No Prior、Predicted Agent-only、Predicted Propagation 的差异只在先验组件，候选池、文本清洗、预算和折划分一致。

Oracle Propagation 不是循环论证：它使用 gold source 只确定下游可观察依赖链的候选上界；具体动作分数来自链上实测的 incoming/outgoing token-dependency strength。源动作没有固定常量高分，也未使用距 gold step 的位置、mode 或注入模板。Shuffled Propagation 在同一外层折、同框架且近似候选规模内置换传播组件。

#### 3. 主要结果（原始分数）

| 条件 | MRR | Recall@1 | Recall@3 | Recall@5 | 症状/末步误判 |
|---|---:|---:|---:|---:|---:|
| No Prior | 0.7299（95% CI [0.7326, 0.7626]） | 0.5869（95% CI [0.5660, 0.6154]） | 0.8700（95% CI [0.8990, 0.9247]） | 0.9408（95% CI [0.9556, 0.9713]） | 0.3165（95% CI [0.2555, 0.3005]） |
| Predicted Agent-only | 0.7369（95% CI [0.7334, 0.7649]） | 0.5895（95% CI [0.5645, 0.6165]） | 0.8640（95% CI [0.8919, 0.9182]） | 0.9498（95% CI [0.9589, 0.9746]） | 0.3307（95% CI [0.2772, 0.3228]） |
| Predicted Propagation | 0.7300（95% CI [0.7266, 0.7572]） | 0.5843（95% CI [0.5614, 0.6106]） | 0.8513（95% CI [0.8722, 0.9011]） | 0.9416（95% CI [0.9508, 0.9676]） | 0.3255（95% CI [0.2752, 0.3204]） |
| Shuffled Propagation | 0.7300（95% CI [0.7272, 0.7573]） | 0.5843（95% CI [0.5622, 0.6119]） | 0.8513（95% CI [0.8716, 0.9004]） | 0.9416（95% CI [0.9506, 0.9678]） | 0.3255（95% CI [0.2758, 0.3202]） |
| Oracle Agent | 0.8420（95% CI [0.8698, 0.8922]） | 0.7322（95% CI [0.7736, 0.8124]） | 0.9397（95% CI [0.9529, 0.9688]） | 0.9865（95% CI [0.9885, 0.9948]） | 0.2610（95% CI [0.1824, 0.2209]） |
| Oracle Propagation | 0.8395（95% CI [0.8675, 0.8910]） | 0.7281（95% CI [0.7696, 0.8087]） | 0.9494（95% CI [0.9618, 0.9754]） | 0.9869（95% CI [0.9888, 0.9950]） | 0.2558（95% CI [0.1791, 0.2161]） |

#### 4. 预注册 Gate 对照

##### Predicted Propagation vs Predicted Agent-only
- MRR：绝对差 -0.0066；相对差 -0.89%；task-cluster paired 95% CI [-0.0121, -0.0006]。
- Recall@1：绝对差 -0.0030；相对差 -0.50%；task-cluster paired 95% CI [-0.0131, 0.0076]。
- Recall@3：绝对差 -0.0185；相对差 -2.14%；task-cluster paired 95% CI [-0.0293, -0.0080]。
- Recall@5：绝对差 -0.0074；相对差 -0.78%；task-cluster paired 95% CI [-0.0131, -0.0020]。

##### Shuffled Propagation vs Predicted Agent-only
- MRR：绝对差 -0.0066；相对差 -0.89%；task-cluster paired 95% CI [-0.0125, -0.0008]。
- Recall@1：绝对差 -0.0030；相对差 -0.50%；task-cluster paired 95% CI [-0.0133, 0.0076]。
- Recall@3：绝对差 -0.0185；相对差 -2.14%；task-cluster paired 95% CI [-0.0297, -0.0081]。
- Recall@5：绝对差 -0.0074；相对差 -0.78%；task-cluster paired 95% CI [-0.0135, -0.0018]。

##### Oracle Agent vs Predicted Agent-only
- MRR：绝对差 0.1324；相对差 17.97%；task-cluster paired 95% CI [0.1193, 0.1456]。
- Recall@1：绝对差 0.2035；相对差 34.51%；task-cluster paired 95% CI [0.1828, 0.2262]。
- Recall@3：绝对差 0.0559；相对差 6.47%；task-cluster paired 95% CI [0.0464, 0.0662]。
- Recall@5：绝对差 0.0250；相对差 2.63%；task-cluster paired 95% CI [0.0189, 0.0316]。

##### Oracle Propagation vs Predicted Agent-only
- MRR：绝对差 0.1306；相对差 17.72%；task-cluster paired 95% CI [0.1175, 0.1443]。
- Recall@1：绝对差 0.2000；相对差 33.92%；task-cluster paired 95% CI [0.1771, 0.2221]。
- Recall@3：绝对差 0.0636；相对差 7.36%；task-cluster paired 95% CI [0.0535, 0.0743]。
- Recall@5：绝对差 0.0253；相对差 2.66%；task-cluster paired 95% CI [0.0185, 0.0325]。

##### No Prior vs Predicted Agent-only
- MRR：绝对差 -0.0006；相对差 -0.08%；task-cluster paired 95% CI [-0.0060, 0.0049]。
- Recall@1：绝对差 0.0007；相对差 0.12%；task-cluster paired 95% CI [-0.0079, 0.0097]。
- Recall@3：绝对差 0.0068；相对差 0.79%；task-cluster paired 95% CI [0.0003, 0.0133]。
- Recall@5：绝对差 -0.0034；相对差 -0.35%；task-cluster paired 95% CI [-0.0098, 0.0034]。

##### Oracle Propagation vs Oracle Agent-only
- MRR：绝对差 -0.0018；相对差 -0.22%；task-cluster paired 95% CI [-0.0036, -0.0004]。

- 公平 Gate 至少一个主要指标满足相对提升≥10%且 CI 下界>0：[]。
- Oracle Propagation > Oracle Agent-only：False。
- Shuffled 不复现增益：False；所有条件 gold coverage=1：True。

#### 5. 与近期论文的边界与更进一步

Who&When（ICML 2025 正式论文，https://proceedings.mlr.press/v267/zhang25cq.html；预印本 https://arxiv.org/abs/2505.00212）提供责任 Agent/步骤任务；本 Pilot 不重复声称谁/何时定位，而是测试传播先验对动作排序的增量。
TraceElephant（ACL 2026 Long，https://aclanthology.org/2026.acl-long.912/；https://arxiv.org/abs/2604.22708）使用全量输入、输出、工具和系统上下文；本 Pilot 借鉴其可观测视图，但限制为可审计的轻量事件表示。
FALAT（https://arxiv.org/abs/2606.00765）已经涉及 typed dependency、source/propagation/symptom/contributing 角色和 dependency-guided ranking；本 Pilot 不把依赖图、传播/症状标签或反向追踪当成单点创新，更进一步仅在新数据组合上检验 strict task-OOF 的增量价值。
TrajDebug（https://arxiv.org/abs/2608.06346）已经研究错误生命周期、恢复和终局影响；Causal Agent Replay（https://arxiv.org/abs/2606.08275）已经研究 do-intervention、重放和置信区间；ErrorProbe（https://arxiv.org/abs/2604.17658）已经研究症状驱动反向追踪和可执行验证。它们是必须正面比较的邻近工作，而不是被忽略的‘空白’。本 Pilot 暂只做离线 Gate，不能把排序结果称为因果根因；后续若进入论文，需要执行重放/替换验证。

#### 6. 可复现性与风险

运行命令、协议、数据 SHA256、每任务预测、失败案例和测试均保存在本目录。模型为标准库线性证据模型，训练严格按任务簇折外；不是大模型 SOTA。主要威胁是 WhoWhenPro 的责任标签不是人工动作干预因果标签，Debate/Dylan 的集合金标也不具备唯一动作语义；因此本报告把结果称为‘离线增量可行性’，不替代后续可执行干预。

### 来源：历史__旧版场景I_故障传播到责任动作定位__real_feasibility_propagation__results_v1_fixed__feasibility_report.md

### 故障传播到责任动作定位：真实可行性 Pilot 报告

#### 结论先行

预注册主 Gate 决策：**NO-GO**。该结论只基于 protocol.json 冻结的任务级折外预测、六个条件和 task-cluster paired bootstrap；不是把数据集责任标注包装成因果证明。

公平比较中，Predicted Propagation 相对 Predicted Agent-only 的 MRR（任务簇宏平均）为 0.0201（相对 2.68%），CI 为 [0.015317176553011718, 0.025184131839250733]。表中均值与 CI 使用同一任务簇宏平均估计量，同时保留 micro_mean 供审计。

#### 1. 数据审计与纳入规则

原始文件共 6257 条；纳入六种多智能体框架 2670 条，展开后候选事件 14792 个；原始任务指纹 1069 个，其中有重复 rollout 的任务簇 742 个。映射行数 2670，映射率 100.00%。

MacNet 使用 accepted_predictions 的多金标集合；Magentic-One、MetaGPT、MathChat 使用公开的 Agent+位置字段；Debate/Dylan 只有 round+Agent 集合，因此不能伪装成唯一动作金标。所有 ground_truth 字段仅用于训练标签与评价，未进入特征。

显式错误词命中 3225 次；is_injected/is_replayed 事件文本丢弃 7031 个，但事件本身仍保留为候选。角色名按首次出现顺序匿名化。

#### 2. 研究逻辑

RQ1 的上游信息是：错误引入或继续传播的事件是否能从可观察的全过程证据、时序变化和依赖聚合中产生软概率。RQ2 的桥接问题是：这些传播软概率是否比‘只知道哪个 Agent 可疑’更能找到责任动作。No Prior、Predicted Agent-only、Predicted Propagation 的差异只在先验组件，候选池、文本清洗、预算和折划分一致。

Oracle Propagation 不是循环论证：它使用 gold source 只确定下游可观察依赖链的候选上界；具体动作分数来自链上实测的 incoming/outgoing token-dependency strength。源动作没有固定常量高分，也未使用距 gold step 的位置、mode 或注入模板。Shuffled Propagation 在同一外层折、同框架且近似候选规模内置换传播组件。

#### 3. 主要结果（原始分数）

| 条件 | MRR | Recall@1 | Recall@3 | Recall@5 | 症状/末步误判 |
|---|---:|---:|---:|---:|---:|
| No Prior | 0.7481（95% CI [0.7326, 0.7626]） | 0.5904（95% CI [0.5660, 0.6154]） | 0.9121（95% CI [0.8990, 0.9247]） | 0.9634（95% CI [0.9556, 0.9713]） | 0.2771（95% CI [0.2555, 0.3005]） |
| Predicted Agent-only | 0.7487（95% CI [0.7334, 0.7649]） | 0.5897（95% CI [0.5645, 0.6165]） | 0.9053（95% CI [0.8919, 0.9182]） | 0.9668（95% CI [0.9589, 0.9746]） | 0.3001（95% CI [0.2772, 0.3228]） |
| Predicted Propagation | 0.7688（95% CI [0.7533, 0.7831]） | 0.6234（95% CI [0.5994, 0.6465]） | 0.9123（95% CI [0.9004, 0.9243]） | 0.9750（95% CI [0.9680, 0.9815]） | 0.2443（95% CI [0.2237, 0.2651]） |
| Shuffled Propagation | 0.7430（95% CI [0.7275, 0.7591]） | 0.5901（95% CI [0.5652, 0.6155]） | 0.8810（95% CI [0.8654, 0.8948]） | 0.9592（95% CI [0.9502, 0.9675]） | 0.2909（95% CI [0.2691, 0.3131]） |
| Oracle Agent | 0.8811（95% CI [0.8698, 0.8922]） | 0.7932（95% CI [0.7736, 0.8124]） | 0.9613（95% CI [0.9529, 0.9688]） | 0.9918（95% CI [0.9885, 0.9948]） | 0.2015（95% CI [0.1824, 0.2209]） |
| Oracle Propagation | 0.8792（95% CI [0.8675, 0.8910]） | 0.7897（95% CI [0.7696, 0.8087]） | 0.9689（95% CI [0.9618, 0.9754]） | 0.9921（95% CI [0.9888, 0.9950]） | 0.1975（95% CI [0.1791, 0.2161]） |

#### 4. 预注册 Gate 对照

##### Predicted Propagation vs Predicted Agent-only
- MRR：绝对差 0.0201；相对差 2.68%；task-cluster paired 95% CI [0.0153, 0.0252]。
- Recall@1：绝对差 0.0337；相对差 5.72%；task-cluster paired 95% CI [0.0248, 0.0428]。
- Recall@3：绝对差 0.0070；相对差 0.77%；task-cluster paired 95% CI [0.0026, 0.0119]。
- Recall@5：绝对差 0.0082；相对差 0.84%；task-cluster paired 95% CI [0.0041, 0.0133]。

##### Shuffled Propagation vs Predicted Agent-only
- MRR：绝对差 -0.0056；相对差 -0.75%；task-cluster paired 95% CI [-0.0117, 0.0004]。
- Recall@1：绝对差 0.0004；相对差 0.07%；task-cluster paired 95% CI [-0.0102, 0.0107]。
- Recall@3：绝对差 -0.0243；相对差 -2.68%；task-cluster paired 95% CI [-0.0361, -0.0131]。
- Recall@5：绝对差 -0.0076；相对差 -0.78%；task-cluster paired 95% CI [-0.0143, -0.0010]。

##### Oracle Agent vs Predicted Agent-only
- MRR：绝对差 0.1324；相对差 17.68%；task-cluster paired 95% CI [0.1193, 0.1456]。
- Recall@1：绝对差 0.2035；相对差 34.50%；task-cluster paired 95% CI [0.1828, 0.2262]。
- Recall@3：绝对差 0.0559；相对差 6.18%；task-cluster paired 95% CI [0.0464, 0.0662]。
- Recall@5：绝对差 0.0250；相对差 2.59%；task-cluster paired 95% CI [0.0189, 0.0316]。

##### Oracle Propagation vs Predicted Agent-only
- MRR：绝对差 0.1306；相对差 17.44%；task-cluster paired 95% CI [0.1175, 0.1443]。
- Recall@1：绝对差 0.2000；相对差 33.91%；task-cluster paired 95% CI [0.1771, 0.2221]。
- Recall@3：绝对差 0.0636；相对差 7.03%；task-cluster paired 95% CI [0.0535, 0.0743]。
- Recall@5：绝对差 0.0253；相对差 2.62%；task-cluster paired 95% CI [0.0185, 0.0325]。

##### No Prior vs Predicted Agent-only
- MRR：绝对差 -0.0006；相对差 -0.08%；task-cluster paired 95% CI [-0.0060, 0.0049]。
- Recall@1：绝对差 0.0007；相对差 0.12%；task-cluster paired 95% CI [-0.0079, 0.0097]。
- Recall@3：绝对差 0.0068；相对差 0.75%；task-cluster paired 95% CI [0.0003, 0.0133]。
- Recall@5：绝对差 -0.0034；相对差 -0.35%；task-cluster paired 95% CI [-0.0098, 0.0034]。

##### Oracle Propagation vs Oracle Agent-only
- MRR：绝对差 -0.0018；相对差 -0.21%；task-cluster paired 95% CI [-0.0036, -0.0003]。
- Recall@1：绝对差 -0.0035；相对差 -0.44%；task-cluster paired 95% CI [-0.0061, -0.0012]。
- Recall@3：绝对差 0.0077；相对差 0.80%；task-cluster paired 95% CI [0.0035, 0.0121]。
- Recall@5：绝对差 0.0003；相对差 0.03%；task-cluster paired 95% CI [-0.0016, 0.0022]。

- 公平 Gate 至少一个主要指标满足相对提升≥10%且 CI 下界>0：[]。
- Oracle Propagation > Oracle Agent-only（至少一个主要指标 CI 下界>0）：True；通过指标：['Recall@3']。
- Shuffled 不复现增益：True；所有条件 gold coverage=1：True。

#### 5. 与近期论文的边界与更进一步

Who&When（ICML 2025 正式论文，https://proceedings.mlr.press/v267/zhang25cq.html；预印本 https://arxiv.org/abs/2505.00212）提供责任 Agent/步骤任务；本 Pilot 不重复声称谁/何时定位，而是测试传播先验对动作排序的增量。
TraceElephant（ACL 2026 Long，https://aclanthology.org/2026.acl-long.912/；https://arxiv.org/abs/2604.22708）使用全量输入、输出、工具和系统上下文；本 Pilot 借鉴其可观测视图，但限制为可审计的轻量事件表示。
FALAT（https://arxiv.org/abs/2606.00765）已经涉及 typed dependency、source/propagation/symptom/contributing 角色和 dependency-guided ranking；本 Pilot 不把依赖图、传播/症状标签或反向追踪当成单点创新，更进一步仅在新数据组合上检验 strict task-OOF 的增量价值。
TrajDebug（https://arxiv.org/abs/2608.06346）已经研究错误生命周期、恢复和终局影响；Causal Agent Replay（https://arxiv.org/abs/2606.08275）已经研究 do-intervention、重放和置信区间；ErrorProbe（https://arxiv.org/abs/2604.17658）已经研究症状驱动反向追踪和可执行验证。它们是必须正面比较的邻近工作，而不是被忽略的‘空白’。本 Pilot 暂只做离线 Gate，不能把排序结果称为因果根因；后续若进入论文，需要执行重放/替换验证。

#### 6. 可复现性与风险

运行命令、协议、数据 SHA256、每任务预测、失败案例和测试均保存在本目录。模型为标准库线性证据模型，训练严格按任务簇折外；不是大模型 SOTA。主要威胁是 WhoWhenPro 的责任标签不是人工动作干预因果标签，Debate/Dylan 的集合金标也不具备唯一动作语义；因此本报告把结果称为‘离线增量可行性’，不替代后续可执行干预。

### 来源：历史__旧版场景I_故障传播到责任动作定位__real_feasibility_propagation__results_v2_diagnostic__feasibility_report.md

### 故障传播到责任动作定位：真实可行性 Pilot 报告

#### 结论先行

预注册主 Gate 决策：**NO-GO**。该结论只基于 protocol.json 冻结的任务级折外预测、六个条件和 task-cluster paired bootstrap；不是把数据集责任标注包装成因果证明。

公平比较中，Predicted Propagation 相对 Predicted Agent-only 的 MRR（任务簇宏平均）为 0.0002（相对 0.04%），CI 为 [-0.004543441891332747, 0.0052022989610850875]。表中均值与 CI 使用同一任务簇宏平均估计量，同时保留 micro_mean 供审计。

#### 1. 数据审计与纳入规则

原始文件共 6257 条；纳入六种多智能体框架 2670 条，展开后候选事件 14792 个；原始任务指纹 1069 个，其中有重复 rollout 的任务簇 742 个。映射行数 2670，映射率 100.00%。

MacNet 使用 accepted_predictions 的多金标集合；Magentic-One、MetaGPT、MathChat 使用公开的 Agent+位置字段；Debate/Dylan 只有 round+Agent 集合，因此不能伪装成唯一动作金标。所有 ground_truth 字段仅用于训练标签与评价，未进入特征。

显式错误词命中 4611 次；is_injected/is_replayed 事件文本丢弃 0 个，但事件本身仍保留为候选。角色名按首次出现顺序匿名化。

#### 2. 研究逻辑

RQ1 的上游信息是：错误引入或继续传播的事件是否能从可观察的全过程证据、时序变化和依赖聚合中产生软概率。RQ2 的桥接问题是：这些传播软概率是否比‘只知道哪个 Agent 可疑’更能找到责任动作。No Prior、Predicted Agent-only、Predicted Propagation 的差异只在先验组件，候选池、文本清洗、预算和折划分一致。

Oracle Propagation 不是循环论证：它使用 gold source 只确定下游可观察依赖链的候选上界；具体动作分数来自链上实测的 incoming/outgoing token-dependency strength。源动作没有固定常量高分，也未使用距 gold step 的位置、mode 或注入模板。Shuffled Propagation 在同一外层折、同框架且近似候选规模内置换传播组件。

#### 3. 主要结果（原始分数）

| 条件 | MRR | Recall@1 | Recall@3 | Recall@5 | 症状/末步误判 |
|---|---:|---:|---:|---:|---:|
| No Prior | 0.6378（95% CI [0.6191, 0.6558]） | 0.4819（95% CI [0.4552, 0.5082]） | 0.7719（95% CI [0.7507, 0.7924]） | 0.9204（95% CI [0.9083, 0.9317]） | 0.5166（95% CI [0.4909, 0.5431]） |
| Predicted Agent-only | 0.6422（95% CI [0.6242, 0.6612]） | 0.4765（95% CI [0.4503, 0.5033]） | 0.8052（95% CI [0.7852, 0.8244]） | 0.9392（95% CI [0.9286, 0.9496]） | 0.5218（95% CI [0.4969, 0.5476]） |
| Predicted Propagation | 0.6424（95% CI [0.6239, 0.6605]） | 0.4841（95% CI [0.4572, 0.5118]） | 0.7814（95% CI [0.7618, 0.8028]） | 0.8886（95% CI [0.8744, 0.9033]） | 0.4910（95% CI [0.4650, 0.5165]） |
| Shuffled Propagation | 0.5414（95% CI [0.5258, 0.5574]） | 0.3200（95% CI [0.2982, 0.3423]） | 0.7443（95% CI [0.7225, 0.7650]） | 0.9243（95% CI [0.9118, 0.9362]） | 0.5269（95% CI [0.5040, 0.5528]） |
| Oracle Agent | 0.7179（95% CI [0.7014, 0.7337]） | 0.5475（95% CI [0.5218, 0.5730]） | 0.9072（95% CI [0.8936, 0.9201]） | 0.9853（95% CI [0.9806, 0.9894]） | 0.4086（95% CI [0.3846, 0.4340]） |
| Oracle Propagation | 0.7182（95% CI [0.7013, 0.7340]） | 0.5568（95% CI [0.5316, 0.5818]） | 0.8809（95% CI [0.8647, 0.8949]） | 0.9823（95% CI [0.9767, 0.9874]） | 0.3807（95% CI [0.3557, 0.4044]） |

#### 4. 预注册 Gate 对照

##### Predicted Propagation vs Predicted Agent-only
- MRR：绝对差 0.0002；相对差 0.04%；task-cluster paired 95% CI [-0.0045, 0.0052]。
- Recall@1：绝对差 0.0077；相对差 1.61%；task-cluster paired 95% CI [0.0035, 0.0122]。
- Recall@3：绝对差 -0.0237；相对差 -2.95%；task-cluster paired 95% CI [-0.0415, -0.0049]。
- Recall@5：绝对差 -0.0506；相对差 -5.38%；task-cluster paired 95% CI [-0.0645, -0.0366]。

##### Shuffled Propagation vs Predicted Agent-only
- MRR：绝对差 -0.1007；相对差 -15.69%；task-cluster paired 95% CI [-0.1158, -0.0849]。
- Recall@1：绝对差 -0.1565；相对差 -32.84%；task-cluster paired 95% CI [-0.1790, -0.1341]。
- Recall@3：绝对差 -0.0609；相对差 -7.56%；task-cluster paired 95% CI [-0.0820, -0.0388]。
- Recall@5：绝对差 -0.0149；相对差 -1.58%；task-cluster paired 95% CI [-0.0249, -0.0048]。

##### Oracle Agent vs Predicted Agent-only
- MRR：绝对差 0.0758；相对差 11.80%；task-cluster paired 95% CI [0.0680, 0.0836]。
- Recall@1：绝对差 0.0710；相对差 14.90%；task-cluster paired 95% CI [0.0572, 0.0852]。
- Recall@3：绝对差 0.1020；相对差 12.67%；task-cluster paired 95% CI [0.0879, 0.1173]。
- Recall@5：绝对差 0.0461；相对差 4.91%；task-cluster paired 95% CI [0.0369, 0.0557]。

##### Oracle Propagation vs Predicted Agent-only
- MRR：绝对差 0.0761；相对差 11.85%；task-cluster paired 95% CI [0.0666, 0.0855]。
- Recall@1：绝对差 0.0804；相对差 16.86%；task-cluster paired 95% CI [0.0645, 0.0958]。
- Recall@3：绝对差 0.0757；相对差 9.40%；task-cluster paired 95% CI [0.0601, 0.0918]。
- Recall@5：绝对差 0.0431；相对差 4.59%；task-cluster paired 95% CI [0.0339, 0.0527]。

##### No Prior vs Predicted Agent-only
- MRR：绝对差 -0.0043；相对差 -0.67%；task-cluster paired 95% CI [-0.0080, -0.0006]。
- Recall@1：绝对差 0.0054；相对差 1.14%；task-cluster paired 95% CI [0.0018, 0.0097]。
- Recall@3：绝对差 -0.0332；相对差 -4.13%；task-cluster paired 95% CI [-0.0499, -0.0159]。
- Recall@5：绝对差 -0.0187；相对差 -2.00%；task-cluster paired 95% CI [-0.0269, -0.0102]。

##### Oracle Propagation vs Oracle Agent-only
- MRR：绝对差 0.0003；相对差 0.04%；task-cluster paired 95% CI [-0.0064, 0.0071]。
- Recall@1：绝对差 0.0093；相对差 1.71%；task-cluster paired 95% CI [-0.0016, 0.0199]。
- Recall@3：绝对差 -0.0263；相对差 -2.90%；task-cluster paired 95% CI [-0.0378, -0.0152]。
- Recall@5：绝对差 -0.0030；相对差 -0.30%；task-cluster paired 95% CI [-0.0077, 0.0013]。

- 公平 Gate 至少一个主要指标满足相对提升≥10%且 CI 下界>0：[]。
- Oracle Propagation > Oracle Agent-only（至少一个主要指标 CI 下界>0）：False；通过指标：[]。
- Shuffled 不复现增益：False；所有条件 gold coverage=1：True。

#### 5. 与近期论文的边界与更进一步

Who&When（ICML 2025 正式论文，https://proceedings.mlr.press/v267/zhang25cq.html；预印本 https://arxiv.org/abs/2505.00212）提供责任 Agent/步骤任务；本 Pilot 不重复声称谁/何时定位，而是测试传播先验对动作排序的增量。
TraceElephant（ACL 2026 Long，https://aclanthology.org/2026.acl-long.912/；https://arxiv.org/abs/2604.22708）使用全量输入、输出、工具和系统上下文；本 Pilot 借鉴其可观测视图，但限制为可审计的轻量事件表示。
FALAT（https://arxiv.org/abs/2606.00765）已经涉及 typed dependency、source/propagation/symptom/contributing 角色和 dependency-guided ranking；本 Pilot 不把依赖图、传播/症状标签或反向追踪当成单点创新，更进一步仅在新数据组合上检验 strict task-OOF 的增量价值。
TrajDebug（https://arxiv.org/abs/2608.06346）已经研究错误生命周期、恢复和终局影响；Causal Agent Replay（https://arxiv.org/abs/2606.08275）已经研究 do-intervention、重放和置信区间；ErrorProbe（https://arxiv.org/abs/2604.17658）已经研究症状驱动反向追踪和可执行验证。它们是必须正面比较的邻近工作，而不是被忽略的‘空白’。本 Pilot 暂只做离线 Gate，不能把排序结果称为因果根因；后续若进入论文，需要执行重放/替换验证。

#### 6. 可复现性与风险

运行命令、协议、数据 SHA256、每任务预测、失败案例和测试均保存在本目录。模型为标准库线性证据模型，训练严格按任务簇折外；不是大模型 SOTA。主要威胁是 WhoWhenPro 的责任标签不是人工动作干预因果标签，Debate/Dylan 的集合金标也不具备唯一动作语义；因此本报告把结果称为‘离线增量可行性’，不替代后续可执行干预。

### 来源：历史__旧版场景I_故障传播到责任动作定位__real_feasibility_propagation__results_v2_diagnostic_pooled__feasibility_report.md

### 故障传播到责任动作定位：真实可行性 Pilot 报告

#### 结论先行

预注册主 Gate 决策：**NO-GO**。该结论只基于 protocol.json 冻结的任务级折外预测、六个条件和 task-cluster paired bootstrap；不是把数据集责任标注包装成因果证明。

公平比较中，Predicted Propagation 相对 Predicted Agent-only 的 MRR（任务簇宏平均）为 0.0002（相对 0.04%），CI 为 [-0.004543441891332747, 0.0052022989610850875]。表中均值与 CI 使用同一任务簇宏平均估计量，同时保留 micro_mean 供审计。

#### 1. 数据审计与纳入规则

原始文件共 6257 条；纳入六种多智能体框架 2670 条，展开后候选事件 14792 个；原始任务指纹 1069 个，其中有重复 rollout 的任务簇 742 个。映射行数 2670，映射率 100.00%。

MacNet 使用 accepted_predictions 的多金标集合；Magentic-One、MetaGPT、MathChat 使用公开的 Agent+位置字段；Debate/Dylan 只有 round+Agent 集合，因此不能伪装成唯一动作金标。所有 ground_truth 字段仅用于训练标签与评价，未进入特征。

显式错误词命中 4611 次；is_injected/is_replayed 事件文本丢弃 0 个，但事件本身仍保留为候选。角色名按首次出现顺序匿名化。

#### 2. 研究逻辑

RQ1 的上游信息是：错误引入或继续传播的事件是否能从可观察的全过程证据、时序变化和依赖聚合中产生软概率。RQ2 的桥接问题是：这些传播软概率是否比‘只知道哪个 Agent 可疑’更能找到责任动作。No Prior、Predicted Agent-only、Predicted Propagation 的差异只在先验组件，候选池、文本清洗、预算和折划分一致。

Oracle Propagation 不是循环论证：它使用 gold source 只确定下游可观察依赖链的候选上界；具体动作分数来自链上实测的 incoming/outgoing token-dependency strength。源动作没有固定常量高分，也未使用距 gold step 的位置、mode 或注入模板。Shuffled Propagation 在同一外层折、同框架且近似候选规模内置换传播组件。

#### 3. 主要结果（原始分数）

| 条件 | MRR | Recall@1 | Recall@3 | Recall@5 | 症状/末步误判 |
|---|---:|---:|---:|---:|---:|
| No Prior | 0.6378（95% CI [0.6191, 0.6558]） | 0.4819（95% CI [0.4552, 0.5082]） | 0.7719（95% CI [0.7507, 0.7924]） | 0.9204（95% CI [0.9083, 0.9317]） | 0.5166（95% CI [0.4909, 0.5431]） |
| Predicted Agent-only | 0.6422（95% CI [0.6242, 0.6612]） | 0.4765（95% CI [0.4503, 0.5033]） | 0.8052（95% CI [0.7852, 0.8244]） | 0.9392（95% CI [0.9286, 0.9496]） | 0.5218（95% CI [0.4969, 0.5476]） |
| Predicted Propagation | 0.6424（95% CI [0.6239, 0.6605]） | 0.4841（95% CI [0.4572, 0.5118]） | 0.7814（95% CI [0.7618, 0.8028]） | 0.8886（95% CI [0.8744, 0.9033]） | 0.4910（95% CI [0.4650, 0.5165]） |
| Shuffled Propagation | 0.5545（95% CI [0.5384, 0.5713]） | 0.3354（95% CI [0.3107, 0.3577]） | 0.7492（95% CI [0.7283, 0.7694]） | 0.9205（95% CI [0.9067, 0.9325]） | 0.5418（95% CI [0.5164, 0.5660]） |
| Oracle Agent | 0.7179（95% CI [0.7014, 0.7337]） | 0.5475（95% CI [0.5218, 0.5730]） | 0.9072（95% CI [0.8936, 0.9201]） | 0.9853（95% CI [0.9806, 0.9894]） | 0.4086（95% CI [0.3846, 0.4340]） |
| Oracle Propagation | 0.7182（95% CI [0.7013, 0.7340]） | 0.5568（95% CI [0.5316, 0.5818]） | 0.8809（95% CI [0.8647, 0.8949]） | 0.9823（95% CI [0.9767, 0.9874]） | 0.3807（95% CI [0.3557, 0.4044]） |

#### 4. 预注册 Gate 对照

##### Predicted Propagation vs Predicted Agent-only
- MRR：绝对差 0.0002；相对差 0.04%；task-cluster paired 95% CI [-0.0045, 0.0052]。
- Recall@1：绝对差 0.0077；相对差 1.61%；task-cluster paired 95% CI [0.0035, 0.0122]。
- Recall@3：绝对差 -0.0237；相对差 -2.95%；task-cluster paired 95% CI [-0.0415, -0.0049]。
- Recall@5：绝对差 -0.0506；相对差 -5.38%；task-cluster paired 95% CI [-0.0645, -0.0366]。

##### Shuffled Propagation vs Predicted Agent-only
- MRR：绝对差 -0.0877；相对差 -13.65%；task-cluster paired 95% CI [-0.1026, -0.0728]。
- Recall@1：绝对差 -0.1410；相对差 -29.60%；task-cluster paired 95% CI [-0.1641, -0.1178]。
- Recall@3：绝对差 -0.0560；相对差 -6.95%；task-cluster paired 95% CI [-0.0771, -0.0336]。
- Recall@5：绝对差 -0.0187；相对差 -1.99%；task-cluster paired 95% CI [-0.0288, -0.0085]。

##### Oracle Agent vs Predicted Agent-only
- MRR：绝对差 0.0758；相对差 11.80%；task-cluster paired 95% CI [0.0680, 0.0836]。
- Recall@1：绝对差 0.0710；相对差 14.90%；task-cluster paired 95% CI [0.0572, 0.0852]。
- Recall@3：绝对差 0.1020；相对差 12.67%；task-cluster paired 95% CI [0.0879, 0.1173]。
- Recall@5：绝对差 0.0461；相对差 4.91%；task-cluster paired 95% CI [0.0369, 0.0557]。

##### Oracle Propagation vs Predicted Agent-only
- MRR：绝对差 0.0761；相对差 11.85%；task-cluster paired 95% CI [0.0666, 0.0855]。
- Recall@1：绝对差 0.0804；相对差 16.86%；task-cluster paired 95% CI [0.0645, 0.0958]。
- Recall@3：绝对差 0.0757；相对差 9.40%；task-cluster paired 95% CI [0.0601, 0.0918]。
- Recall@5：绝对差 0.0431；相对差 4.59%；task-cluster paired 95% CI [0.0339, 0.0527]。

##### No Prior vs Predicted Agent-only
- MRR：绝对差 -0.0043；相对差 -0.67%；task-cluster paired 95% CI [-0.0080, -0.0006]。
- Recall@1：绝对差 0.0054；相对差 1.14%；task-cluster paired 95% CI [0.0018, 0.0097]。
- Recall@3：绝对差 -0.0332；相对差 -4.13%；task-cluster paired 95% CI [-0.0499, -0.0159]。
- Recall@5：绝对差 -0.0187；相对差 -2.00%；task-cluster paired 95% CI [-0.0269, -0.0102]。

##### Oracle Propagation vs Oracle Agent-only
- MRR：绝对差 0.0003；相对差 0.04%；task-cluster paired 95% CI [-0.0064, 0.0071]。
- Recall@1：绝对差 0.0093；相对差 1.71%；task-cluster paired 95% CI [-0.0016, 0.0199]。
- Recall@3：绝对差 -0.0263；相对差 -2.90%；task-cluster paired 95% CI [-0.0378, -0.0152]。
- Recall@5：绝对差 -0.0030；相对差 -0.30%；task-cluster paired 95% CI [-0.0077, 0.0013]。

- 公平 Gate 至少一个主要指标满足相对提升≥10%且 CI 下界>0：[]。
- Oracle Propagation > Oracle Agent-only（至少一个主要指标 CI 下界>0）：False；通过指标：[]。
- Shuffled 不复现增益：False；所有条件 gold coverage=1：True。

#### 5. 与近期论文的边界与更进一步

Who&When（ICML 2025 正式论文，https://proceedings.mlr.press/v267/zhang25cq.html；预印本 https://arxiv.org/abs/2505.00212）提供责任 Agent/步骤任务；本 Pilot 不重复声称谁/何时定位，而是测试传播先验对动作排序的增量。
TraceElephant（ACL 2026 Long，https://aclanthology.org/2026.acl-long.912/；https://arxiv.org/abs/2604.22708）使用全量输入、输出、工具和系统上下文；本 Pilot 借鉴其可观测视图，但限制为可审计的轻量事件表示。
FALAT（https://arxiv.org/abs/2606.00765）已经涉及 typed dependency、source/propagation/symptom/contributing 角色和 dependency-guided ranking；本 Pilot 不把依赖图、传播/症状标签或反向追踪当成单点创新，更进一步仅在新数据组合上检验 strict task-OOF 的增量价值。
TrajDebug（https://arxiv.org/abs/2608.06346）已经研究错误生命周期、恢复和终局影响；Causal Agent Replay（https://arxiv.org/abs/2606.08275）已经研究 do-intervention、重放和置信区间；ErrorProbe（https://arxiv.org/abs/2604.17658）已经研究症状驱动反向追踪和可执行验证。它们是必须正面比较的邻近工作，而不是被忽略的‘空白’。本 Pilot 暂只做离线 Gate，不能把排序结果称为因果根因；后续若进入论文，需要执行重放/替换验证。

#### 6. 可复现性与风险

运行命令、协议、数据 SHA256、每任务预测、失败案例和测试均保存在本目录。模型为标准库线性证据模型，训练严格按任务簇折外；不是大模型 SOTA。主要威胁是 WhoWhenPro 的责任标签不是人工动作干预因果标签，Debate/Dylan 的集合金标也不具备唯一动作语义；因此本报告把结果称为‘离线增量可行性’，不替代后续可执行干预。

### 来源：历史__旧版场景I_故障传播到责任动作定位__real_feasibility_propagation__results_v2_macnet__feasibility_report.md

### 故障传播到责任动作定位：真实可行性 Pilot 报告

#### 结论先行

预注册主 Gate 决策：**NO-GO**。该结论只基于 protocol.json 冻结的任务级折外预测、六个条件和 task-cluster paired bootstrap；不是把数据集责任标注包装成因果证明。

公平比较中，Predicted Propagation 相对 Predicted Agent-only 的 MRR（任务簇宏平均）为 -0.0929（相对 -10.21%），CI 为 [-0.14095679012345677, -0.04768518518518519]。表中均值与 CI 使用同一任务簇宏平均估计量，同时保留 micro_mean 供审计。

#### 1. 数据审计与纳入规则

原始文件共 6257 条；纳入六种多智能体框架 261 条，展开后候选事件 1044 个；原始任务指纹 180 个，其中有重复 rollout 的任务簇 50 个。映射行数 261，映射率 100.00%。

MacNet 使用 accepted_predictions 的多金标集合；Magentic-One、MetaGPT、MathChat 使用公开的 Agent+位置字段；Debate/Dylan 只有 round+Agent 集合，因此不能伪装成唯一动作金标。所有 ground_truth 字段仅用于训练标签与评价，未进入特征。

显式错误词命中 454 次；is_injected/is_replayed 事件文本丢弃 0 个，但事件本身仍保留为候选。角色名按首次出现顺序匿名化。

#### 2. 研究逻辑

RQ1 的上游信息是：错误引入或继续传播的事件是否能从可观察的全过程证据、时序变化和依赖聚合中产生软概率。RQ2 的桥接问题是：这些传播软概率是否比‘只知道哪个 Agent 可疑’更能找到责任动作。No Prior、Predicted Agent-only、Predicted Propagation 的差异只在先验组件，候选池、文本清洗、预算和折划分一致。

Oracle Propagation 不是循环论证：它使用 gold source 只确定下游可观察依赖链的候选上界；具体动作分数来自链上实测的 incoming/outgoing token-dependency strength。源动作没有固定常量高分，也未使用距 gold step 的位置、mode 或注入模板。Shuffled Propagation 在同一外层折、同框架且近似候选规模内置换传播组件。

#### 3. 主要结果（原始分数）

| 条件 | MRR | Recall@1 | Recall@3 | Recall@5 | 症状/末步误判 |
|---|---:|---:|---:|---:|---:|
| No Prior | 0.9477（95% CI [0.9250, 0.9662]） | 0.8954（95% CI [0.8509, 0.9352]） | 1.0000（95% CI [1.0000, 1.0000]） | 1.0000（95% CI [1.0000, 1.0000]） | 0.0134（95% CI [0.0028, 0.0287]） |
| Predicted Agent-only | 0.9093（95% CI [0.8815, 0.9343]） | 0.8213（95% CI [0.7648, 0.8741]） | 0.9963（95% CI [0.9907, 1.0000]） | 1.0000（95% CI [1.0000, 1.0000]） | 0.0537（95% CI [0.0241, 0.0889]） |
| Predicted Propagation | 0.8164（95% CI [0.7842, 0.8496]） | 0.6344（95% CI [0.5704, 0.6987]） | 0.9981（95% CI [0.9944, 1.0000]） | 1.0000（95% CI [1.0000, 1.0000]） | 0.1727（95% CI [0.1208, 0.2250]） |
| Shuffled Propagation | 0.7411（95% CI [0.7021, 0.7815]） | 0.5385（95% CI [0.4677, 0.6036]） | 0.9176（95% CI [0.8769, 0.9556]） | 1.0000（95% CI [1.0000, 1.0000]） | 0.2310（95% CI [0.1708, 0.2861]） |
| Oracle Agent | 0.9986（95% CI [0.9958, 1.0000]） | 0.9972（95% CI [0.9917, 1.0000]） | 1.0000（95% CI [1.0000, 1.0000]） | 1.0000（95% CI [1.0000, 1.0000]） | 0.0000（95% CI [0.0000, 0.0000]） |
| Oracle Propagation | 0.9986（95% CI [0.9958, 1.0000]） | 0.9972（95% CI [0.9917, 1.0000]） | 1.0000（95% CI [1.0000, 1.0000]） | 1.0000（95% CI [1.0000, 1.0000]） | 0.0000（95% CI [0.0000, 0.0000]） |

#### 4. 预注册 Gate 对照

##### Predicted Propagation vs Predicted Agent-only
- MRR：绝对差 -0.0929；相对差 -10.21%；task-cluster paired 95% CI [-0.1410, -0.0477]。
- Recall@1：绝对差 -0.1869；相对差 -22.76%；task-cluster paired 95% CI [-0.2750, -0.0940]。
- Recall@3：绝对差 0.0019；相对差 0.19%；task-cluster paired 95% CI [0.0000, 0.0056]。
- Recall@5：绝对差 0.0000；相对差 0.00%；task-cluster paired 95% CI [0.0000, 0.0000]。

##### Shuffled Propagation vs Predicted Agent-only
- MRR：绝对差 -0.1682；相对差 -18.49%；task-cluster paired 95% CI [-0.2106, -0.1256]。
- Recall@1：绝对差 -0.2828；相对差 -34.43%；task-cluster paired 95% CI [-0.3574, -0.2016]。
- Recall@3：绝对差 -0.0787；相对差 -7.90%；task-cluster paired 95% CI [-0.1204, -0.0435]。
- Recall@5：绝对差 0.0000；相对差 0.00%；task-cluster paired 95% CI [0.0000, 0.0000]。

##### Oracle Agent vs Predicted Agent-only
- MRR：绝对差 0.0894；相对差 9.83%；task-cluster paired 95% CI [0.0620, 0.1176]。
- Recall@1：绝对差 0.1759；相对差 21.42%；task-cluster paired 95% CI [0.1194, 0.2333]。
- Recall@3：绝对差 0.0037；相对差 0.37%；task-cluster paired 95% CI [0.0000, 0.0093]。
- Recall@5：绝对差 0.0000；相对差 0.00%；task-cluster paired 95% CI [0.0000, 0.0000]。

##### Oracle Propagation vs Predicted Agent-only
- MRR：绝对差 0.0894；相对差 9.83%；task-cluster paired 95% CI [0.0634, 0.1171]。
- Recall@1：绝对差 0.1759；相对差 21.42%；task-cluster paired 95% CI [0.1231, 0.2278]。
- Recall@3：绝对差 0.0037；相对差 0.37%；task-cluster paired 95% CI [0.0000, 0.0093]。
- Recall@5：绝对差 0.0000；相对差 0.00%；task-cluster paired 95% CI [0.0000, 0.0000]。

##### No Prior vs Predicted Agent-only
- MRR：绝对差 0.0384；相对差 4.23%；task-cluster paired 95% CI [0.0162, 0.0609]。
- Recall@1：绝对差 0.0741；相对差 9.02%；task-cluster paired 95% CI [0.0296, 0.1218]。
- Recall@3：绝对差 0.0037；相对差 0.37%；task-cluster paired 95% CI [0.0000, 0.0093]。
- Recall@5：绝对差 0.0000；相对差 0.00%；task-cluster paired 95% CI [0.0000, 0.0000]。

##### Oracle Propagation vs Oracle Agent-only
- MRR：绝对差 0.0000；相对差 0.00%；task-cluster paired 95% CI [0.0000, 0.0000]。
- Recall@1：绝对差 0.0000；相对差 0.00%；task-cluster paired 95% CI [0.0000, 0.0000]。
- Recall@3：绝对差 0.0000；相对差 0.00%；task-cluster paired 95% CI [0.0000, 0.0000]。
- Recall@5：绝对差 0.0000；相对差 0.00%；task-cluster paired 95% CI [0.0000, 0.0000]。

- 公平 Gate 至少一个主要指标满足相对提升≥10%且 CI 下界>0：[]。
- Oracle Propagation > Oracle Agent-only（至少一个主要指标 CI 下界>0）：False；通过指标：[]。
- Shuffled 不复现增益：False；所有条件 gold coverage=1：True。

#### 5. 与近期论文的边界与更进一步

Who&When（ICML 2025 正式论文，https://proceedings.mlr.press/v267/zhang25cq.html；预印本 https://arxiv.org/abs/2505.00212）提供责任 Agent/步骤任务；本 Pilot 不重复声称谁/何时定位，而是测试传播先验对动作排序的增量。
TraceElephant（ACL 2026 Long，https://aclanthology.org/2026.acl-long.912/；https://arxiv.org/abs/2604.22708）使用全量输入、输出、工具和系统上下文；本 Pilot 借鉴其可观测视图，但限制为可审计的轻量事件表示。
FALAT（https://arxiv.org/abs/2606.00765）已经涉及 typed dependency、source/propagation/symptom/contributing 角色和 dependency-guided ranking；本 Pilot 不把依赖图、传播/症状标签或反向追踪当成单点创新，更进一步仅在新数据组合上检验 strict task-OOF 的增量价值。
TrajDebug（https://arxiv.org/abs/2608.06346）已经研究错误生命周期、恢复和终局影响；Causal Agent Replay（https://arxiv.org/abs/2606.08275）已经研究 do-intervention、重放和置信区间；ErrorProbe（https://arxiv.org/abs/2604.17658）已经研究症状驱动反向追踪和可执行验证。它们是必须正面比较的邻近工作，而不是被忽略的‘空白’。本 Pilot 暂只做离线 Gate，不能把排序结果称为因果根因；后续若进入论文，需要执行重放/替换验证。

#### 6. 可复现性与风险

运行命令、协议、数据 SHA256、每任务预测、失败案例和测试均保存在本目录。模型为标准库线性证据模型，训练严格按任务簇折外；不是大模型 SOTA。主要威胁是 WhoWhenPro 的责任标签不是人工动作干预因果标签，Debate/Dylan 的集合金标也不具备唯一动作语义；因此本报告把结果称为‘离线增量可行性’，不替代后续可执行干预。

## 历史综合复盘

### 既有复盘

| 场景 I 传播→动作 | 传播链增加复杂度却没有收益 | 显式传播字段和 shuffle 对照可审计 | 传播概率比主体先验更能定位因果动作 | 多轮 NO-GO；首次实现错误不能算结果 | 保留协议和失败案例，拆开 group6 历史 GO | 候选事件/依赖链 schema、传播 shuffle |

## 来源索引

- `历史__旧版场景I_故障传播到责任动作定位__real_feasibility_propagation__results__feasibility_report.md`
- `历史__旧版场景I_故障传播到责任动作定位__real_feasibility_propagation__results_v1_fixed__feasibility_report.md`
- `历史__旧版场景I_故障传播到责任动作定位__real_feasibility_propagation__results_v2_diagnostic__feasibility_report.md`
- `历史__旧版场景I_故障传播到责任动作定位__real_feasibility_propagation__results_v2_diagnostic_pooled__feasibility_report.md`
- `历史__旧版场景I_故障传播到责任动作定位__real_feasibility_propagation__results_v2_macnet__feasibility_report.md`

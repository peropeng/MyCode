# 实验07数据与审计附件

- 当前严格状态：**开发证据**
- 原编号：`E016`
- 机器资产：`实验/实验07_OOPSLA过程中心方法复现/`
- 主结论：`结论/结论07_实验07_OOPSLA过程中心方法复现_开发证据.md`

本文件保存详细指标、原结果摘录和审阅证据；研究判断以主结论为准。

## 原实验结果与指标

以下内容直接并入原结果/报告；它们保留当时数字和判断，但最终等级以本文件开头的严格状态为准。

### 来源：旧实验裁决__实验__开发证据__E016_OOPSLA过程中心方法复现_分支快照_11a2acf__结果.md

### OOPSLA 过程中心方法复现结果

判定：`PARTIAL_REPRODUCTION`

本实验是论文工件复现与研究实现可行性核验，不是 RQ1 Go，也没有调用任何 LLM/API。负结果同样保留为研究证据：它界定了 Graphectory 工件能支持的过程表示范围，以及在线监测/干预尚不能从官方仓库直接获得的边界。

#### 来源与环境

- 官方仓库：<https://github.com/Intelligent-CAT-Lab/Graphectory>
- remote：`https://github.com/Intelligent-CAT-Lab/Graphectory.git`
- 固定 commit：`31a6c3712c94b9b2369d2de916a60e09f9b34f4a`
- `LICENSE` SHA-256：`216e5c256e4a685d7d7b04ee2d69b86c29824212749292b2f12527a591430c79`
- Python：`3.12.13`，隔离环境位于 `runtime/env/graphectory`
- Docker：本机不可用；没有因此替换官方实现或改写算法。

完整命令、返回码、耗时、日志路径、输出 SHA-256 和环境记录在 [manifest.json](manifest.json)；runtime 中保留原始长日志和未提交的官方 clone/LFS 对象。

#### 执行证据

官方 Quick Start 的 `graph_construction/generatejson.py` 对官方 SWE-agent sample 成功处理 `3/3` 条轨迹，生成 3 个 NetworkX node-link JSON 图；运行返回码为 `0`。样例数据通过官方 Git-LFS batch endpoint 获取并按 SHA-256/size 校验。由于本机 Python TLS 对 GitHub 媒体 URL 曾出现 `UNEXPECTED_EOF`，本实验只在本地下载 helper 中使用 `curl` 作为传输回退；没有修改 vendor 中的官方代码。

对生成图的审计结果：

- 时间边：3 个图均生成 `exec` 时间边，边标签可解析为步骤索引。
- 结构边：官方输出使用通用 `hier` 边。`astropy` 样例出现 `directory→file`、`file→block` 等路径证据；并非每条样例都覆盖 block，因此不能把 3 条样例整体写成完整结构合同通过。
- 阶段：官方字段实际为小写 `localization/patch/validation/general`。`astropy` 和 `sympy` 覆盖四类；`django` 样例没有 validation 事件，故聚合覆盖不通过。
- 重复动作：节点确实合并并保留 `step_indices`；但重复节点只有标量 `observation_length/observation_outcome`，没有与每个 occurrence 对齐的 observations/results 序列。不能把该字段提升解释为论文合同要求的逐次观察序列。
- Phase RLE：官方 `get_lang.py --mode phase` 对 3 条图成功生成 RLE 阶段序列。
- Langutory：官方 `get_lang.py --mode lang` 返回失败，错误为 `name 'build_lang_sequence_rle' is not defined`；仓库中只有调用点，没有该函数实现。未修补官方文件来追求通过。

#### R0-D 前缀不变性

候选按轨迹路径字典序排列，且只依据是否含 localization、patch、validation 动作筛选，不读取 `resolved/unresolved` 选择。首条合格的官方支持格式轨迹为 `astropy__astropy-13453.traj`，共 67 个 trajectory steps。对 67 个前缀逐一使用官方 builder 增量重建，并把完整轨迹限制到同一已观测步骤后比较节点/时间边/结构边，结果为 `PREFIX_INVARIANCE_PASSED`。

该结果只证明官方图构造器可对一条本地真实轨迹做前缀构建；没有注入故障、没有按最终成败挑样本、没有调用 Flash，也没有进行 RQ2。

#### REP-Q1 至 REP-Q4

##### REP-Q1：官方样例是否生成一致的 Graphectory/Langutory？

`PARTIAL_REPRODUCTION`。Graphectory 图、时间边、部分层级路径和阶段 RLE 可运行；但重复动作的逐次观察序列、全样例四阶段覆盖和 Langutory 函数实现均未完整满足预注册合同。因此只能支持“过程图构造与阶段 RLE 的实现可行”，不能声称 Definition 1 五项全部复现。

##### REP-Q2：工件是否包含在线监测/干预实现？

`PARTIAL_REPRODUCTION`，并标记 `ARTIFACT_SCOPE_GAP`。对官方源码、测试、示例和脚本的只读审计没有发现 OMI、plan violation、oscillation、prolonged stagnation 三类规则，也没有发现“抑制当前步并返回诊断”或“保留历史并追加阶段建议”的实现。不能把图构造、浏览器 UI 或通用字符串 `suppress/diagnostic` 解释成 OMI。

##### REP-Q3：官方适配器能否对本地真实轨迹做前缀增量构建？

`REPRODUCED`（限定为图构造适配与前缀不变性）。官方 SWE-agent 适配器对首条合格本地轨迹的 67 个前缀均通过不变性审计；最终评估标签未用于选样或结构比较。该结论不延伸到在线告警和干预，因为工件没有公开对应 OMI。

##### REP-Q4：复现出的 OOPSLA 基线能否成为后续 RQ1 的独立、可审计强基线？

`PARTIAL_REPRODUCTION`。过程表示和前缀构造可以作为后续基线的实现起点，且有固定 commit、命令、输出 hash 和审计脚本；但是论文在线规则和干预语义不在官方工件中，当前不能直接运行“完整 OOPSLA 在线基线”或做等预算收益比较。后续若采用规则忠实适配，必须单独标注为论文规则适配，不得写成官方 OMI 复现。

#### 对 RQ1 的边界

本实验没有证明本文的在线故障检测、及时纠偏、Flash 触发策略或责任动作定位有效，也不产生 Go。它给出一个可复核的研究实现边界：官方过程图/阶段 RLE/前缀增量可作为 M1 的论文起点；Langutory 完整实现和 OMI 三规则/两类干预不能从当前工件直接取得，必须在后续研究设计中明确区分论文忠实适配与本文新增方法，并在 RQ1 的自然 Agent 任务和受控故障任务中单独验证。

### 来源：旧实验裁决__实验__开发证据__E016_base_OOPSLA过程中心方法复现__结果.md

### OOPSLA 过程中心方法复现结果

判定：`PARTIAL_REPRODUCTION`

本实验是论文工件复现与研究实现可行性核验，不是 RQ1 Go，也没有调用任何 LLM/API。负结果同样保留为研究证据：它界定了 Graphectory 工件能支持的过程表示范围，以及在线监测/干预尚不能从官方仓库直接获得的边界。

#### 来源与环境

- 官方仓库：<https://github.com/Intelligent-CAT-Lab/Graphectory>
- remote：`https://github.com/Intelligent-CAT-Lab/Graphectory.git`
- 固定 commit：`31a6c3712c94b9b2369d2de916a60e09f9b34f4a`
- `LICENSE` SHA-256：`216e5c256e4a685d7d7b04ee2d69b86c29824212749292b2f12527a591430c79`
- Python：`3.12.13`，隔离环境位于 `runtime/env/graphectory`
- Docker：本机不可用；没有因此替换官方实现或改写算法。

完整命令、返回码、耗时、日志路径、输出 SHA-256 和环境记录在 [manifest.json](manifest.json)；runtime 中保留原始长日志和未提交的官方 clone/LFS 对象。

#### 执行证据

官方 Quick Start 的 `graph_construction/generatejson.py` 对官方 SWE-agent sample 成功处理 `3/3` 条轨迹，生成 3 个 NetworkX node-link JSON 图；运行返回码为 `0`。样例数据通过官方 Git-LFS batch endpoint 获取并按 SHA-256/size 校验。由于本机 Python TLS 对 GitHub 媒体 URL 曾出现 `UNEXPECTED_EOF`，本实验只在本地下载 helper 中使用 `curl` 作为传输回退；没有修改 vendor 中的官方代码。

对生成图的审计结果：

- 时间边：3 个图均生成 `exec` 时间边，边标签可解析为步骤索引。
- 结构边：官方输出使用通用 `hier` 边。`astropy` 样例出现 `directory→file`、`file→block` 等路径证据；并非每条样例都覆盖 block，因此不能把 3 条样例整体写成完整结构合同通过。
- 阶段：官方字段实际为小写 `localization/patch/validation/general`。`astropy` 和 `sympy` 覆盖四类；`django` 样例没有 validation 事件，故聚合覆盖不通过。
- 重复动作：节点确实合并并保留 `step_indices`；但重复节点只有标量 `observation_length/observation_outcome`，没有与每个 occurrence 对齐的 observations/results 序列。不能把该字段提升解释为论文合同要求的逐次观察序列。
- Phase RLE：官方 `get_lang.py --mode phase` 对 3 条图成功生成 RLE 阶段序列。
- Langutory：官方 `get_lang.py --mode lang` 返回失败，错误为 `name 'build_lang_sequence_rle' is not defined`；仓库中只有调用点，没有该函数实现。未修补官方文件来追求通过。

#### R0-D 前缀不变性

候选按轨迹路径字典序排列，且只依据是否含 localization、patch、validation 动作筛选，不读取 `resolved/unresolved` 选择。首条合格的官方支持格式轨迹为官方 sample 中的 `astropy__astropy-13453.traj`，共 67 个 trajectory steps。对 67 个前缀逐一使用官方 builder 增量重建，并把完整轨迹限制到同一已观测步骤后比较节点/时间边/结构边，结果为 `PREFIX_INVARIANCE_PASSED`。

该结果只证明官方图构造器可对一条官方提供的真实 SWE-agent 样例轨迹做前缀构建；它不是本项目新运行的独立 Agent 轨迹，因此不能证明在线 Agent hook 已打通。本阶段没有注入故障、没有按最终成败挑样本、没有调用 Flash，也没有进行 RQ2。

#### REP-Q1 至 REP-Q4

##### REP-Q1：官方样例是否生成一致的 Graphectory/Langutory？

`PARTIAL_REPRODUCTION`。Graphectory 图、时间边、部分层级路径和阶段 RLE 可运行；但重复动作的逐次观察序列、全样例四阶段覆盖和 Langutory 函数实现均未完整满足预注册合同。因此只能支持“过程图构造与阶段 RLE 的实现可行”，不能声称 Definition 1 五项全部复现。

##### REP-Q2：工件是否包含在线监测/干预实现？

`PARTIAL_REPRODUCTION`，并标记 `ARTIFACT_SCOPE_GAP`。对官方源码、测试、示例和脚本的只读审计没有发现 OMI、plan violation、oscillation、prolonged stagnation 三类规则，也没有发现“抑制当前步并返回诊断”或“保留历史并追加阶段建议”的实现。不能把图构造、浏览器 UI 或通用字符串 `suppress/diagnostic` 解释成 OMI。

##### REP-Q3：官方适配器能否对本地真实轨迹做前缀增量构建？

`REPRODUCED`（限定为官方 sample 的图构造适配与前缀不变性）。官方 SWE-agent 适配器对首条合格 sample 轨迹的 67 个前缀均通过不变性审计；最终评估标签未用于选样或结构比较。本项目独立生成轨迹的适配与实时 hook 仍未验证；该结论也不延伸到在线告警和干预，因为工件没有公开对应 OMI。

##### REP-Q4：复现出的 OOPSLA 基线能否成为后续 RQ1 的独立、可审计强基线？

`PARTIAL_REPRODUCTION`。过程表示和前缀构造可以作为后续基线的实现起点，且有固定 commit、命令、输出 hash 和审计脚本；但是论文在线规则和干预语义不在官方工件中，当前不能直接运行“完整 OOPSLA 在线基线”或做等预算收益比较。后续若采用规则忠实适配，必须单独标注为论文规则适配，不得写成官方 OMI 复现。

#### 对 RQ1 的边界

本实验没有证明本文的在线故障检测、及时纠偏、Flash 触发策略或责任动作定位有效，也不产生 Go。它给出一个可复核的研究实现边界：官方过程图/阶段 RLE/前缀增量可作为 M1 的论文起点；Langutory 完整实现和 OMI 三规则/两类干预不能从当前工件直接取得，必须在后续研究设计中明确区分论文忠实适配与本文新增方法，并在 RQ1 的自然 Agent 任务和受控故障任务中单独验证。

## Sol审阅原文

### 2. 文献与方法边界

- Graphectory/OOPSLA 的价值是过程中心表示、结构/时间关系、前缀分析和在线监测范围；不能把过程图 artifact 当作本文在线干预已复现。
- 正式 CCF-A 论文要支撑整篇研究方向；预印本只能补充。Who&When Pro 已覆盖 taxonomy、warm-start 单点注入和 who/when/type 联合预测，不能重复包装为创新。
- 受控仿真只能证明管道和协议可运行；真实 Agent 数据的标签质量、状态重放和干预资格必须单独审计。

## 历史综合复盘

### E016 OOPSLA 过程中心方法复现

- **口语总结：**复现审计能证明论文边界，不能把 artifact 当成我们的新贡献。
- **回答了什么：**Graphectory 的过程表示、前缀分析、在线范围和诊断/回滚语义可被逐项核对。
- **不能说明什么：**不能说明本文已完成同样的 Agent 监控收益或干预复现。
- **只能说明什么：**只能说明一个 CCF-A 过程中心方法锚点和它的适用边界。
- **为何失败/降级：**本地资产/LFS/环境不足，且研究对象与本文故障责任问题不完全同构。
- **Sol 审核办法：**将其降为主线参考与去重审计；结构图是方法来源，不是首创。
- **可复用价值：**schema 审计脚本、prefix/online scope 检查。

## 来源索引

- `旧实验裁决__实验__开发证据__E016_OOPSLA过程中心方法复现_分支快照_11a2acf__结果.md`
- `旧实验裁决__实验__开发证据__E016_base_OOPSLA过程中心方法复现__结果.md`

# 实验24–46分片审计（实验41缺号）

本分片按“原始结果/数据 > 冻结协议 > 实际代码 > 日志 > Markdown > 历史总结”重审。覆盖实验24–40、42–46，共22条JSONL记录；未找到实验41目录、协议、结果或结论，因此不创建虚构记录。外部Parquet、runtime、模型checkpoint、Docker镜像和原始大缓存没有复制或联网重跑，文件/目录计数与SHA-256树哈希见 coverage_24_46.json。

## 1. 分类计数与总判断

| 主分类 | 数量 | 实验 |
|---|---:|---|
| ASSET_STOP | 10 | 25, 28, 31, 35, 36, 37, 38, 39, 40, 42 |
| HARNESS_INVALID | 3 | 24, 27, 43 |
| MULTI_CAUSE_FAILURE | 7 | 29, 30, 32, 34, 44, 45, 46 |
| STORY_MISMATCH | 2 | 26, 33 |
| PAPER_REPRO_BLOCKED | 0（仅作次分类） | — |
| PAPER_BASELINE_FAILED | 0 | — |
| COMBINATION_NO_GAIN | 0（34、44–46作次分类） | — |
| MODULE_NOT_VALIDATED | 0（32、37、39作次分类） | — |
| TRUE_METHOD_NO_GO | 0 | — |

分片内没有满足严格 TRUE_METHOD_NO_GO 的实验：不存在“有效任务定义 + 强基线先复现 + Harness有效 + 同预算 + 三种子/任务配对稳定 + 仍无增益”的完整证据。历史标题中的GO/NO-GO均未直接继承。

可复用的条件性正信号有四个，但不能相加计数：

- 实验29：同题面成功参照在1200条去重交互、5折task-group OOF上，相对fail-fast失败报警召回 0.42056 vs 0.28037，绝对+14.02pp、相对+50%，成功FPR 0.08875，配对CI [0.05607,0.22430]。跨来源完整trace hash交集为0；限制是同一历史资产、同题面可检索条件、无新任务确认。
- 实验30：13条失败运行/12 task clusters上，正确参照+固定tie-break Top-1 0.84615，random 0.53846，但正确参照-only同样0.84615，RQ1报警位置只改善MRR；4-task执行pilot仅1个valid，且proposed未超过current-only。因此是文件路径/参照相关性信号，不是已证实的可执行修复。
- 实验26：13个Exp34 accepted pairs上的受控撤销，rq1_contract 13/13、target recovery 1.0、post-action 0、paired差异CI [0.23077,0.69231]；任务选择与interval均由同一构造资产提供，无独立自然确认。
- 实验33：责任主体对象上fresh confirmation（train731/confirm180）E2 MRR 0.5002 vs 0.3909，相对+28%、CI [0.081,0.1389]；这是有效的OOF上游先验/排序基线，但对象是mistake_agent责任标签，不是当前动作效果或自然因果根因。

可信负结果（仍不计TRUE_METHOD_NO_GO）：

- 实验34修正v2传播相对Agent-only MRR差仅0.0002，CI跨0；v1的+2.68%/+5.72%被注入字段预处理和版本差异掩盖，首轮共享向量结果直接INVALID。
- 实验44–46隔离evaluator后的局部修复均未达到10%：44 SchemaRuleRepair 70/120 vs No 75/120，45 ExactDedupRule 74/120 vs No 75/120，46 LexicalSchemaRule 6/120 vs No 75/120；Oracle分别只多2、2、1个任务，CI下界均为0。三者共享同一120任务和同一类BFCL底座，不计三种独立方法失败。

## 2. 资产/评价资格STOP

实验25是独立选择合同冻结但尚未形成真实action/checkpoint/replay；实验28只完成MP-Bench数据资格（289 traces/867 labels），不是方法GO；实验31只有5任务环境闭环，Trace日志缺少任意中间checkpoint；实验35的30/30、13 effect types全部构造任务，SyncBench自然effect oracle/replay均为0；实验36的G-Memory有3处SyntaxError且自然记忆链缺失；实验37 requirement→evidence mapping为0/365且same-judge风险存在；实验38仅1 task/1 repo/1 effect type、stable oracle为0；实验39的30类记忆错误全由discarded lineage注入；实验40自然qualified cases为0；实验42缺少指定train/dev GPT-4o action-level trajectories/environment_io，test输出不能重命名替代。

这些均不是算法NO-GO。最小修复是先补齐资产/独立Gold/完整状态链，然后重跑冻结Base和最强公平基线。

## 3. Harness问题与BFCL污染裁决

- 实验24三个attempt均未产生持久样本/指标：workspace root安全检查、gc.pid cleanup竞态、runtime/checkpoint路径比较错误。修复前结果完全不可用于科研判断。
- 实验27 34/34任务两候选均非state-changing，checkpoint未重建，replay error=34；只是Stage0资格失败。
- 实验34首轮传播结果因Predicted/Shuffled共享同一向量INVALID；v1修正又有is_injected/is_replayed预处理混杂。
- BFCL实验43–46：实验43的Gate0/Gate1只证明了旧runner的join/replay统计，不能证明下游分数。旧版按full-output digest复用官方stateful evaluator结果，跨candidate namespace污染，故43–46所有旧score、旧排序和由其产生的正/负结论全部INVALID。实验44–46仅采用candidate/task/replay隔离、cleanup和fresh-process审计后的修正版聚合；其结果是探索性负信号，且43必须先用隔离No baseline重获资格。

## 4. 论文与强基线复现状态

| 状态 | 分片内证据 |
|---|---|
| 已复现，可继续使用 | 无论文模块达到“官方主结果+本地Base+A单独有效”的完整状态。实验33/29的自研统计器和BFCL修正版runner可作为透明基线/评测底座，但不是论文复现。 |
| 资产不足，只能理论借鉴 | 实验35的SyncMind/GuardAgent自然资产；实验36的AWM/HiAgent/AgeMem full run与Mem2Act自然数据；实验37过程评价数据；实验40自然记忆闭环；实验42 AppWorld train/dev轨迹。 |
| 正式复现失败，应停止使用 | 实验36 G-Memory pinned code compile失败（3 SyntaxError，help还缺yaml）；不能以该模块为组合前提。 |
| 尚未复现，禁止进入组合实验 | 实验24未运行的OOPSLA-adapted process monitor；实验25/27未来contract；实验35–40未完成自然资格的方法；所有BFCL旧污染score。 |

## 5. 优先级与重审动作

按“基线可信度 × 已有信号 × 失败可定位性 × 最小成本 × 外测可能性”排序：

1. 实验29：先做新task-group确认；已有强正信号、负对照完整、代码和统计可复用。
2. 实验30：把可执行资格作为瓶颈，先扩完整checkpoint replay，再验证文件级参照信号。
3. 实验26：把受控桥接迁移到未参与Exp34/26选择的新任务，避免把constructed interval当自然Gold。
4. 实验24：低成本修复runner并恢复Base/最强基线；若基础设施仍不稳立即停止。
5. 实验43：只做隔离No baseline和evaluator contamination复核；在此之前不得进入BFCL方法组合。

只应归档/不再投入：27（同批资产反复资格失败）、32（synthetic/Oracle/对象混杂）、34传播组合（保留条件分解接口，不再局部加模块）、36 G-Memory代码、37过程评价、38 SyncBench bounded probe、39构造记忆、40自然记忆资产、42 AppWorld当前资产、44–46旧BFCL修复家族。44–46的隔离runner与No/Oracle审计应保留为baseline/负结果，不再以第三个补丁抢救。

## 6. 高优先级最小迭代计划

### 候选A：实验29同题面成功参照的选择性使用

1. 已有结果真正说明什么：在同题面可检索的历史交互中，paired reference在固定成功FPR下比fail-fast多报警14.02pp；shuffle/wrong reference破坏FPR，说明匹配质量有信号。
2. 直接原因：不是代码失败，而是条件性数据/任务异质性和同一历史资产；尚无新任务确认。
3. 可复用：masked OOF runner、5折task-group切分、正确/打乱/错配reference负对照、paired bootstrap。
4. 可否定假设：当“匹配置信度低/首次任务/无可用成功参照”时全量注入反而有害；一个匹配置信度拒绝门应优于全量reference。
5. 最小修改：只增加一个selective reference gate；不改变主指标、阈值、API预算或候选数。
6. 冻结矩阵：Base=fail-fast；Base+A=原paired reference；Base+gate=仅置信度拒绝；Base+A+gate=原参照加门控。A已本地单独有效，故可以进入组合。
7. 数据切分：至少30个未参与Exp29的task groups，按normalized description分组；开发/确认分离，禁止同题面跨集；mask resolved/judgement/future。
8. 指标/成本：failure alarm recall at success FPR≤.10、mean step savings、paired task bootstrap；记录参照检索数、token/latency、拒绝比例。
9. 继续条件：无泄漏、同预算、至少3 seeds或多数task-pair同向、门控删除后增益明显减弱；再做一次确认。
10. 停止条件：A在新Base不优于Base；随机门控相同；增益仅来自更多参照/预算；确认集反向；无参照场景Oracle也无价值。

### 候选B：实验30可执行修复资格门

1. 已有结果真正说明什么：13/12 ranking有文件路径信号，RQ1位置只改善MRR；4-task pilot只有1 valid，且proposed与reference-only等Top1。
2. 直接原因：完整中间workspace缺失、候选块不能从同一base应用，标签是文件级而非根因级。
3. 可复用：edit parser、SWE-Gym/OpenHands data contract、current-only/reference-only/shuffle/wrong controls、single-hunk validator。
4. 可否定假设：文件参照信号只在“可从同一checkpoint replay且action state一致”时有效；replayability gate应减少错误候选。
5. 最小修改：只加入一个state-aware replayability/confidence gate，不加第三模块。
6. 冻结矩阵：Base=current-only/path baseline；Base+A=correct-reference ranking；Base+gate=state gate；Base+A+gate=组合。若A在扩充资格集仍不优于Base，禁止组合。
7. 数据切分：先获取≥30独立task clusters、≥3 repos的完整前后checkpoint；按task cluster开发/确认；Gold patch仅离线上界。
8. 指标/成本：Top1/MRR与公开测试通过率；记录候选数、hunk应用失败、replay重试、token/latency。
9. 继续条件：三种子或多数任务配对同向、A和gate分别通过Base、同预算；确认集冻结后再跑。
10. 停止条件：valid replay仍<90%；reference-only不超过Base；gate与随机gate相同；增益只来自减少候选/更多测试预算。

### 候选C：实验26受控桥接的样本外复核

1. 已有结果真正说明什么：13/13 contract目标撤销恢复、post-action=0；但选择区间和目标来自Exp34 accepted assets，非自然故障。
2. 直接原因：样本外/自然Gold不足，不是已证明的方法失败。
3. 可复用：revoke/restore checkpoint、periodic/fixed_recent/random controls、task-paired bootstrap、integrity/leakage audit。
4. 可否定假设：contract interval只有在“可观察状态改变且replayability高”时有效；低置信动作应回退到periodic/random。
5. 最小修改：只加入一个replayability-confidence gate，不加第三模块。
6. 冻结矩阵：Base=periodic；Base+A=rq1_contract；Base+gate=confidence-only fallback；Base+A+gate=组合。A先在新任务集独立复现。
7. 数据切分：排除Exp26/34的13 pairs；新任务≥30、≥5 repos，开发/确认按task id hash冻结；private fault fields只留offline evaluator。
8. 指标/成本：target revoke recovery、post-action false recovery、interval coverage、mean interventions、paired CI；记录replay calls/restore retries/latency。
9. 继续条件：新任务A正向且三种子/多数task配对同向；门控删除后增益消失；再进入确认。
10. 停止条件：新任务A≤Base；post-action recovery升高；目标位置依赖private fault字段；增益来自更多干预预算。

### 候选D：实验43 BFCL隔离基线再资格

1. 已有结果真正说明什么：Gate0/Gate1记录了120任务双replay一致，但后续发现旧stateful evaluator污染；这不是方法正/负结果。
2. 直接原因：旧版本按full-output digest跨candidate复用checker namespace，所有旧下游score INVALID。
3. 可复用：pinned official commit、fixed 120 selection、metadata-only projection、candidate/task/replay namespace isolation、fresh-process audit。
4. 可否定假设：隔离后No baseline应稳定接近75/120；若No本身变化，历史44–46差值均不可解释。
5. 最小修改：只做Harness isolation/requalification，这是评价修复，不把它包装成方法创新。
6. 冻结矩阵：Base=isolated No；Base+A=尚不运行，待Base稳定后再选一个单模块；不直接运行A+B。
7. 数据切分：固定120（4×30）仅作开发资格；另冻结未参与选择的BFCL确认集后再比较方法；online字段只允许id/result/history response prefix/schema。
8. 指标/成本：VALID rate、双replay一致性、harness exceptions、checker calls、created=removed、fresh-process fingerprint；记录成本。
9. 继续条件：isolated No跨顺序/fresh process一致，0 leak/exception；之后才允许一个模块单测。
10. 停止条件：No仍不稳定；任何旧digest reuse；Gold/future进入policy；方法增益来自candidate数或额外调用预算。

## 7. 跨实验规律与潜在突破口

### 多次支持的稳定事实

1. 局部证据/同任务参照可以有效，但其增益依赖“可匹配历史 + 同一状态/路径”条件；进入下游干预或自然任务后，完整checkpoint和对象定义决定是否仍有资格。
2. 评价资格与算法效果必须分离：Exp24/27/35/38/39/42的runner/构造门通过或失败，都不能替代自然方法分数。
3. Oracle与Gold上界只能回答可修复性上限；Exp31、32、34、44–46均显示上界/标签好看不等于Predicted方法可用。
4. 任务/框架/错误机制异质性很强：Exp34传播、Exp32旧场景、Exp37过程数据和Exp40记忆均有对象或域不匹配。
5. BFCL stateful evaluator污染是系统性Harness问题：43–46旧分数必须整体INVALID；修正版隔离runner才是可复用资产。

### 多次被否定的机制

- 全量传播先验相对Agent-only的稳定增益（Exp34 v2接近0，v1被混杂）。
- 仅靠局部调用裁剪、schema/literal替换的BFCL修复（44–46 Oracle仅1–2/120 rescue）。
- 用synthetic constructed Gate1替代natural action/memory/evidence qualification（35、39）。
- 以Gold/Oracle责任主体、公开patch上界或test outputs替代真实Predicted输入（31、32、33、42）。
- 借论文出现的模块直接组合；Exp36 G-Memory未复现，Exp37评估器没有独立Gold。

### 尚未公平测试的核心假设

- 选择性使用/拒绝比全量注入更好，尤其是参照匹配置信度、可重放状态置信度和恢复性条件。
- 候选覆盖与排序应分离：Exp30/44–46提示先检查候选是否覆盖可修复状态，再评价排序。
- 失败/动作的自然标签对象是否与下游干预对象一致；若不一致，平均无增益不能区分标签失败与机制失败。

### 最值得补做的确认实验

优先补Exp29新task-group门控确认；其次补Exp30/26完整checkpoint的独立任务资格；BFCL只补隔离No baseline。Exp34传播和44–46局部补丁不再加第三模块抢救。

## 8. 三次方法失败计数

| 冻结目标 | 本分片实质方法失败数 | 不计数的失败 |
|---|---:|---|
| RQ1状态转移/动作效果契约（24–27） | 0 | 24/27 runner/checkpoint；25 Stage A未跑；26受控正信号 |
| 历史参照→早停/有限修复（29–31） | 0 | 29/30样本与外测不足；31 checkpoint资产不足 |
| 旧版责任/传播（32–34） | 0 | 32对象/合成混杂；33有效但故事不匹配；34首轮Harness INVALID、v2仅探索性 |
| 方向A/B/C资产资格（35–40、42） | 0 | 全部资产STOP、构造Gate或论文复现阻塞 |
| BFCL接口/修复（43–46） | 0 | 43–46旧evaluator污染；44–46共享固定120、单seed且Oracle上界低，不算三种独立机制失败 |

因此本分片没有触发“三种理论机制实质失败后停止”的冻结目标。44–46虽然都是负向探索，但不应机械累计为三次方法失败。

## 9. 两周执行顺序（分片建议）

| 顺序 | 动作 | 并行/预计耗时 | 当天停止条件 | 进入确认条件 |
|---|---|---|---|---|
| 1 | BFCL隔离No baseline复核（43底座） | 独立，0.5–1天；不联网/API，需已有runtime | No顺序/fresh-process不一致、仍有污染 | 120固定任务一致、0 exception/leak |
| 2 | Exp24 runner修复后只跑资格/Base | 与1并行，1天；源缓存可用前提 | workspace/checkpoint再次失败 | Base与强基线持久结果可复现 |
| 3 | Exp29新task-group Base vs paired reference | 与1/2并行，1–2天 | 参照缺失率高、A≤Base或FPR>0.10 | ≥3 seeds/多数task-pair同向、无泄漏 |
| 4 | Exp30完整checkpoint资产资格与current/reference-only | 2–3天，依赖新资产 | valid replay<90%或A不超Base | ≥30独立clusters、三种子方向一致 |
| 5 | Exp26样本外contract bridge | 2–3天，依赖4类动作资产 | target/post-action分不开或A≤Base | 新任务A正向、门控消融成立 |
| 6 | 仅对通过上述门的候选做一次新机制确认 | 2–3天 | 增益来自预算/候选数/Oracle | 新冻结确认集CI下界>0后才可交给主线程 |

不并行运行需要同一外部runtime/数据写入的任务；不安装新依赖、不启动Docker、不调用付费API。探索性正增益只有在同预算、无错误/泄漏、三种子或任务配对大多数同向时进入一次确认；本分片没有可直接写成最终论文GO的结果。

## 10. 当前不构造论文故事

本分片只保留：实验29/30/26/33的条件性信号、实验34与BFCL44–46的可信探索性负结果、实验24/27/35–40/42的资产或Harness缺口、BFCL旧分数INVALID裁决，以及可复用的OOF/隔离/replay/统计接口。至少一个候选完成“可信Base复现 → 单模块正增益 → 新任务确认”之前，不输出题目、RQ1/RQ2或创新贡献包装。

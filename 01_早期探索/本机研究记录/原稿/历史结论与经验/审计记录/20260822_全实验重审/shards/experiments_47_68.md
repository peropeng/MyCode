# 实验 47–68 分片审计（2026-08-22）

## 审计边界与证据规则

本分片覆盖实验 47–68 共 22 项。审计以可执行结果/原始 JSONL、JSON、CSV、Parquet 和 ledger 为第一证据，冻结协议为第二证据，代码/测试和日志为第三、四证据，最后才参考 README、report 与历史总结。对 48、62、63、65、66、67、68 的数值均核对了结果 JSON/JSONL 的字段或从原始行重算；Exp68 特别重算了 109 行与 102 个完整行。

评分对象的十维均为 0–5；repair_cost 采用“越高越容易/便宜修复”的可执行性分数，overlap_risk 越高表示重叠风险越高。

## 1. 分片总体结论

| primary class | 实验 | 数量 | 判定 |
|---|---|---:|---|
| HARNESS_INVALID | 47, 64, 66, 67, 68 | 5 | 结果不能用于方法判断；修复后必须重跑 |
| ASSET_STOP | 49, 50, 51, 52, 53, 54, 55 | 7 | 资产/评价资格不足，不计方法失败 |
| PAPER_REPRO_BLOCKED | 57, 59, 60, 61, 62 | 5 | 论文/官方协议尚未取得有效复现资格 |
| TRUE_METHOD_NO_GO | 48, 65 | 2 | 在有效、同预算、完整比较下可信负结果 |
| STORY_MISMATCH | 56, 58 | 2 | 结果/资产有效，但不是旧故事中的新方法结果 |
| MULTI_CAUSE_FAILURE | 63 | 1 | 有条件性信号，被异质性和 CI 跨 0 抵消 |
| PAPER_BASELINE_FAILED | 无 | 0 | 本分片没有满足“完整官方资产+合理环境仍无法复现”的项目 |
| COMBINATION_NO_GAIN | 无 | 0 | Exp68 的组合未通过 coverage gate，不能按该类裁决 |
| MODULE_NOT_VALIDATED | 无 primary | 0 | 作为 secondary 见 Exp54；未把借入模块直接当成功 |

因此：

- 真正的可信方法 NO-GO：2 项（Exp48、Exp65）。
- 资产/评价资格 STOP：7 项（Exp49–55）。
- Harness 无效：5 项（Exp47、64、66、67、68）。
- 有可修复或待确认的方向性信号：Exp63（结构信号）和 Exp67（OOF 融合信号）；Exp59 AWM 只是在 n=2、非官方迁移条件下的阻塞性条件信号，不能计入有效正结果。
- 有效但与旧方法故事不匹配：Exp56（Graphectory 核心趋势复现）和 Exp58（AFTraj 外测资产 GO）。
- 本分片没有触发同一冻结目标的三次实质方法失败。

## 2. 逐项分类摘要

| ID | objective / 原始证据摘要 | primary | 方法分数 vs 最强公平 baseline | 结论是否可支持 | 可复用资产 / 下一步 |
|---:|---|---|---|---|---|
| 47 | BFCL 旧 evaluator 跨 candidate digest/cache 污染；修复后的 order/fresh-process 全 match、零 leak | HARNESS_INVALID | 无科学分数 | 只能支持“污染已定位、修复审计通过”，不能支持历史方法结果 | 隔离 namespace、fresh-process audit；用修复 evaluator 重跑 Base/单模块 |
| 48 | 120 task、120200 candidates；No=75，Oracle 仍75，net rescue=0，CI=[0,0] | TRUE_METHOD_NO_GO | .625 vs .625，diff 0 | 可以；同预算、同任务、修复 evaluator 下顺序变换无增益 | 合法 permutation corpus、zero-rescue 负结果；停止第五 operator |
| 49 | AgentIssue 50 tags；函数 Gold 26/50、strict eligible=0、FAIL_TO_PASS=0 | ASSET_STOP | 无 | 不能；缺函数 Gold/可执行失败标签 | commit/patch/schema 清单；仅补齐 >=30 函数 Gold 后重开 |
| 50 | Docker 25 次无网络 run 基础设施通过，但 5/5 marker missing，commit pair 4/5 | ASSET_STOP（secondary HARNESS_INVALID） | qualified marker 0/5 | 不能；退出码不能当 Gold | Docker isolation/marker gap；修 marker contract 后再 Phase B |
| 51 | 可见 rows=1128，但 qualified independent/heldout/process Gold/chains/external 全0；机制有直接重叠 | ASSET_STOP | 无 | 不能；QA rows 不是过程 Gold | schema/overlap audit；取得新非重叠机制和 frozen chains 才重开 |
| 52 | 5 篇形式论文通过，但候选 end-to-end=0、failure/recovery Gold=0、qualified families=0 | ASSET_STOP | 无 | 不能 | ResiliBench/ToolEVO/WMA/OpenApps 缺口表；只找自然 failure/recovery asset |
| 53 | Gate1 再证实 LFS payload/自然 failure/recovery/heldout/offline replay 全缺失 | ASSET_STOP | qualified=0 | 不能 | asset gate；没有新 payload 则归档 |
| 54 | EXP-Bench 461 rows/51 papers/12737 subtasks 但 process Gold、repair pair、frozen chain、CPU smoke=0 | ASSET_STOP | 无 | 不能 | metadata/依赖审计；取得 starter repos 和过程 Gold 才重开 |
| 55 | Gaia2/ARE 160 DAG 可解析，但 real traces/equivalence Gold/repair/heldout 全0 | ASSET_STOP | 无 | 不能 | DAG parser/hash；补真实 agent traces 和独立等价 Gold |
| 56 | Graphectory 官方链 11 commands 全0；8 unit counts 和聚合趋势复现，稀疏 cell 相对误差可达1 | STORY_MISMATCH | 非本课题方法分数 | 可以支持“核心趋势复现”，不能支持新方法 | raw/hash/graph chain；固定为外部复现 baseline |
| 57 | 官方 repo/data 有，但 batched/unbatched embedding 差异 .0508–.0625 >1e-4；训练 fail-closed | PAPER_REPRO_BLOCKED | 无 Acc@1/Acc@5 | 只能支持“复现被环境/contract 阻断”，不能写论文 baseline failed | calibration/fail-closed cache；CPU/官方设备重验 |
| 58 | AFTraj 2276 rows，external 332/217 groups，clean train 1817，forbidden fields/schema pass；仅 asset gate | STORY_MISMATCH | 无方法分数 | 可以支持资产可用，不支持 method GO | observed-prefix split/scanner；冻结 missing/ambiguous policy后跑 Base |
| 59 | AWM n=2：seed0 +.1417、seed1 +.05、seed2 0；HiAgent pending；v3 contract invalid | PAPER_REPRO_BLOCKED（secondary MULTI_CAUSE_FAILURE） | AWM 平均 .2389 vs .175，但不合格 | 不能裁决论文或方法 | v4 contract/negative seed；取得官方完整 test 才继续 |
| 60 | human alignment 317/366=.8661；task52 drift；4 UUID pilot arms、max token 17956>16000、full API pending | PAPER_REPRO_BLOCKED（secondary HARNESS_INVALID） | pilot 不合格 | 只能支持 human trend，不能支持方法比较 | human labels/PRB schema；冻结365/366 policy、修 budget、重跑 full |
| 61 | SyncMind/OpenHands public runtime 不可用；Chromium emulation ConnectionError，plan-row mismatch，0 API | PAPER_REPRO_BLOCKED（secondary HARNESS_INVALID） | 无 | 不能 | ABI/no-LLM smoke；修 plan row 并取得 official runtime |
| 62 | V4 Flash full 722 slots；mean .74368、CI [.70275,.78526]，position gap .26682>.10 | PAPER_REPRO_BLOCKED | 无同 backend baseline；非论文模型 | 可以支持“V4 adapter 有 position bias”，不能称论文复现 | PRB parser/position gate；换论文官方模型/endpoint |
| 63 | 5-fold OOF；structure .69252 vs errors heuristic .66759，+3.73%，CI [-.04966,.09917]；长/短正、中等反 | MULTI_CAUSE_FAILURE | 有方向信号但 CI 跨0 | 可支持条件性信号，不可写确认 GO | OOF folds/features/negative controls；只测试一个 selective gate |
| 64 | 292 slots 中断；durable STARTED 无 terminal；parse coverage .068/.055，无分数 | HARNESS_INVALID | 无 | 不能 | ambiguity ledger/supervisor；修复后 fresh namespace 重跑 |
| 65 | 306 slots 全解析；CBR .69608 vs PAIRWISE .80392，diff -.10784，CI [-.17647,-.04412] | TRUE_METHOD_NO_GO | relative -.1341 | 可以；这是绝对 Rubric 的可信负结果 | fair ledger/position audit；停止 CBR，不加第三模块 |
| 66 | target .60616 vs PAIRWISE .72260，CI [-.17857,-.04850]，但 target coverage .767<.95、34 parse fail、1 transport | HARNESS_INVALID（secondary MULTI_CAUSE_FAILURE） | 诊断性 -16.1%，不具科研资格 | 不能计方法 NO-GO | state contract/scheduler/parse taxonomy；先修 parser/transport 后再裁决 |
| 67 | OOF target .81452 vs generic .77016，+5.76%，CI [-.00855,.1]；generic orientation/input ledger incomplete、1 invalid row | HARNESS_INVALID（secondary MULTI_CAUSE_FAILURE） | 方向性正信号但 comparator 未资格 | 不能写确认正结果 | OOF split/cluster；修 generic ledger后重算并上新确认集 |
| 68 | 原始 target .64220 vs structure .69725，relative -.078947，43 clusters CI [-.108108,-.009901]；7 transport，coverage .93578<.95；完整102行两者均 .6862745 | HARNESS_INVALID（secondary MULTI_CAUSE_FAILURE） | 原始诊断显著更差；完整 rows 无增量 | 不能计最终方法 NO-GO；可作无门控融合负对照 | OOF freeze/external raw recompute；不加第三模块，只有修 transport+新 external 才重跑 |

## 3. 论文/官方方法与强基线状态

| 方法/实验 | 状态 | 是否可继续 |
|---|---|---|
| BFCL evaluator（47/48） | 47 暴露并修复历史候选污染；48 在修复后完成有效负结果 | 48 可作负基线；47 修复 evaluator 可继续重跑 Base/单模块 |
| Graphectory（56） | 官方核心 RQ2 trend reproduced；聚合误差小，稀疏 cell 不完全一致 | 可作复现 baseline/外部证据，不作新方法 |
| StepFinder（57） | repo/data 及版本齐，但 strict embedding prerequisite fail，未到官方主结果 | 暂不进入组合；只做环境/设备合同修复 |
| HiAgent/AWM（59） | 非官方迁移、AWM test=2、HiAgent pending；不能说 paper baseline failed | 不继续在 n=2 调参 |
| AgentJudge/PRB（60） | human trend 可复现；task52 计数漂移、pilot 4 UUID、token budget fail、API 未完整 | 先修版本/budget，再决定是否复现 |
| SyncMind/PRB（61） | official runtime/semantic replay unavailable，smoke 还有 plan-row mismatch | 暂停，不进入组合 |
| PRB V4 Flash（62） | 只能 cross-backend qualification；deepseek-v4-flash 不在 README 明示的论文模型 DeepSeek-V3.2-Exp/GPT-4o 清单 | 不作论文官方 baseline；position bias 仅作评测负对照 |
| PAIRWISE（65–68） | Exp65 是完整强 baseline；Exp66/67/68 的 comparator 分别受 coverage、orientation 或 transport 审计影响 | Exp65 可继续作为 strongest fair baseline；其余修复前不作确认 baseline |

本分片没有 PAPER_BASELINE_FAILED：57/59/60/61/62 都在完整官方主结果或模型/运行时对应关系成立之前被阻断。不能把缺资源、迁移差异或 position gate 失败偷换为论文自身结论失败。

## 4. 当前最值得修复/确认的候选

排序按“基线可信度 × 方向信号 × 失败可定位性 × 最小成本 × 外测可能”，不按叙事：

1. **Exp63：结构轨迹证据的选择性使用**。失败原因最清楚：总体小增益被长度/状态异质性抵消，且 OOF/feature audit 已通过；AFTraj 提供潜在外测资产。
2. **Exp67：执行证据融合的 baseline ledger 修复**。有 +5.76% 方向信号和 target swap=1.0，但 generic comparator 资格不完整；修复主要是审计/重算，不应先加模块。
3. **Exp57：StepFinder embedding contract 修复**。这是低成本的论文/外部 baseline 资格修复，不是方法创新；若 CPU/官方设备仍失败，立即归档。
4. **Exp58：AFTraj 资产 policy 冻结**。外测可能性最高，但先解决 missing/ambiguous Gold 口径；资产 GO 不等于方法 GO。
5. **Exp47/48**只作为 BFCL 负对照和 evaluator 修复基础，不再投入顺序 operator。

## 5. 高优先级候选的最小迭代计划

### 候选 A：Exp63 结构证据的 selective gate

#### 1. 已有结果真正说明什么

同一 PRB asset 的 5-fold GroupKFold OOF 中，16 个结构特征模型比最强 explicit-error heuristic 高 0.02493（相对 3.73%），但 cluster CI [-.049656,.099174] 跨 0。长轨迹/短轨迹正，medium 子集约持平或略差；这支持“结构证据有条件效用”，不支持平均方法 GO。

#### 2. 上一轮失败直接原因

域/轨迹长度异质性和非单调状态规律；不是代码错误，也不是 leakage。没有独立确认，negative-control CI 也偏宽。

#### 3. 可复用内容

OOF fold/cluster split、结构 feature contract、fewer-errors/position/length heuristics、negative controls、bootstrap 统计代码和 Exp65 PAIRWISE baseline。

#### 4. 本轮理论假设

> 结构模型只在冻结的高置信且轨迹长度/状态落入训练支持区间时启用，否则回退到 strongest baseline；该 selective gate 应优于全量结构模型。

#### 5. 最小修改

只增加一个 confidence/coverage-based selective gate；不增加第三模块，不改变主指标，不改变 token/API budget。阈值只由开发 OOF 预注册，禁止按确认集调参。

#### 6. 冻结实验矩阵

- Base：strongest fair PAIRWISE/explicit-error baseline；
- Base + A：原结构模型；
- Base + G：只启用 gate 的回退策略（拒绝时 Base，作为 gate sanity）；
- Base + A + G：gate 选择结构或 Base。

若 A 在完整重算后不优于 Base，则停在 Base/A，不运行组合确认。

#### 7. 数据和切分

结构开发集仅用于选择 gate；确认使用未参与选择的新 UUID/新任务，至少 30 个独立任务并保留 task-level pairing。AFTraj 只能在任务目标和 Gold 语义对齐后作为外部集；不能把 Exp63 的 post-hoc length 子集当确认。

#### 8. 主指标和成本

继续使用 task/UUID paired primary accuracy；同时记录拒绝率/coverage、调用数、token、延迟、探针和失败重试。gate 不得增加调用或候选预算。

#### 9. 探索继续条件

无错误/泄漏、同预算；至少 3 seeds 或大多数独立任务差值同向；gate 相对 Base 真实正增益，删除 gate 后增益消失。

#### 10. 立即停止条件

A 不优于 Base；gate 与随机 gate 相同；增益只来自更多 coverage/预算；新确认集方向反转；简单 length/error heuristic 达到相同结果；Oracle 也无价值。

### 候选 B：Exp67 OOF 融合的审计修复后选择性使用

#### 1. 已有结果真正说明什么

124-row/92-cluster OOF target=.814516、generic=.770161，方向 +5.76%，target swap consistency=1.0；但 CI [-.008547,.1] 跨 0，generic orientation/input ledger 未完整审计且 1 row invalid。

#### 2. 上一轮失败直接原因

首先是 Harness/comparator 资格不足，不是已证明的模型失败；同时小样本/cluster heterogeneity 可能抵消平均增益。

#### 3. 可复用内容

OOF folds、feature/label blindness、cluster bootstrap、generic ledger 的缺字段清单、invalid row 处理和 Exp68 external contract。

#### 4. 本轮理论假设

> 融合仅在 generic 与 execution evidence 的置信度一致且状态未冲突时启用；冲突/低覆盖样本回退到 PAIRWISE，因此 selective fusion 应优于全量 fusion。

#### 5. 最小修改

第一步只修 generic orientation/input ledger 并重算原 target/base；确认 baseline 合格后只加一个冲突门控机制。不得直接把 Exp68 的 7 个 transport failures 当方法错误并加补丁。

#### 6. 冻结实验矩阵

- Base：修复并完整审计的 generic PAIRWISE；
- Base + A：原 OOF fusion；
- Base + G：冲突拒绝/回退 gate sanity；
- Base + A + G：selective fusion。

在 Base+A 未通过同预算、coverage≥.95 前，禁止组合进入确认。

#### 7. 数据和切分

先用原 OOF 仅修复 comparator，不重新选择特征；确认必须是新的、未参与选择的任务/UUID。Exp68 的 109 external 及其 102 complete rows 只作审计负对照，不作确认。

#### 8. 主指标和成本

保持 task-level paired accuracy 和 cluster bootstrap；记录 coverage、拒绝率、transport/parse、token、延迟、调用数。门控不能增加请求。

#### 9. 探索继续条件

baseline ledger 完整且两臂 coverage≥.95；三种子/多数独立任务同向；删除 gate 后增益减弱；无泄漏/无 budget advantage。

#### 10. 立即停止条件

generic audit 仍不完整；fusion 不优于 Base；随机 gate 同效；增益由 transport 修复/更多预算产生；新 external 反转；simple generic margin/length heuristic 同效。

### 候选 C：Exp57 StepFinder 复现资格修复（复现候选，不是新方法）

#### 1. 已有结果真正说明什么

官方 repo/data/version 和 train/test split 已到位，但严格 batched/unbatched embedding contract 在5个文件均失败，故训练和 Acc@1/Acc@5 从未获得。

#### 2. 上一轮失败直接原因

环境/设备/批处理数值不一致；不是论文自身 baseline failed，也不是模型方法负结果。

#### 3. 可复用内容

官方 commit/data revision、train/test overlap audit、严格 1e-4 calibration probe、fail-closed cache。

#### 4. 本轮理论假设

> 在 CPU 或论文同设备且采用官方 batching 后，embedding 差异应回到 1e-4 内；否则该复现环境不具备评价资格。

#### 5. 最小修改

只改变运行环境/embedding execution contract，保持数据、模型版本、阈值和训练配置不变；不放宽 tolerance，不增加模型模块。

#### 6. 冻结实验矩阵

- Base：官方 StepFinder pipeline；
- Base + A：官方 embedding cache under corrected contract；
- Base + G、Base + A + G：不适用；若必须填矩阵，则记录为“禁止运行，A 未先资格通过”。

#### 7. 数据和切分

官方 train2604/test58，继续保持 text no-overlap；新增确认只在官方 held-out test 上，不能用 calibration samples 调训练。

#### 8. 主指标和成本

embedding max absolute deviation、Acc@1/Acc@5、训练时间；记录 device/batch/precision，token 不适用，API=0。

#### 9. 探索继续条件

所有 calibration 文件 ≤1e-4，训练可复现，官方主指标落在论文合理误差范围；之后才进入基线比较。

#### 10. 立即停止条件

CPU/官方设备仍超阈值；通过放宽 tolerance 才能训练；主结果无法复现且差异不能由版本/随机性解释。

## 6. Exp68 原始证据独立复核

- external_predictions.jsonl 为 109 行；external_ledger 为 436 events、218 unique slots。
- 全部 109 行：target=70/109=.6422018348623854；structure=76/109=.6972477064220184；relative=(target-structure)/structure=-.07894736842105263。
- UUID cluster bootstrap：43 clusters、10000 samples、CI=[-.10810810810810811,-.009900990099009901]。
- ledger：PARSED=211、TRANSPORT_FAILED=7；retry=0、duplicate/ambiguous/unknown=0；target coverage=.9357798，低于 prereg .95。
- 102 完整行：target=structure=.6862745098039216；target-structure=0；generic=.6911764705882353。该102行只是同一 external 的完整子集，不能当独立确认。
- 因 target coverage gate 失败，primary 必须是 HARNESS_INVALID；不能把全体负差异直接记 TRUE_METHOD_NO_GO，也不能把102行事后子集写成“组合无增益确认”。

## 7. 跨实验规律

### 已被多次证明的稳定事实

1. 评价对象和 Harness 资格是主要瓶颈：47、50、64、66、67、68 中均有 namespace、marker、terminal、parse、orientation 或 transport 证据问题；这些不得算方法失败。
2. 严格同预算/位置审计能暴露隐藏偏差：48 的 evaluator 修复后 zero rescue，62 的 V4 Flash position gap=.2668，65 的 CBR 虽 swap consistency 高但 utility 低。
3. 论文/外部资产的“论文规模”常不等于本地可执行 Gold：49–55 全部在 asset gate 停止；57/59/60/61/62 在官方复现主结果前阻断。
4. 全量平均会掩盖条件性规律：63 的长/短轨迹方向性正、medium 近零；68 的完整102 rows equal 但含 transport failures 的全体更差。

### 已被多次否定的机制

1. BFCL 同-item call-order permutation：48 在120 task/120200 candidates中 net rescue=0。
2. Counterbalanced absolute Rubric：65 在全解析、同预算下比 PAIRWISE 低13.4%。
3. 直接把新模块/论文名字当有效：59–62 尚未完成官方资格，不能假定借入模块有效。
4. 无条件融合结构+generic：68 原始诊断下降，102完整行无增量；不能继续加第三模块。

### 尚未被公平测试的核心假设

1. 结构证据是否应由长度/状态/置信度选择性启用，而不是全量注入（63）。
2. OOF execution evidence 与 generic pairwise 在冲突时是否需要拒绝/回退门控（67→68）。
3. transport/parse 修复后，Exp68 负方向是否仍存在；当前 coverage 不足，尚非 TRUE_METHOD_NO_GO。
4. AFTraj observed-prefix 外测是否与当前预测对象 Gold 语义一致（58）。

### 最可能形成方法的条件化机制

- selective prediction / reject-and-fallback；
- 轨迹状态/长度条件化 gate；
- provenance/evidence 冲突时的风险控制回退；
- 不改变 API 调用数、不增加候选预算的覆盖率约束。

### 最值得补做的确认实验

先修 Exp67 generic ledger 并重算；并行完成 Exp63 的单一 selective gate 开发冻结。之后在新独立任务/外部 AFTraj（Gold policy 先冻结）确认；Exp68 只作为负对照，不用事后102行确认。

## 8. 三次方法失败计数

| 冻结目标 | 已计入实质方法失败 | 不计入原因 |
|---|---:|---|
| BFCL 同-item 顺序修复（48） | 1 | 有效 evaluator、同预算、120 task paired、zero rescue；不是重复调参 |
| CBR absolute rubric（65） | 1 | 306 slots 全解析、同预算、strongest PAIRWISE、CI 全负 |
| 结构轨迹评分（63） | 0 | 方向性 subgroup 信号、CI 跨0；应做一个条件 gate |
| task-state-aware pairwise（66） | 0 | target coverage .767、34 parse failures、1 transport；HARNESS_INVALID 先行 |
| OOF fusion（67/68） | 0 | generic ledger incomplete（67）和 target coverage .9358/7 transport（68）；不是有效方法裁决 |
| AgentIssue/动态工具/EXPBench/Gaia2（49–55） | 0 | ASSET_STOP；没有评价资格 |
| StepFinder/HiAgent/AWM/AgentJudge/SyncMind/PRB V4（57,59–62） | 0 | PAPER_REPRO_BLOCKED/迁移或模型不匹配；无论文主结果资格 |

## 9. 分片建议的执行顺序

1. **当天**：保留 Exp48、65 为负对照；冻结 Exp63/67 的现有 asset/hash/metrics，不再做 post-hoc 子集。
2. **第1–2天**：修 Exp67 generic orientation/input ledger，重算同一 OOF；若 comparator 仍不完整或 target 不再正，停止该分支。
3. **第1–3天并行**：在不改模型的前提下修 Exp57 CPU/官方设备 embedding contract；同时冻结 AFTraj missing/ambiguous policy。
4. **第3–5天**：只实现 Exp63 一个 selective gate，开发集内预注册 threshold/拒绝率；Exp67 仅在 Base+A 资格通过后才实现同一个冲突回退机制。
5. **第5–7天**：对通过探索门的候选，在新任务/新 UUID 上做确认；要求无 leak、同预算、三 seeds 或多数 paired tasks 同向。
6. **当天停止条件**：Exp63 A≤Base；Exp67 comparator audit仍不合格；任一增益来自更多 API/candidate/token；新确认集反向；random gate/simple heuristic 同效。
7. **暂不投入**：49–55 资产、61 runtime、62 V4 Flash、Exp68 第三模块；47 只为 BFCL 重跑提供 Harness。

## 10. 未读/未逐行证据与风险披露

- 381 个 git-tracked 文件已做路径/哈希/大小清单；巨大第三方 raw/archive、Parquet、candidate replay 和不含科研结论的第三方源码按 schema/hash/调用链核验，不逐行展开。
- Exp48 candidate replay 大文件、Exp56 Graphectory raw tree、Exp58 Parquet、Exp62/65/66 raw prompts 未持久化或不应重读；coverage JSON 标明具体项目。
- Exp59–61 的实时/API/Docker 不能在本审计中重新调用；仅复核已有 ledger、runtime smoke、version 和决策 JSON。
- Exp68 7 transport failures 仍是当前最大风险；修复前只能称 Harness invalid + conditional negative signal。

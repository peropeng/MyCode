# 结论43：方向 D——BFCL 接口契约鲁棒性与失败修复实时 Gate 记录

> 状态：**Gate0/1 GO；四种合法修复机理均 STOP；第二章永久 STOP；两章未 GO**
> 建立时间：2026-08-21
> 候选题目：《面向状态化工具智能体的接口契约鲁棒性诊断与失败修复方法研究》
> 证据原则：公开 response、官方 evaluator 与固定任务可以证明实验床资格；没有 OOF 诊断和修复干预增益前，不得写成两章 GO。

## 0. 当前总览

| 项目 | 当前裁决 | 已有证据 | 尚缺证据 |
|---|---|---|---|
| Gate0：官方资产与严格 join | **GO** | BFCL 四个预注册家族各 200 task/200 public response，均 200/200 严格 join；官方 evaluator/decoder 可导入 | 结果仓库根许可证为 UNKNOWN，因此只提交 metadata/哈希/派生指标，不再分发原文 |
| Gate1：独立样本与稳定 replay | **GO** | 四家族各 30；全局 120 个 task hash、120 个结构签名唯一；双 replay 120/120 一致，0 harness error | 仅证明 replay 合同稳定，不证明诊断、修复或跨模型泛化 |
| 第一章：接口契约失败检测/诊断 | **未运行，CONDITIONAL** | 120 条中 clean VALID 75，存在可稳定重现的失败 | 必须以 grouped OOF、online-only 特征胜过强规则基线；离线 evaluator 错误类不可作输入 |
| 第二章：证据驱动修复 | **永久 STOP** | 隔离重评后：契约 patch `75 -> 77`，调用裁剪 `75 -> 77`，schema/literal 替换 `75 -> 76`；Sol 复审批准的最后一个同 item 调用顺序上界仍为 `75 -> 75`、净救回 0、CI `[0,0]` | 不再增加第五个局部 operator，不训练 Gate2 诊断器 |
| 两章总体 | **STOP** | 数据/evaluator 资格成立，但四种合法机理均未形成第二章信息价值；最后一个桥连 Oracle 上界也为 0 | 转入2025--2026正式论文重筛后的 AgentIssue 资产/Gold Gate0；旧 AgentDojo 动态授权 V1 已因重叠淘汰 |

## 1. 锁定资产

- 官方代码：`ShishirPatil/gorilla` commit `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`。
- 官方包：`bfcl-eval==2026.3.23`，Python `>=3.10`。
- 公开结果索引：`HuanzhiMao/BFCL-Result` commit `6830ed13035c0cfee9aa7a9a0ffed70f10b3dd50`，固定 snapshot `2025-12-16/result/BitAgent_BitAgent-Bounty-8B/multi_turn`。
- 家族：`multi_turn_base`、`multi_turn_miss_func`、`multi_turn_miss_param`、`multi_turn_long_context`。
- 无付费 API、无新模型生成；runtime、raw response、Gold、prompt/state 与 inference log 均不提交。

## 2. 主线程审查修正

初次 120-run 虽为 120/120 replay 一致，但只得到 95 个跨家族唯一结构；原因是四个家族复用了底层场景。主线程拒绝把同题家族变体计为 120 个独立任务，并要求：

1. 结构签名加入 public `question + initial_config + missed_function + involved_classes + path`；
2. 四家族共享全局 `seen_signatures`，每家族仍固定取 30；
3. Gate1 decision 与测试直接要求 `total_unique_structure_signatures=120`；
4. manifest 只保留 task/structure 哈希、计数和布尔，不保留 raw ID 或签名前像。

修正后实际为 120 行、120 个唯一 task hash、120 个唯一结构签名。该修正改变独立性口径，但未改变 replay 结论。

另有两个可信性修正：

- 相对 manifest 输出路径曾误写到 worktree 根目录；已改为实验目录内 `manifests/`，误产物未提交。
- 离线 evaluator 的 coarse error class 最初列入未来 diagnosis/repair 可见字段；已移入严格禁区。它由 Gold/reference 参与产生，只能做离线评价标签，不能作为 online 特征。

## 3. Gate0/1 实测

### Gate0

- 四家族 task 与 response 均为 200/200，ID 无重复，严格 join 4/4 通过。
- 官方 `multi_turn_checker` 与 `BitAgentHandler` 可导入。
- 每家族固定 5 条的 20-sample probe：20/20 join，双 replay 20/20 一致，0 harness error。
- 结果仓库没有可确认根许可证；本实验按最小再分发边界只提交哈希、计数、公开 schema 和派生结果。

### Gate1

| 家族 | 独立任务 | 双 replay 一致 | clean VALID | harness error |
|---|---:|---:|---:|---:|
| base | 30 | 30 | 22 | 0 |
| miss_func | 30 | 30 | 14 | 0 |
| miss_param | 30 | 30 | 22 | 0 |
| long_context | 30 | 30 | 17 | 0 |
| 合计 | 120 | 120 | 75 | 0 |

首次 replay 的其余 45 条由 28 条 force termination 与 17 条 evaluator invalid 构成。错误类型的稳定存在说明后续研究有候选信号，但这些类型本身来自离线 evaluator，不可直接当诊断输入。

## 4. 冻结的 online/Gold 边界

未来在线策略最多接收当前及历史公开 response、公开 task/tool schema 与由其直接计算的语法/类型/枚举/引用一致性特征。严格禁止：

- `ground_truth`、`possible_answer`、evaluator answer/error class；
- future user/assistant/tool turns；
- `initial_config` 或隐藏 state snapshot；
- `inference_log`、最终 score、raw result archive 中的额外日志；
- 用 Gold reference 的 turn 数、目标调用或状态变化反向定义在线规则。

官方 Gold 只能在预测/修复输出完全冻结后，由隔离的离线 evaluator 读取并评分。

## 5. 当前严格裁决

方向 D 已通过数据、join、独立性和 evaluator 稳定性资格门，可以进入 Gate2/3；这比 A/B/C 的自然数据入口更可行。但当前仍是 **0 个章节 GO**：75/120 是公开模型原始正确率，不是本项目方法成绩；120/120 是重复一致率，不是诊断准确率或修复收益。

下一步必须先做最低成本 repairability probe：确认失败 response 中是否保留足够的当轮调用、公开 schema 和必要执行反馈，使 canonicalize/type-enum normalization/abstain-clarify/retry 等变换能产生可被官方 evaluator 重评的真实干预。如果只能读最终调用、缺少必要中间 tool result 或必须重新调用模型，方向 D 应在 Gate2 前 STOP，而不是构造虚假修复。

## 6. “三次无进展后升级 Sol Max”的计数口径

该规则按**同一个明确研究目标**计数：必须先后更换三种实质不同的模块或实验设计，仍都不能达到同一预注册预期，才触发新的 Sol Max 独立调研。以下不计为三种设计：安装/下载失败、依赖修复、同一方案重跑、阈值微调、代码 bug 修正，或不同研究方向各失败一次。

实验44的 Oracle repairability probe 是“BFCL 预执行修复是否具有信息价值”这一目标的**设计 1/3**。即使本轮 STOP，也只记录为 1/3；后续应由 Luna 先尝试边界不同且理论上合理的设计 2、设计 3，不能因单轮失败或五分钟无响应立即切换 Sol。五分钟规则只用于催促执行进度。

## 7. 实验44：修复目标设计 1/3 的实测

设计1冻结为“已有轮次、已有 response item 的执行前契约 patch”：`No`、Envelope/Name/Type canonicalization、删除 schema-invalid call、仅从当前 user turn 唯一字面量补一个 required scalar、整轮 abstain、固定组合，以及一个非 Oracle SchemaRuleRepair 基线。

可信性边界：

- 120 个任务先全部构造 3264 个候选并记录完整输出 digest；之后才打开 `possible_answer` 和 evaluator。
- candidate policy 的输入数据类只含当前及历史 user/response 前缀与公开 function schema；不接收 task、family、Gold、state、path、missed function、reference 长度、未来 turn、offline error 或 inference log。
- 所有 arm（含 No）的 candidate hash 都承诺完整候选输出；完全相同的同任务输出只缓存 evaluator 结果，预注册 candidate row 仍全部保留。
- 初版 support audit 曾把 JSON 空格重序列化误计为 Name/Type/Fill 变化。主线程拒绝后，语义未变时保留原 text；最终 Name/Type/Fill 的真实变化均为 0，DropInvalid 为 354 个候选/102 task，Abstain 为 388 个候选/120 task。
- 主门最强基线在全体 120 task 上先固定为一个真实 arm（No=75，SchemaRule=70），不再逐 task 组合成伪 Oracle 基线。

实测结果：

| 项目 | 结果 |
|---|---:|
| No clean VALID | 75/120 |
| SchemaRuleRepair | 70/120 |
| Oracle VALID | 75/120 |
| Oracle 相对 No | 0% |
| Oracle 净救回 | 0/120 |
| paired bootstrap 95% CI | [0, 0] |
| 全候选 task-level 双 replay 一致 | 120/120 |
| harness error | 0 |

设计1裁决：**STOP**。失败原因是候选没有信息价值，而非 evaluator 不稳定。按照修正后的“三设计”口径，只记为修复目标的 1/3，不进入 Gate2 诊断器，也不因此直接把整个方向 D 判永久 STOP。

设计2应改变修复模块，而不是调设计1阈值：测试“调用级选择性裁剪/隔离”——对已有 turn 内多个已解码调用构造 leave-one-call-out、keep-one-call、删除严格重复调用等 Gold-blind 候选，判断 extra/harmful call 是否可被官方 evaluator 的 Oracle 上界显著救回。设计3若仍需要，则测试基于当前 user 明示 literal 与公开 schema 的单参数/兼容函数局部替换；两者仍不得补未来轮、读取状态或调用模型。

## 8. 实验45：修复目标设计 2/3 的实测

设计2与设计1的模块边界不同：不再修改函数名、参数名或参数值，而是对公开 response 中已存在的 item/call 做选择性裁剪。冻结 arm 为 `No`、`DropOneCall`、`KeepOneCall`、`DropOneResponseItem`、`KeepOneResponseItem`、三种严格去重，并另设一个全局 `ExactDedupRule` 非 Oracle 基线。

可信性边界：

- 与设计1沿用同一个固定 120-task manifest，先冻结全部 9418 个 Gold-blind 候选，再打开 Gold 离线评分。
- policy 只能看当前及历史公开 user/response 前缀与当轮可见 schema；不接收 family、path、Gold、未来 turn、offline error、hidden state 或 inference log。
- support audit 先证明模块确有可操作对象：98/120 含 multi-call，120/120 含 multi-response-item，33 条存在 turn 内重复，8 条存在历史重复；共解码 2433 个 call。
- 全局最强单一 baseline 是 `No=75/120`；`ExactDedupRule=74/120`，没有按任务拼接为伪 baseline。

实测结果：

| 项目 | 结果 |
|---|---:|
| 冻结候选 | 9418 |
| No clean VALID | 75/120 |
| ExactDedupRule | 74/120 |
| Oracle VALID | 75/120 |
| Oracle 相对最强 baseline | 0% |
| Oracle 净救回 | 0/120 |
| paired bootstrap 95% CI | [0, 0] |
| 全候选 task-level 双 replay 一致 | 120/120 |
| harness error | 0 |

设计2裁决：**STOP**。公开 response 中确实存在多调用、多 item 和重复调用，但选择性裁剪不能在官方 evaluator 下救回任何 No 失败样本。因此这是第二种模块的信息价值失败，记为同一修复目标的 **2/3**，不是同一设计的调参重跑。

下一步只运行预注册的设计3：基于当前 user 前缀明示字面量和公开 schema，枚举单参数填充/替换、类型兼容的函数替换，以及最多一次“函数替换+缺失参数填充”。仍然不得新增调用、补未来轮、删除调用、读 hidden state 或调用新模型。只有设计3也未达到预注册门槛，才满足该目标“三种实质不同的模块均无进展”并可委派 Sol Max 做新的独立调研。

## 9. 实验46：修复目标设计 3/3 的实测

设计3的模块边界是“对已有 call 做 schema/当前可见 user literal 支持的局部替换”，与设计1的契约规范化、设计2的调用删除/裁剪都不同。冻结候选族为：已有参数的可见字面量替换、缺失 required 参数填充、兼容参数互换、兼容函数替换、函数替换+一个字面量填充、明示 enum 对齐，并另设全局 `LexicalSchemaRule` 非 Oracle 基线。

可信性边界与主线程修正：

- 同一固定 120 task 的 26503 个候选先全部冻结，取得 25839 个完整输出 digest；`support-only` 重算明确输出 `gold_loaded=false`，之后才打开 `possible_answer` 并导入官方 evaluator。
- policy 的类型表面只有当前/历史 user 前缀、response 前缀与可见 schema；候选不增删、不重排 call，每个候选只针对一个已有 call。
- 主线程拒绝了初版“最多一次局部编辑”与组合算子实际两个原子编辑的矛盾；最终合同明确为每候选最多2个原子字段编辑，且只有“函数替换+填一参数”可使用2个。
- 主线程要求测试覆盖六类算子，并增加实际 phase instrumentation，不再只依赖报告中的布尔声明。最终 10 项测试全部通过。
- 落盘的 29MB candidate replay 经递归 key 审计，只含 task hash、候选/操作索引、完整输出 digest、布尔评分与聚合计数；无 raw response、Gold、schema 或 literal 原文。

support audit 并非为空：

| 候选机会 | 候选数 | 覆盖 task |
|---|---:|---:|
| 已有参数替换 | 5874 | 101 |
| 兼容参数 swap | 2083 | 92 |
| 兼容函数替换 | 8774 | 107 |
| 函数替换+一个 literal | 9532 | 87 |
| 缺失 required+兼容 literal | 0 | 0 |
| enum 明示对齐 | 0 | 0 |

正式结果：

| 项目 | 结果 |
|---|---:|
| 冻结候选 | 26503 |
| No clean VALID | 75/120 |
| LexicalSchemaRule | 5/120 |
| 全局最强 baseline | No（75/120） |
| Oracle VALID（不含 baseline） | 75/120 |
| Oracle 相对最强 baseline | 0% |
| Oracle 净救回 / 受损 / 不变 | 0 / 0 / 120 |
| paired bootstrap 95% CI | [0, 0] |
| 全候选 task-level 双 replay 一致 | 120/120 |
| harness error | 0 |

设计3裁决：**STOP**。主线程已独立复跑 support-only、26503 候选完整 evaluator 双 replay、10项测试、`py_compile`、diff 与结果键审计；复跑结果与提交完全一致。

因此同一目标已正式累计为 **3/3**：契约字段 patch、调用级选择性裁剪、schema/可见字面量替换是三种实质不同的修复模块，均不能救回任何 No 失败任务。现已满足用户定义的 Sol Max 升级条件；下一步由 Sol Max 独立审阅这是 BFCL 公开资产的可观测性上限，还是尚有机理不同的合法修复桥；在复审前不强行训练 Gate2 诊断器。

## 10. Sol Max 独立复审发现的致命 evaluator 隔离缺陷

> 本节覆盖第7—9节的旧 Oracle/STOP 口径。第7—9节的候选定义、Gold 前冻结、support 统计与隐私审计仍可保留，但三组官方 evaluator 分数、Oracle、bootstrap 和 STOP 裁决全部降级为 **INVALID**。

独立复审后主线程直接核对官方 `multi_turn_utils.py`，确认：

1. `execute_multi_turn_func_call` 使用 `model_name + test_entry_id + class_name` 生成实例名，并把有状态 class instance 存入该模块的 `globals()`。
2. 同一 namespace 再次出现时，官方逻辑把它当成“subsequent turns”并复用前一实例；checker 不在 candidate 结束后自动删除。
3. 实验44/45/46 的 `official_outcome` 对同一 task 的所有候选只按 `replay_index + task_hash` 生成 namespace，没有 candidate hash；`No` 后所有候选会沿用前面候选已改变的模拟状态。
4. 两条 replay 流都按同一候选顺序独立污染，所以“120/120 双 replay 一致”并不能检出这种系统误差。

正确修复合同：

- 不改三种已冻结候选规则，因此这是 evaluator bug 修正与重评，不算新的第四种设计。
- namespace 必须包含 task hash、candidate full-output/candidate hash 与 replay index，保证两个 candidate 绝不复用实例。
- 每个 candidate 评分后在 `finally` 中删除 model 与 ground-truth 的全部 involved-class instance，避免内存增长与后续隐式复用。
- 增加全候选原顺序/确定性 shuffle 顺序不变性，并抽样用独立新进程评分对照。若同一 task/candidate 的 outcome 随顺序或进程改变，修复后实验仍 INVALID。
- 重评三组 No/Oracle/强基线和 bootstrap，再根据原门槛分别计数 GO/STOP。

Sol 同时找到一个三组候选确实没覆盖的机理：官方 checker 按 call list 顺序实际执行，只在 response 值比较时做 unordered；而前三组合同均明确 `call_reorder=false`。固定120个任务中98个含 multi-call，旧的17个evaluator-invalid中16个含 multi-call。只有隔离重评仍不能让三种模块 GO 时，才允许唯一一个新桥：**同一已有 response item 内的 call 顺序全排列/最小重排**，不跨 item/turn，不改 call 内容，不读 Gold/未来轮/状态。它不能在旧污染 evaluator 上直接运行。

## 11. 实验47验收后的隔离重评结论

> 本节覆盖第7--10节中“待隔离重评”的中间状态。旧污染分数仍为 INVALID；以下才是当前有效科学结果。

### 11.1 隔离合同

- 每个 candidate/replay 的 official evaluator namespace 都包含 `experiment + task_hash + candidate_hash + full_output_digest + replay_index`。
- checker 前检查 expected model/ground-truth/class instance 不存在；任一 preexisting key 直接标记 `HARNESS_INVALID`。
- `finally` 删除本 candidate 实际创建的 model/ground-truth/class keys；对早退路径中未创建的最大 expected key 只记录，不误判泄漏。
- 正式 replay1 按候选升序，replay2 按逆序；另以 seed `20260821` 对全候选 shuffle 做顺序不变性审计。
- 独立 subprocess 复核全部 120 个 No，并对每个 family x operator 固定抽取至少 5% 非 No 候选。

### 11.2 三种设计的有效结果

| 设计 | 候选数 | No | 全局规则基线 | Oracle | 净 rescue | 相对提升 | 95% CI | 裁决 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 契约 patch | 3264 | 75 | SchemaRuleRepair 70 | 77 | 2 | 2.67% | [0, 4.17pp] | STOP |
| 调用级裁剪 | 9418 | 75 | ExactDedupRule 74 | 77 | 2 | 2.67% | [0, 4.17pp] | STOP |
| schema/literal 局部替换 | 26503 | 75 | LexicalSchemaRule 6 | 76 | 1 | 1.33% | [0, 2.50pp] | STOP |

三者均未达到冻结门：相对全局最强基线至少 10%、净 rescue 至少 8、paired bootstrap 95% CI lower > 0。因此它们现在才能被计为“同一修复信息价值目标下的三种实质不同设计全部无进展”。

### 11.3 harness 验收

- 全量顺序审计：3264/3264、9418/9418、26503/26503 candidate fingerprints 完全一致，mismatch=0。
- 独立新进程：303/303、601/601、1449/1449 完全一致，均包含全部 No 与分层 5% 非 No。
- 三组 created=removed，preexisting=0，final leak=0，checker exception=0，`harness_invalid=false`。
- No 均为 75/120，与实验43的 clean baseline 完全复现。

### 11.4 下一步的唯一合法桥

按用户的“同一目标换三种模块/设计仍无进展才调研”规则，现已正式满足升级条件。Sol Max 独立审阅已完成，只批准一个机理上不重叠的桥：`Within-Item Call Ordering`。

该桥只重排同一已有 response item 内的 calls，保持 call multiset、函数名、参数、值和数量不变；不跨 item/turn，不增删，不读 Gold、future question、tool output 或 hidden state。公开 support 为 98/120 任务存在 multi-call，预计约 119,960 个 changed permutations。

门槛仍为 10% 相对增益、净 rescue >= 8、CI lower > 0，并且要求升/逆序全候选一致、No 120/120 复现、0 harness error 和 fresh-process 一致。若该桥也未过科学门，方向 D 第二章永久 STOP，不再增加第五个局部 operator。

## 12. 实验48：同 item 调用顺序桥的最终裁决

实验48严格执行 Sol Max 复审批准的唯一剩余机理。它只重排同一既有 response item 内的 calls，保持 call multiset、函数名、参数、参数值和数量不变；不跨 item/turn，不增删 call，也不接收 Gold、未来轮、tool output、hidden state 或 evaluator error。

可信性验收：

- 固定120个独立 task/structure；98个 task、668个 item 存在 multi-call support。
- 在读取 Gold 前冻结全部120,200个候选，其中119,960个是非原顺序排列；候选 hash 承诺完整输出。
- 全候选正序/逆序双 replay 共240,400次；120/120 task 的全部 candidate outcome 一致，0 harness error。
- 固定 seed shuffle 的120,200/120,200个 outcome fingerprint 与正式结果一致。
- fresh subprocess 复核全部120个 No 与按 family x operator 分层抽取的6009个非 No，共6129/6129一致。
- evaluator `created=removed=5972`，preexisting=0，final leak=0，checker exception=0；主线程复跑8项合同测试全部通过。

正式结果：

| 项目 | 结果 |
|---|---:|
| No clean VALID | 75/120 |
| SchemaDependencyOrder | 73/120 |
| 全局最强 baseline | No（75/120） |
| 排列 Oracle VALID | 75/120 |
| Oracle 相对提升 | 0% |
| Oracle 净救回 | 0/120 |
| paired bootstrap 95% CI | [0, 0] |
| 科学裁决 | **STOP** |

这不是“尚未找到更好的排序规则”：在冻结边界内，全部非原顺序排列的 Oracle 上界都不能把任何 No 失败任务变为有效。它同时未达到相对提升10%、净救回至少8和CI下界大于0三个预注册门。

因此方向D的第二章现为**永久 STOP**。三次实质不同设计失败后已经按用户要求完成Sol Max独立审阅，审阅所找到的唯一漏检机理也已穷举失败；不再增加第五个局部算子，不以调参、重跑或换规则重新计数，也不进入第一章诊断器训练。方向D整体不能形成符合统一要求的两章毕设。

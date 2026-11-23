# 实验44：方向 D BFCL Oracle repairability 资格报告

## 0. 旧版结果作废与隔离修正版

旧版评分曾按 `(task_hash, full_output_digest)` 缓存官方 checker 结果；官方 `multi_turn_utils` 会按 `model_name + test_entry_id + class_name` 在模块 globals 复用 stateful instance，因此相同 output 的不同 candidate 可能跨 candidate 共享状态。旧版 `857 unique pairs / 2407 duplicate candidates reused` 及其派生分数均为 **INVALID**，本报告不再引用为证据。官方 runtime 未被修改；修正版为每个 candidate/replay 生成含 experiment、task hash、candidate hash、完整输出 digest、replay index 的独立 namespace，并在 `finally` 清理 model、ground_truth 及 involved class instance keys。

修正版正式双 replay 按 candidate 升序与逆序执行，另用固定 seed `20260821` shuffle 全量复核，并用独立 fresh subprocess 复核全部 No 与每个 family×operator 非 No 候选至少 5%。三项顺序/进程审计均按 candidate outcome fingerprint 比较，不以总分替代逐 candidate 证据。

## 1. 最终判定

本实验的 `Gate3 decision = STOP`。固定 120 个 task/structure 上，No 基线双 replay 的 clean `VALID` 为 **75/120**，与实验43 Gate1 完全复现；SchemaRuleRepair 为 **70/120**；允许的全部 Gold-blind candidate 中，Oracle 为 **77/120**。

| 门槛 | 实测 | 判定 |
| --- | ---: | --- |
| No 基线 | 75/120 | 复现 |
| SchemaRuleRepair | 70/120 | No 更强，主门使用 No |
| Oracle VALID | 77/120 | 相对 No 2.6667%，未达到 ≥10% |
| 相对最强基线净救回 | 2/120 | 未达到 ≥8 |
| task/structure paired bootstrap 95% CI | [0, 0.0333] | 下界不大于 0 |
| 所有 candidate replay task 一致性 | 120/120 | 通过 |
| 每家族一致性 | 30/30 × 4 | 通过 |
| harness error | 0 | 通过 |

因此该证据只支持“接口重放和候选评估可复现，但同轮执行前 response patch 的理想信息上界没有研究收益”。按预注册规则，不进入 Gate2 诊断器，不声称 post-execution retry、interactive recovery、后续轮补生成或两章论文 GO。

## 2. 固定样本、冻结和隔离

- 严格复用实验43 Gate1 的四家族各 30 条，120 个 `task_id_sha256` 和 120 个 `structure_signature_sha256` 均唯一；没有重选样本。
- public freeze 阶段只构造 `CandidateInput(question_turns, response_turns, response_value, schema)`。operator 的调用入口是 `apply_operator(name, text, context)`，其中 `context` 只含当前及历史公开 user message、公开 result 字符串和公开 function schema。
- candidate freeze 完成并写入 `candidate_support_audit.json` 后，第二阶段才打开原始 task 和 `possible_answer`，构造 `OfflineCase` 并调用官方 evaluator。candidate 函数没有收到 task、Gold、state、path、missed function、family、reference 长度、未来 turn、error class 或 inference log。
- response 只允许在已有 turn 的已有 response item 上 patch；outer turn 数不变，28 条原始 turn-count mismatch 没有利用 reference 长度补轮。
- `candidate_hash` 是每个 arm 的完整 canonical candidate output 加 operator/turn metadata 的 SHA256；另记录完整 output digest 作为 namespace 输入和等价输出审计。修正版不跨 candidate 复用官方 checker 结果；每个 candidate 的两个 replay 都真实进入独立 namespace，保留每个预注册 spec 的结果行。

## 3. Candidate support audit（未打开 Gold）

候选总量为 **3264**：No 120 条；7 个 operator 在 432 个已有-turn 位置各生成一条；SchemaRuleRepair 120 条。公开 response item 的 parsed shape 为 1063 个 JSON array、340 个 invalid JSON。

为避免格式重序列化伪信号，operator 在 parsed payload 语义未变时保留原始 text；真实变化如下：

| operator | candidate rows | changed rows | changed tasks | 语义变化 rows |
| --- | ---: | ---: | ---: | ---: |
| No | 120 | 0 | 0 | 0 |
| EnvelopeCanonicalize | 432 | 0 | 0 | 0 |
| NameCanonicalize | 432 | 0 | 0 | 0 |
| SafeTypeCoerce | 432 | 0 | 0 | 0 |
| DropInvalid | 432 | 354 | 102 | 354 |
| FillFromCurrentLiteral | 432 | 0 | 0 | 0 |
| Abstain | 432 | 388 | 120 | 388 |
| MinimalCombined | 432 | 354 | 102 | 354 |
| SchemaRuleRepair | 120 | 102 | 102 | 102 |

3264 candidate rows 对应 837 个全局 unique full-output digest；修正版实际执行 **3264 × 2 = 6528** 个 candidate/replay scoring calls，不因 output digest 相同而跨 candidate 复用 checker。候选池、Gold 边界和 Oracle tie 顺序均未改变。

## 4. Replay 与 Oracle 结果

No 的双 replay 为 120/120 一致、0 harness error、92/120 evaluator called、28/120 原始 turn-count mismatch、75/120 clean VALID。所有候选的 task-level replay 一致性为 120/120；任何 candidate 均没有 harness error。

| 家族 | No | SchemaRuleRepair | Oracle | Oracle rescue |
| --- | ---: | ---: | ---: | ---: |
| multi_turn_base | 22/30 | 22/30 | 22/30 | 0 |
| multi_turn_miss_func | 14/30 | 9/30 | 14/30 | 0 |
| multi_turn_miss_param | 22/30 | 22/30 | 24/30 | 2 |
| multi_turn_long_context | 17/30 | 17/30 | 17/30 | 0 |
| 合计 | **75/120** | **70/120** | **77/120** | **2** |

Oracle tie 顺序为 No（零编辑优先）、最小 edit distance、固定 operator/turn 顺序。主门的 stronger baseline 先在全体 120 条上比较：No=75 大于 SchemaRuleRepair=70，因此所有 task 的主门比较、rescue 和 bootstrap 都使用同一个 No arm，不使用 per-task union 混合基线。

固定 seed 20260821、10,000 次 unique-structure cluster paired bootstrap 的 Oracle−No delta 点估计为 0.0167，95% CI=[0, 0.0333]；下界不大于 0，因此不满足 Gate3。

## 5. 隔离、顺序和 fresh-process 审计

- evaluator isolation audit：6528 scoring calls；checker invocation=5758；created=removed=18254；preexisting=0；missing=0；final prefix leak=0；`harness_invalid=false`。334 个 expected key 未创建是 checker 在 turn-count/decode 早退的记录，不是残留实例。
- 固定 seed shuffle：3264/3264 candidate outcome fingerprints 完全一致，升序/逆序正式 replay 的 canonical order digest 不同，shuffle 后两条 order digest 也不同；shuffle created=removed，preexisting=0，final leak=0。
- fresh subprocess：全部 120 个 No 加上 183 个固定 family×operator 非 No 候选，共 303 个 candidate，303/303 outcome fingerprints 一致，checker exception=0，created=removed=1538，final leak=0。

## 6. 研究边界和后续裁决

该 STOP 只针对“公开 response 的执行前、同轮、固定契约 patch”这一最低成本 repairability 假设。它不能被解释为 BFCL evaluator 不可运行；实验43 已证明 Gate0/Gate1 可复现，本实验也证明两次官方 replay 稳定。

真正的 post-execution retry/闭环恢复需要公开的 tool output/state/handler step 和允许补生成的模型响应；本固定 BitAgent 结果缺失这些字段，不能通过 `inference_log` 越界补齐。若未来改变研究问题或获取合规新响应，应重新注册输入边界、修复动作、模型生成和数据许可，不能把本实验的 Oracle 结果扩展成 interactive recovery 结论。

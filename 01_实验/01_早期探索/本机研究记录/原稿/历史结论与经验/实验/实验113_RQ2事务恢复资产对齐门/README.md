# Exp113：RQ2 事务恢复资产对齐门

本目录只冻结 Exp113 的受控资产资格门，不实现 RQ2 方法模块，也不产生章节 GO。
首选 E02 已有 34 tasks / 8 repositories；每个 task 使用同一 checkpoint 的八动作窗口、
可执行干预和 Python compile target probe，并明确标记为 `controlled_syntax_fault_only`。

当前冻结的 `Predicted` adapter 只允许读取 E02 选择清单的身份与窗口几何，再把匹配的
assistant-call 窗口投影成 Exp112C 的匿名 step record。所有 Gold/责任位置/故障注入/探针/
干预/patch/test/resolved 字段在投影前隔离。部署拟合固定使用 Exp112 development train
的 731 records / 716 task groups、5-fold group OOF 和 deployment seed 20260816，E02
记录数为零；不调参、不用 E02 Gold 选模型。

五个 bridge arms（No、Random、Shuffled、Predicted、Oracle）以及 fixed-last、
uniform-replay、fixed-rollback 都冻结为同一 candidate pool 和一个 top-1 intervention /
一个 probe 的预算。Oracle 仅作 evaluator 上界。所有硬条件通过后的唯一资格 verdict 是
`EXP113_ASSET_ALIGNMENT_GO_CONTROLLED_ONLY`，仍不计方法模块或章节 GO。

`No` 的正式语义是 `No attribution`：固定 position 0 的无 RQ1 责任归因处置，
不是 Exp114 的 `No recovery`。本阶段已实现 formal qualification runner，但尚未授权或执行
single formal qualification run，也没有资格结果。
此次冻结纠正只把 SFT 与六个仓库绑定到主线程核对过的
targeted paths，并要求后续 preflight 只核对存在性与 Git HEAD，不做宽泛资产扫描。

phase-2 非正式 runner 已完成：targeted preflight、synthetic smoke、E02 loader-only /
匿名 adapter construction、5-fold OOF 覆盖检查、deployment-fit 接口、预算与 Gate
合同均有实现测试。真实 loader probe 未计算 Predicted/Oracle 指标，也未写正式结果。
修正后的 counterfactual omission 合同把 34*8=272 个候选全部视为可执行：184 个候选
来自 editor calls，其中 122 个是 state-changing editor 的 `state_delta_omission`
（str_replace/create/insert/undo_edit；当前窗口还没有 delete/edit），62 个 editor view
与 88 个非 editor call 属于 stateless omission。总计 150 个 `stateless_noop_omission` 都
保留同一 target probe，不从候选池删除，也不伪装成状态编辑。
这是正式指标前的合同纠正，不是看结果调参。

正式资格 invocation 已按一次性合同执行一次，但归档为 `HARNESS_INVALID`：
`results/execution_attempt_audit.json` 是 immutable attempt 证据，`results/asset_alignment_gate.json`
未生成，因此没有 Gate、recovery 指标或任何方法/章节结论。失败发生在 helper return unpack：固定
helper 实际返回 `(pairwise_probs, predictions, audit)`，而 Exp113 OOF 调用错误地把第一项当作
`predictions`，随后访问 `prediction["pairwise_probs"]` 触发 `KeyError`。mock helper 复制了错误的
返回合同，所以静态测试漏检。该失败不计资产 GO、RQ2 method GO 或章节 GO，也不构成第二次科学试验；
后续只能由新的 Exp113C correction replay 处理，不能重试或覆盖本次 attempt。

E01/E26 是 supportive controlled assets；TraceElephant 的五个历史例保留为负边界（负责
动作 5/5 可应用但撤销后 5/5 仍失败），不与 E02 合并。E61 仍是 PENDING runtime/blocker
资产，不计方法失败。已停止的 Exp112a 重复支线没有正式结果，不构成第二次试验或 GO 证据。

# Exp116E：E02 原生候选后验状态事务恢复的 hardened state-cost / observed provenance 修正

当前状态：`FORMAL_COMPLETED_SINGLE_INVOCATION`。Exp116 原始 invocation 与 Exp116C 字段适配 invocation 均已封存为 `HARNESS_INVALID`，没有正式 scientific metrics；两者不是本轮新的科学试验。Exp116D 的唯一正式结果已封存为独立 diagnostic positive（state attribution 审计阻断），明确不是 GO。Exp116E 已按授权只调用一次并完成封存；`invoked=true`、`formal_attempts=1`，terminal `COMPLETED/COMMITTED` 是唯一权威完成点。不可变 claim 保持 `RUNNING` reservation 状态，不表示运行未完成。

本轮不修改 Exp114，不读取 Exp114 formal metrics，不重复 Exp113J 资产 coverage/SHA/clone/security/qualification 检查；J accepted verdict 只作为继承前提。Exp116D 不调 Exp96/97/98、不搜索论文、不做参数搜索。模型、conditions、seeds、repository folds、Gate、A router 与 E02-native candidate/state/TNR 科学定义均继承 Exp116C。

## 最终检查点故障锚定

evaluator 的 `original_fault_call` 仅保留为 provenance。实际 controlled fault 固定锚定到当前 visible task replay window 内最后一个实际可重放 call：`effective_fault_call = max(call.call_index <= window_end_call)`。稀疏 call stream 没有合法窗口 call 时 fail closed；有效 call 必须存在且不越过 `window_end_call`。reference 与所有非 responsible candidate 使用同一个 effective call；responsible candidate 也接收该 call 参数，但只由底层 Exp114 replay 的 sealed responsible-position 语义免于注入 fault。每个 cache/record/audit 写明 original/effective、anchoring rule/token、window membership、一次 shared reference digest 与 candidate outcomes。

训练标签的 reference eligibility 必须同时满足 `fault_injected=true` 且 final target probe failed。reference probe 通过时不抛 harness exception：该 task 的 responsible label 为 0，并把 reference eligibility 记为失败；它不能被计为 recovery。eligible reference 下，positive label 仍要求 candidate recovery success、target probe pass、TNR pass。未执行的七个非 responsible candidate 仍是受控 label=0、`conflict_count=0`、`conflict_observed=false`、`observed_cost=0`；只有实际执行路径的完整 conflict count 才进入 utility。

## 继承的科学合同

B 仍是一个不可拆的完整模块：candidate posterior/full ranking、Active/Standby/Escalate state utility、same-checkpoint transaction 与 TNR。A 仍是 Exp108-family registered strategy router。protected native order 首位保持已接受 J Gold-free Predicted top1，tail 使用 outer-train-only posterior；outer repository folds、inner group OOF、固定 ExtraTrees 参数、15 conditions、3 seeds、task-cluster bootstrap、strongest fair baseline 与严格 Gate 均不变。Oracle 只作 sealed upper-bound sanity，不进入贡献比较。method/full-chapter GO 固定为 false；即使未来 controlled Gate 通过，也只能是 controlled-only metric candidate。

## 非正式 preflight 与入口

独立预检为 [exp116d_preflight.json](results/exp116d_preflight.json) 与 [attempt audit](results/exp116d_preflight_attempt_audit.json)。它使用 deterministic synthetic underlying 证明 sparse calls 选择窗口末 call、original call 不泄漏、reference fault/probe 资格、responsible immunity、非 responsible fault、8 candidate 共享 reference digest；不读取 Gold，不运行 ranking/metric，不写 formal namespace。该 preflight 是授权前证据，保留不覆盖；E 当前封存状态见 [formal authorization receipt](results/exp116e_formal_authorization.json)。v1–v5 Exp116 preflight 与 Exp116C preflight 均保留为历史证据。

```bash
python3 实验/实验116_RQ2原生候选后验状态事务恢复/runner.py --preflight-final-checkpoint
python3 -m unittest discover -s 实验/实验116_RQ2原生候选后验状态事务恢复/tests -p 'test_*.py'
```

D formal 入口 `--run-final-checkpoint` 的历史结果已封存，D 的诊断正提升不构成 GO：`DIAGNOSTIC_POSITIVE_NOT_GO_INDEPENDENT_REVIEW_BLOCKED`。D output/audit 与 Exp116/Exp116C 旧 audit 只读保留。

## Exp116E 正式结果封存

Exp116E 的唯一 formal invocation 已完成，正式结果、attempt audit、immutable claim、terminal 与独立报告分别见 [formal output](results/asset_alignment_gate_exp116e.json)、[attempt audit](results/execution_attempt_audit_exp116e.json)、[claim](results/exp116e_attempt_claim.json)、[terminal](results/exp116e_attempt_terminal.json) 和 [formal report](results/exp116e_formal_report.json)。结论为 `EXP116E_RQ2_POSITIVE_NOT_YET_GO_HARDENED_STATE_COST`，是 controlled-only 的正提升但不是 GO；`is_method_go=false`、`is_full_chapter_go=false`。

strongest fair baseline 为 `uniform_without_replacement`，RSR `0.18627450980392157`。B RSR 为 `0.3235294117647059`（relative `+0.736842105263158`，pooled task-cluster 95% CI `[0.02941176470588236, 0.2450980392156863]`）；A+B RSR 为 `0.3137254901960784`（relative `+0.6842105263157894`，CI `[0.0196078431372549, 0.24509803921568624]`）；Oracle RSR 为 `0.35294117647058826`。正式审计包含 24 folds、102 caches、1530 records，`core_required=true`、`no_hardcoded_pass=true`，provenance/fault/cache/latch core 审计通过。

唯一科学阻断是 `state_real_at_least_two_classes_per_fold=false` 与 `state_shuffle_nonidentity_and_joint_counts=false`，所以 `b_attribution_required=false`、`b_candidate=false`、`b_formal_module=false`、`a_plus_b_candidate=false`；数值正提升不能写成 GO。Exp116E 与 Exp116D 数值相同表示 hardened state-cost/observed-provenance 后的可信复现与强诊断正提升，不是第二个完整模块结果。未读取 Exp114 formal metrics，也未重复资产复核，因此结果中的 `inherited_asset_metrics_present=false`。

跨 RQ 口径保持分开：RQ1 `9.8031%`、RQ2 incremental `8.8801%`、cross-RQ cumulative `19.5557%`；不得把累计值归为 RQ2。重复的 Exp112a 没有 formal result，不是试验或 GO 证据。

## Exp116E 冻结边界与一次性提交

Exp116E 只做 state-cost 与底层 observed provenance 的互补硬化；不调模型、conditions、seeds、folds、thresholds，不重复资产资格检查，不读取 Exp114 formal metrics。状态现为 `FORMAL_COMPLETED_SINGLE_INVOCATION`，唯一 invocation 已完成且不得重试、覆盖或重新运行。正式 output/audit 已由 terminal `COMPLETED/COMMITTED` 成对封存；immutable claim 的 `RUNNING` 是不可变 reservation，terminal 才是可接受完成标记。

策略臂 utility 与 label provenance 分离：实际 label 的 `observed_cost` 只描述真实执行；counterfactual policy arm 固定使用 `POLICY_ATTEMPT_COST=2`，按实际尝试前缀计算
`success - 0.01*observed_conflicts - 0.0001*(attempts*2)`，首个成功立即停止。top1 成功时 Active/Standby 成本相同并按固定 tie 规则选择；深层成功偏向 Standby；无成功且有冲突时 Escalate utility 更高。

E 的生产 executor 是 canonical `ObservedFinalCheckpointExecutor`。它在 E 自有目录的 mutation hook 记录真实 `raw_fault_events`，只复用只读 Exp114 的 clone/TNR/verifier 定义；adapter 只校验/规范化底层返回，不能从 bool 合成 call/count。每个 cache 记录底层实际 fault occurrence/call/count、语义 reference token、同一 token 进入真实 verifier、verifier exact class/module/字段/source；reference 与 7 个 non-responsible candidate 各应观察到一次 fault，responsible candidate 为零。call_index 必须严格递增且唯一，effective fault 是 visible replay prefix 的最后一次 call；重复/缺失/矛盾证据、同名 fake verifier 或 token 不一致均 fail closed。

held unseal 前，decision digest 纳入每个 visible task 的 `window_end_call`、`effective_fault_call`、anchor token map；hidden original fault/responsible 字段不进入 digest。runtime gate 只接受真实 observed evidence，不能由 wrapper metadata 自盖章。

E 独立命名空间：

- output：`results/asset_alignment_gate_exp116e.json`
- audit/ledger：`results/execution_attempt_audit_exp116e.json`
- persistent claim：`results/exp116e_attempt_claim.json`
- independent terminal：`results/exp116e_attempt_terminal.json`
- authorization receipt：`results/exp116e_formal_authorization.json`
- formal report：`results/exp116e_formal_report.json`
- preflight v2：`results/exp116e_preflight_v2.json` 与 `results/exp116e_preflight_v2_attempt_audit.json`
- current preflight v3：`results/exp116e_preflight_v3.json` 与 `results/exp116e_preflight_v3_attempt_audit.json`（v2 保留为 superseded）
- historical preflight v1：`results/exp116e_preflight.json` 与 `results/exp116e_preflight_attempt_audit.json`（保留、superseded）

正式 claim 在计算前先完整 staged JSON + fsync，再用 no-replace link 与目录 fsync 发布；claim 是不可变 RUNNING reservation，独立 terminal 也以 staged/full-write/fsync + no-replace 发布，COMPLETED terminal 才是唯一可接受 commit marker；任何 RUNNING/FAILED、缺 terminal、缺任一文件、token/inode/SHA 不符均不可接受且不能重试。E paired writer 只按本次已记录的 dev+inode 清理，绝不按字节或未知路径删除竞争者。canonical authorization receipt 与磁盘 RUNNING claim 在 qualification 读取任务前再次校验，任意路径、writer、executor、token 均不能绕过。该入口已经消费唯一 formal invocation，不得再次调用：

```bash
python3 实验/实验116_RQ2原生候选后验状态事务恢复/runner.py --preflight-hardened-state-cost
```

E preflight v3 是 formal 前的历史证据（不覆盖、不重跑）；它仅运行 synthetic state-cost、immutable claim/terminal、严格 anchoring contract 与 responsible-only pair contract。正式结果的 `inherited_asset_metrics_present=false`，因为本轮不读取 Exp114 metrics、也不重验资产。D 的 `+73.6842%` / `+68.4211%` 与 task-cluster CI 仅作为已封存诊断事实，因 state attribution 审计阻断而明确不是 GO。

# Exp113C：RQ2 资产门 Helper 解包纠正式复跑

本目录只冻结 Exp113 的 correction-only replay，不新增数据、不新增方法模块，也不产生章节 GO。
Exp113 的第一次正式 invocation 在任何完整 adapter ranking 或 formal metric 产生前失败：调用方把
固定 helper 的真实返回 `(pairwise_probs, predictions, audit)` 错当成
`(predictions, pairwise_probs, audit)`，触发 `KeyError: 'pairwise_probs'`。失败 audit 与原目录保持
immutable；原 Exp113 formal output 未生成，也没有暴露结果、Gate 或 recovery 指标。

Exp113C 只通过 read-only proxy 把真实 helper tuple 适配为原 Exp113 caller 所需顺序，调用原固定
helper、原 Exp113 fit/qualification 逻辑；不复制或重写 scientific fit。E02 data/adapter、731/716
deployment train、seed/folds/models、omission、arms、baselines、budgets、六条件 Gate 与 diagnostic
边界均与 Exp113 byte/semantic equivalent。若原六条件通过，唯一 corrected verdict 为
`EXP113C_ASSET_ALIGNMENT_GO_CONTROLLED_ONLY_CORRECTED_REPLAY`，仍不是 RQ2 method GO 或 chapter GO。

旧 mock helper 复制了错误的 tuple 合同，因而漏检本 harness defect；Exp113C tests 使用真实顺序并拒绝
旧顺序。新的 formal output 固定为
`results/asset_alignment_gate_corrected.json`，attempt audit 固定为
`results/execution_attempt_audit_corrected.json`，single-write/no-retry/no-overwrite。

Exp113C 唯一正式 invocation 已执行一次并封存为 `HARNESS_INVALID` / `ASSET_SOURCE_INVALID`：
在任何完整 ranking 或 formal metric 产生前，counterfactual replay 对 bound repository source 执行
`git reset --hard 322ef60ba7231bbd4f735b273e88e67afb57ad17` 失败。audit 的
`actual_command_attempts=1`、`formal_output_written=false`，因此没有 corrected formal result、Gate、
recovery 指标或 method/chapter GO 结论。原 Exp113 failed audit 与 Exp113C output 均不可覆盖；本次
失败不构成第二次科学试验，也不计资产或方法失败，当前不修复、不重跑。

Exp113C 不是第二次科学试验，只是对第一次 `HARNESS_INVALID` 的最小 harness correction replay。正式
run 需主线程单独审查和授权。

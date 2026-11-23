# Exp114：RQ2 状态感知事务式恢复

当前状态：`FORMAL_COMPLETE_CONTROLLED_ONLY`。Exp114 唯一 formal invocation 已完成并封存；结果 verdict 为 `EXP114_RQ2_POSITIVE_NOT_YET_GO_STATE_AWARE_TRANSACTIONAL_RECOVERY`，B/A+B 均未通过严格科学 Gate，且 `is_method_go=false`、`is_full_chapter_go=false`。Exp113J 的已接受 GO 只作为 inherited prerequisite；Exp114 不重复 J 的 SHA、覆盖、clone 或 source-security audit。

## 科学边界

Exp114 的 A 是 Exp108 机制家族的严格 outer-repository OOF continuous-utility diagnosis/strategy router；B 是一个不可拆分的完整模块，由 Active/Standby/Escalate 状态规则、同 checkpoint 事务式恢复和 Transactional No-Regression verifier 共同组成。A+B 使用 A 的 route，再进入 B 的状态与事务；B standalone 固定使用 RQ1 Predicted ranking；A standalone 只执行 A route 首候选，不隐式 fallback 到状态或事务。

数据按 repository 做 8 个 outer folds，每个 repository 在每个 seed 恰好 held 一次；seed 固定为 `20260816, 20260817, 20260818`。34 tasks、8 repositories、每 task 8 candidates 的可见响应窗口共 272 calls，冻结为 104 successful state deltas、18 failed-editor transaction no-ops、150 stateless no-ops。

特征只允许匿名结构：position/rank、action family/shape category、response category/status、state-changing、rollback feasibility、window distance、ranking margin/entropy、预计成本，以及冻结的四维注册策略类别 one-hot（`strategy_predicted`、`strategy_fixed_last`、`strategy_uniform_replay`、`strategy_fixed_rollback`）。策略类别是 Gold-free 的枚举，不是 task/repo/id。task/repo/id/hash、Gold、responsible/fault、outer-held、probe、source/path/commit、future 字段均禁止进入 A 的决策。模型固定为 Exp108 的 `ExtraTreesRegressor(256, max_depth=4, min_samples_leaf=20, max_features=1.0, bootstrap=False, n_jobs=1)`；OOF 或 split-conformal 样本不足时 fail closed，不调阈值。

held evaluator/outcome/Oracle 不是从 Exp113J aggregate 直接传入。Exp114 使用 private `RawOutcomeProvider`：outer-train labels 只按显式 train task IDs 投影为四个注册策略臂（`Predicted`、`fixed-last`、`uniform-replay`、`fixed-rollback`）的 continuous utility 样本，保留 arm 身份、zero 与 ties；每个训练样本的策略 feature/order 严格使用该 inherited J arm label 的 frozen `source_selected_position`。uniform-replay 不通过事后 seed 搜索匹配标签，fixed-rollback 不可用时只保留明确 abstention。utility 冻结为 `success - 0.01*conflict_count - 0.0001*(replayed_prefix_window_calls+target_probe_executed)`。不可用 fixed-rollback 是 utility-zero abstention，绝不冒充 selected position。A 只比较策略 feature payload，不按候选 position 重新拟合 RQ1；held route 仍在 decision freeze 后按当前预注册 deterministic seed 生成。

RQ1 Predicted 只投影已接受 J 中 Gold-free 的 `task_id -> Predicted position`；其余 position 按确定性顺序补齐 global order。held latch 在完整 ranking、A route、B state、candidate order digest freeze 前只允许 fail closed；unseal 后仅提供 `responsible_position` 和 `fault_call`。Exp114 不读取 J 的 held probe/TNR outcome，也不将其用于 RSR/TNR；正式 RSR/TNR 只来自 Exp114 same-fault fresh transaction cache。

每个候选使用 J 的 `git clone --no-checkout --no-hardlinks` 本地 source 并 checkout 精确 base commit；每个候选独立 fresh clone，不 reset、不 fetch/pull/remote/submodule。事务只有在 target compile probe、非目标工作树哈希等于 No-recovery reference、`git diff --check`、且没有新增 transaction conflict 时才通过 TNR 并 commit；冲突透明记录且永不算 recovery success。失败是原子 rollback/abstention。

条件注册顺序和预算写入 [protocol.json](protocol.json)，包括 No recovery、Retry、fixed-last、uniform、RQ1 Predicted、A、B、A+B、B deletion/shuffle、A+B route shuffle、random attribution 和不进 Gate 的 Oracle upper bound。pooled paired bootstrap 先对每个 task 的三 seed 差值取均值，再在 34 个 task clusters 上重采样；by-seed 仍以 task 为单位。正式 Gate 只在授权的唯一 invocation 后计算：B 需相对最强公平 baseline >8% 且 pooled CI lower >0（formal module criterion 为 >=10%）；A+B 还需预注册的 15%、三 seed 全正、严格优于 No/Random-attribution/RQ1 controls、Oracle 不低于 A+B、harmful 不恶化，以及 deletion/B-shuffle/route-shuffle 均严格低于完整模块。leakage、fold/provider、same-fault、TNR 与 shuffle 审计必须全部为真。任何结果都不自动等同 method/chapter GO。

## Preflight

执行（修正版 preflight 使用独立路径，不覆盖旧历史 JSON）：

```bash
python3 实验/实验114_RQ2状态感知事务式恢复/runner.py --preflight
python3 -m unittest discover -s 实验/实验114_RQ2状态感知事务式恢复/tests -p 'test_*.py'
```

preflight 只验证科学边界：outer-held latch、registered-arm OOF/state rules、RQ1 prior projection、rank/feature separation、same-fault reference、真实 local clone/TNR fixture、shuffle invariants、双文件 writer fail-closed 与 formal namespace absence。Exp113J 资格只作为一次 inherited accepted fact 读取；不会重复资产覆盖、SHA 或 clone 矩阵。`transactional_recovery_preflight_scientific_v4*.json` 是当前唯一非正式 preformal evidence；v3 与 v2 已明确标记为 superseded，早期 `transactional_recovery_preflight_runnable*.json` 仅作 historical nonformal record。预检 `formal_attempts=0`，不构成科学结论；正式结果已另存于独立 formal output/audit。

formal runner 的唯一一次执行完成了 8 repository outer folds × 3 seeds、outer-train repository-group OOF conformal、13 conditions、task-cluster 5000 paired bootstrap、RSR/harmful/TNR/cost/abstention 记录和独立双文件 writer。结果为 1326 records；strongest fair baseline 是 `retry_same_action`。B standalone RSR=0.17647、relative=20.00%，pooled CI lower=0；A+B RSR=0.16667、relative=13.33%，三 seed 均正但 pooled CI lower=-0.04902，故严格 Gate 未通过。所有 leakage/fold-provider/same-fault/TNR/shuffle 审计为真；Oracle RSR=0.35294；harmful rate 均为 0。上述是 controlled-only 结果，不构成 method/chapter GO。

## Formal archive

唯一命令：`python3 实验/实验114_RQ2状态感知事务式恢复/runner.py --run`；exit=0，elapsed=488.68762925s，formal attempts=1，retry=false，overwrite=false。正式文件为 `results/asset_alignment_gate_transactional_recovery.json` 与 `results/execution_attempt_audit_transactional_recovery.json`，两文件通过 atomic two-file publish；output SHA=`05e33442b04186d66ccf2e0ea20397fad2daf2bd1059674f0fce20c84665dbb2`，audit SHA=`ed719875c80588ad0363eeed0ab01bb5071861fabc4ad8e558d0ea3a8c7687c0`。`is_method_go=false`、`is_full_chapter_go=false` 保持为 false。

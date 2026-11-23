# Exp119C：RQ2 风险门的公平容量同构 helper 修正

当前阶段为 `FORMAL_COMPLETED_CURRENT_ENVELOPE_NON_GO`：本命名空间从已验收 Exp119 复制，仅修正零 held 信息暴露的公平容量 helper 合同。主线程审查提交 `4030479`、33 项测试与预检证据后授权并完成了唯一一次 formal；当前 `authorized=true`、`invoked=true`、`formal_attempts=1`，禁止重试或覆盖。

Exp119 在首个 held unseal、任何 outer-held metric 之前因 anonymous total-order digest/position collision `HARNESS_INVALID`；其 claim/terminal 原始字节 SHA256 分别为 `f19a782924e6d63ebb4c93f19b1b159f632615580a04eec41b3e82f3a8a172aa` 与 `297b72abfb8ac18032bf8cd6c6e099a6fb013213b643a734acb7b160fc807db9`，仍只保留在父 namespace。Exp119 没有正式结果、不是第二次科学试验，也不构成 GO 证据；Exp119C 是独立的一次 helper/capacity correction。

9db5dc7 中的多机制 feasibility/representation/preference/CAPS 设计已被本协议明确标记为 `SUPERSEDED_DESIGN_NOT_IMPLEMENTED`，不得实现，也不构成实验结果。Exp119C 不新增风险门、模型、阈值、action、control 或模块；只修正 Exp119 的公平容量 helper。RQ2 仍只计模块 A（Exp108 诊断策略 route）与模块 B（事务恢复）；Exp119C 不新增第三个模块。

## 边界与人工动机

Exp118C 的数字（B 约 `+3.8462%`、A+B 约 `+15.3846%`、Oracle `12/34` 等）只作为既有设计背景，不是 Exp119C 的输入。Exp119C 的 runner、模型和 selection helper 不得读取 Exp118C 或 Exp119 的任何 outer formal output/audit/claim/terminal/metric 文件，不得用它们拟合、调参或选策略，也不得覆盖旧文件。不得重复资产/hash 安全检查，不得调 Exp96/97/98。

文献检索已由主线程完成并冻结，核心依据只保留 2024 年 CCF B+ 以上的三篇风险门相关工作：

- [Angelopoulos et al., *Conformal Risk Control*, ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/f3549ef9b5ff520a7e41ff3cc306ab2b-Abstract-Conference.html)：吸收风险控制的 safe action set 与部署前保守校准。
- [Farinhas et al., *Non-Exchangeable Conformal Risk Control*, ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/de04896f011beff76c91e094f72727f4-Abstract-Conference.html)：吸收 non-exchangeable、等权 repository-block 的 group-aware conservative calibration。
- [Straitouri et al., *Controlling Counterfactual Harm in Decision Support Systems Based on Prediction Sets*, NeurIPS 2024, DOI 10.52202/079017-4113](https://doi.org/10.52202/079017-4113)：吸收 counterfactual-harm safe action set 与无安全动作时 abstain。

只吸收“风险门”这一机制，不组合新的表示、偏好模型、策略切换模型、外部资产或深度模型。由于训练侧只有 7 个 repository，结果只能表述为 group-aware conservative adaptation，不宣称 IID 或 distribution-free 保证。

## 复用的既有模块合同

B 的完整管线是：

`native posterior/full ranking + inherited absolute success/TNR/cost utility heads + uncertainty → repository-group CRC counterfactual-harm safe action set → inherited multiple-choice capacity objective/DP → same-checkpoint transactional TNR execution`。

Exp119C 只新增 CRC gate；native posterior/full ranking、absolute success/TNR/cost utility heads、uncertainty、capacity objective、DP、same-checkpoint transaction 和真实 TNR provenance 都在当前 outer-train 重新拟合/计算并在 held 前冻结，不读取 Exp118C outer formal 文件。没有新的 action envelope、没有新的 joint-capacity objective、没有新的 state quota。

B 保留父实验的 4-action envelope：`Escalate0` 与 protected native B ranking 的 budget1/2/3。A+B 保留父实验的 13-action envelope：`Escalate0`、`native_fallback`、`A_route`、`A_to_B_stable_dedup`、`B_to_A_stable_dedup` 各 budget1/2/3。A route 使用 Exp108 已注册参数，stable-dedup 与 parent semantics 完全一致；A 不被强制使用。

## Outer-train 标签与安全/成功分离

每个 outer-train task 先由现有 `ObservedFinalCheckpointExecutor.execute_candidate_cache` 执行同 fault、共享一个 reference 的完整 8-candidate cache，再从该真实 cache 按冻结 order、budget 和 first verified success stop 确定性重放 action label。Exp119C production 禁止使用父 `CandidateOutcomeLabelProvider` 的 responsible-only pair；任何缺字段、fault/reference 不一致、未执行行或不完整 provenance 都 fail closed，绝不通过 `setdefault` 合成安全 TNR/provenance。每个 fold 审计 train full-cache count、reference=1、candidate=8、same-fault、shared-reference 与真实 provenance；held cache 仍不能进入决策。

安全标签严格为：

`prefix_safe = no_harm AND complete TNR/provenance`

它绝不包含 `target_probe_pass`。prefix 内每个实际执行 candidate 都参与聚合：任何 `tnr_pass=false`、`conflict_count>0` 或 provenance 不完整都会使 prefix 不安全；`success = recovery_success AND target_probe_pass AND TNR pass` 只属于父 utility/success head。安全但未成功的 prefix（recovery 或 target probe 失败但无 harm 且 TNR/provenance 完整）必须保留为 safety-positive 样本；preflight 还必须同时包含真实安全、TNR 回归、conflict harm 和 safe-but-unsuccessful 样本。

只允许既有 native、visible semantic、TNR、conflict、cost、provenance 和父 utility features；禁止 task/repository/path/hash/Gold/fault metadata/held outcome。匿名 tie 只用 canonical position 与 native vector[8]。

## 唯一新增机制：CRC safety gate

CRC 在既有 action-value/DP 之前运行。分数来自当前 outer-train 的 repository-group cross-fitted harm/nonconformity scores；7 个 train repositories 使用等权、data-independent block weights。固定 policy/risk safe anchor 为同一容量合同下的 `uniform_equal_comparable_budget`。

先由 safe anchor 的 group harm estimate 与 conservative UCB 导出唯一风险 cap `q_anchor`。对每个 action 使用单一 conservatism 参数 `lambda >= 0`：

held unseal 前的资格规则严格为：`Escalate0`，或 `predicted_harm_score + lambda × uncertainty <= q_anchor`。held 决策绝不读取 `prefix_safe`、TNR/provenance、target probe 或任何 held outcome。真实 `prefix_safe = no_harm AND complete TNR/provenance` 只作为 outer-train 标签与执行后的验收/正式指标；它不能回写已冻结 action。

`Escalate0` 永远安全。`lambda` 只在预注册候选 `{0, 0.5, 1, 1.645, 1.96}` 中通过 inner repository-group OOF 选择：先丢弃违反 anchor group-harm cap/UCB 的候选，再在剩余嵌套 safe set 中最大化既有 utility；held unseal 前冻结。`lambda` 增大时 safe set 单调收缩，逐 task harmful-action inclusion loss 单调不增；任何候选都不能宽于 anchor-cap boundary。alpha 不是自由的成功导向阈值，不设独立 alpha grid；如果实现报告 alpha，它只能是由 `q_anchor` 导出的校准报告字段。没有安全的非 Escalate action 时合法 abstain 到 `Escalate0`。

## 容量、公平基线与 CI

容量 helper 统一冻结为：当前 fold 有 `n` 个 task 时总上界始终为 `2n`，奇偶相同；B/AB 的 DP 仍可在同一 `2n` 上界内把 0/1/2/3 action 联合分配，early stop 不改变上界。公平 baseline 为 retry-C-top1、fixed-last、uniform route、A standalone，均与 B/AB 使用同一 outer-fold 上界，且每个 task 固定 budget2、总计 `2n`，公平 baseline 不允许 budget1 或 budget3。

公平容量 map 完全删除跨 task `_anonymous_total_order`、digest/position tie、exact-one-budget1 与 insertion-order 依赖。多个 task 的允许 visible features 完全相同也必须成功，并对称地获得 budget2；task identity rekey 和输入顺序都不能改变 all-budget2 结果。候选内 native 排序/tie 规则、CRC、q_anchor/lambda、action-value、B=4、AB=13、19 conditions、full train cache/memoization、CRC controls 重跑 DP、eligible support、TNR/provenance、Oracle zero、writer/gates 均逐字继承 Exp119。

正式 `strongest_fair_baseline` 只在所有 outer-held baseline/method 执行并 unseal 后，从完整 fair pool 取 pooled 最大 RSR，并另取每 seed 最大 RSR。pooled task-group paired bootstrap CI 始终相对同一个 pooled strongest-fair condition；per-seed strongest 只用于 per-seed 描述与 A+B all-seed-positive gate，绝不拼接进 pooled CI。

## 一次性条件与控制

条件固定为 19 条：7 个 baseline/method（no recovery、retry、fixed、uniform、A、B、A+B）、9 个父 attribution/random controls（candidate posterior deletion/shuffle、state/action deletion/shuffle、A deletion、A route shuffle、coupling deletion/shuffle、protected random equal actual budget）、2 个新 CRC controls（`CRC_deletion`、`CRC_score_shuffle`）和 Oracle。每个 CRC 顶层条件同时生成明确分开的 B/AB paired variant；B gate 只比较 candidate-posterior/state-action/protected-random 与 B CRC variants，AB gate 才比较 B、A/coupling controls 与 AB CRC variants；不跨语境比较。不得为已删除的 feasibility/representation/preference/CAPS 机制保留 controls。

`CRC_deletion` 删除 repository-group calibration，使用预注册 uncalibrated fixed harm-score threshold `0.5`；`CRC_score_shuffle` 乱序 cross-fitted harm/nonconformity scores，保持 score multiset 后重算每个 task×action safe set，并重新运行父 utility selection 与 B 全局 capacity DP，AB 再复用该 control 的 B budget map 选择兼容 AB action。所有 deletion/shuffle 都必须重算 order/action、保持对应 multiset/capacity，并与方法在相同 eligible task-group support 上配对比较；每个比较同时报告 method/control eligible RSR、差值、paired CI、support count/digest 与 full-support RSR。结构退化标记 `structurally_ineligible`，不是 harness pass；N/A 不编码为 0。

Oracle 只在 held unseal 后作为上界使用：存在成功 candidate 则记录 successful position/budget1；没有则记录 zero ceiling、Escalate、success=false，不抛 harness error。Oracle 不参与 selection 或 CRC。

## 严格 GO gate

B candidate 仍为相对 pooled strongest fair baseline `>8%` 且 pooled task-group CI lower >0。B formal module 要求相对同一 pooled baseline `>=10%`、同一 pooled CI lower >0、严格高于所有 eligible parent/CRC controls、harmful rate/count 不高于 formal strongest fair baseline，并通过 CRC、capacity、TNR/provenance 审计。

A+B 要求相对同一 pooled baseline `>=15%`、同一 pooled CI lower >0、三 seed 仅按各自 per-seed strongest baseline 全正，严格高于 B 与 eligible parent AB controls，harm 不高于 formal strongest fair baseline 且不高于 B，Oracle ≥ A+B，全部核心审计通过。任一门槛不满足只保留真实 positive-not-GO，不写 no-go。

## Formal authorization namespace

授权已消费；唯一一次 canonical command 已完成。正式 output SHA256 为 `7e9e31bbde071eaad0554c1ae541dc057176c94fe7a2253799e38e34a847e96e`，audit SHA256 为 `db4de363ede726a57ebbb49ed7d3a14fc0fffe94cb73ff607bc85375815e5922`，terminal 中两者均一致。以下独立正式结果/report/claim/terminal 路径现已归档：`results/exp119c_formal_output.json`、`results/exp119c_formal_audit.json`、`results/exp119c_formal_report.json`、`results/exp119c_attempt_claim.json`、`results/exp119c_attempt_terminal.json`。禁止再次执行或覆盖。原 canonical formal command 为：

```bash
python3 实验/实验119C_RQ2风险门公平容量同构修正/runner.py --run
```

实现验收命令为：

```bash
python3 -m unittest discover -s 实验/实验119C_RQ2风险门公平容量同构修正 -p 'test_runner.py'
python3 实验/实验119C_RQ2风险门公平容量同构修正/runner.py --preflight
```

上述只使用 synthetic/parent train-visible fixture，覆盖 34 tasks、8 repositories、3 seeds、19 conditions，并审计完整 train cache、真实安全/危害标签、CRC safe-set 单调性、equal-block UCB、held 资格隔离、B/AB control DP rerun、4/13 action envelope、all-n/2n fairness、完全相同 visible task payload collision、identity rekey/input-order invariance、exact eligible/full support、Oracle zero ceiling 与 paired writer/no-overwrite。结构退化 control fold 明确记录为 `structurally_ineligible`，不会伪装成 0/pass；正式 gate 只在存在 eligible changed support 的比较上严格判断。Exp119 的 HARNESS_INVALID 只作为不可变父 namespace 归档，不读取其 outer formal 指标，不构成正式结果、第二次科学试验或 GO 证据。

## Formal result and ceiling boundary

Exp119C 有效完成但未达到 GO。最强公平基线 `retry_top1` 为 `11/34 = 0.323529`；B 为 `9/34 = 0.264706`，相对提升 `-18.1818%`、paired bootstrap CI lower `-0.147059`；A+B 为 `11/34 = 0.323529`，相对提升 `0%`、CI lower `0`，三 seed 均未正提升。Oracle 为 `12/34 = 0.352941`，相对最强公平基线也只有 `+9.0909%`，低于 A+B 注册门槛 `+15%`。因此在同一 8-candidate/action envelope 与公平基线下，继续改 B 的风险门、排序或 DP 在数学上不能形成严格章节 GO。

`control_support=false`、`crc_control_support=false`、`crc_controls_nonidentity=false` 进一步阻止归因性 GO：state/action control 全部结构性不可比较，CRC score-shuffle 只有 1 fold / 5 task groups 的 eligible support，且在该 support 上与方法相同。这些是有效正式结果中的可比性边界，不是 harness invalid。结论只约束当前 envelope，不写成整个 RQ2 的全局 no-go；若继续，唯一合理方向是最多增加一个能真实提高 Oracle recoverability 的第三模块，且不得再给 B 叠加机制。

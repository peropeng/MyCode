# 实验 80：AFTraj no_length_C 严格未见确认

## 冻结前半（已提交，尚未解封）

本目录只允许执行 Exp79 预注册保留下来的最小候选 `no_length_C`。本实验不是继续搜索特征，也不是全量扩展：只做一次 official confirmation，以判断开发阶段观察到的提升能否在严格未见 task group 上保留。

第一阶段已经冻结并提交 `protocol.json`、`data_seal.json` 和本 README 的冻结前半。此阶段只读取 official split 的计数/哈希和已有 task-group/canary 封存文件，不读取 official parquet body、turns、Gold 或 label。第一阶段提交之后才允许实现并执行解封 runner。

冻结的 18 个特征为：

`base_score, a_score, score_margin, base_alarm, a_alarm, activity, action_nonempty, content_nonempty, thought_nonempty, action_parseable, call_count, named_call, balanced_action, action_tool_match, role_switch, structure_repeat, structural_delta, recovery_evidence`

最终 Base/A 使用 Exp75 `fit_fold(all_dev)`；gate 使用 all-development utility label 定义、Exp79 的 linear ridge、正则化网格、阈值网格和选择顺序。所有最终参数、特征和数据/参数哈希必须在加载 official body/label 前写入 pre-unseal artifact。

## 解封后固定执行

primary 是严格未见集：从 official 332 行中，整组排除所有包含 Exp73 canary ID 的 task group；不能只删除 canary 行。完整 332 行只做 secondary comparability。开发集与确认集必须验证 ID 和 task group 均零重叠。

冻结比较为 `Base`、`A`、`Base+C(no_length_C)`；C 删除必须逐行精确等于 Base。主指标是 task-group paired bootstrap 2000 次（seed 20260822）的 Exact-F1，同时报告绝对差、相对差、95% CI、better/worse/tie、FAR、ASS、StepAcc。保存逐行去标识预测、route、group hash、Gold/pred 供审计，并确保 Gold 只在全部预测冻结后进入 evaluator。三组的候选/API/token/information budget 相同；C 的本地线性门计算开销单独记录训练/推理 wall time 和 peak RSS，不能宣称计算/延迟零开销。

执行规则：一旦产生完整确认预测，不得重跑、调参或择优。若在产生任何确认预测前发生代码/Harness 错误，可修复后重跑，并计为执行失败。

## 裁决

- `RQ1_CONFIRMATION_GO`：strict 集相对 Base 提升至少 10%，paired CI 下界大于 0，changed groups better>worse，full 332 方向同为正，且 seal、泄漏、删除、零成本审计全通过。
- `POSITIVE_NOT_YET_GO`：strict 集有提升但未满足全部 GO 门；保留为真实正向信号，不写 STOP/NO-GO。
- `CONFIRMATION_NOT_ESTABLISHED`：strict 集不高于 Base，只否定这一个冻结实现；必须报告分组和条件信号，不能直接否定方向。
- `HARNESS_INVALID`：任何封存、泄漏、Gold 提前读取或评价对象错误；结果不作科研解释。

本 README 的最终结果和数字只能在第二阶段提交中追加，不能反向修改冻结规则。

## 唯一确认结果（已完成）

本次运行在两次冻结提交之后执行，确认执行次数为 `1`，结果裁决为 **`POSITIVE_NOT_YET_GO`**：严格未见集确实有提升，但 task-group paired bootstrap 的 95% CI 下界略低于 0，因此不能写成稳定 GO；这不是 NO-GO，也不否定该条件性正信号。该次 execution 内，`_evaluate` 对 strict 311 行调用 1 次、对 full 332 行调用 1 次；所以 strict 311 行在 full 计算中被确定性重复计算，不能表述为“one prediction pass”。

| 数据集 | Base Exact-F1 | C Exact-F1 | 绝对提升 | 相对提升 | 95% CI | exact-correct group better / worse / tie（非组件安全性） |
|---|---:|---:|---:|---:|---|---:|
| strict unseen（311 行、205 组） | 10.5634 | 12.5436 | +1.9802pp | +18.7456% | [-0.0649, 4.7066] | 3 / 0 / 202 |
| full official（332 行、217 组） | 12.5828 | 14.4262 | +1.8434pp | +14.6506% | [-0.0657, 4.3138] | 3 / 0 / 214 |

strict 集的 FAR 为 `34.1772% → 34.1772%`，ASS 为 `2.1558 → 2.1250`，StepAcc 为 `9.8039% → 11.7647%`。C 删除逐行精确回到 Base；开发/official 的 ID 和 task group 均无重叠；12 个 canary 所在 task group 被整组排除；确认特征无 Gold、位置、长度、source、domain 或 task ID；API/network/token 均为 0。这里的 0 只表示 zero external cost，不表示零本地计算。C 的本地开销单独记录在结果 JSON：训练约 `2692.17ms`、确认推理约 `460.08ms`，峰值 RSS 分别为 `122096KB` 和 `158688KB`。

机器可审计明细见 `results/exp80_result.json`，预测前最终参数封存见 `results/pre_unseal.json`。后续若继续，只能把这次结果作为“真实但暂未跨过 CI 门”的正向证据，不能回到本次 official 集调参或重跑择优。

## Post-run audit 勘误（只读证据推导）

原始结果文件保持不变，SHA256 为 `1893939cad107b78adb1f7b6bff2ab1f55290e9f6aee9eae36f0d84fc4309b87`。独立离线审计见 `results/post_run_audit.json`；审计只读取原始 JSON 的去标识 evidence，不读取官方数据，也不重跑 runner。

- strict/full evidence 的 `row_hash` 均无重复；strict 311 行全部出现在 full evidence 中，full 额外 21 行。对应 strict 子集的 `Base/A/C/route` 逐项一致，mismatch 为 0；strict projection 与 full 中 strict projection 的 SHA256 均为 `6559f3535abe9927fab2197ae12bebc85cdd623eb366211451cce6891b126dee`。
- 从 immutable evidence 补齐的 A 基线：strict A Exact-F1=`6.0345`，相对 Base `-4.5289pp`（`-42.8736%`），95% CI=`[-9.8282, 0.7898]`，better/worse/tie=`6/101/98`；full A Exact-F1=`6.4646`，相对 Base `-6.1181pp`（`-48.6231%`），95% CI=`[-11.2796, -0.9789]`，better/worse/tie=`6/109/102`。
- 原始 `audits.zero_cost=true` 是字段命名错误；post-run audit 将其解释为 `zero_external_cost=true`。本地训练、加载和推理 wall time/RSS 均非零。
- 依据原有 C 门重新计算，唯一未满足的 GO 条件仍是 strict CI 下界大于 0；其余相对提升、better>worse 和 full 同向均满足。因此原裁决 `POSITIVE_NOT_YET_GO` 保持有效。

## F1 组件风险审计（只读 evidence）

`3 / 0 / 202` 必须严格解释为“每组 exact-correct 行数的 better / worse / tie”，不能解释为“没有伤害”。逐组按 `TP↑、FP↓、FN↓` 做 Pareto 分解后，strict 实际为：`3 beneficial / 2 harmful / 200 neutral / 0 mixed`。两组 harmful 被 exact tie 隐藏：group `178c329435111886`（row `5e4b90c3f55d4de0`, `e3a45194562b76ca`）和 group `717e3b57902e01f3`（row `d95dc74afcbafc82`, `5243e34e72ee880c`）；每组均新增 1 个 FP，但 TP/FN 不变。三组 beneficial 为 `d4bc48093e82fea1`（row `b28566d95682e148`）、`e9f8a132407ca64d`（row `d0b196993cef8c7b`）和 `f6211bf4f1783c98`（rows `fe4943458a736fc1`, `b45fbdc827cd5101`）。

strict 总组件从 Base `TP=15, FP=116, FN=138` 变为 C `TP=18, FP=116, FN=135`：新增 TP=3、减少 FN=3，净 FP=0，但实际是 harmful 组新增 FP=2、beneficial 组移除 FP=2，净值抵消。固定 2000 次 task-group bootstrap 中有 `82/2000` 个 draw 的 C Exact-F1 为负；例如 draw 43 过采样上述 harmful 组（`178...` 一次、`717...` 两次），Base 组件为 `(14,106,131)`、C 为 `(14,109,131)`，TP/FN 不变而 FP 增加 3，Exact-F1 差为 `-0.1317564`。完整去标识组件、行 hash 和 bootstrap 证据见 `results/f1_component_risk_audit.json`。

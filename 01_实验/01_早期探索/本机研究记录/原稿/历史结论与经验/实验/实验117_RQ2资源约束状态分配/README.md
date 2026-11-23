# Exp117：资源约束状态分配（pre-formal）

当前状态：`HARNESS_INVALID_NO_METRICS`。Exp117 canonical formal invocation 已发生且仅发生一次（`invoked=true`、`formal_attempts=1`、`retry=false`、`overwrite=false`），在 qualification 首折冻结阶段失败；没有 formal output 或 metrics，也没有任何 RQ2/GO 证据。本目录只冻结一个互补的 RQ2 模块 B：E02-native candidate posterior/full ranking、outer-train marginal-value prediction、fold-level capacity-constrained state allocation、same-checkpoint transaction/TNR 四项共同计为一个模块。A 仍是 Exp108-family route；A+B 复用同一 B allocation，不另训第二套状态分配。

Exp116E 只作为已接受的 positive-not-GO parent fact；本目录只记录其四个 artifact SHA，不读取 Exp116E records、不读取 Exp114 formal metrics、不做资产 coverage/SHA/security/clone 复核，也不修改任何旧实验。v1 preflight 是 standard-library synthetic contract；v2 runner 的生产路径动态加载只读 Exp116E runner，并绑定其 visible projection、outer-train label provider、repository-group nested OOF、fixed ExtraTrees candidate model、strategy router、condition record 和 task-cluster aggregate。v2 integration preflight 使用 8-task/4-repository synthetic visible-schema fixture，真实走通 parent model/OOF/router/condition/aggregate 以及训练/held/freeze/unseal、1+1 training pair、1+8 held cache、quota/state/control/digest/writer 链路；底层 verifier 明确为 synthetic，因此 scientific core 不关闭。两种 preflight 都不做 clone、source mutation、实际 replay、Gold、Exp114 formal metric 或 formal execution。

本轮修订的当前非正式证据是 v3：`results/exp117_preflight_v3.json` 及其 attempt audit。v3 不覆盖 v1/v2，而是从当前 runner 重新走一遍相同的 parent-model/OOF/router/allocator/condition/writer 控制流，并额外封存 production guardrails：`require_final_checkpoint=true`、parent 动态 `core_required`、exact parent source/executor、canonical writer/ledger/claim、immutable terminal SHA commit。fixture 仍明确是 synthetic verifier，故 v3 的 `scientific_audits.core_required=false`、不是 formal 结果或 GO 证据；v1/v2 标为 historical/superseded。

## v2 integration evidence

当前 evidence 为 `results/exp117_preflight_v2.json` 及其 attempt audit：3 seeds、12 reduced outer folds、24 held caches、360 records（15 conditions × 8 tasks × 3 seeds），公共条件名使用 `exp117_b` / `exp117_a_plus_b`。v2 审计显示 train/held disjoint、nested OOF exactly-once/group-free、digest-before-unseal、capacity exact、state/candidate/route controls、shared fault anchor 和 TNR fields 均通过；`tnr_real_verifier_provenance=false` 是因为 fixture 明确为 synthetic，故 `core_required=false`、verdict 仅 STOP/preflight evidence，不是科学结果或 GO。

生产入口要求 canonical authorization、canonical output/audit/claim/terminal、parent `FoldEvaluatorSource` 与 `ObservedFinalCheckpointExecutor` exact types，并在所有 task/source read 前再次检查授权、磁盘 RUNNING claim token、exact writer/ledger；production cache 先通过 parent E cache schema/final-checkpoint metadata，parent scientific summary 的动态 `core_required` 再与 Exp117 capacity audits 合取。此次真实 parent projected candidate 不含 synthetic-only `posterior_mean`，在 qualification 阶段触发 `KeyError: 'posterior_mean'`。失败已以独立 audit/immutable claim/terminal 归档；formal output 不存在，metrics 不生成。

## Formal failure archive

本次唯一 invocation 的权威状态为 `HARNESS_INVALID_NO_METRICS`，failure stage=`qualification`，failure class=`KeyError`，error=`'posterior_mean'`。原因是 real parent projected candidate schema 不含 fixture-only `posterior_mean`；本轮不修复、不重跑，也不把失败写成科学结果。原始归档文件保持字节不变：

- `results/execution_attempt_audit_exp117.json` — SHA256 `5d6bb155dd54e8eeed362cc615fac19ccd8019fa76b23b0d9aef72b158afd5e0`
- `results/exp117_attempt_claim.json` — SHA256 `297d07b58a169d7fb428d865dce1accd9638650817b85605fa6be4285cdc47d0`
- `results/exp117_attempt_terminal.json` — SHA256 `bf9ebd7aaad239f308642bb299fc45af64af1db88e0aa2418bab0e3290182916`

`results/exp117_formal_authorization.json` 保留为 invocation 前的授权凭据（`authorized=true`、`invoked=false`、`formal_attempts=0`）；最终失败状态以 claim/terminal 和 failure audit 为准。Exp117 没有 RQ2 metrics、method GO、chapter GO 或其他 GO 证据。

## 冻结协议

每个 held repository fold 有 `n >= 2` 个任务。只分配 `Active(budget=1)` 与 `Standby(budget=3)`；`Escalate` 仅保留为既有无自动恢复对照，不进入 allocator。Standby 名额固定为 `floor(n/2)`，其余为 Active，总容量为偶数折 `2*n`、奇数折 `2*n-1`，奇数折保留一个闲置单位，不补偿、不按结果重分配。

allocator 的训练目标是 `utility(Standby)-utility(Active)`，utility 沿用 Exp116E 的固定公式 `success - 0.01*observed_conflicts - 0.0001*(attempts*2)`。训练标签只来自 outer-train responsible-only pair；held task 在 marginal-value fit 中 fail closed。固定 ExtraTrees 参数和 nested repository OOF 合同不调参。held 只使用 visible structural summary 预测 marginal value，降序分数选择 Standby；并列只用 anonymous visible-feature digest 加 seed，禁止 task/repository/id/Gold。

state deletion 保留完全相同的 quota、预算和总容量，只以匿名 digest 分配；state shuffle 对实际 `(state,budget)` 做确定性非恒等置换，逐折保持 joint multiset、名额和容量。candidate deletion/shuffle、random equal-budget、A route shuffle 和 Oracle upper bound 均保持等预算；Oracle 不进入 strongest fair baseline 或贡献比较。

同 checkpoint/TNR 仅在正式执行中接入已冻结的底层 executor：训练形状为一个 reference 加一个 responsible candidate，held cache 为一个 shared reference 加八个 candidate outcomes。当前 preflight 只用 synthetic shape fixture 验证 `1+1`/`1+8`、TNR 字段和 shared token，不执行实际 replay。

## 审计与 Gate

每折审计 exact Standby/Active count、容量公式、两类 state、state-deletion score independence、state-shuffle nonidentity/joint multiset、candidate controls、train/held disjoint、freeze-before-unseal、same-fault reference 和 TNR。B-only gate 使用 core+B attribution audits，不被 A-only route audit 拖死；A+B 另外要求 route attribution。B candidate 门为 relative `>8%`；正式模块还需 `>=10%`、task-cluster CI lower `>0`、严格胜 candidate/state deletion/shuffle、Oracle `>=B`。A+B 需 relative `>=15%`、三 seed 全正、CI lower `>0`、严格控制项通过。method/chapter flags 固定为 false。

真实 formal 的唯一 canonical invocation 已失败并封存，禁止再次执行。authorization receipt 保留其 invocation 前状态（`authorized=true`、`invoked=false`、`formal_attempts=0`）；最终 archive 状态为 `HARNESS_INVALID_NO_METRICS`、`formal_attempts=1`。formal output 不存在，failure audit/claim/terminal 已归档；generic API 和非 canonical path/type/token 均不得绕过一次性合同。以下三个入口仅为历史非正式预检，不得作为结果：

```bash
python3 实验/实验117_RQ2资源约束状态分配/runner.py --preflight-capacity-state
python3 实验/实验117_RQ2资源约束状态分配/runner.py --preflight-v2
python3 实验/实验117_RQ2资源约束状态分配/runner.py --preflight-v3
```

v1 输出为 `results/exp117_preflight_v1.json`，v2 输出为 `results/exp117_preflight_v2.json`，v3 输出为 `results/exp117_preflight_v3.json`。v1/v2 及对应 attempt audit 保留为 historical/superseded，v3 是当前 nonformal evidence，全部 `formal_attempts=0`；它们不能覆盖本次 formal failure archive。正式入口 `--run` 已消耗且不得重试。

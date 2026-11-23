# Exp112C：RQ1 时序依赖排序纠正式复跑

状态：正式唯一 run 已完成；本目录只承载 Exp112 的 Harness digest 纠正、wrapper、正式输出和 provenance。

## 纠正边界与 provenance

Exp112C 不是新模块、不是调参、不是选择性重跑，也不是 confirmation run。Exp112 原 runner 的 helper digest payload 与 Exp88 的 byte-for-byte tie key 不一致；本次只绑定已修复的 Exp112 runner（commit `4fe2d903496375750013172b59bea5076af8b8f7`）中：

```python
return str(E88._tie_digest(rec, int(index)))
```

wrapper 只读 import Exp112 fixed runner，复用其 `run_seed`、`aggregate`、`audit_bound_assets` 和 frozen helpers；data、seed、fold、graph、optimizer、stack、score、control、bootstrap、fair-baseline 和 Gate 均保持原 Exp112/a13e5aa protocol。新 wrapper 只拥有本目录的 output guard、preflight、metadata 和输出路径。

原 Exp112 immutable formal artifact 永久保留：

- SHA-256：`f7a0420de94ebf3e0e4e100fa203f7c7507dfb8680eeaada7ba88906f54d4197`
- verdict：`HARNESS_INVALID`
- 原文件未被重写，本 runner 未读取其 outer-held metrics；主线程在纠正决策前已见原 provisional 汇总，旧结果仅作为 correction trigger/provenance。

已停止且不构成第二次实验或 GO 证据的 superseded 支线：`0823-exp112-scope-residual`、`0823-exp112a-dependency-ranking`、`0823-exp112a-features`、`0823-exp112a-model`。本次未读取、导入或合并它们，也未使用 Exp111 outer-held、Exp97/98/109/110、confirmation 或新论文。

## 冻结设计与执行

- 数据：Exp96 frozen development partition；loaded 1074、official test 163、overlap removed 40、pool 911、train 731 records / 716 task groups；confirmation boundary 180，未用于 scoring、fit 或 selection。
- 3 seeds：20260816、20260817、20260818；每个 seed 5 outer folds、每个 outer 4 inner folds；strict inner-OOF stacking。
- B2：Exp88 anonymous 结构表示 + 四通道 dependency graph、固定两轮 message passing、215 维 graph feature；pairwise logistic 200 epochs、lr 0.05、l2 0.001、pos_weight 1.0；score alpha 0.5。
- A+B stack：固定 7 个 stack features，stacker 只使用 inner-held OOF A/B2 分数和训练 Gold pair labels。
- 统计：task-group equal step MRR 为主指标；5000 次 paired bootstrap percentile 95% CI；同时报告 R@1/R@3、row-equal 指标、完整覆盖和 controls。
- 正式调用：一次启动、一次写入、不可覆盖、不可重试；API/token/retry/cost 全为 0。

正式输出：[formal_corrected_nested_oof_results.json](results/formal_corrected_nested_oof_results.json)

- SHA-256：`d99f9468adeadec4e69e30e0a2c44aafc277c4a034be0f1b7f678c4da5deb851`
- wall time：`2690.141188375 s`（约 44.84 min）
- execution audit：一次 attempt、一次 completed formal output write、retry false。

## Raw 指标

下表是每个 seed 的 row-equal raw MRR / R@1 / R@3（`n=731`）；Gate 使用 task-group MRR（`n=716`）。`A+B` 即完整 strict stack。

| seed | condition | MRR | R@1 | R@3 |
|---:|---|---:|---:|---:|
| 20260816 | local | 0.312256 | 0.093023 | 0.365253 |
|  | original_A | 0.333989 | 0.056088 | 0.444596 |
|  | pairwise_B | 0.341616 | 0.068399 | 0.452804 |
|  | recency | 0.325645 | 0.088919 | 0.399453 |
|  | A | 0.374366 | 0.155951 | 0.458276 |
|  | B2 | 0.454007 | 0.261286 | 0.458276 |
|  | A+B | 0.485421 | 0.258550 | 0.616963 |
| 20260817 | local | 0.312256 | 0.093023 | 0.365253 |
|  | original_A | 0.334847 | 0.057456 | 0.448700 |
|  | pairwise_B | 0.341809 | 0.068399 | 0.454172 |
|  | recency | 0.325645 | 0.088919 | 0.399453 |
|  | A | 0.373418 | 0.154583 | 0.458276 |
|  | B2 | 0.452259 | 0.257182 | 0.465116 |
|  | A+B | 0.490553 | 0.251710 | 0.636115 |
| 20260818 | local | 0.312256 | 0.093023 | 0.365253 |
|  | original_A | 0.331815 | 0.053352 | 0.444596 |
|  | pairwise_B | 0.339774 | 0.065663 | 0.450068 |
|  | recency | 0.325645 | 0.088919 | 0.399453 |
|  | A | 0.373558 | 0.154583 | 0.458276 |
|  | B2 | 0.451858 | 0.258550 | 0.462380 |
|  | A+B | 0.489772 | 0.259918 | 0.662107 |

## 绝对/相对提升、CI 与 better/worse/tie

公平 baseline 按三 seed 平均后只选择一次，最强 baseline 为 `pairwise_B`，task-group MRR `0.343699579`。下表中的 delta、CI、better/worse/tie 都是相对该同一 baseline 的 task-group 配对比较。

| seed | target | target MRR | absolute Δ | relative Δ | 95% CI [low, high] | better / worse / tie |
|---:|---|---:|---:|---:|---:|---:|
| 20260816 | A | 0.377519343 | 0.033259481 | 9.6612% | [0.019936303, 0.047406207] | 70 / 88 / 558 |
|  | B2 | 0.460097808 | 0.115837946 | 33.6484% | [0.095376149, 0.136203710] | 468 / 143 / 105 |
|  | A+B | 0.493107843 | 0.148847981 | 43.2371% | [0.128175262, 0.169093093] | 464 / 139 / 113 |
| 20260817 | A | 0.377253307 | 0.032796182 | 9.5211% | [0.019475718, 0.046142954] | 69 / 91 / 556 |
|  | B2 | 0.457321267 | 0.112864143 | 32.7658% | [0.093468312, 0.132752570] | 478 / 129 / 109 |
|  | A+B | 0.497867682 | 0.153410558 | 44.5369% | [0.132905434, 0.173690991] | 480 / 129 / 107 |
| 20260818 | A | 0.377397605 | 0.035015855 | 10.2271% | [0.021784756, 0.048923910] | 71 / 89 / 556 |
|  | B2 | 0.457390881 | 0.115009132 | 33.5909% | [0.094546524, 0.134774701] | 483 / 134 / 99 |
|  | A+B | 0.497195450 | 0.154813700 | 45.2167% | [0.134542639, 0.175732078] | 488 / 126 / 102 |

跨 seed pooled task-group paired bootstrap（5000 resamples）：

| target | mean absolute Δ | relative Δ（seed mean） | pooled 95% CI | all seed Δ>0 |
|---|---:|---:|---:|---|
| A | 0.033690506 | 9.8031% | [0.0207722516, 0.0482728125] | yes |
| B2 | 0.114570407 | 33.3350% | [0.0949308927, 0.1342628881] | yes |
| A+B | 0.152357413 | 44.3302% | [0.1323698250, 0.1716386597] | yes |

额外的 `A+B` paired CIs 也为正：vs A `[0.0969177816, 0.1403294751]`，vs B2 `[0.0310983068, 0.0445874725]`。它们按预注册只报告，不作为额外主 Gate。

## Controls、图审计与 nested 审计

Control raw task-group MRR 如下；每个 seed 的 `B2_deletion` 与 `pairwise_B` 完全一致，`B2_shuffle` 和 `random_dependency` 的三 seed 平均均低于 B2，A+B 三个删除/换序 control 均低于完整 A+B。

| seed | B2 deletion | B2 shuffle | random dependency | A+B delete A | A+B delete B2 | A+B shuffle B2 | Oracle |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 20260816 | 0.344260 | 0.342256 | 0.362567 | 0.460098 | 0.377802 | 0.316815 | 1.000000 |
| 20260817 | 0.344457 | 0.339677 | 0.361602 | 0.457321 | 0.377536 | 0.308119 | 1.000000 |
| 20260818 | 0.342382 | 0.346292 | 0.360321 | 0.457391 | 0.377681 | 0.327986 | 1.000000 |

三 seed 的以下审计均为 true：

- `B2_deletion_exact_true_pairwise_B_digest_rank`、`B2_shuffle_graph_utility_multiset_preserved`、`B2_shuffle_changed_when_possible`；
- `random_dependency_node_count_preserved`、`random_dependency_edge_counts_preserved`；
- `global_full_ranking_coverage_100_percent`、`same_record_count_all_conditions`、`a_exp106_exact_cache_agreement`；
- Gold 只用于训练 pair labels 与最终 evaluator；Oracle 只作 evaluator；未使用 Exp111 outer-held 或 Exp97/98/109/110；confirmation 未 scoring；API/token/retry/cost 为 0。

图审计（每个 seed 聚合；边数在三 seed 相同）如下：

| seed | temporal edges | same-role | same-full-shape | same-action | mean coverage (temporal / role / full / action) | isolated rate | utility variance | constant rate | rounds |
|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|
| 20260816 | 13270 | 9388 | 10350 | 2270 | 1.000000 / 0.759136 / 0.866918 / 0.157758 | 0 | 1.452309 | 0 | 2 |
| 20260817 | 13270 | 9388 | 10350 | 2270 | 1.000000 / 0.759136 / 0.866918 / 0.157758 | 0 | 1.436632 | 0 | 2 |
| 20260818 | 13270 | 9388 | 10350 | 2270 | 1.000000 / 0.759136 / 0.866918 / 0.157758 | 0 | 1.453788 | 0 | 2 |

Nested OOF 审计每个 seed 全部为 true：outer-held prediction coverage exactly once；outer-held excluded from all inner fit/held；inner OOF A/B2 coverage exactly once；outer fit groups exact；stack fit uses inner OOF only；outer-held not in stack fit。每个 seed fit counts 为 inner pairwise/B2 `20/20`、outer pairwise/original-A/B2 `5/5/5`、stacker `5`，total pairwise model fits `50`。

## Gate 与结论

- B2 相对最强公平 baseline 的三 seed relative delta 均 >8%，均 >10%，三 seed absolute delta 均为正，pooled CI lower bound `0.094930893 > 0`：B2 同时通过 module candidate 和 formal module feasible。
- A+B 三 seed relative delta 均远超 15%（`43.2371% / 44.5369% / 45.2167%`），三 seed absolute delta 均为正，pooled CI lower bound `0.132369825 > 0`；controls、graph、nested、A-cache、coverage 和 split/Gold audits 全部通过。
- 因此 wrapper 将原 Exp112 `RQ1_CHAPTER_METRIC_GO_CANDIDATE` 映射为 `RQ1_CHAPTER_METRIC_GO_CANDIDATE_CORRECTED_REPLAY`。该映射由完整审计和冻结 A+B Gate 触发，不由单一点估计触发。

正式结果的下一步由主线程按交接继续处理 RQ2/Exp113/Exp114；本目录不扩展模块、不修改 Exp112 固定科学实现或 Gate。

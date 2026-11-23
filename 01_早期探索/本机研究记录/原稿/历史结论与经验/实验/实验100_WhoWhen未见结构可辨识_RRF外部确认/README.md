# Exp100 Who&When Pro 未见结构可辨识：RRF 外部资格 probe

本目录保存一次预注册的外部资产/可观测性资格 probe。该运行不是方法评分，也不是论文 GO。

运行条件：

- 固定 revision：`0bd196c8a040841c4ae167ab33cc8151de246f1f`。
- 固定目标页顺序：`4613 → 4813 → 5613 → 5813`。
- 先排除 Exp81/83/90 已见 ID：`1678` 个唯一 ID，union SHA-256 为 `3fa378ac3c5402c566ab394825d8b731e8da62aee19e6d3e41329ed86be9c4fe`。
- AFTraj 只使用冻结的 `731` 条 train 记录拟合 pairwise_B；外部 Gold 不进入拟合、阈值或方法选择。

本次实际下载了 2 页后提前停止：

| 页 offset | 累计 eligible rows | 累计 task groups | 非同结构向量 rows/groups | 非均匀概率 rows | 累计原始 bytes |
|---:|---:|---:|---:|---:|---:|
| 4613 | 100 | 73 | 0 / 0 | 0 | 709,735 |
| 4813 | 200 | 155 | 78 / 70 | 78 | 1,826,374 |

最终资格结论为 `QUALIFICATION_GO`：Gold 对象门（≥100 rows、≥100 groups）、结构向量门（≥50 rows、≥50 groups）和概率非均匀门（≥50 rows）均通过。未下载 5613、5813。

本次 `method_metrics_computed=false`、`gold_step_scoring=false`，没有计算 MRR 或任何外部方法效果。原始页面保存在被 `.gitignore` 忽略的 `runtime/raw_pages/`，不提交；可审计摘要见 [`results/qualification.json`](results/qualification.json)，页级 manifest 见 [`results/qualification_manifest.json`](results/qualification_manifest.json)。

## 正式外部评分（唯一一次）

资格通过后，按冻结的 200 条 eligible rows、155 个 task groups 和冻结的 AFTraj 731 条训练记录执行了一次正式评分。运行没有联网、没有扩大页范围、没有调用 API，也没有覆盖既有输出；完整原始结果见 [`results/formal_external_results.json`](results/formal_external_results.json)。三个 seed 只用于预注册的 shuffle/bootstrap 审计；确定性方法在三个 seed 上相同。

### 指标和候选定义

主指标是 task-group equal step MRR：先在每个 task group 内计算正确 step 的倒数排名，再对 155 个 group 等权平均，不让行数较多的 group 主导结果。表中的 R@1/R@3 也按 task group 等权计算。row-equal 指标把 200 条行等权，只作为敏感性分析。

| 条件 | 含义 | task-group MRR | task-group R@1 | task-group R@3 | 目标 − 该行条件的绝对差 | 相对差 |
|---|---|---:|---:|---:|---:|---:|
| `recency` | 按最新 step 优先的 recency 基线 | 0.857874 | 0.815054 | 0.884946 | -0.095324 | -11.112% |
| `fixed_first` | 固定最早 step 优先 | 0.330824 | 0.074194 | 0.388172 | +0.431726 | +130.500% |
| `fixed_midpoint` | 固定最接近轨迹中点的 step 优先 | 0.312418 | 0.012903 | 0.311828 | +0.450132 | +144.080% |
| `fixed_last` | 固定最新 step 优先；本数据中与 recency 完全相同 | 0.857874 | 0.815054 | 0.884946 | -0.095324 | -11.112% |
| `pairwise_local_bridge` | Exp88 冻结的局部结构分数，加冻结的 pairwise_B 责任桥 | 0.365557 | 0.000000 | 0.829032 | +0.396993 | +108.600% |
| `rrf_original_A` | recency 与原始 A 角色排序的等权 RRF，`k=60` | 0.762550 | 0.531183 | 0.872043 | 0.000000 | 0.000% |
| `recency_rrf_pairwise_B`（目标） | recency 与 pairwise_B 角色排序的等权 RRF，`k=60` | 0.762550 | 0.531183 | 0.872043 | — | — |
| `deletion_recency` | 删除责任桥后的消融；按协议应退回 recency | 0.857874 | 0.815054 | 0.884946 | -0.095324 | -11.112% |
| `shuffled_pairwise_B_rrf` | 对 pairwise_B 角色概率做固定 seed shuffle 的同预算负对照 | 0.850545* | 0.795699* | 0.884946* | -0.087995* | -10.346%* |

表中差值统一是“目标 − 该行条件”，相对差是除以该行条件的 MRR；星号表示 shuffle 随 seed 改变。recency 是预注册集合上全局一次选出的最强公平基线；`fixed_last` 与它并列，但按冻结的确定性顺序保留 recency 名称。目标与 `rrf_original_A` 在这 200 条外部记录上逐条得到相同排名，因此两者 MRR、R@1、R@3 完全相同；这不是把 A 当成目标的假设，而是正式输出中的观察结果。

### 目标相对最强基线的结果

目标的 task-group MRR 为 `0.7625498911`，recency 为 `0.8578737518`，绝对差为 `-0.0953238607`，相对差为 `-11.111642%`。三个 seed 的方法差值方向都为负：

| seed | 目标 − recency 的 bootstrap 均值 | 95% CI（5000 次 task-group paired bootstrap） |
|---:|---:|---:|
| 20260816 | -0.094990 | [-0.11876472, -0.07247312] |
| 20260817 | -0.095300 | [-0.11878648, -0.07191116] |
| 20260818 | -0.094990 | [-0.11859447, -0.07250768] |

pooled 的 155-group paired bootstrap 均值为 `-0.09547949`，95% CI 为 `[-0.11957373, -0.07179724]`，上界仍小于 0。这是目标相对 recency 的负差异，不是“目标提升的置信区间”。

### 行级敏感性与配对计数

row-equal MRR 中，目标为 `0.7800079116`，recency 为 `0.8632440227`，绝对差 `-0.0832361111`，相对差 `-9.642246%`。目标的 row R@1/R@3 为 `0.575/0.880`，recency 为 `0.820/0.895`；对应的 task-group R@1/R@3 为目标 `0.531183/0.872043`、recency `0.815054/0.884946`。

目标相对各对照的 better/worse/tie（顺序为目标更好/更差/相同）如下；group 计数总和为 155，row 计数总和为 200：

| 对照 | task-group better/worse/tie | row better/worse/tie |
|---|---:|---:|
| recency | 7 / 47 / 101 | 7 / 52 / 141 |
| fixed_first | 133 / 22 / 0 | 170 / 30 / 0 |
| fixed_midpoint | 132 / 23 / 0 | 167 / 33 / 0 |
| fixed_last | 7 / 47 / 101 | 7 / 52 / 141 |
| pairwise_local_bridge | 133 / 22 / 0 | 168 / 32 / 0 |

相对 recency 的计数在三个 seed 中相同。相对 shuffle 的 group 计数依次为 `9/55/91`、`10/54/91`、`7/56/92`，row 计数依次为 `9/62/129`、`10/59/131`、`7/64/129`；这说明目标没有稳定击败负对照。

### E1、删除和 shuffle 诊断

责任角色诊断 E1 在三个 seed 中相同：row top-1 的 original_A/pairwise_B 均为 `0.050000/0.050000`，row balanced 均为 `0.072500/0.072500`；group top-1 均为 `0.056989/0.056989`，group balanced 均为 `0.081989/0.081989`。这与目标 RRF 退化为 `rrf_original_A` 的观察一致。

`deletion_recency == recency` 在三个 seed 上均成立，说明删除责任桥后的消融确实回到了基线，但不能证明桥本身有益。shuffle 的 task-group MRR 为 `0.850545`、`0.850696`、`0.855977`，均高于目标 `0.762550`；因此预注册的“shuffle 应低于目标”门未通过。

### 审计、成本与精确判定

- 资格硬门、源代码/数据 hash、页 hash、seen-ID union（1678 个唯一 ID）全部匹配；外部资产为 200 eligible rows、155 groups。
- 方法输入的 forbidden fields 为空，角色仍匿名，方法记录数为 200；Gold 只在最终 evaluator 中挂接，`method_metrics_fit_external_gold=false`，训练/预测未使用外部 Gold 或词法字段。
- pairwise_B 仅在冻结 AFTraj 731 条训练记录上拟合（2672 条训练特征行、3882 条 pairwise 训练行）；没有额外模型/API 调用或重试。正式 runner 的 `formal_run_count=1`、`network_page_requests=0`、`api_calls=0`、`token_calls=0`，且所有条件记录数一致。

预注册的 `EXTERNAL_RRF_FEASIBILITY_GO` 要求三个 seed 都为正、每个 seed 的 CI 下界都大于 0、删除退回 recency、shuffle 明显弱于目标且审计通过。本次只有审计和删除消融通过；目标三个 seed 均为负、CI 上界均小于 0，shuffle 也高于目标。因此精确判定为：

`STOP_EXP100_FIXED_EXTERNAL_RRF_ONLY`

这个 STOP 只针对固定的 200 条外部页面和本次 `recency_rrf_pairwise_B` 外推，不是整个 Who&When 方向的 NO-GO（`direction_no_go=false`），也不是最终论文 GO（`is_final_paper_go=false`）。它同时不是“正向但 CI 跨 0”的 `POSITIVE_NOT_YET_GO`：这里观察到的是稳定负差异。正式结果 JSON、冻结协议和上述审计字段共同构成可复核证据。

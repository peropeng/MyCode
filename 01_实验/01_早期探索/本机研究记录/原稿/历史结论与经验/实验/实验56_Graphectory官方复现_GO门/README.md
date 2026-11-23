# 实验56：Graphectory 官方 RQ2 主结果复现（GO 门）

状态：`GO_REPRODUCED_RQ2_CORE_TREND`（仅表示 RQ2 核心趋势门通过；不表示逐 cell exact match，冻结裁决见 `results/reproduction_decision.md`）。

## 目的与边界

本实验只裁决 OOPSLA 2026 *Process-Centric Analysis of Agentic Software Systems* 的 Graphectory RQ2 主结果（阶段转移/终止阶段分布）是否可在官方代码、官方 Zenodo 原始轨迹和官方分析入口上重建。它不把预置 graph/CSV 直接绘图，也不调用 LLM/API，不声称本文方法有收益。

输入链必须是：

```text
Zenodo raw_trajectories.tar.gz
  -> official graph_construction/generatejson.py (via scripts/construct.sh)
  -> official graph_analysis.batch_runner (via scripts/analyze.sh)
  -> official plot scripts (via scripts/reproduce.sh)
```

选择 RQ2 是因为官方仓库把 `sankey_grid.png`、`end_phase_donuts.png` 和 `phase_transition_overview.png` 明确列为 RQ2 结果；本实验以 `end_phase_donuts.png` 及其冻结计数表为主结果，阶段转移表作为交叉检查。`lang_construction/get_lang.py --mode lang` 的已知缺陷不作为本 RQ2 入口的替代实现；其失败单独记录，不隐瞒。

## 固定来源与环境

- Graphectory：<https://github.com/Intelligent-CAT-Lab/Graphectory>
- 固定 commit：`31a6c3712c94b9b2369d2de916a60e09f9b34f4a`
- 原始轨迹：Zenodo record `17364210`，`raw_trajectories.tar.gz`；Zenodo MD5 `26e71c7e9257b82be95be34d6edbba98`，本次 87 个 range chunk 合计 1,446,491,536 bytes 的下载 SHA-256 见 `results/source_manifest.json`。
- 论文/工件主结果参考：官方仓库 `data/{SWE-agent,OpenHands}/graphs` 与 `analysis`（仅作 reference，不作为新结果输入）。
- 运行时：Python 3.12.13 / macOS arm64；官方依赖环境路径在被忽略的 `runtime/env/graphectory`；`environment.md` 与冻结 manifest 记录实际版本。Docker 可用但本次未使用，采用官方脚本的原生等价运行环境。

第三方源码、原始轨迹、生成 graph、长日志、虚拟环境和图像均在 `runtime/`，由 `.gitignore` 忽略。提交中只保留可重跑脚本、预注册合同、审计代码和小型冻结结果。

## 预注册接受门

只有下列条件全部满足才记 `GO / REPRODUCED`：

1. 官方 Zenodo 原始轨迹的四个 SWE-agent 与四个 OpenHands 数据源均经官方构图入口成功生成新 graph；每个数据源的输入/输出计数和 hash 可追踪。
2. 官方 `scripts/analyze.sh` 从新 graph 产生八个 `trajectory_metrics.csv`，没有读入官方预计算分析 CSV。
3. 官方 `scripts/reproduce.sh` 在只包含新 graph/新 CSV 的 runtime data root 上成功生成 RQ2 图；冻结表由新 graph 重新解析阶段，不从最终统计文件读取。
4. 新结果与官方同源 graph/analysis reference 的主结果计数/排序逐项比较。交接规则允许“误差≤约5%或核心排序/趋势”；本实验同时报告严格的 status×phase sparse-cell 相对误差，并以官方 RQ2 图的聚合阶段分布作为核心趋势门：8 个单元 graph count 相等，end-phase 与 transition 聚合分布最大绝对百分点差 ≤5 pp，且排序一致。该核心门通过时只记 `CORE_TREND`，不升级成 `EXACT_MATCH`。
5. 命令返回码、耗时、输入输出 SHA-256、轨迹/graph/CSV/figure 计数写入 `results/manifest.json`。

任何一项不满足均不得写成 GO；应写 `NOT_REPRODUCED` 或 `PARTIAL_REPRODUCTION` 并给出 blocker。

## 一键重跑

先准备被忽略的 `runtime/`（官方 clone、Python 环境、已解压 Zenodo 输入和 reference LFS hydration；运行脚本不会下载或修改仓库源代码）：

```bash
python3 run_reproduction.py
```

也可以跳过 runtime 准备，只重跑官方构图、分析、出图和审计：

```bash
python3 run_reproduction.py --skip-hydrate
```

`--skip-hydrate` 是兼容性开关；当前脚本要求 `runtime/` 已由 `hydrate_reference_lfs.py` 和 Zenodo chunk 下载/解压步骤准备好。一次运行的 11 个命令、return code、耗时和 log hash 冻结在 `results/manifest.json`。

脚本使用 `runtime/vendor/Graphectory` 的固定官方 commit；输出均写到 `runtime/repro_data`、`runtime/repro_figures`，裁决和冻结小结果写到 `results/`。

## 不允许的替代

- 不把官方预计算 graph/CSV 复制到新结果目录后称为重建；
- 不用 3 条 sample 的 smoke 结果替代全量 RQ2 结果；
- 不以 `get_lang.py` 缺失函数的兼容补丁伪造 Langutory；
- 不根据最终 resolved/unresolved 标签筛选轨迹；标签只通过官方 evaluation report 进入图的 resolution status；
- 不把 RQ2 复现写成 RQ1/本文方法的 GO。

## 决策记录

最终裁决、逐门证据、剩余风险与下一步见：

- `results/reproduction_decision.md`
- `results/manifest.json`
- `results/rq2_end_phase_counts.csv`
- `results/rq2_phase_transition_counts.csv`
- `results/source_manifest.json`

严格逐 cell 门的限制已经写入冻结裁决：本次 `max_nonzero_relative_error=1.0` 来自极稀疏的 status×phase/transition cell，不能被删掉或解释成 exact；核心聚合趋势仍在 5 pp 内且排序一致。因此结论是 RQ2 核心趋势 `GO`，而不是全量统计 `GO`。

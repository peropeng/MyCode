# EXP-Bench 科研 Agent 过程恢复 Gate0 资格报告

## Decision

`STOP_ASSET`。Gate0 不是章节 GO，也不计入同一冻结目标的三次方法失败。硬门一旦失败，不运行 Gate1 或模型实验。

## 论文站台与重叠

形式论文组为 5 篇：ICLR 2026 EXP-Bench、ACL 2026 Long Agentic Rubrics、NeurIPS 2025 Main Self-Challenging、NeurIPS 2025 Main STRATUS、ICLR 2025 ScienceAgentBench。两章各有 CCF A 正式论文站台，数量门本身通过。

但直接重叠杀测不能忽略：EXP-Bench 已将 research question、incomplete starter code、procedure extraction、step-by-step procedures 和完整 experiment execution/evaluation 放入同一 benchmark；Agentic Rubrics 已做 repository-grounded checklist verification；Self-Challenging 已做 verification function + solution/failure tests；STRATUS 已做安全迭代和 Transactional No-Regression。若候选只实现 rubric/逐步评分/失败步骤局部修复/重跑测试，独立重叠裁决为 `REJECTED_OVERLAP`，不能换成科研数据集来回避。

## 资产与 Gold 计数

| 硬门 | 观测 | 结果 |
|---|---:|---|
| EXP-Bench 官方 repo/license/固定 commit | MIT / `401573342845fe24963d4384e6849d53f046dd23` | PASS |
| EXP-Bench claimed rows/papers/subtasks | 461 / 51 / 12,737 | 仅声明规模，不等于可执行 Gold |
| 独立可执行 task | 0 | FAIL，要求 >=100 |
| 按 paper/family/template 分组 held-out | 0 task / 0 paper | FAIL，要求 >=40 / >=10 papers |
| 程序化 milestone/procedure/evidence Gold | 0 | FAIL，要求 >=100 |
| 可执行 failure step -> repair/rerun outcome Gold | 0 | FAIL，要求 >=50 |
| 冻结 trace -> artifact -> test -> final outcome 链 | 0 | FAIL，要求 >=1 |
| CPU/16GB/无 API/无 GPU smoke | 0 | FAIL，要求 >=1 |
| 外部实验族 | 0 个合格族 | FAIL，要求 >=2 |

EXP-Bench CSV 的 461 行全部有自然语言 `question`、`agent_instructions`、`impl_requirements`、`expected_outcome`、`design`；333 行有 `source_files` 路径，458 行有 GitHub/PDF URL。`source_files` 只是外部仓库中的路径，不是本地 starter code；`expected_outcome`/`design` 是文本，不能当非 LLM Judge Gold。仓库虽追踪 52 个 `*_complete_final.json`、396 个 generated-program JSON 和 351 个 program-analysis JSON，但这些是任务抽取或 agent 输出说明，没有可重放的执行 trace、artifact schema、失败步骤和 repair outcome。

ScienceAgentBench README 声称 102 tasks/44 publications，但完整 `benchmark/datasets`、`gold_programs`、`scoring_rubrics` 位于需密码的外部压缩包；当前浅克隆无这些文件，且其 evaluation 允许 GPT-4o 视觉 judge。MLGym README 声称 13 个 benchmark task families；浅克隆虽有重复轨迹文件，但不能形成 100 个独立、10 篇 held-out source papers 的研究任务，且主要代码为 CC-BY-NC 4.0，运行说明依赖 Docker/模型 API/GPU。

## 资产边界与安全

本 Gate0 仅使用官方页面、官方仓库 shallow/sparse clone、README、CSV/JSON schema 和聚合计数。没有调用模型/API、下载权重/大数据、执行全量 Docker、运行 destructive `docker rmi`，也没有提交第三方 raw data、轨迹、论文全文、密钥或 PII。第三方 clone 位于 ignored `runtime/`。

## 结论

当前最严谨结论是 `STOP_ASSET`：研究问题不是因为三次方法失败而停止，而是因为第一章和第二章都没有合格、可离线、非 LLM Judge 的实验对象。除非主线程重新指定一个能提供冻结执行 trace、artifact/test/evidence Gold 和失败→repair outcome 的官方资产，否则继续改协议、换 rubric 或换科研数据集都不会把候选推进到 Gate1。

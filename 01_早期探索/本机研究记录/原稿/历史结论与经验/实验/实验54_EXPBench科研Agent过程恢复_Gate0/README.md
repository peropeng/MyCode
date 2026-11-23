# 实验54：EXP-Bench 科研 Agent 过程验证与执行恢复 Gate0

## 当前裁决

`STOP_ASSET`。这不是章节 GO，也不计入“同一个冻结目标的三次方法失败”。

候选题的暂定名称为《面向科研智能体的实验过程验证与执行恢复方法研究》。Gate0 只做正式论文、官方仓库、许可、任务/Gold schema 和重叠审计，不训练模型、不调用 API、不运行全量 Docker/评测。

截至 2026-08-21 的可复现证据：

- EXP-Bench 官方仓库 `Just-Curieous/EXP-Bench` 固定 HEAD `401573342845fe24963d4384e6849d53f046dd23`，仓库 MIT；其 CSV 有 461 行、51 个论文来源、12,737 个 subtasks。
- 该 CSV 只给出问题、自然语言 instruction/expected outcome、source-file 路径和 GitHub/PDF URL；461 行中 333 行有 source-file 列表，但本地没有对应 starter repository、执行 trace、artifact/test schema 或可程序化 Gold。
- EXP-Bench 官方评测需要 Docker、模型/API，并把 design/setup/conclusion 等部分交给 LLM judge；因此不能把 461 行文本或 judge 输出当作本课题的过程 Gold。
- 在当前浅克隆中，程序化 milestone/evidence Gold = `0`，可执行失败步骤→repair/rerun outcome Gold = `0`；均未达到硬门 `>=100` 和 `>=50`。
- ScienceAgentBench 官方代码固定 HEAD `c26e151ed601ba109dc4d35e057ff8e73fec469d`，README 声称 102 tasks/44 publications，但完整 benchmark 是需密码的外部压缩包，仓库本地没有 Gold/program artifacts；其评测还依赖 GPT-4o 视觉 judge。MLGym 官方仓库固定 HEAD `9d40c1b5035202018cd7091fb4e83a9c68b377c0`，README 声称 13 个 benchmark task families，主要代码为 CC-BY-NC 4.0，且运行说明要求 Docker/API/GPU，不满足本题规模/许可硬门。

直接重叠压力也已记录：EXP-Bench 已提供 research-question + incomplete starter code + step-by-step procedure 的过程分解和端到端 experiment evaluator；Agentic Rubrics 已提供 repository-grounded rubric verification；Self-Challenging 已提供 verification function 与 solution/failure tests；STRATUS 已形式化 Transactional No-Regression。若以后只剩“生成 rubric/逐步打分/限制修复到失败步骤/重跑测试”，应裁决 `REJECTED_OVERLAP`，不能换科研数据集保留。

## 复现

外部浅克隆必须放在被忽略的 `实验54.../runtime/` 下。本次已在 worktree 的 ignored runtime 中核验，提交不包含第三方代码、raw 数据、论文全文、轨迹或密钥。

```bash
cd 实验/实验54_EXPBench科研Agent过程恢复_Gate0
python3 scripts/audit_sources.py --runtime runtime/sources
python3 -m unittest discover -s tests -v
python3 -m json.tool results/qualification.json >/dev/null
python3 -m json.tool results/asset_census.json >/dev/null
python3 -m json.tool results/gold_census.json >/dev/null
python3 scripts/privacy_audit.py
git diff --check
```

Gate0 后不启动 Gate1：若不先获得可离线、程序化、非 LLM-judge 的 milestone/evidence Gold 及失败→repair outcome Gold，继续改方法没有可解释的实验对象。

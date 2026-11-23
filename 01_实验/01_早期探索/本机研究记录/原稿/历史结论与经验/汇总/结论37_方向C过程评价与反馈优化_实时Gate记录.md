# 结论37：方向C过程评价与选择性反馈优化——实时 Gate 记录

> 状态：候选方向资格实验进行中  
> 建立时间：2026-08-21  
> 证据原则：Judge 生成的解释、rubric 或标签不能同时充当未经独立验证的 Gold；评价准确与反馈改善必须分章独立过门。

## 0. 当前裁决

| 项目 | 状态 | 说明 |
|---|---|---|
| Gate 0：公开 process-evaluation 资产 | **CONDITIONAL** | 多个公开代码/数据 smoke 可运行，但完整 benchmark 依赖 API/模型/重型 Web 环境，部分数据许可或入口未知 |
| Gate 1：requirement/evidence Gold | **STOP** | 数量门可达，但独立 requirement→evidence 映射为 0/365，同 Judge/无逐行 provenance 风险未解决 |
| RQ1：证据约束的过程评价 | 未开始 | 主指标必须联合评价 verdict 与 evidence |
| RQ2：选择性反馈优化 | 未开始 | 正确反馈必须实际改善可执行任务且控制 harmful feedback |
| 两章总体 | 未 GO | Predicted feedback 不胜 No/Random/Shuffled 时递进失败 |

## 1. Gate 0 冻结判据

- 核验 Agent-as-a-Judge/DevAI、SWE-Gym、Plan-RewardBench、Agentic Rubrics、Proposer-Agent-Evaluator 等论文与资源；
- 至少 3 篇正式 CCF A 直接站台；
- 至少 2 个可运行 benchmark；
- 代码、数据、模型、许可证分别核验；
- 只有闭源 Judge、无可审计 Gold 时 STOP。

## 2. Gate 1 冻结判据

- 至少 100 个独立 task/trajectory；
- 至少 300 个 requirement/rubric item；
- 至少 80% requirement 可映射到独立证据；
- 方法输入不得读取隐藏测试结论；
- 若主要标签来自同一个 Judge 自评则 STOP；
- 同一任务的多 trajectory 和 rubric 派生项必须同组。

## 3. 两章桥接预注册

在 Agent、候选数、修正次数和总调用预算相同条件下比较：

1. No Feedback；
2. Random Feedback；
3. Shuffled Predicted Feedback；
4. Predicted RQ1 Feedback；
5. Oracle Requirement Feedback。

先证实 Oracle 相对 No 至少提升 10% 且任务级 CI 下界大于 0；再要求 Predicted 胜 No、Random、Shuffled，同时 harmful feedback 受控。评价器准确但反馈不改善任务时，只能保留单章评价方向，不能声称两章 GO。

## 4. 执行隔离

- 基础分支：`main`
- 基础提交：`7bbe5fb0582815d24789750dbcac2c42ff78cc89`
- 执行分支：`exp/0821-direction-c-gate01`
- worktree：`/Users/peroyang/My/MyWork/worktrees/0821-direction-c-gate01`
- 执行线程只拥有：`实验/实验37_方向C过程评价Gate0Gate1/`
- Docker/Colima 已验证可用；环境成功不计方法证据。

## 5. 实验轮次

| 轮次 | 目标 | 当前结果 | 科研进展 | 下一步 |
|---:|---|---|---|---|
| C1 | Gate 0/1 公开资产与 requirement/evidence 资格 | Gate0 CONDITIONAL；Gate1 STOP | 有排除性进展：确认公开混合池不能承担独立 evidence Gold | 不进入 evaluator/RQ2；先取得带独立测试/人工证据的许可快照 |

## 6. 轮次 C1 验收证据

- 执行提交：`592a4fd`，已由主线程审查并 cherry-pick 为 `0027169`；
- DevAI：55 个任务、365 条声明 requirement、125 条 preference；
- 三个 Agent 的 AaaJ/human judgment 每个来源有 55 文件、366 记录，其中 1 个任务多出 1 条 requirement；
- 持久 requirement 记录中的 `evidence/source/location` 映射：`0/365`；
- Plan-RewardBench：1,171 pair、584 个去重 task UUID、2,128 个去重 trajectory 内容；重复 UUID 和 hard negative 未按独立自然任务计数；
- AaaJ gray-box 标签属于 evaluator 自身 verdict；human 文件虽独立存放，但标注证据和 provenance 未序列化；
- Agent-as-a-Judge trajectory schema、Plan JSONL、SWE-Gym 代码与 PAE Python 3.11 Docker syntax/data smoke 均可运行；这只支持 Gate0 的资产正信号；
- 主线程复验：`python3 -m unittest discover -s 实验/实验37_方向C过程评价Gate0Gate1/tests -v` 为 3/3 通过，`py_compile` 通过。

当前科研裁决：**方向 C 不能按现有公开混合池进入两章实验。** 这是 Gate1 数据证据 STOP，不是“过程评价问题本身被算法否定”。最便宜的解锁条件是获得带逐 requirement 独立测试/仓库/trace 证据的许可数据，或先建 30-task、双独立标注者的小试点；在此之前不训练 evaluator。

## 7. 禁止表述

- 不得把同一 Judge 生成的标签、证据和最终裁决视为独立 Gold；
- 不得用隐藏测试结论作为在线评价输入；
- 不得只提高 Judge 一致率而没有证据正确性；
- 不得只提高评价分而没有最终可执行任务改善；
- 不得通过增加工具/API 调用预算形成不公平增益；
- 不得把 Prompt、rubric JSON 或反馈压缩格式包装成核心创新。

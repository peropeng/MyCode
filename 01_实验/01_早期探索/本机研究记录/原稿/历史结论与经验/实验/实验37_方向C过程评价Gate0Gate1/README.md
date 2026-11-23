# 实验37：方向 C 过程评价 Gate 0/1 资格审计

本实验只回答两个前置问题，不实现完整 evaluator，也不把公开 benchmark 的 Judge 输出当作 Gold：

1. 公开的 Agent-as-a-Judge/DevAI、SWE-Gym、Plan-RewardBench、Agentic Rubrics、Proposer-Agent-Evaluator 是否有正式论文、可下载代码/数据、许可和最低成本 smoke 路径？
2. requirement/evidence Gold 是否能在不读取隐藏终局测试、且不复用同一个 Judge 自评的条件下重建？

## 当前结论

| Gate | 结论 | 依据 |
|---|---|---|
| Gate 0 | `CONDITIONAL` | 5 篇正式论文中至少 3 篇是 ICML/ACL 主会 Long/Regular；AaaJ/DevAI、Plan-RewardBench 和 PAE 可浅克隆并完成数据/语法 smoke。但完整运行分别需要 API/依赖、GPU 或 WebArena/Chrome/Bedrock；SWE-Gym 数据未随仓库发布，PAE 的 `LICENSE.txt` 与 `setup.py` 许可证元数据冲突。 |
| Gate 1 | `STOP` | 数量下限可在“混合池”上达到，但 Gold 不能成立：DevAI 365 条 requirement 的持久记录没有任何 evidence/source/location 字段；AaaJ gray-box 标签是同一 evaluator 的 verdict；Plan 的 chosen/reject 只是 pair preference，且每行没有 panel/meta-review 证据。 |

最便宜的下一步是先锁定一个可研究使用、包含独立证据的 DevAI/软件任务快照，再做 30-task 小试点：每条 requirement 预注册 repository/test/trace evidence，至少两名独立标注者分离 Gold 与 Judge；在此之前不训练 evaluator，也不做 RQ2 反馈闭环。

## 可复现入口

所有公开仓库只用于本地审计，`assets/` 已加入 `.gitignore`，不会进入本分支提交。重新下载：

```bash
./scripts/fetch_public_assets.sh
```

重新生成候选记录和统计：

```bash
python3 scripts/qualify_gate01.py \
  --asset-root assets \
  --output-dir .
```

运行低成本 smoke 并保存日志：

```bash
./scripts/run_smoke.sh logs/smoke_latest.log
```

单元测试（仅标准库）：

```bash
python3 -m unittest discover -s tests -v
```

## 资产审计口径

机器可读的正式论文、代码、commit、数据入口、许可证、环境、smoke 和复现状态见：

- `manifests/papers_repos_datasets.json`
- `manifests/environment.json`

明确区分四种证据：

- `paper_claim`：论文或 README 声称的规模、方法和标签来源；
- `field_present`：克隆文件中实际存在的字段；
- `smoke_pass`：本机/Docker 实际跑过的最低成本命令；
- `not_verified`：需要 API、隐藏数据、模型、许可证确认或重型环境，当前没有据此做正面结论。

## 数据与去重统计

### Agent-as-a-Judge / DevAI

- 本地 `devai/instances`：55 task，365 条声明 requirement，125 条 preference。
- 三个开发 Agent（OpenHands、MetaGPT、GPT-Pilot）各有 55 个 gray-box AaaJ 文件和 55 个人工标记文件；每个来源实际包含 366 条 requirement 记录，其中 `52_Devin_AI_Trains_an_AI` 比基准多 1 条，不能默默当作一致 Gold。
- AaaJ 与 human judgment 文件的 requirement 对象只有 `requirement_id/prerequisites/criteria/category/satisfied`；逐条 evidence、证据来源、文件行号、测试命令、checkpoint 均缺失。
- `scripts/evaluate_confidence.py` 的实际 OpenHands 对比 smoke 为 55 tasks、366 requirements、accuracy 0.9016，但 confidence 全为 1.0000、AUROC 0.4861；这只能证明标签文件可比较，不能证明 human label 是带证据的 Gold。
- 仓库只带 1 个 OpenHands trajectory 和 11 个 workspace 文件集合，不能把 55 task 宣称为 55 条可重放轨迹。

### Plan-RewardBench

- 7 个 JSONL split 共 1,171 pair rows，1,170 个精确 pair 内容；`uuid` 去重后为 584 个 task UUID。
- chosen/reject 两侧的精确 trajectory 内容分别为 1,107/1,031，合并去重 2,128；但同一 UUID 出现频数为 1/2/3/4 = 209/183/172/20，hard-negative/最小编辑 pair 不能折算成 2,128 个独立自然 task。
- 每条记录有 `query/tools/uuid/chosen/reject/_lcp_bucket`，没有 requirement/rubric/evidence 字段；论文/README 声称使用多 LLM judge panel + meta-review，但每行不包含 panel votes、reviewer identity 或独立测试证据。
- 规则扫描在 2,342 条 side trajectory 中只有 8 条出现 `unit test`/`ground truth` 等 marker；这不是“未读取隐藏测试”的证明，只是当前文本字段的可见扫描结果。

### SWE-Gym 与 PAE

- SWE-Gym 仓库 README 声称 2.4K real tasks/11 Python repos 和 234 Lite split，但数据不在浅克隆仓库，HF 数据入口本次返回 401，故任务规模与 license 记为 paper claim/UNKNOWN，未用于 requirement Gold。
- PAE 仓库本地 `data/webarena_map_google_fixed_eval.jsonl` 有 89 个 task map 行；论文另声称 11,220 条训练 trajectory，但完整 HF 数据未下载。Python 3.11 Docker syntax/data smoke 通过；宿主 Python 3.9 因 `match` 语法失败，属于环境不匹配而非成功复现。
- PAE `LICENSE.txt` 是 CC BY-NC 4.0，而 `setup.py` metadata 写 MIT，不能在解决前把它当作无条件可再发布资产。

## 目录说明

- `data/candidate_requirements.jsonl`、`data/candidate_requirements.csv`：365 条 DevAI requirement 的紧凑记录及三套 AaaJ/human 标签字段；无原始 evidence 内容。
- `data/candidate_trajectories.jsonl`：2,342 条 pair side 的紧凑轨迹身份、hash、角色计数、重复 UUID 和 marker 统计；无原始消息复制。
- `data/sample_audit.jsonl`：18 个代表项的人工阅读 + 规则核验记录，包含无 evidence、同 Judge、pair label 和 UUID 去重结论。
- `reports/qualification_report.json`：Gate 判定、阈值、计数、风险和下一动作的机器可读结果。
- `reports/qualification_report.md`：面向主线程的审计报告。
- `logs_preflight.txt`、`logs_runtime_smoke.txt`：实际命令的返回码和失败原因；`logs/smoke_latest.log` 可由 `run_smoke.sh` 重新生成。

## 明确不作的推断

- 不把 AaaJ 的 `satisfied` 结果当 Gold；
- 不把 human 文件的二元标签当作“已拥有 evidence Gold”；
- 不把 Plan chosen/reject 当作 requirement correctness；
- 不把重复 UUID 的 hard-negative rows 当作独立自然 task；
- 不把论文声称的 SWE-Gym/PAE 轨迹规模写成已在本地存在；
- 不把 Gate 0 的可下载/可解析误写成 Gate 1 的科研可行性。

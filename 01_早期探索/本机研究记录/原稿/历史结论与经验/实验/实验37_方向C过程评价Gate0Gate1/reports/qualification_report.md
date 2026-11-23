# 方向 C Gate 0/1 资格实验报告

## 一、裁决

**Gate 0：CONDITIONAL。Gate 1：STOP。**

Gate 0 的 `CONDITIONAL` 不是论文身份不足，而是“公开资产能下载/解析”与“完整评测可在当前低成本环境复现”之间仍有依赖缺口。Gate 1 的 `STOP` 是 Gold 合同失败，不是样本数量不足：requirements 和轨迹都能找到，但没有可独立审计的 requirement→evidence 映射。

## 二、正式论文与资产

正式身份、代码 commit、许可证、数据入口、硬件和 smoke 命令均记录在 `manifests/papers_repos_datasets.json`。本次正式论文核验结果如下：

| 资产 | 正式身份 | 实际公开资产 | 低成本 smoke | 关键限制 |
|---|---|---|---|---|
| Agent-as-a-Judge / DevAI | ICML 2025 PMLR 267 | MIT 代码；55 task/365 requirement 本地实例；HF 数据入口 | Python 3.11 Docker + `validate_trajectory.py`：PASS | DevAI 数据 license UNKNOWN；仅 1 条 trajectory；完整 Judge 需 API |
| SWE-Gym | ICML 2025 PMLR 267 | Apache-2.0 代码；HF 数据入口 | `compileall scripts`：PASS | 2.4K/234 是 README/paper claim；数据未 vendored，HF 本次 401 |
| Plan-RewardBench | ACL 2026 Main Long | Apache-2.0 代码/评估；CC BY 4.0 数据；1,171 JSONL pairs | JSONL reader：PASS | evaluator CLI 依赖 `requests`/`torch`；完整 judge 需 API/GPU/模型 |
| Agentic Rubrics | ACL 2026 Main Long | 正式论文；官方代码、数据和 license 未定位 | UNKNOWN/未运行 | 论文中的 rubric/test alignment 不是已发布 evidence Gold |
| Proposer-Agent-Evaluator | ICML 2025 PMLR 267 | 代码、89-row task map；HF data/checkpoint入口 | Python 3.11 Docker syntax/data：PASS | 需 VLM、Chrome、Bedrock/WebArena；LICENSE.txt CC BY-NC 与 setup.py MIT 冲突 |

其中 ICML/ACL venue 的 CCF A 归类遵循主任务给定规则；这只说明 venue 身份，不替代复现实验。

## 三、Gate 0 证据

### 已证明

1. 五篇论文均有正式出版社/会议页面；AaaJ、SWE-Gym、PAE 为 ICML 2025，Plan-RewardBench、Agentic Rubrics 为 ACL 2026 Main Long。
2. AaaJ、SWE-Gym、Plan-RewardBench、PAE 四个代码仓库可浅克隆并锁定 commit；Agentic Rubrics 没有找到官方 code link，manifest 写 `UNKNOWN`。
3. Docker CLI/Engine 与 Colima 运行正常；`alpine:3.20` 容器 smoke 通过。
4. AaaJ 的一个实际 trajectory schema validator 在 Python 3.11 Docker 中返回 0；Plan JSONL 七个 split 全部可读；SWE-Gym 代码目录可编译；PAE 在 Python 3.11 Docker 中可编译且 89-row task map 可读。

### 未证明

1. AaaJ/Plan 的完整 Judge 没有运行：前者需要 LLM API；后者的 evaluator 还依赖 `torch`/模型。
2. SWE-Gym 的 HF 数据和 license 未锁定；不能声称 2.4K task 在本地可复现。
3. PAE 的全流程需要 Chrome/ChromeDriver、VLM checkpoint、Bedrock/Claude 和大规模 GPU；代码许可证冲突待澄清。

因此 Gate 0 只能 `CONDITIONAL`。下一步不应是训练，而是用干净 Python 3.11 Docker 锁定可研究用数据 snapshot、依赖和许可。

## 四、Gate 1 数量与去重

### Requirement 侧

- DevAI 基准实例：55 task。
- 基准实例的声明 requirement：365；preference：125。
- 三个开发 Agent 各有 55 个 AaaJ gray-box 文件和 55 个人工文件；每种来源实际 366 条 requirement 记录。
- 额外的第 366 条来自 `52_Devin_AI_Trains_an_AI`：基准实例为 4 条，judgment 为 5 条。这个字段对齐差异会阻止“盲目按行 zip”。
- `candidate_requirements.*` 仅输出基准的 365 条，并将各来源标签按 `(criteria, category)` 对齐；证据字段计数为 **0/365**。

### Trajectory 侧

- Plan-RewardBench：1,171 pair rows，1,170 unique pair content。
- UUID 去重后 584 个 task UUID；频数为 209 个只出现一次、183 个出现两次、172 个出现三次、20 个出现四次。
- chosen/reject exact content 去重后分别 1,107/1,031，合并 2,128 条 trajectory content。该数字只能作为“可读轨迹内容规模”，不能当作 2,128 个自然独立 task：同一 UUID 的 hard-negative/最小编辑会重复任务上下文。
- `candidate_trajectories.jsonl` 明确记录 `same_task_duplicate`、`exact_content_unique` 和 `pair_label_is_independent_gold=false`，避免下游误算。

## 五、Gold 与证据审计

### DevAI / AaaJ

`devai/instances/*.json` 的 requirement 只描述 criteria、category、prerequisites；AaaJ/human judgment 文件增加的是 `satisfied`，没有 `evidence`、`source`、`location`、`trace`、`file` 或测试命令。criteria 中出现 `src/*.py` 等 path anchor 只能说明“将来可以设计 probe”，不是已存在的 evidence。

AaaJ gray-box 的 `satisfied` 明确是 evaluator 自己的输出。仓库的 confidence 脚本把它与 `human_as_a_judge` 标签比较，实际 OpenHands smoke 为 55 task / 366 requirement / accuracy 0.9016；但 confidence 是 1.0、AUROC 是 0.4861，且 human 文件没有逐条证据。结果只能说明两份标签可比较，不能将 AaaJ 或 human 文件升级为独立 requirement/evidence Gold。

### Plan-RewardBench

每行实际含 `query/tools/uuid/chosen/reject/_lcp_bucket`。`chosen/reject` 是 pairwise preference 角色，不是 requirement verdict；论文/README 声称多 LLM judge panel + meta-review，但每行没有 vote、reviewer、test execution 或 evidence reference。2,342 side trajectory 中只有 8 条出现 `unit test`/`ground truth` marker，且该扫描不能证明没有读取隐藏测试。

### 代表样本审计

`data/sample_audit.jsonl` 共 18 行：DevAI 的 10 个 requirement（文件路径、训练/输出行为等混合）和 Plan 的 7 个 split 代表轨迹，另含一个重复 UUID case。逐项规则核验的共同结论是：

- criteria/path anchor 可定位未来检查对象，但当前记录无 evidence pointer；
- human label 可见但 annotation/evidence provenance 不可重建；
- Plan trajectory 可见 tool response/role sequence，但无 requirement rubric，chosen/reject 不能作为 requirement Gold；
- repeated UUID 不计为独立 task，只保留 exact trajectory hash 作为规模审计。

## 六、为什么 Gate 1 必须 STOP

Gate 1 要求的不只是 `>=100 task/trajectory` 和 `>=300 requirement item`，还要求至少 80% requirement 可映射到独立证据、且不读取隐藏终局测试。当前混合池可以在表面数量上超过阈值，但：

1. requirement→evidence 映射落盘为 0/365，远低于 80%；
2. AaaJ labels 属于同一 Judge 的 verdict，不能充当 Gold；
3. human labels 没有独立证据/标注过程记录，不能自动视为可重审 Gold；
4. Plan pairs 的标签来源只有论文/README 的高层声明，缺逐行独立审计证据；
5. SWE-Gym 和 Agentic Rubrics 的关键数据/代码不可在本次环境中验证。

继续扩大 API 调用、训练 reward model 或把 2,128 trajectory content 拆成更多“独立样本”都不能修复这个合同问题。

## 七、最便宜的复活方案

1. 先锁定一个 license-cleared、可下载的 DevAI 或软件任务 snapshot；保留原始仓库 commit 和数据 hash。
2. 从 30 个 task 中各抽取 requirement，预注册每条 requirement 的 repository path/line、可运行 test/probe、trace evidence kind 和“不读取 hidden test”的界限。
3. 让两名独立人工标注者（或人工 + deterministic probe）分别记录 evidence span、verdict、evidence sufficiency；Judge 输入只可见公开 evidence。
4. 任务级去重和 split 冻结后再计算 requirement macro-F1、evidence precision/recall 与 risk-coverage。
5. 只有 evidence mapping ≥80%、Gold provenance 可审计，才重开 Gate 1；然后用 50—100 task 做 RQ2 Oracle/Predicted/Random/Shuffled feedback bridge。

# 实验35：方向 A 动作效果验证（Gate 0/1）

本实验对应《20260821_Agent与AgentOps毕设方向重审_三组新方案与Gate实验计划.md》的方向 A 第一周第 1—2 天。目标是审计论文/代码/数据/环境资产，并验证“动作前状态—动作—动作后观察—效果 Oracle—可重放”合同是否能被自动执行。

## 证据边界

- `manifests/` 锁定正式论文页、代码入口、远程 HEAD、许可证和本机运行条件；未能从页面、API、仓库或本机核验的字段写为 `UNKNOWN`。
- `contract/candidate_effect_contract.jsonl` 包含 30 条本轮独立、可复验的构造 smoke 任务，分为 3 个本地环境和多个效果类型。构造任务只证明合同/探针机制，不等于自然 Agent benchmark。
- `results/legacy_candidate_audit.jsonl`（运行脚本生成）仅审计既有 E02/E03 记录；旧记录缺少动作级语义 Gold 的行不能被提升为本轮 Gate 1 Gold。
- 资格审计可以读取 `expected_effect` 作为评测 Gold，但 `scripts/run_gate1.py` 的动作执行和在线探针只读取当前任务的 `pre_state`、`action` 和环境；filesystem probe 采集整个临时目录快照，JSON probe 读取 action 指定的当前文件，CLI probe 运行 action 指定的脚本。Gold 不作为方法输入，只有 observation 冻结后才进入 evaluator。
- 本目录不训练模型、不调用 LLM、不把终局成败或错误词当动作效果 Oracle。

## 运行

在 worktree 根目录执行：

```bash
python3 '实验/实验35_方向A动作效果验证Gate0Gate1/scripts/run_gate0.py'
python3 '实验/实验35_方向A动作效果验证Gate0Gate1/scripts/fetch_syncbench.py'
python3 '实验/实验35_方向A动作效果验证Gate0Gate1/scripts/audit_syncbench.py'
python3 '实验/实验35_方向A动作效果验证Gate0Gate1/scripts/audit_legacy_candidates.py'
python3 '实验/实验35_方向A动作效果验证Gate0Gate1/scripts/run_gate1.py'
python3 -m pytest -q '实验/实验35_方向A动作效果验证Gate0Gate1/tests'
```

`run_gate0.py` 只执行网络 HEAD/页面状态检查、本地仓库只读快照检查和 Docker smoke。`run_gate1.py` 在本实验 `runtime/` 临时目录中运行构造动作，不修改任何外部仓库，并保存每个 task/重复的命令、返回码和 stdout/stderr 摘要。

## 预注册 Gate 判定

Gate 0：5 篇正式方向论文、至少一个可下载/可执行公开入口、可研究许可证或明确风险、至少一条 smoke 命令。缺失许可证不被隐瞒；若主 benchmark 或许可证不能继续使用，Gate 0 为 `CONDITIONAL` 或 `STOP`。

Gate 1：至少 30 个独立 task、至少 3 个 environment、至少 3 个 effect type；稳定 Oracle 比例至少 70%，clean replay 一致率至少 90%。本轮构造 smoke 满足数值门槛才可记为“合同接口 GO”；若自然/公开任务仍没有这些字段，则方向整体只能 `CONDITIONAL`，不可写成双章开题 GO。

## 结果位置

- `results/gate0_asset_audit.json`：Gate 0 页面、远程 HEAD、许可证、环境和 Docker 实测。
- `results/gate1_qualification.json`：30 条构造合同的稳定 Oracle/replay 统计。
- `results/gate1_probe_log.jsonl`：逐任务、逐重复运行日志。
- `tests/test_contract.py::test_online_probes_work_with_gold_stripped`：剥离 Gold 后直接调用三类 online probe 的回归测试。
- `results/legacy_candidate_summary.json` 与 `results/legacy_candidate_audit.jsonl`：旧实验候选字段缺口审计。
- `conclusions/gate0_gate1_conclusion.md`：当前裁决和下一步最便宜动作。

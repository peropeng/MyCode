# 动作效果合同资格报告（Gate 1）

## 1. 统计口径

独立单位是一个独立初始化目录中的一个动作任务；同一 task 的两次 clean replay 不增加 task 数。`expected_effect` 只在动作执行和在线探针完成后用于评测，不能作为方法输入。所有 Oracle 都必须来自可执行确定性检查；本轮没有 LLM 调用。

本轮修订后的 online/evaluator 边界为：online 阶段只读取 `environment`、`pre_state`、`action`；filesystem probe 采集临时目录的完整相对路径/内容快照，JSON probe 读取 action 指定的当前 JSON，CLI probe 运行 action 指定脚本并捕获返回码/stdout/stderr。observation 冻结后，独立 evaluator 才读取 `expected_effect` 比较。3 个 probe 均有 Gold 剥离回归测试。

## 2. 本轮构造合同 smoke

`candidate_effect_contract.jsonl` 有 30 条唯一 task，分布在 3 个环境：`host_filesystem`、`host_json_store`、`local_cli`；共有 13 种效果类型。每条 task 启动两个全新临时目录，执行 action 后运行 deterministic probe：

| 指标 | 结果 | Gate 1 门槛 | 判断 |
|---|---:|---:|---|
| 独立 task | 30 | ≥30 | 通过 |
| environment | 3 | ≥3 | 通过 |
| effect type | 13 | ≥3 | 通过 |
| 两次 clean replay 均匹配 deterministic Oracle | 30/30 = 1.00 | ≥0.70 | 通过 |
| 两次 replay observation 一致 | 30/30 = 1.00 | ≥0.90 | 通过 |
| 构造合同 smoke 子门 | `GO` | — | 仅证明接口与探针可运行 |

完整逐次命令、返回码、stdout/stderr 摘要见 `gate1_probe_log.jsonl`。Docker smoke 也在 runner 中记录为 `PASS`。

## 3. SyncBench 元数据审计

HF SyncBench 300 子集在本机以 revision `d8f957746faa55b414ff93a2ab264e270d474952` 下载；文件 SHA-256 为 `48fda504ccb70ad69f39bfc33aae36f867ccb46a1d8e80785521d2e1d7b3e348`。固定 seed `20260821` 抽取 30 条，不输出 `original_code`、`gold_code`、`initial_error_log`、`gold_summary` 或 `original_summary`。

- 30/30 行拥有 instance/repo/commit/pyfile/test 等元数据。
- 30/30 行只能推导出 `fail-to-pass` 任务类型；没有 Agent action trace。
- `post_observation`、`post_state`、`effect_oracle`、delay 和 replayability 均 `UNKNOWN`/missing。
- 因此 SyncBench 元数据资格数为 30，但稳定 Oracle 数为 0、clean replay 数为 0，不能计入 Gate 1 数值通过。

## 4. 既有实验候选审计

E02 34 行 + E03 preflight 9 行，共 43 个唯一历史候选、8 个仓库；历史记录能证明 checkpoint/replay 或故障终点探针，但没有完整动作级 expected effect/post-state/effect Oracle。43 行全部保留在 `legacy_candidate_audit.jsonl`，qualified rows = 0，不与构造 smoke 合并。

## 5. Gate 1 裁决

- `constructed_contract_gate = GO`：30/3/13/1.00/1.00 均达预注册门槛。
- `direction_gate1_decision = CONDITIONAL`：当前全部合格数值来自构造本地 smoke；公开自然任务的动作前后状态、可执行效果 Oracle 和 clean replay 尚未形成。不能据此宣布方向 A 双章 GO，也不能把 SyncBench 的 gold code/test 结果当作在线输入。

下一条最便宜的实验是从已下载的 SyncBench 30 条中选 3 个仓库，按 commit 建立隔离 Docker worktree，对每条记录执行 test-before → 单个 action → test-after，并记录可审计状态 diff；若至少 30 条最终达到同一阈值，才把方向 Gate 1 从 CONDITIONAL 更新为 GO。

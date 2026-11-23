# 实验55：Gaia2 等价过程验证与局部恢复 Gate0/Gate1

当前裁决：**`STOP_ASSET`**。这不是三次方法失败，也不是对 Gaia2 方向的算法性否定；它是严格资产门停止。Gaia2 的公开场景结构足够丰富，但截至本次冻结审计，公开下载内容没有独立 Agent 轨迹、独立等价/非等价过程 Gold、可执行失败—恢复结果或自然外测，因此不得进入模型/API 方法实验。

## 冻结的两章问题

第一章 RQ1：给定任务约束、公开场景、可见轨迹和环境状态，验证动作 DAG 匹配、状态效果等价、时序/依赖违规，并输出可审计置信；不能读取未来轨迹、隐藏 evaluator Gold 或官方 ARE verifier 的 verdict。

第二章 RQ2：只消费任务级 OOF 的 RQ1 输出和公开 checkpoint/state，预测最小失效闭包与回放起点，并选择替代、重试或安全停止；必须在真实执行后比较 No、Random、Shuffled、Predicted、Oracle 的任务成功、非目标回归和成本。

冻结门槛见 [`protocol/frozen_protocol.json`](protocol/frozen_protocol.json)。

## 实际证据

- 官方 [Gaia2 ICLR 2026 论文页](https://iclr.cc/virtual/2026/poster/10011091) 和 [论文 PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/c26a67e0470774df98c12480ec5d2d7b-Paper-Conference.pdf)确认异步事件、时间约束、噪声、write-action verifier、oracle dependency graph、causality/timing checks。
- 官方 [ARE 仓库](https://github.com/facebookresearch/meta-agents-research-environments)在冻结 commit `7946367413129784139e785ae4c351090002a0bb`，代码许可证为 MIT。该仓库实现了官方验证器和事件/场景运行时，但本次不调用 verifier。
- 官方 [HF Gaia2 数据集](https://huggingface.co/datasets/meta-agents-research-environments/gaia2) revision `78ea3bdbdeec2bdcd6afa5420915d8a22f23ed99` 的 `mini` 文件下载后有 160 行、160 个唯一场景、5 个 capability family；程序化解析 160/160 个事件 DAG 和 160/160 个公开 action DAG。观察到 1,042 个 `OracleEvent` 和 179 个环境事件。
- 160 行中的非空 `execution_trace`、`agent_trace`、`trajectory` 均为 0；因此真实公开 Agent 轨迹严格计数为 0。
- 结构 parser 在 CPU、无 API、无模型下双运行 digest 一致；这只是资产结构 smoke，不是官方环境端到端 replay。官方运行时导入还缺 `inputimeout` 依赖，不能将其包装成执行成功。

详细数字在 [`results/asset_census.json`](results/asset_census.json)、[`results/gold_census.json`](results/gold_census.json) 和 [`results/qualification.json`](results/qualification.json)。

## 论文重叠压力

必须纳入 [Self-Grounded Verification（ICLR 2026）](https://proceedings.iclr.cc/paper_files/paper/2026/hash/3e1fb72d876d634b2ac29e9ac2c937c9-Abstract-Conference.html)、[ReIn（ICLR 2026）](https://proceedings.iclr.cc/paper_files/paper/2026/hash/3144924eaa37b635a79dd382c6d7c825-Abstract-Conference.html)、[ToolEVO（ICLR 2025）](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d8d1d325f822e07d16866780cc23deb2-Abstract-Conference.html)、[Agentic Rubrics（ACL 2026 Long）](https://aclanthology.org/2026.acl-long.697/) 和 [SeekBench（ICLR 2026）](https://iclr.cc/virtual/2026/poster/10007188)。

若未来方案只改变 judge/prompt/calibration，只把 ARE verifier 输出直接用于 recovery，或只是把外部错误诊断接一个 retry，就应裁决 `REJECTED_OVERLAP`。等价状态效果证据、依赖闭包和执行后非目标回归是必须新增且可证伪的部分；本次没有足够 Gold 去测试它们。

## 复现命令

```bash
python3 -m py_compile scripts/*.py tests/*.py
python3 -m unittest discover -s tests -v
python3 scripts/gate_probe.py --input runtime/gaia2_mini.parquet --output results/asset_census.json
python3 scripts/privacy_audit.py
python3 -m json.tool results/qualification.json >/dev/null
git diff --check
```

`runtime/` 包括临时 clone、HF parquet 和 probe 输出，已在 `.gitignore` 中忽略；禁止提交原始大数据、模型、权重、API key 或第三方缓存。

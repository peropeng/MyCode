# 实验 36：方向 B 分层记忆 Gate 0/1

本目录只保存 Gate 0/1 的可复核证据，不把下载的仓库和 249 MB 级数据集提交进 Git。

## 结论先行

- Gate 0：`CONDITIONAL`。已核验 5 篇正式论文、4 个公开代码仓库和 1 个可读取的主动工具调用 benchmark；但只有 AWM 根目录明确 Apache-2.0，HiAgent/G-Memory/AgeMem 根许可证未核实，G-Memory pinned commit 还有语法错误，完整复现没有通过。
- Gate 1：`CONDITIONAL`，不能写成方向 B 已 GO。Mem2ActBench 去重后有 384 个 episode 组，373 个规则上严格依赖历史记忆，人工/规则抽查 40/40 具有跨轮历史依赖和目标工具调用；但 74/384 组不能从一个 shipped session 完整恢复，明确 `stale`/`error-memory` Gold 为 0，数据也没有 `add/retrieve/update/delete` 等主动记忆操作轨迹。
- 最便宜下一步：从已有 30 个 discarded-conflict lineage 中挑 30 组，重组为单一可重放的双 episode tool harness，加入显式 memory write/read/update/delete、stale/conflict/error-memory 注入和确定性 Oracle；只要这 30 组中至少 24 组通过依赖审计且 ≥30 个冲突/错误记忆例可重放，才把 Gate 1 升为 GO。

## 文件导航

- `manifests/paper_repo_dataset_manifest.json`：论文身份、正式链接、仓库 commit、代码/数据许可证、smoke 与复现状态。
- `manifests/asset_smoke_manifest.json`：Docker、各仓库和数据读取命令的返回码与关键日志。
- `scripts/analyze_mem2actbench.py`：只依赖 Python 标准库的字段、去重、工具行为、记忆依赖和冲突证据统计脚本。
- `scripts/run_gate01.sh`：使用本地浅克隆重新生成 `results/`。
- `tests/test_analyze_mem2actbench.py`：3 个最小回归测试。
- `results/mem2actbench_gate1_stats.json`：机器可读总统计。
- `results/mem2actbench_audit_candidates.jsonl`：40 个去重后的抽查候选，仅含 ID/标签/计数，不复制原始对话或个人信息。
- `qualification_report.md`：Gate 0/1 的正式裁决、证据边界、人工抽查与下一步。
- `protocol.md`：数据合同、去重规则、判定定义和复现步骤。
- `logs/`：本轮命令摘要；下载仓库只在本机 `assets/` 保留并由 `.gitignore` 排除。

## 重新运行

先在 `assets/` 下载/浅克隆 manifest 中列出的仓库，然后：

```bash
scripts/run_gate01.sh
python3 tests/test_analyze_mem2actbench.py
```

脚本会对 `Mem2ActBench/qa_dataset.jsonl`、`Mem2ActBench/toolmem_conversation.jsonl` 和 `processed_data/conflict_evolutions.csv` 做完整扫描。没有 API key、GPU 或 LLM Judge 也可以完成本 Gate 的数据审计。

## 重要边界

论文存在不等于代码可复现；README 中的 MIT/Apache classifier 不等于仓库已授予可再分发许可证；`grounding_info`、`evolution_chain` 和 `has_temporal_conflict` 是 benchmark 生成/标注字段，不等于真实系统运行时观测到的记忆治理行为。

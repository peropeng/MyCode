# 实验 39：方向 B 主动记忆合同

本实验是方向 B 的下一轮最低成本资格探针：从实验 36 已核验的
Mem2ActBench `processed_data/conflict_evolutions.csv` 中选取 30 个有
`discarded_source_ids` 的 lineage，重组成 10 个 `stale`、10 个
`conflict`、10 个 `error_memory` 单任务。它是 **constructed/recomposed
feasibility harness**，不是自然 benchmark，也不是分层记忆方法的结果。

## 结论

- 30/30 任务通过确定性的构造干预依赖判据；这不是自然任务或真实 Agent 依赖；
- 30/30 clean replay 通过；
- 3 类 intervention 标签各 10 项，删除或篡改 memory 都改变可观测工具参数和结果；三类使用同一 policy/store/evaluator，不是三种算法效果；
- 构造合同子门槛为 `GO`，但方向 B 总 Gate 1 仍为 `CONDITIONAL`。

原因是 discarded lineage 的分类由本 harness 注入，并非 Mem2ActBench 的
运行时 stale/error Gold；固定 policy 对可见 `fact_text` 求指纹，evaluator
又用同一事实指纹判定，所以 30/30 只说明合同能区分干预条件，不能声称真实
Agent 记忆依赖或三类治理算法效果。实验 36 已发现 shipped
`toolmem_conversation` 不包含这 30 个 discarded source 的完整 session；该缺口
在每个 manifest task 的 `source_trace` 中显式记录，不能据此声称自然主动记忆治理。

## 文件

- `manifests/task_manifest.jsonl`：30 个可追溯任务；含 source episode、CSV
  lineage 行、record 行、session/turn 引用（缺失处明确标记）、重组规则、Gold
  和许可证状态。
- `scripts/build_manifest.py`：从 pinned Mem2ActBench checkout 重建 compact
  manifest，不复制完整会话。
- `scripts/run_contract.py`：标准库实现的 MemoryStore、固定 agent policy、三
  条件重放、Gold/online 隔离、依赖/重放/篡改判据。
- `scripts/run_gate1.sh`：从已提交 manifest 重建 `results/`。
- `results/contract_results.jsonl`：逐任务机器可读证据。
- `results/contract_summary.json`：汇总统计和 Gate 裁决；`source_trace_documented=30/30`，但 `complete_selected_source_session_trace=0/30`。
- `results/qualification_report.md`：面向论文方向审查的边界说明。
- `tests/test_contract.py`：隔离、确定性、类别/trace 和 mutation 回归测试。

## 复现

已提交的 manifest 足以从干净结果目录重跑，无需下载大数据：

```bash
rm -rf results
scripts/run_gate1.sh
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/build_manifest.py scripts/run_contract.py
```

如需从原始 pinned checkout 重建 manifest（该 checkout 被 `.gitignore` 排除）：

```bash
python3 scripts/build_manifest.py \
  --source-root assets/Mem2ActBench \
  --output manifests/task_manifest.jsonl
```

`assets/` 不提交仓库或大数据；source commit、许可不确定性和上游来源见
`manifests/task_manifest.jsonl` 与 `protocol.md`。

## 不得外推

本实验不提供 Gate 3 utility 对比，不提供 RQ1/RQ2 效应量，不证明真实 agent
能可靠管理记忆，不证明 discarded lineage 是自然 stale/error memory，不把
stale/conflict/error_memory 当作三种治理算法，也不支持两章论文 GO。后续若
继续，必须用 license-cleared 的真实/独立标注轨迹替换或补充当前 constructed
intervention。

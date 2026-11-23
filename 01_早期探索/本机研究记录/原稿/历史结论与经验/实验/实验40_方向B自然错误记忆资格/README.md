# 实验 40：方向 B 自然错误记忆/冲突资格审计

## 裁决

本轮 **Gate 1 = STOP**，不是方向 B 的两章 GO。审计了四个论文官方/作者官方入口：

| 资产 | 下载/代码 | 可见数据字段 | 自然有害记忆后果 |
|---|---|---|---|
| ACL 2026 *How Memory Management Impacts LLM Agents* | 代码浅克隆；官方 Drive 的 `memory.zip`、`metrics.zip` 成功下载 | 23,388 条 driving memory 只有场景、历史/未来轨迹、目标和 objects；无 retrieval/use、工具调用、任务结果、error Gold | 0 个合格案例；论文声称 error propagation，但仓库没有结果轨迹，且 memory 与 GT token 交集为 0 |
| Fine-Mem | 官方仓库浅克隆，Apache-2.0 | 只有 README/LICENSE；论文描述的 chunk QA、INSERT/UPDATE/DELETE/SKIP 与 EARA 轨迹未随仓库发布 | 0 个 |
| AgeMem | 官方仓库浅克隆 | 代码支持 6 类 memory/context 工具，数据须外部 HotpotQA；未提供自然 stale/conflict/error 运行轨迹 | 0 个 |
| Mem2ActBench | 官方仓库完整数据已读 | 400 QA、2,029 session；有历史对话和 source tool result，但没有 memory operation/retrieval trace，也没有 stale/error Gold；冲突字段是构造元数据 | 0 个 |

`results/natural_case_manifest.jsonl` 对 Mem2ActBench 去重后的 384 个 episode 逐项列出字段证据；`results/audit_summary.json` 给出 Gate 门槛和四项资产状态。未把 L4、`has_temporal_conflict`、discarded lineage 或被动 QA 当成自然有害后果。

ACL 的 pickle 只由 `scripts/run_binary_audit_docker.sh` 在固定 NumPy 的 Docker 沙箱内读取；宿主 `audit_natural_assets.py` 永远不反序列化。沙箱输出必须带输入文件 SHA256、image ID 和 `--network none --read-only --cap-drop ALL --security-opt no-new-privileges:true --pids-limit 128` 证明，否则主审计只保留文件存在性和 `null` 计数。

## 最低成本下一步

只有在取得许可清楚、跨独立 session 的自然轨迹，并同时包含 `memory content → retrieve/use → target tool call → tool/task result → independent stale/conflict/error label` 后，才值得重开 Gate 1。若作者不能提供这类可审计数据，方向 B 应停止两章投入，保留为“长上下文记忆驱动工具调用”子题。

## 复现

```bash
scripts/run_binary_audit_docker.sh assets results/binary_audit_sandbox
python3 scripts/audit_natural_assets.py --binary-summary results/binary_audit_sandbox/acl_binary_summary.json
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/audit_natural_assets.py
git diff --check
```

下载的仓库、压缩包和 pickle 全部位于 `assets/`，不会提交进 Git。

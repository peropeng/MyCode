# 实验58：AFTraj 外测资产恢复与资格 Gate0

本目录只做 AFTraj 外部测试资产恢复、版本/许可追踪、字段契约和任务级独立性审计。它不是 AgentForesight 方法复现，也不产出模型增益或两章开题 GO。

## 官方来源与冻结口径

- 论文配套代码：[ZBox1005/AgentForesight](https://github.com/ZBox1005/AgentForesight)，冻结提交 `af549083fcc6c3eff4ccc558534515e46ca0578e`，仓库 `LICENSE` 为 MIT。
- 数据：[ZBox008003/AFTraj](https://huggingface.co/datasets/ZBox008003/AFTraj)，revision `main`，数据卡声明 CC BY 4.0。
- 论文：[AgentForesight: Online Auditing for Early Failure Prediction in Multi-Agent Systems](https://arxiv.org/abs/2605.08715)。
- 原始 parquet、官方仓库和运行时均放在被 `.gitignore` 忽略的 `third_party/` 下，不提交到本仓库。

## 运行

需要一个带 `pyarrow` 的 Python 运行时（本机使用 Codex bundled Python）。先按官方 URL 下载/检出资产，再运行：

```bash
cd 实验/实验58_AFTraj外测资产恢复_Gate0
python scripts/audit_aftraj.py \
  --data-dir ../../third_party/data/AFTraj \
  --repo-dir ../../third_party/AgentForesight \
  --output-dir results
```

脚本是确定性的；`results/artifact_hashes.json` 列出其它 JSON 产物的 SHA-256。用相同原始字节运行两次，两个结果目录的 `artifact_hashes.json` 应完全一致。

## 资格边界

Gate0 仅在以下事实均通过时报告 `GO_ASSET_ONLY`：官方提交可定位、三份数据文件哈希/大小与官方入口一致、2,276 条计数和 11/7 列 schema 对齐、官方 test ID 可解析、unsafe 的 `mistake_step` 在范围内且与 `mistake_agent`/turn role 对齐、以及 group split 没有外测任务泄漏到 clean train。任何这些硬条件失败都报告 `STOP_ASSET`。

当前实际审计还会列出但不把下列事项硬改成通过：

- `unsafe_source` 实际为 `injected=728`、`diagnosed=386`；按数据卡分别解释为受控注入与多评审诊断/自然失败来源。
- 任务级分组使用历史合同 `sha1(lowercase + collapse whitespace + UTF-8(task))[:16]`；预期为 1,381 组，其中 735 组同时有 safe/unsafe。
- `splits_test.json` 预期为 169 safe + 163 unsafe；外测组内的非 test 行必须从训练侧剔除。
- `gold_answer` 只作为标签/数据 provenance，绝不能作为特征；脚本列出缺失/歧义，但不会把它们伪装成方法 GO。官方卡允许 process-style 场景为空；本版实际共有 203 条空 answer（safe agentic 104、unsafe agentic 95、unsafe coding 4），其中没有官方 test 行。
- `conv_id` 也只作索引；实际 ID 含 `safe`/`unsafe`/`injected`/`diagnosed` 等标签或来源 token，严禁送入模型。
- 在线方法只能消费当前可见 `turns[0:k]`；完整轨迹中的未来 turn、`mistake_*`、`unsafe_source`、`gold_answer` 和全轨迹 `num_turns` 均在禁止字段审计中明确列出。

查看 `results/gate_summary.json`、`results/dataset_statistics.json`、`results/external_test_manifest.json`、`results/group_split_manifest.json` 和 `results/forbidden_field_audit.json` 获取机器可读证据。`results/external_test_manifest.json` 中的 conv ID 仅用于锁定/重取样本，不是模型特征。

## 已知数据歧义

本 Gate 会诚实列出 203 条 `gold_answer` 缺失（官方卡所述 process-style 空 answer，其中 4 条为 unsafe coding）、五个任务组存在 answer 值差异，以及 95 条 diagnosed 的可选 `mistake_reason` 为空；这些不影响 1,114 条 decisive-step/agent 的唯一性和 turn-role 对齐，但如果后续实验需要 answer supervision，必须预注册排除/处理规则。另有 15 条 decisive turn 的 `action` 与 `content` 同时为空，仅 `thought` 非空，索引和 role 仍然可对齐。

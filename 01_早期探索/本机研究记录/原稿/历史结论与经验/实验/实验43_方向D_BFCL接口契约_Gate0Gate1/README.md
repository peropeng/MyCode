# 方向 D：BFCL 接口契约鲁棒性 Gate0/Gate1

本实验对官方 Berkeley Function Calling Leaderboard（BFCL）的公开任务与公开模型响应做资格审计，目标是判断“接口契约鲁棒性→修复”是否具备可复现的后续实验入口。结论分成两层：Gate0 资产/协议可行性为 **GO**；Gate1 的双 replay 稳定性为 **GO**。这不是“修复有效”或“可直接支撑两章论文”的结论，后续仍需独立的在线诊断、修复和对照实验。

## 当前结论

| 项目 | 结果 |
| --- | --- |
| 预注册家族 | `multi_turn_base`、`multi_turn_miss_func`、`multi_turn_miss_param`、`multi_turn_long_context`，各有官方任务、官方 evaluator 和公开响应 |
| 资产审计 | 4/4 任务集与响应集严格按 `id` join；每集 200 行；固定 SHA256 与来源已记录 |
| Gate0 probe | 20/20 双 replay 一致、0 harness error、每家族 5/5 join，GO |
| Gate1 | 120/120 入选，四家族各 30；`total_unique_structure_signatures=120`；120/120 双 replay 一致；0 harness error；每家族均 30/30，GO |
| 公开响应的 clean `VALID`（两次均为 VALID） | 75/120（base 22、miss_func 14、miss_param 22、long_context 17） |
| 解释 | Gate1 证明“公开 response + 官方 evaluator 的重放契约稳定”，不证明模型质量、修复收益或跨模型泛化 |

`MODEL_FORCE_TERMINATED`（响应 turn 数与官方 reference 不同）和 `MODEL_EVALUATION_INVALID` 是公开响应的模型/评估结果，不计作 harness error。官方 evaluator 异常单独记为 `TEST_HARNESS_ERROR`；本次为 0。

## 固定来源与版本

完整来源、commit、下载 URL、行数与 SHA256 位于 [`manifests/source_manifest.json`](manifests/source_manifest.json)。关键锁定项为：

- 官方代码仓库 `ShishirPatil/gorilla`，`main` 的 `git ls-remote` commit `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`。
- PyPI `bfcl-eval==2026.3.23`，wheel SHA256 `3bb6dfa5f0c68ad403c9ec50b00db2bb3b4cc9b38ab1ff33f48fe30d853d3a0a`，Python `>=3.10`。
- 官方结果索引 `HuanzhiMao/BFCL-Result`，`main` 的 `git ls-remote` commit `6830ed13035c0cfee9aa7a9a0ffed70f10b3dd50`。响应只通过该固定 commit 的 raw URL 下载到 `runtime/public_results/`；该目录被 `.gitignore` 忽略，不提交原文。
- 结果仓库固定 commit 没有可确认的根许可证，因此本提交采用最小的 metadata-only 边界：只提交哈希、计数、公开字段 schema、选择摘要和派生统计，不再分发原始 response、prompt、state、inference log、Gold 或 score 文件。

四个预注册家族映射到官方 canonical 文件：`BFCL_v4_multi_turn_{base,miss_func,miss_param,long_context}.json`。没有用替代命名偷偷替换家族。

## 选择和去重

选择完全 deterministic：按 `sha256(public_task_id)` 升序扫描。任务选择的结构签名为：

```text
sha256(canonical_json({
  question,
  initial_config,
  missed_function,
  involved_classes: sorted(involved_classes),
  path
}))
```

Gate1 先按上述顺序依次处理四个家族，并维护一个全局 `seen_signatures`；因此不仅家族内去重，而且跨家族也去重。最终 `gate1_manifest_*.jsonl` 共 120 行、120 个唯一 `task_id_sha256`、120 个唯一 `structure_signature_sha256`。manifest 不保存原始 task ID，也不保存 signature preimage。

## 在线/离线边界

冻结给未来 diagnosis/repair policy 的投影只有 `id`、`result`（提交 manifest 中进一步只保留 `task_id_sha256`、schema 摘要和派生指标）。`inference_log`、token/latency 元数据、task 的 `initial_config`/state、Gold、`possible_answer`、evaluator answer、未来 turn 和离线 evaluator 的 coarse error class 都不进入 online policy。

官方 `possible_answer` 只在投影冻结之后由独立的离线 evaluator 阶段读取，用于重放判定；它不写入提交产物，也不作为诊断/修复特征。该边界是本实验的安全前提，Gate2 若实现在线修复必须继续保持它。

## 目录和产物

- [`contract/protocol.json`](contract/protocol.json)：预注册协议、门槛、去重和 online boundary。
- [`scripts/audit_gate0.py`](scripts/audit_gate0.py)：来源/版本、家族资产、schema、严格 join、hash 和 metadata-only 边界审计。
- [`scripts/run_replay.py`](scripts/run_replay.py)：固定选择、全局去重、官方 decoder/evaluator 双 replay；相对输出路径会解析到本实验根目录。
- [`manifests/`](manifests/)：只含哈希、计数、布尔和必要公开 schema 的选择/来源清单。
- [`results/gate0_summary.json`](results/gate0_summary.json)、[`results/gate0_probe.json`](results/gate0_probe.json)、[`results/gate1_summary.json`](results/gate1_summary.json)：机器可读结果。
- [`qualification_report.md`](qualification_report.md)：可行性判断、失败类别、边界与后续 Gate2 计划。
- [`command_log.md`](command_log.md)：实际运行命令和结果。

`runtime/` 只放下载源、wheel、venv、官方只读 checkout 和缓存，全部忽略，不应提交。不要在宿主反序列化不可信 pickle；本实验只读取官方 JSON/JSONL。

## 重跑

先进入本实验目录（再按 `source_manifest.json` 的固定 URL 下载 runtime 资产，并安装锁定 wheel/依赖），然后执行：

```bash
cd 实验/实验43_方向D_BFCL接口契约_Gate0Gate1
runtime/venv312/bin/python -m pip install pytest
runtime/venv312/bin/python scripts/audit_gate0.py
runtime/venv312/bin/python scripts/run_replay.py \
  --sample-size 5 \
  --output results/gate0_probe.json \
  --manifest-output manifests/gate0_probe_manifest.jsonl
runtime/venv312/bin/python scripts/run_replay.py \
  --sample-size 30 \
  --output results/gate1_summary.json \
  --manifest-output manifests/gate1_manifest.jsonl
runtime/venv312/bin/python -m pytest -q tests
```

当前执行使用 Python 3.12 venv，安装官方 wheel 后补齐官方 import/evaluator 所需的公开依赖；没有发起 API 请求，也没有生成模型响应。运行脚本前应确认四个固定 raw 文件和官方 task/Gold 文件已按来源清单放入 `runtime/`。

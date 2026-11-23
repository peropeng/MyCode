# 实验73：AgentForesight 公平在线基线资格

本实验只恢复 AFTraj 官方 test split 上的公平 DeepSeek-V4-Flash 在线 Base，
不复现 AgentForesight-7B，也不与论文发布的 DeepSeek-V4-Pro 数字作公平优劣比较。

## 关键审计结论

官方 `inference/infer_api.py` 在 `rec.label == "safe"` 时走一次 `audit_full`，
否则走 `audit_incremental`。这把 Gold label 用于在线调用调度，并造成不等预算，
因此静态审计结果固定为 `HARNESS_INVALID`，不计为方法失败，也不用于基线分数。

公平 Base 对 safe/unsafe 完全使用同一策略：每一步只把当前 prefix 和工具定义交给
官方 prompt/parser；首次官方 parser 返回合法的非负 step 就报警，否则观察下一步，
直到结束后返回 SAFE。评估阶段才读取 label 和 `mistake_step`。

## 冻结流程

```bash
python3 audit_official_runner.py \
  --source /path/to/AgentForesight/inference/infer_api.py \
  --output results/official_runner_audit.json

python3 build_manifest.py \
  --data-dir /path/to/AFTraj \
  --output results/manifest.json

python3 -m unittest discover -s tests -v
```

12 条 canary 通过后，使用仅从 macOS Keychain 注入凭据的 launcher：

```bash
python3 secure_launcher.py runner.py run --mode canary \
  --data-dir /path/to/AFTraj \
  --official-repo /path/to/AgentForesight \
  --manifest results/manifest.json \
  --ledger results/canary.ledger.jsonl \
  --output results/canary_result.json

python3 runner.py estimate \
  --canary-result results/canary_result.json \
  --manifest results/manifest.json \
  --output results/full_call_estimate.json
```

只有 `PASS_CANARY` 且估算调用数不超过 3000 才允许启动一次 332 条全量：

```bash
python3 secure_launcher.py runner.py run --mode full \
  --data-dir /path/to/AFTraj \
  --official-repo /path/to/AgentForesight \
  --manifest results/manifest.json \
  --ledger results/full.ledger.jsonl \
  --output results/full_result.json
```

ledger 是 append-only 的逐 prefix slot 记录；每个 slot 最多一次网络调用且不重试。
凭据不写入 prompt、结果、ledger 或日志。canary/成本门失败是资格 STOP，不是算法
NO-GO。

## Sol 恢复执行结果（2026-08-22）

全新的 `canary_sol_recovery` 不复用前三次尝试的任何 slot。12 条轨迹全部完成，
119/119 次请求传输成功，但只有 100/119 通过锁定的官方 parser（成功率
84.03%）。因未达到 100% parse gate，结果为 `STOP_CANARY`；未估算全量调用数，
也未运行 332 条 full Base。

证据保存在 `results/canary_sol_recovery.ledger.jsonl` 和
`results/canary_sol_recovery_result.json`。ledger 包含 1 条 meta、119 组成对的
started/finished 记录，无未完成 slot、19 个 parser-invalid 响应的 hash 均不同。
独立凭据扫描确认 Keychain secret 在两个 artifact 中的出现次数均为 0。

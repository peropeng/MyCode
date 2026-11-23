# 实验64：逐轨迹绝对评分（开发资格门）

这是一个 position-invariant evaluator 的开发门。它把同一行的两个 agent execution
分别独立打绝对分，再和调用数、completion cap 相等的 pairwise original+swap 聚合
比较。实验目标是机制可行性，不是论文官方数字复现，也不把结果直接写成两章 GO。

当前提交包含：

* 冻结协议 `PROTOCOL.md` 与机器可读 `results/preregistered_plan.json`；
* 开发/确认资产边界 `results/asset_manifest.json`；
* 只保存摘要的 `runner.py`、append-only ledger 与 parser；
* 分离的 canary/dev launcher；
* 离线 mock 和覆盖安全边界的单元测试。

## 重要限制

开发集为 `planning_multi_hard` 73 行/41 UUID，确认集为实验63 manifest 中的
`planning_single_hard` 与 `tool_irrelevance` 元数据。运行器不读取确认集 JSONL；本轮
不执行真实 API 请求。Mock 结果只能证明程序链路，不是评估证据。开发门即使通过也
只允许主线程另行批准一次确认实验，且 `chapter_go` 始终为 false。

## 运行

离线计划与 mock：

```sh
python3 runner.py --mode plan --output /tmp/exp64_plan.json
python3 runner.py --mode mock \
  --ledger /tmp/exp64_mock_ledger.jsonl \
  --output /tmp/exp64_mock.json
```

安全 launcher 仅作为未来 live 的保护层；canary 永远只取
`planning_multi_easy.jsonl` 的固定物理 source line 1，并核对完整文件 hash、选中行
hash 和 UUID hash：

```sh
scripts/safe_launch_canary.sh
EXP64_DEV_CONFIRMATION=ALLOW_EXP64_DEV_73 scripts/safe_launch_dev.sh
```

launcher 会从 Keychain 临时注入 key；不要在 shell 中设置、打印或保存 API key。
本提交的验收只运行离线命令和 fake transport 测试，不运行 live launcher。合同测试
会通过 `EXP64_CANARY_MOCK=1` 调用真实 canary launcher 路径，证明只生成 4 slots、
不读取 Keychain 且网络请求为 0。

Live canary 只有在 4/4 requests 都成功解析、两臂 terminal/network counts 均为 2/2、
ledger 没有 retry/duplicate/ambiguous/issues/unknown/missing 字段、且 prompt/raw 审计
通过时才返回 `CANARY_PASS_TRANSPORT_AND_PARSE`；否则返回 `CANARY_STOP` 并以非零状态
退出。Mock 始终返回 `CANARY_SMOKE_ONLY`。

## 结果解释

真实开发结果必须同时满足协议中的相对收益、UUID 聚类 bootstrap、解析覆盖、ledger
完整性和 prompt 审计；否则结论是 `STOP_POINTWISE_ABSOLUTE_SCORE_DEV`。Mock 返回
`MOCK_ONLY_NOT_ACCURACY`，永远不能变成 GO。

## 固定 live canary（唯一一次）

2026-08-22 已经通过安全 launcher 执行唯一一次固定 canary；没有执行 dev，也没有
重跑或重置 ledger。使用 `planning_multi_easy.jsonl` 物理 source line 1，严格 4 个
requests（PAIRWISE original/swap、POINTWISE chosen/reject），模型为
OpenCode Go `deepseek-v4-flash`，temperature=0、retry=0。

结果为 `CANARY_PASS_TRANSPORT_AND_PARSE`：

* network requests 4；PAIRWISE/POINTWISE 各 2；transport calls 4；
* parsed 4/4，两臂 parsed-call coverage 均 1.0；
* expected/unique/completed slots = 4/4/4；terminal counts = 2/2；
* retry、duplicate、ambiguous、unknown、issues、missing terminal fields、非法
  network delta 全为 0；prompt/raw 审计通过。

脱敏原始证据保存在 `results/canary_result.json` 与
`results/canary_ledger.jsonl`；其中只有 hash、长度、解析结果和安全 transport metadata，
不含 key、raw prompt、raw response 或 reasoning。

## 唯一 live dev 尝试：AMBIGUOUS

2026-08-22 获批准执行唯一一次 live dev。进程在 21 个 terminal 事件后，于
`row_index=5 / PAIRWISE / swap` 的 durable `STARTED` 事件后中断。因此
`results/dev_ledger.jsonl` 有 43 条事件（22 STARTED、21 terminal），该 slot 永久
标记为 AMBIGUOUS，未进行重发、重跑、删除或重置；没有完整 `dev_result.json`。最终 gate decision 为
`AMBIGUOUS_DEV_INTERRUPTED`，`dev_go_candidate=false`、`chapter_go=false`；准确率、
最强基线、相对提升和 bootstrap 均不计算。详见 `results/gate_decision.json`。

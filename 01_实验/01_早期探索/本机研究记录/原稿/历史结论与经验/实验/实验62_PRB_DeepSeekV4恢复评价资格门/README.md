# 实验62：Plan-RewardBench × DeepSeek V4 Flash 资格复验

本实验只判断 OpenCode Go `deepseek-v4-flash` 是否能按 Plan-RewardBench
`robust_recovery` 的官方协议完成固定评委请求。它是 cross-backend
qualification，不是论文使用的 DeepSeek-V3.2-Exp/GPT-4o 官方数值复现，也
不直接产生任何章节 GO。

## 固定资产与协议

- 官方仓库 commit：`ffe6fbe923bddf6deea54f92d3ffe2f45f38de54`。
- `robust_recovery.jsonl`：361 rows、121 UUID，源文件只读，SHA-256 记录在
  `results/asset_manifest.json`。
- prompt、trajectory formatting、A/B swap 和 winner marker 优先级与官方
  `eval/evaluate_benchmark_final.py` 对齐。Go 适配仅替换为 OpenAI-compatible
  SSE、`max_completion_tokens=256`、`top_p=1`、`reasoning_effort=none`，并将
  失败设为 fail-closed、retry=0。
- Key 只由 `scripts/safe_launch.sh` 从 macOS Keychain
  service `codex-opencode-go`、account `$USER` 注入；结果和日志不含 key、prompt、
  reasoning 或 raw response。

## 四种模式

```bash
python3 runner.py --mode plan --output results/protocol_plan.json
python3 runner.py --mode mock --output results/mock_result.json
python3 runner.py --mode canary --live --output results/canary_result.json
python3 runner.py --mode full --output /tmp/full.json   # fail-closed
```

经独立双重确认后，full 只能由固定 launcher 启动；本实验已按授权执行过一次，
不得再次运行：

```bash
PRB_V4_FULL_CONFIRMATION=ALLOW_PRB_V4_FULL_361 ./scripts/safe_launch_full.sh
```

如需修订指标定义，只能使用已落盘的四条脱敏记录离线重算，不能重新调用模型：

```bash
python3 scripts/recompute_canary.py \
  --input results/canary_result.json \
  --output results/canary_result.json
```

完整评测只可由新的 `scripts/safe_launch_full.sh` 触发（需调用者显式提供
`PRB_V4_FULL_CONFIRMATION=ALLOW_PRB_V4_FULL_361`）；它固定 722 slots、
4 workers、seed `20260822`、retry 0，并使用 append-only
`results/full_ledger.jsonl`。每个 slot 在请求前 durable 写入 `STARTED`，完成后
写入 `PARSED`/`TRANSPORT_FAILED`/`PARSE_FAILED`；已有 `STARTED` 但没有 terminal
event 的 slot 标为 `AMBIGUOUS`，恢复时绝不重发。

真实 full 的资格门为：
parsed coverage ≥0.95、official mean ≥0.60、UUID-cluster bootstrap CI lower
>0.50、position gap ≤0.10、underlying-choice swap consistency ≥0.60，且 slot
唯一性/重试/泄漏/持久化合同全部通过。通过只记
`QUALIFIED_CROSS_BACKEND_EVALUATOR`，`chapter_go` 仍为 `false`；mock 只记链路
状态，不能替代真实资格结果。

本次唯一授权的 full run 已完成 722/722 个 logical slots（实际 HTTP 722、
retry=0、重复=0、ambiguous=0），712 parsed、9 parse failures、1 transport
failure，parsed coverage=0.98615。官方均值为 0.74368，UUID-cluster bootstrap
95% CI=[0.70275, 0.78526]；original/swap position score 分别为 0.87746/0.61064，
signed gap=absolute gap=0.26682，cluster bootstrap CI=[0.21350, 0.32235]。
underlying-choice swap consistency=0.69516，both-positions-correct rate=0.54416。
因此仅 position-gap 门失败，结果为 `STOP_PRB_V4_QUALIFICATION`；这不是论文
DeepSeek-V3.2-Exp/GPT-4o 的官方数值复现，也不构成章节 GO。`strict_accuracy`
为 0.67978，仅作为把 Tie 视为 0 的非官方诊断指标。

默认建议先运行 `plan`、离线测试和 `mock`。真实 canary 固定取 stable-sort
后的两个 distinct UUID，每个只取一行，original+swap，严格 4 个 HTTP 请求、
零重试；所有请求完成后才进行本地 position deblind。`full` 需要独立的确认
token 和 launcher sentinel，且同一 ledger 上任何未完成 STARTED 都不得重发。

## 当前门

`results/gate_decision.json` 记录以下状态：

- `PENDING_FULL_361_PAIR_RESULTS`：四个 canary 请求均完成并可解析，但完整361
  对尚未执行；或
- `FAIL_CANARY_TRANSPORT_OR_PARSE`：传输/解析/请求数合同失败；或
- `STOP_PRB_V4_QUALIFICATION`：full 已完成但至少一个预注册资格门失败；或
- `QUALIFIED_CROSS_BACKEND_EVALUATOR`：full 已完成且全部资格门通过。

mock 的 `SMOKE_CHAIN_PASS_NOT_ACCURACY` 仅是链路证据。`chapter_go` 永远为
`false`，不把 canary 资格结果冒充两章 GO。

本次真实 canary 已按安全 launcher 执行一次：4/4 HTTP 请求、4/4 严格解析、
零重试、零传输/解析失败；解盲后的官方 `official_mean_score` 为 0.75，两个完整
swap pair 中 1 个底层选择 position-consistent（0.5），且 1/2 pair 两个 position
均正确（`both_positions_correct_rate=0.5`）。这里的 0.75 是官方
`official_mean_score`；本次无 Tie，因此与非官方 `strict_accuracy` 恰好相同。
若出现 Tie，官方分数按 0.5，strict 指标不得代替官方均值。完整运行及其
脱敏 ledger/full_result 的 SHA-256、门检查和审计证据见
`results/gate_decision.json`、`results/full_result.json` 与
`results/full_ledger.jsonl`；所有输出继续保持 `chapter_go=false`。

# Pair3 离线 fail-closed harness

本目录冻结 Agent-as-a-Judge 与 Plan-RewardBench 的本地复现输入，提供一个**不调用网络/API**的 Pair3 GO 门 harness。它只读取显式传入的本地资产，检查数据合同、生成可审计的运行计划，并在缺少真实评分结果、密钥或资产校验信息时保持 `PENDING`，绝不把 `PENDING` 推断为 `GO`。

## 范围

- DevAI：55 个 task、365 条 requirement（以本地资产实际计数为准）。
- Plan-RewardBench：`robust_recovery` 的 361 个 pair、121 个 uuid，以及 A/B swap 配对合同。
- 三个预注册 seed、paired bootstrap、position consistency 聚合器。
- OpenAI-compatible transport 接口只用于离线契约测试；真正请求默认拒绝，API key 只从环境读取且永不写入日志。

本轮新增两条独立路径：

- `offline_repro.py` 严格按 task 文件与 `requirement_id` 配对官方 GPT-Pilot
  `gray_box`/`human_as_a_judge` 资产。human 仅作参照，不是把 agent 输出当 Gold；
  preferences 单独计数且不混入 requirement agreement。
- `pilot_runner.py` 提供四条件 `Base/A/B/A+B` 的 4-UUID 小样本链，每个
  condition/position/seed 一次 final judge；A/A+B 各增加一次 selector。默认
  offline；只有 `--live --max-uuids 4` 才允许网络，推荐通过
  `launch_live.sh` 从 Keychain service `codex-opencode-go` 注入凭据。
  selector 只看 index/role/action/长度/短 preview 的 step catalog，随后本地
  read 选中的完整 steps；selector 失败绝不回退到全轨迹。所有调用结束后才用
  PRB chosen/reject 做本地解盲（original=A、swap=B，Tie
  算错）；A/A+B selector+final 还要通过 16k/slot、均值不超过 Base 1.10x 的
  输入 token fairness gate。live 记录并校验每次 HTTP status、finish_reason、
  usage、SSE 完整结束；结果只保留 winner、response hash/长度，不保留 reasoning
  原文。fairness 优先使用 live `usage.prompt_tokens`，缺失才估算，并在结果中
  标记 measurement source；smoke 的 stub 评分字段明确标为非效应证据。

## 快速检查

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile pair3_harness.py prepare_assets.py
python3 pair3_harness.py verify --manifest manifest.json
python3 offline_repro.py --output results/offline_reproduction.json
python3 pilot_runner.py --output results/pilot_pending.json
python3 pilot_runner.py --smoke --output results/pilot_smoke.json
```

`verify` 只做离线资产与合同检查。首次运行前可用 `prepare_assets.py` 从只读源目录生成 `manifest.json`；若源资产缺失、数量不符或 hash 尚未冻结，命令以非 GO 的 `PENDING` 结果退出/报告。

## 当前状态

`PENDING`。当前官方 judgment 快照实测 55 task、366 requirement，而冻结合同要求 365；离线复现因此只能报告 measured alignment/trend，不能升级为 GO。pilot smoke 只验证执行链、JSON parse 与 position 对齐，绝不代表 accuracy 或章节 GO。

真实 4-UUID pilot 已按固定命令执行一次：
`./launch_live.sh --output results/pilot_live_4uuid.json`。本次固定
`Base/A/B/A+B × original/swap × seeds 11,22,33`，完成 96 个 final slots 与
48 个 selector slots；实际 HTTP 为 judge 94、selector 48，未重试。94/96 个
final 结果通过严格 JSON parser（97.9167%），其中 2 个 A selector 失败后按
fail-closed 跳过对应 final slot，position alignment 仍为 true。

调用结束后才做本地解盲：整体 pair accuracy 为 74/94 = 0.787234；按条件为
Base 18/24 = 0.750000、A 18/22 = 0.818182、B 18/24 = 0.750000、A+B
20/24 = 0.833333。完整 original/swap 对中 27/47 同时正确，swap consistency
= 0.574468。transport usage 覆盖 140 次调用，2 次 selector 失败回退估算；
selector/judge latency（min/mean/max ms）分别为 1150.946/3583.948/34740.061
与 1640.650/6662.244/52186.994。

fairness gate 未通过：measurement source 为
`mixed_transport_usage_and_estimate`，最大 final-slot 输入为 17,956 tokens，
超过预注册 16,000 上限（条件均值 A/Base=0.997940、A+B/Base=1.068375，仍不替代
硬上限）。离线捕获的同构 144 条 prompt 中，`chosen`、`reject`、`_lcp_bucket`
均为 0 命中；pilot 结果不保存 prompt/reasoning/secret。该 pilot 保持
`PENDING_NO_API_RESULTS`，`chapter_go=false`，不作章节效应结论。

冻结 benchmark 实测为 DevAI 55 task / 365 requirement，以及 PRB `robust_recovery`
361 pair / 121 uuid；两仓库 commit 分别为 `43c2fa7b...9dd0` 和
`ffe6fbe9...de54`。PRB 三 seed、每 pair 原序与 swap 各一次时，仅最终
pairwise judge 就至少需要 `361 × 2 × 3 = 2166` 次逻辑请求；Agent-as-a-Judge
55 task 的入口调用至少 165 次，实际 locate/read/retrieve/judge 工具循环会更多。
因此凭据就绪后仍应先做单条 transport smoke 和小样本成本审计，再启动完整运行。

## 离线安全边界

- `PAIR3_OFFLINE=1`（默认）时 transport 直接 fail-closed，不创建 socket、不发 HTTP 请求。
- 不接受命令行或配置文件中的 key；兼容 transport 仅从环境变量读取 key，日志使用固定脱敏值。
- live pilot 必须同时显式提供 `--live --max-uuids 4`；不存在隐式联网或 retry。
- `launch_live.sh` 只从 Keychain service `codex-opencode-go` 读取 secret，不写入日志/结果文件。
- 资产源使用绝对路径或显式 CLI 参数，不从网络下载，不修改源目录。

详见 [PROTOCOL.md](PROTOCOL.md)。

# 实验 59：HiAgent / AWM 跨后端机制迁移复现

本实验是 Pair1 STOP 后的备用路线。它只回答一个窄问题：在同一个
OpenCode Go `deepseek-v4-flash` 后端、相同任务顺序和固定随机种子下，两个公开
记忆机制是否仍有方向性增益。它不是原论文数值复现，也不是第 1/2 章 GO。

## 两个独立子复现

| 子复现 | 公共任务 | Base | 方法臂 | 主指标 |
| --- | --- | --- | --- | --- |
| A | HiAgent 官方 Tyreworld `p01`--`p10` | Standard：完整可观察历史 | HiAgent：子目标 + 已完成子目标摘要 | episode success |
| B | AWM README 的 Mind2Web `aa` 单网站 | empty workflow | AWM：训练集 `aa` 的离线 workflow induction | mean step success |

每个子复现默认运行 3 个固定 seed（`0,1,2`），同一任务成对比较。预注册 Gate
要求三次 seed 的方法臂主指标都严格高于 Base，且 task-level paired bootstrap
的点估计大于 0；任一条件失败即该子复现 `STOP`。只有 A、B 都通过，才可由主线程
另行设计共同的 Base/A/B/A+B 章节实验。本目录不会把失败结果改写成 GO。

## 当前状态

本 worktree 默认没有 API secret，也没有 Mind2Web `aa` 数据下载，因此当前可完成
的状态是 `PENDING_API_AND_DATA`：资产、数据合同、泄漏审计、transport schema
和可直接运行命令已经冻结；不能用 dry-run 或合成分数宣称迁移复现通过。

## 运行

```bash
cd "实验/实验59_HiAgent_AWM迁移复现_GO门"
python3 scripts/prepare_assets.py
python3 -m unittest discover -s tests -v
python3 scripts/schema_smoke.py
# fetch public aa train + test_task into ignored runtime/ (no LLM API call)
bash scripts/fetch_mind2web.sh
# audit v4 full-DOM visibility and policy-field contract (no LLM API call)
python3 scripts/mind2web_observation_audit.py \
  --mind2web-data runtime/mind2web-aa/data \
  --output results/mind2web_observation_contract_v4.json
```

真实运行只从环境变量读取 secret，严禁把 key 写进命令、文件或日志。需要显式
提供 OpenAI-compatible endpoint 和 key（变量名可使用 `PAIR2_API_KEY` /
`PAIR2_BASE_URL`，也接受 `OPENCODE_API_KEY` / `OPENCODE_BASE_URL` 或
`OPENAI_API_KEY` / `OPENAI_BASE_URL`）：

```bash
export PAIR2_API_KEY='(由调用环境安全注入；不要写入 shell 历史)'
export PAIR2_BASE_URL='(OpenCode Go 的 OpenAI-compatible base URL)'
python3 scripts/run_pair2.py --experiment hiagent --seeds 0,1,2
python3 scripts/run_pair2.py --experiment awm --mind2web-data /path/to/Mind2Web/data --seeds 0,1,2
python3 scripts/aggregate_gate.py --experiment hiagent
python3 scripts/aggregate_gate.py --experiment awm
```

脚本会拒绝没有 secret 或 endpoint 的真实运行，并只输出脱敏后的请求统计。原始
请求/响应只放在被 `.gitignore` 忽略的 `runtime/`，提交中只保留数据合同、manifest
和冻结的汇总决策。

protocol v4 重新冻结 AWM 的 policy observation contract：每一步发送完整
`cleaned_html`，公开硬上限为 300000 chars，超过上限或缺失即 fail-closed，不做
prefix 截断；历史只保留 agent 自己的 step index 和 action，不重复旧 DOM。policy
仍不读取 `pos_candidates`、`neg_candidates`、rank、operation、future 或 success。
离线 audit 必须证明 aa test 的每个 target backend id 都存在于当前 DOM，且 policy
字段泄漏为 0。v3 的 16000-char 截断导致该合同失效，其指标全部排除 Gate。

v4 将 AWM induction 设为 `max_completion_tokens=2048`：官方 GPT-4o 脚本为 1024，
DeepSeek 迁移为 2048 以适配同一 induction 的输出长度；仍要求流式
`finish_reason=stop`，这不改变 Gate、prompt 语义或评分门槛。所有 action/summary
仍为 256，统一 `reasoning_effort=none`。v1--v3 smoke 或无效 observation contract
结果均不能作为方法效果结论。

AWM 预注册主指标改为 task-level mean `step_success`（严格 action exact-match
比例）；`episode_success`、`action_f1_mean` 与 `element_accuracy` 仍保留为辅助
指标。三次 seed 均须 method 的 step_success 严格高于 Base，paired bootstrap 仍以
task id 为单位；缺失/无效合同只能产生 `PENDING_*`，不能产生 STOP 或 GO。

完整 runner 支持显式 `--stream` 与 `--max-retries 0`，二者和 call-kind 预算会写入
backend/transport manifest。正式评分前必须先运行 observation audit；默认仍保留非流式、
最多 2 次 retry 的兼容行为。
完整 17 条 `aa` train induction message 的离线尺寸和脱敏 body hash 记录在
`results/awm_induction_prompt_manifest.json`，不包含 prompt 正文。

### macOS Keychain 启动方式

不希望把 key 放入 shell 环境或历史时，可将其存入 macOS Keychain 的 generic
password 项：service=`codex-opencode-go`、account=`$USER`。可使用 Keychain
Access 图形界面，或运行下面的命令后在隐藏提示中输入 key（命令本身不含 key）：

```bash
security add-generic-password -U -s codex-opencode-go -a "$USER" -w
```

然后透传原有 runner 参数：

```bash
bash scripts/run_with_keychain.sh --transport-smoke
# smoke 成功后再启动单任务试跑
bash scripts/run_with_keychain.sh --experiment awm --mind2web-data /path/to/Mind2Web/data --seeds 0,1,2
```

`run_with_keychain.sh` 仅在 Darwin 上运行，从该 service/account 读取一次值，作为
当前 `run_pair2.py` 子进程的 `PAIR2_API_KEY` 环境变量，并固定
`PAIR2_BASE_URL=https://opencode.ai/zen/go/v1`。key 不进入参数、日志或文件；Keychain
缺条目、空值或非 macOS 时 fail-closed（退出码 78）。启动器不会创建或更新
Keychain 项。`--transport-smoke` 会切换到 `transport_smoke.py`，设置
`max_retries=0` 并且只发 1 个 `/chat/completions` 请求；它只保存响应 schema、
usage、latency 和响应 hash，不保存完整响应。smoke 失败时应停止，不继续启动子复现。

如需诊断流式协议，使用严格有界入口；它固定 seed 0、`max_retries=0`，只允许一次
AWM induction，或 HiAgent 的 `p01.pddl` 两臂各最多 5 步。流式入口只写脱敏的长度、
hash、usage、调用计数和任务指标，不写 prompt/response：

```bash
bash scripts/run_with_keychain.sh --stream-smoke --mode awm-induction \
  --mind2web-data /path/to/Mind2Web/data --max-retries 0 \
  --output results/stream_smoke_awm_induction.json
bash scripts/run_with_keychain.sh --stream-smoke --mode hiagent-p01 \
  --max-steps 5 --max-retries 0 \
  --output results/stream_smoke_hiagent_p01.json
```

`GO_STREAM_SMOKE` 或 `GO_STREAM_INDUCTION_ONLY` 仅表示该有界执行链完成，不能作为
完整实验 Gate 或方法效果结论；流式错误时入口 fail-closed 并停止后续任务。

若单请求 smoke 返回 401/403，可在不启动子复现的前提下做一次受限访问诊断：

```bash
python3 scripts/models_auth_diagnostic.py --unauthenticated
bash scripts/run_with_keychain.sh --models-auth-diagnostic --authenticated
```

两次命令各至多请求一次同一 `/models`，使用固定 User-Agent；第二次仅在授权
`/models` 返回 200 且包含 `deepseek-v4-flash` 时再发恰好一次带正常 User-Agent
的 chat smoke。诊断结果只保留 status、content-type、latency、response hash、
有限错误字段、模型数量/目标模型存在性和 usage，不保存模型列表、token header
或完整 body。

## 证据边界

- HiAgent 的 10 个 PDDL problem 文件来自 pinned HiAgent asset commit；policy 只
  看到 goal、当前 observation 和历史，不看到 `difficulty`、PDDL `subgoals` 或
  未来动作。
- AWM 的 test policy 只看到任务、当前 cleaned DOM、过去自己的动作/观察和（方法
  臂）由训练集诱导的 workflow；不传入 `pos_candidates`、`neg_candidates`、
  future action、最终 success 标签或 target operation。目标 action 只用于离线评分。
- AWM 的官方 `memory/exemplars.json` 默认不注入 policy；如需 teacher-forced
  ablation，必须显式开启并单独标记，不能混入主 Gate。
- 本实验使用迁移 adapter 和标准库 simulator，不声称复刻原论文的完整 Docker、
  模型或 benchmark harness。所有 transport 调用、重试、token usage、估算费用
  字段都会记录在本地运行 manifest 中。

## 真实运行前的调用量预算

默认 `max_steps=30`、3 个 seed、transport 最多 2 次 retry：A 的逻辑请求上界约为
`3 × 10 × 30 × (1 Standard + 3 HiAgent control + 1 summary)` = 4,500 次，线缆级
尝试上界为逻辑请求的 3 倍；实际会因提前成功和没有新子目标而更低。B 的逻辑请求
为 `3 × (1 induction + 2 × test action steps)`，实际 test action steps 必须在
运行 manifest 中报告。没有安全注入 key/endpoint 时这些调用不会发生。

Mind2Web 的公开 training source 和官方 `test.zip` 均由
`fetch_mind2web.sh` 自动取得到 `runtime/mind2web-aa/`。OSU-NLP-Group 的官方
README 明确说明 test archive 的密码是 `mind2web`；脚本只使用该公开说明的固定值，
不猜测密码，也不记录密码或解压后的 benchmark rows。为避免把数 GB 的全量 JSON
放入运行时，脚本优先使用 Hugging Face dataset-viewer 的 Parquet 导出，按
`website == aa` 过滤为 `data/train/aa.json`，并从官方加密 archive 的
`test_task/*.json` 流式过滤为 `data/test_task/aa.json`。来源 revision、URL、OID、
SHA-256、行数和步数写入 `results/mind2web_data_manifest.json`；该 manifest 不含
benchmark 内容。若环境缺少 `pyarrow`，脚本回退到官方训练 JSON shards 的标准库
流式过滤。

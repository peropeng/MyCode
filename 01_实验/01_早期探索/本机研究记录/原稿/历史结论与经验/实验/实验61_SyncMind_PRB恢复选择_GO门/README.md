# 实验 61：SyncMind × PRB 恢复选择可行性门

本目录是配对四（SyncMind + Plan-RewardBench）的资产、环境和运行合同。
它锁定官方 SyncMind 方法代码、SyncBench 300-instance evaluation subset、
本地 `robust_recovery` 资产，并准备一个不默认联网的 10-instance smoke runner。

当前裁决是 **PENDING**，不是 GO：本任务完成了隔离 Python 3.12 的 import/config
语义 smoke，并实际启动了官方 OpenHands runtime client 两次（A 一次原始尝试、一次
amd64/ABI 修复重试），但 BrowserEnv 的 Chromium 在 Colima amd64 仿真中崩溃，未
完成 CmdRunAction；B 也完成了真实 `get_config`/作者镜像 inspect 后在同一 client
启动层停止。未调用模型 API、未运行 10 个真实任务，也没有恢复成功率或候选选择
结果。论文 runtime blocker 保留。任何没有真实 10-instance、固定预算、四臂结果的
报告都不能把本目录写成章节 GO。

## 资产

`runtime/` 是本机 ignored 运行缓存，不提交第三方仓库或 48 MB CSV。可用
`python3 scripts/manifest_assets.py` 重新校验并生成 `results/asset_manifest.json`。
当前锁定值、计数和 schema 见该 manifest：

- SyncMind：`https://github.com/xhguo7/SyncMind`，commit
  `a48c469fc71a9f4f968c74813c66adf61be85f02`；根目录没有 LICENSE 文件，许可为
  UNKNOWN，不能把其派生代码或镜像直接再发布。
- SyncBench：Hugging Face `xuehang/SyncBench`，revision
  `d8f957746faa55b414ff93a2ab264e270d474952`，`syncbench/syncbench_300.csv`，
  300 行、21 个仓库、19 个字段。锁定 revision 的 `README.md` front matter
  明确 `license: mit`，hash 也写入 manifest。`gold_code`、`gold_summary`、
  new-context 和测试结果字段只用于离线资产审计，不能进入在线 agent/evaluator
  prompt。
- PRB：本地只读 `Plan-RewardBench/benchmark/robust_recovery.jsonl`，361 对、
  121 个 UUID。Pair4 中的 B 是固定数量恢复候选的质量选择，不复制 Pair3
  的 judge-prompt 对照；PRB 的 chosen/reject 只能在 API 调用完成后的解盲评分
  或独立 evaluator 资格核验中使用。

## 官方入口和环境

官方 SyncMind README 给出的 OpenHands 入口是：

```text
cd SyncMind/syncmind/framework/OpenHands
```

并给出以下两个命令脚本：

```bash
bash ./evaluation/benchmarks/syncmind/scripts/run_infer.sh \
  llm.gpt_4o HEAD CodeActAgent 300 independent false 30 1
bash ./evaluation/benchmarks/syncmind/scripts/run_eval.sh <result-path>
```

协作基线只把 `independent` 改为 `collaborative`；其余预算参数必须保持一致。
README 还说明论文环境使用 OpenHands 0.10.0 的 `OpenHands10` 入口；该仓库
当前公开 URL 返回 404。我们另锁定公开 upstream OpenHands 0.10.0 tag
（`642e01b...`）作 ABI 对照，并分别审计 SyncMind 的 paper-era `v1_syncmind`
更新路径：v1 的 import/symbol coverage 通过 0.10.0。当前 framework/v2 plugin
则缺少 0.10.0 的 `core.loop`、`core.setup` 和 `runtime.base`，不能误 overlay
到旧版本；SyncMind README 明确它同步 OpenHands 0.27.0，manifest 对公开
0.27.0 tag（`f69bf1f...`）也完成 coverage probe，记录
`CONDITIONAL_OVERLAY_ABI_COMPATIBLE`。这证明了两个版本各自的静态入口，但
不能把 0.27 overlay 说成论文 0.10.0 的精确数值复现；运行前仍需真实 smoke。

宿主机是 macOS arm64；官方 evaluator 在代码中要求 sandbox platform
`linux/amd64`，因此真实运行依赖 Docker/Colima 的 amd64 仿真。环境 probe
只做 Docker client/server、架构、Python/Poetry 和带
`--platform linux/amd64` 的 `hello-world` 检查，不清理 Docker，不构建 10 个
benchmark 镜像。宿主 Python 为 3.9.6、Poetry 不在 PATH，但已用用户态
`/Users/peroyang/.local/bin/python3.12` 建立 experiment-local venv（Python
3.12.13），没有全局安装。`scripts/setup_v1_runtime.sh` 使用显式路径和 ignored
`runtime/`，依赖解析采用仅在该 venv 内的 legacy resolver；实际包版本及哈希由
`results/runtime_smoke.json` 记录。它是可执行 smoke profile，不声称重建完整
论文 Poetry lock。
注意：该公开 0.10.0 tag 的 `pyproject.toml`/包元数据仍报告
`openhands-ai==0.9.8`；本实验以 git commit `642e01b...` 和源码路径锁定版本，
不把包字符串单独当作论文 provenance。

## 使用

计划/mock 命令只生成离线结果，不创建 socket；下面的环境/runtime smoke 是
单独显式步骤，其中 sandbox 命令会访问本机 Docker daemon，但容器网络固定为
`none`：

```bash
python3 runner.py --plan --data runtime/syncbench/syncbench_300.csv \
  --out results/smoke_plan.json
python3 runner.py --mock --data runtime/syncbench/syncbench_300.csv \
  --out results/mock_smoke.json
python3 scripts/probe_environment.py --out results/environment_probe.json
python3 scripts/probe_v1_overlay.py \
  --syncmind-root runtime/syncmind \
  --openhands-root runtime/openhands-0.10.0 \
  --out results/v1_overlay_probe.json
python3 scripts/manifest_assets.py

# Prepare the ignored Python 3.12/v1 overlay without touching global Python.
bash scripts/setup_v1_runtime.sh \
  --python /Users/peroyang/.local/bin/python3.12 \
  --syncmind-root runtime/syncmind \
  --openhands-root runtime/openhands-0.10.0 \
  --runtime-root runtime

# Real no-API semantic smoke; the image must already be a local linux/amd64 image.
PYTHONPATH=runtime/overlay-v1:runtime/openhands-0.10.0 \
  runtime/py312-venv/bin/python scripts/runtime_smoke.py \
  --python runtime/py312-venv/bin/python \
  --syncmind-root runtime/syncmind \
  --openhands-root runtime/openhands-0.10.0 \
  --overlay-root runtime/overlay-v1 \
  --sandbox-image alfin06/agentissue-bench:lagent_239 \
  --out results/runtime_smoke.json

# Third-stage official client probe. This is bounded: first run once; if A
# fails, run the same command once with --retry-environment-repaired, then
# run once with --only-b for the independent B attempt. Never repeat a layer.
# It never calls a model or OpenCode API and must not be repeated after a
# result has been produced.
PYTHONPATH=runtime/overlay-v1:runtime/openhands-0.10.0 \
  runtime/py312-venv/bin/python scripts/full_no_llm_runtime_smoke.py \
  --python runtime/py312-venv/bin/python \
  --openhands-root runtime/openhands-0.10.0 \
  --syncmind-root runtime/syncmind \
  --overlay-root runtime/overlay-v1 \
  --syncbench runtime/syncbench/syncbench_300.csv \
  --runtime-root runtime \
  --runtime-image ghcr.io/all-hands-ai/runtime:0.9-nikolaik \
  --task-image xuehang/15_spacy_callee:3.11 \
  --out results/full_no_llm_runtime_smoke.json

# Only after an A failure, the one permitted repair retry:
# (repeat the command above with --retry-environment-repaired)
# Then, without rerunning A, the one B attempt:
# (repeat it with --only-b)
```

`--mock` 是确定性的离线 parser/公平性 smoke，输出只能是
`SMOKE_CHAIN_PASS_NOT_ACCURACY`。真实调用必须由操作者显式提供
`--live --confirm-live-10`，并通过 `scripts/safe_launch.sh` 从 macOS Keychain
service `codex-opencode-go` 注入 key；本任务没有执行该路径。

`scripts/probe_v1_overlay.py` 已在临时目录 materialize
`updates/v1_syncmind` 到 OpenHands 0.10.0 的 `evaluation/syncmind`，完成
路径合同和 `compileall`（无 API、无 vendor 修改）；结果为
`PASS_STATIC_EXECUTABLE_CANDIDATE`。第二阶段的
`results/runtime_smoke.json` 进一步记录 `IMPORT_PASS`、
`CONFIG_CONSTRUCTION_PASS`、`SANDBOX_COMMAND_PASS` 已通过，且
`api_calls=network_requests=network_model_calls=0`；
`FULL_NO_LLM_RUNTIME_PASS` 仍为 `PENDING`，因为没有把 container-only shell
冒充官方 OpenHands runtime client。第三阶段的
`results/full_no_llm_runtime_smoke.json` 记录了真实
`create_runtime`/`EventStreamRuntime` 启动：A 的首个请求暴露了 public
`0.9-nikolaik` client 拒绝 OH0.10 `CmdRunAction.hidden` 的 wire ABI 差异；一次
明确的 `linux/amd64`/进程内兼容 shim 修复重试后，Chromium 在 QEMU 的
`zygote IsSingleThreaded`/SIGSEGV 阶段失败。B 的 v1 `get_config` 和作者镜像
inspect 通过，但同一 client ready 阶段失败，未进入 `initialize_runtime`、
controller 或 prompt。13 条 pip check 冲突均分类为预构建镜像路径的
optional/mismatched，浏览器仿真失败才是 runtime blocker；所有自有容器均验证
无 running 残留，`FULL_NO_LLM_RUNTIME_PASS` 仍为 `PENDING`。

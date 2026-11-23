# 实验65离线核心

该目录冻结了换序绝对 Rubric 评分开发资格门：资产校验、匿名 prompt、严格 JSON parser、
306-slot 规划、三臂聚合、固定基线、UUID 配对 bootstrap、纯函数 gate，以及受限在线 canary
和一次性 detached 开发 child。

确认性 JSONL 保持封存。canary 只使用 planning_multi_easy 的固定物理 line 2（6 slots）；
mock 不联网，live 只能由固定 launcher 触发。51 行 live child 只能由 detached supervisor
启动，所有 durable records 去标识化且不含凭据/raw 内容；retry 仍固定为 0。
冻结模型元数据使用 `reasoning_effort: none`；mock 只能返回 `MOCK_ONLY_NOT_ACCURACY`。
slot 生成会强制执行 scaffolding 控制面审计，但不会扫描原始 INPUT 值。

## 使用

```bash
python3 runner.py /absolute/path/to/safety_refusal.jsonl
python3 -m unittest discover -s tests -v
python3 -m py_compile runner.py tests/test_runner.py
sh scripts/safe_launch_canary.sh                 # live；固定路径、无参数
EXP65_CANARY_MOCK=1 sh scripts/safe_launch_canary.sh  # 仅 smoke，不查 Keychain
EXP65_DEV_CONFIRMATION=ALLOW_EXP65_DEV_51 sh scripts/safe_launch_dev_background.sh
sh scripts/status_dev_background.sh               # 只读状态
```

第一条命令只校验冻结资产并输出 `validated_rows` 与 `slots`，不会把任何原始内容写盘或打印。
canary 产物为 `results/canary_ledger.jsonl`、`canary_result.json`、`canary_gate.json`；开发
child 产物为固定 `dev_ledger.jsonl`、`dev_result.json`、`gate_decision.json`，监督记录位于
`results/dev_supervisor.pid.json`、`dev_supervisor.status.json` 与 sanitized log。协议见
`PROTOCOL.md`，机器可读冻结项见 `results/preregistered_plan.json` 与 `results/asset_manifest.json`。
supervisor 会在启动 child 前持久化 `LAUNCHING` 意图；残留意图、空 ledger 或任一残留产物
均不会被 status 误报为 `NOT_STARTED`，也不能再次启动。

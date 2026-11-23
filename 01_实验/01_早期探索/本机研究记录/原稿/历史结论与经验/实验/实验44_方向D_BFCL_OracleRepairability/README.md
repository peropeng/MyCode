# 方向 D：BFCL Oracle repairability Gate3

本实验只回答一个窄问题：在实验43已经锁定的 120 个 BFCL 多轮任务上，若只对公开 BitAgent response 做“执行前、同轮 patch”，理想 Oracle 是否能在离线官方 evaluator 中获得足够的有效率提升。

## 结论口径

实验43 的公开 BitAgent `result` 只有每轮模型输出字符串。真正的 tool output、状态和 handler step 位于不能进入 online policy 的 `inference_log`。因此本实验不声称 post-execution retry、闭环恢复、补生成后续轮，所有 operator 只能改写已经存在的 response item。

Oracle 只用于信息上界：候选输出先完全冻结并记录 digest，再由隔离的官方 evaluator 读取原始 task/Gold 评分。任何 Gold、initial state、path、missed function、future turn、reference length、error class 或 score 都不传给 candidate policy。

## 固定样本与 operator

样本严格复用实验43 Gate1 的四家族各 30 条、全局 120 个 structure/task digest，不重新采样。operator 类型（含 No）预注册为 8 个：

`No`、`EnvelopeCanonicalize`、`NameCanonicalize`、`SafeTypeCoerce`、`DropInvalid`、`FillFromCurrentLiteral`、`Abstain`、`MinimalCombined`。

候选池是 `No + 每个已有 turn × 每个固定 operator`。局部 operator 只作用于该已有 turn 中已存在的 response item。SchemaRuleRepair 是额外报告的固定规则基线：按 turn/response 顺序，最多对第一个发生变化的 response 应用一次 `Envelope → Name → Type → Drop`；它不是第九个 operator 类型，也不读取 Gold。

`FillFromCurrentLiteral` 只有在当前可见 user text 中恰好存在一个、且类型匹配的显式 literal 时才填一个缺失 required scalar；不根据任务目标猜参数。`DropInvalid` 只删除公开 schema 无法解释的调用或明确不完整的调用；不会把未来调用补回来。

## 运行

runtime 不复制到本目录，默认只读复用实验43的锁定 runtime；也可通过 `--source-root` 指向同一份只读 runtime。先执行：

```bash
runtime/venv312/bin/python scripts/prepare_metadata.py
runtime/venv312/bin/python scripts/run_repairability.py
runtime/venv312/bin/python -m pytest -q tests
```

正式评分的 replay1 按固定 candidate 顺序执行，replay2 按其逆序执行；每个 candidate/replay 都带有 `experiment`、task hash、candidate hash、完整输出 digest 和 replay index 的独立 evaluator namespace，并在 `finally` 中清理官方 `multi_turn_utils` globals。需要做固定 seed 的顺序复核时运行：

```bash
runtime/venv312/bin/python scripts/run_repairability.py \
  --candidate-order shuffle --shuffle-seed 20260821 --output-root /tmp/bfcl-e44-shuffle
```

若本机没有 `runtime/`，使用实验43 runtime 的完整绝对路径，例如：

```bash
/path/to/venv312/bin/python scripts/prepare_metadata.py \
  --source-experiment /Users/peroyang/My/MyWork/worktrees/0821-direction-d-bfcl-gate01/实验/实验43_方向D_BFCL接口契约_Gate0Gate1
/path/to/venv312/bin/python scripts/run_repairability.py \
  --source-root /Users/peroyang/My/MyWork/worktrees/0821-direction-d-bfcl-gate01/实验/实验43_方向D_BFCL接口契约_Gate0Gate1/runtime
```

脚本会对 No、所有局部候选和 SchemaRuleRepair 各做两次官方 evaluator clean replay；不按相同 output digest 跨 candidate 复用 checker 结果。`candidate_replay.json` 中包含 metadata-only evaluator isolation audit；`TEST_HARNESS_ERROR` 单列。结果只提交 hash、计数、布尔结果和聚合统计，不提交 raw response、Gold、schema source 或 inference log。

旧版结果（在审计前按 task/output digest 缓存 checker 结果）因官方 stateful evaluator namespace 跨 candidate 污染，全部标记为 `INVALID`，不得作为本实验结论。本版隔离重评为 No=75/120、SchemaRuleRepair=70/120、Oracle=77/120、净救回=2/120，仍为 STOP。

## Gate3 预注册门槛

No 必须复现 75/120 VALID。Oracle 相对于 No 与 SchemaRuleRepair 中较强者，要求 VALID 相对提升至少 10%、至少净救回 8/120，且固定 seed、10,000 次 task/structure cluster paired bootstrap 的 95% CI 下界大于 0。所有候选 replay 的 task-level 一致性要求 120/120、每家族 30/30、harness error 为 0；隔离审计还要求 created=removed、preexisting=0、final leak=0。

任一门槛失败即 `Gate3 STOP`，不训练 Gate2 诊断器，不声称 interactive recovery，也不能据此宣称两章毕设论文可行。

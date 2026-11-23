# 方向 D：BFCL Within-Item Call Ordering

本实验验证一个与实验44–46不同、且经独立审阅批准的机制：只在一个已有 response item 的 JSON call list 内改变调用顺序。目标是检验 BFCL 官方 evaluator 是否会因 stateful multi-call 的执行顺序而产生可修复失败。

## 机制边界

- 固定复用实验43 Gate1 的 120 个 task/structure（四家族各 30），不重新抽样。
- `Permutation` 对每个可解析的 multi-call item 枚举全部唯一非原顺序排列。只改变该 item 的顺序，保持 call multiset、函数名、参数、值、数量、item/turn 数和所有其他字段不变。
- 公开冻结阶段只读取 task 的公开问题/schema 与公开 BitAgent response。每个候选先计算完整输出 `candidate_hash` 和 `candidate_output_digest`，然后才加载 Gold/evaluator。
- `SchemaDependencyOrder` 是单一全局规则 baseline：使用公开 schema 名称/描述和当前可见 user 文本，read/search/list/get 优先于 create/update/delete/send；用户显式顺序和原顺序作固定 tie-break。它不是逐 task union，也不被计入 Oracle 候选池。
- policy 输入不包含 Gold、possible_answer、initial_config、missed_function、future turn/reference count、tool output、state、offline error、inference log、family/task/path/raw id。

## 隔离与复核

每个 candidate/replay 的 official checker namespace 包含 `experiment + task_hash + candidate_hash + full_output_digest + replay_index`。调用前存在预期 key 即 `HARNESS_INVALID`；`finally` 中清理所有已创建 key，要求 created=removed、最终 leak=0。正式 replay1 按 canonical ascending，replay2 按全候选 reverse；另用固定 seed shuffle 比较逐 candidate outcome fingerprint，并在独立 subprocess 中复核全部 120 个 No 及每个 family×operator 非 No 至少 5%。

结果只提交 hash、索引、布尔、计数、聚合和 bootstrap；`candidate_replay.jsonl` 是逐候选 metadata-only 证据，不含 response/Gold 原文。

## 结果

支持审计得到 668 个 multi-call item、98 个 task，call 数分布为 2/3/4/5/7：290/140/132/85/21；非原顺序排列恰为 119,960，因此总候选为 120,200（No 120 + Permutation 119,960 + baseline 120）。

正式双 replay：No=75/120，`SchemaDependencyOrder`=73/120，global strongest=No，Oracle（No+全部排列）=75/120，净救回 0，相对增益 0，paired structure bootstrap 95% CI=[0, 0]。候选 120/120 task 正逆序一致；240,400 scoring call 中 evaluator exception=0、preexisting=0、created=removed=5,972、final leak=0。

科学门判定：**STOP**。失败原因是相对增益低于 10%、净救回低于 8、bootstrap CI 下界不为正。按总合同，方向 D 第二章永久停止，不再增加第五个本地 operator；保留该机制作为“stateful evaluator 顺序影响未形成可修复收益”的负结果。

## 重跑

先确认实验43外部 runtime 已存在，然后执行：

```bash
runtime/venv312/bin/python scripts/prepare_metadata.py
runtime/venv312/bin/python scripts/throughput_probe.py --sample-size 10000
runtime/venv312/bin/python scripts/run_call_order.py --progress-every 10000
runtime/venv312/bin/python scripts/order_invariance.py
runtime/venv312/bin/python scripts/fresh_process_audit.py
runtime/venv312/bin/python -m pytest -q tests
```

默认 runtime 路径锁定在实验43的外部只读目录；来源 commit、wheel 和固定选择摘要位于 `manifests/source_linkage.json`。

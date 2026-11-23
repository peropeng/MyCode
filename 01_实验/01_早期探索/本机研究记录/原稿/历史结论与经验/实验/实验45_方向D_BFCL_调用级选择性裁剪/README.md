# 方向 D：BFCL 调用级选择性裁剪 Oracle probe

本实验是同一“BFCL 预执行修复是否有信息价值”目标下，与实验44 不同的设计 2/3：不修改函数名、参数值，不补生成，不重排调用；只对公开 BitAgent `result` 中已经存在且可 JSON 解析的调用做删除/保留子集。它回答的是：失败是否主要来自同一轮中的多余、重复或有害调用，而不是字段格式问题。

## 结论边界

候选函数只接收当前已有 response item 的 JSON 文本、响应前缀（用于 History 去重）和调用级位置；不接收 user/schema/task/family/path/missed function/initial state/reference length/error/inference log/future turn/raw id。候选输出在任何 `possible_answer` 或 evaluator 被打开前冻结，保存完整输出的 hash；随后才由隔离官方 evaluator 读取原始任务与 Gold。没有模型、付费 API、tool output、状态重放或未来轮补生成。

设计 1（实验44 的 canonicalize/drop-invalid/literal-fill/abstain）旧版结果因 evaluator state contamination 已 INVALID；修正版为 `Oracle=77/120, No=75/120, rescued=2`。本实验不改设计 1 阈值，也不把其 operator 重新混入候选池。

## 固定算子与候选生成

固定顺序为：

1. `No`；
2. `DropOneCall`：每个可解析 call 的 turn/item/call index 各一候选；
3. `KeepOneCall`：多 call item 中每个 call 各一候选，只保留该 item 的一个 call；
4. `DropOneResponseItem`：同一 turn 有多个 response item 时逐个删除；
5. `KeepOneResponseItem`：同一 turn 有多个 response item 时逐个保留；
6. `DeduplicateExactWithinItem`：一个 item 内 canonical JSON 完全相同的 call 只保留首次；
7. `DeduplicateExactWithinTurn`：一个 turn 内跨 item 的 canonical JSON 完全相同 call 只保留首次；
8. `DeduplicateExactHistory`：只删除与更早已观察 history turn 完全相同的 call，保留最早出现。

`ExactDedupRule` 是额外固定规则 baseline，不是 Oracle 的逐 task 选择：对完整输出至多做一遍 `WithinItem → WithinTurn → History`，保持 turn/item/call 顺序。

所有删除均为最小子集操作：不会新增、重排、改值；空 item 以 `[]` 保留其位置，空 response turn 仍保留。不可 JSON parse、非 list/dict、不可表示为 call 的 response item 不产生 call-level candidate，support audit 记录其不适用原因。

## 运行

runtime 不提交到本目录，默认从实验43 的锁定 runtime 只读复用。先生成固定 hash manifests，再只做 public support audit：

```bash
runtime/venv312/bin/python scripts/prepare_metadata.py \
  --source-experiment /path/to/实验43_方向D_BFCL接口契约_Gate0Gate1
runtime/venv312/bin/python scripts/run_call_pruning.py --support-only \
  --source-root /path/to/实验43_方向D_BFCL接口契约_Gate0Gate1/runtime
```

support audit 必须在全量 scoring 前完成，报告真实 multi-call、duplicate、multi-item、JSON shape 与每个 operator 的 candidate support。只有 audit 完成后才允许：

```bash
runtime/venv312/bin/python scripts/run_call_pruning.py \
  --source-root /path/to/实验43_方向D_BFCL接口契约_Gate0Gate1/runtime
```

runner 对每个 candidate/replay 使用含 experiment、task hash、candidate hash、完整 output digest 和 replay index 的独立 official evaluator namespace；replay1 按 candidate 顺序、replay2 按逆序执行，绝不跨 candidate 复用 checker 结果。结果只提交 hash、布尔、计数、每家族聚合和 bootstrap 统计，不提交 raw response、Gold、call value、schema 原文或 inference log。旧版按 output digest 缓存的结果及“unique output reuse”口径均为 **INVALID**。

## Gate 结果

No 必须复现 `75/120`。首先在全 120 条上比较 `No` 与 `ExactDedupRule`，选择一个真实全局最强 arm（同分选 No）；不能使用 per-task union 作为 baseline。Oracle 允许从全部调用级候选中按规定 tie 规则逐 task 选择，但只作为信息上界。

Oracle 相对全局最强 arm 要求：VALID 相对提升至少 10%、至少净救回 8/120、固定 seed `20260821` 的 10,000 次 unique-structure paired bootstrap 95% CI 下界大于 0。所有 candidate 双 replay task 一致性为 `120/120`、每家族 `30/30`，harness error 为 0；隔离 audit 要求 created=removed、preexisting=0、final leak=0。修正版结果 No=75、ExactDedupRule=74、Oracle=77、rescue=2、bootstrap CI=[0,0.0417]，故 `设计2/3 STOP`；不训练 Gate2，也不声称两章毕设可行。通过只表示可进入下一阶段，不等于两章 GO。

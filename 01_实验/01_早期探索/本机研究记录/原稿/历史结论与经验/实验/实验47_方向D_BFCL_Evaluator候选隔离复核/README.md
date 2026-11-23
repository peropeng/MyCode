# BFCL evaluator 候选隔离复核

本目录只保存实验44/45/46 的 evaluator 状态隔离 helper、顺序不变性审计和 fresh-process 抽样审计；不复制官方 runtime，不保存 raw response、Gold、schema/literal、state 或 candidate 原文。

旧版实验44/45/46 曾按 full-output digest 跨 candidate 复用官方 checker 结果。官方 `multi_turn_utils` 的 stateful instance namespace 不包含 candidate，故旧版分数和 unique-output reuse 口径均为 `INVALID`。本版 helper 不改官方 runtime：每个 candidate/replay 使用 `experiment + task_hash + candidate_hash + full_output_digest + replay_index` namespace，按官方 `_eval` 和 `re.sub(r'[-./:]','_',...)` 规则生成 model/ground_truth/involved-class keys，并在 `finally` 清理。

## 审计命令

在本 worktree 根目录运行：

```bash
/path/to/runtime/venv312/bin/python 实验/实验47_方向D_BFCL_Evaluator候选隔离复核/order_invariance.py
/path/to/runtime/venv312/bin/python 实验/实验47_方向D_BFCL_Evaluator候选隔离复核/fresh_process_audit.py
/path/to/runtime/venv312/bin/python -m pytest -q 实验/实验47_方向D_BFCL_Evaluator候选隔离复核/test_evaluator_isolation.py
```

`order_invariance.json` 比较 canonical 与固定 seed `20260821` shuffle 的逐 candidate outcome fingerprint；正式 replay1/replay2 本身分别按升序/逆序执行。三组全量结果分别为 3264/3264、9418/9418、26503/26503 一致，且两条 shuffle 顺序均发生变化。

`fresh_process_audit.json` 每组在独立 subprocess 复核全部 120 个 No，并按 family×operator 对非 No 候选固定 hash 顺序抽取至少 5%；结果分别为 303/303、601/601、1449/1449 一致。报告只落 hash、索引、布尔、计数和聚合；`harness_invalid`、preexisting、created/removed、final leak 均纳入判定。

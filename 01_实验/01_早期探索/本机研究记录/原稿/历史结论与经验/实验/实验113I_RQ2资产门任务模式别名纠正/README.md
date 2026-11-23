# Exp113I：RQ2 资产门 task schema alias 纠正

Exp113I 是独立的、alias-only 资产资格基础设施修正。它只为 Exp113H/G
corrected anonymous adapter task 添加兼容字段：

```text
instance_id == task_id
```

I 不改变 `task_id`、`candidate_map`、`candidate_id`、candidate 顺序或位置，
也不改变 feature、ranking、Gold latch、模型、回放、fault/probe、arms、
baselines、预算或 Gate 六条件。它针对 H 唯一正式 attempt 的
`KeyError: 'instance_id'`，该 H 失败已在 H 目录独立封存为
`FORMAL_HARNESS_INVALID`；H runner、tests、preflight 两份结果与 failure
audit 均只读复核。

## Non-formal exhaustive preflight

入口：

```text
python3 实验/实验113I_RQ2资产门任务模式别名纠正/scripts/run_task_schema_alias_preflight.py --preflight
```

预检对 34 tasks / 8 repositories / 272 candidates 做两项穷举证明：

- 添加 alias 后删除 `instance_id`，task payload 与 H/G corrected task 深度相等；
- 以 alias task 调用 inherited `F._candidate_map`，34/34 成功，272/272 candidate
  map 与 candidate IDs 完全一致，response counts 为 104/18/150。

同时复核 H fixed-rollback 32 available + 2 abstention，两个 task 为
`getmoto__moto-6387` 与 `pandas-dev__pandas-57058`。预检不读取 Gold/evaluator，
不运行 ranking/model/metric，不调用正式 `--run`。

## Formal integration outcome

正式入口为：

```text
python3 实验/实验113I_RQ2资产门任务模式别名纠正/scripts/run_task_schema_alias_preflight.py --run
```

I 在调用 H qualification 的严格作用域内只替换 schema builder、I decorator、
I writer、I 独立 output/audit paths 与 failure writer，`finally` 恢复所有 hook。
executor 与 H rollback-abstention/conflict-abort 语义原样继承。I verdict 为：

```text
GO   EXP113I_ASSET_ALIGNMENT_GO_CONTROLLED_ONLY_TASK_SCHEMA_ALIAS
STOP EXP113I_ASSET_ALIGNMENT_STOP_TASK_SCHEMA_ALIAS
```

I 唯一正式 `--run` 已执行一次并以 `HARNESS_INVALID` 失败：

```text
exit: 1
failure_stage: formal_executor_clone_reset
root cause: inherited H executor git reset --hard <base_commit> exited 128
formal output: absent
failure audit: present, single write, retry=false, overwrite=false
```

因此没有 I Gate/verdict 或 GO 结果；本轮不修复、不重跑。failure audit 的
`inherited_asset_metrics_present=false`，成功 output 后才可为 true。

## Verification

```text
python3 -m unittest discover -s 实验/实验113I_RQ2资产门任务模式别名纠正/tests -p 'test_*.py'
python3 -m py_compile 实验/实验113I_RQ2资产门任务模式别名纠正/scripts/run_task_schema_alias_preflight.py 实验/实验113I_RQ2资产门任务模式别名纠正/tests/test_task_schema_alias_preflight.py
git diff --check
```

I 不修改 H/G/F/D/C、Exp114 或任何旧结果；I formal output 不存在，独立
failure audit 已归档。

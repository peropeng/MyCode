# Exp113E：RQ2 资产门编辑重放语义诊断

Exp113E 是独立的、非正式 root-cause diagnostic。它只解释 Exp113D
`str_replace old text count is not exactly one`，不修复 D、不重跑 D，也不
产生资产门、method 或 chapter 结果。

## Frozen boundary

- 继承 Exp113D 已提交的 34 条 selected local sources、base commit 与三根
  source binding；不修改 D inventory、audit 或 output。
- 只从 E02 manifest 使用 `instance_id/repository/base_commit/sft_index/`
  `target_path_hash/window_start_call/window_end_call/window_size` 八个字段。
- 只读取 raw SFT parquet 的 `messages` 列，按原始 assistant call 顺序重放。
  不读取 `responsible_position`、fault、Gold/evaluator 字段，不选择 arm，不
  做 ranking/model/fit/metric，也不注入 fault。
- 每个 task 使用：

  ```text
  git clone --no-checkout --no-hardlinks <selected-local-source> <temporary>
  git checkout --detach <base_commit>
  git rev-parse HEAD
  ```

  临时 clone 自动清理；代码没有 fetch/pull/remote/submodule 或网络 fallback。

## Diagnostic fields

每个 state-changing editor call 记录 task、call index、prefix/window/suffix
位置、相对路径、target 是否存在、`old_str` 是否非空、occurrence count、
此前 applied/failed 数量，以及相邻 trajectory response 的 success/failure/
missing 信号。失败调用不修改 clone，诊断继续下一个 call/task；不保留 raw
old/new 文本，只保留必要的 response hash。

root-cause 分类固定为：

1. `runner_mistook_originally_failed_editor_call_as_state_delta`
2. `base_snapshot_mismatch`
3. `preceding_replay_semantics_mismatch`
4. `duplicate_old_legal_semantics_difference`
5. `other_missing_or_unclassified_adjacent_response` / 其他 editor precondition

## Run and result

```text
python3 实验/实验113E_RQ2资产门编辑重放语义诊断/scripts/run_edit_replay_diagnostic.py --run
```

结果独立写入：

`results/edit_replay_semantics_diagnostic.json`

该 JSON 明确 `formal_attempts=0`、`formal_metrics_generated=false`，并报告
34 tasks / 272 candidate-window calls、所有不可重放 calls、首个 formal-equivalent
failure 及其 prefix/window 边界。它不是资产资格门、方法结论或章节 GO。

标准库测试：

```text
python3 -m unittest discover -s 实验/实验113E_RQ2资产门编辑重放语义诊断/tests -p 'test_*.py'
```

本 README 在 diagnostic 完成后只记录该独立诊断摘要；不授权任何 D formal
重跑或科学协议修改。

## Completed diagnostic snapshot

本次修正后的非正式 probe 已完成 34/34 tasks、272/272 candidate-window
calls；输出 SHA256 为：

`5ef707c32c844a4d7484b60ce8044c7ded8ed25163a6f9cf8bf41cff6ff6fd16`

共发现 17 个 strict replay 不可重放 state-changing calls，formal
replay scope（prefix/window）为 0；另有 60 个 trajectory/runner semantic
mismatch 记录，其中 formal-scope semantic mismatch 为 25。根因计数为：

```text
clone_or_replay_state_mismatch                         2
other_missing_or_unclassified_adjacent_response       1
preceding_replay_semantics_mismatch                   10
runner_mistook_originally_failed_editor_call_as_state_delta 4
```

修正后的 `tree_blob_present`、`checkout_path_present` 与
`before_call_path_present` 均逐 call 记录；只有三者状态一致时才允许
`base_snapshot_mismatch` 分类。本次没有该分类，且
`first_formal_equivalent_failure=null`、
`first_str_replace_formal_equivalent_failure=null`：在禁用 lazy fetch 的
真实 local clone、无 arm/fault 的 probe 中没有复现 formal-scope strict
failure。

两个 `clone_or_replay_state_mismatch` 都发生在 suffix，不是 base snapshot
结论：

```text
Project-MONAI__MONAI-4745  call 17  str_replace  test_concat.py
pandas-dev__pandas-57058    call 22  create       test_pct_change_fix.py
```

前者的 call 16 是相邻 response 明确失败的 `create`，但 runner 仍将其应用，
所以 call 17 前文件已存在（`before_call_path_present=true`），而冻结 tree/
checkout 仍为 false；call 17 的成功 response 随后无法在该错误状态上完成
`str_replace`。后者的 call 17 是成功 `create`，call 22 再次 create 同一路径，
因此 call 22 前文件同样存在而 base tree/checkout 不含该路径。两者均是
replay state 与 frozen base tree 的分歧；JSON 同时保留相邻 response、此前
applied/failed 计数和 tree/filesystem 三态，不能被解释为 base blob 缺失。

焦点反证也已记录：

- `pandas-dev__pandas-49011` call 18 (`pandas/core/base.py`) 的
  `source_tree_blob_present/tree_blob_present/checkout_path_present/`
  `before_call_path_present` 全为 true，occurrence count 为 1，且
  `previous_calls_applied=0`；该 call 可应用，无 root cause。
- `pandas-dev__pandas-57058` calls 13、15 的目标 blob、checkout 文件和
  before-call 文件均存在，但相邻 response 为 failure；runner 将两个失败
  call 当作 state delta，分类为
  `runner_mistook_originally_failed_editor_call_as_state_delta`。
- `dask__dask-9378` 的 `dask/array/ma.py` 与 `dask__dask-8685` 的
  `dask/array/creation.py` 也均通过 source/tree/checkout/path 一致性检查。

因此旧诊断中的 `base_snapshot_mismatch` 结论不再使用；旧提交仍保留在 Git
历史中，当前 JSON 为独立替代结果。诊断没有读取 Gold、没有选择 arm、没有
注入 fault，也没有生成 formal attempts/metrics（`formal_attempts=0`、
`formal_metrics_generated=false`）；不构成资产、方法或章节结论。D 的
audit/output 保持不变。

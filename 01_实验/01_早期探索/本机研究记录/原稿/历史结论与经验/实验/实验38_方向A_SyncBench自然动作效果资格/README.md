# 实验 38：SyncBench 自然动作效果资格与公开 replay

本轮只审计 SyncBench 的自然 benchmark 资产，目标是验证方向 A Gate 1 的
`pre → public action/patch → post → effect Oracle → clean replay` 合同。
实验 35 已经证明本地构造合同可以运行，但 30 条 SyncBench 样本仍是
`METADATA_ONLY`；本目录不把构造任务混入自然任务统计。

当前已收口的证据是 14 条同一 Requests 仓库元数据行的独立性审计，其中 1 条
公开 Git transition candidate 完成了 2 次 Docker replay。由于本轮没有完成
30-task/3-repo 全量物化，`results/summary.json` 将 bounded probe 标为
`STOP`，但保留整体方向 Gate1 为 `CONDITIONAL`；不要把 bounded STOP 写成
整个方向永久 NO-GO。

## 证据边界

- 数据源：SyncBench Hugging Face 数据集，固定 revision
  `d8f957746faa55b414ff93a2ab264e270d474952`；来源和下载摘要写入
  `manifests/dataset_manifest.csv`。
- 方法代码：SyncMind GitHub `a48c469fc71a9f4f968c74813c66adf61be85f02`。
- CSV 的 `original_code`、`gold_code`、错误日志和测试摘要属于离线评测字段。
  它们可以用于资格审计，但不会写入在线 action/probe 输入，也不会作为
  本目录的 `public action` 声称。
- 本轮只有在源仓库公开 Git 历史中找到目标文件的对应后继 commit，并可由
  `git diff <target> <public_state> -- <path>` 重建补丁时，才把 action 标为
  `NATURAL_EXECUTED`。找不到时标为 `ACTION_MISSING`，禁止用 `gold_code`
  直接改文件。
- `CONSTRUCTED` 永远不计入本轮自然资格；`METADATA_ONLY` 只计 schema/独立性
  审计，不计 Oracle/replay。

## 运行

```bash
python3 scripts/discover_public_actions.py \
  --dataset-csv runtime/syncbench/syncbench_300.csv \
  --repo-cache runtime/repo_cache --per-repo 1 \
  --repos https://github.com/psf/requests
python3 scripts/run_replay.py --task-manifest manifests/task_manifest.csv \
  --repo-cache runtime/repo_cache --replays 2
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/*.py
git diff --check
```

`discover_public_actions.py` 会在临时缓存中使用 GitHub 的 filter clone，
不把仓库、镜像或大数据提交到 Git。`run_replay.py` 为每个任务生成独立的
Docker workspace，记录 test-before、公开 patch、test-after、返回码、超时、
stdout/stderr 摘要和文件状态差异。若依赖安装或上游网络使任务不能执行，
结果会保留具体失败分类而不是静默丢弃样本。

## Gate 1 判据

不下调实验 35 的门槛：至少 30 个独立 task、至少 3 个仓库/环境、至少 3 类
动作效果、稳定 Oracle ≥70%、clean replay ≥90%。本目录只输出本轮自然子门
结果；不得声称 Gate 3、RQ1/RQ2 或两章 GO。

## 结果

- `manifests/task_manifest.csv`：无 Gold 的任务、版本、公开状态 commit、补丁
  URL/SHA 和独立性标签。
- `results/task_results.jsonl`：逐任务逐 replay 证据。
- `results/summary.json`、`results/qualification_report.md`：汇总与裁决。

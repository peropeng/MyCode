# EXP42 qualification report

## Verdict

`Gate0 = STOP`，`Gate1 ready = STOP`。

这是“指定资产资格门”的 STOP，不是说 AppWorld 引擎不可运行：官方仓库、PyPI
包、data、experiment-output bundle 和本地 verifier 均成功运行。STOP 的直接原因
是合同要求的两个 train/dev GPT-4o 输出目录均不存在：

```text
simplified_react_code_agent_gpt-4o-2024-05-13_train
simplified_react_code_agent_gpt-4o-2024-05-13_dev
```

官方 bundle 中存在的是 test split 的 `react_gpt4o_test_normal` 和
`react_gpt4o_test_challenge`。它们 metadata 的 LLM tooltip 是
`gpt-4o-2024-05-13`，但不能被重命名为 train/dev 轨迹。它们的每个任务都有
`api_calls.jsonl`、DB JSONL、code/data version 和 evaluation report，而
`logs/environment_io.md` 计数为 0/168 与 0/417。

## What passed

- 官方 tag dereference 到 `66ad8099e12188ece0d3fe45e661dbc01880813b`。
- PyPI metadata 为 `appworld==0.1.3.post1`、Apache-2.0、Python >=3.11,<4.0。
- `appworld install`、data 下载、experiment-output 下载和 `verify tasks` 均成功。
- train/dev 有 90/57 个任务；147/147 都有 `evaluation.py`、`solution.py`、
  `compiled_solution.py` 和 `answer.json`。这里只记录文件存在性，不提交内容。
- 固定 10 个 smoke 任务（train 5、dev 5）具有 10 个唯一 generator ID；scenario
  未在公开 specs/metadata 中序列化，故严格记 UNKNOWN。
- 本机入口 smoke 对 10/10 任务均能构造 AppWorld、save_state、load_state；另对
  同一初始化中间态调用 `world.evaluate()`，返回 `TestTracker`。这只是入口
  可调用性证据，不是动作效果 Oracle 或 replay 证据。

## Why no Gate1

没有合法的 train/dev GPT-4o action-level trajectory（尤其是 environment I/O 或
等价可重建记录），就不能从 test baseline 的终态 DB/API log 反推动作效果。不能
把 protected `solution.py`、`evaluation.py`、DB 行或 API 日志复制进仓库，也不能
把构造数据冒充自然任务。因此本轮不做 30-task Gate1，不给方向 A 两章 GO。

复开门槛：取得许可明确、可复验的 train/dev action-level 轨迹；重新按至少 30
独立 task、3 environment/effect type、stable Oracle 和 clean replay 预注册门槛
做实验41。机器可读证据见 `results/gate0_summary.json`、两个 manifest 和协议文件。

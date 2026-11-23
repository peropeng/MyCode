# 实验63：位置无关结构轨迹评分开发门

本实验验证一个新的 Chapter 1 候选机制：把每条 agent trajectory 映射为固定的、
不依赖 pair 显示位置且不读取 query/tools 语义的结构特征，再用预注册的 L2 logistic
regression 做 pairwise 评分。它不调用 DeepSeek/API，不重跑实验62，也不打开确认集。

## 当前机器结论

唯一一次开发 OOF CV 已完成，机器结论为：

`STOP_POSITION_INVARIANT_SCORE_DEV`

这不是章节 GO。结果如下：

| 指标 | 结果 |
|---|---:|
| rows / UUID | 361 / 121 |
| orientation chosen-first | 170/361 = 0.470914 |
| structural model OOF accuracy | 0.692521 |
| strongest heuristic | fewer explicit errors |
| strongest heuristic accuracy | 0.667590 |
| relative gain | 3.734% |
| UUID-cluster paired bootstrap (10,000) | estimate 0.024793; 95% CI [-0.049656, 0.099174] |
| shuffled-label negative control | accuracy 0.529086; 95% CI [0.482094, 0.581267] |

虽然模型整体高于 strongest heuristic，仍未达到预注册的 +10%、bootstrap lower > 0、
每 fold 严格胜出和负对照 upper ≤ 0.55 等门条件；第 3 fold 模型为 0.541667，
strongest heuristic 为 0.833333。所有结果以
`results/dev_result.json` 和 `results/gate_decision.json` 为准，不应事后调参或据此
改门。

## 资产与确认集隔离

开发源是 `robust_recovery.jsonl`，SHA-256 为
`6db997789a0f6c19c13920eca8632e16fd35ba3bd78c6634cc35b22415bf9025`。确认集
`planning_single_hard.jsonl`（158 rows / 97 UUID）和 `tool_irrelevance.jsonl`
（275 rows / 147 UUID）只生成文件级 manifest，状态为 `SEALED_CONFIRMATORY`，没有
读取其候选轨迹、标签、query 或 tools 内容。

## 文件

* `PROTOCOL.md`：冻结的特征、模型、基线、负对照和机器门；
* `results/preregistered_plan.json`：执行前冻结计划；
* `runner.py`：无网络的唯一执行器；
* `results/asset_manifest.json`：开发/确认资产 hash、bytes、rows、UUID 数和 schema；
* `results/dev_result.json`：OOF 摘要、fold、bootstrap、分层错误和探索解释；
* `results/gate_decision.json`：机器门结论；
* `tests/test_runner.py`：schema 变体、位置不变、方向、GroupKFold、bootstrap 和密封
  manifest 合同测试。

运行器执行前需要 `numpy`、`scikit-learn`；命令为：

```sh
python3 -m unittest discover -s 实验/实验63_位置无关结构轨迹评分_开发门/tests -v
python3 实验/实验63_位置无关结构轨迹评分_开发门/runner.py --execute
```

本次运行实际 API/network calls 均为 0；代码和结果不保存 raw trajectory/query/tools/
prompt/credential。

# Exp75：AFTraj 前缀状态转移风险开发资格门

这是一个离线探索门，不是论文 GO。它在 Exp73 官方公平 Base STOP 后，使用 Exp58 资产中的非官方 test、按 task group 去重叠训练组，比较冻结的 memoryless/current-turn Base 与唯一新增的角色匿名因果状态转移/恢复记忆 A。

先读 [`PROTOCOL.md`](PROTOCOL.md) 和 [`protocol.json`](protocol.json)。协议、封存组哈希与 canary ID 必须先冻结，再生成结果。原始 AFTraj 只能从只读路径传入，不得复制到 Git；官方 test 只读取 ID/hash/count 封存信息，不读取正文或标签。所有线上调用、模型、token 均为 0。

```bash
python3 -m unittest discover -s tests -v
python3 runner.py audit --data-dir /Users/peroyang/My/MyWork/worktrees/0822-aftraj-asset/third_party/data/AFTraj
python3 runner.py run --data-dir /Users/peroyang/My/MyWork/worktrees/0822-aftraj-asset/third_party/data/AFTraj --output results/exp75_result.json
```

结果必须同时给出 Exact-F1、ASS、FAR、StepAcc、task-group paired bootstrap 95% CI、三 seed 配对差、better/worse/tie、masked-error 诊断、Base deletion、调用/ token/ 延迟零预算与泄漏/切分审计。探索门只能给出 `CONTINUE_EXPLORATION` 或 `STOP_*`，不能宣称论文资格。

## 最终冻结重跑摘要（2026-08-23）

封存审计通过：原始 safe/unsafe 为 1,162/1,114 行；官方 test 为 332 行、217 个 task groups；Exp73 canary 为 12 行；排除官方 test group overlap 后 clean train 为 1,817 行（safe 910、unsafe 907、1,164 groups），test/canary 泄漏为 0。官方 test 正文与标签未打开，只使用 ID/hash/count 封存信息。网络/API、调用数、token、延迟均为 0。

三组冻结 seed（20260822、20260823、20260824）的 fold assignment 均不同，但每折均选择 `current_activity`、Base threshold 1.5、A threshold 1.5，最终 OOF 指标一致：

| 方法 | Exact-F1 | ASS | FAR | StepAcc |
| --- | ---: | ---: | ---: | ---: |
| Base | 12.8173 | 1.5171 | 28.4615% | 11.1356% |
| Base+A | 10.8664 | 3.7552 | 100.0000% | 16.3175% |

A−Base Exact-F1 配对差为 **−1.9509pp**；每个 seed 的 task-group paired bootstrap（1,164 groups、2,000 resamples）95% CI 为 **[-4.3788, 0.3728]**，better/worse/tie 为 **60/622/482**。A 的 FAR=100% 对应 1,817/1,817 条轨迹报警（safe 910/910），是状态累积导致的过报警，而非 safe 标签处理错误；state deletion 精确回到 Base。masked-error 后差值仍为 −1.9509pp。诊断分层为 diagnosed **+12.4096pp**、injected **−5.6448pp**。

`pooled` 的 5,451 行是三 seed 重复 OOF 的描述性拼接，不是独立样本；推断 CI 仅使用各 seed 的独立 task groups。最终裁决为 **`STOP_A_NOT_POSITIVE`**，不进入论文 GO。

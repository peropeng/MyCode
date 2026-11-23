# Exp76：AFTraj 可恢复非单调复位状态机开发资格门

这是一次离线、探索性的开发资格门，不是论文 GO。Exp75 的单调状态机制只作历史背景；本目录只运行新的 Base 与唯一机制 B，不导入 Exp75 runtime/result。

## 运行前冻结

`protocol.json`、`data_seal.json`、官方 test task-group hash、Exp73 canary ID 和 B 的机制 spec/hash 在 OOF 运行前冻结。B 的状态只有 `NORMAL` 与 `PENDING`：当前可观测且 JSON parseable、named 或 tool-matched 的新 action transition 使状态进入 `PENDING`；PENDING 中随后的 content 非空且 action 为空立即 recovery，回到 `NORMAL`，该 recovery turn hazard 为零。仅 PENDING 且未恢复时，有限最近窗口中的重复结构、连续新 action/tool transition 或固定阈值 structural break 产生 bounded hazard。pending 窗口为 3 turn，hazard 窗口为 3 turn，hazard 上界为 3.0；固定权重、窗口权重和阈值网格写在 `protocol.json`，不得看结果改动。

B 只把当前 Base 结构分数与当前 bounded hazard 相加。B deletion 必须逐前缀、逐预测回到 Base。没有单调累计、轨迹总长/位置、Gold、source/domain、身份、未来、LLM、API 或额外 token/调用预算。

## 数据与统计

复用已验证的 AFTraj seal 与 clean-selection 逻辑，但实现独立复制到本目录。只读取非官方 test 行；官方 split 只用于 ID/hash 封存校验，官方正文和标签不 materialize。所有官方 test task groups 与 Exp73 canary 先排除，再按 task group 做 5-fold OOF；3 个冻结 seed 独立报告。Base candidate/threshold 与 B threshold 只用训练折选择。推断单位是 task group；paired bootstrap 为每 seed 2,000 次。

主比较只有 `Base` vs `Base+B`，主指标 Exact-F1，并报告 ASS、FAR、StepAcc、每 seed 差异、task-group paired bootstrap CI、better/worse/tie、masked-error、B deletion、报警计数和零 API/token/network 预算。Exp75 FAR=100% 仅作描述性历史参照，不构成 paired 证据。

## 审计命令

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile feature_contract.py runner.py
python3 runner.py audit --data-dir /Users/peroyang/My/MyWork/worktrees/0822-aftraj-asset/third_party/data/AFTraj
python3 runner.py run --data-dir /Users/peroyang/My/MyWork/worktrees/0822-aftraj-asset/third_party/data/AFTraj --output results/exp76_result.json
python3 -m json.tool protocol.json >/dev/null
python3 -m json.tool data_seal.json >/dev/null
git diff --check
```

长日志和运行时临时文件不入 Git；最终结果 JSON 与本 README 必须入 Git。

## 最终冻结 OOF 结果（2026-08-23）

协议、data seal、B mechanism spec hash（`25ea01135d625b51256285ec23413a2727316de6a53895b94f5b587705c14192`）均在运行前通过审计。clean selection 为 1,817 行（safe 910、unsafe 907）、1,164 个 task groups；官方 test 为 332 行/217 个 groups，Exp73 canary 为 12 行，三者只用于封存排除与校验，官方正文/标签没有 materialize。5-fold task-group OOF 使用冻结 seeds `20260822/20260823/20260824`，三组 fold assignment digest 均不同；API、network、token、latency 均为 0。

三 seed 的 Base 与 Base+B 指标一致重复如下（`pooled` 仅为描述性三次重复，不是独立样本）：

| 方法 | Exact-F1 | ASS | FAR | StepAcc | safe alarms | unsafe alarms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Base | 12.8173 | 1.5171 | 28.4615% | 11.1356% | 259 | 410 |
| Base+B | 12.8010 | 1.5207 | 28.5714% | 11.1356% | 260 | 411 |

B−Base Exact-F1 为 **−0.0162pp**，每个 seed 的 task-group paired bootstrap（1,164 groups、2,000 resamples）95% CI 为 **[−0.0414, 0.0000]**；三 seed 均为负，better/worse/tie 汇总为 **0/3/3,489**。masked-error 后差值仍为 −0.0162pp，预测未因诊断 mask 改变；B deletion 逐预测回到 Base。source 分层为 diagnosed 0.0000pp、injected −0.0252pp，domain 分层为 agentic −0.0251pp、coding/math 0.0000pp，因此不存在仅事后 injected/domain 正向的解释。

相对 Exp75 FAR=100.0% 的变化仅作描述性历史参照：Base+B FAR=28.5714%，−71.4286pp；这不是 paired 证据，也未作为方法输入。按预注册继续/停止规则，最终裁决为 **`STOP_B_NOT_POSITIVE`**；不进入论文 GO，不再因近零负差调整冻结权重或阈值。

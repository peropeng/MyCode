# Exp78：AFTraj 时序效用选择上界与可观测门探针

这是一个廉价、离线的探索性可行性探针，不是论文 GO，也没有打开官方 AFTraj test、调用 API 或训练新模型。它只读取 Exp75 已封存的 clean non-test 开发数据：1,817 行（safe 910、unsafe 907）、1,164 个 task groups；官方 test 的正文与标签没有物化，只使用 Exp75 的 split ID、hash、count 和 task-group 排除封存。

## 冻结协议

运行前先冻结了 [`protocol.json`](protocol.json) 与 [`data_seal.json`](data_seal.json)。结果中的协议 SHA 为：

```text
protocol  a366538c24747ecbe605999473796565c34d5a05b6e6c2734fadab005d289730
data seal d953dfb3ce7f1e892a18e258e301ce3d3eaebc8b7ae03dcc0079691df633155c
```

C 的输入是首个 Base/A 当前前缀决策分歧处的 28 个匿名数值：Base/A 当前分数、margin、报警位、当前结构事件、动作/工具/recovery 证据，以及上限为 4 的若干因果计数和 Exp75 状态记忆。没有文本、角色值、task/conv ID、source/domain、Gold、mistake 字段、总长度、未来或 resolved/final 状态。`prior_*_count_cap` 和 `state_memory` 是协议允许的当前前缀有界状态，不是显式位置/总长度字段；它们可能与轨迹进度相关，属于该廉价可观测探针的已知限制。

C 是 fold-local 的标准化线性 ridge utility gate：训练折 Gold 只生成 “A 是否救回 Base” 标签，正负样本拟合后在训练折 Exact-F1 上选择冻结的正则/阈值网格；测试折 `use_gold=False`，只用当前 prefix 特征。它在分歧处接受 A 或回退 Base，不是论文意义上的 A+C 组合。random 与 label-shuffled gate 仅作为负对照。所有调用、token、延迟均为 0。

每个 seed/fold 的 normal 与 shuffled gate 现在都在结果 JSON 中给出可重建的 fitted parameter payload：28 个 feature→coefficient、intercept、feature means/scales、constant fallback、regularization/threshold、label counts 与 `model_sha256`。参数 hash 覆盖除 hash 字段外的完整 payload；测试会从 payload 重建 gate 并逐样本核对 route decision。

首分歧处的 C 决策本身不读取未来；一旦选择 A 或 Base，之后只让所选的原始冻结路线按其通常的逐 prefix 因果规则继续处理可见回合，最终输出该路线的 first-alarm 结果。未来回合只能影响已选路线之后的正常预测，不能反过来改变首分歧处的 C 特征或选择。

## 阶段 0：选择上界

保守 oracle 只能在首个 Base/A 决策分歧处从两个已经冻结的完整路线中二选一，不能改候选、阈值或未来预测；Gold 只在评价侧选择能 exact 的路线，否则选择 false-alarm/step error 不更差的路线。

| 方法 | Exact-F1 | ASS | FAR | StepAcc |
| --- | ---: | ---: | ---: | ---: |
| Base | 12.8173 | 1.5171 | 28.4615% | 11.1356% |
| A | 10.8664 | 3.7552 | 100.0000% | 16.3175% |
| conservative oracle ceiling | 23.7576 | 1.1591 | 28.4615% | 21.6097% |

Oracle 相对 Base 的绝对增益为 **+10.9403pp**，相对增益 **+85.3561%**；三 seed 相同，Base/oracle task-group paired better/worse/tie 为 **91/0/1073**。首分歧共 1,779/1,817 行（覆盖 97.91%）：

| 首分歧类别 | 行数 | task groups |
| --- | ---: | ---: |
| rescuable（A exact、Base 错） | 95 | 91 |
| harmful（Base exact、A 错） | 699 | 653 |
| no_difference（两路 exact 正确性相同） | 985 | 873 |
| no_divergence | 38 | 28 |

source/domain 只作评价侧事后分层。以 seed 20260822 为例，source 的 Base→oracle→C Exact-F1 为 diagnosed `7.4510→22.0149→15.4143`、injected `20.3222→32.0468→26.0241`；domain 为 agentic `11.8770→21.4433→20.6544`、coding `30.6122→46.2963→31.7568`、math `0→9.5506→0`。

## 阶段 1：三 seed OOF

每个 seed 使用 5-fold task-group OOF；Base/A 每折先复现 Exp75，再允许打开 C。三 seed 均复现 Base Exact-F1 `12.8172588832`、A `10.8663729809`，且每 seed group better/worse/tie 均为 `60/622/482`。

| seed | Base+C Exact-F1 | Δ vs Base | C vs Base paired 95% CI | random | shuffled | C−shuffled paired Δ (95% CI) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 20260822 | 18.3509 | +5.5336pp | [3.7978, 7.5267] | 12.3192 | 13.5529 | +4.7980 [3.1073, 6.6361] |
| 20260823 | 18.2156 | +5.3984pp | [3.6243, 7.3478] | 11.1217 | 13.1562 | +5.0594 [3.3513, 6.9951] |
| 20260824 | 18.3395 | +5.5223pp | [3.7927, 7.5032] | 12.5984 | 13.1812 | +5.1583 [3.4260, 7.1271] |

C 的首分歧 coverage 为 `1779/1817=97.91%`，accept-A 率为 `31.14%/31.48%/31.53%`；rescuable 命中率均为 `49/95=51.58%`，harmful acceptance 为 `7/699=1.00%`、`9/699=1.29%`、`8/699=1.14%`。C 的 task-group better/worse/tie 分别为 `45/7/1112`、`45/9/1110`、`45/8/1111`。C-vs-random 的 paired Δ 为 `+6.0317`、`+7.0939`、`+5.7411pp`，95% CI 均为正；C-vs-shuffled 也均为正。label-shuffled gate 自身相对 Base 的小幅正差（`+0.7356/+0.3390/+0.3640pp`）被单独保留为负对照，不能解释为 C 机制结果。

ASS/FAR/StepAcc（seed 20260822）为：Base `1.5171/28.4615%/11.1356%`，A `3.7552/100%/16.3175%`，Base+C `1.3077/29.0110%/16.3175%`；其余 seed 的完整指标、paired bootstrap、fold fit、匿名 group/prediction 证据均在 [`results/exp78_result.json`](results/exp78_result.json)。

masked-error 后 Base 与 C 预测逐行不变；C deletion 逐行回到 Base；每个 fold 的 train/test groups 不交叉；所有成本仍为 0。未做未预注册的 feature-family deletion 来挑选主方法，避免看到结果后改变特征或权重；有界状态的可观测性限制如上明确记录。

结果 JSON 还包含首分歧 index 的 exact 分布及 `0/1/2/3/4/5-7/8-15/16+/none` 只读审计分层，并报告各 bucket 的 Base/A/oracle/C/random/shuffled 指标。该 index 审计是在预测完成后生成，明确不进入特征、拟合、阈值或模型选择。

`prior_*_count_cap` 与 `state_memory` 虽然是当前 prefix 可观测且协议允许的有界状态，但可能成为轨迹进度/位置的间接代理；这不是已解决的鲁棒性问题。正式确认 Exp78 方向前，必须另行预注册并独立完成 feature-family deletion 与 position-counterfactual robustness gate。本次不做事后 deletion、不调整主方法/特征/权重，也不把该结果写成已通过正式确认。

## 裁决

```text
CONTINUE_EXPLORATION
```

含义仅是：选择上界确实存在，且这个透明 C gate 在三 seed 均有真实正增益、优于 random/shuffled、无泄漏、零额外预算。它不打开官方 test，不构成论文资格或在线 AgentForesight 结果。

## 复现

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile runner.py
python3 runner.py --data-dir /Users/peroyang/My/MyWork/worktrees/0822-aftraj-asset/third_party/data/AFTraj --output results/exp78_result.json
python3 -m json.tool results/exp78_result.json >/dev/null
```

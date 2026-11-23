# Exp82：AFTraj F1 组成风险门（开发集 OOF）

## 边界与勘误

本实验只在 AFTraj clean development 数据上运行 3 个冻结 seed、5 个 task-group fold 的 OOF：1,817 行、1,164 个 task groups（safe 910、unsafe 907）。Exp80 已经消费过 official 332 行；Exp82 没有再次读取或物化 official body/label，也不能把它当作新的 confirmation set。Exp80 的 component audit 只提供了本轮机制的动机，未被回测、复制进输入或用作标签。

因此，原始 runner 返回的 `CONTINUE_CONFIRMATION` 不能直接当作 D 的 GO。只读裁决层 [`results/decision_scope_audit.json`](results/decision_scope_audit.json) 将结论拆成两个对象：`D_decision=NO_INCREMENTAL_GAIN`，`old_C_status=CONTINUE_EXTERNAL_CONFIRMATION`。

运行前勘误后的协议和数据 seal 已提交。当前 SHA：

```text
protocol  e03920786bc7f55d81e05c70429c947f04bd48f71c2962307b4ea05d3fa87013
data seal b69f8e8b246badcc9f77b10c1833daa2345935482829599bfef626fd9d483072
```

## D 做了什么

D 完全沿用 Exp79 `no_length_C` 的 18 个当前前缀特征、linear ridge、正则/阈值网格、Base/A 路线和候选预算；唯一变化是 outer-train 的效用标签：

- `positive_rescue`：A exact、Base 不 exact；
- `negative_risk`：Base exact、A 不 exact，或 Base abstain→A 错误报警（新增 FP）；
- `neutral`：其余情况，计入审计但不作为 ridge 正/负样本。

Gold 只在对应 outer-train fold 生成标签。outer-test 的 Gold 只用于最终 evaluator 和组成审计，不能进入特征、训练、阈值或路由。

## 结果

三个 seed 的数字完全一致。主指标是 task-group paired bootstrap 2,000 次。

| 方法 | Exact-F1 | 相对 Base | ASS | FAR | StepAcc |
|---|---:|---:|---:|---:|---:|
| Base | 12.8173 | — | 1.5171 | 28.4615% | 11.1356% |
| Exp79 old C（18 维） | 18.3282 | +5.5109pp / +43.00% | 1.3070 | 29.1209% | 16.3175% |
| Exp82 D | 18.3282 | +5.5109pp / +43.00% | 1.3070 | 29.1209% | 16.3175% |

D vs Base 的每个 seed 95% CI 都是 `[3.7375, 7.4690]`，task-group `better/worse/tie = 45/8/1111`。D vs old C 的差值为 `0.0000pp`，CI `[0.0000, 0.0000]`，1,164 个 group 全部 tie。也就是说：本轮 F1 组成标签没有带来旧 C 之上的新提升，但旧 C 的开发集正增益被精确重现。

## 组成风险审计

D vs Base 的每个 seed 都是：

| Pareto 组成类别 | task groups |
|---|---:|
| beneficial（TP 不降、FP/FN 不升，至少一项改善） | 45 |
| harmful（TP 不升、FP/FN 不降，至少一项恶化） | 12 |
| neutral | 1,106 |
| mixed | 1 |

Exact-F1 的 `8` 个 worse group 少于组成审计的 `12 harmful + 1 mixed`，因为部分 group 的 TP/FP/FN 变化没有改变 exact-correct 行数；这正是本轮增加组成审计的原因，不应把两组计数混为一谈。

首分歧 1,779 行中，D 的路由审计为：

- 可救回 95 行，接受 A 50 行（52.63%）；
- negative-risk 1,122 行，接受 A 13 行（1.16%）；
- 其中 Base abstain→A 错误报警的新 FP 接受 10 行；
- 总接受 A 580 行，另有 38 行没有分歧并直接走 Base。

这些路由数字与 old C 完全相同，所以 D 没有实际改变 risk trade-off。

## 负对照与审计

- old C 三 seed 精确重现 Exp79 的 Base/A/old-C 指标、bootstrap 和 group counts；
- D deletion 逐行回到 Base；
- shuffled-D 的 Exact-F1 为 `12.8091 / 12.8173 / 12.8173`，均远低于 D；
- deterministic random route 的 Exact-F1 为 `12.3192 / 11.1217 / 12.5984`，均低于 D；
- masked-error、future-causality、fold-local Gold 隔离和 18 维特征审计通过；
- API/network/token 均为 0；本地 wall time 约 84.5 秒，峰值 RSS 约 299.5 MiB；
- 禁止使用 position、length、task、domain、source、ID、Gold、future、text、error-word 字段。

完整机器结果在 [`results/exp82_result.json`](results/exp82_result.json)。

## 裁决（只读 scope resolution）

```text
D_decision=NO_INCREMENTAL_GAIN
old_C_status=CONTINUE_EXTERNAL_CONFIRMATION
```

D 的绝对停止理由是：D 相对 old C 为 `0.0000pp`，95% CI `[0, 0]`，1,164 个 task group 全部 tie；运行时逐行 route decision 也完全相同；component-harm 没有下降（D 与 old C 相对 Base 都是 12 个 harmful group，new-FP accepted 都是 10 行）。因此只能停止“F1-component-aware 重标改变线性边界”这个冻结实现，不能把它写成 D 的新提升。

old C 仍然可以继续：相对 Base 三个 seed 都是 `+5.5109pp`，95% CI 下界 `+3.7375pp`，所以 `old_C_status=CONTINUE_EXTERNAL_CONFIRMATION`。这不是对 D 的 GO，而是对已经存在的 old-C 开发正信号的继续确认资格。

Exp82 将“风险控制子目标”记为第 1 次实质机制无增益，排除了“仅重标新增 FP 即可改变线性边界”的解释；该失败不计入选择门总体方向的三次方法失败，也不否定选择门方向。由于 official 已被 Exp80 消费，本实验本身没有新的确认集，后续必须使用真正未见的外部 Agent 数据/环境，或明确记录为开发集正结果而不升级为最终 GO。

## 复现命令

```bash
python3 -m py_compile runner.py tests/test_exp82.py
python3 -m unittest discover -s tests -v
python3 runner.py \
  --data-dir /Users/peroyang/My/MyWork/worktrees/0822-aftraj-asset/third_party/data/AFTraj \
  --output results/exp82_result.json
```

# Exp92：成功参照任务组 split-conformal 边际风险校准

## 结论先说

本实验通过了预注册的可行性门：

```text
GROUP_CONFORMAL_FEASIBILITY_GO
```

这是一个实验级 GO，不是最终论文 GO，也不是外部确认集 GO。它说明：在已经冻结的 1,200 条轨迹上，给成功参照加入“任务组最大分数的 split-conformal 分位数”后，paired-reference 在三个 seed 都保留了真实提升，同时把两种误报率都控制在 10%以内。

## 本轮到底改了什么

只增加一个机制：

1. 每个 outer fold 内，只看 calibration success task groups；
2. 一个任务组的分数是该组所有 success runs、四个固定前缀 `[0.2, 0.4, 0.6, 0.8]` 分数的最大值；
3. 固定 `alpha=0.10`，若校准组数为 `n`，取 `k=ceil((n+1)*(1-alpha))`；
4. `k>n` 时明确 `NO_ALARM`，否则取第 `k` 小的组分数 `q`；
5. 部署阈值为 `nextafter(q,+inf)`，所以恰好等于 `q` 的分数不报警。

模型、特征、任务、前缀、切分、候选数、重试和 API 预算均未改变。这个构造只声称交换性下的有限样本“任务组边际风险”控制，不声称每个任务的条件风险上界，也不声称 95% 的 CP 条件保证。

## 数据与预算

| 项目 | 设置 |
|---|---:|
| 去重后轨迹 | 1,200 |
| success / failure 轨迹 | 1,093 / 107 |
| 任务组 | 281 |
| 含 failure 的任务组 | 82 |
| outer folds | 5 |
| seeds | 20260823、20260824、20260825 |
| 每组前缀 | 0.2、0.4、0.6、0.8 |
| 任务组 paired bootstrap | 5,000 次 |
| 外部 API | 0 |

数据 SHA-256、Exp89/Exp86/Exp91 只读代码和结果锚点均通过封存校验；跨来源轨迹重叠为 0。

## 最强公平基线

按协议，先要求一个方法在三个 seed 同时满足 success row-FPR 和 task-group any-alarm FPR 均不超过 10%，再比较三 seed 的平均 failure recall。最终全局基线是：

```text
paired_reference_cp
```

它不是按 seed 临时挑的。其三 seed 平均召回为 4.984%，高于其他风险合格候选，因此这是较强的公平比较对象，而不是只和弱的 clean baseline 比较。

## 主要结果

下面同时列出两种“提升差值”，不能混为一个数：

- “轨迹召回差”是 107 条 failure trajectory 中被报警的比例之差；每条轨迹等权。
- “任务组 bootstrap 差”是 82 个 failure task groups 等权后的 paired bootstrap 点估计；GO 使用它的 95% CI 下界。

| seed | paired CP 轨迹召回 | paired conformal 轨迹召回 | 轨迹召回差 | 相对提升 | conformal row-FPR | conformal group-any FPR | 任务组 bootstrap 差 | 95% CI | better/worse/tie |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 20260823 | 4.673% | 14.019% | +9.346 个百分点 | +200.0% | 2.653% | 7.636% | +8.740 个百分点 | [+3.455, +14.837] | 8/0/74 |
| 20260824 | 2.804% | 14.953% | +12.150 个百分点 | +433.3% | 3.111% | 9.091% | +12.602 个百分点 | [+6.098, +19.919] | 12/0/70 |
| 20260825 | 7.477% | 14.019% | +6.542 个百分点 | +87.5% | 2.928% | 7.636% | +6.301 个百分点 | [+1.829, +11.789] | 6/0/76 |

直白地说：三个 seed 都抓到了更多 failure，而且没有靠把 success 误报率推到 10%附近来换取提升；任务组层面的 95% CI 下界也都已经大于 0。

## 删除参照的对照

`reference_deletion_conformal` 与 `clean_no_reference_conformal` 是严格相同的 alias，分数、阈值、预测和指标均相同。paired conformal 相对这个删除参照的任务组 bootstrap 差为：

| seed | 差值 | 95% CI | better/worse/tie |
|---|---:|---:|---:|
| 20260823 | +12.195 个百分点 | [+5.488, +19.715] | 12/1/69 |
| 20260824 | +14.837 个百分点 | [+7.724, +22.764] | 14/0/68 |
| 20260825 | +13.618 个百分点 | [+6.707, +21.545] | 13/1/68 |

这说明提升不是“共形阈值本身”在 clean 分支上带来的；paired 输入仍增加了有效信号。

## 校准折审计

paired conformal 的每个 fold 均使用约 39--49 个 success task groups；三 seed 的 `(n, k)` 分别为：

| seed | 每 fold 的 `n` | 每 fold 的 `k` | ties |
|---|---|---|---|
| 20260823 | 44、39、43、45、49 | 41、36、40、42、45 | 每 fold 1 |
| 20260824 | 41、42、42、46、45 | 38、39、39、43、42 | 每 fold 1 |
| 20260825 | 47、40、42、46、45 | 44、37、39、43、42 | 每 fold 1 |

每个 fold 的精确 `q`、`nextafter` threshold、报警组数和 tie 计数都保存在 `results.json` 的 `seed_results.*.folds.*.conformal_calibration` 中。外层 test 只在这些阈值冻结以后评分。

## 机制控制与边界

跨任务参照作为预注册控制完整报告如下：

| seed | cross-group 轨迹召回 | row-FPR | group-any FPR |
|---|---:|---:|---:|
| 20260823 | 7.477% | 2.745% | 7.636% |
| 20260824 | 14.953% | 7.411% | 13.818% |
| 20260825 | 5.607% | 2.836% | 8.727% |

因此本实验支持的准确说法是“paired success reference + task-group conformal risk calibration 可行并通过本地资格门”。跨任务控制在部分 seed 也有信号、且一个 seed 的 group-any FPR 超过 10%，所以不能把全部提升归因于“同任务唯一性”，也不能宣称已经完成外部确认。

## 审计与执行记录

- 正式数据评分：1 次；没有第二次结果性重跑。
- Exp91 的 clean/paired CP 锚点重现：通过。
- 数据封存、只读资产哈希、预期计数、零重叠、禁用文本/ID/错误词/长度/位置/Gold/未来信息：通过。
- fit、calibration、outer test 按任务组隔离；阈值只从 calibration success groups 计算。
- 经验 deletion 和 conformal deletion 均通过严格 alias 审计。
- `test_protocol.py` 与 `test_runner.py` 共 15 项单测通过，`py_compile` 通过。

完整原始数字、每 fold 阈值、所有方法指标、bootstrap 比较和审计布尔值见同目录 `results.json`。本结果是一个稳定的实验级 GO；下一步应把它与另一个独立 GO 分开复核，不能直接写成两章论文结论。

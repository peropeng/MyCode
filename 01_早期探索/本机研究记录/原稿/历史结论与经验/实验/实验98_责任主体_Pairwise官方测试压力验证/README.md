# Exp98：责任主体 Pairwise 官方测试压力验证

## 一句话结论

官方测试集上，`pairwise_B` 的 E2 步骤排序相对预注册的 `original_A` 确实提高了，但提高幅度较小，161 个 task group 的 paired bootstrap 95% CI 仍跨过 0。因此本实验结论是：

> `OFFICIAL_HOLDOUT_POSITIVE_NOT_YET_GO`

这不是方法 STOP，也不是责任桥方向 NO-GO；它保留了一个真实但尚未达到稳定 GO 门槛的正向信号。

## 正式运行边界

- 正式运行次数：1 次；固定 seeds：`20260816/20260817/20260818`。
- freeze commit：`f249dc8053002c454efdb4fe817c663af1ba36f4`。
- 训练：731 条记录、716 个 task group。
- official test：163 条记录、161 个 task group。
- train 与 official test 的 task group 交集：0。
- API/token 调用：0。
- official Gold/error 字段只在训练完成后的最终评分 helper 中读取；审计全部通过。

## E2 主结果

主指标是 task-group paired E2 MRR，主比较按冻结协议使用 `pairwise_B - original_A`。

| seed | original_A MRR | pairwise_B MRR | 绝对提升 | 相对提升 | 95% CI（绝对 MRR 差） |
|---|---:|---:|---:|---:|---:|
| 20260816 | 0.309877 | 0.317839 | +0.007962（+0.7962pp） | +2.5694% | [-0.001218, +0.022240] |
| 20260817 | 0.309877 | 0.317839 | +0.007962（+0.7962pp） | +2.5694% | [-0.001186, +0.022333] |
| 20260818 | 0.309877 | 0.317839 | +0.007962（+0.7962pp） | +2.5694% | [-0.001329, +0.022420] |

换成容易理解的话：三次正式计算中，Pairwise 都比 original_A 高约 0.8 个百分点；但按任务组重采样后，合理的不确定范围仍包含“没有提升”，所以不能把它写成稳定 GO。

补充条件：

- `local` MRR：0.279526；删除 bridge 后也是 0.279526，说明提升不是删除条件造成的。
- `recency` MRR：0.328030，高于 pairwise_B；它是预注册的公平描述基线，说明 Pairwise 虽相对 original_A 有正信号，但目前不是整体最强方法。
- `shuffled_B` MRR：0.269701/0.270559/0.278356，三次都低于 pairwise_B，支持概率与匿名角色的对应关系包含真实信号。
- pooled 161 个 task group 的 CI：`[-0.001150, +0.021695]`，仍跨 0。

## 配对方向计数

以下是逐条记录 reciprocal-rank 的 better/worse/tie；置信区间仍按 task group 计算，不能把这些计数当作独立任务数。

| seed | Pairwise vs original_A | Pairwise vs local | Pairwise vs shuffled_B |
|---|---:|---:|---:|
| 20260816 | 7 / 8 / 148 | 84 / 10 / 69 | 106 / 17 / 40 |
| 20260817 | 7 / 8 / 148 | 84 / 10 / 69 | 100 / 24 / 39 |
| 20260818 | 7 / 8 / 148 | 84 / 10 / 69 | 105 / 23 / 35 |

## E1 诊断

三次的 E1 role top-1 数值相同：majority `0.638037`，original_A `0.613497`，pairwise_B `0.625767`。Pairwise 相对 original_A 的逐条 better/worse/tie 为 `5 / 3 / 155`。这说明本实验的 E2 正向信号并不等价于 E1 top-1 已经稳定改善；E1 只作诊断，不能替代 E2 主指标。

## 审计与判定

- 资产 hash：32/32 通过。
- Gold/error 泄漏：未发现；official test 在拟合阶段使用哨兵值。
- train/official task group 泄漏：0。
- deletion=local：三 seed 均通过。
- shuffle negative control：三 seed 均低于 Pairwise。
- 所有审计：通过。
- 预注册 verdict：`OFFICIAL_HOLDOUT_POSITIVE_NOT_YET_GO`。
- `is_experiment_go=false`、`is_final_paper_go=false`、`direction_no_go=false`。

## 残余风险

1. 三个 seed 的点估计完全相同，当前实现的拟合本身是确定性的；seed 主要影响 shuffle/Bootstrap，不能把三行结果误解成三次独立随机训练。
2. 相对 original_A 的提升只有约 2.57%，低于最终论文要求的至少 10%；本实验不能支持 final paper GO。
3. Recency 的 MRR 仍高于 Pairwise，说明 Pairwise 尚未成为最强公平基线上的胜者。
4. 数据仍来自同一 AFTraj 体系，尚未通过真实外部 Agent 框架/环境门。

本实验因此应保留为“官方测试边界上的正向但未确认信号”，不能因为 CI 跨 0 就抹掉，也不能因为三 seed 为正就提前宣称第二个稳定 GO。

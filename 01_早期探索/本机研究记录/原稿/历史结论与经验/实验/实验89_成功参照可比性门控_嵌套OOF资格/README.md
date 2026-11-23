# Exp89：成功参照可比性选择门的嵌套 OOF 资格

本实验只检验一个机制：当前前缀与成功参照的匿名动作类别分布足够相似时使用 paired-reference scorer，否则回退到 clean no-reference scorer。门阈值和报警阈值均在每个 outer fold 的 train/calibration task groups 内选择；outer test 只用于最终评分。

## 结果结论

结果状态是 `POSITIVE_NOT_YET_GO`，不是 GO，也不是 STOP。

数据资格通过：1200 条去重运行、281 个任务组，其中 107 条失败、1093 条成功；数据 seal、历史 Exp29 方向锚点、无泄漏和零 API 审计均通过。

| seed | clean no-reference 召回 / 成功 FPR | gated paired 召回 / 成功 FPR | 相对 no-reference 的任务组配对差 |
|---|---:|---:|---:|
| 20260823 | 3.738% / 2.928% | 23.364% / 8.966% | +21.748 个百分点，95% CI [13.211, 30.488] 个百分点 |
| 20260824 | 1.869% / 3.294% | 23.364% / 6.953% | +24.187 个百分点，95% CI [15.041, 33.537] 个百分点 |
| 20260825 | 0.935% / 1.921% | 28.037% / 13.266% | +28.862 个百分点，95% CI [19.512, 38.431] 个百分点 |

中文解释：成功参照本身确实带来真实提高，三个 seed 都比无参照基线多抓到约 22–29 个百分点的失败；任务组 bootstrap 的 95% CI 下界也都大于 0。这个正信号必须保留。

但可比性门没有完成它的风险控制目标：5 个 outer fold × 3 个 seed 都选择了“全部使用参照”的 sentinel，校准和测试覆盖率都是 100%，因此 gated paired 与 ungated paired 完全相同。seed 20260825 的成功误报率为 13.266%，超过预设的 10% 上限。跨任务组参照也仍相对无参照提高 +15.244、+23.171、+22.561 个百分点，说明当前动作直方图分数没有证明“同任务参照可比性”是唯一增益来源。

因此本实验证明的是：

- `成功参照`在当前历史数据上有稳定、无泄漏、同预算的条件性正信号；
- 本次冻结的 `normalized action histogram + finite quantile gate + no-reference fallback` 没有把该信号转化为稳定的风险合格 GO；
- 不能把它写成最终确认、论文 GO 或方向 NO-GO。

## 停止边界与下一步

本次没有触发 STOP。若未来要停止，绝对对象只能是本 README 对应的这一套固定 comparability formula、阈值网格和回退实现；必须以三个外层测试 seed 的逐 seed 差值、FPR、覆盖率和随机覆盖对照为硬证据。不得据此否定 Exp86 的成功参照正结果。

任何下一轮都必须另行冻结一个理论上不同的最小机制，并继续保留本次相对 clean no-reference 的正向差值作为历史基线。

结果文件见 [`results.json`](results.json)，冻结合同见 [`protocol.json`](protocol.json)。

# Exp102 选择性回退：历史确认与官方边界压力复制

本实验只冻结一个部署动作：把 Exp101 已经固定的 9 特征成本敏感 gate 零调参部署到两个历史边界。Exp97 的 180 rows/168 task groups 与 Exp98 的 163 rows/161 task groups 都曾有历史 arm 结果，因此这里是“gate 机制未见的压力复制”，不是全新确认，也不是 final paper confirmation。

## Stage B 压力复制授权边界

Stage B 已授权唯一一次正式压力复制；前两次因 Harness 问题未进入评分，第 3 次修复后已完成唯一正式运行。外部 Gold 只能在所有 arm 预测、gate decisions 和 shuffle decisions 完整后由最终 evaluator 读取；仍禁止读取任何历史 aggregate 或指标，仍禁止 confirmation/new-confirmation 评分。`runner.py --preflight`/`--dry-run` 只报告未评分；正式结果已写入固定输出。

冻结数据为 Exp96 的 731 条训练记录、716 个 task groups，三个 seed（20260816、20260817、20260818）。每个 seed 先按原 5 个 group folds 生成标准 OOF 的 `original_A`/`pairwise_B` 预测，再用全部 Exp96 OOF gate samples 拟合一份最终 gate。随后每个外部边界各自只在全部 731 条训练记录上拟合一次两个 arm，并对外部记录预测；外部 Gold 只在所有 arm 预测和 gate 选择完成后交给 evaluator。

因此每个 seed 预计进行 10 次 Exp96 OOF arm fit（5 folds × 2 arms）和 4 次边界 deployment arm fit（2 boundaries × 2 arms），共 14 次；三个 seed 共 42 次 arm fit。gate 使用 Exp101 固定的加权 logistic：L2=1.0、lr=0.05、200 epochs、threshold=0.5，不搜参、不调阈值、不增加候选/API/token 预算。

正式调度器严格按“无 Gold 的输入变换 → 两个 arm 预测 → gate decisions → 保持选择率的 shuffle decisions → 最终 evaluator attach Gold → 指标计算”执行。attach 只有在实际预测、两类 decision 覆盖完整且 fit-complete 审计通过时才会调用；aggregate 完成后才以独占方式写唯一输出文件。

## 冻结边界与条件

两个边界都评估 `local`、`original_A`、`pairwise_B`、`recency`、`selective_gate`、`deletion_pairwise_B` 和 `shuffled_gate_decision`。`deletion_pairwise_B` 是部署删除对照，固定为始终使用 `pairwise_B`；外部公平基线则只在该边界的 `local/original_A/pairwise_B/recency` 上按三 seed task-group 平均 MRR 全局选择一次，绝不按 seed 重选。

主指标是 task-group 等权 step MRR，row-equal MRR 只作敏感性；使用 5000 次 task-group paired bootstrap，并报告 R@1、R@3、better/worse/tie、选择/回退率、shuffle 选择率、删除对照、成本和 Gold 隔离审计。

## 判定

单个边界只有在三个 seed 相对该边界唯一最强公平基线全部为正、每个 CI 下界大于 0、删除严格退回 `pairwise_B`、shuffle 保持选择率但性能低于 gate 且审计全部通过时，才是 `STRESS_REPLICATION_GO`。两个边界都通过才是总体 `STRESS_REPLICATION_GO`。

任一边界出现干净正提升但未过全部门槛，保留 `POSITIVE_NOT_YET_GO`，不能因为 CI 跨 0 就停止；混合方向且无稳定负证据为 `STRESS_REPLICATION_INCONCLUSIVE`。稳定全不正时最多写 `STOP_EXP102_FIXED_DEPLOYMENT_ONLY`，只停止这个固定 deployment，不扩大为 pairwise、recency、Exp101 gate 或责任排序方向 NO-GO。最终论文的 10% 相对提升、CI 和真正新外部 confirmation 另行判断。

Stage B 唯一正式输出预注册为 `results/formal_stress_replication_results.json`，最大运行次数为 1，禁止覆盖、重试和调参。第 3 次（也是最后一次授权尝试）已生成该结果文件；前两次 Harness 无效尝试不计入有效方法运行。

## 无效执行记录

前两次已授权尝试均为 Harness 无效，不构成方法 retry 或调参。第 1 次在 Exp96 标准 OOF 审计阶段因布尔门错误失败：三个“外部 Gold 已使用”标志要求为 `False`，旧检查却把它们和正向覆盖字段统一按 truthiness 检查。第 2 次在 Exp98 边界加载阶段失败：冻结 loader 的 boundary 不包含 `official_ids`，runner 错读了不存在的字段。两次都发生在外部 Gold attach 和任何方法指标计算之前；没有生成正式结果文件，`invalid_execution_attempts=2`。第 3 次修复只改变 Harness 审计/loader bookkeeping，不改变方法、数据、特征、阈值、基线或指标，并成功生成唯一正式结果。

## 第 3 次正式结果（唯一有效运行）

运行命令使用冻结的 source/data 路径，退出码为 0，耗时约 82.81 秒。资产 hash 全部匹配；共 3 个 seed、2 个边界，Exp96 OOF arm fit 为 30 次，外部 arm fit 为 12 次，总计 42 次；API/token 调用均为 0。调度审计确认 aggregate 在写文件前完成，Gold 只在最终 evaluator attach，未读取历史 aggregate/指标。

主指标是 task-group 等权 step MRR；row MRR 仅作敏感性。公平基线在每个边界的 `local/original_A/pairwise_B/recency` 中全局一次选择：

| 边界 | 最强基线 | 基线 MRR | gate MRR | 绝对提升 | 相对提升 | pooled 95% CI | 边界判定 |
|---|---:|---:|---:|---:|---:|---:|---|
| Exp97 confirmation（180 rows/168 groups） | pairwise_B | 0.363027 | 0.397362 | +0.034334 | +9.458% | [0.018263, 0.052985] | `STRESS_REPLICATION_GO` |
| Exp98 official（163 rows/161 groups） | recency | 0.328717 | 0.361692 | +0.032974 | +10.031% | [-0.010907, 0.076318] | `POSITIVE_NOT_YET_GO` |

每个 seed 的 gate 相对该边界全局基线 task-group MRR 和 5000 次 paired bootstrap CI：

- Exp97：20260816 为 0.397362−0.363027=+0.034334，CI [0.018461, 0.052083]；20260817 同为 +0.034334，CI [0.018849, 0.052101]；20260818 同为 +0.034334，CI [0.018353, 0.052579]。三 seed CI 下界均大于 0。
- Exp98：20260816 为 0.361692−0.328717=+0.032974，CI [-0.010330, 0.077865]；20260817 同为 +0.032974，CI [-0.010902, 0.076784]；20260818 同为 +0.032974，CI [-0.010898, 0.076309]。三 seed 方向为正，但 CI 均跨 0。

配对 better/worse/tie 在三个 seed 中保持一致：Exp97 相对 `pairwise_B` 为 task-group `17/0/151`、row `17/0/163`；Exp98 相对 `recency` 为 task-group `77/56/28`、row `78/57/28`。Exp97 gate 的 task-group R@1/R@3 为 0.144345/0.453869（row 为 0.138889/0.427778），对应 `pairwise_B` 为 0.102679/0.430060（row 为 0.100000/0.405556）。Exp98 gate 的 task-group R@1/R@3 为 0.093168/0.453416（row 为 0.092025/0.447853），对应 `recency` 为 0.099379/0.357143（row 为 0.098160/0.361963）。

选择率与成本对照：Exp97 选择 `pairwise_B` 为 90.556%、回退 `recency` 为 9.444%；Exp98 分别为 84.663% 和 15.337%。两个边界的 shuffled decision 都保持完全相同选择率；删除 gate 后严格等于 `pairwise_B`。shuffle 的 task-group MRR 在三个 seed 中均低于 gate：Exp97 为 0.363374/0.346487/0.369191，Exp98 为 0.311155/0.304441/0.324840。

## 精确结论

Exp97 历史边界满足三 seed 正向、每个 CI 下界大于 0、删除对照、shuffle 对照和审计门，因此边界级为 `STRESS_REPLICATION_GO`。Exp98 也有稳定的真实正向点估计（+10.031%），但三 seed CI 和 pooled CI 均跨 0，因此保留为 `POSITIVE_NOT_YET_GO`，不是 STOP。

总体精确判定为 `POSITIVE_NOT_YET_GO`：一个边界 GO、另一个边界只有尚未确认的正信号。`direction_no_go=false`；这不是责任排序方向 NO-GO，也不是 final paper GO，更不是全新 external confirmation。最终论文的 10% 门、CI 下界和真正未见外部确认仍需单独满足。

# Exp131：RQ1 状态势能候选快速筛选

本轮执行与评价已完成，候选未通过预声明开发正信号，停止扩大和系数扫描。整个 RQ1 的可靠领先目标仍未达成。

固定开发 pilot 为历史 Exp129 的 120 组中的 32 组，按公开 metadata 和固定 seed 的哈希分层选取，配额为 7/7/6/6/6。fit320 组327条、validation40组、pilot32组按 task_group 隔离。选择清单及收据在 `splits/`，原时点协议 `protocol.json` 保留，后续方法与计算预算由训练前冻结的 `method_protocol.json` 明确。

| 新训条件 | 步骤命中/32 | 角色命中/32 | MRR | 选轮/实跑轮数 |
|---|---:|---:|---:|---:|
| legacy_AB_same_budget | 18 | 26 | 0.7396 | 16/22 |
| C | 22 | 30 | 0.7979 | 8/14 |
| A | 20 | 28 | 0.7813 | 10/16 |
| B | 21 | 29 | 0.7823 | 8/14 |
| AB | 20 | 28 | 0.7760 | 10/16 |

同批冻结四基线为 All-at-Once23、Binary Search13、SDBL21、StepFinder22。All-at-Once的1条无效输出仍保留在32分母；三个单步生成基线没有完整 MRR。旧 V22 同批为20/32，只作为不同历史训练预算的开发参考。

预声明正门要求 AB 至少比最强四基线多2例，即本批至少25/32，并严格高于新训旧AB、C、A、B；两项均未通过。AB 对 C 为0赢2输，对 B 为0赢1输，未新增命中；对 All-at-Once 为5赢8输、净差−3。

候选共用任务和事实上下文生成的二次状态势能 `ψ_j(m)=u_j·m+0.5q_j·m²`。A 将记忆覆盖过程的势能变化分配到真实来源和接收候选，B 比较同一潜在写入省略下动态与冻结记忆轨迹的势能差。原 V19 base/g/P/memory 路径保持，公式和固定 float32 次序见方法协议及 `potential_model.py`。这是模型内部读出改变，未建立真实系统因果或证明创新性。

五条件均从头以 seed20260816 初始化，每轮共用固定组序及 dropout 种子；scaler 只拟合 fit，损失为原 V21 半梯度四槽，加原 V22 fit-only 五层组权重。AdamW lr0.001、wd0.0001、batch16组、clip1、最多25轮、patience6，按 validation 的最早最佳 Top1 保留完整 checkpoint，无 refit。新四条件注册660786参数，旧AB543858，差116928；注册数不等于严格有效容量匹配。

五份 selected checkpoint 全部选完并封存后，评价器才统一读取 pilot 标签。训练、方法、公共特征、split、scaler 和评价器分别记录 source/hash 收据。公共731条 records.gold 始终为 None；训练只读冻结 fit 标签，选轮只读 validation 标签，未读历史180或官方163标签。无新 API、模型下载或基线执行。

首 worker 于北京时间14:16:10启动，统一评价于14:28:37完成。实际训练和评价共同墙钟747.129784秒，包含协调等待及评价启动时间，低于1800秒预算。队列自身712.5秒，评价器计时3.532秒，详见 `results/pilot1/run_wall_clock_receipt.json`。

结果入口为 `results/pilot1/REPORT.md`、`comparison.json` 和 `comparison.csv`。五模型、完整选轮 history、逐条预测、失败列表、四基线切片及历史参考均保存。`verify_delivery.py` 对已保存数据进行排名键前驱计数、分数分解、数值和配对计数、标签范围、checkpoint/scaler/hash、组序及墙钟核验，共71项通过；没有重跑模型或 Gold reader。独立 split 复核与 sol 静态代码审查来源收入 `results/independent_review/`，范围与版本以各自收据为准。

本32组只用于开发筛选，不构成独立显著确认。本轮结果和协议不因后续候选而覆盖；下一轮结构假说、预算及评估规则须另行预声明。

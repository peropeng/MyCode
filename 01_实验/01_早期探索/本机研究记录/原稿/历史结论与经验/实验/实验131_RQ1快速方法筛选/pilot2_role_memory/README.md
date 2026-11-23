# 第二轮：角色记忆与参考写入的受限结构试验

本轮六条件已从头训练并统一评价，预声明门未通过，停止该结构扩展。RQ1 的可靠领先目标仍未完成。本32组已在上一轮使用，仅作继续开发筛选，不是新heldout或独立确认。

| 条件 | 命中/32 | 角色命中/32 | MRR | 选轮/实跑轮数 |
|---|---:|---:|---:|---:|
| legacy_AB_same_budget_CE | 19 | 27 | 0.7509 | 3/9 |
| C | 22 | 29 | 0.7964 | 8/14 |
| A | 17 | 27 | 0.7161 | 4/10 |
| B | 22 | 29 | 0.7964 | 8/14 |
| AB | 17 | 27 | 0.7161 | 4/10 |
| A_skip_B | 17 | 27 | 0.7161 | 4/10 |

同批四缓存基线为AA23、Binary13、SDBL21、StepFinder22。AB需至少25/32并严格胜所有五个本轮控制，三项门均失败。六路均由patience提前停止，20轮上限未触及。

A将1×96全局状态替换成7×96公开角色状态，共享原update与543858参数，每步只写当前角色。共享全局已见角色均值保留间接耦合；A不是additive score，也不构成严格有效容量匹配。B以先前同角色的事实x均值替换候选输入并执行一次write，D/U共享初始改写状态，之后逐未来真实角色动态/冻结更新与读出；该均值只是假设参考，不能视为已知正常输入。A_skip_B保持同一角色状态、参数及previous-role/nonterminal mask，初始干预改为原skip-write。四个新条件和legacy参考均用同一listwise CE，不使用V21四槽SG辅助。

公开无标签预检确认C与旧C同权重eval逐bit相同，单角色A/C及batched/slow replay在3e-6数值等价容差内吻合，跨角色非写状态精确不变，有限梯度与69节点计时通过。self-reference的D/U残差1.49e-8、B残差1.51e-10保留，未修正分数。源、参数、split、scaler、优化与tie规则在训练前冻结。

依据公开计时和此前并发运行的实际波动，六路共同最大轮数在训练前仅一次由25下调20；`budget_selection_receipt.json`记录已有依据，没有补造精确完成时间估计。实际训练队列384.282秒，训练和统一评价共同墙钟约446.19秒，低于1800秒。所有模型/selection hash封存后才读取本轮32组评价标签。

已保存分数组件显示，AB的B在273/411候选非零，原始候选池化RMS约0.0005318，base RMS约3.95386；skip的B RMS约0.00132376，单B约0.0270287。AB/A/skip的完整排序存在差异，本轮Gold排名、Top1/MRR等指标未体现改进。上述RMS仅描述保存分数的大小，不建立退化原因或因果归因，未据此调系数。

结果在 `results/used_development32/`，模型、完整选轮和原始日志在 `results/`。`audit/root_pilot2_result_check.json`为主协调者对保存结果的独立复算PASS，`audit/pilot2_role_memory_review.json`为独立代码审查PASS；没有重跑模型评价。原pilot1的75个冻结资产与根manifest保持原hash。

预测中的 `gold_B_eligible`、`gold_B_eligible_records`、`B_eligible_candidates`描述新B共同的公开参考mask；该mask实际作用于B、AB、A_skip_B，C/A没有启用B，legacy使用其原始非terminal候选范围。所有本轮任务指标仍包含全部32组。

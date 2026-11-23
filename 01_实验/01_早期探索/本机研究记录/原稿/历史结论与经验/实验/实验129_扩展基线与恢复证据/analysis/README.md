# 固定前缀统计分析

`run_analysis.py`只读取已冻结输入、本地真实分数和已发表的API批次结果，不加载模型、不发网络请求。依赖Python 3.10+和NumPy，实验运行使用已有实验124虚拟环境的NumPy 1.26.4。

```powershell
& 'D:/Code/毕设/graduate-thesis-experiments/工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe' -X utf8 'D:/Code/毕设/graduate-thesis-experiments/工作区/1002-exp129-expanded-baselines/实验/实验129_扩展基线与恢复证据/analysis/run_analysis.py' --prefix-count 120 --out 'D:/Code/毕设/graduate-thesis-experiments/工作区/1002-exp129-expanded-baselines/实验/实验129_扩展基线与恢复证据/analysis/prefix120_v1'
```

`--prefix-count`支持20、40、60、80、100、120，始终按冻结manifest顺序取前缀。输出目录必须位于本`analysis/`内且不存在，避免覆盖已有结果。未完成批次不会被当成完成结果：主状态会标为incomplete，并列出缺失来源、未运行/进行中记录及真正可配对的共同任务组。

任务明细保留真实API失败和格式失败，按已尝试失败计分；尚未提交请求的resource block不计零分。已经提交但批次尚未发表最终预测的记录也不提前判失败。本文合法历史OOF分数属于真实预测，但其历史推断耗时保持null。StepFinder共享批次耗时按batch_id去重，不直接累加复制到每行的批次值。

原生完整排序仅适用于本文和StepFinder，按冻结的score降序、匿名结构digest升序、原步号升序校验。角色准确率区分模型原生角色输出与按所选步骤派生角色。EASD范围用真实(role,step)集合评价；cap5未运行，保持null。

主区间只针对严格步骤准确率的四个“本文减文献基线”比较。每个domain×来源层内按任务组有放回抽样，五法共享10000轮索引，seed=20261002；各层按实际n_h/n汇总。报告95%边际区间和四对照Bonferroni98.75%区间，不扩展为所有指标的同时区间。仅对五个层均有共同任务的集合计算主bootstrap。

主要输出为`summary.json`、`task_metrics.jsonl`、`strata_summary.jsonl`、`paired_comparisons.json`、`resource_summary.json`和`报告.md`。`bootstrap_draws.npz`保存全部重采样索引与样本次序，`bootstrap_differences.npz`保存四个比较的差值分布。`analysis_manifest.json`记录读入文件快照hash、脚本hash、版本及输出hash，费用采用真实usage账本中的人民币上下界，非最终发票金额。

`validate_results.py --analysis-dir <已完成输出目录>`从原始预测独立核对角色、金标准排序位置、胜负平、任务均值与全部重采样差值；它通过统计金标准排序键之前的候选数检查排名，不重复依赖分析器的排序函数。验证结果保存在输出目录下`independent_validation.json`，不会修改其他输出或重新运行模型。

# Exp153 候选条件全轨迹上下文

唯一主方法为 AB_GLOBAL。两套既有训练条件分别评价，历史曝光数据不作为新盲测。

入口：`trainer153.py run` → `predict153.py` → `evaluate153.py` → `finalize153.py`。评价前验证全部108拟合模型与69264输出封存，当前evaluator首次目标评价标签加入前冻结评价代码；AF原731标签在训练入口已加载，仅当前fit/val用于loss/选轮。

收尾审计：PASS；完成优化阶段 198/198（source18、AF selection90/refit90），拟合模型108，费用新增0。初始化文件及AF seed汇总副本另列。

前次runtime不合规尝试已归档：71个完成阶段、1个partial阶段、72个物理启动与44个无效模型，目标输出/评分0。有效阶段198加前次71为物理完成269，有效启动198加前次72为物理启动270/授权270。物理optimizer updates为有效updates加已弃用32791..32827的区间：133882..133918；旧partial不作假精确计数。新增2个GPU人工修复案例合计4forward/4backward/0updates，与原CPU fixture累计单列。

结果入口：`compact_summary.json`、`main_decision_packet.json`；完整表及逐任务结果为 `comparison.json`，救回/损坏为 `paired_counterexamples.json`，资源及约束为 `resource_audit.json`、`final_execution_audit.json`。

Holm3为coding363对当轮SF与AF120对当轮SF/缓存AA；Holm8为coding363和AF716各对AB_REF/LOCAL/STATIC/VALUE_PERM。AF重复记录先组内均值；分层只作描述，历史B/143/SF保留原主方法身份。是否支持继续由root决定，不能晋升较好的control。

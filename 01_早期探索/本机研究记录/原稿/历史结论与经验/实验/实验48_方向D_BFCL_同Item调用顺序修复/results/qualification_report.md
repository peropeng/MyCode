# 方向 D：Within-Item Call Ordering Gate 报告

本报告及 results 只提交 hash、索引、bool、计数、聚合和 bootstrap；不包含 raw response、Gold、schema/literal、state 或 inference log。

- 固定样本：120 条，四家族各 30；No=75/120。
- Multi-call support：98 个 task，668 个 item；candidate permutation=119960（预期 119960）。
- SchemaDependencyOrder=73/120；全局最强 baseline=No（75/120）。
- Oracle（No+全部非原顺序排列）=75/120；相对 strongest=0.0000；净救回=0。
- Bootstrap：point=0.0000，95% CI=[0.0000, 0.0000]。
- 候选正逆序：120/120 task 全候选一致；harness task=0。
- 隔离：calls=240400，created=5972，removed=5972，preexisting=0，leak=0。

## 决策：STOP

失败原因：

- ORACLE_RELATIVE_GAIN_BELOW_10_PERCENT
- RESCUED_TASKS_BELOW_8:0
- PAIRED_CLUSTER_BOOTSTRAP_CI_LOWER_NOT_POSITIVE

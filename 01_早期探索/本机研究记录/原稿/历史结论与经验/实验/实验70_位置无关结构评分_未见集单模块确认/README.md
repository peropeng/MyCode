# 实验70：位置无关结构评分未见集单模块确认

本实验只确认实验63开发期已经冻结的 16 维结构评分器在
`planning_single_hard.jsonl` 上的方向性表现。它不是新的特征搜索、阈值搜索、
selector 或 API 实验。

执行顺序固定为：

1. 先提交本目录的 `protocol.md`、`results/preregistered_protocol.json`、runner 和测试的冻结提交；
2. 冻结后才打开 `planning_single_hard.jsonl` 的 chosen/reject 轨迹；
3. `tool_irrelevance.jsonl` 在本实验中完全不打开；
4. 只比较开发期冻结的 `fewer_explicit_errors` Base 与开发集全量拟合的 16 维结构模型 Base+A；
5. 使用三个预注册 orientation seed，不调用 API，不改变预算。

本实验永远不会把探索性正结果写成章节 GO。只有出现真实正向、三个 seed 方向一致或 UUID 多数同向、且无泄漏时，才允许下一轮确认；否则立即科学停止。

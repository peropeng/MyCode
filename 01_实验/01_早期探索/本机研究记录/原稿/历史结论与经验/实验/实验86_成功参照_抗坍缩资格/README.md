# Exp86：成功参照早期预警的抗坍缩资格

本实验是历史 E29 的同数据鲁棒资格复跑，不是新确认集，也不是论文结果包装。历史 E29 的条件性信号为：1200 条去重运行、281 个任务组、5-fold；同题面成功参照失败召回 42.06%，最强历史当前-only Fail-Fast 28.04%，绝对提升 14.02 个百分点（相对 50.0%），成功误停率 8.87%，失败轨迹配对 bootstrap 95% CI 为 [5.61, 22.43] 个百分点。

本轮先独立重跑历史实现，再冻结并测试一个只保留“同任务成功参照 + 动作类别分布”的清洁表示。清洁表示不读取题面文本、任务 ID、resolved/judgement/final judge、错误词、动作/参照长度、显式前缀位置或 role name。`clean_no_reference` 是同一清洁输入契约下的无参照强基线；`clean_cross_group_reference` 在每个 outer train/test partition 内把参照确定性置换到另一个 task group，保持参照候选数且严禁 donor 与目标同组，作为反事实负对照；`reference_deletion` 是显式删参照消融。

预运行修正：最初草案把“同一参照内部打乱动作顺序”作为控制，但清洁表示的归一化直方图对顺序不敏感，因此该控制无效。该草案尚未写结果或评分，已停止并改为跨 task group 参照置换；修正详情在 `protocol.json` 中封存。

冻结细节见 [`protocol.json`](protocol.json)，数据与历史锚点见 [`data_seal.json`](data_seal.json)。数据文件不进入 Git，默认放在 `/Users/peroyang/My/MyWork/tmp/exp86-e29-evidence/`。

判定分层：

- `REPRODUCED_ROBUST_GO`：历史复现、清洁方法相对最强公平无参照基线至少相对 10%、task-group paired bootstrap 95% CI 下界大于 0、三个预冻结 seed 同向、删除/打乱参照使增益消失或明显减弱、泄漏/预算审计通过。
- `POSITIVE_NOT_YET_GO`：有真实清洁正增益但任一 GO 门未过；保留信号，不能写正式 GO。
- `STOP_EXACT_CLEAN_IMPLEMENTATION`：只表示该清洁表示没有可复现增益，绝不等同于 E29 方向 NO-GO；历史正结果仍保留。

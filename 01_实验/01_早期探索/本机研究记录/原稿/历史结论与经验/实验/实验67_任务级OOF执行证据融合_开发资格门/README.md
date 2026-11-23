# 实验67：任务级 OOF 执行证据融合

这是一个离线、一次性的开发资格门，目标是检验“generic PAIRWISE winner 与标签盲执行
结构差分融合”是否比现有 generic 聚合及固定结构启发式更稳健。通过不等于章节 GO。

运行前必须完成 runner/协议/测试冻结，并写入冻结 runner 的 SHA。运行命令从仓库根目录
执行：

```bash
python3 -m unittest discover -s 实验/实验67_任务级OOF执行证据融合_开发资格门/tests -v
python3 实验/实验67_任务级OOF执行证据融合_开发资格门/runner.py
```

runner 只打开 `safety_refusal.jsonl`、`planning_multi_hard.jsonl` 和 Exp65/Exp66 generic
PAIRWISE 结果。五个确认/易集资产始终封存；禁止通过参数替换路径绕过 basename/symlink
保护。没有 HTTP、OpenCode、Keychain 或 API 调用。

结果应同时查看 `oof_result.json` 与 `gate_decision.json`：invalid 输入、OOF cluster 泄漏、
特征泄漏、coverage、swap consistency 或统计门任一失败都是 STOP；`chapter_go` 永远为
false。原始任务、工具、轨迹、候选、UUID 和响应不写入结果。

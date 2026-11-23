# Exp215：ToolMaze 本地重新规划实际小试

冻结的八条流程已在 2026-10-08 09:28:25 UTC 完成。原 `MCPAgent` 的初始化、系统提示、`step` 与文本解析器，原 `ExecutionEngine.run`、`ToolExecutor`、first-touch 扰动、插件以及 `JudgeSystem` 均实际执行。两种方法均未完成固定任务；这批结果验证了本机运行链路，没有证明恢复方法增量。

| 方法 | P0 完整成功 | P2 完整成功 | P2 实际扰动命中 | 原 PRR | 原 RC | 实际工具调用 |
|---|---:|---:|---:|---:|---:|---:|
| ORIGINAL_MCP | 0/2 | 0/2 | 2 | 0/2 | 1.0 | 39 |
| LOCAL_REPLAN | 0/2 | 0/2 | 2 | 0/2 | 1.0 | 39 |

八条均为 `COMPLETE`，没有把不可运行组件记为失败。P0 未暴露扰动，PRR、RC 保持 `null`。P2 各条实际命中一次，均未满足原 Judge 的完整恢复判定。成功前缀在扰动之后的相同工具及参数重复次数均为 0；全流程其他重复调用另外以描述性字段保存，不混入前缀恢复指标。

固定任务为 `C2_task_001`、`C3_task_001`，各自 P0/P2 × 两种方法。固定温度 0、每轮最多 1024 输出、最多 15 轮。没有根据得分更换任务、改提示、修解析器或重抽输出。LOCAL_REPLAN 只在实际工具返回显式 `error` 后追加协议原文指令；C2/P2 触发一次，C3/P2 触发十四次，P0 的 LOCAL_REPLAN 均未触发指令。

实际共 82 次本地生成 POST，78 次原工具调用，344,545 输入 tokens、34,878 输出 tokens，费用 0。每次生成前获取 root 所有共享锁的 byte 0 lease，以原完整消息精确计算 input tokens，满足 `input + 1024 + 1 <= 65536` 才执行。SDK retry 与应用重试均为 0。82 份请求摘要、原始响应字节摘要和实际 usage 已只读核对，未发现不一致。服务、guardian 和共享状态由 root 管理，本实验没有停止或修改它们。

C2 两个无扰动运行在最后 `create_reminder` 调用中输出 `//` 注释，原 JSON 解析器将它当作最终文本，工具没有执行。P2 曾实际切换天气工具，但最终同样没有完成提醒，因此没有取得完整恢复成功。C3 的原方法 P0 出现无效日历参数及不存在的 `manual_availability_check`；其余 C3 运行出现重复构造或虚构的 fallback 工具，耗尽十五轮。这些是正常模型负例，原结果全部保留。

另一个限制来自实际服务：C3/P0 两法的首请求字节规范化摘要相同、输入均为 876 tokens，但首输出文本不同；此时恢复指令尚未触发。因此温度 0 没有使这次本地运行文本严格一致，不能把所有路径差异归因于恢复指令。逐对首输入及首输出摘要位于 `results/summary.json`。

Actor 只接收原 engine 的公开用户 query、公开工具定义和自身实际观测。完整 TaskJSON 的路径和扰动注解只供原 observer engine/Judge 使用，不传给 Actor。`Gold_loads=0` 的计数指未读取外部 AF/confirmation Gold，不表示原 Judge 没有读取其合法的基准注解。插件的提醒、消息、文档、金融等均为本地模拟；没有真实消息发送、支付或服务事务。这不是远程事务恢复证据、CCF A 完整外部方法比较或 RQ1 桥接证明。

新增依赖轮包共 5,427,809 字节，安装在本实验 `deps`，没有修改指定共享 venv。`wheels`、`deps` 作为忽略的复现资产保留。原 source 下 `.py/.yaml` 已在运行前后核对，字节未改。

最短复核入口为 `results/summary.json`、`results/report.json`。各流程目录保存公开输入投影、真实模型请求/原始响应/usage/lease、原工具观测、native trace、原 context history、Actor conversation、原 Judge、原 metrics 和最终行。只读重新汇总可使用：

```powershell
& 'D:/Code/毕设/graduate-thesis-experiments/工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe' -B '实验/实验215_ToolMaze本地重新规划小试/summarize215.py'
```

原生成入口为 `runner215.py`，已由不可覆盖的 `results/attempt_claim.json` 消耗本次调用名额，直接重跑会拒绝。后续不同配置须重新阅读论文、独立冻结并单独记录，不能覆盖本批负例。当前无正的 clean P0 能力，不扩大本配置的效果队列。

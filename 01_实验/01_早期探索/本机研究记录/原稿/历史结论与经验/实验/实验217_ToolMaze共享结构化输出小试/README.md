# Exp217：原生结果保留，完整结构化接口未合格

冻结的八条流程在 2026-10-08 11:30:59 UTC 全部完成。原 `ExecutionEngine.run`、`ToolExecutor`、本地插件、first-touch 扰动和原 Judge 均实际执行。但协议指定的 `response_format.schema` 在本机运行时没有施加完整 Schema，不能将本批当作已通过的结构化接口小试。

| 条件 | 原 Judge P0 | 原 Judge P2 | P2 命中与 PRR | P2 RC | 实际工具调用 |
|---|---:|---:|---:|---:|---:|
| STRUCTURED_CONTINUE | 1/2 | 2/2 | 2 次命中，2/2 | 0 | 28 |
| STRUCTURED_LOCAL_REPLAN | 1/2 | 2/2 | 2 次命中，2/2 | 0 | 28 |

这些是未合格接口下的真实原生观测，原始分数保持不变。C2/P0 两法通过；C3/P0 两法失败，缺少一条完整路径中的 `get_bank_balance_sheet_native`。C3/P0 实际将 broker ledger 与 bank archive 混合使用，没有通过原路径判定。P2 中两法都切换了受扰动的路径，并通过原 Judge；LOCAL 只在实际错误后各追加一次 Exp215 原文指令。两法成功数、工具数、请求数、恢复成本和前缀重复数均没有形成提升。

实际共 64 次生成 POST、56 次工具调用、76,747 输入 tokens、3,254 输出 tokens、8 个流程 controller，费用 0。原始响应、实际 SDK wire 请求和事前 tokenizer 请求逐项核对：64 份字节摘要及 usage 均一致，包含声明 Schema 和 seed 的实际请求体与 tokenizer 体完全相同。共享 byte0 lease 串行，SDK 与应用重试均为 0。未改变 root 的模型服务、guardian 或共享状态。

运行后发现每条最后输出都是合法 JSON，但均不符合声明的 `{final_answer: string}` 或 `{tool, arguments}` 形状，共 8 次形状违规，JSON 解码失败 0 次；实际未观察到虚构工具名，不能据此声称枚举约束已强制生效。生成内容没有被修补或补入参考答案；原 Judge 仍按其原生工具覆盖规则判分。

问题已由当前构建对应的一手源码定位。响应的 `system_fingerprint` 为 `b11459-f498f864f`；既有 Exp194 核验的 parser commit 为 `f498f864fbc0472004ee1c3616c1188c68eb157f`。`server-common.cpp` 的 1303–1310 行表明：`type=json_object` 分支可读取顶层 `schema`，`type=json_schema` 分支读取的是 `response_format.json_schema.schema`。Exp217 冻结协议指定的是后一类型与前一位置，因此完整 Schema 被忽略。完整来源、SHA、代码片段、实际字段和八个违规原始响应入口均保存在 `results/wire_interface_audit.json`。

最小机械修正应保持公共 Schema 不变，将其放到 `response_format.json_schema.schema`。本任务没有以修正为名重跑已取得结果的行，也没有重置 64 POST、8 controller 的累计值；修正后的接口和资源范围须由 root 另行冻结。本批 P2 参照已经 2/2、RC=0，在这两个任务上也没有显示本文恢复收益空间。

四个新 TaskJSON 从作者 Hugging Face 数据集 revision `08b0239a98b0b07839d673f5bc0ef7d836db9296` 下载，共 79,535 字节，保存于本实验 `public_tasks`；共享输入目录未改。Actor 只得到原公开 query、公开广告工具与自身观测；路径、预期参数和扰动标签只供原 observer/Judge 使用。未读取外部 AF/confirmation Gold。插件的消息、会议与金融动作是本地模拟，没有真实外部副作用。

公共输出 Schema 按原 FC 参数定义逐工具构造，没有使用预期参数。双方共用相同初始提示、Schema、seed、输出上限和原执行核心。唯一恢复条件差异是实际显式错误后的固定指令。与 Exp215 的接口差异为原始 JSON 解码为 `AgentAction`、声明 Schema 与显式 seed；不同任务和共同接口调整不能当作恢复方法增量。Exp215 所有原结果未改。

依赖只读复用 Exp215 的 `deps`，没有安装或下载新依赖、模型。原 source 的 `.py/.yaml` 前后 SHA 全部一致。执行器、数据下载、原始模型/工具/扰动/Judge 行均已封存。

复核入口为 `results/summary.json`、`results/report.json` 和 `results/wire_interface_audit.json`。只读重新汇总命令：

```powershell
& 'D:/Code/毕设/graduate-thesis-experiments/工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe' -B '实验/实验217_ToolMaze共享结构化输出小试/summarize217.py'
```

`runner217.py` 已存在不可覆盖的 attempt claim，直接重跑会拒绝。当前没有扩大队列，也不声称正式 CCF A 整体方法比较、RQ1 桥接、真实远程事务恢复或配对因果效果。

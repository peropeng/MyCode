# 实验219：ToolMaze 同一失败状态的继续与局部重规划

固定4题均完成真实配对。原生 Judge 下，`STRUCTURED_CONTINUE` 通过2/4，`STRUCTURED_LOCAL_REPLAN` 通过3/4；配对为1胜、0负、3平。该结果只说明这4题上局部重规划存在一个成功变化，不能据此作确认性、显著性或整体外部基线优势结论。机械修复超过原5分钟窗口，时间门为 **FAIL**；保留超时事实，同时保留后续经授权完成的正常配对结果。

## 比较对象与共同状态

冻结方案见 `protocol.json`。顺序固定为 `C2_task_001`、`C3_task_001`、`C2_task_002`、`C3_task_002`，均为现有公开任务的 P2 永久故障。每题只实际生成一次前缀，执行原生 `ExecutionEngine.run` 至首个真实、显式的扰动错误。封存后从同一失败状态复制两臂，预算均为 `15-prefix_rounds`，包含前缀的每臂总轮数不超过15。

本地模型为现有 `qwen2.5-coder-7b-instruct-q4_k_m`，温度0、seed 20261008、每轮最多1024 output tokens，单槽、65536上下文、SDK/application 重试0。实际 wire 使用原解析器接受的 `response_format.json_schema.schema` 嵌套字段，包含全部公开工具参数 schema。没有修改生成的语义、指定正确替代工具或参数，也没有对模型负结果 reroll。

两臂共同拥有公开任务、公开工具定义、真实前缀消息和输出。LOCAL 仅在实际错误后添加实验215已经冻结的475字符提示，要求保留成功工作、根据实际工具观察重新规划、避免重复已经完成的副作用动作；后续错误沿用同一固定政策。四题各只追加一次该提示。两臂首个续步的实际 tokenizer 计数之差均为91 input tokens，且这一请求的消息差异恰好只有固定提示；轨迹分叉后的全部 token 差异不能都归因于提示。

科学状态覆盖 engine、context/history/data/metadata、executor、first-touch 激活与扰动映射、公开定义顺序、actor 消息和 token/轮数等状态，并保留内部别名。网络池、artifact 路径、observer callback 与物理费用账本作为运行句柄单列排除。每题原状态和两份副本的科学状态 SHA256 相同；真正可变的运行对象在三者间重叠为0。源代码与 literal fixture 数据共享但只读，运行前后检查其指纹。不可变 Enum 不作为共享可变状态计入。

## 逐题结果

`重复` 表示同工具及同参数调用超过首次的次数，包括失败工具重试；它不是实际远程事务次数。`final` 为最终回答是否出现的补充指标，不替换原生 Judge 的 TSR。

| 任务 | 前缀/每臂余量 | CONTINUE Judge | LOCAL Judge | CONTINUE / LOCAL RC | final 两臂 | 重复 CONTINUE / LOCAL | 新分支 POST 每臂 |
|---|---:|---|---|---:|---|---:|---:|
| C2_task_001 | 2 / 13 | PASS | PASS | 0 / 0 | 是 / 是 | 0 / 0 | 5 / 5 |
| C3_task_001 | 2 / 13 | FAIL | PASS | 1 / 0.571429 | 否 / 否 | 7 / 8 | 13 / 13 |
| C2_task_002 | 2 / 13 | PASS | PASS | 0 / 0 | 是 / 是 | 0 / 0 | 6 / 6 |
| C3_task_002 | 4 / 11 | FAIL | FAIL | 1 / 1 | 否 / 否 | 11 / 6 | 11 / 11 |

| 原生指标与补充量 | CONTINUE | LOCAL |
|---|---:|---:|
| TSR | 2/4 = 0.50 | 3/4 = 0.75 |
| PRR，resolved hits / hits | 2/4 = 0.50 | 3/4 = 0.75 |
| RC，原定义的全样本归一化恢复负担 | 0.50 | 0.392857 |
| 出现 final_answer | 2/4 | 2/4 |
| 同工具同参数重复调用总数 | 18 | 14 |
| 故障后重复故障前已成功调用 | 0 | 1 |
| 每臂政策 POST，含共享前缀 | 45 | 45 |
| 每臂政策 input / output tokens，含共享前缀 | 69782 / 2959 | 75500 / 2981 |
| 各臂实际新分支 POST | 35 | 35 |

LOCAL 的唯一 Judge 成功变化在 `C3_task_001`，但该臂没有最终回答，且仍有8次同参数重复模拟调用。`C3_task_002` 的 LOCAL 减少了部分重复失败，却转为重复邮件模拟调用，并重读一次已成功的 account balance；该题原 Judge 仍为 FAIL。原生 Judge 按有效工具路径评判，本批数据上的 PASS 不要求存在最终回答，也不能证明完整参数语义或远程事务恢复。

## 初始失败、修复与时间门

初次运行实际生成两个001前缀，共4 POST、3421 input / 132 output tokens，并已分配6个逻辑 controller。三个状态 hash 本已相等，但隔离审计误将不可变 `StepStatus` Enum 及临时审计投影容器计入共享可变对象，因而两题为 UNKNOWN，另两题未运行也保留 UNKNOWN。原始 `results/` 不覆盖、不改为恢复失败0。

唯一机械纠正见 `copy_audit_repair219a.py`。它从已经封存的完整失败状态恢复前两题，不再次生成或执行前缀；两个构造器只加载公开定义和只读 fixture 元数据。原来分配但未执行的4个逻辑臂槽位复用，账本从4 POST继续。后两题使用一次新前缀与两份直接 RAM 副本。没有增加题、重试、预算、工具或提示。

以下时刻均为2026-10-08 UTC；北京时间在该列加8小时。文件最后写入是已观测的文件系统时间，不冒称额外记录的代码语义完成事件。POST claim 在 SDK 调用前立即写入；实际发包瞬间未单独记录。

| 事件 | 原记录时刻 | 超过原修复截止的秒数 |
|---|---|---:|
| 首次工程错误 | 12:09:28.240894 | — |
| 原5分钟修复截止 | 12:14:28.240894 | 0 |
| 修复文件最后写入 | 12:18:04.019609 | 215.778715 |
| 封存前缀恢复等价证书 | 12:18:06.656250 | 218.415356 |
| 两副本等价与隔离证书 | 12:18:07.470721 | 219.229827 |
| 首次分支 POST 的发送前 claim | 12:18:07.707893 | 219.466999 |
| 首次分支 POST 响应 receipt | 12:18:08.183989 | 219.943095 |
| 固定4题全部完成 | 12:20:47.509032 | — |

时间门 FAIL，原起点、截止与4 POST账本均未重置。首两题修复后的完整性正常后，按已有授权继续固定后两题；全部在用户22:00北京时间死线前完成。正常模型失败和未出现 final_answer 均原样保留。

## 证据、资源与复核

连续物理账本为80次模型 POST：共享前缀10次、新分支70次；修复阶段新增76次。实际共136403 input / 5599 output tokens；两臂政策账本分别计入同一前缀，因此政策总 tokens 比物理总量多9220。逻辑 controller 为12，费用0元，下载、新依赖、新权重、远程副作用与外部 Gold 均为0。

只读复核保存在 `FINAL_EVIDENCE_AUDIT.json`：80份请求、实际 wire、原始响应、usage、请求/响应 SHA 与嵌套完整 schema 逐条一致；80份 schema 独立校验均通过，全部 finish_reason 为 stop。8臂原生 Judge 与原指标按封存轨迹回读重算一致；4份复制证书及公开参数 schema 核对通过。303份原 `.py/.yaml` 源文件（含272个 plugin 文件）当前 SHA 与运行前清单一致，冻结 protocol/runner/transport/validator 与 claim SHA 一致。共338项证据核对通过；复核没有执行模型或工具。

关键文件：

- `results/report.json`：初始 UNKNOWN 与4 POST账本。
- `copy_audit_repair219a/results/report.json`：修复后的固定4题完整结果与连续80 POST账本。
- `results/paired_tasks/*/prefix_once/` 与修复结果内的 `prefix_once/`：唯一实际前缀、完整状态与切点。
- 修复结果内 `corrected_copy_certificate.json`、`copy_certificate.json`：等价与隔离证书。
- 各臂 `native_full_trace.json`、`original_judge.json`、`original_metrics.json`、`model/*`：实际轨迹、原判据与逐次 wire/raw 证据。

这是内部局部重规划对照，不是 AgentRewind 复现，也不占“正式出版、CCF A、核心完整且本机非零”的外部整体基线名额。实验215、217及217b的失败和成功边界继续保留；本次不覆盖旧结果。

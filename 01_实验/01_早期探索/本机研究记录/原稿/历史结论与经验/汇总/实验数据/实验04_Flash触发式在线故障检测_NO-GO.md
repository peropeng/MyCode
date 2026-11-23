# 实验04数据与审计附件

- 当前严格状态：**NO-GO**
- 原编号：`E013`
- 机器资产：`实验/实验04_Flash触发式在线故障检测/`
- 主结论：`结论/结论04_实验04_Flash触发式在线故障检测_NO-GO.md`

本文件保存详细指标、原结果摘录和审阅证据；研究判断以主结论为准。

## 原实验结果与指标

以下内容直接并入原结果/报告；它们保留当时数字和判断，但最终等级以本文件开头的严格状态为准。

### 来源：旧实验裁决__实验__失败与停止__E013_Flash触发式在线故障检测_分支快照_17eb42d__结果.md

### P2 Pilot 结果记录

#### 当前状态（2026-08-20）

真实 `deepseek-v4-flash` 运行已经完成全部 480 条请求。私有响应聚合为 `478 ok + 2 invalid_step`；两条无效结构化响应都保留为解析失败（不静默补成 `none`），每种方法各一条。原始 prompt、请求、响应、标签映射和 API key 均未写入 tracked 文件。

选择与请求合同仍是冻结版本：30 个 confirmation/test task clusters、10 个 dev clusters、60 条 test trajectories、10 个 repository families、每条轨迹每种 Flash 方法最多 3 次调用。`results.json` 是这次真实运行的 v1 聚合；[v2_dev_schedule_audit.json](v2_dev_schedule_audit.json) 是仅使用已有响应生成的独立开发集 schedule 审计。

##### 选择摘要

| 项目 | 当前值 |
|---|---:|
| confirmation/test task clusters | 30 |
| dev task clusters | 10 |
| confirmation/test trajectories | 60 |
| repository families | 10 |
| SFT / Verifier source rows | 491 / 2,636 |
| prepared requests（Periodic + Triggered） | 480 |
| completed responses | 480 / 480 |
| response status | 478 `ok` / 2 `parse_error`（`invalid_step`） |
| model | `deepseek-v4-flash` |
| max_tokens | 4096 |
| bounded_concurrency | 4 |

`selection_manifest.json` 只含源文件哈希、task/trajectory/repository 哈希和计数；私有 cache 保持 ignored，不作为提交内容。

#### v1 真实 API 结果（confirmation/test）

| 方法 | 75% 前失败截获率 | success 误报 | 平均提前量（全部失败） | API/轨迹 | Token/轨迹 | 延迟/轨迹（ms） | 解析率 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Rule-only | 1.000 | 1.000 | 0.7341 | 0 | 0 | 0 | N/A |
| Periodic-Flash | 0.8667 | 0.5333 | 0.3649 | 3 | 10,394.5 | 10,645.5 | 1.0000 |
| Triggered-Flash | 0.6333 | 0.4667 | 0.4311 | 3 | 5,154.7 | 9,116.8 | 0.9944 |

这次 v1 的明确结果是：Periodic-Flash 截获率 `26/30=.8667`、success 误报 `16/30=.5333`；Triggered-Flash 截获率 `19/30=.6333`、success 误报 `14/30=.4667`，两者平均都是 3 次调用/轨迹。结构化解析失败为 2 条 `invalid_step`，不被视为正常无告警。

Gate 结果为 **NO-GO**：最小任务/仓库/解析率门槛通过，但 Triggered-Flash 的 success 误报门槛失败、相对最强同预算基线为 `-0.3667`、paired bootstrap 下界不大于 0，因此 `go=false`。本轮不执行新的 API 调用，不调整冻结研究方向。

#### v2 开发集 schedule 审计（诊断，不是方法）

仅用已有 480 条响应做离线聚合，在 dev split 上选出 `last-trigger + threshold=.75`：每条轨迹只保留冻结 Triggered-Flash schedule 中 `event_step` 最大的那一次响应，因此平均调用数为 1。

| split | 失败截获率（75% 前） | success 误报 | API/轨迹 | 计数 |
|---|---:|---:|---:|---|
| dev（选择集） | `3/10=.30` | `1/10=.10` | 1 | 20 条选中响应均 `ok` |
| sealed test（只审计） | `4/30=.1333` | `6/30=.20` | 1 | 60 条选中响应均 `ok` |

`last-trigger` 是事后、非因果策略：选择最后一个触发点需要知道后续轨迹事件，不能作为在线方法或研究方法声明。sealed test 数字只是对该诊断策略的泛化检查，不能回写为阈值/调度选择依据；详细的分子分母、来源哈希和审计边界见 [v2_dev_schedule_audit.json](v2_dev_schedule_audit.json)。因此 v2 也不构成研究 Go。

#### Sol/high 审阅：数据合同与 M1 缺陷（本次不修）

审阅指出，当前 M1/可见证据层还不能承担过程故障真值合同：

- SFT success 与 Verifier unresolved 来自混杂的来源/终局语义，配对并不等于同一过程故障标签；
- 终局 `resolved` 只表示最终状态，不等于过程 fault，也不能定义 first-fault 区间；
- view 被 edit 规则匹配会造成动作类型/可见证据误判；
- `visible_evidence` 对源码和日志按关键词扫描，源代码/日志中的 `error`、`test`、`edit` 等词可能污染过程证据。

这些问题阻断了把 480 条 Flash 响应解释成正向方法证据。本次收尾只把它们记录为审阅结果，不修 M1、不重定义数据合同、不改变研究方向；现有 480 条响应只作为冻结管线的**负证据**，不算研究 Go。若未来继续实验，必须先独立修复并重新验收该数据合同。

#### 解释边界

本 Pilot 是自然轨迹 shadow 检测，不包含实际 Agent loop 纠偏、回退或成功率干预。即使检测指标达到 Gate，也只能支持“在线故障检测 RQ1 Pilot Go”；不能声称“纠偏提高解决率”，也不能替代 P1 受控三类故障或 P3 自然失败最小干预。

## Sol审阅原文

### 1. 标签和目标污染

- 历史 `resolved`/成功终局标签只能描述结果，不是过程故障 Gold。
- 成功参照偏离、错误词、最后触发词和文件命中只是风险或相关性证据；没有同状态干预不能称责任动作。
- `last-trigger` 等只读末步或未来字段会造成未来泄漏；必须按执行前缀建立递增证据。
- 原生测试通过是一个可执行探针，不是语义因果 Oracle；AST/语法检查也只能证明语法状态。

## 历史综合复盘

### E013 Flash 触发式在线故障检测（P2）

- **口语总结：**Flash 不是“在线监控算法”，API 触发也不能替代可执行探针。
- **回答了什么：**语义诊断在触发条件、提示 schema 和证据引用上的失败边界；Flash 试验未形成可靠在线主结果。
- **不能说明什么：**不能说明 `deepseek-v4-flash` 能发现自然故障、生成可靠修复或提高责任定位。
- **只能说明什么：**只说明 API/语义层必须被形式证据门控，且 no-API/Periodic-API 必须是公平基线。
- **为何失败/降级：**在线资产、触发覆盖和结果一致性不足；有“零编辑/不稳定输出”负证据。
- **Sol 审核办法：**Flash 仅作必要时语义诊断，要求引用事件 ID/探针；随后实验未解决资产 STOP。
- **可复用价值：**提示 schema、API 预算和证据绑定规则；模型名不是创新。

## 来源索引

- `旧实验裁决__实验__失败与停止__E013_Flash触发式在线故障检测_分支快照_17eb42d__结果.md`

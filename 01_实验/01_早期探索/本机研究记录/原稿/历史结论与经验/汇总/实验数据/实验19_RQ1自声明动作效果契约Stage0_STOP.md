# 实验19数据与审计附件

- 当前严格状态：**STOP**
- 原编号：`E035`
- 机器资产：`实验/实验19_RQ1自声明动作效果契约Stage0/`
- 主结论：`结论/结论19_实验19_RQ1自声明动作效果契约Stage0_STOP.md`

本文件保存详细指标、原结果摘录和审阅证据；研究判断以主结论为准。

## 原实验结果与指标

以下内容直接并入原结果/报告；它们保留当时数字和判断，但最终等级以本文件开头的严格状态为准。

### 来源：旧实验裁决__实验__失败与停止__E035_RQ1自声明动作效果契约Stage0__PREREGISTRATION.md

### RQ1 自声明动作效果契约自然在线 Stage0

状态：`PREREGISTERED_NOT_RUN`（2026-08-21 冻结）。

本目录只承载一个隔离的 live-loop 实现预检。它不修改 RQ1 研究方向，不声称算法收益，不构成科学 Go/No-Go。运行条件、任务、工具字段、监测规则、预算、密钥环境名和验证器参数以同目录 `config.json` 为唯一冻结配置；必须先提交该配置，之后才允许添加 runner。

#### 冻结比较

- 三个既定 Django SWE-bench 任务：10880、10999、11265；不按模型输出、告警或结果改选。
- 同一个 `deepseek-v4-flash`、温度 0、每个条件最多 12 个模型动作。
- `vanilla` 的 bash 工具只有 `command`。
- `contract_monitor` 的 bash 工具固定要求 `command`、`expected_effect`、`target_paths`、`success_criterion`；后三项均为动作前由 Agent 自声明的文本/路径字段。
- 监测器只读取当前/历史已经出现的命令返回码、tracked diff 与声明路径。仅以下两类触发：非零返回码与声明的成功预期冲突；或非空 `target_paths` 之外出现 tracked changed path。
- 触发后追加固定结构化 observation，包含 event id、完整声明合同、实际 returncode、changed paths、mismatch types 和 `[last healthy step,current step]` 候选区间。不得自动回滚，不执行 `success_criterion`，不得读取 gold patch、test_patch、resolved 或未来状态。

#### 安全与隔离

唯一允许的密钥来源是运行进程的 `OPENCODE_GO_API_KEY`。runner 不把它写入文件、配置、manifest、prompt、trajectory 或日志；调用模型时只可在内存中映射给 `OPENAI_API_KEY`。自定义环境必须从 prompt template vars 和 bash 子进程环境中移除所有 secret-like 变量。所有源仓库复制到本实验 ignored `runtime/` 后才执行；源目录必须保持不变，任务 workspace 在每个条件结束时必须恢复。

#### 结果边界

`--dry-run` 只做资产复制前的可收集性检查，不需要密钥，也不调用 API。Stage0 结果只能报告资产、环境、接口和安全检查是否可行；未运行的 API loop 不得伪造为结果，更不得称作科学 Go。

## 历史综合复盘

### 既有复盘

- **E035 自声明动作效果契约 Stage0：**回答自声明契约能否作为自然轨迹输入格式；不能说明 Agent 自声明真实可靠；只能说明预注册资产合同。自然资产不足，Stage0 STOP。

## 来源索引

- `旧实验裁决__实验__失败与停止__E035_RQ1自声明动作效果契约Stage0__PREREGISTRATION.md`

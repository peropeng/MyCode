# 实验21数据与审计附件

- 当前严格状态：**STOP**
- 原编号：`E037`
- 机器资产：`实验/实验21_RQ1阶段承诺行动资格/`
- 主结论：`结论/结论21_实验21_RQ1阶段承诺行动资格_STOP.md`

本文件保存详细指标、原结果摘录和审阅证据；研究判断以主结论为准。

## 原实验结果与指标

以下内容直接并入原结果/报告；它们保留当时数字和判断，但最终等级以本文件开头的严格状态为准。

### 来源：旧实验裁决__实验__失败与停止__E037_RQ1阶段承诺行动资格__结果.md

### 实验 37：阶段承诺 Agent 行动资格预检结果

状态：ACTOR_QUALIFICATION_NO_GO；formal_rq1_go=false。

#### 1. 运行概况

公开 dry-run 结果为 DRY_RUN_COMPLETE，未调用 API；两个固定任务的 source、validator Python 和问题陈述均可用。资格运行包含 2 个任务和 2 个可解析 commitment。

两条轨迹均完成 EXPLORE 4、PATCH 3、VALIDATE 2 个阶段动作。django__django-11292 的动作分布为 read 5、search 2、shell 2；django__django-11433 为 read 4、search 2、shell 2。后者在 PATCH 阶段另有 1 次缺少 action 字段的解析错误。公开报告只保留这些聚合事实，不展开 commitment、题解或 raw 事件原文。

#### 2. Gate 结果

| Gate | 结果 |
| --- | --- |
| 任务数 | 2/2 |
| commitment 解析 | 2/2 |
| replace 且产生 tracked edit | 0/2，失败 |
| edit 后 VALIDATE shell | 0/2，失败 |
| focused verifier 完成 | 2/2，均 FAIL |
| source unchanged | 合格 |
| workspace restore | 合格 |
| Agent prefix 泄漏 | 0，合格 |
| 密钥泄漏 | 0，合格 |

两个任务都没有产生资格 Gate 所需的真实 replace/tracked edit，因此也没有满足 edit 后验证 shell 条件。虽然 focused verifier 均已完成，但两次结果均为 FAIL；资格合同本身要求完成而不要求通过，仍不能弥补前述两个硬失败项。

#### 3. 冻结结论

按预注册规则，任一任务未满足 Gate 即停止此 scaffold；本轮明确为 ACTOR_QUALIFICATION_NO_GO。停止继续调同一 deepseek-v4-flash 自由修复脚手架，不把本结果解释为对实验 34 受控机制的否定。

本资格结果不是 RQ1 Go，也不支持 monitor 收益或方法效果结论。报告仅汇总公开 JSON 与事件计数，未复制承诺文本、题解或 raw 原文。

## 历史综合复盘

### 既有复盘

- **E037 阶段承诺 Agent 行动资格：**回答阶段承诺字段是否能筛出可审计动作；不能说明“承诺后执行”具有因果效力；只能说明资格预检。仍缺真实两态动作。

## 来源索引

- `旧实验裁决__实验__失败与停止__E037_RQ1阶段承诺行动资格__结果.md`

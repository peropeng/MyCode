# 实验20数据与审计附件

- 当前严格状态：**STOP**
- 原编号：`E036`
- 机器资产：`实验/实验20_RQ1结构化编辑动作契约/`
- 主结论：`结论/结论20_实验20_RQ1结构化编辑动作契约_STOP.md`

本文件保存详细指标、原结果摘录和审阅证据；研究判断以主结论为准。

## 原实验结果与指标

以下内容直接并入原结果/报告；它们保留当时数字和判断，但最终等级以本文件开头的严格状态为准。

### 来源：旧实验裁决__实验__失败与停止__E036_RQ1结构化编辑动作契约__结果.md

### 实验 36 结果

状态：`DEV_NO_GO_ACTION_STARVATION`

#### 观测

4/4 运行均完成每条 16 步；contract 字段解析为 `32/32`。动作分布如下：

| 条件与任务 | 动作分布 |
| --- | --- |
| contract / `django__django-11292` | `shell` 13，`read` 3 |
| vanilla / `django__django-11292` | `shell` 14，`read` 2 |
| contract / `django__django-11433` | `shell` 14，`read` 2 |
| vanilla / `django__django-11433` | `shell` 11，`read` 4，`search` 1 |

合计：`shell` 52，`read` 11，`search` 1，`replace` 0；`0` tracked edit，`0` mismatch，4 条无 final。focused verifier：vanilla `0/2`，contract `0/2`。source unchanged，workspace restored。

#### 判定与边界

结构化工具未消除 Flash 行动饥饿，是对当前 Flash Agent 主体/scaffold 适配的有效负结果；不证明动作效果契约理论总体无效，不计正式 RQ1 Go，与实验 35 共同触发独立审阅。不加步数、不换任务。

边界：Agent prefix 不读 `test_patch`；posthoc evaluator 读 `test_patch`。

## 历史综合复盘

### 既有复盘

- **E036 结构化编辑动作契约：**回答结构化编辑是否更适合核对路径/哈希/编译；不能说明结构化编辑就是责任 Gold；只能说明编辑格式和 mismatch 分类。开发复验没有形成独立数据。

## 来源索引

- `旧实验裁决__实验__失败与停止__E036_RQ1结构化编辑动作契约__结果.md`

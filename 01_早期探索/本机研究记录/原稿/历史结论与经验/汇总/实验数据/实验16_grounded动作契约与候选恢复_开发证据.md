# 实验16数据与审计附件

- 当前严格状态：**开发证据**
- 原编号：`E032`
- 机器资产：`实验/实验16_grounded动作契约与候选恢复/`
- 主结论：`结论/结论16_实验16_grounded动作契约与候选恢复_开发证据.md`

本文件保存详细指标、原结果摘录和审阅证据；研究判断以主结论为准。

## 原实验结果与指标

以下内容直接并入原结果/报告；它们保留当时数字和判断，但最终等级以本文件开头的严格状态为准。

### 来源：旧实验裁决__实验__开发证据__E032_RQ1_grounded动作契约与候选恢复__reports__pilot_result.md

### Grounded contract + candidate sandbox Pilot 结果

结论：**PILOT DIRECTIONAL GO**。这是开发性方向 Go，不计 30-task 正式 Go。

#### 冻结比较

- Vanilla continue；
- 每仓一个固定单 probe 的 Periodic verification；
- 实验 31 的 Ungrounded Full：deepseek-v4-flash 自由生成 contract 并选择 recovery；
- Grounded sandbox：从 proposed action 编译合同，并在同一 checkpoint 比较 APPLY_INTENDED 与 ROLLBACK。

6 个任务、3 个独立 runtime 仓库、三类各 2。任务和 mutation 均未复用实验 31。旧模块基线实际调用 deepseek-v4-flash 18 次（6 contract + 12 decisions），全部有效；Grounded 不使用 LLM 自由生成实体。

#### 主结果

| condition | fault completion | clean 不必要干预 | 12 个成对决策正确 |
|---|---:|---:|---:|
| Vanilla | 0/6 | 0/6 | 6/12 |
| Periodic | 2/6 | 0/6 | 8/12 |
| Ungrounded Full | 2/6 | 2/6 | 6/12 |
| Grounded sandbox | 6/6 | 0/6 | 12/12 |

Grounded 相对最强基线绝对多完成 4/6；三类中的 SPEC_OR_PARAMETER 和 CODE_ARTIFACT 均单独为正，ENV_OR_FILE_STATE 与强基线持平。冻结 Gate 全部通过。

#### 机制证据

- 四个非空编辑任务：Periodic 没有捕获；Ungrounded Full 检测后都选择 ROLLBACK，恢复健康但放弃 intended edit；Grounded 的 APPLY_INTENDED 候选同时满足 compiled target hash 和 targeted probe，因此完成 4/4。
- 两个原子文件状态任务：APPLY_INTENDED 与 ROLLBACK 产生相同 post-state，按 API 前冻结的候选等价规则合并，选择成本更低的 ROLLBACK，完成 2/2。
- 六个 clean 对照：actual state hash 与 targeted probe 均匹配 compiled contract，Grounded 全部 CONTINUE，没有干预。

#### 可以与不可以声称的结论

可以声称：在新的 6 个受控软件仓库动作故障上，把自由文本预期替换为 action/tool-schema grounded contract，并以同 checkpoint 的有限候选验证代替默认 rollback，出现明确方向性增益。

不可以声称：

- RQ1 已正式 Go；
- 对自然 Agent 轨迹或任意软件任务外部有效；
- 已达到统计显著性；
- RQ2 已完成。

#### 扩样前风险

当前 Grounded 能从 proposed action 得到精确 intended operation，因此受控工具执行偏差是其最匹配场景。下一阶段正式试验必须加入至少 30 个独立动作实例、更多 test nodes 和非平凡 intended edits，并比较相同两候选预算；不能把同一 mutation 的文本变体当独立任务。正式 Gate 仍要求任务级 paired bootstrap CI 下界大于 0、至少 10pp 增量、clean 伤害不超过 10pp，且至少两类单独为正。

## Sol审阅原文

### 3. RQ1 缩小建议

Sol 建议以“动作效果契约是否能比固定周期探针更早、更少成本地发现可执行状态转变”为开发主假设，保留 2–3 个模块：

1. 事件和状态的可递增过程证据；
2. 形式探针/状态哈希优先，必要时才证据门控语义诊断；
3. 面向 RQ2 的保守区间或证据交接，不在 RQ1 直接宣称责任动作。

这只是更可检验的研究设计，不是文献直接保证的结论。强制加入 post-hoc/LOPO 周期调度、随机相位、动作触发和泄漏审计，才能区分方法增益与检查位置覆盖差异。

## 历史综合复盘

### 既有复盘

- **E032 grounded 动作契约：**回答将声明动作与目标状态/恢复证据绑定有协议价值；不能说明 grounded 结果可自然泛化；只能说明证据字段和 clean/fault 门。

## 来源索引

- `旧实验裁决__实验__开发证据__E032_RQ1_grounded动作契约与候选恢复__reports__pilot_result.md`

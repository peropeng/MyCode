# 实验27数据与审计附件

- 当前严格状态：**Stage0 STOP**
- 原编号：`E043`
- 机器资产：`实验/实验27_RQ1双竞争编辑批契约最终实验/`
- 主结论：`结论/结论27_实验27_RQ1双竞争编辑批契约最终实验_Stage0STOP.md`

本文件保存详细指标、原结果摘录和审阅证据；研究判断以主结论为准。

## 原实验结果与指标

以下内容直接并入原结果/报告；它们保留当时数字和判断，但最终等级以本文件开头的严格状态为准。

### 来源：旧实验裁决__实验__失败与停止__E043_RQ1双竞争编辑批契约__方案.md

### Exp43：双竞争编辑批契约最终受控实验（Stage0 预注册合同）

#### 1. 研究命题与论文边界

RQ1 只检验一个可证伪的窄命题：在真实 Agent 轨迹中，两个真实、同一目标文件、确实改变状态的编辑形成一个编辑批次后，结构化 `batch_contract` 能否在批次结束处识别动作执行效果违约，并给出可交给 RQ2 的批级状态证据。这里的故障是受控的 action-effect violation，不是自然 Agent 故障，不等价于责任主体预测，也不声称已经完成在线故障检测的自然有效性。

样本严格继承 Exp11 的 34 个冻结记录：8 个仓库、33 个 repository-target 簇和每条记录的冻结检查点。每条记录只使用 Exp11 已确定的两个真实同文件编辑；窗口从原检查点起至第二个候选编辑，保留窗口内所有真实 editor 事件，不添加人工 distractor。不得因 Stage0 资格或 sealed 结果替换任务、仓库、检查点、候选位置或故障类。

本实验结论最多是 `RQ1_CONTROLLED_BATCH_EFFECT_GO` 或 `RQ1_CONTROLLED_BATCH_EFFECT_NO_GO` 的受控方向性证据。无论哪一标签，`formal_rq1=false`、`natural=false`；它不能直接升级为论文最终结论。

#### 2. Stage0 资产资格（sealed 前）

`frozen_assignment.json` 是唯一冻结选择输入。按仓库分层后，以 `SHA256(instance_id)`（同 hash 时以 instance_id）确定顺序，分配 candidate1/candidate2，严格 17/17。A/B/C 只在 private evaluator 字段中确定，按仓库、候选位置和同一 SHA 的确定性平衡规则分配，A、B、C 各至少 8 条且尽量平衡。`responsible_position`、`later_same_file_position`、fault slot/class 和 Exp11 选择证据只能出现在 private evaluator 区域；方法输入边界不能读取它们。

Stage0 必须在临时 workspace 中对每条冻结记录完成三项检查：

1. 从该仓库 base commit 重建 `window_start - 1` 检查点，状态 hash 与 Exp11 冻结 checkpoint hash 一致；
2. 从同一 base commit 重放至 candidate1 前后，目标文件状态 hash 确实变化；
3. 从同一 base commit 重放至 candidate2 前后，目标文件状态 hash 确实变化。

Stage0 只读 Exp11 runner 的解析、编辑重放和状态 hash 函数以及既有本地仓库资产；不注入 A/B/C，不执行任何方法、基线、探针、测试标签或成绩计算。任一检查失败必须输出 `STAGE0_STOP` 和原因，保留原 34 条样本，不得换样本。

#### 3. 受控违约与拟议方法

sealed 阶段为每条记录生成三种事先冻结的 action-effect violation：

* A：两个声明编辑完成后，在目标文件追加语法破坏，语法确认失败；
* B：两个声明编辑完成后新增一个未声明路径，目标文件保持声明效果，但 allowed-path 不变量失败；
* C：两个声明编辑完成后向目标文件追加仍可编译的未声明内容，使干净批次目标 hash 不一致。

`batch_contract` 只在第二候选编辑后做一次结构化确认：声明路径集合、目标文件预期 hash、目标语法确认和批次状态证据。干净批次不得告警；三类违约均必须告警。告警输出仅包含 RQ2 所需的 `batch_start`、`batch_end`、两个候选动作、受影响路径、批状态证据和确认探针；禁止输出单动作 mismatch、fault step、fault class 或 responsible agent。

#### 4. 比较设计（sealed 前冻结）

完整报告下列强基线及成本：state/hash reads、expensive probes、wall-clock seconds。

* **Two-probe fixed periodic**：8 个候选位置中枚举全部 `C(8,2)=28` 个 two-probe schedule；post-hoc 最优只作非部署上界，不能冒充泛化结果。
* **LOPO periodic**：每次只在其余 7 个仓库选择最佳 schedule，再在留出的仓库测试；禁止用留出仓库结果调参。
* **Random phase**：完整报告四个固定 phase `(0,4)`、`(1,5)`、`(2,6)`、`(3,7)`，不得事后挑选一个。
* **Action-triggered**：恰在同两个真实候选编辑之后各做一次同类型 probe，最多两次；不得偷看故障类或最终结果。

#### 5. 全部 Gate 与停止条件

资格 Gate：有效任务 `>=30`、仓库恰为 8、repository-target/checkpoint 簇 `>=30`（预期 33）、A/B/C 各 `>=8`、每条有两个真实状态改变的同文件编辑；TC-VIR `>=0.80`、clean FPR `<=0.10`；完整性、样本冻结和输入泄漏均为 0。Stage0 任何一项不满足即 `STAGE0_STOP`，不进入 sealed。

研究 Gate：相对 LOPO periodic 的敏感性绝对提升 `>=0.10`；repository-cluster bootstrap 10000 次、seed `20260820` 的 95% CI 下界 `>0`；至少 6/8 仓库为正；post-hoc 最优 periodic 若追平或超过 `batch_contract`，立即 NO-GO。相对 action-triggered 的 recall 不低于 0.05 以内，并且 expensive probes 或 wall-clock 至少降低 20%。告警区间 coverage `>=0.80`，宽度至少覆盖两个真实候选，延迟不超过一个候选步；clean FPR、TC-VIR、方法输入完整性和泄漏仍满足资格 Gate。

任一研究 Gate 失败、任一 sealed 运行完整性失败、任何禁用字段进入方法、或发现样本/规则在结果后改变，立即停止并标记 `RQ1_CONTROLLED_BATCH_EFFECT_NO_GO`。满足全部研究 Gate 才能标记 `RQ1_CONTROLLED_BATCH_EFFECT_GO`；这两个标签都保留 `formal_rq1=false`、`natural=false`。

#### 6. 入口与执行顺序

```bash
python3 qualify_assets.py --prepare-assignment
python3 qualify_assets.py --qualify
python3 -m py_compile qualify_assets.py test_qualify_assets.py
python3 -m unittest discover -s . -p 'test_*.py' -v
### Stage0 通过且主线程书面验收后，才另行实现并执行一次 sealed 方法；本目录当前没有 sealed 入口。
```

`qualification.json` 是 Stage0 唯一输出，包含 assignment/Exp11/source 的 hash、资格统计、逐任务 hash 化检查和停止原因，不包含原始 editor 文本。Stage0 结束后不得自行执行任何 A/B/C 注入、在线 API、方法成绩或基线成绩。

## Sol审阅原文

## Sol独立审阅意见及后续验证

## 来源索引

- `旧实验裁决__实验__失败与停止__E043_RQ1双竞争编辑批契约__方案.md`

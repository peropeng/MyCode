# 实验25数据与审计附件

- 当前严格状态：**资产STOP**
- 原编号：`E041`
- 机器资产：`实验/实验25_RQ1动作状态效果契约独立确认/`
- 主结论：`结论/结论25_实验25_RQ1动作状态效果契约独立确认_资产STOP.md`

本文件保存详细指标、原结果摘录和审阅证据；研究判断以主结论为准。

## 原实验结果与指标

以下内容直接并入原结果/报告；它们保留当时数字和判断，但最终等级以本文件开头的严格状态为准。

### 来源：旧实验裁决__实验__失败与停止__E041_RQ1动作状态效果契约独立确认__方案.md

### Exp41：RQ1 动作—状态效果契约独立确认

状态：`STAGE_A_ASSET_FREEZE_ONLY`；本文件与 `selection_contract.json`、`config.json` 在任何方法或基线运行前冻结。

#### 研究问题和边界

RQ1 只问：真实软件 Agent 执行状态改变动作后，能否把 proposed action 编译成 repository-grounded expected effect，并依据动作前后仓库状态和可执行后果发现效果不一致、输出候选风险区间。它不主张一般语义正确，不把终局 resolved 或任务成败当作在线标签，也不预测 responsible agent。Stage A 只做资产冻结和资格探针，不构造 fault、不运行方法、不运行基线、不计算区间成绩。

CCF-A 锚点严格限于：OOPSLA2026 的过程事件、检查点和前缀监测；ACL2026 OS-Sentinel 的形式验证器与语义 Judge 职责分离；ACL2026 ARCHITECT 的沙箱执行和干预证据。它们是设计边界和证据链锚点，不是本文动作效果契约的原样来源，也不被声称已经证明本文结论。Who&When 只作为 RQ2 背景，不进入本阶段方法。Exp34 的 13 个 exact pair（含 task_id、repository、class、seed）全部列在 `selection_contract.json` 中并排除；不把 Exp34 的受控 fault 或任何方法结果带入本确认集。

#### 事前选择合同

候选池是编号11的允许投影：只保留 `instance_id/task_id`、repository、base commit、SFT 行号、助手的 structured editor action 元数据和可见工具观察。Gym Parquet 只读固定列，SFT Parquet 只读 `messages`。不读取 resolved、test patch、FAIL_TO_PASS、PASS_TO_PASS、future evaluation、gold patch 或任何方法/基线成绩。

`selection_contract.json` 固定 34 条候选的身份和 base commit。先固定六仓库 allowlist：mypy、moto、MONAI、conan、pydantic，以及本阶段只为资产补齐而获取的 pandas；dask 和 dvc 不因结果落选，而是因本阶段不需要额外 source cache 被预先排除。对 allowlist 内候选按 `SHA256(task_id)` 十六进制升序、再按 task_id 排序，前 24 条按 rank 0–7、8–15、16–23 分配 A、B、C。该规则不读取方法结果，且冻结为 A/B/C=8/8/8、6 repositories、24 pairs。若任何配额或资产资格不足，立即 STOP，不改配额、不换样本。

新增 pandas source 仅写入被 `.gitignore` 忽略的 `cache/source_repos/pandas`：partial clone、no checkout，只 fetch 冻结 base commits；报告记录 origin、base commit/tree SHA 和对象大小。该缓存不是公开结果，来源变化或 base 缺失都会使 Stage A 停止。

#### 资格探针

对每个冻结 task，确认 base commit 存在；从 SFT 的助手输出中解析真实 `str_replace_editor` 的 `create/insert/str_replace`，关联是否出现可见执行观察，但不保留参数文本。按轨迹顺序在内存中以 base 文件为初态重放第一个可应用且造成真实状态改变的 clean action，记录动作类别、路径哈希、前后状态哈希和 changed-path 哈希。只调用非研究性质的内存语法或状态探针来证明 probe 可执行；不运行 Agent、测试套件、在线 monitor、baseline 或 fault 注入。source 仓库不 checkout、不写入，资格报告应证明 source 状态和虚拟 workspace 不变。

资格通过不等于研究 Go：Stage A 只允许输出 `ASSET_STAGE_A_QUALIFIED`，并把 `formal_revised_p1_go` 固定为 false。公开报告不包含题面、源码、观察原文、承诺文本、patch、fault、区间或成绩。

#### 后续阶段预注册方法与 Gate

后续唯一主方法为 `contract`；预注册比较 `vanilla`、`confirmed-editor/action-only`、`OOPSLA-adapted`、cost-matched periodic 和 every-action probe 上界。只有在不重新选择样本、不调阈值且完整性为 0 的条件下，才可评估：24/6/8-8-8；paired effective interval recall ≥ .80；clean FPR ≤ .10；相对最强非 Oracle 绝对增益 ≥ .15 且 paired task bootstrap 95% 下界 > 0；mean width ≤ `max(4, 轨迹事件数的25%)`；mean probes 不超过最强 cost-matched baseline；三类至少两类分别为正；RQ2 handoff coverage ≥ .80；0 泄漏、source/cache unchanged、workspace restored。通过名只允许 `RQ1_SMALL_CONFIRMATORY_GO`，`formal_revised_p1_go=false`。

上述指标在 Stage A 不计算。Stage A 的唯一交付是资产和资格证据；任何不满足结构配额、base、真实 structured editor action、clean action 状态改变或 probe 可执行性的任务，都使本阶段 STOP，而不是删除失败任务或调低门槛。

## 来源索引

- `旧实验裁决__实验__失败与停止__E041_RQ1动作状态效果契约独立确认__方案.md`

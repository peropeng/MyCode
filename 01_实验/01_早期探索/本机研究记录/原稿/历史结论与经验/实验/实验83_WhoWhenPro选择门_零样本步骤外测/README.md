# 实验83：Who&When Pro failure-only decisive-step 零样本外测

本实验的边界已经冻结：Who&When Pro 只有失败轨迹和 decisive-step Gold，没有同任务完整 safe execution，因此本实验不定义 Exp80 的 safe/unsafe Exact-F1，也不把结果称为 Exp80 同指标确认或 RQ1 GO。它只检查 Exp80 冻结的 `no_length_C` 选择门能否在新的 failure-only 轨迹上定位 Gold decisive step。

冻结前阶段只读取 Exp81 已缓存的 schema 样例来确定 adapter。旧样例 ID 集（287 个唯一 ID，含重复记录共 288 条）的 SHA256、文件 SHA256 和三个 API 样例 ID 已记录在 `source_manifest.json`；旧样例禁止进入外测方法指标。

冻结的合格条件是：trajectory 为 JSON list；去掉 user 后收集顶层 `kind=action` 事件；每个 action 具有唯一整数 `step_number`；Gold 为含整数 `step` 的 JSON，且该 step 精确存在于事件中。没有 action 的 round-only/agent-only、嵌套 round、缺失/重复 step 和 Gold 不合格逐原因计数；不把嵌套结构猜测性压平。planning 等无 step 的顶层元事件只要不是 nested round，就不改变 flat action 的资格。

固定 revision 的新页面只有在冻结提交后才能通过 datasets-server 读取：offset 为 `[713,1713,2713,3713,4713,5713]`，每页 100 行，总下载上限 20 MiB。原始页面只写入被忽略的 `runtime/raw_pages/`。

输入 adapter 只保留匿名 role equality/change、thought/action/content 的结构状态和显式 public tools；不读取 `ground_truth`、`is_injected`、`is_replayed`、`mode`、任务/框架/benchmark/ID 等字段作为方法特征。预测内部 index 会转回源 `step_number`。

执行比较 Base、A、C、C deletion、固定 step=1、固定 midpoint 和确定性 random route；C 模型、特征、阈值和参数直接从 Exp80 `pre_unseal.json` 重建，禁止在 WWP 调参。主指标是 eligible failure rows 的 exact StepAcc，task-group paired bootstrap 2000 次（seed 20260822）；同时报告 ASS、abstain、Gold>1 层位置审计和 framework/benchmark 分组。

## 裁决

- `EXTERNAL_FAILURE_LOCALIZATION_GO`：eligible≥100、groups≥100，C 相对最强公平基线绝对提升>0且相对≥10%，bootstrap CI 下界>0，better>worse，Gold>1 相对 Base 为正，且 seal/deletion/leakage/cost 全通过。
- `POSITIVE_VS_BASE_NOT_GO`：C 相对 Base 有真实提升但未过最强基线、10%或CI门；保留提升，不能写 STOP。
- `ZERO_SHOT_NOT_ESTABLISHED`：C≤Base，只否定这一个冻结 adapter+模型外推。
- `ASSET_ADAPTER_STOP`：eligible 或 groups 不足100；报告缺资格的绝对原因，不计方法失败。
- `HARNESS_INVALID`：revision、seal、Gold隔离、adapter、评价或成本审计失败；不作科研解释。

结果数字只能在冻结后追加提交。

## 执行结果（初始资格审计 + 修正后唯一有效外测）

首轮冻结实现把所有非 `kind=action` 顶层事件都排除，导致 74 条带 planning 元事件的合法 flat-action DSQA 行被误归为 `round_only_or_agent_only`。首轮结果保留为 `results/exp83_initial_harness_invalid.json`，裁决不作科研解释；该问题是资格 Harness 错误，不是方法失败。

随后只修正了这一条资格规则：收集顶层 `kind=action` 事件，忽略不含 nested round 的 planning 元事件；仍排除真正 round-only/agent-only、nested round 和 Gold step 不在事件中的行。修正版 protocol/data seal 重新冻结后，六个固定页面均以 revision `0bd196c8a040841c4ae167ab33cc8151de246f1f` 返回 200；每页 100 行，原始响应合计 `4,916,119` bytes，未触发 20 MiB 上限。新页与旧 287 个唯一样例 ID 无重叠，因此最终输入 600 行。修正版有 373 个合格 flat-action decisive-step rows、326 个 task groups；排除为 `round_only_or_agent_only=226`、`gold_step_not_in_events=1`，其余资格错误均为 0；当前合格行的 source `step_number` 均严格递增，adapter 对非递增行直接排除，不通过排序改变因果时序。

修正版主结果为 `ZERO_SHOT_NOT_ESTABLISHED`，不是资产 STOP，也不是方法方向 NO-GO：

| 方法 | exact StepAcc | ASS | abstain |
|---|---:|---:|---:|
| Base | 0/373 = 0.00% | 1.8070 | 0.00% |
| A | 0/373 = 0.00% | 1.8070 | 0.00% |
| C（Exp80 gate） | 0/373 = 0.00% | 1.8070 | 0.00% |
| C deletion | 0/373 = 0.00% | 1.8070 | 0.00% |
| fixed step=1 | 0/373 = 0.00% | 1.9383 | 0.00% |
| fixed midpoint | 212/373 = 56.84% | 0.5442 | 0.00% |

C 相对 Base 的差为 `0.00` 个百分点，task-group bootstrap 95% CI `[0.00, 0.00]`，better/worse/tie=`0/0/326`。由于 Base、A、C 都完全相同，C deletion 精确回到 Base，说明 gate 在这些零样本轨迹上没有产生可观测路由改变。最强公平基线是预注册候选中的 `fixed_midpoint`（56.84%）；C 相对它为 `-56.84pp`，95% CI `[-62.09,-51.61]`，因此不能把零样本外测写成提升。

Gold 源 step 分布为 `2:178, 3:110, 4:51, 5:16, 6:8, 7:7, 9:2, 11:1`，没有 step=1；Gold>1 的 C-vs-Base 仍为 `0.00pp`（better/worse/tie=`0/0/326`），C-vs-step1 也为 `0.00pp`。四类 eligible benchmark（dabench、databench、dsqa、tablebench）均为 Base/A/C `0.00%`，fixed midpoint 分别为 `59%/66%/43.84%/55%`。

泄漏、删除、旧样例排除和零 API/token 方法成本审计均通过；masked-injection audit 373/373 行预测不变。这里的 STOP 只停止“Exp80 固定模型 + 当前透明 adapter 在 WWP failure-only step localization 上的零样本迁移”这一冻结目标：绝对证据是 `0/373`、C 与 Base 逐行一致、326 个 task group 全 tie，且 midpoint 仅作强位置基线达到 `212/373=56.84%`。这计为 WhoWhen zero-shot transfer 冻结目标的实质方法失败 `1/3`，不计为整体选择门方向失败；AFTraj 上已有的真实正信号保留，不停止 AFTraj 后续确认或其他机制。机器明细在 `results/exp83_result.json`，下载/响应 hash 在 `source_manifest.json`。

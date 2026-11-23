# 实验24数据与审计附件

- 当前严格状态：**基础设施STOP**
- 原编号：`E040`
- 机器资产：`实验/实验24_RQ1状态转移证书链/`
- 主结论：`结论/结论24_实验24_RQ1状态转移证书链_基础设施STOP.md`

本文件保存详细指标、原结果摘录和审阅证据；研究判断以主结论为准。

## 原实验结果与指标

以下内容直接并入原结果/报告；它们保留当时数字和判断，但最终等级以本文件开头的严格状态为准。

### 来源：旧实验裁决__实验__失败与停止__E040_RQ1状态转移证书链__结果归档.md

### Exp40 结果归档：RQ1 状态转移证书链 Sealed 实验

封存状态：`SEALED_INFRASTRUCTURE_FAILED`
封存结论：`INFRASTRUCTURE_NO_RESULT`

本文件记录 Exp40 的三次执行尝试。实验没有产生可持久化的样本结果或指标：`persisted_sample_count=0`、`metric_count=0`。`formal_go=false`；`research_no_go=false` 表示本轮没有形成研究方法的 NO_GO 判定，而不是方法通过或失败的结论。

#### 三次尝试

| 尝试 | 发生点 | evaluator / 持久化状态 | 结果 |
| --- | --- | --- | --- |
| `attempt-001` | 首个实例进入 evaluator 前，`_replay_evaluator_impl` 因 runtime 父目录尚不存在而拒绝 `unsafe workspace root`。 | evaluator 未调用；workspace、checkpoint、result 均不存在；持久化样本 `0`，指标 `0`。 | 基础设施预检失败。 |
| `attempt-002` | 首个冻结实例 `django__django-11555` 已创建临时 workspace，并在内存中完成首个 evaluator 的标签/diff 构造；随后清理 workspace 时 Git 的 `gc.pid` 消失，触发 `FileNotFoundError`。 | 结果和 checkpoint 均未持久化；没有完成样本记录或聚合指标；持久化样本 `0`，指标 `0`。 | 中断式 evaluator/清理失败，不能作为有效样本。 |
| `attempt-003` | evaluator 调用前的 `_start_running_manifest` 路径校验。实现把 `restart.runtime_path`（attempt-003 runtime 根目录）与传入的 `checkpoint_path` 比较，而不是与 runtime 根目录比较，因而必然报路径不匹配。 | evaluator 未调用；workspace 未创建；checkpoint、result 均不存在；持久化样本 `0`，指标 `0`。 | 最后一次基础设施路径比较 bug。 |

#### 可审计事实

- 三次尝试都没有产生 `experiment_result.json`，也没有产生可用于聚合的 checkpoint。
- `attempt-002` 虽然在内存中到达标签/diff 构造，但没有形成持久化样本或指标，不能被当作部分 RQ1 数据。
- `attempt-003` 是预 evaluator 失败；其路径比较缺陷属于 runner 基础设施，不是状态转移证书链方法的实验结果。
- 全部历史 attempt 记录保留在 [sealed_manifest.json](sealed_manifest.json) 与 [recovery_audit.json](recovery_audit.json) 中；旧 workspace 只作为失败审计痕迹，不得复用。

#### 研究解释边界

本封存不能用于比较 RQ1 方法与基线，不能支持 `VALUABLE_DIRECTIONAL_GO`、`NO_GO`、准确率、风险召回、区间覆盖、成本或任何其他方法优劣结论。它只能说明 Exp40 的执行基础设施在三次尝试中均未完成可审计的结果落盘。

因此，本归档明确记录：

- `formal_go=false`
- `research_no_go=false`
- 不把 `INFRASTRUCTURE_NO_RESULT` 改写成研究方向 NO_GO
- 不允许第四次尝试；Exp40 到此封存，不再执行 `attempt-003` 或任何后续重试

本归档未运行 live/API，也未修改算法、Gate、样本选择或 runner。

## 来源索引

- `旧实验裁决__实验__失败与停止__E040_RQ1状态转移证书链__结果归档.md`

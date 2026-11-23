# Exp112：RQ1 时序交互依赖完整排序

## 冻结模块

Exp112 验证一个完整的 RQ1 替换模块 B2：

`anonymous step behavior representation → temporal/agent-interaction/tool-state dependency graph → global full ranking`。

表示、四类依赖通道的两轮无参数消息聚合、B2 pairwise locator 和全步骤排名共同只计一个模块。冻结的 B2 数值分数为：

`0.5 * minmax(frozen pairwise_B numeric E2 score) + 0.5 * minmax(graph utility)`。

A+B 是严格 inner-OOF learned stacking；A、B2、A+B、deletion、shuffle、random-dependency 和 Oracle 条件均在运行前冻结。Exp111 outer-held 结果、Exp97/98/109/110、confirmation 和新论文均未进入输入。

## 执行记录

协议冻结提交为 `a13e5aa`，实现提交为 `b47232a`。唯一正式命令于 2026-08-23 执行一次，耗时 `2930.586394875` 秒，API/token/retry/cost 均为 0；正式 JSON 写入一次且未覆盖，SHA-256 为 `f7a0420de94ebf3e0e4e100fa203f7c7507dfb8680eeaada7ba88906f54d4197`。实际 attempt 见 [execution_attempt_audit.json](results/execution_attempt_audit.json)。

正式 JSON 的不可变判定为 `HARNESS_INVALID`：B2-deletion 在每个 seed 的 3 条记录上未与真实 Exp88 digest-tie pairwise_B 精确一致。原因是初始实现用不同 JSON key 构造了匿名 digest，属于实现审计错误；并非方法方向的负结果。修复提交为 `4fe2d90`，现已直接复用 `E88._tie_digest` 并由单元测试锁定。

正式 JSON 不可覆盖，故修复后没有第二次 formal invocation，也没有改写正式指标。只读复核见 [posthoc_alignment_and_provenance_audit.json](results/posthoc_alignment_and_provenance_audit.json)：使用 immutable raw scores 重算 digest tie，3 个受影响 record index（273、729、730）均恢复 deletion 精确一致；该复核不改变正式 JSON，也不把 provisional 数字升级为章节 GO。

## 不可变 formal raw signal（仅作边界证据）

全局最强公平基线为 `pairwise_B`。下表保留正式 JSON 的原始 task-group MRR；因 formal verdict 为 `HARNESS_INVALID`，这些数字不能直接作为 GO 证据。

| seed | pairwise_B | B2 | B2 相对差 | A+B | A+B 相对差 |
|---|---:|---:|---:|---:|---:|
| 20260816 | 0.344260 | 0.460073 | +33.6411% | 0.493108 | +43.2371% |
| 20260817 | 0.344457 | 0.457321 | +32.7658% | 0.497868 | +44.5370% |
| 20260818 | 0.342382 | 0.457391 | +33.5909% | 0.497195 | +45.2167% |

正式 raw pooled 95% CI 为 B2 `[0.094922, 0.134263]`、A+B `[0.132370, 0.171639]`；A+B 对 A `[0.096918, 0.140329]`，A+B 对 B2 `[0.031107, 0.044604]`。图通道、nested OOF、Gold/coverage、shuffle、random edge-count 和 A cache 审计均通过；唯一阻断是 deletion digest 等价审计。

因此本目录不宣布 Exp112 模块或 RQ1 章节 GO。应由主线程决定是否将修复后的只读复核作为后续资产，或在新的明确授权下重新规划一次 formal；不得覆盖本次 immutable formal 输出。

## 验证

- Exp112：`py_compile` 与 18 项协议/runner 单元测试通过；synthetic full smoke 覆盖 14 条 condition、全部 aggregate/audit key；preflight 通过。
- Exp106 最小协议/runner 回归通过。
- Exp111 runner/corrective/postrun 回归通过；其既有 pre-run freeze 测试因 Exp111 正式结果已存在而有一项预期冲突，未修改只读 Exp111 目录。

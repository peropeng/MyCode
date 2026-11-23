# Gate0/Gate1 资格报告：方向 D（BFCL 接口契约鲁棒性→修复）

## 1. 判定摘要

本次资格实验的判定为：

| Gate | 判定 | 证据 | 含义 |
| --- | --- | --- | --- |
| Gate0 | **GO** | 官方仓库/包可安装导入；四家族任务、官方 evaluator、公开 response 均存在；4×200 严格 join；20 条 probe 两次一致；metadata-only 边界可执行 | 可以进入固定样本 replay 资格实验 |
| Gate1 | **GO** | 120 条、四家族各 30；全局结构签名唯一；120/120 两次 outcome 一致；0 evaluator/harness exception；每家族 30/30 | 公开响应重放协议稳定，可作为后续诊断/修复的受控入口 |
| 修复研究 | **未判定** | 尚未运行在线诊断、修复策略、clean/repair 对照或新模型响应 | 不能据此声称 repair benefit、泛化或两章论文成立 |

Gate1 的“GO”是资格与 replay stability 结论，而不是 120 个任务全部正确。第一次 replay 的 `VALID` 数为 75/120；其余是公开响应的 `MODEL_FORCE_TERMINATED` 或 `MODEL_EVALUATION_INVALID`。这些结果应保留为后续分层/修复研究的现状基线。

## 2. 官方资产核验

来源和 SHA256 集中在 [`manifests/source_manifest.json`](manifests/source_manifest.json)，避免在本报告复制 raw ID 或原始响应。锁定情况如下：

- `ShishirPatil/gorilla` 官方主源：`git ls-remote` 得到 `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`；根 LICENSE 为 Apache-2.0，数据 README 标注 `apache-2.0`。
- `bfcl-eval==2026.3.23`：PyPI wheel 安装并成功导入 `bfcl_eval`；官方 `multi_turn_checker` 和 `BitAgentHandler` 均可 import。
- `HuanzhiMao/BFCL-Result`：官方 leaderboard 链接指向该结果仓库；固定 `git ls-remote` commit 为 `6830ed13035c0cfee9aa7a9a0ffed70f10b3dd50`。四个 raw 文件按固定 URL 下载并保存 SHA256/200 行计数。
- 结果仓库锁定 commit 没有可确认根 LICENSE。本实验不把“公开可下载”扩大解释为“可自由再分发”，只提交不可逆哈希、计数、schema 摘要、选择 digest 和派生统计。

没有使用付费 API；没有生成模型响应。并发 clone/fetch 的临时目录不作为来源证据，证据来自 `git ls-remote`、固定 commit raw URL/hash、以及独立官方代码 checkout/installed wheel metadata。

## 3. 四家族、task↔response join 与 schema

四家族使用官方当前命名：

| 家族 | 官方 task 文件 | 官方 response 文件 | 任务/响应行数 | 严格 join |
| --- | --- | --- | ---: | --- |
| `multi_turn_base` | `BFCL_v4_multi_turn_base.json` | `BFCL_v4_multi_turn_base_result.json` | 200/200 | 200/200 |
| `multi_turn_miss_func` | `BFCL_v4_multi_turn_miss_func.json` | `BFCL_v4_multi_turn_miss_func_result.json` | 200/200 | 200/200 |
| `multi_turn_miss_param` | `BFCL_v4_multi_turn_miss_param.json` | `BFCL_v4_multi_turn_miss_param_result.json` | 200/200 | 200/200 |
| `multi_turn_long_context` | `BFCL_v4_multi_turn_long_context.json` | `BFCL_v4_multi_turn_long_context_result.json` | 200/200 | 200/200 |

审计要求 task 至少有 `id/question/initial_config/path/involved_classes`，response 至少有 `id/result`，且未知顶层字段不接受。公开响应以 list turn 为主；long-context 固定 snapshot 中存在公开失败记录，`result` 为 string 的记录也会被 schema 审计记录，不被伪造为成功调用。

## 4. Gate0 probe

选择按 `sha256(public_task_id)` 升序，每家族取 5 条；任务结构签名为协议中定义的 `question + initial_config + missed_function + sorted(involved_classes) + path` 的 canonical JSON SHA256。Gate0 probe 结果：

| 家族 | 选中 | join | 双 replay 一致 | clean VALID |
| --- | ---: | ---: | ---: | ---: |
| base | 5 | 5 | 5 | 5 |
| miss_func | 5 | 5 | 5 | 3 |
| miss_param | 5 | 5 | 5 | 3 |
| long_context | 5 | 5 | 5 | 2 |
| 合计 | 20 | 20 | 20 | 13 |

没有 harness error。该 probe 足以确认四家族可进入 Gate1，但不用于估计模型总体质量。

## 5. Gate1 固定 120 条与全局去重

Gate1 严格使用一个跨家族 `seen_signatures`。依次扫描 base、miss_func、miss_param、long_context，每家族取 30 个已 join 且结构签名未出现的任务。最终清单验证为：

- 120 个 manifest 行；每家族 30 行；
- 120 个唯一 `task_id_sha256`；
- 120 个唯一 `structure_signature_sha256`；
- 机器可读 `gate1_summary.json` 记录 `total_unique_structure_signatures=120`，且 Gate1 decision 直接要求该值等于 120；
- 没有原始 task ID、Gold、response archive 或 signature preimage。

这一步是对早期“仅家族内去重”风险的修正；跨家族重复结构不能被四次计数。若未来数据更新导致任何家族无法凑足 30 个全局唯一任务，正确判定是 Gate1 STOP，而不是换成未注册家族或放宽去重。

## 6. Gate1 replay 结果

| 家族 | 选中 | join | 双 replay 一致 | clean VALID | evaluator called | harness error | 首次 replay 状态（VALID / invalid / force） |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| base | 30 | 30 | 30 | 22 | 26 | 0 | 22 / 4 / 4 |
| miss_func | 30 | 30 | 30 | 14 | 19 | 0 | 14 / 5 / 11 |
| miss_param | 30 | 30 | 30 | 22 | 25 | 0 | 22 / 3 / 5 |
| long_context | 30 | 30 | 30 | 17 | 22 | 0 | 17 / 5 / 8 |
| 合计 | 120 | 120 | 120 | 75 | 92 | 0 | 75 / 17 / 28 |

Gate1 门槛为总一致数至少 114/120、每家族至少 25/30、harness error 为 0；实际为 120/120、30/30、0，因此判定 GO。错误类别仅用于离线结果聚合，不进入 online diagnosis/repair 的可见字段：

- `TURN_COUNT_MISMATCH`：28 条，归入公开 response shape/force termination；
- `STATE_MISMATCH`：13 条；
- `EXECUTION_RESPONSE_MISMATCH`：3 条；
- `EMPTY_TURN_RESPONSE`：1 条。

## 7. 在线边界与 Gold 禁区

未来策略最多看到冻结的 `id + result` 投影及不含 raw ID 的 schema/aggregate 摘要。以下内容永不作为 online 输入：

- `ground_truth`、`possible_answer`、evaluator answer；
- future user/assistant/tool turns；
- task 的 `initial_config`/state snapshot；
- `inference_log`、token/latency 元数据；
- 离线 evaluator 的 coarse error class；
- raw task ID、原始 response、prompt 或 score 文件。

官方 Gold 仅在投影冻结之后、隔离的离线 scoring 阶段被 evaluator 读取。提交文件只含 hash/count/布尔/schema/派生指标。任何 Gate2 实现都必须由测试证明诊断策略调用路径没有接收上述禁区字段。

## 8. 可行性判断和后续计划

当前最稳妥的判断是“资格可行，研究价值待验证”：

1. 资产和接口契约可固定、可下载、可严格 join，且官方 evaluator 在无 API 情况下可重放。
2. 四家族之间存在可检测的结构重复风险；全局去重后仍能各取 30，说明本次固定 snapshot 的样本量足够。
3. 公开 response 本身的 clean VALID 只有 75/120，且 miss_func、long_context 的 force/invalid 较多。这支持把“响应 shape/契约错误诊断”作为后续问题，但不支持直接把 75/120 当成修复增益。
4. 后续 Gate2 应预注册 repair policy 的输入 schema、允许动作和禁止字段，至少保留 untouched baseline、诊断后修复、随机/规则对照三组；只在已冻结公开 response 上做不生成新模型输出的变换，另设人工或离线 evaluator 对照。
5. 若研究问题必须测“修复后模型重新生成”的收益，则需要另行确认模型权重/计算资源、生成许可和响应再分发边界，不能从本 Gate0/Gate1 资格实验推断。

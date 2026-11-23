# 方向 B 分层记忆管理与可靠利用：Gate 0/1 资格报告

日期：2026-08-21
执行分支：`exp/0821-direction-b-gate01`
基线：`main@4cb7d20ada545f47f20374103bc41e05e084aaa0`

## 1. 最终裁决

| Gate | 裁决 | 依据 |
|---|---|---|
| Gate 0：论文、代码和 benchmark 是否可复现 | **CONDITIONAL** | 5 篇正式论文、4 个公开代码仓库和 Mem2ActBench 数据资产已锁 commit；AWM/HiAgent/AgeMem 的低成本 smoke 通过，G-Memory pinned commit 存在语法错误；只有 AWM 根许可证明确，3 个项目许可证未核实；没有一项完整端到端复现通过。 |
| Gate 1：是否有真实 memory-dependent 工具任务和 ≥30 个冲突案例 | **CONDITIONAL（不能宣称 GO）** | 数量和任务合同足够：384 个去重 episode、373 个严格记忆候选、40/40 抽查为跨轮历史依赖且有 target tool gold、53 个 temporal/discarded conflict 证据组；但 74/384 不能从单个 shipped session 完整恢复，显式 stale/error-memory Gold 均为 0，且没有主动 memory operation trace。 |

因此方向 B 目前是“可继续做低成本 Harness 修补”的备选，不是已经满足两章论文的 GO。当前证据支持一个**长上下文记忆驱动工具调用**问题，不足以直接支持“分层记忆构建 + 可靠治理”两章。

## 2. Gate 0 资产核验

### 2.1 正式论文身份

已从 PMLR、ACL Anthology、NeurIPS proceedings 核验：

- AWM：ICML 2025，PMLR full proceedings paper；
- HiAgent：ACL 2025 Volume 1 Long Paper；
- G-Memory：NeurIPS 2025 Main；
- AgeMem：ACL 2026 Volume 1 Long Paper；
- How Memory Management Impacts LLM Agents：ACL 2026 Volume 1 Long Paper；
- Mem2ActBench：ACL 2026 Volume 1 Long Paper / benchmark。

论文身份、作者、CCF venue 口径、正式 URL 和代码链接见 `manifests/paper_repo_dataset_manifest.json`。论文正式存在不被当作代码可复现证据。

### 2.2 仓库、许可证和 smoke

| 资产 | 代码证据 | 许可证证据 | 实际最低 smoke |
|---|---|---|---|
| AWM | depth-1 clone，HEAD 已锁 | 根 `LICENSE` 为 Apache-2.0 | WebArena `pipeline.py --help` 返回 0；Docker Python 3.11 AST parse 29 个文件通过 |
| HiAgent | depth-1 clone，HEAD 已锁 | 根 LICENSE 缺失；只有嵌入 WebShop LICENSE.md | `python3 -m compileall -q agentboard` 返回 0 |
| G-Memory | depth-1 clone，HEAD 已锁 | LICENSE/COPYING 缺失 | compileall 返回 1，3 个文件 SyntaxError；`tasks/run.py --help` 返回 1（缺 PyYAML） |
| AgeMem | depth-1 clone，HEAD 已锁 | 根 LICENSE 缺失；pyproject 只有 Apache classifier，不能视为授权文本 | AgentScope module compileall 返回 0 |
| Mem2ActBench | depth-1 clone，HEAD 已锁 | README 声称 MIT，但仓库无 LICENSE；上游 BFCL/OASST1/ToolACE 条款未审 | 5 个构造脚本 compile；400 QA/2029 session JSONL 读取返回 0 |

完整返回码和未运行原因见 `manifests/asset_smoke_manifest.json`。Docker CLI/server 为 `29.7.2/29.5.2`，`hello-world` 返回 0。

### 2.3 Gate 0 的解释

“公开仓库存在”可以支持继续投入，但“至少 3 个可运行开源实现”尚未被严格证明：AWM 的代码许可清楚，HiAgent/AgeMem/G-Memory 的根许可证不足或未知，G-Memory 还无法通过语法级 smoke。Mem2ActBench 的数据读取资产真实存在，且有主动 target tool call 字段，但它是任务合同/长上下文 benchmark，不是已经验证的 memory manager environment。

## 3. Gate 1 数据合同与统计

### 3.1 数据规模与去重

来自 `results/mem2actbench_gate1_stats.json`：

| 指标 | 数值 |
|---|---:|
| QA 原始行 | 400 |
| 长 session 行 | 2,029 |
| `has_tool_calls=true` session | 1,932 |
| 唯一原始 source ID | 494 |
| 去重后 episode 组 | 384 |
| 因相同 source episode 去掉的衍生 QA | 16 |
| 去重后有 lineage 的 episode | 375 |
| 去重后严格记忆候选 | 373 |
| strict 候选率 | 97.14% |

QA 字段类型已递归统计；`level` 为 L1=237、L2=101、L3=17、L4=45（去重后 L1=227、L2=96、L3=17、L4=44）。grounding 类型计数为 explicit=385、inferred=158、default=279。目标工具名 250 种，所有 400 行都有非空 target tool call 合同。

### 3.2 记忆依赖与工具行为

人工/规则抽查的 40 个 episode 使用“30 个总体 hash 抽样 + 10 个 L4/temporal conflict oversample”，不复制原始文本：

| 抽查项 | 结果 | 解释 |
|---|---:|---|
| 语义上依赖历史 query/evolution 的样本 | 40/40 | query 使用“that/earlier/we discussed”等指代，或参数只在历史 fact 中出现 |
| 有 target tool gold | 40/40 | 但这是 benchmark 合同，不是已执行 API |
| session 中有 assistant tool call + tool result | 38/40 | 是比 target label 更强的工具行为证据 |
| source 可在一个 shipped session 完整恢复 | 29/40 | 11 个样本的 source IDs 分散、缺失或未被同一 session 包含 |
| L4/temporal conflict label | 10/40 | 其中 8 个有专用 `has_temporal_conflict` |
| 显式 stale label | 0/40 | 未发现专用 metadata 字段 |
| 显式 error-memory label | 0/40 | 未发现专用 metadata 字段 |

总体上 364/384 个去重 episode 所在 session 有 assistant/tool 观察，302/384 个 episode 的 exact source 也有 tool turn；这个差距说明不能把 session 级工具行为无条件回写到 QA source。所有统计均由标准库脚本生成，不使用 LLM Judge。

### 3.3 冲突、过时与错误记忆证据

| 证据层级 | 去重组数 | 能证明什么 | 不能证明什么 |
|---|---:|---|---|
| L4 或 temporal label | 44 | benchmark 有高难/冲突候选 | L4 中含 19 个 Multi-hop-Reasoning，不全是时序冲突 |
| 专用 `has_temporal_conflict=true` | 25 | 构造标注明确声称存在时序冲突 | 不是运行时检验过的 stale memory 后果 |
| conflict CSV 非空 `discarded_source_ids` | 30 | 有来源被丢弃的冲突 lineage，可用于重组 | 丢弃由构造脚本产生，不是 Agent 误用错误记忆的结果 |
| temporal 或 discarded union | 53 | 数量上超过 Gate 1 的 30 例门槛 | 仍没有 stale/error-memory 操作和任务结果 Gold |
| 专用 stale label | 0 | 无 | 不能声称已有 stale benchmark |
| 专用 error-memory label | 0 | 无 | 不能声称已有 harmful-memory benchmark |

因此“≥30 个冲突相关候选”在**资产筛选意义**上满足，但“≥30 个可重放的 stale/conflict/error-memory 任务”尚未满足。

## 4. 数据完整性与泄漏风险

### 4.1 session 映射不完整

384 个去重 episode 中仅 310 个能在至少一个 `toolmem_conversation` session 中完整覆盖其 source IDs，74 个不能；原始 QA 行对应为 323/400 完整、77/400 不完整。55 个 episode 的 source IDs 跨多个 session 行，说明标签具备跨上下文来源，但不等于系统保存过可检索的持久记忆。

### 4.2 Gold 字段和生成性

QA 行含 `evolution_chain`、`tool_call.grounding_info`、`complexity_metadata` 等构造/标注字段。若把这些字段直接给被测 Agent，Gold 会泄漏；可执行评测只能向 Agent 提供选定 session 的 turns 和当前 query，其他字段仅供 scorer 使用。`tool_call` 本身是目标合同，不能作为“Agent 实际调用成功”。

### 4.3 不是主动记忆治理 benchmark

仓库中存在从 memory 到 tool 的参数映射和 conflict 构造脚本，但 shipped QA/session schema 没有可验证的 `memory_write`、`memory_retrieve`、`memory_update`、`memory_delete`、删除原因、过时状态或错误经验导致的后果字段。因而目前最多支持“历史信息检索→工具参数构造”的离线资格实验。

## 5. 结论与最便宜下一动作

### 保留

1. 用 384 episode 去重合同作为低成本 memory-dependent tool calling 数据起点；
2. 用 25 temporal label + 30 discarded lineage 作为冲突重组候选池；
3. 保留 40 样本人工抽查和 364 个 session/tool 观察的阴性对照；
4. 采用 AWM/HiAgent/AgeMem 的代码接口作为记忆 harness 参考，而不是直接宣称已复现。

### 必须补齐后才能 Gate 1 GO

1. 从 30 个 discarded lineage 中构造 30 个独立双 episode 任务，把全部 source/context 放入单一可重放记录；
2. 加入确定性的 memory store stub，记录 add/retrieve/update/delete、命中的来源、时效和冲突解决动作；
3. 生成至少 10 stale、10 conflict、10 error-memory 任务，并让错误记忆造成可观测的工具参数或任务结果后果；
4. 用 clean replay 检查同一任务状态恢复，确保 query 不直接暴露 Gold；
5. 若至少 24/30 通过真实记忆依赖审计，且 ≥30 个冲突/错误记忆例可重放，再重新裁决 Gate 1；否则停止方向 B 的两章投入，保留为数据/工具调用子题。

## 6. 需要主线程决定的边界

- 是否接受“工具调用长上下文”作为方向 B 的暂时主域；若必须是跨独立 session 的主动记忆治理，当前 Gate 1 只能维持 `CONDITIONAL`。
- 是否允许把 30 个 conflict lineage 重组为新 harness；这是下一步最小增量，但会创建新数据合同，不能冒充原始 benchmark 的自然 Gold。

# Gate0 资格报告

## 裁决

**方向：`REJECTED_OVERLAP`。**

资产状态同时为 **`CONDITIONAL_ASSET_BLOCKED`**，并有一项硬件/API 门达到 `STOP_ASSET`。Gate0 不能写章节 GO；本方向没有进入模型/API 实验，也不计入同一目标“三次实质设计失败”。

## 证据摘要

| 硬门 | 预注册要求 | 观察值 | 结果 |
|---|---|---:|---|
| 正式论文 | 3–5 篇核心，且每章有 2025–2026 CCF A Full/Regular/Long 站台 | 5 篇核心候选；ACL 2026 Long 直接站台可用 | 通过 |
| 环境/自然外测 | ≥2 可运行资产，≥1 自然外测 | 4 个仓库定义的环境候选；0 个无模型/API 本地入口；0 个带冻结链的自然外测资产 | 阻塞 |
| 独立任务 | ≥50，分组后 ≥20 held-out | 可见 1128 行（1000 MEM1 demo + 128 CoMem QA），合格独立任务 0，held-out 0 | 阻塞 |
| process-fidelity Gold | ≥30 个程序化 Gold | 0；没有 constraint+tool result+source anchor+transform+executable outcome 链 | 阻塞 |
| 冻结轨迹链 | ≥1 条官方冻结、可本地 deterministic replay | 0 | 阻塞 |
| 第二章 | 可消费 OOF risk 做 restore/replay/replan | 文献中有 restore/active recall，但无第一章 OOF 资产或独立干预合同 | 阻塞 |
| 公平与硬件 | 无 API、16GB Apple Silicon 可离线重放 | 官方路径需要 vLLM/权重、付费/私有 API、H100/H200/A100 或 live web | STOP_ASSET |
| 重叠 | 不能只剩摘要/召回/token/verifier 增量 | OCR-Memory、CoMem、SUPO、Sculptor 已直接覆盖 | **REJECTED_OVERLAP** |

## 资产细节

- `MIT-MI/MEM1@2609aef4` 是作者声明的 official implementation，MIT。`examples/demo.jsonl` 有 1000 行，字段包含 query、turn response/tool/internal-state 和 exact-match 标签，但没有显式用户约束、source anchor、provenance exactness Gold 或 restore/replay 入口。
- `horizon-llm/CoMem@bb552535` 是作者声明的 official implementation，Apache-2.0。仓库的 `browsecomp-128/standardized_data.jsonl` 有 128 行，但每行只有 `task_id/task_question/ground_truth`；CoMem 的 README 明确 action-consistency reward 优化 functional equivalence，同时评测脚本需要模型服务、GPU 和 API key。
- `Ignoramus0817/FS-Researcher@a9f0483` 没有 LICENSE 文件，也没有随仓库发布数据/trajectory；README 依赖 OpenAI-compatible、Serper 和 Jina API。
- `tenghaohuang/GTA@032f3da` 是作者官方 ACL 2026 Long 代码，但没有 LICENSE 文件或冻结数据；其流程会爬实时网站并生成任务，不得把动态生成数据当作本轮自然冻结外测。
- Sculptor、COMPASS、SUPO、OCR-Memory 的官方论文页/PDF 没有作者代码/数据入口。不能因为论文报告了 Mind2Web/AppWorld/GAIA/BrowseComp/SWE-Bench/CodeGym 结果，就把外部数据写成本地可复现实验资产。

## 重叠裁决

OCR-Memory 的 ACL 官方摘要与论文 pp.1–2 明确写出：轨迹使用 visual anchors 定位，随后从外部日志确定性获取 verbatim text，并用 active recall 恢复高分辨率；pp.8–9 在 Mind2Web/AppWorld 评价 evidence recovery 和 agent task success。这不是普通“摘要质量”邻近工作，而是本题 evidence/provenance/restore 的直接实现。

CoMem 的官方 README 明确把 action-consistency reward 定义为压缩记忆是否诱导正确 downstream behavior，即 functional equivalence。SUPO 的 ACL 官方摘要明确将 task-relevant tool-use history summary 与 agent policy 端到端联合优化并用 interactive function-calling/search success 评价。Sculptor 已提供可逆的 context fragment/fold/summary/hide/restore/search 工具。

最新压力论文 CAPS（arXiv:2608.08960）只作为非正式 open gap 记录：它用 history recovery、matched-state decision 和 complete trajectory 证明“读回文本”并不保证正确行动策略，代码仍承诺 future release。它进一步说明 process fidelity 重要，但不能作为资产或 CCF A 站台。

## 后续

停止该候选的 Gate1 模型/API 实验。除非先提出不落入上述覆盖面的独立机制，并重新取得含自然冻结轨迹、程序化 Gold、held-out 分组和无模型 replay 的公开资产，否则不继续投入实验预算。

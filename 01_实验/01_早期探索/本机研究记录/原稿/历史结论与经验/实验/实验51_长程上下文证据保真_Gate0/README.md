# 实验51：长程上下文证据保真 Gate0

## 当前裁决

`REJECTED_OVERLAP`（同时存在 `CONDITIONAL_ASSET_BLOCKED` 级别的资产缺口）。本目录只证明 Gate0 审计结果，不声称任何章节 GO。

候选题目：**面向长程智能体的证据保真上下文管理与执行恢复方法研究**。

冻结的核心目标是：

```text
公开长程 Agent trace prefix + 用户约束 + tool results + source anchors
  -> 结构化 working state / provenance + 可逆 context transform
  -> 程序化 constraint/evidence retention、provenance exactness、restore fidelity
```

第二章只能消费第一章在未见任务上产生的 OOF evidence/constraint-loss risk，触发 checkpoint restore、prefix replay、replan 或 continue，并以真实长程任务成功和约束违反评价。

## 为什么现在停止

1. OCR-Memory（ACL 2026 Long）已经把轨迹渲染为带视觉 anchor 的图像，再从外部日志**确定性恢复逐字文本**，并做 active recall/分辨率恢复，在 Mind2Web/AppWorld 上评价；这直接覆盖本题的 evidence fidelity、provenance anchor 与 reversible recovery 核心。
2. CoMem（ICML 2026）明确以 action-consistency reward 优化压缩状态的 functional equivalence，直接覆盖“压缩后下游行为仍等价”的主论证；SUPO（ACL 2026 Long）把工具历史摘要与 agent policy 端到端联合优化，直接覆盖 context transform→agent outcome 链。
3. Sculptor 已有 fragment/summary/hide/restore/search；COMPASS、FS-Researcher 已有 Context Manager / persistent workspace / citation-grounded notes。若新增只剩“摘要更准确、约束召回更高、少 token、再加 verifier”，属于要求文件第 3、6 节明确排除的包装增量。
4. 本地可见资产也无法满足硬门：MEM1 demo 只有 1000 行轨迹样例，CoMem 只有 128 条 `task_id/task_question/ground_truth` 题目；FS-Researcher 与 GTA 的仓库没有冻结数据/轨迹，另外四个正式工作没有作者官方代码入口。按严格规则，合格 process-fidelity Gold、自然外测资产、无模型 deterministic replay 均为 0。

## 已审计入口

详细 URL、论文类型、commit、许可证、schema、限制和访问日期见：

- `source_manifest.json`：正式论文、压力论文、作者官方仓库及其入口审计；
- `asset_census.json`：公开任务/trajectory/schema/Gold/环境计数，区分“可见行数”和“合格资产”；
- `overlap_matrix.json` / `overlap_matrix.md`：逐方法重叠证据和候选增量判定；
- `qualification.json` / `qualification_report.md`：冻结门、实际值、最终状态；
- `protocol.md`：在观察结果前冻结的 Gate0 协议。

## 可复现检查

在本目录执行：

```bash
python3 audit_gate0.py --json
python3 -m unittest -v test_gate0.py
python3 privacy_audit.py
python3 -m py_compile audit_gate0.py privacy_audit.py test_gate0.py
git diff --check
```

审计脚本只读取本地小型 manifest/census/matrix，不调用模型/API、不下载权重/大数据、不启动 Docker、不修改系统。所有第三方浅克隆均位于 `/tmp/context-gate0-repos.*`，没有提交到本实验目录。

## 结论的边界

`REJECTED_OVERLAP` 是当前方向在统一要求下的研究设计裁决，不是声称“上下文管理没有研究价值”。若要恢复研究，必须先提出与 OCR-Memory/CoMem/SUPO/Sculptor 不同的可证伪机制，并重新冻结包含自然轨迹、source anchor、程序化 Gold、held-out 分组和无模型 replay 的资产合同；不得通过降低本目录已经冻结的门槛恢复。

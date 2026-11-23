# Gaia2 等价过程验证与依赖感知局部恢复：资格报告

日期：2026-08-21（Asia/Shanghai）
裁决：**`STOP_ASSET`**
性质：Gate0/Gate1 资产审查；不计入同一目标的三次方法失败。

## 1. 结论先行

Gaia2/ARE 确实提供了动态、异步、时间约束、多应用和 write-action verifier 研究对象，且官方代码和数据入口可核验。`mini` 公开配置也能在无模型/无 API 的纯结构 parser 中稳定解析 160 个场景，覆盖 5 个 capability family。

但本题需要的不是“有很多 oracle 场景”，而是能独立评价等价过程验证并在执行后评价局部恢复的 Gold。当前公开 `mini` parquet 的 160 行没有非空 Agent 轨迹；其中 `OracleEvent` 是官方解决方案标注，不能当 independent Gold；本次没有调用官方 verifier，也没有任何失败—恢复执行结果。因此 Gate1 的关键计数为 0，严格停止。

## 2. 论文、代码和资产核验

| 项目 | 证据 | 结果 |
|---|---|---|
| 正式论文 | [Gaia2 ICLR 2026 论文页](https://iclr.cc/virtual/2026/poster/10011091)、[官方 PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/c26a67e0470774df98c12480ec5d2d7b-Paper-Conference.pdf) | 通过 |
| 官方平台/代码 | `facebookresearch/meta-agents-research-environments`，冻结 `7946367413129784139e785ae4c351090002a0bb` | 通过 |
| 代码许可 | 仓库 `LICENSE` 为 MIT，SHA-256 `da6d3703ed11cbe42bd212c725957c98da23cbff1998c05fa4b3d976d1a58e93` | 通过 |
| 数据许可 | [HF Gaia2 README](https://huggingface.co/datasets/meta-agents-research-environments/gaia2) 声明 CC-BY-4.0，并提示 Llama 3.3/4 条款可能适用 | 有条件通过，需保留来源和衍生使用审查 |
| 官方规模 | 文档/前置 metadata：10 universes、800 core scenarios、5×160、mini 160 | 通过；README 后文另有 200 的不一致叙述，按实际文件/前置 metadata 记录 |
| action DAG | 每条 mini row 的 `events` 含 event id、dependencies、event time/relative time、action app/function/args | 160/160 结构解析通过 |
| 动态/noise | 公开 scenario 有 ENV events 和 augmentation；官方文档明确随机 failure probability、tool augmentation、environment events | 资产存在 |
| evaluator | 官方 ARE 代码含 validation/judge；本次未调用 verifier | 代码入口存在；独立 Gold 不成立 |

下载规模：官方代码 clone 约 69.4 MB；`demo` 约 0.6 MB；`mini` 162,426,171 bytes。没有下载五个约 160 MB 的完整 capability 文件、CLI 全量测试集、模型或权重。

## 3. 严格计数

| Gate1 硬门 | 要求 | 观察值 | 结果 |
|---|---:|---:|---|
| 独立外部场景 | ≥100，≥2 families | 160，5 families | PASS（仅结构/资产层） |
| 可解析公开 action DAG/state/evaluator | ≥100 | action DAG 160/160；evaluator 仅代码入口，未形成独立 Gold | 资产通过，Gold 不通过 |
| 独立等价/非等价过程 Gold | ≥60 | 0 | FAIL |
| 真实公开 Agent 轨迹/官方公开运行 | ≥20 | 0 | FAIL |
| 可执行失败→局部修复 outcome | ≥40 | 0 | FAIL |
| held-out 修复 outcome | ≥20 | 0 | FAIL |
| CPU/no API/no model 双运行 digest smoke | ≥1 | 1 个 parser smoke；两次 digest 相同 | PASS（仅结构 parser） |
| 端到端官方环境无模型 replay | ≥1 | 0 | FAIL |
| 自然外测候选 | ≥1 | 0 | FAIL |

### 排除规则

1. 1,042 个 `OracleEvent` 只证明官方场景结构；它们是官方解答/验证输入，不是 independent equivalence Gold。
2. 对 Oracle action 做变异再让官方 verifier 判定，只能是构造控制，不能满足“真实 Agent 轨迹至少 20”或独立 Gold 门。
3. LLM judge 的软检查没有被调用，也不计入程序化 Gold。
4. 没有“失败 trace + recovery action + post-recovery state/result”三件套，因此 failure→repair 与 held-out 均为 0。
5. Gaia2 是模拟用户环境，不把它冒充自然部署外测。

## 4. 重叠 kill

ARE 论文已经明确写出 oracle action DAG 的拓扑依赖、动作参数 hard/soft check、causality 和 timing 检查，并指出 soft check 可使用 LLM judge；[Self-Grounded Verification](https://proceedings.iclr.cc/paper_files/paper/2026/hash/3e1fb72d876d634b2ac29e9ac2c937c9-Abstract-Conference.html) 直接研究轨迹 verifier 的过度接受；[ReIn](https://proceedings.iclr.cc/paper_files/paper/2026/hash/3144924eaa37b635a79dd382c6d7c825-Abstract-Conference.html) 直接研究外部错误诊断和恢复计划；[ToolEVO](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d8d1d325f822e07d16866780cc23deb2-Abstract-Conference.html) 直接研究工具变化下的适应；[Agentic Rubrics](https://aclanthology.org/2026.acl-long.697/) 直接研究上下文 grounded verifier；[SeekBench](https://iclr.cc/virtual/2026/poster/10007188) 直接评估 groundedness/recovery/calibration 过程。

因此只有以下增量才可能继续活过 overlap kill：不读取 hidden oracle、用可观察 post-action state 证明效果等价、以依赖闭包决定 replay 起点，并用真实执行后的成功/非目标回归/成本验证恢复。只换 judge、规则、置信校准或直接读取 ARE verifier 输出，均应 `REJECTED_OVERLAP`。

本次由于资产硬门已失败，没有执行任何方法比较，故重叠状态记录为 `HIGH_RISK_CONDITIONAL` 而非伪造正结果。

## 5. 复现与验证

已运行：

- `python3 -m py_compile scripts/*.py tests/*.py`：通过；
- `python3 -m unittest discover -s tests -v`：3 tests，全部通过；
- `python3 scripts/gate_probe.py --input runtime/gaia2_mini.parquet --output results/asset_census.json`：160 行，160 unique，5 families，DAG 160/160，real trace 0；
- `python3 -m json.tool results/qualification.json`：通过；
- `python3 scripts/privacy_audit.py`：将在提交前运行；
- `git diff --check`：将在提交前运行。

未运行：完整 800 场景、官方模型评测、API 调用、权重下载、完整 Docker benchmark、官方 verifier、RQ1/RQ2 方法实验。原因是 Gate1 关键资产计数已为 0，继续运行会违反冻结停止规则且不能补足独立 Gold。

## 6. 实时决策

- `three_design_failure_count = 0`；资产失败、依赖缺失和未下载不计方法失败。
- 不委派 Sol 独立审阅：尚未针对同一冻结预期完成三种实质方法设计并全部失败。
- 不再下载 Gaia2 全量文件，不进入模型/API 阶段。
- Gaia2 的可复用结论是“公开动态事件/DAG 资产很丰富，但公开验证输入不是独立 Agent 过程 Gold”；下一候选应优先选能同时提供真实 Agent traces、程序化失败/修复结果和无模型回放的两章方案。

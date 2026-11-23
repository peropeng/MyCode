# 候选组三 Gate0：动态工具可靠性估计与自适应恢复

当前裁决为 `CONDITIONAL_ASSET_BLOCKED`，不是章节 GO，也不是方法失败。

本 Gate0 审计题目《面向动态工具环境的智能体可靠性估计与自适应恢复方法研究》的论文站台、官方代码/数据入口、可运行性、程序化 Gold、自然外测和直接重叠。冻结的第一章目标是：只使用当前 trace prefix、公开 tool schema、调用结果类别和依赖图，预测下一调用成功概率、失败类型和校准不确定性；主指标只能是预注册的 task-grouped Brier score。第二章只消费第一章 OOF 风险，选择 retry、alternative tool、dependency repair、checkpoint backtrack 或 safe stop，并以真实 task success 为主指标。

## 当前事实

- 核心正式论文组满足数量和方向站台：ToolEVO、Web Agents with World Models、ReIn、ResiliBench 均为 ICLR 2025/2026 Conference，BacktrackAgent 为 EMNLP 2025 Main。新增 OpenApps 为 ICLR 2026 Oral 的官方环境候选；`Do Large Language Models Know What They Are Capable Of?` 为 ICLR 2026 Conference，属于必须纳入的重叠压力。
- ResiliBench 的 5,040 task / 30 API / 五类错误是论文和官方 README 声称的参数化构造资产；本次浅克隆看到的 JSON 只是 Git-LFS pointer（最大约 63.5 MB，tool registry 约 70 KB，real API task 约 329 KB），未下载大数据。因此尚未证明本地可执行或可审计 Gold。
- ToolEVO 官方仓库公开了 ToolQA-D 测试和训练文件，但 README 要求外部 ToolQA 语料、API server、Llama3-8B/Qwen2-7B 权重；仓库没有声明 LICENSE。其工具演化错误来自 API name/parameter/response variation，不能直接当自然随机服务故障。
- WMA 官方仓库带 8 个 sample JSON（每个 10 rows，重复任务很明显），样例包含 prefix/action/next-state，但没有稳定的 executor-level failure type Gold；完整 WebArena 环境要求 Docker，生成轨迹脚本使用 OpenAI，不能在无模型/无 API 下形成完整自然外测。
- OpenApps 官方仓库明确声称单 CPU、Python、透明 state 和 ground-truth rewards，配置中有 28 个原始任务、243 个 goal variation 和 100 个 longer-horizon 任务。它适合作为可运行 GUI environment / reward audit 候选，但 GUI state/design variation 不是随机工具故障，不能单独满足本题 failure Gold 或自然 tool-failure 外测。
- 公开正式论文中尚未发现与本题完全相同的“prefix + schema + result category + dependency graph → next-call failure probability/calibration → recovery choice”闭环；但 ResiliBench、ToolEVO、WMA、ReIn、BacktrackAgent 和 ICLR 2026 capability-awareness paper 已覆盖相邻组合。若增量最终只剩换分类器、校准器或成本项，必须改判 `REJECTED_OVERLAP`。

## 为什么不是 GO

Gate0 还没有冻结至少 30 个任务的、由执行器/状态转移/工具返回直接产生的 next-call failure + failure-type Gold；也没有冻结至少 30 个任务的可执行 recovery candidate/result Gold；没有一个已验证的自然/官方冻结 trajectory 可以在本机离线重放并完成第一条 baseline/Gold 审计。ResiliBench 的构造故障不能作为唯一证据，OpenApps 的 GUI variation 不能偷换成工具失败，WMA 的样例不能凭文件行数冒充独立自然任务。

因此当前只能保留条件资格：若 Gate1 能在不改标签、不引入未来信息、不依赖付费 API/大模型的前提下，从 ResiliBench/ToolEVO 形成程序化故障 Gold，并以 WMA/WebArena 或其他自然 Agent 资产完成外测和 recovery 对照，再复核重叠；否则为 `STOP_ASSET`。本 Gate0 不训练模型、不调用 API、不下载权重或大数据、不运行全量 Docker。

## 复现

```bash
python3 scripts/audit_sources.py --runtime runtime/sources
python3 -m unittest discover -s tests -v
python3 scripts/privacy_audit.py
python3 -m json.tool results/qualification.json >/dev/null
git diff --check
```

浅克隆仅用于本地只读审计，位于被忽略的 `runtime/`；没有提交第三方源码、raw trajectory、论文全文、密钥或个人信息。

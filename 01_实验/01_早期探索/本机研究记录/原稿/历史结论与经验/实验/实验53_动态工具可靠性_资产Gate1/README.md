# 候选组三 Gate1：动态工具可靠性估计与自适应恢复资产审计

本 Gate1 的严格裁决是 STOP_ASSET。它不测模型效果，不计入“同一冻结目标的三次方法失败”，也不把 OpenApps 的 GUI 变体或 ResiliBench 的参数化故障偷换成自然随机工具故障。

## 冻结目标与硬门

继承 Gate0 的冻结目标：

- 第一章只用当前 prefix、公开 tool schema、调用结果类别和依赖图，预测下一调用成功概率、failure type 与校准不确定性；主指标为 task-grouped Brier score。
- 第二章只能消费第一章 OOF 风险，执行 retry、alternative tool、dependency repair、checkpoint backtrack 或 safe stop，以 task success 为主指标。
- 需要至少 30 个 executor-derived next-call failure/type Gold、30 个 executable recovery Gold、按 task/tool/workflow 分组后 20 个 held-out、1 个无模型 offline replay、1 个自然/真实 Agent 外测和 2 个 tool/failure families。
- LLM/Judge 不能产生 Gold；未来错误不能泄漏到 pre-call prefix；构造故障不能作为唯一外部证据。

冻结 protocol 在 protocol/frozen_protocol.json，官方来源和 bytes/OID 在 manifests/source_manifest.json。

## Phase A 证据

| 资产 | 审计结果 | failure Gold | recovery Gold | 关键阻断 |
|---|---:|---:|---:|---|
| ResiliBench 300746f9... | 11 个 LFS pointer；计划 483,073,122 B（约 460.6 MiB） | 0 | 0 | 超过 250 MiB 总计划上限，未下载 payload；纸面 5,040 task/30 API 不能晋升为本地 Gold；构造故障不能独立作自然外测 |
| OpenApps 1103573a... | 28 original / 243 goal variations / 100 longer-horizon | 0 | 0 | 透明 state/reward 可复核，但仓库没有自然随机 tool-failure trajectory；GUI/config 变化不算 failure |
| WMA dd894640... | 8 sample JSON，共 80 行，样本动作/observation/next-state | 0 | 0 | 没有 executor failure/type/recovery 字段；样本是重复小样本；完整 WebArena 需要 Docker，轨迹脚本导入 OpenAI |
| ToolEVO b7eebb48... | test 15 文件/1,530 行；MCTS 15 文件/12,518 行 | 0 | 0 | JSONL 只有 qid/question/answer；官方主路径还需要外部 ToolQA/API server/权重；API variation 不是自然随机 failure Gold |
| ICLR 2026 capability-awareness | 只有官方论文入口 | 0 | 0 | 无可冻结 repo/trajectory；只能作为 overlap pressure，不能作本题 tool-failure Gold |

ResiliBench pointer 的每个 path/OID/size 都记录在 manifest。最大 pointer payload 为 63,513,155 B，且总和是预算的 1.84 倍；因此只审计 schema/metadata，不拉取任何 LFS 内容。

逐文件字段、空 failure/recovery 字段集合和 OpenApps state/reward 字段见 results/schema_census.json；资产数量和 bytes 见 results/asset_census.json。

### OpenApps 无模型 smoke

在本次运行中，使用 Python 3.12 临时 venv，仅安装 hydra-core 与 deepdiff，执行上游 task/reward comparator 两次：

- list_task_keys() 返回 271；
- AddToDoTask 对官方 initial_state.json 生成 target state，正例 reward check 为 true；
- 初始 state 作为负例 reward check 为 false；
- 两个新鲜进程结果一致；
- 这是 browser-free state/reward smoke，不是自然 tool failure replay，也没有模型、API、Docker。

若清理了 ignored runtime，runner 会将这项标记为 unavailable，不会把它算作 offline replay 硬门。

## Phase B 裁决

Phase A 已明确多个硬门为 0，因此 Phase B 不运行：

- next-call failure/type Gold：0 / 30
- executable recovery Gold：0 / 30
- grouped held-out：0 / 20
- qualified no-model replay：0 / 1
- natural/real-Agent external：0 / 1
- tool/failure families：0 / 2

在这些前置事实下继续拆分、重放或注入失败只会造成后验样本膨胀或构造标签，不能形成有效的可行性证据。results/split_replay.json 明确记录了未运行原因，results/qualification.json 的 counts_as_method_failure 为 false。

## 复现命令

第三方仓库只应放在 ignored runtime/sources，不要提交原始源码、轨迹或权重。已有 runtime 时：

    python3 scripts/audit_gate1.py --write-results
    python3 -m py_compile scripts/*.py
    python3 -m unittest discover -s tests -v
    python3 scripts/privacy_audit.py
    python3 -m json.tool results/qualification.json >/dev/null
    git diff --check

runner 不会自动 clone、下载 LFS、安装依赖、启动 Docker 或调用 API。OpenApps reward smoke 只在 runtime/openapps-venv312/bin/python（Python 3.12）存在时执行。代码和数据 license 只按官方仓库显示记录，不能从论文声称推断。

## 当前结论

候选三在严格的本题目标下没有可审计的两章 Gold/外测闭环，停止资产路线。这不等于“动态工具可靠性”问题在学术上不存在，而是当前选定官方资产无法在预算、无模型、无未来泄漏和自然外测约束下支撑该毕设题目；不应再投入模型实验或改写阈值。

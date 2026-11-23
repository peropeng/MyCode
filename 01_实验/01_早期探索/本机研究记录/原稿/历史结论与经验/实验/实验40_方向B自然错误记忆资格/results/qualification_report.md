# 方向 B 自然错误记忆/冲突资产 Gate 1 资格报告

日期：2026-08-21
执行分支：`exp/0821-direction-b-natural-memory`
基线：`main@1fc0cff539c2e09915694fa766871ad290eeb2ca`

## 1. 最终裁决

**Gate 1：STOP。** 本轮没有任何一个案例同时具备：历史 memory 内容、明确 retrieve/use 运行事件、目标工具调用、工具/任务结果，以及独立错误/过时/冲突 Gold。因此不能把四项资产合并计为自然有害记忆，也不能宣称方向 B 两章 GO。

| 门槛 | 结果 | 判定 |
|---|---:|---|
| 独立 task ≥100 | Mem2ActBench 去重 384 个 episode；ACL memory 23,388 条 token 记录，但两者都缺运行链字段 | 数量形式满足，语义资格不满足 |
| natural stale/conflict/error ≥30 | **0** | STOP |
| 代表审计 ≥80% 真依赖记忆且有工具行为 | 不能计算：没有 natural case；Mem2ActBench 的 target tool Gold/source tool turn 不是 memory manager 的运行结果 | STOP |

## 2. ACL 2026：How Memory Management Impacts LLM Agents

正式论文：[ACL Anthology 2026.acl-long.27](https://aclanthology.org/2026.acl-long.27/)。作者仓库：[yuplin2333/agent_memory_manage](https://github.com/yuplin2333/agent_memory_manage)，锁定 `4dc29e366965de25bb61b42ee4d0188f0f453c28`；根目录没有 LICENSE/COPYING/NOTICE，许可证 **UNKNOWN**。

论文 README 的运行入口是 `python main_strict.py`（错误经验会被加入 memory 的主实验）和 `python main_noerrorprop.py`（用 reference result 做 error-free 对照）。入口依赖外部 Agent-Driver、预缓存 nuScenes 数据、`gt_traj.pkl` 和 OpenAI API/模型，仓库本身只提供 patch。

通过官方 Agent-Driver 入口 [PointsCoder/Agent-Driver](https://github.com/PointsCoder/Agent-Driver)（MIT，锁定 `292ff04e89b3f7a7925e93be202a85d87862763c`）和作者官方 Drive 文件夹取得并审计。所有 pickle 读取均在 Docker 沙箱中完成，主审计脚本不执行反序列化；本轮安全摘要为 `SANDBOXED_OK`，image ID 为 `sha256:65cb5e44fe73b63aa5f979d36713382f2f15a7b1246978f7d69bb644eb10eedb`，运行命令包含 `--network none --read-only --cap-drop ALL --security-opt no-new-privileges:true --pids-limit 128`，输入只读挂载，输出写入专用目录。

沙箱记录的输入指纹为：`agentdriver_memory/memory/database.pkl` 122,151,034 bytes / SHA-256 `ac87c2a23bf1356c3328a1cff21f7aaae0663b216ad0f9ca0be397cffaed14fc`；`agentdriver_gt_traj.pkl` 993,403 bytes / SHA-256 `217b25beb3af89cdafad4446d1b10255c5a71839453cbc41432b42340c80f571`。

通过该安全边界取得并审计：

- `memory.zip`：HTTP 200，66,833,778 bytes；解压 `memory/database.pkl` 116 MB，`dict` 共 **23,388** 条 token 记录。
- 每条记录字段恰为 `ego_fut_traj`、`ego_fut_traj_diff`、`ego_hist_traj`、`ego_hist_traj_diff`、`ego_states`、`goal`、`objects`；没有 error、label、score、Gold、retrieval、use、tool、task-result 字段。
- `metrics.zip`：HTTP 200，19,637,745 bytes；读取 `gt_traj.pkl` 得 **6,019** 条 val token。与 memory database token 交集为 **0**，所以本轮不能把 GT 误配给 memory 记录来制造错误标签。
- `finetune.zip` 因网络 SSL 失败未取得；`val.zip` 标称约 4.35 GB，未下载，避免无必要的大数据消耗。二者不是本轮 Gate 1 的必要条件。

论文确实讨论 error propagation 与 misaligned experience replay，但该论断不是逐条可复核的自然 memory trace。现有 binary 只说明“过去预测轨迹被存储”，不能证明某条错误 memory 被 retrieve/use 后改变了后续工具/任务结果；合格自然案例数 **0**。

## 3. Fine-Mem

正式论文：[ACL Anthology 2026.acl-long.900](https://aclanthology.org/2026.acl-long.900/)。作者仓库：[LVYUERLVR/Fine-Mem](https://github.com/LVYUERLVR/Fine-Mem)，锁定 `8f36a39e6eb91c32fb0ce9bed2ce1efa4c58b2e2`，根 LICENSE 为 **Apache-2.0**。

仓库实际只有 README 和 LICENSE，没有数据、session、运行结果或轨迹清单。论文层面定义 memory item `{id, content, update_step}`，操作为 `INSERT/UPDATE/DELETE/SKIP`；chunk-level QA 由 GPT-4o-mini 构造，EARA 需要追踪 downstream retrieve 到 memory operation，但这些 records/labels 没有随官方仓库发布。论文声称使用 Memalpha 与 MemoryAgentBench，未在此官方仓库提供数据 URL 或可下载的自然错误经验。

因此 Fine-Mem 自身可作为接口参考，不能提供自然案例；合格数 **0**。未运行 VERL/RL/GPU 或付费 API。

## 4. AgeMem

正式论文：[ACL Anthology 2026.acl-long.981](https://aclanthology.org/2026.acl-long.981/)。作者仓库：[y1y5/AgeMem](https://github.com/y1y5/AgeMem)，锁定 `98f563f907d67b2f2436e3ae7b7ceff32e482814`。根目录没有 LICENSE；`pyproject.toml` 的 Apache classifier 不是许可证授权文本，故许可证 **UNKNOWN**。

README/代码声明六个 tool：`Summary_context`、`Clear_context/Filter_context`、`Retrieve_memory`、`Add_memory`、`Update_memory`、`Delete_memory`。训练数据依赖外部 HotpotQA；schema 是 `question`、`answer`、`context`、可选 `supporting_facts`。仓库没有自然跨 session memory operation logs、stale/conflict/error Gold 或任务结果轨迹，且正式训练入口 `trinity run --config examples/agemem_hotpotqa/agemem_train.yaml` 需要大模型、Ray/vLLM、DashScope key 和 RL 资源。

因此 AgeMem 只有“代码支持主动操作”的资格，不提供自然案例；合格数 **0**。未下载 HotpotQA、模型或运行 RL。

## 5. Mem2ActBench

正式论文：[ACL Anthology 2026.acl-long.370](https://aclanthology.org/2026.acl-long.370/)。作者代码/数据：[Cantaloupe-M/Mem2ActBench](https://github.com/Cantaloupe-M/Mem2ActBench)，锁定 `b00726940b5abbe9bd324bdd7a2cb272f5c62a29`。README 声称 MIT，但 pinned repo 没有 LICENSE；上游 BFCL/OASST1/ToolACE 条款未审，整体许可证 **UNKNOWN**。

脚本读取完整 `qa_dataset.jsonl` 与 `toolmem_conversation.jsonl`，并按排序 source IDs 去重：

| 字段 | 数量 |
|---|---:|
| QA 行 | 400 |
| session 行 | 2,029 |
| 去重 episode | 384 |
| 有 evolution/history memory content | 375 |
| 有完整 selected source session | 310 |
| 有历史 assistant tool call + tool result | 307 |
| 有 target tool Gold 合同 | 384 |
| 有显式 memory lifecycle/retrieve trace | 0 |
| 有 target task result（不是 source history result） | 0 |
| 有显式 stale/error-memory Gold | 0 |
| `has_temporal_conflict` 元数据 episode | 25 |
| conflict CSV 有 discarded source 的行 | 145 |
| discarded source 与 QA source overlap | 0 |
| natural qualified cases | **0** |

关键边界：`tool_call` 是 reverse-generated 目标合同，不是被测 Agent 已执行的 target action；session 内的 source assistant/tool turns 是历史来源行为，不是 memory manager retrieve/use。L4、temporal-conflict 元数据和 discarded lineage 是构造流水线证据，不能作为自然 harmful-memory Gold。`natural_case_manifest.jsonl` 对 384 个 episode 全量逐项记录上述布尔字段和失败原因，没有复制对话正文。

## 6. 复现和下一动作

```bash
scripts/run_binary_audit_docker.sh assets results/binary_audit_sandbox
python3 scripts/audit_natural_assets.py --binary-summary results/binary_audit_sandbox/acl_binary_summary.json
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/audit_natural_assets.py
git diff --check
```

机器可读证据：`manifests/asset_manifest.json`、`results/audit_summary.json`、`results/natural_case_manifest.jsonl`。最低成本的继续条件是从作者取得许可清楚的跨 session 自然运行轨迹，并逐项提供 memory content、retrieve/use、target tool call、tool/task result、独立 error/stale/conflict label；否则方向 B 停止两章投入，仅保留“长上下文记忆驱动工具调用”子题。

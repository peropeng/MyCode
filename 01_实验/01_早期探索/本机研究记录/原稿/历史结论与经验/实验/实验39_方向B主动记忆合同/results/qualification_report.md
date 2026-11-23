# 实验39：方向 B 主动记忆合同可行性报告

日期：2026-08-21

## 结论先行

- 本轮是 **constructed/recomposed feasibility harness**，不是 Mem2ActBench 自然 benchmark 结果；共执行 30 个任务。
- 10 stale / 10 conflict / 10 error-memory intervention 标签均已覆盖；构造干预依赖通过 30/30，clean replay 通过 30/30。三类使用同一 policy/store/evaluator，不是三种方法效果。
- 构造合同子门槛：**GO**；方向 B 总 Gate 1：**CONDITIONAL**。本轮不宣称 Gate 3、RQ1/RQ2 或两章 GO。

## 机器可复核统计

| 指标 | 结果 |
|---|---:|
| 任务数 | 30 |
| 类别计数 | `{"conflict": 10, "error_memory": 10, "stale": 10}` |
| 构造干预依赖（非真实 Agent 依赖） | 30/30 (100.0%) |
| clean replay | 30/30 (100.0%) |
| source trace 已记录（含显式缺失标记） | 30/30 |
| 选定 source 的完整 shipped session trace | 0/30 |
| discarded source session 缺口被显式记录 | 30/30 |
| 篡改/移除 memory 改变工具观测 | 30/30 |

## 合同和隔离

1. 每项任务固定引用 conflict CSV 行、sorted/discarded source IDs、原始事实 CSV 行以及已 shipped 的 session/turn；缺失的 discarded session 以 `not_present_in_shipped_toolmem_conversation` 明确记录。`source_trace_documented` 不等于完整自然 session trace；本轮 30 项的完整 selected-source session trace 为 0/30。
2. `MemoryStore` 显式记录 `add/retrieve/update/delete`。正确、无记忆、有害记忆三个条件都单任务重放；无记忆条件只写入无关 decoy，不向目标 key 提供答案。
3. Agent-facing `online_view` 只含 query、工具 schema、当前 memory observation；事实指纹由 agent 从可见 fact 文本计算。expected fingerprint、expected args 和自然标签只在 evaluator-only Gold 中使用。
4. 重复运行使用无时间戳、无随机数的 store 和 policy；输出包含逐任务 JSONL、汇总 JSON 和本报告。

## 已实测与仍 UNKNOWN

已实测：30 个任务的三条件重放、store 生命周期、Gold/online 隔离、重复一致性、memory 删除/篡改敏感性、类别计数和 trace 字段。构造干预依赖是固定 policy 从 fact_text 计算指纹并由同一合同 Gold 判定的结果，不是自然任务或真实 Agent 依赖。

仍 UNKNOWN：真实 agent/真实记忆管理器的泛化；discarded lineage 是否在上游完整会话中代表自然 stale/error memory；源数据及上游代码再分发许可；Gate 3 utility；RQ1/RQ2；两章论文效应。三类 intervention 标签不对应三种不同治理算法，不能把 30/30 解读为三类方法效果。

## 复现

```bash
scripts/run_gate1.sh
python3 -m unittest discover -s tests -v
```

结果目录可删除后重建；runner 只依赖已提交的 task manifest，不需要下载大数据。

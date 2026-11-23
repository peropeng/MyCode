# Exp85：责任主体到步骤排序的去捷径抗坍缩资格

## 结论

本实验结论更正为 `GO_CANDIDATE_PENDING_ERROR_LENGTH_AUDIT`：在 E33 的 AFTraj fresh confirmation task groups 上，去除位置、任务文本/ID、域名和原始角色身份后，责任主体到步骤的 bridge 仍然有效；但错误/验证/重试词以及长度/活动量特征仍保留在输入中，因此暂不能称为完整 `REPRODUCED_ROBUST_GO`。这是一项部分去捷径正向候选，不是两个独立章节 GO，也不是外部 Agent 数据确认。

## 先复现原结果

只读复用了 E33 的冻结源码和 AFTraj 数据。原始 `run_confirmation.py` 在 911 条 pool 中得到 731 train、180 confirm，官方 test overlap removed=40；生成的 `confirmation_results.json` 与历史文件字节级一致，SHA-256 均为 `7722178c087ddee1ce8ea526543d7b64ebe03043c61a8a30d13b0b49739c3cce`。

历史结果的中文含义是：E1 责任主体 Top-1 为 71.11%，强基线 58.89%，相对提高 20.75%；E2 full MRR=0.5002，no_bridge/local MRR=0.3909，相对提高 27.96%，paired task-group bootstrap 95% CI 下界为 0.0810。

## 冻结的唯一诊断

- 每条轨迹按真实角色首次出现顺序改成 `role_0`, `role_1`, …；原始角色名和角色身份规则不进入模型。
- `task` 清空、`conv_id` 变成 opaque id、`domain` 清空；`task_group` 只用于切分和分组抽样。
- E1 只保留 9 个可观察统计特征：消息数/比例、长度统计、错误/验证/重试密度、角色数和失败输出标记；位置、角色身份、域名和 task overlap 特征删除。注意：这意味着错误词和长度/活动量仍在输入中，本实验没有审计它们。
- E2 固定 `w_pos=0`；同分排序使用匿名角色加当前内容的稳定哈希，不读取步骤 index。`recency` 是明确报告的简单强基线。
- `mistake_agent` 只作为 train task_group 的 E1 监督标签，绝不作为输入特征；confirm 的 `mistake_agent` 和所有 `mistake_step` 只用于评分。5-fold train OOF 和 train→confirm bridge 都按 task_group 严格样本外。

## 去捷径结果（三个预注册 seed）

每个 E2 数字按 `[R@1, R@3, MRR]` 排列；三个 seed 的点估计完全一致。

| 条件 | R@1 | R@3 | MRR | 相对最强公平基线 |
|---|---:|---:|---:|---:|
| full 去捷径 bridge | 29.44% | 66.67% | **0.5143** | **+23.69%** |
| local | 17.78% | 57.22% | 0.4158 | — |
| no_bridge | 17.78% | 57.22% | 0.4158 | — |
| recency | 8.89% | 41.11% | 0.3234 | — |
| shuffle bridge | 14.44%--16.11% | 41.67%--46.67% | 0.3603--0.3780 | 低于 no_bridge |

Full 相对 local/no_bridge 的 task-group paired bootstrap 95% CI 下界在三个 seed 为 0.0672、0.0683、0.0678，全部大于 0；相对提高均为 23.69%。配对逐组比较为 93 个 better、31 个 worse、56 个 tie。删除 bridge 后 no_bridge 与 local 完全相同；在每条轨迹内置乱 bridge 概率后 MRR 下降到 0.3603--0.3780，因此 bridge 的增益不是任意分数或额外预算造成的。

E1 也保留正向信号：去捷径方法 Top-1=69.44%，最强 train-only baseline 是匿名后的 majority=59.44%，相对提高 16.82%；168 个 task groups 中 23 better、5 worse、152 tie，paired CI 下界为 0.0476。

## 已通过与尚未通过的范围

已通过的只是四类条件：原始角色身份、任务文本/ID、域名，以及 E2 的显式位置项和 index tie-break。尚未通过、也没有在 Exp85 中测试的是：`sig_density`、`ver_density`、`retry_density`、`has_fail_output` 等错误/验证/重试词面，以及 `avg_len`、`tot_len`、`frac_msgs`、`n_msgs` 等长度/活动量信息。它们可能仍然解释一部分提升，所以 Exp85 的数值必须保留，但正式稳健 GO 暂缓。

## 为什么不是“无条件论文 GO”

本实验只证明一个冻结 AFTraj confirmation 条件下、部分去捷径后的正向可行性。AFTraj 仍是单一外部轨迹资产，且 E1→E2 是一个依赖级联，不能拆成两个独立 GO。下一步由独立 Exp88 冻结审计错误词、错误标记、验证/重试词和长度/活动量；在 Exp88 前不计正式稳健 GO。若后续失败，停止的应是那个具体错误词/长度审计配置，而不是把 Exp85 的部分正向候选改写成方向 NO-GO。

完整 JSON、哈希审计、每 seed 原始 rank 和 OOS 细节见 `results/aggregate_results.json`、`results/original_replay/`、`results/robust/`。冻结协议和单测在同目录根部。

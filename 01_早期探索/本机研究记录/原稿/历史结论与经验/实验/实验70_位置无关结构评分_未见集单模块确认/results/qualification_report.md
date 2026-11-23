# 实验70结果：未见集单模块确认

实验状态：`STOP_POSITION_INVARIANT_SCORE_CONFIRM`

这不是 `TRUE_METHOD_NO_GO`。输入、基线、模型、切分和审计均有效，但本轮未得到
探索继续所需的真实 pooled 正增益，因此停止该结构模块在当前确认对象上的继续迭代。

## 冻结与数据

* 冻结提交：`935c6f0a2567ff8d4fe491895a92d601e4a5f2f4`。
* 最终 runner 修复提交：见本实验分支最后提交；修复只抑制已知的有限 NumPy matmul
  warning，不改变计算。
* 确认源：`planning_single_hard.jsonl`，158 rows、97 UUID，SHA-256
  `9ba7bc2d5ba8762bdf2c81156ce3d2d62ccc95f018d5a2d5d1543d6ec84c1ae5`。
* 三个预注册 orientation seed：`20260822`、`20260824`、`20260825`；比例分别为
  `0.512658`、`0.500000`、`0.474684`。
* API calls/network calls：`0/0`。
* `tool_irrelevance.jsonl`：未打开、未统计、未哈希。

## 主结果

三 seed 作为方向鲁棒性检查，UUID 是唯一 paired statistical unit：

| seed | Base | Base+A | delta |
|---:|---:|---:|---:|
| 20260822 | 0.645570 | 0.601266 | -0.044304 |
| 20260824 | 0.556962 | 0.613924 | +0.056962 |
| 20260825 | 0.594937 | 0.582278 | -0.012658 |

474 个 seed-row observations 的 pooled accuracy：

* Base：`0.599156`
* Base+A：`0.599156`
* delta：`0.000000`，relative gain：`0.000000`
* UUID 中 Base+A 更好/更差/持平：`28/36/33`
* paired UUID bootstrap（97 UUID、10000 次、seed `20260826`）：估计
  `-0.032646`，95% CI `[-0.102520, 0.038946]`

Swap consistency 为 Base `0.272152`、Base+A `0.550633`。这说明结构模型比错误数
heuristic 更接近位置互补，但没有转化为准确率增益。

长度层 pooled delta：short `+0.033333`（7 UUID）、medium `-0.016667`
（84 UUID）、long `+0.250000`（6 UUID）。短/长层数量不足以作为独立确认，且中层占
绝大多数；不能事后将长层结果当作总体 GO。

## 审计结论

`all_orientation_balanced=true`、`uuid_cross_statistical_unit=false`、
`forbidden_semantic_fields_read=false`、原始轨迹和逐行 label 均未持久化；只保留
hash、数值和布尔审计结果。首次运行前的冻结资产校验 bug 已在 `952b507` 修复，
确认集内容在修复前未打开；修复后直接重算结果与 JSON 完全一致。

本结果只排除“全量使用冻结结构模型在该未见集上稳定优于 frozen heuristic”的假设，
不排除尚未测试的长度/不确定性选择性门控；后者必须另行预注册并使用保留的
`tool_irrelevance.jsonl` 或新的严格确认集。

# 实验12数据与审计附件

- 当前严格状态：**NO-GO**
- 原编号：`E023`
- 机器资产：`实验/实验12_责任主体预测/`
- 主结论：`结论/结论12_实验12_责任主体预测_NO-GO.md`

本文件保存详细指标、原结果摘录和审阅证据；研究判断以主结论为准。

## 原实验结果与指标

以下内容直接并入原结果/报告；它们保留当时数字和判断，但最终等级以本文件开头的严格状态为准。

### 来源：旧实验裁决__实验__失败与停止__E023_NO-GO_责任主体预测__强基线阻断记录.md

### 近年强协议核验与阻断记录

#### MP-Bench 公开仓库

本轮下载了 MP-Bench 代码仓库实际提交 `65cae1f9db9de342f604822416f29c1f59ee5534` 并检查 `leaderboard.json` 和 `submissions/`：

- `leaderboard.json` 只公布 All-at-Once Qwen3-8B 的 aggregate step-level nDCG@5（manual 0.317、automatic 0.676），没有逐轨迹、逐 Agent 的预测文件。
- 仓库唯一 `sample_submissions/predictions_*.json` 是每条轨迹统一 `[0,1,2]` 的示例，不是 Qwen3-8B 输出；不能冒充可比较的 Qwen3 预测。
- 官方运行脚本依赖 Qwen3 模型和本地推理栈/API；当前受控环境没有 `torch`、`transformers`、`accelerate` 或可用 API 密钥。未把 leaderboard 的 step-level 数字换算成 Agent nDCG，也未将样例当强基线。

#### Who&When 官方协议

实际执行：

```text
python3 third_party/WhoWhen/Automated_FA/inference.py \
  --method all_at_once --model gpt4o-mini \
  --is_handcrafted False \
  --directory_path third_party/WhoWhen/Who&When/Algorithm-Generated
```

退出码为 1，首个阻断为 `ModuleNotFoundError: No module named 'dotenv'`；同时环境没有 `openai`、`torch`、`transformers`、`accelerate` 和 `OPENAI/AZURE/HF` 密钥。由于方向1和方向2在公开简单基线前已分别 NO-GO，按照冻结规则没有继续下载大模型或把协议阻断包装成成绩。

#### 结论

本轮两次 NO-GO 是在同数据、同分组、同预算的可运行简单基线比较中得到的科研结果，不是强基线环境失败导致的 NO-GO。若 Sol/high 审查后提出第三方向并通过简单门槛，再单独补齐公开 Qwen3/Who&When 协议；本文件中的阻断证据不支持声称已超过官方强基线。

### 来源：旧实验裁决__实验__失败与停止__E023_NO-GO_责任主体预测__方向1_全局结构软回归__结果.md

### RQ1 公开专家标签结果

- 轨迹总数：289
- 有效责任软标签轨迹：277
- 最强可运行基线：`most_content`
- 主指标 nDCG：方法 0.9056；基线 0.8844；相对提升 2.39%
- GO：NO-GO
- 科研无进展计数：1/2（方法 nDCG 未达到预注册 10% 门槛；不是环境或代码失败）

#### 方法和基线

- `method`: nDCG 0.9056, Top-1 0.5848, Brier 0.0550, 覆盖率 1.0000
- `masked_error`: nDCG 0.9041, Top-1 0.5957, Brier 0.0552, 覆盖率 1.0000
- `with_names_diagnostic`: nDCG 0.9044, Top-1 0.5776, Brier 0.0550, 覆盖率 1.0000
- `order_reversed`: nDCG 0.9056, Top-1 0.5848, Brier 0.0550, 覆盖率 1.0000
- `random`: nDCG 0.7531, Top-1 0.2888, Brier 0.0733, 覆盖率 0.9711
- `last_active`: nDCG 0.8466, Top-1 0.5054, Brier 0.0605, 覆盖率 0.9964
- `most_active`: nDCG 0.8723, Top-1 0.5632, Brier 0.0574, 覆盖率 1.0000
- `most_content`: nDCG 0.8844, Top-1 0.4982, Brier 0.0565, 覆盖率 1.0000
- `full_trace_direct`: nDCG 0.8583, Top-1 0.4765, Brier 0.0666, 覆盖率 0.9964

#### 快捷方式审计

```json
{
  "role_anonymous_ndcg": 0.9055885437390864,
  "with_role_names_diagnostic_ndcg": 0.9043584922724094,
  "role_name_increment": -0.0012300514666769846,
  "role_order_permutation": {
    "protocol": "reverse first-appearance candidate list; role-keyed scores",
    "ndcg": 0.9055885437390864,
    "delta": 0.0
  },
  "error_word_mask_ndcg": 0.904108368059701,
  "error_word_mask_delta": -0.0014801756793854093,
  "gain_retention_after_error_mask": 0.9299846679099898
}
```

#### 统计

```json
{
  "ndcg": {
    "delta": 0.0211407363958874,
    "ci_low": 0.0050870488871393085,
    "ci_high": 0.03585521058714877,
    "n": 277
  },
  "top1": {
    "delta": 0.08664259927797834,
    "ci_low": 0.018050541516245487,
    "ci_high": 0.15162454873646208,
    "n": 277
  },
  "brier": {
    "delta": -0.0014953641561180743,
    "ci_low": -0.0036179169564995355,
    "ci_high": 0.0007067240676634917,
    "n": 277
  },
  "cross_entropy": {
    "delta": -0.009784878019070228,
    "ci_low": -0.021231995869020522,
    "ci_high": 0.002230121249818742,
    "n": 277
  },
  "coverage": {
    "delta": 0.0,
    "ci_low": 0.0,
    "ci_high": 0.0,
    "n": 277
  }
}
```

### 来源：旧实验裁决__实验__失败与停止__E023_NO-GO_责任主体预测__方向2_局部峰值成对排序__结果.md

### 方向2结果：局部证据峰值与轨迹内成对排序

- 轨迹总数：289；有效标签：277
- 主指标 Top-1：方法 0.5704；最强简单基线 `most_active` 0.5632；相对提升 1.28%
- GO：NO-GO
- 科研无进展计数：2/2（新方法 Top-1 未达到预注册 10% 门槛；不是环境或代码失败）

#### 方法与基线

- `method`：Top-1 0.5704
- `masked_error`：Top-1 0.5848
- `with_names_diagnostic`：Top-1 0.5632
- `order_reversed`：Top-1 0.5704
- `random`：Top-1 0.2888
- `last_active`：Top-1 0.5054
- `most_active`：Top-1 0.5632
- `most_content`：Top-1 0.4982
- `full_trace_direct`：Top-1 0.4765

#### 快捷方式审计

```json
{
  "role_anonymous_top1": 0.5703971119133574,
  "with_role_names_diagnostic_top1": 0.5631768953068592,
  "role_order_permutation_top1": 0.5703971119133574,
  "error_word_mask_top1": 0.5848375451263538,
  "gain_retention_after_error_mask": 3.0
}
```

#### 主比较的 paired bootstrap

```json
{
  "delta": 0.007220216606498195,
  "ci_low": -0.039711191335740074,
  "ci_high": 0.05776173285198556,
  "n": 277
}
```

### 来源：旧实验裁决__实验__失败与停止__E023_NO-GO_责任主体预测__科研进展台账.md

### RQ1 科研进展台账

#### 第 1 次科研无进展：方向1 全局结构软回归

- 研究改变：角色无关的整条轨迹结构/内容证据 + 训练折内岭软回归。
- 有效实验：289 条公开轨迹，277 条有责任软标签；按规范化题面哈希五折 grouped OOF；5 项单元测试通过。
- 最强简单基线：`most_content`，Agent nDCG 0.8844478。
- 方法：Agent nDCG 0.9055885，相对 +2.39%；paired bootstrap 95% CI [0.0050870, 0.0358552]。
- 结论：统计上有正增益，但低于预注册 10% 门槛，NO-GO；这是科研无进展，不是下载、环境或代码失败。

#### 第 2 次科研无进展：方向2 局部峰值成对排序

- 研究改变：前/当前/后匿名局部窗口峰值 + 同轨迹责任 Agent 成对差分排序；不复用方向1的全局软回归目标。
- 有效实验：同一 277 条公开软标签轨迹、同一题面分组和五折 OOF；方向2额外 3 项单元测试通过。
- 最强简单基线：`most_active`，Top-1 0.5631769。
- 方法：Top-1 0.5703971，相对 +1.28%；paired bootstrap 95% CI [-0.0397112, 0.0577617]。
- 结论：未达到 10% 门槛且区间跨 0，NO-GO；这是第二次科研无进展，不是下载、环境或代码失败。

#### 规则触发

两次独立科研方向均完成真实数据、分组 OOF、基线、审计和统计后仍未过门槛，已达到“科研两次无进展”触发条件。下一步应由主线程调用 Sol/high 做独立审查和新方向调研；本执行分支不再自行开展第三个方向，也不降低门槛。

### 来源：旧实验裁决__实验__失败与停止__E023_NO-GO_责任主体预测__结果.md

### RQ1 公开专家标签结果

- 轨迹总数：289
- 有效责任软标签轨迹：277
- 最强可运行基线：`most_content`
- 主指标 nDCG：方法 0.9056；基线 0.8844；相对提升 2.39%
- GO：NO-GO

#### 方法和基线

- `method`: nDCG 0.9056, Top-1 0.5848, Brier 0.0550, 覆盖率 1.0000
- `masked_error`: nDCG 0.9041, Top-1 0.5957, Brier 0.0552, 覆盖率 1.0000
- `with_names_diagnostic`: nDCG 0.9044, Top-1 0.5776, Brier 0.0550, 覆盖率 1.0000
- `order_reversed`: nDCG 0.9056, Top-1 0.5848, Brier 0.0550, 覆盖率 1.0000
- `random`: nDCG 0.7531, Top-1 0.2888, Brier 0.0733, 覆盖率 0.9711
- `last_active`: nDCG 0.8466, Top-1 0.5054, Brier 0.0605, 覆盖率 0.9964
- `most_active`: nDCG 0.8723, Top-1 0.5632, Brier 0.0574, 覆盖率 1.0000
- `most_content`: nDCG 0.8844, Top-1 0.4982, Brier 0.0565, 覆盖率 1.0000
- `full_trace_direct`: nDCG 0.8583, Top-1 0.4765, Brier 0.0666, 覆盖率 0.9964

#### 快捷方式审计

```json
{
  "role_anonymous_ndcg": 0.9055885437390864,
  "with_role_names_diagnostic_ndcg": 0.9043584922724094,
  "role_name_increment": -0.0012300514666769846,
  "role_order_permutation": {
    "protocol": "reverse first-appearance candidate list; role-keyed scores",
    "ndcg": 0.9055885437390864,
    "delta": 0.0
  },
  "error_word_mask_ndcg": 0.904108368059701,
  "error_word_mask_delta": -0.0014801756793854093,
  "gain_retention_after_error_mask": 0.9299846679099898
}
```

#### 统计

```json
{
  "ndcg": {
    "delta": 0.0211407363958874,
    "ci_low": 0.0050870488871393085,
    "ci_high": 0.03585521058714877,
    "n": 277
  },
  "top1": {
    "delta": 0.08664259927797834,
    "ci_low": 0.018050541516245487,
    "ci_high": 0.15162454873646208,
    "n": 277
  },
  "brier": {
    "delta": -0.0014953641561180743,
    "ci_low": -0.0036179169564995355,
    "ci_high": 0.0007067240676634917,
    "n": 277
  },
  "cross_entropy": {
    "delta": -0.009784878019070228,
    "ci_low": -0.021231995869020522,
    "ci_high": 0.002230121249818742,
    "n": 277
  },
  "coverage": {
    "delta": 0.0,
    "ci_low": 0.0,
    "ci_high": 0.0,
    "n": 277
  }
}
```

## 历史综合复盘

### 既有复盘

- **E023 责任主体预测：**回答主体软预测与局部步骤排序能否组合；不能把主体标签当因果或当前题目；只能说明强基线和 OOF 桥接要求。后续受用户禁多 Agent 责任主体主线、标签构造和数据边界影响而降级。

## 来源索引

- `旧实验裁决__实验__失败与停止__E023_NO-GO_责任主体预测__强基线阻断记录.md`
- `旧实验裁决__实验__失败与停止__E023_NO-GO_责任主体预测__方向1_全局结构软回归__结果.md`
- `旧实验裁决__实验__失败与停止__E023_NO-GO_责任主体预测__方向2_局部峰值成对排序__结果.md`
- `旧实验裁决__实验__失败与停止__E023_NO-GO_责任主体预测__科研进展台账.md`
- `旧实验裁决__实验__失败与停止__E023_NO-GO_责任主体预测__结果.md`

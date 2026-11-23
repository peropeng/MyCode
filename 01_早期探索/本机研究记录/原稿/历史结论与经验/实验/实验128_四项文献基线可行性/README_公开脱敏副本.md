# Exp128：四项文献基线可行性实验

**状态：四项真实小样本诊断与恢复均已完成。** All-at-Once、Binary Search、SDBL（EASD）统一使用官方 DeepSeek V4.1 Flash API；StepFinder 保持原生学习模型。

| 方法 | AF 六条步骤命中 | moto 三状态恢复 | 三状态提交次数 |
|---|---:|---:|---|
| All-at-Once | 4/6 | 3/3 | 2／1／1 |
| Binary Search | 2/6 | 3/3 | 1／1／1 |
| SDBL（EASD，论文重建） | 5/6 | 3/3 | 2／1／1 |
| StepFinder | 3/6 | 3/3 | 3／2／1 |

真实 API 请求57次，输入410,381、输出2,144 tokens；按官方闲时费率估算 **0.39361812元**。账户余额 **[账户数值已隐去]→[账户数值已隐去]元人民币**，全程执行1元余额下限及逐次最坏费用预留。所有恢复、保护和合法编辑检查通过。

All-at-Once一次角色格式失败保留在分母。EASD Scope Hit@3为0/6，不能把最终定位成绩解释为范围划定收益。三个恢复状态候选很少、没有错误后的后续编辑，只证明可行性，不证明排序或闭包优越。历史全731条MRR仍为本文0.496057、StepFinder0.845827。

- [当前完整对比报告](API完整对比报告.md)：诊断、恢复、费用、失败原因和适配限定。
- `LATEST.json`：当前交付入口；`results/final_comparison/comparison.json`：机器可读四项完整比较及CSV分表。
- `results/flash_api_v1/`：三项真实API预测；`results/api_calls/`：全部请求、响应、usage与前后余额。
- `recovery/runs/*_flash_v1/`：三项新增恢复结果；`recovery/runs/stepfinder_v2/`：未改动的真实StepFinder恢复结果。
- `results/final_delivery_verification.json`、`stepfinder/api_result_independent_review.json`：完整性与独立复核。
- `protocol.json`、`protocol_api_amendment_20261002.json`、`authorization.balance_20261002.json`：协议与此次明确授权。
- [最初免费阶段记录](README_初始免费阶段.md)：历史资源门、StepFinder初跑和修复；其中“API尚未授权”是当时状态，已被后续人的明确授权替代。

原始 `delivery_manifest.json` 对应初始提交 `ce8d54f`；当前文件封存见 `final_delivery_manifest.json`。API生成前代码提交为 `518cd99`，预测程序和输入在生成后没有更改。只读复核使用 `verify_delivery.py --include-api --out <新的结果文件>`，不必重复调用API或重新执行原生测试。

SDBL仍属论文重建；作者完整提示和角色权限表未公开，未知权限不凭名字补造。其余机制与来源详见 `literature/机制核对.md`。本轮无需更换基线，也没有扩大为全量运行。

# Exp84：TraceElephant 选择门零样本步骤外测

本实验只检验 Exp80 的冻结 `no_length_C` 选择门能否在 TraceElephant 的 failure-only ordered traces 上进行外部决定步骤定位。它不是 Exp80 safe/unsafe 配对 Exact-F1 的确认，也不把失败轨迹之前的成功前缀伪装成 safe execution。

## 固定边界

- 数据固定为 TraceElephant HF revision `a78a57cdcdf74a080b1bec0f56f85228d86acbac`。
- 只复用 Exp81 已下载的 ZIP central directory；只用 HTTP Range 读取其余 `trace_metadata.json` 与 `step_records.json` 成员，不读取 PNG、不下载完整 ZIP。
- 已用于适配器开发的 `assistantbench_task_0_gpt-4o_8jqg5bbthx21` 整个 run 在资格筛选前排除，不计入任何指标。
- Base/A/18 维 C 参数逐字节来自 Exp80 `results/pre_unseal.json`，TraceElephant 不调参、不调用 LLM/API。
- 适配器只产生因果前缀结构特征：匿名角色相等性、tool-call 结构、输出/输入存在性；不读任务说明、Gold、错误原因、语义文本或未来事件。

## 运行

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile adapter.py runner.py
python3 runner.py --output-dir .
git diff --check
```

成功运行后：

- `source_manifest.json` 记录每个 Range 请求的 URL、精确范围、HTTP 206、Content-Range、字节数和 SHA-256；
- `results/exp84_result.json` 记录资格计数、Base/A/C 及固定对照、任务组 paired bootstrap、非首步层和审计结论；
- `results/row_predictions.json` 记录去标识逐行 step_id 映射；
- `runtime/` 只用于临时文件（如果产生），不提交。

资格不足、Range 不是 206、范围不精确、JSON/step_id 不可审计或超过 80 MiB 时，结论是 `ASSET_ADAPTER_STOP` 或 `HARNESS_INVALID`，不会解释成方法 NO-GO。

## 本次实际结果

修复并强制 `recovery_evidence=0` 后的第四次科学执行通过全部 Harness 和泄漏审计：219 个剩余 run 中 217 条符合资格，覆盖 172 个 task group；2 条因 `mistake_step` 不可解析排除。876 个 Range 响应全部为 HTTP 206 且范围精确，总下载 37,181,864 B（约 35.5 MiB），无 PNG/整包/API。

| 方法 | Exact StepAcc | 正确条数 | ASS（非 abstain） |
|---|---:|---:|---:|
| Base | 1.843% | 4/217 | 12.416 |
| A | 1.843% | 4/217 | 9.258 |
| C | 1.843% | 4/217 | 9.258 |
| always-step1 | 5.530% | 12/217 | 9.945 |
| midpoint（最强公平基线） | 8.295% | 18/217 | 7.465 |

因此本次主指标没有 `C > Base`，且 C 比 midpoint 低 6.452 个百分点（paired bootstrap 95% CI [-10.714, -2.336]），裁决为 `ZERO_SHOT_NOT_ESTABLISHED`。绝对范围是：只否定当前 TraceElephant failure-only 适配器上的 Exp80 C Exact StepAcc 零样本外推；不否定 Exp80 方向，也不把资产或 Harness 问题写成方法 NO-GO。

仍保留一个次级信号：C 将 Base 的 ASS 从 12.416 降到 9.258，并把覆盖率从 82.028% 提到 100%。该距离/覆盖信号不能替代 Exact StepAcc GO，但应作为后续“定位距离或 abstention-aware 风险”假设的候选证据。

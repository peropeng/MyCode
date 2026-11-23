# Gate0 资格报告

## 顶层裁决

- 原题 / strict named-function localization：`STOP_FUNCTION_GOLD_26_LT_30`。
- 若第一章改为 file + code-region（有效代码 hunk/line-range）：`CONDITIONAL_ASSET_BLOCKED`，原因是 6 条 strict asset join 缺失，且非空 `FAIL_TO_PASS` 为 0/44。

## 判定表

| 硬门或审计项 | 结果 |
|---|---|
| 冻结 50 主 tag 且 registry 存在 | 通过，50/50；registry 总计 85，额外 35 排除 |
| 主表 50 行与 tag/reference 严格连接 | 通过，50/50 |
| patch/test exact metadata linkage | 44/50；6 个主任务无唯一官方记录，不能猜配 |
| exact instance/repo/base/setup identity | 44/44；repo 原始字符串相等 0/44，但归一化后 44/44 |
| `test_patch` 非空 | 43/44 匹配记录 |
| `FAIL_TO_PASS` 非空 | 0/44；严格可执行资产 0/50 |
| 官方 developer patch file Gold | 43/50；来源是 `agent_issue.json` 的 `patch` 字段 |
| 稳定 file Gold ≥40/50 | 通过，43/50（patch-only 候选口径） |
| strict named-function Gold ≥30/50 | 不通过，26/50；原题 STOP |
| reframed code-region Gold ≥30/50 | 通过候选计数，32/50；不等同 named function |
| 结构去重 split | 当前粗粒度 2 components；file 42 held-out / 1 train，region 31 held-out / 1 train；虽 cross-split 均 0，但 train<20，split 不可行 |
| strict eligible held-out ≥20 | 不通过，strict eligible=0，无可冻结 strict split |
| 10% relative + paired bootstrap | 只能记录候选 n=42/31；connected-component split 不可行，状态 `STOP_NO_FEASIBLE_CONNECTED_COMPONENT_SPLIT`，无模型 outcomes |
| wrapper 合同 | dry-run/tests 通过；3 条计划命令：1 pull + fresh `test_buggy`/`test_fixed`；无 entrypoint override |

## 解释与最小后续证据

不能把 6 个缺失任务从论文主集静默删掉，也不能用旧集合近似编号补齐。若 file + code-region 改题继续推进，Gate1 前对这 6 个 `unavailable_in_official_checkout` 身份各取最小单 tag 证据：唯一 buggy/base commit、developer patch changed-file metadata、非空失败触发 test metadata、image tag 和可复核 linkage；image execution may resolve 只是待验证可能性，不是当前事实，仍不得在 Gate0 伪造或批量下载。

功效审计没有把“≥20 个 group”当作效果已可检验。当前粗粒度 split 的 train 仅 1 条，不能形成预注册的 train/held-out 双侧 split，状态为 `STOP_NO_FEASIBLE_CONNECTED_COMPONENT_SPLIT`。补足可行 split 后，n=42 / 31 的参考最小 discordant gain 为 4；10% relative 的最小整数 gain 还取决于 baseline 原始成功数。Gate0 未运行 baseline 或方法，因此不报告相对提升或 CI 通过。

证据文件：`results/asset_census.json`、`results/gold_census.json`、`results/independence_power.json`、`results/privacy_audit.json`。本 Gate 未执行 Docker pull/run/rmi、官方破坏性 runner、模型/API 调用或上传。

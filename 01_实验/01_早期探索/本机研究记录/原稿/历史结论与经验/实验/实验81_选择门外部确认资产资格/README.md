# Exp81：选择门外部确认资产资格

## 结论（只针对 Exp80 外部确认资产）

两个官方资产都不能直接承接 Exp80 的 safe/unsafe 配对指标，裁决均为
`ASSET_INCOMPATIBLE_CURRENT_METRIC`。这不是 Exp80 方法 NO-GO，也不是因为下载失败：
在只下载 7,840,851 字节的受限审计中，已经能从真实文件字段确认缺口，因此没有继续下载
大文件、没有运行 Base/A/C、没有调用 LLM/API 方法。

绝对理由只有一个：Exp80 的主指标必须在同一任务组中比较“完整成功执行”和“带决定性步骤的完整失败执行”。这两个公开发布物都只发布注入错误后的失败轨迹；其中失败前的成功前缀不是一条完成的 safe execution，不能把它改标成 safe，否则会把评价对象从“完整运行结果”偷换成“人工截取前缀”。因此两者严格可确认的 safe 组都是 0，严格确认组都是 0。注意，这不等于“没有失败证据”：TraceElephant 有 174 个 failure-only 决定步骤任务组，Who&When Pro 的受限样本有 218 个 failure-only 任务组；只是当前 safe/unsafe 配对指标不能使用它们。

| 资产 | 固定版本与真实计数 | safe 完整执行 | failure 执行 | 决定性步骤 Gold | 严格确认组 | 裁决 |
|---|---|---:|---:|---:|---:|---|
| TraceElephant | HF `a78a57cd…`；ZIP 596,610,649 B；220 个 failure trace unit；174 个唯一 `task_id` failure groups | 0 | 220 | 220/220 `mistake_step`；按 `task_id` 计 174 个 failure-only decisive-step groups | 0 | `ASSET_INCOMPATIBLE_CURRENT_METRIC` |
| Who&When Pro | HF `0bd196c8…`；四 split 共 10,784 行；完整 task group 未全量枚举 | 0 | 10,784 | 受限真实样本 288 行中 288/288 的 `ground_truth.step` 可解析；218 个 sample groups | 0 | `ASSET_INCOMPATIBLE_CURRENT_METRIC` |

这里的 failure 不是从论文摘要倒推：TraceElephant 的 ZIP 中实际解析了 220 个 `trace_metadata.json`，220 个均有 `mistake_step`；Who&When Pro 用 datasets-server 的真实行（text 首行、中部、末行以及分散 range 样本）解析到 `ground_truth` 和有序 `trajectory`。数据卡的“注入一个错误”只是对字段证据的来源说明，不是替代字段的唯一证据。

## TraceElephant

官方代码仓库固定在 GitHub commit `0ce8abb2855de9f454f27f6b0795a4b7e6c8d5fc`，数据固定在 HuggingFace revision `a78a57cdcdf74a080b1bec0f56f85228d86acbac`，数据许可为 CC-BY-4.0。

只读取了 `data.zip` 的 ZIP central directory 和少量 member range：

- `data.zip` 原始大小 `596,610,649` 字节，超过 50 MiB 上限；没有下载全包；
- central directory 证明共有 2,827 个 ZIP entry，其中 220 个 `step_records.json`、220 个 `trace_metadata.json`、2,070 个 PNG；
- 220 个 metadata 的 `mistake_step` 均存在，唯一 `task_id` 为 174；
- 一个真实 `step_records.json` member 证明轨迹是有序前缀，含 input/output/message/tool-call 证据，可做结构特征适配；但它没有完整 safe outcome；
- 数据许可允许离线研究和派生审计结果（需按 CC-BY-4.0 署名），不需要付费模型或私有凭证来做本门。

因此 TraceElephant 的 failure-only decisive-step groups 不是 0，适合做“失败归因/决定步定位”的外部数据参考，不能直接做 Exp80 的 safe-vs-unsafe 选择门确认。继续下载 569 MiB 左右的完整包也不会补出缺失的 safe 行，所以在此资产入口停止是资产结论，不是算法停止。

## Who&When Pro

官方代码仓库固定在 GitHub commit `14369dcb079c7cdf86ed2924145d5a28ff5c73b2`，数据固定在 HuggingFace revision `0bd196c8a040841c4ae167ab33cc8151de246f1f`，数据许可为 CC-BY-4.0。数据文件树和大小如下：

下面的 10,784 是该 pinned HuggingFace revision 的 datasets-server 实际行数；不继承项目页面或论文摘要中可能出现的其他总数。

| 文件 | 行数 | 原始大小（字节） |
|---|---:|---:|
| `data/text.jsonl` | 6,257 | 75,566,568 |
| `data/image.jsonl` | 3,107 | 6,792,962,340 |
| `data/image_gui.jsonl` | 504 | 11,188,209,213 |
| `data/video.jsonl` | 916 | 21,347,304 |
| 合计 | 10,784 | 18,078,085,425 |

审计读取了 text 的真实行和小 range；没有下载 image/image_gui 媒体。text 真实行的 schema 是 `id, framework, benchmark, task, trajectory, ground_truth, extras`；样例中 `trajectory` 是按 `step_number` 排序的事件列表，`ground_truth` 直接含 `step` 和 `mode`。分散样本 288 行中，288/288 有 `ground_truth`，0/288 有显式 safe/success 字段；其余 split 的行数和字段类型由官方 datasets-server schema/size 响应锁定。四个 split 的发布契约都是错误注入轨迹，不提供完整成功运行作为配对对照。

受限样本的 288 行中有 218 个按规范归一化 task 的 sample groups，且都有可解析的 failure `ground_truth.step`；由于没有枚举全部 10,784 行，完整 `decisive_step_unsafe_groups` 必须记为 unknown/null，不能误写成 0。它可以做 failure-only 失败步骤定位或错误类型分析，但不能给 Exp80 提供 50 个 safe 组和 50 个 decisive-step unsafe 组。只下载 text 的 75.6 MB 也不会解决这个语义缺口，故不把它标成 `PARTIAL_ASSET_PILOT`；也不把它标成 `ASSET_BLOCKED`，因为元数据和真实样例已经足够判定当前指标不相容。

## 18 维输入的边界

两项资产都能提供有序 prefix 的一部分结构信号（activity、内容/动作/思考存在性、调用/角色/重复/结构变化等可通过适配器派生），但：

- `base_score, a_score, score_margin, base_alarm, a_alarm` 不是数据字段，必须由 Exp80 的方法运行后产生；
- `recovery_evidence` 需要完整成功/恢复结果，两项资产的发布记录都没有；
- TraceElephant 使用 message/input/output/tool-call schema，Who&When Pro 的不同 framework 使用不同事件 schema，需先冻结透明 adapter；
- 即使所有 18 维都能适配，也不能在没有 safe 完整执行的情况下定义 Exp80 的 paired Exact-F1。

因此本实验不会偷偷把“schema 能解析”写成“外部确认可运行”。

## 可复现与文件

```bash
python3 audit_assets.py --output-dir .
python3 -m unittest discover -s tests -v
python3 -m json.tool protocol.json >/dev/null
python3 -m json.tool census.json >/dev/null
python3 -m json.tool source_manifest.json >/dev/null
python3 -m py_compile audit_assets.py
git diff --check
```

`source_manifest.json` 记录精确 URL、revision/commit、ETag、HTTP range、响应字节数、SHA-256 和 UTC 时间；`census.json` 记录字段级计数和裁决。原始 range/API 响应只写入被 `.gitignore` 忽略的 `runtime/`，不提交到仓库。成功审计运行的总下载量为 `7,840,851` 字节，低于 `52,428,800` 字节硬上限。

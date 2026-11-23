# Exp77：AFTraj 成功参照迁移资产资格门

本实验只判断 AFTraj 是否有足够的、可独立配对的成功参照资产，供后续把 E29 的成功参照机制迁移到外部数据。它不是 Base/A 方法实验，也不是方法失败结论。

## 结论

结论为 STOP_ASSET。clean non-test 数据共有 1,817 条轨迹（safe 910、unsafe 907），1,164 个 task group。只有 2 个 group 同时拥有至少 2 个不同 safe conv_id 和至少 2 个不同完整 trace hash；这 2 个 group 都没有 unsafe 轨迹。因此严格资格定义下 qualified group 为 0，safe reference-query pair 与 unsafe reference-query pair 均为 0。

所有门的实际值都已写入 [census_result.json](census_result.json)；失败门包括：

- qualified task groups：0 / 60；
- qualified domain groups：0 / 3（每域至少 10 组也不满足）；
- diagnosed query groups：0 / 30；
- injected query groups：0 / 30；
- independent safe/unsafe queries：0 / 120；
- confirmation groups：0 / 24，且两类 source 均不存在。

因此本实验不运行 Base/A，不降低阈值，不更改 pairing，不输出 dev/confirmation 组清单，也不宣称方法失败。若未来资产或冻结 seal 改变，应重新注册并重新 census。

## 冻结规则与证据

- protocol 先于 census 冻结，见 [protocol.json](protocol.json)。
- 只读 /Users/peroyang/My/MyWork/worktrees/0822-aftraj-asset/third_party/data/AFTraj 的 parquet。
- 复用 Exp75/Exp76 的官方 test ID/group seal 与 Exp73 canary seal。官方 test 正文/标签不从 parquet 投影；只读取 split ID、seal 元数据和 task-group hash。
- clean 行在 parquet scanner 中先按官方 test ID 过滤，再按官方 test task group 过滤；canary 仍显式排除。
- task group 为规范化 task description 的 sha1(normalized task)[:16]。资格要求同组至少 2 个不同 safe conv_id、至少 2 个不同完整 trace hash、至少 1 个独立 unsafe trajectory，并且存在一个 safe reference 能与 safe query 和 unsafe query 都以不同完整 trace hash 配对；禁止自参照。
- 完整 trace hash 覆盖 tools 与全部 turns。另计算 NFKC、大小写/空白归一化后的可见 turns hash，用于重复/近重复审计。
- [group_manifest.json](group_manifest.json) 每个 clean group 一条记录，只保存 salted/one-way hashes、计数、布尔值和长度分布，不保存 task、conv_id、turn、答案或正文。

## 复现

    python3 census.py --data-dir /Users/peroyang/My/MyWork/worktrees/0822-aftraj-asset/third_party/data/AFTraj --output-dir .
    python3 -m unittest discover -s tests -v
    python3 -m py_compile census.py
    python3 -m json.tool protocol.json >/dev/null
    python3 -m json.tool census_result.json >/dev/null
    python3 -m json.tool group_manifest.json >/dev/null
    git diff --check

本目录没有网络/API、模型、提示词或方法运行；method_run=false、base_or_a_run=false 且 network_calls=0 已在结果中冻结。

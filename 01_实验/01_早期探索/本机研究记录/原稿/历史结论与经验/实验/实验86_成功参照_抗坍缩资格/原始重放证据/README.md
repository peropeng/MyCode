# Exp86 原始重放证据

本目录保存 Exp86 所引用的历史 E29 原始重放配置和结果 JSON，两个文件均从清理前的 `/Users/peroyang/My/MyWork/tmp/exp86-e29-evidence/` 按字节复制，未改写内容：

- [`e29-replay-config.json`](e29-replay-config.json)：SHA-256 `e3c2e307a0ee3fb5022c26e6546f77d95f5ac5c3ab256350e9ab61e3548bf71e`。
- [`e29-replay-results.json`](e29-replay-results.json)：SHA-256 `da2bd11786aaba9566a4ef0ed8ded76b3ac29eae6fdd026871f9ed52802f4c2f`。

保留这两个 JSON 是为了让历史重放的冻结配置、原始指标、比较项和判定字段在仓库内有最小可审计原件；`historical_replay_summary.json` 和 `results.json` 仍是 Exp86 的正式摘要/结果入口。本次归档不修改任何冻结结果、协议或 data seal。

两份 Parquet 没有复制进 Git。它们是可从 [`data_seal.json`](../data_seal.json) 中记录的不可变 Hugging Face revision 重新取得的缓存，数据 URL、revision、字节数、SHA-256 和行数已经封存；将约 70 MB 缓存再次提交会扩大仓库而不增加实验结论。需要重放时，应先按 `data_seal.json` 的 URL 和 SHA 准备本地缓存，再依照冻结协议执行。

原始 JSON 内仍可见 `/Users/peroyang/My/MyWork/tmp/exp86-e29-evidence/` 绝对路径。这些路径是当时命令和 provenance 字符串，不是当前归档的运行依赖，也不表示必须恢复根目录 `tmp` 才能读取本目录 JSON。当前 runner 的默认数据路径仍由冻结实验文件记录；本说明只解释历史证据的迁移边界。

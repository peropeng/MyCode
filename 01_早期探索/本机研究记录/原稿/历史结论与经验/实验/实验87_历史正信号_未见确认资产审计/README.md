# Exp87：历史正信号的未见确认资产审计

本实验只审计资产资格，不运行 Exp29、Exp33 或 Exp80 的方法，不调用 API、不联网、不下载数据，也不改变历史结果的 GO/NO-GO 含义。审计脚本读取已经存在的本地 Parquet、split、协议和结果，重新计算原始行、ID 集和 task-group 集，并核对历史 SHA-256。

## 结论先行

三条历史正信号线目前都没有可直接进入“真正未见确认”的 row/group：

| 线 | 本地原始资产 | 原主指标所需对象 | 真正未见 rows | 真正未见 groups | 资产层结论 |
|---|---:|---|---:|---:|---|
| Exp29 成功参照早期预警 | OpenHands SFT 491 行 + Verifier 2636 行 | 同 task 的成功参照 + 失败轨迹 | 0 | 0 | `NO_QUALIFYING_UNSEEN_GROUPS` |
| Exp33 责任主体→步骤 | AFTraj unsafe 1114 行 | 有 `mistake_agent`/`mistake_step` 的失败轨迹 | 0 | 0 | `NO_QUALIFYING_UNSEEN_GROUPS` |
| Exp80 AFTraj 选择门 | AFTraj safe 1162 + unsafe 1114 = 2276 行 | safe/unsafe Gold 与同组配对评估 | 0 | 0 | `NO_QUALIFYING_UNSEEN_GROUPS` |

这三个“0”不是方法 NO-GO，也不计入三次方法失败。它们表示：在当前本地资产和冻结历史边界下，没有同时满足“原始数据存在、Gold 有效、没有打开过、task-group 不重叠、可以支持原主指标”的对象。

## 每条线的绝对理由

### Exp29

实际找到的两个 Parquet 位于旧研究资源目录：

`实验/实验08_RQ1论文指导方法冻结/研究资源/第三方仓库/data/`

脚本按历史 `probe.py` 重新解析，结果与历史 `probe_summary.json` 的 parser、pairing 和 1216 条 matched-row 记录逐条一致：491 条成功参考、2636 条 verifier 行、1266 个 verifier task groups、281 个匹配组、1200 条去重交互。

其中所有“有失败且有 SFT 成功参照”的组都已经在 Exp29 的 281 个匹配组中打开并用于配对/评估。剩余 1420 条 verifier 行、985 个组没有本地 SFT 成功参照（其中 1208 条失败行来自 907 个组），只能支持当前-only/no-reference 类分析，不能支持 Exp29 的 paired-reference 主指标。因此不能把它们改名为新确认集；重复行、去重前的 16 条重复交互也不产生新组。

### Exp33

当前本地有三个字节一致的 AFTraj 副本，四个源文件 SHA-256 相同。按照 Exp33 的实际代码和 `group6-confirm-v1` 协议，unsafe 1114 行被完整划分为：

`163 条官方 test + 40 条与官方 test task-group 重叠而排除 + 911 条历史 pool`。

911 条 pool 又已经分成 `731 条 train + 180 条 confirmation`。因此 1114 条 unsafe 行没有剩余。那 40 条重叠行虽然不是最终训练行，但它们已经被读取以执行去重，而且属于官方 test 的同组，绝不能拿来伪造新确认。Exp33 的原始 E2 是 failure-only 主体到步骤排序，没有成功对象；AFTraj safe 行不能补成新的 `mistake_agent` Gold。

### Exp80

按照 Exp75/78/79/80 的冻结 split 和 whole-group exclusion，AFTraj 全部 2276 行、1381 个组被完整划分为：

`332 条 official test / 217 组 + 1817 条 clean development / 1164 组 + 127 条同 official task-group 的排除行 / 19 组`。

1817 条 clean development 已用于 Exp78/79 的方法选择、OOF 和 Exp80 的最终拟合；332 条 official test 已被 Exp80 打开评估；127 条排除行只要重用就会产生同组泄漏。Exp80 的 strict primary 只是从已打开 official test 中去掉 12 条 canary 组，得到 311 行/205 组，不是新数据。三个 AFTraj 副本的 hashes 也完全一致，不能计成三个外部确认集。

## Gold、泄漏与原主指标边界

- Exp29 的 `resolved`、verifier judgement 和 final judge prompt 是 Gold/未来信息，历史 runner 已做 mask；task description/hash 是配对和分组条件，不是未见资产证明。
- Exp33 的 `mistake_agent` 和 `mistake_step` 是 Gold，`mistake_reason`/`unsafe_source` 是标签或来源字段；它们只能做目标或审计，不能进入特征。
- Exp80 的 `gold_answer`、`mistake_step`、`mistake_agent`、`mistake_reason`、`unsafe_source`、完整未来 turns 和 official test body/label 都不应进入方法输入。脚本只用 schema、ID、task 和 split 做资格审计。

原主指标仍然可以在历史资产上重现或解释：Exp29 是 success-FPR 约束下的 failure alarm recall，Exp33 是 E2 MRR（E1 是其依赖的上游任务），Exp80 是 safe/unsafe Exact-F1。这里的结论只是它们都没有新的、未打开的确认资产。

## 真正缺失的最小资产

- Exp29：一批全新、原始可读的 OpenHands-like success/failure 轨迹；至少预冻结约 30 个独立 task groups，必须同时有独立成功参照、失败轨迹、可见工具状态和证明参照先于当前失败的来源/时间信息。
- Exp33：一批此前未打开的 unsafe Agent 轨迹，至少包含有效 turns、角色/动作/内容、`mistake_agent`、`mistake_step`，并在方法选择前冻结 train/confirmation task-group split。
- Exp80：一批此前未打开的 safe/unsafe Agent 轨迹，包含 safe/unsafe outcome Gold（process-style safe 行允许 `gold_answer` 为空）、unsafe `mistake_step`、原始 turns/tool state、冻结 task-group key 和完整 source hash；不可与 Exp75/78/79/80 的任何 ID/group 重叠。

拿到上述资产后才进入“Base → 单模块 → 未见确认”的可行性漏斗。本实验本身不建议继续重切当前数据，也不建议因此停止任何历史正信号方法。

## 复核命令

```bash
python3 '实验/实验87_历史正信号_未见确认资产审计/audit_assets.py'
python3 -m unittest discover -s '实验/实验87_历史正信号_未见确认资产审计/tests' -p 'test_*.py'
```

生成的 `asset_manifest.json` 保存每条线的 source hash、原始 split、ID/group digest、Gold/泄漏字段、打开状态、绝对停止理由和最小缺失资产。它不保存原始轨迹正文，也不会写入源数据目录。

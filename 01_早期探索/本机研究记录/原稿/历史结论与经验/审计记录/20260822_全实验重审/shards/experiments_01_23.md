# 实验 01–23 证据审计分片

审计范围是 实验/实验01_* 至 实验/实验23_* 的全部实际存在目录。证据顺序为 raw JSON/结构化结果与可执行记录 > 本地冻结配置/协议 > 实际 runner/core code > 单元测试与运行日志 > 结论 Markdown。文件名中的 GO、NO-GO、STOP 没有被继承为分类依据。相同数据上的方向1/方向2、file/hunk、dev/posthoc 只计一份证据。

## 分类计数

| 主分类 | 数量 | 实验 |
|---|---:|---|
| PAPER_BASELINE_FAILED | 1 | E07 |
| ASSET_STOP | 9 | E03、E05、E13、E17、E19、E20、E21、E22、E23 |
| HARNESS_INVALID | 1 | E11 |
| MODULE_NOT_VALIDATED | 1 | E08 |
| STORY_MISMATCH | 8 | E01、E02、E04、E06、E09、E14、E16、E18 |
| MULTI_CAUSE_FAILURE | 2 | E12、E15 |
| TRUE_METHOD_NO_GO | 1 | E10 |
| PAPER_REPRO_BLOCKED | 0 | — |
| COMBINATION_NO_GAIN | 0（作为主分类） | 组合负结果作为 E10/E14 次分类 |

本分片 23 行 JSONL 均包含固定字段；详见 experiments_01_23.jsonl。本分片只有 1 次“实质方法失败”计数，来自 E10；其余是资产、评价对象、论文复现、Harness 或待确认方向性结果。

## 最强正信号（不等于论文 GO）

1. E02 是最可信的受控机制信号：34 个任务、8 个仓库、同 3-probe 预算，checkpoint binary Top-1=1.0，uniform=0.470588，差值 0.529412，任务级 paired bootstrap 95% CI [0.352941, 0.705882]，34/34 干预恢复闭环。协议明确只支持受控 checkpoint localization，不支持自然 Agent 过程归因，因此主类为 STORY_MISMATCH。
2. E18 是当前最值得做新任务确认的动作效果契约：13 个已资格化 pair、5 个仓库，action-effect recall=1.0，periodic=0.538462，开发集 paired CI [0.230769, 0.692308]；A/B 有效、C=3 个任务无增益。formal_go_count=0，同 dev 的 posthoc robustness 不计独立确认。
3. E16 的 6-task pilot 方向更强但成本公平性仍需审计：grounded sandbox fault completion=6/6，periodic=2/6，clean unnecessary=0；只有 6 tasks、没有 CI，grounded 是 deterministic contract 而 ungrounded full 使用 18 API calls，必须在新任务、统一预算中确认。
4. E12 方向1有小幅、可定位信号：role-anonymous nDCG=0.905589，most_content=0.884448，差值 0.021141、CI [0.005087,0.035855]，但相对增益仅 2.39%，方向2共享同一 277 records 且近零，不可累计为两个正结果。适合单一条件门控/分组模型确认。
5. E01 的 20/20 applicability 与 replay consistency 是很好的基础设施/数据合同结果，不是方法正结果。

## 唯一可信方法 NO-GO 候选

E10 full action ranking 在 71 file-level records、64 task clusters 上，相对同任务成功参考文件 baseline：

- full MRR 0.668619 vs same_task_file 0.830282；
- 差值 -0.161663，相对 -19.47%；
- paired CI [-0.271911,-0.071512]；
- Recall@3 也为负；
- 同一批 action/hunk 事后分析不计第二个独立失败。

输入中 Gold patch 仅作评价标签，当前失败行不作参考；因而按当前协议暂记 TRUE_METHOD_NO_GO，计数 1。但 bridge 单测无法加载缺失的 gate_a，且 same-task baseline 很强，可能含任务条件先验。当天的最小动作不是加模块，而是修复仅用于复跑审计的 import，并在新任务确认该 baseline 是否存在身份捷径。

E04、E09、E14 的负差不能计 TRUE_METHOD_NO_GO：三者结果均有 raw paired negative/无增益，但主要标签是 endpoint verifier success/failure，不是 process-fault onset 或责任 Gold；E04 还存在 visible source/log keyword、view/edit matching 等数据合同问题。E03/E15 的样本/资格门不足，也不计方法失败。

## 资产 STOP

- E03：请求 15/执行 9；A=5、B=4、C=0；RQ1 CI 下界为 0，RQ2 adaptive 与 predicted uniform 并列；C native/mutant preflight 不足。
- E05：base/results.json 报 1/8、results_round2.json 报 5/8、a580f43/results.json 报 0，存在必须解决的 provenance/分支冲突；没有 formal phase1。
- E13：58 runtime candidates，但 clean replay tasks/repos 都为 0，缺依赖/命令/可执行环境。
- E17：冻结 qualification 因 -nauto addopts 与 moto freezegun 缺失被拒；posthoc 修依赖不能算正式资格。
- E19–E21：natural task focused verifier 从起点即失败；E19 无 clean baseline，E20 parquet/validator/source repo 外部资产缺失，E21 有 commitment parse 但没有 tracked edit/post-validation。
- E22：inventory 44 traces 有价值，但 10-task replay exact=7/10，目标路径不存在/py_compile 失败，未达到 exact>=8 gate。
- E23：44 traces、10/10 repo coverage，但 sealed trigger coverage 0.735294 < 0.8，Phase1/API 未启动。

上述 STOP 都不计方法 NO-GO。最小修复均是资产/路径/资格重建，再按 Base→单模块顺序运行。

## Harness / 协议问题

单测 fallback 命令使用 Python unittest，因为环境没有 pytest（python3 -m pytest ... 直接报 No module named pytest）。已运行的 unittest 结果详见 coverage：

- E01、E02、E03 两分支、E04、E05 两分支、E06、E07 两分支、E08 E017、E11、E12 direction2、E13 两分支、E14、E15、E17、E18、E19、E21、E22、E23 的本地单测大多通过。
- E08 64c0800：48 tests 中 1 个因外部 trace_metadata.json 缺失错误。
- E09：历史 成功参照实验/早期预警/run_experiment.py 缺失，导入即失败。
- E10：gate_a 缺失，bridge 导入即失败。
- E12 direction1：normalize_public_labels 缺失导致 2 个测试错误。
- E16：runner 引用不存在的 31_RQ1动作效果验证与恢复可行性实验 路径，2 个测试导入错误。
- E20：外部 swebench_verified.parquet 缺失，2 个测试错误。
- 这些错误不直接改变已有 raw 结果，但阻止独立复跑，必须在确认实验前修复或明确资产边界。

## 需要主线程冲突复核

1. E05 的 1/8、5/8、0/8 qualified_count 必须按 manifest、commit、命令日志逐项核对；不能直接采用历史结论。
2. E07 的官方仓库可部分运行，但 official_get_lang_lang returncode=1 且 languatory.json 缺失；本分片按 PAPER_BASELINE_FAILED，若主线程认定关键官方资产不完整，可改为 PAPER_REPRO_BLOCKED，但不能把它当已验证模块。
3. E10 的 same-task_file baseline 是公平但很强的条件先验；建议在新任务确认，确认后再决定是否把负结果固定为可靠方法失败。
4. E04/E09/E14 的 endpoint labels 与过程 fault 研究对象不一致，不能被平均指标的 NO-GO 名称覆盖。
5. E16/E18 的 pilot/dev 正信号必须使用新任务 confirmation；同 dev posthoc、API deterministic contract 与 ungrounded API cost 不得混为正式提升。

## 推荐继续顺序（供主线程合并排序）

1. 先修 E05/E17/E22/E23 的资产资格，优先让一个统一真实环境达到冻结门。
2. 在可用的受控资产上做 E18 新任务确认；若确认，再做 E16 四条件统一预算复跑。
3. E02 作为可信强 Base/controlled benchmark，补新种子而不是扩张故事。
4. E12 仅做一个预冻结条件门控确认，不把 direction1/direction2 组合。
5. E10 只做复跑审计和新任务 baseline 检验；不要用第三模块抢救。


# Exp130 V9 完整 AB15 独立终审

审阅日期：2026-10-03。对象为执行工作区 `1003-exp130-ours-diagnosis/实验/实验130_语义多关系诊断改进` 的 V9；本文件仅记录只读终审，不修改科学协议、模型、训练产物或前序审阅。

## 结论

**流程、产物绑定、已执行结果与报告一致性：PASS。V9 预声明强门：FAIL，目标未建立。** 三个固定种子的 fixed120 正确数为 **56 / 50 / 47**，四项原强门均为 false。完整执行的是 AB 的 3×5＝15 折；其余五个条件共 75 折为 `NOT_EXECUTED_BY_PREDECLARED_GATE`，机制合取门为 **NOT_EVALUATED**。不能把未运行的条件记为失败、零效果或消融证据，也不能据此认定 A/B 单独有效或无效。

本轮可进入 V9 最终封存。审阅时 `completion.json` 和 `delivery_manifest.json` 尚未发布；以下是实际产物与封存代码的预封存核查通过，最终 manifest 发布后的逐项 SHA 检查由主线程另行完成。本结论不批准 V10 采用、冻结或训练。

## 实际 15 折与统计证据

独立读取全部 15 个结果、15 个 held-evaluation 前冻结记录及 15 个 checkpoint 文件，校验 **45 个必需训练产物** 的成员关系、路径及 SHA；没有反序列化 checkpoint 或运行模型。科学绑定中的 15 个源文件均与当前字节一致，全部结果和冻结记录使用同一绑定。重新按冻结的排序、随机种子和步进切分规则构造 716 个 task group 的外层五折，训练／验证／held 分组均对应原协议。每折 held group 数为 144、143、143、143、143；重复记录仍作为同一个 task group 处理。

内层选择符合固定验证折、严格首次最大 Top-1、patience＝15；选轮后从新初始化在其余四个外折重训对应轮数。全部 refit 长度一致。代码中的 checkpoint→冻结记录→held evaluation 顺序已在训练入口审阅；当前全部文件的保存时间次序也与之相符，文件时间仅作补充证据。

| 固定种子 | outer 0–4 选定 epoch | 内层实际轮数 | fixed120 正确数 | 全量 task-group Top-1 | 全量 task-group MRR |
| --- | --- | --- | ---: | ---: | ---: |
| 20260816 | 6, 3, 6, 5, 3 | 21, 18, 21, 20, 18 | 56 | 0.557262569832 | 0.714056407523 |
| 20260817 | 7, 10, 5, 17, 4 | 22, 25, 20, 32, 19 | 50 | 0.548184357542 | 0.705614519382 |
| 20260818 | 4, 15, 8, 8, 8 | 19, 30, 23, 23, 23 | 47 | 0.553770949721 | 0.711615400034 |

逐一重建 3×731＝2193 条 OOF 记录的完整排序、预测、Gold 排名、Top-1、reciprocal rank、R@3、signed error 和角色正确性，核对公开元数据与已封存合法 task-row Gold；未新读标签源或执行基线。每个种子覆盖全部 731 条记录且无重复／漏项，分数有限且本批实际没有分数完全相等的记录。全量指标按 716 个 task group 等权计算；对应原始记录正确数 400 / 394 / 398，不能用记录正确率替换表中的 group 指标。

独立重算三个种子的全部 12 个 fixed120 配对比较，包括五层各 24 条的固定分层、bootstrap seed＝20261002、10000 次重采样、95% 和 98.75% 区间及 wins/losses/ties，与发布统计一致。主种子相对四个缓存基线的结果如下；区间与差值单位均为百分点。

| 基线 | 基线正确数 | AB−基线 | 98.75% 配对区间 | wins / losses / ties |
| --- | ---: | ---: | --- | --- |
| All-at-once | 77 | −17.5000 | [−31.6667, −2.5000] | 16 / 37 / 67 |
| Binary Search | 51 | +4.1667 | [−10.0000, +17.921875] | 25 / 20 / 75 |
| SDBL | 69 | −10.8333 | [−25.0000, +3.3333] | 18 / 31 / 71 |
| cached StepFinder | 71 | −12.5000 | [−25.0000, 0.0000] | 14 / 29 / 77 |

因此 `primary120_above77`、`all4_adjusted_lower_positive`、`all3seed120_above77`、`all3full_no_cached_StepFinder_regression` 均为 false，与 `stage1_decision.json` 完全一致。三种子全量 Top-1 相对 cached StepFinder 的差值分别为 −0.201117318436、−0.219622905028、−0.201815642458。

主线程另有完整 OOF 独立重建凭据 `v9_oof_independent_check.json`；本审阅核对其方法、PASS 结果及全部 86 个绑定来源的当前 SHA。其覆盖全量 cached StepFinder 配对区间、分层与 canonical tie 重建；本审阅自己的重算覆盖上面的全部实际 OOF 指标和 fixed120 区间，未重复执行该凭据的整套计算。

held 行为汇总的节点／记录权重也独立核对一致。gate 均值约 0.5401 / 0.5422 / 0.5390，slot effective rank 约 1.9525 / 1.7748 / 1.6954；A/B centered RMS 小于 base 的现象可以描述，但不是 A/B 因果贡献的估计。`B_nonzero_suffix_fraction=1` 也不能证明有效责任信号。15 折耗时之和 9536.124 秒，调度墙钟 5996.297 秒，与两 seed 并发及报告口径一致。

其余五个条件的结果、checkpoint、freeze 和 evaluation 目录均不存在；机制合取产物不存在，scheduler lock 已不存在。调度完成记录为 `COMPLETE_AB15_TARGET_NOT_ESTABLISHED`，保留 attempt001，不存在以新种子或重试替换本轮结果的证据。

## 方法、输入与报告边界

已完成且仍由 SHA 绑定的 CPU 实现、资源、数据与论文原文审阅沿用，不重复运行。当前归因 core 与最初失败数值夹具时相同；CPU `attempt_001` 的失败报告、零边界诊断与源码快照仍保留。后续 `attempt_002` 的 13 项通过对应已审阅的 real-MLP 浮点数值契约修正，不是掩码、阈值化或 core 改写；不能改称最初严格 byte-zero 检查通过。

正式报告保留五篇固定论文 Who&When、StepFinder、TraceElephant、Graphectory、AEGIS 的具体作用与证据边界。终审发现补充近邻的文字未覆盖原八篇中的 CHIEF、DCFA、GraphTracer；作者已补充这三篇的原文链接／章节及 Gold outcome、oracle 纠正与环境重执行边界，同时字节保留训练前八篇审阅。最新报告相对前一版只有该出版补充，没有统计、协议或科学源文件改变。八篇快照中的“待实现／未验证”明确标注为训练前历史状态，不能替代当前实现和结果。已有门控、替换、保留乘积、删除与后缀重放等近邻不支持泛称首创；latent 账本不等价于真实任务因果责任。

输入几何原审阅与原始审计快照保持原字节。新输入的 trace 内平均 cosine 增高、中心化能量下降可作为描述；对单位向量，`E=(n−1)/n·(1−mean_pair_cosine)`，这两项不是独立证据。输入中心化 effective rank 与训练后 slot rank 不同，也不能凭输入余弦把性能下降归因为任务文本。模板、任务、原始角色、精度与后端等因素混杂，learned projection 可以重新缩放差异；本次没有相应因果消融。原 StepFinder 缓存与新输入包存在差异；All-at-once、Binary Search、SDBL 原已消费公开任务／角色信息，报告没有把所有基线一概写成“没有任务信息”。

最新正式报告正确保留：强门失败、75 折按门未执行、机制未评估、仅复用开发集证据、零本版 API 调用且未执行基线，以及输入几何仅作观察。不存在把 Binary Search 的 +9.8039% 相对点估计写成显著提升、把历史版本数字写成 V9 结果，或把新候选版本写成已获批准的表述。

## 预封存与版本保留

审阅 `v9/seal.py` 的递归成员范围：科学源文件、正式报告、全部 V9 源码与 `results/v9` 文件均纳入，排除 `.pyc`／`__pycache__`。实际预枚举包含全部上述 45 个训练产物。封存入口会复制本终审、encoder 原始日志与 scheduler 原始日志，再写 completion，最后枚举发布 manifest；两份原始日志目前存在。由于最终复制与 completion 尚未发生，此处不把预枚举数量当成最终 manifest 数量。

本轮额外核对最新／历史报告及 reporter 与各自回执一致，`publication_history_v2` 保留旧报告 SHA `20c8c5bc…d051b4e`；原 CPU 失败报告及诊断、成功夹具四个发布文件均与原已审 SHA 一致。八篇近邻、输入几何、主线程 OOF 重建与其 Windows 路径分隔符修复前源码／修复说明快照均与原件字节相同。路径修复属于独立读取器，未修改科学训练或评价程序。

## 关键 SHA-256

| 证据 | SHA-256 |
| --- | --- |
| `results/v9/pre_training_binding.json` | `f0ee57d08204b451a888ba40673246fedd044f1da3aee89b0fca74abc2e28c5c` |
| `v9/scientific_protocol.json` | `e8eba55cc9c02248f76bfc25057659299012d61d316591d038ab87dd28a0e1aa` |
| `results/v9/evaluation/AB/summary.json` | `c6e7e46a533a054dad55efece9372333fc1c725f01a34bde0008ec0d249d54cf` |
| `results/v9/stage1_decision.json` | `afd6bc326844bff610a0544d139f6997bacd3bbbaa363c5507b8845964959cbe` |
| `results/v9/stage1_validation.json` | `5fb9d70135486829910971ed67c4d5d2832fe978f66fd23a7d2bceb720e2cfc2` |
| `results/v9/execution_scheduler_v1/completion.json` | `dd00da5c054528e148f51404ee1021ff87896ba3ea17c288ac8a145b988f9642` |
| `实验报告_v9.md` | `9dd8c092e2547cf04bd1c5d4c93097317f837755a21e8a9857b9b0bdea8d04c7` |
| `v9/report.py` | `e6d46a509d2f408be28794ecd7234a4f0b87329022a4972662f96bf2cb481fb4` |
| `v9/seal.py` | `d3e7e145248a1f43006b1e13bfa1cef3a05462dea332cbf490d698b52ac8fa21` |
| `independent_checks/v9_oof_independent_check.json` | `16c396328f256d8ae2ea14393acb0178f8279e6f542e8836141a47af69ab5476` |
| `independent_checks/v9_near_neighbor_audit.json` | `c8ca705b384609f08338611cb497f59b7a11a09f9547057888a507f2dd051a7c` |
| `independent_checks/v9_input_geometry_review.md` | `a4e861cb9d535c50a43832a040fdeaa9691ce4e2b1e92dad5df63d92aadd25e2` |

审阅执行范围仅为源码／文档阅读、文件哈希和既有结果的独立算术重建；未运行模型、训练、编码器、测试、基线或外部 API，未改动执行工作区。当前没有阻止 V9 如实封存的未解决问题。

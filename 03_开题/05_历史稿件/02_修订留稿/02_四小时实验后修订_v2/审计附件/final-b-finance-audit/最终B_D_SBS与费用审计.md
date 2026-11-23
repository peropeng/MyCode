# 最终B、D、SBS及费用关闭：只读独立审计

2026年10月12日，依据四小时权威交付目录及其直接引用的保存证据核对。本次只读取文件、重算SHA-256、解析既有源码AST、统计JSON和进行Decimal算术；没有运行产品测试、原生恢复、模型/API、查询新余额、读取Gold标签、修改账本、产生新候选或重发请求。所有审计输出均在本目录。

**结论：所要求的核心事实全部得到保存证据支持，没有发现需改写的科学结果或费用差额。B仍没有完整共同自然终态，D没有新增合格整体基线，SBS完成流程但未产生责任步骤。27条新请求全部结算，费用上界0.45924094元；旧4842号未知请求及0.533734元完整预留原样保留。**

## 1. 核验范围与证据完整性

已读取 `FOUR_HOUR_FINDINGS.md`、`PAIRED_RECOVERY_MATRIX.json`、`THIRD_BASELINE_QUALIFICATION.json`、`SBS_ACTUAL_PREFIX_AUDIT.json`、`FINANCE_AND_RESUME_RECEIPT.json`、`ROOT_WINDOW_CLOSED_ACTUAL.json` 和 `DELIVERY_MANIFEST.json`。另对交付manifest登记文件及其JSON中的直接path/SHA引用核验字节，不重新评价标签或运行任务。

- 本次检查202个直接path/SHA引用位置，涉及142个不同文件，缺失与哈希不符均为0。计数范围包含manifest自身的登记引用及关闭补充文件，故不应与原manifest报告的188个引用强行视为相同统计口径。
- 既有三候选的源码快照、请求和响应文件SHA逐一相符；实际请求canonical body SHA也与所声明记录相符。
- 连续账本在本次审计前后SHA均为 `7028a495741bcab6843a560dd2214743a88ccaff994dec8996f46ccaa069a154`。
- 本次没有做实时进程探测；“已关闭”依据已保存的实际父进程STOP、Job为空和子孙进程停止回执，而非本次新启动或停止任何进程。

原始核验结果见 [audit_results.json](D:/Code/毕设/graduate-thesis-experiments/工作区/1012-astra-v2/final-b-finance-audit/audit_results.json)，逐引用结果见 [direct_reference_checks.json](D:/Code/毕设/graduate-thesis-experiments/工作区/1012-astra-v2/final-b-finance-audit/direct_reference_checks.json)。

## 2. B：18计划槽、5条付费轨迹、6次POST、0完整共同自然终态组

矩阵键集恰为2题×3条件×3重复，共18槽，无重复键或缺槽。两题为moto5134与moto5286；条件为SOURCE3、SF_ALG50、NO_DIAG。

| 任务/重复 | SOURCE3 | SF_ALG50 | NO_DIAG |
|---|---|---|---|
| moto5134 / trial1 | 1次已结算生成；后续资金删失，保留原工程未知 | 1次已结算生成；后续因旧进程不存在性检查删失 | 资金边界，未POST |
| moto5134 / trial2 | 1次已结算生成，已有候选，原生接口未知 | 2次已结算生成，第二次已有候选，原生接口未知 | 1次已结算生成，已有候选，原生接口未知 |
| moto5134 / trial3 | 未运行，原生工程资格未闭合 | 未运行，原生工程资格未闭合 | 未运行，原生工程资格未闭合 |
| moto5286 / 三次重复 | 三槽均未运行，完整首请求峰值受当时资金边界阻断 | 同左 | 同左 |

由矩阵逐行及连续账本分别重算，5个不同付费flow、6个POST，费用合计0.21202918元，互相一致。18槽的公开目标G、普通保护O、独立终验字段全部为null；完整三条件共同自然终态组为0。矩阵保存的可信业务原生测试调用计数合计0，但存在验证worker及接口的实际尝试和工程错误，不能把这个数字扩大成“完全没有尝试启动本地验证”。

5个启动且付费的槽位在各自固定30分钟内都没有交付已验证成功，相应交付字段均为false；13个未启动槽的交付值保持null。旧版本使用 `fixed_budget_verified_success`，trial2补充使用 `fixed_30min_verified_delivery_success`，本审计已按相同端点归一。部分旧 `fixed_budget_outcome` 文本仍保留工程删失原值，不能只读取该旧字段而忽略新端点字段。

**论文边界：** 可以报告固定预算下已启动的五条轨迹没有已验证交付，并描述具体工程/资金原因；不能填成“18次算法全部失败”，不能进行三个条件的恢复率排序，也不能把C的8次独立验收或历史Agentless/EnAgent结果补到B的空位。已出现的JSON解析或补丁应用失败可以作为候选级正常负例保存，但它们不使完整方法的自然终态自动变成已知。

**直接来源：** [最终18槽矩阵](D:/Code/毕设/graduate-thesis-experiments/结论/20261012_审阅后四小时执行/PAIRED_RECOVERY_MATRIX.json)，本审计生成的 [归一化槽表](D:/Code/毕设/graduate-thesis-experiments/工作区/1012-astra-v2/final-b-finance-audit/B_18_slots_normalized.json)。

## 3. B候选AST相同：字节级事实成立，测试结论不存在

重新读取trial2的三个 `business_source.json`，每个包含704个业务源码文件。三份快照两两相比，仅 `moto/events/models.py` 字节不同，其他703个文件完全相同。差异的非空行全部为注释；完整 `models.py` AST三者相同，其保存序列化SHA为：

`fd59eb105f38490399a5c64b00d30f15036be3037e45eaed487d89c4dabbcf92`

本次使用Python 3.13，显式设置 `ast.dump(..., include_attributes=False, show_empty=True)`保留空字段后与原摘要一致；默认省略空字段会产生另一摘要，但不改变三者AST相等。这是审计表示规则的差异，不是源码变化。

三候选均通过 `_MISSING` 哨兵区分缺失键与值为null的已存在键，并调整exists分支。SF使用call26、call24历史线索，SOURCE3使用call24，NO_DIAG使用call16；请求中的证据确有不同。NO_DIAG仍接收合法历史编辑线索，所以应描述为“不使用学习诊断排序的同恢复器控制”，不宜改写成“完全无历史信息”。

**论文边界：** 可以说这些不同输入在本次已应用候选上没有形成代码结构差异，且这一观察与当前失败反馈可能起主导作用相容；不能证明反馈是唯一原因，不能证明排序一般无用，更不能把AST相同等同测试通过、修复正确或普遍功能等价。三个候选的公开业务执行和独立终验均未被观测。

**直接来源：** [既有三候选公开审计及快照路径](D:/Code/毕设/graduate-thesis-experiments/实验/实验260_排序与当前反馈共同恢复/resource_v2/EXISTING_CANDIDATE_PUBLIC_AUDIT260.json)、[独立重算candidate_AST字段](D:/Code/毕设/graduate-thesis-experiments/工作区/1012-astra-v2/final-b-finance-audit/audit_results.json)。

## 4. D：第三整体基线资格仍未闭合

PatchPilot与AOrchestra均为 `UNQUALIFIED_UNRUN`，`scientific_success=null`，`effective_baseline=false`。本轮D模型POST为0，模型费用0，新增有效外部基线数0。

PatchPilot完成115.249秒的机械修复，保留12样本/批量4及反馈细化、重新定位和选择核心；原生资格仍因pytest收集标记和文件句柄目标识别而未知。AOrchestra保留作者调度、SWE子代理、ACI、Memory20、轨迹摘要与上下文更新；读取/编辑与公开API检查通过，但生成pytest止于Windows标准化NUL路径问题，可信原有G/O未运行。完整首body已准备而未POST，也不等于完整方法试验已经开始。

**论文边界：** 正式发表、作者核心保留、若干接口通过、原生资格通过、完整方法终态和有效非零是不同门槛。当前可以报告实施障碍和已完成入口，不能写PatchPilot或AOrchestra“算法0成功”或“恢复率0%”。第三有效整体名额仍缺；此前有效的Agentless与EnAgent保留，但不是本轮新重复。

**直接来源：** [第三基线最终资格](D:/Code/毕设/graduate-thesis-experiments/结论/20261012_审阅后四小时执行/THIRD_BASELINE_QUALIFICATION.json)。

## 5. SBS：两次完整无步骤输出，而非非零强基线资格

从9个保存的真实响应逐一核对：af_0598完成4个前缀，af_0478完成5个前缀；9条第一非空行均为 `1. No.`，响应非空，finish_reason均为stop，总completion tokens为719。响应文件SHA、canonical body声明与对应账本条目一致。作者判断条件是是否以 `1. yes` 开头，本次9条均不满足；以 `1. no` 开头的正常否定路径全部满足，没有把合法的编号格式误作解析失败。

最终责任步骤输出0，`effective_nonzero_qualification=false`，严格步骤匹配为 `NOT_APPLICABLE_NO_STEP_OUTPUT`；对应资格文件Top1/MRR均为null。两个样本来自已曝光历史AF集合，不是软件18题或23题来源池。本次没有读取历史Gold标签内容。

**论文边界：** 可以写作者累计前缀、首次肯定停止的流程在两个固定样本上完整运行，且这次未得到责任步骤输出；不能据此宣称该方法普遍恒零，不能用这个无有效输出配置证明本文优越，也不能补造完整排名、MRR或未经标签评价的Top1=0。

**直接来源：** [最终SBS前缀审计](D:/Code/毕设/graduate-thesis-experiments/结论/20261012_审阅后四小时执行/SBS_ACTUAL_PREFIX_AUDIT.json)、[原资格结论](D:/Code/毕设/graduate-thesis-experiments/实验/实验263_SBS固定历史资格/NONZERO_QUALIFICATION263.json)、[作者实际停止谓词](D:/Code/毕设/graduate-thesis-experiments/工作区/1012-exp263-sbs-postreview/实验/实验263_SBS固定历史资格/author_adapted/utils.py:165)。

## 6. 费用、旧账与关闭状态

连续账本共4870条。新条目恰为4844—4870，27条，27个不同logical call ID，全部SETTLED。逐条保存的finance receipt与账本字段一致。再从27个实际响应usage独立计算费用：cache-hit输入、cache-miss输入和输出分别乘保存的已核低谷费率0.02/1/4元每百万token，逐条费用均与账本相符，合计0.45924094元。本次未重新查询价格，也没有重定价旧请求。

| 任务/用途 | 新SETTLED请求 | usage费用上界（元） |
|---|---:|---:|
| moto5134，B排序恢复对照 | 6 | 0.21202918 |
| moto7081，C已有进展压力小试 | 12 | 0.24134996 |
| af_0478，SBS | 5 | 0.00334456 |
| af_0598，SBS | 4 | 0.00251724 |
| 合计 | 27 | 0.45924094 |

SBS两题合计0.00586180元。D模型请求费用为0。上述是保存usage与费率计算出的上界，不是发票或银行实际扣款证明；缓存命中差异也使它不能直接用于宣称方法成本优势。

旧账基准支出30.13967058元，加本轮0.45924094元，精确得到累计30.59891152元。前4843条按canonical JSON重算SHA为 `1ee6d81af657f8fe176807b75fac02c7088d01cca5b7060895ddca374ea23f6e`，与历史锚点完全相同；旧4842整行摘要和旧4843整行也分别一致。旧4842仍为 `UNKNOWN_FULL_RESERVATION_RETAINED`，body SHA不变，global reserve及当前held均为0.533734元。新27条中没有重发旧4842或4843的body。旧未知仍未知，不能把“本轮新增未知0”写成“全账没有未知”。

窗口原定为19:29:05—23:29:05，实际关闭记录为23:29:27.533。保存的18个namespace关闭证明全部存在、SHA相符，记录的子孙进程停止与所属Job为空均为true；8次独立终验关闭总回执也相符。18个namespace由B的7个登记流、C的9个流、SBS的2个流构成，**不是B的18个计划科学槽位**。B的7个登记流只有5个付费，不能把登记与付费数量混用；8次独立终验属于C，不能填回B。

最终保存余额GET为2.41元，只是当时余额观察，不用其差额推断旧未知请求usage。`FINANCE_AND_RESUME_RECEIPT.json`保留了22:09的旧 `as_of_UTC`，并以 `final_as_of_UTC` 明确记录23:29:27的最终核对；V2引用关闭时刻应使用最终字段和ROOT关闭记录，避免把旧汇总时间当最终结束时间。

**直接来源：** [最终费用回执](D:/Code/毕设/graduate-thesis-experiments/结论/20261012_审阅后四小时执行/FINANCE_AND_RESUME_RECEIPT.json)、[实际窗口关闭](D:/Code/毕设/graduate-thesis-experiments/结论/20261012_审阅后四小时执行/ROOT_WINDOW_CLOSED_ACTUAL.json)、[旧4843历史锚点](D:/Code/毕设/graduate-thesis-experiments/工作区/1012-exp259-window-finance-postreview/实验/实验259_四小时连续费用隔离/HISTORICAL_ANCHOR_4843.json)、[独立usage算术与旧前缀检查](D:/Code/毕设/graduate-thesis-experiments/工作区/1012-astra-v2/final-b-finance-audit/audit_results.json)。

## 7. 可直接写入V2的精简表述

> 四小时排序恢复比较保留2题、3条件、3重复的18个预定槽位，实际5条轨迹产生6次已结算生成。由于公开原生验证接口及资金边界，尚无完整三条件共同自然终态，公开目标、普通保护和独立终验均未形成已知结果，因而不能估计排序对恢复率的收益。第二次重复中三个已应用候选仅在注释上不同，完整代码AST相同；这一事实只说明本次候选未形成代码结构差异，不能替代测试或因果归因。

> PatchPilot和AOrchestra保留了作者核心流程，但本轮原生资格未闭合，未开展完整模型试验，不能按算法零成功处理。SBS在两个已曝光历史样本上完成九个累计前缀判断，均正常输出No，未得到责任步骤，故本轮没有取得有效非零资格。已有Agentless、EnAgent仍为有效整体对手，第三个有效整体基线仍待补足。

> 本轮27条新请求全部结算，按保存usage计算的费用上界为0.45924094元，旧账累计上界为30.59891152元；旧4842号未知请求的0.533734元完整预留未释放、未重发。所有窗口内已登记流及独立终验均有关闭回执。费用及运行关闭得到核实，不意味着研究假设已经得到支持。

上述表述不替代C机制审计。本审计只为核对总费用读取C的12条请求与关闭元数据，未重新裁决其九条轨迹的保护机制效应。

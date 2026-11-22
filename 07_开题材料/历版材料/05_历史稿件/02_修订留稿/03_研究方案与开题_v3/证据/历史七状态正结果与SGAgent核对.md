# 历史七状态正结果与SGAgent核对

核对日期：2026年10月13日。只读既有封存记录和公开论文；没有重跑、模型请求或新Gold读取。辅助结构化证据见[只读核对JSON](D:/Code/毕设/graduate-thesis-experiments/工作区/1013-proposal-v3/baselines/历史七状态与SGAgent_只读核对.json)。

## 1. 用户指出的正结果应保留

**实验172确有G153单root恢复5/7、Agentless 0/7的正向开发结果。** 七个task_id不同，同题三方法起点源码库存摘要相同。按照5个本文独占成功、0个对手独占成功计算，双侧精确McNemar值为0.0625。它可以作为继续研究的依据；不能被后来不同任务、不同模型和不同恢复机制的五题结果覆盖，也尚未达到通常0.05显著性阈值。

实验172主比较另外运行G153_JOINT_VBR，得到6/7。其对Agentless的原始p=0.03125，预设Holm两比较调整后0.0625；与single的p=1。用户表的5/7对应single条件，不能悄悄换成joint6/7提高叙述力度。[冻结计划](D:/Code/毕设/graduate-thesis-experiments/工作区/1007-exp172-seven-task-joint/实验/实验172_七任务完整方法与联合恢复/approved_plan.json)与[原始21流程及汇总](D:/Code/毕设/graduate-thesis-experiments/工作区/1007-exp172-seven-task-joint/实验/实验172_七任务完整方法与联合恢复/main_completion_packet.json)提供直接来源。

| task_id | 来源 | 步数 | 单root候选闭包数 | 公开目标数 | 私有保持数 | single | joint | Agentless |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Project-MONAI__MONAI-2238 | 既有重建退化前缀 | 9 | 1 | 1 | 3 | 1 | 1 | 0 |
| dask__dask-9378 | 既有重建退化前缀 | 12 | 3 | 1 | 135 | 1 | 1 | 0 |
| getmoto__moto-7081 | RAW:3395 | 24 | 7 | 3 | 2 | 0 | 0 | 0 |
| getmoto__moto-5072 | 既有重建退化前缀 | 10 | 1 | 1 | 90 | 1 | 1 | 0 |
| getmoto__moto-5134 | 既有重建退化前缀 | 27 | 4 | 1 | 11 | 1 | 1 | 0 |
| getmoto__moto-7317 | RAW:4308 | 29 | 7 | 1 | 49 | 0 | 1 | 0 |
| getmoto__moto-6212 | RAW:1738 | 16 | 6 | 1 | 14 | 1 | 1 | 0 |

这里的7是七个不同issue标识各对应一个失败状态，不是7次同题重复；也是已曝光开发状态，不能称7个独立盲测问题。MONAI2238、dask9378、moto5072和moto5134的manifest明确记载：该轮评价不是原issue修复目标，也不是原智能体当时执行测试的原始观察。它们由历史记录编辑重建状态后重新执行原生测试而获得退化证书；moto7081、7317、6212接自实验165的公开RAW轨迹自然退化分支。所有目标均为本轮声明的恢复合同，不应整体改名为标准SWE-bench issue解决率。逐题base commit、前缀坐标、起点摘要和manifest路径已放入辅助JSON。

## 2. C₀、预算和方法版本

C₀是每题冻结失败前缀重建后的代码状态；三个方法每题独立恢复到同一库存摘要。实验172复用实验166固定十题中具有完整dense检索缓存且完整query≤8192的七题，事前因容量排除moto6352、moto5286、pydantic8567。不是根据这轮胜负保留七题，但整体来源池早已曝光。

同轮生成后端为Qwen2.5-Coder-7B-Instruct GGUF Q4_K_M，模型SHA为`509287f78cb4d4cf6b3843734733b914b2c158e43e22a7f4bf5e963800894d3c`。每flow外部上限360秒、9次公开native、一次最终私有验收、64次模型调用、24576输出token；上下文槽32768，模型输入cap30000。G153使用旧的训练排序与合法单root依赖闭包恢复，single没有生成补丁调用；joint加入预定二root闭包联合，仍为9次公开预算。它们不是当前SOURCE3+Flash语义生成恢复器。

Agentless使用作者commit `5ce5888b9f149beaace393957a55ea8ee46c9f71` 派生的本地完整阶段适配，层级定位和dense检索结合、3补丁、2复现测试、回归/复现筛选、归一化投票。7条均有阶段记录，累计21次补丁生成、3个可用补丁、14次复现生成、1个有效复现、3次候选回归和1次候选复现；最终3条COMPLETED、4条MODEL_SEMANTIC_FAILURE，已知失败不是工程NA。但“阶段都走过”不能改写为所有阶段都产生有效产物，也不等同作者40候选/40复现规模的表现。[Agentless作者核与适配审计](D:/Code/毕设/graduate-thesis-experiments/工作区/1007-exp172-seven-task-joint/实验/实验172_七任务完整方法与联合恢复/agentless166_source_audit.json)。

共同可用信息是失败当前代码、公共恢复目标/反馈、公共回归及合法工具；G直接消费轨迹排序，Agentless采用其当前仓库/目标视图，并可检索许可前缀，没有被迫接G的候选池。方法视图不同属于冻结算法设计，应披露为同许可证据而非完全相同输入字符串。

验收在`environment166.py`的最终override中取已选候选对应的公开目标结果与公开回归结果，再执行私有保持测试，并核合法编辑和360秒；缺乏可信公开/私有结果保持unknown。验收对象是指定目标＋保持合同。不能因此声称整个原issue已经完整解决。[验收实现](D:/Code/毕设/graduate-thesis-experiments/工作区/1007-exp172-seven-task-joint/实验/实验172_七任务完整方法与联合恢复/environment166.py)。

## 3. 保留正结果，同时披露唯一多赢的疑点

joint比single多赢的moto7317存在同一source SHA `2bf878c9cf15d2989b787d94460e222b62afda68ec70a7ca1c3b14d5f4db051d`、同一请求节点、同样省略call24/26/28时，single第2次公开失败而joint第2次通过。失败日志为CreationTime与before/after时间界限断言，含本地/UTC时间差；已存证据没有建立最终根因。那次候选本身还是单root，不能把多出的1次成功归功于pair算子。需保留原始结果与疑点，不能为得到更好统计事后删该题或重选结果。[同状态不一致证据](D:/Code/毕设/graduate-thesis-experiments/工作区/1007-exp172-seven-task-joint/实验/实验172_七任务完整方法与联合恢复/same_state_native_inconsistency_audit.json)。

这个疑点限制joint增益解释，不抹除single本来5个成功、Agentless0个成功的观察。前者可支持“该开发合同上旧诊断引导恢复有作用的初步迹象”，不能单靠它证明学习排序本身优于无诊断恢复器，亦不能证明当前生成式方法已经稳定优于强外部方法。

## 4. 为什么后来五题2/5对3/5不是反证替换

后期五题为moto5406、moto6387、moto5980、mypy15155、moto5516，与旧七题task_id交集为0。后期使用Flash生成式部署和更新后的公共恢复/验收合同；本文是历史排序证据引导的语义修改，Agentless也变为不同采样与工具部署。后期五题还有30分钟交付与自然终态两个端点，旧七题则使用360秒合同。任务、机制、后端、内部采样和端点均已变化，两个结果不能当同条件重复的互相否定。

应在开题中并列写：早期七状态旧部署观察为5/7对0/7，支持继续探索；后期五题生成式部署为2/5对3/5，暴露新协议下竞争力尚未确立。两批都是开发证据，下一步要冻结同一生成式方法、强基线和共同接口后再比较。[已复核后期五题结果与逐题表](../../01_Astra两小时独立审阅/04_开题报告_V1_六章完整稿.md)。

## 5. SGAgent身份、工程NA与下一步

SGAgent全称为**Suggestion-Guided LLM-Based Multi-Agent Framework for Repository-Level Software Repair**，作者稿确认TOSEM 2026录用，DOI为10.1145/3818617；既有出版社核定在线日期2026-05-26。TOSEM在项目已读CCF2026第七版软件工程A类期刊表第2项。作者[论文v2](https://arxiv.org/abs/2602.23647v2)、[完整方法](https://arxiv.org/html/2602.23647v2)、[公开仓库](https://github.com/iSEngLab/SGAgent)和本地[正式身份核定](D:/Code/毕设/graduate-thesis-experiments/工作区/1003-diagnosis-investigation/exp132_review/final_window_1745/sgagent_primary/sgagent_selection_evidence.json)互相对应。本轮出版社DOI访问403，未用占位卷期或作者PDF页脚的2024模板日期替代正式身份。

本地固定作者commit `33a2cfe61d56494ab2d20a2b0c48c1f43e37b452`。完整设计含KG/14工具、locator、二次关系检索的suggester、fixer、多候选、独立复现、回归/复现筛选及投票、记忆摘要。已有source map说明原KG是内存实现，不能把可选Neo4j安装当必需大工程。论文说7类关系而已核作者代码有6种显式关系及测试查询启发式，应保持实际作者实现并披露差异，不凭空加第7种边。[实际源码与适配差异](D:/Code/毕设/graduate-thesis-experiments/工作区/1007-exp166-four-paper-baselines/实验/实验166_四项正式论文基线快速整体验证/sg166_final1912_source_map.json)。

实验166历次SG工程累计61次真实响应、12065输出token；只有1次早期native且验收未知；正式目标调用0。最后4次响应到locator三次模型调用与两次工具调用，sufficiency未完成；suggester、patch、reproduction和候选验收皆0。最终错误涉及嵌套工具参数JSON的Windows转义，早期还出现公共native guard/coverage未知。故旧表NA应明确为**完整运行资格未通过**，不是修复0/7，也不是论文没有实现。[最终真实资格收据](D:/Code/毕设/graduate-thesis-experiments/工作区/1007-exp166-four-paper-baselines/实验/实验166_四项正式论文基线快速整体验证/sg166_final1912_real_fixture_receipt.json)、[最后完整链收据](D:/Code/毕设/graduate-thesis-experiments/工作区/1007-exp166-four-paper-baselines/实验/实验166_四项正式论文基线快速整体验证/sg166_wholepipeline_receipt.json)。

## 6. 唯一备选结论：改为SGAgent

**固定三主Agentless、EnAgent、PatchPilot；唯一备选改为SGAgent。AOrchestra保留历史候选档案，不作为第二备选。**

| 判断维度 | SGAgent | AOrchestra | 对决定的影响 |
|---|---|---|---|
| 直接问题覆盖 | 将定位转为关系检索和可执行修复建议，正面挑战本文诊断到干预接口 | 动态创建子代理并配置模型、任务、工具和上下文，主要检验编排 | 当前RQ不研究动态编排，SG是更需要排除的替代解释 |
| 正式身份/核心 | TOSEM2026；原KG、14工具和多阶段源码可用 | ICML2026；79作者文件exact可用 | 两者都合格，不能因旧报告遗漏SG而排除 |
| 已达工程阶段 | 旧7B61工程调用，完整流程仍未过；当前Flash部署未知 | 最新ACI和公开API已过，但生成pytest和原G/O未闭合，模型POST0 | AOr工程更近；没有依据声称SG更便宜或一定可跑 |
| 完整核心下一步 | 保留作者raw+variant0+8变体、完整角色循环、独立复现、投票、摘要；解除旧3p2t资源适配和双层JSON障碍，接共同原生合同 | 解决Windows设备路径/pytest与原G/O，之后保留10主尝试、50子步、Memory20与window100 | SG源码/运输核定工作更多；AOr长链完整生成的模型费用仍未知 |
| 是否不可替代 | 直接检验显式语义建议能否优于历史步骤排序证据 | 当前三主已经覆盖固定、搜索/集成及反馈细化，动态编排不是当前核心主张 | SG相关性优势超过AOr已有工程进度优势，选择SG |

这不是预测SG胜率或启动新的修复循环。只有PatchPilot按预先规则确认无法取得共同协议资格后，才启动SG的唯一备用资格路线；SG自身先完整固定作者阶段/采样，再做同两题三重复的资格小试。若SG也不通过，第三有效方法继续空缺，不能自动跳到AOrchestra。当前Agentless和EnAgent历史有效数仍为2。

SG的公开验证脚本消费预生成复现JSONL，而所读入口没有完整新的独立生成端点；不能读取这些目标复现/结果填空。后续需按论文方法补齐独立生成端点并显式冻结测试采样数。新协议固定独立生成2个复现测试，先在C₀验证并保留全部有效测试用于候选比较；这一数目是本研究部署选择，不声称作者默认。旧适配为9次native上限只执行至多1个有效复现的限制不继承到完整自然终态。已读作者core中zero_llm与eighty_llm实际均temperature0.8，按固定作者源码保留，不能凭变量名写成greedy。完整成本尚未实测，不能承诺在现有余额中完成。

## 7. 可纳入开题的文字

> 早期开发实验在七个历史失败状态上观察到，旧G153单root恢复成功5例，Agentless本地7B适配成功0例，双侧精确配对检验p=0.0625。该结果为利用轨迹诊断开展恢复提供初步依据，但评价对象主要为重建后的原生退化恢复，模型、方法及预算均区别于当前生成式部署。后期另一批五题的自然终态为本文2/5、Agentless3/5，说明新部署的竞争力仍待验证。两批证据分别保留，不合并也不互相覆盖。

> 整体比较固定Agentless、EnAgent和PatchPilot三项主基线，以SGAgent为唯一备选，分别检验固定流程、集成搜索、反馈细化和诊断后显式语义建议。SGAgent具有正式TOSEM2026身份及作者实现，旧工程未取得完整执行资格，故只计为备选设计，不填入零成功或有效成绩。AOrchestra保留为历史候选与相关工作，不设置第二备用路线。

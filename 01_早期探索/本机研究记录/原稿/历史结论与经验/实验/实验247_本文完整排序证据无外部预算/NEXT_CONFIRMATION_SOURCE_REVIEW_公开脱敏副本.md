# 下一轮确认任务与整体基线：只读来源审查

建议在实验248的两道开发题小试后，先冻结通用改进，再依原计划顺序对 **dask 9378、moto 5072** 做本轮共同资格门检。两题通过后，以本文、Agentless、EnAgent完成同条件配对。本轮不新搭另一个基线；PatchPilot保留为已有完整实现的候补，不把其停止记录判成失败。本文档只提供选择与执行条件，没有运行模型、业务native、独立终验，也没有修改账本或已有封存源码。

## 选择来自冻结顺序

权威来源是原23题资格清单和《新确认集与共同预算_前瞻.json》，后者明确按原自然顺序排除两道MONAI小试，不按本文输赢替换。23题由15个已有编辑退化和8个原问题未修复构成；主计划21题，当前完整三方共同组5题，其外16题是10个历史回归资格、6个原问题资格。conan 14397已有本轮收集/资格不一致排除，其他15题没有本轮共同放行，不能从历史结果填成已完成。

余16题依次为：dask 9378、moto 5072、moto 5134、moto 5286、moto 6352、pydantic 8567、mypy 10392、mypy 11134、moto 7081、moto 6212、conan 14397、moto 4972、moto 5587、pydantic 8965、dask 8484、MONAI 4109。完整ID、原资格类别与原计划下标见同名JSON。

实验248源码协议的开发小试仅包含mypy 15155、moto 5516；首选两题均不在其中。本次选择未读取任何方法在这两题的补丁或独立验收结果。它们是相对于248开发机制的后续确认题，仍属于有历史使用的来源池，不能称为整个研究从未接触的盲测集；RQ1训练重叠仍须另核。

| 顺序 | 原公开目标G / 保留测试O | 当前可复用证据 | 本轮尚缺 |
|---|---|---|---|
| 1：`dask__dask-9378` | G：`test_like_funcs[empty_like]`；O：`test_mixed_concatenate[<lambda>25]`，均在`dask/array/tests/test_masked.py` | publicpack与原SHA相等；119个C0业务文件无缺失/漂移；原模板466文件一致；现有CPython 3.8.20入口和base均存在 | 实际物理Python身份、当前G失败/O通过、共同信息许可及进程停止证据 |
| 2：`getmoto__moto-5072` | G：`test_close_account_returns_nothing`；O：`test_list_organizational_units_for_parent_exception`，均在`tests/test_organizations/test_organizations_boto3.py` | publicpack与原SHA相等；691个C0业务文件无缺失/漂移；原模板1571文件一致；现有CPython 3.11.15入口和base均存在 | 同上；不要把当前其他moto题的运行资格移植为本题资格 |

两题原`source_inventory_reference`均逐字节与合同SHA一致；C0业务清单摘要分别为`0fd76c9ee56f07af4835c6c767409f115f7659ffbdf2a6886481131e30c9e639`、`1f06d9ed196c12b7bab30681bdba2e722de51fd42e0736b684e09f982a65a37e`。原合同的`physical_product_python_expected`仍为空，因此“路径存在/源码相等”不能替代当前native资格。没有执行解释器或业务测试来夸大这一结论。

具体下一步是逐题复制相同C0并生成各方法相同的公开输入，使用现有解释器，在Root拥有的Job与四槽调度下完成一次零模型门检。核实际业务加载路径、精确G/O收集及结果、当前ABI、公开目标遮罩和全部子进程停止；dask尤其保留CPython3.8，不迁移到3.11。失败只作一次最多五分钟机械修复；仍不合格则全方法共同记资格未知，并按冻结顺序转下一题，保留失败。不能因为本文难修而跳题。

## 两个候选基线的完整性与成本

正式出版与可执行是两个条件。PatchPilot为[ICML 2025正式论文](https://proceedings.mlr.press/v267/li25cf.html)，SWE-agent为[NeurIPS 2024正式论文](https://papers.nips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html)；两会议列在[CCF人工智能A类目录](https://www.ccf.org.cn/Academic_Evaluation/AI/)。这两项均不能替代至少一项2026正式方法的要求；保留EnAgent，其本地正式出版复核记录为ICSE2026，DOI `10.1145/3744916.3787761`。

### PatchPilot：已有完整候补，不作为“新找到”的对手

作者仓库[固定commit `84ec3d3`](https://github.com/ucsb-mlsec/PatchPilot/tree/84ec3d3fbc34269078f9f9b62b9d390947344944)仍是查询到的main。实际读取了`reproduce/reproduce.py`、`fl/localize.py`调用链、`repair/repair.py`、`repair/bfs.py`和模型工厂。原31个源码/许可文件逐字节符合已保存manifest。其核心包括复现、分层定位、计划逐步编辑、PoC及功能验证、失败反馈细化/重新定位与最终选择，不是README空项目。

必须使用**最新`工作区/1011-pp22`**而非早期227/237短配置。最新源码入口和参数封存为：12候选、batch4、4次细定位、top_n5、context_window15；定位温度0.7；PoC最多7次反思；每计划步最多5次生成；功能测试文件选择上限3、温度0.3、输出1024；计划/审阅/细化/功能测试选择开启，`refine_for_nopoc`、`reloca_for_nopoc`、混合模型选项关闭；原投票重试和提前结束规则保留。PoC及BFS输出4096，原BFS温度0.8；各角色保留源码自己的温度和输出大小。实际模型统一Flash，是模型适配而非论文模型成绩复现。

作者README示例的context_window是20，最新项目封存是15；裸CLI默认max_samples又为20。应公开这三个来源差异，不能将“完整核心/12候选”写成所有参数均与任一作者入口完全相同。早期227的4候选、batch1、定位1、top_n3属于旧短配置，不能据此描述最新PP22。

没有必须下载的训练权重；原依赖有CST、fuzzysearch、tokenizer、实际coverage、flake8、Git及产品依赖。已有官方离线依赖与缓存，原31文件已核。PP22的Root发布脚本绑定实际`MECHANICAL_FULL_INTERFACES_0POST_PASS`、原Git/PoC/coverage/ABI/完整停止及首请求；已有真实机械放行，不能说仍从零搭建。普通原始SWE任务支持依赖容器/任务环境，当前Windows native适配替换的是执行边界，不能删掉真实测试。

最新`run_control/getmoto__moto-5406/PARENT_TERMINAL_FULL_SCIENCE243_V10.json`记录`NATIVE_SUPERVISION/ROOT_SHARED_STOP`，不能据此给PatchPilot算法0分或判断弱。若未来继续，应由Root核完整消息、未完成阶段、费用与停止点后续跑，已结算请求不重发。当前不优先恢复的原因是新题共同资格、功能测试选择及多阶段费用仍会占用余额，而已有Agentless/EnAgent可以直接检验248缺口；不是用一次偶然失败淘汰对手。

### SWE-agent：出版与核心成立，当前五分钟部署不成立

实际经GitHub API读取了论文时期[v0.4.0源码](https://github.com/SWE-agent/SWE-agent/tree/1e065f8c860a6a8aa8b06a38bb68f1e00b8bd128)：`agents.py`完整动作/反馈循环、`swe_env.py`执行环境、`models.py`、`config/default.yaml`及依赖。环境直接使用Docker容器及Linux命令，不是可直接替换成Windows普通subprocess的抽象桩。当前PATH和标准Docker安装路径均未找到可用入口，未声称穷尽全机，也未安装Docker或下载镜像。

[论文§4、附录B.1/B.5](https://papers.nips.cc/paper_files/paper/2024/file/5a7c947568c1b1328ccc5230172e1e7c-Paper-Conference.pdf)的最终配置为温度0、100行窗口、最后5条观测；报告pass@1，原每题4美元上限。源码数据类的温度默认1不能误作论文实验值，top_p默认1；原动作解析、搜索/编辑工具、lint拒绝、演示与历史处理应整体保留。论文使用GPT-4 Turbo/Claude3 Opus，不需要本地训练权重；换Flash后必须标记适配并重新取得有效表现。本次只确认该版本的核心存在，没有宣称它是论文唯一精确实验commit。

缺现成Linux/Docker执行边界与同C0/公开许可适配，五分钟不足以完成公平门检；因此不启用。需要新镜像、环境和完整工具隔离时，禁止用删工具、去真实执行、替换成普通修复提示来凑一个“整体基线”。

## 概率性和本轮可支持的结论

小试用于判断完整链是否可运行、机制是否触及预先解释的失败位置。两道开发题一次成功不能证明机制必然有效，一次失败也不能说明方法无效。SWE-agent论文附录B.5的多次运行显示单题结果会变化；这支持预先规划重复，而不是失败后只给本文追加机会。

建议先用两道自然顺序新题完成每方法一个完整轨迹，报告所有成功、自然失败和删失；这只是可行性配对。若余额足以覆盖**所有方法、两题相同次数**，再在看新结果前冻结第二次独立重复的种子/顺序；同时报告逐次pass@1和方法×题结果，不从两次中只取较好一次冒充原指标。不能为某方法一直重试到成功，不能根据第一个seed结果改变任务或参数。两题/两次规模仍不足以证明总体显著优势。

Root最新实际查询消息将余额更新为**[账户数值已隐去]元**，增加原因未确认、不是Root充值；两道248首个实际请求合计0.0364518元。本审查没有自行查询或改变资金。原00:17的[账户数值已隐去]元仅保留为历史观测。Root将按连续账本追加cap后再放行确认实验；余额增加不使本审查获得执行授权，也不改变强对手选择。

下一批按完整封存请求和方法自然阶段预估、实时余额及预留决定能否完成共同配对；不充值、不下载大模型。资金不足则保留未完成的自然端点，不把未跑基线计为失败。并行复用模型并发2/公共native槽4的Root共用调度。Root将另建确认实验工作树并明确独占执行Agent；本轮可并行准备两题零模型资格，但须先统一共同maskedscope、current-C0 supplement和物理native Job契约。本审查没有另开工程或科学队列。

## 交付证据

同名JSON保存来源23、前瞻21、248开发协议的原路径和SHA，余16题状态，所选两题精确合同/pack/运行环境/字节检查，以及31个PatchPilot作者文件核验。论文与作者源码属于外部证据；本机路径存在、SHA和停止原因属于本次只读观察；后续资格、运行费用和科学效果仍待实际执行。

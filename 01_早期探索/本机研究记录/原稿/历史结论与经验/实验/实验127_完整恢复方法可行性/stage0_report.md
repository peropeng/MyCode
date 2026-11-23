# Exp127 Stage0 资产审计

本报告仅覆盖已授权的资产核验，正式实验协议和完整方法设计仍由主对话负责。审计于2026-09-22开始，跨午夜于2026-09-23封存。**34项资产全部留账；当前满足完整恢复合同、可直接正式纳入的最小清单为0。**这不是“没有真实错误编辑”：其中14项原始日志支持编辑引入新错误的判断，但尚未完成统一失败状态、检查点和目标/保留验收的复建核验。

## 1. 资产覆盖与身份映射

八个仓库的34个`base_commit`均以当前`git cat-file -t`确认是本地commit对象，并记录其tree对象。原始OpenHands SFT文件SHA为`ea4bf37de020e165c5210bedddeef523d8834a89a35a8c65fec24f76f0eae4f1`，SWE-Gym元数据SHA为`60569cea74bb281f7a5579467436a2bc1932c6e0c5f2f7fa0d084392abd9ad97`。逐文件原始字节SHA见`input_manifest.json`；没有改动旧资产。

34项原轨迹共1716条消息、789次函数调用。`message_mapping.jsonl`为每条消息保留稳定ID、角色、原内容SHA和全部调用ID；`call_mapping.jsonl`为每次调用保留消息索引、消息内序号、字符区间、原调用SHA、完整参数、响应索引/SHA以及旧锚点位置。消息编号和调用编号均从0开始，不能互相替代；思考、读取和无调用步骤保留为空映射，未按Gold补造编辑。旧272锚点只占调用34.47%，新账本覆盖全部789调用。

这是**完整身份与观测编辑参数映射，不是已验证的完整可执行状态历史**。197次`str_replace`和42次`create`的参数均可获得；239次操作中原日志明确成功230次、明确拒绝8次、没有相邻响应1次。拒绝的调用不能作为实际delta重放，缺响应不能猜成功。另有3次`insert`、13次`undo_edit`超出第一版两种编辑范围，15次编辑目标位于仓库外的`/workspace/`。shell命令和脚本也可能写文件或改变环境；例如MONAI-4745使用echo生成脚本，mypy-10392脚本创建目录/文件，mypy-15155脚本curl远端gist。已保留真实命令，未把这些副作用伪装成文本替换。

原始中间失败状态没有在本次审计中物化或重放。账本中的旧E02 `checkpoint_hash`是内容摘要，不是Git检查点对象，也不证明存在自然失败状态；旧Exp123受控快照不替代同轨迹原始失败检查点。

## 2. 证据必须分开解释

- **原日志中的真实编辑错误**：14项能把具体编辑参数、新错误观察和后续修正联系起来，逐项见`source_log_review.json`。例如pandas-52518调用15能输出原describe结果，调用16引入`pd.NA`，调用17同脚本出现`NameError`；它支持运行能力退化的源日志证据，但该脚本没有独立冻结断言。
- **原Issue未修复**：原输入本来失败或输出不符合Issue时，回到旧状态不等于任务修好。moto-6355调用4退出0其实缺少应抛异常；pydantic-8567调用4能输出JSON但`y`序列化仍不对。其后新增TypeError/NameError是编辑错误，前面的exit0却不是目标通过。
- **测试/环境改变**：moto-5134调用17通过后，调用18扩充测试，调用19失败，不能当同断言退化。mypy等外层脚本可能不传播子进程退出码，捕获异常后也会退出0；不据零退出码认定测试成功。
- **人工故障注入**：Exp123源码206—241行通过`responsible_position`/`fault_suppressed_by_responsible_omission`控制注入。34项旧受控compile/TNR恢复结果全部排除为新真实编辑合同的科学样本，原轨迹可用性照常保留；本轮未使用这些开关制造任何结果。
- **官方补丁参照**：六例moto仅证明原Issue测试接通，不归因于本文方法，也不证明14项自然中间错误的验收已就绪。

14项是源日志证据清单，不是按本文方法成功率挑选的正式实验子集，不构成责任Gold、独立复现或恢复成功。其余20项也全部保留，静态审查未建立同等证据并不证明绝无自然退化。

## 3. 所有34项逐任务账本

表中“源新错”是上面的静态日志证据；“原生桥”只表示官方base/reference FTP/PTP既有运行。所有行的新合同状态都是待核实、当前不纳入；旧Exp123受控科学结果都是排除。完整提交/tree、具体原命令、全部FTP/PTP节点、编辑参数、拒绝/缺失调用和逐项理由保存在机器账本，未隐藏不利任务。

| 任务 | SFT行 | 消息/调用 | 替换/创建 | FTP/PTP元数据 | 源新错 | 原生桥 |
|---|---:|---:|---:|---:|---|---|
| Project-MONAI__MONAI-3384 | 239 | 31/14 | 2/1 | 152/152 | 未建立 | 未接通核验 |
| Project-MONAI__MONAI-4109 | 73 | 61/28 | 9/1 | 1/54 | 未建立 | 未接通核验 |
| Project-MONAI__MONAI-4745 | 489 | 67/24 | 6/1 | 2/4 | 未建立 | 未接通核验 |
| Project-MONAI__MONAI-5543 | 238 | 39/18 | 3/1 | 2/3 | 有 | 未接通核验 |
| Project-MONAI__MONAI-5908 | 53 | 35/15 | 5/1 | 10/20 | 未建立 | 未接通核验 |
| conan-io__conan-14397 | 215 | 21/8 | 2/1 | 2/2 | 未建立 | 未接通核验 |
| conan-io__conan-15121 | 381 | 65/30 | 2/2 | 1/3 | 未建立 | 未接通核验 |
| dask__dask-8685 | 389 | 29/12 | 3/1 | 1/599 | 未建立 | 未接通核验 |
| dask__dask-9212 | 165 | 31/15 | 3/2 | 2/103 | 有 | 未接通核验 |
| dask__dask-9378 | 112 | 101/50 | 18/1 | 3/134 | 未建立 | 未接通核验 |
| getmoto__moto-4972 | 248 | 53/24 | 4/1 | 1/60 | 未建立 | 官方参照6例 |
| getmoto__moto-5134 | 154 | 101/49 | 21/1 | 2/12 | 未建立 | 官方参照6例 |
| getmoto__moto-5286 | 143 | 55/26 | 8/2 | 1/171 | 有 | 官方参照6例 |
| getmoto__moto-5406 | 125 | 41/19 | 3/2 | 1/26 | 未建立 | 未接通核验 |
| getmoto__moto-6212 | 13 | 53/25 | 4/1 | 1/16 | 未建立 | 官方参照6例 |
| getmoto__moto-6352 | 328 | 45/21 | 8/1 | 2/89 | 未建立 | 未接通核验 |
| getmoto__moto-6355 | 151 | 35/16 | 3/1 | 1/24 | 有 | 未接通核验 |
| getmoto__moto-6387 | 91 | 61/30 | 11/1 | 1/3 | 未建立 | 未接通核验 |
| getmoto__moto-7023 | 278 | 39/18 | 4/1 | 1/8 | 有 | 官方参照6例 |
| getmoto__moto-7167 | 192 | 33/14 | 2/1 | 1/193 | 未建立 | 官方参照6例 |
| getmoto__moto-7331 | 135 | 73/35 | 10/1 | 4/191 | 未建立 | 未接通核验 |
| iterative__dvc-3914 | 231 | 57/26 | 17/1 | 2/7 | 未建立 | 未接通核验 |
| iterative__dvc-6954 | 184 | 37/17 | 2/2 | 1/12 | 未建立 | 未接通核验 |
| pandas-dev__pandas-48686 | 410 | 31/14 | 2/1 | 2/627 | 有 | 未接通核验 |
| pandas-dev__pandas-49011 | 245 | 53/25 | 2/1 | 3/131 | 未建立 | 未接通核验 |
| pandas-dev__pandas-52518 | 431 | 49/23 | 4/1 | 1/96 | 有 | 未接通核验 |
| pandas-dev__pandas-57058 | 405 | 65/30 | 5/2 | 1/13 | 有 | 未接通核验 |
| pydantic__pydantic-8004 | 183 | 53/25 | 4/2 | 1/15 | 有 | 未接通核验 |
| pydantic__pydantic-8316 | 97 | 37/16 | 4/1 | 1/143 | 未建立 | 未接通核验 |
| pydantic__pydantic-8567 | 177 | 79/38 | 8/2 | 1/158 | 有 | 未接通核验 |
| python__mypy-10392 | 33 | 53/24 | 5/1 | 1/1 | 有 | 未接通核验 |
| python__mypy-11134 | 267 | 33/14 | 3/1 | 2/0 | 有 | 未接通核验 |
| python__mypy-11567 | 94 | 39/18 | 6/1 | 1/0 | 有 | 未接通核验 |
| python__mypy-15155 | 339 | 61/28 | 4/1 | 1/0 | 有 | 未接通核验 |

逐项纳入/排除/待核实理由如下；调用号对应完整映射，可直接定位原始参数与输出：

- **Project-MONAI__MONAI-3384**：仅见新增test_tile_on_grid.py成功；无同一保留断言编辑前通过、编辑后失败证据。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **Project-MONAI__MONAI-4109**：原torch.jit.script(pixelshuffle)已失败，连续TorchScript兼容性调整最终成功；失败变化不足以证明已正常功能被破坏。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **Project-MONAI__MONAI-4745**：shell echo生成测试脚本的转义引起SyntaxError，随后混合类型测试TypeError；包含editor合同以外shell写文件，不能据此认定库代码真实退化。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **Project-MONAI__MONAI-5543**：call7替换父类depth参数后报缺depth；call13插入初始化语句后call14出现IndentationError，call15修缩进后call16成功。此证据含insert操作，超出第一版仅文本替换/创建范围；没有冻结共同功能保留测试。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **Project-MONAI__MONAI-5908**：原shape错误后新均值维度运算报Dimension out of range；脚本捕获异常始终exit0。可见失败修复尝试，未证实原本正常功能退化。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **conan-io__conan-14397**：自建CLI脚本出现NoneType路径错误；没有同测试正常基准，也没有原FTP/PTP现行执行证据。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **conan-io__conan-15121**：原自建脚本因循环import失败，后换成subprocess仿写脚本通过；测试对象已变化，不能把后者作为Conan修复验证。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **dask__dask-8685**：首个test_eye失败后通过；没有可据以确认编辑前已正常功能被破坏的保留测试。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **dask__dask-9212**：原枚举token断言失败但模块可导入；call8新增@normalize_token.register(Enum)未import Enum，call9导入NameError；call10补import后call11通过。支持新增导入错误，不等于原Issue已恢复。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **dask__dask-9378**：多次原empty_like mask断言持续失败，且脚本修改和undo穿插；未见通过的共同保留基准。success split名称不能覆盖本日志中的持续失败。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **getmoto__moto-4972**：NoRegion为脚本配置，原DeleteMetricFilter正则问题及独立regex片段测试不证明退化；官方FTP/PTP桥另行可用。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **getmoto__moto-5134**：call17原脚本测试通过，call18扩充测试输入/断言，call19失败。不是同一测试的通过到失败证据；后续错误夹杂断言和排序变化，不自动定因。官方桥单独归因。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **getmoto__moto-5286**：原Domain字段KeyError后call14在_base_json添加不存在的moto.cognitoidp.backends导入，call15 ModuleNotFoundError；call16移除此实现后后续成功。真实新增导入错误有源日志；官方桥仅测base/reference。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **getmoto__moto-5406**：原跨region建表断言失败，修改后脚本/edge tests通过；没有已通过保留功能被编辑破坏的日志证明。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **getmoto__moto-6212**：原字符串.get错误被脚本捕获，exit0不等于通过；最终输出改善，未证明编辑诱发的已正常功能退化。官方桥可用。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **getmoto__moto-6352**：自建脚本NoRegion后补配置成功，未提供库编辑因果退化证据。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **getmoto__moto-6355**：call10新增TopicNotFound("...")，call11 TypeError明确指向该行；call13修构造后call14为预期NotFoundException。call4退出0实际上未抛Issue要求异常，不能作为目标通过证据。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **getmoto__moto-6387**：invalid literal for int None持续出现，末次观测不含完成退出码；缺少一致通过基准/完整末态验证。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **getmoto__moto-7023**：call6新增未定义EntityNotFoundException，call12 NameError；call13改为错误带参EntityNotFound，call14 TypeError；call15空参后成功。没有编辑前同脚本执行，不能直接证明保留断言退化；官方桥可用。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **getmoto__moto-7167**：只见本轨迹自建脚本通过，未见功能退化前后对照；官方FTP/PTP桥是独立设施证据。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **getmoto__moto-7331**：测试脚本多次导入当前版本不存在的mock名称，后变更测试import通过；需区分环境/脚本兼容问题与库退化。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **iterative__dvc-3914**：自建脚本单次成功，无一致保留功能编辑前后退化证据。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **iterative__dvc-6954**：脚本exit0仍含参数丢失或传输错误，后换test_params成功；不能把零退出码当任务通过。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **pandas-dev__pandas-48686**：call9新增pd.Timestamp却未import pd；同脚本call7原混合时区错误变为call10未定义pd；call11补import后call12成功。exit均0因捕获异常，属于新错误证据而非目标基准通过到失败。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **pandas-dev__pandas-49011**：只见自建复现脚本正常退出；无完整保留断言的退化对照。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **pandas-dev__pandas-52518**：强片段：call15同repro_script能输出np.float64/Float64 describe，call16改成pd.NA后call17未定义pd；call18改NA后call19又报NAType不能转float，call20修后call21正常。脚本只打印未冻结独立断言，需复建与保留验收。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **pandas-dev__pandas-57058**：call23能import库但捕获原argmax空序列错误；call24文本替换拼接行导致call25 SyntaxError，call27更正后call28正常。证明新增源码语法错误，不把call23 exit0当目标成功。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **pydantic__pydantic-8004**：call16添加未导入_typing_extra引用后call17 NameError，call19/20修引用后call21成功；原_t2属性Issue和新增_t5边界测试仍需区分。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **pydantic__pydantic-8316**：同HTTPResponse断言原已失败，多次替换改变错误输出但仍未过；不能从失败到失败推断保留功能退化。undo_edit存在。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **pydantic__pydantic-8567**：call4原脚本可创建模型/输出JSON但y序列化仍违反Issue；call25在另一个闭包引用未定义serialization_schema，call26 NameError，call27/28参数传递修复后call29恢复执行。支持真实新增运行错误，原Issue未解决的输出不算目标通过。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **python__mypy-10392**：call11/14写入未适当缩进代码；自建test_script在call16/18/20依次IndentationError，后更正缩进call22执行完成。没有编辑前同测试运行；脚本还写测试目录，需单独状态约束。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **python__mypy-11134**：call7 mypy能运行但报告67错误且外层exit0；call9新增未缩进return False，call10导入IndentationError；call11修后call12返回原67错误。证明新增导入失败，非原Issue修复。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **python__mypy-11567**：call5添加ParamSpecExpr分支而未导入，call7/9/11 NameError；call12补import后转None.accept错误，后修成功。测试在编辑后才创建，无先验保留基准。 真实编辑参数可读；完整失败状态和统一验收待核实。
- **python__mypy-15155**：原RuntimeError后call16未缩进补丁导致call17 IndentationError；call19修缩进后call20 TypeOfAny NameError，补import后call26正常。外层subprocess不传子退出码且运行脚本会curl远端gist，输入不可仅凭当前Git冻结。 真实编辑参数可读；完整失败状态和统一验收待核实。

## 4. 既有目标与保留测试

34项SWE-Gym的FTP/PTP节点、test_patch和官方reference patch均在当前Parquet中可读，base_commit与逐任务E02记录一致。元数据可读不等于测试当前可运行。原轨迹中Python/pytest/tox等命令及原始输出在`source_test_observations.jsonl`中，命令筛选是宽松清单而非全部是真测试；没有执行这些命令。

六例moto的逐节点审计、实际argv/cwd、base/reference返回码和输出路径收录于`native_reference_evidence.json`。所引用result、XML、stdout/stderr、patch和修复前失败attempt全部核对字节SHA。已选成功attempt为：4972/5134=`native-env-03`，5286=`native-env-02`，6212/7023/7167=`native-env-01`。每例base退出1、reference退出0；逐节点结论合计7个FTP在base失败且reference通过、460个PTP两态通过，原五个截断节点按已存唯一collection映射解决。计数是任务内节点，不是467个独立样本。

原测试环境为`工作区/0922-recovery-audit/.venv/Scripts/python.exe`，实际命令为该解释器加`-m pytest -q --disable-warnings --junitxml=...`及完整已保存节点数组，不能把数组拼成未经转义的shell字符串。其余28项没有该门当前原生测试执行证据。旧门采用Windows原生pytest，未运行官方Linux/container harness；本轮未启动任何新测试。

## 5. 本机环境、模型与A+B入口

主线程提供的`stage0_environment.json`保留观测时间和限定搜索范围。RTX5070 12227MiB、驱动596.21、Exp124环境torch2.7.1+cu128的CUDA可用；Exp123审计Python3.13.12含pyarrow25.0.1；原生测试Python3.11.15含pytest7.4.4。环境路径和包版本按原始机器文件保留。

`Qwen/Qwen3-Embedding-0.6B` revision `97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3`在`工作区/0922-exp124-ranking-baselines/third_party/Qwen3-Embedding-0.6B`的6个文件存在且SHA符合既有冻结值。StepFinder源码及15个checkpoint也存在；二者是embedding/排序资产，不是生成修复模型。限定缓存搜索发现其他embedding/视觉模型目录，不据此声称全盘无生成模型。常见loopback服务端口11434/1234/8000/8080/5000/3000未监听。

当前进程`DASHSCOPE_API_KEY`、`DEEPSEEK_API_KEY`非空配置存在，只输出名字与布尔值。具体模型、端点、凭据有效性及费用协议未核验，API调用为0；不能继续沿用Exp124旧资源门“当前无配置”的结论。

`stage0_ranker_entry.json`封存现A+B源码、符号行号、数据路径和SHA：Exp112C调用修正的Exp112 helper，Exp96提供pairwise；Exp113C的`HelperTupleOrderProxy`是旧部署接口所需修正。现loader只读返回731记录、716任务组、7366步；confirmation Gold未读取且未评分、未拟合、未用于选择。

旧Exp112C输出是OOF分数/指标，没有完整持久化推理系数；限定公开实验目录未找到完整模型权重。Exp113J只有34项各8锚点顺序，Exp113 adapter硬编码8步且content/thought为空；pairwise helper没有持久化返回权重。因此不能将旧顺序当作这些完整实际轨迹的新预测。全步骤适配和经协议允许的固定重训/导出待主线程完整协议，本轮均未实施。

## 6. 资产阻塞与停止位置

目前缺口是：实际错误状态和共同前态的重建验证；已拒绝/缺响应及shell副作用的可执行状态语义；独立目标与保留条件的冻结及可运行性；完整轨迹A+B推理接口和持久化资产；如协议选择调用生成模型，其具体模型/费用/端点合同仍未核验。14项源新错证据有助于后续明确合同，但不能在本轮自动补做。

Stage0未新增训练、预测、恢复比较、轨迹重放、native测试、API调用或下载。Exp125/126保持暂停；没有新正式protocol/method文件。提交本目录后等待主对话完整执行协议。

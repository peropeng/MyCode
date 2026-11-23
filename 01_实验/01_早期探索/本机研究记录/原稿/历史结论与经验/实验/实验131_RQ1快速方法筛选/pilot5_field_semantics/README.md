# P5 字段内容贡献与跨字段二阶相容

此固定组合已淘汰。AB在已用开发32上命中20条（62.5%），少于缓存C的22条与最强缓存基线的23条。它未达到25条，也未严格胜其他六配置。所有六个新线性头均收敛；没有以求解失败解释负结果，也不会依此32结果修改scale、L2、seed或二阶公式。

|配置|命中 /32|Top1|MRR|角色命中 /32|描述性验证命中 /40|
|---|---:|---:|---:|---:|---:|
|缓存 C|22|68.750%|0.79635|29|27|
|A|20|62.500%|0.76853|30|26|
|B|21|65.625%|0.77656|28|27|
|AB|20|62.500%|0.76927|30|26|
|AB_marginal|20|62.500%|0.77009|29|25|
|AA_duplicate|21|65.625%|0.78576|31|26|
|Joint|21|65.625%|0.77578|29|26|

四个既有缓存基线all-at-once / binary-search / SDBL / StepFinder分别23 / 13 / 21 / 22条，没有新执行。AB相对C改善0条、退步2条；AB与A、AB_marginal的32条Top1正确性相同，但其参数、原始分数和全部排序不因此相同。全部32任务保留，AB的12条归责错误与运行错误分别记录；训练、编码、评价没有运行失败。

该路线增加原始字段的完整1024维语义表示，基座C保持冻结。输入只来自原fit327、验证40、已用开发32共399条的 `record.public.task/turns`，含原始公开role和content/action/thought；匿名role只继续服务旧基座和分组。统一compact JSON生成E0（三字段空）、每个Ef（仅单字段非空）、EJ（三字段原文），按整包SHA去重。空/null统一空串，原非空字符串和空白保留；空Ef复用E0，m≤1的EJ精确复用相同包。共4175步、6527包、975098非padding token，最大1786，未截断。

现成本地Qwen3-Embedding-0.6B以local_files_only、trust_remote_code=False、BF16 CUDA SDPA、eval/inference_mode、use_cache=False编码，取last real token的完整1024维后float32 L2。seed20261003、deterministic、TF32关闭，固定每批≤16序列和≤8192 padding token，逐512包block留checkpoint。输入、模型资产和源码hash先冻结；16个长度分层包预检与padding检查通过，估计118.59秒后按已有授权全编码，实际59.500秒、峰值GPU分配1.519GB。样本向量尾896维能量占85.65%，此值只是向量能量比例，不等于语义或诊断信息量。

对非空字段令 `δf=Ef−E0`，空字段δf精确0；`α=max(sqrt(Σf||δf||²),1e−4)`，`xf=δf/α`。A拼接三个xf；B为 `sqrt(2)*concat(xc⊙xa,xc⊙xt,xa⊙xt)`，m≤1精确0；M拼接各xf平方，用于排除字段内二阶特征的影响。Joint用 `(EJ−E0)/max(||EJ−E0||,1e−4)`，1024维后补2048零，只启B头；它的有效输入维度不同，不声称各配置严格容量匹配。没有使用已被否决的 `Joint−Σδ` 混合换基定义。

四种表示各用原fit320组的单标量 `σ=max(sqrt(mean_group mean_record mean_step ||X||²),1e−4)`；含零行，不加V22分层权重，不按Gold或m筛选，不做逐坐标RMS，B不做独立row L2。σA=1、σB=0.013605204966551、σM=0.053148015962118、σJoint≈1，均未触floor。预检核对字段交换、B与M的二阶平方和恒等式、空字段/m≤1零值、3072维与Joint尾零、所有399条缓存C排序保持及有限梯度。

B公共覆盖fit172/327条、验证19/40条、开发17/32条，对应466 / 43 / 60步。17/32只是存在多字段公开步骤的任务数，不是Gold步骤覆盖率，也没有成为评价子集。A/B同非零行余弦均值fit−0.00117、验证0.00749、开发0.00379；低余弦并不证明两项独立贡献成立。

七配置为缓存C、A、B、AB、AB_marginal、AA_duplicate、Joint；实际新拟合六头。每个注册两组3072无bias系数，禁用块固定0；AA_duplicate在两块均用A及原L2，AB_marginal用M替B。拟合沿P4已审通用凸目标：原fit OOF缓存C标准化分数、合法fit Gold、V22组权重的记录均值CE加固定C1 L2；验证/开发继续使用原full-fit C缓存，没有再推断基座。固定float64 CPU1 zero-init LBFGS的300/375迭代/评估限额、history50、strong_wolfe、grad tolerance1e−7、change tolerance1e−12，无验证选参或aux。六头12–19迭代、最终grad∞最大7.74e−8、全finite，无限额触发；合计3.688秒，满足180秒共同预算。

`protocol.json`在2026-10-04 08:28:11 UTC、拟合前冻结。六组参数及缓存C先seal，随后只做一次同32七配置比较；验证40仅在拟合后描述，不作选择。`results/`保存每closure日志、模型、原始预测、配对改善/退步及门判据；`encoding_results/`保留全向量、字段数组和13个blocks；派生features压缩包、源码、输入、sigma和独立审查回执一并封存。

正式裁决 `STOP_FIELD_SEMANTIC_COMBINATION`。此32用于过多轮开发，不能称独立确认；embedding差分、对角二阶乘积及其线性头只是表征工程假说，不是已验证矛盾、真实因果效果或论文原创性。RQ1总体目标未完成，后续推进不同信息路线，RQ2暂停。

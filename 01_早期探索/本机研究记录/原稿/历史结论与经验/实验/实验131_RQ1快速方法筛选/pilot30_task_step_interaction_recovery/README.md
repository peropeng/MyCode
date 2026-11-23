# P30 在既有任务条件化 Joint 上增加独立 q 门控

本轮冻结P28 A角色e/优先级和原归一C，复用P29/P5 Joint1024原字节，仅把原公开task128转float64并按L2、下限1e-4归一为q。P5的E0与EJ编码packet本身都包含task和rawrole，因此Joint=(EJ−E0)已任务、主体条件化。step_only技术名表示只使用既有Joint、没有额外独立q门控，不能解释成完全没有任务信息；packet_context_provenance_addendum保存这一来源澄清，没有更改原合同公式。

一次CPU Generator seed20260816先生成Wq0(16×128)，再生成Wx0(16×1024)，均标准正态float64。两个头复制相同矩阵，v16全零、无偏置。任务门控为tanh(Wq q)逐元素乘tanh(Wx x)，对照仅取后者；v读取各隐藏向量除以固定sigma的结果，再加原C。两个sigma只在初始W0的原fit数据上，用等组、等记录、等步骤的总行能量RMS一次确定，零行包含、下限1e-4，训练后不再计算。实际sigma task=1.554323742030391、step=2.5022730362351027。

任务头学习Wq/Wx/v；对照注册Wq但冻结、不使用、不处罚它。两者注册18448参数，任务有效18448、对照16400，额外任务容量与变化性不同，不能称纯参数匹配的因果隔离。q门控是测试一种额外交互结构，并非首次加入任务或发明经典乘法/tanh。

两个头均回到原GLOBAL组加权CE+.2平均全部非Gold softplus，保留327fit/320组，不使用P29 Goldrole条件mask。正则为.5(v²+ΔWx²+任务头ΔWq²)/totalgroupweight，围绕初始化而非绝对W惩罚；AdamW全部weight_decay0，W lr1e-3、v lr1e-2、全局clip1、CPU float64单线程、最多两个工作进程。相同每epochseed及组shuffle，max20、patience6，不降轮或扫描。

两个头都按部署后的固定A角色优先AB在验证40上的Top1选模，包含epoch0，取最早严格最大。B独立全局解码只是同一选中头的推理消融，没有独立按B验证指标再选检查点。epoch0胜出明确表示没有新增学习收益；有限训练完成不构成原凸1e-7梯度证书。

七配置为C、A_role_first、B_task_global_decode、B_step_only_global_decode、主AB_task_role_first、AB_step_only_control及AB_task_soft_descriptive。soft在结果前已声明仅描述性，排除主门槛。主方法需至少25/32，严格超过五个主对照与四缓存基线23/13/21/22，两个头均有限、按预定停止规则完整训练，才过探索门槛。

两个选中头与全部输入、尺度、初始化、源码绑定，以及所有72条七配置score/rolepriority/fullorder封存后，一次读取32开发标签；验证沿用固定选模标签。硬排序保留所有角色与步骤，按角色优先、角色内分数、匿名digest/index，评估消费声明顺序并独立验证。角色为每条轨迹首次出现的匿名主体ordinal，不是七种跨任务职能。

唯一预检验证共享初始化、全399初始分数严格C、全72初始A角色排序与P28相同。合成两步检查中v=0时Wq/Wx任务梯度为零，v更新后两者都非零；对照Wq无梯度且不动、q=0使任务纠正零、固定sigma/delta ridge/input detach等均通过。没有新增预训练A、C或编码器前向，新增头的训练前向当然发生。完整结果20:04 UTC、训练截止20:02:30预留90秒；方案19:52:01.251起、研究16:24连续计时，RQ1继续、RQ2暂停。

原计划实际未启动训练：20:02:30固定训练界到达，源码PASS在20:02:37.567返回；原20:04目标未达。pretraining_budget_stop保存0合格新训练、0优化、没有读取本轮fit/val/dev标签，不能称为方法负结果。独立恢复run另存pilot30_task_step_interaction_recovery；失败永久保留，原数学检查和输入初始化不改。

本目录为同一科学假设的首次实际训练工程恢复。原20:04预算失败1、0训练留在原目录；新训练界20:12:30、结果界20:14，模型和初始化/数据/尺度逐字节复制，只有PRIVATE和DUE两处操作变更。原数学预检按原20:00:23时间/hash复用，未重执行，没有重抽矩阵、重算RMS或恢复已学权重。

完整恢复结果20:10:14.502 UTC保存，七开发配置全部22/32；验证C/A/Btask/Bstep/ABtask/ABstep/soft为27/30/27/27/30/30/29。两个头各6epoch/pat6、120updates，共240，两个都按部署AB验证选中epoch0/30hits，没有新增学习收益。选择Wq/Wx位移和v范数均0；最终task为Wq1.151108/Wx2.315181/v1.163080，控制Wq仍0/Wx2.713349/v1.365284。

独立恢复run7.938秒，原科学设计19:52:01到结果1093.250秒，16:24累计13574.500秒，包含原失败等待，不能仅报拟合耗时或声称原20:04按期完成。两非凸头有限且按预定规则完整训练；gradient_convergence_certified=false，旧凸1e-7资格不适用。停止固定独立q门控组合，RQ1继续。

恢复首次freeze20:10:03.663协议SHA0d73349434e17450c786677877cc001c4b05cb3ae37afe459fcee81acb48e765。20:10:04.271（文件LastWrite独立观察）追加11个操作metadata字段并Windows换行dump，科学和runtime字段没变，早于run20:10:06.558、FIT读取20:10:06.852；实际运行协议b02304a921bd3b87faade5784d7dd717884044c31f3d7142f3bd110cf77a29be。初版未在当时另存，已在执行后去除11字段并恢复原UTF8 LF，按原freeze输出SHA精确验证，另存protocol_initial_freeze_restored.json并诚实标记恢复来源；protocol_metadata_amendment_receipt追加此证据。之后不覆写冻结协议。

原输入初始化和复用角色缓存保留在单成员inputs_archive.zip，33684020字节，SHA6e2bd26f3fea4055f2fda7a538a24f946bf04c4365d77ea3bdae7f5fc17f1aae，成员inputs.pt SHA3e851fa020008dcbc51df77b8036abb5490d62b55817dd4c224a17451a0183d5与原输入和独立private副本完全一致。ZIP是结果后交付归档（20:14:02），不冒称预冻结或结果截止前创建；不含真实labels.pt。

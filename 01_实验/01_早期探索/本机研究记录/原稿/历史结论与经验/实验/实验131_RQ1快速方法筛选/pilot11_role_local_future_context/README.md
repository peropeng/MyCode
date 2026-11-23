# P11 角色条件本地观察残差

P10的描述性validation结果为C27/40、A27/40、B28/40、AB26/40。这里检验一个固定假设：CodeWriter与CodeTester的本地测试事件可能有不同的归因含义，共享一组A3权重可能不合适。

唯一表征改变是把P10已缩放A3按公开actor role交叉到CodeWriter、CodeTester、other三个互斥桶，形成9维并填充至1024。复制三项原值，不重新计算尺度；互斥桶保持每行平方范数，沿用P10的sigma。角色来自原步骤公开信息及N4观察身份，不来自Gold。

C原分数与P10已拟合B参数/预测作为明确缓存控制。仅A_role、AB_role是两个新拟合头；B不重复训练。原327fit/320组、40validation、32开发成员，以及group weights、listwise CE、active L2、CPU float64 LBFGS和1e-7梯度阈值全部沿用。

两个新头与缓存控制绑定全部封存后，一次评估开发32并提供validation40的描述统计。AB_role至少25/32且严格超过两个缓存控制、新A_role及四个基线才通过筛选。重复使用的开发32不构成独立确认；角色交叉是待检验的方法假设，不宣称创新。

研究clock仍从2026-10-04 16:24UTC累计，目标16:54新结果、17:24绝对边界。负结果保存后继续下一项RQ1假设，RQ2保持暂停。

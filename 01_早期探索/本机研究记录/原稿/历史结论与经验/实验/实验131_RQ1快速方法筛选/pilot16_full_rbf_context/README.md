# P16 完整上下文差分RBF残差

方向在P15结果之前固定。依据P10原full1024future线性validation28/40与P12 task128future25/40，检验截断及任务逐元素乘积可能丢失信息的假设。

仅复用P8已经按fit尺度处理的完整1024维deltaPast与deltaFuture。不做task乘积、prefix截断、新输入row-normalization或新编码。普通RBF候选、原型、通常median bandwidth、zero-preserving映射及fit组RMS完全沿用P14已审核函数，各分支64有效坐标补零至1024。

三个新头A_fullRBF、B_fullRBF、AB_fullRBF共享原groupweighted CE+active L2及float64 CPU LBFGS tol_change0，grad_inf≤1e-7门槛不放宽。327fit/320组、40validation、32开发成员全部保留；三头和C缓存绑定全部封存后才一次开发评估与描述性validation。

缓存C保持原样；P14 task128RBF与P10 fullFuture linear B作为有原protocol和差异说明的参考。信息内容、距离几何和任务条件化同时改变，不能将结果归因于单一原因，不宣称文献创新。AB至少25/32且严格超过C/A/B及四个缓存基线、全部三头收敛才通过探索门；已用开发32不构成独立确认。

研究计时仍从2026-10-04 16:24UTC累计，目标17:23结果、17:24绝对边界。归档不阻塞科学运行，所有负结果与失败保存，RQ2保持暂停。

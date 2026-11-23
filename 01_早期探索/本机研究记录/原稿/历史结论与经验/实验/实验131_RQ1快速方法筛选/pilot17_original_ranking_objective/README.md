# P17 原项目排序目标残差

已有14个合格head的fit/validation诊断显示，P10 fullFuture B有训练收益且validation略高于C，AB虽平均CE更低，Top1仍未形成互补。P17检验目标函数是否更应强调候选排序。诊断脚本与原报告原样保存在evidence目录，未重新执行，也没有开发预测或Gold读取。

全部输入精确复用P10缓存：A为原scaled local3维观察填充至1024，B为原scaled future1024，C为原OOFfit和fullfit val/dev分数；尺度、全部327/40/32成员完全不变，没有新编码或新特征文件。

唯一科学改变为原项目v15.loss.ranking_loss：每record的CE加0.2×mean(nonGold softplus(score_j-score_Gold))，单候选pair项精确零。CE约束候选概率分布，pair项直接约束Gold与每个非Gold的排序间隔；0.2直接继承已有C/P8目标，没有系数搜索。v22组权重、组内record平均、0.5active L2和总组权重归一保持。

新目标只在本目录实现，不修改任何旧共享代码。用原ranking_loss逐record循环对照新向量实现，校验数值与梯度，包含n1、非零Gold位置及fit真实长度配synthetic Gold0，不读取新真实标签。新A_rank、B_rank、AB_rank全部零初始化，保持CPU float64 LBFGS lr1/300/375/history50/strongwolfe/tol_change0与原grad_inf≤1e-7。

三个新头及C绑定封存后才一次开发32和描述性validation40。C与P10同feature纯CE A/B/AB保持明确缓存参考。AB_rank至少25/32且严格超过C/A_rank/B_rank和四个缓存基线、三头均收敛才通过探索门；已用开发仅作筛选，仍需独立确认，不宣称新loss发明。

原17:24结果要求已由P10及后续P16在17:23:04完成保存满足，旧回执不改。P17是新接续17:44目标，研究累计仍从16:24计算；fit600秒/run1800秒与17:44取先到者，RQ1继续，RQ2暂停。

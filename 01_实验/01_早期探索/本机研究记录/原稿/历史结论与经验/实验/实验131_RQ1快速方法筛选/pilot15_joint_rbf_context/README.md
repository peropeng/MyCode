# P15 联合过去未来RBF单头

方向在P14结果之前于17:07:41 UTC固定。以原P13已缩放A128/B128拼接并除sqrt2为256维联合输入，完全复用P14公开fit组代表点、去重、最多64 farthest-first原型、通常positive-pair median bandwidth、origin-subtracted RBF及fit组RMS规则。联合有效64坐标补零至1024，原始零输入显式保持零。

只新拟合一个bias-free wJoint，注册及active参数1024、有效参数最多64。评分是原C+phiJoint@wJoint，没有将缓存unary分数加入joint。P14已合格A_RBF、B_RBF及C作为原样参数/预测缓存控制，additiveAB_RBF为附加缓存参考。联合与additive的有效参数数64/128及输入/kernel几何不同，不能宣称完全相同函数容量或把结果归因于单一交互。

原327/40/32成员、group-weighted CE+.5L2、CPU float64、LBFGS lr1/300/375/history50/strongwolfe/tol_change0与原grad_inf≤1e-7不变。新头及所有缓存参数/原protocol/raw预测哈希封存后，才一次开发32与描述性validation40。已用开发仅作筛选，不构成独立确认，不做bandwidth/seed/coef搜索。

本轮新joint为22/32、validation27/40，grad_inf=8.92198e-8合格，与C/A缓存持平，没有达到25/32且严格超过C/A/B及四基线的门槛。负结果完整保留，不证明方法潜力被排除。

研究时钟仍从16:24 UTC累计，结果17:19:02 UTC已保存，早于17:24绝对界。RQ1继续，RQ2暂停。

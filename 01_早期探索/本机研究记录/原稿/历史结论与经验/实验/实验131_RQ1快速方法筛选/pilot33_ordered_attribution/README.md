# P33 有序归因似然

固定主方法AB_forward为19/32，低于25/32和C/A的22/32，决定STOP_FIXED_ORDERED_ATTRIBUTION_COMBINATION。没有更换主方法。三模型均通过梯度资格；模型训练运行失败0。

| 配置 | 开发32 | 描述性验证40 |
|---|---:|---:|
| C | 22/32 | 27/40 |
| A_role_first | 22/32 | 30/40 |
| B_forward_global | 20/32 | 25/40 |
| B_reverse_global | 21/32 | 26/40 |
| B_CE_global | 21/32 | 26/40 |
| AB_forward_role_first | 19/32 | 28/40 |
| AB_reverse_control | 20/32 | 28/40 |
| AB_CE_control | 20/32 | 29/40 |
| AB_forward_soft_descriptive | 19/32 | 27/40 |

本轮使用标准logistic stick-breaking类别分解，[Khan等2012](https://proceedings.mlr.press/v22/khan12.html)与[Linderman等2015](https://arxiv.org/abs/1506.05843)提供家族背景。只使用普通确定性likelihood，没有Bayesian采样或外部代码。正向与逆向各一新1024biasfree零初始化head，另有同输入、权重和ridge的新role-CE-only控制，三者全部移除旧.2pair项。原P29 x/C和固定P28A逐字节复用，不依赖P32学到的head或新特征。

每role按固定次序分解概率；C构成非末step hazard offset，末hazard固定1。FIT只用标注类别所在role的前缀NLL，原327记录/320组保留，48singleton数据loss0，未按prefix长度再归一。标注类别作为一次事件是建模选择，不证明是首个真实错误或后续无故障；offset使用完整公开C，因此不能宣称因果或online检测。预测所有publicrole，t=C+(logp_w-logp_zero)数值残差精确保留零初始化C。

三head最后梯度forward=5.47756194697e-08、reverse=9.50137671995e-08、CE=1.44440124108e-08，11/12/11迭代合计34，均≤1e-7。固定组权重/ridge相同，无验证选择。新head算术和训练正常发生，无新预训练A或编码forward。

方案实际于20:41:11写入，在20:42:29记录P32结果尚不存在，概念时钟20:40:50包含起草/等待；20:44:15后才按预登记派发。模块名冲突与状态literal换行共2个训练前工程错误真实留版本修复；旧数学PASS220885b8与实际源码97211e版本不覆盖，20项新数学fixture只执行一次，最终binding318fb690诚实复用。20:59:01协议一次冻结后源/协议/审查字节均未改。3head、72×9完整orders和216个公开LPw/LPzero/δ概率记录先seal后once32，再描述性40。

结果于2026-10-04T20:59:10.171695+00:00保存，21:04目标达成；设计20:40:50→结果1100.170s（含等待和修复），global16:24→结果16510.170s，frozenrun5.515s。公开输入与已有P29 archive member完全相同，引用原32MB ZIP与已验证receipt，未声称新归档；own private byte-copy保留。未因负结果调方向/solver/目标，开发32仍为已使用探索集，RQ1继续、RQ2暂停。

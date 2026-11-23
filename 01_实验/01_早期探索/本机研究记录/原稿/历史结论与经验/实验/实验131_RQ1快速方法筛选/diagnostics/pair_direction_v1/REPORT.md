# 配对方向信息快验

只评价冻结fit/validation中同角色、非exact、恰有一个Gold端点的公共缓存边；方向指标不能当完整任务准确率。

| 条件 | 组等权方向准确率 | 原始pair命中/总数 | 梯度∞范数 | 收敛 |
|---|---:|---:|---:|---|
| F | 61.4286% | 34/53 | 7.01e-08 | True |
| D | 71.9048% | 40/53 | 9.1e-08 | True |
| Net | 65.2381% | 37/53 | 9.55e-08 | True |

Net−D组等权差 -6.6667%，赢7组、输9组、平19组。预声明5pp且赢组多于输组的门：False。决策：ABANDON_CHI_DIRECTION。

fit覆盖270/320组、277/327条、455对；validation覆盖35/40组、35/40条、53对。无覆盖分母完整保存。

现有三个Python运行时都缺sklearn，训练前单独冻结protocol_amendment.json，使用现成torch float64 CPU1线程LBFGS优化同一C=1加权和L2目标；没有安装依赖。三路零初值、相同成员与组→record→pair→±权重，分别fit-only加权RMS，不中心化。所有模型/参数hash封存后才第一次构造和评价validation。

三路实际训练1.640秒，总计2.406秒。连续margin、逐组胜负、覆盖、closure及限额情况见comparison.json。

没有读取或重评pilot32，没有改原pilot1代码、协议、模型、结果或manifest。本信息试验不构成完整A+B、任务优越、创新性或真实系统因果证据；后续结构由主协调者另行预声明。

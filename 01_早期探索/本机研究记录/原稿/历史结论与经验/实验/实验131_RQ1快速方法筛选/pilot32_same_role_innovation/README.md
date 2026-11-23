# P32 同角色内容创新

固定主方法AB_past为23/32，单独B_past为24/32；AB未达到25/32，也未严格胜出单独B与最好缓存基线23/32，故STOP_FIXED_SAME_ROLE_INNOVATION_COMBINATION。不用单独B或控制替换主方法。验证40只描述、未选模型；开发32已重复使用，是探索结果。

| 配置 | 开发32 | 描述性验证40 |
|---|---:|---:|
| C | 22/32 | 27/40 |
| A_role_first | 22/32 | 30/40 |
| B_past_global | 24/32 | 29/40 |
| B_future_global | 19/32 | 28/40 |
| B_linear_cached_global | 21/32 | 26/40 |
| AB_past_role_first | 23/32 | 32/40 |
| AB_future_control | 19/32 | 30/40 |
| AB_linear_cached_control | 21/32 | 29/40 |
| AB_past_soft_descriptive | 23/32 | 32/40 |

特征是x减同角色严格过去/未来步骤均值，空参照零→原x，无自身、跨角色或位置/count输入。各1433空参照/2742非空，各一个fit-only等组/记录/步骤含零rowenergy RMS，σpast=.9415745356748833、future=.9366082395469142。399记录/4175步保留，原x/C/A逐字节相同。

两1024biasfree零初始化head采用原GLOBAL CE+.2非Goldsoftplus与同ridge，原327fit/320groups/权重保留，最终梯度past=5.96537346943e-08、future=5.10089156137e-08，14/16迭代合格。原cachedlinear控制未重拟合，无新编码或预训练A forward；正常新head运算与两次训练发生。

只执行8个新几何fixture与72缓存对照复现，generic GLOBAL梯度证据诚实复用不重旧链。源码PASS后于20:43:09冻结一次协议，源/协议/版本审查后未改。2head与72×9完整输出先seal，再一次开发32与描述性验证40。结果2026-10-04T20:43:18.829557+00:00保存，20:48目标达成；设计20:37:20→结果358.828s，global16:24→结果15558.828s，frozenrun6.703s。

公开输入已于结果后压缩为两段≤64MiB ZIPparts，member/concat SHA流式验证；原tensor和ZIP留在owned private，无Gold/pyc/cache进入公开archive。原预算失败与恢复时点保持；不调本固定失败组合，RQ1继续、RQ2暂停。

独立实际模型/数据/seal/metric/clock与公开archive完整流式读回审查已PASS，版本化初稿与最终稿分别保留。

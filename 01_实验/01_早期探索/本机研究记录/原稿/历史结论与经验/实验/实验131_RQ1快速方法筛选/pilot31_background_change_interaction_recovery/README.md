# P31 同编码器背景与变化乘积：恢复执行结果

主方法AB_cross为22/32，平方控制AB_square为23/32；固定主门槛未通过，决定为`STOP_FIXED_BACKGROUND_CHANGE_COMBINATION`。主方法不超过C/A的22/32，也低于预先声明的平方控制。平方控制与最好缓存基线23/32持平，不事后替换为主方法。

| 预先声明配置 | 使用过的开发32 | 描述性验证40 |
|---|---:|---:|
| C | 22/32 | 27/40 |
| A_role_first | 22/32 | 30/40 |
| B_cross_global_decode | 21/32 | 25/40 |
| B_square_global_decode | 22/32 | 27/40 |
| B_linear_cached_global_decode | 21/32 | 26/40 |
| AB_cross_role_first | 22/32 | 27/40 |
| AB_square_control | 23/32 | 30/40 |
| AB_linear_cached_control | 21/32 | 29/40 |
| AB_cross_soft_descriptive | 22/32 | 27/40 |

两组新1024维无bias凸head从零初始化，用相同原GLOBAL groupweighted CE+0.2非Gold softplus及ridge；fit327记录/320组完整保留，LBFGS最终梯度cross=9.55863701151e-08、square=4.58886152591e-08，均≤1e-7。Cachedlinear是原P29已合格全局head，未重拟合；全部九配置复用原C/A，未进行新编码或预训练A推理。新head训练/投影运算正常发生，不能把这些算作零算术。

输入cross=a*x、square=x²使用同一编码器1024维坐标；a为原E0未经重归一的float32背景向量升为float64，x为原Joint1024。两特征各用一个fit-only等组/记录/步骤rowenergy RMS，含零。E0含task/rawrole+空字段，不是已知正常执行；Joint本已包含任务和角色信息。这里检验表示组合，不能解释为真实因果干预。

原UTC20:24窗口只有公开准备与检查，源码审查太晚而预算停止：有效新模型0、私有Gold未读、准确率为空。这个失败和21file原交付清单独立保留。本目录是同算法第一次正式训练的工程恢复；协议于20:30:24初次冻结时就写齐原MISS、恢复契约、未重做数学证据、launcher与原时钟，后续没有改写协议。恢复结果于2026-10-04T20:30:32.354775+00:00保存，20:34目标达成；原科学设计到结果983.772s（含失败准备），全局16:24到结果14792.351s，frozen run 7.172s。

两head与72×9公开scores/角色优先级/完整order在一次开发32 Gold读取前封存，验证40只描述不选模型。开发集已反复使用，只是探索证据；门槛失败保留，不调σ/solver/特征公式。RQ1继续，RQ2暂停。

公开输入和raw产品与原目录四个ZIP分片内member逐字一致，具体恢复见`shared_inputs_archive_reference.json`与原archive receipt。两个raw文件和private tensor均仍留在owned执行工作区；156MB raw由`.gitignore`排除，仓库分片可完整恢复，不含Gold、pyc或pycache。所有包装receipt均在结果后追加，没有假称预先创建。

独立实际审查已PASS，见`focused_actual_review.json`；原失败与恢复的交付清单分别封存，science不因包装改变。

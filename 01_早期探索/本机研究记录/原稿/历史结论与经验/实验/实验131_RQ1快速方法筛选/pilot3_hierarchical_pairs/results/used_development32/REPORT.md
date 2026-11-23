# Exp131 第三轮层次角色与互反D比较开发筛选

五路从头训练，在全checkpoint选轮/hash封存后统一评价已使用的开发32组。

| 条件 | 命中/32 | MAP步骤角色命中/32 | MRR | 选轮/实跑轮数 |
|---|---:|---:|---:|---:|
| C | 22 | 29 | 0.7964 | 8/14 |
| A | 21 | 31 | 0.7873 | 4/10 |
| B | 21 | 28 | 0.7688 | 8/14 |
| AB | 18 | 29 | 0.7272 | 15/20 |
| AB_loss_only | 19 | 31 | 0.7401 | 9/15 |

固定四基线命中：all_at_once:23, binary_search:13, sdbl:21, stepfinder:22. 无效输出保留32分母，三生成式单点基线MRR不可用。

预声明正门未通过：AB至少25/32并严格胜C/A/B/AB_loss_only。

| AB 对比 | 赢 | 输 | 平 | 净命中差 |
|---|---:|---:|---:|---:|
| all_at_once | 5 | 10 | 17 | -5 |
| binary_search | 9 | 4 | 19 | +5 |
| sdbl | 5 | 8 | 19 | -3 |
| stepfinder | 3 | 7 | 22 | -4 |
| C | 1 | 5 | 26 | -4 |
| A | 1 | 4 | 27 | -3 |
| B | 2 | 5 | 25 | -3 |
| AB_loss_only | 3 | 4 | 25 | -1 |

A的role head独立读query、同role g均值/最大值及log角色节点数；节点score从角色总证据与role内定位概率组合。B直接读公共cachedD antisymmetric384特征，用零init无bias线性头和degree归一符号汇总，不调用旧graph projection。RMS在全部fit公共eligible pair上组→record→pair等权，仅用RMS、无中心化，不按Gold筛fit统计。缺边回写0；辅助BCE只用Gold端点，不给neitherGold边伪标签。

AB_loss_only启A与系数1辅助BCE，不写B分数，保留全参数clip1产生的间接耦合。a_score/层次offset是logits−t的派生归一化量，随t/B改变，不能当独立A加分归因；真实A效应以条件消融判断。role概率质量为softmax(e)，joint MAP角色仍可能改变，不保证硬角色准确率保护。

日志CE_loss历史字段实际是总record objective，B/AB/AB_loss_only包含辅助BCE，不能作纯CE横比。五路共同633619参数、fit320组327条/val40、AdamW1e-3/1e-4、batch16组、V22 fit组权重、seed20260816/共同行序，训练前唯一共同25→20降轮，patience6，最早val最佳，无refit。

实际队列392.27秒；训练至统一评价共同墙钟603.25秒。模型、日志、来源和逐条失败完整保存。

本轮只属反复使用开发集的工程筛选，不是新heldout、独立显著确认或原创/真实系统因果证据。 未通过门，停止该组合扩展与系数调节。

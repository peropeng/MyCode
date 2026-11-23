# 第三轮结果与连续执行状态

本轮五条件已完成：C22/32，A21/32，B21/32，AB18/32，AB_loss_only19/32。四缓存AA23、Binary13、SDBL21、StepFinder22，全部32分母保留。预声明门三项均失败，停止该组合，继续下一不同信息路线；RQ1总体目标未完成。

AB准确率56.25%，错误14/32；AA71.875%，AB净少5例、差−15.625个百分点。AB选轮validation31/40，反复使用开发32为18/32，作为开发过拟合警示，不建立独立泛化结论。A角色命中31/32但步骤21/32；aux-only19/32，必须保留该控制，不把A归一化offset或clip耦合当独立加分解释。

训练前公共无GoldRMS使用2300真实same-role/nonexact fit配对、317组324记录，未按Gold筛统计。独立role head929→96→1，B为384维零init无bias互反D比较，全部633619参数；辅助BCE系数1、仅Gold端点，neitherGold不伪标。旧全局memory保留，旧memory A/B输出禁用。经典层次softmax/配对比较不宣称原创或真实系统因果。

五路共同训练前25→20，patience6；AB触及20 cap，选15，其余均早停。CE_loss历史日志字段为总objective，含启用aux；a_score=logits−t只是随t/B变化的层次offset。role概率质量由独立e决定，但joint MAP步骤所属role仍可能变化。

队列392.265秒，训练至评价共同603.247秒。全5 checkpoint/selection先封存，再一次评价已使用的开发32；不是新heldout或独立确认。audit中独立代码审查与保存数据/sha核验PASS，未为归档重复评价。根层continuous_rq1_progress.json为mutable状态，旧protocol/原75资产保持不变。

# P9分支分数尺度融合

本轮使用现成P8特征缓存，A为历史相邻语义差分、B为未来相邻语义差分。每个record的C/A/B原始分数按population variance和固定epsilon `1e-4`做可导标准化，再以fit学习的softplus正权重融合。C/A/B/AB均使用相同C校准，禁用分支head和beta冻结；没有新编码、下载或基线推理。

原fit327（320组）、validation40、已反复使用的development32保持不变。四个fresh条件同seed20260816、AdamW `1e-3`、weight decay `1e-4`、最多20epochs/patience6，以最早validation命中严格提高选checkpoint；全部四个新checkpoint选定封存后才一次读取development32并评价。

北京时间10月4日23:55:19已保存真实比较，早于10月5日00:24硬截止。结果为C18、A18、B17、AB16/32，AB准确率50%；四缓存基线为23/13/21/22。固定增益门槛均未通过，决定 `STOP_FIXED_SCORE_CALIBRATION_SCREEN`。从15:24UTC开始端到端1879.654s；训练、验证、一次评价和保存804.188s/1800s，运行失败0。不宣称充分收敛、独立确认或RQ1完成。

中文直接交付在 `result_summary.txt`；完整比较在 `results/used_development32/comparison.json`。四个条件的原始预测保存raw、z、alpha、effective贡献及最终float32分数，可逐项精确重建；四checkpoint、optimizer/RNG、完整history/selection、标签访问、all4 seal、协议、聚焦源码及实际审查、日志都保留。

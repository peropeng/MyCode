# P10 本地测试观察与未来语义残差

A 聚合原步骤已有 supplied-test 执行观察：检查后模块完成、test-stage AssertionError、到达断言数的 log1p。缺失和未知观察为零。它描述已提供测试的执行事件，不认证任务正确性。原320个fit组等权计算单个RMS尺度，保持所有零行；有效维度3，填充至1024。

B 直接使用 P8 已封存并按fit尺度处理的 deltaFuture1024。C 直接使用 P5 的已有分数：fit为P4 own-C OOF，validation/development为P3 full-fit C。C是缓存对照，A/B/AB是三个新拟合的线性残差头。

沿用P4/P5组加权listwise CE与active L2、原float64 CPU LBFGS。只用327条fit标签拟合；三个头全部封存之后一次评估32条已用开发样本，并在之后提供40条validation的描述统计。不进行validation选参或development调参。

门槛是AB至少25/32且严格超过C/A/B及四个缓存基线，全部头梯度达到既有1e-7阈值。32条样本已在历史轮使用，任何阳性仅是开发筛选，不能宣称独立确认。

研究计时从2026-10-04 16:24UTC开始；16:39为实现冻结目标，17:24为实际结果绝对边界。源准备和协调延迟计入总钟。冻结实际时间及是否达到目标由protocol.json记录；不得重置研究计时。共享三个头拟合预算600秒，冻结run预算1800秒。

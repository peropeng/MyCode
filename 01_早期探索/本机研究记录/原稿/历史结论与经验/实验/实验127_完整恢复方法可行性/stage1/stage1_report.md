# Stage 1：自然中间状态退化资格结果

固定 11 项 moto 轨迹全部执行完成；3 项满足相同原生测试先通过、后失败且保留相关通过测试的资格条件。8 项未观察到符合条件的新退化，无任务因环境或预算阻塞。所有探针均为本轮新运行，不能写作原 Agent 当时的同测试观察。

|任务|结论|失败 call|可见目标数|隐藏保留数|探针数|秒|
|---|---|---:|---:|---:|---:|---:|
|getmoto__moto-5134|qualified|26|1|12|6|23.77|
|getmoto__moto-6355|not_qualified_no_fixed_test_regression_with_preservation|—|0|0|4|28.51|
|getmoto__moto-4972|not_qualified_no_fixed_test_regression_with_preservation|—|0|0|5|49.58|
|getmoto__moto-5286|qualified|14|147|23|4|228.27|
|getmoto__moto-5406|not_qualified_no_fixed_test_regression_with_preservation|—|0|0|5|36.89|
|getmoto__moto-6212|not_qualified_no_fixed_test_regression_with_preservation|—|0|0|6|34.49|
|getmoto__moto-6352|qualified|7|8|81|3|44.96|
|getmoto__moto-6387|not_qualified_no_fixed_test_regression_with_preservation|—|0|0|13|48.71|
|getmoto__moto-7023|not_qualified_no_fixed_test_regression_with_preservation|—|0|0|5|28.85|
|getmoto__moto-7167|not_qualified_no_fixed_test_regression_with_preservation|—|0|0|4|246.80|
|getmoto__moto-7331|not_qualified_no_fixed_test_regression_with_preservation|—|0|0|9|212.32|

5134：固定 null/exists 原生集成测试在 call 16、20、24 后通过，call 26 后退化；本轮恢复该中途已实现功能，不声称原 Issue 全量修复。原日志 call 17→19 的复现脚本已变，因此没有把那一对运行当作相同测试证据。

5286：call 14 引入不存在的项目内模块导入后，多个此前通过的原生用例失败，同时仍有相关原生用例通过。它是实际编辑造成的项目状态问题，不是预先缺失依赖。

6352：call 7 改变调用端、传入 description，而被调用的 SecretsManagerBackend.update_secret 签名尚未同步，属于连续修改之间、离线探针发现的暂时不一致状态。按冻结规则纳入，但不能把它写成原 Agent 已停止的真实失败案例。

三个失败前缀都在触发退化的业务编辑后立即截断，前缀内错误后的后续编辑数为 0。因此它们可检查完整恢复管线，但不足以证明依赖闭包优于简单撤销或减少后续有效编辑损失。

资格阶段只执行真实轨迹的严格文本替换/创建；96 条 shell 命令与相关脚本经过精确审查但没有原样运行。固定外部测试目录由 base 测试加官方 test_patch 构成，仅使用测试补丁，没有读取官方修复补丁。测试前后业务树与冻结测试字节一致。

API 请求 0；A+B 训练与恢复候选在本封存之后执行。LATS 实际模型运行因用户最新 API 暂停要求保持未运行。

前两条资格执行使用 source_versions/first_two_runner.py；其余使用 run_stage1.py。唯一代码差别是将收集阶段的 business_state_unchanged 从记录升级为拒绝条件；前两条实际值也均为 true，无须重跑。

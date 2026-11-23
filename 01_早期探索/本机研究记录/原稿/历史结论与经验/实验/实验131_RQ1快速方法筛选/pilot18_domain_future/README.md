# P18 元数据分区草案：未训练，未进入方法比较

此草案将数据集的 domain 用作未来上下文的分区门控。数值构建保存后，公开输入合同核对发现 domain 仅供报告，并非推断可用输入，因此在训练之前停止。没有读取新 Gold、没有优化步骤、没有模型性能结果。feature_receipt 的数值 PASS 只证明构建完成，不代表符合方法边界。

boundary_rejection.json 保存合同位置、合同 SHA 与停止时点。源代码、尺度、数值回执、精确验证过的特征 ZIP 和 scratch 私有原始缓存均保留用于溯源。后续公开 task 分区使用独立目录 pilot18_task_partition_future_context，并不是将本草案事后改名为有效实验。

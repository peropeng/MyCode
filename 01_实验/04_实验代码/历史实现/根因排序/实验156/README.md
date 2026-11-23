# 实验156历史实现

此处展开可公开源码，保留原字节、英文提示词及内部导入布局。实验编号只用于追溯，不代表正式实验名称。现有结果属于前期可行性测试。

文件用于直接阅读和迁移核对，不应执行旧调度、旧授权或旧截止时钟。已完成终态不追加生成。数据、模型、日志、Checkpoint及未公开评价材料继续保留在完整原件附件中。

## 可直接阅读的文件

- [实验156_固定模型位置角色强对照/common.py](%E5%AE%9E%E9%AA%8C156_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E4%BD%8D%E7%BD%AE%E8%A7%92%E8%89%B2%E5%BC%BA%E5%AF%B9%E7%85%A7/common.py)
- [实验156_固定模型位置角色强对照/diagnostics156.py](%E5%AE%9E%E9%AA%8C156_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E4%BD%8D%E7%BD%AE%E8%A7%92%E8%89%B2%E5%BC%BA%E5%AF%B9%E7%85%A7/diagnostics156.py)
- [实验156_固定模型位置角色强对照/evaluate156.py](%E5%AE%9E%E9%AA%8C156_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E4%BD%8D%E7%BD%AE%E8%A7%92%E8%89%B2%E5%BC%BA%E5%AF%B9%E7%85%A7/evaluate156.py)
- [实验156_固定模型位置角色强对照/finalize156.py](%E5%AE%9E%E9%AA%8C156_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E4%BD%8D%E7%BD%AE%E8%A7%92%E8%89%B2%E5%BC%BA%E5%AF%B9%E7%85%A7/finalize156.py)
- [实验156_固定模型位置角色强对照/launch156.py](%E5%AE%9E%E9%AA%8C156_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E4%BD%8D%E7%BD%AE%E8%A7%92%E8%89%B2%E5%BC%BA%E5%AF%B9%E7%85%A7/launch156.py)
- [实验156_固定模型位置角色强对照/paired_stats156.py](%E5%AE%9E%E9%AA%8C156_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E4%BD%8D%E7%BD%AE%E8%A7%92%E8%89%B2%E5%BC%BA%E5%AF%B9%E7%85%A7/paired_stats156.py)
- [实验156_固定模型位置角色强对照/predict156.py](%E5%AE%9E%E9%AA%8C156_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E4%BD%8D%E7%BD%AE%E8%A7%92%E8%89%B2%E5%BC%BA%E5%AF%B9%E7%85%A7/predict156.py)
- [实验156_固定模型位置角色强对照/prepare156.py](%E5%AE%9E%E9%AA%8C156_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E4%BD%8D%E7%BD%AE%E8%A7%92%E8%89%B2%E5%BC%BA%E5%AF%B9%E7%85%A7/prepare156.py)
- [实验156_固定模型位置角色强对照/rules156.py](%E5%AE%9E%E9%AA%8C156_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E4%BD%8D%E7%BD%AE%E8%A7%92%E8%89%B2%E5%BC%BA%E5%AF%B9%E7%85%A7/rules156.py)
- [实验156_固定模型位置角色强对照/test_rules156.py](%E5%AE%9E%E9%AA%8C156_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E4%BD%8D%E7%BD%AE%E8%A7%92%E8%89%B2%E5%BC%BA%E5%AF%B9%E7%85%A7/test_rules156.py)

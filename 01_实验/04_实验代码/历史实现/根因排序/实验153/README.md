# 实验153历史实现

此处展开可公开源码，保留原字节、英文提示词及内部导入布局。实验编号只用于追溯，不代表正式实验名称。现有结果属于前期可行性测试。

文件用于直接阅读和迁移核对，不应执行旧调度、旧授权或旧截止时钟。已完成终态不追加生成。数据、模型、日志、Checkpoint及未公开评价材料继续保留在完整原件附件中。

## 可直接阅读的文件

- [实验153_候选条件全轨迹上下文/activate_repair153.py](%E5%AE%9E%E9%AA%8C153_%E5%80%99%E9%80%89%E6%9D%A1%E4%BB%B6%E5%85%A8%E8%BD%A8%E8%BF%B9%E4%B8%8A%E4%B8%8B%E6%96%87/activate_repair153.py)
- [实验153_候选条件全轨迹上下文/check_repaired_backend153.py](%E5%AE%9E%E9%AA%8C153_%E5%80%99%E9%80%89%E6%9D%A1%E4%BB%B6%E5%85%A8%E8%BD%A8%E8%BF%B9%E4%B8%8A%E4%B8%8B%E6%96%87/check_repaired_backend153.py)
- [实验153_候选条件全轨迹上下文/common.py](%E5%AE%9E%E9%AA%8C153_%E5%80%99%E9%80%89%E6%9D%A1%E4%BB%B6%E5%85%A8%E8%BD%A8%E8%BF%B9%E4%B8%8A%E4%B8%8B%E6%96%87/common.py)
- [实验153_候选条件全轨迹上下文/context_models.py](%E5%AE%9E%E9%AA%8C153_%E5%80%99%E9%80%89%E6%9D%A1%E4%BB%B6%E5%85%A8%E8%BD%A8%E8%BF%B9%E4%B8%8A%E4%B8%8B%E6%96%87/context_models.py)
- [实验153_候选条件全轨迹上下文/data153.py](%E5%AE%9E%E9%AA%8C153_%E5%80%99%E9%80%89%E6%9D%A1%E4%BB%B6%E5%85%A8%E8%BD%A8%E8%BF%B9%E4%B8%8A%E4%B8%8B%E6%96%87/data153.py)
- [实验153_候选条件全轨迹上下文/evaluate153.py](%E5%AE%9E%E9%AA%8C153_%E5%80%99%E9%80%89%E6%9D%A1%E4%BB%B6%E5%85%A8%E8%BD%A8%E8%BF%B9%E4%B8%8A%E4%B8%8B%E6%96%87/evaluate153.py)
- [实验153_候选条件全轨迹上下文/finalize153.py](%E5%AE%9E%E9%AA%8C153_%E5%80%99%E9%80%89%E6%9D%A1%E4%BB%B6%E5%85%A8%E8%BD%A8%E8%BF%B9%E4%B8%8A%E4%B8%8B%E6%96%87/finalize153.py)
- [实验153_候选条件全轨迹上下文/fixture_context153.py](%E5%AE%9E%E9%AA%8C153_%E5%80%99%E9%80%89%E6%9D%A1%E4%BB%B6%E5%85%A8%E8%BD%A8%E8%BF%B9%E4%B8%8A%E4%B8%8B%E6%96%87/fixture_context153.py)
- [实验153_候选条件全轨迹上下文/launch153.py](%E5%AE%9E%E9%AA%8C153_%E5%80%99%E9%80%89%E6%9D%A1%E4%BB%B6%E5%85%A8%E8%BD%A8%E8%BF%B9%E4%B8%8A%E4%B8%8B%E6%96%87/launch153.py)
- [实验153_候选条件全轨迹上下文/paired_stats153.py](%E5%AE%9E%E9%AA%8C153_%E5%80%99%E9%80%89%E6%9D%A1%E4%BB%B6%E5%85%A8%E8%BD%A8%E8%BF%B9%E4%B8%8A%E4%B8%8B%E6%96%87/paired_stats153.py)
- [实验153_候选条件全轨迹上下文/predict153.py](%E5%AE%9E%E9%AA%8C153_%E5%80%99%E9%80%89%E6%9D%A1%E4%BB%B6%E5%85%A8%E8%BD%A8%E8%BF%B9%E4%B8%8A%E4%B8%8B%E6%96%87/predict153.py)
- [实验153_候选条件全轨迹上下文/record_runtime_failure.py](%E5%AE%9E%E9%AA%8C153_%E5%80%99%E9%80%89%E6%9D%A1%E4%BB%B6%E5%85%A8%E8%BD%A8%E8%BF%B9%E4%B8%8A%E4%B8%8B%E6%96%87/record_runtime_failure.py)
- [实验153_候选条件全轨迹上下文/test_context153.py](%E5%AE%9E%E9%AA%8C153_%E5%80%99%E9%80%89%E6%9D%A1%E4%BB%B6%E5%85%A8%E8%BD%A8%E8%BF%B9%E4%B8%8A%E4%B8%8B%E6%96%87/test_context153.py)
- [实验153_候选条件全轨迹上下文/trainer153.py](%E5%AE%9E%E9%AA%8C153_%E5%80%99%E9%80%89%E6%9D%A1%E4%BB%B6%E5%85%A8%E8%BD%A8%E8%BF%B9%E4%B8%8A%E4%B8%8B%E6%96%87/trainer153.py)
- [实验153_候选条件全轨迹上下文/sources/original_models.py](%E5%AE%9E%E9%AA%8C153_%E5%80%99%E9%80%89%E6%9D%A1%E4%BB%B6%E5%85%A8%E8%BD%A8%E8%BF%B9%E4%B8%8A%E4%B8%8B%E6%96%87/sources/original_models.py)
- [实验153_候选条件全轨迹上下文/sources/owned_exp130_model.py](%E5%AE%9E%E9%AA%8C153_%E5%80%99%E9%80%89%E6%9D%A1%E4%BB%B6%E5%85%A8%E8%BD%A8%E8%BF%B9%E4%B8%8A%E4%B8%8B%E6%96%87/sources/owned_exp130_model.py)

## 继续保留在原件或上游的条目

- `stepfinder_model.py`：原作者源码使用官方固定来源获取，不在本研究目录重托管。

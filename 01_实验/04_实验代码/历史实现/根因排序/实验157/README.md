# 实验157历史实现

此处展开可公开源码，保留原字节、英文提示词及内部导入布局。实验编号只用于追溯，不代表正式实验名称。现有结果属于前期可行性测试。

文件用于直接阅读和迁移核对，不应执行旧调度、旧授权或旧截止时钟。已完成终态不追加生成。数据、模型、日志、Checkpoint及未公开评价材料继续保留在完整原件附件中。

## 可直接阅读的文件

- [实验157_固定模型数据划分敏感性/common.py](%E5%AE%9E%E9%AA%8C157_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E6%95%B0%E6%8D%AE%E5%88%92%E5%88%86%E6%95%8F%E6%84%9F%E6%80%A7/common.py)
- [实验157_固定模型数据划分敏感性/context_base.py](%E5%AE%9E%E9%AA%8C157_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E6%95%B0%E6%8D%AE%E5%88%92%E5%88%86%E6%95%8F%E6%84%9F%E6%80%A7/context_base.py)
- [实验157_固定模型数据划分敏感性/data157.py](%E5%AE%9E%E9%AA%8C157_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E6%95%B0%E6%8D%AE%E5%88%92%E5%88%86%E6%95%8F%E6%84%9F%E6%80%A7/data157.py)
- [实验157_固定模型数据划分敏感性/evaluate157.py](%E5%AE%9E%E9%AA%8C157_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E6%95%B0%E6%8D%AE%E5%88%92%E5%88%86%E6%95%8F%E6%84%9F%E6%80%A7/evaluate157.py)
- [实验157_固定模型数据划分敏感性/finalize157.py](%E5%AE%9E%E9%AA%8C157_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E6%95%B0%E6%8D%AE%E5%88%92%E5%88%86%E6%95%8F%E6%84%9F%E6%80%A7/finalize157.py)
- [实验157_固定模型数据划分敏感性/launch157.py](%E5%AE%9E%E9%AA%8C157_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E6%95%B0%E6%8D%AE%E5%88%92%E5%88%86%E6%95%8F%E6%84%9F%E6%80%A7/launch157.py)
- [实验157_固定模型数据划分敏感性/models157.py](%E5%AE%9E%E9%AA%8C157_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E6%95%B0%E6%8D%AE%E5%88%92%E5%88%86%E6%95%8F%E6%84%9F%E6%80%A7/models157.py)
- [实验157_固定模型数据划分敏感性/paired_stats157.py](%E5%AE%9E%E9%AA%8C157_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E6%95%B0%E6%8D%AE%E5%88%92%E5%88%86%E6%95%8F%E6%84%9F%E6%80%A7/paired_stats157.py)
- [实验157_固定模型数据划分敏感性/predict157.py](%E5%AE%9E%E9%AA%8C157_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E6%95%B0%E6%8D%AE%E5%88%92%E5%88%86%E6%95%8F%E6%84%9F%E6%80%A7/predict157.py)
- [实验157_固定模型数据划分敏感性/prepare157.py](%E5%AE%9E%E9%AA%8C157_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E6%95%B0%E6%8D%AE%E5%88%92%E5%88%86%E6%95%8F%E6%84%9F%E6%80%A7/prepare157.py)
- [实验157_固定模型数据划分敏感性/test_splits157.py](%E5%AE%9E%E9%AA%8C157_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E6%95%B0%E6%8D%AE%E5%88%92%E5%88%86%E6%95%8F%E6%84%9F%E6%80%A7/test_splits157.py)
- [实验157_固定模型数据划分敏感性/trainer157.py](%E5%AE%9E%E9%AA%8C157_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E6%95%B0%E6%8D%AE%E5%88%92%E5%88%86%E6%95%8F%E6%84%9F%E6%80%A7/trainer157.py)
- [实验157_固定模型数据划分敏感性/sources/original_models.py](%E5%AE%9E%E9%AA%8C157_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E6%95%B0%E6%8D%AE%E5%88%92%E5%88%86%E6%95%8F%E6%84%9F%E6%80%A7/sources/original_models.py)
- [实验157_固定模型数据划分敏感性/sources/owned_exp130_model.py](%E5%AE%9E%E9%AA%8C157_%E5%9B%BA%E5%AE%9A%E6%A8%A1%E5%9E%8B%E6%95%B0%E6%8D%AE%E5%88%92%E5%88%86%E6%95%8F%E6%84%9F%E6%80%A7/sources/owned_exp130_model.py)

## 继续保留在原件或上游的条目

- `stepfinder_model.py`：原作者源码使用官方固定来源获取，不在本研究目录重托管。

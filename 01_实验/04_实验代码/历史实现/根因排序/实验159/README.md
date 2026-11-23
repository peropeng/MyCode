# 实验159历史实现

此处展开可公开源码，保留原字节、英文提示词及内部导入布局。实验编号只用于追溯，不代表正式实验名称。现有结果属于前期可行性测试。

文件用于直接阅读和迁移核对，不应执行旧调度、旧授权或旧截止时钟。已完成终态不追加生成。数据、模型、日志、Checkpoint及未公开评价材料继续保留在完整原件附件中。

## 可直接阅读的文件

- [实验159_论文强基线跨划分复验/common.py](%E5%AE%9E%E9%AA%8C159_%E8%AE%BA%E6%96%87%E5%BC%BA%E5%9F%BA%E7%BA%BF%E8%B7%A8%E5%88%92%E5%88%86%E5%A4%8D%E9%AA%8C/common.py)
- [实验159_论文强基线跨划分复验/context_base.py](%E5%AE%9E%E9%AA%8C159_%E8%AE%BA%E6%96%87%E5%BC%BA%E5%9F%BA%E7%BA%BF%E8%B7%A8%E5%88%92%E5%88%86%E5%A4%8D%E9%AA%8C/context_base.py)
- [实验159_论文强基线跨划分复验/data159.py](%E5%AE%9E%E9%AA%8C159_%E8%AE%BA%E6%96%87%E5%BC%BA%E5%9F%BA%E7%BA%BF%E8%B7%A8%E5%88%92%E5%88%86%E5%A4%8D%E9%AA%8C/data159.py)
- [实验159_论文强基线跨划分复验/evaluate159.py](%E5%AE%9E%E9%AA%8C159_%E8%AE%BA%E6%96%87%E5%BC%BA%E5%9F%BA%E7%BA%BF%E8%B7%A8%E5%88%92%E5%88%86%E5%A4%8D%E9%AA%8C/evaluate159.py)
- [实验159_论文强基线跨划分复验/finalize159.py](%E5%AE%9E%E9%AA%8C159_%E8%AE%BA%E6%96%87%E5%BC%BA%E5%9F%BA%E7%BA%BF%E8%B7%A8%E5%88%92%E5%88%86%E5%A4%8D%E9%AA%8C/finalize159.py)
- [实验159_论文强基线跨划分复验/launch159.py](%E5%AE%9E%E9%AA%8C159_%E8%AE%BA%E6%96%87%E5%BC%BA%E5%9F%BA%E7%BA%BF%E8%B7%A8%E5%88%92%E5%88%86%E5%A4%8D%E9%AA%8C/launch159.py)
- [实验159_论文强基线跨划分复验/models159.py](%E5%AE%9E%E9%AA%8C159_%E8%AE%BA%E6%96%87%E5%BC%BA%E5%9F%BA%E7%BA%BF%E8%B7%A8%E5%88%92%E5%88%86%E5%A4%8D%E9%AA%8C/models159.py)
- [实验159_论文强基线跨划分复验/paired_stats159.py](%E5%AE%9E%E9%AA%8C159_%E8%AE%BA%E6%96%87%E5%BC%BA%E5%9F%BA%E7%BA%BF%E8%B7%A8%E5%88%92%E5%88%86%E5%A4%8D%E9%AA%8C/paired_stats159.py)
- [实验159_论文强基线跨划分复验/predict159.py](%E5%AE%9E%E9%AA%8C159_%E8%AE%BA%E6%96%87%E5%BC%BA%E5%9F%BA%E7%BA%BF%E8%B7%A8%E5%88%92%E5%88%86%E5%A4%8D%E9%AA%8C/predict159.py)
- [实验159_论文强基线跨划分复验/predict159_runtime_entry.py](%E5%AE%9E%E9%AA%8C159_%E8%AE%BA%E6%96%87%E5%BC%BA%E5%9F%BA%E7%BA%BF%E8%B7%A8%E5%88%92%E5%88%86%E5%A4%8D%E9%AA%8C/predict159_runtime_entry.py)
- [实验159_论文强基线跨划分复验/prepare159.py](%E5%AE%9E%E9%AA%8C159_%E8%AE%BA%E6%96%87%E5%BC%BA%E5%9F%BA%E7%BA%BF%E8%B7%A8%E5%88%92%E5%88%86%E5%A4%8D%E9%AA%8C/prepare159.py)
- [实验159_论文强基线跨划分复验/select159.py](%E5%AE%9E%E9%AA%8C159_%E8%AE%BA%E6%96%87%E5%BC%BA%E5%9F%BA%E7%BA%BF%E8%B7%A8%E5%88%92%E5%88%86%E5%A4%8D%E9%AA%8C/select159.py)
- [实验159_论文强基线跨划分复验/trainer159.py](%E5%AE%9E%E9%AA%8C159_%E8%AE%BA%E6%96%87%E5%BC%BA%E5%9F%BA%E7%BA%BF%E8%B7%A8%E5%88%92%E5%88%86%E5%A4%8D%E9%AA%8C/trainer159.py)
- [实验159_论文强基线跨划分复验/sources/original_models.py](%E5%AE%9E%E9%AA%8C159_%E8%AE%BA%E6%96%87%E5%BC%BA%E5%9F%BA%E7%BA%BF%E8%B7%A8%E5%88%92%E5%88%86%E5%A4%8D%E9%AA%8C/sources/original_models.py)
- [实验159_论文强基线跨划分复验/sources/owned_exp130_model.py](%E5%AE%9E%E9%AA%8C159_%E8%AE%BA%E6%96%87%E5%BC%BA%E5%9F%BA%E7%BA%BF%E8%B7%A8%E5%88%92%E5%88%86%E5%A4%8D%E9%AA%8C/sources/owned_exp130_model.py)

## 继续保留在原件或上游的条目

- `stepfinder_model.py`：原作者源码使用官方固定来源获取，不在本研究目录重托管。

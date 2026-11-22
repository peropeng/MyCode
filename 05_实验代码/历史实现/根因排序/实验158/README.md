# 实验158历史实现

此处展开可公开源码，保留原字节、英文提示词及内部导入布局。实验编号只用于追溯，不代表正式实验名称。现有结果属于前期可行性测试。

文件用于直接阅读和迁移核对，不应执行旧调度、旧授权或旧截止时钟。已完成终态不追加生成。数据、模型、日志、Checkpoint及未公开评价材料继续保留在完整原件附件中。

## 可直接阅读的文件

- [实验158_StepFinder论文双预设强对照/common.py](实验158_StepFinder论文双预设强对照/common.py)
- [实验158_StepFinder论文双预设强对照/context_base.py](实验158_StepFinder论文双预设强对照/context_base.py)
- [实验158_StepFinder论文双预设强对照/data158.py](实验158_StepFinder论文双预设强对照/data158.py)
- [实验158_StepFinder论文双预设强对照/evaluate158.py](实验158_StepFinder论文双预设强对照/evaluate158.py)
- [实验158_StepFinder论文双预设强对照/finalize158.py](实验158_StepFinder论文双预设强对照/finalize158.py)
- [实验158_StepFinder论文双预设强对照/launch158.py](实验158_StepFinder论文双预设强对照/launch158.py)
- [实验158_StepFinder论文双预设强对照/models158.py](实验158_StepFinder论文双预设强对照/models158.py)
- [实验158_StepFinder论文双预设强对照/paired_stats158.py](实验158_StepFinder论文双预设强对照/paired_stats158.py)
- [实验158_StepFinder论文双预设强对照/predict158.py](实验158_StepFinder论文双预设强对照/predict158.py)
- [实验158_StepFinder论文双预设强对照/prepare158.py](实验158_StepFinder论文双预设强对照/prepare158.py)
- [实验158_StepFinder论文双预设强对照/select158.py](实验158_StepFinder论文双预设强对照/select158.py)
- [实验158_StepFinder论文双预设强对照/test_presets158.py](实验158_StepFinder论文双预设强对照/test_presets158.py)
- [实验158_StepFinder论文双预设强对照/trainer158.py](实验158_StepFinder论文双预设强对照/trainer158.py)
- [实验158_StepFinder论文双预设强对照/sources/original_models.py](实验158_StepFinder论文双预设强对照/sources/original_models.py)
- [实验158_StepFinder论文双预设强对照/sources/owned_exp130_model.py](实验158_StepFinder论文双预设强对照/sources/owned_exp130_model.py)

## 继续保留在原件或上游的条目

- `stepfinder_model.py`：原作者源码使用官方固定来源获取，不在本研究目录重托管。

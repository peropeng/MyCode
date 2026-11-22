# 实验134历史实现

此处展开可公开源码，保留原字节、英文提示词及内部导入布局。实验编号只用于追溯，不代表正式实验名称。现有结果属于前期可行性测试。

文件用于直接阅读和迁移核对，不应执行旧调度、旧授权或旧截止时钟。已完成终态不追加生成。数据、模型、日志、Checkpoint及未公开评价材料继续保留在完整原件附件中。

## 可直接阅读的文件

- [实验134_状态动作表示与关系排序/check_engineering.py](实验134_状态动作表示与关系排序/check_engineering.py)
- [实验134_状态动作表示与关系排序/common.py](实验134_状态动作表示与关系排序/common.py)
- [实验134_状态动作表示与关系排序/evaluate_development.py](实验134_状态动作表示与关系排序/evaluate_development.py)
- [实验134_状态动作表示与关系排序/finalize_local_stage.py](实验134_状态动作表示与关系排序/finalize_local_stage.py)
- [实验134_状态动作表示与关系排序/models.py](实验134_状态动作表示与关系排序/models.py)
- [实验134_状态动作表示与关系排序/prepare_data.py](实验134_状态动作表示与关系排序/prepare_data.py)
- [实验134_状态动作表示与关系排序/prepare_features.py](实验134_状态动作表示与关系排序/prepare_features.py)
- [实验134_状态动作表示与关系排序/train.py](实验134_状态动作表示与关系排序/train.py)
- [实验134_状态动作表示与关系排序/confirmation/check_contract.py](实验134_状态动作表示与关系排序/confirmation/check_contract.py)
- [实验134_状态动作表示与关系排序/confirmation/freeze_protocol.py](实验134_状态动作表示与关系排序/confirmation/freeze_protocol.py)
- [实验134_状态动作表示与关系排序/confirmation/paid_methods.py](实验134_状态动作表示与关系排序/confirmation/paid_methods.py)
- [实验134_状态动作表示与关系排序/confirmation/paired_statistics_reference.py](实验134_状态动作表示与关系排序/confirmation/paired_statistics_reference.py)
- [实验134_状态动作表示与关系排序/confirmation/paired_stats.py](实验134_状态动作表示与关系排序/confirmation/paired_stats.py)
- [实验134_状态动作表示与关系排序/confirmation/predict_local.py](实验134_状态动作表示与关系排序/confirmation/predict_local.py)
- [实验134_状态动作表示与关系排序/confirmation/resume_budget_0320.py](实验134_状态动作表示与关系排序/confirmation/resume_budget_0320.py)
- [实验134_状态动作表示与关系排序/confirmation/run_paid.py](实验134_状态动作表示与关系排序/confirmation/run_paid.py)
- [实验134_状态动作表示与关系排序/confirmation/score_fresh.py](实验134_状态动作表示与关系排序/confirmation/score_fresh.py)
- [实验134_状态动作表示与关系排序/confirmation/select_public.py](实验134_状态动作表示与关系排序/confirmation/select_public.py)
- [实验134_状态动作表示与关系排序/confirmation/shared.py](实验134_状态动作表示与关系排序/confirmation/shared.py)
- [实验134_状态动作表示与关系排序/sources/model_adapters.py](实验134_状态动作表示与关系排序/sources/model_adapters.py)
- [实验134_状态动作表示与关系排序/sources/owned_exp130_model.py](实验134_状态动作表示与关系排序/sources/owned_exp130_model.py)
- [实验134_状态动作表示与关系排序/sources/prepare_features_before_length_batching.py](实验134_状态动作表示与关系排序/sources/prepare_features_before_length_batching.py)

## 继续保留在原件或上游的条目

- `stepfinder_model.py`：原作者源码使用官方固定来源获取，不在本研究目录重托管。

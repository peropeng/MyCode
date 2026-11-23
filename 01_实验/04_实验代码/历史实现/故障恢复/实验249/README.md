# 实验249历史实现

此处展开可公开源码，保留原字节、英文提示词及内部导入布局。实验编号只用于追溯，不代表正式实验名称。现有结果属于前期可行性测试。

文件用于直接阅读和迁移核对，不应执行旧调度、旧授权或旧截止时钟。已完成终态不追加生成。数据、模型、日志、Checkpoint及未公开评价材料继续保留在完整原件附件中。

## 可直接阅读的文件

- [实验249_固定顺序新任务共同确认/common249.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/common249.py)
- [实验249_固定顺序新任务共同确认/common249_ROOT_BATCH2.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/common249_ROOT_BATCH2.py)
- [实验249_固定顺序新任务共同确认/common249_ROOT_BATCH3.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/common249_ROOT_BATCH3.py)
- [实验249_固定顺序新任务共同确认/materialize249_ROOT_BATCH2.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/materialize249_ROOT_BATCH2.py)
- [实验249_固定顺序新任务共同确认/materialize249_ROOT_BATCH2_R2.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/materialize249_ROOT_BATCH2_R2.py)
- [实验249_固定顺序新任务共同确认/materialize249_ROOT_BATCH3.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/materialize249_ROOT_BATCH3.py)
- [实验249_固定顺序新任务共同确认/materialize249_ROOT_MASK_V2.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/materialize249_ROOT_MASK_V2.py)
- [实验249_固定顺序新任务共同确认/native249.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/native249.py)
- [实验249_固定顺序新任务共同确认/native249_ROOT_BATCH2.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/native249_ROOT_BATCH2.py)
- [实验249_固定顺序新任务共同确认/native249_ROOT_BATCH2_R2.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/native249_ROOT_BATCH2_R2.py)
- [实验249_固定顺序新任务共同确认/native249_ROOT_BATCH3.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/native249_ROOT_BATCH3.py)
- [实验249_固定顺序新任务共同确认/native249_ROOT_BATCH3_R2.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/native249_ROOT_BATCH3_R2.py)
- [实验249_固定顺序新任务共同确认/native249_ROOT_MASK_V2.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/native249_ROOT_MASK_V2.py)
- [实验249_固定顺序新任务共同确认/native249_ROOT_MASK_V3_CAPACITY.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/native249_ROOT_MASK_V3_CAPACITY.py)
- [实验249_固定顺序新任务共同确认/native249_ROOT_PUBLIC_CHANNEL_V4.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/native249_ROOT_PUBLIC_CHANNEL_V4.py)
- [实验249_固定顺序新任务共同确认/native_capacity249_ROOT_V11_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/native_capacity249_ROOT_V11_SOURCE.py)
- [实验249_固定顺序新任务共同确认/physical_identity249.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/physical_identity249.py)
- [实验249_固定顺序新任务共同确认/prepare249_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/prepare249_SOURCE.py)
- [实验249_固定顺序新任务共同确认/batch2_SOURCE_preparation/prepare_batch2_grants_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/batch2_SOURCE_preparation/prepare_batch2_grants_SOURCE.py)
- [实验249_固定顺序新任务共同确认/batch3_SOURCE_preparation/prepare_batch3_grants_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/batch3_SOURCE_preparation/prepare_batch3_grants_SOURCE.py)
- [实验249_固定顺序新任务共同确认/last_nine_qualification_SOURCE/audit_public_mask_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/last_nine_qualification_SOURCE/audit_public_mask_SOURCE.py)
- [实验249_固定顺序新任务共同确认/last_nine_qualification_SOURCE/common_last_nine249.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/last_nine_qualification_SOURCE/common_last_nine249.py)
- [实验249_固定顺序新任务共同确认/last_nine_qualification_SOURCE/native_capacity249_ROOT_V11_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/last_nine_qualification_SOURCE/native_capacity249_ROOT_V11_SOURCE.py)
- [实验249_固定顺序新任务共同确认/last_nine_qualification_SOURCE/native_last_nine249.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/last_nine_qualification_SOURCE/native_last_nine249.py)
- [实验249_固定顺序新任务共同确认/last_nine_qualification_SOURCE/physical_identity249.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/last_nine_qualification_SOURCE/physical_identity249.py)
- [实验249_固定顺序新任务共同确认/last_nine_qualification_SOURCE/prepare_last_nine_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/last_nine_qualification_SOURCE/prepare_last_nine_SOURCE.py)
- [实验249_固定顺序新任务共同确认/last_nine_qualification_SOURCE/windows_native_cwd.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/last_nine_qualification_SOURCE/windows_native_cwd.py)
- [实验249_固定顺序新任务共同确认/method_sources/audit_current_decorators249_READONLY.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/method_sources/audit_current_decorators249_READONLY.py)
- [实验249_固定顺序新任务共同确认/method_sources/common_C0_export249_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/method_sources/common_C0_export249_SOURCE.py)
- [实验249_固定顺序新任务共同确认/method_sources/dispatch_one249.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/method_sources/dispatch_one249.py)
- [实验249_固定顺序新任务共同确认/method_sources/ours_candidate_native249.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/method_sources/ours_candidate_native249.py)
- [实验249_固定顺序新任务共同确认/method_sources/ours_entry249.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/method_sources/ours_entry249.py)
- [实验249_固定顺序新任务共同确认/method_sources/ours_launcher249.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/method_sources/ours_launcher249.py)
- [实验249_固定顺序新任务共同确认/method_sources/prepare_agentless249_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/method_sources/prepare_agentless249_SOURCE.py)
- [实验249_固定顺序新任务共同确认/method_sources/prepare_candidate_grant249_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/method_sources/prepare_candidate_grant249_SOURCE.py)
- [实验249_固定顺序新任务共同确认/method_sources/prepare_final249_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/method_sources/prepare_final249_SOURCE.py)
- [实验249_固定顺序新任务共同确认/method_sources/prepare_model_grant249_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/method_sources/prepare_model_grant249_SOURCE.py)
- [实验249_固定顺序新任务共同确认/method_sources/prepare_ours_repeats249_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/method_sources/prepare_ours_repeats249_SOURCE.py)
- [实验249_固定顺序新任务共同确认/method_sources/seal_final249_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/method_sources/seal_final249_SOURCE.py)
- [实验249_固定顺序新任务共同确认/method_sources/seal_ours249_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/method_sources/seal_ours249_SOURCE.py)
- [实验249_固定顺序新任务共同确认/method_sources/shared_input249.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/method_sources/shared_input249.py)
- [实验249_固定顺序新任务共同确认/method_sources/shared_public249.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/method_sources/shared_public249.py)
- [实验249_固定顺序新任务共同确认/method_sources/trial_runtime249.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/method_sources/trial_runtime249.py)
- [实验249_固定顺序新任务共同确认/method_sources/agentless_core/agentless178.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/method_sources/agentless_core/agentless178.py)
- [实验249_固定顺序新任务共同确认/method_sources/agentless_core/normalization_adapter_v3_241.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/method_sources/agentless_core/normalization_adapter_v3_241.py)
- [实验249_固定顺序新任务共同确认/next_six_current_C0_SOURCE/audit_public_mask_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/next_six_current_C0_SOURCE/audit_public_mask_SOURCE.py)
- [实验249_固定顺序新任务共同确认/next_six_current_C0_SOURCE/bind_after_mask_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/next_six_current_C0_SOURCE/bind_after_mask_SOURCE.py)
- [实验249_固定顺序新任务共同确认/next_six_current_C0_SOURCE/common_current_C0.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/next_six_current_C0_SOURCE/common_current_C0.py)
- [实验249_固定顺序新任务共同确认/next_six_current_C0_SOURCE/native_capacity249_ROOT_V11_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/next_six_current_C0_SOURCE/native_capacity249_ROOT_V11_SOURCE.py)
- [实验249_固定顺序新任务共同确认/next_six_current_C0_SOURCE/native_current_C0.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/next_six_current_C0_SOURCE/native_current_C0.py)
- [实验249_固定顺序新任务共同确认/next_six_current_C0_SOURCE/physical_identity249.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/next_six_current_C0_SOURCE/physical_identity249.py)
- [实验249_固定顺序新任务共同确认/next_six_current_C0_SOURCE/prepare_current_C0_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/next_six_current_C0_SOURCE/prepare_current_C0_SOURCE.py)
- [实验249_固定顺序新任务共同确认/next_six_current_C0_SOURCE/validate_current_C0_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/next_six_current_C0_SOURCE/validate_current_C0_SOURCE.py)
- [实验249_固定顺序新任务共同确认/next_six_qualification_SOURCE/common_next_six249.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/next_six_qualification_SOURCE/common_next_six249.py)
- [实验249_固定顺序新任务共同确认/next_six_qualification_SOURCE/native_next_six249.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/next_six_qualification_SOURCE/native_next_six249.py)
- [实验249_固定顺序新任务共同确认/next_six_qualification_SOURCE/physical_identity249.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/next_six_qualification_SOURCE/physical_identity249.py)
- [实验249_固定顺序新任务共同确认/next_six_qualification_SOURCE/prepare_next_six_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/next_six_qualification_SOURCE/prepare_next_six_SOURCE.py)
- [实验249_固定顺序新任务共同确认/next_six_qualification_SOURCE/validate_next_six_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/next_six_qualification_SOURCE/validate_next_six_SOURCE.py)
- [实验249_固定顺序新任务共同确认/next_six_registry_SOURCE/prepare_registry_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/next_six_registry_SOURCE/prepare_registry_SOURCE.py)
- [实验249_固定顺序新任务共同确认/next_six_registry_SOURCE/qualification_registry_common_SOURCE.py](%E5%AE%9E%E9%AA%8C249_%E5%9B%BA%E5%AE%9A%E9%A1%BA%E5%BA%8F%E6%96%B0%E4%BB%BB%E5%8A%A1%E5%85%B1%E5%90%8C%E7%A1%AE%E8%AE%A4/next_six_registry_SOURCE/qualification_registry_common_SOURCE.py)

## 继续保留在原件或上游的条目

- `materialize249_ROOT_ONLY.py`：私有评价或账户信息相关入口，待逐项公开核定。
- `bind_current_C0_after_gates_ROOT_ONLY.py`：私有评价或账户信息相关入口，待逐项公开核定。
- `materialize_last_nine_ROOT_ONLY.py`：私有评价或账户信息相关入口，待逐项公开核定。
- `final249_ROOT_ONLY.py`：私有评价或账户信息相关入口，待逐项公开核定。
- `materialize_current_C0_ROOT_ONLY.py`：私有评价或账户信息相关入口，待逐项公开核定。
- `generate_next_six_registry_ROOT_ONLY_SOURCE.py`：私有评价或账户信息相关入口，待逐项公开核定。

# 实验251历史实现

此处展开可公开源码，保留原字节、英文提示词及内部导入布局。实验编号只用于追溯，不代表正式实验名称。现有结果属于前期可行性测试。

文件用于直接阅读和迁移核对，不应执行旧调度、旧授权或旧截止时钟。已完成终态不追加生成。数据、模型、日志、Checkpoint及未公开评价材料继续保留在完整原件附件中。

## 可直接阅读的文件

- [实验251_Agentless完整参数新任务共同确认/copy_sources251_SOURCE.py](实验251_Agentless完整参数新任务共同确认/copy_sources251_SOURCE.py)
- [实验251_Agentless完整参数新任务共同确认/deliver251_SOURCE.py](实验251_Agentless完整参数新任务共同确认/deliver251_SOURCE.py)
- [实验251_Agentless完整参数新任务共同确认/dense_preparation_plan251_SOURCE.py](实验251_Agentless完整参数新任务共同确认/dense_preparation_plan251_SOURCE.py)
- [实验251_Agentless完整参数新任务共同确认/derive_boundary_sources251_SOURCE.py](实验251_Agentless完整参数新任务共同确认/derive_boundary_sources251_SOURCE.py)
- [实验251_Agentless完整参数新任务共同确认/entry251.py](实验251_Agentless完整参数新任务共同确认/entry251.py)
- [实验251_Agentless完整参数新任务共同确认/freeze_final251_SOURCE.py](实验251_Agentless完整参数新任务共同确认/freeze_final251_SOURCE.py)
- [实验251_Agentless完整参数新任务共同确认/prepare251_SOURCE.py](实验251_Agentless完整参数新任务共同确认/prepare251_SOURCE.py)
- [实验251_Agentless完整参数新任务共同确认/prepare_false_grants251_SOURCE.py](实验251_Agentless完整参数新任务共同确认/prepare_false_grants251_SOURCE.py)
- [实验251_Agentless完整参数新任务共同确认/public_body251.py](实验251_Agentless完整参数新任务共同确认/public_body251.py)
- [实验251_Agentless完整参数新任务共同确认/runtime251.py](实验251_Agentless完整参数新任务共同确认/runtime251.py)
- [实验251_Agentless完整参数新任务共同确认/validate251_SOURCE.py](实验251_Agentless完整参数新任务共同确认/validate251_SOURCE.py)
- [实验251_Agentless完整参数新任务共同确认/agentless_core/agentless178.py](实验251_Agentless完整参数新任务共同确认/agentless_core/agentless178.py)
- [实验251_Agentless完整参数新任务共同确认/agentless_core/normalization_adapter_v3_241.py](实验251_Agentless完整参数新任务共同确认/agentless_core/normalization_adapter_v3_241.py)
- [实验251_Agentless完整参数新任务共同确认/agentless_core/retrieval178.py](实验251_Agentless完整参数新任务共同确认/agentless_core/retrieval178.py)
- [实验251_Agentless完整参数新任务共同确认/native_core/contracts241.py](实验251_Agentless完整参数新任务共同确认/native_core/contracts241.py)
- [实验251_Agentless完整参数新任务共同确认/native_core/generated_scope_v2_241.py](实验251_Agentless完整参数新任务共同确认/native_core/generated_scope_v2_241.py)
- [实验251_Agentless完整参数新任务共同确认/native_core/guarded_reproduction_invalid_SOURCE.py](实验251_Agentless完整参数新任务共同确认/native_core/guarded_reproduction_invalid_SOURCE.py)
- [实验251_Agentless完整参数新任务共同确认/native_core/product_entry241.py](实验251_Agentless完整参数新任务共同确认/native_core/product_entry241.py)
- [实验251_Agentless完整参数新任务共同确认/native_core/supervision_classification241.py](实验251_Agentless完整参数新任务共同确认/native_core/supervision_classification241.py)
- [实验251_Agentless完整参数新任务共同确认/native_core/winjob241.py](实验251_Agentless完整参数新任务共同确认/native_core/winjob241.py)
- [实验251_Agentless完整参数新任务共同确认/runner_R2_SOURCE/controller_executor251_R2.py](实验251_Agentless完整参数新任务共同确认/runner_R2_SOURCE/controller_executor251_R2.py)
- [实验251_Agentless完整参数新任务共同确认/runner_R2_SOURCE/mechanical_nested_Job251_R2.py](实验251_Agentless完整参数新任务共同确认/runner_R2_SOURCE/mechanical_nested_Job251_R2.py)
- [实验251_Agentless完整参数新任务共同确认/runner_R2_SOURCE/prepare_runner251_SOURCE.py](实验251_Agentless完整参数新任务共同确认/runner_R2_SOURCE/prepare_runner251_SOURCE.py)
- [实验251_Agentless完整参数新任务共同确认/runner_R2_SOURCE/runner251.py](实验251_Agentless完整参数新任务共同确认/runner_R2_SOURCE/runner251.py)
- [实验251_Agentless完整参数新任务共同确认/runner_R2_SOURCE/validate_runner251_SOURCE.py](实验251_Agentless完整参数新任务共同确认/runner_R2_SOURCE/validate_runner251_SOURCE.py)
- [实验251_Agentless完整参数新任务共同确认/runner_SOURCE/prepare_runner251_SOURCE.py](实验251_Agentless完整参数新任务共同确认/runner_SOURCE/prepare_runner251_SOURCE.py)
- [实验251_Agentless完整参数新任务共同确认/runner_SOURCE/runner251.py](实验251_Agentless完整参数新任务共同确认/runner_SOURCE/runner251.py)
- [实验251_Agentless完整参数新任务共同确认/runner_SOURCE/validate_runner251_SOURCE.py](实验251_Agentless完整参数新任务共同确认/runner_SOURCE/validate_runner251_SOURCE.py)

## 继续保留在原件或上游的条目

- `dispatch_once251_ROOT_ONLY.py`：私有评价或账户信息相关入口，待逐项公开核定。
- `final_once251_ROOT_ONLY.py`：私有评价或账户信息相关入口，待逐项公开核定。
- `native_once251_ROOT_ONLY.py`：私有评价或账户信息相关入口，待逐项公开核定。
- `capture_handoff251_ROOT_ONLY.py`：私有评价或账户信息相关入口，待逐项公开核定。
- `capture_handoff251_ROOT_ONLY.py`：私有评价或账户信息相关入口，待逐项公开核定。

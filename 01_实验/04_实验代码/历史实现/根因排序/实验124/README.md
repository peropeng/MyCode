# 实验124历史实现

此处展开可公开源码，保留原字节、英文提示词及内部导入布局。实验编号只用于追溯，不代表正式实验名称。现有结果属于前期可行性测试。

文件用于直接阅读和迁移核对，不应执行旧调度、旧授权或旧截止时钟。已完成终态不追加生成。数据、模型、日志、Checkpoint及未公开评价材料继续保留在完整原件附件中。

## 可直接阅读的文件

- [实验124_责任排序强基线与外部迁移/audit_assets.py](%E5%AE%9E%E9%AA%8C124_%E8%B4%A3%E4%BB%BB%E6%8E%92%E5%BA%8F%E5%BC%BA%E5%9F%BA%E7%BA%BF%E4%B8%8E%E5%A4%96%E9%83%A8%E8%BF%81%E7%A7%BB/audit_assets.py)
- [实验124_责任排序强基线与外部迁移/batch_check.py](%E5%AE%9E%E9%AA%8C124_%E8%B4%A3%E4%BB%BB%E6%8E%92%E5%BA%8F%E5%BC%BA%E5%9F%BA%E7%BA%BF%E4%B8%8E%E5%A4%96%E9%83%A8%E8%BF%81%E7%A7%BB/batch_check.py)
- [实验124_责任排序强基线与外部迁移/bindings.py](%E5%AE%9E%E9%AA%8C124_%E8%B4%A3%E4%BB%BB%E6%8E%92%E5%BA%8F%E5%BC%BA%E5%9F%BA%E7%BA%BF%E4%B8%8E%E5%A4%96%E9%83%A8%E8%BF%81%E7%A7%BB/bindings.py)
- [实验124_责任排序强基线与外部迁移/describe_results.py](%E5%AE%9E%E9%AA%8C124_%E8%B4%A3%E4%BB%BB%E6%8E%92%E5%BA%8F%E5%BC%BA%E5%9F%BA%E7%BA%BF%E4%B8%8E%E5%A4%96%E9%83%A8%E8%BF%81%E7%A7%BB/describe_results.py)
- [实验124_责任排序强基线与外部迁移/package_results.py](%E5%AE%9E%E9%AA%8C124_%E8%B4%A3%E4%BB%BB%E6%8E%92%E5%BA%8F%E5%BC%BA%E5%9F%BA%E7%BA%BF%E4%B8%8E%E5%A4%96%E9%83%A8%E8%BF%81%E7%A7%BB/package_results.py)
- [实验124_责任排序强基线与外部迁移/report_results.py](%E5%AE%9E%E9%AA%8C124_%E8%B4%A3%E4%BB%BB%E6%8E%92%E5%BA%8F%E5%BC%BA%E5%9F%BA%E7%BA%BF%E4%B8%8E%E5%A4%96%E9%83%A8%E8%BF%81%E7%A7%BB/report_results.py)
- [实验124_责任排序强基线与外部迁移/runner.py](%E5%AE%9E%E9%AA%8C124_%E8%B4%A3%E4%BB%BB%E6%8E%92%E5%BA%8F%E5%BC%BA%E5%9F%BA%E7%BA%BF%E4%B8%8E%E5%A4%96%E9%83%A8%E8%BF%81%E7%A7%BB/runner.py)
- [实验124_责任排序强基线与外部迁移/seal_delivery.py](%E5%AE%9E%E9%AA%8C124_%E8%B4%A3%E4%BB%BB%E6%8E%92%E5%BA%8F%E5%BC%BA%E5%9F%BA%E7%BA%BF%E4%B8%8E%E5%A4%96%E9%83%A8%E8%BF%81%E7%A7%BB/seal_delivery.py)
- [实验124_责任排序强基线与外部迁移/smoke.py](%E5%AE%9E%E9%AA%8C124_%E8%B4%A3%E4%BB%BB%E6%8E%92%E5%BA%8F%E5%BC%BA%E5%9F%BA%E7%BA%BF%E4%B8%8E%E5%A4%96%E9%83%A8%E8%BF%81%E7%A7%BB/smoke.py)
- [实验124_责任排序强基线与外部迁移/test_contract.py](%E5%AE%9E%E9%AA%8C124_%E8%B4%A3%E4%BB%BB%E6%8E%92%E5%BA%8F%E5%BC%BA%E5%9F%BA%E7%BA%BF%E4%B8%8E%E5%A4%96%E9%83%A8%E8%BF%81%E7%A7%BB/test_contract.py)
- [实验124_责任排序强基线与外部迁移/verify_delivery.py](%E5%AE%9E%E9%AA%8C124_%E8%B4%A3%E4%BB%BB%E6%8E%92%E5%BA%8F%E5%BC%BA%E5%9F%BA%E7%BA%BF%E4%B8%8E%E5%A4%96%E9%83%A8%E8%BF%81%E7%A7%BB/verify_delivery.py)

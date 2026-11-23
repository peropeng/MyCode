# Exp127：完整恢复方法可行性 — Stage0资产审计

**Stage0结论：34项资产保留完整账本，14项有源日志支持的真实编辑新错误；当前完整合同已验证可直接纳入任务为0。**六例moto官方补丁测试接通不归因于本文方法。详见[Stage0报告](stage0_report.md)、[逐任务账本](task_ledger.json)和[最小任务清单](minimum_tasks.json)。

本目录根文件封存Stage0，不包含模型比较或正式方法协议。授权边界见[收据](scope_receipt.json)。后续经主线程新授权的Stage1放独立子目录，不改变这些根文件。

## 交付内容

- `message_mapping.jsonl` / `call_mapping.jsonl`：1716条消息和789次调用的完整稳定身份映射；保留239次文本替换/创建的真实参数，以及拒绝、缺响应、其他编辑类型和仓库外路径。
- `source_test_observations.jsonl` / `source_log_review.json`：原命令/原观察和全部34项逐项证据解释，区别新编辑错误、原Issue失败及测试自身变化。
- `repository_objects.json` / `input_manifest.json`：当前基础Git对象、输入与证据原始字节SHA。
- `native_reference_evidence.json`：六例既有base/reference测试记录、完整argv/cwd及逐节点来源，不是新实验结果。
- `stage0_environment.json` / `stage0_ranker_entry.json`：主线程独立核验的环境、模型、API配置存在性和A+B入口；没有密钥值。
- `audit_assets.py`：静态审计入口，不导入旧runner，不运行任何原轨迹命令；`verify_delivery.py`仅做包与映射完整性检查。
- `delivery_manifest.json`：Stage0根文件字节封存名单。`.gitattributes`设置`* -text`，避免Git行尾转换改变SHA。

## 只读复核

在本worktree执行（PowerShell）：

```powershell
& 'D:/Code/毕设/graduate-thesis-experiments/工作区/0922-exp123-recovery-selection/.venv/Scripts/python.exe' -X utf8 'D:/Code/毕设/graduate-thesis-experiments/工作区/0922-exp127-complete-recovery/实验/实验127_完整恢复方法可行性/verify_delivery.py' --inputs

& 'D:/Code/毕设/graduate-thesis-experiments/工作区/0922-exp123-recovery-selection/.venv/Scripts/python.exe' -X utf8 'D:/Code/毕设/graduate-thesis-experiments/工作区/0922-exp127-complete-recovery/实验/实验127_完整恢复方法可行性/audit_assets.py' --check --main-root 'D:/Code/毕设/graduate-thesis-experiments' --source-checkout 'D:/Code/毕设/graduate-thesis-experiments/工作区/0922-exp127-complete-recovery'
```

合入main后，`verify_delivery.py`可在任何目录直接使用：把脚本路径换为`D:/Code/毕设/graduate-thesis-experiments/实验/实验127_完整恢复方法可行性/verify_delivery.py`即可；不依赖当前cwd和pyarrow。`--inputs`额外读取清单内原输入，原worktree或临时资产不在时应省略该参数，不能把源文件丢失写成验证通过。

静态重建需要既有pyarrow环境及封存时来源；`--source-checkout`明确绑定原代码checkout，不随脚本搬到main自动漂移。源码/输入发生变化时`--check`应报告差异，而不是覆盖证据。已有`delivery_manifest.json`时，非`--check`生成模式会拒绝执行。主线程环境probe采用独占创建输出，若再次核验须输出到新的获准位置，不能覆盖本快照。

全部复核仅验证字节、映射、既有日志归属，不运行业务测试，不证明完整方法效果。

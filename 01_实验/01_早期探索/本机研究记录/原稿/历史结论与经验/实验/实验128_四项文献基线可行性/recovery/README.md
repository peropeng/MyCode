# 四项诊断的共用恢复适配器

`adapter.py` 把真实诊断预测接到 Exp127 的严格选择性回滚执行器。固定沿用 getmoto__moto-5134、5286、6352 三个中间开发状态，每源任务一个状态；合法候选数分别为 4、2、1。它们只检验小样本可行性，不能证明排序或闭包增益，也不等于完整原 Issue 修复。

输入 JSONL 每行的必需字段为 `sample_id`（也接受 `instance_id`）、`predicted_step`（从零开始的 assistant 决策步骤）、`diagnostic_elapsed_seconds`。`method` 可省略，由命令指定；`status` 缺省为 `completed`。应保留 `prediction_source`、真实调用及响应定位等证据。阻塞预测写 `status: blocked` 和 `reason`；无预测时自动记为 `NOT_RUN_DIAGNOSIS_BLOCKED`，`success: null`，不进入恢复成功率分母。含 mock、simulation、synthetic、fixture 标记的预测不能进入实际执行。

StepFinder 另需 `ranking`，必须是覆盖所有 assistant 步骤的真实完整排序，且第一项等于 `predicted_step`。其余三项不能提交拼凑的完整排名。单步骤策略首先尝试该步骤对应的合法业务编辑；余项按逆执行时间补齐。输出分别记录 `native_diagnostic_order`、`fallback_order` 和每候选的 `ordering_source`，后备顺序不参与原生诊断排名指标。

可在本实验执行 worktree 中运行：

```powershell
python -X utf8 '实验/实验128_四项文献基线可行性/recovery/adapter.py' export-inputs --out '实验/实验128_四项文献基线可行性/samples/recovery_inputs.jsonl'
python -X utf8 '实验/实验128_四项文献基线可行性/recovery/adapter.py' preflight --verify-replay
python -X utf8 '实验/实验128_四项文献基线可行性/recovery/adapter.py' run --method all_at_once --predictions '<真实预测JSONL>' --out '<新的结果目录>'
```

可用方法标识为 `all_at_once`、`binary_search`、`sdbl`、`stepfinder`。导出、预检和结果目录均拒绝覆盖；重跑需要指定新的 `--out` 和 `--runtime`，禁止覆写既有证据。`--stage1` 用于显式指定既有 Exp127 Stage 1 目录。默认从本实验 worktree 推导 Windows 项目根，不使用历史 macOS 路径。

输入导出函数 `export_inputs(stage1)` 只读取各任务 `visible/source_prefix.json`。它提取公开原任务、完整截断前消息、assistant 步骤、相邻执行观察，以及 `new_failure_observation.visible_target_feedback`；不读取官方修复、责任标注、资格中的先前通过判定或保护测试反馈。失败反馈来自 Exp127 新执行的离线测试，不声称来自原轨迹测试。样本带 `messages`、`steps` 及兼容别名 `turns`，调用端应按目标方法取一个表示，避免向模型重复发送。

执行时直接抽取并使用既有 `stage2/recovery.py` 的 `apply_edit`、`provenance`、`closure`、`candidate_plans`、`materialize`、`snapshot` 等原函数，不加载原 A+B 排序器。每次结果保存原执行器 SHA256。文本来源与文件创建条件定义依赖；`old_str` 必须唯一匹配；先撤销后继闭包，再从公共检查点完整重放。源脚本和源测试保持在实际重放中，但只有 `repo/moto/*.py` 业务编辑可作撤销根，涉及非业务文件的消息原子组或闭包无资格。

共同预算是最多六次环境提交、每次测试最多 120 秒、诊断加执行共 900 秒。代码从共同时间中预留最多 120 秒作最后一次保护验收（当剩余不足 240 秒时预留其一半），防止搜索用尽后完全没有验收机会；不会增加总预算。首个可见测试通过后停止搜索，随后只作一次保护验收；候选耗尽或后续重放失败时，仍验收最后一个成功重建的状态。时间耗尽导致验收未启动时，单独记未覆盖，不能报告已完成验收。

最终成功要求恢复测试通过、保护测试通过、编辑合法同时成立。合法性检查拒绝业务目录之外的改动，并复核冻结测试库存。原 pytest 隔离环境、网络与子进程限制、写入保护、节点覆盖检查保持启用。每提交保存实际省略及保留编辑数、重放状态和原因、测试明细、阶段耗时；最终保存文件快照、全库库存、`no_final_state`。保护失败率只计算真正完成保护验收的状态，同时报告验收覆盖数。模型 API 调用不属于此执行器；此模块内调用次数、token 与费用都是零，诊断端账单保留在原预测文件中。

已完成的 `preflight.json` 是环境检查记录，三个状态的全量文件字节重放一致，冻结测试库存匹配。`test_adapter.py` 的七项测试覆盖单步后备边界、StepFinder 完整排名校验、可见输入读取边界、首过即停、后续重放失败时最终状态选择、缺诊断不计失败，以及相对 CLI 输出路径必须转成绝对隔离日志路径。契约测试使用局部合成环境桩，测试文件中明确标记，不是基线实验或模型响应。

`runs/stepfinder_v1` 保留首轮基础设施失败记录：相对输出路径被错误传给冻结测试目录中的隔离保护进程，导致 guard 未加载，pytest 内部错误且实际测试节点未执行。这轮由 `INVALIDATED_ENVIRONMENT_RUN.json` 明确排除，不计恢复成功率。修复使用同样真实预测、新结果目录及新运行目录重新执行，详见 `runs/stepfinder_v2`。现版本对没有任何受保护完整可见测试覆盖的运行输出 `NOT_EVALUABLE_ENVIRONMENT_FAILURE`、`success: null`；同时分列实际提交数、可评价数，环境阻塞不能当作功能损坏或零成功率。

后续真实 API 诊断轮的有效恢复结果位于 `runs/all_at_once_flash_v1`、`runs/binary_search_flash_v1`、`runs/sdbl_flash_v1`。三者均恢复 3/3，总提交数为 4、3、4，保护验收均为 3 次且全部通过。各目录含 `audit.json`、`task_metrics.csv`、`attempt_metrics.csv`；汇总见 `api_round_report.md` 和 `api_round_metrics.json`。诊断端人民币费用范围单列，恢复侧 API 调用为零。已有 StepFinder 结果未重跑，并通过其汇总 SHA256 未变核验。生成这些审计与表格的只读结果处理入口为 `summarize_api_round.py`。

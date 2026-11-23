# Exp129 的本文方法与 StepFinder 本地入口

固定 120 个共同任务组的两份原生方法结果已完成，位于 `diagnostic120_v1/`。本文方法复用合法的 20260816 strict nested OOF 全分数；StepFinder 使用对应 held-fold 已训练权重及真实 Qwen 嵌入缓存，实际执行 GPU 前向。没有新训练、生成 API、模型下载，也没有使用历史 180 条保留数据。

| 120 组固定开发子集 | 本文 A+B | StepFinder |
|---|---:|---:|
| 严格步骤准确率 | 27/120 = 0.2250 | 71/120 = 0.5917 |
| 角色准确率（由步骤映射） | 75/120 = 0.6250 | 100/120 = 0.8333 |
| ±1 步容差 | 0.4750 | 0.7583 |
| ±3 步容差 | 0.6500 | 0.8667 |
| 完整 MRR | 0.434718 | 0.722535 |
| 格式有效输出 | 120/120 | 120/120 |

这 120 组在五个非空领域×来源层中各取 24 组，是均衡开发子集的描述性证据。历史全体 731 条/716 组的已有 MRR 仍为本文 0.496057、StepFinder 0.845827，不被本表替代。首 20/40/60/80/100/120 个固定前缀和分层描述见 `diagnostic120_v1/descriptive_native_summary.json`；未依据这些结果改变样本、模型或并列规则。

## 真实资产与字段可用性

`Exp112C/results/formal_corrected_nested_oof_results.json` 实际保存 `raw_scores/A_plus_B`，不只是 Gold 的名次。每个 seed 都有 731 条完整步骤分数。本轮仅提取 seed=20260816 的 A+B 分数，使用冻结的 Exp124 原记录索引及缓存 `input_sha` 核对输入；没有用全量部署模型评价 AF，没有读取 Oracle 分数来产生预测。

Exp112C 封存 LF SHA 为 `d99f9468adeadec4e69e30e0a2c44aafc277c4a034be0f1b7f678c4da5deb851`。科学 helper 的 LF SHA 与 Exp124 preclaim binding 逐项相符；预测仍取自原先合法的组外折结果。文件读取会解析含其他历史结果字段的同一 JSON，但推断路径仅使用指定 A+B 分数；Gold 只在独立 `verify_native.py` 和描述统计程序中用于预测落盘后的核验。

StepFinder 延续 Exp128 已审计入口，直接导入官方 `48d71c7090adca3667a31b043a78484f407b4a2f` 代码。真实 Qwen3-Embedding-0.6B、所有选用 checkpoint 和缓存均经过原冻结 SHA/绑定核对。每条使用 seed=20260816 所属 held fold，完整保留原批次成员和 padding 长度，并在本次调用中合并相同批次，避免重复前向。

独立核验 `diagnostic120_v1/independent_validation.json` 的 240 条方法×样本记录全部通过：本文分数逐值等于原 OOF，Gold 平均秩与历史记录完全相同；StepFinder 的新前向分数逐值等于 Exp124，原生次序也全部相同。

## 共同严格并列规则

在新样本推断前，主协议固定两个完整打分方法共同使用：**精确分数降序 → 冻结 Exp88 匿名结构 digest 升序 → 原执行下标升序**。不将近似分数人为分桶，不根据结果选择规则，也不修改任何模型分数。

该 digest 仅由匿名角色和内容/动作/思考的结构签名构成，直接调用已封存的 Exp88 函数。`ranking`、`predicted_step` 与 `predicted_role` 均由这一严格全次序产生。原 Exp112C 使用相同分数/digest 键的平均秩来评价；因此本轮另存 `historical_midrank_by_step` 和精确同键组，不能用 `raw_rank <= 1` 替代严格 Top1。

StepFinder 另存 `native_ranking_score_then_index`、`native_top_step` 和 `common_tie_changes_native_ranking`。共同 tie 是评价适配，不能冒称官方 StepFinder 原本采用匿名 digest。`historical_midrank_by_step` 对本文可与原历史评价直接核对；在 StepFinder 行中，它只是同一个 Exp112C 匿名键平均秩函数的辅助向量，不表示 StepFinder 原论文的评价规则。

实际 120 条中，两法均没有完全相同的分数/digest 键。本文共同严格 Gold 秩相对历史平均秩的差异为 0；StepFinder 共同次序相对原生次序的改变为 0。这是执行后的审计事实，没有反过来参与规则选择。

## 计算范围和时间

StepFinder 实际执行 43 次原批次前向，680 条不同轨迹进入计算；仅冻结的 120 条进入本轮评价，其余批次伙伴输出没有扩充评价分母。伙伴中包含旧先导索引 40、121、205、639、693，只为保留原批次计算形状；旧先导的全部 6 个任务组都被排除在本轮 120 组评价之外。没有把这些伙伴声称为“未推理”。

本地总阶段约 28.124 秒，StepFinder 资源启动/完整文件核验约 25.321 秒；43 个评分前向合计 0.814 秒，各批次包含特征读取和必要 checkpoint 加载的时间合计 1.681 秒。每条保存其共享批次延迟和按当批选中样本数摊销的辅助时间；同一批次复制到多条输出的延迟不能再求和当总资源开销。

本文历史每条推断时间没有保存，因此其 `diagnostic_elapsed_seconds` 和 `pure_model_elapsed_seconds` 为 null，当前仅另记缓存读取/严格排序导出的耗时。`actual_model_execution=true` 表示使用真实历史模型预测，`current_model_forward_executed=false` 明确本轮没有重新推断。不能把此次读取缓存的速度当成本文模型的诊断速度，也不据此与 API 或 StepFinder 声称速度优势。

## 扩展恢复入口

`predict.py --mode recovery` 为新增且已冻结的公开恢复前缀提供两个真实入口：

- 本文读取原 Exp127 `stage2/training/weights.json`，SHA 为 `0dc6b1c8d6a15bba06a9d17830f139222d889d375bb4b7187e7e980f93dfc176`，直接调用原 `deployment.predict`。权重的 731 条/716 组训练边界和原候选前 seal 已核对；没有重训，且此部署权重仅用于恢复。
- StepFinder 固定使用既有 seed=20260816 fold0，将新前缀的可见 content/action/thought 与匿名角色交给真实本地 Qwen 编码。不会根据恢复结果挑选 checkpoint。

两法都保留原部署的固定观测投影，不额外编码顶层任务说明、失败反馈或独立 observation 字段。恢复输入需含非空 `turns` 和 `sample_id`，每步有 `role`。Gold 字段禁止进入入口。候选资格、回滚闭包、后备次序和恢复测试由共同执行器负责，本入口只返回真实步骤分数及共同排序。

截至本说明写入，新增恢复样本尚未交付该入口，**没有提前评分未知样本，也没有给恢复成功率赋值**。运行后会生成独立的新目录和报告，不覆盖 Exp128 或本轮诊断记录。

## 可执行命令与交付

本地运行环境复用 `工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe`。以下命令需要把 `--out` 换成尚不存在的新目录：

```powershell
$python = 'D:/Code/毕设/graduate-thesis-experiments/工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'
$exp = 'D:/Code/毕设/graduate-thesis-experiments/工作区/1002-exp129-expanded-baselines/实验/实验129_扩展基线与恢复证据'
& $python -B -X utf8 "$exp/native/predict.py" --mode af --inputs "$exp/samples/diagnostic_inputs.jsonl" --out "$exp/native/new_diagnostic_run" --limit 120
& $python -B -X utf8 "$exp/native/predict.py" --mode recovery --inputs '已冻结恢复输入JSONL的绝对路径' --out "$exp/native/new_recovery_run"
```

`--start` 与 `--limit` 只按已冻结输入顺序切片，不执行基于模型分数的样本筛选。`--methods ours` 或 `--methods stepfinder` 可用于分别运行，默认两者。AF 本轮已运行一次，不需要为读取既有结果重新运行。

代码与记录均位于本目录：`assets.py` 负责只读资产绑定和共同 tie，`predict.py` 是正式入口，`inspect_assets.py` 只核对资产，`verify_native.py` 在落盘后读取评价标签核验，`summarize_native.py` 只做描述统计。`asset_availability.json` 记录推断前资产检查。大权重保持在旧公开资产目录；本轮新增编码仅写本 worktree 的 `scratch/native/`。

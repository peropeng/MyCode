# StepFinder：Exp128 小样本真实运行

**结论：现有资源可直接运行，但应称“StepFinder 的 AF-Traj 同数据适配及固定 checkpoint 编码恢复迁移”，不能称原论文全部实验复现。** 本轮完成固定 AF 6 条、moto 恢复前缀 3 条的真实模型诊断；没有新训练、模型下载、生成 API 或付费模型请求。恢复是否成功由统一执行器的真实测试裁定，本目录不以诊断完成冒充恢复成功。

## 来源、依赖及机制

2026-10-02 实时检查的[官方仓库](https://github.com/taiyu-zhu/StepFinder) HEAD 仍为 `48d71c7090adca3667a31b043a78484f407b4a2f`，与 Exp124 固定版本相同，许可证 MIT。机器证据见 `live_source_check.json`。本轮直接导入该版本 `model.py` 与 `Q3Emb.py`，导入前将官方源码 LF SHA 与 Exp124 冻结记录逐项对照。Qwen 所有 6 个模型/分词器文件均重算 SHA；`model.safetensors` 为 `0437e45c94563b09e13cb7a64478fc406947a93cb34a7e05870fc8dcd48e23fd`，来源版本为 `97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3`。实际资源检查见每次 `*.run.json`。

环境复用 `工作区/0922-exp124-ranking-baselines/.venv`：Python 3.12.14、torch 2.7.1+cu128、transformers 4.51.3、numpy 1.26.4、RTX 5070。设置 Hugging Face/Transformers offline，未联网获取权重。本轮没有新增依赖。

| 机制 | 实际执行及差异 |
|---|---|
| 语义编码 | 官方 Qwen3-Embedding-0.6B，FP16、last-token pooling；取前 128 维内容、前 32 维角色，不使用随机向量或规则分数。每个内容文本最多 8192 tokens，batch 8。 |
| TFE | 官方 LayerNorm → 双层双向 LSTM（每方向 hidden 64）→ LayerNorm；mask 与 packed sequence 保留。 |
| ASI | 官方双头步间注意力；角色向量余弦偏置及全轨迹角色均值门控，alpha=0.1。 |
| 评分 | 官方 MLP 标量 + 多尺度差分（scales=[1,2]，beta=0.9）+ 位置偏置（gamma=0.4）；得到每一步完整实数分数。 |
| 训练权重 | 复用 Exp124 真正训练好的 state_dict，严格加载全部键，不训练替代网络。原训练为交叉熵 + 0.9×时序一致性损失；本輪没有训练。 |
| AF checkpoint | 固定 seed=20260816，使用各 record_id 对应的 held fold。逐条核对输入 SHA、缓存 SHA、embedding binding、checkpoint SHA、held/fit 组分离。 |
| 恢复 checkpoint | 在恢复结果出现前固定 seed=20260816、fold0；这仅是既有 AF 模型的迁移可行性，不是全量部署模型或使用恢复结果挑选的模型。 |
| 输入适配 | 延续 Exp124：将非空 content/action/thought 序列化为 JSON 内容，role_n 为角色输入。官方特征构建原本仅用 content，因此属于明确的数据适配。 |
| 提示与标签 | StepFinder 神经评分无需生成式诊断提示。官方仓库中的轨迹再生成提示及 LLM 排名提示不是该模型的推理环节，未调用。AF 评价标签只在预测落盘后由报告程序读取，不进入适配器模型输入。 |
| 确定性排名 | 分数降序、并列按原步骤下标升序。输出为真实全排序，不是 Top1 后补齐。角色是从最高分步骤映射得到，标记 `derived_from_predicted_step`。 |

AF 不使用任务题目、角色描述或正确答案，保持旧模型固定投影。恢复也保持同一投影：单独的 observation 字段、顶层 failure_feedback、task、role_descriptions 未额外编码；具体非空字段计数见 `summary.json`。不能把这项输入使用差异隐藏为与生成式方法完全相同的表示。三条恢复轨迹均只有 role_0，不能据其角色预测声称多角色归因能力。恢复 50 个内容文本均未触及 8192-token 截断。

## 固定样本与实际结果

AF 输入只读统一 `samples/af_inputs.jsonl`，固定索引为 721、693、205、40、121、639，不追加评价样本。最终输出为 `af_predictions_v2.jsonl`：

| 项目 | 结果 |
|---|---:|
| 真实完成/格式有效 | 6/6 |
| 步骤准确率 | 3/6 = 0.5000 |
| 角色准确率（步骤映射） | 5/6 = 0.8333 |
| full MRR | 0.585417 |
| 平均逐条诊断时间 | 0.102560 秒 |
| 含公共资源核验的本轮进程时间 | 4.862586 秒 |

这些只是预定少量开发轨迹的可执行检查。历史相同 731 条/716 组的正式既有结果仍为 A+B full MRR=0.496057、StepFinder=0.845827，不被上述 6 条结果替代。

恢复诊断输出为 `recovery_predictions.jsonl`，固定权重下得到：

| sample_id | 轨迹步数 | Top1（0-based） | 诊断秒数 |
|---|---:|---:|---:|
| getmoto__moto-5134 | 27 | 4 | 18.299579 |
| getmoto__moto-5286 | 15 | 1 | 0.274770 |
| getmoto__moto-6352 | 8 | 3 | 0.155333 |

第一条包括首次加载 Qwen 的 15.147431 秒；恢复进程总计 22.382441 秒，其中公共资源核验约 3.635 秒。全部 3 条都输出完整分数和排名，通过输入哈希、排列、角色映射、真实编码及固定 checkpoint 审计。峰值 CUDA 已分配约 3.740 GiB。适配器将完整排序交给统一恢复执行器，不自行解释候选资格、补齐候选或修改测试预算；真实恢复结果以执行器独立表为准。

`diagnostic_elapsed_seconds` 包括该条的缓存读取/编码、首次所需模型加载及评分；`encoding_elapsed_seconds`、`pure_model_elapsed_seconds`、`cache_read_elapsed_seconds` 分别保存。一次性启动、导入和所有文件 SHA 核验另计于 `*.run.json` 的 `source_verification_seconds` 与 `wall_seconds`。AF 复用已存在编码，当前编码时间为 0；不能据此宣称其端到端速度胜于须实时编码或调用模型的方法。

## 数值重现修复记录

首轮 `adapter_v1_singleton.py` 每次前向只放一条轨迹，但沿用原 held batch 的 padding 长度。6 条排名全部与 Exp124 一致，最大分数差为 0.001165390，未通过预设 1e-4 核对。因此保留 `af_predictions.jsonl`、`af_predictions.run.json` 和 `af_validation.json`，没有覆盖或删除首轮记录。

1e-4 是本适配器自设的数值复现核对阈值，不是论文统计阈值，不用于选模型或判断方法优劣。第二版恢复了每条所在的原批次成员及计算形状；6 条全分数与既有结果逐值完全相同，最大差为 0，审计见 `af_validation_v2.json`。参数、输入、样本清单和排名规则未变，没有重新训练。

首轮实际 6 次前向/6 条轨迹；第二版实际 6 次 batch 前向/82 条轨迹（82 个不同 record_id）。原批次伙伴也确实进入神经网络计算，不能称“未推理”；仅固定的 6 条进入本轮评价，伙伴输出未另存为新评价结果。恢复另有 3 次评分模型前向、50 个内容文本的 7 次 Qwen batch 前向及 1 个角色文本编码。完整计算账本在 `summary.json`。

## 运行和产物

从项目 Windows 根目录运行时，显式传入已有资源根目录，例如：

```powershell
$old = 'D:/Code/毕设/graduate-thesis-experiments/工作区/0922-exp124-ranking-baselines'
$exp = 'D:/Code/毕设/graduate-thesis-experiments/工作区/1002-exp128-four-baselines/实验/实验128_四项文献基线可行性'
& "$old/.venv/Scripts/python.exe" -B -X utf8 "$exp/stepfinder/adapter.py" --mode af --old-root $old --input "$exp/samples/af_inputs.jsonl" --output "$exp/stepfinder/new_af_run.jsonl"
& "$old/.venv/Scripts/python.exe" -B -X utf8 "$exp/stepfinder/adapter.py" --mode recovery --old-root $old --input "$exp/samples/recovery_inputs.jsonl" --output "$exp/stepfinder/new_recovery_run.jsonl"
```

输出文件必须为新名字；脚本拒绝覆盖既有预测和运行记录。`--device cpu` 仅是显式可选环境参数，本轮没有 CPU 结果。输入每行含 `sample_id`、非空 `turns`；AF 还须有原始 `record_id`，并保持 turns 与缓存完全一致。恢复内容仅使用公开观测字段，不调用正确答案。

- `adapter.py`：当前正式适配器；`adapter_v1_singleton.py`：数值核对首轮的可审查源码。
- `af_predictions_v2.jsonl`、`recovery_predictions.jsonl`：最终真实预测、完整分数、角色映射、来源、耗时、费用。
- `*.run.json`：输入/输出/代码 SHA、环境、模型与文件来源、实际运行时间。
- `verify_run.py`、`af_validation_v2.json`、`recovery_validation.json`：预测落盘后的真实结果核验。
- `summarize.py`、`summary.json`：只在预测完成后合并评价标签计算的小样本报告、计算次数和投影差异。
- `live_source_check.json`：官方仓库与当前 commit 的实时公共元数据核对。

所有模型调用、生成 token 和 API 费用字段均为 0；这专指模型 API。官方 GitHub 公共元数据查询另行记录，不把 HTTP 查询冒称模型推理。第三方权重与恢复嵌入留在已有资源或本 worktree 的 `scratch/stepfinder`，不提交大型模型，不覆盖旧实验。

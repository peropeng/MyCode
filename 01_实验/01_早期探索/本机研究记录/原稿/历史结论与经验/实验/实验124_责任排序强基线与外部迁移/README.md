# Exp124：责任排序强基线与外部迁移

状态：Panel A 已实际完成15个outer fold、三种子2193条折外预测；Panel B 资产门停止；Who&When 生成模型基线未完成。最终裁决：**当前A+B显著弱于新增StepFinder同数据适配基线，方法新增增量不成立**（`STRONG_BASELINE_GAIN_NOT_ESTABLISHED`）。这是既有开发集内部证据，不是新独立外测，也不覆盖历史Exp112C。

## 可向导师说明的结果

在相同731条记录、716个独立任务组、全部7366个候选步骤上，新增实际运行的StepFinder同数据适配实现。原A+B沿用未改动的合法Exp112C预测；最强合法比较器为`StepFinder`。任务先在组内平均，再对三种子平均；不能把2193条seed×record当独立样本。

| 方法 | full MRR | R@1 | R@3 |
|---|---:|---:|---:|
| A_plus_B | 0.496057 | 0.262104 | 0.651420 |
| StepFinder | 0.845827 | 0.760591 | 0.924232 |
| pairwise_B | 0.343700 | 0.068901 | 0.456448 |
| local | 0.314238 | 0.094972 | 0.367528 |
| recency | 0.330520 | 0.090782 | 0.407821 |

| seed | A+B full MRR | StepFinder full MRR | StepFinder R@1 | StepFinder R@3 |
|---:|---:|---:|---:|---:|
| 20260816 | 0.493108 | 0.844403 | 0.758380 | 0.925978 |
| 20260817 | 0.497868 | 0.849396 | 0.767807 | 0.918645 |
| 20260818 | 0.497195 | 0.843682 | 0.755587 | 0.928073 |

| 配对比较 | MRR绝对差 | 相对提升 | 任务级95% CI | 三种子均正 |
|---|---:|---:|---|---|
| A+B − StepFinder | -0.349770 | -41.35% | [-0.377511, -0.321637] | False |
| A+B − pairwise_B | +0.152357 | +44.33% | [+0.132089, +0.172067] | True |
| A+B − local | +0.181819 | +57.86% | [+0.161660, +0.201850] | True |
| A+B − recency | +0.165537 | +50.08% | [+0.136575, +0.193267] | True |

CI为716个任务组等权、每任务先汇总三种子、5000次配对bootstrap；主门同时要求相对最强者≥10%、CI下界>0、三种子均正及审计全部通过。StepFinder另报MRR@3=0.831394，不能与表中的full MRR混称。完整逐任务值、逐候选分数、排序、种子和训练过程分别在`panel_a.json`、`folds/`、`freezes/`。

补充描述性分层（在终态之后计算，不参与Gate、不据此调参）：496条/496组`injected`中，A+B MRR为0.523325、StepFinder为0.923314；235条/220组`diagnosed`中，分别为0.434581和0.671129。三个领域`agentic/coding/math`方向也均为A+B较低。完整分层见`results/descriptive_strata.json`。这保留了人工注入任务占比较高的适用范围，也说明差距并不只出现在注入子集。

历史Exp112C相对早期结构基线的结果仍然有效；新增对照表明，不能再据此主张当前匿名结构A+B已经超越语义时序强方法。本轮没有追加模型或重调门槛来改变这一结论。

## 同数据适配具体做了什么

固定官方StepFinder commit `48d71c7090adca3667a31b043a78484f407b4a2f`，直接导入官方`model.py`的TFE、ASI、评分头和联合损失，使用真实`Qwen/Qwen3-Embedding-0.6B` revision `97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3`。所有模型文件核对固定版本来源SHA；权重SHA为`0437e45c94563b09e13cb7a64478fc406947a93cb34a7e05870fc8dcd48e23fd`。

两方使用同一匿名角色记录及完整turn候选。StepFinder把可见`content/action/thought`序列化为内容文本，角色输入为`role_n`；任务ID、题目、来源、Gold和错误解释不进入表示。原A+B只利用这些观测的结构；StepFinder保留真实语义嵌入，不能把其弱化成随机向量或小模型。官方原实现只编码`content`，因此本轮准确名称是“同数据适配”，不是使用作者4168条生成训练集的原论文复现。

沿用E96固定三seed五折任务划分。每outer在其余四折中固定第一折验证、其余三折训练，按验证任务等权Top1选epoch（并列最早），然后以同一官方默认超参在完整outer-train重拟合该epoch数。held只在checkpoint与配置落盘后评价一次。官方每epoch查看test选checkpoint的做法未沿用。共30个模型fit：15个内部选epoch fit、15个完整outer-train refit；不是反复选择held最优结果。

## 外部迁移与剩余基线

| 分支 | 状态 | 可核实原因 |
|---|---|---|
| TraceElephant外测 | `ASSET_STOP`；新外部评价0 | 固定revision全部220 run已有历史用途：Exp84评价217 run/172组，另2 run曾筛选标签、1 run用于适配器开发。重新下载不能清除历史暴露。 |
| Who&When整段/逐步归因 | `NOT_RUN_RESOURCE_GAP` | 未发现实验可用的生成API配置、常见本地生成服务监听或生成模型文件；空`.ollama/models`不是可用模型。Qwen embedding不具备生成归因能力。 |
| 历史180条confirmation | 保持封存 | 未进入编码、拟合、评分或选模型。 |

外测门使用同revision的历史逐run下载账本和机器结果逐项核对，未把仅5条恢复接入案例误当成全部历史使用。多Gold/step_id映射规则已在协议冻结，但先验历史用途门已剔除全集；因此没有合法任务需要进入问句重叠和新模型评价阶段，不声称跨数据去重已通过。TraceElephant标签语义也未混入AFTraj的同一种因果真值。最小剩余外测缺口是**真正未用于开发/评价且步骤标签适配的独立任务**；本轮不能宣称正式论文强基线和迁移证据已齐全。

## 环境、冻结和审计

实际运行环境：Python 3.12.14 / torch 2.7.1+cu128 / CUDA 12.8 / RTX 5070 12 GiB。正式训练代码commit：f3b7acd10d329913cb98aaf4a04ac98f8a6df83c；协议SHA `9d67043361ba6a02cf2bc9295bf51350e8ed9293370cb13d08349e2478be8495`。嵌入用时122.77秒；15折选epoch＋refit＋held用时合计878.63秒。训练峰值CUDA已分配显存0.106GiB、嵌入峰值2.980GiB；这是进程分配量，不是整机桌面显存。新付费资源、LLM API及生成token调用均为0；公开资产HTTP下载与元数据请求另计，失败重试总流量未完整计量。旧A+B运行硬件不同，未作公平速度优劣声称。

Windows TLS/大文件流超时通过官方URL分块下载与SHA检查修复；PyArrow选择可下载的20.0.0，torch选择支持RTX5070的2.7.1+cu128，未缩小Qwen或改StepFinder模型。标量预检编码慢，在任何fit/held前提交协议v2批量性能修订，保留v1与旧缓存；最终特征全部重建为batch8。64条训练输入/874步数值核验：最低余弦0.999984887，平均0.999996965；FP16最大绝对差0.0703125，无混合缓存。

历史Exp112C结果LF SHA `d99f9468adeadec4e69e30e0a2c44aafc277c4a034be0f1b7f678c4da5deb851`吻合封存；Windows checkout物理SHA因CRLF不同而另记。迁移仓库缺少旧`4fe2d9` Git对象，原协议也没有封存全runner哈希，因此不能虚称旧对象逐文件验证。本轮绑定权威`ab1fa8d5b23a9d591c5809ea299ce381eb99b21c`源码、原结果已封存的tie函数SHA、科学常量、精确数据SHA和划分算法。原artifact未存逐fold组名单，本轮独立重建并逐fold校验原确定性keyset；同时校验每记录候选长度、raw rank组汇总与旧结果一致。这个来源限制保留在`preclaim_binding.json`。

独立终态审计确认：15个checkpoint在held前冻结、每seed 731条预测恰好覆盖一次、组隔离、候选全排列及分数/Gold rank一致、原比较器候选范围一致、原子输出不覆盖。`.gitattributes`禁止字节转换，集成后可再校验冻结SHA。

## 交付和复核

- 协议：`protocol.json`；初始协议和性能修订保留为`protocol_v1_preflight.json`。
- 正式结果：`results/panel_a.json`、`metrics_table.json`、`final_audit.json`、`independent_result_audit.json`。
- 来源与边界：`asset_gate.json`、`preclaim_binding.json`、`model_source_manifest.json`、`external_gate.json`、`who_when_resource_gate.json`。
- 可审查资产：`results/checkpoints.zip`（15个实际state_dict）和`results/embeddings.zip`（731条特征），逐文件SHA见`artifact_manifest.json`；公开Qwen权重未提交。
- 运行日志、耗时与训练轨迹：`results/logs/`、`cost_and_execution.json`、`freezes/`。保留执行worktree中的模型、独立环境及原始资产。

无需训练即可运行`verify_delivery.ps1`，或用任意Python 3执行`verify_delivery.py`，核对归档成员、runner、protocol和终态审计。实际命令为在保存的worktree内用`.venv/Scripts/python.exe -X utf8`依次执行`smoke.py`、`runner.py prepare`、`runner.py run`、`package_results.py`、`verify_delivery.py`；输出已发布后禁止同路径覆盖重跑。

许可证：StepFinder MIT（仓内LICENSE实读），AFTraj CC BY4.0，Qwen Apache2.0；TraceElephant历史固定资产审计记录CC BY4.0。未重新分发第三方源码或公开模型权重。

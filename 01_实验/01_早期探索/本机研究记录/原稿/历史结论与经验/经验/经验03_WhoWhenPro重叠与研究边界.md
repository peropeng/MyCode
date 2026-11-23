# Who&When Pro 重叠与进一步研究澄清

核验日期：2026-08-16

## 1. 直接结论

Who&When Pro 与场景 C 的**基础层高度重叠**，但与“验证故障假设后再用于责任定位”的完整机制并不相同。

必须撤回或降级为基线的创新表述：

- 建立 Agent 失败 taxonomy；
- 从成功轨迹注入单点错误；
- 生成责任 Agent、决定性步骤和错误类型 Gold；
- 联合预测 who / when / error type；
- 比较 All-at-once、Step-by-step 和 Binary-search。

这些均已由 Who&When Pro 明确实现，不得作为本研究的首创贡献。

## 2. Pro 已经完成什么

权威入口：[arXiv HTML](https://arxiv.org/html/2607.09996)、[项目页](https://whowhenpro.github.io/)、[代码](https://github.com/whowhenpro/whowhen_pro)、[数据](https://huggingface.co/datasets/Leoxx/whowhen_pro)。

| 项目 | Who&When Pro |
|---|---|
| 数据规模 | 12,326 条失败轨迹、26 个 benchmark、15 个 Agent 框架、9 类任务、3 种模态 |
| taxonomy | 18 个 error mode，覆盖 perception、reasoning、planning、action、verification、coordination 等 |
| Gold 构造 | 精确重放成功前缀，在步骤 `t` 注入一个 on-policy 错误；若后续转为失败，则注入 Agent、步骤和 mode 构成 Gold |
| 重放可信度 | 静态工具输出内容寻址缓存；有状态环境重放并做 fidelity check，漂移即中止 |
| 评价任务 | Agent accuracy、Step exact accuracy、Error macro-F1、三项 Joint accuracy |
| 基线协议 | All-at-once、Step-by-step、Binary-search；主结果采用 closed-book All-at-once |
| 人工核验 | 100 条分层样本：步骤 94%、Agent 90%、错误类型 90% 接受；Fleiss κ=0.73；2% 无明确决定性错误 |

论文的重要负面发现：最佳文本 Step accuracy 为 73.9%，最佳 Error macro-F1 仅 22.2%；模型经常把规划、验证和协作根因误判成后期 reasoning 症状；轨迹超过 12K token 时步骤准确率约降至 50%；完整轨迹协议虽优于增量协议，仍未解决根因类型判断。

## 3. 与修订后场景 C 的边界

| 层次 | Pro | 修订后场景 C |
|---|---|---|
| 数据与 Gold | warm-start 注入并给出 who/when/type Gold | 直接复用 Pro，不重复造 benchmark |
| 基础预测 | 一次提示联合生成 Agent、步骤和 mode | 将 Pro All-at-once 作为强基线 |
| 假设处理 | 输出一个 mode，没有独立验证门 | 先生成候选故障假设，再检索与假设独立的事件证据 |
| 判断语义 | 单一分类结果 | `ENTAILED / CONTRADICTED / INSUFFICIENT`，允许拒识 |
| 证据评价 | 不要求证据集合联合正确 | 同时评价 hypothesis verdict 与必要证据集合 |
| 对定位的作用 | mode、step、agent 联合预测 | 验证后的假设作为软先验，检验是否改善 Step/Agent 排名，而不是直接宣称有效 |
| 重点难例 | 广泛 benchmark 分析 | 长轨迹与 planning/verification/coordination 的症状—根因混淆 |
| 安全出口 | 必须给预测 | 低证据充分度时选择性拒识，报告 risk–coverage |

因此，Oracle responsible-agent prior → mistake-step 的现有 Bridge 只证明“正确上游信息有机会帮助下游搜索”，属于机制探针，不是论文创新或最终方法。

## 4. 修订后的开题题目与研究问题

建议题目：

> **基于可验证故障假设与证据约束的 Agent 失败归因研究——面向长轨迹症状—根因混淆与选择性拒识**

核心问题：

1. 将 mode/agent/step 从一次性联合生成改为“候选假设—证据验证—责任定位”，能否改善 Pro 的 Step、Error 和 Joint 指标？
2. 增益是否集中在 planning、verification、coordination 和长轨迹，而非容易识别的 perception/action？
3. 当证据不足时拒识，能否以可接受 coverage 换取更低的联合错误风险？
4. 在原始 Who&When 自然失败轨迹上，方向是否仍成立，还是只在 Pro 的注入失败上有效？

上述问题即使得到“无增益”也可形成有效结论：明确两阶段分解何时无效、注入 Gold 与自然失败之间的外部效度差异，以及证据充分度能否识别不可靠归因。因此毕业交付不依赖正结果。

## 5. 最小实验路线

1. 复跑 Pro 官方 evaluation harness，冻结 All-at-once / Step-by-step / Binary-search 基线；
2. 只在训练/开发划分设计假设模板、证据检索器和置信门，测试集不得读取注入 prompt 或 Gold mode；
3. 比较 `Joint Direct`、`Hypothesis Only`、`Evidence Only`、`Verified Hypothesis`、`Verified + Abstain`；
4. 主指标沿用 Pro 的 Agent/Step/Error/Joint，并增加 verdict+evidence 严格联合正确率、MRR/Recall@K、risk–coverage、ECE；
5. 按轨迹长度、模态和错误族分层，做任务级 paired bootstrap；
6. 在原始 Who&When 184 条自然失败轨迹外测，单独报告标签歧义，不与 Pro 构造性 Gold 混算。

## 6. 当前实施状态

- 原始 Who&When 184 条已在本机完成 schema、索引和 Recency 基线审计；
- Pro 论文 HTML、项目页、数据卡和代码结构已核验；
- Pro 代码网页核验 main HEAD 为 `db3946cae6895c8056b9b482c283fc3949a6654f`；
- 数据卡显示公开数据约 10.7K 可浏览行、CC BY 4.0；论文统计口径为 12,326 条，下载后必须解释两者差异；
- 当前执行沙箱无法解析 `github.com` DNS，尚未把 Pro 仓库和数据下载到 `third_party/`。这属于本轮网络环境限制，不能写成已经本地复跑。

## 7. 开题口径

允许说：

> 本研究以 Who&When Pro 的 warm-start Gold、18 类 taxonomy 和官方协议为基础，不重复构建同类 benchmark；进一步研究可验证假设、独立证据和选择性拒识是否缓解长轨迹中的症状—根因混淆。

禁止说：

> 本研究首次提出 Agent 故障 taxonomy、单点注入、who/when/type 联合归因，或已在 Pro 全量数据上验证有效。

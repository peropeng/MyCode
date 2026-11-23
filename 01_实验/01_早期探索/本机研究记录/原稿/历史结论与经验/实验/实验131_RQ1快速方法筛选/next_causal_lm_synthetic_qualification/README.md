# 固定生成模型合成资格

固定合成资格结果为 `STOP_FIXED_MODEL_PROMPT_ROUTE_SYNTHETIC_GATE_FAILED`。A有3/6、B有0/6配对分差严格为正，预先门槛为两类各至少5/6。 科学执行32.953s/600s，使用cuda:0、torch.bfloat16；24输出及12计时全部完成。

符号答案的描述性命中为A 6/12、B 6/12；24例答案计数为{'Yes': 24, 'No': 0, 'tie': 0}，Yes/No的全词表概率和范围为[0.9997515082359314, 0.9999942779541016]。这些描述项不改变预定门槛。 512 token单次forward计时中位数0.468500s，最大0.516000s；投影只适用于重复该人工输入，排除加载、tokenization、传输/保存与真实输入分布。

本轮仅使用每类6对手写人工对照。24个输出不是24个独立样本；不说明总体准确率、泛化、显著性、真实数据增益或两项方法创新。A只判断给定简单上下文，B只比较报告内容是否相容；分数是模型意见，不提供任务真值、执行真实性、责任或因果归因。

使用固定`Qwen/Qwen3-0.6B` revision `c1899de289a04d12100db370d81485cdf75e47ca`，stock eager、eval/inference、无KV cache、不生成文本，只投影最后实际token。每个prompt为一个user message，关闭thinking；固定Yes/No须各为一个不同token，无截断、调词或案例修订。

固定9文件下载单独计时37.328s，总1519207673B；权重SHA256为`f47f71177f32bcd101b7573ec9171e6a57f4f4d31148d38e382306f42996874b`。1.5GB权重保留在本执行worktree的scratch，未纳入普通git；`asset_receipt.json`保存原始地址及完整文件hash。

目录保存五个冻结源、合同与独立审查、完整rendered prompt/input IDs、24份float32全词表logits及逐例分数/概率、12次计时、资源决策和独占运行起止记录。旧实验科学文件保持原样。未读取真实AFTraj、Gold或缓存预测，未编码399或训练；最新方法性能仍为P8 AB22/32。RQ1继续，RQ2暂停。后续真实输入试验需要单独前瞻合同。

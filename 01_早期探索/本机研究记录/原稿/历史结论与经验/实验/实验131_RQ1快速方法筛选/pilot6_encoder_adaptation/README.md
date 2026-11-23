# Pilot6：编码器任务适配与跨任务组标注案例检索

固定组合 AB 在同一开发集得到 **17/32（53.125%）**；预注册裁决为 `STOP_LORA_RETRIEVAL_COMBINATION`。这 32 个任务已在前几轮使用，本轮是开发证据，不是独立泛化确认。

## 输入与方法

所有配置均重新初始化：fit 为 320 个任务组、327 条轨迹，validation 为 40 组/40 条，development 为 32 组/32 条，成员与原冻结划分相同。公共编码不读取 Gold，也没有截断或删除步骤。共同 C 将完整 1024 维 EJ 编码通过可训练 Linear1024→128（含 bias）与 L2 归一化送入原 V19 C；其余原输入、关系及 fit-only 结构缩放器保持不变。
A 在已有 Qwen3-Embedding-0.6B 的最后 4 层 q/v 上训练 rank4 LoRA；其余编码器参数冻结，encoder 保持 eval。B 使用当前编码器的 detached fit 案例库，以 cosine/0.1 的正负标注案例核密度比形成每步分数，加入 `gamma*b`；gamma 从 0 开始、每次优化后限制非负。fit 查询排除整个自身任务组并重新归一化类别质量，validation/development 只检索 fit。案例库不使用 V22 分层权重。
C、A、B、AB、AB_shift 五配置共享初始化种子。AB_shift 只把库内 Gold 按固定 SHA 偏移移位，真正 CE 目标保持原 Gold。每个 epoch 后按当前编码器重建库再验证；同指纹库可复用，选中检查点保存严格对应的 epoch-end 库。
所有配置注册 675,059 个诊断器/投影/gamma 参数与 81,920 个 LoRA 参数；仅 A、AB、AB_shift 启用 LoRA 训练。历史缓存 C 使用不同的旧输入与容量，作为历史参考；本轮 fresh C 才是共同输入/容量对照。

## 冻结训练与预算

AdamW 的诊断器/投影/gamma 学习率为 0.001，LoRA 为 0.0002，weight decay 为 0.0001；batch 为 16 个任务组，沿用 V22 fit 分层组权与组内轨迹平均 CE，全部活动梯度共同 clip1。五配置统一最多 7 个 epoch、patience4，不使用 scheduler、不 refit；以最早达到最高 validation 任务组 Top1 的 epoch 选择检查点。
正式监督前，仅依据公开无 Gold 计时把原共同 cap10 改为 cap7。原 STOP 预算回执保持原字节，另存修订回执；修正初始建库计数后，cap10 为 2371.320s，cap7 的保守估计为 1709.212s（26 次 fit 库刷新）。统一上限仍为 1800s，实际完整训选及开发评价为 1441.953s。公开 prefix 缓存另用 68.093s。
共同 7 轮是预算筛选，不构成充分收敛证明，也不能据此排除方法潜力。所有五份检查点及对应库封存后才读取本轮开发标签并统一评价一次，未根据本轮开发结果调整参数。

## 固定开发集结果

| 配置 | Top1 | MRR | Top3 | 选中 epoch | 训练 epoch | 选中 validation |
|---|---:|---:|---:|---:|---:|---:|
| C | 15/32 (46.875%) | 0.659710 | 0.875000 | 6 | 7 | 29/40 |
| A | 17/32 (53.125%) | 0.691964 | 0.843750 | 6 | 7 | 28/40 |
| B | 15/32 (46.875%) | 0.659710 | 0.875000 | 6 | 7 | 29/40 |
| AB | 17/32 (53.125%) | 0.690923 | 0.843750 | 6 | 7 | 28/40 |
| AB_shift | 17/32 (53.125%) | 0.690080 | 0.843750 | 6 | 7 | 28/40 |

既有四基线均只使用冻结缓存，没有重新执行：

| 基线 | Top1 | AB 净命中差 |
|---|---:|---:|
| all_at_once | 23/32 (71.875%) | -6 |
| binary_search | 13/32 (40.625%) | +4 |
| sdbl | 21/32 (65.625%) | -4 |
| stepfinder | 22/32 (68.750%) | -5 |

历史 cached C 为 22/32。本轮 AB 的诊断错误为 15 个；正式训练和评价执行失败为 0，诊断错误与运行失败分开记录。

预注册门槛是 AB 至少 25/32、严格高于 fresh C/A/B/AB_shift，并严格高于历史 cached C22。门槛逐项结果：`{"AB_atleast25": false, "AB_strictly_above_newC_A_B_ABshift": false, "AB_strictly_above_old_cachedC": false}`。完整配对增减、每条排序及分数、分层结果分别保存在 comparison、各配置原始 predictions 和 descriptive_strata 中。

## 同一检查点的检索写回

| 配置 | gamma | base→final Top1 改变任务 | 修正命中/损失 |
|---|---:|---:|---:|
| C | 0.00000000 | 0 | 0/0 |
| A | 0.00000000 | 0 | 0/0 |
| B | 0.01963420 | 0 | 0/0 |
| AB | 0.02024688 | 0 | 0/0 |
| AB_shift | 0.00486668 | 0 | 0/0 |

此审计只读取已经保存的同一检查点 base_score、gamma_b 与最终分数，没有额外推理或读取 Gold 源。gamma 梯度参与全局 clip，因而即使 AB 优于 A，也可能部分来自裁剪耦合；检索的即时排序写回与完整机制归因需要区分，后者仍需要未来预注册的 loss-only 或 clip 解耦控制。

## 保留证据

五份 selected.pt、五份严格匹配的 selected_bank.pt、各轮 history、选择回执、all5 封存回执、一次开发评价原始分数、参数/预算/资产/完整任务梯度预检和独立代码/freeze 审查均已保留。source_snapshot.zip 固定本轮与只读旧实现源码，delivery_manifest.json 逐文件绑定字节与 SHA。
399 份 prefix 缓存约 3.326 GB，按既定交付方式留在本执行 worktree 的 ownscratch，不压缩入仓库、不删除。prefix_cache_retention_receipt.json 与 cache_manifest.json 保留每份绝对路径、SHA、字节数；源码、P5 公共 packets、模型资产 SHA 与 cache_protocol 固定 chunk plan 可用于重建。保留本 worktree 及其缓存。
RQ2 继续暂停。即使本轮门槛通过，也只支持开发候选，RQ1 可靠增益目标仍未据此完成。

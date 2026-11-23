# P8：相邻双向原始 token 上下文

本轮使用原 C 的完整七组输入和结构，在每步原始 token 上加入一个相邻过去包和一个相邻未来包的上下文差分，分别训练两个无偏置 1024→1 头。六路均从相同种子重新训练，原 C 参数先初始化，新增头为零并恢复初始化 RNG。

| 配置 | 命中 / 32 | Top1 | MRR | 训练 epoch | 选中 epoch | validation / 40 |
|---|---:|---:|---:|---:|---:|---:|
| C | 22 | 68.750% | 0.7979 | 14 | 8 | 27 |
| A | 22 | 68.750% | 0.7979 | 14 | 8 | 27 |
| B | 22 | 68.750% | 0.8344 | 19 | 13 | 28 |
| AB | 22 | 68.750% | 0.7979 | 14 | 8 | 27 |
| AA_duplicate | 21 | 65.625% | 0.7823 | 14 | 8 | 27 |
| AB_length_only | 22 | 68.750% | 0.7979 | 14 | 8 | 27 |

主方法 AB 为 22/32（68.750%），本轮诊断错误 10 条。固定门槛要求至少 25/32，且严格高于 C/A/B/AA_duplicate/AB_length_only；实际裁决为 `STOP_ADJACENT_CONTEXT_COMBINATION`。

四个冻结缓存基线在同 32 条上的命中数为 all_at_once 23、binary_search 13、SDBL 21、StepFinder 22；历史缓存 C 为 22/32。新六路均完成训练和 checkpoint 封存后才读取一次 development32 Gold，未重新执行基线或 API。

新公开编码预检用 74.984s 完成固定 243 次模型调用与合成 MATH 检查。正式公开编码保留全部 399 条、4175 步，以原 manifest 顺序完成 7951 次调用、557312 个 MATH block operator；连同加载、逐记录落盘、四组 fit-only RMS 与 scaled 保存共 1076.703s，固定预算 3600s。原始及 scaled 特征、所有成员/来源/scaler/call 哈希均保留。

每相邻 i,j=i+1 编码 [S Ti S Tj] / [S Tj S Ti]，池化最后当前包 nativeEOS151643，并减去相同 RoPE 位置的单包 unary。注意力 mask 与 cache_position 始终局部从零开始；原始独立 packet IDs、S271、无 padding、FP32/query128 MATH 保持冻结定义。此处只增加相邻语义信息；B 在完整轨迹上使用下一包。

四组 global RMS 在 327 条 fit、320 个组上按组→记录→步等权计算总向量能量，包含显式零端点，不除以 1024；validation/development 使用相同四个标量。AA_duplicate 两头复用同一 past 特征与 sigma；length control 为固定 19 个三次以内单项式，两个方向各只有 19 个有效坐标，注册参数仍与 AB 相同。

真实训练与验证使用共同 max20/patience6、AdamW lr0.001/wd0.0001、batch16groups、全局梯度 clip1。目标是旧 v15 ranking_loss，即 CE 加 0.2 倍负例 softplus 均值，按记录均值→原 V22 fit-only 组权重→batch 组均值汇总。本轮共同训练/验证/六 checkpoint seal/一次32评估及科学结果保存耗时 822.843s，预算 1800s，dev 读取前保留固定 90s 余量。

新六路使用共同的 epoch seed+epoch 重置与独立组 shuffle。原输入、初始化与旧 C 损失等价的检查不代表重现历史整条训练轨迹；max20 是公开计时预算筛选，不能据此宣称充分收敛。

同 checkpoint 的 base→final 排名、实际 float32 (final-base) 与 float32 (residualA+residualB) 分别保存。直接写回发生变化仍不能单独排除共享训练与全局梯度裁剪耦合。

保存分数的补充分析显示，AB 在 29/32 条上的实际写回跨度小于 base 的 Top1–Top2 间隔，足以保证这些条目 Top1 不变；余下 3 条实际也未翻转。这只是固定 checkpoint 的描述性界，不能解释模型潜在收益或用作调参依据。

development32 已在此前方向筛选中多次使用，因此本轮是开发证据。RQ1 目标保持未完成，RQ2 仍暂停；独立泛化确认需要另一个事先冻结的评估阶段。

交付包含科学源码、冻结 protocol、全部六路 selected checkpoint/optimizer/RNG、训练历史/selection、标签访问时间与精确成员、原始32分数/排名、公开编码向量及四标量、逐调用/逐文件哈希、独立审查和日志。公开向量 ZIP 按 64MiB 分块，重建步骤与全部成员 SHA 见 public_feature_archive_receipt.json。P6 的399 prefix缓存与本轮原始 scratch 缓存继续保留。

# 实验57：StepFinder 官方复现（Hand-Crafted / GO 门）

上一轮裁决：`NOT_REPRODUCED_EMBEDDING_COMPATIBILITY`。那一轮的 batched 兼容 cache、严格等价失败、校准结果与恢复 provenance 均作为历史审计证据保留；本轮正式复现改用官方逐 step unbatched 路径。

本实验冻结并复现 StepFinder 在 Who&When Hand-Crafted 子集上的官方主路径。冻结的来源为：

- StepFinder MIT：`3b2366396fbe321d0da518fa625402e4cd93d559`。
- Who&When MIT：`b2bae5c5b06d681d04ea5e9b63b7a30525c04925`。
- `Qwen/Qwen3-Embedding-0.6B` Apache-2.0，revision `97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3`。
- 官方 HC train 2,604 条；Who&When HC test 58 条。Who&When Appendix F 明确 step index 从 0 开始。

## 当前合同与审计

`scripts/prepare_data.py` 从官方 Who&When HC test 生成 StepFinder 所需的 normalized test JSON，只添加 `history[*].step_id` 与按顶层 `mistake_step` 生成的 `history[*].is_mistake`；不改变问题、答案、历史 content/role 或标注字段。官方特征代码读取 `content` 与 `name`（若无则 `role`），不读取 top-level 根因 agent/reason/answer。

已验证：58 条 test、2,604 条 train、train/test 问题文本零重叠；每条 test 的 0-based `mistake_step` 合法且恰好一个标签。官方顶层 `mistake_agent` 与历史 role 前缀在 55/58 条一致；20/22/49.json 的不一致被原样保留并在结果中披露，未用 agent 字段替换 step 标签。

## 运行

```bash
python3.12 -m venv runtime/.venv
runtime/.venv/bin/pip install -r runtime/StepFinder/requirements.txt psutil pypdf
PYTORCH_ENABLE_MPS_FALLBACK=1 ./reproduce.sh
```

`reproduce.sh` 依次执行合同审计、固定 revision 模型下载、5 条官方 unbatched fixture 确定性与 cache schema 合同、5 条官方 unbatched smoke、正式 unbatched embedding、3 个预注册种子 StepFinder 与同 split 参数匹配 sequential BiLSTM 基线、指标聚合。正式 cache 由 `scripts/encode_features_unbatched.py` 逐文件调用官方 `TemporalFeatureExtractor.process_log`，每个文件完成后 fsync append-only provenance；中断后只恢复有本 wrapper 证据的 cache。模型/第三方仓库/缓存/长日志只在 `runtime/`，由 `.gitignore` 排除。

由于论文代码对每个 step 单独调用 encoder，本轮不以 batched 兼容实现替代官方语义。`scripts/verify_unbatched_fixture.py` 在无 cache 临时目录中重复执行官方 `TemporalFeatureExtractor.process_log`，并核对官方 `encode_dir` 写出的三键 cache schema；`scripts/encode_features_unbatched.py` 只负责逐文件 checkpoint、schema 校验和 provenance。`scripts/encode_features_batched.py` 与 `compat/BATCHED_FEATURES.md` 仅作为上一轮兼容路径的历史对照，不进入本轮正式结果。

## Gate

`results/Q_reproduction_unbatched.md` 是本轮裁决入口（历史 `Q_reproduction.md` 不覆盖）。预注册门为：StepFinder 三种子 Acc@1 均值落入论文约 22.99% ±3 个百分点、均值方向超过同 split 参数匹配 sequential BiLSTM、Acc@3/MRR@3/每轨迹推理时间均可追踪、数据合同通过，且 aggregate 重新核对 contract/model/feature/code hashes、每个 seed 恰有一对方法结果。fixture 合同失败时应停止，不得用更多种子、放宽数值门或改标签制造 GO。即使门通过，3 条 agent-role 标注不一致仍是 Who&When 合同限制，不能把结论外推到通用 agent 泛化。

参数匹配基线为输入 160、2 层双向 LSTM、hidden size 75、线性逐步 scorer，并在 logits 上加入与官方完全相同的固定线性位置 bias（gamma=0.4，0-based `-t/(T-1)`，不增加参数）；其 278,551 个参数与官方 StepFinder 默认 277,633 个参数相差 0.33%。StepFinder 与基线都读取完整有序轨迹并使用同一 mask；这只支持同 split 的方向性比较，不消除官方每 epoch 在 58 条 test 上选 checkpoint 的 protocol 偏差。

上一轮正式 embedding 的 batch32/48/64 可恢复 checkpoint 探针不作为本轮 cache 来源。新结果分别写入 `results/unbatched_fixture_contract.json`、`results/unbatched_feature_provenance.jsonl` 和 `results/feature_manifest_unbatched.json`，并绑定每个 cache 的文件 hash/tree hash。旧的 `results/batched_vs_unbatched_smoke.json` 与 `results/device_noise_calibration.json` 必须保留为历史审计证据，不再作为本轮训练前门。

结果 JSON 记录设备、MPS fallback、Python/Torch 版本、官方源码 hash、输入/cache/model hash、命令行、耗时、峰值 RSS、每种子指标以及按轨迹长度/责任位置分层结果。

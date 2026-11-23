# AgentIssue-Bench Gate1：最小非破坏 Docker 资产验证

本实验只验证镜像资产、镜像架构、`show_diff` 链、统一测试 marker 与 fresh replay，不调用模型/API、不生成 patch、不评价定位或修复方法。官方来源冻结为 commit `1d498dec35e347c4e7b9e1c318ef28fc5fa97318`，tag 通过 `pull_images.py::IMAGE_TAGS` 的 1-based index 在 runtime 恢复；提交物不含 raw tag、issue、patch、test 或源码。

## 预注册选择

Phase A 固定为缺失身份中 registry 压缩体积最小的 index 29、15、19，加最小 arm64 control index 48 与最小 amd64 control index 28。Phase B 为 index 17、31、13，但只有 Phase A 五个样本全部通过才允许执行。

每个样本依次执行一次单 tag pull、一次 image inspect、一次 `show_diff`，以及 `test_buggy` 和 `test_fixed` 各两次 fresh container。每次 run 都显式指定 `--network none` 与 `--platform`，不覆盖镜像 ENTRYPOINT，900 秒超时；完整 stdout/stderr 只写 ignored runtime。

## Phase A 裁决

Phase A 结果为 `CONDITIONAL_ASSET_BLOCKED`，blocking reason `HARNESS_CONTRACT_INVALID`，qualified `0/5`。5 个镜像均成功 pull，inspect 得到预期架构/OS/digest，show_diff 均非空；但统一 marker 合同没有在任何样本上成立：marker enum 全为 `missing`。因此容器 exit code 没有被替代性解释为测试结果。

index 29、15、19、28 的 diff 标题可得到唯一 buggy/fixed commit hash，但 index 48 的 diff 只有泛化标题，无法形成唯一 commit 对。index 15、19 的 fixed replay 与 index 28 的 buggy replay/fixed replay还出现非零或无 marker 的执行结果；这些是资产/harness 阻塞证据，不是研究方法失败。所有 replay 的 marker enum 在同一 tag 内保持稳定，但“稳定的 missing”仍不满足 fail-to-pass。

由于预注册要求 Phase A 五个样本全通过，Phase B 没有运行。该结论不是方法 No-Go，也不把下载、架构模拟、依赖安装或 harness 问题计入研究设计失败；它只说明当前 8-tag 资产不能支撑统一 Gold 测试链。

## 复现与安全

```bash
python3 scripts/gate1_runner.py --phase A
python3 -m unittest discover -s tests -v
python3 scripts/privacy_audit.py
```

`--phase B` 会在读取 `results/phase_a.json` 后要求 Phase A 为 GO，否则拒绝执行。不得运行官方 `test_agentissue_bench.py`、`eval_patches.py` 或 `remove_images.py`；本实验不执行 `docker rmi`、`docker system prune`，因此本机镜像层会保留。

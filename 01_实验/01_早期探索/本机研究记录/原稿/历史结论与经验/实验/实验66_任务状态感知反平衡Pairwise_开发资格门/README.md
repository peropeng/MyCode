# 实验66离线假设生成与预注册骨架

本目录记录 Exp65 错误重叠的事后聚合探针，并冻结一个不调用 API 的 Exp66 开发门。当前结论
是 `HYPOTHESIS_STOP_EXISTING_RUBRIC_DIRECTION`：CBR 低于 generic Pairwise，且错误高度重叠；
替代假设是任务状态感知的反平衡 Pairwise verifier。这里没有任何 `DEV_GO_CANDIDATE` 或
章节 GO。

运行探针（只读 `safety_refusal.jsonl`、`planning_multi_hard.jsonl` 和 Exp65 去标识化结果）：

```bash
python3 hypothesis_probe.py
```

运行离线测试：

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile hypothesis_probe.py tests/test_hypothesis_probe.py
```

测试包含资产 SHA/行数/UUID 校验、候选身份换序映射、相对门比例公式、mock 永不 GO，以及
通过 monkeypatch/open guard 证明确认集不会被打开。脚本不接受模型参数，不读 Keychain，不联网，
也不写入原文内容。

结果文件：

- `results/hypothesis_report.json`：Exp65 错误重叠、组合上限、planning_multi_hard 聚合结构和
  替代方法依据；
- `results/asset_manifest.json`：开发资产哈希/规模及确认集封存元数据；
- `results/preregistered_plan.json`：目标方法 prompt 结构、等调用量、解析契约、统计与门禁。

执行边界：先运行完整 73 行 synthetic mock（292 槽、0 网络），其结果严格为
`MOCK_ONLY_NOT_ACCURACY`。Exp66 不新增 live canary；复用 Exp65 已通过的同 endpoint、
`deepseek-v4-flash`、SSE 和 `winner`+`brief_reasoning` schema 证据。只有主线程审查并明确
授权后，固定监督器才可启动一次完整开发集 live run；`planning_single_hard` 与
`tool_irrelevance` 在本实验中始终封存。

## 基础设施重试记录

这里透明记录监督器基础设施尝试，不把启动故障当作科学观察：

- attempt1 仅产生 `EXP66_STOP: NameError` 的监督器日志；旧 PID/status 记录显示
  `credential_persisted=false`，没有 `dev_ledger.jsonl`、`dev_result.json` 或
  `gate_decision.json`，因此可核验的网络请求数为 0、模型输出为 0，
  `scientific_observation=false`。
- attempt1 没有改变 prompt、模型、执行 schedule、统计 gate 或资产哈希；这些预注册对象
  在本次交接中保持不变。
- attempt2 只允许作为上述 NameError 的基础设施重启，使用新的、一次性的
  `dev_attempt2_ledger.jsonl`、`dev_attempt2_result.json`、`gate_attempt2_decision.json`、
  `dev_attempt2_supervisor.{pid,status}.json` 和 `dev_attempt2_supervisor.log` 命名空间。
  启动前必须验证 attempt1 证据、四要素授权及授权顺序；它不构成新实验、也不允许重跑或
  覆盖 attempt1 证据。

每行各执行 generic/state-aware 两次（original/swap）；73 行的统计推断按 41 个 UUID
cluster 配对。四槽顺序采用预注册的、与标签无关的四序列 Latin cycle，避免固定先执行
generic 臂造成时间漂移混杂。

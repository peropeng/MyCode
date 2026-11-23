# EXP38 SyncBench 自然动作效果 replay 资格报告

> 本报告只覆盖当前落盘的 1 个公开 patch candidate；不把未执行的 14 条元数据或构造任务计入 Gate 1。

## 裁决

- `bounded_probe_decision`: **STOP**；`direction_gate1_decision`: **CONDITIONAL**。
- replay task：1；manifest task：1；repo：1；effect type：1。
- stable Oracle rows：0/2；clean replay rows：2/2。
- 30-task、3-repo、3-effect-type、70% stable Oracle、90% clean replay 门槛均未被本轮数据覆盖；bounded probe STOP，方向整体保留 CONDITIONAL，不能宣布 Gate1 GO，更不能宣布 Gate3/RQ1/RQ2 或两章 GO。

## 资产与动作边界

- SyncBench CSV 的字段审计见 `manifests/dataset_manifest.csv`；它有 `repo_url/commit/pyfile_path/unittest_path/original_code/gold_code`，但没有 action/patch/agent trajectory 字段。
- 当前 candidate 的公开 action 不是直接写入 `gold_code`：补丁由 Requests 公共 Git 历史 target `c0813a2d…` 到 public state `e1887993…` 的 `git diff --binary -- src/requests/adapters.py` 重建，并以 manifest SHA 校验。
- Docker runner 只读取任务 manifest 中的公开 commit/path/test/patch SHA；`gold_fields_read_by_runner=false`。

## 逐 replay 失败分类

| task | replay | pre | post | stable Oracle | clean replay | 分类 |
|---|---:|---|---|---|---|---|
| 4_requests_callee__adapters___urllib3_request_context__c08 | 1 | TEST_HARNESS_ERROR | TEST_HARNESS_ERROR | NO | YES | DEPENDENCY_SETUP_FAILED, TEST_HARNESS_ERROR |
| 4_requests_callee__adapters___urllib3_request_context__c08 | 2 | TEST_HARNESS_ERROR | TEST_HARNESS_ERROR | NO | YES | DEPENDENCY_SETUP_FAILED, TEST_HARNESS_ERROR |

## 最低成本下一步

若仍要推进 A，应先把公开 action/commit/test 的获取与依赖环境锁成可批量物化入口，再按独立 source commit 去重扩展到 30 task/3 repo。若公开 benchmark 继续只有元数据而无行动轨迹，应保持方向 A CONDITIONAL/STOP，不能以构造 smoke 或 `gold_code` 替代自然动作。

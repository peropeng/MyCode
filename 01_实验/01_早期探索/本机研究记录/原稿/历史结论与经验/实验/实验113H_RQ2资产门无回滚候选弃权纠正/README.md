# Exp113H：RQ2 资产门 fixed-rollback 无候选弃权纠正

Exp113H 是独立的资产资格基础设施修正，完整继承 Exp113G 的
response-conditioned transaction、explicit conflict-abort、local selected
source、helper correction、34 tasks/8 candidates、arms、baselines 与 Gate
六条件。H 唯一新增语义是 fixed-rollback 在没有任何成功 `state_delta`
candidate 时透明弃权，不把弃权伪装成 rollback success。正式集成已经实现，
唯一授权的正式 invocation 已执行一次但以 `HARNESS_INVALID` 失败；没有 H
正式 GO/STOP 结果。

## Frozen fixed-rollback contract

若候选池包含成功 state-delta candidate，仍调用继承的 fixed-rollback
规则（最后一个成功 state-delta candidate），不改变原选择。若没有成功
state-delta candidate，唯一选择为：

```text
position=-1
selected_candidate_id=null
intervention_kind=rollback_unavailable_abstention
intervention_executable=true
state_changing=false
omit_call_delta=false
rollback_available=false
abstained=true
```

冻结的两个弃权 task 为 `getmoto__moto-6387` 与
`pandas-dev__pandas-57058`；其余 32 tasks 保持继承 fixed-rollback 选择。
任何非 fixed-rollback label 使用 `-1` 都 fail closed。

## Non-formal selection/integration preflight

唯一入口：

```text
python3 实验/实验113H_RQ2资产门无回滚候选弃权纠正/scripts/run_rollback_abstention_preflight.py --preflight
```

它对 34 tasks 生成完整 8-label selection audit：fixed-last 与
uniform-replay 均在 `0..7`，fixed-rollback 为 `32` normal + `2` abstention。
selection 阶段不读取 Gold/evaluator，不运行 model/ranking/fault/metric，
且仅在 H run context 内 patch inherited baseline selector，finally 恢复。

同时执行一个真实 local git fixture：`-1` branch 从 exact base clone 完整
重放 8 calls，不省略任何 call，`fault_delta_omitted=false`，运行同一 target
compile probe；fixture 明确记录 abstention、probe、fault timing 与 cleanup。

结果独立、exclusive/no-overwrite：

```text
results/rollback_abstention_selection_preflight.json
results/rollback_abstention_selection_preflight_attempt_audit.json
```

H formal output/audit 独立且 preflight 时保持不存在：

```text
results/asset_alignment_gate_rollback_abstention.json
results/execution_attempt_audit_rollback_abstention.json
```

已实际完成一次 nonformal preflight：selection coverage `34/34`，其中
fixed-rollback `32` normal、`2` abstention；fixture status 为 `ok`，
`formal_attempts=0`。结果 SHA256：

```text
preflight output: 9a41503b58d9c8d8c9b96a7eecc9f76075bffdd9a1f0270633d9d0986805277c
attempt audit:    81ee4a9729a320617a9a26f370a77fe5111a877678aa3d5004669e0c945911e6
```

## Formal integration outcome

唯一正式入口为：

```text
python3 实验/实验113H_RQ2资产门无回滚候选弃权纠正/scripts/run_rollback_abstention_preflight.py --run
```

`RollbackAbstentionExecutor` 复用 G 的 corrected task builder、local clone、
response-conditioned conflict-abort replay、独立 reset、fault/probe 时序与
六项 Gate。排名完成并 unseal evaluator 后，普通 fixed-rollback 继续使用最后
一个成功 state-delta；仅两个冻结 task 的 `position=-1` 分支完整重放
prefix/window，不省略 candidate，`fault_delta_omitted=false`，并记录
`rollback_available=false`、`abstained=true`。任何其他 label 使用 `-1`
都会 fail closed；conflict 永不计 recovery success。

正式输出和 attempt audit 通过 `ORIGINAL -> D runtime -> H exclusive writer`
链路分别单次写入，禁止 retry/overwrite。成功正式输出后 audit 才标记
`inherited_asset_metrics_present=true`；运行异常或输出尚未成功写入时为
`false`。H verdict 映射为：

```text
GO   EXP113H_ASSET_ALIGNMENT_GO_CONTROLLED_ONLY_ROLLBACK_ABSTENTION
STOP EXP113H_ASSET_ALIGNMENT_STOP_ROLLBACK_ABSTENTION
```

两者都不等于 method/chapter GO。

本次唯一正式 attempt 的归档结果：

```text
exit: 1
result: HARNESS_INVALID
failure_stage: formal_executor_candidate_map
root cause: H corrected task lacks instance_id required by inherited F._candidate_map
formal output: absent
failure audit: present, single write, retry=false, overwrite=false
```

失败发生在最终 formal aggregate/Gate 形成前，因此没有正式 verdict、Gate
结论或可报告的资产 GO 证据；本轮不修复、不重跑。

## Boundary

本次冻结执行了唯一一次 formal `--run`；没有读取中间 ranking/metric，也没有
触发第二次调用。正式 output 不存在，独立 failure audit 保留。fixture 的合成
fault/probe 仅用于证明 `-1` 路径没有跳过继承 execution contract。弃权不计
recovery success，也不是 method/chapter GO。

## Verification

```text
python3 -m unittest discover -s 实验/实验113H_RQ2资产门无回滚候选弃权纠正/tests -p 'test_*.py'
python3 -m py_compile 实验/实验113H_RQ2资产门无回滚候选弃权纠正/scripts/run_rollback_abstention_preflight.py 实验/实验113H_RQ2资产门无回滚候选弃权纠正/tests/test_rollback_abstention_preflight.py
git diff --check
```

G preflight output/audit SHA 保持不变；H formal output 不存在，failure audit
已归档。H 没有 GO 结果，method/chapter GO 均为 false。

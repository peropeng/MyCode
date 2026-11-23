# Exp113J：逐臂新克隆隔离纠正

Exp113J 是独立的、仅限资产资格基础设施的 pre-formal 修正。Exp113I 的唯一正式
attempt 已封存为 `FORMAL_HARNESS_INVALID`：继承 H executor 在共享 clone 上执行
`git reset --hard 5adf30beb3581e951556fd8c4f027828bf367a70` 时 exit 128，I formal
output 不存在，I failure audit 保留且不重跑。J 不修改 I/H/G/F/D/C 或旧结果。

诊断中 checkout 后 `HEAD` 仍为该 commit 且 commit object 可达，但 status 已显示大量
未物化路径；随后 reset stderr 报 `unable to read sha1 file` 并以 128 退出。也就是说，
该 selected source 的 object database 缺少 reset 需要重新物化的 tree blobs：checkout
阶段看似成功不代表 reset 所需的完整 blob 集可读。J 用独立 fresh clone + exact checkout
隔离每个 label，正式 executor 不再经过该共享 clone/reset 边界。

## 唯一修正边界

J 继承 I 的 `instance_id == task_id` alias、H 的 fixed-rollback 32 available + 2
`rollback_unavailable_abstention`、G/F 的 response-conditioned conflict-abort replay、
local selected-source binding、helper tuple、arms/baselines、budget、Gold latch 与
六项 Gate。唯一变化是 executor 的隔离边界：每个 task 的 8 个 arm/baseline 都从
selected local source 独立执行

```text
git clone --no-checkout --no-hardlinks <selected-local-source> <temporary>
git checkout --detach <frozen_base_commit>
```

formal executor 不共享 clone、不调用 reset、不 fetch/pull/remote/submodule；每个临时
clone 在 label 完成后自动清理。每个 branch 重新验证 `HEAD == base_commit`，sentinel
`fixed-rollback=-1` 仍完整重放且不省略任何 call，其他 label 的 `-1` fail closed。

## 非正式穷举预检

```text
python3 实验/实验113J_RQ2资产门逐臂新克隆隔离纠正/scripts/run_fresh_clone_isolation_preflight.py --preflight
```

预检覆盖 34 tasks / 8 repositories / 272 candidate branches（每 task 8 labels），
并执行可见 response-conditioned prefix/window replay 与 target compile probe；不读
Gold/evaluator、不运行 ranking/model/metric、不注入 formal fault。冻结证据应为：

- fresh clone/checkout/cleanup `272/272`，所有 path 独立且 exact base 可达；
- response counts `104 state_delta / 18 failed_transaction_noop / 150 stateless`；
- fixed-rollback `32 available + 2 abstained`，两个 task 为
  `getmoto__moto-6387`、`pandas-dev__pandas-57058`；
- 该 nonformal preflight 自身记录 `formal_attempts=0`；授权 formal invocation 之前，J
  formal output/audit 均不存在。

预检另保存 I reset 诊断字段（source、task、HEAD/object/status、reset stderr、清理
状态），诊断只在 disposable clone 中调用 reset，不修改 selected source；J 正式与
非正式 branch executor 都不调用 reset。

## Formal invocation result

```text
python3 实验/实验113J_RQ2资产门逐臂新克隆隔离纠正/scripts/run_fresh_clone_isolation_preflight.py --run
```

formal output/audit 是 J 独立 namespace、single invocation/no-retry/no-overwrite。
主线程授权后，以上 exact command 已执行且仅执行一次：exit `0`，elapsed
`362.544591166` seconds。最终 output/audit SHA256 为：

```text
output: 996b5685a72b19c22a617b762c028bb95e12b7e86989075e17c8dd70afe57494
audit:  365ea9653d1916aeb784dddf13b32ff9c418fe099c2a38e4c4e25593e7abf1b9
```

最终审计覆盖 34 tasks / 8 repositories / 272 candidate records、每 task 8 labels，
response counts `104/18/150`，fixed-rollback `32 available + 2 abstained`。所有
branch 均使用独立 fresh clone，exact base 与 cleanup 通过，`reset_invoked=false`；
fault/probe/conflict audit 保留，conflict 不计 recovery success，Gold 在 ranking 后
才 unseal。Gate 六条件均为 true，且 `source_verdict` 保留。

J GO verdict 为
`EXP113J_ASSET_ALIGNMENT_GO_CONTROLLED_ONLY_FRESH_CLONE_ISOLATION`，STOP verdict 为
`EXP113J_ASSET_ALIGNMENT_STOP_FRESH_CLONE_ISOLATION`；本次结果为 GO，但始终将
method/chapter GO 标为 false。correction layer 没有新生成科学 metrics，output 仅
标记 inherited asset metrics present；资产门结论不等于 method/chapter GO。
formal output 与 audit 均 single-write，attempts=1，retry/overwrite=false。

## Verification

```text
python3 -m unittest discover -s 实验/实验113J_RQ2资产门逐臂新克隆隔离纠正/tests -p 'test_*.py'
python3 -m py_compile 实验/实验113J_RQ2资产门逐臂新克隆隔离纠正/scripts/run_fresh_clone_isolation_preflight.py 实验/实验113J_RQ2资产门逐臂新克隆隔离纠正/tests/test_fresh_clone_isolation_preflight.py
git diff --check
```

J data seal 固定 runner/protocol、preflight 与 formal output/audit hash，并固定 I/H
legacy SHA/absence contract；本次 formal invocation 后不再重跑。

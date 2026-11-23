# 实验 79：AFTraj 选择门的位置与进度鲁棒资格

## 结论

本实验的执行恢复成功，预注册科研裁决为 **`CONTINUE_CONFIRMATION`**。这两个结论必须分开理解：前者表示 Exp78 复现 mismatch 已被定位并修复；后者表示三个冻结的删减 variant 均满足鲁棒资格门，可以继续后续确认流程，但不等于已经取得 official test 结论。

本实验只使用封存的 AFTraj clean development rows，未打开 official test/canary，网络/API/token/latency 成本均为 0。

## 执行恢复根因

失败 runner 的 full_C 特征、utility labels、ridge 拟合和 OOF route 本身与 Exp78 一致。实际 mismatch 只来自 shuffled-label negative control：失败实现使用 `79000000 + seed * 31 + fold` 初始化 shuffle RNG，而 Exp78 的冻结实现使用 `78000000 + seed * 31 + fold`。这使三个 seed 的 shuffled control 漂移，并被总复现检查报告为 `STOP_REPRO_INVALID`。

恢复实现复用了 Exp78/Exp75 的 fold assignment、fold-local Base/A fit、score streams、metrics 和 task-group comparisons，并恢复 Exp78 的 shuffle RNG namespace。runner 现在先逐项复现三 seed 的 Base/A/C/oracle/random/shuffled、全部 paired bootstrap 和 task-group counts；只有复现全部通过后才会打开删减 variant 与 FORBIDDEN position-only 控制。

## 冻结契约

- `protocol.json` SHA256：`f3ee9dcacc501e4d7f20640c738d08df4260b40a5e0c1c8db51792df0e262a7b`
- `data_seal.json` SHA256：`f1985bb23d22111f41ef0354d8a6377ea8733fcb08bcf32e3575dbda32d449ed`
- 两个文件均从失败执行 worktree 字节级复制，`cmp` 一致；未修改 feature sets、seeds、folds、grid 或门槛。
- `position_only_control` 始终是 `FORBIDDEN_CONTROL_ONLY`，不参与方法或确认候选。
- index=1 只做固定的 post-prediction audit，不参与训练、阈值或模型选择。

## 主要数值

Base Exact-F1 在三个 seed 均为 `12.81725888324873`。三 seed 的结果如下；括号内为相对 Base 的 Exact-F1 增量：

| variant | seed 20260822 | seed 20260823 | seed 20260824 | 三 seed group better/worse/tie 合计 |
|---|---:|---:|---:|---:|
| full_C | 18.350899 (+5.533640) | 18.215613 (+5.398354) | 18.339529 (+5.522270) | 135 / 24 / 3333 |
| no_progress_C | 18.350899 (+5.533640) | 18.215613 (+5.398354) | 18.339529 (+5.522270) | 135 / 24 / 3333 |
| no_length_C | 18.328173 (+5.510914) | 18.328173 (+5.510914) | 18.328173 (+5.510914) | 135 / 24 / 3333 |
| current_core_C | 18.328173 (+5.510914) | 18.328173 (+5.510914) | 18.328173 (+5.510914) | 135 / 24 / 3333 |
| position_only_control | 12.817259 (+0.000000) | 12.817259 (+0.000000) | 12.817259 (+0.000000) | 0 / 0 / 3492 |

`current_core_C` 每 seed 的 paired 95% CI 为 `[3.737510763472981, 7.469006866607089]`；探索 CI 不作为预注册硬门。position-only 每 seed 都精确回到 Base，因此所有确认 variant 相对 position-only 的方向均为正。

固定 index=1 层每 seed 有 1277 rows / 771 task groups；`current_core_C` 相对 Base 的 Exact-F1 增量均为 `11.348787837282565`，group better/worse/tie 为 `45/8/718`，paired 95% CI 为 `[7.771350168110255, 15.566510241644588]`。

按冻结协议，`no_length_C` 与 `current_core_C` 的 feature list 都是同一组 18 个 current-core 特征，因此数值完全相同；结果里的最小候选 tie-break 按冻结 variant 顺序记录为 `no_length_C`，不是看结果挑特征。

## 资格门审计

以下条件全部通过：

- no_progress、no_length、current_core 均在 3/3 seed 优于 Base；
- current_core changed task groups 多数正向，且相对 position-only 的方向一致；
- index=1 固定层的 current_core 在 3/3 seed 为正；
- 所有 variant 的 C deletion 精确回到 Base；
- masked-error、future-causality、fold-local training、参数重建和 feature isolation 审计通过；
- official test 未打开，零外部成本。

完整机器可审计结果见 `results/exp79_result.json`。

## 复现

```bash
python3 runner.py \
  --data-dir /Users/peroyang/My/MyWork/worktrees/0822-aftraj-asset/third_party/data/AFTraj \
  --output results/exp79_result.json

python3 -m unittest discover -s tests -v
python3 -m py_compile runner.py tests/test_exp79.py
```

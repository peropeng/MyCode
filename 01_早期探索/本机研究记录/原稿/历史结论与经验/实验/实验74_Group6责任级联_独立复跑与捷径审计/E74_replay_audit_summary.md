# E74 Group6 独立复跑与捷径审计

本实验只做 E33 的独立可执行复跑和资格审计；不继承 E33 历史 GO，也不把 E1、E2 当作两个独立数据集正结果。冻结协议见 `protocol/E74_frozen_protocol.json`，原始逐条预测、步骤 rank 和 bootstrap 输入见 `results/shortcut_audits/shortcut_audit_results.json`。

## 冻结与资产

- 基准分支/提交：`main` / `b03ef20`；执行分支：`exp/0822-exp74-group6-independent-replay`。
- 只读实现：`0820-oopsla-reproduction` 归档中的 `real_feasibility_group6`，绑定 source commit `abb0028` 及 protocol 中的 11 个源码/测试 SHA-256。
- AFTraj 四个文件从 `0822-aftraj-asset` 字节复制到被 git 忽略的 `runtime/AFTraj`；四个 SHA-256 已写入冻结协议。
- E33 历史结果 SHA-256：`group6_results.json=ec2c7be6d320cf5926d3db30c96c562515070f61aafc40437d2d3ea333156075`，`confirmation_results.json=7722178c087ddee1ce8ea526543d7b64ebe03043c61a8a30d13b0b49739c3cce`，`module_audit.json=3a26a73e1cdda145d787da4434c03b169df345378bb83ec6dcb60a2eb617fd48`。

## 原样复跑

命令（无网络、无 API）：

```bash
python3 "$SRC/scripts/run_e1_e2.py" --data-dir "$DATA" --output results/official --seed 20260816 --n-folds 5 --n-boot 2000
python3 "$SRC/scripts/run_confirmation.py" --data-dir "$DATA" --output results/confirmation --seed 20260816 --n-boot 2000
```

`results/official/group6_results.json` 和 `results/confirmation/confirmation_results.json` 与 E33 历史 JSON 字节级一致（SHA-256 分别为上面两值），因此原始数值重现：

| split | E1 方法 | 最强简单基线 | E1 相对差 | E1 paired CI | E2 full MRR | 最强非 Oracle MRR | E2 相对差 | E2 paired CI | 原结果门 |
|---|---:|---:|---:|---|---:|---:|---:|---|---|
| official test (163) | 0.7607 | 0.6258 | +21.57% | [0.0675, 0.2025] | 0.5453 | 0.4179 | +30.49% | [0.0979, 0.1598] | E1 PASS / E2 PASS |
| fresh confirmation (180) | 0.7111 | 0.5889 | +20.75% | [0.0611, 0.1889] | 0.5002 | 0.3909 | +27.96% | [0.0810, 0.1389] | E1 GO / E2 GO |

confirmation pool 为 911，train 731，confirm 180；官方 test 任务组与 pool 交集为 0，train/confirm 任务组交集为 0。E2 full 的桥接 rec 索引与评价 rec 索引完全相同，且来源为 E1 test/confirm OOS 概率；审计结果中的 `bridge_oos_only=true`。

## 四类预注册否证审计

每个条件使用相同 split、seed、2000 次 bootstrap、LR 超参、E2 权重和调用预算；审计脚本只变换可观察输入。另运行了预先写入脚本的 `combined_transparent` 联合压力测试，不是调参。

| 条件 | official E1 | official E2 | confirmation E1 | confirmation E2 | 解读 |
|---|---|---|---|---|---|
| role anonymized + candidate order permutation | 0.7423，+18.63%，CI [0.0491, 0.1902] | MRR 0.5344，+27.88%，CI [0.0840, 0.1495]，GO | 0.7111，+20.75%，CI [0.0611, 0.1889] | MRR 0.5075，+29.83%，CI [0.0864, 0.1461]，GO | 单独去除角色名/候选顺序后仍有信号 |
| drop domain/role prior | 0.7485，+19.61%，CI [0.0552, 0.1902] | MRR 0.5320，+27.30%，CI [0.0826, 0.1466]，GO | 0.7167，+21.70%，CI [0.0667, 0.1889] | MRR 0.5034，+28.78%，CI [0.0818, 0.1415]，GO | 不是单独 domain/role prior 充分解释 |
| mask error/failure words | 0.7485，+19.61%，CI [0.0552, 0.1902] | MRR 0.5427，+35.44%，CI [0.1059, 0.1767]，GO | 0.7111，+20.75%，CI [0.0556, 0.1944] | MRR 0.4895，+29.57%，CI [0.0770, 0.1465]，GO | 不是单独错误词面充分解释 |
| drop task/conv ID + length/position controls | 0.8344，+33.33%，CI [0.1227, 0.2883] | MRR 0.4919，+35.58%，CI [0.0966, 0.1646]，GO | 0.7500，+27.36%，CI [0.0778, 0.2500] | MRR 0.4887，+34.30%，CI [0.0949, 0.1583]，GO | 单独去除 task/长度/位置不消除信号 |
| **combined transparent**（以上联合作用） | **0.3804，-39.22%，CI [-0.3620, -0.1166]，NO_GO** | MRR 0.3568，+8.78%，CI [-0.0105, 0.0681]，NO_GO | **0.3889，-33.96%，CI [-0.3056, -0.0889]，NO_GO** | MRR 0.3826，+15.21%，CI [0.0337, 0.0706]，GO | E1 联合透明配置失效；不能标记 robust candidate |

## 审计结论

原 E33 管道不是 `HARNESS_INVALID`：代码、数据、官方 test 和新鲜 confirmation 原样可复现，split 无任务重叠，E2 使用严格 OOS 桥接。四个单独去捷径审计均保留方向性正信号；但把角色/域/任务标识/长度位置一起去除后的透明配置在 E1 official 与 confirmation 均稳定低于最强简单基线，E2 official 也未过 10%+CI 门。因此本次 E74 不能标记 `ROBUST_MECHANISM_GO_CANDIDATE`；按冻结标签应记为 `SHORTCUT_DEPENDENT`（联合透明压力测试失败），而不是新的方法 GO 或两个独立 GO。

这不是对 E33 的 `TRUE_METHOD_NO_GO`：原始固定角色级联在其 AFTraj 协议上仍是可复现的正结果；否证只说明目前没有证据证明它在联合去除这些可观测捷径后仍是稳健机制。E1→E2 是一个级联依赖，不能计为两个独立研究 GO。

## 验证命令

```bash
python3 -m unittest discover -s 实验/实验74_Group6责任级联_独立复跑与捷径审计/tests -v   # 5/5
python3 -m py_compile 实验/实验74_Group6责任级联_独立复跑与捷径审计/scripts/run_shortcut_audits.py
AFTRAJ_DIR=runtime/AFTraj python3 -m unittest discover -s "$SRC/tests" -v  # 13/13
```

未执行联网或 API 调用；未改写旧 E33、归档源代码、AFTraj 源资产或其他 worktree。主要剩余风险是联合透明条件同时删除了全部结构、任务和错误词面信息，因而不能区分“依赖某一捷径”与“可观察信息被整体抽空”；要证明跨数据集机制仍需新的真实 Agent 数据与独立确认集。

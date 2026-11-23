# Exp111：RQ1 范围优先层次责任步骤排序

## 目的与模块边界

Exp111 验证 RQ1 的完整模块 B：

`failure scope posterior → scope-conditioned localization → global full ranking`。

三步共同计一个模块。范围候选是轨迹中实际出现的匿名 `(role, phase)` cell，`phase=min(2, floor(3*i/n))`；cell posterior 均匀分配到步骤形成 `q`，locator 只使用 q/role/phase/affinity 与匿名单步结构、相对位置的 q-gated 交互。最终分数固定为：

`0.5 * minmax(frozen pairwise_B numeric E2 score) + 0.5 * minmax(scope-conditioned locator utility)`。

所有步骤保留在全局排名中，数值相等（`1e-12` 内）使用平均秩。scope deletion 将所有 q 派生特征置零，逐记录精确回退到 Exp111 的 numeric-score/average-tie `pairwise_B` base；这不是 Exp106 的 anonymous-digest tie 语义，二者的对齐残余见 [baseline_alignment_audit.json](results/baseline_alignment_audit.json)。

## 冻结数据与嵌套 OOF

- Exp96 development partition：731 records、716 task groups；3 seeds：`20260816/17/18`；5 outer folds。
- 每个 outer-train 再以其余 4 个 outer folds 产生 inner-held scope OOF；scope model 只在 inner-fit 拟合。
- outer scope model 用全部 outer-train 拟合并只预测 outer-held；locator 使用 outer-train 的 inner-OOF scope 特征拟合，只预测 outer-held。
- confirmation boundary 只做边界计数，未评分、未拟合、未做方法选择；未读取 Exp97/98/109/110。
- API/token 调用为 0；正式 JSON 成功写入一次且未覆盖。命令过程说明见下文的 provenance 审计。

冻结协议见 [protocol.json](protocol.json)，只读资产标识见 [data_seal.json](data_seal.json)。

## 冻结前置、正式输出与过程 provenance

冻结前置证据来自 commit `216b47c`：`test_exp111_protocol.py` 在 formal 输出不存在时通过 7/7。该测试保持 freeze-time 语义，formal 输出产生后不应把它当作当前 post-run 测试运行。

正式输出固定为 [formal_nested_oof_results.json](results/formal_nested_oof_results.json)，当前 SHA-256 为：

`9ca6755ae620569f0ecb91d3ec0111094e6b3ad8b7983e131dbb5ca2a237b49c`

成功写入耗时 `1005.1333 s`。实际过程有两次命令尝试：第一次完整计算后在写结果前因 Harness 审计字段名错误退出，且没有输出；修复后第二次命令完成唯一成功写入，之后没有重跑或覆盖。

正式 JSON 内的 `single_run=true`、`retry=false`、`retries=0` 不能准确代表上述两次命令的真实过程历史，不应被重新解释为“成功写入语义”；这是残余 provenance 偏差。该偏差不改变方法数值判定，但必须与结果分开披露。完整只读记录见 [posthoc_alignment_and_provenance_audit.json](results/posthoc_alignment_and_provenance_audit.json) 与详细尝试记录 [execution_attempt_audit.json](results/execution_attempt_audit.json)。

## 关键结果

三 seed 全局最强公平 baseline 一次性选择为 `pairwise_B`。formal JSON 内部使用 numeric-score/average-tie 语义，task-group equal step MRR 为 `0.3434897142`；Exp106 冻结公平 baseline 使用 anonymous-digest tie，三 seed 平均为 `0.3436995786`。两种语义只造成 `0.0002098645` 的 baseline 平均差，但正式报告采用对齐审计中的 Exp106 digest-tie group maps，不能把两者混写。

| seed | B MRR | B 相对 baseline | A+B MRR | A+B 相对 baseline | B 95% CI | A+B 95% CI |
|---|---:|---:|---:|---:|---|---|
| 20260816 | 0.3937105 | +14.4341% | 0.3834615 | +11.4552% | [0.0303909, 0.0682395] | [0.0234162, 0.0555308] |
| 20260817 | 0.3942795 | +14.5338% | 0.3836386 | +11.4427% | [0.0313269, 0.0682907] | [0.0238849, 0.0558817] |
| 20260818 | 0.3924204 | +14.6852% | 0.3833750 | +12.0416% | [0.0316566, 0.0690669] | [0.0254134, 0.0569799] |

三 seed 平均相对提升：B `+14.5510%`，A+B `+11.6465%`。B pooled task-group paired bootstrap CI 为 `[0.0324628, 0.0688316]`；A+B pooled CI 为 `[0.0242072, 0.0558362]`。B deletion 与 Exp111 的 numeric-score/average-tie `pairwise_B` base 逐记录严格一致，但不应无保留地称为 Exp106 digest-tie baseline 的 exact 回退；B shuffle、random-scope 的三 seed 平均 MRR 分别为 `0.3434261`、`0.3603128`，均低于 B 的 `0.3934702`；Oracle scope 平均为 `0.6972419`，不低于 B。

只读 baseline 对齐审计把 Exp111 的 B/A+B group maps 直接与 Exp106 formal `pairwise_B` digest-tie maps 配对：B 三 seed平均相对提升为 `+14.4808%`，aligned pooled CI 为 `[0.0322794, 0.0685771]`；A+B 为 `+11.5776%`，aligned pooled CI 为 `[0.0240226, 0.0557158]`。因此经 baseline 对齐审计，B 仍达 `>=10%` 正式模块门；原始 formal JSON 的 `FORMAL_MODULE_FEASIBLE` verdict 保留，但存在上述 residual alignment defect。逐 seed差值、better/worse/tie、5000 bootstrap、受影响 group/record 和 tie 语义见 [baseline_alignment_audit.json](results/baseline_alignment_audit.json)。

Exp106 A 的 MRR 精确复现缓存：`0.3775193428 / 0.3772533069 / 0.3773976048`。A+B 相对 A 的 pooled CI 为 `[-0.0005780, 0.0127359]`，下界未过 0。

## Gate 判定

- B：formal JSON 的 numeric baseline 与对齐审计的 Exp106 digest baseline 下，三 seed 绝对差均为正、对齐后平均相对提升 `+14.4808%`、pooled CI 下界大于 0，判定经 baseline 对齐审计仍为 `FORMAL_MODULE_FEASIBLE`；也满足 >8% 模块候选门。
- A+B：相对最强公平 baseline 未达到冻结的 15% 门（+11.6465%），因此不能宣布 RQ1 章节 GO。
- 即使主 15% 门已达到，A+B 对 A 的互补 pooled CI 下界也必须大于 0；本次为负，报告为互补证据不足而不是章节候选。
- 该结论只属于 Exp111 固定 scope-first 模块；不把跨 RQ 累计 `19.5557%` 写入本实验，也不把本结果宣布为 RQ2 增益。

## Scope 与审计

scope posterior 未退化：三 seed 的 uniform/single-cell/degenerate rate 均为 0；normalized entropy 约 `0.784`。正式 JSON 中的 scope 汇总曾把 prediction insertion order 与 record index 错配。正式 JSON 不改写；由其中保存的 `scope_predictions[i]` 按固定 record index `i` 与冻结 records 做只读重算，得到以下校正值，完整证据见 [scope_alignment_audit.json](results/scope_alignment_audit.json)：

| seed | formal JSON 旧 accuracy | 只读校正 accuracy | formal JSON 旧 range recall | 只读校正 range recall |
|---|---:|---:|---:|---:|
| 20260816 | 0.6073871409 | 0.6552667579 | 0.2435020520 | 0.2900136799 |
| 20260817 | 0.5663474692 | 0.6333789330 | 0.2380300958 | 0.3036935705 |
| 20260818 | 0.5827633379 | 0.6497948016 | 0.2708618331 | 0.3132694938 |

`scope_entropy`、`normalized_scope_entropy`、`uniform_scope_rate`、`single_cell_rate`、`scope_degenerate_rate` 与正式 JSON 一致。该错配只影响这两个派生 scope 汇总字段，不影响已写入的 ranking、group MRR、paired bootstrap、Gate、split 或 controls；Gate 只读取未改变的 `scope_degenerate_rate=0`。runner 的修复也未重跑 formal，上述校正值是 alignment audit，不替代正式 JSON 原字段。

## Pairwise baseline tie compatibility

Exp106/Exp88 历史实现按 `(-numeric_score, anonymous_digest)` 排序，因此数值相同的步骤会被 anonymous digest 打散；Exp111 按冻结协议对 `1e-12` 内数值相等步骤使用纯数值平均秩。两者不是完全相同的 baseline 实现：每个 seed 有 15 条记录、13 个 task groups 受到影响，Exp111 numeric-average baseline 比 Exp106 digest-tie 结果低约 `0.0002098645`。完整只读组合与影响计数见 [baseline_alignment_audit.json](results/baseline_alignment_audit.json)。

使用 Exp106 digest-tie group maps 做完整 5000-bootstrap 对齐复算，B 相对提升为 `+14.3643% / +14.4640% / +14.6149%`，对齐 pooled CI 为 `[0.0322794, 0.0685771]`，因此 B 的 `>=10%` Gate 不变；A+B 对齐平均为 `+11.5776%`，仍未达 15% 章节门。该差异是 tie-rule compatibility 差异，不是 data mapping/order 问题；formal JSON 原始 verdict 保留并明确标记 residual alignment defect。

## Anonymous role encoding residual

`MAX_ANON_ROLES=7` 固定为 `role_0..role_6` 的 one-hot 宽度。冻结的 731-record development schema 最大匿名 role 数为 7，overflow record 为 0；该宽度在 formal 前固定，不按 outer fold 学习，不使用 Gold、metric 或 Gate 决策。它不构成 outer-held leakage，但属于冻结 protocol 未单列的可复现性 underspecification。Exp112 必须在 formal 前显式冻结该宽度/编码，或改用宽度无关编码。

## 验证

```text
python3 -m unittest 实验/实验111_RQ1范围优先层次责任步骤排序/tests/test_exp111_postrun.py
3 tests OK

python3 -m unittest 实验/实验111_RQ1范围优先层次责任步骤排序/tests/test_exp111_corrective_audits.py
3 tests OK

python3 -m unittest 实验/实验111_RQ1范围优先层次责任步骤排序/tests/test_exp111_runner.py
14 tests OK

python3 -m unittest discover -s 实验/实验106_责任排序_Top1提升级联/tests -p 'test_exp106*.py'
19 tests OK

python3 -m py_compile 实验/实验111_RQ1范围优先层次责任步骤排序/runner.py 实验/实验111_RQ1范围优先层次责任步骤排序/tests/test_exp111_postrun.py 实验/实验111_RQ1范围优先层次责任步骤排序/tests/test_exp111_corrective_audits.py
python3 -m json.tool 实验/实验111_RQ1范围优先层次责任步骤排序/results/execution_attempt_audit.json >/dev/null
python3 -m json.tool 实验/实验111_RQ1范围优先层次责任步骤排序/results/scope_alignment_audit.json >/dev/null
python3 -m json.tool 实验/实验111_RQ1范围优先层次责任步骤排序/results/baseline_alignment_audit.json >/dev/null
git diff --check
```

当前不声称 Exp111 全量 discover：freeze test 按设计要求 formal 输出不存在，因此 formal 产生后分别运行 freeze-time evidence（freeze commit 的 7/7）与上述 post-run/corrective/runner tests。

方法判定保持不变：B 为 `FORMAL_MODULE_FEASIBLE`，A+B 未达到 chapter GO；process/provenance deviation 单独记录，不把它写成方法 NO-GO。

Exp112 只能作为下一固定替换模块继续；不得在 Exp111 结果上调 locator 权重、阈值、baseline、seed、split 或统计门。

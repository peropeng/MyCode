# 方向 D：BFCL Schema/可见字面量局部替换设计 3/3

本实验针对同一个目标“BFCL 公开 BitAgent response 是否存在可由执行前公开信息修复的价值”，在实验44（契约/字段修复）和实验45（调用级裁剪/去重）之后，测试第三个实质不同的模块：只对已经存在的 call 做一次 schema 兼容的局部参数/函数替换。

## 预注册算子

固定候选族为：

1. `No`；
2. `ReplaceOneArgumentFromObservedLiteral`：枚举当前及历史可见 user 前缀中的每个显式、类型/枚举兼容 literal，替换一个已有参数；
3. `FillOneMissingRequiredFromObservedLiteral`：对每个已有 call 的每个缺失 required 参数，为每个兼容显式 literal 分别生成候选；
4. `SwapTwoCompatibleArgumentValues`：交换同一已有 call 中两个 schema 类型交叉兼容的已有值；
5. `ReplaceFunctionCompatible`：将已有 function 替换为公开 schema 中参数兼容的 function，只保留目标 function 接受的已有参数；
6. `ReplaceFunctionAndFillOneLiteral`：兼容函数替换后，最多用一个当前可见 literal 填一个缺失 required 参数；
7. `EnumAlignFromObservedText`：仅在 enum 字面量于当前/历史 user 前缀明确出现时替换一个已有参数。

`DropOneOptionalArgument` 不进入候选池，也不作为本设计进展证据，因为删除与实验45调用裁剪重叠。另设一个固定的 `LexicalSchemaRule`：只用 user 文本与公开 schema 的 lexical overlap 及固定顺序 tie-break，对全任务最多做一次局部编辑。它是一个真实全局 baseline，不是逐 task 拼接。

## 泄漏隔离与两阶段边界

policy 的完整输入类型 `PublicProjection` 只有：当前及历史 user message、当前及历史 response item 前缀、公开 function schema。不能访问 task/family/path/Gold/possible_answer/reference turn length/initial state/missed function/offline error/inference log/future turn。所有 120 条任务的所有候选及完整输出 hash 在 `possible_answer` 打开前一次性冻结；support-only 阶段只执行该公共阶段。

每个候选只针对一个已有 call，最多进行 2 个原子字段编辑；`SwapTwoCompatibleArgumentValues` 交换两个已有参数 slot，`ReplaceFunctionAndFillOneLiteral` 进行 function name 替换加一个 required literal 填充，这两个算子都可能使用 2 个编辑，其余算子最多 1 个字段编辑。候选保持 call 数量、顺序和 response item/turn 结构；语义未变化（例如仅 JSON 排版变化）不计 support。原始 response、Gold、schema 原文和用户 literal 不提交，结果仅含 hash、索引、布尔与聚合统计。

## 运行

复用实验43锁定 runtime，不复制 runtime。旧版按 full-output digest 复用 checker 的结果因 stateful evaluator namespace 跨 candidate 污染而 **INVALID**；本版每个 candidate/replay 独立隔离，正式 replay1/2 按升序/逆序执行：

```bash
/path/to/runtime/venv312/bin/python scripts/prepare_metadata.py
/path/to/runtime/venv312/bin/python scripts/run_schema_literal.py --support-only
/path/to/runtime/venv312/bin/python scripts/run_schema_literal.py
/path/to/runtime/venv312/bin/python -m pytest -q tests
```

固定 seed 顺序复核及 fresh-process 分层抽样由实验47审计脚本执行；本版结果为 No=75/120、LexicalSchemaRule=6/120、Oracle=76/120、净救回=1，仍为 STOP。

本机默认 source root 为：

`/Users/peroyang/My/MyWork/worktrees/0821-direction-d-bfcl-gate01/实验/实验43_方向D_BFCL接口契约_Gate0Gate1/runtime`

## Gate 门槛

固定 120 条（四家族各 30）。`No` 必须复现 75/120。先在全样本比较 `No` 与 `LexicalSchemaRule`，按总体得分选择一个全局最强 baseline（同分固定选 No），禁止 per-task 取并集。Oracle 只在六类本设计局部候选中逐 task 选择有效候选，作为信息上界。

GO 必须同时满足：相对全局最强 baseline 增益至少 10%；净救回至少 8/120；固定 seed=20260821、10,000 次 unique-structure paired bootstrap 的 95% CI 下界大于 0；所有候选双 replay 的 task-level 一致性恰为 120/120、每家族 30/30、harness error=0。任一失败即“设计 3/3 STOP”，不进入 Gate2，不声称两章毕设 GO。

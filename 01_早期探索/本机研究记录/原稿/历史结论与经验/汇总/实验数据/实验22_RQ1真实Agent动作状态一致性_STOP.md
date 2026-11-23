# 实验22数据与审计附件

- 当前严格状态：**STOP**
- 原编号：`E038`
- 机器资产：`实验/实验22_RQ1真实Agent动作状态一致性/`
- 主结论：`结论/结论22_实验22_RQ1真实Agent动作状态一致性_STOP.md`

本文件保存详细指标、原结果摘录和审阅证据；研究判断以主结论为准。

## 原实验结果与指标

以下内容直接并入原结果/报告；它们保留当时数字和判断，但最终等级以本文件开头的严格状态为准。

### 来源：旧实验裁决__实验__失败与停止__E038_RQ1真实Agent动作状态一致性__数据资格预检.md

### Experiment 38：真实 Agent 动作状态一致性数据资格预检

状态：`DATA_QUALIFICATION_GO`（仅表示数据具备进入下一步动作—状态一致性开发实验的候选，不是 RQ1 方法 Go）。

#### 输入与边界

输入固定为：

`/Users/peroyang/My/MyWork/毕设实验/.cache/traceelephant-preflight/data.zip`

库存程序只读取以下对象，不解压整个压缩包，也不联网、不修改输入缓存：

`data/swe-agent-runs-swe-bench/*/step_records.json`

`data/swe-agent-runs-swe-bench/*/trace_metadata.json`

实际 schema 为：`step_records.json` 是 step 字典列表；每个 step 的 tool call 位于 `output.choices[].message.tool_calls[]`，参数位于 `function.arguments`；历史工具观察位于后续 step 的 `input.messages[]`，通过 `tool_call_ids` 关联。`trace_metadata.json` 提供 `task_id` 和 `run_id` 身份字段。本轮没有读取 metadata 中的结果标签、错误归因或 evaluator 字段。

#### 盘点结果

| 项目 | 数值 |
|---|---:|
| trace/任务 | 44 |
| 仓库 | 10 |
| step | 1,551 |
| tool action | 1,190 |
| 明确状态改变动作 | 201 |
| 有完整可重放编辑参数的 trace | 30 |
| 有编辑观察确认且可入选的 trace | 27 |
| 有显式 checkpoint 记录的 trace | 0 |
| 输出候选 | 10 |
| 候选仓库 | 7 |

明确动作类型按动作记录识别为：`replace=94`、`create=37`、`insert=4`、`undo_edit=19`、明显 shell mutation=47。候选资格要求至少一个带完整编辑参数且有观察确认的状态改变动作；没有使用最终成功/失败、resolved、gold patch 或 test patch 过滤。

候选按固定键 `(repo, instance_id, first_state_change_event_id)` 排序，并事前采用“每个仓库取最早合格 trace，再按同一全局顺序填充至 10 个”的覆盖策略，确保不因可检测性或结果挑选仓库。候选为：

`django__django-10999`、`django__django-11141`、`django__django-11206`、`django__django-11239`、`matplotlib__matplotlib-20488`、`psf__requests-1724`、`pytest-dev__pytest-10081`、`scikit-learn__scikit-learn-10908`、`sphinx-doc__sphinx-10323`、`sympy__sympy-12489`。

完整机器结果见 [`inventory_result.json`](inventory_result.json)，冻结选择参数见 [`inventory_config.json`](inventory_config.json)。

#### 关键缺口

- 0/44 trace 明确记录可恢复 checkpoint；当前候选依赖编辑调用参数重放，不应声称有完整 checkpoint 恢复能力。
- 仅 2/44 trace 记录可识别的返回码/退出状态；工具观察普遍缺少标准化 return code。
- 38/44 trace 有可识别 diff 证据；其余 trace 不能直接依赖 diff 观测。
- 43/44 trace 有可识别验证/复现命令；验证命令记录仍不完全。
- `workdir_recorded=44/44` 主要来自任务输入中的 `/testbed` 工作目录提示，不等价于结构化 cwd 字段。

因此本结果只支持“存在跨至少 3 个仓库、带可重放编辑参数的真实动作轨迹，可继续做动作—状态一致性开发实验”；不支持将库存直接当作在线检测效果或责任定位结论。

### 来源：旧实验裁决__实验__失败与停止__E038_RQ1真实Agent动作状态一致性__重放资格结果.md

### Experiment 38：RQ1 真实 Agent 动作状态一致性重放资格

状态：REPLAY_QUALIFICATION_NO_GO；research_go=false。

这只是 Phase1 的离线重放资格结论，不是 RQ1 方法结论，也不是 RQ2 的 Go。实验按冻结选择、固定 source tar 与真实 step_records.json 顺序执行；未运行 trace 中的验证命令，validation_command_recorded 仅作记录，不参与筛选或 Gate。

#### Gate 结果

| Gate | 实际 | 要求 | 结果 |
|---|---:|---:|---|
| base build | 10/10 | 10/10 | PASS |
| target exact replay | 7/10 | ≥8/10 | FAIL |
| repository coverage | 3 | ≥3 | PASS |
| changed path evidence | 7/10 | ≥8/10 | FAIL |
| source cache unchanged | true | true | PASS |
| workspace restore | true | true | PASS |
| forbidden field reads | 0 | 0 | PASS |

因此本阶段只能判定 REPLAY_QUALIFICATION_NO_GO，不把失败改写成研究方向否定，也不将其升级为研究 Go。

#### 每任务结果

| instance | target | changed path | .py syntax probe | 备注 |
|---|---|---|---|---|
| django__django-10999 | exact | django/utils/dateparse.py | PASS | trace 转义文本解码后可唯一匹配 |
| django__django-11141 | NO | — | — | target 前没有捕获的 editor create，reproduce_error.py 不在 pristine source |
| django__django-11206 | exact | django/utils/numberformat.py | PASS | — |
| django__django-11239 | NO | — | — | target 前没有捕获的 editor create，reproduce_error.py 不在 pristine source |
| sphinx-doc__sphinx-10323 | NO | — | — | target 前没有捕获的 editor create，test_literalinclude.py 不在 pristine source |
| sphinx-doc__sphinx-10466 | exact | sphinx/builders/gettext.py | PASS | — |
| sphinx-doc__sphinx-10673 | exact | doc/conf.py | PASS | — |
| sympy__sympy-12489 | exact | sympy/combinatorics/permutations.py | PASS | trace 转义文本解码后可唯一匹配 |
| sympy__sympy-13091 | exact | sympy/core/basic.py | PASS | — |
| sympy__sympy-13551 | exact | sympy/concrete/products.py | FAIL (returncode 1) | 目标编辑本身精确适用；语法探针结果单独记录 |

失败任务保持原始资格失败：没有使用手写 mutation、最终 patch、结果标签或网络下载来补齐缺失的 prerequisite 文件。每个 workspace 均执行 reset/clean 并移除，10 个 source tar 的 SHA-256 前后相同。

#### 解释边界

7/10 的真实 editor 目标动作可以在固定 base source 上精确重放，且覆盖 3 个仓库；这说明动作参数—仓库状态接口具有可继续开发的局部可行性，但未达到事前 Gate 的 8/10 资格阈值。下一步若继续，应先单独处理“trace 中通过非 editor shell 创建 prerequisite 文件”的记录完整性问题，不能把 shell mutation 手工改写为 editor replay。

机器可核验明细见 replay_preflight_result.json；冻结规则见 replay_preflight_config.json。

## 历史综合复盘

### 既有复盘

- **E038 真实 Agent 动作状态一致性：**回答 trace、source、checkpoint、状态哈希能否一致；不能说明真实 Agent 责任因果；只能说明状态一致性是前置门。资格/来源获取失败，STOP。

## 来源索引

- `旧实验裁决__实验__失败与停止__E038_RQ1真实Agent动作状态一致性__数据资格预检.md`
- `旧实验裁决__实验__失败与停止__E038_RQ1真实Agent动作状态一致性__重放资格结果.md`

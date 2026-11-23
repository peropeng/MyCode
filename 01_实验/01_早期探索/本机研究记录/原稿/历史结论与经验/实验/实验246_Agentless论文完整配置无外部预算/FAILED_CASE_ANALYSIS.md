# mypy15155 与 moto5516 的公开失败机制

两题的主要问题在于当前代码、当前故障与历史编辑之间的绑定，以及故障消费者没有进入修复闭包。状态保护没有拒绝已生成的有效修复。继续增加相同位置的采样不能直接解决这两个原因。以下只检查既有公开请求、响应、应用及原生记录，没有新增模型调用、产品执行、私有测试、Gold 或费用写入。逐条文件 SHA 与公开记录见同目录 `FAILED_CASE_ANALYSIS.json`。

## mypy15155：模型把历史代码当作当前代码

本文用 RQ1 排序后的三个合法历史编辑，步骤为 7、10、9，全部指向 `mypy/expandtype.py`。当前污染 C0 的 `visit_erased_type`（219–225 行）含调试输出和 `AnyType(TypeOfAny.special_form)`，但文件没有导入 `TypeOfAny`。

| 尝试 | 完整输出及应用 | 公共结果 |
|---|---|---|
| 1 | JSON 正常结束，493 output tokens；提出删除历史版本的 `raise RuntimeError()` 并返回 `t`。SEARCH 中的历史代码不在实际 C0，应用报 `SEARCH_NOT_UNIQUE_OR_MISSING`。 | 未产生可测试候选，当前状态保留。 |
| 2 | JSON 正常结束，455 output tokens；提出导入 `TypeOfAny` 并替换历史版本的 raise。同样 SEARCH 不匹配，整组修改回滚。 | 未产生可测试候选，当前状态保留。 |
| 3 | JSON 正常结束，306 output tokens；终于精确匹配当前污染块，把它恢复为 `raise RuntimeError()`。合法应用成功。 | 目标 `testGenericLambdaGenericMethodNoCrash` 仍失败，detail 为 `SystemExit: 2`，完整公共 stdout 的业务栈底为 `expandtype.py:221 RuntimeError`；普通 `GraphSuite::test_scc` 通过。 |

第三个候选被 SET 接受，但目标失败数仍为 1，最终选择按相同失败数和改动规模返回 C0。模型的三次 rationale 将当前污染 C0 称作 pristine，显示它虽收到当前源摘要、SHA 和历史标签，仍混淆了历史 before/after 与当前文件。前两次失败属于模型提出不可应用的搜索块，不能记作原生工程未知或输出截断。

公共调用栈已给出 `checkexpr.py:1432 → expandtype.py:148 freshen_function_type_vars → expand_type → visit_erased_type`。但闭包提取器收到的 initial failure detail 只有 `SystemExit: 2`，没有消费已经共享的完整 captured output。三次 relation manifest 均无业务栈锚点，退回排序编辑根；仅有 3 条 `ExpandTypeVisitor` 类到 `expand_type` 的静态引用，额外上下文 1 个 span、472 bytes。它没有形成从实际故障调用者到被调函数参数及当前污染块的完整修复上下文。

Agentless 的四个补丁均成功解析与应用，说明其定位及完整当前源上下文在应用性上有实际优势。但四个生成复现测试都未被验证，包含 `SCOPE_V2_UNRESOLVED_OPEN_DESCRIPTOR`，最终按普通测试和标准化频次回退投票，选 sample 1。其修复选择缺少有效的目标区分器，不能据此将它的候选代码用于本文新请求。

## moto5516：修复了另一套 API 的实现

本文前三项合法证据为历史步骤 20、9、35，全部指向 `moto/ec2/models/fleets.py`。该文件的 `FleetsBackend.delete_fleets` 实现 EC2 Fleet；本题公共目标执行的是 Spot Fleet。

| 尝试 | 完整输出及应用 | 公共结果 |
|---|---|---|
| 1 | JSON 正常结束，357 output tokens；修改 `fleets.py:304 delete_fleets`，取消无条件重新插入，并补返回列表。合法应用。 | 普通测试通过，目标仍为 `test_spot_fleet.py:364`：返回列表 `[]` 的长度为 0，期望 1。SET 接受。 |
| 2 | JSON 正常结束，521 output tokens；仍修改同一函数，在非终止分支重新保存到 `self.fleets`。合法应用。 | 普通测试通过，目标同样失败。SET 接受。 |
| 3 | JSON 正常结束，188 output tokens；认为当前代码语义已正确，返回 `edits: []`。 | 没有新候选。最终选择相同失败数下的 C0。 |

公开业务源码的真实静态调用链是 `responses/spot_fleets.py:5 cancel_spot_fleet_requests → models/spot_requests.py:462`；后者在 470 行无条件删除 `self.spot_fleet_requests`。`describe_spot_fleet_requests`（452 行）读取此字典。这与非终止取消后返回空列表的实际错误一致。三个输出没有编辑这条消费者路径，因此修复 `fleets.py` 无法影响已观测到的 Spot Fleet 目标。此为公开源码与错误相一致的静态机制判断，未新增原生执行来验证任何替代修复。

三次闭包均无业务 traceback 锚点，因为断言落在公开测试和 sure 内，failure anchor 又排除了测试及 site-packages。静态根仍为排序编辑的 `FleetsBackend`，生成 5 条到 `models/__init__.py` 的导入引用，额外上下文仅 1 个 span、224 bytes。闭包没有利用公开失败文本中的 `cancel_spot_fleet_requests`、`describe_spot_fleet_requests` 操作名称去定位合法业务消费者。

Agentless 四个补丁也都改 `fleets.py`，全部合法；四个生成测试实际复现了故障，但每个候选仍未解决复现。最终按官方普通测试回退及标准化频次选 sample 0。它的复现阶段提供了有价值的负反馈，但候选定位同样受历史编辑位置误导，不能仅靠增加相同补丁采样推断收益。

## 通用修改的依据

应保持 RQ1 顺序、同三次尝试上限、完整关系闭包和 SET，把 SHA 验证的当前 incumbent 故障作为主要锚点；已有完整公共 stdout/stderr 应参与业务 traceback 提取。没有业务栈时，可从已公开测试或故障文本的 API 消费者调用定位合法当前业务函数，标注静态可能关系，不能冒称因果边。每次请求的末尾应显式呈现当前故障处的完整函数和 SEARCH 唯一性约束，清楚标注历史编辑不可当作当前文件。既有公共 Goal 尚失败时，空编辑不能解释为修复完成。

这些是统一适用于五题的机制变更，需新版本前瞻封存与小试。分析没有证明新机制已成功，也没有授权读取私有结果、复制其他方法补丁或按胜负换题。

关键执行位置：`工作区/1011-our19/environment240.py:270` 的 closure 输入，`failure_anchors240.py:31` 的业务帧过滤，`relations240.py:69` 的静态调用索引，以及 `r/3/f`、`r/4/f` 的三组公开响应与 relation manifests。

# 下一路线：公开信息存在性与覆盖

此次只读取现有合法 731 条的 `conv_id/domain/task/tools/turns`，所有 ID 由 Gold 全为 None 的原缓存限定。731 条 task+turns 投影哈希逐条与原缓存相同；未读取 protected180/163、safe 数据或新标签，未运行模型、工具或文本中的代码。

| 分母 | tools 非空 | action 非空 | name+arguments JSON 调用 | 较早 id→较晚 call_id 且同 name | action 内 test_code+assert |
|---|---:|---:|---:|---:|---:|
| 合法 731 | 704 | 725 | 694 | 441 | 163 |
| 当前 399 | 384 | 395 | 382 | 218 | 86 |
| fit 327 | 315 | 324 | 313 | 176 | 72 |
| validation 40 | 40 | 40 | 40 | 24 | 8 |
| development 32 | 29 | 31 | 29 | 18 | 6 |

tools 只有 name/description 两个字符串字段，全 731 共 1243 项、5 个名称、6 种精确描述。原缓存基线输入只有 task 与 turns 的 role/content/action/thought；tools 属于数据可见但未进入该输入合同的信息。

当前 399 的 4175 个 turn 中，action 为 999 个整段 JSON 数组、66 个调用样式文本、157 个其他文本、2953 个空串。字面 ID 关联覆盖 218 条，881 个 JSON 返回对象中 878 个找到较早同 ID、同名称的调用；返回角色均为 environment。调用参数含 expression、computed/expected、solution_code/test_code 等键，完整角色与各分母覆盖见结构补充统计。

这些 action/content JSON 已在原输入合同内，可以确认其记录中的结构与关联。此次不验证执行真实性、结果正确性或独立测试资格。test_code 与 verify_answer.expected 由 agent 动作携带；tools 描述未提供结构化参数约束。399 条 task 中未出现固定口径的 assert 行，36 条含函数定义文本候选。不能据此把 agent 自带测试或 expected 升格为任务的独立判据。

首轮只搜索显式 call_id/tool_call_id，得到同键跨 turn 重复为零；固定哈希原文样本随后发现 action 使用 id。首轮源码、协议和结果完整保留，跨 id→call_id 关联与动作测试内容由独立冻结的 structured_strings_addendum 补充，避免把首轮数字误读为无关联。

public_scope_binding 记录精确 ID 过滤、原缓存与源 Parquet 哈希；两份协议绑定各自处理源码和统计口径；record_presence_inventory 与 structured_strings_record_presence 提供逐记录存在性；hash_fixed_raw_pointers 提供每个公开 domain 的固定哈希样本、原字段指针与值哈希。summary 和 structured_strings_summary 保留完整分母、domain 与角色统计。

此次是信息资格审计，不是新 A+B 结果。最近模型结果仍为 P8 AB 22/32（68.75%）；RQ1 目标未完成，RQ2 暂停。后续信息资格与公平输入合同由 root 核定。

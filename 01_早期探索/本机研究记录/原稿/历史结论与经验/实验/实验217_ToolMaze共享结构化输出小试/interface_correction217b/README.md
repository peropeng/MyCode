# Exp217b：嵌套字段机械修复与能力检查

Root 确认 Exp217 冻结字段给错后，授权在本子目录修正为本机 parser 实际读取的 `response_format.json_schema.schema`。原 64 POST、八条结果、协议与 adapter 已先封存为提交 `c0c359bc` 并建立 432 文件字节快照；修复后这些旧文件全部 SHA 不变。旧八条未改名、未回写分数，其“完整 Schema 被忽略”的标签保留。

2026-10-08 11:41:21 UTC 修复检查完成。先进行唯一一次资源强制验证：提示只有 `Output plain DONE.`，Schema 要求仅含唯一 const marker 的 JSON，max64。实际返回完整匹配 marker 的 JSON，required、additionalProperties=false 和 stop 均通过。该输出只证明运行时约束，不作为语义或任务能力。

资源验证通过后，执行两项已有任务的全新 P0 `STRUCTURED_CONTINUE` controller；不重新跑原八条恢复比较，也不改任务、业务参数或初始公开提示。

| 原生能力检查 | 原 Judge | 实际模型 POST | 实际工具调用 | 输出格式/Schema | 工作流限制 |
|---|---|---:|---:|---|---|
| C2_task_002 P0 | PASS | 7 | 6 | 完整符合 | 发出 final_answer；未重复同工具及参数 |
| C3_task_002 P0 | PASS | 15 | 15 | 完整符合 | 达到十五轮上限；未发 final_answer；同参数邮件模拟调用共七次 |

现有只读 `jsonschema` 库已验证全部 23 份实际生成输出，包括资源验证与两个 controller：完整 Schema 错误 0、非法 JSON 0、未广告工具 0。每份实际 SDK wire 字节、原始响应字节、精确 tokenizer 输入和 usage 均核对一致。没有安装新依赖或改共享 venv。

新增 23 POST（资源 1、原生任务 22）、35,665 输入 tokens、1,479 输出 tokens、21 次本地原工具调用、三个 controller。Exp217 累积为 87 POST、112,412 输入、4,733 输出、11 controller，费用 0，低于累计上限。全部调用为同一本地模型、显式 seed20261008、温度0，byte0 lease 串行，重试0。原模型服务与 guardian 未修改或停止。

原 Judge 的 PASS 使用原基准工具覆盖/路径规则。C3 的六次重复邮件模拟动作没有因此被判失败，故能力结论必须限定在接口和原路径覆盖。参数语义、工作流终止和无重复副作用没有由本检查独立证明。原插件都是本地模拟，实际邮件发送、支付或远程交易均为 0。

公共工具 Schema 沿用 Exp217，业务参数由模型自行生成，没有填参考值。原 Engine、ToolExecutor、插件、first-touch、Judge 保留；本子目录只检查一个 CONTINUE 条件，未得出 LOCAL_REPLAN 的恢复增量。旧错误 wire 下 P2 参照已2/2、RC0，仍只保留为旧原生观测；正确 wire 的 P2 没有在本检查中重评，未扩大这两题的恢复队列。

权威入口为 `results/summary217b.json`、`results/resource_probe_result.json`、`results/report.json` 和 `results/old_namespace_unchanged.json`。新原始模型/工具/context/Judge 行保存在本子目录的 `results/flows`。复核只读 Schema 汇总：

```powershell
& 'D:/Study/miniconda/python.exe' -B '实验/实验217_ToolMaze共享结构化输出小试/interface_correction217b/summarize217b.py'
```

该汇总只使用已经存在的库；没有模型、原生工具或网络调用。生成入口带不可覆盖 claim，资源验证和已取得结果的任务不重试。下一步的科学比较由 root 重新阅读论文并独立冻结，不能把机械格式修复当作研究方法收益。

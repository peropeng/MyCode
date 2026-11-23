# 实验247：完整排序证据的前瞻扩展与6387接口修复

本目录封存一个与旧 K=3 路径区分的新版本：保留 RQ1 的原始排序、关系上下文、实际 C0 PASS 集保护、普通行为保护、恢复与最终选择，按全部合法原编辑逐步扩大证据前缀。前三步历史关系池保持原最多三条，第四步起随当前前缀扩展。公共 G/O 全 PASS 即自然停止，尚未全 PASS 时至合法证据用尽为止；不增加同前缀重采样。

这是内部证据参数变化后的前瞻版本，不能把它与旧 K=3 的差异解释成单纯延长外部预算，也不能把本次单题改进称为已经整体超过强基线。当前固定共同分母为五题。来源池的 23 个 issue、前瞻主计划 21 题、当前完整共同评价五题是不同口径，详见主线报告。

## 已归档的公开观测

| 任务 | 精确复用的已付费请求 | 本目录新增执行 | 公开状态 |
|---|---:|---|---|
| 5406 | 1 | 无 | 原公开自然 PASS 路径核验 |
| 6387 | 3 | 第四步模型生成 1 次、公开 native 1 次 | G/O 全 PASS，原 SET 自然选择第四步 |
| 5980 | 1 | 无 | 原公开自然 PASS 路径核验 |
| mypy15155 | 3 | 无 | 三条合法证据已穷尽的公开路径核验 |
| 5516 | 3 | 无 | 第四步完整 body 已准备，尚未 POST |

11 条旧请求均逐次核对完整 body、seed、tools 与响应的精确 SHA。旧请求没有重发；重放使用真实公开 native 记录恢复运行时字典顺序与状态。6387 从第三步已接纳的 incumbent 续接，未误用旧最终回退到 C0 的目录。

6387 第四步实际请求 body 的 canonical SHA256 为 `369ce741fd86b51db83ee027c1a212ea46fc268c651c7f234ed17f9011e916f8`，实际新增 usage 为输入 155630、输出 554 tokens，结算 0.0568668 元。生成结果规范化 `responses.py` 的 `Paths.Items.Path`，并保留此前 `models.py` 的修改。公开验收与父子 Job 停止均有实际记录。原规则选定快照 `exp247_4`，完整 actor inventory SHA256 为 `c496fbb2ed8a82044ded3857e68476070381edf4ab8c01b2b301c8e0155cad2d`；业务源码 inventory SHA256 为 `dadd38b3ecaa19420057dcd86311c57be8b31a3824cdc8e32eb4394c461ca3b3`。

独立终验与整体接纳由 Root 单独执行。Root 的具体授权与结果接纳文件只登记路径，未在本交接中读取或复制 private 细节：

- `ROOT_ACTUAL_FIRST_MODEL_6387.json`
- `ROOT_ACTUAL_PUBLIC_NATIVE_6387_ATTEMPT4.json`
- `ROOT_ACTUAL_FINAL_6387_ATTEMPT4.json`
- `ROOT_RESULT6387_APPROVED.json`

绝对路径见 [ROOT_REFERENCE_PATHS.json](ROOT_REFERENCE_PATHS.json)。整体结论以 Root 接纳记录和主线共同矩阵为准，公开 PASS 不替代独立终验。

## 旧预算与时钟

旧版本、旧授权、旧结果和旧预算成绩均保留。6387 原科学 T0 为 `2026-10-11T06:32:04.884913+00:00`，已复用公开前缀耗时 97.712173 秒；新增前瞻执行区间始于 `2026-10-11T16:02:17.193329+00:00`。归档分别保存原 T0 的连续 wall、两段间归档间隔、新执行区间以及前缀加新增区间的计时，不把新 lease 的零点当作旧科学时钟的新起点。

30 分钟 / 128 次模型请求意图 / 131072 输出 tokens 的预算观察与完整轨迹结果分别记录。后续成功不改写旧预算内未交付结果；资金、费用未知或进程保护中断仍属删失或未知，不填成自然算法失败。连续财务账本及原已付费用没有重置。

## 可复核入口与执行边界

以下源码均保存精确字节，实际运行时的代码与输入绑定见 `SOURCE_SEAL.json`、`FOLLOWUP_SOURCE_SEAL.json`、`FINAL_SOURCE_SEAL247.json`。这些历史封印不被交接清单重写。

| 入口 | 作用 |
|---|---|
| `prepare247.py` | 从只读原数据重建五题公开前缀，核完整 body，停在第一个未发送请求；会写检查点 |
| `dispatch247.py --index 1 --root-grant <具体授权>` | 对最初准备的单条请求执行严格授权、全额预留和一次 POST |
| `continue247.py --index 1` | 消费精确匹配的已结算响应及公开 native 证据，恢复原核心，停在新请求/新 native 边界或自然终态 |
| `dispatch_next247.py --ready-dir <forward中的ready目录> --root-grant <具体授权>` | 后续单条模型请求入口；未在本次6387自然终态后使用 |
| `native247.py --ready <NATIVE_READY.json> --root-grant <具体授权>` | 原 G/O、原运行环境、共同四槽与 Job 约束下的一次公开验收 |
| `final247_ROOT_ONLY.py --ready FINAL_PRESERVATION_READY247_SOURCE.json --root-grant <Root具体授权>` | 已选业务源码冻结后，由 Root 对原独立保留性范围执行一次终验；无反馈回模型路径 |
| `verify_archive247.py` | 只校验公开归档的文件大小与 SHA，不导入实验执行模块、不触发模型或 native |

不要为“查看结果”再次运行 `prepare247.py` 或 `continue247.py`，它们会重写工作检查点。已完成状态应使用只读归档校验。已结算请求不重复 POST；已有请求意图、费用未知或 native 启动意图均禁止自动重发/重跑。当前 Root 授权不能当作未来新运行的授权。实验依赖原始只读绑定、公共 pack、既有运行环境和连续账本，归档不是脱离这些资产的重新计费实验。

在本机使用已配置 Python 运行只读校验：

```powershell
& 'D:/Code/毕设/graduate-thesis-experiments/工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe' '<本实验绝对路径>/verify_archive247.py'
```

## 归档与提交范围

`PAID_PREFIX_ARCHIVE_MAP.json` 列出 11 条原请求及完整请求、响应、HTTP 响应和已结算 receipt 的本地逐字节副本；`LOCAL_ARCHIVE_MANIFEST.json` 列出公开消息、模型与工具边界、快照、公开 native、自然终态、源码及检查点的大小与 SHA。末态完整公开检查点为 `forward/1/TERMINAL_CHECKPOINT247_PUBLIC.json`。`PUBLIC_OBSERVATION6387.json` 提供紧凑的公开观测索引。

大消息、业务源码快照、运行树和检查点保存在本地并由清单绑定；选定提交包含源码、协议、公开结论、机制分析与归档清单。Root 授权文件、接纳文件和 `final_private_ROOT/` 不进入本代理读取/哈希的公开清单，也不由本提交打包。早期 `BODY_MISMATCH` / `REPLAY_ERROR` 文件是已修复的源码准备诊断，清单单列，不能把它们当作最终实验结果；最终前缀核验见 `PREPARE_STATUS.json` 和各题 `EXACT_REUSE.json`。

失败机制及下一项研究建议见 [FAILED6387_MECHANISM_READONLY.md](FAILED6387_MECHANISM_READONLY.md) 和配套 JSON。后续新机制由 Root 在独立版本中冻结，本目录已获结果保持不变。worktree 保留至 Root 验收、集成并确认归档完整；本交接未修改主线报告或其他实验。

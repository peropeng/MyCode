# 实验13数据与审计附件

- 当前严格状态：**STOP**
- 原编号：`E025`
- 机器资产：`实验/实验13_可见验证命令语义回归预检/`
- 主结论：`结论/结论13_实验13_可见验证命令语义回归预检_STOP.md`

本文件保存详细指标、原结果摘录和审阅证据；研究判断以主结论为准。

## 原实验结果与指标

以下内容直接并入原结果/报告；它们保留当时数字和判断，但最终等级以本文件开头的严格状态为准。

### 来源：旧实验裁决__实验__失败与停止__E025_base_可见验证命令语义回归预检__结果.md

### 可见验证命令语义回归预检结果：NO-GO

#### 结论

本轮冻结协议没有达到预检门槛，必须标记为 `25_NO-GO_可见验证命令语义回归预检`。
这不是把失败命令当作绿色，也没有用 AST 差异或哈希变化替代验证命令：候选提取
成功，但本地真实复跑没有得到一个 clean 绿色任务，因此语义闭环为 0，不能声称
第三类“编译通过但局部测试/语义回归失败”已经得到可用证据。

#### 候选提取

| 项目 | 数量 |
|---|---:|
| SFT 轨迹行 | 491 |
| SWE-Gym metadata 行 | 2,438 |
| 通过题面匹配且有候选的独立任务 | 105 |
| 候选仓库 | 8 |
| 实际运行（每仓库最多 10 个，固定选择） | 58 |
| 实际运行命令类型 | Python 57，mypy 1 |

候选的必要条件是：轨迹中同一条命令在生产编辑前后均有可见的 exit/return code
0 观察，且编辑路径不是测试、fixture 或复现脚本。命令全文不写入报告；每个候选
的 `command_hash`、`observation_hash` 和路径哈希在 `results.json` 中逐条保存。

#### 真实复跑结果

| 门槛 | 结果 | 冻结要求 | 判定 |
|---|---:|---:|---|
| clean 稳定绿色独立任务 | 0 | ≥15 | 未通过 |
| clean 绿色覆盖仓库 | 0 | ≥3 | 未通过 |
| clean→semantic-fail→revert-clean 闭环 | 0 | ≥10 | 未通过 |
| 可接受闭环的编译检查 | 无候选闭环 | 全部通过 | 未形成 |
| 泄漏审计 | PASS | 全部通过 | 通过 |

58 个运行候选的原因分解如下。计数之和为 58，未隐藏环境失败：

- `local_pre_failed_missing_dependency`: 33；
- `local_pre_failed_missing_command_or_file`: 5；
- `local_pre_failed_runtime_error`: 3；
- `replay_error_unsupported_edit`: 15；
- `replay_error_str_replace_count`: 1；
- `replay_error_create_existing`: 1。

本机只有 Python 3.9.6 和 parquet 读取依赖；未发现可复用 venv。直接探测的
`boto3`、`moto`、`monai`、`pandas`、`dask`、`dvc`、`conan`、`pydantic`、
`numpy`、`pytest`、`mypy` 均不可导入。脚本只在临时 workspace 提供了 `python`
到当前 `python3` 的本地别名，未联网安装或修改系统；缺少第三方包仍按命令实际
非零处理。15 个编辑应用失败和 2 个文本/创建冲突也保留为可审计的重放失败，
没有将它们降级成绿色。

#### 泄漏与数据审计

- SFT 只物化 `messages`；metadata 只物化 `instance_id/repo/base_commit/problem_statement`。
- 候选、排序和语义变体只依赖轨迹 action/observation 及允许的检查点字段。
- 语义变体仅在边界编辑实际引入的代码片段中尝试，避开字符串/注释并要求整文件
  `ast.parse` 成功；没有候选进入闭环，所以没有把编译或差异伪装成故障结果。
- 输出不含原始题面、命令、观察、路径或代码；只含哈希、返回码、长度和失败类别。
- `results.json` 的 `leakage_audit.status` 为 `PASS`，但它不改变整体 NO-GO。

数据哈希：SFT `ea4bf37de020e165c5210bedddeef523d8834a89a35a8c65fec24f76f0eae4f1`；
SWE-Gym metadata `60569cea74bb281f7a5579467436a2bc1932c6e0c5f2f7fa0d084392abd9ad97`。
八个仓库 HEAD 和每个命令哈希见 `results.json`。

#### 最小修复建议

1. 恢复与轨迹一致的、版本固定的 OpenHands/SWE-Gym testbed 或本地 venv，至少提供
   轨迹命令涉及的仓库依赖和 `pytest/mypy` 入口；不在本实验中联网盲装。
2. 对 15 个编辑应用失败样本补充可验证的 action 状态（或明确排除需要 shell 写入
   的轨迹），再从同一 `base_commit` 重放；不可应用的样本不能进入闭环分母。
3. 环境修复后使用 `复现命令.md` 原命令重跑；只有达到 15/3 和 10 个闭环才可把
   目录改回 GO 候选，否则继续保持 NO-GO。

## 历史综合复盘

### 既有复盘

- **E025 可见验证命令语义回归预检：**回答命令/测试“可见”不等于语义 oracle；不能由 AST/命令通过判定责任；只能说明验证命令语义和 oracle 资格需单独审计。缺真实任务和强基线，STOP。

## 来源索引

- `旧实验裁决__实验__失败与停止__E025_base_可见验证命令语义回归预检__结果.md`

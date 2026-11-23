# 实验03数据与审计附件

- 当前严格状态：**STOP**
- 原编号：`E012`
- 机器资产：`实验/实验03_多类型故障区间与责任动作定位/`
- 主结论：`结论/结论03_实验03_多类型故障区间与责任动作定位_STOP.md`

本文件保存详细指标、原结果摘录和审阅证据；研究判断以主结论为准。

## 原实验结果与指标

以下内容直接并入原结果/报告；它们保留当时数字和判断，但最终等级以本文件开头的严格状态为准。

### 来源：旧实验裁决__实验__失败与停止__E012_base_多类型故障区间与责任动作定位__C-mutant-preflight结果.md

### C 类生产 diff mutant → 可见探针第三轮预检结果

#### 结论

本轮只验证 C 类“生产文件最小语义 mutant 是否能被固定可见探针稳定区分”，不是冻结的 P1 全量实验。正式结果文件为 `c_mutant_preflight_results.json`：共尝试 70 条，接受 1 条，覆盖 1 个仓库，因此按冻结门槛诚实记为 `NO-GO-C-MUTANT-PREFLIGHT`；未运行 RQ1/RQ2 全量。

唯一接受实例是 `pydantic__pydantic-8004`（`pydantic/pydantic`）。它满足同一生产 mutant 与同一探针的连续序列：clean 2 次 `rc=0`，mutant 2 次 `rc!=0` 且编译通过，revert 2 次 `rc=0`；探针文件 hash 在各阶段保持不变，revert 后仓库 HEAD 与状态审计恢复一致。

#### 固定结果摘要

| 项目 | 结果 |
|---|---:|
| 候选数 / 尝试数 | 70 / 70 |
| 接受数 | 1 |
| 覆盖仓库数 | 1（`pydantic/pydantic`） |
| 目标门槛 | 至少 15 条、至少 5 个仓库 |
| 结论 | `NO-GO-C-MUTANT-PREFLIGHT` |

排除原因按正式 JSON 记录为：`clean_not_stably_green=38`、`clean_probe_nonzero=38`、`fault_not_stably_red=3`、`clone_failed:CalledProcessError=4`、`no_applicable_mutant=17`、`mutant_compile_failed=4`、`probe_script_missing=1`、`mutant_application_failed=2`。这些计数不通过调阈值、标签匹配或结果后搜索改写。

#### 环境与审计

- 基础提交：`main@11786cd7bd2437a9f4db5f33ffb0dfd420229863`。
- 驱动解释器：Python 3.9.6；探针解释器为 worktree-local C 预检环境中的 Python 3.12.13。
- 接受实例的 base commit：`0a2377e6eba9127e5debe5fda96dfd64a5b2030f`。
- 接受实例的可见命令：`python3 reproduce.py`；生产 mutant 为目标返回表达式替换为 `return None`。
- 生产路径 hash、探针路径 hash、探针命令 hash、环境 hash、repo HEAD/status 与 stdout/stderr hash 均写入正式 JSON。
- 检测器泄漏审计：未读取 `resolved`、`test_patch`、`FAIL_TO_PASS`、mutant 位置/类型或最终结果作为选择特征。

#### 复现

```bash
python3 -m py_compile run_c_mutant_preflight.py test_c_mutant_preflight.py
python3 -m unittest discover -s . -p 'test_*.py' -v
python3 run_c_mutant_preflight.py --config config.json \
  --output c_mutant_preflight_results.json \
  --runtime c_mutant_runtime/final2 \
  --venv .venv-c-preflight
```

完整 JSON 是本报告的唯一正式机器结果；`c_mutant_preflight_results_small*.json` 与 `c_mutant_preflight_results_moto*.json` 均为临时试跑产物，已删除并加入忽略规则。

### 来源：旧实验裁决__实验__失败与停止__E012_base_多类型故障区间与责任动作定位__C-preflight结果.md

### C 类可执行性补充预检（第二轮，停止于证据整理）

#### 范围与停止条件

本轮只检查 C 类 clean/fault 成对可执行性，不修改 A/B、故障定义、阈值、Gate 或 RQ1/RQ2 实验逻辑；未达到 15 条、5 个仓库前不运行 45-task 全量。候选必须是轨迹中被重复 visible command 调用的非生产 Python 脚本，clean endpoint 两次稳定通过，注入 `return None` 或编译通过的运行失败变体后同一命令两次稳定失败。

#### 环境与分层安装

- 使用 worktree-local `.venv-c-preflight`，创建解释器为 `/Users/peroyang/.local/bin/python3.12`，版本 `Python 3.12.13`。
- 第一层安装：pip/setuptools/wheel、pytest。
- 第二层按首个真实 stderr 的缺失模块安装：`boto3`、`numpy`、`PyYAML`、`patch-ng`、`typing_extensions`、`pandas`、`pydantic`。未安装仓库全量依赖或系统级包。
- 运行脚本：`run_c_preflight.py`；结果分别保存为 `c_preflight_baseline.json`、`c_preflight_minimal.json`。

#### 候选与失败分解

去重后 41 个候选，分布为 moto 20、MONAI 6、dvc 6、pandas 3、conan 3、mypy 2、pydantic 1，覆盖 7 个仓库。

两层运行均为 41 attempts、0 accepted：

| 层 | clean replay 失败 | clean visible command 失败 | clean compile 失败 | accepted |
|---|---:|---:|---:|---:|
| pytest-only baseline | 24 | 16 | 1 | 0 |
| minimal dependency layer | 24 | 16 | 1 | 0 |

对 41 个候选做无命令回放核验后，17 个窗口可完整重放，23 个因 `ValueError`、1 个因 `FileNotFoundError` 在 clean replay 被排除。17 个可重放 endpoint 在 baseline 下 visible command 均稳定 `rc=1`，没有 clean pass，因此没有进入 fault pair；不能把这些失败重标成 C fault。

首轮 stderr 的真实缺依赖证据：

- moto：`ModuleNotFoundError: No module named 'boto3'`；
- MONAI：`No module named 'numpy'`；
- dvc：`No module named 'yaml'`；
- conan：`No module named 'patch_ng'`；
- mypy：`No module named 'typing_extensions'`。

#### 关键执行链阻塞

第二层安装后结果仍为 0/41，但运行后核验发现 `run_experiment.run_visible_command` 使用 `bash -lc`，本机 login shell 会把 `PATH` 重置到 `/usr/bin/python3`（Python 3.9.6），所以 `python3` 命令没有使用 `.venv-c-preflight/bin/python`；直接验证为：

```text
env PATH="<venv>/bin:$PATH" bash -lc 'which python3; python3 --version'
/usr/bin/python3
Python 3.9.6
```

因此 `c_preflight_minimal.json` 的 0/41 只能作为“执行链仍无 accepted pair”的证据，不能作为依赖安装后 C 的科研 NO-GO 结论，也不能声称 Python 3.12 依赖已被有效验证。`run_c_preflight.py` 已补上绝对 venv Python 命令替换以供后续审阅/复跑，但遵循主线程指令，本轮不再试跑或继续安装。

#### 结论

本轮尚未得到任何 clean/fault C pair，更不满足 15 条/5 仓库；不运行全量。基于真实候选回放与失败分解，本轮记为 P1 C-preflight 第二次无进展，交由主线程触发 Sol/high 独立审阅。当前结果不改变 P1 方向，也不宣称依赖校准后的最终 C 能力。

#### 复现命令

```bash
python3.12 -m venv .venv-c-preflight
.venv-c-preflight/bin/python -m pip install --upgrade pip setuptools wheel
.venv-c-preflight/bin/python -m pip install pytest
.venv-c-preflight/bin/python -m pip install boto3 numpy PyYAML patch-ng typing_extensions pandas pydantic
python3 -m py_compile run_experiment.py test_experiment.py run_c_preflight.py
python3 -m unittest discover -s . -p 'test_*.py' -v
python3 run_c_preflight.py --config config.json --output c_preflight_baseline.json --runtime c_preflight_runtime/baseline --venv .venv-c-preflight --profile pytest-only --repeats 2
python3 run_c_preflight.py --config config.json --output c_preflight_minimal.json --runtime c_preflight_runtime/minimal --venv .venv-c-preflight --profile pytest+boto3+numpy+pyyaml+patch-ng+typing_extensions+pandas+pydantic --repeats 2
```

### 来源：旧实验裁决__实验__失败与停止__E012_base_多类型故障区间与责任动作定位__结果.md

### P1 protocol-v2 preflight 结果（诚实 NO-GO）

#### 运行身份

- Worktree：`/Users/peroyang/My/MyWork/worktrees/0820-p1-multifault`
- 基础分支：`main`，基础提交 `11786cd7bd2437a9f4db5f33ffb0dfd420229863`
- 执行分支：`exp/0820-p1-multifault`
- 本报告是 15-task preflight，不是 45-task 冻结全量；C 尚未得到可接受样本，因此没有运行全量。
- 结果文件：`preflight_results.json`

#### 冻结协议 v2

本轮在扩样前冻结了 `方案.md` v2 与 `config.json`：

- RQ1 使用单遍、前缀可见的在线 monitor；主指标为成对 `Verified/Effective Interval Recall`。fault 区间必须覆盖责任动作、满足宽度门槛，且同 instance 的 clean 对照不能告警。没有可执行失败证据的固定窗口/随机窗口按 clean 误报处理。
- RQ2 的 `fixed/random/shuffled/predicted + uniform/adaptive` 都使用同一个 `replay_probe_budget=3`；`full_trace_per_step` 仅是高成本上界。
- C 只能使用轨迹中重复出现、clean endpoint 实际通过的 Python 可见命令；fault 由 `return None` 或编译通过的运行失败变体注入，最终必须由该 visible command 失败验收，不能由 AST 结果替代。
- A/B 的干预不执行与其探针类型无关的 visible command；这修复了首轮 7 条中 2 个干预失败的实现不对称。

#### 数据与可复现性

- SFT 行数：491；SWE-Gym 行数：2438。
- SFT SHA-256：`ea4bf37de020e165c5210bedddeef523d8834a89a35a8c65fec24f76f0eae4f1`。
- SWE-Gym SHA-256：`60569cea74bb281f7a5579467436a2bc1932c6e0c5f2f7fa0d084392abd9ad97`。
- 预检候选（执行前）：moto 51、pandas 43、pydantic 4、conan 10、dvc 17、MONAI 29、dask 15、mypy 18。
- 依赖环境未安装 mypy/moto/MONAI/pandas/dask/dvc/conan/pydantic 等大依赖；未为了本轮结果安装它们。

#### 本轮执行结果

请求 15 条（每类 5 条），按冻结冗余选择 60 条尝试；实际接受 9 条、覆盖 6 个仓库：

| 类型 | 接受数 | RQ1 coverage | RQ1 Effective Recall | RQ2 Predicted+Adaptive | 闭环 |
|---|---:|---:|---:|---:|---:|
| A syntax/import | 5 | 1.000 | 1.000 | 1.000 | 1.000 |
| B tool/file-state | 4 | 1.000 | 0.750 | 1.000 | 1.000 |
| C semantic regression | 0 | — | — | — | — |
| 合计 | 9 | 1.000 | 0.889 | 1.000 | 1.000 |

排除计数（候选级；同一候选可能贡献多个原因）：`clean_endpoint_visible_command_failed=9`、`clean_endpoint_not_executable=26`、`clean_endpoint_replay_failed=17`、`checkpoint_not_clean=25`、`checkpoint_replay_error=19`、`checkpoint_tool_error:ValueError=19`、`checkpoint_compile_failed=6`、`clean_endpoint_compile_failed=4`。这些是执行/探针可用性证据，不把不可运行命令降级为 A/B，也不把 C 改成标签匹配。

RQ1 的 adaptive probe 为 0.889，fixed-periodic 为 0.778，相对提升 14.3%，但 paired bootstrap 95% CI 为 `[0.0, 0.3333]`，clean false-alarm 为 0.111，因而尚未过 Gate。fixed-window 虽 raw coverage 为 1.000，但 clean false-alarm 为 1.000，Effective Recall 为 0，未被允许免费得分。

RQ2 的 predicted+uniform 与 predicted+adaptive Verified Yield 都为 1.000；实际平均 replay probes 分别为 2.778 与 1.667，均未超过共享上限 3。二者无增量（相对最强非 Oracle 基线 0，CI `[0.0, 0.0]`），这是当前小样本的真实结果，不通过成本口径规避。

#### C 阻塞与下一步边界

首轮 C=0 的实现原因已定位并修复：gate_a 将测试/复现脚本标成 `code=False`，候选提取器曾错误地把它们排除。修复后静态得到 904 个 Python 窗口、389 个非生产脚本窗口、213 个带重复 visible command 的窗口，去重为 41 个 instance 级非生产可见候选（至少 7 个仓库）。本轮仍未接受 C，说明这些候选必须逐个在 clean/fault pair 中验证；候选数量本身不能证明达到每类 15 条。下一步仅允许继续做 C 的真实命令 preflight/依赖可用性分解，不安装大依赖、不改故障定义、不运行 45-task 全量，直到主线程审阅。

#### 泄漏审计与复现命令

检测器只消费动作、diff、工具结果、仓库状态、`py_compile`、导入解析和 visible command 结果；未读取 `resolved`、accepted patch、test patch、FAIL_TO_PASS、注入位置/类型或最终结果。所有 9 条 accepted record 的 leakage audit 通过。

```bash
python3 -m py_compile run_experiment.py test_experiment.py
python3 -m unittest discover -s . -p 'test_*.py' -v
python3 run_experiment.py --config config.json --output preflight_results.json --preflight
```

结论：`NO-GO (preflight only)`。样本数、类型覆盖、clean FPR、RQ1 bootstrap、RQ2 增益及 C 支撑均不足，不能外推为 P1 研究 Gate 通过。

### 来源：旧实验裁决__实验__失败与停止__E012_多类型故障区间与责任动作定位_分支快照_851989c__C-native-test-preflight结果.md

### C 类生产 mutant → 仓库原生测试开发切片结果

结论：`STOPPED_BEFORE_FULL_RUN`。开发切片以 moto、pydantic、dask、mypy、conan 各最多一条为上限；实际候选中 conan 没有 C production-edit 候选。其余四仓库各一条均已完成真实工作树物化、生产 diff 符号提取与仓库原生测试选择。只有 moto 找到未被轨迹触碰的精确符号测试节点，但其 clean 运行返回 `rc=4`，因此 clean-green 仓库数为 0，未达到至少 3 仓库的提升门槛，严格停止，未运行全候选 clean2 → mutant2 → revert2 阶段。

正式机器结果为 worktree-local ignored 文件 `c_native_test_preflight_results.json`，包含每条选择（生产路径、符号、测试文件、node、精确命中数、路径距离和实例哈希平局数）、真实退出码、stderr 分类/摘录/hash、环境与包清单 hash、测试 hash、运行前后 production diff hash。

| 仓库 | 结果 | 原因 |
| --- | --- | --- |
| getmoto/moto | clean 非绿 | 选中 `tests/test_core/test_responses_module.py::TestResponsesModule::test_moto_as_late_as_possible`，真实 `pytest` 返回 `4` |
| pydantic/pydantic | 排除 | production diff 的 `inspect_namespace` 没有在未触碰仓库测试 node 中精确出现 |
| dask/dask | 排除 | 窗口物化后没有 production Python diff |
| python/mypy | 排除 | production diff 符号没有在未触碰仓库测试 node 中精确出现 |
| conan-io/conan | 排除 | 冻结的 70 条 C production-edit 候选中没有该仓库候选 |

M1 判定没有使用词法扫描：词法/AST 精确符号只用于事前固定仓库测试，结果判定只读取真实 exit code、运行前后 filesystem diff 与探针 hash delta。选择阶段未读取 `test_patch`、`FAIL_TO_PASS`、`resolved` 或任何未来结果。

复现命令：

```bash
python3 -m py_compile run_c_native_test_preflight.py test_c_native_test_preflight.py
python3 -m unittest test_c_native_test_preflight.py -v
python3 run_c_native_test_preflight.py --config config.json \
  --output c_native_test_preflight_results.json \
  --runtime c_native_test_runtime/dev --venv .venv-c-preflight --timeout 120
```

## 历史综合复盘

### E012 多类型故障区间

- **口语总结：**多类故障预检能告诉我们探针边界，但把多类型预检写成正式区间检测还太早。
- **回答了什么：**语法/文件/验证探针的接口和故障类别可编码，C-mutant/C-native 的资格问题可自动记录。
- **不能说明什么：**不能说明多类型自然故障已覆盖，也不能说明区间边界比周期基线好。
- **只能说明什么：**只能说明预检合同和负证据，属于资产/方法准备而非 RQ1 Go。
- **为何失败/降级：**没有独立自然任务和足够状态证书，且不同分支有不同快照。
- **Sol 审核办法：**把探针事实、语义 Judge 和责任定位拆开；预先冻结漏斗门。后续仍因资产不足归档。
- **可复用价值：**故障类 A/B/C 的契约字段、clean/fault 双门、泄漏字段黑名单。

## 来源索引

- `旧实验裁决__实验__失败与停止__E012_base_多类型故障区间与责任动作定位__C-mutant-preflight结果.md`
- `旧实验裁决__实验__失败与停止__E012_base_多类型故障区间与责任动作定位__C-preflight结果.md`
- `旧实验裁决__实验__失败与停止__E012_base_多类型故障区间与责任动作定位__结果.md`
- `旧实验裁决__实验__失败与停止__E012_多类型故障区间与责任动作定位_分支快照_851989c__C-native-test-preflight结果.md`

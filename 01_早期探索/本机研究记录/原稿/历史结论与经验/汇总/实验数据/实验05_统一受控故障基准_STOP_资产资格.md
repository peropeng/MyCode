# 实验05数据与审计附件

- 当前严格状态：**STOP（资产资格）**
- 原编号：`E014`
- 机器资产：`实验/实验05_统一受控故障基准/`
- 主结论：`结论/结论05_实验05_统一受控故障基准_STOP_资产资格.md`

本文件保存详细指标、原结果摘录和审阅证据；研究判断以主结论为准。

## 原实验结果与指标

以下内容直接并入原结果/报告；它们保留当时数字和判断，但最终等级以本文件开头的严格状态为准。

### 来源：旧实验裁决__实验__开发证据__E014_base_统一受控故障基准__结果.md

### Phase0 环境资格检查结果

本轮实际运行时间为 `2026-08-20T06:28:08Z` 至 `2026-08-20T06:32:14Z`。判定只报告机械资格事实，不外推研究结论。

- 候选顺序严格为：pydantic、dask、conan、dvc、mypy、MONAI、pandas、moto。
- 8/8 均从固定 SHA 建立 clean detached worktree，安装命令返回码均为 0；dirty source 的原始 status 完整保存在 `manifest.json`，且所有 source status 前后哈希一致。
- qualified 数量为 **1/8**，唯一 qualified 为 `moto`：collect-only 返回码 0，固定 node 三次测试返回码均为 0，测试时长分别为 0.679s、0.590s、0.570s，source/worktree tracked status 未改变。
- 失败候选均在固定 node 的 collect-only 阶段停止：pydantic、dask、mypy 为仓库 pytest 配置引用的未安装插件参数；conan 缺少 `webtest`；dvc 缺少 `dvc_ssh`；MONAI 固定 node 未找到匹配测试；pandas editable build 缺少 `ninja`。这些失败均只记录，不追加依赖、不替换 node。
- 因 qualified 数量少于 5，本轮在 Phase0 诚实停止；这是环境合同预检，不是研究 Gate；没有运行故障注入、模型/API 调用、Phase1 或正式 Gate。
- 逐候选命令、返回码、超时、摘要、SHA-256、Python/环境信息和依赖声明哈希以 `results.json`、`manifest.json` 为准；源仓库泄漏审计见 `leakage_audit.json`。

### 来源：旧实验裁决__实验__开发证据__E014_base_统一受控故障基准__结果_round2.md

### Phase0 Round2 环境资格结果

本文件只报告固定环境合同的执行事实，不声明研究 Go/No-Go，不运行故障注入、模型/API、Phase1 或正式研究 Gate。

#### 总体结果

- 候选总数：8；顺序保持为 pydantic、dask、conan、dvc、mypy、MONAI、pandas、moto。
- 8/8 的 source SHA 与配置中的 expected SHA 一致；source 状态前后哈希未发生变化。
- 5/8 通过资格条件：安装完成、固定 node collect 返回 0、随后连续 3 次固定测试返回 0、source/worktree tracked status 未改变。
- qualified 候选：pydantic、conan、mypy、MONAI、moto。
- 所有候选均执行到其合同允许的停止阶段；没有因达到 5 个 qualified 而提前跳过后续候选。

#### 逐候选事实

| 候选 | 固定 node | 安装/收集/测试结果 | 资格事实 |
|---|---|---|---|
| pydantic | `tests/test_version.py::test_version_attribute_is_present` | 两条安装命令均 rc=0；collect rc=0；测试 rc=[0,0,0] | qualified |
| dask | `dask/tests/test_config.py::test_canonical_name` | 安装 rc=[0,0]；collect rc=3；断网 sandbox 下 `pytest-rerunfailures` 尝试绑定 `127.0.0.1` 被拒绝 | 未通过，停止于 collect |
| conan | `test/unittests/client/tools/files/rename_test.py::TestRename::test_rename_empty_folder` | 安装 rc=[0,0]；collect rc=0；测试 rc=[0,0,0] | qualified |
| dvc | `tests/unit/test_config.py::test_to_relpath` | 安装 rc=[0,0]；collect rc=3；断网 sandbox 下 `pytest-rerunfailures` 尝试绑定 `127.0.0.1` 被拒绝 | 未通过，停止于 collect |
| mypy | `mypy/test/test_config_parser.py::FindConfigFileSuite::test_no_config` | 安装 rc=[0,0]；collect rc=0；测试 rc=[0,0,0] | qualified |
| MONAI | `tests/utils/test_version.py::TestVersionCompare::test_compare_leq_00_1_6_0` | 安装 rc=[0,0]；collect rc=0；测试 rc=[0,0,0] | qualified |
| pandas | `pandas/tests/config/test_config.py::TestConfig::test_api` | 工具安装 rc=0；固定 editable 安装 rc=1，Meson-Python 报告找不到 `meson` executable；按合同停止，未收集/测试 | 未通过，停止于安装 |
| moto | `tests/test_core/test_config.py::test_whitelist` | 安装 rc=[0,0]；collect rc=0；测试 rc=[0,0,0] | qualified |

#### 泄漏与范围审计

`leakage_audit_round2.json` 记录：`all_source_status_unchanged=true`、`sensitive_values_recorded=false`、`model_or_api_calls=false`、`phase1_executed=false`、`formal_gate_executed=false`。运行时写入仅限被忽略的 `runtime_round2/`；原始命令摘要经过脱敏并保留 SHA-256。

逐命令记录、环境 freeze、依赖声明哈希、测试文件哈希、source/worktree 前后状态和完整候选顺序，以 `manifest_round2.json`、`results_round2.json` 和 `leakage_audit_round2.json` 为准。

### 来源：旧实验裁决__实验__开发证据__E014_统一受控故障基准_分支快照_a580f43__结果.md

### 执行结果

首次执行（2026-08-20，修复 venv 隔离后）结论：`STOP_INSUFFICIENT_QUALIFIED_REPOS`。固定池的 10 个本地真实 Git 仓库均在环境创建前冻结为干净状态，但所配置的既有官方测试节点在 3 次 clean 尝试中均返回 4（收集/节点不可用），故没有一个可被冻结为 3/3 clean 参照；没有运行 Phase 1 的 15 例，也没有运行正式 Gate。

机器可读证据为 `manifest.json` 与 `results.json`。每个仓库的 SHA、Python、lock hash 和失败原因均被保留；本次失败原因不是 mutation 成绩，故没有发生换库。先前错误写入目标仓库的 venv 已隔离至 `/tmp/trackb-venv-quarantine.QMSxBm`，可恢复；当前脚本只使用本实验目录的私有环境。

## 历史综合复盘

### E014 统一受控故障基准

- **口语总结：**基准把场地画平了，但没有替方法跑出冠军。
- **回答了什么：**统一仓库、manifest、故障合同和 leakage audit 可以重复使用。
- **不能说明什么：**不能说明某个 detector 优于周期基线或真实 Agent 可泛化。
- **只能说明什么：**只能说明基准与输入边界准备到什么程度。
- **为何失败/降级：**同名 base/分支快照、资产和运行缓存有差异，独立确认未完成。
- **Sol 审核办法：**固定 commit、任务独立性、source hash 和 forbidden fields；保留为开发证据。
- **可复用价值：**manifest、任务/仓库分组、泄漏审计字段。

## 来源索引

- `旧实验裁决__实验__开发证据__E014_base_统一受控故障基准__结果.md`
- `旧实验裁决__实验__开发证据__E014_base_统一受控故障基准__结果_round2.md`
- `旧实验裁决__实验__开发证据__E014_统一受控故障基准_分支快照_a580f43__结果.md`

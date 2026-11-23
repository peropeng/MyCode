# 结论35：方向A动作效果验证与恢复——实时 Gate 记录

> 状态：**STOP（2026-08-21 最终裁决）**
> 建立时间：2026-08-21  
> 研究方向：《面向工具增强智能体的动作效果验证与故障恢复方法研究》  
> 证据原则：只记录当前工作区可复验结果；计划、论文声称、未提交 WIP 和 LLM 解释均不算本地实验结果。

## 0. 当前总览

| 项目 | 当前状态 | 证据等级 |
|---|---|---|
| 方向 A Gate 0：正式方向与公开资产 | **STOP** | AppWorld 引擎与 147 个 train/dev task 可运行，但冻结的公开 train/dev GPT-4o 动作级轨迹不存在；替代 test 输出无 `environment_io.md`，不满足数据合同 |
| 方向 A Gate 1：动作效果合同 | **STOP / 未进入自然 30-task Gate** | 构造合同子门 `GO` 不能替代自然数据；SyncBench bounded replay 与 AppWorld 最终资产资格均未取得稳定自然动作 Oracle |
| RQ1：动作效果验证 | **STOP** | Gate0/1 未通过，不进入方法 Gate |
| RQ2：选择性恢复 | **STOP** | 没有合格自然动作证据，不能运行 Oracle Bridge |
| 两章总体 | **STOP** | 独立复审冻结条件规定 AppWorld 任一门失败即永久停止 A；不得再以构造任务补位 |

## 1. 冻结的首轮判据

### Gate 0

- 至少 3 篇正式 CCF A 论文直接覆盖动作效果验证或执行错误恢复；
- 至少 1 个可下载、可执行 benchmark；
- 代码、数据和许可证分别核验，未知字段写 `UNKNOWN`；
- 论文存在但代码占位不得写成可复现。

### Gate 1

- 至少 30 个独立 task；
- 至少 3 个仓库或执行环境；
- 至少 3 类动作效果；
- 至少 70% 样本拥有稳定 `pre/action/post/effect` Oracle；
- clean replay 一致率至少 90%；
- LLM 自评不能作为唯一 Oracle；
- 构造与自然样本必须分开统计。

### Gate 3：两章桥接

- 先比较 `No / Random / Oracle Effect Evidence`；
- Oracle 相对最强公平对照的 Recovery Success 至少提升 10%，且任务级 paired bootstrap 95% CI 下界大于 0；
- Oracle 无增益直接判方向 A 的“验证→恢复”桥接 NO-GO；
- 之后比较 `Shuffled Predicted / Predicted / Oracle`，Predicted 必须胜 No、Random、Shuffled，不能用 Oracle 冒充第一章输出。

## 2. 2026-08-21 环境记录

### Git 与执行隔离

- 基础仓库：`/Users/peroyang/My/MyWork/毕设实验`
- 基础分支：`main`
- 基础提交：`1c9fd1264a55aea1716bb3a6b1eed09c17a04a05`
- 执行分支：`exp/0821-direction-a-gate01`
- 独立 worktree：`/Users/peroyang/My/MyWork/worktrees/0821-direction-a-gate01`
- 执行线程归属：仅修改 `实验/实验35_方向A动作效果验证Gate0Gate1/`

### Docker 安装与验证

- 安装命令：`brew install docker colima`
- Docker client：`29.7.2`
- Docker server：`29.5.2`
- Colima：macOS Virtualization.Framework，`aarch64`，Docker runtime；启动配置 4 CPU、8 GiB 内存、40 GiB 请求磁盘。
- 第一次 VM 镜像下载因 `unexpected EOF` 失败，第二次成功；属于网络重试，不是研究结果。
- 第一次容器拉取因 VM `/etc/resolv.conf` 指向不存在的 `systemd-resolved` stub 而失败；已在明确目标 `/etc/resolv.conf` 写入 `1.1.1.1`、`8.8.8.8` 修复。
- 最终 smoke：`docker run --rm hello-world` 返回码 0，并成功输出 `Hello from Docker!`。

裁决：**Docker 环境 GO（基础设施）**。只说明容器运行时可用，不说明任何论文方向或方法可行。

## 3. Gate 0 已取得的外部身份证据

以下仅是论文正式身份核验，不等于代码与实验复现完成：

1. **VeriGUI**：ACL Anthology 显示 `2026.acl-long.1335`，ACL 2026 Volume 1 Long，论文任务直接涉及 action-effect verification、failure recognition 与 self-correction。
2. **SyncMind**：PMLR 显示 ICML 2025 正式论文，定义 out-of-sync recovery；官方摘要称 SyncBench 有 24,332 个实例、21 个 GitHub 仓库和可执行验证测试，并给出公开项目入口。
3. **Fission-GRPO**：ACL Anthology 存在 `2026.acl-long.1880` 正式页；仓库是否仍为占位、训练数据是否开放尚待本地 manifest 核验。
4. **GuardAgent**：PMLR 存在 ICML 2025 正式页；代码、数据和根许可证尚待本地 manifest/smoke 核验。
5. **Process-Centric Analysis**：正式身份与本地 artifact 边界已有历史核验；本轮仍需把代码 commit、许可证和 smoke 状态写入统一 manifest。

当前 Gate 0 裁决：**资产身份与最低 smoke 子门 GO，方向 Gate0 CONDITIONAL**。5 个公开仓库已完成 clean probe，Docker 可执行；但 SyncMind/GuardAgent 根许可证为 `UNKNOWN`，且本轮没有完成任一公开 benchmark 的端到端复现。

## 4. 实验轮次与进展计数

| 轮次 | 目标 | 当前结果 | 是否科研进展 | 下一动作 |
|---:|---|---|---|---|
| 1 | 方向 A Gate 0/1：公开资产与 30-task 动作效果合同 | Gate0 CONDITIONAL；Gate1 CONDITIONAL | 有：构造合同证明接口可执行，同时明确自然资产缺口 | 在 3 个 SyncBench 仓库中物化自然任务并执行 test-before → action → test-after |
| 2 | SyncBench 公开动作 bounded replay | 子探针 STOP；方向 Gate1 仍 CONDITIONAL | 取得负证据：公开数据字段不足，唯一公开 patch 候选无稳定 Oracle | 等独立方向审阅；不继续用 gold_code 或构造 patch 扩样本 |
| 3 | AppWorld 最终资产资格与 10-task smoke | Gate0 STOP；Gate1 未进入；方向 A 永久 STOP | 取得决定性负证据：引擎和 evaluator 可运行，但冻结的公开动作级轨迹资产不存在 | 停止 A，转向 BFCL 接口契约鲁棒性方向 |

“三次实验无进展”按以下口径计数：只有一次完整、预注册、产生可审查结果的实验才计一轮；单纯安装依赖、网络重试或修复 Docker 不计科研实验轮次。连续三轮未改善方向/数据/桥接证据时，委派 Sol Max 做独立方向审阅。

## 5. 轮次 A1 验收证据

- 执行提交：`b32e7afc4d5a0d0bc4f4b9c2d0904337027db222`；Oracle 隔离修正提交：`c4cc9db1be961299e31d048647fb58b5af8c9558`；主线程审查后分别 cherry-pick 为 `bbec486`、`3f44459`。
- 构造合同：30 个独立构造 task、3 个本地执行环境抽象、13 类 effect；稳定 Oracle 为 30/30，clean replay 为 30/30。因此只有 **constructed contract subgate=GO**。
- SyncBench：30 条样本来自 16 个仓库，当前仅元数据可解析；动作级 effect Oracle 为 0/30，clean replay 为 0/30。因此自然 Agent 数据资格尚未成立。
- 旧 E02/E03 候选：43 条，按当前合同的 stable Oracle 与 qualified row 均为 0；不能用旧受控结果填补本轮 Gate1。
- 初始实现曾由 filesystem online probe 直接读取 evaluator-only `expected_effect` 选择目标路径。主线程拒绝验收；修正后 filesystem 统一采集完整临时目录，JSON 只读 action 声明路径，CLI 只执行 action 声明脚本，Gold 仅在 observation 冻结后比较。
- 主线程复验：构造合同仍为 30/30 Oracle、30/30 replay；隔离测试 3/3 通过，`py_compile`、`git diff --check` 通过；复验后 worktree clean。

当前科研裁决：**方向 A 的验证接口可执行，但真实任务数据仍是硬阻塞，尚未取得任一章节 GO。** 下一轮必须直接消除自然 replay 缺口，不能继续扩充构造任务或把工程 smoke 当成方法结果。

## 6. 轮次 A2 验收证据

- 执行提交：`5a8113cd983b332b76eb9370b67732ed465846f6`，主线 cherry-pick 为 `92aa618`。
- SyncBench 300-row CSV 有 repo URL、target commit、文件/测试路径、`original_code`、`gold_code` 和错误摘要，但没有 public action/patch 或 Agent trajectory 字段；Gold 代码不能直接当在线 action。
- bounded discovery 审计 14 条独立性记录，只找到 Requests 的 1 个公共 Git transition，可由 public target→state diff 重建 patch；未达到 30 task、3 repo、3 effect type。
- 该任务两次 Docker replay 均成功物化 commit 并应用相同 SHA256 patch；clean replay 为 2/2。但 pre/post 都因 pytest fixture recursive dependency 出现 harness setup ERROR，稳定 fail→pass Oracle 为 0/2。
- 初版把 0.15s/0.14s 的 pytest wall-clock 差异误判为 replay mismatch，并把 fixture setup error 写成 target test failure。主线程退回后，已规范化 timing，改为 `TEST_HARNESS_ERROR`/`DEPENDENCY_SETUP_FAILED`。
- 子探针裁决为 `STOP`；由于只覆盖 bounded 14-row discovery/1 repo，方向 Gate1 仍为 `CONDITIONAL`，不能外推整个 SyncBench 都不可执行。
- 主线程复验：6/6 单测、`py_compile`、diff check 通过；Gold 字段未进入 runner manifest/online input。

当前科研裁决：**A2 没有消除自然动作合同缺口，也没有取得方法进展。** 若独立审阅不能指出一个已公开 action/patch/test 且可批量物化的新入口，应停止方向 A，而不是继续从 `gold_code` 逆造 action。

## 7. 轮次 A3：AppWorld 最终资格门与最终 STOP

- 独立 Sol Max 复审只允许 A 再执行一次 AppWorld 资格—Oracle 桥实验，并预注册：任何冻结门失败，A 永久 STOP。
- 锁定官方 `stonybrooknlp/appworld` tag `v0.1.3.post1`、commit `66ad8099e12188ece0d3fe45e661dbc01880813b` 与 `appworld==0.1.3.post1`；无付费 API。
- `appworld install`、data 下载、experiment-output 下载均成功；`appworld verify tasks` 对 train+dev 147/147 通过。147/147 task 均有 evaluator/solution/compiled solution/answer 入口；固定 train 5 + dev 5 的 smoke 均能构造 `AppWorld`、保存/恢复 checkpoint，并调用中间态 evaluator。
- 但预注册的两个官方输出目录 `simplified_react_code_agent_gpt-4o-2024-05-13_train` 与 `..._dev` 均不存在。官方 bundle 中虽有 `react_gpt4o_test_normal`（168 task）和 `react_gpt4o_test_challenge`（417 task），但两者 `environment_io` 均为 0，且属于 test split，不能改名替代 train/dev 自然动作轨迹。
- AppWorld 的 scenario ID 也未在可公开提交的 specs/metadata 中序列化；不能读取受保护 generator 源码反推并据此声称 30 个 scenario 独立。
- 因动作级自然轨迹资产合同失败，实验42裁决 `Gate0=STOP`、`Gate1 ready=STOP`，不运行 30-task Gate1，不从 validation solution、ground-truth API calls 或数据库终态逆造动作。
- 提交仅保留版本、哈希、计数、字段存在性和派生裁决；本地 runtime、受保护 bundle 与原始任务内容均忽略。Docker/venv 可运行只算基础设施，不改变科研 STOP。

最终科研裁决：**方向 A Gate0 STOP、Gate1 STOP、RQ1 STOP、RQ2 STOP、两章 STOP。** 这是冻结门槛下的数据资格失败，不代表动作效果验证在一般意义上没有研究价值；它只说明在当前时间、预算、公开资产和禁止 Gold 逆造的约束下，不可作为本毕设主线。

## 8. 绝对禁止的结论

- Docker、checkpoint、JSON schema 或 replay 脚本可运行，不等于 RQ1/RQ2 GO；
- 现有 34 个受控语法案例不能单独满足 Gate 1 的三种效果类型和自然外测；
- 不能用注入位置、private fault step 或最终隐藏测试作为 verifier 输入；
- 不能把资格审计读到的 Gold 泄漏给正式方法；
- Gate 1 不过时，不得以“先训练再补数据”绕过；
- Oracle Bridge 不过时，不得继续用更多 API 或复杂恢复器补救两章关系。

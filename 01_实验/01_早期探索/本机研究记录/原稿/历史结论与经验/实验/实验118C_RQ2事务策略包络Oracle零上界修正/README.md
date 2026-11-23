# Exp118C：RQ2 资源约束事务策略包络

Exp118C 是一次可行性实验，目标是判断 RQ2 是否能形成严格章节 GO；目标不是把预先列出的配置逐一跑完。先保留最大的注册策略包络，再在每个 outer-train 内用 repository-group nested OOF 做唯一的 family/action/coupling 选择，最后对每个 outer fold 解封一次 held 数据。若严格 GO 成立，实验线立即停止；若未成立，只停止这一个固定实现并保留所有真实非误差正提升。

## 冻结模块

B 是一个完整模块：native candidate posterior/full ranking → task×transaction-arm 的预期 Recovery/TNR utility 与 uncertainty → 固定总容量下的确定性 multiple-choice resource allocation → 同一 final checkpoint 的 transactional no-regression。动作语义固定为 Escalate=0、Active=1、Standby=2/3 次；状态不是事后阈值。B standalone 使用 frozen native-B ranking 与预算图。

A 只使用父实验已注册的 strategy-utility route，父 Exp96/97/98 参数不变。A+B 复用同一张 B state/budget map，不二次拟合 B；只在 outer-train nested-OOF 中选择 native fallback、A route、A→B stable dedup、B→A stable dedup 四种有限耦合。A+B 的完整 13 项语义包络是 Escalate0 加上四种路线各自 budget1/2/3。B standalone 单列为 Escalate0 加 protected-native(B) 的 budget1/2/3。A 只有在 A-deletion 与 A-route-shuffle 严格下降时才被视为有贡献。

动作价值不是 held 后验上的手写 top 分数：每个 outer-train 仅用 responsible-only same-fault transaction-pair 标签，按 repository-group nested OOF 交叉拟合 success/TNR/cost utility 与 uncertainty，再拟合 outer-train 模型给 held 任务预测。模型只使用可见、可解释特征（posterior mass、native/route overlap、rollback/executable/state-changing 比例、expected cost 等），所有任务系数均由 outer-train rows 拟合，不注入波形、哈希相位或 task-specific 固定交互。family 用 inner-OOF 的实际 policy value 与预注册安全 tie-break 选择；A route 也来自父注册 strategy utility arm 的同一训练内选择。held 只提供解封前可见候选特征，预测、预算图、13 项包络和所有 controls 在一次 decision digest 中冻结。

## 条件与控制

固定条件包含 no recovery、retry top1、fixed last、uniform equal/comparable budget、A standalone、B、A+B、candidate posterior deletion/shuffle、state/action deletion/shuffle、A deletion/route shuffle、coupling deletion/shuffle、protected random equal actual budget、Oracle。所有排序 tie 只允许 `position + native_feature_vector[8]`；缺失、错误宽度、非数值或非有限值 fail closed。容量是每 fold `2n if even else 2n-1` 的总 attempts 上限，不固定 state quota、不强制浪费；DP 由 outer-train action-value 决定 state counts。deletion/shuffle 控制保持 full 决策的实际 budget multiset 与总 attempts，并报告实际 attempts/cost。

正式指标主项为 task-level Recovery Success Rate，附带三 seed、逐 seed strongest-fair baseline/absolute/relative 与 all-seed-positive、task-group paired bootstrap 95% CI、better/worse/tie、harmful、TNR、attempts/cost、coverage/state 与 repository/failure subgroup。公平基线选择规则在 protocol 中冻结并自动升级到最强同信息基线。

运行时审计从当前 fold source access log 重算 freeze→unseal 顺序；从冻结 assignment rows 重算容量上限和 multiset；正式 cache 必须通过父 E schema、final-checkpoint/fault-anchor、共享 reference 与真实 TNR verifier provenance 校验。TNR 审计要求实际选择候选的 target/TNR/conflict/cost/provenance 字段，不把“所有候选都 TNR pass”误作门槛。若 full 数据的动作/route/coupling/posterior shuffle 语义上退化，control 会返回 `nonidentity=false, degenerate=true`，按注册语义重算并继续产出完整 metrics/STOP；只有字段、multiset、核心 provenance 或 freeze 顺序非法才 fail closed 为 harness error。正式 output/audit 由 exclusive staged pair writer 交叉验证 SHA 后发布，任一步失败清理半成品，最后才写 COMMITTED terminal。

## Exp118C 唯一修正

父 Exp118 的唯一正式调用在 Oracle 记录阶段因 zero-success task 抛出 `CapacityContractError`，形成 `HARNESS_INVALID`；父 claim/terminal 与目录保持只读、原 SHA 不变。Exp118C 只修正这一 harness 语义：held cache 执行并 unseal 后，Oracle 先筛选同时满足 `recovery_success && target_probe_pass && tnr_pass` 的候选。若存在，记录 `order=[position]`、`budget=1`、`success=true`、`oracle_state=OracleResolved`；若不存在，记录空 order、budget=0、attempts/cost=0、`state=Escalate`、`oracle_state=OracleUnrecoverable`、`success=false`。zero ceiling 是合法 Oracle 上界，不是 harness error。

Oracle 只作为 post-unseal upper bound，不进入 method selection、nested OOF 或 decision digest；解封后成功候选身份不进入冻结 digest。Oracle RSR 严格校验为“可恢复 task 数 / 全部 task 数”。synthetic preflight 明确包含至少一个 zero-ceiling task 与可恢复 task，并要求完整产出 metrics 与科学 STOP/GO。不读取 Exp117C outer-held metrics，不做重复资产/hash 检查，不搜索论文，也不调整 Exp96/97/98。

## 唯一正式结果

主线程仅执行一次 canonical `python3 实验/实验118C_RQ2事务策略包络Oracle零上界修正/runner.py --run`，exit 0，未 retry、未 overwrite，`attempts=1`、`status=COMPLETED`。原始 claim/terminal 已以 `COMMITTED` 归档；output SHA 为 `cbb112e21ee6a5a9d7312be3eebdf98c1b915c8991bb6da80955ddc0e4f25f5e`，audit SHA 为 `b3b13a926a59b3db52f06859de26eee00fd2fe320e453af8bd80b575ba8b8031`，claim SHA 为 `332ace13767b97627b3a756978416295a942940dda8e5296579ae76fe0b3eebb`，terminal SHA 为 `d83c465c12bb78c89e1c3df59c57cb4d5f3282a59b9ef745e45fa692749f2e41`。

正式结果是有真实正信号的 scientific STOP，不是 no-go：B RSR 为 `0.2647058823529412`，相对最强公平基线 `+0.03846153846153855`，但 CI lower 为 `-0.1372549019607843`；A+B RSR 为 `0.29411764705882354`，相对 `+0.15384615384615397`，三 seed 全正，但 CI lower 为 `-0.08823529411764706`。Oracle 为 `0.35294117647058826 = 12/34`。harmful 计数为 baseline 28、B 30、A+B 42；candidate-posterior-shuffle 为 `0.0392156862745098`；A deletion、candidate-posterior deletion、coupling deletion 均为 `0.29411764705882354`。state/route/coupling controls overall false，因此 verdict 为 `EXP118C_RQ2_STOP`，`is_full_chapter_go=false`。这些真实正信号必须保留，用于下一模块升级；本次没有章节 GO，也不再重跑 Exp118C。

## 证据状态

`data_seal.json` 已更新为唯一一次 `formal_attempts=1`、`COMPLETED`、scientific STOP，并覆盖 Exp118C 冻结 protocol/README/runner/tests、授权 receipt、离线 preflight 与四个正式原始产物。父 Exp118 的 `HARNESS_INVALID` 文件保持不变；Exp118C 是其 harness-only correction 的一次正式执行，不是重复试验或无效重试。

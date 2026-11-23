# Exp115：RQ2 全排序状态事务恢复升级

当前状态：`PREFLIGHT_BLOCKED_INCOMPATIBLE_EXP112C_PROJECTION`。本目录只完成兼容性诊断、协议封存、测试和非正式 preflight；没有运行 Exp115 formal，没有生成 formal output/audit，也没有重验 Exp113J 资产。

## 阻断结论

Exp112C 的冻结 B2/A+B global full-ranking scorer 不是一个可直接接受任意候选字典的打分函数。它绑定 Exp88/AFTraj trajectory `turns`：17 个匿名结构 descriptor，加 frozen local score、normalized relative position、三阶段 one-hot、anonymous first-appearance role index，形成 23 维 h0；随后在 temporal、same-role、same-full-shape、same-nonempty-action 四个 trajectory graph channel 上做固定两轮 message passing，得到 215 维节点特征。B2 numeric score 还依赖冻结 pairwise-B numeric E2 score，并以 Exp88 anonymous role+shape digest 做 tie key。

E02/J 的 8 个候选是 checkpoint action/response/state rows（position、action family/shape、response category/status、state-changing、rollback feasibility 等），不是 Exp88 `turns` trajectory；没有冻结的 content/action/thought、anonymous role、local-score/phase 或 graph-neighbor 映射。Exp112C 正式结果只保存排名、指标和审计，不保存可用于 E02 的 serialized model weights、feature encoder 或 projection adapter。把 E02 call 人工包装成 turns 会新增未注册表示/启发式，违反“只能复用冻结表示/评分函数”的边界。

因此不能声称已经接入 Exp112C 全排序，也不能用新启发式替代。preflight 以 `PREFLIGHT_BLOCKED` fail closed，并保留后续若主线程提供冻结、无损 adapter 时的设计边界。

## 预注册升级边界（仅设计，未执行）

若未来获得兼容的冻结 scorer，`protected_full_ranking` 才能按以下顺序构造：接受的 J Gold-free Predicted top1 首位；A 选中的策略 top；Exp112C full-ranking tail，去重后 budget=3。tie 必须沿用 Exp112C 的 Exp88 anonymous role+shape digest。top1 保护是机制性保底，不是按 held task 手工修补。

B 仍是一个完整模块：state posterior、same-checkpoint transaction 和 TNR 不拆计数。Active/Standby/Escalate 预算固定为 1/3/0；posterior 必须来自 outer-train-only candidate/strategy recovery utility 的 group OOF，常量或样本不足就 fail closed。A+B、full-ranking deletion/shuffle、state-posterior shuffle、route shuffle、random equal-budget 和 Oracle 条件及 task-cluster 3-seed bootstrap 均只在 scorer 兼容后才可执行。

即使后续 controlled-only Gate 通过，也不能把同一批已经用于 Exp114 诊断的 34 tasks 当作自然失败外部有效性证据；`is_method_go=false`、`is_full_chapter_go=false` 永久保持。

## Preflight / formal guard

```bash
python3 实验/实验115_RQ2全排序状态事务恢复升级/runner.py --preflight
python3 -m unittest discover -s 实验/实验115_RQ2全排序状态事务恢复升级/tests -p 'test_*.py'
```

preflight 输出：[exp115_preflight_blocked.json](results/exp115_preflight_blocked.json)；attempt audit：[exp115_preflight_blocked_attempt_audit.json](results/exp115_preflight_blocked_attempt_audit.json)。两者只记录兼容性阻断、`formal_attempts=0`、无 held metrics/asset recheck。Exp115 formal namespace 必须不存在，且本目录不覆盖 Exp114 formal output/audit。

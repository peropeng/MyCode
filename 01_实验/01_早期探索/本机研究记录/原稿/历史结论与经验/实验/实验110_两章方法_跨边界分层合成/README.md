# 实验110：两章方法的跨边界分层合成

## 目的

本实验不重跑模型、数据、Gold 或 API，只对实验109唯一正式结果中已经冻结的逐 task-group MRR 做一次 cache-only 分层 bootstrap。目标是回答：两个历史边界上，实验108 utility router 相对各边界在实验109中已经选定的 strongest component 的小幅正增益，合并后是否具有跨边界的稳定正下界。

这是一次 **adaptive post-hoc synthesis**。实验97/98均已用于历史方法开发或压力检查，因此不是 pristine unseen confirmation；即使通过，也只支持两章开题的外部合成证据，不等于论文最终 GO。

## 冻结输入

- 唯一输入：`../实验109_两章方法_历史边界外部确认/results/formal_external_confirmation_results.json`
- SHA-256：`02c172b668b780fba1bf8471f454a3c7f6b5a3352fd46c2b80c5235400e4ace8`
- 边界及 task group 数：实验97为168组，实验98为161组。
- 用户已确认资产哈希全部匹配，因此不重复执行额外安全/资产扫描；分析器仅校验冻结输入绑定及必要结构。

## 固定统计方法

1. 每个边界使用实验109已选定的 `strongest_component_comparator`：实验97为 `exp106_top1_cascade`，实验98为 `exp101_hard_gate`。
2. 每个 task group 先计算每个 seed 的 `exp108_utility_router - strongest component`，再在3个 seed上取平均，形成每组一个差值。
3. 在实验97的168组和实验98的161组内分别有放回采样；每次先求两个边界各自的均值，再以 `0.5 / 0.5` 等权合成。
4. 固定 `10,000` 次、随机种子 `20260823`，报告 percentile 95% CI。
5. 按 task-group 数加权的合成只作为敏感性分析，不进入 GO 判定。

## 固定判定

仅当以下条件全部成立，输出 `TWO_CHAPTER_OPENING_EXTERNAL_SYNTHESIS_GO`：

- 两个边界相对 strongest fair baseline 的平均相对提升都不低于10%，且每个边界、每个 seed 的 fair CI 下界都大于0；
- 两个边界、每个 seed 相对既定 strongest component 的点估计差都大于0；
- 实验109的 deletion、shuffle 与必要审计全部通过；
- 0.5/0.5 跨边界合成的 bootstrap 95% CI 下界大于0。

若点估计仍为正但任一 GO 条件未通过，输出 `POSITIVE_NOT_YET_GO`；只有合成及相关增益均非正才停止本合成，输出 `STOP_EXP110_SYNTHESIS_ONLY`。无论结果如何，`direction_no_go=false`、`adaptive_posthoc=true`、`pristine_unseen=false`、`final_paper_go=false`。

## 执行

冻结前预检：

```bash
python3 analyze.py --preflight
python3 -m py_compile analyze.py tests/test_exp110.py
python3 -m unittest discover -s tests -v
```

冻结提交后只执行一次正式合成：

```bash
python3 analyze.py --formal
```

正式输出固定为 `results/formal_external_synthesis_results.json`。如果文件已存在，程序拒绝覆盖；不重试、不覆盖。


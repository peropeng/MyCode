# Exp68 deployment freeze

本目录是 Exp67 冻结融合器的部署与外部开发候选门。它没有 live 默认路径；
`runner.py --train-model` 只拟合已消费训练资产，`online_runner.py --mock` 才会
读取外部资产并产生 218 次 synthetic calls。mock 结果必须标记
`MOCK_ONLY_NOT_ACCURACY`。attempt1 的 lbfgs 数值失败已记录在
`results/preregistered_plan.json`；attempt2 只允许 liblinear 数值稳定修复，未打开
目标资产。attempt3 仅为已授权 loader 增加严格 bytes JSONL parser；普通 guard
继续拒绝目标资产，mock 不打开目标资产。

冻结前检查：

```sh
python3 实验/实验68_冻结OOF融合器_PlanningMultiEasy外部开发门/runner.py --train-model
python3 -m unittest discover -s 实验/实验68_冻结OOF融合器_PlanningMultiEasy外部开发门/tests -v
python3 实验/实验68_冻结OOF融合器_PlanningMultiEasy外部开发门/online_runner.py --mock
```

部署模型 JSON 只含哈希、行数、模型参数、特征名、warnings 和审计；不含 query、
tools、messages、prompt、response、candidate 或 credential。外测 live 需要主线程
明确审查冻结 commit，并注入四要素：非空 `OPENCODE_API_KEY`、`--confirm-child`、
`EXP68_EXTERNAL_CHILD_SENTINEL=1`、`EXP68_EXTERNAL_CONFIRMATION=ALLOW_EXP68_EXTERNAL_109_ATTEMPT1`。
live supervisor 命令见 [PROTOCOL.md](PROTOCOL.md)。

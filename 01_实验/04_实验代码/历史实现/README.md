# 历史实现直接浏览

按原研究问题和历史来源展开16组主线/精选证据中的可公开代码，不将恢复后的目录数写成正式实验数。旧版本各自保留，源码原字节与完整附件一致。新维护入口与当时的冻结Prompt分开，翻译或修改Prompt必须另立实验条件。

| 研究问题 | 历史来源 | 当前取舍 | 展开源码数 | 阅读入口 |
| --- | --- | --- | ---: | --- |
| RQ1 | 实验124 | 精选证据 | 11 | [文件导航](%E6%A0%B9%E5%9B%A0%E6%8E%92%E5%BA%8F/%E5%AE%9E%E9%AA%8C124/README.md) |
| RQ1 | 实验134 | 主线材料 | 22 | [文件导航](%E6%A0%B9%E5%9B%A0%E6%8E%92%E5%BA%8F/%E5%AE%9E%E9%AA%8C134/README.md) |
| RQ1 | 实验153 | 主线材料 | 16 | [文件导航](%E6%A0%B9%E5%9B%A0%E6%8E%92%E5%BA%8F/%E5%AE%9E%E9%AA%8C153/README.md) |
| RQ1 | 实验156 | 精选证据 | 10 | [文件导航](%E6%A0%B9%E5%9B%A0%E6%8E%92%E5%BA%8F/%E5%AE%9E%E9%AA%8C156/README.md) |
| RQ1 | 实验157 | 精选证据 | 14 | [文件导航](%E6%A0%B9%E5%9B%A0%E6%8E%92%E5%BA%8F/%E5%AE%9E%E9%AA%8C157/README.md) |
| RQ1 | 实验158 | 主线材料 | 15 | [文件导航](%E6%A0%B9%E5%9B%A0%E6%8E%92%E5%BA%8F/%E5%AE%9E%E9%AA%8C158/README.md) |
| RQ1 | 实验159 | 精选证据 | 15 | [文件导航](%E6%A0%B9%E5%9B%A0%E6%8E%92%E5%BA%8F/%E5%AE%9E%E9%AA%8C159/README.md) |
| RQ1 | 实验161 | 精选证据 | 7 | [文件导航](%E6%A0%B9%E5%9B%A0%E6%8E%92%E5%BA%8F/%E5%AE%9E%E9%AA%8C161/README.md) |
| RQ1 | 实验162 | 精选证据 | 7 | [文件导航](%E6%A0%B9%E5%9B%A0%E6%8E%92%E5%BA%8F/%E5%AE%9E%E9%AA%8C162/README.md) |
| RQ2 | 实验224 | 精选证据 | 77 | [文件导航](%E6%95%85%E9%9A%9C%E6%81%A2%E5%A4%8D/%E5%AE%9E%E9%AA%8C224/README.md) |
| RQ2 | 实验239 | 精选证据 | 510 | [文件导航](%E6%95%85%E9%9A%9C%E6%81%A2%E5%A4%8D/%E5%AE%9E%E9%AA%8C239/README.md) |
| RQ2 | 实验241 | 精选证据 | 165 | [文件导航](%E6%95%85%E9%9A%9C%E6%81%A2%E5%A4%8D/%E5%AE%9E%E9%AA%8C241/README.md) |
| RQ2 | 实验248 | 精选证据 | 13 | [文件导航](%E6%95%85%E9%9A%9C%E6%81%A2%E5%A4%8D/%E5%AE%9E%E9%AA%8C248/README.md) |
| RQ2 | 实验249 | 主线材料 | 60 | [文件导航](%E6%95%85%E9%9A%9C%E6%81%A2%E5%A4%8D/%E5%AE%9E%E9%AA%8C249/README.md) |
| RQ2 | 实验250 | 主线材料 | 67 | [文件导航](%E6%95%85%E9%9A%9C%E6%81%A2%E5%A4%8D/%E5%AE%9E%E9%AA%8C250/README.md) |
| RQ2 | 实验251 | 主线材料 | 28 | [文件导航](%E6%95%85%E9%9A%9C%E6%81%A2%E5%A4%8D/%E5%AE%9E%E9%AA%8C251/README.md) |

## 原作者实现与公开边界

- [StepFinder官方源码](https://github.com/taiyu-zhu/StepFinder)：固定上游文件继续按工程清单获取。
- [Agentless官方源码](https://github.com/OpenAutoCoder/Agentless)：本目录中的agentless178等是历史适配和集成入口，不能当作上游最新版。
- [EnAgent论文](https://conf.researchr.org/details/icse-2026/icse-2026-research-track/233/Agent-Based-Ensemble-Reasoning-for-Repository-Level-Issue-Resolution)及[相关公开工件Trae Agent](https://github.com/bytedance/trae-agent)：不能用上游当前版本替换旧已执行快照。本目录展开的是本研究保留的适配与控制代码，原作者代码归属以封存清单和上游许可为准。

环境、依赖副本、运行工作树、数据、模型、响应、逐题评价记录、具体评价选择器与疑似凭据文件没有混入源码树。它们并未删除，完整原件仍保存在既有附件中；逐文件公开状态和目录排除原因见[机器清单](%E5%85%AC%E5%BC%80%E6%BA%90%E7%A0%81%E6%B8%85%E5%8D%95.json)。无法确认能否公开的条目标为待核定，不据此宣称整组代码或实验已完成。

本轮只展开和核对文件，没有执行原脚本、训练、测试集评价或模型API调用。

# 实验实现与研究问题

## 根因排序

已有完整模型是冻结AB_GLOBAL；独立入口`src/thesis_recovery/rq1_study.py`定义研究设置。无多关系层条件只替换关系层，仍有配对和候选注意力；无候选条件注意力条件使用全轨迹均值背景，不能写成删除全部上下文。coding-only还涉及数据规模和训练更新差异，不单独证明数学数据迁移收益。设置依据见[审查](根因排序/设置审查.md)。

公开代码附件中保存当前源码、模型、配置、锁文件和可运行工具。恢复后可在`本地恢复/原始项目/02_工作区/01_工程/src/thesis_recovery`直接阅读Python实现。`根因排序/run_ranking.py`是中文维护入口，仅回放现有输出。训练需要独立的新配置与授权，本轮没有训练。

## 运行故障恢复

RQ2尚未冻结最终组合，见[探索方案](故障恢复/探索方案.md)。冻结历史实现保持原字节，当前适配器为`rq2_control_env.py`，入口为`tools/run_rq2_controls.py`，独立验收入口为`accept_rq2_controls.py`。当前源码包的两个控制条件分别保存启动器，不将其临时选择写成最终模块。

整体方法基线是Agentless、EnAgent、AOrchestra，原作者代码、许可来源与适配关系留在相应档案。排序器接同一个恢复器的条件只用于机制分析，不替代整体方法基线。新API配置由研究者填写，不能执行原封存调度或继承旧预算。

完整[代码原件包](https://github.com/peropeng/MyCode/releases/download/research-materials-v1/current-code.tar.gz)包含src、tools、tests、manifests、reproduction及核对回执，可公开下载后直接阅读。恢复接口、数据源目录和中文导读属于本次整理；旧英文Prompt/注释是结果身份的一部分，单独封存。修改后的中文Prompt应建立新配置和新结果，不覆盖冻结实现。

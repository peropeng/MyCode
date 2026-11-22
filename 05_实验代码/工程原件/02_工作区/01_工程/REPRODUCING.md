# 换机恢复

需要有权访问私有仓库的GitHub账户、Python 3.12和uv。在Windows启用Git长路径支持：

```powershell
gh repo clone peropeng/graduate-thesis -- --config core.longpaths=true
cd graduate-thesis/02_工作区/01_工程
uv sync --frozen --extra embedding --extra recovery
uv run python tools/fetch_external.py --core
uv run python -m thesis_recovery verify-ranking
```

仓库顶层只有实验、工作区、开题、论文四类目录。实验从RQ1与RQ2两个入口进入，原编号标识历史来源。

已有回放特征和3个当前检查点随Git保存，以上回放无需下载大型编码模型。恢复当前方法的完整文件依赖及原生测试环境：

```powershell
uv run python tools/restore_current_method.py --with-models
uv run python tools/rebuild_native_environment.py
```

当前自有资源附件约32 MB，其余文件从锁定上游获取并核对SHA256。`--with-models`另取约1.2 GB的Qwen3-Embedding-0.6B，省略时暂缓该模型。排序215项、恢复3058项文件分别恢复到本目录的`.rebuild/current-method/ranking`和`recovery`。

原生环境为Windows x64、Python 3.11.15及74项锁定依赖。封存配置保持原字节，实际环境配置使用当前主机路径。旧入口通过`tools/run_legacy.py --root <恢复目录> <入口相对路径>`加载，默认关闭网络且不执行主入口。这里恢复的是当前部署依赖，不代表开题20题的各仓库环境和共同故障起点已经全部核定。

RQ1/RQ2的训练资料和有效成果另有[私有数据备份](https://github.com/peropeng/graduate-thesis/releases/tag/rq1-rq2-research-inputs-v1)。面向当前学术实验，先恢复选定训练输入；不默认展开44组历史档案。恢复清单逐文件记录SHA256，不依赖本机旧Git目录：

```powershell
uv run python tools/restore_research_data.py --bundle rq1-training-inputs-restored.tar.gz
uv run python tools/restore_research_data.py --verify-only --bundle rq1-training-inputs-restored.tar.gz
```

数据恢复到本工程`.rebuild/paper-inputs`。其中`rq1-source`保存492条训练、122条验证轨迹、对应标签和特征；`rq2-experiment129`及`experiment244`、`experiment257`、`experiment260`、`experiment261`、`experiment262`保存原始结果与证据。下载的附件先核对整体SHA256，再核对每个文件；遇到本机不同字节的同名文件会停止，不覆盖。按用途用`--bundle <附件名>`取所需包；省略该参数会恢复全部历史数据包，仅在确需完整回溯时使用，不是新实验前置条件。

当前基线与恢复器的源码、固定输入和必要代表记录按`manifests/experiment_use_priorities.json`选取。250/251的完整基线及261的AOrchestra实现仍需适配统一20题配置；尚无仅凭恢复历史包即可启动全部正式实验的承诺。两个保留索引给出逐组取舍，结论级材料不继续恢复旧环境、旧模型和全量缓存。

补充保留的RQ1方法发展与RQ2恢复可行性材料位于`.rebuild/paper-inputs/retained-experiments/rq1`和`rq2`。以下是完整档案回溯命令，仅在需要核对历史来源时执行，不作为日常学术运行准备：

```powershell
uv run python tools/restore_research_data.py --bundle retained-feasibility-experiments-original.tar.gz --bundle rq1-ranking-development-records-original.tar.gz --bundle rq1-supplementary-original-records.tar.gz
uv run python tools/restore_research_data.py --verify-only --bundle retained-feasibility-experiments-original.tar.gz --bundle rq1-ranking-development-records-original.tar.gz --bundle rq1-supplementary-original-records.tar.gz
```

这些附件保存本轮实际找回的原字节。部分历史大附件已删除，旧训练检查点、特征和大体积记录仍有缺口；有固定上游、软件包或差分配方的第三方依赖另列为“未展开”，不计作丢失数据。逐文件状态见`manifests/retained_feasibility_experiments.json`引用的清单。不能将上述命令成功理解为所有历史材料完整恢复。各组的研究用途见两个实验入口下的`保留实验索引.md`。当前3个模型、614条训练/验证资料和重建特征继续使用已有恢复包。

本轮清单和入口说明也随私有附件`retained-experiment-recovery-index.tar.gz`保留。若新克隆的源码版本尚不含本轮清单，先在仓库根目录下载并展开该索引包，再进入工程运行上述数据恢复命令：

```powershell
gh release download rq1-rq2-research-inputs-v1 --repo peropeng/graduate-thesis --pattern retained-experiment-recovery-index.tar.gz --dir 02_工作区/01_工程/.restore-cache
tar -xzf 02_工作区/01_工程/.restore-cache/retained-experiment-recovery-index.tar.gz
```

124、130、131、132的历史参数和派生缓存已完整恢复至本机，并另存`.restore-cache/rq1-ranking-development-original.tar.gz`。它们不属于这四组的默认换机记录包；当前方法仍使用已单独保留的3个排序模型与选定训练输入。

RQ1轨迹和训练标签与原始文件字节一致。删除前的特征缓存未找回完整副本，当前特征由同一冻结编码器、原始特征函数和原始614条公共轨迹重建，记录独立的新SHA256，不能称为原缓存。依据见`verification/rq1_training_data_recovery.json`与`rq1_training_feature_rebuild.json`。需要重新生成时先恢复上述资料及Qwen模型，再使用`tools/rebuild_training_features.py`；输出已存在时不会覆盖。

使用已恢复的特征不需要CUDA编码环境。仅在重新生成特征时，Windows/Python 3.12可将`torch==2.7.1+cu128`从PyTorch官方cu128索引单独安装到`.external/torch-cuda`，原CPU环境保持独立；固定安装包来源及SHA256见`manifests/training_encoder_runtime.json`。本机该运行库已安装，下载分段、重复安装包和临时下载缓存因自动审批拦截删除而暂存，不属于研究数据。

恢复的自有训练源码、模型定义及已有结果位于`01_实验/历史结论与经验/实验`中的134、136、150、152C、153、158来源目录。旧训练入口仍含历史路径、协议和截止时间，保留原字节用于迁移，不直接执行它们。当前RQ1独立设置与训练入口见`src/thesis_recovery/rq1_study.py`，准备协议后按明确条件启动，不启用旧全套调度。15次训练和420次恢复属于旧版工作量估计，当前定稿未写死。RQ2重新探索方法，整体基线、独立评价及各项作用分析尚未完成。

旧开题留稿、参考汇报和论文PDF等本地历史材料不属于当前方法运行依赖。与当前方法有关的训练输入、模型、有效结果和原始恢复记录必须保留，不能再作为普通历史过程文件删除。

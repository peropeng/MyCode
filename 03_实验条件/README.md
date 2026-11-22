# 实验条件与换机恢复

公开入口不依赖原主机盘符、个人Python环境或私有Git提交。默认恢复到本仓库忽略目录`本地恢复/原始项目`，保留冻结实现所需的原内部相对布局。下载代码包后，旧清单中92个不同Git内容对象已带实体，不需要从旧私有历史执行git show。封存的旧REPRODUCING说明保留当时状态，当前下载与恢复步骤以本页为准。

## 代码环境

查阅实现可直接进入[仓库内的源码导航](../05_实验代码/工程原件/README.md)，不用先执行恢复命令。以下步骤用于运行原版本，补齐模型、依赖和未展开的大型清单；浏览副本与附件原件的对应关系见源码目录中的机器清单。

使用Python 3.12和uv，源码、3个已有排序模型和回放特征已直接在仓库中。可直接进入：

```powershell
cd 05_实验代码/工程原件/02_工作区/01_工程
uv sync --frozen --extra embedding --extra recovery
uv run python tools/fetch_external.py --core
uv run python -m thesis_recovery verify-ranking
```

回放只核对原模型输出，不构成新科学实验；本方法3份小型回放模型与特征可随Git获取，完整副本也在代码附件中。6份本方法/StepFinder现有模型都已保留，StepFinder相关模型在当前依赖内容包内。下载Qwen大型编码器仅在确实需要从原轨迹重建特征时进行，固定来源见数据目录；现有缓存为同冻结编码器重建版本，不能称丢失原缓存。需要完整旧布局及所有机器清单时，仍可运行`restore.py --code`恢复到`本地恢复/原始项目`。

## 完整档案

恢复工具的解密依赖与训练环境分开，建议单独建立环境：

```powershell
uv venv 本地恢复/恢复环境 --python 3.12
uv pip install --python 本地恢复/恢复环境/Scripts/python.exe -r 03_实验条件/requirements.txt
gh release download rq1-rq2-research-inputs-v1 --repo peropeng/graduate-thesis --pattern mycode-recovery-key.json --dir 本地配置
本地恢复/恢复环境/Scripts/python.exe 03_实验条件/restore.py --history --key-file 本地配置/mycode-recovery-key.json
```

密钥通过原私有仓库的既有访问权限取得，不能提交或贴入公开Issue；也可由研究者通过合适渠道提供密钥文件。`--history`不列名称会恢复全部已列受保护附件，可追加明确附件名仅取所需组。代码包和加密包下载、解密后分别校验，已有不同字节的同名文件会停止，不覆盖。`current-inputs-full.tar`按原格式保存在工程`.restore-cache`，由原对象配方解压内容，不直接当目录树展开。

当前依赖及原生环境还需显式恢复：

```powershell
cd 本地恢复/原始项目/02_工作区/01_工程
uv run python tools/restore_current_method.py
uv run python tools/rebuild_native_environment.py
```

此native迁移链明确支持Windows x64、Python 3.11.15和锁定依赖，负责独立测试与Windows进程清理。没有验证Linux上的同等native行为，不承诺换操作系统即能直接启动全部实验。系统、Python、包锁、上游版本与运行差异须写入新回执。

## API与新实验

复制`配置样例/api.example.json`和`run.example.json`到忽略的`本地配置`，由研究者填写。地址、模型、密钥环境变量、预算与超时均未预设。历史档案中deepseek-flash等名称只是已执行条件，不自动成为新实验配置。公开入口不会读取历史授权或自动续发模型请求。

已经终态的流程不重跑。真正续跑之前核对输入、代码、Prompt、参数、消息状态、当前源码、Checkpoint、游标、已结算响应、未决请求及累计时间/费用。条件变化另立记录，不拼接成绩。旧消息中的本机绝对路径是原件来源，不是当前配置。最新RQ2八流程已全部终态，恢复后用于查阅，旧case不能在新主机直接运行，也不应自动再次生成。

准备后续新条件时，先恢复必要数据、当前依赖和native环境，再用`05_实验代码/故障恢复/relocate_case.py --task <原任务ID> --python <native解释器> --output 本地恢复/新条件/case.json`建立独立的路径重定位视图。该工具只修改明确的路径字段，保留公共历史及原件字节，不读取API配置、不执行测试；环境与公开C0须重新核定。随后使用新trial保存新结果，不能覆盖原八流程。历史未完成流程若无法完整重建状态，标为待核定，不用这个新视图冒充科学续跑。

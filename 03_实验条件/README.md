# 实验条件与换机恢复

日常代码与研究材料从MyCode获取，不再使用旧私有仓库。运行文件统一放在Git忽略的`工作区/`，完整旧布局恢复到`工作区/恢复/原始项目`。原主机的四类旧目录原位保留，具体位置见[文件位置与同步范围](../文件位置与同步范围.md)。冻结说明中的旧路径和仓库标识只用于来源追溯，当前步骤以本页为准。

## 浏览与排序回放

源码可以从[工程导航](../05_实验代码/工程原件/README.md)直接浏览，无需解密。已有三个本方法模型、三个StepFinder模型均保留；其中三个小型本方法回放模型及特征已随Git提供，其余在内容附件内。运行时使用工作区内的完整旧布局，先恢复代码包，再复核已有输出：

```powershell
python 03_实验条件/restore.py --code
cd 工作区/恢复/原始项目/02_工作区/01_工程
uv sync --frozen --extra embedding --extra recovery
uv run python tools/fetch_external.py --core
uv run python -m thesis_recovery verify-ranking
```

回放不训练、不发模型请求，不构成新科学实验。原训练特征缓存仍有缺口，当前特征是冻结编码器的重建件。只有需要从轨迹重建特征时才下载[Qwen编码模型](编码模型来源.json)。

## 完整原件与本机凭据

从仓库根目录执行，恢复工具使用Python 3.12：

```powershell
uv venv 工作区/恢复/恢复环境 --python 3.12
uv pip install --python 工作区/恢复/恢复环境/Scripts/python.exe -r 03_实验条件/requirements.txt
工作区/恢复/恢复环境/Scripts/python.exe 03_实验条件/restore.py --code
```

代码包含旧清单所需92份Git内容原件，不需要访问旧私有历史。受保护档案需要研究者单独保存的`mycode-recovery-key.json`；把现存密钥复制到`工作区/私有配置/`，或用`--key-file`指定外部文件。密钥没有在线私库获取步骤，不能从公开Git重建，换机时需随离线备份单独转移。原主机的旧密钥副本仍在原临时材料目录，未删除。

```powershell
工作区/恢复/恢复环境/Scripts/python.exe 03_实验条件/restore.py --history current-inputs-full.tar
```

不列附件名称的`--history`会恢复[清单](../06_实验记录/恢复清单.json)中全部受保护原件；可只列所需附件名。所有附件来自MyCode Release，下载与解密分别校验。同名文件字节不同时停止，不覆盖。`current-inputs-full.tar`是内容对象包，按原配方留在工程`.restore-cache`，不能直接按源码树展开。

## 当前依赖与原生环境

先检查代码原件和本地内容包完整，再显式准备依赖：

```powershell
python 03_实验条件/prepare_dependencies.py
python 03_实验条件/prepare_dependencies.py --prepare
cd 工作区/恢复/原始项目/02_工作区/01_工程
uv sync --frozen --extra embedding --extra recovery
uv run python tools/rebuild_native_environment.py
```

第一步只读检查。第二步复用冻结恢复配方并从固定公共来源准备依赖；本地原件或内容包缺失/变化时停止，不向旧私库或旧Git提交回退。不直接运行冻结`restore_current_method.py`作为当前恢复入口。环境重建支持Windows x64、Python 3.11.15和锁定依赖；Linux完整原生行为尚未验证。系统与包锁变化应单独记录，不能宣称现有结果可无条件迁移。

## API配置与后续实验

把`配置样例/api.example.json`及`run.example.json`复制到`工作区/私有配置/`后由研究者填写。地址、模型、密钥变量、预算和超时保持空模板；历史deepseek-flash等名称不自动成为新配置。配置不进入Git，归档和实验输出均放工作区。

已经终态的流程只查阅或回放，不重跑。续跑前必须核对协议、输入、代码、Prompt、参数、请求发送状态、公开反馈、源码、Checkpoint、游标及累计资源；条件变化另建记录，不拼接成绩。

准备新条件时，可用`05_实验代码/故障恢复/relocate_case.py --task <原任务ID> --python <native解释器> --output 工作区/恢复/新条件/case.json`建立独立路径视图。工具不读取API配置、不执行测试，公共历史及原件字节保持；新环境与C0仍须核定。不能把新视图冒充旧流程的科学续跑。

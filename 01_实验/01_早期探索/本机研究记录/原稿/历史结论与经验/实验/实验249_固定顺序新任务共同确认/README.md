# 固定顺序新任务共同确认

本实验准备依冻结plan21的自然顺序确认六个issue：dask 9378、moto 5072、moto 5134、moto 5286、moto 6352、pydantic 8567。先核前两题的当前C0资格，其余四题只保留计划。每方法、每题预定三次完整重复；三个方法全部完成时是54条轨迹、6个issue，不能把重复轨迹当新题或只报三次中的最好结果。

本文采用实验248冻结的当前失败绑定改进，保留RQ1排序、关系闭包、SET和三次生成上限。对手保留Agentless完整4组定位×10补丁、40复现样本，以及EnAgent N=3、生成最多200步、选择最多30轮。模型统一DeepSeek Flash，旧结果保留；方法生成源码还须由Root在开发小试结束后另行绑定和放行，本目录当前不包含已获授权的科学生成器。

每条完整轨迹同时观察30分钟、128调用、131072输出token内是否已交付合格修复，以及相同内部参数继续至自然终态的结果。资金、费用未知、用户窗口结束或进程保护中断保留删失。三次重复都报告；不因一次偶然成败改题、加机会或换参数。来源池有历史使用，未宣称全研究未见或RQ1训练无重叠。

## 已准备的实际入口

`ROOT_FIRST_TWO_IDENTITY_COMMANDS249.json`给出前两题精确命令，`grant_templates`保留全部false模板。`SOURCE_SEAL249.json`绑定34个源码、46个公开输入；当前没有模型、产品测试、独立终验或账本写入。

1. `native249.py --stage identity`：Root逐题签新grant后执行。使用现有working124控制器VENV；父进程挂起创建worker，核held PID/创建时间/请求镜像与具体Job归属后恢复。产品解释器以`-S -B`运行固定身份探针，实际自身WinAPI记录物理image/PID/birth/Job及ABI，全部子进程停止后封存。它不导入业务包、不跑pytest；配置中的base路径只是候选，不能替代实测。
2. `materialize249_ROOT_ONLY.py`：Root另签精确两题grant并绑定原隔离manifest SHA后才读取原公开测试文件和hidden节点元数据。使用已封存原模板文件清单，不运行Git。按当前六题同一AST规则遮住Goal及独立保留测试函数/装饰器，保留行跨度，无法映射则整文件省略。仅输出mask视图和摘要，原正文与hidden节点列表不输出。其他四题保留未材料化条目，不能执行。
3. `native249.py --stage current_C0`：需先绑定本题新身份回执与父STOP、两题共同mask范围。先由原trusted qualifier执行精确G/O，必须得到真实G失败、O通过；另执行mask视图中的原O，验证shared_native_v14 guard和tool channel完整性。两项phase、native计数、来源与叶结果分别记录。mask中的`pass`占位绝不充当Goal通过。

原native执行器是`native_executor242_prospective.py`；容量适配是`native_capacity_v10.py`；公共mask界面直接绑定Root shared_native_v14原四文件；并发使用V5同一锁文件的1、2、4、5字节槽，不动财务0号字节。G/O探针沿用原`qualify.probe`和`run.probe`/`assess_probe`函数，保留原选择器、测试保护与完整叶覆盖校验。仅把输出、授权和固定身份前缀绑定到本实验；不会修改旧源。

## 当前待Root绑定的内容

身份grant需Root置`root_authorized/native_authorized=true`，给有限lease和停止路径，并核工作VENV文件SHA；原模板中的其他权限继续false。材料化grant还需Root绑定原隔离manifest SHA；这些私有节点元数据未被source准备读取。C0 grant需原G/O执行许可、新identity及父STOP SHA、mask范围SHA，并明确当前运行时clock策略；3.8与3.11分别实测，不能跨ABI继承能力。

控制器脚本使用CPython3.12；产品身份探针只用3.8兼容stdlib语法。shared_v14的sitecustomize已自带`Path.is_relative_to`兼容处理，这是源码事实，不是3.8实际通过的证据。工程门检失败只作一次最多五分钟机械修复；固定六槽不删Dask，可并行推进已可运行的Moto资格，失败仍保留为共同资格未知。不得升级产品Python来掩盖兼容问题。

实际资格结果只有在原G/O、mask普通探针、产品身份、完整STOP和Root共同放行均明确后才成立。现阶段所有grant为false，没有科学结果。

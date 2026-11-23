# AOrchestra 固定 SWE 作者流程备用部署提案

已继续实补独立Exp226候选：新增实际owner/executor/Win32 Job/产品Python入口、共享Flash回调和单题CLI，完整作者核纯fixture通过；当前事实和接手命令见 [HANDOFF226.md](HANDOFF226.md)。以下保留首次提案的来源与监督判据；早期缺项列表已有接口实现，但仍未完成真实机械准入，因此deployable_now仍为false。

判定：作者完整核心可复用，旧197的监督竞态有局部机械修正方案；当前还不能直接投入实际比较。`controller_proposal.py` 是保留作者主循环的接线提案，必须在独立备用目录完成 owner/executor 接线、身份准入、source seal 和 root grant，才构成可部署版本。本准备没有模型、历史native、公私验收、server、GPU、下载、Gold或财务动作。

正式出处沿用[ICML2026 PMLR论文页](https://proceedings.mlr.press/v306/ruan26e.html)及作者 `fix/swebench-grader-audit` 冻结pin `1fccfed44dcb4be05360ddc84373858cb40302c0`。已逐文件核对旧197的79个作者文件SHA，未修改旧源码。没有重新筛选其他论文。

共同输入绑定当前224 V2的registry SHA `298efeac0dcf0498ed8f78e0067c8e24a963e24c29442fc0df64d8e047b7a37c`，23份pack的SHA全部核对通过。冻结总预算沿用64次模型调用、65536输出token、900秒、64个native根和每根90秒；2026-10-09 10:00北京时间硬截止，不能给Main、child、Memory和trace summary各自重置。

旧错误精确位置是 `owned197.py:birth` 的 `QueryFullProcessImageNameW` 断言；`execute` 每2ms发现新Job PID后查询，断言逃逸进入finally关闭Job。`final_interruption197.json`记载parent root46/helper root56和 `wc -l < toy197/__init__.py`，编辑已发生但完整终局缺失。旧结果仍为null。

最小修正只改变监督观测分类：对同一个已持有句柄，同时证实本Job归属、birth、wait signaled、非STILL_ACTIVE退出码和非零退出时间的后裔，影像不可读记为 `EXITED_DESCENDANT_IMAGE_UNAVAILABLE`，继续收集父进程终局；该记录始终不是已认证影像。活进程未知、无法证明Job/birth、controller或产品Python影像未知仍中止。OpenProcess需同时使用 `PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE`，不能靠重新打开PID移植身份。9个离线判据通过；未宣称实际复现竞态或完成WinAPI集成。

接线提案直接调用作者 `SWEBenchRunner`，保留 Main JSON→动态SWE child→DISCUSSION/COMMAND→原完整ACI→Memory(max_memory20)→原trace summary→context更新→Submit及默认10次Main、50步child。旧197的合成fake、压缩Memory2、玩具测试和旧deadline都不复用。仅替换executor/真实环境文字/公开验收部署接口和LLM传输；typed Instance的patch/test_patch必须为空，原stock loader禁止执行。

所有已载入的 `create_llm_instance` aliases都替换，Main/child/Memory和硬编码Gemini summary送至同一Flash传输；原AsyncLLM角色prompt和采样保留，每次请求补全同一个完整publicpack，seed/thinking和累计费用由root冻结owner控制。factory在原AsyncLLM构造前把model映射为Flash，避免进入Gemini thinking分支。原作者cost tracker的模型价格和top-level子费用不完整，不能当权威金额；必须以实际共享账本为准。

作者Delegate/summary/runner会捕获异常，缺项和财务失败可能呈现reward0。因此owner必须设置不可清除的unknown latch，并在作者run返回后检查；财务、部署、源漂移不能成为方法0。声明共同预算正常耗尽与工程/金额截断分开记录，私有验收只在合法immutable selection后交外部一次执行。

缺项集中在 `preparation_receipt.json`：新独立owner和NativeExecutor、实际Python自报身份与Job、同FAILED C0及全业务hash、真实共享Flash callback、当轮普通测试verifier、最终once-private外部回调、新source seal和root准入、监督策略实际集成及中性工具准入。旧197 NativeExecutor绑定toy/旧账本，不能直接搬用；225现有owner可作为只读迁移参考，但不得引用其当前授权作为备用准入。

离线检查命令（仅本目录写receipt，不启动作者runtime）：

```powershell
& 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/Code/毕设/graduate-thesis-experiments/工作区/1008-2320-baseline-main/baseline2026_readiness/aorchestra_backup_preparation/controller_proposal.py' --check --write-receipt
& 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B 'D:/Code/毕设/graduate-thesis-experiments/工作区/1008-2320-baseline-main/baseline2026_readiness/aorchestra_backup_preparation/prepare_source_map.py'
```

本目录不提供live CLI，避免把尚未接线的草案当成已具备完整部署。`source_map.json`列出原核路径、SHA和入口行；`purechecks_receipt.json`区分离线通过和未执行事项。没有改写当前224/225目录、旧197源码、grant或账本，也没有业务答案和预评补丁。

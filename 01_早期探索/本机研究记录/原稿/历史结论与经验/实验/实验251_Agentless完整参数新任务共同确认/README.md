# Agentless 完整参数共同确认

本目录准备 Agentless 在新共同任务上的完整部署，目前仅有源码、公开输入检查和请求预览。模型发送、真实产品测试及一次独立终验分别等待主线程的精确 grant；所有模板权限均为 false。源码检查或合成检查点检查不代表方法已完成真实小试。

方法采用 [Agentless 正式论文](https://doi.org/10.1145/3715754) 及 [作者固定提交的运行说明](https://github.com/OpenAutoCoder/Agentless/blob/5ce5888b9f149beaace393957a55ea8ee46c9f71/README_swebench.md) 的完整采样参数：四组细定位，每组十个补丁，共40个补丁；40个复现样本。细定位温度为0.8，每组补丁与复现样本均保留首个贪心、其余0.8的规则。真实密集检索、文件频数合并、复现验证、普通测试筛选、归一化及投票选择全部保留。`agentless_core/agentless178.py`、作者核心函数及提示词按字节复制，完整模型阶段最多88次。

本机部署统一使用 DeepSeek Flash、既有本地 Qwen 检索及原共同任务的局部 G/O 范围。论文使用 GPT-4o、OpenAI embedding，并从完整仓库发现回归测试；这些替换需要披露，不能把本机部署称作论文原始经验成绩复现。局部 O 仍由原测试完成，G 用于共同验收，不加入 Agentless 的补丁排序规则。历史参数凭据中 `first5406_only` 是旧运行范围，不能充当本轮授权。

固定计划为 Dask 9378、Moto 5072/5134/5286/6352、Pydantic 8567，每题预定三条完整独立轨迹，master 为2026101201、2026101202、2026101203。先完成当前已接受 C0 的 Moto 5072 小试，再推进 Dask。六个 issue、每方法18条轨迹分别计数；报告全部重复，不只取最佳结果。客户端 seed 只标识请求，不能保证服务端确定性。其他方法补丁、私有验收结果和其他 trial 的模型输出都不进入新轨迹。

`entry251.py` 用完整原核心重建轨迹，在每个模型和原生测试边界停下。完整消息、阶段、已用步数、全部候选和快照、复现样本、投票、工具状态与结算来源均保存。续跑仅消费同一 trial 中 body 精确一致且 SETTLED 的响应，以及已完成父 Job STOP 的公开原生记录。inflight、费用未知和启动未知均不自动重发。源码预览另存于 `source_previews`；真实 trial 的 T0 从主线程授权的准备开始，首次 POST 单独记录，续跑不重置时钟。

同一轨迹同时观察30分钟、128调用、131072输出 token 内是否已交付合格修复，以及保持内部参数继续到自然终态的结果。24小时与进程/token保护是部署删失条件，不能称无预算算法失败。独立验收只在完整公开选择被冻结后执行一次，其结果不会反馈给模型。

当前 Moto 5072 的公开源码、完整查询和4033个向量已有精确匹配缓存，复用的是固定预处理资产，并单独披露历史准备时间。Dask 缺完整匹配缓存，当前实际入口在任何 POST 前关闭；`DASK_ZERO_API_DENSE_PREPARATION_PLAN251_SOURCE.json` 给出既有本地模型的完整准备方案。尚未编码，没有借用其他 issue 的向量或省略检索。

主线程启动清单在 `FIRST_TWO_THREE_CONTRACTS251_SOURCE.json`。实际准备使用 `entry251.py --contract <合同> --root-preparation-grant <精确准备授权>`，随后根据 `STATUS.json` 的边界先生成全 false 模板，再由主线程放行 `dispatch_once251_ROOT_ONLY.py` 或 `native_once251_ROOT_ONLY.py`。自然终态后用 `freeze_final251_SOURCE.py` 冻结原选择；只有公开 G/O 实际通过的选定快照才交 `final_once251_ROOT_ONLY.py` 作一次独立验收。

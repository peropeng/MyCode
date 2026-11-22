# AOrchestra原作者固定源码

此目录直接展开本研究原261归档使用的79项AOrchestra原作者源码，供导师和研究者浏览。它们是第三方作者作品，不是本论文原创代码。官方来源为[FoundationAgents/AOrchestra](https://github.com/FoundationAgents/AOrchestra)。固定版本、历史来源分支和逐文件身份保存在[来源清单](来源清单.json)，不以当前上游版本替换旧已执行快照。

## 许可与原件

源码遵循随目录提供的[Apache License 2.0](LICENSE)。许可文件从同一固定版本补齐，官方固定树中没有NOTICE文件。79项原件均保持原字节、文件名和内部包布局，原作者README保留在[原始源码说明](原始源码/README.md)。本页是新增中文导读，不改写原作者提示词。

原作者示例配置中的API Key均为占位符，没有真实凭据。示例地址、模型和运行参数只反映该固定源码的上游配置，不代表本研究后续API选择；后续实际配置仍由研究者在仓库的空模板中填写。

## 主要阅读入口

- [主调度器](原始源码/aorchestra/main_agent.py)
- [SWE-bench子智能体](原始源码/aorchestra/subagents/swebench_agent.py)
- [SWE-bench运行器](原始源码/aorchestra/runners/swebench_runner.py)
- [任务委派工具](原始源码/aorchestra/tools/delegate.py)
- [SWE-bench提示词](原始源码/aorchestra/prompts/swebench.py)
- [模型调用与异步接口](原始源码/base/engine/async_llm.py)
- [框架结构说明](原始源码/aorchestra/README.md)

## 与原261实验的关系

原261基于此固定作者实现，另有输入约束、Windows兼容、模型调用记账、进程清理和独立验收适配。这里展示作者源码，不能把它与本研究适配器混称为新原创方法，也不能只依据此目录宣称原261已可在任意主机直接续跑。完整原件、当时输入与运行状态继续保存在既有研究附件中，已完成终态不重跑。

本轮只复制、检查许可和核对字节，没有执行任何原入口、训练、测试集评价或模型调用。

## 全部源码导航

- [.env.example](原始源码/.env.example)
- [README.md](原始源码/README.md)
- [aorchestra/README.md](原始源码/aorchestra/README.md)
- [aorchestra/__init__.py](原始源码/aorchestra/__init__.py)
- [aorchestra/common/__init__.py](原始源码/aorchestra/common/__init__.py)
- [aorchestra/common/utils.py](原始源码/aorchestra/common/utils.py)
- [aorchestra/config.py](原始源码/aorchestra/config.py)
- [aorchestra/main_agent.py](原始源码/aorchestra/main_agent.py)
- [aorchestra/prompts/__init__.py](原始源码/aorchestra/prompts/__init__.py)
- [aorchestra/prompts/gaia.py](原始源码/aorchestra/prompts/gaia.py)
- [aorchestra/prompts/swebench.py](原始源码/aorchestra/prompts/swebench.py)
- [aorchestra/prompts/terminalbench.py](原始源码/aorchestra/prompts/terminalbench.py)
- [aorchestra/runners/__init__.py](原始源码/aorchestra/runners/__init__.py)
- [aorchestra/runners/gaia_runner.py](原始源码/aorchestra/runners/gaia_runner.py)
- [aorchestra/runners/swebench_runner.py](原始源码/aorchestra/runners/swebench_runner.py)
- [aorchestra/runners/terminalbench_runner.py](原始源码/aorchestra/runners/terminalbench_runner.py)
- [aorchestra/sub_agent.py](原始源码/aorchestra/sub_agent.py)
- [aorchestra/subagents/__init__.py](原始源码/aorchestra/subagents/__init__.py)
- [aorchestra/subagents/react_agent.py](原始源码/aorchestra/subagents/react_agent.py)
- [aorchestra/subagents/swebench_agent.py](原始源码/aorchestra/subagents/swebench_agent.py)
- [aorchestra/tools/__init__.py](原始源码/aorchestra/tools/__init__.py)
- [aorchestra/tools/complete.py](原始源码/aorchestra/tools/complete.py)
- [aorchestra/tools/delegate.py](原始源码/aorchestra/tools/delegate.py)
- [aorchestra/tools/submit.py](原始源码/aorchestra/tools/submit.py)
- [aorchestra/tools/trace_formatter.py](原始源码/aorchestra/tools/trace_formatter.py)
- [base/__init__.py](原始源码/base/__init__.py)
- [base/agent/__init__.py](原始源码/base/agent/__init__.py)
- [base/agent/base_action.py](原始源码/base/agent/base_action.py)
- [base/agent/base_agent.py](原始源码/base/agent/base_agent.py)
- [base/agent/memory.py](原始源码/base/agent/memory.py)
- [base/agent/react_agent.py](原始源码/base/agent/react_agent.py)
- [base/engine/__init__.py](原始源码/base/engine/__init__.py)
- [base/engine/async_llm.py](原始源码/base/engine/async_llm.py)
- [base/engine/cost_monitor.py](原始源码/base/engine/cost_monitor.py)
- [base/engine/logs.py](原始源码/base/engine/logs.py)
- [base/engine/utils.py](原始源码/base/engine/utils.py)
- [bench_aorchestra_swebench.py](原始源码/bench_aorchestra_swebench.py)
- [benchmark/aorchestra_bench_gaia.py](原始源码/benchmark/aorchestra_bench_gaia.py)
- [benchmark/bench_gaia.py](原始源码/benchmark/bench_gaia.py)
- [benchmark/bench_swebench.py](原始源码/benchmark/bench_swebench.py)
- [benchmark/bench_terminalbench.py](原始源码/benchmark/bench_terminalbench.py)
- [benchmark/benchmark.py](原始源码/benchmark/benchmark.py)
- [benchmark/common/__init__.py](原始源码/benchmark/common/__init__.py)
- [benchmark/common/env.py](原始源码/benchmark/common/env.py)
- [benchmark/common/incremental_runner.py](原始源码/benchmark/common/incremental_runner.py)
- [benchmark/common/runner.py](原始源码/benchmark/common/runner.py)
- [benchmark/gaia/__init__.py](原始源码/benchmark/gaia/__init__.py)
- [benchmark/gaia/llm_scorer.py](原始源码/benchmark/gaia/llm_scorer.py)
- [benchmark/gaia/scorer.py](原始源码/benchmark/gaia/scorer.py)
- [benchmark/gaia/tools/__init__.py](原始源码/benchmark/gaia/tools/__init__.py)
- [benchmark/gaia/tools/execute_code.py](原始源码/benchmark/gaia/tools/execute_code.py)
- [benchmark/gaia/tools/extract_url_jina.py](原始源码/benchmark/gaia/tools/extract_url_jina.py)
- [benchmark/gaia/tools/google_search.py](原始源码/benchmark/gaia/tools/google_search.py)
- [benchmark/gaia/tools/multimodal_toolkit.py](原始源码/benchmark/gaia/tools/multimodal_toolkit.py)
- [benchmark/swebench/__init__.py](原始源码/benchmark/swebench/__init__.py)
- [benchmark/swebench/aci_tools.py](原始源码/benchmark/swebench/aci_tools.py)
- [benchmark/swebench/data_loader.py](原始源码/benchmark/swebench/data_loader.py)
- [benchmark/swebench/result_reporter.py](原始源码/benchmark/swebench/result_reporter.py)
- [benchmark/swebench/swebench_executor.py](原始源码/benchmark/swebench/swebench_executor.py)
- [benchmark/swebench/swebench_selected_ids.json](原始源码/benchmark/swebench/swebench_selected_ids.json)
- [benchmark/swebench/utils.py](原始源码/benchmark/swebench/utils.py)
- [benchmark/terminalbench/__init__.py](原始源码/benchmark/terminalbench/__init__.py)
- [benchmark/terminalbench/base_executor.py](原始源码/benchmark/terminalbench/base_executor.py)
- [benchmark/terminalbench/daytona_executor.py](原始源码/benchmark/terminalbench/daytona_executor.py)
- [benchmark/terminalbench/docker-compose-build.yaml](原始源码/benchmark/terminalbench/docker-compose-build.yaml)
- [benchmark/terminalbench/docker_executor.py](原始源码/benchmark/terminalbench/docker_executor.py)
- [benchmark/terminalbench/docker_manager.py](原始源码/benchmark/terminalbench/docker_manager.py)
- [benchmark/terminalbench/e2b_executor.py](原始源码/benchmark/terminalbench/e2b_executor.py)
- [benchmark/terminalbench/result_reporter.py](原始源码/benchmark/terminalbench/result_reporter.py)
- [benchmark/terminalbench/utils.py](原始源码/benchmark/terminalbench/utils.py)
- [requirements.txt](原始源码/requirements.txt)
- [config/example/benchmarks/aorchestra_gaia.yaml](原始源码/config/example/benchmarks/aorchestra_gaia.yaml)
- [config/example/benchmarks/aorchestra_swebench.yaml](原始源码/config/example/benchmarks/aorchestra_swebench.yaml)
- [config/example/benchmarks/aorchestra_terminalbench.yaml](原始源码/config/example/benchmarks/aorchestra_terminalbench.yaml)
- [config/example/benchmarks/gaia.yaml](原始源码/config/example/benchmarks/gaia.yaml)
- [config/example/benchmarks/swebench.yaml](原始源码/config/example/benchmarks/swebench.yaml)
- [config/example/benchmarks/terminalbench.yaml](原始源码/config/example/benchmarks/terminalbench.yaml)
- [config/example/model_config.yaml](原始源码/config/example/model_config.yaml)
- [swebench_grader_audit.md](原始源码/swebench_grader_audit.md)

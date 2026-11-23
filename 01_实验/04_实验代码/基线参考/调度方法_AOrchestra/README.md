# AOrchestra原作者固定源码

此目录直接展开本研究原261归档使用的79项AOrchestra原作者源码，供导师和研究者浏览。它们是第三方作者作品，不是本论文原创代码。官方来源为[FoundationAgents/AOrchestra](https://github.com/FoundationAgents/AOrchestra)。固定版本、历史来源分支和逐文件身份保存在[来源清单](%E6%9D%A5%E6%BA%90%E6%B8%85%E5%8D%95.json)，不以当前上游版本替换旧已执行快照。

## 许可与原件

源码遵循随目录提供的[Apache License 2.0](LICENSE)。许可文件从同一固定版本补齐，官方固定树中没有NOTICE文件。79项原件均保持原字节、文件名和内部包布局，原作者README保留在[原始源码说明](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/README.md)。本页是新增中文导读，不改写原作者提示词。

原作者示例配置中的API Key均为占位符，没有真实凭据。示例地址、模型和运行参数只反映该固定源码的上游配置，不代表本研究后续API选择；后续实际配置仍由研究者在仓库的空模板中填写。

## 主要阅读入口

- [主调度器](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/main_agent.py)
- [SWE-bench子智能体](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/subagents/swebench_agent.py)
- [SWE-bench运行器](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/runners/swebench_runner.py)
- [任务委派工具](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/tools/delegate.py)
- [SWE-bench提示词](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/prompts/swebench.py)
- [模型调用与异步接口](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/base/engine/async_llm.py)
- [框架结构说明](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/README.md)

## 与原261实验的关系

原261基于此固定作者实现，另有输入约束、Windows兼容、模型调用记账、进程清理和独立验收适配。这里展示作者源码，不能把它与本研究适配器混称为新原创方法，也不能只依据此目录宣称原261已可在任意主机直接续跑。完整原件、当时输入与运行状态继续保存在既有研究附件中，已完成终态不重跑。

本轮只复制、检查许可和核对字节，没有执行任何原入口、训练、测试集评价或模型调用。

## 全部源码导航

- [.env.example](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/.env.example)
- [README.md](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/README.md)
- [aorchestra/README.md](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/README.md)
- [aorchestra/__init__.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/__init__.py)
- [aorchestra/common/__init__.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/common/__init__.py)
- [aorchestra/common/utils.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/common/utils.py)
- [aorchestra/config.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/config.py)
- [aorchestra/main_agent.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/main_agent.py)
- [aorchestra/prompts/__init__.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/prompts/__init__.py)
- [aorchestra/prompts/gaia.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/prompts/gaia.py)
- [aorchestra/prompts/swebench.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/prompts/swebench.py)
- [aorchestra/prompts/terminalbench.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/prompts/terminalbench.py)
- [aorchestra/runners/__init__.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/runners/__init__.py)
- [aorchestra/runners/gaia_runner.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/runners/gaia_runner.py)
- [aorchestra/runners/swebench_runner.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/runners/swebench_runner.py)
- [aorchestra/runners/terminalbench_runner.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/runners/terminalbench_runner.py)
- [aorchestra/sub_agent.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/sub_agent.py)
- [aorchestra/subagents/__init__.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/subagents/__init__.py)
- [aorchestra/subagents/react_agent.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/subagents/react_agent.py)
- [aorchestra/subagents/swebench_agent.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/subagents/swebench_agent.py)
- [aorchestra/tools/__init__.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/tools/__init__.py)
- [aorchestra/tools/complete.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/tools/complete.py)
- [aorchestra/tools/delegate.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/tools/delegate.py)
- [aorchestra/tools/submit.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/tools/submit.py)
- [aorchestra/tools/trace_formatter.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/aorchestra/tools/trace_formatter.py)
- [base/__init__.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/base/__init__.py)
- [base/agent/__init__.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/base/agent/__init__.py)
- [base/agent/base_action.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/base/agent/base_action.py)
- [base/agent/base_agent.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/base/agent/base_agent.py)
- [base/agent/memory.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/base/agent/memory.py)
- [base/agent/react_agent.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/base/agent/react_agent.py)
- [base/engine/__init__.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/base/engine/__init__.py)
- [base/engine/async_llm.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/base/engine/async_llm.py)
- [base/engine/cost_monitor.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/base/engine/cost_monitor.py)
- [base/engine/logs.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/base/engine/logs.py)
- [base/engine/utils.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/base/engine/utils.py)
- [bench_aorchestra_swebench.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/bench_aorchestra_swebench.py)
- [benchmark/aorchestra_bench_gaia.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/aorchestra_bench_gaia.py)
- [benchmark/bench_gaia.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/bench_gaia.py)
- [benchmark/bench_swebench.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/bench_swebench.py)
- [benchmark/bench_terminalbench.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/bench_terminalbench.py)
- [benchmark/benchmark.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/benchmark.py)
- [benchmark/common/__init__.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/common/__init__.py)
- [benchmark/common/env.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/common/env.py)
- [benchmark/common/incremental_runner.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/common/incremental_runner.py)
- [benchmark/common/runner.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/common/runner.py)
- [benchmark/gaia/__init__.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/gaia/__init__.py)
- [benchmark/gaia/llm_scorer.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/gaia/llm_scorer.py)
- [benchmark/gaia/scorer.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/gaia/scorer.py)
- [benchmark/gaia/tools/__init__.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/gaia/tools/__init__.py)
- [benchmark/gaia/tools/execute_code.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/gaia/tools/execute_code.py)
- [benchmark/gaia/tools/extract_url_jina.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/gaia/tools/extract_url_jina.py)
- [benchmark/gaia/tools/google_search.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/gaia/tools/google_search.py)
- [benchmark/gaia/tools/multimodal_toolkit.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/gaia/tools/multimodal_toolkit.py)
- [benchmark/swebench/__init__.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/swebench/__init__.py)
- [benchmark/swebench/aci_tools.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/swebench/aci_tools.py)
- [benchmark/swebench/data_loader.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/swebench/data_loader.py)
- [benchmark/swebench/result_reporter.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/swebench/result_reporter.py)
- [benchmark/swebench/swebench_executor.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/swebench/swebench_executor.py)
- [benchmark/swebench/swebench_selected_ids.json](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/swebench/swebench_selected_ids.json)
- [benchmark/swebench/utils.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/swebench/utils.py)
- [benchmark/terminalbench/__init__.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/terminalbench/__init__.py)
- [benchmark/terminalbench/base_executor.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/terminalbench/base_executor.py)
- [benchmark/terminalbench/daytona_executor.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/terminalbench/daytona_executor.py)
- [benchmark/terminalbench/docker-compose-build.yaml](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/terminalbench/docker-compose-build.yaml)
- [benchmark/terminalbench/docker_executor.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/terminalbench/docker_executor.py)
- [benchmark/terminalbench/docker_manager.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/terminalbench/docker_manager.py)
- [benchmark/terminalbench/e2b_executor.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/terminalbench/e2b_executor.py)
- [benchmark/terminalbench/result_reporter.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/terminalbench/result_reporter.py)
- [benchmark/terminalbench/utils.py](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/benchmark/terminalbench/utils.py)
- [requirements.txt](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/requirements.txt)
- [config/example/benchmarks/aorchestra_gaia.yaml](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/config/example/benchmarks/aorchestra_gaia.yaml)
- [config/example/benchmarks/aorchestra_swebench.yaml](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/config/example/benchmarks/aorchestra_swebench.yaml)
- [config/example/benchmarks/aorchestra_terminalbench.yaml](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/config/example/benchmarks/aorchestra_terminalbench.yaml)
- [config/example/benchmarks/gaia.yaml](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/config/example/benchmarks/gaia.yaml)
- [config/example/benchmarks/swebench.yaml](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/config/example/benchmarks/swebench.yaml)
- [config/example/benchmarks/terminalbench.yaml](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/config/example/benchmarks/terminalbench.yaml)
- [config/example/model_config.yaml](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/config/example/model_config.yaml)
- [swebench_grader_audit.md](%E5%8E%9F%E5%A7%8B%E6%BA%90%E7%A0%81/swebench_grader_audit.md)

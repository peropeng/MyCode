# EnAgent部署所用的作者主体

这里补齐历史EnAgent部署中实际使用的Trae生成器、工具、提示词和补丁选择器，避免只看到外层controller、bridge而无法检查方法主体。它属于RQ2整体方法基线的来源代码，不是本项目原创，也不表示RQ2方案已经定稿。

## 从哪里开始阅读

| 环节 | 源码入口 | 作用 |
| --- | --- | --- |
| 原作者生成过程 | [base_agent.py](%E5%8E%9F%E4%BD%9C%E8%80%85%E6%BA%90%E7%A0%81/trae_agent/agent/base_agent.py)、[trae_agent.py](%E5%8E%9F%E4%BD%9C%E8%80%85%E6%BA%90%E7%A0%81/trae_agent/agent/trae_agent.py) | 维护任务执行、模型步骤及工具结果 |
| 原作者提示词 | [agent_prompt.py](%E5%8E%9F%E4%BD%9C%E8%80%85%E6%BA%90%E7%A0%81/trae_agent/prompt/agent_prompt.py) | 保留原系统提示，不在迁移时翻译或改写 |
| 工具与编辑 | [base.py](%E5%8E%9F%E4%BD%9C%E8%80%85%E6%BA%90%E7%A0%81/trae_agent/tools/base.py)、[edit_tool.py](%E5%8E%9F%E4%BD%9C%E8%80%85%E6%BA%90%E7%A0%81/trae_agent/tools/edit_tool.py)、[bash_tool.py](%E5%8E%9F%E4%BD%9C%E8%80%85%E6%BA%90%E7%A0%81/trae_agent/tools/bash_tool.py) | 定义工具契约、文本编辑及命令操作 |
| 候选补丁选择 | [selector_agent.py](%E5%8E%9F%E4%BD%9C%E8%80%85%E6%BA%90%E7%A0%81/evaluation/patch_selection/trae_selector/selector_agent.py)、[utils.py](%E5%8E%9F%E4%BD%9C%E8%80%85%E6%BA%90%E7%A0%81/evaluation/patch_selection/trae_selector/utils.py) | 原候选结构、选择代理与补丁规范化 |
| 本项目历史运行接线 | [enagent_native.py](%E5%8E%86%E5%8F%B2%E8%BF%90%E8%A1%8C%E9%80%82%E9%85%8D/enagent_native.py) | 从固定作者文件提取原类及方法，注入受控环境与后端，组织生成、剪枝和投票 |
| 后续完整参数部署 | [实验250源码](../../%E5%8E%86%E5%8F%B2%E5%AE%9E%E7%8E%B0/%E6%95%85%E9%9A%9C%E6%81%A2%E5%A4%8D/%E5%AE%9E%E9%AA%8C250/README.md) | 查看继承的controller、worker、checkpoint和主机兼容层 |

作者源码内部保留原Python包目录，以维持导入和来源定位。另包含同一固定版本的完整源码依赖子树，方便顺着导入查阅；没有复制数据、运行目录、模型、私有验收测试或个人配置。

## 来源和版本

作者主体来自[ByteDance Trae Agent](https://github.com/bytedance/trae-agent)。版本固定为历史`enagent_native.py`启动时强制校验的作者提交，并由原部署的源码映射核对，未用上游最新版替换。精确版本、固定下载地址、每个文件的来源与字节对应关系存于[来源映射](%E6%9D%A5%E6%BA%90%E6%98%A0%E5%B0%84.json)。

证据链为：原实验250的worker实际加载原实验175的`enagent_native.py`，该核心校验作者版本并读取Trae及selector源码；实验250的纯请求构造器也引用同一封存Trae目录。

原运行映射记录了11份作者文件。这11份从相同固定上游取得后恢复为原Windows换行，全部匹配原映射记录的文件字节。其余源码来自同一固定上游版本，属于依赖补齐，不能声称每一份都已由原运行映射逐项证明执行过。本项目历史适配核心也与原运行映射记录完全匹配。

## 许可和使用边界

原作者主体按原版本的MIT许可保留，完整许可见[LICENSE](%E5%8E%9F%E4%BD%9C%E8%80%85%E6%BA%90%E7%A0%81/LICENSE)，版权所有者为ByteDance及其关联方。固定版本的[依赖声明](%E5%8E%9F%E4%BD%9C%E8%80%85%E6%BA%90%E7%A0%81/pyproject.toml)原样保留。本项目原适配层与作者主体分开放置，不将整段源码重新署名为本项目原创。

历史代码包含旧路径、原英文注释和原Prompt，保持结果来源身份。直接导入旧适配器仍会检查旧作者路径并寻找原依赖；本目录用于浏览和核对，不承诺复制后即可在任意主机直接运行。跨主机启动须在新的适配入口显式绑定作者目录、任务状态、环境、后端及资源范围，不能继承旧授权或调度。

本次只恢复并展开源码、核对许可和来源，没有执行代理、模型、工具或任务测试，也没有重新生成任何实验成绩。

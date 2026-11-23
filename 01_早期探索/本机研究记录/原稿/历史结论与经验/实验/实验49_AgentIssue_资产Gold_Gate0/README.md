# AgentIssue-Bench Gate0：资产、Gold、独立性与安全入口

裁决分两档：原题的命名函数定位为 `STOP_FUNCTION_GOLD_26_LT_30`；若将题目明确改写为 file + code-region（有效代码 hunk/line-range），资产层仍为 `CONDITIONAL_ASSET_BLOCKED`。本 Gate 只读取 metadata，未拉镜像、未运行容器、未调用模型/API。

本实验只判断候选组一是否有资格进入后续可执行实验，不生成 patch，也不把安装、下载、harness 修复或同一设计重跑计作研究失败。

## 冻结来源与严格边界

- 官方仓库：`https://github.com/alfin06/AgentIssue-Bench`，MIT，冻结 commit `1d498dec35e347c4e7b9e1c318ef28fc5fa97318`。
- 论文主集严格取该 commit `pull_images.py::IMAGE_TAGS` 的 50 个 tag；Docker Hub 当前 85 个 tag 中额外 35 个排除。
- 官方 `AgentIssue-Bench Spreadsheet.xlsx :: 50 AgentIssue-Bench` 有 50 行，tag/reference 严格连接 50/50。
- `agent_issue.json` 的官方 `patch` 字段是 developer patch Gold 来源；不使用生成 patch、模型得分或 LLM judge。`tmp_tasks_map.json` 只作官方 test metadata 对照。
- 每条交叉匹配必须 exact `instance_id`、归一化 repo（只剥除前缀 `repo/`）、exact `base_commit` 与 `environment_setup_commit`；还必须有非空 `test_patch` 与非空 `FAIL_TO_PASS`。`PASS_TO_PASS` 单独计数，不能替代失败触发集合。
- 所有 raw issue、patch、test、源码、镜像层和 secret 均留在 `.gitignore` 的 `runtime/`；提交只含脚本、合同、hash、索引、bool、计数、架构、大小和聚合。

## Gate0 census

| 项目 | 结果 | 解释 |
|---|---:|---|
| 主 tag / registry | 50/50 | 只用冻结主集，额外 35 tag 不混入 |
| registry 架构 | amd64 36，arm64 14 | 只报告官方 manifest metadata |
| spreadsheet/reference/image | 50/50 | 主表身份完整 |
| patch metadata exact / test metadata exact | 44/50 / 44/50 | 6 个主任务没有唯一官方 JSON 记录，不能猜配 |
| exact instance/repo(base normalized)/base/setup | 44/44/44/44 | raw repo spelling 相等为 0/44（`repo/` 前缀差异被显式报告） |
| nonempty `test_patch` / nonempty `FAIL_TO_PASS` / nonempty `PASS_TO_PASS` | 43/44 / 0/44 / 0/44 | 严格可执行资产为 0/50 |
| 官方 developer patch file Gold | 43/50 | 仅 `agent_issue.json::patch` 的派生 file set |
| strict named-function Gold | 26/50 | 不能达到硬门 30；原题因此 STOP |
| reframed code-region Gold | 32/50 | code hunk line-range；不能冒充命名 function |
| strict eligible file/equivalent Gold | 0/50 / 0/50 | test trigger 条件未满足 |

## 独立性与功效

split 不是只声明同 repo 不跨 split，而是把 repository 节点与相同/近同 patch-structure 节点连接成 deterministic connected components，整组件冻结。当前粗粒度结构形成 2 个组件：patch-only file candidate 为 held-out 42 / train 1，code-region candidate 为 held-out 31 / train 1；两者虽为 0 same-repository cross-split、0 near-template cross-split，但预注册要求 train 与 held-out 均至少 20 条，故 split 不可行。strict eligible 0 条，也没有可冻结 strict held-out split。

file-region 的协议层功效审计只能记录候选 n=42（equivalent n=31）；由于 connected-component split 不可行，状态为 `STOP_NO_FEASIBLE_CONNECTED_COMPONENT_SPLIT`。在最有利“无回归、仅 discordant gains”假设下，若后续补足可行 split，固定 95% bootstrap lower>0 的参考最小 gain 为 4；10% relative 门的整数增量依赖 baseline 原始成功数。Gate0 没有 baseline/method outcomes，不声称效果或 CI 已通过。

## 为什么停止/阻塞

按原题 function localization，26/50 < 30/50，硬裁决是 `STOP_FUNCTION_GOLD_26_LT_30`。即使主线程接受把第一章改成 file + code-region，6 条严格 patch/test asset join 缺失、`FAIL_TO_PASS` 全空且 strict eligible=0，仍只能 `CONDITIONAL_ASSET_BLOCKED`，不能把 patch-only 的 32/50 写成原 function gate 通过。

若继续，Gate1 前只需针对 6 个 `unavailable_in_official_checkout` 身份取得最小单 tag 证据：唯一 buggy/base commit、developer patch changed-file metadata、非空失败触发 test metadata、image tag 与可复核 linkage；image execution may resolve，但这只是待验证可能性，不是当前事实。仍不得批量拉镜像或伪造补数。

## 安全 single-tag wrapper

`scripts/single_tag_gate1.py` 默认只打印计划。计划为一次 `docker pull IMAGE`，以及两个 fresh、无网络容器：`docker run --rm --network none IMAGE test_buggy` 和 `docker run --rm --network none IMAGE test_fixed`。官方 image ENTRYPOINT 保持不覆盖，不显式指定错误的 `test` entrypoint。live 模式需同时传 `--live --confirm-live-gate1`。

wrapper 拒绝空、通配符、逗号列表、shell 字符和非 50-tag 值；不注入环境变量、不收集 API key、不挂载主机、不上传网络、不执行 `docker rmi` 或 `system prune`，Gate0 未执行任何 Docker 命令。

## 结果与复现

- `results/asset_census.json`：50 个匿名 task record、严格 join、Gold、split 与总裁决。
- `results/gold_census.json`：Gold 派生 hash/计数/排除枚举。
- `results/independence_power.json`：connected-component split 与功效协议。
- `results/registry_snapshot.json`：50 条匿名 registry 记录。
- `results/privacy_audit.json`：递归隐私审计。

```bash
python3 实验/实验49_AgentIssue_资产Gold_Gate0/scripts/gate0_audit.py --offline-registry
python3 -m unittest discover -s 实验/实验49_AgentIssue_资产Gold_Gate0/tests -v
python3 实验/实验49_AgentIssue_资产Gold_Gate0/scripts/single_tag_gate1.py --tag agixt_1026
python3 实验/实验49_AgentIssue_资产Gold_Gate0/scripts/privacy_audit.py
```

本目录未执行 Docker pull/run/rmi，未运行官方破坏性评测脚本。

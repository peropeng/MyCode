# 实验42：方向 A AppWorld Gate0 / 10-task smoke

本实验只回答一个资格问题：锁定的官方 AppWorld 引擎、数据、任务验证器和
baseline 输出是否能在本机以无付费 API 的方式复验，并且是否存在方向 A 合同所
要求的 train/dev GPT-4o 轨迹资产。它不运行新的 Agent，不调用 OpenAI 或其他
模型 API，不把 protected bundle 解包后的内容提交到 Git，也不把十个 smoke
任务伪装成 Gate1 的 30 个自然任务。

## 锁定资产和保护边界

- 官方仓库：`stonybrooknlp/appworld`，tag `v0.1.3.post1`，commit
  `66ad8099e12188ece0d3fe45e661dbc01880813b`。
- PyPI：`appworld==0.1.3.post1`，Python 要求 `>=3.11`，metadata license
  `Apache-2.0`。
- public portion 按仓库 Apache-2.0；data、app/API 实现、任务评价和解法属于
  protected portion。官方条款要求 protected bundle 或其衍生物公开再分发时
  仍使用加密格式，并要求不要把 bundle 派生内容发布为明文。
- `runtime/` 中的 venv、官方 clone、data、experiment outputs 和 smoke 产物
  都是本地 ignored runtime；提交物只有版本、路径、计数、哈希、字段存在性和
  资格结论，不含任务 instruction、solution、evaluation code、DB 行、API
  日志或 bundle 派生原文。

## 实际执行

在 worktree 根目录执行：

```bash
python3.12 -m venv 实验/实验42_方向A_AppWorld_Gate0资格/runtime/venv
实验/实验42_方向A_AppWorld_Gate0资格/runtime/venv/bin/pip install appworld==0.1.3.post1
cd 实验/实验42_方向A_AppWorld_Gate0资格/runtime/appworld_root
appworld install
NO_PROXY=s3.us-west-2.amazonaws.com appworld download data
NO_PROXY=s3.us-west-2.amazonaws.com appworld download experiment-outputs
appworld verify tasks
```

实测：install、两个 download 均退出 0；`verify tasks` 对 train+dev 共 147 个
任务完成，退出 0。下载 data 约 183 MB，experiment outputs 约 750 MB。下载器
使用的 S3 端点在本机默认代理下出现 TLS EOF，补充该域名 `NO_PROXY` 后官方
命令成功；没有输入 API key、密码或人工许可。

## 10-task 固定 smoke

`scripts/audit_static.py` 按 task ID 的 SHA-256 排序，分别选 train/dev 各 5 个，
且 generator ID 全部唯一。提交的每行只包含 task/generator 的 SHA-256、split、
计数、布尔存在性、应用集合指纹和入口 smoke 状态；不包含原始 task/generator
ID、任务编号、protected 文件名或 specs/metadata key 列表。scenario 不在公开
schema 中序列化，因此严格记为 UNKNOWN，不从受保护 generator 推断。

运行：

```bash
python3.12 实验/实验42_方向A_AppWorld_Gate0资格/scripts/audit_static.py \
  --root 实验/实验42_方向A_AppWorld_Gate0资格/runtime/appworld_root \
  --repo 实验/实验42_方向A_AppWorld_Gate0资格/runtime/appworld_repo \
  --output 实验/实验42_方向A_AppWorld_Gate0资格
```

train/dev 数据均具备 `evaluation.py`、`solution.py`、`compiled_solution.py` 和
`answer.json`（仅记录存在性，不提交内容）。每个选中任务都能构造
`AppWorld`、保存并恢复 checkpoint；当前 smoke 还在初始化后直接调用一次
`world.evaluate()`，返回 `TestTracker`。这证明引擎入口可运行，不证明动作
效果 Oracle、自然 action 或 clean replay 已经具备。

## 资格裁决

本轮裁决为 `Gate0 = STOP`、`Gate1 ready = STOP`，原因是合同指定的两个路径：

```text
simplified_react_code_agent_gpt-4o-2024-05-13_train
simplified_react_code_agent_gpt-4o-2024-05-13_dev
```

在官方 experiment-output bundle 中均不存在。官方确实提供了
`react_gpt4o_test_normal` 和 `react_gpt4o_test_challenge`，metadata 标明
`gpt-4o-2024-05-13`；但它们是 test split，且每个已下载任务有
`api_calls.jsonl`、DB JSONL、code/data version 和 evaluation report，**没有**
`logs/environment_io.md`。因此不能把 test baseline 重命名或替换成 train/dev
轨迹，更不能仅凭 DB 终态组成方向 A 的动作效果 Oracle。

完整机器可读证据：

- `manifests/asset_manifest.json`：仓库/PyPI/license/请求路径/替代输出摘要；
- `manifests/ten_task_manifest.jsonl`：十个固定任务的去重和字段存在性；
- `results/gate0_summary.json`：命令、计数、状态 smoke 和 STOP 原因；
- `contract/protocol.json`：预注册门槛与 protected-content 边界。

后续若要复开资格门，必须先取得可合法使用的 train/dev GPT-4o action-level
轨迹（包含 environment I/O 或等价可重建记录），然后另做至少 30 task、3 类
effect、stable Oracle 和 clean replay 的 Gate1；本实验不声称已进入实验41。

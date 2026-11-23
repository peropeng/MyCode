# Gate 0/1 环境报告

运行日期：2026-08-21。所有外部仓库检查均为只读；动作合同的临时目录位于本实验的 gitignored `runtime/`。

CCF 第七版目录入口 `https://www.ccf.org.cn/Academic_Evaluation/By_category/2026-03-31/870181.shtml` 本轮 HTTP 200；该页面只用于 venue 分类核验，不把 venue 等级当作论文质量证明。

## Docker/Colima

| 命令 | 返回码 | 关键 stdout/stderr |
|---|---:|---|
| `docker context show` | 0 | `colima` |
| `docker version --format 'client={{.Client.Version}} server={{.Server.Version}} os={{.Server.Os}} arch={{.Server.Arch}}'` | 0 | `client=29.7.2 server=29.5.2 os=linux arch=arm64` |
| `docker run --rm hello-world` | 0 | stdout 含 `Hello from Docker!`；stderr 为空 |

Docker 当前可用，不构成 Gate 0/1 环境阻塞。完整摘要和每次 runner 记录见 `gate0_asset_audit.json` 与 `gate1_qualification.json`。

## 本机锁定仓库 clean probe

`run_gate0.py` 对以下已锁定 commit 的本地环境执行了只读测试，5/5 返回码为 0，并检查执行前后的 `git status --porcelain` 为空：

- pydantic `2151025aa51263f3016502b00010b78e4481eaa1`：`tests/test_version.py::test_version_attribute_is_present`，1 passed。
- conan `0789d17f29928faed8239bba955bb523320c244a`：`test/unittests/client/tools/files/rename_test.py::TestRename::test_rename_empty_folder`，1 passed。
- mypy `7f88c95bbf9af181a4de13e2c242c89216f15b19`：`FindConfigFileSuite::test_parent_config_with_and_without_git`，1 passed。
- MONAI `e04a802191385370c3118651d972461df5d0daad`：`TestVersionCompare::test_compare_leq_00_1_6_0`，1 passed。
- moto `7ffce303011e76e1c6782ba5ea718e9374acdc0a`：`tests/test_core/test_config.py::test_whitelist`，1 passed。

## Python 测试运行器

系统 `/Library/Developer/CommandLineTools/usr/bin/python3` 没有安装 pytest，命令返回 `No module named pytest`，未把它记为方法失败。使用已锁定的 pydantic 运行环境执行：

```text
/.../runtime/envs/pydantic/bin/python -m pytest -q 实验/实验35_方向A动作效果验证Gate0Gate1/tests
3 passed in 0.70s（含剥离 Gold 的 online probe 回归）
```

## 限制

- SyncBench 300 CSV 已从 HF revision `d8f957746faa55b414ff93a2ab264e270d474952` 下载并校验；本轮只抽取 30 条元数据，不运行其中 30 个外部仓库。
- SWE-Gym/BFCL 数据未下载；OpenHands SFT 路径缺失；checkpoint-gate Gym parquet 存在但仅作旧证据。
- 本轮不调用 API、不训练模型、不修改外部仓库，也未运行完整 Graphectory/SyncMind/GuardAgent Docker 复现。

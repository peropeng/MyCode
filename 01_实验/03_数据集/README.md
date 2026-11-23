# 当前研究数据集

按当前开题[表5-1 数据来源及用途](../../03_%E5%BC%80%E9%A2%98/01_%E5%BD%93%E5%89%8D%E6%9D%90%E6%96%99_v1.0/%E5%BC%80%E9%A2%98%E6%8A%A5%E5%91%8A_%E8%AF%84%E8%AE%AE%E4%BF%AE%E8%AE%A2%E7%A8%BF_v1.0.md)，当前使用以下三个数据集。

| 数据集 | 用途 | 官方来源 | 实际下载 |
| --- | --- | --- | --- |
| AgenTracer | 根因排序模型学习，以及代码与数学任务比较。 | [官方来源](https://github.com/bingreeky/AgenTracer) | [agentracer-data-v1.0.0.zip](https://github.com/bingreeky/AgenTracer/releases/download/data-v1.0.0/agentracer-data-v1.0.0.zip) |
| AFTraj | 不同记录形式下的根因排序评价。 | [官方来源](https://huggingface.co/datasets/ZBox008003/AFTraj) | [aftraj_safe.parquet](https://huggingface.co/datasets/ZBox008003/AFTraj/resolve/b7cb236e348bb4ac10059dce4da91a05ee8cc8f7/aftraj_safe.parquet)、[aftraj_unsafe.parquet](https://huggingface.co/datasets/ZBox008003/AFTraj/resolve/b7cb236e348bb4ac10059dce4da91a05ee8cc8f7/aftraj_unsafe.parquet)、[splits_test.json](https://huggingface.co/datasets/ZBox008003/AFTraj/resolve/b7cb236e348bb4ac10059dce4da91a05ee8cc8f7/splits_test.json) |
| SWE-Gym | 构造共同故障状态，评价软件任务恢复。 | [官方来源](https://huggingface.co/datasets/SWE-Gym/SWE-Gym) | [任务数据](https://huggingface.co/datasets/SWE-Gym/SWE-Gym/resolve/bb94ed9e39bbeb96a7fcbfb533b80f25a7fd59cb/data/train-00000-of-00001.parquet)、[配套公共执行轨迹](https://huggingface.co/datasets/SWE-Gym/OpenHands-SFT-Trajectories/resolve/4aaa5a4a4b5861f4799d2336908760c190ac3b17/data/train.success.oss-00000-of-00001.parquet) |

## 版本与获取

AgenTracer使用`data-v1.0.0`。AFTraj及SWE-Gym各文件使用锁定版本，具体版本、下载地址、许可和已有核对记录见[来源与下载清单](%E6%9D%A5%E6%BA%90%E4%B8%8E%E4%B8%8B%E8%BD%BD.json)。SWE-Gym的任务数据与配套公共执行轨迹统一归入SWE-Gym。

下载上游文件后，仍需按实验清单核对选定输入与封存原件的对应关系。AgenTracer采用官方来源获取，未确认的再分发许可不作扩展。

以下命令只列出这三个数据集，不下载或解析数据：

```powershell
python 01_实验/03_数据集/fetch_data.py
```

显式指定名称后下载到忽略的本地目录，可用`--filename`选择所需文件：

```powershell
python 01_实验/03_数据集/fetch_data.py --name AgenTracer
python 01_实验/03_数据集/fetch_data.py --name AFTraj --filename aftraj_safe.parquet
python 01_实验/03_数据集/fetch_data.py --name SWE-Gym --filename train-00000-of-00001.parquet
```

下载器不读取轨迹或评价标签。编码器模型作为[实验条件依赖](../02_%E5%AE%9E%E9%AA%8C%E6%9D%A1%E4%BB%B6/%E7%BC%96%E7%A0%81%E6%A8%A1%E5%9E%8B%E6%9D%A5%E6%BA%90.json)单独登记。

# v10 CPU 输入补充候选

当前状态是未训练的 CPU 原型，尚未正式采用。v9 正按原绑定执行；本目录没有编码、GPU、优化器或科学训练入口。

六条件共同保留 v9 的 task128 与 task+原始单步128，并追加既有 content128 的逐行 float32 L2 向量。旧 content 来自当前单步的非空 content/action/thought，不含 task、role、任务 ID 或旧基线输出。原始向量范数被舍弃，不拟合跨记录统计；NPZ 中的 agent32 不读取。

唯一结构改变是共享 input_projection 从 224→96 扩为 352→96，列顺序为旧 step128、任务 query96、新增 content128。所有六条件有相同的 231578 个参数，比 v9 增加 12288 个；共同评分末端的一个标量 bias 仍只改变候选共同平移。A/B、记忆与 pair/head 运算直接继承冻结 v9，不新增评分出口或超参数搜索。

`data.py` 先以 Gold 关闭模式读取 v9 公共数据，再核对全部 731 个旧 NPZ 的封存 SHA、embedding binding 和完整有序匿名 turns 的 input SHA。旧 runner 与 text_of 源片段均匹配原冻结，逐步核对原始三字段与匿名三字段一致并登记 text_of、原向量、归一向量的 SHA。缓存来源由这些既有绑定确立，本次没有重新编码来证明数值可复现性。

`verify_input_cpu.py` 已通过五类改动相关检查：731 条/716 组/7366 步对应关系；六条件相同初始化与参数数；合成 CE+0.2pairwise 梯度通达 task 和两路128维输入以及四个 query 块；改变一个 content 行只改变其自己的记忆前 x；新增列置0并恢复旧列时，六条件复现 v9 分数，最大误差为 float64 舍入量。原 v9 的完整核心值/梯度报告直接绑定复用，没有重复无关测试。

证据为 `results/v10/cpu_input_v1/input_audit.json` 与 `report.json`。CPU 运行1线程，零真实 Gold、零 optimizer、零 GPU、零 API、零基线执行。该候选是共同表示补充，不是新增论文创新；是否进入新科学版本，要等 v9 完整15折门的裁决和另行冻结决定。

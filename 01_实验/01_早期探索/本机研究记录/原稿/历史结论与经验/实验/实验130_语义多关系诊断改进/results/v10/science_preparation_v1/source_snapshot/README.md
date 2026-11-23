# v10 CPU 输入补充候选

当前状态是已通过独立审阅的未训练 CPU 原型，并已新增尚未采用、冻结或发布的科学入口草案。v9 正按原绑定执行；v10 没有执行编码、GPU、优化器或科学训练。CPU 检查当时目录只有三份 Python 文件，没有科学入口；该时刻 README 的原字节已保存在 `results/v10/cpu_review_snapshot_v1/README.md`，与原审阅记录区分。

六条件共同保留 v9 的 task128 与 task+原始单步128，并追加既有 content128 的逐行 float32 L2 向量。旧 content 来自当前单步的非空 content/action/thought，不额外拼接 task、role、任务 ID 或旧基线输出；原正文可能自然提到任务或角色，并未做语义清除。原始向量范数被舍弃，不拟合跨记录统计；NPZ 中的 agent32 不读取。

唯一结构改变是共享 input_projection 从 224→96 扩为 352→96，列顺序为旧 step128、任务 query96、新增 content128。所有六条件有相同的 231578 个参数，比 v9 增加 12288 个；共同评分末端的一个标量 bias 仍只改变候选共同平移。A/B、记忆与 pair/head 运算直接继承冻结 v9，不新增评分出口或超参数搜索。

`data.py` 先以 Gold 关闭模式读取 v9 公共数据，再核对全部 731 个旧 NPZ 的封存 SHA、embedding binding 和完整有序匿名 turns 的 input SHA。旧 runner 与 text_of 源片段均匹配原冻结，逐步核对原始三字段与匿名三字段一致并登记 text_of、原向量、归一向量的 SHA。缓存来源由这些既有绑定确立，本次没有重新编码来证明数值可复现性。

`verify_input_cpu.py` 已通过五类改动相关检查：731 条/716 组/7366 步对应关系；六条件相同初始化与参数数；合成 CE+0.2pairwise 梯度通达 task 和两路128维输入以及四个 query 块；改变一个 content 行只改变其自己的记忆前 x；新增列置0并恢复旧列时，六条件复现 v9 分数，最大误差为 float64 舍入量。原 v9 的完整核心值/梯度报告直接绑定复用，没有重复无关测试。

证据为 `results/v10/cpu_input_v1/input_audit.json` 与 `report.json`。CPU 运行1线程，零真实 Gold、零 optimizer、零 GPU、零 API、零基线执行。该候选是共同表示补充，不是新增论文创新；是否进入新科学版本，要等 v9 完整15折门的裁决和另行冻结决定。

新增草案包括 `science_data.py`、`runner.py`、`schedule.py`、评估与结果验证文件，以及 `scientific_protocol.json`。三份原型 Python 文件和 CPU 报告保持原 SHA。科学草案的唯一模型/输入变化是同一公共 content128 通路；固定 seed、组折、损失、优化设置、AB 主模型、原强门、六机制比较以及先 AB15 后条件75均照用 v9。

`readiness.py` 要求 v9 的调度器已结束、全部15折/冻结/checkpoint/评估被最终清单封存且原强门明确 FAIL。它逐项校验前版清单，重新按原门读取完整汇总，并拒绝前版 PASS、未完成、仍有运行锁或出现未授权控制的状态。此前不允许 v10 冻结；即使前版满足，还必须有另行匹配协议与前版清单的 `scientific_adoption.json`，之后才可创建新绑定，并以独立 `scientific_release.json` 控制 GPU/训练及 Gold 读取路径。

草案只做了静态/合成入口检查：新增外层前置条件16项、沿用 AB15→75门11项通过。测试中的仿真 adoption/binding/release 全在各检查的 `synthetic_files` 子目录，不是实际发布；生产位置没有这些文件，也没有调用 freeze、preflight 或 fit。原型通过或入口检查通过均不等于精度通过或已决定采用。

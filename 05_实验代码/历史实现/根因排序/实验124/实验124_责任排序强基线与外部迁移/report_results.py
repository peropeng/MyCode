"""Generate advisor-readable report after all formal outputs exist."""
import statistics,json
from runner import HERE,ROOT,load,publish,sha,data
p=load(HERE/'results/panel_a.json'); final=load(HERE/'results/final_audit.json'); independent=load(HERE/'results/independent_result_audit.json'); ext=load(HERE/'results/external_gate.json')
assert final['all_pass'] and independent['all_pass']
old=load(ROOT/'实验/实验112C_RQ1时序依赖排序纠正式复跑/results/formal_corrected_nested_oof_results.json')
folds=[load(f) for f in sorted((HERE/'results/folds').glob('*.json'))]
emb=load(HERE/'results/embedding_audit.json'); parity=load(HERE/'results/embedding_batch_parity.json'); bind=load(HERE/'results/preclaim_binding.json')
matrix=[]
for c in ['A_plus_B','StepFinder','pairwise_B','local','recency']:
    if c=='StepFinder':
        r1=statistics.mean(s['stepfinder_r1'] for s in p['seeds']); r3=statistics.mean(s['stepfinder_r3'] for s in p['seeds']); m3=statistics.mean(s['stepfinder_mrr_at3'] for s in p['seeds'])
    else:
        r1=statistics.mean(statistics.mean(s['group_r_at_1'][c].values()) for s in old['results_by_seed']); r3=statistics.mean(statistics.mean(s['group_r_at_3'][c].values()) for s in old['results_by_seed'])
        m3=None
    matrix.append({'method':c,'mrr':p['task_mrr_seed_mean'][c],'r_at_1':r1,'r_at_3':r3,'mrr_at3':m3})
cost={'fold_train_validation_refit_held_seconds':sum(f['seconds'] for f in folds),'embedding_seconds':emb['seconds'],'training_peak_cuda_allocated_bytes':max(f['peak_gpu_bytes'] for f in folds),'embedding_peak_cuda_allocated_bytes':emb['peak_gpu_bytes'],'actual_fits':30,'checkpoint_count':15,'selection_epochs':sum(len(f['selection']) for f in folds),'full_outer_refit_epochs':sum(f['selected_epoch'] for f in folds),'paid_api_calls':0,'llm_generation_calls':0,'embedding_model_generation_tokens':0,'paid_cost':0,'runtime':'Python 3.12.14 / torch 2.7.1+cu128 / CUDA 12.8 / RTX 5070 12 GiB','initial_asset_gate_runtime':'Legacy Python 3.13 for read-only asset reconstruction, then formal isolated Python 3.12','network':'Torch wheel 3273024349 bytes and Qwen weights 1191586416 bytes successfully SHA-verified; failed full-stream requests and dependency traffic not fully metered, so these sizes are not a total transfer-cost claim.'}
_,development,_=data()
cost['final_cache_local_embedding_content_forward_calls']=sum((len(r['turns'])+7)//8 for r in development)
cost['final_cache_local_embedding_role_forward_calls']=len({t['role'] for r in development for t in r['turns']})
cost['embedding_forward_call_accounting']='Exact from completed fresh final cache and fixed batch8 loop; scalar preflight and synthetic smoke calls additional, not included in final-cache count.'
cost['embedding_input_tokens']=None
publish(HERE/'results/cost_and_execution.json',cost)
publish(HERE/'results/metrics_table.json',{'unit':'task-group equally weighted, records within group and then three seeds averaged','rows':matrix,'seeds':p['seeds'],'comparisons':p['comparisons'],'no_new_external_scores':True})
table='\n'.join(f"| {x['method']} | {x['mrr']:.6f} | {x['r_at_1']:.6f} | {x['r_at_3']:.6f} |" for x in matrix)
comparison='\n'.join(f"| A+B − {c} | {v['absolute_delta']:+.6f} | {v['relative_gain']:+.2%} | [{v['ci95'][0]:+.6f}, {v['ci95'][1]:+.6f}] | {v['all_seed_positive']} |" for c,v in p['comparisons'].items())
seedtable='\n'.join(f"| {s['seed']} | {s['task_mrr']['A_plus_B']:.6f} | {s['task_mrr']['StepFinder']:.6f} | {s['stepfinder_r1']:.6f} | {s['stepfinder_r3']:.6f} |" for s in p['seeds'])
verdict='同数据强基线比较通过预注册内部增量门' if p['decision']=='INTERNAL_GO' else '同数据强基线下，原方法新增增量未证成'
text=f'''# Exp124：责任排序强基线与外部迁移

状态：Panel A 已实际完成15个outer fold、三种子2193条折外预测；Panel B 资产门停止；Who&When 生成模型基线未完成。最终裁决：**{verdict}**（`{p['decision']}`）。这是既有开发集内部证据，不是新独立外测，也不覆盖历史Exp112C。

## 可向导师说明的结果

在相同731条记录、716个独立任务组、全部7366个候选步骤上，新增实际运行的StepFinder同数据适配实现。原A+B沿用未改动的合法Exp112C预测；最强合法比较器为`{p['strongest_baseline']}`。任务先在组内平均，再对三种子平均；不能把2193条seed×record当独立样本。

| 方法 | full MRR | R@1 | R@3 |
|---|---:|---:|---:|
{table}

| seed | A+B full MRR | StepFinder full MRR | StepFinder R@1 | StepFinder R@3 |
|---:|---:|---:|---:|---:|
{seedtable}

| 配对比较 | MRR绝对差 | 相对提升 | 任务级95% CI | 三种子均正 |
|---|---:|---:|---|---|
{comparison}

CI为716个任务组等权、每任务先汇总三种子、5000次配对bootstrap；主门同时要求相对最强者≥10%、CI下界>0、三种子均正及审计全部通过。StepFinder另报MRR@3={statistics.mean(s['stepfinder_mrr_at3'] for s in p['seeds']):.6f}，不能与表中的full MRR混称。完整逐任务值、逐候选分数、排序、种子和训练过程分别在`panel_a.json`、`folds/`、`freezes/`。

## 同数据适配具体做了什么

固定官方StepFinder commit `48d71c7090adca3667a31b043a78484f407b4a2f`，直接导入官方`model.py`的TFE、ASI、评分头和联合损失，使用真实`Qwen/Qwen3-Embedding-0.6B` revision `97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3`。所有模型文件核对固定版本来源SHA；权重SHA为`0437e45c94563b09e13cb7a64478fc406947a93cb34a7e05870fc8dcd48e23fd`。

两方使用同一匿名角色记录及完整turn候选。StepFinder把可见`content/action/thought`序列化为内容文本，角色输入为`role_n`；任务ID、题目、来源、Gold和错误解释不进入表示。原A+B只利用这些观测的结构；StepFinder保留真实语义嵌入，不能把其弱化成随机向量或小模型。官方原实现只编码`content`，因此本轮准确名称是“同数据适配”，不是使用作者4168条生成训练集的原论文复现。

沿用E96固定三seed五折任务划分。每outer在其余四折中固定第一折验证、其余三折训练，按验证任务等权Top1选epoch（并列最早），然后以同一官方默认超参在完整outer-train重拟合该epoch数。held只在checkpoint与配置落盘后评价一次。官方每epoch查看test选checkpoint的做法未沿用。共30个模型fit：15个内部选epoch fit、15个完整outer-train refit；不是反复选择held最优结果。

## 外部迁移与剩余基线

| 分支 | 状态 | 可核实原因 |
|---|---|---|
| TraceElephant外测 | `ASSET_STOP`；新外部评价0 | 固定revision全部220 run已有历史用途：Exp84评价217 run/172组，另2 run曾筛选标签、1 run用于适配器开发。重新下载不能清除历史暴露。 |
| Who&When整段/逐步归因 | `NOT_RUN_RESOURCE_GAP` | 未发现实验可用的生成API配置、常见本地生成服务监听或生成模型文件；空`.ollama/models`不是可用模型。Qwen embedding不具备生成归因能力。 |
| 历史180条confirmation | 保持封存 | 未进入编码、拟合、评分或选模型。 |

外测门使用同revision的历史逐run下载账本和机器结果逐项核对，未把仅5条恢复接入案例误当成全部历史使用。多Gold/step_id映射规则已在协议冻结，但先验历史用途门已剔除全集；因此没有合法任务需要进入问句重叠和新模型评价阶段，不声称跨数据去重已通过。TraceElephant标签语义也未混入AFTraj的同一种因果真值。最小剩余外测缺口是**真正未用于开发/评价且步骤标签适配的独立任务**；本轮不能宣称正式论文强基线和迁移证据已齐全。

## 环境、冻结和审计

实际运行环境：{cost['runtime']}。正式训练代码commit：{', '.join(sorted({f['git_commit'] for f in folds}))}；协议SHA `{bind['protocol_sha256']}`。嵌入用时{cost['embedding_seconds']:.2f}秒；15折选epoch＋refit＋held用时合计{cost['fold_train_validation_refit_held_seconds']:.2f}秒。训练峰值CUDA已分配显存{cost['training_peak_cuda_allocated_bytes']/1024**3:.3f}GiB、嵌入峰值{cost['embedding_peak_cuda_allocated_bytes']/1024**3:.3f}GiB；这是进程分配量，不是整机桌面显存。新付费资源、LLM API及生成token调用均为0；公开资产HTTP下载与元数据请求另计，失败重试总流量未完整计量。旧A+B运行硬件不同，未作公平速度优劣声称。

Windows TLS/大文件流超时通过官方URL分块下载与SHA检查修复；PyArrow选择可下载的20.0.0，torch选择支持RTX5070的2.7.1+cu128，未缩小Qwen或改StepFinder模型。标量预检编码慢，在任何fit/held前提交协议v2批量性能修订，保留v1与旧缓存；最终特征全部重建为batch8。64条训练输入/874步数值核验：最低余弦{parity['minimum_cosine']:.9f}，平均{parity['mean_cosine']:.9f}；FP16最大绝对差{parity['max_absolute_feature_difference']:.7f}，无混合缓存。

历史Exp112C结果LF SHA `d99f9468adeadec4e69e30e0a2c44aafc277c4a034be0f1b7f678c4da5deb851`吻合封存；Windows checkout物理SHA因CRLF不同而另记。迁移仓库缺少旧`4fe2d9` Git对象，原协议也没有封存全runner哈希，因此不能虚称旧对象逐文件验证。本轮绑定权威`ab1fa8d5b23a9d591c5809ea299ce381eb99b21c`源码、原结果已封存的tie函数SHA、科学常量、精确数据SHA和划分算法。原artifact未存逐fold组名单，本轮独立重建并逐fold校验原确定性keyset；同时校验每记录候选长度、raw rank组汇总与旧结果一致。这个来源限制保留在`preclaim_binding.json`。

独立终态审计确认：15个checkpoint在held前冻结、每seed 731条预测恰好覆盖一次、组隔离、候选全排列及分数/Gold rank一致、原比较器候选范围一致、原子输出不覆盖。`.gitattributes`禁止字节转换，集成后可再校验冻结SHA。

## 交付和复核

- 协议：`protocol.json`；初始协议和性能修订保留为`protocol_v1_preflight.json`。
- 正式结果：`results/panel_a.json`、`metrics_table.json`、`final_audit.json`、`independent_result_audit.json`。
- 来源与边界：`asset_gate.json`、`preclaim_binding.json`、`model_source_manifest.json`、`external_gate.json`、`who_when_resource_gate.json`。
- 可审查资产：`results/checkpoints.zip`（15个实际state_dict）和`results/embeddings.zip`（731条特征），逐文件SHA见`artifact_manifest.json`；公开Qwen权重未提交。
- 运行日志、耗时与训练轨迹：`results/logs/`、`cost_and_execution.json`、`freezes/`。保留执行worktree中的模型、独立环境及原始资产。

无需训练即可运行`verify_delivery.ps1`，或用任意Python 3执行`verify_delivery.py`，核对归档成员、runner、protocol和终态审计。实际命令为在保存的worktree内用`.venv/Scripts/python.exe -X utf8`依次执行`smoke.py`、`runner.py prepare`、`runner.py run`、`package_results.py`、`verify_delivery.py`；输出已发布后禁止同路径覆盖重跑。

许可证：StepFinder MIT（仓内LICENSE实读），AFTraj CC BY4.0，Qwen Apache2.0；TraceElephant历史固定资产审计记录CC BY4.0。未重新分发第三方源码或公开模型权重。
'''
(HERE/'README.md').write_text(text,encoding='utf-8')
print(json.dumps({'decision':p['decision'],'strongest_baseline':p['strongest_baseline'],'table':matrix,'comparison_to_stepfinder':p['comparisons']['StepFinder'],'cost':cost},ensure_ascii=False,indent=2))

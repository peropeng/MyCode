本脚本仅给ROOT执行，当前未运行。默认调用只输出关闭回执，不读写账、不创建授权文件。

ROOT复核后，用旧实际财务解释器执行：

```powershell
& 'D:/Code/毕设/graduate-thesis-experiments/工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe' -B 'D:/Code/毕设/graduate-thesis-experiments/工作区/1012-exp259-window-finance-postreview/实验/实验259_四小时连续费用隔离/ROOT_CALLER_STAGING/register260_source3_root_only.py' --execute-root-only
```

精确绑定41920/134362801232005425/RootExp260_Flow_814f53883450ed544ec42809，Ready指定的SOURCE3/Moto5134/trial1、原T0、完整caller seal/contract与原未发送body。完整科学授权取260模板全部六个true必需字段，native权限只在科学whole中放行；财务policy/release仍native/private=false。stage recover、index0..2/turn1..128/call1..128，role取原FIRST_UNPOST_READY，不扩大动态角色。

脚本构建真config（不改旧cap/phase）、含260实际公共adapter的新dispatcher seal、policy、finance release与staged whole。原ActualIO byte0中prepare_registration→protected→原子write→读回，增加revision使并发旧GET快照失效；提交之后才发布whole runtime grant。脚本不GET余额、不POST、不执行native，也不恢复owner。ROOT检查登记回执后另行按Ready.resume_control恢复。

构建/登记可失败；任何失败须保存原始异常，不自动重试或覆盖authority。首次构建后再次执行默认拒绝覆盖，ROOT应先查账/文件边界，不重新POST。父ROOT已审旧闭合review仍逐次实际验证。三分钟helper只机械构造ROOT已指定单一flow，不自动证明具体方法资格。

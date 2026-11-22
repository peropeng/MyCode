"""Read-only execution observation; sole writer of coordination/lane224.json."""
import datetime,hashlib,json,os,sys,time
from decimal import Decimal
from pathlib import Path
E=Path(__file__).resolve().parent
ROOT=E.parents[3]
COORD=ROOT/'工作区/1008-2320-baseline-main/coordination'
STATE=ROOT/'工作区/1003-diagnosis-investigation/exp132_review/new_window_2332/finance/shared_flash_budget.json'
def read(p,default=None):
 try:return json.loads(p.read_text('utf-8-sig'))
 except FileNotFoundError:return default
def atomic(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.'+str(os.getpid())+'.tmp')
 tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,p)
def snapshot():
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 runtime=read(COORD/'runtime_release.json',{})
 ledger=read(STATE,{})
 rows=[];active=[];latest=None
 for namespace in ('engineering_core_check','fresh_main'):
  recovery=E/namespace/'recovery'
  for flow in sorted(recovery.glob('*/*')):
   result=read(flow/'result.json')
   events=[]
   if (flow/'stage_ledger.jsonl').exists():
    events=[json.loads(x) for x in (flow/'stage_ledger.jsonl').read_text('utf-8-sig').splitlines() if x.strip()]
   last=events[-1] if events else {}
   progress=last.get('at_utc')
   if progress and (latest is None or progress>latest):latest=progress
   receipts=[read(p) for p in (flow/'llm').glob('*_finance_receipt.json')]
   settled=[r for r in receipts if r.get('status')=='SETTLED' and not r.get('already_settled_prefix_reuse')]
   row={'namespace':namespace,'task_id':flow.parent.name,'method':flow.name,'stage':last.get('stage'),
        'last_progress_utc':progress,'logical_returned_calls':sum(x.get('stage')=='Flash_actual_response224' for x in events),
        'new_paid_calls':len(settled),'new_fees_CNY':str(sum((Decimal(r['usage_peak_cost_CNY']) for r in settled),Decimal(0))),
        'public_native_calls':sum(x.get('stage')=='public_native_actual' for x in events),
        'candidate_applications':sum(x.get('stage')=='patch_application' for x in events),
        'ledger_mtime_utc':datetime.datetime.fromtimestamp((flow/'stage_ledger.jsonl').stat().st_mtime,datetime.timezone.utc).isoformat() if events else None,
        'result':{k:result.get(k) for k in ('status','success','primary_eligible','runtime_core','new_paid_API','hidden_acceptance_calls')} if result else None}
   if row['result']:row['result'].pop('runtime_core',None);row['core_complete']=result.get('runtime_core',{}).get('complete')
   rows.append(row)
   if not result:active.append(row)
 completed=[r for r in rows if r['result']]
 controls={p.name:read(p,{}) for p in E.glob('execution_checkpoint224_*.json')}
 main=[r for r in completed if r['namespace']=='fresh_main']
 core=[r for r in completed if r['namespace']=='engineering_core_check']
 value={'schema':'lane224-observation/1','at_utc':now,'owner':'Agentless与本文执行线','worktree':str(E.parents[1]),
        'root_runtime_ready':runtime.get('root_runtime_ready',False),'runner':read(E/'supervision.json',{}),
        'runners':{p.name:read(p,{}) for p in E.glob('supervision_*_224.json')},'method_queue_controls':controls,
        'boundary_report':read(E/'boundary_report224.json',{}),
        'phase':active[-1]['namespace'] if active else ('WAIT_ROOT_RUNTIME_RELEASE' if not runtime.get('root_runtime_ready') else 'READY_OR_BETWEEN_FLOWS'),
        'current_case':active[-1]['task_id'] if active else None,'last_progress_utc':latest,
        'main_completed':len(main),'main_success':sum(r['result']['success'] is True for r in main),
        'main_known_failure':sum(r['result']['success'] is False for r in main),'main_unknown':sum(r['result']['success'] is None for r in main),
        'core_completed':len(core),'core_nonzero':any(r['result']['success'] is True and r.get('core_complete') for r in core),
        'new_paid_calls':sum(r['new_paid_calls'] for r in rows),'new_fees_CNY':str(sum((Decimal(r['new_fees_CNY']) for r in rows),Decimal(0))),
        'shared_spent_CNY':ledger.get('spent_CNY'),'shared_held_CNY':ledger.get('held_CNY'),'shared_blocked':ledger.get('blocked'),
        'rows':rows,'active_flows':active,'next_action':'本文main-ours与AL新5093工程core5093独立受root分方法grant调度；旧2238不重跑',
        'blockers':[] if runtime.get('root_runtime_ready') else ['ROOT_RUNTIME_RELEASE_MISSING_OR_NOT_READY_NO_POST_NATIVE'],
        'analysis_evidence':str(E/'公开失败分析与候选确认设计224.md'),
        'deployment_review':read(E/'deployment_review224.json',{}),
        'prepared_source_syntax_pass':True,'ready_to_seal_against_published_transport':True,
        'protocol_sha256':hashlib.sha256((E/'protocol224.json').read_bytes()).hexdigest(),
        'ready_seal_sha256':hashlib.sha256((E/'fresh_ready_seal224.json').read_bytes()).hexdigest(),
        'ready_seal_path':str(E/'fresh_ready_seal224.json'),
        'source_root_protocol_sha256':read(E/'protocol224.json')['source_root_protocol_sha256'],
        'engineering_grant_expected':str(E/'engineering_core_release224.json'),
        'main_grant_expected':str(E/'fresh_main_release224.json'),
        'ours_main_grant_expected':str(E/'fresh_ours_main_release224.json'),
        'second_core_grant_expected':str(E/'engineering_second_core_release224.json'),
        'method_grant_required_fields':{'root_authorized':True,'source_seal_sha256':'CURRENT_READY_SEAL_SHA256','phase':'Round2320Main for ours; Round2320Pilot for core5093','allowed_through_index':2},
        'ours_main_command':[str(ROOT/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'),'-B',str(E/'supervise_fresh224.py'),'main-ours'],
        'second_core_command':[str(ROOT/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'),'-B',str(E/'supervise_fresh224.py'),'core5093'],
        'engineering_command':[str(ROOT/'工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe'),'-B',str(E/'supervise_fresh224.py'),'core']}
 atomic(COORD/'lane224.json',value)
 atomic(E/'lane_observation224.json',value)
 print(json.dumps({k:value[k] for k in ('at_utc','phase','current_case','main_completed','core_completed','new_paid_calls','shared_spent_CNY','shared_held_CNY')},ensure_ascii=False),flush=True)
 return value
if __name__=='__main__':
 if '--watch' in sys.argv:
  while True:
   snapshot()
   if (E/'STOP_OBSERVER224.json').exists():break
   time.sleep(120)
 else:snapshot()

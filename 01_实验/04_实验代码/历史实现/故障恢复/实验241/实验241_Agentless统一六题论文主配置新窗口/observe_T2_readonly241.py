from pathlib import Path
import json,re
E=Path(__file__).resolve().parent;f=E/'runtime_v7_SOURCE/science_once_six/getmoto__moto-6387/actor_flow'
ev=[json.loads(x) for x in (f/'events.jsonl').read_text('utf-8').splitlines()]
x=ev[-1];rsp=sorted(p for p in (f/'llm').glob('*_response.json') if re.match(r'^\d+_response.json$',p.name))
patches=sum(x.get('stage')=='llm' and x.get('evidence',{}).get('role')=='patch' for x in ev)
repros=sum(x.get('stage')=='llm' and x.get('evidence',{}).get('role')=='reproduction' for x in ev)
r={'UTC':x.get('at_utc'),'event':x.get('event'),'stage':x.get('stage'),'role':x.get('evidence',{}).get('role'),'requests':len(list((f/'llm').glob('*_request.json'))),'responses':len(rsp),'patch_responses':patches,'repro_responses':repros,'result_exists':(f/'result.json').exists(),'immutable_exists':(f/'immutable_selection.json').exists(),'authorSTOP_exists':(f.parent/'supervision/PARENT_STOP.json').exists(),'private_namespace_exists':(f/'external_once_private').exists()}
if rsp:
 rec=[json.loads(p.read_text('utf-8'))['_finance_receipt'] for p in rsp];r.update(fee_accounting_upper_CNY=sum(float(v['usage_accounting_upper_CNY']) for v in rec),finance_statuses=list(set(v['status'] for v in rec)),recent_balance_CNY=rec[-1].get('balance_after_CNY'))
print(json.dumps(r,ensure_ascii=False))
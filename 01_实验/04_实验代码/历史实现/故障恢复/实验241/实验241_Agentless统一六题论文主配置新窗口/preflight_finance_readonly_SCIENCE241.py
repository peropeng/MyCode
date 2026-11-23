"""Authorized atomic read/current balance GET only; never writes ledger or POST."""
from pathlib import Path
import datetime,importlib.util,json,os,sys,time,hashlib
E=Path(__file__).resolve().parent;D=E/'runtime_v6_MECHANICAL_SOURCE'
R=Path('D:/Code/毕设/graduate-thesis-experiments');F=R/'工作区/1010-unified-six/finance'
sys.dont_write_bytecode=True
p=json.loads((D/'science_release_candidate_FALSE/getmoto__moto-5406/protocol.SOURCE_ONLY.json').read_text('utf-8'))
for path in reversed(p['controller_dependency_paths']):sys.path.insert(0,path)
spec=importlib.util.spec_from_file_location('_AL241_READONLY_PREFLIGHT_ROOT_COMPLETION',F/'completion_transport_v3.py')
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
io=m.LegacyIO();cfg=json.loads(Path(p['finance_config']).read_text('utf-8'));transport=m.make_transport(cfg,io)
with io.lock(time.monotonic()+30):
 state=io.read();pending=transport.validate(state,p['finance_phase']);blockflag=io.blocked()
 unknown=[v for v in pending if str(v['status']).startswith('UNKNOWN')]
 safe={'at_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'atomic_state_read_under_original_byte0':True,
  'state_path':str(io.m.STATE),'state_raw_SHA256_at_read':hashlib.sha256(io.m.STATE.read_bytes()).hexdigest(),
  'blocked':bool(state.get('blocked') or blockflag),'blocked_reason':state.get('blocked_reason'),
  'record_count':len(state['reservations']),'spent_CNY':state['spent_CNY'],'held_CNY':state['held_CNY'],
  'UNKNOWN_pending':len(unknown),'RESERVED_pending':sum(v['status']=='RESERVED' for v in pending),
  'pending_roles':[{'ordinal':v['ordinal'],'phase':v['pilot'],'status':v['status'],'reserve_CNY':v['global_reserve']} for v in pending],
  'phase_spent_CNY':state['pilots'][p['finance_phase']]['spent_CNY'],'phase_held_CNY':state['pilots'][p['finance_phase']]['held_CNY'],
  'cumulative_cap_CNY':cfg['cumulative_cap_CNY'],'old_continuous_rows_not_reset':True,'manual_state_field_write':False,
  'POST_or_paid_generation':0,'shared_ledger_write':0}
key=os.environ.get('DEEPSEEK_API_KEY')
safe['paid_key_present']=bool(key)
if key:safe['current_balance_CNY']=str(io.balance(key,time.monotonic()+30))
else:safe['current_balance_CNY']=None
safe['can_start_under_readonly_snapshot']=not safe['blocked'] and not unknown and bool(key)
out=D/'SCIENCE_READONLY_FINANCE_PREFLIGHT241.json'
out.write_text(json.dumps(safe,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(safe,ensure_ascii=False,separators=(',',':')))

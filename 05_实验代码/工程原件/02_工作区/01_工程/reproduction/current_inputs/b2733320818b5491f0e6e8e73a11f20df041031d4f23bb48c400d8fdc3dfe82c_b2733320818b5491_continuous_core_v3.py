"""Active two-slot transport. Import has no network/ledger writes. HTTP outside byte0.
Existing284 rows/costs are never reset or repriced. Root must deploy explicitly.
"""
import sys
sys.dont_write_bytecode=True
import copy,datetime,hashlib,importlib.util,json,math,os,threading,time
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path
D=Decimal
HERE=Path(__file__).resolve().parent
PRICE={'verified_utc':'2026-10-08T17:31:01+00:00','source':'https://api-docs.deepseek.com/zh-cn/quick_start/pricing/','source_SHA256':'5a7b1832592387340f2fc456399b34b89b05f3fa167c2e35909e2fa4afe021e3','peak':['.04','2','8'],'offpeak':['.02','1','4'],'weekday_peak_UTC':[[1,4],[6,10]],'holidays':'conservative:weekday peak even if holiday; never false offpeak'}
class FinanceError(RuntimeError):pass
class FinanceGateRejected(FinanceError):pass
class FinanceUnknown(FinanceError):pass
# Compatibility names remain aliases, so callers see the original finance class names.
GateRejected=FinanceGateRejected
Unknown=FinanceUnknown
def dec(x):
 v=D(str(x))
 if not v.is_finite() or v<0:raise Unknown('INVALID_FINANCE_NUMBER')
 return v
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def offpeak_interval(start,end):
 verified=datetime.datetime.fromisoformat(PRICE['verified_utc']).timestamp()
 if not verified<=start<=end<=verified+86400:return False
 a=datetime.datetime.fromtimestamp(start,datetime.timezone.utc);b=datetime.datetime.fromtimestamp(end,datetime.timezone.utc)
 day=a.replace(hour=0,minute=0,second=0,microsecond=0)
 while day<=b:
  if day.weekday()<5:
   for lo,hi in ((1,4),(6,10)):
    if start<(day+datetime.timedelta(hours=hi)).timestamp() and end>=(day+datetime.timedelta(hours=lo)).timestamp():return False
  day+=datetime.timedelta(days=1)
 return True
def bounds(body,c):
 if body.get('model')!='deepseek-flash' or body.get('thinking')!={'type':'disabled'}:raise GateRejected('MODEL_THINKING_CHANGED')
 n=body.get('max_tokens');msgs=body.get('messages')
 if isinstance(n,bool) or not isinstance(n,int) or not 1<=n<=c['max_per_call_output'] or not isinstance(msgs,list) or not msgs or isinstance(body.get('seed'),bool) or not isinstance(body.get('seed'),int):raise GateRejected('BODY_BOUND_REQUIRED')
 # Financial upper bound is not a tokenized-context measurement. The model
 # service enforces its official1M context; preserve the complete body.
 # A successful response cannot exceed that input capacity. Reserve at
 # full peak rate and keep the existing unknown-response full-hold policy.
 cap=c.get('official_model_input_capacity_tokens')
 if cap!=1048576:raise GateRejected('OFFICIAL_MODEL_CAPACITY_BINDING_REQUIRED')
 legacy_size=len(canonical(body).encode())+4096*len(msgs)+2048
 size=min(legacy_size,cap)
 reserve=(D(size)*2+D(n)*8)/1000000
 return {'input_bound':size,'max_tokens':n,'global_reserve':str(reserve),'pilot_reserve':str(reserve),'reservation_version':'parallel_full_body_provider_capacity_peak_2_8_v2','legacy_body_byte_padding_upper':legacy_size,'official_input_capacity_tokens':cap,'context_enforced_by_provider_no_local_byte_gate':True}
def usage(response,b,start,end,price_verified):
 if response.get('model')!='deepseek-flash':raise Unknown('RESPONSE_MODEL')
 u=response.get('usage',{});p=u.get('prompt_tokens');o=u.get('completion_tokens')
 if any(isinstance(v,bool) or not isinstance(v,int) or v<0 for v in (p,o)) or p>b['input_bound'] or o>b['max_tokens']:raise Unknown('USAGE_BOUNDS')
 hit=u.get('prompt_cache_hit_tokens',0);miss=u.get('prompt_cache_miss_tokens',p-hit)
 if any(isinstance(v,bool) or not isinstance(v,int) or v<0 for v in (hit,miss)) or hit+miss!=p:raise Unknown('CACHE_USAGE')
 peak=(D(hit)*D('.04')+D(miss)*2+D(o)*8)/1000000
 discounted=price_verified and offpeak_interval(start,end)
 amount=peak/2 if discounted else peak
 return {'price_basis':'verified_whole_interval_offpeak_CNY' if discounted else 'conservative_peak_CNY','usage_accounting_upper_CNY':str(amount),'usage_peak_equivalent_CNY':str(peak),'usage_peak_cost_CNY':str(amount),'legacyusage_peak_cost_CNY':str(amount),'legacy_scalar_definition':'compatibility field equals accounting upper, not peak equivalent','price_reference':PRICE,'not_invoice':True}
def flow_time_left(env):
 value=env.time_left()
 if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value>604800:
  raise GateRejected('FINITE_BOUNDED_FLOW_REQUIRED')
 return value

def new_requests_closed(c,clock):
 if Path(c['closure_flag']).exists():return True
 if c.get('forward_closure_flag') and Path(c['forward_closure_flag']).exists():return True
 boundary=c.get('no_new_utc')
 return boundary is not None and clock()>=datetime.datetime.fromisoformat(boundary).timestamp()

def birth(pid):
 if os.name!='nt':
  try:os.kill(pid,0);return 'live-posix:'+str(pid)
  except OSError:return None
 import ctypes
 from ctypes import wintypes as W
 k=ctypes.WinDLL('kernel32',use_last_error=True)
 k.OpenProcess.argtypes=[W.DWORD,W.BOOL,W.DWORD];k.OpenProcess.restype=W.HANDLE
 h=k.OpenProcess(0x1000,False,pid)
 if not h:return None
 try:
  fs=[W.FILETIME() for _ in range(4)];k.GetProcessTimes.argtypes=[W.HANDLE]+[ctypes.POINTER(W.FILETIME)]*4
  if not k.GetProcessTimes(h,*[ctypes.byref(f) for f in fs]):return None
  return str((fs[0].dwHighDateTime<<32)|fs[0].dwLowDateTime)
 finally:k.CloseHandle.argtypes=[W.HANDLE];k.CloseHandle(h)
def owner():
 return {'owner_PID':os.getpid(),'owner_birth':birth(os.getpid()),'owner_thread':threading.get_ident()}
def alive(r):
 if birth(r.get('owner_PID',-1))!=r.get('owner_birth'):return False
 if r['owner_PID']==os.getpid():return any(t.ident==r.get('owner_thread') and t.is_alive() for t in threading.enumerate())
 return True
class Transport:
 def __init__(self,io,c,clock=time.time,monotonic=time.monotonic,pause=time.sleep,owner_fn=owner,alive_fn=alive,price_verified=True):
  self.io=io;self.c=c;self.clock=clock;self.mono=monotonic;self.pause=pause;self.owner=owner_fn;self.alive=alive_fn;self.price_verified=price_verified
 def validate(self,s,phase):
  if s.get('schema')!='shared-Flash-window-budget/1' or s.get('window')!='new_window_2332' or dec(s.get('cap_CNY'))!=8 or dec(self.c['cumulative_cap_CNY'])!=8 or dec(self.c['floor_CNY'])!=D('1.02') or phase not in s['pilots'] or phase not in self.c['phases']:raise Unknown('LEGACY_SCHEMA_NO_RESET')
  cap=dec(self.c['phases'][phase]['cap_CNY'])
  if dec(s['pilots'][phase]['cap_CNY'])!=cap or phase not in ('Round2320Pilot','Round2320Main') or cap>(D('2.00') if phase=='Round2320Pilot' else D('5.05264124')):raise Unknown('UNREGISTERED_OR_EXCESS_PHASE_CAP')
  dec(s['spent_CNY']);dec(s['held_CNY'])
  pending=[r for r in s['reservations'] if r['status']=='RESERVED' or str(r['status']).startswith('UNKNOWN')]
  if sum((dec(r['global_reserve']) for r in pending),D(0))!=dec(s['held_CNY']):raise Unknown('HELD_SUM_MISMATCH')
  for name,p in s['pilots'].items():
   if sum((dec(r['pilot_reserve']) for r in pending if r['pilot']==name),D(0))!=dec(p['held_CNY']):raise Unknown('PHASE_HELD_SUM_MISMATCH')
  return pending
 def write(self,s):
  s['parallel_finance_revision']=int(s.get('parallel_finance_revision',0))+1
  self.io.write(s)
 def checked(self,s,phase):
  try:pending=self.validate(s,phase)
  except Exception:
   self.block(s,None,'INVALID_LEDGER_NO_RESET');raise Unknown('INVALID_LEDGER_NO_RESET') from None
  if s.get('blocked') or self.io.blocked():raise Unknown('GLOBAL_BLOCKED_NO_NEW_POST')
  bad=[r for r in pending if r['status']=='RESERVED' and (not self.alive(r) or self.clock()>r.get('lease_expires_epoch',0))]
  if bad:
   for r in bad:r.update(status='UNKNOWN_FULL_RESERVATION_RETAINED',error='ORPHAN_OR_EXPIRED_OWNER')
   self.block(s,None,'ORPHAN_OR_EXPIRED_OWNER');raise Unknown('ORPHAN_FULL_HOLD_BLOCKED')
  return pending
 def cap_check(self,s,phase,b):
  g=dec(b['global_reserve']);p=s['pilots'][phase];cap=dec(self.c['phases'][phase]['cap_CNY'])
  if dec(s['spent_CNY'])+dec(s['held_CNY'])+g>8 or dec(p['spent_CNY'])+dec(p['held_CNY'])+g>cap:raise GateRejected('GLOBAL_OR_PHASE_CAP')
 def temporary_cap_wait(self,s,phase,b):
  """Only live pending holds can delay an otherwise affordable reservation."""
  g=dec(b['global_reserve']);p=s['pilots'][phase]
  global_cap=dec(self.c['cumulative_cap_CNY']);phase_cap=dec(self.c['phases'][phase]['cap_CNY'])
  permanent=dec(s['spent_CNY'])+g>global_cap or dec(p['spent_CNY'])+g>phase_cap
  pressured=dec(s['spent_CNY'])+dec(s['held_CNY'])+g>global_cap or dec(p['spent_CNY'])+dec(p['held_CNY'])+g>phase_cap
  return pressured and not permanent
 def block(self,s,r,reason):
  s.update(blocked=True,blocked_reason=reason)
  if r is not None:r.update(status='UNKNOWN_FULL_RESERVATION_RETAINED',error=reason)
  self.write(s);self.io.block({'reason':reason,'at_epoch':self.clock(),'full_peak_held_retained':True})
 def generate(self,env,body,role,phase='Round2320Pilot'):
  key=os.environ.get('DEEPSEEK_API_KEY')
  if not key:raise GateRejected('API_KEY_UNAVAILABLE')
  body=copy.deepcopy(body);b=bounds(body,self.c);sha=digest(body);me=self.owner()
  if not me.get('owner_birth'):raise Unknown('OWNER_BIRTH_UNKNOWN')
  rid=None;until=self.mono()+flow_time_left(env)
  # Persist the complete redacted body even for a gate rejection, before any POST.
  self.io.request(env,role,body,b,key)
  while rid is None:
   if new_requests_closed(self.c,self.clock) or self.mono()>=until:raise GateRejected('NO_NEW_FLASH_OR_FLOW_DEADLINE')
   with self.io.lock(until):
    s=self.io.read();pending=self.checked(s,phase)
    full=len(pending)>=2;revision=int(s.get('parallel_finance_revision',0))
    queue=full or self.temporary_cap_wait(s,phase,b)
    if not queue:self.cap_check(s,phase,b)
   if queue:self.pause(.02);continue
   # No network runs while byte0 is held. If the ledger changes during GET,
   # discard its account snapshot and fetch again before reserving.
   try:balance=dec(self.io.balance(key,until))
   except Exception as error:
    with self.io.lock(self.mono()+30):self.block(self.io.read(),None,'BALANCE_BEFORE_UNKNOWN')
    self.io.error(env,role,{'status':'UNKNOWN_BEFORE_RESERVATION','error':type(error).__name__+': '+str(error)},key)
    raise Unknown('BALANCE_BEFORE_UNKNOWN') from None
   with self.io.lock(until):
    s=self.io.read();pending=self.checked(s,phase)
    if len(pending)>=2 or int(s.get('parallel_finance_revision',0))!=revision or self.temporary_cap_wait(s,phase,b):continue
    self.cap_check(s,phase,b)
    g=dec(b['global_reserve']);p=s['pilots'][phase]
    floor=dec(self.c['floor_CNY'])+dec(self.c['margin_CNY'])
    if balance-dec(s['held_CNY'])-g<floor:
     if balance-g>=floor:continue # only live held pressure; release byte0 before retry
     raise GateRejected('BALANCE_MINUS_ALL_PENDING_FLOOR')
    if new_requests_closed(self.c,self.clock) or self.mono()>=until:raise GateRejected('NO_NEW_FLASH_OR_FLOW_DEADLINE')
    else:
     rid=max((r['ordinal'] for r in s['reservations']),default=0)+1
     row={'ordinal':rid,'slot_ordinal':rid,'pilot':phase,'status':'RESERVED','at_epoch':self.clock(),'lease_expires_epoch':self.clock()+max(0,until-self.mono())+90,'role':role,'call_ordinal':int(env.calls),'body_SHA256':sha,'balance_before_CNY':str(balance),**me,**b}
     s['held_CNY']=str(dec(s['held_CNY'])+g);p['held_CNY']=str(dec(p['held_CNY'])+g);s['reservations'].append(row);self.write(s);self.io.event({'type':'RESERVED',**row})
  posted=False;receipt=None;raw=None
  try:
   # Last atomic permission check prevents a reserved-but-not-yet-posted call
   # from starting after another request has made the window UNKNOWN.
   with self.io.lock(self.mono()+30):
    s=self.io.read();r=next(r for r in s['reservations'] if r['ordinal']==rid)
    if s.get('blocked') or self.io.blocked() or new_requests_closed(self.c,self.clock) or flow_time_left(env)<=0:
     raise Unknown('PERMISSION_OR_DEADLINE_AFTER_RESERVATION')
    r['post_dispatch_epoch']=self.clock();row=copy.deepcopy(r);self.write(s)
   posted=True
   raw=self.io.post(body,key,min(120,max(.1,flow_time_left(env)))) # intentionally OUTSIDE byte0
   returned=self.clock()
   self.io.raw_response(env,role,raw,key) # before status/JSON/usage validation
   result=self.io.decode(raw)
   cost=usage(result,b,row['post_dispatch_epoch'],returned,self.price_verified)
   if dec(cost['usage_peak_equivalent_CNY'])>dec(b['global_reserve']):raise Unknown('PEAK_USAGE_EXCEEDS_RESERVE')
   with self.io.lock(self.mono()+30):
    s=self.io.read();r=next(r for r in s['reservations'] if r['ordinal']==rid)
    if r['status']!='RESERVED':raise Unknown('OWN_SLOT_ALREADY_UNKNOWN')
    r.update(cost,finished_epoch=returned,finished_utc=datetime.datetime.fromtimestamp(returned,datetime.timezone.utc).isoformat(),balance_after_status='PENDING')
    self.release(s,r,dec(cost['usage_accounting_upper_CNY']),'SETTLED')
    receipt=copy.deepcopy(r);self.io.event({'type':'SETTLED',**receipt})
   # A known usage charge settles independently of another request's full hold.
   # An account GET failure/low floor blocks new work without erasing known cost.
   self.io.receipt(env,receipt,key)
   try:balance=dec(self.io.balance(key,self.mono()+30))
   except Exception:raise Unknown('BALANCE_AFTER_KNOWN_USAGE_UNKNOWN') from None
   with self.io.lock(self.mono()+30):
    s=self.io.read();r=next(r for r in s['reservations'] if r['ordinal']==rid)
    r.update(balance_after_CNY=str(balance),balance_after_status='KNOWN');s['last_valid_balance_CNY']=str(balance);self.write(s)
    receipt=copy.deepcopy(r)
   self.io.receipt(env,receipt,key)
   if balance<dec(self.c['floor_CNY'])+dec(self.c['margin_CNY']):raise Unknown('POST_BALANCE_BELOW_PROTECTED_FLOOR_KNOWN_USAGE')
   result=self.io.clean(result,key);result['_finance_receipt']=receipt
   self.io.final_response(env,result,key)
   return result
  except Exception as error:
   with self.io.lock(self.mono()+30):
    s=self.io.read();r=next(r for r in s['reservations'] if r['ordinal']==rid)
    known=r['status']=='SETTLED'
    reason='KNOWN_USAGE_SETTLED_ACCOUNT_OR_ARTIFACT_UNKNOWN' if known else 'POST_OR_SETTLEMENT_UNKNOWN_FULL_PEAK_HOLD'
    self.block(s,None if known else r,reason);receipt=copy.deepcopy(r)
   self.io.error(env,role,{'status':'KNOWN_USAGE_SETTLED_QUEUE_BLOCKED' if known else 'UNKNOWN_FULL_RESERVATION_RETAINED','ordinal':rid,'posted':posted,'error':type(error).__name__+': '+str(error),'raw_response_saved':raw is not None,'receipt':receipt},key)
   self.io.receipt(env,receipt,key)
   raise Unknown(reason) from None
 def release(self,s,r,cost,status):
  p=s['pilots'][r['pilot']]
  s['held_CNY']=str(dec(s['held_CNY'])-dec(r['global_reserve']));p['held_CNY']=str(dec(p['held_CNY'])-dec(r['pilot_reserve']))
  if cost is not None:s['spent_CNY']=str(dec(s['spent_CNY'])+cost);p['spent_CNY']=str(dec(p['spent_CNY'])+cost)
  r['status']=status;self.write(s)
class LegacyIO:
 def __init__(self):
  path=Path('D:/Code/毕设/graduate-thesis-experiments/工作区/1007-exp174-flash-feasibility/实验/实验174_Flash完整恢复可行性小试/flash_budget174.py')
  sys.path.insert(0,str(path.parent));spec=importlib.util.spec_from_file_location('_inactive_parallel_legacy174',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.NO_NEW=float('inf') # isolated helper only; candidate enforces new-reserve deadline itself, settlements remain possible
  self.m=m
 @contextmanager
 def lock(self,deadline):
  try:
   with self.m.financial_lock(deadline):yield
  except self.m.FinanceGateRejected as error:raise FinanceGateRejected(str(error)) from None
 def read(self):return json.loads(self.m.STATE.read_text('utf-8-sig'))
 def write(self,s):self.m.atomic(self.m.STATE,s)
 def event(self,x):self.m.event(x)
 def block(self,x):self.m.atomic(self.m.BLOCK,x)
 def blocked(self):return self.m.BLOCK.exists()
 def clean(self,x,key):return self.m.clean(x,key)
 def balance(self,key,deadline):
  import requests
  r=requests.get('https://api.deepseek.com/user/balance',headers={'Authorization':'Bearer '+key},timeout=min(30,max(.1,deadline-time.monotonic())));r.raise_for_status();return self.m.balance_value(r.json())
 def post(self,body,key,timeout):
  import requests
  r=requests.post('https://api.deepseek.com/chat/completions',headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},json=body,timeout=timeout)
  return {'status_code':r.status_code,'content_type':r.headers.get('Content-Type'),'body_text':r.text}
 def decode(self,raw):
  if not 200<=raw['status_code']<300:raise FinanceUnknown('HTTP_STATUS_'+str(raw['status_code']))
  return json.loads(raw['body_text'])
 def stem(self,env):return Path(env.out)/'llm'/f'{int(env.calls):03d}'
 def request(self,env,role,body,b,key):
  self.m.save(str(self.stem(env))+'_request.json',{'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'role':role,'call_ordinal':int(env.calls),'body':self.clean(body,key),'body_SHA256':digest(body),'bounds':b})
 def raw_response(self,env,role,raw,key):
  self.m.save(str(self.stem(env))+'_http_response.json',self.clean(raw,key))
  try:self.m.save(str(self.stem(env))+'_response.json',self.clean(json.loads(raw['body_text']),key))
  except (ValueError,TypeError,KeyError):pass
 def receipt(self,env,receipt,key):self.m.save(str(self.stem(env))+'_finance_receipt.json',self.clean(receipt,key))
 def error(self,env,role,error,key):self.m.save(str(self.stem(env))+'_error.json',self.clean(error,key))
 def final_response(self,env,result,key):self.m.save(str(self.stem(env))+'_response.json',self.clean(result,key))
_instance=None
_init=threading.Lock()
def generate(env,body,role,phase='Round2320Pilot'):
 global _instance
 with _init:
  if _instance is None:_instance=Transport(LegacyIO(),json.loads((HERE/'round_finance_config.json').read_text('utf-8-sig')))
 return _instance.generate(env,body,role,phase)

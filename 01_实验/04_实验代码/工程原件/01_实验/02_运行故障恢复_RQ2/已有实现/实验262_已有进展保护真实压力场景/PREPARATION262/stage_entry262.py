"""Only Root-preparation-authorized actual clock/body prep or paused owner."""
import argparse,datetime,hashlib,json,os,subprocess,sys,time
from pathlib import Path
P=Path(__file__).resolve().parent;H=P.parent
PYTHON=Path('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')
SITE=Path('D:/Code/毕设/graduate-thesis-experiments/工作区/0922-exp124-ranking-baselines/.venv/Lib/site-packages')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def checked(r):
 if sha(r['path'])!=r['sha256']:raise RuntimeError('EXP262_PREPARATION_REF_DRIFT')
 return read(r['path'])
def pub(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def authority(path,trial,condition):
 g=read(path);template=read(P/'ROOT_PREPARATION_GRANT262_TEMPLATE_FALSE.json')
 if g.get('schema')!=template['schema'] or g.get('preparation_authorized') is not True:raise RuntimeError('EXP262_PREPARATION_DEFAULT_CLOSED')
 if any(g.get(k) is not False for k in ('model_authorized','native_authorized','finance_authorized','private_authorized')):raise RuntimeError('EXP262_PREPARATION_ONLY_REQUIRED')
 if g.get('task_id')!='getmoto__moto-7081' or g.get('trial_id')!=trial or g.get('allowed_order')!=['SET','COUNT','O_ONLY']:raise RuntimeError('EXP262_EXACT_PREDECLARED_GROUP_REQUIRED')
 if g.get('old_flow_resume_authorized') is not False or g.get('fresh_predeclared_trial') is not True:raise RuntimeError('EXP262_FRESH_GROUP_REQUIRED')
 if g.get('preparation_source_seal')!=template['preparation_source_seal'] or g.get('caller_source_seal')!=template['caller_source_seal']:raise RuntimeError('EXP262_EXACT_PREP_CALLER_SEAL_REQUIRED')
 for key in ('preparation_source_seal','caller_source_seal'):
  seal=checked(g[key])
  for p,h in {**seal['sources'],**seal.get('dependencies',{}),**seal.get('public_inputs_SHA256',{})}.items():
   if sha(p)!=h:raise RuntimeError('EXP262_PREPARATION_SOURCE_INPUT_DRIFT:'+p)
 sampling=checked(g['independent_sampling_plan']);amendment=checked(g['finance_amendment']);registered=checked(g['amendment_registered_receipt']);group=checked(g['group_policy'])
 if sampling.get('root_authorized') is not True or sampling['budget_amendment']!=g['finance_amendment'] or sampling['window_id']!=amendment['window_id']:raise RuntimeError('EXP262_PREPARATION_TRUE_PLAN_EXACT_AMENDMENT_REQUIRED')
 if registered['budget_amendment']!=g['finance_amendment'] or registered.get('actual_same_byte0_ledger_commit') is not True:raise RuntimeError('EXP262_ACTUAL_FINANCE_BOOK_REQUIRED')
 if group.get('root_authorized') is not True or group.get('trial_id')!=trial or group.get('condition_order')!=['SET','COUNT','O_ONLY'] or group.get('budget_amendment')!=g['finance_amendment']:raise RuntimeError('EXP262_ROOT_GROUP_POLICY_REQUIRED')
 slot=next(s for s in sampling['slots'] if s['trial_id']==trial and s['policy']==condition)
 c=checked(slot['contract'])
 if c['method_source_seal']!=g['caller_source_seal'] or c['trial_master_seed']!=2026101200+int(trial[-1]):raise RuntimeError('EXP262_ORIGINAL_SEED_CALLER_CONTRACT_REQUIRED')
 if time.time()>=datetime.datetime.fromisoformat(g['lease_end_UTC']).timestamp() or time.time()>=datetime.datetime.fromisoformat('2026-10-12T22:49:05+08:00').timestamp() or any(Path(p).exists() for p in g['root_stop_paths']):raise RuntimeError('EXP262_PREPARATION_LEASE_STOP_OR_NO_NEW_LONG')
 return g,c,slot
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=('inspect','prepare','launch'));p.add_argument('--trial',choices=('trial1','trial2','trial3'));p.add_argument('--condition',choices=('SET','COUNT','O_ONLY'));p.add_argument('--root-preparation-grant');p.add_argument('--policy');p.add_argument('--finance-grant');p.add_argument('--whole-grant');a=p.parse_args()
 if a.action=='inspect':print(json.dumps(read(P/'ROOT_PREPARATION_GRANT262_TEMPLATE_FALSE.json'),ensure_ascii=False));return
 if not all((a.trial,a.condition,a.root_preparation_grant)):raise RuntimeError('EXP262_EXPLICIT_ROOT_PREPARATION_GRANT_REQUIRED')
 g,c,slot=authority(a.root_preparation_grant,a.trial,a.condition);out=Path(c['output_root']);t0=out/'SCIENCE_T0_TRIAL_PREPARATION_STARTED.json'
 if a.action=='prepare':
  if t0.exists() or any(out.rglob('SETTLED_RAW_RESPONSE.json')) or any(out.rglob('POST_INTENT.json')):raise RuntimeError('EXP262_PREPARATION_ONCE_NO_RESET_OR_OLD_RESPONSE')
  pub(t0,{'schema':'EXP262-Root-authorized-actual-trial-preparation-T0/1','monotonic':time.monotonic(),'at_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'task_id':c['task_id'],'trial_id':c['trial_id'],'policy':c['policy'],'Root_preparation_grant':ref(a.root_preparation_grant),'group_policy':g['group_policy'],'previous_source_only_preparation_cost_disclosed_separately':True,'actual_POST_not_started':True,'real_preparation_time_included':True,'not_a_reset_of_old_scientific_clock':True})
  argv=[str(PYTHON),'-X','utf8','-B',str(H/'SOURCE/environment262.py'),'--contract',slot['contract']['path']]
 else:
  if not t0.exists() or not all((a.policy,a.finance_grant,a.whole_grant)):raise RuntimeError('EXP262_SEPARATE_ROOT_AUTHORITY_PATHS_AND_T0_REQUIRED')
  argv=[str(PYTHON),'-X','utf8','-B',str(P/'launch262.py'),'--root-preparation-grant',a.root_preparation_grant,'--trial',a.trial,'--condition',a.condition,'--policy',a.policy,'--finance-grant',a.finance_grant,'--whole-grant',a.whole_grant,'--suspend-timeout','600']
 child=dict(os.environ);child.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONPATH=str(SITE)+(os.pathsep+os.environ['PYTHONPATH'] if os.environ.get('PYTHONPATH') else ''))
 code=subprocess.call(argv,cwd=str(H/'SOURCE'),env=child,creationflags=0x08000000)
 if code:raise RuntimeError('EXP262_PREPARATION_OR_HELD_OWNER_NONZERO:'+str(code))
 if a.action=='prepare':
  if ref(out/'calls/call001/FIRST_UNPOST_BODY.json')!=slot['first_complete_body']:raise RuntimeError('EXP262_ACTUAL_PREPARATION_CHANGED_COMPLETE_BODY')
  pub(out/'ROOT_ACTUAL_PREPARATION_COMPLETE262.json',{'science_T0':ref(t0),'complete_body':ref(out/'calls/call001/FIRST_UNPOST_BODY.json'),'caller_source_seal':g['caller_source_seal'],'prepared_from_current_qualified_partial_no_native_repeat':True,'POST_native_private_finance':0})
if __name__=='__main__':main()

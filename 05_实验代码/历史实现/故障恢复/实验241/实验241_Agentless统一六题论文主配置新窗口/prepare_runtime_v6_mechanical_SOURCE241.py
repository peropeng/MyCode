"""One delegated Root mechanical scope, all author/source data remain unchanged."""
from pathlib import Path
import ast,copy,datetime,hashlib,json
E=Path(__file__).resolve().parent;OLD=E/'runtime_v3_SOURCE';D=E/'runtime_v6_MECHANICAL_SOURCE'
R=Path('D:/Code/毕设/graduate-thesis-experiments');W=R/'工作区/1010-unified-six'
SHARED=R/'工作区/1009-exp239-enagent-flash-auto/实验/实验239_EnAgent_统一六题财政V3_SOURCE/shared_native_v6_SOURCE'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
def write(n,s):ast.parse(s);(D/n).write_text(s,'utf-8')
def replace(s,a,b):
 if a not in s:raise RuntimeError('SOURCE_ANCHOR_MISSING '+a[:80])
 return s.replace(a,b)
if D.exists():raise RuntimeError('NEW_MECHANICAL_SCOPE_ONCE_NO_OVERWRITE')
D.mkdir()
for f in OLD.glob('*.py'):write(f.name,f.read_text('utf-8-sig'))
save(D/'PAPER_CORE_SOURCE_PROVENANCE241.json',read(OLD/'PAPER_CORE_SOURCE_PROVENANCE241.json'))
s=(D/'contracts241.py').read_text('utf-8')
s=replace(s,"if not grant.get('new_start_UTC') or not start<=now<start+3600:","stage_wall=300 if grant.get('stage')=='MECHANICAL_ZERO_POST' else 3600\n if not grant.get('new_start_UTC') or not start<=now<start+stage_wall:")
s=replace(s,"raise DeclaredBudgetEnd('NEW_SINGLE_FLOW3600_CLOCK_NOT_CURRENT')","raise DeclaredBudgetEnd('NEW_STAGE_FIXED_CLOCK_NOT_CURRENT')")
# Native-only mechanical must never accidentally inherit generation/final authority.
s=replace(s,"if protocol.get('scope')!='UNIFIED_SIX_NEW_WINDOW'", "if grant.get('stage')=='MECHANICAL_ZERO_POST' and (grant.get('model_generation_authorized') is not False or grant.get('private_acceptance_authorized') is not False):\n  raise EngineeringUnknown('ZERO_POST_NO_PRIVATE_MECHANICAL_BOUNDARY_REQUIRED')\n if protocol.get('scope')!='UNIFIED_SIX_NEW_WINDOW'")
write('contracts241.py',s)
s=(D/'supervisor_runtime_v3_241.py').read_text('utf-8')
s=replace(s,"deadline_epoch(self.g['new_start_UTC'])+3600-time.time()", "deadline_epoch(self.g['new_start_UTC'])+(300 if self.g['stage']=='MECHANICAL_ZERO_POST' else 3600)-time.time()")
s=replace(s,"if x.mode=='mechanical':env.pop('DEEPSEEK_API_KEY',None);env.pop('OPENAI_API_KEY',None)","if x.mode=='mechanical':\n  for key in list(env):\n   if key in ('DEEPSEEK_API_KEY','OPENAI_API_KEY') or key.endswith(('_API_KEY','_ACCESS_TOKEN','_SECRET_KEY')):env.pop(key,None)")
write('supervisor_runtime_v3_241.py',s)
assert sha(D/'agentless_paper_main241.py')==sha(OLD/'agentless_paper_main241.py')
task='getmoto__moto-5406'
p=read(OLD/'candidate'/task/'protocol.SOURCE_ONLY.json')
p.update(execution_authorized=False,source_only=True,model_generation_authorized=False,native_authorized=False,
 public_contract=str(OLD/'candidate'/task/'public_contract.json'),masked_native_owner_root=str(D),
 core_source=str(D/'agentless_paper_main241.py'),output_root=str(D/'mechanical_once5406/actor_flow'),
 supervision_output_root=str(D/'mechanical_once5406/supervision'),shared_public_helper={'path':str(SHARED/'native_masked_public239.py'),'sha256':None},
 masked_native_guard_directory=str(SHARED/'guard_v6'),mechanical_only_delegated_Root_authority=True,
 scientific_generation_and_private_prohibited=True,mechanical_single_case_only=task,
 prior_runtime_v3_source_snapshot=str(OLD/'SOURCE_SEAL.json'),shared_v6_SHA_pending=True,
 mechanical_root_wall_seconds=300,no_C0_ABI_or_fixture_rerun=True)
save(D/'protocol.MECHANICAL.pending.json',p)
g=read(OLD/'candidate'/task/'ROOT_MECHANICAL_GRANT.false.template.json')
g.update(root_authorized=False,model_generation_authorized=False,native_authorized=False,
 private_acceptance_authorized=False,new_start_UTC=None,max_wall_seconds=300,
 source_seal_sha256=None,protocol_sha256=None,protocol_raw_sha256=None,
 delegated_by_Root_current_task=True,one_launch_only=True)
save(D/'ROOT_MECHANICAL_GRANT.pending.false.json',g)
old_seal=read(OLD/'SOURCE_SEAL.json')
save(D/'SOURCE_SEAL.pending.json',{'schema':'Agentless241-new-mechanical-v6-pending-source-seal/1',
 'author_pin':old_seal['author_pin'],'sources':{str(f):sha(f) for f in D.glob('*.py')},
 'external_sources_pending_shared_v6':True,'old_source_seal':str(OLD/'SOURCE_SEAL.json'),
 'source_only':True,'actual_native_API_private_fiscal':0})
save(D/'PREPARED_PENDING_SHARED_V6.json',{'directory':str(D),'at_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'author_core_exact_old_bytes':True,'actual_model_native_encoder_POST_ledger_private':0,
 'shared_v6_SHA_pending':True,'all_authorizations_still_false':True,'Root_authorized_next':'bind actual v6 SHA -> new seal -> native-only mechanical true grant -> one <=300s parent run until STOP',
 'dataset_raw_or_old_runs_copied':False,'old_runtime_v3_sources_unchanged':True})
print(canonical({'directory':str(D),'prepared':True,'grant_false_pending_v6':True,'experiments':0}))

"""Audit existing completed one-shot receipts; AST-only original bounds; draft only."""
from pathlib import Path
import ast,copy,datetime,hashlib,json
from decimal import Decimal
E=Path(__file__).resolve().parent;D=E/'runtime_v6_MECHANICAL_SOURCE';OUT=D/'mechanical_once5406/actor_flow'
R=Path('D:/Code/毕设/graduate-thesis-experiments');W=R/'工作区/1010-unified-six'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
mechanical=read(OUT/'MECHANICAL_ZERO_POST_RESULT.json');parent=read(D/'mechanical_once5406/supervision/PARENT_STOP.json')
assert parent['exit_code']==0 and not parent['timeout']
assert all(parent['stop_receipt'].get(k) is True for k in ('root_stopped','own_Job_empty_before_close','descendants_stopped'))
collection=mechanical['collection'];leaf=mechanical['first_leaf']
assert collection['known'] and leaf['known'] and len(collection['pytest']['collected'])==6919
assert all(v['status']=='passed' for v in leaf['pytest']['outcomes'].values())
body_path=OUT/'FIRST_BODY_ZERO_POST.json';body=read(body_path);cfg=read(W/'finance/finance_config_science_common_C0_v4.json')
# Compile only the original pure canonical/bounds functions, never the transport.
f=W/'finance/continuous_core_v3.py';tree=ast.parse(f.read_text('utf-8-sig'))
rows=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('canonical','bounds')]
assert {n.name for n in rows}=={'canonical','bounds'}
class GateRejected(ValueError):pass
ns={'json':json,'D':Decimal,'GateRejected':GateRejected}
exec(compile(ast.Module(body=rows,type_ignores=[]),str(f),'exec'),ns)
bound=ns['bounds'](body,cfg)
events=[json.loads(s) for s in (OUT/'events.jsonl').read_text('utf-8').splitlines() if s.strip()]
controller=[x['identity'] for x in events if x.get('event')=='CONTROLLER_SELF_IDENTITY_BEFORE_AUTHOR_IMPORT']
certificates=[]
for run in sorted((OUT/'masked_public_native').iterdir()):
 p=run/'actual_python_identity.json'
 if p.exists():certificates.append({'path':str(p),'sha256':sha(p),'actual':read(p)})
receipt={'schema':'Agentless241-complete-v6-one-shot-mechanical-audit/1','at_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'task_id':'getmoto__moto-5406','status':'MECHANICAL_ZERO_POST_QUALIFIED_PENDING_ROOT_ACCEPTANCE',
 'source_seal_path':str(D/'SOURCE_SEAL.json'),'source_seal_digest':digest(read(D/'SOURCE_SEAL.json')),
 'source_seal_rawSHA':sha(D/'SOURCE_SEAL.json'),'mechanical_result':str(OUT/'MECHANICAL_ZERO_POST_RESULT.json'),
 'mechanical_result_SHA256':sha(OUT/'MECHANICAL_ZERO_POST_RESULT.json'),'parent_STOP':str(D/'mechanical_once5406/supervision/PARENT_STOP.json'),
 'parent_STOP_SHA256':sha(D/'mechanical_once5406/supervision/PARENT_STOP.json'),'parent_seconds':parent['seconds'],'parent_timeout':False,'parent_exit_code':0,
 'parent_actual_STOP':parent['stop_receipt'],'actual_controller_self':controller,'actual_product_self_certificates':certificates,
 'collection':{'known':collection['known'],'leaf_count':len(collection['pytest']['collected']),'seconds':collection['execution']['seconds'],
  'collection_errors':len(collection['pytest']['collection_errors']),'safe_denied_platform_probes':len(collection['execution']['observed_safe_denied_platform_probes']),
  'other_guard_denials':len(collection['execution']['guard_denials']),'STOP':collection['execution']['stop_receipt'],'not_a_whole_C0_PASS_pool':True},
 'first_leaf':{'selected':list(leaf['pytest']['outcomes']),'known':leaf['known'],'actual_three_phases':leaf['pytest']['outcomes'],'seconds':leaf['execution']['seconds'],
  'safe_denied_platform_probes':len(leaf['execution']['observed_safe_denied_platform_probes']),'other_guard_denials':len(leaf['execution']['guard_denials']),
  'STOP':leaf['execution']['stop_receipt']},'first_actual_author_body':{'path':str(body_path),'SHA256':sha(body_path),'bytes':body_path.stat().st_size,
   'canonical_bytes':len(canonical(body).encode()),'model':body['model'],'max_tokens':body['max_tokens'],'Root_common_C0_injected':True,
   'original_pure_bounds_source':str(f),'original_bounds_source_SHA256':sha(f),'actual_full_bounds':bound,'bounds_passed':True,
   'actual_POST':False,'no_body_clipping_or_reduced_prompt':True},'model_generation_private_fiscal_IO':0,'fee_CNY':'0',
 'original_C0_ABI_or_fixture_not_repeated':True,'science_method_success':None,'author40patch40repro_not_run_or_scored':True,'one_mechanical_run_only_no_retry':True}
save(D/'MECHANICAL_AUDIT_V6_241.json',receipt)

base=read(D/'protocol.MECHANICAL.release.json');gbase=read(D/'ROOT_MECHANICAL_GRANT.actual.json');commands={}
for task in base['task_order']:
 p=copy.deepcopy(base);p.update(task_id=task,execution_authorized=False,source_only=True,native_authorized=False,model_generation_authorized=False,
  public_contract=str(E/'runtime_v3_SOURCE/candidate'/task/'public_contract.json'),
  GPU_public_index_binding=str(E/'runtime_v3_SOURCE/candidate'/task/'GPU_INDEX_BINDING.json'),
  output_root=str(D/'science_once_six'/task/'actor_flow'),supervision_output_root=str(D/'science_once_six'/task/'supervision'),
  mechanical_only_delegated_Root_authority=False,mechanical_single_case_only=None,mechanical_root_wall_seconds=None,
  scientific_generation_and_private_prohibited=True,Root_actual_241_mechanical_candidate={'path':str(D/'MECHANICAL_AUDIT_V6_241.json'),'sha256':sha(D/'MECHANICAL_AUDIT_V6_241.json')},
  same_author_core_4L40P40T_and_all_parameters=True,one_runtime_seal_all_six_no_per_task_code_edits=True)
 out=D/'science_release_candidate_FALSE'/task;save(out/'protocol.SOURCE_ONLY.json',p)
 g=copy.deepcopy(gbase);g.update(stage='FULL_PAPER_MAIN_SCIENCE_ONCE',task_id=task,root_authorized=False,native_authorized=False,
  model_generation_authorized=False,private_acceptance_authorized=False,parent_controller_job_qualified=False,
  new_start_UTC=None,max_wall_seconds=3600,source_seal_sha256=receipt['source_seal_digest'],protocol_sha256=digest(p),
  protocol_raw_sha256=sha(out/'protocol.SOURCE_ONLY.json'),neutral_mechanical_qualification_sha256=sha(D/'MECHANICAL_AUDIT_V6_241.json'),
  launch_authorized_only_after_Root_v6_narrow_leaf_PASS=False,science_Root_release_pending=True)
 save(out/'ROOT_SCIENCE_GRANT.false.template.json',g)
 command=[g['controller_physical_python_expected'],'-X','utf8','-B',str(D/'supervisor_runtime_v3_241.py'),'science',
  '--protocol',str(out/'protocol.SCIENCE.release.json'),'--grant',str(out/'ROOT_SCIENCE_GRANT.actual.json'),
  '--seal',str(D/'SOURCE_SEAL.json'),'--contract',p['public_contract']]
 commands[task]={'command_AFTER_Root_release_only':command,'protocol_false_source':str(out/'protocol.SOURCE_ONLY.json'),
  'grant_false_template':str(out/'ROOT_SCIENCE_GRANT.false.template.json'),'full_author40patch40repro':True,'independent_final_Root_only_after_author_STOP_once':True}
save(D/'SCIENCE_SIX_EXACT_COMMANDS_ALL_FALSE241.json',{'source_seal_digest':receipt['source_seal_digest'],'task_order':base['task_order'],
 'all_scientific_grants_false':True,'same_frozen_runtime_source_required':True,'commands':commands})
print(canonical({'mechanical_audit':str(D/'MECHANICAL_AUDIT_V6_241.json'),'auditSHA':sha(D/'MECHANICAL_AUDIT_V6_241.json'),
 'body_SHA':sha(body_path),'bounds_passed':True,'bound_CNY':bound['global_reserve'],'parent_seconds':parent['seconds'],'STOP':parent['stop_receipt'],
 'science_commands':str(D/'SCIENCE_SIX_EXACT_COMMANDS_ALL_FALSE241.json'),'science_grants_false':True}))
